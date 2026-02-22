import socket
import select
import sys

HOST = "0.0.0.0"
PORT = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(False)
s.bind((HOST, PORT))
s.listen(10)

print("Servidor select escuchando en puerto", PORT)

esperando_leer = [s]

try:
    while True:
        listos_leer, _, _ = select.select(esperando_leer, [], [])

        for sock in listos_leer:
            if sock is s:
                conn, addr = s.accept()
                print("El cliente ", addr, "se ha conectado :)")  
                print("Clientes activos:", len(esperando_leer))
                conn.setblocking(False)
                esperando_leer.append(conn)

            else:
                datos = sock.recv(4096)

                if datos:
                    print("Recibidos", len(datos), "bytes")
                    sock.sendall(datos)
                else: # Datos = b''
                    print("El cliente se ha desconectado :(")
                    esperando_leer.remove(sock)
                    sock.close()
                    print("Clientes activos:", len(esperando_leer) - 1)

except KeyboardInterrupt:
    print("\nServidor cerrando...")

finally:
    for sock in esperando_leer:
        sock.close()
