import subprocess
import json

import store

def send_request(host, port, method, data):
    d = json.dumps({
        'method': method,
        'data': data
    })
    result = subprocess.getoutput("python3 client.py {} {} '{}'".format(host, port, d))
    result.strip('=')
    # print(result)

    return result

'''
    目前感覺所有 API 都必須是雙向的
    也就是說一個 function 要能處理收發 request
    python 有一個特性，就是可以取兩個名字一樣的 function (只要參數不一樣就好)
    目前打算用這種方式去解決
'''


# p2p_port
# broadcast API
def sendHeader(block_hash, block_header, block_height):
    for neighbor in store.neighbor_list:
        # TODO: Send json via socket client
        pass

    error = 0

    return error

# Send request
def getBlocks(hash_count, hash_begin, hash_stop):
    d = json.dumps({
        'hash_count': hash_count,
        'hash_begin': hash_begin,
        'hash_stop': hash_stop
    })
    for neighbor in store.neighbor_list:
        n_host = neighbor.ip
        n_port = neighbor.p2p_port      
        '''
            TODO: 
            我現在是把每一次接收到的結果都當成最終的 result
            文件中是寫 return Block header of the block_hash
            但我沒有看到如何去比較哪個 hash 才是最長的？
            FIXME: 
            目前想到的解法是多傳一個 node.height 回來, 這樣就可以比較誰最長 (但我還沒實作)
            BTW 這個 API 真的很謎
        '''
        result = send_request(n_host, n_port, 'getBlocks', d)

    # TODO: Error handling & 判斷
    error = 0

    return error, result

# Receive request
def getBlocks(host, port, data):
    hash_count = data['hash_count']
    hash_begin = data['hash_begin']
    hash_stop = data['hash_stop']

    # 先找到那個 block 再回 block headers list
    result = []
    count = 0
    append = 0  

    # Brute force QAQ
    for block in store.node.chain:
        # 到尾了
        if hash_stop == block.hash:
            append = 0
            continue
        if append == 1:
            result.append(block.hash)
        # 如果到 begin 的下一個開始計
        if hash_begin == block.hash:
            append = 1

    # TODO: Error handling
    error = 0
    return result
    
# user_port
# Non broadcast API
def getBlockCount():
    if self == None:
        error = 1
        result = 0
    else:
        error = 0
        result = self.height

    return error, result

def getBlockHash(block_height):
    if block_height != None:
        # os.system('python3 socket/app-client.py {} {}'.format(HOST, P2P_PORT))
        result = self.chain[block_height].block_hash
        error = 0
    else:
        result = 0
        error = 1

    return result

# 目前我只想得到 O(n) 直接去暴力搜那個 hash 在哪裡 QQ
def getBlockHeader(block_hash):
    for block in self.chain:
        if block.block_hash == block_hash:
            error = 0
            result = block.block_header
            return error, result
    
    error = 1
    result = 0
    return error, result   


# send_request('127.0.0.1', 1234, 'sendHeader', 'aaaa')