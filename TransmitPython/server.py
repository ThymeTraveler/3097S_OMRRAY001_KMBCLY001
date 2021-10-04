import socket
import time
import numpy as np
fileName = "input.txt"
f = open(fileName, "r") #open file for reading
ArrayofString = f.read().splitlines() #enter file lines into array
ArrayOfFloat = np.asarray(ArrayofString, dtype=np.float64, order='C') #converts array from the line above to a numpy array of float

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('192.168.0.200', 1616))
serverSocket.listen(5) #queue for new connections

while True:
    # now our endpoint knows about the OTHER endpoint.
    clientsocket, address = serverSocket.accept()
    print(f"Connection from {address} has been established.")
    for I in range(len(ArrayofString)):
        clientsocket.send(bytes(f'{ArrayOfFloat[I]:+.9f}',"ascii"))
        print(f'{ArrayOfFloat[I]:+.9f}')
    clientsocket.close()
    break