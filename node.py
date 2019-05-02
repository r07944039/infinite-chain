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
    def __init__(self,target):
        # Genesis block
        block = Block('0000000000000000000000000000000000000000000000000000000000000000',
                      target, 2321)
        self.chain = []
        self.chain.append(block)
        self.height = 0
