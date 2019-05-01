#!/usr/bin/env python3

import hashlib
import store
import os
import random

def sha256(data):
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()

class Miner:
    # def __init__(self):

    def _add_new_block(self, block):
        store.node.chain.append(block)
        store.node.height += 1
        
    def mining(self):
        height = store.node.height
        block = store.node.chain[height]
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
        sendHeader(new_block.block_hash, new_block.block_header, height)
        # print(nonce)

        return nonce
    
    def mine(self):
        self.mining()