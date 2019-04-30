#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json

import libclient

sel = selectors.DefaultSelector()


def load_json(query):
    q = json.loads(query)
    # print(q)
    method = q["method"]
    value = q["data"]
    # print(method, value)

    return method, value

# TODO
def create_request(method, value):
    if method == "getBlockHash":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(method=method, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(method + value, encoding="utf-8"),
        )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <json_request>")
    sys.exit(1)

print((sys.argv))
host, port = sys.argv[1], int(sys.argv[2])
query = sys.argv[3]
# method, value = sys.argv[3], sys.argv[4]
method, value = load_json(query)
request = create_request(method, value)
start_connection(host, port, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()