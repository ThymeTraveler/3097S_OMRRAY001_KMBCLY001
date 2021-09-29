import numpy as np

#the block below is used for extracting the information from the mp3
import audio2numpy as a2n
x,sr=a2n.audio_from_file("sound.mp3")

for i in x:
     print(i)