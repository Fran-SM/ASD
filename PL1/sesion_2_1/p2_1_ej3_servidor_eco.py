import socket
import sys

def dar_servicio(sd,addr):
    while True:
        print("El cliente ",addr," se a conectado :)")
        data = sd.recv(1024)
        if not data:
            print("El cliente ",addr," se a desconectado :(")
            break
        sd.sendall(data)
    sd.close()

puerto = int(sys.argv[1])

s = socket.socket()
s.bind(("0.0.0.0", puerto))
s.listen(1)

while True:
    print("Esperando cliente")
    sd, addr = s.accept()
    dar_servicio(sd,addr)
