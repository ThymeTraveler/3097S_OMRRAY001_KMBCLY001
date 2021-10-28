from ctypes import *
from numpy.ctypeslib import ndpointer
import numpy as np
import time


import os.path
dll_name = "ICM20948.so"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
#myDll = ctypes.CDLL(dllabspath)


#load the compiled C library
lib = cdll.LoadLibrary(dllabspath)
getValues = lib.getValues 
getValues.restype = ndpointer(dtype=c_float,
                          shape=(200,))

begin=time.time()
result = getValues(c_int(200))
print(result)
print(str(time.time()-begin))

# After testing this yields a small improvement, not sure if 14% is worth it for our use case. Python is just easier to use, but I did put a lot of work into 
#getting this working