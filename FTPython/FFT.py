import numpy as np

fileName = "rand2000.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C')

transformed = np.fft.fft(ArrayOfFloat)
n = transformed.size
filter = np.zeros(n)
filterStartpercent=0.0
filterStopPercent=13.0
filterStart=int(np.ceil((filterStartpercent/100)*n))
filterStop=int(np.ceil((filterStopPercent/100)*n))
#filter[:,:,filterStart,filterStop] = 1.0
#filter[:,:,n-filterStart,n-filterStop]=1.0
#filter[filterStart:filterStop]=1.0
#filter[n-filterStop:n-filterStart]=1.0
LPFCompressed=np.array(transformed[filterStart:filterStop])
#LPFCompressed.append(transformed[n-filterStop:n-filterStart])
LPFCompressed=np.append(LPFCompressed,transformed[n-filterStop:n-filterStart])

np.savetxt('test.out', LPFCompressed, delimiter=',')   
np.savetxt('og.out', transformed, delimiter=',')  




