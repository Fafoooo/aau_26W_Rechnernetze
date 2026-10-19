# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 multi-thread mit persistenten Verbindungen und zentralem 5s-Logger.
"""HTTP/1.0: eigener Worker je Request, geordnete Pipeline, Queue-Logger."""
import argparse
from dataclasses import dataclass
from datetime import datetime
from email.utils import formatdate
import importlib.util
import json
import mimetypes
import os
from pathlib import Path
import queue
import re
import signal
import socket
import sys
import threading
import time
from zoneinfo import ZoneInfo


# Die sicherheitskritische Dateiöffnung wird unverändert aus Ü3.4 verwendet.
_spec = importlib.util.spec_from_file_location('rn_http09', Path(__file__).parents[1] / 'ue3.4' / 'server.py')
assert _spec is not None and _spec.loader is not None
_http09 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_http09)
open_resource = _http09.open_resource
REASONS = {200: 'OK', 400: 'Bad Request', 403: 'Forbidden', 404: 'Not Found',
           405: 'Method Not Allowed', 408: 'Request Timeout', 414: 'URI Too Long',
           431: 'Request Header Fields Too Large', 500: 'Internal Server Error',
           505: 'HTTP Version Not Supported'}
TOKEN = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
# Nur bekannte Kommalisten vereinigen; insbesondere nie Host/Content-Length.
LIST_HEADERS = frozenset({'accept', 'accept-charset', 'accept-encoding',
                          'accept-language', 'allow', 'connection', 'pragma'})
VIENNA = ZoneInfo('Europe/Vienna')


class HTTPError(Exception):
    def __init__(self, status, method='INVALID', legacy=False):
        self.status = status
        self.method = method
        self.legacy = legacy
        super().__init__(REASONS[status])


@dataclass(frozen=True)
class Request:
    method: str
    target: str
    keep_alive: bool
    legacy: bool = False


class Reader:
    """Ein Puffer pro Verbindung erhält bereits empfangene Pipeline-Bytes."""
    def __init__(self, connection, timeout):
        self.connection = connection
        self.timeout = timeout
        self.buffer = b''

    def read(self):
        deadline = time.monotonic() + self.timeout
        while True:
            end = self.buffer.find(b'\r\n\r\n')
            first = self.buffer.split(b'\r\n', 1)[0]
            first_end = self.buffer.find(b'\r\n')
            legacy = first_end >= 0 and len(first.split(b' ')) == 2
            if len(first) > 8192:
                raise HTTPError(414, legacy=legacy)
            # Simple-Request endet bereits nach einer Zeile (RFC 1945 §3.1).
            if legacy:
                request = parse_request(first, legacy=True)
                if self.buffer[first_end + 2:]:
                    raise HTTPError(400, request.method, legacy=True)
                self.buffer = b''
                return request
            if (end < 0 and len(self.buffer) > 16384) or end > 16384:
                raise HTTPError(431)
            if end >= 0:
                block, self.buffer = self.buffer[:end], self.buffer[end + 4:]
                return parse_request(block)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise HTTPError(408)
            self.connection.settimeout(remaining)
            try:
                chunk = self.connection.recv(4096)
            except socket.timeout as error:
                raise HTTPError(408) from error
            if not chunk:
                if self.buffer:
                    raise HTTPError(400)
                return None
            self.buffer += chunk


def parse_request(block, legacy=False):
    # Header-TEXT erlaubt ISO-8859-1; die Requestzeile bleibt strikt ASCII.
    lines = block.decode('latin-1').split('\r\n')
    words = lines[0].split(' ')
    method = words[0] if words and TOKEN.fullmatch(words[0]) else 'INVALID'
    if legacy:
        if (len(lines) != 1 or len(words) != 2 or method != 'GET' or
                not lines[0].isascii() or not words[1].startswith('/') or
                any(ord(c) <= 32 or ord(c) == 127 for c in words[1])):
            raise HTTPError(400, method, legacy=True)
        return Request(method, words[1], False, legacy=True)
    if not lines[0].isascii():
        raise HTTPError(400, method)
    if len(words) != 3 or not TOKEN.fullmatch(words[0]):
        raise HTTPError(400, method)
    method, target, version = words
    if version not in ('HTTP/1.0', 'HTTP/1.1'):
        raise HTTPError(505, method)
    if not target.startswith('/') or any(ord(c) <= 32 or ord(c) == 127 for c in target):
        raise HTTPError(400, method)
    if len(lines) > 101:
        raise HTTPError(431, method)
    headers = {}
    for line in lines[1:]:
        name, separator, value = line.partition(':')
        if not separator or not TOKEN.fullmatch(name):
            raise HTTPError(400, method)
        if any((ord(c) < 32 and c != '\t') or ord(c) == 127 for c in value):
            raise HTTPError(400, method)
        name, value = name.lower(), value.strip(' \t')
        # RFC 1945 §4.2: Listen in Empfangsreihenfolge zusammenführen.
        if name in headers:
            if name not in LIST_HEADERS:
                raise HTTPError(400, method)
            value = headers[name] + ', ' + value
        headers[name] = value
    if version == 'HTTP/1.1' and not headers.get('host'):
        raise HTTPError(400, method)
    if 'transfer-encoding' in headers:
        raise HTTPError(400, method)
    length = headers.get('content-length', '0')
    # Ohne Request-Body-Unterstützung sind nur explizite Null-Längen erlaubt.
    if not length or not length.isascii() or not length.isdecimal() or length.strip('0'):
        raise HTTPError(400, method)
    options = [item.strip().lower() for item in headers.get('connection', '').split(',')]
    return Request(method, target, 'keep-alive' in options and 'close' not in options)


class AccessLogger:
    """Nur dieser Thread schreibt JSON-Zeilen; Queue ist die Übergabe."""
    def __init__(self, stream, interval=5.0):
        self.stream = stream
        self.interval = interval
        self.entries = queue.Queue()
        self.thread = threading.Thread(target=self.run, name='access-logger')

    def start(self):
        self.thread.start()

    def record(self, method, address, status):
        self.entries.put({'timestamp': datetime.now(VIENNA).isoformat(timespec='milliseconds'),
                          'method': method, 'ip': address[0], 'port': address[1],
                          'status': status, 'worker': threading.current_thread().name})

    def run(self):
        pending = []
        deadline = time.monotonic() + self.interval
        while True:
            remaining = max(0.0, deadline - time.monotonic())
            try:
                entry = self.entries.get(timeout=remaining)
            except queue.Empty:
                entry = 'TICK'
            if entry is None:
                self.flush(pending)
                return
            if entry != 'TICK':
                pending.append(entry)
            if time.monotonic() >= deadline:
                self.flush(pending)
                pending.clear()
                deadline = time.monotonic() + self.interval

    def flush(self, entries):
        for entry in entries:
            self.stream.write(json.dumps(entry, ensure_ascii=True) + '\n')
        self.stream.flush()

    def close(self):
        self.entries.put(None)
        self.thread.join()


def respond(connection, request, root, keep_alive, timeout, error=None):
    """Eine Antwort mit exakter Byte-Länge, auch HEAD und Fehler."""
    status = error or (200 if request.method in ('GET', 'HEAD') else 405)
    resource = None
    content_type = 'text/plain; charset=utf-8'
    try:
        if status == 200:
            try:
                resource = open_resource(root, request.target)
                content_type = mimetypes.guess_type(getattr(resource, 'resource_name'))[0]
                content_type = content_type or 'application/octet-stream'
            except FileNotFoundError:
                status = 404
            except (PermissionError, ValueError, UnicodeError):
                status = 403
            except OSError:
                status = 403
        body = f'{status} {REASONS[status]}\n'.encode('utf-8')
        # Simple-Response: nur Datei, auch bei Fehlern keinerlei Statusbytes.
        if request.legacy and status != 200:
            return status
        length = os.fstat(resource.fileno()).st_size if resource else len(body)
        headers = [f'HTTP/1.0 {status} {REASONS[status]}', f'Date: {formatdate(usegmt=True)}',
                   f'Content-Length: {length}',
                   f'Content-Type: {content_type}',
                   'Connection: keep-alive' if keep_alive else 'Connection: close']
        if keep_alive:
            headers.append(f'Keep-Alive: timeout={max(1, int(timeout))}')
        if status == 405:
            headers.append('Allow: GET, HEAD')
        connection.settimeout(timeout)
        if not request.legacy:
            connection.sendall(('\r\n'.join(headers) + '\r\n\r\n').encode('ascii'))
        if request.method != 'HEAD':
            if resource:
                # Beschränken verhindert Framingfehler, wenn eine Datei wächst.
                remaining = length
                while remaining:
                    chunk = resource.read(min(65536, remaining))
                    if not chunk:
                        raise OSError('Datei während der Übertragung verkürzt')
                    connection.sendall(chunk)
                    remaining -= len(chunk)
            else:
                connection.sendall(body)
        return status
    finally:
        if resource:
            resource.close()


class HTTPServer:
    def __init__(self, root, host='127.0.0.1', port=80, timeout=5.0,
                 max_requests=100, max_clients=64, log_stream=None, log_interval=5.0):
        self.root = Path(root).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError('DocumentRoot muss ein Verzeichnis sein')
        if not 0 < timeout < float('inf') or max_requests < 1 or max_clients < 1:
            raise ValueError('Timeout und Limits müssen positiv sein')
        self.host, self.port, self.timeout = host, port, timeout
        self.max_requests = max_requests
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.connections = set()
        self.readers = set()
        self.slots = threading.BoundedSemaphore(max_clients)
        self.logger = AccessLogger(sys.stdout if log_stream is None else log_stream, log_interval)

    def worker(self, connection, address, request, keep_alive, result, error):
        status = error or 500
        try:
            status = respond(connection, request, self.root, keep_alive, self.timeout, error)
            result.append(True)
        except (OSError, ValueError):
            result.append(False)
        finally:
            self.logger.record(request.method, address, status)

    def client(self, connection, address):
        try:
            with connection:
                reader = Reader(connection, self.timeout)
                for number in range(self.max_requests):
                    if self.stop.is_set():
                        break
                    error = None
                    try:
                        request = reader.read()
                    except HTTPError as failure:
                        error = failure.status
                        request = Request(failure.method, '/', False, legacy=failure.legacy)
                    except OSError:
                        break
                    if request is None:
                        break
                    keep_alive = (not request.legacy and request.keep_alive and
                                  number + 1 < self.max_requests and error is None)
                    result = []
                    worker = threading.Thread(target=self.worker,
                                              args=(connection, address, request, keep_alive, result, error),
                                              name=f'request-{address[1]}-{number + 1}')
                    worker.start()
                    # Ein eigener Thread je Anfrage, aber Antworten bleiben geordnet.
                    worker.join()
                    if not keep_alive or not result or not result[0]:
                        break
        finally:
            with self.lock:
                self.connections.discard(connection)
                self.readers.discard(threading.current_thread())
            self.slots.release()

    def serve(self, ready=None):
        self.logger.start()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                listener.bind((self.host, self.port))
                listener.listen(64)
                listener.settimeout(0.2)
                if ready:
                    ready(listener.getsockname())
                while not self.stop.is_set():
                    try:
                        connection, address = listener.accept()
                    except socket.timeout:
                        continue
                    if not self.slots.acquire(blocking=False):
                        connection.close()
                        continue
                    reader = threading.Thread(target=self.client, args=(connection, address),
                                              name=f'reader-{address[1]}')
                    with self.lock:
                        self.connections.add(connection)
                        self.readers.add(reader)
                    reader.start()
        finally:
            self.stop.set()
            with self.lock:
                connections, readers = list(self.connections), list(self.readers)
            for connection in connections:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            for reader in readers:
                reader.join()
            # Erst nach allen Produzenten darf der Logger sein Stoppsignal erhalten.
            self.logger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document_root', type=Path)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--max-requests', type=int, default=100)
    parser.add_argument('--max-clients', type=int, default=64)
    parser.add_argument('--log-file', type=Path, help='JSONL anhängen; Standard: stdout')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('Port muss 0..65535 sein')
    stream = None
    try:
        stream = args.log_file.open('a', encoding='utf-8') if args.log_file else None
        server = HTTPServer(args.document_root, args.host, args.port, args.timeout,
                            args.max_requests, args.max_clients, stream)
        signal.signal(signal.SIGINT, lambda signum, frame: server.stop.set())
        signal.signal(signal.SIGTERM, lambda signum, frame: server.stop.set())
        server.serve(lambda address: print(f'HTTP/1.0 auf {address[0]}:{address[1]}', flush=True))
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError) as error:
        parser.exit(1, f'Startfehler: {error}\n')
    finally:
        if stream is not None:
            stream.close()


if __name__ == '__main__':
    main()
