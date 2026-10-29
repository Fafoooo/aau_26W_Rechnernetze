#!/usr/bin/env python3
"""TCP server reused for Assignment 06 end-to-end experiments."""

import socket

HOST = "10.0.2.2"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print("Connection from", addr)

        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                print(f"Received {len(data)} bytes")
                conn.sendall(data)
