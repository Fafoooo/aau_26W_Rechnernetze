
#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        with conn:
            print("Connection from", addr)
            conn.sendall(b"RN-Lab forensic test server\n")
