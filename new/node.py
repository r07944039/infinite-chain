#!/usr/bin/env python3
import threading

from block.block import Block

class Node():
    def __init__(self, target):
        # Genesis block
        # 要吃 config.js
        block = Block('0000000000000000000000000000000000000000000000000000000000000000',
                      target, '00002321')
        self.chain = []
        self.chain.append(block)
        self.height = 0
        self.lock = threading.Lock()

    def add_new_block(self, block):
        self.lock.acquire()
        self.chain.append(block)
        self.height += 1
        self.lock.release()

# node = Node()