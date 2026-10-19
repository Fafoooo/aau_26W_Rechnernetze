# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 multi-thread mit persistenten Verbindungen und zentralem 5s-Logger.
"""Echte Loopback-TCP-Tests; keine simulierten Serverantworten."""
import importlib.util
import os
from pathlib import Path
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('tested_http09', HERE / 'server.py')
assert SPEC is not None and SPEC.loader is not None
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def receive_all(connection):
    data = bytearray()
    while True:
        try:
            chunk = connection.recv(65536)
        except ConnectionResetError:
            # Schließen mit ungelesenen überlangen Daten darf TCP-RST erzeugen.
            break
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


class HTTP09Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rn-http09-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'www'
        self.root.mkdir()
        (self.root / 'index.html').write_bytes(b'<h1>Index</h1>')
        self.binary = bytes(range(256)) * 1024
        (self.root / 'binary.dat').write_bytes(self.binary)
        (self.root / 'leer').write_bytes(b'')
        (self.root / 'a b.txt').write_bytes(b'Leerzeichen')
        (self.root / 'ä.txt').write_bytes('UTF-8'.encode())
        (self.root / 'sub').mkdir()
        (self.root / 'sub' / 'index.html').write_bytes(b'Unterverzeichnis')
        (self.root / 'ohne-index').mkdir()
        self.secret = Path(self.temp.name) / 'secret'
        self.secret.write_bytes(b'NIEMALS SENDEN')
        (self.root / 'link').symlink_to(self.secret)
        (self.root / 'dirlink').symlink_to(self.root / 'sub', target_is_directory=True)
        os.mkfifo(self.root / 'fifo')
        self.stop = threading.Event()
        self.ready = threading.Event()
        self.errors = []
        self.thread = threading.Thread(target=self.run_server, name='test-http09-server')
        self.thread.start()
        self.addCleanup(self.shutdown)
        self.assertTrue(self.ready.wait(3), self.errors)

    def run_server(self):
        try:
            server.serve(self.root, port=0, timeout=0.4, ready=self.started, stop=self.stop)
        except BaseException as error:
            self.errors.append(error)
            self.ready.set()

    def started(self, address):
        self.address = address
        self.ready.set()

    def shutdown(self):
        self.stop.set()
        self.thread.join(3)
        self.assertFalse(self.thread.is_alive(), 'Serverthread hängt')
        self.assertEqual(self.errors, [])

    def connect(self):
        connection = socket.create_connection(self.address, timeout=2)
        self.addCleanup(connection.close)
        return connection

    def exchange(self, request):
        with self.connect() as connection:
            connection.sendall(request)
            return receive_all(connection)

    def test_binary_and_no_headers(self):
        self.assertEqual(self.exchange(b'GET /binary.dat\r\n'), self.binary)

    def test_index_and_directories(self):
        for target, body in [(b'/', b'<h1>Index</h1>'), (b'/sub', b'Unterverzeichnis'),
                             (b'/sub/', b'Unterverzeichnis'), (b'/leer', b'')]:
            with self.subTest(target=target):
                self.assertEqual(self.exchange(b'GET ' + target + b'\r\n'), body)

    def test_encoded_paths_and_query(self):
        self.assertEqual(self.exchange(b'GET /a%20b.txt?x=1\r\n'), b'Leerzeichen')
        self.assertEqual(self.exchange(b'GET /%C3%A4.txt\r\n'), b'UTF-8')

    def test_errors_are_silent(self):
        targets = [b'/missing', b'/ohne-index/', b'/../secret', b'/%2e%2e/secret',
                   b'/link', b'/dirlink/', b'/fifo', b'/binary.dat/', b'/%00',
                   b'/%zz', b'/%', b'/%ff', b'/a\\b', b'/#fragment']
        requests = [b'GET ' + target + b'\r\n' for target in targets]
        requests += [b'HEAD /\r\n', b'POST /\r\n', b'GET / HTTP/1.0\r\n\r\n',
                     b'GET /\n', b'GET  /\r\n', b'GET /\r\nX: y\r\n',
                     b'GET /' + b'x' * 8192 + b'\r\n']
        for request in requests:
            with self.subTest(request=request[:80]):
                self.assertEqual(self.exchange(request), b'')

    def test_fragmentation(self):
        with self.connect() as connection:
            for fragment in (b'G', b'ET /bi', b'nary.dat\r', b'\n'):
                connection.sendall(fragment)
            self.assertEqual(receive_all(connection), self.binary)

    def test_incomplete_eof(self):
        with self.connect() as connection:
            connection.sendall(b'GET /')
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(receive_all(connection), b'')

    def test_sequential_single_thread(self):
        with self.connect() as first, self.connect() as second:
            first.sendall(b'GET /')
            second.sendall(b'GET /sub/\r\n')
            second.settimeout(0.05)
            with self.assertRaises(socket.timeout):
                second.recv(1)
            first.sendall(b'\r\n')
            self.assertEqual(receive_all(first), b'<h1>Index</h1>')
            second.settimeout(2)
            self.assertEqual(receive_all(second), b'Unterverzeichnis')

    def test_cli_help_and_invalid_options(self):
        for args, code in [(['--help'], 0), (['--port', '-1'], 2),
                           (['--timeout', 'nan'], 2), (['--timeout', '0'], 2)]:
            result = subprocess.run([sys.executable, str(HERE / 'server.py'), str(self.root), *args],
                                    capture_output=True, timeout=5)
            self.assertEqual(result.returncode, code, result.stderr)

    def test_original_zip_files_exactly(self):
        archive = HERE.parent / 'Angabe' / 'document_root.zip'
        with zipfile.ZipFile(archive) as zipped:
            self.assertIsNone(zipped.testzip())
            entries = [entry for entry in zipped.infolist() if not entry.is_dir()]
            self.assertTrue(entries)
            # Das Original bleibt unverändert; nur eine temporäre Testkopie entsteht.
            prefix = 'document_root/' if all(e.filename.startswith('document_root/') for e in entries) else ''
            for entry in entries:
                relative = Path(entry.filename.removeprefix(prefix))
                self.assertFalse(relative.is_absolute() or '..' in relative.parts)
                destination = self.root / 'original' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(zipped.read(entry))
            for entry in entries:
                relative = entry.filename.removeprefix(prefix)
                with self.subTest(file=relative):
                    target = '/original/' + relative
                    request = ('GET ' + target + '\r\n').encode('ascii')
                    self.assertEqual(self.exchange(request), zipped.read(entry))

    def test_cli_serves_and_sigterm_exits_cleanly(self):
        process = subprocess.Popen([sys.executable, str(HERE / 'server.py'), str(self.root), '--port', '0'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            assert process.stdout is not None
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(3), 'CLI meldet keine Startbereitschaft')
            banner = process.stdout.readline()
            self.assertTrue(banner.startswith('HTTP/0.9 auf '), banner)
            host, port = banner.split()[-1].split(':')
            with socket.create_connection((host, int(port)), timeout=3) as connection:
                connection.sendall(b'GET /binary.dat\r\n')
                self.assertEqual(receive_all(connection), self.binary)
            process.send_signal(signal.SIGTERM)
            _, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    unittest.main()
