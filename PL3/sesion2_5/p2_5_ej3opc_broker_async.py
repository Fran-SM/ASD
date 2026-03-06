import asyncio

HOST = "0.0.0.0"
PORT = 11111
usuarios = {}


async def dar_servicio(reader, writer):

    data = await reader.read(1024)

    if not data:
        writer.close()
        await writer.wait_closed()
        return


    peticion = data.decode("utf-8").strip()
    print("Peticion recibida:", peticion)

  
    partes = peticion.split()

    # Respuesta por defecto
    respuesta = "ERROR\n"
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

    # Enviar respuesta al cliente
    writer.write(respuesta.encode("utf-8"))
    await writer.drain()

    print("Respuesta enviada:", respuesta.strip())
    print("Usuarios registrados:", usuarios)
    print("El cliente", addr, "se ha desconectado :(")

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(dar_servicio, HOST, PORT)

    print("Broker async escuchando en el puerto", PORT)

    async with server:
        await server.serve_forever()


asyncio.run(main())