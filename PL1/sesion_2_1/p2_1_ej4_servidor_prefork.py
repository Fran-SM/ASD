import os
import sys
import socket

def dar_servicio(sd,addr):
    while True:
        print("El cliente ",addr," se a conectado :)")
        data = sd.recv(1024)
        if not data:
            print("El cliente ",addr," se a desconectado :(")
            print("Esperando cliente")
            break
        sd.sendall(data)
    sd.close()

HOST = "0.0.0.0"
PORT = int(sys.argv[1])

s = socket.socket()
print("Esperando cliente")
s.bind((HOST, PORT))
s.listen(10)
for _ in range(3):
    if os.fork() == 0:
        
        break
while True:
    
    sd, addr = s.accept()
    
    dar_servicio(sd,addr)

