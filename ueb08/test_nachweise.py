# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Gesicherte Blatt08-PCAPs offline prüfen; Format-, Routing-, TCP- und Erklärungsfehler testen.
"""Offline-Tests: echte Belege lesen; mutierte/synthetische Fälle sind nur Negativkontrollen."""
import copy
import hashlib
import html
import json
import re
import struct
import subprocess
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
import messen
import pcap

BASE = Path(__file__).resolve().parent
EVIDENCE = BASE / "nachweise/run01"
SOURCES = {"messen.py": "erklaerung_messung.md", "pcap.py": "erklaerung_pcap.md", "test_nachweise.py": "erklaerung_tests.md"}


def explanations(source, markdown):
    expected = [(i, line) for i, line in enumerate(source.splitlines(), 1) if line.strip()]
    found = [(int(n), html.unescape(text)) for n, text in re.findall(r"^\| (\d+) \| <code>(.*?)</code> \| .+ \|$", markdown, re.M)]
    pcap.require(found == expected, "Erklärungszeilen fehlen, sind doppelt oder veraltet")


class EvidenceTests(unittest.TestCase):
    def load(self, filename):
        return pcap.read_pcap(EVIDENCE / filename)

    def test_complete_saved_analysis(self):
        saved = json.loads((EVIDENCE / "results.json").read_text())
        self.assertEqual(messen.analyse(EVIDENCE), saved["analysis"])
        self.assertEqual(len(saved["capture_packet_counts"]), 11)
        for name, count in saved["capture_packet_counts"].items():
            packets = self.load(name)
            self.assertEqual(len(packets), count)
            report = (EVIDENCE / (name + ".txt")).read_text()
            self.assertEqual(int(re.search(r"Packets captured: (\d+)", report).group(1)), count)
            self.assertRegex(report, r"received/dropped on interface .*: \d+/0 ")

    def test_saved_neighbours_and_learning(self):
        state = json.loads((EVIDENCE / "results.json").read_text())["state"]
        self.assertEqual(state["82_neigh_before"], "")
        self.assertEqual(state["82_neigh_after_first"], state["82_neigh_after_second"])
        self.assertIn("10.0.1.3 dev client1-eth0 lladdr 00:00:00:00:00:02", state["82_neigh_after_first"])
        self.assertEqual(state["83_fdb_start"], [])
        self.assertEqual([(e["mac"], e["ifname"]) for e in state["83_fdb_after_ping1"]], [("00:00:00:00:00:01", "p1"), ("00:00:00:00:00:03", "p3")])
        self.assertEqual([(e["mac"], e["ifname"]) for e in state["83_fdb_after_ping2"]], [("00:00:00:00:00:01", "p1"), ("00:00:00:00:00:02", "p2"), ("00:00:00:00:00:03", "p3")])

    def test_templates_unchanged(self):
        with zipfile.ZipFile(BASE / "Angabe/uebb8_template.zip") as archive:
            for name in archive.namelist():
                if not name.endswith("/"):
                    self.assertEqual((BASE / "Angabe" / Path(name).name).read_bytes(), archive.read(name))

    def test_line_explanations(self):
        for name, document in SOURCES.items():
            explanations((BASE / name).read_text(), (BASE / document).read_text())
        sample = "x = 1\n\nprint(x)\n"
        valid = "| 1 | <code>x = 1</code> | Wert setzen. |\n| 3 | <code>print(x)</code> | Wert ausgeben. |\n"
        explanations(sample, valid)
        for broken in (valid.splitlines()[0], valid + valid, valid.replace("x = 1", "x  = 1")):
            with self.assertRaises(ValueError):
                explanations(sample, broken)

    def test_pcaps_readonly_and_independent_decoder(self):
        for path in sorted(EVIDENCE.glob("*.pcap")):
            before = hashlib.sha256(path.read_bytes()).digest()
            result = subprocess.run(["tcpdump", "-nn", "-e", "-r", str(path)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(len(result.stdout.splitlines()), len(self.load(path.name)))
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)

    def test_byteorders_and_timestamp_magics(self):
        raw = (EVIDENCE / "82_erster_ping.pcap").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            for endian, magic in (("<", b"\xd4\xc3\xb2\xa1"), (">", b"\xa1\xb2\xc3\xd4"), ("<", b"\x4d\x3c\xb2\xa1"), (">", b"\xa1\xb2\x3c\x4d")):
                converted, position = magic + struct.pack(endian + "HHIIII", *struct.unpack("<HHIIII", raw[4:24])), 24
                while position < len(raw):
                    header = struct.unpack("<IIII", raw[position:position + 16])
                    converted += struct.pack(endian + "IIII", *header) + raw[position + 16:position + 16 + header[2]]
                    position += 16 + header[2]
                target = Path(directory) / "converted.pcap"
                target.write_bytes(converted)
                self.assertEqual(pcap.read_pcap(target), self.load("82_erster_ping.pcap"))

    def test_corrupt_pcap_and_packet_lengths(self):
        raw = (EVIDENCE / "84_lanA.pcap").read_bytes()
        broken_link = bytearray(raw)
        broken_link[20:24] = struct.pack("<I", 113)
        truncated_record = bytearray(raw)
        truncated_record[32:36] = struct.pack("<I", 1)
        with tempfile.TemporaryDirectory() as directory:
            for value in (b"", b"BAD!" + raw[4:], raw[:25], raw[:-1], bytes(broken_link), bytes(truncated_record)):
                target = Path(directory) / "bad.pcap"
                target.write_bytes(value)
                with self.assertRaises(ValueError):
                    pcap.read_pcap(target)
        for value in (b"", bytes(14)[:12] + b"\x08\x06", bytes(12) + b"\x08\x00" + bytes(20)):
            with self.assertRaises(ValueError):
                pcap.frame(value, 1)

    def test_echo_negative_attribution_ttl_mac_checksum(self):
        before, after = self.load("84_lanA.pcap"), self.load("84_lanB.pcap")
        for field, value in (("icmp_id", -1), ("icmp_seq", 999), ("ttl", 64), ("src_mac", "00:00:00:00:00:03"), ("ip_checksum_valid", False), ("icmp_checksum_valid", False)):
            damaged = copy.deepcopy(after)
            pcap.select(damaged, "icmp_type", 8)[0][field] = value
            with self.assertRaises(ValueError):
                pcap.echo_pairs(before, damaged)
        with self.assertRaises(ValueError):
            pcap.echo_pairs(before + pcap.select(before, "icmp_type", 8), after)

    def test_tcp_negative_missing_fin_ack_and_payload(self):
        before, after = self.load("85_lanA.pcap"), self.load("85_lanB.pcap")
        for removed in (8, 9):
            with self.assertRaises(ValueError):
                pcap.tcp_flow(before[:removed] + before[removed + 1:], after[:removed] + after[removed + 1:], messen.REQUEST, messen.RESPONSE)
        for field, value in (("ttl", 64), ("tcp_checksum_valid", False), ("src_port", 999)):
            damaged = copy.deepcopy(after)
            damaged[0][field] = value
            with self.assertRaises(ValueError):
                pcap.tcp_flow(before, damaged, messen.REQUEST, messen.RESPONSE)
        with self.assertRaises(ValueError):
            pcap.tcp_flow(before, after, b"falsche Anfrage", messen.RESPONSE)

    def test_tcp_stream_reordering_retransmission_and_gaps(self):
        part = lambda seq, payload: dict(src_ip="10.0.1.2", tcp_seq=seq, payload_hex=payload.hex())
        self.assertEqual(pcap.tcp_stream([part(12, b"cd"), part(10, b"ab"), part(11, b"bc")], "10.0.1.2"), b"abcd")
        for segments in ([part(10, b"a"), part(12, b"c")], [part(10, b"ab"), part(11, b"x")], []):
            with self.assertRaises(ValueError):
                pcap.tcp_stream(segments, "10.0.1.2")

    def test_capture_readiness_idle_eof_and_timeout(self):
        process = types.SimpleNamespace(stderr=types.SimpleNamespace(fileno=lambda: 9))
        selector = Mock()
        selector.__enter__ = Mock(return_value=selector)
        selector.__exit__ = Mock(return_value=False)
        selector.select.side_effect = [[], [1], [1]]
        with patch.object(messen.selectors, "DefaultSelector", return_value=selector), patch.object(messen.time, "monotonic", side_effect=[0, 0.1, 0.2, 0.3]), patch.object(messen.os, "read", side_effect=[b"Capturing on lab\n", b"File: -\n"]):
            self.assertIn(b"File: -", messen.ready(process, b"File: -"))
        for chunks, times in (([b""], [0, 0.1]), ([], [0, 6])):
            selector.select.side_effect = None
            selector.select.return_value = [1]
            with patch.object(messen.selectors, "DefaultSelector", return_value=selector), patch.object(messen.time, "monotonic", side_effect=times), patch.object(messen.os, "read", side_effect=chunks), self.assertRaises(ValueError):
                messen.ready(process, b"File: -")

    def test_isolation_failure_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "new"
            with patch.object(messen.os, "geteuid", return_value=0), patch.object(messen.os, "unshare", side_effect=PermissionError), patch.object(messen, "Lab") as constructor, self.assertRaises(PermissionError):
                messen.measure(target)
            self.assertFalse(target.exists())
            constructor.assert_not_called()
            with patch.object(messen.os, "geteuid", return_value=0), patch.object(messen.os, "unshare"), patch.object(messen, "Lab") as constructor, self.assertRaises(FileExistsError):
                messen.measure(Path(directory))
            constructor.assert_not_called()

    def test_cleanup_escalation_and_nonzero_ping(self):
        with tempfile.TemporaryDirectory() as directory:
            lab = messen.Lab(Path(directory))
            process = Mock()
            process.poll.return_value = None
            process.communicate.side_effect = [subprocess.TimeoutExpired("own-worker", 3), (b"", b"")]
            lab.processes.append(process)
            lab.cleanup()
            process.terminate.assert_called_once()
            process.kill.assert_called_once()
            self.assertEqual(process.communicate.call_count, 2)
            with patch.object(messen.subprocess, "run", return_value=types.SimpleNamespace(returncode=1, stdout="100% packet loss", stderr="")), self.assertRaises(ValueError):
                lab.ping(None, "10.0.1.2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
