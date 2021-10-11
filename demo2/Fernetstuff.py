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

def decrypt_message(encrypted_message,outputFile):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    
    with open(outputFile, "w") as Decrypt_file:
      Decrypt_file.write(decrypted_message.decode())

def decrypt_file(inputFile,outputFile):
    with open(inputFile) as f:
        contents = f.read()
        decrypt_message(contents,outputFile)


def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    with open(outputFile, "wb") as encrypt_file:
        encrypt_file.write(encrypted_message)


def encrypt_file(inputFile,outputFile):
    with open(inputFile) as f:
        contents = f.read()
        encrypt_message(contents,outputFile)