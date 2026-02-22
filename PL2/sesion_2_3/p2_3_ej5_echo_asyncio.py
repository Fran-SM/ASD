import asyncio
import sys

HOST = "0.0.0.0"
DEFAULT_PORT = 7000


async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        while True:
            data = await reader.read(4096)  
            if not data:                    
                break
            if data:
                print("Recibidos", len(data), "bytes")
                writer.write(data)               
                await writer.drain()             
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    #port = DEFAULT_PORT
    port = int(sys.argv[1])

    server = await asyncio.start_server(handle_echo, HOST, port)

    print(f"Servidor escuchando en {port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())