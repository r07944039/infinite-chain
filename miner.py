#!/usr/bin/env python3

import hashlib
import store
import os
from block.block import Block
from store import debug
from api import sendHeader

def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
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
        pre_string = header.version + block.block_hash + header.merkle_root + header.target
        #nonce = os.urandom(4).hex()
        nonce_count = 0
        nonce = '{0:08x}'.format(nonce_count)
        mine = pre_string + nonce
        while int(sha256(mine),16) > int(header.target,16):
            #nonce = os.urandom(4).hex()
            nonce_count += 1
            nonce = '{0:08x}'.format(nonce_count)     
            mine = pre_string + nonce
        
        # Add block into your block chain
        new_block = Block(block.block_hash, header.target, nonce)
        self._add_new_block(new_block)
        # Boardcast new block to network
        # FIXME: 改好 api 後要打開
        sendHeader(new_block.block_hash, new_block.block_header.header, height)
        debug(nonce)
        return nonce
    
    def mine(self):
        self.mining()
