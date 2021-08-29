import numpy

fileName = "input.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array


import soundfile as sf
sf.write('sound.wav', yourArray, 48000)