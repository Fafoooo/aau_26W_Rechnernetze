# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Offline-PCAP-Analyse gegen Originaldumps und echte Wireshark-CSV-Exporte testen.
import csv
from pathlib import Path
import struct
import tempfile
import unittest
from analyse import analyse, http_messages, reassemble, records

ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    def test_protocol_counts(self):
        found = analyse(ROOT / 'Angabe/dump_protocols.pcap')
        self.assertEqual(found['packets'], 39)
        self.assertEqual(found['frame_bytes'], 4167)
        self.assertEqual(found['tcp_connections'], 1)
        self.assertEqual(found['protocol_packets'], {'Ethernet': 39, 'IPv4': 29,
                         'ARP': 10, 'UDP': 9, 'TCP': 16, 'ICMP': 4, 'DNS': 6, 'DHCP': 3})

    def test_gui_conversations(self):
        for suffix in ('protocols', 'http'):
            with self.subTest(dump=suffix):
                found = analyse(ROOT / f'Angabe/dump_{suffix}.pcap')['streams']
                with (ROOT / f'ue2.10/gui_tcp_conversations_{suffix}.csv').open() as source:
                    expected = list(csv.DictReader(source))
                self.assertEqual(len(found), len(expected))
                for stream, row in zip(found, expected):
                    self.assertEqual(stream['client'], [row['Address A'], int(row['Port A'])])
                    self.assertEqual(stream['server'], [row['Address B'], int(row['Port B'])])
                    self.assertEqual(sum(stream['packets']), int(row['Packets']))
                    self.assertEqual(sum(stream['frame_bytes']), int(row['Bytes']))
                    self.assertEqual(stream['frame_bytes'][0], int(row['Bytes A → B']))
                    self.assertEqual(stream['frame_bytes'][1], int(row['Bytes B → A']))
                    self.assertAlmostEqual(float(stream['duration_seconds']), float(row['Duration']), places=9)
                    self.assertTrue(stream['syn_ack'])

    def test_gui_hierarchy(self):
        found = analyse(ROOT / 'Angabe/dump_protocols.pcap')['protocol_packets']
        names = {'Ethernet': 'Ethernet', 'Internet Protocol Version 4': 'IPv4',
                 'User Datagram Protocol': 'UDP', 'Dynamic Host Configuration Protocol': 'DHCP',
                 'Domain Name System': 'DNS', 'Transmission Control Protocol': 'TCP',
                 'Internet Control Message Protocol': 'ICMP', 'Address Resolution Protocol': 'ARP'}
        with (ROOT / 'ue2.10/gui_protocol_hierarchy_protocols.csv').open() as source:
            for row in csv.DictReader(source):
                if row['Protocol'] in names:
                    self.assertEqual(found[names[row['Protocol']]], int(row['Packets']))

    def test_padding_not_tcp_payload(self):
        stream = analyse(ROOT / 'Angabe/dump_protocols.pcap')['streams'][0]
        self.assertEqual(stream['tcp_payload_bytes'], [115, 740])
        self.assertEqual(stream['unique_tcp_payload_bytes'], [115, 740])
        self.assertEqual(stream['http_responses'][0]['body_bytes'], 577)

    def test_chunked_body(self):
        result = http_messages(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n'
                               b'2\r\nab\r\n1\r\nc\r\n0\r\n\r\n')
        self.assertEqual(result[0]['body_bytes'], 3)

    def test_persistent_http(self):
        result = http_messages(b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\na'
                               b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nbc')
        self.assertEqual([part['body_bytes'] for part in result], [1, 2])

    def test_missing_header_terminator(self):
        with self.assertRaises(ValueError):
            http_messages(b'HTTP/1.1 200 OK\r\n')

    def test_incomplete_body(self):
        with self.assertRaises(ValueError):
            http_messages(b'HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\na')

    def test_invalid_chunk(self):
        with self.assertRaises(ValueError):
            http_messages(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n3\r\nab')

    def test_reassemble_retransmission(self):
        self.assertEqual(reassemble([(12, b'cd'), (10, b'abc'), (10, b'abc')]), b'abcd')

    def test_reassemble_conflict(self):
        with self.assertRaises(ValueError):
            reassemble([(10, b'abc'), (11, b'X')])

    def test_reassemble_gap(self):
        with self.assertRaises(ValueError):
            reassemble([(10, b'a'), (12, b'c')])

    def test_reassemble_empty(self):
        self.assertEqual(reassemble([]), b'')

    def test_invalid_pcap(self):
        # Auch Testdateien bleiben im aufrufenden Projekt-/Scratch-TMPDIR.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.pcap'
            path.write_bytes(b'not a capture')
            with self.assertRaises(ValueError):
                list(records(path))

    def test_truncated_pcap(self):
        original = (ROOT / 'Angabe/dump_protocols.pcap').read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cut.pcap'
            path.write_bytes(original[:-1])
            with self.assertRaises(ValueError):
                list(records(path))

    def test_big_endian(self):
        raw = b'\xff' * 14
        header = b'\xa1\xb2\xc3\xd4' + struct.pack('>HHIIII', 2, 4, 0, 0, 65535, 1)
        record = struct.pack('>IIII', 1, 123, 14, 14) + raw
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'big.pcap'
            path.write_bytes(header + record)
            self.assertEqual(list(records(path)), [(1_000_123_000, raw, 14)])


if __name__ == '__main__':
    unittest.main()
