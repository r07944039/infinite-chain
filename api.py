import pickle
import socket
import hashlib
import json
import globs

from block.block import Block

def create_sock(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(globs.RETRY_TIMEOUT)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        s.connect((host, port))
    except socket.error as err:
        print("create_sock: " + host + ":" + str(port), ": ", err)
        return None
    return s

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


def header_to_items(header):
    prev_block = header[8:72]
    transactions_hash = header[72:136]
    target = header[136:-136] # 64
    nonce = header[-136:-128] # 8
    beneficiary = header[-128:]

    return prev_block, transactions_hash, target, nonce, beneficiary


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
    if cur_height < int(new_height):
        return False
    return True

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
        req = _pack({
            'method': 'sendHeader',
            'data': d
        })
        print(req)
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return
        sock.send(req)
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            print(r)

    def getBlocks(self, n, arg):
        print(arg)

        d = json.dumps({
            'hash_count': arg['hash_count'],
            'hash_begin': arg['hash_begin'],
            'hash_stop': arg['hash_stop']
        })
        req = _pack({
            'method': 'getBlocks',
            'data': d
        })
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return
        sock.send(req)
        print(req)
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            result = r['result']
            if len(result) > 1:
                print(len(result))
                #result = max(result[0], result[1])
                # check for the branch 
                for header in result:
                    prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(header)
                    # FIXME: 因為 transactions 的部分還沒處理好，目前先直接寫死說每個都是空字串
                    new_block = Block(prev_block, transactions_hash, target, nonce, beneficiary, [])
                    self.s.node.add_new_block(new_block)

    # n is a online neighbor
    def hello(self, n, arg):
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return
        sock.send(_pack({
            "method": "hello",
            "data": "hello from " + str(self.s.port)
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print(unpack(recv))

# Response 的 sock 都不可以 sock.close()
# 不然還沒有 send 回去 socket 就被關掉
# 對方會收到 Connection reset by peers
# 且對方的 recv 會一直 block 直到 timed out
class Response:
    def __init__(self, server):
        self.s = server

    def sendHeader(self, sock, data):
        block_hash = data['block_hash']
        block_header = data['block_header']
        block_height = data['block_height']
        prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(block_header)

        need_getBlocks = False

        height = self.s.node.get_height()
        chain = self.s.node.get_chain()

        # drop and triger sendHeader back
        if _verify_shorter(block_height, height):
            pass

        else:

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
                self.s.broadcast(self.s.apib.getBlocks, arg)
        
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
                result.append(block.block_header.header)
                append = 0
                break
            if append == 1:
                result.append(block.block_header.header)
            # 如果到 begin 的下一個開始計
            if hash_begin == block.block_hash:
                append = 1
        # debug(result)
        # 如果找不到結果就回傳錯誤
        if len(result) == 0:
            error = 1
        else:
            error = 0
        res = {
            'result': result,
            'error': error
        }

        sock.send(_pack(res))

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

        sock.send(_pack(res))

    def getBlockHash(self, sock, data):
        height = data['block_height']
        if height > self.s.node.get_height():
            error = 1
            result = ""
        else:
            error = 0
            chain = self.s.node.get_chain()
            result = chain[height]

        res = {
            'error': error,
            'result': result
        }

        sock.send(_pack(res))

    def getBlockHeader(self, sock, data):
        block_hash = data['block_hash']
        chain = self.s.node.get_chain()
        for block in chain:
            header = block.block_header
            if block.block_hash == block_hash:
                result = {
                    "version": header.version,
                    "prev_block": header.prev_block,
                    "merkle_root": header.merkle_root,
                    "target": header.target,
                    "nonce": header.nonce
                }
                error = 0
            else:
                error = 1
                result = {}

        res = {
            'error': error,
            'result': result
        }

        sock.send(_pack(res))

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
        elif method == 'getBlockHash':
            self.getBlockHash(sock, data)
        elif method == 'getBlockHeader':
            self.getBlockHeader(sock, data)
        elif method == 'hello':
            self.echo(sock, data)
        else:
            pass

# For user_port
class SendTo:
    def __init__(self, server):
        self.s = server

    def getBlockCount(self, n, arg):
        sock = create_sock(n.host, n.user_port)
        if sock == None:
            return
        sock.send(_pack({
            'method': 'getBlockCount'
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print(unpack(recv))

    def getBlockHash(self, n, arg):
        sock = create_sock(n.host, n.user_port)
        if sock == None:
            return
        sock.send(_pack({
            'method': 'getBlockHash',
            'data': {
                'block_height': arg['block_height']
            }
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print(unpack(recv))

    def getBlockHeader(self, n, arg):
        height = self.s.node.get_height()
        chain = self.s.node.get_chain()

        sock = create_sock(n.host, n.user_port)
        if sock == None:
            return
        sock.send(_pack({
            'method': 'getBlockHeader',
            'data': {
                'block_hash': chain[height].block_hash
            }
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print(unpack(recv))
