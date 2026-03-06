# p2_5_ej1_chat_async.py

import asyncio
import sys


class ChatProtocol(asyncio.DatagramProtocol):
    # Esta funcion se ejecuta automaticamente cuando llega un datagrama UDP
    def datagram_received(self, data, addr):
        try:
            mensaje = data.decode().strip()
            print("\n" + mensaje, flush=True)
        except:
            print("\n[ERROR] No se pudo decodificar el mensaje recibido", flush=True)


async def shell_interactivo(transport, nick):

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_running_loop()

    # Conectar el teclado al bucle de eventos
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    # Aqui guardamos la IP y puerto del destinatario actual
    destino = None

    while True:
        print("> ", end="", flush=True)

        # Esperamos una linea por teclado
        linea = await reader.readline()

        # Si no llega nada, seguimos esperando
        if not linea:
            continue

        # Pasamos de bytes a texto y quitamos espacios/saltos sobrantes
        linea = linea.decode().strip()

        # Si el usuario solo pulsa ENTER, no hacemos nada
        if linea == "":
            continue

        # Si la linea empieza por /QUIT, terminamos el programa
        if linea.startswith("/QUIT"):
            print("Cerrando chat...")
            break

        # Si la linea empieza por /CONNECT, cambiamos el destino activo
        elif linea.startswith("/CONNECT"):
            vectorEntrada = linea.split()

            # Comprobamos que haya 3 partes:
            # /CONNECT ip puerto
            if len(vectorEntrada) != 3:
                print("Uso correcto: /CONNECT <ip> <puerto>")
                continue

            ip_destino = vectorEntrada[1]

            try:
                puerto_destino = int(vectorEntrada[2])
            except ValueError:
                print("El puerto debe ser un numero entero")
                continue

            destino = (ip_destino, puerto_destino)
            print("Conectado al destino", destino)

        # Si no es un comando especial, se trata como mensaje normal
        else:
            # Si no hay destino, no se puede enviar
            if destino is None:
                print("No hay destino seleccionado. Usa /CONNECT <ip> <puerto>")
                continue

            mensaje = "(" + nick + ") > " + linea

            # Enviar por UDP al destino actual
            transport.sendto(mensaje.encode(), destino)


async def main():
    # Comprobar argumentos de linea de comandos
    if len(sys.argv) != 3:
        print("Uso: python3 p2_5_ej1_chat_async.py <nick> <puerto>")
        sys.exit(1)

    nick = sys.argv[1]

    try:
        puerto_local = int(sys.argv[2])
    except ValueError:
        print("El puerto local debe ser un numero entero")
        sys.exit(1)

    loop = asyncio.get_running_loop()

    # Crear el endpoint UDP que escuchara en todas las interfaces
    transport, _ = await loop.create_datagram_endpoint(
        ChatProtocol,
        local_addr=("0.0.0.0", puerto_local)
    )

    print("Chat iniciado como", nick)
    print("Escuchando en UDP en el puerto", puerto_local)
    print("Usa /CONNECT <ip> <puerto> para elegir destinatario")
    print("Usa /QUIT para salir")

    try:
        # Lanzamos el shell interactivo
        await shell_interactivo(transport, nick)
    finally:
        # Cerrar el socket UDP al terminar
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())