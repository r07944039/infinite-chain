#!/usr/bin/env python3

import json

from server import Server
from node import Node
from miner import Miner
from store import debug
import store
import api


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
    
    # Open socket server
    f = open("config.json", 'r')
    data = json.load(f)
    f.close()

    host = '127.0.0.1'
    store.P2P_PORT = data['p2p_port']
    p2p_port = store.P2P_PORT
    user_port = data['user_port']
    # 因為很多地方要用，所以存成 global variable
    store.neighbor_list = data['neighbor_list']
    store.target = data['target']
    
    # Init Node
    store.node = Node(store.target)

    server_p2p = Server(host, p2p_port)
    server_p2p.listen()

    server_user = Server(host, user_port)
    server_user.listen()

    node = store.node
    # Current block
    cblock = node.chain[node.height]

    # TODO: getBlocks
    # api.getBlocks(cblock.)
    # api.boardcast(host, p2p_port, 'sendHeader', 'aaaa')
    
    # Init miner
    miner = Miner()
    
    # Scheduling
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
    
