import pickle
import socket
import hashlib
import json
import globs
import os
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

from block.block import Block
from transaction import Transaction

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
    # return d


def unpack(packet):
    '''
        照以前的傳法 pickle 會噴錯
        pickle 是給 python socket 用的, 但是 JS 那邊沒有 pickle
        所以助教的 msg 會 unpack 失敗
        但我們送回去時還是得用 pickle

    '''
    # print(type(packet))

    # if type(packet) is bytes:
    #     packet = json.loads(pickle.loads(packet))
    # elif type(packet) is str:
    #     packet = packet.decode("utf-8")
    #     packet = json.loads(packet)

    # print(packet.decode("utf-8"))
    
    print(type(packet))
    print(packet)
    
    # print(type(packet))
    # if type(packet) is bytes:
    #     packet = packet.decode("utf-8")
    #     print(packet)
    # print(packet)
    # print(type(packet))
    # d = pickle.loads(packet)
    # return json.loads(d)
    # packet = json.loads(pickle.loads(packet))

    # 助教傳來的格式
    try:
        packet = json.loads(packet)
    # 我們自己 socket 的格式
    except:
        packet = json.loads(pickle.loads(packet))
    return packet


def header_to_items(header):
    '''
        FIXME: 寫的跟助教文件不太一樣 ...
    '''
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

def verify_signature(self, trans):
    vk = VerifyingKey.from_pem(trans.sender_pub_key)
    try:
        vk.verify(trans.signature, trans.msg)
        return True
    except BadSignatureError:
        return False

class Broadcast:
    def __init__(self, server):
        self.s = server

    # def sendHeader(self, n, arg):
    #     block_hash = arg['block_hash']
    #     block_header = arg['block_header']
    #     block_height = arg['block_height']

    #     d = json.dumps({
    #         'block_hash': block_hash,
    #         'block_header': block_header,
    #         'block_height': block_height
    #     })
    #     req = _pack({
    #         'method': 'sendHeader',
    #         'data': d
    #     })
    #     print(req)
    #     sock = create_sock(n.host, n.p2p_port)
    #     if sock == None:
    #         return
    #     sock.send(req)
    #     recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
    #     sock.close()
    #     if recv:
    #         r = unpack(recv)
    #         print(r)

    '''
        基本上是跟 sendHeader 一樣
        只是多了一個 transactions
        要注意的地方: 沒有傳 hash 了
    '''
    def sendBlock(self, n, arg):
        # block_hash = arg['block_hash']
        # header = arg['block_header']
        height = arg['block_height']
        # print(header)

        d = json.dumps({
            "version": 2,
            "prev_block": arg['prev_block'],
            "transactions_hash": arg['transactions_hash'],
            "beneficiary": arg['beneficiary'],
            "target": arg['target'],
            "nonce": arg['nonce'],
            "transactions": arg['transactions']
        })
        req = _pack({
            'method': 'sendBlock',
            'height': height,
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
            print('sendBlock: ', r)

    def getBlocks(self, n, arg):
        # print(arg)

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
            print('getBlocks: ', r)

            if len(result) > 0:
                # print(len(result))
                #result = max(result[0], result[1])
                # check for the branch 
                for header in result:
                    prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(header)
                    # FIXME: 因為 transactions 的部分還沒處理好，目前先直接寫死說每個都是空字串
                    # 不知道為什麼目前同步只會成功一點 不會全部成功...
                    # balance 先亂寫 = =
                    new_block = Block(prev_block, transactions_hash, target, nonce, beneficiary, [], 0)
                    # 後面傳的 True 代表要把整個檔案重寫
                    self.s.node.add_new_block(new_block, True)
                    print("done")

    def sendTransaction(self, n, arg):
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return

        sock.send(_pack({
            "method": "sendTransaction",
            "data": arg
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print("sendTransaction: ", unpack(recv))

    def sendtoaddress(self, n, arg):
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return

        sock.send(_pack({
            "method": "sendtoaddress",
            "data": arg
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print("sendtoaddress: ", unpack(recv))

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

    # def sendHeader(self, sock, data):
    #     block_hash = data['block_hash']
    #     block_header = data['block_header']
    #     block_height = data['block_height']
    #     prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(block_header)

    #     need_getBlocks = False

    #     height = self.s.node.get_height()
    #     chain = self.s.node.get_chain()

    #     # drop and triger sendHeader back
    #     if _verify_shorter(block_height, height):
    #         pass

    #     else:

    #         if _verify_height(block_height, height):
    #             need_getBlocks = True
    #         if _verify_prev_block(prev_block, chain):
    #             need_getBlocks = True
    #             error = 1
    #         if _verify_hash(block_hash, block_header):
    #             # 只是本人 hash 值不對，感覺可以直接 drop 掉
    #             error = 1

    #         if need_getBlocks:
    #             cur_height = height
    #             cur_hash = chain[cur_height].block_hash
    #             hash_count = block_height - cur_height
    #             hash_begin = cur_hash
    #             hash_stop = block_hash
    #             arg = {
    #                 'hash_count': hash_count,
    #                 'hash_begin': hash_begin,
    #                 'hash_stop': hash_stop
    #             }
    #             self.s.broadcast(self.s.apib.getBlocks, arg)
        
    #     error = 0
    #     res = {
    #         'error': error
    #     }
    #     sock.send(_pack(res))

    def sendBlock(self, sock, data, block_height):
        # block_hash = data['block_hash']
        # block_header = data['block_header']
        # block_height = data['block_height']
        # prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(block_header)
        # print(type(data))

        prev_block = data['prev_block']
        # header 自己用拼的
        block_header = str(data['version']).zfill(8)+ prev_block + data['transactions_hash'] + data['target'] + data['nonce'] + data['beneficiary']
        block_hash = sha256(block_header)

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

    def sendTransaction(self, sock, data):
        t = Transaction(data['fee'], data['nonce'], data['sender_pub_key'], data['to'], data['value'], data['wallet'])
        
        if t.verify_signature():
            error = 0
            self.s.node.trans_pool['waiting'].append(t)
        else:
            error = 1
        
        res = {
            'error': error
        }

        sock.send(_pack(res))

    def getbalance(self, sock, data):
        chain = chain = self.s.node.get_chain()
        cur_height = self.s.node.get_height()  
        addr = data['address']
            
        # 只使用最長鏈之中 confirmation 大於等於 3 的 block 來計算賬戶餘額
        if cur_height - 3 > 0:
            balance = chain[cur_height - 3].balance[addr]
        else: 
            balance = chain[cur_height].balance[addr]
        
        # 先寫死
        error = 0

        res = {
            'error': error,
            'balance': balance
        }

        sock.send(_pack(res))
    
    def sendtoaddress(self, sock, data):
        fee = self.s.wallet.fee
        cur_height = self.s.get_height()
        chain = self.s.block.get_chain()
        pubk = self.s.wallet.pub_key
        nonce = os.urandom(8).hex()
        to = data['address']
        value = data['amount']

        # Setup a transaction
        t = Transaction(fee, nonce, pubk, to, value, self.s.wallet)
        
        # sendTransaction
        # arg = {
        #     "nonce": t.nonce,
        #     "sender_pub_key": t.pubk,
        #     "to": t.to,
        #     "value": t.value,
        #     "fee": t.fee,
        #     "signature": t.signature
        # }
        arg = t.get_transaction()
        # TODO: 檢查餘額
        if is_valid():
            self.s.node.trans_pool['waiting'].append(t)
        else:
            self.s.node.trans_pool['invalid'].append(t)
        self.s.broadcast(self.s.apib.sendTransaction, arg)
        
        # 先寫死
        error = 0

        res = {
            "error": error
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
            if type(query['data']) is dict:
                data = query['data']
            else:
                data = json.loads(query['data'])
        # if method == 'sendHeader':
        #     self.sendHeader(sock, data)
        if method == 'sendBlock':
            self.sendBlock(sock, data, query['height'])
        elif method == 'getBlocks':
            self.getBlocks(sock, data)
        elif method == 'getBlockCount':
            self.getBlockCount(sock)
        elif method == 'getBlockHash':
            self.getBlockHash(sock, data)
        elif method == 'getBlockHeader':
            self.getBlockHeader(sock, data)
        elif method == 'sendTransaction':
            self.sendTransaction(sock, data)
        elif method == 'getbalance':
            self.getbalance(sock, data)
        elif method == 'sendtoaddress':
            self.sendtoadress(sock, data)
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

    def getbalance(self, n, arg):
        sock = create_sock(n.host, n.user_port)
        if sock == None:
            return
        address = arg['address']
        sock.send(_pack({
            'method': 'getbalance',
            'data': {
                'address': address
            }
        }))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            print('getbalance: ', unpack(recv))
