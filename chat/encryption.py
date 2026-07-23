import secrets 
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AAD = b"encrypted-chat-v1"
NONCE_SIZE = 12
MAX_MESSAGE_SIZE = 1_048_548

def encrypt_message(cipher: AESGCM, message: str) -> bytes:
    data = message.encode("utf-8")
    if not data:
        raise ValueError("Message is empty.")
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is to long.")
    nonce = secrets.token_bytes(NONCE_SIZE)
    return nonce + cipher.encrypt(nonce, data, AAD)