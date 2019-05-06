class Neighbor:
    def __init__(self, host, p2p_port, user_port):
        self.name = ""
        self.host = host
        self.p2p_port = p2p_port
        self.user_port = user_port
        self.p2p_sock = None # socket object used for send recv
        self.user_sock = None
        self.online = False