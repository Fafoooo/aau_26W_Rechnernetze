#!/usr/bin/env python3

import socket

SERVER = ("10.0.2.2", 5000)

with socket.create_connection(SERVER) as sock:
    sock.sendall(b"Hello from client")
    print(sock.recv(4096).decode())
