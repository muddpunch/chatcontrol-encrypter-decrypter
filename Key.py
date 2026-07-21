from cryptography.fernet import Fernet 

key = Fernet.generate_key()

with open("key.txt", "wb") as file:
    file.write(key)

#Creates a key for the encryption in key.txt