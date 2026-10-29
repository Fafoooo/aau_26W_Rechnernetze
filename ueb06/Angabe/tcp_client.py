#!/usr/bin/env python3
"""TCP client reused for Assignment 06 end-to-end experiments."""

import socket

SERVER = "10.0.2.2"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((SERVER, PORT))
    print(f"Connected to {SERVER}:{PORT}")

    for message in [
        b"Network layer test 1\n",
        b"Network layer test 2\n",
        b"Network layer test 3\n",
    ]:
        client.sendall(message)
        print("Reply:", client.recv(4096))
