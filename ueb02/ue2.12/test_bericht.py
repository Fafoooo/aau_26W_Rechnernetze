# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Objekte, HTTP-Header, Bytes und Persistenz der originalen HTTP-Dumps prüfen.
import unittest
from bericht import ROOT, analyse, report


class HTTPTests(unittest.TestCase):
    def test_three_objects(self):
        result = analyse(ROOT / 'Angabe/dump_http.pcap')
        self.assertEqual(result['tcp_connections'], 3)
        self.assertEqual(result['packets'], 68)
        self.assertEqual(result['frame_bytes'], 37475)
        expected = [('GET /test/ HTTP/1.0', 145, 'text/html'),
                    ('GET /test/logo.gif HTTP/1.0', 4445, 'image/gif'),
                    ('GET /test/TechnikErleben.png HTTP/1.0', 27065, 'image/png')]
        for stream, (request, size, content_type) in zip(result['streams'], expected):
            self.assertEqual(stream['http_requests'][0]['start_line'], request)
            response = stream['http_responses'][0]
            self.assertEqual(response['start_line'], 'HTTP/1.1 200 OK')
            self.assertEqual(response['body_bytes'], size)
            self.assertEqual(int(response['headers']['content-length']), size)
            self.assertEqual(response['headers']['content-type'], content_type)
            self.assertEqual(response['headers']['connection'], 'close')
            self.assertEqual(stream['unique_tcp_payload_bytes'], stream['tcp_payload_bytes'])

    def test_all_byte_metrics(self):
        streams = analyse(ROOT / 'Angabe/dump_http.pcap')['streams']
        self.assertEqual([sum(s['frame_bytes']) for s in streams], [1236, 5814, 30425])
        self.assertEqual([sum(s['ip_bytes']) for s in streams], [1096, 5618, 29809])
        self.assertEqual([s['tcp_payload_bytes'] for s in streams], [[138, 422], [146, 4728], [156, 27349]])
        self.assertEqual([s['duration_seconds'] for s in streams], ['0.301299000', '0.301248000', '0.502194000'])

    def test_persistent_comparison(self):
        ordinary = analyse(ROOT / 'Angabe/dump_http.pcap')['streams']
        persistent = analyse(ROOT / 'Angabe/dump_http_persistent.pcap')
        self.assertEqual(persistent['tcp_connections'], 1)
        stream = persistent['streams'][0]
        self.assertEqual(len(stream['http_requests']), 3)
        self.assertEqual(sum(stream['frame_bytes']), 36123)
        self.assertEqual(stream['duration_seconds'], '0.704626000')
        expected_hashes = [s['http_responses'][0]['body_sha256'] for s in ordinary]
        self.assertEqual([r['body_sha256'] for r in stream['http_responses']], expected_hashes)
        self.assertTrue(all(r['headers']['connection'] == 'Keep-Alive' for r in stream['http_requests']))

    def test_report_runs(self):
        text = report()
        self.assertIn('dump_http.pcap: 68 Pakete, 3 TCP-Verbindungen', text)
        self.assertIn('Body: 27065 B; Typ image/png', text)
        self.assertIn('TCP-Nutzbytes', text)


if __name__ == '__main__':
    unittest.main()
