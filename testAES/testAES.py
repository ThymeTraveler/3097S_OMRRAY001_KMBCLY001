import AESstuff,time

input=input("\n\nplease enter the file name that you want to use to test encryption \n(eg. 100kitem.txt, rand2000.txt, rand10000.txt and test.csv): ")

begin=time.time()
AESstuff.encryptFile(input,"password","Encrypted") #Encrypt mp3 using AES
print("\nencryption took " + str(time.time()-begin) + " seconds\n")

AESstuff.decryptFile("Encrypted.enc","password")

string="\nThe file has been encrypted and then decrypted so you can check the accuracy of the encryption.\nThe output file name is \"output\". \nIf you open it in a text editor the data will be the same as "+input+"\'s data.\n \n "

print(string)