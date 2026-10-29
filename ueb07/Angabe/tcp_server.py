#!/usr/bin/env python3

import socket

HOST = "10.0.2.2"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Listening on {HOST}:{PORT}")

    conn, addr = server.accept()
    with conn:
        print("Connection from", addr)
        data = conn.recv(4096)
        print("Received:", data.decode())
        conn.sendall(b"Hello from server")
