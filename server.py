import asyncio
import json

import api
import store


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handle_echo(self, reader, writer):
        data = reader.read(4096)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        # print(message)
        req = json.loads(message)
        method = req['method']
        value = req['value']


        if method == "sendHeader":
            error = api.sendHeader_receive(value)
            data = {"error": error}
        else:
            if method == "getBlocks":
                error, result = api.getBlocks_receive(value)
            elif method == "getBlockCount":
                error, result = api.getBlockCount_receive()
            elif method == "getBlockHash":
                error, result = api.getBlockHash_receive(value)
            elif method == "getBlockHeader":
                error, result = api.getBlockHeader_receive(value)
            else:
                error = 1
                result = f'Error: invalid method "{method}".'

            data = {"error": error, "result": result}

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        writer.drain()

        print("Close the connection")
        writer.close()

    async def main(self):
        # server = await asyncio.start_server(
        #     self.handle_echo, self.host, self.port)

        # addr = server.sockets[0].getsockname()
        # print(f'Serving on {addr}')

        # async with server:
        # await server.serve_forever()
        
        server = await loop.create_server(self.handle_echo, self.host, self.port)
        # addr = server.sockets[0].getsockname()

        print(f'Serving on {self.host}:{self.port}')
        # loop.run_until_complete(server)
        loop.run_until_complete(asyncio.wait(server))

# asyncio.run(main())