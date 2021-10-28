import demo2
import numpy as np
fileName = "rand10000.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array
ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C') #converts array from the line above to a numpy array of float

demo2.method1(ArrayOfFloat,"testFile")
