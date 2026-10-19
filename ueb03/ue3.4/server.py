# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 multi-thread mit persistenten Verbindungen und zentralem 5s-Logger.
"""Absichtlich kleiner, sequenzieller HTTP/0.9-Dateiserver (nur POSIX)."""
import argparse
import os
from pathlib import Path
import signal
import socket
import stat
import time
from urllib.parse import unquote_to_bytes


MAX_LINE = 8192


def open_resource(root, target):
    """Öffne nur reguläre Dateien unter root, ohne Symlinks zu verfolgen."""
    if not target.startswith('/') or '#' in target:
        raise ValueError('Erwartet wird ein absoluter URL-Pfad ohne Fragment')
    encoded = target.split('?', 1)[0]
    # unquote akzeptiert sonst auch kaputte %-Sequenzen unverändert.
    digits = '0123456789abcdefABCDEF'
    for index, char in enumerate(encoded):
        if char == '%' and (len(encoded[index + 1:index + 3]) != 2 or
                            any(c not in digits for c in encoded[index + 1:index + 3])):
            raise ValueError('Ungültige Prozentkodierung')
    path = unquote_to_bytes(encoded).decode('utf-8', errors='strict')
    if any(ord(c) < 32 or ord(c) == 127 for c in path) or '\\' in path:
        raise ValueError('Unzulässiges Zeichen im Pfad')
    parts = [part for part in path.split('/') if part not in ('', '.')]
    if '..' in parts:
        raise ValueError('Verzeichnisausbruch')
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        # openat + O_NOFOLLOW verhindert auch Symlink-Rennen beim Öffnen.
        for index, part in enumerate(parts):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            if index < len(parts) - 1 or path.endswith('/'):
                flags |= os.O_DIRECTORY
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        index_used = stat.S_ISDIR(os.fstat(descriptor).st_mode)
        if index_used:
            child = os.open('index.html', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                            dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError('Keine reguläre Datei')
        result = os.fdopen(descriptor, 'rb')
        setattr(result, 'resource_name', 'index.html' if index_used else parts[-1])
        descriptor = None
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)


def read_request(connection, timeout):
    """TCP liefert Stücke, keine Zeilen: bis CRLF sammeln, aber begrenzen."""
    deadline = time.monotonic() + timeout
    data = bytearray()
    while b'\r\n' not in data:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Anfragefrist überschritten')
        connection.settimeout(remaining)
        chunk = connection.recv(min(1024, MAX_LINE + 2 - len(data)))
        if not chunk:
            raise ValueError('Unvollständige Anfrage')
        data.extend(chunk)
        if len(data.split(b'\r\n', 1)[0]) > MAX_LINE:
            raise ValueError('Anfrage zu lang')
    line, extra = bytes(data).split(b'\r\n', 1)
    if extra:
        raise ValueError('HTTP/0.9 hat keine Header und keine Pipeline')
    method, target = line.decode('ascii').split(' ')
    if method != 'GET' or not target:
        raise ValueError('Nur GET /pfad CRLF, ohne Versionsfeld')
    return target


def handle_client(connection, root, timeout):
    """Im aufrufenden Thread: lesen, Datei binär senden, immer schließen."""
    with connection:
        try:
            target = read_request(connection, timeout)
            with open_resource(root, target) as resource:
                connection.settimeout(timeout)
                while chunk := resource.read(65536):
                    connection.sendall(chunk)
        except (OSError, ValueError, UnicodeError):
            # Bei Fehlern weder Statuszeile noch Header oder Fehlertext senden.
            pass


def serve(root, host='127.0.0.1', port=80, timeout=5.0, ready=None, stop=None):
    """Keine Worker: ein langsamer Client blockiert alle nachfolgenden."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('DocumentRoot muss ein Verzeichnis sein')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(32)
        listener.settimeout(0.2)
        if ready is not None:
            ready(listener.getsockname())
        while stop is None or not stop.is_set():
            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            handle_client(connection, root, timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document_root', type=Path)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--timeout', type=float, default=5.0)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535 or not 0 < args.timeout < float('inf'):
        parser.error('Port muss 0..65535 und Timeout endlich und positiv sein')
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        serve(args.document_root, args.host, args.port, args.timeout,
              ready=lambda address: print(f'HTTP/0.9 auf {address[0]}:{address[1]}', flush=True))
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError) as error:
        parser.exit(1, f'Startfehler: {error}\n')


if __name__ == '__main__':
    main()
