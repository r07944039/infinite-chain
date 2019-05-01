#!/usr/bin/env python3

from server import Server
from node import Node
from miner import Miner
import store

DEBUG = 1

def debug(s):
    if DEBUG == 1:
        print(s)


def yield_next():
    if store.state == 'miner' and store.count >= 100:
        store.state = 'server'
        store.count = 0
    if store.state == 'server' and store.count >= 100:
        store.state = 'miner'
        store.count = 0

if __name__ == '__main__':

    # Init state and count; 
    store.state = 'server'
    store.count = 0
    
    # Init Node
    store.node = Node()
    
    # Open socket server
    server = Server('127.0.0.1', 1234)
    server.listen()
    
    # Init miner
    miner = Miner()
    
    try:
        while True:
            # print(store.count)
            if store.state is 'miner':
                # miner.mine()
                yield_next()
            elif store.state is 'server':
                server.select()
                yield_next()
            else:
                # print("No state")
                break
            store.count += 1
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    