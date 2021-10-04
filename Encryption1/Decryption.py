from cryptography.fernet import Fernet

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    
    with open("decrypted.txt", "w") as Decrypt_file:
      Decrypt_file.write(decrypted_message.decode())

if __name__ == "__main__":
   with open('encrypted.txt') as f:
    contents = f.read()

    decrypt_message(contents)