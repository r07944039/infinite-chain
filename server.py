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
    def __init__(self, host, port, name, node, wallet):
        self.name = name
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.neighbors = [] # Static neighbors list, not guaranteed to be online
        for n in globs.NEIGHBORS: # Add other neighbors
            if n.p2p_port != port and n.user_port != port:
                self.neighbors.append(n)
        self.buffer_size = globs.DEFAULT_SOCK_BUFFER_SIZE
        # 這不用 thread 在 test connection 還是會被 block 住
        # threading.Thread(target=self.try_neighbors_sock).start()
        # time.sleep(3)
        self.apib = api.Broadcast(self)
        self.apir = api.Response(self)
        # keep pinging neighbors
        threading.Thread(target=self.__retry_neighbors).start()
        self.node = node
        # self.wallet = wallet
        # loop through all online neighbor and call callback function
    def broadcast(self, callback, arg):
      for n in self.neighbors:
        # 原本只允許 P2P port 來用這隻 api
        # 但發現這樣在 sendtoaddress call sendTransaction 的時候會 self.name 會 == user
        # 所以先把它註解掉
        if n.online == True and n.p2p_sock != None:
        # if n.online == True and self.name == P2P and n.p2p_sock != None:
          threading.Thread(
            target=self.__sock_broadcast_handler,
            args=(callback, n, arg,)
          ).start()

    # 會等收到回應後才做事的 broadcast
    # 為了在 mine 到 block 後可以給別人做檢查寫的
    def block_broadcast(self, callback, arg):
      for n in self.neighbors:
        if n.online == True and self.name == P2P and n.p2p_sock != None:
          self.__sock_broadcast_handler(callback, n, arg)
          # 在這邊基本上 neighbor 只會有一個所以這個 for 迴圈應該只會執行一次
          # 所以在發現大家都沒有在線上的狀況應該要回傳 False 
          # 就不用跟別人比較就能 add new block
          return True
        else:
          return False
      
    
    def send_to(self, callback, host, port, arg):
      for n in self.neighbors:
        if (n.online == True and self.name == USER
        and n.host == host and n.user_port == port
        and n.user_sock != None):
          threading.Thread(
            target=self.__sock_send_to_handler,
            args=(callback, n, arg,)
          ).start()
    
    def listen(self):
      lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      lsock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      lsock.bind((self.host, self.port))
      lsock.listen(globs.BACKLOG_SIZE)
      print('listening on', (self.host, self.port))
      lsock.setblocking(False)
      self.sel.register(lsock, selectors.EVENT_READ, self.__accept)
      while True:
        events = self.sel.select()
        for key, mask in events:
          callback = key.data
          callback(key.fileobj, mask)

    def __accept_handler(self, conn, mask):
        packet = conn.recv(self.buffer_size)  # Should be ready
        if packet:
            data = api.unpack(packet)
            threading.Thread(target=self.apir.router, args=(conn, data,)).start()
        else:
            # print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

    def __accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        # print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.__accept_handler)
    
    def __sock_broadcast_handler(self, callback, n, arg):
      try:
        callback(n, arg)
      except socket.error as err:
        # DEBUG
        print("offline: ", n.host, n.p2p_port, ": ", err)
        n.p2p_sock = None
        n.online = False
    
    def __sock_send_to_handler(self, callback, n, arg):
      try:
        callback(n, arg)
      except socket.error as err:
        # DEBUG
        print("offline: ", n.host, n.user_port, ": ", err)
        n.user_sock = None
        n.online = False
    
    def __try_neighbors_sock(self):
      for n in self.neighbors:
        if self.name == P2P and n.p2p_sock == None:
          n.p2p_sock = self.__try_p2p(n)
          # print(self.name + ": check online: ", n.host, n.p2p_sock)
        elif self.name == USER and n.user_sock == None:
          n.user_sock = self.__try_user(n)
          # print(self.name + ": check online: ", n.host, n.user_sock)
        if n.p2p_sock != None or n.user_sock != None:
          n.online = True
    
    def __try_p2p(self, n):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(globs.RETRY_TIMEOUT)
      s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      try:
        s.connect((n.host, n.p2p_port))
      except socket.error as err:
        # print(self.name + ": retry: " + n.host + ":" + str(n.p2p_port), ": ", err)
        return None
      return s
    
    def __try_user(self, n):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(globs.RETRY_TIMEOUT)
      s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
      try:
        s.connect((n.host, n.user_port))
      except socket.error as err:
        # print(self.name + ": retry: " + n.host + ":" + str(n.user_port), ": ", err)
        return None
      return s

    def __retry_neighbors(self):
      while True:
        # Try to connect with offline neighbors
        self.__try_neighbors_sock()
        time.sleep(globs.HEALTH_CHECK_INTERVAL)
