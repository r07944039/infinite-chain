#!/usr/bin/env python3

import json

from server import Server
from node import Node
from miner import Miner
import store

DEBUG = 0

def debug(s):
    if DEBUG == 1:
        print(s)


def yield_next():
    s = store.routines[store.state]
    debug(s)
    if s == None:
        print("state: " + store.state + " does not exist")
        exit(1)
    if store.count >= s['max_count']:
        store.state = s['to']
        store.count = 0
    
if __name__ == '__main__':

    # Init state and count; 
    store.state = store.START_FROM
    store.count = 0
    
    # Init Node
    store.node = Node()
    
    # Open socket server
    f = open("config.json", 'r')
    data = json.load(f)
    f.close()

    host = '127.0.0.1'
    p2p_port = data['p2p_port']
    user_port = data['user_port']
    neighbor_list = data['neighbor_list']
    target = data['target']

    server_p2p = Server(host, p2p_port)
    server_p2p.listen()

    server_user = Server(host, user_port)
    server_user.listen()
    
    # Init miner
    miner = Miner()
    
    try:
        while True:
            debug(store.state)
            if store.state is store.MINER:
                miner.mine()
                yield_next()
            elif store.state is store.P2P:
                server_p2p.select()
                yield_next()
            elif store.state is store.USER:
                server_user.select()
                yield_next()
            else:
                # print("No state")
                break
            store.count += 1
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    