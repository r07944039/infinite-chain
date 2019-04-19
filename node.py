#!/usr/bin/env python3

import socket
import json
import hashlib
import random
import os

def sha256(data):
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()

# node
def mining(version, prev_block,merkle_root, target):
	pre_string = version + prev_block + merkle_root + target
	nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
	mine = pre_string + nonce
	while sha256(mine) > target:
		nonce = hex(os.urandom(random.randint(0, 2**32)))[2:]
		mine = pre_string + nonce

	return nonce

# p2p_port
def sendHeader(block_hash,block_header,block_height):
	error = 0 

	return error

def getBlocks(hash_count,hash_begin,hash_stop):
	error = 0
	result = ""

	return error,result

# user_port
def getBlockCount():
	error = 0
	result = ""

	return error,result

def getBlockHash(block_height):
	error = 0
	result = ""

	return error,result

def getBlockHeader(block_hash):
	error = 0
	result = ""

	return error,result



def main():
	with open("config.json",'r') as f:
		data = json.load(f)


	HOST = '127.0.0.1'  
	P2P_PORT = data[p2p_port]
	USER_PORT = data[user_port]
	NEIGHBOR_LIST = data[neighbor_list]
	TARGET = data[target]

	# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	#     s.bind((HOST, PORT))
	#     s.listen()
	#     conn, addr = s.accept()
	#     with conn:
	#         print('Connected by', addr)
	#         while True:
	#             data = conn.recv(1024)
	#             if not data:
	#                 break
	#             conn.sendall(data)



main()












