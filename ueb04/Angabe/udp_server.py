#!/usr/bin/env python3
"""Simple UDP server for Assignment 04."""

import socket
import sys


HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.2"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"UDP server listening on {HOST}:{PORT}")
print("Press Ctrl+C to stop.")

try:
    while True:
        data, address = server.recvfrom(4096)
        print(f"Received from {address}: {data!r}")
        server.sendto(b"ACK: " + data, address)
except KeyboardInterrupt:
    print("\nServer stopped.")
finally:
    server.close()
