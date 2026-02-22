import socket
import threading
import sys
import queue
import time

def dar_servicio(sd, addr, thread_id):
    print("El cliente", addr, "se a conectado :) y lo esta antendiendo", thread_id)
    while True:
        data = sd.recv(1024)
        if not data:
            print("El Cliente", addr, "se a desconectado :( y lo estaba antendiendo", thread_id)
            break
        sd.sendall(data)
    sd.close()

def hilo_jefe(host, port, q):
    server = socket.socket() 
    server.bind((host, port))
    server.listen(10)

    print("Servidor escuchando en", port)

    while True:
        print("Esperando cliente...")
        sd, addr = server.accept()
        print("El cliente", addr, "se a conectado :)")
        q.put((sd, addr)) 
        print("Cliente", addr, "metido en cola")

def hilo_trabajador(q, thread_id):
    while True:
        print("Hilo trabajador", thread_id, "esperando trabajo...")
        sd, addr = q.get()
        print("Hilo trabajador", thread_id, "ya tiene trabajo")
        dar_servicio(sd, addr, thread_id)

num_workers = int(sys.argv[1])
port = int(sys.argv[2])

q = queue.Queue(num_workers)  

jefe_thread = threading.Thread(target=hilo_jefe, args=("0.0.0.0", port, q))
jefe_thread.start()

for i in range(1, num_workers + 1):
    trabajador = threading.Thread(target=hilo_trabajador, args=(q, i))
    trabajador.start()

while True:
    time.sleep(60)