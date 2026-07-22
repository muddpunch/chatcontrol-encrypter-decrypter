from cryptography.fernet import Fernet 
from pathlib import Path

KEY_FILE = Path(__file__).with_name("key.txt")
def main () -> None:
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    print(f"New key generated! Generated key: {key.decode('ascii')}")
# Creates a key for the encryption in key.txt
if __name__ == "__main__":
    main()