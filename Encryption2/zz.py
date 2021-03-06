from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pathlib import Path
import logging
import concurrent.futures
import sys
import getopt

B_S = 16
B_M = 100

global AsciiStuff
AsciiStuff = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.1234567890"

MW = 10


def generateKey(length, key):
    retKey = str()
    
    
    for i in range(length):
        retKey += key[i % len(key)]
        
    return retKey

def vencrypt(Gospel, key):

    key = generateKey(len(Gospel), key)
    ciphertext = "E"
    
    for index, char in enumerate(Gospel):
        ciphertext += AsciiStuff[(AsciiStuff.find(key[index]) + AsciiStuff.find(char)) % len(AsciiStuff)]
        
    return ciphertext

def vdecrypt(ciphertext, key):

    key = generateKey(len(ciphertext), key)
    Gospel = str()
    ciphertext = ciphertext[1:]
    
    for index, char in enumerate(ciphertext):
        Gospel += AsciiStuff[(AsciiStuff.find(char) - AsciiStuff.find(key[index])) % len(AsciiStuff)]
        
    return Gospel

def encryptFile(filePath, password):

    try:
    
        logging.info("Started encoding: " + filePath.resolve().as_posix())
        hashObj = SHA256.new(password.encode('utf-8'))
        hkey = hashObj.digest()
        encryptPath = Path(filePath.parent.resolve().as_posix() + "/" + vencrypt(filePath.name, password) + ".enc")
        
        if encryptPath.exists():
            encryptPath.unlink()
            
        with open(filePath, "rb") as input_file, encryptPath.open("ab") as output_file:
            content = b''
            content = input_file.read(B_S*B_M)

            while content != b'':
                output_file.write(encrypt(hkey, content))
                content = input_file.read(B_S*B_M)

            logging.info("Encoded " + filePath.resolve().as_posix())
            logging.info("To " +encryptPath.resolve().as_posix())
            
    except Exception as e:
        print(e)

def decryptFile(filePath, password):

    logging.info("Started decoding: " + filePath.resolve().as_posix())
    
    try:
    
        hashObj = SHA256.new(password.encode('utf-8'))
        hkey = hashObj.digest()
        DFP = Path(filePath.parent.resolve().as_posix() + "/" + vdecrypt(filePath.name, password)[:-4])
        
        if DFP.exists():
            DFP.unlink()
            
        with filePath.open("rb") as input_file, DFP.open("ab") as output_file:
            values = input_file.read(B_S*B_M)
            
            while values != b'':
                output_file.write(decrypt(hkey, values))
                values = input_file.read(B_S*B_M)

        logging.info("Decoded: " + filePath.resolve().as_posix()[:-4])
        logging.info("TO: " + DFP.resolve().as_posix() )

    except Exception as e:
        print(e)

def pad(Gospel, B_S, PAD):

    return Gospel + PAD * ((B_S - len(Gospel) % B_S) % B_S)

def encrypt(key, Gospel):

    PAD = b'\0'
    cipher = AES.new(key, AES.MODE_ECB)
    result = cipher.encrypt(pad(Gospel, B_S, PAD))
    
    return result

def decrypt(key, Gospel):

    PAD = b'\0'
    decipher = AES.new(key, AES.MODE_ECB)
    pt = decipher.decrypt(Gospel)
    
    for i in range(len(pt)-1, -1, -1):
    
        if pt[i] == PAD:
            pt = pt[:i]
            
        else:
            break
    return pt

def getMaxLen(arr):
    maxLen = 0
    for elem in arr:
        if len(elem) > maxLen:
            maxLen = len(elem)
    return maxLen

def getTargetFiles(fileExtension):
    fileExtensions = []
    if len(fileExtension) == 0:
        fileExtensions.append("*")
    else:
        for Extension in fileExtension:
            fileExtensionFormatted = "*."
            for char in Extension:
                fileExtensionFormatted += "[" + char + "]"
            fileExtensions.append(fileExtensionFormatted)

    return fileExtensions

def generateEncryptThreads(fileExtensions, password, removeFiles):
    fileExtensionFormatted = getTargetFiles(fileExtensions)
    filePaths = []
    for fileExtension in fileExtensionFormatted:
        filePaths = filePaths + list(Path(".").rglob(fileExtension))

    with concurrent.futures.ThreadPoolExecutor(max_workers=MW) as executor:
        for filePath in filePaths:
            executor.submit(encryptFile, *(filePath, password))
    if removeFiles:
        for filePath in filePaths:
            filePath.unlink()

def generateDecryptThreads(password, removeFiles):
    filePaths = list(Path(".").rglob("*.[eE][nN][cC]"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=MW) as executor:
        for filePath in filePaths:
            executor.submit(decryptFile, *(filePath, password))
    if removeFiles:
        for filePath in filePaths:
            filePath.unlink()

def removeEncryptedFiles():
    filePaths = list(Path(".").rglob("*.[eE][nN][cC]"))
    for filePath in filePaths:
            filePath.unlink()

def removeExFiles(fileExtensions):
    fileExtensionFormatted = getTargetFiles(fileExtensions)
    filePaths = []
    for fileExtension in fileExtensionFormatted:
        filePaths = filePaths + list(Path(".").rglob(fileExtension))
    for filePath in filePaths:
        filePath.unlink()

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    if len(sys.argv[1:]) < 1:

        print("(1) - encrypt\n(2) - decrypt\n(3) - remove .enc files\n(4) - remove other files")
        mode = int(input("---> "))
        password = str()
        passwordConfirm = str()

        if mode == 1 or mode == 2:
            password = input("password: ")
            passwordConfirm = input("confirm password: ")

        if password != passwordConfirm:
            logging.error("Passwords not matching")
            exit()

        if mode == 1:
            fileExtensions = input("Enter file extensions (jpg png ...): ").split()
            removeFiles = input("Remove unencrypted files afterwards(Y): ")
            if removeFiles[0].upper() == 'Y':
                removeFiles = True
            else:
                removeFiles = False
            generateEncryptThreads(fileExtensions, password, removeFiles)

        elif mode == 2:
            removeFiles = input("Remove encrypted files afterwards(Y): ")
            if removeFiles[0].upper() == 'Y':
                removeFiles = True
            else:
                removeFiles = False
            generateDecryptThreads(password, removeFiles)

        elif mode == 3:
            removeEncryptedFiles()

        elif mode == 4:
            fileExtensions = input("Enter file extensions (jpg png ...): ").split()
            removeExFiles(fileExtensions)

    else:
    
        removeFiles = False
        password = ""
        mode = 0
        opts, args = getopt.getopt(sys.argv[1:], "rm:p:w:vh")

        for opt, arg in opts:
        
            if opt == '-r':
                removeFiles = True
                
            elif opt == '-m':
                mode = int(arg)
                
            elif opt == '-w':
                MW = int(arg)
                
            elif opt == '-p':
                password = arg
                
            elif opt == '-h':
                print(helpText)
                
                exit()

        if mode == 0 or (password == "" and mode in (1,2,5)):
            print("Missing arguments!\nType -h as argument to get help Page.")
            exit()

        if mode == 1:
            generateEncryptThreads(args, password, removeFiles)

        elif mode == 2:
            generateDecryptThreads(password, removeFiles)

        elif mode == 3:
            removeEncryptedFiles()

        elif mode == 4:
        
        
            if args == []:
                filePaths = list(Path(".").rglob("*.*"))
                removePaths = list()
                
                for index, filePath in enumerate(filePaths):
                
                    if not ".enc" in filePath.name and not ".py" in filePath.name:
                        removePaths.append(filePath)
                        
                try:
                
                    for removeFilePath in removePaths:
                    
                        removeFilePath.unlink()

                except Exception as e:
                
                    print(e)

            else:
            
                removeExFiles(args)

        elif mode == 5:
        
            encryptFile(Path(args), password)