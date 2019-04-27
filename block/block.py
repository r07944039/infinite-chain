#!/usr/bin/env python3

import hashlib


def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Block_header():
    def __init__(self, prev_block, target, nonce, height):
        self.version = "00000001"
        self.prev_block = prev_block
        self.merkle_root = 0000000000000000000000000000000000000000000000000000000000000000
        self.target = target
        self.nonce = nonce
        self.height = height


class Block_hash():
    def __init__(self, version, prev_block, merkle_root, target, nonce):
        unhash = '{}{}{}{}{}'.format(
            version, prev_block, str(merkle_root), str(target), str(nonce))
        self.hash = sha256(unhash)


class Block():
    def __init__(self, prev_block, target, nonce, height):
        block_header = Block_header(prev_block, target, nonce, height)
        block_hash = Block_hash(block_header.version, block_header.prev_block,
                                block_header.merkle_root, block_header.target, block_header.nonce)
        self.block_header = block_header
        self.block_hash = block_hash