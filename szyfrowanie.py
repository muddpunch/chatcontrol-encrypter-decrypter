from pathlib import Path
from cryptography.fernet import Fernet

# key path relative to script, not to the directory.
KEY_FILE = Path(__file__).with_name("key.txt")
# load that gened key
def load_cipher() -> Fernet:
    try:
        key = KEY_FILE.read_bytes().strip()
        return Fernet(key)
    except FileNotFoundError:
        raise SystemExit("No key.txt found. First open Key.py")
    except ValueError:
        raise SystemExit("No valid key.txt. Generate new key from Key.py")
def main() -> None:
    message = input ("Message: ")
    if not message:
        raise SystemExit("Message cannot be empty.")
    # fernet encrypts utf-8 bytes and returns an ascii token
    encrypted = load_cipher().encrypt(message.encode("utf-8"))
    print(f"Encrypted message: {encrypted.decode('ascii')}")
if __name__ == "main":
    main()