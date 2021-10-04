import socket
import time
import numpy as np
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.200', 1616))
ArrayofString=[]


while True:
    full_msg = ''
    i=0
    while True:
        msg = s.recv(12)
        if len(msg) <= 0:
            break
        full_msg = msg.decode("ascii")

        if len(full_msg) > 0:
            ArrayofString.append(full_msg)
              
    break
print("data recieved")


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

import Encryption
with open("fftcompressed.out") as f:
    message = f.read()
    Encryption.encrypt_message(message)

import ftplib
session = ftplib.FTP('192.168.0.200','rayhaan2120@gmail.com','password')
file = open('encrypted.txt','rb')                  # file to send
session.storbinary('STOR encrypted.txt', file)     # send the file
file.close()                                    # close file and FTP
session.quit()