# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: Ü4.3 UDP-Client für eine frei änderbare UTF-8-Nachricht implementieren;
# Defaultziel 10.0.0.2:5000, echte Quelladresse und Nutzlastlänge anzeigen.
"""Ein Datagramm senden; der Server des Aufgabenblatts antwortet nicht."""

import argparse
import socket
import sys


def send(host, port, message, local_host="0.0.0.0", local_port=0):
    payload = message.encode("utf-8")
    if len(payload) > 4096:
        raise ValueError("Empfänger unterstützt höchstens 4096 Nutzbytes")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(3)
        client.bind((local_host, local_port))
        client.connect((host, port))
        sent = client.send(payload)
        if sent != len(payload):
            raise OSError("Datagramm nicht vollständig gesendet")
        address, source_port = client.getsockname()
        print(f"SENT {address}:{source_port} -> {host}:{port} {sent} bytes {payload!r}", flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="10.0.0.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--message", default="Hello from Mininet!")
    parser.add_argument("--local-host", default="0.0.0.0")
    parser.add_argument("--local-port", type=int, default=0)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 0 <= args.local_port <= 65535:
        parser.error("Zielport muss 1..65535, Quellport muss 0..65535 sein")
    try:
        return send(args.host, args.port, args.message, args.local_host, args.local_port)
    except (OSError, ValueError) as error:
        print(f"ERROR client: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
