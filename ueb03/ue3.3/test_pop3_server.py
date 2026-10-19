# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Ü3.3 unabhängig mit poplib und Rohsockets auf Zustände, Parallelität, CRLF, Dot-Stuffing und transaktionale Löschungen testen.
"""Echte TCP-Tests; poplib ist nur unabhängiger Testclient, nicht Implementierung."""

from concurrent.futures import ThreadPoolExecutor
import poplib
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import unittest

from pop3_server import canonical_message, create_server, load_database, message_uid


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.db = load_database()
        # Nur diese frische Instanz ergänzen; Originaldateien bleiben unverändert.
        self.db.users["bob"] = {
            "password": "bob-test",
            "messages": [{"id": 99, "raw": "Subject: Dots\n\n.first\n.\n..third\nGrüße\n"}],
        }
        self.db.users["empty"] = {"password": "empty-test", "messages": []}
        self.server = create_server(port=0, database=self.db, client_timeout=2)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.01})
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(3)
        self.assertFalse(self.thread.is_alive())
        self.assertFalse(self.server._connections)

    def connect(self, user="alice", password="secret"):
        client = poplib.POP3(*self.server.server_address, timeout=2)
        self.addCleanup(client.close)
        client.user(user)
        client.pass_(password)
        return client

    def raw(self):
        connection = socket.create_connection(self.server.server_address, timeout=2)
        reader = connection.makefile("rb")
        self.addCleanup(connection.close)
        self.addCleanup(reader.close)
        self.assertTrue(reader.readline().startswith(b"+OK "))
        return connection, reader

    def test_original_data_and_readme_password_discrepancy(self):
        self.assertTrue(self.db.authenticate("alice", "secret"))
        self.assertFalse(self.db.authenticate("alice", "alice123"))
        self.assertEqual(len(load_database().get_messages("alice")), 4)
        client = self.connect()
        self.assertEqual(client.stat()[0], 4)
        client.quit()

    def test_poplib_full_session_sizes_capa_uidl_top_noop(self):
        client = self.connect()
        expected = [canonical_message(record["raw"]) for record in self.db.get_messages("alice")]
        self.assertEqual(client.stat(), (len(expected), sum(map(len, expected))))
        self.assertEqual(set(client.capa()), {"USER", "TOP", "UIDL", "RESP-CODES", "EXPIRE", "IMPLEMENTATION"})
        listing = client.list()[1]
        self.assertEqual(listing, [f"{n} {len(mail)}".encode() for n, mail in enumerate(expected, 1)])
        for number, mail in enumerate(expected, 1):
            self.assertEqual(client.list(number).split()[1:], [str(number).encode(), str(len(mail)).encode()])
            _, lines, _ = client.retr(number)
            self.assertEqual(b"\r\n".join(lines) + b"\r\n", mail)
            uid = client.uidl(number).split()[-1]
            self.assertEqual(uid.decode(), message_uid("alice", self.db.get_messages("alice")[number - 1]))
        self.assertEqual(len(client.uidl()[1]), 4)
        _, top_lines, _ = client.top(1, 0)
        self.assertEqual(b"\r\n".join(top_lines) + b"\r\n", expected[0].partition(b"\r\n\r\n")[0] + b"\r\n\r\n")
        self.assertTrue(client.noop().startswith(b"+OK"))
        client.quit()

    def test_wire_dot_stuffing_crlf_and_unicode_octets(self):
        client = self.connect("bob", "bob-test")
        expected = canonical_message(self.db.get_messages("bob")[0]["raw"])
        self.assertEqual(client.stat(), (1, len(expected)))
        self.assertEqual(b"\r\n".join(client.retr(1)[1]) + b"\r\n", expected)
        self.assertEqual(client.top(1, 2)[1], [b"Subject: Dots", b"", b".first", b"."])
        client.quit()
        connection, reader = self.raw()
        connection.sendall(b"USER bob\r\nPASS bob-test\r\nRETR 1\r\n")
        self.assertTrue(reader.readline().startswith(b"+OK"))
        self.assertTrue(reader.readline().startswith(b"+OK"))
        self.assertTrue(reader.readline().startswith(b"+OK"))
        lines = []
        while True:
            line = reader.readline()
            self.assertTrue(line.endswith(b"\r\n"))
            if line == b".\r\n":
                break
            lines.append(line)
        self.assertIn(b"..first\r\n", lines)
        self.assertIn(b"..\r\n", lines)
        self.assertIn(b"...third\r\n", lines)
        connection.sendall(b"QUIT\r\n")
        self.assertTrue(reader.readline().startswith(b"+OK"))
        self.assertEqual(reader.readline(), b"")

    def test_dele_rset_update_and_uid_stability_after_renumber(self):
        client = self.connect()
        uid = client.uidl(2).split()[-1]
        client.dele(1)
        self.assertEqual(len(self.db.get_messages("alice")), 4)
        self.assertEqual(client.stat()[0], 3)
        self.assertTrue(client.list()[1][0].startswith(b"2 "))
        for command in ("RETR 1", "LIST 1", "UIDL 1", "TOP 1 0", "DELE 1"):
            with self.subTest(command=command), self.assertRaises(poplib.error_proto):
                client._shortcmd(command)
        client.rset()
        self.assertEqual(client.stat()[0], 4)
        client.dele(1)
        client.quit()
        self.assertEqual(len(self.db.get_messages("alice")), 3)
        second = self.connect()
        self.assertEqual(second.uidl(1).split()[-1], uid)
        second.quit()

    def test_disconnect_rolls_back_and_unlocks(self):
        client = self.connect()
        client.dele(2)
        client.close()  # Kein QUIT: simulierter Client-Absturz.
        lock = self.server.maildrop_lock("alice")
        self.assertTrue(lock.acquire(timeout=2))
        lock.release()
        self.assertEqual(len(self.db.get_messages("alice")), 4)
        next_client = self.connect()
        self.assertEqual(next_client.stat()[0], 4)
        next_client.quit()

    def test_concurrent_users_and_same_maildrop_rejected(self):
        barrier = threading.Barrier(3)
        release = threading.Event()

        def session(user, password):
            client = self.connect(user, password)
            try:
                barrier.wait(timeout=3)
                self.assertTrue(release.wait(timeout=3))
                return client.stat()[0]
            finally:
                client.quit()

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(session, "alice", "secret")
            second = pool.submit(session, "bob", "bob-test")
            try:
                barrier.wait(timeout=3)
                self.assertGreaterEqual(len(self.server._connections), 2)
                blocked = poplib.POP3(*self.server.server_address, timeout=2)
                self.addCleanup(blocked.close)
                blocked.user("alice")
                with self.assertRaisesRegex(poplib.error_proto, "IN-USE"):
                    blocked.pass_("secret")
                blocked.quit()
            finally:
                release.set()
            self.assertEqual(first.result(timeout=3), 4)
            self.assertEqual(second.result(timeout=3), 1)

    def test_authorization_wrong_states_and_syntax(self):
        client = poplib.POP3(*self.server.server_address, timeout=2)
        self.addCleanup(client.close)
        self.assertIn("USER", client.capa())
        for command in ("STAT", "PASS secret", "RETR 1", "DELE 1", "NOOP", "RSET", "LIST", "UIDL", "TOP 1 0", "BOGUS", "CAPA x", "QUIT x"):
            with self.subTest(command=command), self.assertRaises(poplib.error_proto):
                client._shortcmd(command)
        client.user("alice")
        with self.assertRaises(poplib.error_proto):
            client.pass_("alice123")
        with self.assertRaises(poplib.error_proto):
            client.pass_("secret")
        client.user("alice")
        with self.assertRaises(poplib.error_proto):
            client.noop()
        with self.assertRaises(poplib.error_proto):
            client.pass_("secret")
        client.user("alice")
        with self.assertRaises(poplib.error_proto):
            client._shortcmd("PASS")
        with self.assertRaises(poplib.error_proto):
            client.pass_("secret")
        client.user("nobody")
        with self.assertRaises(poplib.error_proto):
            client.pass_("secret")
        client.user("alice")
        client.pass_("secret")
        for command in ("USER bob", "PASS secret", "STAT x", "NOOP x", "RSET x", "LIST 0", "LIST -1", "LIST +1", "LIST abc", "LIST 99", "LIST 1 2", "RETR", "TOP 1 -1", "TOP 1 nope", "DELE 2 3", "AUTH", "STLS", "APOP a b"):
            with self.subTest(command=command), self.assertRaises(poplib.error_proto):
                client._shortcmd(command)
        self.assertEqual(client.stat()[0], 4)
        client.quit()

    def test_fragmentation_multiple_commands_and_lowercase(self):
        connection, reader = self.raw()
        wire = b"user alice\r\npass secret\r\nstat\r\nnoop\r\nquit\r\n"
        for octet in wire:
            connection.sendall(bytes([octet]))
        for _ in range(5):
            self.assertTrue(reader.readline().startswith(b"+OK"))
        self.assertEqual(reader.readline(), b"")

    def test_command_length_limit_and_invalid_framing(self):
        connection, reader = self.raw()
        maximum = b"USER " + b"x" * (255 - len(b"USER \r\n")) + b"\r\n"
        self.assertEqual(len(maximum), 255)
        connection.sendall(maximum)
        self.assertTrue(reader.readline().startswith(b"+OK"))
        connection.sendall(b"USER " + b"x" * 249 + b"\r\n")
        self.assertTrue(reader.readline().startswith(b"-ERR"))
        self.assertEqual(reader.readline(), b"")
        other, output = self.raw()
        other.sendall(b"USER alice\n")
        self.assertTrue(output.readline().startswith(b"-ERR"))
        self.assertEqual(output.readline(), b"")
        third, result = self.raw()
        third.sendall(b"USER \xff\r\nCAPA\r\n")
        self.assertTrue(result.readline().startswith(b"-ERR"))
        self.assertTrue(result.readline().startswith(b"+OK"))

    def test_empty_mailbox_and_quit_in_authorization(self):
        client = self.connect("empty", "empty-test")
        self.assertEqual(client.stat(), (0, 0))
        self.assertEqual(client.list()[1], [])
        self.assertEqual(client.uidl()[1], [])
        client.rset()
        with self.assertRaises(poplib.error_proto):
            client.retr(1)
        client.quit()
        anonymous = poplib.POP3(*self.server.server_address, timeout=2)
        self.addCleanup(anonymous.close)
        anonymous.quit()
        self.assertEqual(len(self.db.get_messages("alice")), 4)

    def test_timeout_rolls_back_and_releases_lock(self):
        self.server.client_timeout = 0.1
        client = self.connect()
        client.dele(1)
        # Blockierendes Lesen wartet auf den echten Server-Timeout, kein blindes sleep.
        self.assertEqual(client.file.readline(), b"")
        lock = self.server.maildrop_lock("alice")
        self.assertTrue(lock.acquire(timeout=2))
        lock.release()
        self.assertEqual(len(self.db.get_messages("alice")), 4)

    def test_server_close_aborts_active_session_without_update(self):
        client = self.connect()
        client.dele(1)
        self.server.shutdown()
        self.server.server_close()
        self.assertEqual(client.file.readline(), b"")
        self.assertEqual(len(self.db.get_messages("alice")), 4)
        self.assertFalse(self.server._connections)

    def test_password_with_spaces(self):
        self.db.users["bob"]["password"] = "test with spaces"
        client = self.connect("bob", "test with spaces")
        self.assertEqual(client.stat()[0], 1)
        client.quit()

    def test_canonicalization_preserves_trailing_blank_lines(self):
        self.assertEqual(canonical_message("a\rb\nc\r\n\r\n"), b"a\r\nb\r\nc\r\n\r\n")
        self.assertEqual(canonical_message(b"header\n\nbody"), b"header\r\n\r\nbody\r\n")
        self.assertNotEqual(message_uid("alice", {"id": 1, "raw": "x"}),
                            message_uid("alice", {"id": 2, "raw": "x"}))

    def test_real_server_cli_and_client_cli_subprocesses(self):
        root = Path(__file__).resolve().parents[1]
        process = subprocess.Popen([sys.executable, str(root / "ue3.3" / "pop3_server.py"),
                                    "--port", "0"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        try:
            banner = process.stdout.readline().strip()
            self.assertTrue(banner.startswith("POP3 plaintext lab: 127.0.0.1:"), banner)
            port = int(banner.rsplit(":", 1)[1])
            self.assertIn("alice / secret", process.stdout.readline())
            result = subprocess.run([sys.executable, str(root / "ue3.2" / "pop3_client.py"),
                                     "--port", str(port), "--user", "alice", "--password", "secret"],
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("QUIT bestätigt", result.stdout)
            print("\nEchter CLI-Lauf (separater Server- und Clientprozess):\n" + result.stdout)
            client = poplib.POP3("127.0.0.1", port, timeout=2)
            try:
                client.user("alice")
                client.pass_("secret")
                self.assertEqual(client.stat()[0], 4)
                client.quit()
            finally:
                client.close()
        finally:
            process.send_signal(signal.SIGINT)
            try:
                _, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise
            self.assertEqual(process.returncode, 0, stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
