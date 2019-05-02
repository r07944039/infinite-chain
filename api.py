import subprocess
import json
from block.block import Block
import store
from store import debug

def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

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

    if cur_height != new_height - 1:
        error = 1
    return error


def _add_new_block(block):
    store.node.chain.append(block)
    store.node.height += 1

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
    TODO: 猜測用相同名字可能會出錯，但因為還沒測過發送 request 所以 function name 暫時保留
'''


# p2p_port
# broadcast API
# Send request
def sendHeader(block_hash, block_header, block_height):
    d = json.dumps({
        'block_hash': block_hash,
        'block_header': block_header,
        'block_height': block_height
    })    
    for neighbor in store.neighbor_list:
        n_host = neighbor['ip']
        n_port = neighbor['p2p_port']
        result = send_request(n_host, n_port, 'sendHeader', d)

    error = 0

    return error

# Receive request
def sendHeader(data):
    block_hash = data['block_hash']
    block_header = data['block_header']
    block_height = data['block_height']

    prev_block = block_header[8:72]
    target = block_header[-72:-8]
    nonce = block_header[-8:]

    if verify_height(block_height):
        error = 1
        '''
        檢查是不是height只差1
        可能要再接getblocks之類的去同步
        '''
        return error
    if verify_prev_block(prev_block):
        '''
        檢查前一個block_hash是不是現在header的prev_block
        可能要再接getblocks之類的去同步
        '''
        error = 1
        return error
    if verify_hash(block_header):
        # 只是本人hash值不對，感覺可以直接drop掉
        error = 1
        return error

    new_block = Block(block_hash, target, nonce)
    _add_new_block(new_block)

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
    result = 0
    result = send_request_without_data(host, port, 'getBlockCount')

    if result == 0:
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
    result = 0
    d = json.dumps({
        'block_height': store.node.height
    })
    result = send_request(host, port, 'getBlockHash', d)

    if result == 0:
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

# Send request
def getBlockHeader(host, port):
    error = 0
    result = 0
    node = store.node
    q = json.dumps({
        'block_hash': node.chain[node.height].block_hash
    })
    result = send_request(host, port, 'getBlockHeader', q)
    if result == 0:
        error = 1

    return error, result

def getBlockHeader(data):
    error = 0
    result = 0
    block_hash = data['block_hash']
    chain = store.node.chain

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

    if result == 0:
        error = 1
        
    return error, result
