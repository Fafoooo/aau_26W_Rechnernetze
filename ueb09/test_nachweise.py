# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Blatt09-Belege, Originaltreue, Parserfehler, Isolation, CLI und Zeilenerklärungen unabhängig testen.
"""Offline-Regressionen; keine Netzwerkänderung, keine privilegierte Ausführung."""
import copy
import html
import json
import re
import struct
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
import auswertung
import messen
import pcap

BASE = Path(__file__).resolve().parent
OUT = BASE / "nachweise/run01"


class EvidenceTests(unittest.TestCase):
    def test_complete_evidence(self):
        result = auswertung.analyse(OUT)
        self.assertEqual(len(result["flows"]), 2)
        self.assertEqual(result["fault"]["server_arp_wrong_gateway"], 12)
        self.assertEqual([f["greeting_bytes"] for f in result["flows"]], [28, 28])
        self.assertEqual(json.loads((OUT / "auswertung.json").read_text()), result)

    def test_original_archive(self):
        with zipfile.ZipFile(BASE / "Angabe/uebb9_tempplate.zip") as archive:
            for name in archive.namelist():
                self.assertEqual((BASE / "Angabe" / name).read_bytes(), archive.read(name))

    def test_independent_tcpdump_counts(self):
        state = json.loads((OUT / "results.json").read_text())
        for name, count in state["capture_counts"].items():
            with self.subTest(name=name):
                result = subprocess.run(["tcpdump", "-nn", "-r", str(OUT / name)], capture_output=True, text=True, check=True)
                self.assertEqual(len(result.stdout.splitlines()), count)
                capture_log = (OUT / (name + ".txt")).read_text()
                self.assertIn(f"Packets captured: {count}", capture_log)

    def test_cli_all_tasks(self):
        for task in ("9.1", "9.3", "9.4", "9.5", "9.6"):
            result = subprocess.run(["python3", "-B", str(BASE / ("ue" + task) / "pruefen.py")], cwd=BASE.parent, capture_output=True, text=True, check=True)
            self.assertIsInstance(json.loads(result.stdout), dict)

    def test_negative_tcp_mutations(self):
        original = pcap.read_pcap(OUT / "nachher-server.pcap")
        client = auswertung.CLIENTS[0]
        for mutation in ("no_synack", "bad_ack", "no_fin", "payload", "rst"):
            packets = copy.deepcopy(original)
            flow = [p for p in packets if p.get("proto") == 6 and {p["src_ip"], p["dst_ip"]} == {client, auswertung.SERVER}]
            synack = next(p for p in flow if p["flags"] & 0x12 == 0x12)
            if mutation == "no_synack":
                packets.remove(synack)
            if mutation == "bad_ack":
                synack["ack"] += 2
            if mutation == "no_fin":
                packets.remove(next(p for p in flow if p["flags"] & 1))
            if mutation == "payload":
                next(p for p in flow if p["payload"])["payload"] = b"wrong".hex()
            if mutation == "rst":
                synack["flags"] |= 4
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                auswertung.check_flow(packets, client)

    def test_bad_pcap(self):
        raw = (OUT / "vorher-server.pcap").read_bytes()
        for broken in (b"", b"BAD!" + raw[4:], raw[:-1], raw[:25]):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "broken.pcap"
                path.write_bytes(broken)
                with self.assertRaises(ValueError):
                    pcap.read_pcap(path)

    def test_endian_and_nanoseconds(self):
        raw = (OUT / "vorher-server.pcap").read_bytes()
        for magic, endian in ((b"\xd4\xc3\xb2\xa1", "<"), (b"\xa1\xb2\xc3\xd4", ">"), (b"\x4d\x3c\xb2\xa1", "<"), (b"\xa1\xb2\x3c\x4d", ">")):
            rebuilt = magic + struct.pack(endian + "HHIIII", *struct.unpack("<HHIIII", raw[4:24]))
            position = 24
            while position < len(raw):
                values = struct.unpack("<IIII", raw[position:position + 16])
                length = values[2]
                rebuilt += struct.pack(endian + "IIII", *values) + raw[position + 16:position + 16 + length]
                position += 16 + length
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "converted.pcap"
                path.write_bytes(rebuilt)
                self.assertEqual(pcap.read_pcap(path), pcap.read_pcap(OUT / "vorher-server.pcap"))

    def test_isolation_failure_precedes_changes(self):
        with patch.object(messen.os, "geteuid", return_value=0), patch.object(messen.os, "unshare", side_effect=PermissionError), patch.object(messen, "Lab") as lab, self.assertRaises(PermissionError):
            messen.measure(BASE / "nachweise/must-not-exist")
        lab.assert_not_called()
        self.assertFalse((BASE / "nachweise/must-not-exist").exists())

    def test_existing_evidence_not_overwritten(self):
        with patch.object(messen.os, "geteuid", return_value=0), patch.object(messen.os, "unshare"), patch.object(messen, "Lab") as lab, self.assertRaises(FileExistsError):
            messen.measure(OUT)
        lab.assert_not_called()

    def test_wait_readiness_idle_then_ready(self):
        with patch.object(messen.selectors, "DefaultSelector") as factory, patch.object(messen.time, "monotonic", side_effect=[0, 0.1, 0.2]), patch.object(messen.os, "read", return_value=b"File: -"):
            selector = factory.return_value.__enter__.return_value
            selector.select.side_effect = [[], [(object(), 1)]]
            stream = Mock()
            self.assertEqual(messen.wait_token(stream, b"File: -"), b"File: -")
            self.assertEqual(selector.select.call_count, 2)

    def test_ai_labels_and_line_coverage(self):
        text = (BASE / "zeilenerklaerung.md").read_text()
        sections = re.split(r'^## `([^`]+)`\s*$', text, flags=re.M)
        mapping = {sections[i]: [(int(n), html.unescape(source)) for n, source in re.findall(r'^- L(\d+): <code>(.*?)</code> —', sections[i + 1], re.M)] for i in range(1, len(sections), 2)}
        for path in sorted(BASE.rglob("*.py")):
            if "Angabe" in path.parts:
                continue
            lines = path.read_text().splitlines()
            self.assertIn("KI-Kennzeichnung", lines[0])
            self.assertIn("gpt-6.1-sol", lines[0])
            self.assertEqual(mapping[path.relative_to(BASE).as_posix()], [(n, line) for n, line in enumerate(lines, 1) if line.strip()])


if __name__ == "__main__":
    unittest.main()
