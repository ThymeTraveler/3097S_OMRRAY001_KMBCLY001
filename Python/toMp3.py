import numpy as np
import wave

fileName = "input.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array

ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C')

import soundfile as sf
sf.write('sound.wav', ArrayOfFloat, 48000)

data, sampleRate = sf.read('sound.wav')

for I in data:
        print(I)