# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Ü2.10 praktisch bearbeiten: echte eigene Loopback-HTTP-Aufzeichnung
# reproduzierbar aufzeichnen, deren Inhalt und Sicherheitsgrenzen offline testen.
"""Offline-Tests der tatsächlich mit dumpcap geschriebenen klassischen PCAP-Datei."""
import json
import os
from pathlib import Path
import socket
import struct
import unittest
from capture_demo import BODY, REQUEST, capture

ROOT = Path(os.environ.get("RN_CAPTURE_DIR", Path(__file__).resolve().parent)).resolve()


def read_packets(path):
    data = Path(path).read_bytes()
    formats = {b"\xd4\xc3\xb2\xa1": ("<", 1_000_000),
               b"\xa1\xb2\xc3\xd4": (">", 1_000_000),
               b"\x4d\x3c\xb2\xa1": ("<", 1_000_000_000),
               b"\xa1\xb2\x3c\x4d": (">", 1_000_000_000)}
    if data[:4] not in formats:
        raise ValueError("Klassisches PCAP erwartet")
    order, resolution = formats[data[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack(order + "HHiIII", data[4:24])
    if (major, minor, linktype) != (2, 4, 1):
        raise ValueError("PCAP 2.4 mit Ethernet-Linktyp erwartet")
    offset = 24
    packets = []
    while offset < len(data):
        sec, usec, included, original = struct.unpack(order + "IIII", data[offset:offset + 16])
        offset += 16
        frame = data[offset:offset + included]
        offset += included
        if len(frame) != included or included != original or included > snaplen:
            raise ValueError("Abgeschnittenes Paket")
        if frame[12:14] != b"\x08\x00":
            raise ValueError("Nur IPv4 ist erlaubt")
        ip = frame[14:]
        ihl = (ip[0] & 15) * 4
        ip_length = struct.unpack("!H", ip[2:4])[0]
        fragment = struct.unpack("!H", ip[6:8])[0]
        if ip[0] >> 4 != 4 or ihl < 20 or ip[9] != 6 or fragment & 0x3FFF:
            raise ValueError("Unfragmentiertes IPv4/TCP erwartet")
        if ip_length > len(ip) or ip_length < ihl + 20:
            raise ValueError("Ungültige IPv4-Länge")
        tcp = ip[ihl:ip_length]
        source_port, target_port, sequence = struct.unpack("!HHI", tcp[:8])
        header_length = (tcp[12] >> 4) * 4
        if header_length < 20 or header_length > len(tcp):
            raise ValueError("Ungültige TCP-Headerlänge")
        packets.append({"time": sec + usec / resolution, "length": original,
                        "source": socket.inet_ntoa(ip[12:16]),
                        "target": socket.inet_ntoa(ip[16:20]),
                        "sport": source_port, "dport": target_port,
                        "sequence": sequence, "flags": tcp[13],
                        "payload": tcp[header_length:]})
    return packets


class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads((ROOT / "eigene_aufzeichnung.json").read_text())
        cls.packets = read_packets(ROOT / "eigene_aufzeichnung.pcap")

    def test_01_real_nonempty_capture(self):
        self.assertGreaterEqual(len(self.packets), 7)
        self.assertIn(f"Packets captured: {len(self.packets)}", self.metadata["dumpcap_log"])

    def test_02_only_own_loopback_tuple(self):
        ports = (self.metadata["client_port"], self.metadata["server_port"])
        for packet in self.packets:
            self.assertEqual((packet["source"], packet["target"]), ("127.0.0.1", "127.0.0.1"))
            self.assertIn((packet["sport"], packet["dport"]), (ports, ports[::-1]))

    def test_03_exact_http_request(self):
        payload = b"".join(p["payload"] for p in self.packets
                           if p["sport"] == self.metadata["client_port"])
        self.assertEqual(payload, REQUEST)

    def test_04_exact_http_response(self):
        response = b"".join(p["payload"] for p in self.packets
                            if p["sport"] == self.metadata["server_port"])
        header, body = response.split(b"\r\n\r\n", 1)
        self.assertTrue(header.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertIn(f"Content-Length: {len(BODY)}".encode(), header)
        self.assertEqual(body, BODY)
        self.assertEqual(len(response), self.metadata["response_bytes"])

    def test_05_tcp_open_close_no_reset(self):
        flags = [packet["flags"] for packet in self.packets]
        self.assertTrue(any(flag & 2 and not flag & 16 for flag in flags))
        self.assertTrue(any(flag & 2 and flag & 16 for flag in flags))
        self.assertGreaterEqual(sum(bool(flag & 1) for flag in flags), 2)
        self.assertFalse(any(flag & 4 for flag in flags))

    def test_06_safe_capture_options(self):
        command = self.metadata["command"]
        self.assertEqual(command[command.index("-i") + 1], "lo")
        self.assertIn("-p", command)
        self.assertEqual(command[command.index("-a") + 1], "duration:3")
        self.assertIn("src host 127.0.0.1 and dst host 127.0.0.1", self.metadata["capture_filter"])

    def test_07_refuse_to_overwrite(self):
        with self.assertRaises(FileExistsError):
            capture(ROOT / "eigene_aufzeichnung.pcap")


if __name__ == "__main__":
    unittest.main(verbosity=2)
