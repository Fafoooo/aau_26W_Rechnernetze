# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: Ü4.3 UDP-Client/Server auf echten Loopback-Sockets testen,
# UTF-8, leere Nachricht, Grenzen, Timeout und CLI-Fehler nachprüfen.
"""Automatisierte Tests; ausschließlich eigener lokaler UDP-Verkehr."""

import contextlib
import io
from pathlib import Path
import selectors
import socket
import subprocess
import sys
import unittest

import client

BASE = Path(__file__).resolve().parent


class UDPTests(unittest.TestCase):
    def test_send_utf8_empty_and_exact_limit(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("127.0.0.1", 0))
            receiver.settimeout(2)
            port = receiver.getsockname()[1]
            for message in ("Hello from Mininet!", "Grüße 🌍", "", "x" * 4096):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(client.send("127.0.0.1", port, message), 0)
                data, address = receiver.recvfrom(65535)
                self.assertEqual(data, message.encode("utf-8"))
                self.assertEqual(address[0], "127.0.0.1")

    def test_oversized_rejected_before_socket(self):
        with self.assertRaises(ValueError):
            client.send("127.0.0.1", 5000, "ä" * 2049)

    def test_cli_three_datagrams(self):
        server = subprocess.Popen([sys.executable, "-B", str(BASE / "server.py"), "--host", "127.0.0.1",
                                   "--port", "0", "--count", "3", "--timeout", "3"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            assert server.stdout is not None
            with selectors.DefaultSelector() as selector:
                selector.register(server.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(3), "Server nicht bereit")
            ready = server.stdout.readline().strip()
            self.assertTrue(ready.startswith("READY 127.0.0.1:"))
            port = ready.rsplit(":", 1)[1]
            for message in ("Hello from Mininet!", "Grüße 🌍", ""):
                result = subprocess.run([sys.executable, "-B", str(BASE / "client.py"), "--host", "127.0.0.1",
                                         "--port", port, "--message", message], capture_output=True, text=True, timeout=3)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(repr(message.encode("utf-8")), result.stdout)
            output, error = server.communicate(timeout=4)
            self.assertEqual(server.returncode, 0, error)
            self.assertEqual(output.count("RECEIVED "), 3)
            self.assertIn("b''", output)
        finally:
            if server.poll() is None:
                server.terminate()
            server.communicate(timeout=3)

    def test_cli_rejects_arguments(self):
        for script, arguments in (("client.py", ["--port", "0"]), ("client.py", ["--local-port", "-1"]),
                                  ("server.py", ["--count", "-1"]), ("server.py", ["--timeout", "nan"]),
                                  ("server.py", ["--timeout", "0"])):
            result = subprocess.run([sys.executable, "-B", str(BASE / script), *arguments],
                                    capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, 2)

    def test_timeout(self):
        result = subprocess.run([sys.executable, "-B", str(BASE / "server.py"), "--host", "127.0.0.1",
                                 "--port", "0", "--count", "1", "--timeout", "0.05"],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 1)
        self.assertIn("READY", result.stdout)
        self.assertIn("timed out", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
