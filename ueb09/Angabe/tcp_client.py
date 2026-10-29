
#!/usr/bin/env python3
import socket
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.10.2.10"
PORT = 5000

with socket.create_connection((HOST, PORT), timeout=5) as s:
    print(s.recv(4096).decode(errors="replace"), end="")
