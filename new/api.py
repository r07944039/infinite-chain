import pickle
import socket

def pack(method, value):
    return pickle.dumps({
        "method": method,
        "value": value,
    })

def unpack(packet):
    return pickle.loads(packet)

def header_to_items(header):
    prev_block = header[8:72]
    target = header[-72:-8]
    nonce = header[-8:]

    return prev_block, target, nonce

def verify_hash(block_hash, block_header):
    error = 0
    if sha256(block_header) != block_hash:
        error = 1
    return error


def verify_prev_block(prev_block):
    error = 0
    pre_block_hash = store.node.chain[-1].block_hash
    if prev_block != pre_block_hash:
        error = 1
    return error


def verify_height(new_height):
    error = 0
    cur_height = store.node.height

    if cur_height != int(new_height) - 1:
        error = 1
    return error

def verify_shorter(new_height):
    cur_height = store.node.height

    if cur_height >= int(new_height):
        error = 1
    return error 

class Broadcast:
    def __init__(self, server):
        self.s = server

    # def sendHeader(self, n, block_hash, block_header, block_height):
    #     try:
    #         d = json.dumps({
    #             'block_hash': block_hash,
    #             'block_header': block_header,
    #             'block_height': block_height
    #         })
    #         n.p2p_sock.settimeout(5)
    #         n.p2p_sock.send(pack(
    #             "sendHeader",
    #             d
    #         ))
    #         recv = n.p2p_sock.recv(4096)
    #         if recv:
    #             r = unpack(recv)
    #             block_hash = r['block_hash']
    #             block_header = r['block_header']
    #             block_height = r['block_height']
    #             prev_block, target, nonce = header_to_items(block_header)
                
    #             need_getBlocks = False

    #             if verify_shorter(block_height):
    #                 # drop and triger sendHeader back
    #                 error = 1
    #                 return error    
    #             if verify_height(block_height):
    #                 need_getBlocks = True
    #             if verify_prev_block(prev_block):
    #                 need_getBlocks = True
    #             if verify_hash(block_hash, block_header):
    #                 # 只是本人 hash 值不對，感覺可以直接 drop 掉
    #                 error = 1
    #                 return error

    def getBlockCount(self, n, arg):
        try:
            n.p2p_sock.settimeout(5)
            n.p2p_sock.send(pack(
                'sendBlockCount'
            ))
            recv = n.p2p_sock.recv(4096)
            if recv:
                print(unpack(recv))
        except socket.error as err:
            # DEBUG
            print("offline: ", n.host, n.p2p_port, ": ", err)
            n.p2p_sock = None
            n.online = False

    
    # n is a online neighbor
    def hello(self, n, arg):
        try:
            n.p2p_sock.settimeout(5)
            n.p2p_sock.send(pack(
                "hello",
                "hello from " + str(self.s.port)
            ))
            recv = n.p2p_sock.recv(1024)
            if recv:
                print(unpack(recv))
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