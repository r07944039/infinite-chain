# Blockchain HW2

## File Structure
- main
    1. New a Node
    2. Open first socket server: p2p_port
    3. Open second socket server: user_port
    4. Start mining
    5. Scheduling through 2.3.4.
- store
    - Store all elements we need:
        1. Current node and its state
        2. Scheduling parameters
- node
    1. Data structure
        - blocks: 會存一陣列為 blocks，為目前此 node 挖到最長的 chain
        - height: 這個 blocks 有多長
    2. New a Block (Genesis block)
- block
    - Data structure
        - header
            - version
            - prev_block
            - merkle_root
            - target
            - nonce
        - hash
- api
    - List all apis we need
- miner
    - Mining algorithum
- server
    - Open a socket server with libserver

## TODOs
- 需要一個 Json parser
- 做完 p2p 相關的 APIs
- 做完 user 相關的 APIs
- 其他 APIs
- socket
- 整個 network boardcast 的問題

## Note
- 為什麼 height 不放在 block 裡面？
    因為一開始要判斷是否為創世區塊時會不方便
    暫時先把 height 放在 Node 裡面