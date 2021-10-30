import AESstuff,Fernetstuff,FFTstuff,FTPstuff,FTPstuff,ICM20948,MP3stuff
import threading,time, numpy as np
from datetime import datetime
n=1

def testCSV(axes,acc,gyro):
    import csv
    with open('input.csv', 'w') as csvfile:
        fieldnames = ['pitch', 'roll','yaw','Ax','Ay','Az','Gx','Gy','Gz']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        numValues=int(len(acc)/3)
        for i in range(numValues):
            writer.writerow({'pitch':axes[i], 'roll':axes[i+numValues],'yaw':axes[i+2*numValues],'Ax': acc[i],'Ay':acc[i+numValues],'Az':acc[i+2*numValues],'Gx': gyro[i],'Gy':gyro[i+numValues],'Gz':gyro[i+2*numValues]})
    FTPstuff.send("input.csv")

def method1(input,type):
    
    normalisingFactor = np.abs(input).max()  #normalising factor so that all values are between -1 and 1
    normal_array = input/normalisingFactor #normalising the array by dividing my the factor
    begin=time.time()
    MP3stuff.compress(normal_array,type) #compress using mp3 method
    print("compression took " + str(time.time()-begin))
    now = datetime.now() # Get the date and time for unique file name
    dt_string = now.strftime("%d-%m-%Y-%H-%M") # format date time string
    filenameNoExt=dt_string+"_"+str(n)+"_"+type +"_"+str(normalisingFactor)+"_"#file name is date-time_normalisingFactor_batchNo_sensorType
    begin=time.time()
    AESstuff.encryptFile(type+".mp3","password",filenameNoExt) #Encrypt mp3 using AES
    print("encryption took " + str(time.time()-begin))
    FTPstuff.send(filenameNoExt+".enc") # send encrypted file over FTP
   
    
    

if __name__ == '__main__':
    running =True
    batchSize=int(input("Please enter the batch size: "))
    while running:
        begin=time.time() #start time
        values1,values2,values3=ICM20948.getValues(batchSize) # get values from IMU
        print("Data acquistion took " + str(time.time()-begin)) #print time taken for data acquisition
        testCSV(values1,values2,values3) #send input values to FTP server in a csv file
        AESstuff.removeEncryptedFiles() #delete temp files from prev loop
        begin=time.time()
        x = threading.Thread(target=method1, args=(values1,"axes",)) #send each sensor's data to a different thread to be compressed
        x.start()
        y = threading.Thread(target=method1, args=(values2,"acc",))
        y.start()
        z = threading.Thread(target=method1, args=(values3,"gyro",))
        z.start()
        n=n+1 #increment batch number for this run

        x.join()#remove these joins if you want to continue collecting data during compression and encryption 
        y.join() #these joins are only useful for timing purposes 
        z.join()
        print("TOTAL compression + encryption + transmission took " + str(time.time()-begin))#will not work correctly without the joins
        running=False #remove this to collect data indefinitely
    