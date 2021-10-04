import cryptography
from cryptography.fernet import Fernet

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    with open("encrypted.txt", "wb") as encrypt_file:
        encrypt_file.write(encrypted_message)

if __name__ == "__main__":

   with open("fftcompressed.out") as f:
    message = f.read()
    encrypt_message(message)
    
   