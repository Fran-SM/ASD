import socket
import select
import sys


HOST = "0.0.0.0"
PORT = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(False)  # para que no se bloquee
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)
print(f"Servidor select escuchando en puerto {PORT}")

esperando_leer = [s]  # lista de sockets para leer

try:
    while True:
        listos_leer, _, _ = select.select(esperando_leer, [], [])

        for s in listos_leer:  # recorremos los sockets listos
            if s is esperando_leer[0]:  # comprobamos el pasivo sin usar índices
                conn, addr = s.accept()
                print(f"El cliente {addr} se ha conectado :)")
                conn.setblocking(False)
                esperando_leer.append(conn)
            else:
                # socket de datos existente
                try:
                    datos = s.recv(4096)
                except ConnectionResetError:
                    datos = b""

                if datos:
                    # eco
                    s.sendall(datos)
                else:
                    # conexión cerrada por el cliente
                    try:
                        peer = s.getpeername()
                    except OSError:
                        peer = '<desconocido>'
                    print(f"Cliente desconectado {peer}")
                    esperando_leer.remove(s)
                    s.close()
except KeyboardInterrupt:
    print("\nServidor cerrando...")
finally:

    for s in esperando_leer:
        s.close()


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
                print("El cliente", addr, "se ha conectado :) | Clientes activos:", len(esperando_leer))  
                conn.setblocking(False)
                esperando_leer.append(conn)

            else:
                datos = sock.recv(4096)

                if datos:
                    sock.sendall(datos)
                else: # Datos = b''
                    print("El cliente se ha desconectado :(| Clientes activos:", len(esperando_leer) - 1)
                    esperando_leer.remove(sock)
                    sock.close()

except KeyboardInterrupt:
    print("\nServidor cerrando...")

finally:
    for sock in esperando_leer:
        sock.close()
