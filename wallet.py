

'''
    目前先將 wallet 獨立成一個 class
    如果未來發現沒有必要可以合併進 node/transaction
'''
class Wallet():
    def __init__(self, pub, priv, fee):
        self.pub_key = pub
        self.priv_key = priv
        self.fee = fee