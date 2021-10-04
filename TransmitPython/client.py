import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.200', 1616))
ArrayofString=[]


while True:
    full_msg = ''
    i=0
    while True:
        msg = s.recv(12)
        if len(msg) <= 0:
            break
        full_msg = msg.decode("ascii")

        if len(full_msg) > 0:
            ArrayofString.append(full_msg)
              
    break
print("done")

