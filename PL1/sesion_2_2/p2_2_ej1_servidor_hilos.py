import socket
import threading
import sys

def dar_servicio(sd, addr):
    nombre_hilo = threading.current_thread().name
    print("El cliente", addr, "se a conectado :) y lo esta antendiendo", nombre_hilo)

    while True:
        data = sd.recv(1024)
        if not data:
            print("El Cliente", addr, "se a desconectado :( y lo estaba antendiendo", nombre_hilo)
            break
        sd.sendall(data)

    sd.close()

def hilo_jefe(host, port):
    s = socket.socket()
    s.bind((host, port))
    s.listen(10)

    while True:
        print("Esperando cliente...")
        sd, addr = s.accept()
        th = threading.Thread(target=dar_servicio, args=(sd, addr))
        th.start()

PORT = int(sys.argv[1])
jefe = threading.Thread(target=hilo_jefe, args=("0.0.0.0", PORT))
jefe.start()
