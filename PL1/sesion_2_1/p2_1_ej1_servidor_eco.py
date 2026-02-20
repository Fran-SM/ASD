import socket

s = socket.socket()
s.bind(("0.0.0.0", 7000))
s.listen(1)

while True:
    print("Esperando a cliente")
    conn, addr = s.accept()
    while True:
        print("Usuario: ",addr," se a conectado :)")
        data = conn.recv(1024)
        if not data:
            print("Usuario: ",addr," se a desconectado :(")
            break
        conn.sendall(data)
    conn.close()
