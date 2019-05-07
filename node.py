#!/usr/bin/env python3
import threading
import os
from block.block import Block
from api import _header_to_items

class Node():
    def __init__(self, target, p2p_port):
        # Genesis block
        # 要吃 config.js
        block = Block('0000000000000000000000000000000000000000000000000000000000000000',
                      target, '00002321')
        self.chain = []
        self.chain.append(block)
        self.height = 0
        self.lock = threading.Lock()
        
        f_name = '{}{}'.format("node_", str(p2p_port))
        self.file_name = os.path.join(os.getcwd(), f_name)

    def add_new_block(self, block):
        self.lock.acquire()
        self.chain.append(block)
        self.height += 1
        self.lock.release()
        self.write_file(block.block_header.header)

    def get_chain(self):
        self.lock.acquire()
        chain = self.chain
        self.lock.release()
        return chain

    def get_height(self):
        self.lock.acquire()
        height = self.height
        self.lock.release()
        return height

    def write_file(self, header):
        # with open(self.file_name, 'r') as f:
        #     header = f.readlines()
        with open(self.file_name, 'a') as f:
            f.write(header + "\n")
    
    def read_file(self):
        with open(self.file_name, 'r') as f:
            header = f.readlines()
        for h in header:
            prev_block, target, nonce = _header_to_items(h[:-1])
            block = Block(prev_block, target, nonce)
            self.chain.append(block)
            self.height += 1      
        
    def check_file(self):
        if os.path.exists(self.file_name):
            self.read_file()
            return True
