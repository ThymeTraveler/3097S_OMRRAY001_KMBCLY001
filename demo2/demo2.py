import AESstuff,Fernetstuff,FFTstuff,FTPstuff,FTPstuff,ICM20948,MP3stuff
import threading,time, numpy as np
from datetime import datetime
n=1

def method1(input):
    global n
    normalisingFactor = np.linalg.norm(input)
    normal_array = input/normalisingFactor
    MP3stuff.compress(normal_array)
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M")
    filenameNoExt=dt_string+"_"+str(normalisingFactor)+"_"+str(n)
    AESstuff.encryptFile("sound.mp3","password",filenameNoExt)
    FTPstuff.send(filenameNoExt+".enc")
    print("n is "+str(n))
    


running =True

while running:
    begin=time.time()
    values1,values2,values3=ICM20948.getValues(100)
    print("Data acquistion took " + str(time.time()-begin))
    AESstuff.removeEncryptedFiles()
    x = threading.Thread(target=method1, args=(values1,))
    x.start()
    y = threading.Thread(target=method1, args=(values2,))
    y.start()
    z = threading.Thread(target=method1, args=(values3,))
    z.start()
    n=n+1
    
    