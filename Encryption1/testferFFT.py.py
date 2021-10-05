
import numpy as np
import time

fileName = "rand10000.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

#begin timing after intial file load in (as to only measure speed of algorithim)
begin=time.time()
ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C') #converts items to a numpy array of float

transformed = np.fft.fft(ArrayOfFloat) #applies fft to array of float
n = transformed.size

#start and stop percentage of filter (the % of coeffecients maintained is 2x the difference between these two)
filterStartpercent=0.0
filterStopPercent=13.0

#Find the appropriate indexes for start and stop from the percentages
filterStart=int(np.ceil((filterStartpercent/100)*n))
filterStop=int(np.ceil((filterStopPercent/100)*n))

#Create a numpy array filled only with the items that fall within the specified start/stop ranges from the beginning and end of the fft array
LPFCompressed=np.array(transformed[filterStart:filterStop])
LPFCompressed=np.append(LPFCompressed,transformed[n-filterStop:n-filterStart])

np.savetxt('fftcompressed.out', LPFCompressed, delimiter=',',fmt='%1.3f')   #save output file
#np.savetxt('og.out', ArrayOfFloat, delimiter=',')  #used to debug - to check if the ArrayOfFloat is a problem

begin2=time.time()
import Encryption
with open("fftcompressed.out") as f:
    message = f.read()
    Encryption.encrypt_message(message)
print(str(time.time()-begin2)+ " seconds") #end timer and print

print("total: "+str(time.time()-begin)+ " seconds") #end timer and print