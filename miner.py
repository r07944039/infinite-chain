import time
import hashlib
import os

from block.block import Block
import api

def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Miner:
    def __init__(self, name, p2pserver, userserver, node, beneficiary):
        self.name = name
        self.p2p = p2pserver
        self.user = userserver
        self.node = node
        self.beneficiary = beneficiary

    def mining(self):
        height = self.node.get_height()
        chain = self.node.get_chain()
        block = chain[height]
        header = block.block_header
        # FIXME: 刪掉 merkle tree，不知道會不會有什麼影響
        # pre_string = header.version + block.block_hash + \
        #     "0000000000000000000000000000000000000000000000000000000000000000" + header.target
        pre_string = header.version + block.block_hash + header.target
        nonce = os.urandom(4).hex()
        nonce_count = int(nonce, 16)
        mine = pre_string + nonce

        while int(sha256(mine), 16) > int(header.target, 16):
            nonce_count += 1
            nonce = '{0:08x}'.format(nonce_count)
            if len(nonce) > 8:
                nonce_count = 0
                nonce = nonce[1:]
            mine = pre_string + nonce

        # Add block into your block chain
        # FIXME: 寫死 transactions & balance 亂寫
        new_block = Block(block.block_hash, sha256(""), header.target, nonce, self.beneficiary, [], 0)
        self.node.add_new_block(new_block, False)

        # Boardcast new block to network
        # sendHeader_send(new_block.block_hash,
        #                 new_block.block_header.header, height)
        header = new_block.block_header
        arg = {
            # 'block_hash': new_block.block_hash,
            # 'block_header': new_block.block_header, 
            "version": 2,
            "prev_block": header.prev_block,
            "transactions_hash": header.transactions_hash,
            "beneficiary": header.beneficiary,
            "target": header.target,
            "nonce": header.nonce,
            "transactions": header.transactions,
            'block_height': height
        }
        self.p2p.broadcast(self.p2p.apib.sendBlock, arg)

        print(nonce)
        return nonce

    def mine(self):
        if self.node.check_file():
            # FIXME: 這邊要改
            arg = {
              'hash_count': 2, 
              'hash_begin': "0000063cd8f0327016240097e455422ea3a26dadd3b39cde25c18deb60b4d9cd", 
              'hash_stop': "00002ec4e51f5fede85226d18a91a413482d3f5f5cd5ebe6d4e0e23cf5510ab8"
            }
            # print(arg)
            self.p2p.broadcast(self.p2p.apib.getBlocks, arg)
        # print("done!!!!!")
        while True:
            # keep mining
            # print(self.p2p.neighbors)
            # self.p2p.broadcast(self.p2p.apib.hello, {})
            # print('mined!!')
            # time.sleep(1)
            self.mining()
