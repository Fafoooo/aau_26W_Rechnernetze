# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Ü3.3 als Socket-POP3-Threadserver mit Originaldatenbank, Zuständen, Maildrop-Sperren und GUI-API implementieren und testen.
"""Lokaler, unverschlüsselter POP3-Lernserver; keine produktiven Zugangsdaten."""

import argparse
import hashlib
import importlib.util
import ipaddress
from pathlib import Path
import socket
import socketserver
import threading


CRLF = b"\r\n"


def load_database():
    """Originaldatei relativ zum Skript laden, ohne sie zu ändern/kopieren."""
    path = Path(__file__).resolve().parents[1] / "Angabe" / "SampleDataBase.py"
    spec = importlib.util.spec_from_file_location("rn_sample_database", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Originaldatenbank nicht ladbar: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SampleDataBase()


def canonical_message(raw):
    """Mail in Bytes mit CRLF und genau einem hinzugefügten End-CRLF umwandeln."""
    data = raw.encode("utf-8") if isinstance(raw, str) else bytes(raw)
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", CRLF)
    return data if data.endswith(CRLF) else data + CRLF


def message_uid(user, record):
    """Stabile, druckbare UID unabhängig von der Sitzungs-Nachrichtennummer."""
    identity = f"{user}\0{record['id']}\0".encode("utf-8")
    return hashlib.sha256(identity + canonical_message(record["raw"])).hexdigest()


class POP3Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Ein Worker pro TCP-Verbindung; ein exklusiver Maildrop-Lock pro Benutzer."""

    allow_reuse_address = True
    daemon_threads = False
    block_on_close = True

    def __init__(self, address, database=None, client_timeout: float = 600):
        self.database = load_database() if database is None else database
        self.client_timeout = client_timeout
        self._guard = threading.Lock()
        self._maildrop_locks = {}
        self._connections = set()
        self._closing = False
        super().__init__(address, POP3Handler)

    def maildrop_lock(self, user):
        """Lock-Erzeugung ist selbst gegen gleichzeitige Logins geschützt."""
        with self._guard:
            return self._maildrop_locks.setdefault(user, threading.Lock())

    def server_close(self):
        """Offene Sitzungen abbrechen (Rollback), dann auf Worker-Ende warten."""
        with self._guard:
            self._closing = True
            connections = list(self._connections)
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        super().server_close()


class POP3Handler(socketserver.StreamRequestHandler):
    """Zustandsautomat: AUTHORIZATION -> TRANSACTION -> UPDATE nur durch QUIT."""

    server: POP3Server

    def handle(self):
        self.request.settimeout(self.server.client_timeout)
        self.user = None
        self.candidate = None
        self.lock = None
        self.messages = []
        self.deleted = set()
        with self.server._guard:
            if self.server._closing:
                return
            self.server._connections.add(self.request)
        try:
            self.reply(True, "RN POP3 ready (local plaintext lab)")
            while True:
                line = self.rfile.readline(256)
                if not line:
                    break
                if len(line) > 255 or not line.endswith(CRLF):
                    self.reply(False, "command too long or missing CRLF; closing")
                    break
                command = line[:-2]
                if not command or any(octet < 32 or octet > 126 for octet in command):
                    self.candidate = None
                    self.reply(False, "invalid command encoding")
                    continue
                name, separator, argument = command.decode("ascii").partition(" ")
                name = name.upper()
                args = argument.split(" ") if separator else []
                try:
                    if self.dispatch(name, argument, args):
                        break
                except ValueError:
                    self.reply(False, "invalid arguments or no such message")
        except (OSError, TimeoutError):
            pass  # Kein QUIT: insbesondere keine Löschungen übernehmen.
        finally:
            if self.lock is not None:
                self.lock.release()
            with self.server._guard:
                self.server._connections.discard(self.request)

    def reply(self, success, text):
        """Genau eine Statuszeile senden."""
        prefix = b"+OK " if success else b"-ERR "
        self.wfile.write(prefix + text.encode("ascii") + CRLF)

    def multiline(self, text, lines):
        """Status, dot-gestuffte Datenzeilen und Punkt-Endmarke senden."""
        self.reply(True, text)
        for line in lines:
            self.wfile.write((b"." if line.startswith(b".") else b"") + line + CRLF)
        self.wfile.write(b".\r\n")

    def active_messages(self):
        """Nummern bleiben während der Sitzung trotz DELE unverändert."""
        return [(number, message) for number, message in enumerate(self.messages, 1)
                if number not in self.deleted]

    def message(self, token):
        """Nur positive dezimale Nummern nicht gelöschter Nachrichten zulassen."""
        if not token.isascii() or not token.isdecimal():
            raise ValueError("not a message number")
        number = int(token)
        if not 1 <= number <= len(self.messages) or number in self.deleted:
            raise ValueError("no such message")
        return number, self.messages[number - 1]

    def login(self, password):
        """Authentifizieren, exklusiven Lock holen und konsistenten Snapshot bilden."""
        if self.candidate is None:
            self.reply(False, "send USER first")
            return
        user = self.candidate
        self.candidate = None
        if not self.server.database.authenticate(user, password):
            self.reply(False, "authentication failed")
            return
        lock = self.server.maildrop_lock(user)
        if not lock.acquire(blocking=False):
            self.reply(False, "[IN-USE] maildrop locked")
            return
        self.lock = lock
        self.messages = [dict(record, raw=canonical_message(record["raw"]))
                         for record in self.server.database.get_messages(user)]
        self.user = user
        self.reply(True, "maildrop locked and ready")

    def dispatch(self, name, argument, args):
        """Befehl ausführen; True bedeutet Sitzungsende, False Weiterarbeiten."""
        if name not in ("USER", "PASS"):
            self.candidate = None  # PASS darf nur unmittelbar auf erfolgreiches USER folgen.
        if name == "CAPA" and not args:
            self.multiline("capabilities", [b"USER", b"TOP", b"UIDL", b"RESP-CODES",
                                           b"EXPIRE NEVER", b"IMPLEMENTATION RN-POP3"])
        elif name == "QUIT" and not args:
            if self.user is not None:
                # UPDATE: Original-API liefert die lebende, veränderbare Nachrichtenliste.
                records = self.server.database.get_messages(self.user)
                removed = {self.messages[n - 1]["id"] for n in self.deleted}
                records[:] = [record for record in records if record["id"] not in removed]
            self.reply(True, "goodbye")
            return True
        elif self.user is None:
            if name == "USER":
                self.candidate = None
                if len(args) != 1 or not args[0]:
                    raise ValueError("USER requires one name")
                self.candidate = args[0]
                self.reply(True, "send PASS")
            elif name == "PASS":
                if not argument:
                    self.candidate = None
                    raise ValueError("PASS requires a password")
                self.login(argument)  # Ein Passwort darf Leerzeichen enthalten (RFC 1939).
            else:
                self.reply(False, "authenticate with USER and PASS first")
        elif name in ("STAT", "NOOP", "RSET") and not args:
            if name == "RSET":
                self.deleted.clear()
            active = self.active_messages()
            self.reply(True, f"{len(active)} {sum(len(m['raw']) for _, m in active)}")
        elif name in ("LIST", "UIDL") and len(args) <= 1:
            if args:
                number, record = self.message(args[0])
                value = len(record["raw"]) if name == "LIST" else message_uid(self.user, record)
                self.reply(True, f"{number} {value}")
            else:
                lines = []
                for number, record in self.active_messages():
                    value = len(record["raw"]) if name == "LIST" else message_uid(self.user, record)
                    lines.append(f"{number} {value}".encode("ascii"))
                self.multiline("listing follows", lines)
        elif name in ("RETR", "DELE") and len(args) == 1:
            number, record = self.message(args[0])
            if name == "DELE":
                self.deleted.add(number)
                self.reply(True, "message marked")
            else:
                self.multiline(f"{len(record['raw'])} octets", record["raw"][:-2].split(CRLF))
        elif name == "TOP" and len(args) == 2:
            _, record = self.message(args[0])
            if not args[1].isascii() or not args[1].isdecimal():
                raise ValueError("invalid body line count")
            count = int(args[1])
            header, separator, body = record["raw"].partition(CRLF + CRLF)
            if not separator:
                header, body = record["raw"][:-2], b""
            body_lines = body[:-2].split(CRLF) if body.endswith(CRLF) else []
            self.multiline("top follows", header.split(CRLF) + [b""] + body_lines[:count])
        else:
            self.reply(False, "unknown command, wrong state or invalid arguments")
        return False


def create_server(host="127.0.0.1", port=11110, database=None, client_timeout: float = 600):
    """GUI-API: gebundenen Server erzeugen; port=0 wählt einen freien Testport."""
    return POP3Server((host, port), database, client_timeout)


def main(argv=None):
    """CLI: bewusst nur lokale Testkonten über unverschlüsseltes POP3 verwenden."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=11110)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--allow-remote-plaintext", action="store_true")
    args = parser.parse_args(argv)
    try:
        local = ipaddress.ip_address(args.host).is_loopback
    except ValueError:
        local = args.host == "localhost"
    if not local and not args.allow_remote_plaintext:
        parser.error("Nicht-Loopback benötigt --allow-remote-plaintext; nur Testdaten!")
    with create_server(args.host, args.port, client_timeout=args.timeout) as server:
        print(f"POP3 plaintext lab: {server.server_address[0]}:{server.server_address[1]}", flush=True)
        print("Testkonto alice / secret; keine echten Zugangsdaten verwenden.", flush=True)
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
