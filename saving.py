import binascii 
from pathlib import Path
from cryptography.fernet import Fernet
KEY_FILE = Path(__file__).with_name("key.txt")

def main() -> None:
    raw = input ("Paste key: ").strip()
    try:
        key = raw.encode("ascii")
        Fernet(key)
    except (UnicodeEncodeError, ValueError, binascii.Error):
        raise SystemExit("Invalid Fernet key.")

    old_key = KEY_FILE.read_bytes().strip() if KEY_FILE.exists() else b""
    if old_key and old_key != key:
        confirm = input("Replace current key? [y/N]: ").strip().lower()
        if confirm not in {"y", "yes"}:
            print("Cancelled.")
            return
    KEY_FILE.write_bytes(key)
    print("Key saved to key.txt")
if __name__ == "__main__":
    main()