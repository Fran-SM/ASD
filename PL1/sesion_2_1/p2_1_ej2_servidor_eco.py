import socket
import sys

puerto = int(sys.argv[1])

s = socket.socket()
s.bind(("0.0.0.0", puerto))
s.listen(1)

while True:
    print("Esperando a cliente")
    conn, addr = s.accept()
    while True:
        print("El cliente ", addr," se a conectado :)")
        data = conn.recv(1024)
        if not data:
            print("El cliente ", addr," se a desconectado :(")
            break
        conn.sendall(data)
    conn.close()