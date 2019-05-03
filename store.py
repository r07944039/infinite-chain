node = ""
state = ""
count = 0
target = ""
neighbor_list =[]


# Debug function
DEBUG = 1

def debug(s):
    if DEBUG == 1:
        print(s)

# max_count 決定跑幾次後會禮讓(yield)給別人
# 類似於 coroutine 的 priority
MINER_COUNT = 1
P2P_COUNT = 1
USER_COUNT = 1

MINER = 'miner'
P2P = 'p2p'
USER = 'user'

# routine 從這個開始
START_FROM = MINER

# p2p user server 的 select timeout
# 如果等於 none 將會直到有人進來才會繼續
# 這是 blocking 的
select_timeout = 1

routines = {
    MINER: {
        "to": P2P,
        "max_count": MINER_COUNT 
    },
    P2P: {
        "to": USER,
        "max_count": P2P_COUNT
    },
    USER: {
        "to": MINER,
        "max_count": USER_COUNT
    },
}