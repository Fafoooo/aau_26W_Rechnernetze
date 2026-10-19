# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: HTTP-Objekte, Bytearten, TCP-Dauer und Keep-Alive-Vergleich aus Original-PCAPs berichten.
"""Bericht ausschließlich aus echten Offline-Aufnahmen, keine Netzabfragen."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ue2.11'))
from analyse import analyse


def report():
    lines = ['Byteangaben dezimal; Dauer = letztes minus erstes Paket der Verbindung.']
    for name in ('dump_http.pcap', 'dump_protocols.pcap', 'dump_http_persistent.pcap'):
        result = analyse(ROOT / 'Angabe' / name)
        lines.append(f"\n{name}: {result['packets']} Pakete, {result['tcp_connections']} TCP-Verbindungen")
        for stream in result['streams']:
            lines.append(f"Stream {stream['stream']}: {stream['client']} → {stream['server']}")
            lines.append(f"  Frame-Bytes C→S/S→C: {stream['frame_bytes']}; Summe {sum(stream['frame_bytes'])}")
            lines.append(f"  IPv4-Bytes C→S/S→C: {stream['ip_bytes']}; Summe {sum(stream['ip_bytes'])}")
            lines.append(f"  TCP-Nutzbytes C→S/S→C: {stream['tcp_payload_bytes']}; Summe {sum(stream['tcp_payload_bytes'])}")
            lines.append(f"  Dauer: {stream['duration_seconds']} s")
            requests, responses = stream['http_requests'], stream['http_responses']
            if len(requests) != len(responses):
                raise ValueError('Anfragen und Antworten nicht paarbar')
            for request, response in zip(requests, responses):
                lines.append(f"  {request['start_line']} → {response['start_line']}")
                lines.append(f"    Body: {response['body_bytes']} B; Typ {response['headers']['content-type']}")
    return '\n'.join(lines)


if __name__ == '__main__':
    print(report())
