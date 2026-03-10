import selectors
import socket
import sys

HOST = "0.0.0.0"
PORT = 7000

sel = selectors.DefaultSelector()

def aceptar_conexion(sock_pasivo, mask):
    conn, addr = sock_pasivo.accept()
    print(f"[*] Nuevo cliente conectado desde {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=difundir_mensaje)

def difundir_mensaje(sock_emisor, mask):
    try:
        datos = sock_emisor.recv(4096)
        
        if datos:
            print(f"[>] Difundiendo {len(datos)} bytes de {sock_emisor.getpeername()}")
        
            for key in sel.get_map().values():
                destinatario = key.fileobj

                if key.data == difundir_mensaje:
                    try:
                        destinatario.sendall(datos)
                    except Exception as e:
                        print(f"[!] Error enviando a un cliente: {e}")
        
        else:
            print(f"[*] Cliente {sock_emisor.getpeername()} desconectado.")
            sel.unregister(sock_emisor)
            sock_emisor.close()
            
    except ConnectionResetError:
        sel.unregister(sock_emisor)
        sock_emisor.close()

def main():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    lsock.bind((HOST, PORT))
    lsock.listen(10)
    
    # Registramos el socket pasivo con el callback de aceptar
    sel.register(lsock, selectors.EVENT_READ, data=aceptar_conexion)

    try:
        while True:
            eventos = sel.select(timeout=None)
            for key, mask in eventos:
                callback = key.data
                callback(key.fileobj, mask)
    except KeyboardInterrupt:
        print("\nApagando servidor...")
    finally:
        sel.close()

if __name__ == "__main__":
    main()