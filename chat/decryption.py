from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import AAD, NONCE_SIZE

def decrypt_message(cipher: AESGCM, payload: bytes) -> str:
    if len(payload) < NONCE_SIZE + 16:
        raise ValueError("Invalid encrypted message.")
    nonce = payload[:NONCE_SIZE]
    ciphertext = payload[NONCE_SIZE:]
    plaintext = cipher.decrypt(nonce, ciphertext, AAD)
    return plaintext.decode("utf-8")