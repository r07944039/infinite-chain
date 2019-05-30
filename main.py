import threading
import server
import argparse
import json
import time
import globs
import neighbor
import miner

from node import Node
from wallet import Wallet


# set flags
parser = argparse.ArgumentParser()
# parser.add_argument("host", type=str, help="host")
# parser.add_argument("port", type=int, help="port")
parser.add_argument("configfile", type=str, help="configfile path")
args = parser.parse_args()

# print(args.configfile)
# read config from json
# set globs here
# Open socket server
HOST = '127.0.0.1'
f = open(args.configfile, 'r')
config = json.load(f)
# print(config)
f.close()

for n in config['neighbor_list']:
  globs.NEIGHBORS.append(
    neighbor.Neighbor(n['ip'], n['p2p_port'], n['user_port'])
  )

# print(globs.NEIGHBORS.append)


def main():
  # 建立 node
  # FIXME: 先寫死 transactions
  node = Node(config['target'], config['p2p_port'], config['beneficiary'], [])
  
  # 開 wallet
  wallet = Wallet(config['wallet']['public_key'], config['wallet']['private_key'], config['fee'])

  # 開啟 port listening
  s1 = server.Server(HOST, config['p2p_port'], 'p2p', node, wallet)
  s2 = server.Server(HOST, config['user_port'], 'user', node, wallet)
  t1 = threading.Thread(target=s1.listen)
  t2 = threading.Thread(target=s2.listen)
  t1.start()
  t2.start()
  

  # 不挖礦的情況
  if config['mining'] is False:
    pass
  else:
    # 挖礦前延遲
    # time.sleep(globs.WAIT_SECONDS_BEFORE_MINER) # Wait for socket connection
    time.sleep(config['delay'])
    # 建立礦工
    # 因為 beneficiary 貌似不會更動，所以讓 miner 挖到的每一塊都記錄相同的 beneficiary
    m = miner.Miner('miner', s1, s2, node, config['beneficiary'])
    t3 = threading.Thread(target=m.mine)
    t3.start()

main()
