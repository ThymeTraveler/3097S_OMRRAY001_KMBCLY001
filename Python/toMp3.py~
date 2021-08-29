import numpy as np
import wave

fileName = "bigInput.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C')

import soundfile as sf
sf.write('sound.wav', ArrayOfFloat, 48000)

#data, sampleRate = sf.read('sound.wav')

wav = 'sound.wav'
cmd = 'lame --preset standard %s' % wav
import subprocess
subprocess.call(cmd, shell=True)

#the commented out block below would be used for extracting the information from the mp3
import audio2numpy as a2n
x,sr=a2n.audio_from_file("sound.mp3")

for i in x:
    print(i)