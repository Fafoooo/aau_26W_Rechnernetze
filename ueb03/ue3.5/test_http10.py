# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 multi-thread mit persistenten Verbindungen und zentralem 5s-Logger.
"""HTTP/1.0-Integrationstests mit echten Sockets, Threads und Logausgabe."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from email.utils import parsedate_to_datetime
import importlib.util
import io
import json
import os
from pathlib import Path
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from zoneinfo import ZoneInfo


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('tested_http10', HERE / 'server.py')
assert SPEC is not None and SPEC.loader is not None
server = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = server
SPEC.loader.exec_module(server)


class Wire:
    """Testclient: Content-Length statt EOF als Antwortgrenze auswerten."""
    def __init__(self, connection):
        self.connection = connection
        self.buffer = b''

    def response(self, head=False):
        while b'\r\n\r\n' not in self.buffer:
            chunk = self.connection.recv(65536)
            if not chunk:
                raise AssertionError('EOF vor vollständigen Responseheadern')
            self.buffer += chunk
        header, self.buffer = self.buffer.split(b'\r\n\r\n', 1)
        lines = header.decode('ascii').split('\r\n')
        headers = dict(line.split(': ', 1) for line in lines[1:])
        length = 0 if head else int(headers['Content-Length'])
        while len(self.buffer) < length:
            chunk = self.connection.recv(65536)
            if not chunk:
                raise AssertionError('EOF vor vollständigem Responsebody')
            self.buffer += chunk
        body, self.buffer = self.buffer[:length], self.buffer[length:]
        return int(lines[0].split(' ')[1]), headers, body


class HTTP10Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rn-http10-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'www'
        self.root.mkdir()
        (self.root / 'index.html').write_bytes(b'<h1>HTTP10</h1>')
        self.binary = bytes(range(256)) * 1024
        (self.root / 'binary.dat').write_bytes(self.binary)
        (self.root / 'empty').write_bytes(b'')
        (self.root / 'ä.txt').write_bytes(b'Umlaut')
        (self.root / 'dir').mkdir()
        (self.root / 'dir' / 'index.html').write_bytes(b'Unterindex')
        (self.root / 'noindex').mkdir()
        secret = Path(self.temp.name) / 'secret'
        secret.write_bytes(b'Secret')
        (self.root / 'link').symlink_to(secret)
        (self.root / 'dirlink').symlink_to(self.root / 'dir', target_is_directory=True)
        os.mkfifo(self.root / 'fifo')
        self.log = io.StringIO()
        self.instance = server.HTTPServer(self.root, port=0, timeout=0.6,
                                          max_requests=4, log_stream=self.log)
        self.ready = threading.Event()
        self.errors = []
        self.thread = threading.Thread(target=self.run_server, name='test-http10-server')
        self.thread.start()
        self.addCleanup(self.shutdown)
        self.assertTrue(self.ready.wait(3), self.errors)

    def run_server(self):
        try:
            self.instance.serve(self.started)
        except BaseException as error:
            self.errors.append(error)
            self.ready.set()

    def started(self, address):
        self.address = address
        self.ready.set()

    def shutdown(self):
        self.instance.stop.set()
        self.thread.join(3)
        self.assertFalse(self.thread.is_alive(), 'Server bleibt beim Shutdown hängen')
        self.assertFalse(self.instance.logger.thread.is_alive())
        self.assertEqual(self.errors, [])

    def connect(self):
        connection = socket.create_connection(self.address, timeout=3)
        self.addCleanup(connection.close)
        return connection

    def exchange(self, request, head=False):
        with self.connect() as connection:
            connection.sendall(request)
            response = Wire(connection).response(head)
            return response

    def receive_all(self, connection):
        """Legacy-Antwort ohne Framing bis zum wirklichen EOF/RST lesen."""
        chunks = []
        while True:
            try:
                chunk = connection.recv(65536)
            except ConnectionResetError:
                break
            if not chunk:
                break
            chunks.append(chunk)
        return b''.join(chunks)

    def test_legacy_get_files_and_close(self):
        for path, expected in [(b'/', b'<h1>HTTP10</h1>'), (b'/dir', b'Unterindex'),
                               (b'/dir/', b'Unterindex'), (b'/binary.dat', self.binary),
                               (b'/empty', b''), (b'/%C3%A4.txt?x=1', b'Umlaut')]:
            with self.subTest(path=path), self.connect() as connection:
                # Kein Half-close: Der Server muss allein CRLF als Ende erkennen.
                connection.sendall(b'GET ' + path + b'\r\n')
                self.assertEqual(self.receive_all(connection), expected)
                self.assertEqual(connection.recv(1), b'')

    def test_legacy_fragmented_request(self):
        with self.connect() as connection:
            for part in [b'G', b'ET ', b'/binary.', b'dat', b'\r']:
                connection.sendall(part)
                connection.settimeout(0.03)
                with self.assertRaises(socket.timeout):
                    connection.recv(1)
            connection.settimeout(3)
            connection.sendall(b'\n')
            self.assertEqual(self.receive_all(connection), self.binary)

    def test_legacy_errors_are_silent(self):
        requests = [b'GET ' + path + b'\r\n' for path in
                    [b'/missing', b'/noindex/', b'/../secret', b'/%2e%2e/secret',
                     b'/link', b'/dirlink/', b'/fifo', b'/%00', b'/%zz', b'/%ff', b'/#x']]
        requests += [b'HEAD /\r\n', b'G@T /\r\n', b'GET http://evil/\r\n',
                     b'GET /\xff\r\n', b'GET /\x00\r\n',
                     b'GET /\r\nConnection: keep-alive\r\n\r\n',
                     b'GET /\r\nGET /binary.dat\r\n']
        for request in requests:
            with self.subTest(request=request), self.connect() as connection:
                connection.sendall(request)
                self.assertEqual(self.receive_all(connection), b'')

    def test_legacy_and_explicit_versions_remain_distinct(self):
        for version, expected in [(b'HTTP/0.9', 505), (b'HTTP/9.9', 505),
                                  (b'HTTP/1.0', 200), (b'HTTP/1.1', 200)]:
            with self.subTest(version=version), self.connect() as connection:
                connection.sendall(b'GET / ' + version + b'\r\n')
                connection.settimeout(0.03)
                with self.assertRaises(socket.timeout):
                    connection.recv(1)
                connection.settimeout(3)
                connection.sendall(b'Host: localhost\r\n\r\n')
                self.assertEqual(Wire(connection).response()[0], expected)
        with self.connect() as connection:
            # Wechsel auf Simple-Request auch nach einem persistenten Full-Request.
            connection.sendall(b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n'
                               b'GET /binary.dat\r\n')
            wire = Wire(connection)
            self.assertEqual(wire.response()[2], b'<h1>HTTP10</h1>')
            self.assertEqual(wire.buffer + self.receive_all(connection), self.binary)

    def test_legacy_requests_have_separate_workers_and_logs(self):
        ports = []
        for request, expected in [(b'GET /\r\n', b'<h1>HTTP10</h1>'),
                                  (b'GET /dir\r\n', b'Unterindex'),
                                  (b'GET /missing\r\n', b''), (b'HEAD /\r\n', b'')]:
            with self.connect() as connection:
                ports.append(connection.getsockname()[1])
                connection.sendall(request)
                self.assertEqual(self.receive_all(connection), expected)
        self.shutdown()
        entries = [json.loads(line) for line in self.log.getvalue().splitlines()]
        entries = sorted(entries, key=lambda entry: ports.index(entry['port']))
        self.assertEqual(len(entries), 4)
        self.assertEqual([entry['status'] for entry in entries], [200, 200, 404, 400])
        self.assertEqual([entry['method'] for entry in entries], ['GET', 'GET', 'GET', 'HEAD'])
        self.assertEqual(len({entry['worker'] for entry in entries}), 4)
        self.assertTrue(all(entry['worker'].startswith('request-') for entry in entries))

    def test_latin1_header_text_and_ascii_request_line(self):
        request = b'GET / HTTP/1.0\r\nX-Note: Gr\xfc\xdfe \x80\xff\tText\r\n\r\n'
        self.assertEqual(self.exchange(request)[::2], (200, b'<h1>HTTP10</h1>'))
        for request in [b'GET /\xe4 HTTP/1.0\r\n\r\n', b'G\xc9T / HTTP/1.0\r\n\r\n',
                        b'GET / HTTP/1.\xff\r\n\r\n', b'GET / HTTP/1.0\r\nX-\xe4: ok\r\n\r\n']:
            with self.subTest(request=request):
                self.assertEqual(self.exchange(request)[0], 400)

    def test_repeated_list_headers_and_connection_precedence(self):
        lists = {'Accept': ('text/html', 'image/gif'), 'Accept-Charset': ('iso-8859-1', 'us-ascii'),
                 'Accept-Encoding': ('gzip', 'x-compress'), 'Accept-Language': ('de', 'en'),
                 'Allow': ('GET', 'HEAD'), 'Pragma': ('no-cache', 'extension')}
        for name, (first, second) in lists.items():
            header = (name + ': ' + first + '\r\n' + name.upper() + ': ' + second + '\r\n').encode('ascii')
            with self.subTest(name=name):
                self.assertEqual(self.exchange(b'GET / HTTP/1.0\r\n' + header + b'\r\n')[0], 200)
        with self.connect() as connection:
            wire = Wire(connection)
            connection.sendall(b'GET / HTTP/1.0\r\nConnection: extension\r\n'
                               b'cOnNeCtIoN: Keep-Alive\r\n\r\n')
            self.assertEqual(wire.response()[1]['Connection'], 'keep-alive')
            connection.sendall(b'GET /dir HTTP/1.0\r\nConnection: close\r\n'
                               b'Connection: keep-alive\r\n\r\n')
            status, headers, body = wire.response()
            self.assertEqual((status, headers['Connection'], body), (200, 'close', b'Unterindex'))
            self.assertEqual(connection.recv(1), b'')
        with self.connect() as connection:
            connection.sendall(b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n'
                               b'Connection: close\r\n\r\n')
            self.assertEqual(Wire(connection).response()[1]['Connection'], 'close')
            self.assertEqual(connection.recv(1), b'')

    def test_header_controls_and_framing_still_rejected(self):
        for value in [b'\x00', b'\x01', b'\x0b', b'\x1f', b'\x7f', b'a\nb', b'a\rb']:
            with self.subTest(value=value):
                self.assertEqual(self.exchange(b'GET / HTTP/1.0\r\nX: ' + value + b'\r\n\r\n')[0], 400)
        for headers in [b'Host: a\r\nhost: a', b'Host: a\r\nHost: b',
                        b'Content-Length: 0\r\ncontent-length: 0', b'Content-Length: 0, 0',
                        b'Content-Length: \xb2', b'Transfer-Encoding: identity',
                        b'Connection: keep-alive\r\nContent-Length: 0\r\nContent-Length: 1']:
            with self.subTest(headers=headers), self.connect() as connection:
                connection.sendall(b'GET / HTTP/1.0\r\n' + headers + b'\r\n\r\n'
                                   b'GET / HTTP/1.0\r\n\r\n')
                wire = Wire(connection)
                status, response, _ = wire.response()
                self.assertEqual((status, response['Connection']), (400, 'close'))
                self.assertEqual(wire.buffer + self.receive_all(connection), b'')

    def test_get_head_binary_and_indexes(self):
        for path, expected in [(b'/', b'<h1>HTTP10</h1>'), (b'/dir', b'Unterindex'),
                               (b'/dir/', b'Unterindex'), (b'/binary.dat', self.binary),
                               (b'/empty', b''), (b'/%C3%A4.txt?x=1', b'Umlaut')]:
            with self.subTest(path=path):
                status, headers, body = self.exchange(b'GET ' + path + b' HTTP/1.0\r\n\r\n')
                self.assertEqual((status, body), (200, expected))
                self.assertEqual(int(headers['Content-Length']), len(expected))
                self.assertEqual(headers['Connection'], 'close')
                self.assertIsNotNone(parsedate_to_datetime(headers['Date']).tzinfo)
                status, headers, body = self.exchange(b'HEAD ' + path + b' HTTP/1.0\r\n\r\n', True)
                self.assertEqual((status, body), (200, b''))
                self.assertEqual(int(headers['Content-Length']), len(expected))
                if path in (b'/', b'/dir', b'/dir/'):
                    self.assertEqual(headers['Content-Type'], 'text/html')

    def test_persistent_sequential_and_head_error_framing(self):
        with self.connect() as connection:
            wire = Wire(connection)
            requests = [(b'GET', b'/', 200, False), (b'HEAD', b'/missing', 404, True),
                        (b'GET', b'/binary.dat', 200, False), (b'GET', b'/empty', 200, False)]
            for index, (method, path, expected, head) in enumerate(requests):
                connection.sendall(method + b' ' + path + b' HTTP/1.0\r\nConnection: keep-alive\r\n\r\n')
                status, headers, body = wire.response(head)
                self.assertEqual(status, expected)
                self.assertEqual(headers['Connection'], 'close' if index == 3 else 'keep-alive')
                if path == b'/binary.dat':
                    self.assertEqual(body, self.binary)
            self.assertEqual(connection.recv(1), b'')

    def test_pipelining_order_and_each_request_gets_new_thread(self):
        with self.connect() as connection:
            port = connection.getsockname()[1]
            wire = Wire(connection)
            connection.sendall(b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n'
                               b'HEAD /binary.dat HTTP/1.0\r\nConnection: keep-alive\r\n\r\n'
                               b'GET /dir HTTP/1.0\r\nConnection: close\r\n\r\n')
            self.assertEqual(wire.response()[2], b'<h1>HTTP10</h1>')
            self.assertEqual(wire.response(True)[2], b'')
            self.assertEqual(wire.response()[2], b'Unterindex')
            self.assertEqual(connection.recv(1), b'')
        self.shutdown()
        entries = [json.loads(line) for line in self.log.getvalue().splitlines()]
        entries = [entry for entry in entries if entry['port'] == port]
        self.assertEqual([entry['method'] for entry in entries], ['GET', 'HEAD', 'GET'])
        self.assertEqual(len({entry['worker'] for entry in entries}), 3)
        self.assertTrue(all(entry['worker'].startswith('request-') for entry in entries))

    def test_explicit_close_wins_and_default_close(self):
        for header in [b'', b'Connection: keep-alive, close\r\n', b'Connection: close\r\n']:
            with self.subTest(header=header), self.connect() as connection:
                connection.sendall(b'GET / HTTP/1.0\r\n' + header + b'\r\n')
                self.assertEqual(Wire(connection).response()[1]['Connection'], 'close')
                self.assertEqual(connection.recv(1), b'')

    def test_fragmented_request_and_no_body(self):
        with self.connect() as connection:
            for part in [b'GE', b'T /binary.dat HTTP/', b'1.0\r', b'\nContent-Len', b'gth: 00\r\n\r', b'\n']:
                connection.sendall(part)
            self.assertEqual(Wire(connection).response()[2], self.binary)

    def test_errors_and_security(self):
        for path, expected in [(b'/missing', 404), (b'/noindex/', 404), (b'/link', 403),
                               (b'/dirlink/', 403), (b'/../secret', 403),
                               (b'/%2e%2e/secret', 403), (b'/%00', 403), (b'/%zz', 403),
                               (b'/%ff', 403), (b'/fifo', 403), (b'/#x', 403)]:
            with self.subTest(path=path):
                status, headers, body = self.exchange(b'GET ' + path + b' HTTP/1.0\r\n\r\n')
                self.assertEqual(status, expected)
                self.assertEqual(int(headers['Content-Length']), len(body))
        for method in [b'POST', b'OPTIONS', b'DELETE']:
            status, headers, _ = self.exchange(method + b' / HTTP/1.0\r\n\r\n')
            self.assertEqual(status, 405)
            self.assertEqual(headers['Allow'], 'GET, HEAD')

    def test_invalid_sizes_headers_and_request_lines(self):
        cases = [b'Content-Length: -1', b'Content-Length: 1', b'Content-Length: +0',
                 b'Content-Length: ' + b'9' * 5000,
                 b'Content-Length: nope', b'Content-Length:', b'Content-Length: 0\r\nContent-Length: 0',
                 b'Transfer-Encoding: chunked', b' bad: folded', b'Bad Header: x',
                 b'Host : x', b'Host: x\x00', b'Broken', b'X: a\r\nX: b']
        for headers in cases:
            with self.subTest(headers=headers):
                status, response, _ = self.exchange(b'GET / HTTP/1.0\r\n' + headers + b'\r\n\r\n')
                self.assertEqual(status, 400)
                self.assertEqual(response['Connection'], 'close')
        requests = [(b'GET / HTTP/9.9\r\n\r\n', 505), (b'GET  / HTTP/1.0\r\n\r\n', 400),
                    (b'G@T / HTTP/1.0\r\n\r\n', 400), (b'GET http://evil/ HTTP/1.0\r\n\r\n', 400),
                    (b'GET /' + b'a' * 8200 + b' HTTP/1.0\r\n\r\n', 414),
                    (b'GET / HTTP/1.0\r\nX: ' + b'a' * 17000 + b'\r\n\r\n', 431),
                    (b'GET / HTTP/1.0\r\n' + b''.join(f'X-{i}: 0\r\n'.encode() for i in range(101)) + b'\r\n', 431)]
        for request, expected in requests:
            with self.subTest(request=request[:70]):
                self.assertEqual(self.exchange(request)[0], expected)

    def test_http11_browser_compatibility_subset(self):
        self.assertEqual(self.exchange(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')[0], 200)
        self.assertEqual(self.exchange(b'GET / HTTP/1.1\r\n\r\n')[0], 400)

    def test_timeout_partial_and_incomplete_eof(self):
        with self.connect() as connection:
            connection.sendall(b'GET / HTTP/1.0\r\nX:')
            self.assertEqual(Wire(connection).response()[0], 408)
        with self.connect() as connection:
            connection.sendall(b'GET / HTTP/1.0\r\n')
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(Wire(connection).response()[0], 400)

    def test_parallel_clients_despite_blocked_reader(self):
        with self.connect() as slow:
            slow.sendall(b'GET / HTTP/1.0\r\nX:')
            def fetch(_):
                return self.exchange(b'GET /binary.dat HTTP/1.0\r\n\r\n')[2]
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(fetch, range(16)))
            self.assertEqual(results, [self.binary] * 16)

    def test_absolute_request_deadline_even_with_trickling_bytes(self):
        with self.connect() as connection:
            stopped = threading.Event()
            def trickle():
                try:
                    for byte in b'GET / HTTP/1.0\r\nX: slow\r\n\r\n':
                        if stopped.wait(0.08):
                            return
                        connection.sendall(bytes([byte]))
                except OSError:
                    pass
            sender = threading.Thread(target=trickle)
            sender.start()
            started = time.monotonic()
            try:
                self.assertEqual(Wire(connection).response()[0], 408)
                self.assertLess(time.monotonic() - started, 1.2)
            finally:
                stopped.set()
                sender.join(2)
                self.assertFalse(sender.is_alive())

    def test_max_clients_rejects_overload_and_recovers(self):
        self.instance.slots = threading.BoundedSemaphore(1)
        with self.connect() as first:
            first.sendall(b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n')
            self.assertEqual(Wire(first).response()[0], 200)
            with self.connect() as excess:
                try:
                    excess.sendall(b'GET / HTTP/1.0\r\n\r\n')
                    self.assertEqual(excess.recv(1), b'')
                except ConnectionResetError:
                    pass
        self.assertTrue(self.instance.slots.acquire(timeout=2))
        self.instance.slots.release()
        self.assertEqual(self.exchange(b'GET / HTTP/1.0\r\n\r\n')[0], 200)

    def test_empty_eof_is_not_a_request(self):
        with self.connect() as connection:
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(connection.recv(1), b'')
        self.shutdown()
        self.assertEqual(self.log.getvalue(), '')

    def test_shutdown_closes_active_client_and_flushes_logs(self):
        with self.connect() as connection:
            connection.sendall(b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n')
            self.assertEqual(Wire(connection).response()[0], 200)
            self.shutdown()
            self.assertEqual(connection.recv(1), b'')
        entries = [json.loads(line) for line in self.log.getvalue().splitlines()]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['method'], 'GET')
        self.assertEqual(entries[0]['ip'], '127.0.0.1')
        parsed = datetime.fromisoformat(entries[0]['timestamp'])
        self.assertEqual(parsed.utcoffset(), parsed.astimezone(ZoneInfo('Europe/Vienna')).utcoffset())

    def test_original_zip_files_exactly(self):
        with zipfile.ZipFile(HERE.parent / 'Angabe' / 'document_root.zip') as zipped:
            self.assertIsNone(zipped.testzip())
            for entry in zipped.infolist():
                if entry.is_dir():
                    continue
                relative = Path(entry.filename)
                self.assertFalse(relative.is_absolute() or '..' in relative.parts)
                destination = self.root / 'original' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                expected = zipped.read(entry)
                destination.write_bytes(expected)
                request = ('GET /original/' + entry.filename + ' HTTP/1.0\r\n\r\n').encode('ascii')
                self.assertEqual(self.exchange(request)[2], expected)

    def test_cli_process_sigint_flushes_log_file(self):
        self.cli_process_signal(signal.SIGINT)

    def test_cli_process_sigterm_flushes_log_file(self):
        self.cli_process_signal(signal.SIGTERM)

    def cli_process_signal(self, signum):
        log_file = Path(self.temp.name) / 'access.jsonl'
        process = subprocess.Popen([sys.executable, str(HERE / 'server.py'), str(self.root),
                                    '--port', '0', '--log-file', str(log_file)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            # readline folgt dem explizit geflushten Ready-Banner des Servers.
            assert process.stdout is not None
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(3), 'CLI meldet keine Startbereitschaft')
            banner = process.stdout.readline()
            self.assertTrue(banner.startswith('HTTP/1.0 auf '), banner)
            host, port = banner.split()[-1].split(':')
            with socket.create_connection((host, int(port)), timeout=3) as connection:
                connection.sendall(b'GET / HTTP/1.0\r\n\r\n')
                self.assertEqual(Wire(connection).response()[0], 200)
            process.send_signal(signum)
            _, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            entries = [json.loads(line) for line in log_file.read_text().splitlines()]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['status'], 200)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_cli_invalid_limits_and_missing_root(self):
        for options in [('--timeout', 'nan'), ('--timeout', '0'), ('--max-requests', '0'),
                        ('--max-clients', '0'), ('--port', '65536')]:
            result = subprocess.run([sys.executable, str(HERE / 'server.py'), str(self.root), *options],
                                    capture_output=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)
        for invalid_root in [self.root / 'missing', self.root / 'index.html']:
            result = subprocess.run([sys.executable, str(HERE / 'server.py'), str(invalid_root)],
                                    capture_output=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)


class LoggerTests(unittest.TestCase):
    def test_real_five_second_batch_and_final_flush(self):
        class ObservedStream(io.StringIO):
            def __init__(self):
                super().__init__()
                self.written = threading.Event()
                self.write_time = None
            def flush(self):
                if self.getvalue():
                    self.write_time = time.monotonic()
                    self.written.set()
                super().flush()
        stream = ObservedStream()
        logger = server.AccessLogger(stream)
        started = time.monotonic()
        logger.start()
        try:
            logger.record('GET', ('127.0.0.1', 12345), 200)
            self.assertFalse(stream.written.wait(0.15), 'Logger darf nicht sofort ausgeben')
            self.assertTrue(stream.written.wait(6), '5s-Ausgabe fehlt')
            assert stream.write_time is not None
            self.assertGreaterEqual(stream.write_time - started, 4.9)
            logger.record('HEAD', ('127.0.0.1', 12346), 404)
        finally:
            logger.close()
        entries = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual([entry['method'] for entry in entries], ['GET', 'HEAD'])


if __name__ == '__main__':
    unittest.main()
