import hashlib
from ecdsa import SigningKey, VerifyingKey, BadSignatureError, SECP256k1

def sha256(data):
    m = hashlib.sha256()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Transaction():
    def __init__(self, fee, nonce, sender_pub_key, to, value, wallet):
        self.fee = fee
        self.nonce = nonce 
        self.sender_pub_key = sender_pub_key
        self.to = to
        self.value = value
        self.msg = sha256(self.nonce + self.sender_pub_key + self.to + self.value + self.fee)
        
        sk = SigningKey.from_string(bytes.fromhex(wallet.priv_key), curve=SECP256k1)
        self.signature = sk.sign(bytes(self.msg,'utf-8')).hex()

    def get_transaction(self):
        return {
            "fee": self.fee,
            "nonce": self.nonce,
            "sender_pub_key": self.sender_pub_key,
            "signature": self.signature,
            "to": self.to,
            "value": self.value
        }

    def verify_signature(self):
        vk = VerifyingKey.from_string(bytes.fromhex(self.sender_pub_key), curve=SECP256k1)
        try:
            vk.verify(bytes.fromhex(self.signature), bytes(self.msg,'utf-8'))
            return True
        except BadSignatureError:
            return False
