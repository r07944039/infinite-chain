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

    # node
    def mining(self, version, prev_block, merkle_root, target):
        pre_string = version + prev_block + merkle_root + target
        nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
        mine = pre_string + nonce
        while sha256(mine) > target:
            nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
            mine = pre_string + nonce

        return nonce

    # p2p_port
    def sendHeader(self, block_hash, block_header, block_height):
        error = 0
        result = ""

        return error

    def getBlocks(self, hash_count, hash_begin, hash_stop):
        error = 0
        result = ""

        return error, result

    # user_port
    def getBlockCount(self):
        error = 0
        result = ""

        return error, result

    def getBlockHash(self, block_height):
        error = 0
        result = ""

        return result

    def getBlockHeader(self):
        error = 0
        result = block_header

        return result


def connectSocket():
    f = open("config.json", 'r')
    data = json.load(f)
    f.close()
    # print(data)

    HOST = '127.0.0.1'
    P2P_PORT = data['p2p_port']
    USER_PORT = data['user_port']
    NEIGHBOR_LIST = data['neighbor_list']
    TARGET = data['target']

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((HOST, PORT))
    #     s.listen()
    #     conn, addr = s.accept()
    #     with conn:
    #         print('Connected by', addr)
    #         while True:
    #             data = conn.recv(1024)
    #             if not data:
    #                 break
    #             conn.sendall(data)



if __name__ == '__main__':
    '''
        1. 先確認 network 中有沒有已經存在的 blockchain
        2. 若是沒有，就自己新增一個 Genesis block
        3. 若是有，就去要到最新(長)的 block -> prev_block
    '''
    
    connectSocket()

    block = Block('0000000000000000000000000000000000000000000000000000000000000000', '0001000000000000000000000000000000000000000000000000000000000000', 2321, 0)
    node = Node()
