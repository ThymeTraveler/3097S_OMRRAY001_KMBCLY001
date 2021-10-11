import numpy as np
import wave
import time


def compress(ArrayofString):


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


    print("MP3 time: "+str(time.time()-begin)+ " seconds") #end timer and print


def decompress(inputFile,outputFile):
    #the block below is used for extracting the information from the mp3
    import audio2numpy as a2n
    x,sr=a2n.audio_from_file(inputFile)
    np.savetxt(outputFile, x.real, fmt='%1.3f')  #outputs the uncompressed data to a file called ifft.out