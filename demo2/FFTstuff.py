import numpy as np
import time

def compress(ArrayofString,outputFile):


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

    np.savetxt(outputFile, LPFCompressed, delimiter=',',fmt='%1.3f')   #save output file
    #np.savetxt('og.out', ArrayOfFloat, delimiter=',')  #used to debug - to check if the ArrayOfFloat is a problem

    print("FFT compression time: "+str(time.time()-begin)+ " seconds") #end timer and print

def decompress(inputfile,outputFile):
    FFTPercent=26
    f = open(inputFile, "r") #open file for reading
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
    np.savetxt(outputFile, output.real, fmt='%1.3f')  #outputs the uncompressed data to a file called ifft.out


