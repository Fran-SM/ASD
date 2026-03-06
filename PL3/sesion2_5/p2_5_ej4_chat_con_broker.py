import asyncio
import sys

PUERTO_BROKER = 11111


class ChatProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        mensaje = data.decode().strip()
        print("\n" + mensaje, flush=True)


async def get_my_ip():

    _, writer = await asyncio.open_connection("8.8.8.8", 53)
    ip = writer.get_extra_info("sockname")[0]
    writer.close()
    await writer.wait_closed()

    return ip


async def hablar_con_broker(ip_broker, peticion):

    reader, writer = await asyncio.open_connection(ip_broker, PUERTO_BROKER)
    writer.write(peticion.encode("utf-8"))
    await writer.drain()
    data = await reader.read(1024)
    respuesta = data.decode("utf-8").strip()
    writer.close()
    await writer.wait_closed()

    return respuesta


async def shell_interactivo(transport, nick, ip_broker):
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_running_loop()

    # Conectar el teclado al bucle de eventos
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    destino = None

    while True:
        print("> ", end="", flush=True)

        # Esperamos una linea por teclado
        linea = await reader.readline()

        if not linea:
            continue

        # Pasamos de bytes a texto y quitamos espacios/saltos sobrantes
        linea = linea.decode().strip()

        if linea == "":
            continue

        if linea.startswith("/QUIT"):
            respuesta = await hablar_con_broker(ip_broker, "LEAVE " + nick + "\n")

            if respuesta == "OK":
                print("Cerrando chat...")
            else:
                print("No se pudo borrar el nick del broker")

            break

        elif linea.startswith("/CONNECT"):
            vectorEntrada = linea.split()


            if len(vectorEntrada) != 2:
                print("Uso correcto: /CONNECT <nick>")
                continue

            nick_destino = vectorEntrada[1]

            respuesta = await hablar_con_broker(ip_broker, "QUERY " + nick_destino + "\n")

            if respuesta == "ERROR":
                print("Ese usuario no esta registrado")
            else:
                partes = respuesta.split()

                # Debe venir: OK ip puerto
                if len(partes) == 3 and partes[0] == "OK":
                    ip_destino = partes[1]
                    puerto_destino = int(partes[2])

                    destino = (ip_destino, puerto_destino)
                    print("Conectado al nick", nick_destino, "en", destino)
                else:
                    print("Respuesta invalida del broker")

        l
        else:
            if destino is None:
                print("No hay destino seleccionado. Usa /CONNECT <nick>")
                continue

            mensaje = "(" + nick + ") > " + linea

            
            transport.sendto(mensaje.encode("utf-8"), destino)


async def main():

    nick = sys.argv[1]
    ip_broker = sys.argv[2]

    loop = asyncio.get_running_loop()

    # Crear endpoint UDP en puerto 0 para que el sistema elija uno libre
    transport, _ = await loop.create_datagram_endpoint(
        ChatProtocol,
        local_addr=("0.0.0.0", 0)
    )

    puerto_local = transport.get_extra_info("sockname")[1]
    ip_local = await get_my_ip()

    print("Mi IP es", ip_local)
    print("Mi puerto UDP es", puerto_local)

    peticion_join = "JOIN " + nick + " " + ip_local + " " + str(puerto_local) + "\n"
    respuesta = await hablar_con_broker(ip_broker, peticion_join)

    if respuesta == "ERROR":
        print("El nick que has elegido ya esta en uso")
        transport.close()
        sys.exit(1)

    if respuesta != "OK":
        print("Respuesta inesperada del broker:", respuesta)
        transport.close()
        sys.exit(1)

    print("Chat iniciado como", nick)
    print("Registrado correctamente en el broker", ip_broker)
    print("Usa /CONNECT <nick> para elegir destinatario")
    print("Usa /QUIT para salir")

    try:
        await shell_interactivo(transport, nick, ip_broker)
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())