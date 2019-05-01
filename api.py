# p2p_port
# broadcast API
def sendHeader(self, block_hash, block_header, block_height):
    error = 0
    result = ""

    return error

def getBlocks(self, hash_count, hash_begin, hash_stop):
    error = 0
    result = ""

    return error, result

# user_port
# Non broadcast API
def getBlockCount(self):
    if self == None:
        error = 1
        result = 0
    else:
        error = 0
        result = self.height

    return error, result

def getBlockHash(self, block_height):
    if block_height != None:
        # os.system('python3 socket/app-client.py {} {}'.format(HOST, P2P_PORT))
        result = self.chain[block_height].block_hash
        error = 0
    else:
        result = 0
        error = 1

    return result

# 目前我只想得到 O(n) 直接去暴力搜那個 hash 在哪裡 QQ
def getBlockHeader(self, block_hash):
    for block in self.chain:
        if block.block_hash == block_hash:
            error = 0
            result = block.block_header
            return error, result
    
    error = 1
    result = 0
    return error, result      