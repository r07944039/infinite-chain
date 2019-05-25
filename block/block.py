#!/usr/bin/env python3

import hashlib


def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Block_header():
    def __init__(self, prev_block, transactions_hash, target, nonce, beneficiary, transactions):
        # 作業中的 version 和 merkle_root 為固定的
        self.version = "00000001"
        self.prev_block = prev_block
        self.transactions_hash = sha256(transactions_hash)
        self.target = target
        self.nonce = nonce
        self.beneficiary = beneficiary
        self.transactions = transactions
        self.header = self.version + str(self.prev_block) + self.transactions_hash + self.target + self.nonce + self.beneficiary


class Block():
    def __init__(self, prev_block, transactions_hash, target, nonce, beneficiary, transactions):
        block_header = Block_header(prev_block, transactions_hash, target, nonce, beneficiary, transactions)
        self.block_header = block_header
        self.block_hash = sha256(self.block_header.header)
        # self.block_hash = block_hash.hash