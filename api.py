import pickle
import socket
import hashlib
import json
import globs
import os
import logging
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

from block.block import Block
from transaction import Transaction


logging.basicConfig(level=logging.INFO,
            format='[+]%(levelname)-8s %(message)s')
# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)


def create_sock(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(globs.RETRY_TIMEOUT)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        s.connect((host, port))
    except socket.error as err:
        logging.error("create_sock: " + host + ":" + str(port) + ": " + err)
        # print("create_sock: " + host + ":" + str(port), ": ", err)
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
    # 助教傳來的格式
    try:
        packet = json.loads(packet)
    # 我們自己 socket 的格式
    except:
        packet = json.loads(pickle.loads(packet))
    return packet


def header_to_items(header):
    prev_block = header[8:72]
    transactions_hash = header[72:136]
    target = header[136:-136] # 64
    nonce = header[-136:-128] # 8
    beneficiary = header[-128:]

    return prev_block, transactions_hash, target, nonce, beneficiary



def verify_version(version):
    if int(version) != 2:
        return True
    return False

def verify_target(target, old_target, block_hash):
    if target == old_target:
        if block_hash <= target:
            return False
    return True

def verify_hash(block_hash, block_header):
    if sha256(block_header) != block_hash:
        return True
    return False

def verify_prev_block(prev_block, chain, height):
    if height == 0:
        return False
    pre_block_hash = chain[-1].block_hash
    if prev_block != pre_block_hash:
        return True
    return False

# def verify_height(new_height, cur_height):
#     if cur_height != int(new_height) - 1:
#         return True
#     return False

def verify_shorter(new_height, cur_height):
    if cur_height < int(new_height):
        return False
    return True

def verify_transection_hash(transactions,transactions_hash):
    sig = ""
    for trans in transactions:
        sig += trans['signature']

    if sha256(sig) != transactions_hash:
        return True
    return False   

def verify_signature(pub_key, sig, msg):
    vk = VerifyingKey.from_string(bytes.fromhex(pub_key), curve=SECP256k1)
    try:
        vk.verify(bytes.fromhex(sig), bytes(msg,'utf-8'))
        return True
    except BadSignatureError:
        return False

def verify_not_exist_signature(sig_list, sig):
    if sig in sig_list:
        return False
    return True

def verify_balance(balance, fee, value):
    if balance < fee + value:
        return False
    return True


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

        new_block = Block(arg['prev_block'], arg['transactions_hash'], arg['target'], arg['nonce'], arg['beneficiary'], arg['transactions'], arg['balance'])

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
        logging.info("Sent sendBlock > " + d)
        # print(req)
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return
        sock.send(req)
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            
            # print('sendBlock: ', r)

            # 如果接到別人確認過沒問題的 block 才可以加入 chain 上
            if r['error'] == 0:
                self.s.node.add_new_block(new_block, False)
                logging.info("Received response sendBlock > " + json.dumps(r))
                # print("Add new block!")
            else:
                logging.error("Received response sendBlock > " + json.dumps(r))
    # 沒有用到此功能
    # def getBlocks(self, n, arg):
    #     # print(arg)

    #     d = json.dumps({
    #         'hash_count': arg['hash_count'],
    #         'hash_begin': arg['hash_begin'],
    #         'hash_stop': arg['hash_stop']
    #     })
    #     req = _pack({
    #         'method': 'getBlocks',
    #         'data': d
    #     })
    #     sock = create_sock(n.host, n.p2p_port)
    #     if sock == None:
    #         return
    #     sock.send(req)
    #     print(req)
    #     recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
    #     sock.close()
    #     if recv:
    #         r = unpack(recv)
    #         result = r['result']
    #         print('getBlocks: ', r)

    #         if len(result) > 0:
    #             # check for the branch 
    #             for data in result:
    #                 prev_block = data['prev_block']
    #                 transactions_hash = data['transactions_hash']
    #                 beneficiary = data['beneficiary']
    #                 target = data['target']
    #                 nonce = data['nonce']
    #                 transactions = data['transactions']
    #                 balance = data['balance']
    #                 # prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(header)
    #                 # FIXME: 因為 transactions 的部分還沒處理好，目前先直接寫死說每個都是空字串
    #                 # 不知道為什麼目前同步只會成功一點 不會全部成功...
    #                 # balance 先亂寫 = =
    #                 new_block = Block(prev_block, transactions_hash, target, nonce, beneficiary, transactions, balance.copy())
    #                 # 後面傳的 True 代表要把整個檔案重寫
    #                 self.s.node.add_new_block(new_block, True)
    #                 print("done")

    def sendTransaction(self, n, arg):
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            logging.error("SOCK is None")
            return

        req = {
            "method": "sendTransaction",
            "data": arg
        }

        sock.send(_pack(req))

        logging.info("Sent sendTransaction > " + json.dumps(req))

        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            if r['error'] == 0:
                logging.info("Received response sendTrasaction > " + json.dumps(r))
            else:
                logging.error("Received response sendTrasaction > " + json.dumps(r))
            # print("sendTransaction: ", unpack(recv))

    

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
        logging.info("Received sendBlock > " + json.dumps(data))
        version =  data['version']
        prev_block = data['prev_block']
        transactions_hash = data['transactions_hash']
        beneficiary = data['beneficiary']
        target = data['target']
        nonce = data['nonce']
        transactions = data['transactions']
        print("transactions ", transactions)

        # header 自己用拼的
        block_header = str(version).zfill(8) + prev_block + transactions_hash + target + nonce + beneficiary
        block_hash = sha256(block_header)

        #need_getBlocks = False
        error = 0

        height = self.s.node.get_height()
        chain = self.s.node.get_chain()

        if verify_shorter(block_height, height):
            print("shorter")
            error = 1
        else:
            if verify_version(version):
                print("version")
                error = 1
            if verify_target(target, chain[-1].block_header.target, block_hash):
                print("target")
                error = 1
            if verify_transection_hash(transactions,transactions_hash):
                print("t_hash")
                error = 1
            if verify_prev_block(prev_block, chain, height):
                print("prev_block")
                #need_getBlocks = True
                error = 1

            balance = chain[-1].block_header.balance

            for tx in transactions:
                t = Transaction(tx['fee'], tx['nonce'], tx['sender_pub_key'], tx['to'], tx['value'], self.s.node.wallet)
                if not t.verify_signature():
                    print("sig")
                    error = 1
                    break
                if not verify_not_exist_signature(self.s.node.trans_sig_list, t.signature):
                    print("exist")
                    error = 1
                    break
                if not verify_balance(balance[t.sender_pub_key], t.fee, t.value):
                    print("balance")
                    error = 1
                    break
                
                balance[t.sender_pub_key] -= t.fee + t.value
                balance[t.to] += t.value

            # 這個不需要，因為我們靠sendblock的先挖先贏，就能強勢同步其他node
            # if need_getBlocks:
            #     cur_height = height
            #     cur_hash = chain[cur_height].block_hash
            #     hash_count = block_height - cur_height
            #     hash_begin = cur_hash
            #     hash_stop = block_hash
            #     arg = {
            #         'hash_count': hash_count,
            #         'hash_begin': hash_begin,
            #         'hash_stop': hash_stop
            #     }
            #     self.s.broadcast(self.s.apib.getBlocks, arg)
        
        res = {
            'error': error
        }
        sock.send(_pack(res))

        if not error:
            logging.info("Sent response sendBlock > " + json.dumps(res))
            if beneficiary not in balance:
                balance[beneficiary] = 1000
            else:
                balance[beneficiary] += 1000
            new_block = Block(prev_block, transactions_hash, target, nonce, beneficiary, transactions, balance.copy())
           
            self.s.node.add_new_block(new_block, False)
        else:
            logging.error("Sent response sendBlock > " + json.dumps(res))

    # 沒有用到此功能
    # def getBlocks(self, sock, data):
    #     hash_count = data['hash_count']
    #     hash_begin = data['hash_begin']
    #     hash_stop = data['hash_stop']

    #     # 先找到那個 block 再回 block headers list
    #     result = []
    #     count = 0
    #     append = 0

    #     chain = self.s.node.get_chain()

    #     # Brute force QAQ
    #     for block in chain:
    #         # 到尾了
    #         if hash_stop == block.block_hash:
    #             back = {
    #                 "version": 2,
    #                 "prev_block": block.block_header.prev_block,
    #                 "transactions_hash": block.block_header.transactions_hash,
    #                 "beneficiary": block.block_header.beneficiary,
    #                 "target": block.block_header.target,
    #                 "nonce": block.block_header.nonce,
    #                 "transactions": block.block_header.transactions,
    #                 "balance": block.block_header.balance.copy()
    #             }
    #             result.append(back)
    #             append = 0
    #             break
    #         if append == 1:
    #             back = {
    #                 "version": 2,
    #                 "prev_block": block.block_header.prev_block,
    #                 "transactions_hash": block.block_header.transactions_hash,
    #                 "beneficiary": block.block_header.beneficiary,
    #                 "target": block.block_header.target,
    #                 "nonce": block.block_header.nonce,
    #                 "transactions": block.block_header.transactions,
    #                 "balance": block.block_header.balance.copy()
    #             }
    #             result.append(back)
    #             #result.append(block.block_header.header)
    #         # 如果到 begin 的下一個開始計
    #         if hash_begin == block.block_hash:
    #             append = 1
    #     # debug(result)
    #     # 如果找不到結果就回傳錯誤
    #     if len(result) == 0:
    #         error = 1
    #     else:
    #         error = 0
    #     res = {
    #         'result': result,
    #         'error': error
    #     }
        
    #     sock.send(_pack(res))

    def getBlockCount(self, sock):
        height = self.s.node.get_height()
        if height == 0:
            error = 1
        else:
            error = 0

        res = {
            'result': {
                "height": height
            },
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
        logging.info("Received sendTransaction > " + json.dumps(data))
        t = Transaction(data['fee'], data['nonce'], data['sender_pub_key'], data['to'], data['value'], self.s.node.wallet)
        
        if t.verify_signature():
            error = 0
            self.s.node.trans_pool['waiting'].append(t)
        else:
            error = 1

        chain = chain = self.s.node.get_chain()
        cur_height = self.s.node.get_height()
        if t.sender_pub_key not in chain[cur_height].block_header.balance:
            chain[cur_height].block_header.balance[t.sender_pub_key] = 0
        if t.to not in chain[cur_height].block_header.balance:
            chain[cur_height].block_header.balance[t.to] = 0
        
        res = {
            'error': error
        }

        sock.send(_pack(res))
        if error == 0:
            logging.info("Sent response sendTransaction > " + json.dumps(res))
        else:
            logging.error("Sent response sendTransaction > " + json.dumps(res))

    def getbalance(self, sock, data):
        logging.info("Received getbalance > "+ json.dumps(data))
        chain = chain = self.s.node.get_chain()
        cur_height = self.s.node.get_height()  
        addr = data['address']
            
        # 只使用最長鏈之中 confirmation 大於等於 3 的 block 來計算賬戶餘額
        if cur_height - 3 > 0:
            balance = chain[cur_height - 3].block_header.balance[addr]
        else: 
            balance = chain[cur_height].block_header.balance[addr]
        
        # 先寫死
        error = 0

        res = {
            'error': error,
            'balance': balance
        }

        sock.send(_pack(res))
        logging.info("Sent response getbalance > " + json.dumps(res))
    
    def sendtoaddress(self, sock, data):
        logging.info("Received sendtoaddress > " + json.dumps(data))
        fee = self.s.node.wallet.fee
        cur_height = self.s.node.get_height()
        chain = self.s.node.get_chain()
        pubk = self.s.node.wallet.pub_key
        nonce = os.urandom(8).hex()
        to = data['address']
        value = data['amount']

        # Setup a transaction
        t = Transaction(fee, nonce, pubk, to, value, self.s.node.wallet)
        
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

        print(chain[cur_height].block_header.balance)
        if t.sender_pub_key not in chain[cur_height].block_header.balance:
            chain[cur_height].block_header.balance[t.sender_pub_key] = 0
        if t.to not in chain[cur_height].block_header.balance:
            chain[cur_height].block_header.balance[t.to] = 0
        if t.fee + t.value <= chain[cur_height].block_header.balance[self.s.node.wallet.pub_key]:
            self.s.node.trans_pool['waiting'].append(t)
        else:
            self.s.node.trans_pool['invalid'].append(t)
        
        self.s.broadcast(self.s.apib.sendTransaction, arg)
        
        # 先寫死
        error = 0

        res = {
            "error": error
        }

        # print(res)
        sock.send(_pack(res))
        logging.info("Sent response sendtoaddress > " + json.dumps(res))

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
            self.sendtoaddress(sock, data)
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
        req = {
            'method': 'getbalance',
            'data': {
                'address': address
            }
        }
        sock.send(_pack(req))

        logging.info("Sent getbalance > " + json.dumps(req))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            if r['error'] == 0:
                logging.info("Received response getbalance > " + json.dumps(r))
            else:
                logging.error("Sent getbalance > " + json.dumps(req))
            
            # print('getbalance: ', unpack(recv))

    def sendtoaddress(self, n, arg):
        sock = create_sock(n.host, n.p2p_port)
        if sock == None:
            return

        req = {
            "method": "sendtoaddress",
            "data": arg
        }

        sock.send(_pack(req))

        logging.info("Sent sendtoaddress > " + json.dumps(req))
        recv = sock.recv(globs.DEFAULT_SOCK_BUFFER_SIZE)
        sock.close()
        if recv:
            r = unpack(recv)
            if r['error'] == 1:
                logging.error("Received response sendtoaddress > " + json.dumps(r))
            else:
                logging.info("Received response sendtoaddress > " + json.dumps(r))
            # print("sendtoaddress: ", unpack(recv))
