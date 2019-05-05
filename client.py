#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json

import libclient


def load_json(query):
    q = json.loads(query)
    # print(q)
    method = q["method"]
    if 'data' in q:
        value = q["data"]
    else:
        value = None
        
    # print(method, value)

    return method, value

def load_json_h(query):
    q = json.loads(query)
    # print(q)
    method = q["method"]
    node = q["node"]
    if 'data' in q:
        value = q["data"]
    else:
        value = None
        
    # print(method, value)

    return method, value, node

def create_request(method, value):
    # if method is not None:
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(method=method, value=value),
    )
    # else:
    #     return dict(
    #         type="binary/custom-client-binary-type",
    #         encoding="binary",
    #         content=bytes(method + value, encoding="utf-8"),
    #     )

def create_request_h(method, value, node):
    # if method is not None:
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(method=method, value=value, node=node),
    )
    # else:
    #     return dict(
    #         type="binary/custom-client-binary-type",
    #         encoding="binary",
    #         content=bytes(method + value, encoding="utf-8"),
    #     )


def start_connection(host, port, request, sel):
    addr = (host, port)
    print("===========================================")
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)
    return message


# if len(sys.argv) != 4:
#     print("usage:", sys.argv[0], "<host> <port> <json_request>")
#     sys.exit(1)

# print((sys.argv))
def send_socket_req(host, port, query):
    sel = selectors.DefaultSelector()
    method, value = load_json(query)
    request = create_request(method, value)
    start_connection(host, port, request, sel)
    # print(request)
    select(sel)

def send_header(host, port, query):
    sel = selectors.DefaultSelector()
    method, value, node = load_json_h(query)
    request = create_request_h(method, value, node)
    print(request)
    msg = start_connection(host, port, request, sel)
    result = msg.write()
    # print(result)
    sel.close()

    return result
    # print(request)
    # select(sel)

def select(sel):
    try:
        while True:
            events = sel.select(timeout=None)
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