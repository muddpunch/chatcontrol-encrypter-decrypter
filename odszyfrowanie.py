from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

# use same shared key that was encrypted?
KEY_FILE = Path(__file__).with_name("key.txt")

# load and vali that shared key
def load_cipher() -> Fernet:
    try:
        key = KEY_FILE.read_bytes().strip()
        return Fernet(key)
    except FileNotFoundError:
        raise SystemExit("No key.txt found.")
    except ValueError:
        raise SystemExit("No valid key.txt.")
def main() -> None:
    encrypted = input("Encrypted message: ").strip()
    if not encrypted:
        raise SystemExit("Message cannot be empty.")
    # decrypt fails if token was either modified or encrypted with some another key.
    try:
        decrypted = load_cipher().decrypt(encrypted.encode("ascii"))
        print(f"Decrypted message: {decrypted.decode('utf-8')}")
    except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError):
        raise SystemExit("Invalid message or invalid key.")

if __name__ == "__main__":
    main()
