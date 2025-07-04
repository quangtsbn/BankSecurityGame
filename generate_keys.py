import os
from utils.crypto_utils import generate_rsa_keys

os.makedirs("keys", exist_ok=True)
print("--- Đang tạo khóa cho khách hàng ---")
generate_rsa_keys(private_path="keys/customer_private.pem", public_path="keys/customer_public.pem")
print("\n--- Đang tạo khóa cho ngân hàng ---")
generate_rsa_keys(private_path="keys/bank_private.pem", public_path="keys/bank_public.pem")
print("\nHoàn tất tạo khóa!")