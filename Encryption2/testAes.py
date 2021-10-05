import numpy as np
import wave
import time



fileName = "rand10000.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

#begin timing after intial file load in (as to only measure speed of algorithim)
begin=time.time()

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C') #converts array from the line above to a numpy array of float

#this block writes the ArrayOfFloat to a .wav audio file (this is also )
import soundfile as sf
sf.write('sound.wav', ArrayOfFloat, 48000)

#This line below is used to extract the data in the .wav to an array - only useful for validation
#data, sampleRate = sf.read('sound.wav')

#This block converts the .wav file into an mp3 and applies the appropriate compression (uses BASH)
wav = 'sound.wav'
cmd = 'lame --preset standard %s' % wav
import subprocess
subprocess.call(cmd, shell=True)





import zz
from pathlib import Path
begin2=time.time()
zz.encryptFile(Path("sound.mp3"),"password")
print(str(time.time()-begin2)+ " seconds") #end timer and print

print("total: "+str(time.time()-begin)+ " seconds") #end timer and print