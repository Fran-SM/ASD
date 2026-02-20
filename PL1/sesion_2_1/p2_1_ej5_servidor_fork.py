import socket
import sys
import os
import signal

def dar_servicio(sd,addr):
    while True:
        print("El cliente ",addr," se a conectado :)")
        data = sd.recv(1024)
        if not data:
            print("El cliente ", addr," se ha desconectado :(")
            break
        sd.sendall(data)
    sd.close()

HOST = "0.0.0.0"
PORT = int(sys.argv[1])



signal.signal(signal.SIGCHLD, signal.SIG_IGN)



s = socket.socket()

s.bind((HOST, PORT))
s.listen(10)

while True:
    print("Esperando cliente")
    sd, addr = s.accept()
    pid = os.fork()

    if pid == 0:
        s.close()
        dar_servicio(sd,addr)
        sys.exit(0)
    else:
        sd.close()
