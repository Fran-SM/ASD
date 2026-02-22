import selectors
import socket

HOST = "0.0.0.0"
PORT1 = 7777 
PORT2 = 7778

sel = selectors.DefaultSelector()


def aceptar_conexiones_echo(key, mask):
    sock_listen = key.fileobj
    conn, addr = sock_listen.accept()
    print("Conectado (ECHO):", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=dar_servicio_echo)


def aceptar_conexiones_upper(key, mask):
    sock_listen = key.fileobj
    conn, addr = sock_listen.accept()
    print("Conectado (MAYUS):", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=dar_servicio_upper)


def dar_servicio_echo(key, mask):
    sock = key.fileobj
    datos = sock.recv(4096)
    if datos:
        print("Recibidos", len(datos), "bytes")
        sock.sendall(datos)
    else: # Datos = b''
        print("El cliente se ha desconectado :(")
        sel.unregister(sock)
        sock.close()


def dar_servicio_upper(key, mask):
    sock = key.fileobj
    datos = sock.recv(4096)
    if datos:
        datos = datos.decode("utf-8").upper().encode("utf-8")
        print("Recibidos", len(datos), "bytes")
        sock.sendall(datos)
    else: # Datos = b''
        print("El cliente se ha desconectado :(")
        sel.unregister(sock)
        sock.close()


def main():
    # Socket escucha 1 (echo)
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.bind((HOST, PORT1))
    s1.listen()
    s1.setblocking(False)

    # Socket escucha 2 (MAYUS)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.bind((HOST, PORT2))
    s2.listen()
    s2.setblocking(False)

    print(f"Servidor escuchando: ECHO en {PORT1} y MAYUS en {PORT2}")

    # Cada socket de escucha se asocia a SU callback aceptar_...
    sel.register(s1, selectors.EVENT_READ, data=aceptar_conexiones_echo)
    sel.register(s2, selectors.EVENT_READ, data=aceptar_conexiones_upper)

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
        sel.unregister(s1)
        sel.unregister(s2)
        s1.close()
        s2.close()
        sel.close()

if __name__ == "__main__":
    main()