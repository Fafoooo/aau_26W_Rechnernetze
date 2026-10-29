# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: Ü4.3 UDP-Beispiel aus dem Blatt als testbaren Server mit CLI,
# begrenzter Datagrammzahl und Timeout umsetzen; Standard 10.0.0.2:5000.
"""UDP-Empfänger ohne Antwort, entsprechend dem Beispiel im Aufgabenblatt."""

import argparse
import math
import socket
import sys


def serve(host, port, count, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.settimeout(timeout)
        server.bind((host, port))
        address, actual_port = server.getsockname()
        print(f"READY {address}:{actual_port}", flush=True)
        received = 0
        while count == 0 or received < count:
            data, peer = server.recvfrom(4096)
            print(f"RECEIVED {peer[0]}:{peer[1]} {data!r}", flush=True)
            received += 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="10.0.0.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--count", type=int, default=0, help="0: bis Timeout/Abbruch")
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535 or args.count < 0:
        parser.error("Port muss 0..65535 und count >= 0 sein")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout muss endlich und positiv sein")
    try:
        return serve(args.host, args.port, args.count, args.timeout)
    except OSError as error:
        print(f"ERROR server: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
