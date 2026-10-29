# KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.
# Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Auftrag: Ü4.6 TCP-Client für eine oder mehrere CLI-Nachrichten implementieren;
# Echo-Antworten prüfen, UTF-8/LF-Limits beachten und mit Half-Close/FIN schließen.
"""Sende Nachrichten in einer TCP-Verbindung und prüfe jedes Echo exakt."""

import argparse
import math
import socket
import sys

from protocol import ProtocolError, encode_frame, iter_frames


def exchange(host, port, messages, timeout=30.0):
    """Request/Response vermeidet volle Sendepuffer bei vielen Nachrichten."""
    frames = [encode_frame(text) for text in messages]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout)
        connection.connect((host, port))
        replies = iter_frames(connection)
        for expected, frame in zip(messages, frames):
            connection.sendall(frame)
            actual = next(replies, None)
            if actual != expected:
                raise ProtocolError(f"Echo falsch/fehlend: erwartet {expected!r}, erhalten {actual!r}")
            print(f"REPLY {actual!r}", flush=True)
        connection.shutdown(socket.SHUT_WR)
        if next(replies, None) is not None:
            raise ProtocolError("Unerwartete zusätzliche Antwort")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("messages", nargs="+", help="Ein Argument = eine Nachricht; leerer Text: ''")
    parser.add_argument("--host", default="10.0.2.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--timeout", type=float, default=30.0, help="Sekunden pro Socket-Operation")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port muss 1..65535 sein")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Timeout muss endlich und positiv sein")
    try:
        exchange(args.host, args.port, args.messages, args.timeout)
        return 0
    except (OSError, ProtocolError) as error:
        print(f"ERROR client: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
