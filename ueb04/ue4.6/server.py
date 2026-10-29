# KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.
# Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Auftrag: Ü4.6 TCP-Echo-Server auf 10.0.2.2:5000 mit persistenten Nachrichten,
# READY-Ausgabe, CLI, begrenzten Verbindungen, Timeouts und sauberem Schließen.
"""Sequentieller IPv4-TCP-Server; ein Client nach dem anderen, ohne Threads."""

import argparse
import math
import socket
import sys

from protocol import ProtocolError, encode_frame, iter_frames


def serve(host, port, connections, timeout):
    """Zähle angenommene Verbindungen; 0 bedeutet Betrieb bis Timeout/Abbruch."""
    failed = False
    accepted = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.settimeout(timeout)
        listener.bind((host, port))
        listener.listen(5)
        address, actual_port = listener.getsockname()
        print(f"READY {address}:{actual_port}", flush=True)
        while connections == 0 or accepted < connections:
            connection, peer = listener.accept()
            accepted += 1
            with connection:
                connection.settimeout(timeout)
                try:
                    for text in iter_frames(connection):
                        print(f"RECEIVED {peer[0]}:{peer[1]} {text!r}", flush=True)
                        connection.sendall(encode_frame(text))
                    connection.shutdown(socket.SHUT_WR)
                except (OSError, ProtocolError) as error:
                    failed = True
                    print(f"ERROR connection: {error}", file=sys.stderr, flush=True)
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="10.0.2.2")
    parser.add_argument("--port", type=int, default=5000, help="0: freier Testport")
    parser.add_argument("--connections", type=int, default=0, help="0: unbegrenzt")
    parser.add_argument("--timeout", type=float, default=30.0, help="Sekunden pro Socket-Operation")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535 or args.connections < 0:
        parser.error("Port muss 0..65535, connections muss >= 0 sein")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout muss endlich und positiv sein")
    try:
        return serve(args.host, args.port, args.connections, args.timeout)
    except OSError as error:
        print(f"ERROR server: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
