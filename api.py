# import subprocess
import socket
import json
import hashlib

from block.block import Block
from store import debug
from client import send_socket_req
from client import send_header
import store
import threading


def is_connected(host, port):
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, port), 2)
        return True
    except:
        pass
    return False


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

    if cur_height != int(new_height) - 1:
        error = 1
    return error


def header_to_items(header):
    prev_block = header[8:72]
    target = header[-72:-8]
    nonce = header[-8:]

    return prev_block, target, nonce


def _add_new_block(block):
    store.node.chain.append(block)
    store.node.height += 1


def send_request(host, port, method, data):
    d = json.dumps({
        'method': method,
        'data': data,
        'node': store.P2P_PORT
    })
    # result = subprocess.getoutput("python3 client.py {} {} '{}'".format(host, port, d))
    # threading.Thread(target=send_socket_req, args=(host, port, d))
    # result = send_socket_req(host, port, d)
    result = send_header(host, port, d)
    # result.strip('=')
    print(result)
    return result

# TODO: python 裡面是不是有方法可以少傳 parameter?


def send_request_without_data(host, port, method):
    d = json.dumps({
        'method': method
    })
    # result = subprocess.getoutput("python3 client.py {} {} '{}'".format(host, port, d))
    # result.strip('=')
    result = send_socket_req(host, port, d)
    print("???????????")
    print(result)

    return result

# p2p_port
# broadcast API
# Send request


def sendHeader_send(block_hash, block_header, block_height):
    d = json.dumps({
        'block_hash': block_hash,
        'block_header': block_header,
        'block_height': block_height
    })
    for neighbor in store.neighbor_list:
        n_host = neighbor['ip']
        n_port = neighbor['p2p_port']
        if is_connected(n_host, n_port):
            print('================start sendHeader==================')
            result = send_request(n_host, n_port, 'sendHeader', d)
            print(result)

    error = 0

    return error

# Receive request


def sendHeader_receive(data):
    d = json.loads(data)
    block_hash = d['block_hash']
    block_header = d['block_header']
    block_height = d['block_height']

    prev_block, target, nonce = header_to_items(block_header)

    need_getBlocks = False

    if verify_height(block_height):
        need_getBlocks = True

    if verify_prev_block(prev_block):
        need_getBlocks = True

    if verify_hash(block_hash, block_header):
        # 只是本人 hash 值不對，感覺可以直接 drop 掉
        error = 1
        return error

    if need_getBlocks:
        cur_height = store.node.height
        cur_hash = store.node.chain[cur_height].block_hash
        hash_count = block_height - cur_height
        hash_begin = cur_hash
        hash_stop = block_hash
        result = getBlocks_send(hash_count, hash_begin, hash_stop)

        # check if reult[0] == hash_begin(current header)

        for header in result[1:]:
            prev_block, target, nonce = header_to_items(header)
            new_block = Block(prev_block, target, nonce)
            _add_new_block(new_block)

    else:
        new_block = Block(prev_block, target, nonce)
        _add_new_block(new_block)

    error = 0

    return error

# Send request


def getBlocks_send(hash_count, hash_begin, hash_stop):
    d = json.dumps({
        'hash_count': hash_count,
        'hash_begin': hash_begin,
        'hash_stop': hash_stop
    })
    result = []
    for neighbor in store.neighbor_list:
        n_host = neighbor['ip']
        n_port = neighbor['p2p_port']
        if is_connected(n_host, n_port):
            result.append(send_request(n_host, n_port, 'getBlocks', d))

    # TODO: 目前 result 是直接取較長的
    if len(result) > 1:
        result = max(result[0], result[1])
    # TODO: Error handling & 判斷
    error = 0

    return error, result

# Receive request


def getBlocks_receive(data):
    d = json.loads(data)
    hash_count = d['hash_count']
    hash_begin = d['hash_begin']
    hash_stop = d['hash_stop']

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


def getBlockCount_send(host, port):
    error = 0
    result = 0
    result = send_request_without_data(host, port, 'getBlockCount')

    if result == 0:
        error = 1

    return error, result

# Receive request


def getBlockCount_receive():
    error = 0
    result = store.node.height

    return error, result

# Send request


def getBlockHash_send(host, port):
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


def getBlockHash_receive(data):
    error = 0
    d = json.loads(data)
    block_height = d['block_height']
    node = store.node
    chain = node.chain
    if block_height > node.height:
        error = 1
        result = 0
        return error, result

    result = chain[block_height].block_hash
    return error, result

# Send request


def getBlockHeader_send(host, port):
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


def getBlockHeader_receive(data):
    error = 0
    result = 0
    d = json.loads(data)
    block_hash = d['block_hash']
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
