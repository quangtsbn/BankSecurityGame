import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from base64 import b64encode, b64decode

def generate_rsa_keys(private_path="keys/customer_private.pem", public_path="keys/customer_public.pem"):
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open(private_path, "wb") as f: f.write(private_key)
    public_key = key.publickey().export_key()
    with open(public_path, "wb") as f: f.write(public_key)
    print(f"Đã tạo khóa tại: {private_path} và {public_path}")

def sign_data(private_key_path, data):
    with open(private_key_path, "r") as f: private_key = RSA.import_key(f.read())    
    h = SHA256.new(data)
    signature = pkcs1_15.new(private_key).sign(h)
    return b64encode(signature).decode('utf-8')

def verify_signature(public_key_path, data, signature):
    with open(public_key_path, "r") as f: public_key = RSA.import_key(f.read())
    h = SHA256.new(data)
    try:
        pkcs1_15.new(public_key).verify(h, b64decode(signature))
        return True
    except (ValueError, TypeError): return False

def encrypt_aes(data, key):
    if isinstance(data, str): data = data.encode('utf-8')
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return {"ciphertext": b64encode(ciphertext).decode('utf-8'), "nonce": b64encode(cipher.nonce).decode('utf-8'), "tag": b64encode(tag).decode('utf-8')}

def decrypt_aes(encrypted_package, key):
    try:
        cipher = AES.new(key, AES.MODE_GCM, nonce=b64decode(encrypted_package["nonce"]))
        plaintext = cipher.decrypt_and_verify(b64decode(encrypted_package["ciphertext"]), b64decode(encrypted_package["tag"]))
        return plaintext.decode('utf-8')
    except (ValueError, KeyError): return None