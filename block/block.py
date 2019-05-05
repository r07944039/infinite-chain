#!/usr/bin/env python3

import hashlib


def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Block_header():
    def __init__(self, prev_block, target, nonce):
        # 作業中的 version 和 merkle_root 為固定的
        self.version = "00000001"
        self.prev_block = prev_block
        self.merkle_root = "0000000000000000000000000000000000000000000000000000000000000000"
        self.target = target
        self.nonce = nonce
        # FIXME: 這邊會導致整的 blockchain 無法跑
        # 因為下面三個變數在 sendHeader_receive 裡面呼叫 new_block 的時候是傳 list 進來
        print(type(self.version))
        print(self.prev_block)
        print(type(self.merkle_root))
        print(self.target)
        print(self.nonce)
        if type(self.prev_block) == list:
            self.prev_block = ""
        if type(self.target) == list:
            self.target = ""  
        if type(self.nonce) == list:
            self.nonce = ""
        self.header = self.version + str(self.prev_block) + self.merkle_root + self.target + self.nonce

# 可刪？
class Block_hash():
    def __init__(self, version, prev_block, merkle_root, target, nonce):
        unhash = '{}{}{}{}{}'.format(
            version, prev_block, merkle_root, str(target), str(nonce))
        self.hash = sha256(unhash)


class Block():
    def __init__(self, prev_block, target, nonce):
        block_header = Block_header(prev_block, target, nonce)
        # block_hash = Block_hash(block_header.version, block_header.prev_block,
        #                         block_header.merkle_root, block_header.target, block_header.nonce)
        self.block_header = block_header
        self.block_hash = sha256(self.block_header.header)
        # self.block_hash = block_hash.hash