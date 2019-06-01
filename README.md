# Blockchain HW2

## Quick Start
```

# 開啟節點
$ make run

# 開啟第一個鄰居節點
$ make n1

# 清除資料
$ make clean

```


## File Structure
- main
    1. New a Node
    2. Open first socket server: p2p_port
    3. Open second socket server: user_port
    4. Start mining
- node
    可以視為 blockchain 網路中一個獨立運作的節點, 每個節點可以自己挖礦, 跟別的結點互動或是處理 request
    1. Data structure
        - chain: 為目前此 node 挖到最長的 chain
        - height: chain 的長度
        - trans_pool: transactions pool
        - trans_sig_list: 有過交易的簽名
        - wallet
    2. New a Block (Genesis block)
- block
    - Data structure
        - header
            - version: 目前為第 2 版
            - prev_block
            - transactions_hash
            - target
            - nonce
            - beneficiary
            - transactions: 儲存與這個 block 相關的交易
            - balance: 目前每個 node 錢包的結餘
        - hash
- wallet
    - public key
    - private key
    - fee
- transaction
    - fee
    - nonce
    - sender_pub_key
    - to
    - value
    - wallet
- api
    - List all apis we need
- miner
    - Mining algorithum
- server
    - Open a socket server
    - handling sending request