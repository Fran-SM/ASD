import asyncio
import sys
from redis.asyncio import Redis

CLAVE_REDIS_USERS = "chat_p2p:users"
CANAL_EVENTOS = "chat_p2p:events"

class ChatProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        mensaje = data.decode().strip()
        print(f"\r{mensaje}\n> ", end="", flush=True)

async def get_my_ip():
    try:
        _, writer = await asyncio.open_connection("8.8.8.8", 53)
        ip = writer.get_extra_info("sockname")[0]
        writer.close()
        await writer.wait_closed()
        return ip
    except Exception:
        return "127.0.0.1"

async def oir_eventos_redis(ps):
    try:
        async for aviso in ps.listen():
            if aviso["type"] == "message":
                el_texto = aviso["data"]
                print(f"[INFO] {el_texto}")
    except asyncio.CancelledError:
        pass

async def registrar_en_redis(redis, nick, ip, puerto):
    existe = await redis.hexists(CLAVE_REDIS_USERS, nick)
    if existe:
        return False
    valor = f"{ip}:{puerto}"
    await redis.hset(CLAVE_REDIS_USERS, nick, valor)
    await redis.publish(CANAL_EVENTOS, f"¡EVENTO!: {nick} se ha unido al chat.")
    return True

async def borrar_de_redis(redis, nick):
    borrados = await redis.hdel(CLAVE_REDIS_USERS, nick)
    if borrados > 0:
        await redis.publish(CANAL_EVENTOS, f"¡EVENTO!: {nick} ha abandonado el chat.")
    return borrados > 0

async def consultar_usuario(redis, nick):
    valor = await redis.hget(CLAVE_REDIS_USERS, nick)
    if valor is None:
        return None
    ip, puerto = valor.rsplit(":", 1)
    return (ip, int(puerto))

async def shell_interactivo(transport, nick, redis):
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_running_loop()

    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    destino = None

    while True:
        print("> ", end="", flush=True)
        linea = await reader.readline()
        if not linea: break
        
        linea = linea.decode().strip()
        if not linea: continue

        if linea.startswith("/QUIT"):
            await borrar_de_redis(redis, nick)
            print("Cerrando chat...")
            break

        elif linea.startswith("/CONNECT"):
            partes = linea.split()
            if len(partes) != 2:
                print("Uso: /CONNECT <nick>")
                continue
            
            nick_destino = partes[1]
            datos = await consultar_usuario(redis, nick_destino)

            if datos:
                destino = datos
                print(f"Conectado a {nick_destino} en {destino}")
            else:
                print("Usuario no encontrado.")

        else:
            if destino:
                mensaje = f"({nick}) > {linea}"
                transport.sendto(mensaje.encode("utf-8"), destino)
            else:
                print("Usa /CONNECT <nick> primero.")

async def main():
    if len(sys.argv) < 3:
        print("Uso: python script.py <tu_nick> <ip_redis>")
        return

    nick = sys.argv[1]
    ip_redis = sys.argv[2]
    loop = asyncio.get_running_loop()
    
    # Crear endpoint UDP en puerto 0 para que el sistema elija uno libre
    transport, _ = await loop.create_datagram_endpoint(
        ChatProtocol, local_addr=("0.0.0.0", 0)
    )
    puerto_local = transport.get_extra_info("sockname")[1]
    ip_local = await get_my_ip()

    redis = Redis(host=ip_redis, port=6379, decode_responses=True)
    ps = redis.pubsub()
    await ps.subscribe(CANAL_EVENTOS)

    registrado = await registrar_en_redis(redis, nick, ip_local, puerto_local)
    if not registrado:
        print("Error: El nick ya está en uso.")
        transport.close()
        await redis.aclose()
        return

    tarea_eventos = asyncio.create_task(oir_eventos_redis(ps))

    print(f"--- Chat P2P con Redis Pub/Sub ---")
    print(f"Identidad: {nick} ({ip_local}:{puerto_local})")

    try:
        await shell_interactivo(transport, nick, redis)
    finally:
        tarea_eventos.cancel()
        await ps.unsubscribe(CANAL_EVENTOS)
        transport.close()
        await redis.aclose()

if __name__ == "__main__":
    asyncio.run(main())