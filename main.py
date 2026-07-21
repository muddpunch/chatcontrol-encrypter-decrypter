import time
import sys 
import os 
import random
import string
<<<<<<< Updated upstream
from cryptography import Fernet
=======
from cryptography import fernet

print("""What do you want to do?
      1.Generate new key.
      2.Encrypt your message.
      3.Decrypt a message(Remember to have the same key as the sender of the message)
      
      """)
choice = int(input("Choose a number:"))
>>>>>>> Stashed changes
