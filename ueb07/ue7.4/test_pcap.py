# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Echte PCAP offline prüfen; Protokoll, Echo-Zuordnung, Header und Readiness-Frist negativ testen.
"""Nur Dateilesen und Bytekopien: keine Sockets, Netzänderungen oder neuen Messdaten."""
import ast
import json
from pathlib import Path
import struct
import unittest
from unittest.mock import MagicMock, Mock, patch

from pcap_pruefen import inspect

BASE = Path(__file__).resolve().parents[1]
EVIDENCE = BASE / "nachweise/run01"


def capture(packets, endian="<", nano=False):
    magic = 0xa1b23c4d if nano else 0xa1b2c3d4
    raw = struct.pack(endian + "IHHIIII", magic, 2, 4, 0, 0, 262144, 1)
    for packet in packets:
        raw += struct.pack(endian + "IIII", 0, 0, len(packet), len(packet)) + packet
    return raw


def positions(packet):
    icmp = 14 + (packet[14] & 15) * 4
    quoted = icmp + 8
    return icmp, quoted, quoted + (packet[quoted] & 15) * 4


class PcapTests(unittest.TestCase):
    def setUp(self):
        self.raw = (EVIDENCE / "fault.pcap").read_bytes()
        self.expected = json.loads((EVIDENCE / "fault-frames.json").read_text())
        self.assertIn(self.raw[:4], (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"))
        self.packets, offset = [], 24
        while offset < len(self.raw):
            length = struct.unpack_from("<I", self.raw, offset + 8)[0]
            self.packets.append(bytearray(self.raw[offset + 16:offset + 16 + length]))
            offset += 16 + length
        self.assertEqual(len(self.packets), 4)
        self.assertEqual([packet[positions(packet)[0]] for packet in self.packets], [8, 3, 8, 3])

    def parse(self, raw):
        with patch.object(Path, "read_bytes", return_value=bytes(raw)):
            return inspect("synthetische-bytekopie.pcap")

    def reject(self, packets, message=None):
        with self.assertRaisesRegex(AssertionError, message or ".*"):
            self.parse(capture(packets))

    def test_real_capture_and_unchanged_result_shape(self):
        self.assertEqual(inspect(EVIDENCE / "fault.pcap"), self.expected)
        self.assertEqual(self.expected, json.loads((EVIDENCE / "results.json").read_text())["fault"])

    def test_all_four_pcap_magics(self):
        for endian in ("<", ">"):
            for nano in (False, True):
                with self.subTest(endian=endian, nano=nano):
                    self.assertEqual(self.parse(capture(self.packets, endian, nano)), self.expected)

    def test_wrong_quoted_protocol(self):
        _, quoted, _ = positions(self.packets[1])
        self.packets[1][quoted + 9] = 17
        self.reject(self.packets, "Zitiertes Protokoll")

    def test_wrong_quoted_echo_type_or_code(self):
        _, _, echo = positions(self.packets[1])
        for offset, value in ((echo, 0), (echo + 1, 1)):
            with self.subTest(offset=offset):
                packets = [packet.copy() for packet in self.packets]
                packets[1][offset] = value
                self.reject(packets, "Zitierter Echo Request")

    def test_error_for_unknown_id_or_sequence(self):
        _, _, echo = positions(self.packets[1])
        for offset in (echo + 4, echo + 6):
            with self.subTest(offset=offset):
                packets = [packet.copy() for packet in self.packets]
                packets[1][offset] ^= 1
                self.reject(packets, "nicht eindeutig")

    def test_duplicate_errors_do_not_cover_both_requests(self):
        first = positions(self.packets[1])[2]
        second = positions(self.packets[3])[2]
        self.packets[3][second + 4:second + 8] = self.packets[1][first + 4:first + 8]
        self.reject(self.packets, "nicht eindeutig")

    def test_duplicate_request_keys_even_with_matching_errors(self):
        for first, second, part in ((0, 2, 0), (1, 3, 2)):
            a, b = positions(self.packets[first])[part], positions(self.packets[second])[part]
            self.packets[second][b + 4:b + 8] = self.packets[first][a + 4:a + 8]
        self.reject(self.packets, "Doppelte Echo-ID/Sequenz")

    def test_minimum_quote_is_valid_but_seven_echo_bytes_are_not(self):
        _, _, echo = positions(self.packets[1])
        for length in (8, 7):
            with self.subTest(echo_bytes=length):
                packets = [packet.copy() for packet in self.packets]
                packets[1] = packets[1][:echo + length]
                struct.pack_into("!H", packets[1], 16, len(packets[1]) - 14)
                if length == 8:
                    self.assertEqual(self.parse(capture(packets)), self.expected)
                else:
                    self.reject(packets)

    def test_quoted_options_shift_echo_header(self):
        packet = self.packets[1]
        _, quoted, _ = positions(packet)
        packet[quoted + 20:quoted + 20] = b"\x01\x01\x01\x00"
        packet[quoted] = 0x46
        for offset in (16, quoted + 2):
            struct.pack_into("!H", packet, offset, struct.unpack_from("!H", packet, offset)[0] + 4)
        self.assertEqual(self.parse(capture(self.packets)), self.expected)
        packet[positions(packet)[2] + 6] ^= 1
        self.reject(self.packets, "nicht eindeutig")

    def test_bad_ip_header_bytes(self):
        _, quoted, _ = positions(self.packets[1])
        cases = ((0, 14, b"\x44"), (0, 14, b"\x65"), (1, quoted, b"\x44"),
                 (1, quoted, b"\x65"), (1, quoted + 2, b"\x00\x1b"),
                 (1, quoted + 6, b"\x20\x00"), (1, quoted + 6, b"\x00\x01"))
        for frame, offset, value in cases:
            with self.subTest(frame=frame, offset=offset, value=value):
                packets = [packet.copy() for packet in self.packets]
                packets[frame][offset:offset + len(value)] = value
                self.reject(packets)

    def test_claimed_quoted_options_must_be_present(self):
        _, quoted, _ = positions(self.packets[1])
        self.packets[1] = self.packets[1][:quoted + 28]
        struct.pack_into("!H", self.packets[1], 16, len(self.packets[1]) - 14)
        self.packets[1][quoted] = 0x46
        self.reject(self.packets)

    def test_truncated_records_and_packets(self):
        for raw in (self.raw[:-1], self.raw[:30]):
            with self.subTest(length=len(raw)), self.assertRaisesRegex(AssertionError, "Abgeschnitten"):
                self.parse(raw)
        raw = bytearray(self.raw)
        struct.pack_into("<I", raw, 36, struct.unpack_from("<I", raw, 36)[0] + 1)
        with self.assertRaisesRegex(AssertionError, "Abgeschnittenes Paket"):
            self.parse(raw)

    def test_invalid_global_header_bytes(self):
        for raw in (self.raw[:23], b"BAD!" + self.raw[4:]):
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                self.parse(raw)
        raw = bytearray(self.raw)
        struct.pack_into("<I", raw, 20, 113)
        with self.assertRaisesRegex(AssertionError, "Ethernet erwartet"):
            self.parse(raw)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((BASE / "verify_namespaces.py").read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "capture_fault")
        block = next(node for node in ast.walk(function) if isinstance(node, ast.With) and
                     ast.unparse(node.items[0].context_expr) == "selectors.DefaultSelector()")
        wrapper = ast.parse("def wait(process):\n    start = b''\n    return start\n")
        assert isinstance(wrapper.body[0], ast.FunctionDef)
        wrapper.body[0].body.insert(1, block)
        self.clock, self.os, selectors = Mock(), Mock(), Mock()
        manager = selectors.DefaultSelector.return_value = MagicMock()
        self.selector = manager.__enter__.return_value
        namespace = {"time": self.clock, "os": self.os, "selectors": selectors}
        exec(compile(ast.fix_missing_locations(wrapper), "<original-readiness-block>", "exec"), namespace)
        self.wait = namespace["wait"]
        self.process = Mock()

    def test_idle_and_capturing_message_are_not_readiness(self):
        self.clock.monotonic.side_effect = [0, 0, 1, 2, 3]
        self.selector.select.side_effect = [[], [True], [], [True]]
        self.os.read.side_effect = [b"Capturing on 'client-eth0'\n", b"File: -\n"]
        self.assertIn(b"File: -", self.wait(self.process))
        self.assertEqual(self.selector.select.call_count, 4)
        self.assertEqual(self.os.read.call_count, 2)

    def test_idle_only_fails_at_full_deadline(self):
        self.clock.monotonic.side_effect = [0, 0, 1, 2, 3, 4, 5]
        self.selector.select.return_value = []
        with self.assertRaisesRegex(RuntimeError, "Capture nicht bereit"):
            self.wait(self.process)
        self.assertEqual(self.selector.select.call_count, 5)
        self.os.read.assert_not_called()

    def test_select_timeout_is_bounded_by_remaining_time(self):
        self.clock.monotonic.side_effect = [0, 4.75, 5]
        self.selector.select.return_value = []
        with self.assertRaisesRegex(RuntimeError, "Capture nicht bereit"):
            self.wait(self.process)
        self.selector.select.assert_called_once_with(0.25)

    def test_eof_is_not_readiness(self):
        self.clock.monotonic.side_effect = [0, 0]
        self.selector.select.return_value = [True]
        self.os.read.return_value = b""
        with self.assertRaises(RuntimeError):
            self.wait(self.process)

    def test_readiness_marker_can_span_reads(self):
        self.clock.monotonic.side_effect = [0, 0, 1]
        self.selector.select.return_value = [True]
        self.os.read.side_effect = [b"Fi", b"le: -\n"]
        self.assertEqual(self.wait(self.process), b"File: -\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
