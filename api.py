import subprocess
import json

import store
from store import debug

def send_request(host, port, method, data):
    d = json.dumps({
        'method': method,
        'data': data
    })
    result = subprocess.getoutput("python3 client.py {} {} '{}'".format(host, port, d))
    result.strip('=')
    print(result)

    return result

# TODO: python 裡面是不是有方法可以少傳 parameter?
def send_request_without_data(host, port, method):
    d = json.dumps({
        'method': method
    })
    result = subprocess.getoutput("python3 client.py {} {} '{}'".format(host, port, d))
    result.strip('=')
    print(result)

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
        result.append(send_request(n_host, n_port, 'getBlocks', d))

    # TODO: 目前 result 是直接取較長的
    result = max(result[0], result[1])
    # TODO: Error handling & 判斷
    error = 0

    return error, result

# Receive request
def getBlocks(data):
    # debug(data)
    hash_count = data['hash_count']
    hash_begin = data['hash_begin']
    hash_stop = data['hash_stop']

    # 先找到那個 block 再回 block headers list
    result = []
    count = 0
    append = 0  

    # FIXME: 找不到助教範例裡面的 hash
    # Brute force QAQ
    for block in store.node.chain:
        # 到尾了
        if hash_stop == block.block_hash:
            append = 0
            continue
        if append == 1:
            result.append(block.block_hash)
        # 如果到 begin 的下一個開始計
        if hash_begin == block.block_hash:
            append = 1
    
    debug(result)
    # 如果找不到結果就回傳錯誤
    if len(result) == 0:
        error = 1

    return error, result
    
# user_port
# Non broadcast API
# Send request
def getBlockCount(host, port):
    error = 0
    result = send_request_without_data(host, port, 'getBlockCount')

    if result == None:
        error = 1

    return error, result

# Receive request
def getBlockCount():
    error = 0
    result = store.node.height

    return error, result

# Send request
def getBlockHash(host, port):
    error = 0
    d = json.dumps({
        'block_height': store.node.height
    })
    result = send_request(host, port, 'getBlockHash', d)

    if result == None:
        error = 1

    return error, result

# Receive request
def getBlockHash(data):
    error = 0
    block_height = data['block_height']
    node = store.node
    chain = node.chain
    if block_height > node.height:
        error = 1
        result = 0
        return error, result

    result = chain[block_height].block_hash
    return error, result


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
