import pickle

def pack(method, value):
    return pickle.dumps({
        "method": method,
        "value": value,
    })

def unpack(packet):
    return pickle.loads(packet)

class Broadcast:
    def __init__(self, server):
        self.s = server
    
    # n is a online neighbor
    def hello(self, p2p_sock):
        p2p_sock.settimeout(5)
        p2p_sock.send(pack(
            "hello",
            "hello from " + str(self.s.port)
        ))
        recv = p2p_sock.recv(1024)
        if recv:
            print(unpack(recv))

class Response:
    def __init__(self, server):
        self.s = server
    
    def echo(self, sock, data):
        sock.send(pack('', str(self.s.port)))
        # don't close sock
    
    def router(self, sock, data):
        print(data)
        if data['method'] == 'sayHello':
            self.echo(sock, data)
        else:
            pass