#!/usr/bin/env python3

import socket
import json
import hashlib
import random
import os
from block.block import Block


def sha256(data):
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()


class Node():
    def __init__(self):
        # Genesis block
        block = Block('0000000000000000000000000000000000000000000000000000000000000000', '0001000000000000000000000000000000000000000000000000000000000000', 2321)
        self.chain = []
        self.chain.append(block)
        self.height = 0

    def _add_new_block(self, block):
        self.chain.append(block)
        self.height += 1

    # p2p_port
    def sendHeader(self, block_hash, block_header, block_height):
        error = 0
        result = ""

        return error

    def getBlocks(self, hash_count, hash_begin, hash_stop):
        error = 0
        result = ""

        return error, result

    # node
    def mining(self, block):
        header = block.block_header
        pre_string = header.version + header.prev_block + header.merkle_root + header.target
        nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
        mine = pre_string + nonce
        while sha256(mine) > header.target:
            nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
            mine = pre_string + nonce
        
        # Add block into your block chain
        new_block = Block(block.block_hash, header.target, nonce)
        _add_new_block(new_block)

        # Boardcast new block to network
        sendHeader(new_block.block_hash, new_block.block_header, self.height)

        return nonce

    # user_port
    def getBlockCount(self):
        if self == None:
            error = 1
            result = 0
        else:
            error = 0
            result = self.height

        return error, result

    def getBlockHash(self, block_height):
        if block_height != None:
            # os.system('python3 socket/app-client.py {} {}'.format(HOST, P2P_PORT))
            result = self.chain[block_height].block_hash
            error = 0
        else:
            result = 0
            error = 1

        return result

    # 目前我只想得到 O(n) 直接去暴力搜那個 hash 在哪裡 QQ
    def getBlockHeader(self, block_hash):
        for block in self.chain:
            if block.block_hash == block_hash:
                error = 0
                result = block.block_header
                return error, result
        
        error = 1
        result = 0
        return error, result      

def connectSocket():
    f = open("config.json", 'r')
    data = json.load(f)
    f.close()
    # print(data)

    global HOST
    global P2P_PORT
    global USER_PORT
    global NEIGHBOR_LIST
    HOST = '127.0.0.1'
    P2P_PORT = data['p2p_port']
    USER_PORT = data['user_port']
    NEIGHBOR_LIST = data['neighbor_list']
    TARGET = data['target']

    os.system('python3 socket/app-server.py {} {}'.format(HOST, P2P_PORT))

if __name__ == '__main__':
    '''
        1. 先確認 network 中有沒有已經存在的 blockchain
        2. 若是沒有，就自己新增一個 Genesis block
        3. 若是有，就去要到最新(長)的 block -> prev_block
        4. 開啟自己的 socket server
        5. 開始 mining
    '''

    node = Node()
    connectSocket()