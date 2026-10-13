# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.4 gegen feste Binärvektoren, alle Flags, Grenzen und ungültige Nachrichten.

import itertools
import unittest
from unittest import mock

from support import load_module, run_cli

protocol = load_module("ue1.4/protocol.py", "ueb01_protocol")
CANONICAL = bytes.fromhex("10 00 00 2a 00 00 00 05 68 65 6c 6c 6f")


class ProtocolTests(unittest.TestCase):
    def test_independently_specified_binary_vectors(self):
        vectors = [
            ((False, False, 42, b"hello"), "10 00 00 2a 00 00 00 05 68 65 6c 6c 6f"),
            ((False, True, 1, b"x"), "10 01 00 01 00 00 00 01 78"),
            ((True, False, 256, b"x"), "10 02 01 00 00 00 00 01 78"),
            ((True, True, 65535, b"\x00\xff"), "10 03 ff ff 00 00 00 02 00 ff"),
        ]
        for fields, hexadecimal in vectors:
            with self.subTest(fields=fields):
                expected = bytes.fromhex(hexadecimal)
                self.assertEqual(protocol.create_message(*fields), expected)
                self.assertEqual(protocol.parse_message(expected), fields)

    def test_all_flags_bounds_and_binary_payloads_roundtrip(self):
        for is_data, is_urgent, sequence, payload in itertools.product(
            (False, True), (False, True), (1, 42, 65535), (b"\x00", b"\x00\xffabc", "ä🌍".encode("utf-8"))
        ):
            fields = (is_data, is_urgent, sequence, payload)
            with self.subTest(fields=fields):
                message = protocol.create_message(*fields)
                parsed = protocol.parse_message(message)
                self.assertEqual(parsed, fields)
                self.assertIs(type(parsed.is_data), bool)
                self.assertIs(type(parsed.is_urgent), bool)
                self.assertEqual(len(message), 8 + len(payload))
                self.assertEqual(protocol.create_message(*parsed), message)

    def test_strict_flag_types(self):
        for bad in [0, 1, None, "True", [], 1.0]:
            for flags in [(bad, True), (False, bad)]:
                with self.subTest(flags=flags), self.assertRaises(TypeError):
                    protocol.create_message(*flags, 1, b"x")

    def test_strict_sequence_types(self):
        for bad in [True, False, None, "1", 1.0]:
            with self.subTest(sequence=bad), self.assertRaises(TypeError):
                protocol.create_message(False, False, bad, b"x")

    def test_positive_uint16_boundaries(self):
        for bad in [-1, 0, 65536, 2**80]:
            with self.subTest(sequence=bad), self.assertRaises(ValueError):
                protocol.create_message(False, False, bad, b"x")

    def test_payload_types_and_empty_payload(self):
        for bad in ["x", bytearray(b"x"), memoryview(b"x"), None, 1]:
            with self.subTest(payload=bad), self.assertRaises(TypeError):
                protocol.create_message(False, False, 1, bad)
        with self.assertRaises(ValueError):
            protocol.create_message(False, False, 1, b"")

    def test_uint32_length_guard_with_controlled_small_limit(self):
        with mock.patch.object(protocol, "MAX_PAYLOAD_LENGTH", 2):
            with self.assertRaises(ValueError):
                protocol.create_message(False, False, 1, b"abc")

    def test_parser_types(self):
        for bad in ["message", None, bytearray(CANONICAL), memoryview(CANONICAL), 123]:
            with self.subTest(message=bad), self.assertRaises(TypeError):
                protocol.parse_message(bad)

    def test_all_truncated_header_lengths(self):
        for length in range(8):
            with self.subTest(length=length), self.assertRaises(ValueError):
                protocol.parse_message(CANONICAL[:length])

    def test_wrong_versions(self):
        for version in [0, 1, 3, 31]:
            message = (version << 11).to_bytes(2, "big") + CANONICAL[2:]
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "Versionsnummer"):
                protocol.parse_message(message)

    def test_each_of_nine_reserved_bits(self):
        for bit in range(2, 11):
            message = bytearray(CANONICAL)
            byte_index = 1 if bit < 8 else 0
            message[byte_index] |= 1 << (bit % 8)
            with self.subTest(bit=bit), self.assertRaisesRegex(ValueError, "Reservierte"):
                protocol.parse_message(bytes(message))

    def test_parser_rejects_zero_sequence(self):
        message = CANONICAL[:2] + b"\x00\x00" + CANONICAL[4:]
        with self.assertRaisesRegex(ValueError, "1..65535"):
            protocol.parse_message(message)

    def test_zero_payload_length_with_and_without_data(self):
        for payload in [b"", b"hello"]:
            message = CANONICAL[:4] + b"\x00\x00\x00\x00" + payload
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "nicht leer"):
                protocol.parse_message(message)

    def test_length_mismatch_small_and_uint32_max(self):
        for claimed_length in [1, 4, 6, 4294967295]:
            message = CANONICAL[:4] + claimed_length.to_bytes(4, "big") + CANONICAL[8:]
            with self.subTest(length=claimed_length), self.assertRaisesRegex(ValueError, "Payload-Länge"):
                protocol.parse_message(message)

    def test_truncated_payload_extra_bytes_and_header_only(self):
        for message in [CANONICAL[:-1], CANONICAL + b"x", CANONICAL[:8]]:
            with self.subTest(message=message), self.assertRaises(ValueError):
                protocol.parse_message(message)

    def test_default_cli_matches_canonical_vector(self):
        process = run_cli("ue1.4/protocol.py")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn(CANONICAL.hex(" "), process.stdout)
        self.assertIn("Roundtrip identisch: True", process.stdout)

    def test_cli_binary_parser_and_utf8_payload(self):
        parsed = run_cli("ue1.4/protocol.py", "--message-hex", CANONICAL.hex())
        self.assertEqual(parsed.returncode, 0, parsed.stderr)
        generated = run_cli("ue1.4/protocol.py", "--data", "--urgent", "--sequence", 65535, "--payload", "ä")
        self.assertEqual(generated.returncode, 0, generated.stderr)
        self.assertIn("10 03 ff ff 00 00 00 02 c3 a4", generated.stdout)

    def test_invalid_cli_inputs(self):
        for arguments in [("--sequence", "0"), ("--payload", ""), ("--message-hex", "xx"), ("--message-hex", "18 00 00 2a 00 00 00 01 78")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.4/protocol.py", *arguments)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Protokollfehler", process.stderr)


if __name__ == "__main__":
    unittest.main()
