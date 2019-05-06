import selectors
import socket
import pickle
import time
import threading
import neighbor
import globs
import api

P2P = 'p2p'
USER = 'user'

class Server:
    def __init__(self, host, port, name, node):
        self.name = name
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.neighbors = [] # Static neighbors list, not guaranteed to be online
        for n in globs.NEIGHBORS: # Add other neighbors
            if n.p2p_port != port and n.user_port != port:
                self.neighbors.append(n)
        self.buffer_size = 4096
        # 這不用 thread 在 test connection 還是會被 block 住
        # threading.Thread(target=self.try_neighbors_sock).start()
        # time.sleep(3)
        self.apib = api.Broadcast(self)
        self.apir = api.Response(self)
        # keep pinging neighbors
        threading.Thread(target=self.retry_neighbors).start()
        self.node = node

    def handler(self, conn, mask):
        packet = conn.recv(self.buffer_size)  # Should be ready
        if packet:
            data = api.unpack(packet)
            threading.Thread(target=self.apir.router, args=(conn, data,)).start()
        else:
            # print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

    def accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        # print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.handler)

    def listen(self):
      lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      lsock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      lsock.bind((self.host, self.port))
      lsock.listen(10)
      print('listening on', (self.host, self.port))
      lsock.setblocking(False)
      self.sel.register(lsock, selectors.EVENT_READ, self.accept)
      while True:
        events = self.sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
    
    def broadcast_hanlder(self, callback, n, arg):
      try:
        callback(n, arg)
      except socket.error as err:
        # DEBUG
        print("new offline: ", n.host, n.p2p_port, ": ", err)
        n.p2p_sock = None
        n.online = False

    # loop through all online neighbor and call callback function
    def broadcast(self, callback, arg):
        for n in self.neighbors:
          if n.online == True and self.name == P2P and n.p2p_sock != None:
            threading.Thread(
              target=self.broadcast_hanlder,
              args=(callback, n, arg,)
            ).start()
    
    # def send_to(self, callback, host, port, arg):
    #   for n in self.neighbors:
    #     if n.host == host and n.user_port == port and n.user_sock != None:
    #       threading.Thread(target=callback, args=(n, arg,)).start()
      
    
    def try_neighbors_sock(self):
      for n in self.neighbors:
        if self.name == P2P and n.p2p_sock == None:
          n.p2p_sock = self.try_p2p(n)
          # print(self.name + ": check online: ", n.host, n.p2p_sock)
        elif self.name == USER and n.user_sock == None:
          n.user_sock = self.try_user(n)
          # print(self.name + ": check online: ", n.host, n.user_sock)
        if n.p2p_sock != None or n.user_sock != None:
          n.online = True
    
    def try_p2p(self, n):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(5)
      s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      try:
        s.connect((n.host, n.p2p_port))
      except socket.error as err:
        # print(self.name + ": retry: " + n.host + ":" + str(n.p2p_port), ": ", err)
        return None
      return s
    
    def try_user(self, n):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(5)
      s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      try:
        s.connect((n.host, n.user_port))
      except socket.error as err:
        # print(self.name + ": retry: " + n.host + ":" + str(n.user_port), ": ", err)
        return None
      return s

    def retry_neighbors(self):
      while True:
        # Try to connect with offline neighbors
        self.try_neighbors_sock()
        time.sleep(globs.HEALTH_CHECK_INTERVAL)
