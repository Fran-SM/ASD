import socket

HOST = "0.0.0.0"
PORT = 11111

usuarios = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

print("Broker escuchando en el puerto", PORT)

while True:

    conn, addr = s.accept()
    print("Cliente conectado desde", addr)

    datos = conn.recv(1024)

    if not datos:
        conn.close()
        continue

    peticion = datos.decode("utf-8").strip()
    print("Peticion recibida:", peticion)

    partes = peticion.split()

    respuesta = "ERROR\n"

    if len(partes) > 0:
        comando = partes[0]

        if comando == "JOIN":
            if len(partes) == 4:
                nick = partes[1]
                ip = partes[2]

                try:
                    puerto = int(partes[3])

                    if nick in usuarios:
                        respuesta = "ERROR\n"
                    else:
                        usuarios[nick] = (ip, puerto)
                        respuesta = "OK\n"

                except ValueError:
                    respuesta = "ERROR\n"

        elif comando == "LEAVE":
            if len(partes) == 2:
                nick = partes[1]

                if nick in usuarios:
                    del usuarios[nick]
                    respuesta = "OK\n"
                else:
                    respuesta = "ERROR\n"

        elif comando == "QUERY":
            if len(partes) == 2:
                nick = partes[1]

                if nick in usuarios:
                    ip, puerto = usuarios[nick]
                    respuesta = "OK " + ip + " " + str(puerto) + "\n"
                else:
                    respuesta = "ERROR\n"

    conn.sendall(respuesta.encode("utf-8"))

    print("Respuesta enviada:", respuesta.strip())
    print("Usuarios registrados:", usuarios)

    conn.close()