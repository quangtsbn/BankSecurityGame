from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import json
from utils import crypto_utils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_and_seamless_key'
socketio = SocketIO(app)

game_states = {}

def analyze_transaction(tx_package, aes_key):
    data_to_sign = (tx_package["from_account"] + tx_package["transaction_id"] + tx_package["encrypted_payload"]["ciphertext"]).encode('utf-8')
    is_signature_valid = crypto_utils.verify_signature("keys/customer_public.pem", data_to_sign, tx_package['signature'])
    decrypted_data = crypto_utils.decrypt_aes(tx_package['encrypted_payload'], aes_key) if is_signature_valid else None
    return {'is_fully_valid': is_signature_valid and (decrypted_data is not None)}

def load_all_transactions():
    all_txs = []
    level_boundaries = []
    for i in range(1, 4):
        try:
            with open(f"data/level_{i}_transactions.json", 'r') as f:
                level_txs = json.load(f)
                all_txs.extend(level_txs)
                level_boundaries.append(len(all_txs))
        except FileNotFoundError:
            print(f"Warning: data/level_{i}_transactions.json not found.")
            break
    return all_txs, level_boundaries

@app.route('/')
def index(): return render_template('index.html')

@socketio.on('disconnect')
def handle_disconnect():
    game_states.pop(request.sid, None)
    print(f'Client disconnected: {request.sid}')

@socketio.on('start_game')
def handle_start_game():
    sid = request.sid
    all_transactions, level_boundaries = load_all_transactions()
    with open("data/aes_key.bin", "rb") as f: aes_key = f.read()

    game_states[sid] = {
        'transactions': all_transactions,
        'analyzed_txs': [analyze_transaction(tx, aes_key) for tx in all_transactions],
        'level_boundaries': level_boundaries,
        'current_index': 0,
        'current_level': 1,
        'score': 0,
    }
    
    emit('game_started', {'total_transactions': len(all_transactions)})
    send_transaction_data(sid)

def send_transaction_data(sid):
    state = game_states.get(sid)
    if not state: return
    index = state['current_index']
    
    emit('new_transaction_data', {
        'transaction': state['transactions'][index],
        'score': state['score'],
        'current_index': index,
        'current_level': state['current_level']
    })

@socketio.on('player_action')
def handle_player_action(data):
    sid = request.sid
    state = game_states.get(sid)
    if not state: return

    action = data.get('action')
    tx = state['transactions'][state['current_index']]
    with open("data/aes_key.bin", "rb") as f:
        aes_key = f.read()
    
    data_to_sign = (tx["from_account"] + tx["transaction_id"] + tx["encrypted_payload"]["ciphertext"]).encode('utf-8')
    is_signature_valid = crypto_utils.verify_signature("keys/customer_public.pem", data_to_sign, tx['signature'])
    
    if action == 'check_signature':
        msg_type = 'log-success' if is_signature_valid else 'log-fail'
        message = 'Phản hồi: Chữ ký RSA hợp lệ. Tính toàn vẹn (SHA) được đảm bảo.' if is_signature_valid else 'Phản hồi: CẢNH BÁO! Chữ ký RSA không hợp lệ.'
        emit('action_result', {'action': action, 'type': msg_type, 'message': message})
            
    elif action == 'decrypt':
        response = {'action': action}
        if not is_signature_valid:
            response.update({'type': 'log-fail', 'message': 'Phản hồi: Không thể giải mã vì chữ ký không hợp lệ. Luôn xác thực trước!'})
        else:
            decrypted_json_str = crypto_utils.decrypt_aes(tx['encrypted_payload'], aes_key)
            if decrypted_json_str:
                decrypted_data = json.loads(decrypted_json_str)
                response.update({
                    'type': 'log-success', 
                    'message': 'Phản hồi: Giải mã AES thành công. Thông tin chi tiết đã được hiển thị.',
                    'decrypted_info': {
                        'to_account': decrypted_data.get('to_account', 'Không rõ'),
                        'amount': decrypted_data.get('amount', 0)
                    }
                })
            else:
                response.update({'type': 'log-fail', 'message': 'Phản hồi: CẢNH BÁO! Giải mã AES thất bại.'})
        
        emit('action_result', response)


@socketio.on('player_decision')
def handle_player_decision(data):
    sid = request.sid; state = game_states.get(sid)
    if not state: return
    player_decision = data.get('decision')
    truth = state['analyzed_txs'][state['current_index']]
    
    is_correct, message = False, ""
    if player_decision == 'approve' and truth['is_fully_valid']:
        is_correct, state['score'], message = True, state['score'] + 1, "QUYẾT ĐỊNH ĐÚNG! Giao dịch hợp lệ đã được phê duyệt."
    elif player_decision == 'reject' and not truth['is_fully_valid']:
        is_correct, state['score'], message = True, state['score'] + 1, "QUYẾT ĐỊNH ĐÚNG! Giao dịch không an toàn đã bị chặn."
    else:
        is_correct, message = False, "QUYẾT ĐỊNH SAI! Bạn đã phê duyệt giao dịch nguy hiểm." if player_decision == 'approve' else "QUYẾT ĐỊNH SAI! Bạn đã từ chối giao dịch hợp lệ."

    emit('decision_judged', {'correct': is_correct, 'message': message, 'score': state['score']})

@socketio.on('request_next_transaction')
def handle_next_transaction():
    sid = request.sid; state = game_states.get(sid)
    if not state: return
    
    state['current_index'] += 1
    
    if state['current_index'] >= len(state['transactions']):
        emit('game_over', {'score': state['score']})
        return
        
    if state['current_index'] in state['level_boundaries']:
        state['current_level'] += 1
        emit('level_up', {'new_level': state['current_level']})
        
    send_transaction_data(sid)

if __name__ == '__main__':
    required_files = ["keys/customer_public.pem", "data/aes_key.bin", "data/level_1_transactions.json"]
    if not all(os.path.exists(p) for p in required_files):
        print("LỖI: Thiếu các file cần thiết.\nVui lòng chạy:\n1. python generate_keys.py\n2. python create_sample_data.py")
    else:
        print("Server đang chạy tại http://127.0.0.1:5000")
        socketio.run(app, debug=True)