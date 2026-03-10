import selectors
import socket
import random

HOST = '0.0.0.0'
PORT = 8888

sel = selectors.DefaultSelector()

# Definimos los estados posibles
ESTADO_NOMBRE = 1
ESTADO_ADIVINANDO = 2

class EstadoCliente:
    """Clase para guardar el estado individual de cada jugador."""
    def __init__(self):
        self.nombre = None
        self.numero = random.randint(1, 100)
        self.intentos = 0
        self.fase = ESTADO_NOMBRE

def aceptar_conexion(sock_pasivo, mask):
    conn, addr = sock_pasivo.accept()
    print(f"[*] Nuevo jugador desde {addr}")
    estado = EstadoCliente()
    conn.sendall("Bienvenido/a al juego. ¿Cómo te llamas?\n".encode("utf-8"))
    sel.register(conn, selectors.EVENT_READ, data=estado)

def dar_servicio(sock, mask):
    estado = sel.get_key(sock).data
    
    try:
        datos = sock.recv(1024)
        if not datos:
            raise ConnectionError()
        
        linea = datos.decode("utf-8").strip()
        
        # MÁQUINA DE ESTADOS
        if estado.fase == ESTADO_NOMBRE:
            estado.nombre = linea
            msg = f"Hola {estado.nombre}, he pensado un numero entre 1 y 100.\nAdivina: "
            sock.sendall(msg.encode("utf-8"))
            estado.fase = ESTADO_ADIVINANDO
            
        elif estado.fase == ESTADO_ADIVINANDO:
            try:
                intento = int(linea)
                estado.intentos += 1
                
                if intento < estado.numero:
                    sock.sendall("Es mayor\nAdivina: ".encode("utf-8"))
                elif intento > estado.numero:
                    sock.sendall("Es menor\nAdivina: ".encode("utf-8"))
                else:
                    msg = f"¡Acertaste, {estado.nombre}! ¡En {estado.intentos} intentos!\n"
                    sock.sendall(msg.encode("utf-8"))
                    print(f"[*] {estado.nombre} ha ganado.")
                    sel.unregister(sock)
                    sock.close()
            except ValueError:
                sock.sendall("Por favor, introduce un numero\nAdivina: ".encode("utf-8"))
                
    except (ConnectionError, Exception):
        print("[*] Cliente desconectado.")
        sel.unregister(sock)
        sock.close()

def main():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen(10)
    lsock.setblocking(False)
    
    sel.register(lsock, selectors.EVENT_READ, data=None)
    
    print(f"Servidor de Juego (Selectors) escuchando en {PORT}...")

    try:
        while True:
            eventos = sel.select()
            for key, mask in eventos:
                if key.data is None:
                    aceptar_conexion(key.fileobj, mask)
                else:
                    dar_servicio(key.fileobj, mask)
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
    finally:
        sel.close()

if __name__ == "__main__":
    main()