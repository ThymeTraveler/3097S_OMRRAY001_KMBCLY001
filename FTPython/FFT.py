import numpy as np
import time

fileName = "rand10000.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

#begin timing after intial file load in (as to only measure speed of algorithim)
begin=time.time()

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C')

transformed = np.fft.fft(ArrayOfFloat)
n = transformed.size
filter = np.zeros(n)
filterStartpercent=0.0
filterStopPercent=13.0
filterStart=int(np.ceil((filterStartpercent/100)*n))
filterStop=int(np.ceil((filterStopPercent/100)*n))
LPFCompressed=np.array(transformed[filterStart:filterStop])
LPFCompressed=np.append(LPFCompressed,transformed[n-filterStop:n-filterStart])

np.savetxt('fftcompressed.out', LPFCompressed, delimiter=',',fmt='%1.3f')   
#np.savetxt('og.out', ArrayOfFloat, delimiter=',')  #used to debug - to check if the ArrayOfFloat is a problem

print(str(time.time()-begin)+ " seconds") #end timer and print




