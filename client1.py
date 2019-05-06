import asyncio
import json

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 1234)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(4096)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

s = json.dumps({"method":"sendHeader","data": { \
		"block_hash": "00000f55c821fdd5d88b5a1071ec70064681ebef1ca7829500de95ba4dc33077", \
		"block_header" : "00000001000005f3aaef1c4ef5f896ce123d6124f88b863635872ab489985c69e62a53a40000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000348510", \
		"block_height" : "2" \
	}})


# asyncio.run(tcp_echo_client(s))
