import pickle
import socket
import hashlib
import json

from block.block import Block

def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

def _pack(data):
    d = json.dumps(data)
    return pickle.dumps(d)

def unpack(packet):
    d = pickle.loads(packet)
    return json.loads(d)

def _header_to_items(header):
    prev_block = header[8:72]
    target = header[-72:-8]
    nonce = header[-8:]

    return prev_block, target, nonce

def _verify_hash(block_hash, block_header):
    # error = 0
    if sha256(block_header) != block_hash:
        # error = 1
        return True
    return False


def _verify_prev_block(prev_block, chain):
    # error = 0
    pre_block_hash = chain[-1].block_hash
    if prev_block != pre_block_hash:
        # error = 1
        return True
    return False


def _verify_height(new_height, cur_height):
    # cur_height = node_height

    if cur_height != int(new_height) - 1:
        return True
    return False

def _verify_shorter(new_height, cur_height):
    error = 0
    # cur_height = node_height

    if cur_height >= int(new_height):
        error = 1
    return error 

class Broadcast:
    def __init__(self, server):
        self.s = server

    def sendHeader(self, n, arg):
        block_hash = arg['block_hash']
        block_header = arg['block_header']
        block_height = arg['block_height']

        d = json.dumps({
            'block_hash': block_hash,
            'block_header': block_header,
            'block_height': block_height
        })
        n.p2p_sock.settimeout(5)
        req = _pack({
            'method': 'sendHeader',
            'data': d
        })
        print(req)
        n.p2p_sock.send(req)
        recv = n.p2p_sock.recv(1024)
        if recv:
            r = unpack(recv)
            print(r)

    def getBlocks(self, n, arg):

        d = json.dumps({
            'hash_count': arg['hash_count'],
            'hash_begin': arg['hash_begin'],
            'hash_stop': arg['hash_stop']
        })
        req = _pack({
            'method': 'getBlocks',
            'data': d
        })
        print(req)
        n.p2p_sock.send(req)
        recv = n.p2p_sock.recv(1024)
        if recv:
            r = unpack(recv)
            print("sss: ", r)
            result = r['data']['result']
            if len(result) > 1:
                result = max(result[0], result[1])
                for header in result[1:]:
                    prev_block, target, nonce = _header_to_items(header)
                    new_block = Block(prev_block, target, nonce)
                    self.s.node.add_new_block(new_block)
    
    # n is a online neighbor
    def hello(self, n, arg):
        n.p2p_sock.settimeout(5)
        # n.p2p_sock.send(_pack({
        #     "method": "hello"
        #     "data": "hello from " + str(self.s.port)
        # }))
        recv = n.p2p_sock.recv(1024)
        if recv:
            print(unpack(recv))

class Response:
    def __init__(self, server):
        self.s = server

    def sendHeader(self, sock, data):
        block_hash = data['block_hash']
        block_header = data['block_header']
        block_height = data['block_height']
        prev_block, target, nonce = _header_to_items(block_header)
        
        need_getBlocks = False

        height = self.s.node.get_height()
        chain = self.s.node.get_chain()

        # drop and triger sendHeader back
        error =  _verify_shorter(block_height, height)
        if _verify_height(block_height, height):
            need_getBlocks = True
        if _verify_prev_block(prev_block, chain):
            need_getBlocks = True
            error = 1
        if _verify_hash(block_hash, block_header):
            # 只是本人 hash 值不對，感覺可以直接 drop 掉
            error = 1

        if need_getBlocks:
            cur_height = height
            cur_hash = chain[cur_height].block_hash
            hash_count = block_height - cur_height
            hash_begin = cur_hash
            hash_stop = block_hash
            # FIXME: 這邊要改
            arg = {
                'hash_count': hash_count, 
                'hash_begin': hash_begin, 
                'hash_stop': hash_stop
            }
            # self.s.broadcast(self.s.apib.getBlocks, arg)
            # error = getBlocks(hash_count, hash_begin, hash_stop)
            
        error = 0
        res = {
            'error': error
        }
        sock.send(_pack(res))

    def getBlocks(self, sock, data):
        hash_count = data['hash_count']
        hash_begin = data['hash_begin']
        hash_stop = data['hash_stop']

        # 先找到那個 block 再回 block headers list
        result = []
        count = 0
        append = 0

        chain = self.s.node.get_chain()

        # FIXME: 找不到助教範例裡面的 hash
        # Brute force QAQ
        for block in chain:
            # 到尾了
            if hash_stop == block.block_hash:
                append = 0
                continue
            if append == 1:
                result.append(block.block_hash)
            # 如果到 begin 的下一個開始計
            if hash_begin == block.block_hash:
                append = 1

        # debug(result)
        # 如果找不到結果就回傳錯誤
        if len(result) == 0:
            error = 1

        res = {
            'result': result,
            'error': error
        }
        sock.send(_pack({
            'method': 'getBlocks',
            'data': res
        }))

    def getBlockCount(self, sock):
        height = self.s.node.get_height()
        if height == 0:
            error = 1
        else:
            error = 0
        res = {
            'result': result,
            'error': error
        }
        sock.send(_pack({
            'method': 'getBlockCount',
            'data': res
        }))
    
    def echo(self, sock, data):
        print('echo')
        # sock.send(_pack('', str(self.s.port)))
        # don't close sock
    
    def router(self, sock, query):
        # print('recv:', data)
        method = query['method']
        if 'data' in query:
            data = json.loads(query['data'])
        if method == 'sendHeader':
            self.sendHeader(sock, data)
        elif method == 'getBlocks':
            self.getBlocks(sock, data)
        elif method == 'getBlockCount':
            self.getBlockCount(sock)
        elif method == 'hello':
            self.echo(sock, data)
        else:
            pass

# For user_port
class SendTo:
    def __init__(self, server):
        self.s = server

    def getBlockCount(self, n, arg):
        n.p2p_sock.settimeout(5)
        n.p2p_sock.send(_pack({
            'method': 'getBlockCount'
        }))
        recv = n.p2p_sock.recv(1024)
        if recv:
            print(unpack(recv))

    