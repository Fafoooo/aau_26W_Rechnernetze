# KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)
# Datum: 2026-10-19
# Anfrage: Ü3.2 als reinen Socket-POP3-Client mit USER/PASS, LIST, RETR, QUIT und echten Fehler-/Fragmentierungstests implementieren.
"""Einfacher unverschlüsselter POP3-Client für lokale Laborkonten, ohne poplib."""

import argparse
import getpass
import ipaddress
import socket
import sys
from typing import Literal, overload


class POP3Error(Exception):
    """Negative Antwort des Servers (-ERR)."""


class ProtocolError(Exception):
    """Ungültige, zu lange oder unvollständige Serverantwort."""


class POP3Client:
    """Synchrone Socket-API; ein Objekt entspricht einer TCP-Sitzung."""

    def __init__(self, host="127.0.0.1", port=11110, timeout=10):
        self.socket = socket.create_connection((host, port), timeout=timeout)
        self.reader = self.socket.makefile("rb")
        self.closed = False
        try:
            self.greeting = self.status()
        except Exception:
            self.close()
            raise

    def read_line(self, limit=1024 * 1024):
        """Gepufferte CRLF-Zeile: TCP-Paketgrenzen sind keine Zeilengrenzen."""
        line = self.reader.readline(limit + 1)
        if not line or len(line) > limit or not line.endswith(b"\r\n"):
            raise ProtocolError("Fehlende CRLF-Zeile, EOF oder Zeilenlimit überschritten")
        return line[:-2]

    def status(self):
        """Statuszeile von höchstens 512 Bytes inklusive CRLF prüfen."""
        line = self.read_line(512)
        if line == b"-ERR" or line.startswith(b"-ERR "):
            raise POP3Error(line.decode("ascii", errors="replace"))
        if line != b"+OK" and not line.startswith(b"+OK "):
            raise ProtocolError(f"Ungültiger Status: {line!r}")
        return line

    @overload
    def command(self, text: str, multiline: Literal[False] = False) -> bytes: ...

    @overload
    def command(self, text: str, multiline: Literal[True]) -> list[bytes]: ...

    def command(self, text: str, multiline: bool = False) -> bytes | list[bytes]:
        """Einen Befehl senden und Status bzw. dot-entstuffte Daten lesen."""
        if self.closed:
            raise ProtocolError("Verbindung bereits geschlossen")
        if any(ord(character) < 32 or ord(character) > 126 for character in text):
            raise ValueError("Befehle müssen druckbares ASCII ohne CR/LF sein")
        wire = text.encode("ascii") + b"\r\n"
        if len(wire) > 255:
            raise ValueError("POP3-Befehl länger als 255 Bytes")
        try:
            self.socket.sendall(wire)
            result = self.status()
            if not multiline:
                return result
            lines = []
            size = 0
            while True:
                line = self.read_line()
                if line == b".":
                    return lines
                if line.startswith(b".."):
                    line = line[1:]
                elif line.startswith(b"."):
                    raise ProtocolError("Nicht dot-gestuffte Datenzeile")
                size += len(line) + 2
                if size > 20 * 1024 * 1024:
                    raise ProtocolError("Labordatenlimit von 20 MiB überschritten")
                lines.append(line)
        except (ProtocolError, OSError):
            self.close()  # Nach Framing-/Transportfehlern keine weitere Synchronität annehmen.
            raise

    def login(self, user, password):
        """USER und PASS nacheinander; Passwort nie protokollieren."""
        if not user or " " in user or not password:
            raise ValueError("Benutzer ohne Leerzeichen und nichtleeres Passwort erforderlich")
        self.command(f"USER {user}")
        return self.command(f"PASS {password}")

    def list_messages(self):
        """LIST ohne Argument liefert alle (Nummer, Oktettzahl)-Paare."""
        lines = self.command("LIST", multiline=True)
        result = []
        try:
            for line in lines:
                number, size = line.split()
                if not number.isdigit() or not size.isdigit() or int(number) < 1:
                    raise ValueError("invalid listing")
                result.append((int(number), int(size)))
            if len({number for number, _ in result}) != len(result):
                raise ValueError("duplicate message number")
        except ValueError as error:
            self.close()
            raise ProtocolError("Ungültige LIST-Daten") from error
        return result

    def retrieve(self, number):
        """Eine Mail als Bytes inklusive wiederhergestellter CRLF zurückgeben."""
        if not isinstance(number, int) or number < 1:
            raise ValueError("Positive Nachrichtennummer erforderlich")
        lines = self.command(f"RETR {number}", multiline=True)
        return b"".join(line + b"\r\n" for line in lines)

    def quit(self):
        """QUIT bestätigen lassen und auch bei Fehlern lokale Ressourcen schließen."""
        if self.closed:
            return None
        try:
            return self.command("QUIT")
        finally:
            self.close()

    def close(self):
        """Nur Transport schließen; ohne QUIT gibt es keinen UPDATE-Auftrag."""
        if not self.closed:
            self.closed = True
            try:
                self.reader.close()
            finally:
                self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        if exception_type is None:
            self.quit()
        else:
            self.close()  # Fehlerpfad bricht ab, statt mögliche Löschungen zu bestätigen.


def main(argv=None):
    """Testkonto anmelden, alle Nachrichten auflisten und genau eine abrufen."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=11110)
    parser.add_argument("--user", default="alice")
    parser.add_argument("--password", help="Nur für Testdaten; sonst verdeckte Abfrage")
    parser.add_argument("--message", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--allow-remote-plaintext", action="store_true")
    args = parser.parse_args(argv)
    try:
        local = ipaddress.ip_address(args.host).is_loopback
    except ValueError:
        local = args.host == "localhost"
    if not local and not args.allow_remote_plaintext:
        parser.error("Nicht-Loopback benötigt --allow-remote-plaintext; keine echten Passwörter!")
    password = args.password if args.password is not None else getpass.getpass("POP3-Testpasswort: ")
    try:
        with POP3Client(args.host, args.port, args.timeout) as client:
            print(client.greeting.decode("ascii"))
            client.login(args.user, password)
            listing = client.list_messages()
            print("LIST (Nummer, Oktette):", listing)
            if listing:
                print(f"RETR {args.message}:")
                print(client.retrieve(args.message).decode("utf-8", errors="replace"), end="")
            else:
                print("Maildrop leer; keine Nachricht abrufbar.")
        print("QUIT bestätigt; Verbindung geschlossen.")
    except (OSError, POP3Error, ProtocolError, ValueError) as error:
        print(f"POP3-Fehler: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
