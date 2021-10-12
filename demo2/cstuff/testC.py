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
                          shape=(10,))

begin=time.time()
result = getValues(c_int(10))
print(result)
print(str(time.time()-begin))

# After testing this yields no noticable improvement. There does seem to be a bug where the function doesn't return all the values but there is no need to fix
#the bug as using C provides no benefit and any further development would be a waste of time.