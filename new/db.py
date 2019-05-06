import threading

class DB:
    def __init__(self, data):
        self.data = data
        self.lock = threading.Lock()
    
    def get(self, key):
      return self.data[key]

    def set(self, key, val):
      self.lock.acquire()
      self.data[key] = val
      self.lock.release()
