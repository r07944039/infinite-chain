node = ""
state = ""
count = 0

# max_count 決定跑幾次後會禮讓(yield)給別人
# 類似於 coroutine 的 priority
MINER_COUNT = 100 
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
select_timeout = 0.05

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