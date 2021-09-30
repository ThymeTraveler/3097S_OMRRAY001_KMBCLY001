import numpy as np
import time

fileName = "mp3sin.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

#begin timing after intial file load in (as to only measure speed of algorithim)
begin=time.time()

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C') #converts items to a numpy array of float

transformed = np.fft.fft(ArrayOfFloat) #applies fft to array of float




np.savetxt("mp3sinFFT.txt", transformed, delimiter=',',fmt='%1.3f')   #save output file
#np.savetxt('og.out', ArrayOfFloat, delimiter=',')  #used to debug - to check if the ArrayOfFloat is a problem






