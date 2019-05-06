import time

class Miner:
  def __init__(self, name, p2pserver, userserver, node):
    self.name = name
    self.p2p = p2pserver
    self.user = userserver
    self.node = node
  
  def mine(self):
    while True:
      # keep mining
      # print(self.p2p.neighbors)
      self.p2p.broadcast(self.p2p.apib.hello, {})
      print('mined!!')
      time.sleep(1)