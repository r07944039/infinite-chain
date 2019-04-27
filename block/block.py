#!/usr/bin/env python3
# coding: -*- utf-8 -*-

import hashlib


def sha256(data):
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()


class block_header():
    def __init__(self, prev_block, target, nonce):
        self.version = "00000001"
        self.prev_block = prev_block
        self.merkle_root = 0000000000000000000000000000000000000000000000000000000000000000
        self.target = target
        self.nonce = nonce


class block_hash():
    def __init__(self, version, prev_block, merkle_root, target, nonce):
        unhash = "{}{}{}{}{}".format(
            str(version), str(prevblock), str(merkle_root), str(target), str(nonce))
        self.hash = sha256(unhash)


class block():
    def __init__(self, block_header, block_hash):
        self.block_header = block_header
        self.block_hash = block_hash