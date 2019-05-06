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
    def __init__(self, host, port, name):
        self.name = name
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.neighbors = [] # Static neighbors list, not guaranteed to be online
        for n in globs.NEIGHBORS: # Add other neighbors
            if n.p2p_port != port and n.user_port != port:
                self.neighbors.append(n)
        self.buffer_size = 1024
        # keep pinging neighbors
        threading.Thread(target=self.retry_neighbors).start()
        # threading.Thread(target=self.retry_neighbors).start()
        # threading.Thread(target=self.retry_neighbors).start()
        # threading.Thread(target=self.retry_neighbors).start()
        self.apib = api.Broadcast(self)
        self.apir = api.Response(self)

    def handler(self, conn, mask):
        packet = conn.recv(self.buffer_size)  # Should be ready
        if packet:
            data = api.unpack(packet)
            print(data)
            # print('echoing', repr(data), 'to', conn)
            # 開 thread 去 handle
            threading.Thread(target=self.apir.router, args=(conn, data))
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
    
    # loop through all online neighbor and call callback function
    def broadcast(self, callback):
          for n in self.neighbors:
            if n.online == True:
              try:
                callback(n)
              except socket.error as err:
                # DEBUG
                print(str(self.port) + " port: offline: ", n.host, n.p2p_port, n.user_port, ": ", err)
                # n.p2p_sock.close()
                # n.user_sock.close()
                n.online = False
    
    def retry_neighbors(self):
      while True:
        # Try to connect with offline neighbors
        for n in self.neighbors:
          if n.online == False:
            port = 0
            if self.name == P2P:
                port = n.p2p_port
            elif self.name == USER:
                port = n.user_port
            try:
              s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              s.settimeout(2)
              s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
              s.connect((n.host, port))
            except socket.error as err:
              print(self.name + ": retry: " + n.host + ":" + str(port), ": ", err)
              continue
              # if alive
              n.online = True
              n.p2p_sock = s
              n.user_sock = s
              print(str(self.port) + " port: online: ", n.host, n.p2p_port, n.user_port)
        self.broadcast(self.apib.hello)
        time.sleep(globs.HEALTH_CHECK_INTERVAL)
