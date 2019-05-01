#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
from termcolor import colored, cprint

import libserver


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        global sel
        sel = selectors.DefaultSelector()


    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        cprint("accepted connection from {}".format(addr), 'magenta', attrs=['bold'])
        conn.setblocking(False)
        message = libserver.Message(sel, conn, addr)
        sel.register(conn, selectors.EVENT_READ, data=message)

    def listen(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print("listening on", (self.host, self.port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
    
    def select(self):
        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()
