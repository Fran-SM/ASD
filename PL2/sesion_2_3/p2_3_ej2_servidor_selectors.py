import selectors
import socket
import sys

def aceptar_conexiones(key, mask):
    sock = key.fileobj
    conn, addr = sock.accept() 
    print("El cliente ", addr, "se ha conectado :)")  
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=dar_servicio)

def dar_servicio(key, mask):
    sock = key.fileobj
    datos = sock.recv(4096)

    if datos:
        print("Recibidos", len(datos), "bytes")
        sock.sendall(datos)
    else: # Datos = b''
        print("El cliente se ha desconectado :(")
        sel.unregister(sock)
        sock.close()
def main():
    sel = selectors.DefaultSelector()
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(False)
    s.bind((HOST, PORT))
    s.listen(10)

    print("Servidor selectors escuchando en puerto", PORT)
    sel.register(s, selectors.EVENT_READ, data=aceptar_conexiones)

    try:
        while True:
            if not sel.get_map(): break # Salir cuando no queden sockets
            eventos = sel.select()
            for key, mask in eventos:
                callback = key.data
                callback(key, mask)

    except KeyboardInterrupt:
        print("\nServidor cerrando...")
    finally:
        sel.unregister(s)
        s.close()
        sel.close()
if __name__ == "__main__":
    main()