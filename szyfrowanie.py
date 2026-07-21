<<<<<<< Updated upstream
import os 
import sys
import time
import random
import string
from cryptography.fernet import Fernet

cipher = Fernet(key)

=======
from pathlib import Path 
from cryptography.fernet import Fernet 

KEY_FILE = Path(__file__).with_name("key.txt")

def get_cipher() -> Fernet:
    key = KEY_FILE.read_bytes().strip()
    if not key:
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
    return Fernet(key)
def main() -> None:
    message = input("Wiadomość: ")
    if not message:
        raise SystemExit("Wiadomość nie może być pusta.")
    encrypted = get_cipher().encrypt(message.encode("utf-8"))
    print(encrypted.decode("ascii"))
if __name__ == "__main__":
    main()
>>>>>>> Stashed changes
