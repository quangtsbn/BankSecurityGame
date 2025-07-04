import os
import json
import uuid
import base64
from Crypto.Random import get_random_bytes
from utils.transaction_utils import create_secure_transaction
from utils.crypto_utils import generate_rsa_keys

# --- THIẾT LẬP BAN ĐẦU ---
os.makedirs("data", exist_ok=True)
os.makedirs("keys", exist_ok=True)

# 1. Tạo khóa cho kẻ tấn công (nếu chưa có)
HACKER_PRIVATE_KEY_PATH = "keys/hacker_private.pem"
if not os.path.exists(HACKER_PRIVATE_KEY_PATH):
    print("--- Đang tạo khóa cho Kẻ tấn công ---")
    generate_rsa_keys(private_path=HACKER_PRIVATE_KEY_PATH, public_path="keys/hacker_public.pem")

# 2. Tạo khóa AES chung
AES_KEY = get_random_bytes(16)
with open("data/aes_key.bin", "wb") as f:
    f.write(AES_KEY)
print(f"\nĐã tạo và lưu khóa AES tại data/aes_key.bin")

# --- ĐỊNH NGHĨA CÁC GIAO DỊCH CHO TỪNG CẤP ĐỘ ---

# ==================== CẤP ĐỘ 1: GIAO DỊCH CƠ BẢN ====================
print("\n--- Đang tạo dữ liệu cho Cấp độ 1 ---")
level_1_transactions = []

# Giao dịch hợp lệ 1
tx1_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-001", "to_account": "RECV-A", "amount": 1500.75}
level_1_transactions.append(create_secure_transaction("keys/customer_private.pem", tx1_data, AES_KEY))

# Giao dịch hợp lệ 2
tx2_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-002", "to_account": "RECV-B", "amount": 99.99}
level_1_transactions.append(create_secure_transaction("keys/customer_private.pem", tx2_data, AES_KEY))

with open("data/level_1_transactions.json", "w") as f:
    json.dump(level_1_transactions, f, indent=4)
print("Đã tạo file data/level_1_transactions.json")

# ==================== CẤP ĐỘ 2: TẤN CÔNG CƠ BẢN ====================
print("\n--- Đang tạo dữ liệu cho Cấp độ 2 ---")
level_2_transactions = level_1_transactions.copy()

# Tấn công 1: Dữ liệu bị thay đổi sau khi ký (Tampering Attack)
# Chữ ký sẽ không còn khớp với nội dung gói tin.
print("Thêm giao dịch bị thay đổi (Tampering Attack)...")
tampered_tx_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-003", "to_account": "HACK-ACC-1", "amount": 50000.00}
tampered_tx = create_secure_transaction("keys/customer_private.pem", tampered_tx_data, AES_KEY)
tampered_tx["from_account"] = "ATTACKER-FAKE-ACC" # Thay đổi dữ liệu sau khi đã ký
level_2_transactions.append(tampered_tx)

# Tấn công 2: Dữ liệu mã hóa bị hỏng (Corruption Attack)
# Chữ ký vẫn hợp lệ, nhưng khi giải mã AES sẽ thất bại vì tag không khớp.
print("Thêm giao dịch bị hỏng (Corruption Attack)...")
corrupted_tx_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-004", "to_account": "RECV-D", "amount": 123.45}
corrupted_tx = create_secure_transaction("keys/customer_private.pem", corrupted_tx_data, AES_KEY)
# Làm hỏng ciphertext
original_ciphertext = base64.b64decode(corrupted_tx["encrypted_payload"]["ciphertext"])
corrupted_ciphertext = bytearray(original_ciphertext)
corrupted_ciphertext[5] = (corrupted_ciphertext[5] + 1) % 256 # Thay đổi 1 byte
corrupted_tx["encrypted_payload"]["ciphertext"] = base64.b64encode(corrupted_ciphertext).decode('utf-8')
level_2_transactions.append(corrupted_tx)

with open("data/level_2_transactions.json", "w") as f:
    json.dump(level_2_transactions, f, indent=4)
print("Đã tạo file data/level_2_transactions.json")

# ==================== CẤP ĐỘ 3: THỬ THÁCH NÂNG CAO ====================
print("\n--- Đang tạo dữ liệu cho Cấp độ 3 ---")
level_3_transactions = level_2_transactions.copy()

# Tấn công 3: Kẻ gian dùng khóa riêng của mình để ký (Impersonation Attack)
# Gói tin có vẻ hợp lệ, nhưng chữ ký được tạo bởi khóa của hacker, không phải của khách hàng.
print("Thêm giao dịch giả mạo (Impersonation Attack)...")
impersonation_tx_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-001", "to_account": "HACK-ACC-2", "amount": 999999.99}
# Dùng khóa của hacker để ký
impersonation_tx = create_secure_transaction(HACKER_PRIVATE_KEY_PATH, impersonation_tx_data, AES_KEY)
level_3_transactions.append(impersonation_tx)

# Thêm một giao dịch hợp lệ cuối cùng để kiểm tra sự tập trung
final_valid_tx_data = {"transaction_id": str(uuid.uuid4()), "from_account": "CUST-005", "to_account": "RECV-E", "amount": 789.00}
level_3_transactions.append(create_secure_transaction("keys/customer_private.pem", final_valid_tx_data, AES_KEY))


with open("data/level_3_transactions.json", "w") as f:
    json.dump(level_3_transactions, f, indent=4)
print("Đã tạo file data/level_3_transactions.json")

print("\nHoàn tất tạo tất cả dữ liệu game!")