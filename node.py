#!/usr/bin/env python3
import hashlib
import threading
import os
from block.block import Block
from api import header_to_items


def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

class Node():
    def __init__(self, target, p2p_port, beneficiary, transactions, balance, wallet):
        # Genesis block
        # 要吃 config.js
        # 一開始 balance 是 0
        block = Block('0000000000000000000000000000000000000000000000000000000000000000', sha256(""), target, '00002321', beneficiary, transactions, balance)
        self.chain = []
        self.chain.append(block)
        self.height = 0
        self.lock = threading.Lock()
        self.trans_sig_list = []
        self.trans_pool = {
            "waiting": [],
            "invalid": []
        }
        self.wallet = wallet
        
        f_name = '{}{}'.format("node_", str(p2p_port))
        self.file_name = os.path.join(os.getcwd(), f_name)

    def add_new_block(self, block, clear):
        self.lock.acquire()

        # TODO: 寫好後要用助教的 code 測試

        # waiting list 裡面有這個 trans 的都要排除
        delete = [tran for tran in block.block_header.transactions if tran in self.trans_pool['waiting']]
        for tran in delete:
            self.trans_pool['waiting'].remove(tran)
        
        # 把 invalid list 的再檢查一次，看能不能移到 waiting 裡面
        for tran in self.trans_pool['invalid']:
            if tran.value + self.wallet.fee <= block.block_header.balance:
                self.trans_pool['waiting'].append(tran)
                self.trans_pool['invalid'].remove(tran)
        
        # 把確定的 trans_sig 塞進 self.trans_sig_list 裡面
        for tran in block.block_header.transactions:
            self.trans_sig_list.append(tran.signature)

        
        self.chain.append(block)
        self.height += 1
        self.lock.release()
        if clear is True:
            self.rewrite_file()
            return
        else: 
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
        self.lock.acquire()
        # with open(self.file_name, 'r') as f:
        #     header = f.readlines()
        with open(self.file_name, 'a') as f:
            f.write(header + "\n")
        self.lock.release()

    # For the first time getBlocks
    def rewrite_file(self):
        self.lock.acquire()
        with open(self.file_name, 'w+') as f:
            # Erase the content 
            print("ERASE THE CONTENT")
            f.seek(0)
            f.truncate()
            # Write all blocks into the file
            # print("STOP")
            for block in self.chain:
                f.write(block.block_header.header + "\n")
            f.close()
        self.lock.release()
    
    def read_file(self):
        with open(self.file_name, 'r') as f:
            header = f.readlines()
        for h in header:
            prev_block, transactions_hash, target, nonce, beneficiary = header_to_items(h[:-1])
            # FIXME: balance 亂寫成 0
            block = Block(prev_block, transactions_hash, target, nonce, beneficiary, [], {})
            self.chain.append(block)
            self.height += 1      
        
    def check_file(self):
        if os.path.exists(self.file_name):
            self.read_file()
            return True
