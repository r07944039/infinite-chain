import pickle
import socket

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
    def hello(self, n):
        try:
            n.p2p_sock.settimeout(5)
            n.p2p_sock.send(pack(
                "hello",
                "hello from " + str(self.s.port)
            ))
            recv = n.p2p_sock.recv(1024)
            # if recv:
            #     print(unpack(recv))
        except socket.error as err:
            # DEBUG
            print(" offline: ", n.host, n.p2p_port, ": ", err)
            n.p2p_sock = None
            n.online = False

class Response:
    def __init__(self, server):
        self.s = server
    
    def echo(self, sock, data):
        sock.send(pack('', str(self.s.port)))
        # don't close sock
    
    def router(self, sock, data):
        # print('recv:', data)
        if data['method'] == 'hello':
            self.echo(sock, data)
        else:
            pass