import asyncio
import sys
from redis.asyncio import Redis


CLAVE_REDIS = "chat_p2p:users"

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


async def registrar_en_redis(redis, nick, ip, puerto):
    existe = await redis.hexists(CLAVE_REDIS, nick)
    if existe:
        return False
    valor = ip + ":" + str(puerto)
    await redis.hset(CLAVE_REDIS, nick, valor)

    return True


async def borrar_de_redis(redis, nick):

    borrados = await redis.hdel(CLAVE_REDIS, nick)
    return borrados > 0


async def consultar_usuario(redis, nick):

    valor = await redis.hget(CLAVE_REDIS, nick)
    if valor is None:
        return None
    ip, puerto = valor.rsplit(":", 1)
    puerto = int(puerto)
    return (ip, puerto)

async def shell_interactivo(transport, nick, redis):
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
            borrado = await borrar_de_redis(redis, nick)

            if borrado:
                print("Cerrando chat...")
            else:
                print("No se pudo borrar el nick de Redis")

            break


        elif linea.startswith("/CONNECT"):
            vectorEntrada = linea.split()


            if len(vectorEntrada) != 2:
                print("Uso correcto: /CONNECT <nick>")
                continue

            nick_destino = vectorEntrada[1]

            datos = await consultar_usuario(redis, nick_destino)

            if datos is None:
                print("Ese usuario no esta registrado")
            else:
                destino = datos
                print("Conectado al nick", nick_destino, "en", destino)

        # Si no es un comando especial, es un mensaje normal
        else:
            if destino is None:
                print("No hay destino seleccionado. Usa /CONNECT <nick>")
                continue

            mensaje = "(" + nick + ") > " + linea

            # Enviar mensaje
            transport.sendto(mensaje.encode("utf-8"), destino)


async def main():

     nick = sys.argv[1]
    ip_redis = sys.argv[2]

    loop = asyncio.get_running_loop()

    # Crear endpoint UDP en puerto 0 para que el sistema elija uno libre
    transport, _ = await loop.create_datagram_endpoint(
        ChatProtocol,
        local_addr=("0.0.0.0", 0)
    )


    puerto_local = transport.get_extra_info("sockname")[1]
    ip_local = await get_my_ip()

 
    redis = Redis(host=ip_redis, port=6379, decode_responses=True)

    print("Mi IP es", ip_local)
    print("Mi puerto UDP es", puerto_local)


    registrado = await registrar_en_redis(redis, nick, ip_local, puerto_local)

    if not registrado:
        print("El nick que has elegido ya esta en uso")
        transport.close()
        await redis.aclose()
        sys.exit(1)

    print("Chat iniciado como", nick)
    print("Registrado correctamente en Redis", ip_redis)
    print("Usa /CONNECT <nick> para elegir destinatario")
    print("Usa /QUIT para salir")

    try:
        await shell_interactivo(transport, nick, redis)
    finally:
        transport.close()
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())