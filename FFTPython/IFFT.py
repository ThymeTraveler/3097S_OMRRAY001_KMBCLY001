import numpy as np
FFTPercent=26
f = open("fftcompressed.out", "r") #open file for reading
Arrayoftest = f.read().splitlines() #enter file lines into array

#creates numpy array of floats from python array of strings
Arrayofcomplex=np.array(eval(Arrayoftest[0])) 
for I in range(1,len(Arrayoftest)):
    Arrayofcomplex=np.append(Arrayofcomplex,eval(Arrayoftest[I]))

No_items=int(ceil(len(Arrayoftest)*(100/FFTPercent))) #calculates the number of items that should be in the orignal uncompressed file


zeroPadded=np.zeros(No_items,dtype=complex) #array of zeros for zeropadding
midpoint=int(np.ceil(Arrayofcomplex.size/2.0)) #find the midpoint of the input array
zeroPadded[0:midpoint]=Arrayofcomplex[0:midpoint] #Fills the positive freq components into the array with zeros
zeroPadded[No_items-midpoint:No_items]=Arrayofcomplex[midpoint:Arrayofcomplex.size] #fills the negative freq components in

output= np.fft.ifft(zeroPadded) #applies IFFT to the zeropadded array
np.savetxt('ifft.out', output.real, fmt='%1.3f')  #outputs the uncompressed data to a file called ifft.out