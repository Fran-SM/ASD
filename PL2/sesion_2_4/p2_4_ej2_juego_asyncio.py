import asyncio
import random

HOST = '0.0.0.0'
PORT = 8888

async def jugar(reader, writer):
    writer.write("Bienvenido/a al juego. ¿Cómo te llamas?\n"
                 .encode("utf-8"))
    await writer.drain()

    nombre = (await reader.read(1024)).decode("utf-8").strip()
    
    numero = random.randint(1, 100)
    intentos = 0
    writer.write(f"Hola {nombre}, he pensado un numero entre 1 y 100.\n"
                .encode("utf-8"))
    await writer.drain()
    
    while True:
        writer.write(b"Adivina: ")
        await writer.drain()

        linea = (await reader.read(1024)).decode("utf-8").strip()
        if not linea: break
        
        try:
            intento = int(linea)
            intentos += 1
            
            if intento < numero:
                writer.write("Es mayor\n".encode("utf-8"))
                await writer.drain()
            elif intento > numero:
                writer.write("Es menor\n".encode("utf-8"))
                await writer.drain()
            else:
                writer.write(f"¡Acertaste, {nombre}! ¡En {intentos} intentos!\n".encode("utf-8"))
                await writer.drain()
                break
        except ValueError:
            writer.write("Por favor, introduce un numero\n".encode("utf-8"))
            await writer.drain()

    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(jugar, HOST, PORT)
    print(f"Servidor asyncio escuchando en {HOST}:{PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())