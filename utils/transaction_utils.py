import json
import uuid
from . import crypto_utils

def create_secure_transaction(customer_private_key_path, transaction_data, aes_key):
    transaction_json = json.dumps(transaction_data)
    encrypted_payload = crypto_utils.encrypt_aes(transaction_json, aes_key)
    data_to_sign = (transaction_data["from_account"] + transaction_data["transaction_id"] + encrypted_payload["ciphertext"]).encode('utf-8')
    signature = crypto_utils.sign_data(customer_private_key_path, data_to_sign)
    return {
        "transaction_id": transaction_data["transaction_id"],
        "from_account": transaction_data["from_account"],
        "encrypted_payload": encrypted_payload,
        "signature": signature
    }