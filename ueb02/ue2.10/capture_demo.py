# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Ü2.10 praktisch bearbeiten: reproduzierbare echte Paketaufzeichnung
# ausschließlich selbst erzeugter harmloser Loopback-HTTP-Kommunikation, mit Tests.
"""Einmaliger lokaler HTTP-Austausch; dumpcap zeichnet nur dessen 4-Tupel auf."""
import argparse
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import threading
import time

BODY = b"RN UE2.10: harmless loopback demo\n"
REQUEST = b"GET /rn-demo HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"


def capture(output):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb"):
        pass
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    process = None
    worker = None
    errors = []
    received = []
    try:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        listener.settimeout(5)
        client.bind(("127.0.0.1", 0))
        client.settimeout(5)
        server_port = listener.getsockname()[1]
        client_port = client.getsockname()[1]
        capture_filter = (
            f"ip and tcp and src host 127.0.0.1 and dst host 127.0.0.1 and "
            f"((src port {client_port} and dst port {server_port}) or "
            f"(src port {server_port} and dst port {client_port}))"
        )
        command = ["sudo", "-n", "dumpcap", "-i", "lo", "-p", "-F", "pcap", "-f",
                   capture_filter, "-a", "duration:3", "-w", "-"]
        with output.open("wb") as capture_file:
            process = subprocess.Popen(command, stdout=capture_file,
                                       stderr=subprocess.PIPE)
        assert process.stderr is not None
        startup = bytearray()
        deadline = time.monotonic() + 5
        while b"Capturing on" not in startup:
            if process.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError("dumpcap nicht bereit: " + startup.decode(errors="replace"))
            if select.select([process.stderr], [], [], 0.1)[0]:
                startup.extend(os.read(process.stderr.fileno(), 4096))
        time.sleep(0.2)

        def serve():
            try:
                connection, address = listener.accept()
                with connection:
                    connection.settimeout(3)
                    request = bytearray()
                    while b"\r\n\r\n" not in request:
                        part = connection.recv(4096)
                        if not part or len(request) > 8192:
                            raise RuntimeError("Unvollständige/zu lange HTTP-Anfrage")
                        request.extend(part)
                    if address[0] != "127.0.0.1" or bytes(request) != REQUEST:
                        raise RuntimeError("Unerwartete Anfrage")
                    response = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
                                + f"Content-Length: {len(BODY)}\r\n".encode()
                                + b"Connection: close\r\n\r\n" + BODY)
                    connection.sendall(response)
            except Exception as error:
                errors.append(repr(error))

        worker = threading.Thread(target=serve, name="rn-loopback-http")
        worker.start()
        client.connect(("127.0.0.1", server_port))
        client.sendall(REQUEST)
        while True:
            part = client.recv(4096)
            if not part:
                break
            received.append(part)
        client.close()
        worker.join(timeout=5)
        if worker.is_alive() or errors:
            raise RuntimeError(f"Serverfehler: {errors}")
        response = b"".join(received)
        if not response.startswith(b"HTTP/1.1 200 OK\r\n") or not response.endswith(BODY):
            raise RuntimeError("Falsche HTTP-Antwort")
        remaining = process.communicate(timeout=8)[1]
        log = (bytes(startup) + remaining).decode(errors="replace")
        if process.returncode != 0 or output.stat().st_size <= 24:
            raise RuntimeError(log)
        return {"output": str(output), "server_port": server_port,
                "client_port": client_port, "capture_filter": capture_filter,
                "response_bytes": len(response), "body": BODY.decode(),
                "command": command, "dumpcap_log": log}
    finally:
        client.close()
        listener.close()
        if worker is not None:
            worker.join(timeout=6)
        if process is not None and process.poll() is None:
            try:
                process.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                subprocess.run(["sudo", "-n", "kill", "-INT", str(process.pid)],
                               check=True, timeout=3)
                process.communicate(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("eigene_aufzeichnung.pcap"))
    arguments = parser.parse_args()
    result = capture(arguments.output)
    metadata = arguments.output.with_suffix(".json")
    metadata.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
