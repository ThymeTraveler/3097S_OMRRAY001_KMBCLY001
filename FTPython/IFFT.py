import numpy as np

f = open("fftcompressed.out", "r") #open file for reading
Arrayoftest = f.read().splitlines() #enter file lines into array
Arrayofcomplex=np.array(eval(Arrayoftest[0]))
for I in range(1,len(Arrayoftest)):
    Arrayofcomplex=np.append(Arrayofcomplex,eval(Arrayoftest[I]))

zeroPadded=np.zeros(10000,dtype=complex)
midpoint=int(np.ceil(Arrayofcomplex.size/2.0))
zeroPadded[0:midpoint]=Arrayofcomplex[0:midpoint]
zeroPadded[10000-midpoint:10000]=Arrayofcomplex[midpoint:Arrayofcomplex.size]

output= np.fft.ifft(zeroPadded)
np.savetxt('ifft.out', output.real, fmt='%1.3f')  