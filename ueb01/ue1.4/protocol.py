# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.4 nutze exakt !HHI, V=2, reserved=0, positive uint16 und validierten Roundtrip.

"""Ü 1.4: 8-Byte-Protokollheader und variable, nichtleere Nutzlast."""

import argparse
import struct
import sys
from typing import NamedTuple


HEADER = struct.Struct("!HHI")
VERSION = 2
MAX_SEQUENCE = 65535
MAX_PAYLOAD_LENGTH = 4294967295


class MessageFields(NamedTuple):
    is_data: bool
    is_urgent: bool
    sequence_number: int
    payload: bytes


def validate_sequence(sequence_number: int) -> None:
    if type(sequence_number) is not int:
        raise TypeError("sequence_number muss int sein; bool ist nicht erlaubt.")
    if not 1 <= sequence_number <= MAX_SEQUENCE:
        raise ValueError("sequence_number muss im Bereich 1..65535 liegen.")


def create_message(is_data: bool, is_urgent: bool, sequence_number: int, payload: bytes) -> bytes:
    if type(is_data) is not bool or type(is_urgent) is not bool:
        raise TypeError("is_data und is_urgent müssen echte bool-Werte sein.")
    validate_sequence(sequence_number)
    if type(payload) is not bytes:
        raise TypeError("payload muss bytes sein.")
    if not 1 <= len(payload) <= MAX_PAYLOAD_LENGTH:
        raise ValueError("payload muss nichtleer sein und ihre Länge in uint32 passen.")
    word = (VERSION << 11) | (int(is_data) << 1) | int(is_urgent)
    return HEADER.pack(word, sequence_number, len(payload)) + payload


def parse_message(message: bytes) -> MessageFields:
    if type(message) is not bytes:
        raise TypeError("message muss bytes sein.")
    if len(message) < HEADER.size:
        raise ValueError("Nachricht ist kürzer als der 8-Byte-Header.")
    word, sequence_number, payload_length = HEADER.unpack_from(message)
    version = word >> 11
    reserved = (word >> 2) & 0x1FF
    if version != VERSION:
        raise ValueError("Versionsnummer muss 2 sein.")
    if reserved != 0:
        raise ValueError("Reservierte Bits müssen 0 sein.")
    validate_sequence(sequence_number)
    if payload_length == 0:
        raise ValueError("payload darf nicht leer sein.")
    if payload_length != len(message) - HEADER.size:
        raise ValueError("Payload-Länge im Header stimmt nicht mit der Nachricht überein.")
    return MessageFields(bool(word & 0b10), bool(word & 0b1), sequence_number, message[HEADER.size:])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", action="store_true", help="D-Flag setzen")
    parser.add_argument("--urgent", action="store_true", help="U-Flag setzen")
    parser.add_argument("--sequence", type=int, default=42)
    parser.add_argument("--payload", default="hello", help="Als UTF-8 kodierte Nutzlast")
    parser.add_argument("--message-hex", help="Statt Erzeugen eine Hex-Nachricht parsen")
    args = parser.parse_args(argv)
    try:
        if args.message_hex is None:
            message = create_message(args.data, args.urgent, args.sequence, args.payload.encode("utf-8"))
        else:
            message = bytes.fromhex(args.message_hex)
        fields = parse_message(message)
    except (ValueError, TypeError) as error:
        print(f"Protokollfehler: {error}", file=sys.stderr)
        return 1
    print(f"Nachricht (Hex): {message.hex(' ')}")
    print(f"Header: {HEADER.size} Bytes; Version: {VERSION}; Reserviert: 0")
    print(f"D: {fields.is_data}; U: {fields.is_urgent}; Sequenz: {fields.sequence_number}")
    print(f"Payload ({len(fields.payload)} Bytes): {fields.payload!r}")
    print(f"Roundtrip identisch: {create_message(*fields) == message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
