# KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.
# Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Auftrag: Eigene echte stdlib-unittest-Tests für Ü4.6 TCP erstellen und ausführen:
# Fragmentierung, Coalescing, Limits, Fehler, Verbindungen, UTF-8, leerer Text, CLI/EOF.
"""Deterministische Parser-Tests plus echte IPv4-TCP-Sockets und CLI-Prozesse."""

from pathlib import Path
import selectors
import socket
import subprocess
import sys
import threading
import unittest

from protocol import MAX_FRAME_BYTES, RECV_BYTES, ProtocolError, encode_frame, iter_frames

HERE = Path(__file__).resolve().parent


class ChunkSocket:
    """Erzwingt recv-Grenzen unabhängig von TCP-Segmentierung und Scheduling."""

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def recv(self, limit):
        chunk = next(self.chunks, b"")
        if len(chunk) > limit or limit != RECV_BYTES:
            raise AssertionError("recv-Limit nicht eingehalten")
        return chunk


class FramingTests(unittest.TestCase):
    def test_fragmentation_including_utf8_and_empty(self):
        chunks = [bytes([byte]) for byte in "Grüße 🌍\n\nEnde\n".encode("utf-8")]
        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["Grüße 🌍", "", "Ende"])

    def test_coalescing_and_remaining_partial_frame(self):
        chunks = [b"one\n\ntw", b"o\nthree", b"\n"]
        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["one", "", "two", "three"])

    def test_exact_limit(self):
        wire = encode_frame("ä" * (MAX_FRAME_BYTES // 2))
        chunks = [wire[i:i + RECV_BYTES] for i in range(0, len(wire), RECV_BYTES)]
        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["ä" * 2048])

    def test_outgoing_invalid(self):
        for text in ("a\nb", "x" * 4097, "ä" * 2049, "\ud800"):
            with self.subTest(text_kind=repr(text[:8])):
                with self.assertRaises(ProtocolError):
                    encode_frame(text)

    def test_invalid_frames_and_truncated_eof(self):
        for chunks in ([b"\xff\n"], [b"\xc3\n"], [b"missing LF"], [b"\xc3"]):
            with self.subTest(chunks=chunks):
                with self.assertRaises(ProtocolError):
                    list(iter_frames(ChunkSocket(chunks)))

    def test_oversized_with_and_without_lf(self):
        for ending in (b"", b"\n"):
            chunks = [b"x" * RECV_BYTES] * 4 + [b"x" + ending]
            with self.subTest(ending=ending):
                with self.assertRaises(ProtocolError):
                    list(iter_frames(ChunkSocket(chunks)))

    def test_empty_stream_is_not_empty_message(self):
        self.assertEqual(list(iter_frames(ChunkSocket([]))), [])
        self.assertEqual(encode_frame(""), b"\n")


class TCPTests(unittest.TestCase):
    def start_server(self, count=1, timeout=2.0):
        command = [sys.executable, "-B", "server.py", "--host", "127.0.0.1",
                   "--port", "0", "--connections", str(count), "--timeout", str(timeout)]
        process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.cleanup_process, process)
        assert process.stdout is not None
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(selector.select(5), "Keine READY-Ausgabe innerhalb von 5 s")
        ready = process.stdout.readline().strip()
        self.assertRegex(ready, r"^READY 127\.0\.0\.1:[1-9][0-9]*$")
        return process, int(ready.rsplit(":", 1)[1])

    def cleanup_process(self, process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
        process.stdout.close()
        process.stderr.close()

    def finish_server(self, process, expected_code=0):
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, expected_code, stderr)
        return stdout, stderr

    def connect(self, port):
        connection = socket.create_connection(("127.0.0.1", port), timeout=2)
        self.addCleanup(connection.close)
        return connection

    def run_client(self, port, *messages, timeout="2"):
        return subprocess.run([sys.executable, "-B", "client.py", "--host", "127.0.0.1",
                               "--port", str(port), "--timeout", timeout, "--", *messages],
                              cwd=HERE, text=True, capture_output=True, timeout=5)

    def test_real_tcp_fragmented_writes(self):
        process, port = self.start_server()
        with self.connect(port) as connection:
            for byte in "Grüße 🌍\n".encode("utf-8"):
                connection.sendall(bytes([byte]))
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(list(iter_frames(connection)), ["Grüße 🌍"])
            self.assertEqual(connection.recv(1), b"")
        stdout, stderr = self.finish_server(process)
        self.assertIn("'Grüße 🌍'", stdout)
        self.assertEqual(stderr, "")

    def test_real_tcp_coalesced_and_exact_limit(self):
        process, port = self.start_server()
        messages = ["one", "", "ä" * 2048, "last"]
        with self.connect(port) as connection:
            connection.sendall(b"".join(encode_frame(text) for text in messages))
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(list(iter_frames(connection)), messages)
        self.finish_server(process)

    def test_cli_single_persistent_and_multiple_connections(self):
        process, port = self.start_server(count=3)
        for messages in (("single",), ("eins", "Grüße 🌍", ""), ("last",)):
            result = self.run_client(port, *messages)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), [f"REPLY {text!r}" for text in messages])
        stdout, stderr = self.finish_server(process)
        self.assertEqual(stdout.count("RECEIVED "), 5)
        self.assertEqual(stderr, "")

    def test_empty_connection_then_valid_connection(self):
        process, port = self.start_server(count=2)
        with self.connect(port) as connection:
            connection.shutdown(socket.SHUT_WR)
            self.assertEqual(connection.recv(1), b"")
        result = self.run_client(port, "still alive")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.finish_server(process)

    def test_real_tcp_invalid_frames_and_recovery(self):
        payloads = [b"\xff\n", b"partial", b"\xc3\n", b"x" * 4097, b"x" * 4097 + b"\n"]
        for payload in payloads:
            with self.subTest(length=len(payload), prefix=repr(payload[:8])):
                process, port = self.start_server(count=2)
                with self.connect(port) as connection:
                    connection.sendall(payload)
                    connection.shutdown(socket.SHUT_WR)
                    try:
                        self.assertEqual(connection.recv(1), b"")
                    except ConnectionResetError:
                        pass
                result = self.run_client(port, "after error")
                self.assertEqual(result.returncode, 0, result.stderr)
                stdout, stderr = self.finish_server(process, expected_code=1)
                self.assertIn("ERROR connection:", stderr)
                self.assertIn("'after error'", stdout)

    def test_server_accept_timeout(self):
        process, unused_port = self.start_server(timeout=0.15)
        stdout, stderr = self.finish_server(process, expected_code=1)
        self.assertIn("ERROR server:", stderr)

    def test_server_connection_timeout(self):
        process, port = self.start_server(timeout=0.15)
        with self.connect(port) as connection:
            self.assertEqual(connection.recv(1), b"")
        stdout, stderr = self.finish_server(process, expected_code=1)
        self.assertIn("ERROR connection:", stderr)

    def test_client_rejects_bad_missing_extra_or_silent_reply(self):
        for response in (b"wrong\n", b"first\nextra\n", b"", b"\xff\n", b"first", None):
            with self.subTest(response=response):
                errors = []
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                    listener.bind(("127.0.0.1", 0))
                    listener.listen(1)
                    listener.settimeout(3)
                    port = listener.getsockname()[1]

                    def peer():
                        try:
                            connection, address = listener.accept()
                            with connection:
                                connection.settimeout(3)
                                request = bytearray()
                                while not request.endswith(b"\n"):
                                    data = connection.recv(1024)
                                    if not data:
                                        raise AssertionError("Client sendete keinen vollständigen Request")
                                    request.extend(data)
                                if bytes(request) != b"first\n":
                                    raise AssertionError("Falscher Request")
                                if response is not None:
                                    connection.sendall(response)
                                    connection.shutdown(socket.SHUT_WR)
                                if connection.recv(1) != b"":
                                    raise AssertionError("Client hat nicht geschlossen")
                        except Exception as error:
                            errors.append(error)

                    thread = threading.Thread(target=peer)
                    thread.start()
                    try:
                        result = self.run_client(port, "first", timeout="0.3")
                    finally:
                        thread.join(4)
                    self.assertFalse(thread.is_alive(), "Test-Peer hängt")
                    self.assertEqual(errors, [])
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn("ERROR client:", result.stderr)

    def test_cli_rejects_bad_arguments_and_payloads(self):
        for script, arguments in (("server.py", ["--connections", "-1"]),
                                  ("server.py", ["--port", "65536"]),
                                  ("client.py", ["--port", "0", "x"]),
                                  ("client.py", ["--timeout", "nan", "x"]),
                                  ("server.py", ["--timeout", "0"]),
                                  ("client.py", [])):
            with self.subTest(script=script, arguments=arguments):
                result = subprocess.run([sys.executable, "-B", script, *arguments], cwd=HERE,
                                        text=True, capture_output=True, timeout=3)
                self.assertEqual(result.returncode, 2)
        for text in ("a\nb", "x" * 4097):
            result = self.run_client(1, text)
            self.assertEqual(result.returncode, 1)
            self.assertIn("ERROR client:", result.stderr)
            self.assertNotIn("Connection refused", result.stderr)


if __name__ == "__main__":
    unittest.main()
