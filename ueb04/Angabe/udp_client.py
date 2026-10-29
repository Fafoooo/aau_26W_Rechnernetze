#!/usr/bin/env python3
"""Simple UDP client for Assignment 04."""

import socket
import sys


SERVER = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.2"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
MESSAGE = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Hello from Mininet!"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(2)

try:
    client.sendto(MESSAGE.encode(), (SERVER, PORT))
    print(f"Sent {MESSAGE!r} to {SERVER}:{PORT}")

    data, address = client.recvfrom(4096)
    print(f"Received from {address}: {data.decode(errors='replace')}")
except socket.timeout:
    print("No UDP response received within 2 seconds.")
finally:
    client.close()
