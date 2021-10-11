import AESstuff,Fernetstuff,FFTstuff,FTPstuff,FTPstuff,ICM20948,MP3stuff
import threading,time, numpy as np
n=1

def method1(input):
    global n
    normalisingFactor = np.linalg.norm(input)
    normal_array = input/normalisingFactor
    MP3stuff.compress(normal_array)
    AESstuff.encryptFile("sound.mp3","password",str(normalisingFactor)+"_encrypted"+str(n))
    FTPstuff.send(str(normalisingFactor)+"_encrypted"+str(n)+".enc")
    print("n is "+str(n))
    


running =True
AESstuff.removeEncryptedFiles()
while running:
    begin=time.time()
    values1,values2,values3=ICM20948.getValues(10000)
    print("Data acquistion took " + str(time.time()-begin))
    
    x = threading.Thread(target=method1, args=(values1,))
    x.start()
    y = threading.Thread(target=method1, args=(values2,))
    y.start()
    z = threading.Thread(target=method1, args=(values3,))
    z.start()
    n=n+1
    
    