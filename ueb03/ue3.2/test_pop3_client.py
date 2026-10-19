# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Ü3.2 mit unabhängigem skriptgesteuertem TCP-Gegenüber und dem Ü3.3-Server inklusive Fehler- und Fragmentierungspfaden testen.
"""Socket-Tests ohne poplib im eigenen Client und ohne Fremdpakete."""

from contextlib import contextmanager
import importlib.util
from pathlib import Path
import socket
import subprocess
import sys
import threading
import unittest

from pop3_client import POP3Client, POP3Error, ProtocolError


@contextmanager
def scripted_server(steps, fragmented=True):
    """Ein echtes TCP-Gegenüber; (erwarteter Befehl, Antwort), None = Begrüßung."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    listener.settimeout(3)
    errors = []

    def run():
        try:
            with listener.accept()[0] as connection:
                connection.settimeout(3)
                connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                with connection.makefile("rb") as reader:
                    for expected, reply in steps:
                        if expected is not None:
                            actual = reader.readline()
                            if actual != expected:
                                raise AssertionError(f"Erwartet {expected!r}, erhalten {actual!r}")
                        chunks = (bytes([octet]) for octet in reply) if fragmented else [reply]
                        for chunk in chunks:
                            connection.sendall(chunk)
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=run)
    worker.start()
    try:
        yield listener.getsockname()
    finally:
        worker.join(5)
        listener.close()
        if worker.is_alive():
            raise AssertionError("Testgegenüber hängt")
        if errors:
            raise errors[0]


def load_server():
    """Server aus Nachbarverzeichnis laden; keine Änderung am Originalpaket."""
    path = Path(__file__).resolve().parents[1] / "ue3.3" / "pop3_server.py"
    spec = importlib.util.spec_from_file_location("rn_pop3_integration_server", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClientTests(unittest.TestCase):
    def test_fragmented_full_session_and_dot_unstuffing(self):
        steps = [(None, b"+OK ready\r\n"),
                 (b"USER alice\r\n", b"+OK user\r\n"),
                 (b"PASS secret\r\n", b"+OK pass\r\n"),
                 (b"LIST\r\n", b"+OK list\r\n1 29\r\n2 12\r\n.\r\n"),
                 (b"RETR 1\r\n", b"+OK data\r\nSubject: Dots\r\n\r\n..a\r\n..\r\n...b\r\n.\r\n"),
                 (b"QUIT\r\n", b"+OK bye\r\n")]
        with scripted_server(steps) as address:
            with POP3Client(*address) as client:
                client.login("alice", "secret")
                self.assertEqual(client.list_messages(), [(1, 29), (2, 12)])
                self.assertEqual(client.retrieve(1), b"Subject: Dots\r\n\r\n.a\r\n.\r\n..b\r\n")
            self.assertTrue(client.closed)

    def test_negative_list_is_single_line_and_session_stays_usable(self):
        steps = [(None, b"+OK\r\n"), (b"LIST\r\n", b"-ERR not logged in\r\n"),
                 (b"NOOP\r\n", b"+OK\r\n"), (b"QUIT\r\n", b"+OK\r\n")]
        with scripted_server(steps) as address, POP3Client(*address) as client:
            with self.assertRaises(POP3Error):
                client.list_messages()
            self.assertEqual(client.command("NOOP"), b"+OK")

    def test_rejected_login_cli_does_not_leak_password(self):
        steps = [(None, b"+OK\r\n"), (b"USER alice\r\n", b"+OK\r\n"),
                 (b"PASS lab-only-sensitive\r\n", b"-ERR bad login\r\n"), (b"", b"")]
        with scripted_server(steps) as address:
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),
                                     "--host", address[0], "--port", str(address[1]),
                                     "--password", "lab-only-sensitive"],
                                    capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1)
        self.assertIn("bad login", result.stderr)
        self.assertNotIn("lab-only-sensitive", result.stdout + result.stderr)

    def test_greeting_errors_close_connection(self):
        for greeting, error in [(b"-ERR unavailable\r\n", POP3Error),
                                (b"HELLO\r\n", ProtocolError),
                                (b"+OKX\r\n", ProtocolError),
                                (b"+OK\n", ProtocolError),
                                (b"+OK " + b"x" * 510 + b"\r\n", ProtocolError)]:
            with self.subTest(greeting=greeting[:20]):
                with scripted_server([(None, greeting), (b"", b"")], fragmented=False) as address:
                    with self.assertRaises(error):
                        POP3Client(*address)

    def test_truncated_multiline_and_invalid_dot_stuffing(self):
        for response in (b"+OK\r\nSubject: x\r\n", b"+OK\r\n.bad\r\n"):
            with self.subTest(response=response):
                with scripted_server([(None, b"+OK\r\n"), (b"RETR 1\r\n", response)], fragmented=False) as address:
                    client = POP3Client(*address)
                    with self.assertRaises(ProtocolError):
                        client.retrieve(1)
                    self.assertTrue(client.closed)

    def test_malformed_listing_rejected(self):
        for data in (b"1\r\n", b"0 12\r\n", b"1 -4\r\n", b"one 4\r\n", b"1 4\r\n1 4\r\n"):
            with self.subTest(data=data):
                with scripted_server([(None, b"+OK\r\n"),
                                      (b"LIST\r\n", b"+OK\r\n" + data + b".\r\n")]) as address:
                    client = POP3Client(*address)
                    with self.assertRaises(ProtocolError):
                        client.list_messages()
                    self.assertTrue(client.closed)

    def test_injection_length_and_invalid_message_blocked_locally(self):
        with scripted_server([(None, b"+OK\r\n"), (b"QUIT\r\n", b"+OK\r\n")]) as address:
            with POP3Client(*address) as client:
                for command in ("USER alice\r\nDELE 1", "USER ä", "X" * 254, "NOOP\t"):
                    with self.subTest(command=command), self.assertRaises(ValueError):
                        client.command(command)
                for number in (0, -1, "1"):
                    with self.subTest(number=number), self.assertRaises(ValueError):
                        client.retrieve(number)
                with self.assertRaises(ValueError):
                    client.login("alice bob", "secret")
        with self.assertRaises(ProtocolError):
            client.command("NOOP")
        self.assertIsNone(client.quit())

    def test_context_exception_aborts_without_quit(self):
        with scripted_server([(None, b"+OK\r\n"), (b"", b"")]) as address:
            with self.assertRaisesRegex(RuntimeError, "abort"):
                with POP3Client(*address) as client:
                    raise RuntimeError("abort")
            self.assertTrue(client.closed)

    def test_quit_error_still_closes(self):
        with scripted_server([(None, b"+OK\r\n"), (b"QUIT\r\n", b"-ERR update failed\r\n")]) as address:
            client = POP3Client(*address)
            with self.assertRaises(POP3Error):
                client.quit()
            self.assertTrue(client.closed)

    def test_full_socket_client_against_own_server_and_cli(self):
        module = load_server()
        with module.create_server(port=0) as server:
            worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
            worker.start()
            try:
                with POP3Client(*server.server_address) as client:
                    client.login("alice", "secret")
                    listing = client.list_messages()
                    self.assertEqual(len(listing), 4)
                    for number, size in listing:
                        self.assertEqual(len(client.retrieve(number)), size)
                result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),
                                         "--port", str(server.server_address[1]), "--password", "secret"],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Welcome to the POP3 lab", result.stdout)
                self.assertIn("QUIT bestätigt", result.stdout)
                self.assertNotIn("secret", result.stdout)
            finally:
                server.shutdown()
                worker.join(3)
                self.assertFalse(worker.is_alive())

    def test_empty_mailbox_cli_quits_without_retr(self):
        steps = [(None, b"+OK\r\n"), (b"USER alice\r\n", b"+OK\r\n"),
                 (b"PASS secret\r\n", b"+OK\r\n"), (b"LIST\r\n", b"+OK\r\n.\r\n"),
                 (b"QUIT\r\n", b"+OK\r\n")]
        with scripted_server(steps) as address:
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),
                                     "--port", str(address[1]), "--password", "secret"],
                                    capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Maildrop leer", result.stdout)
        self.assertIn("QUIT bestätigt", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
