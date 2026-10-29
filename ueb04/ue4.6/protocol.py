# KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.
# Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Auftrag: Ü4.6 TCP-Protokoll für einzelne und persistente UTF-8-Nachrichten
# mit LF-Framing, Fragmentierung, Coalescing, EOF und Größenlimit implementieren.
"""Kleines Echo-Protokoll: UTF-8-Text (maximal 4096 Bytes), dann ein LF-Byte."""

MAX_FRAME_BYTES = 4096
RECV_BYTES = 1024


class ProtocolError(ValueError):
    """Der Peer oder die Eingabe verletzt das vereinbarte Nachrichtenformat."""


def encode_frame(text):
    """Prüfe ausgehenden Text und hänge genau einen Frame-Abschluss an."""
    if "\n" in text:
        raise ProtocolError("Eingebettetes LF ist nicht erlaubt")
    try:
        payload = text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ProtocolError("Text ist nicht als UTF-8 kodierbar") from error
    if len(payload) > MAX_FRAME_BYTES:
        raise ProtocolError("Frame überschreitet 4096 Nutzbytes")
    return payload + b"\n"


def iter_frames(connection):
    """Liefere vollständige Texte; nur EOF zwischen Frames ist regulär."""
    pending = bytearray()
    while True:
        chunk = connection.recv(RECV_BYTES)
        if not chunk:
            if pending:
                raise ProtocolError("EOF in unvollständigem Frame (LF fehlt)")
            return
        pending.extend(chunk)
        while b"\n" in pending:
            end = pending.index(b"\n")
            if end > MAX_FRAME_BYTES:
                raise ProtocolError("Frame überschreitet 4096 Nutzbytes")
            payload = bytes(pending[:end])
            del pending[:end + 1]
            try:
                text = payload.decode("utf-8", errors="strict")
            except UnicodeDecodeError as error:
                raise ProtocolError("Frame enthält ungültiges UTF-8") from error
            yield text
        if len(pending) > MAX_FRAME_BYTES:
            raise ProtocolError("Frame überschreitet 4096 Nutzbytes")
