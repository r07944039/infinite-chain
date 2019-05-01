# Blockchain HW2

## Structure
- Node
    - blocks: 會存一陣列為 blocks，為目前此 node 挖到最長的 chain
    - height: 這個 blocks 有多長
    - socket 部分:
      - P2P port: 
      - user port: 
- Block
    - header
        - version
        - prev_block
        - merkle_root
        - target
        - nonce
    - hash

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