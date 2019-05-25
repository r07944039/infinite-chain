import hashlib
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

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
        
        # SECP256k1 is the Bitcoin elliptic curve
        sk = SigningKey.from_pem(wallet.priv_key)
        # vk = sk.get_verifying_key()
        self.signature = sk.sign(self.msg)
        # vk.verify(sig, b"message") # True


    def get_transaction(self):
        return {
            "fee": self.fee,
            "nonce": self.nonce,
            "sender_pub_key": self.sender_pub_key,
            "signature": self.signature,
            "to": self.to,
            "value": self.value
        }

    def verify_signature(self, trans):
        vk = VerifyingKey.from_pem(trans.sender_pub_key)
        try:
            vk.verify(trans.signature, trans.msg)
            return True
        except BadSignatureError:
            return False
