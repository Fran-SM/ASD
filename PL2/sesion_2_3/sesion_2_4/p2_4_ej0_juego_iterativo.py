import socket
import random

HOST = '0.0.0.0'
PORT = 8888

def jugar(conn):
    conn.sendall("Bienvenido/a al juego. ¿Cómo te llamas?\n"
                 .encode("utf-8"))
    # Leemos el nombre
    nombre = conn.recv(1024).decode("utf-8").strip()
    
    # Pensamos el número
    numero = random.randint(1, 100)
    intentos = 0
    conn.sendall(f"Hola {nombre}, he pensado un numero entre 1 y 100.\n"
                .encode("utf-8"))
    
    while True:
        conn.sendall(b"Adivina: ")
        linea = conn.recv(1024).decode("utf-8").strip()
        if not linea: break # Cliente desconectado
        
        try:
            intento = int(linea)
            intentos += 1
            
            if intento < numero:
                conn.sendall("Es mayor\n".encode("utf-8"))
            elif intento > numero:
                conn.sendall("Es menor\n".encode("utf-8"))
            else:
                conn.sendall(f"¡Acertaste, {nombre}! ¡En {intentos} intentos!\n".encode("utf-8"))
                break
        except ValueError:
            conn.sendall("Por favor, introduce un numero\n".encode("utf-8"))

def main():
    sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sp.bind((HOST, PORT))
    sp.listen(5)
    print(f"Servidor Iterativo escuchando en {HOST}:{PORT}")
    while True:
        sd, addr = sp.accept()
        print(f"Jugador conectado: {addr}")
        jugar(sd)
        sd.close()

if __name__ == "__main__":
    main()