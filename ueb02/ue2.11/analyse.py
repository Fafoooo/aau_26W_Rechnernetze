# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Original-PCAPs reproduzierbar auswerten: Protokolle, TCP-Verbindungen,
# HTTP-Objekte, Frame-/Nutzbytes und Dauer; Ergebnisse unabhängig prüfen.
"""Offline-Analyse klassischer Ethernet/IPv4-PCAPs, ausschließlich Standardbibliothek.

Bewusst begrenzt: keine VLANs, IPv6, IP-Fragmente oder TCP-Sequence-Wraps.
Ungeeignete Eingaben werden abgewiesen, statt plausible Zahlen zu erfinden.
"""
import argparse
from collections import Counter
import hashlib
import ipaddress
import json
from pathlib import Path
import struct


def records(path):
    """Liefert Zeit in Nanosekunden, aufgezeichnete Bytes und Originallänge."""
    data = Path(path).read_bytes()
    formats = {b'\xd4\xc3\xb2\xa1': ('<', 1000), b'\xa1\xb2\xc3\xd4': ('>', 1000),
               b'\x4d\x3c\xb2\xa1': ('<', 1), b'\xa1\xb2\x3c\x4d': ('>', 1)}
    if len(data) < 24 or data[:4] not in formats:
        raise ValueError('Klassische PCAP-Datei erforderlich')
    order, scale = formats[data[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack(order + 'HHIIII', data[4:24])
    if (major, minor) != (2, 4) or linktype != 1:
        raise ValueError('Nur PCAP 2.4 mit Ethernet unterstützt')
    pos = 24
    while pos < len(data):
        if pos + 16 > len(data):
            raise ValueError('Abgeschnittener Record-Header')
        sec, fraction, captured, wire = struct.unpack_from(order + 'IIII', data, pos)
        pos += 16
        if fraction * scale >= 1_000_000_000 or captured > snaplen or captured > wire:
            raise ValueError('Ungültiger PCAP-Record')
        if captured != wire or pos + captured > len(data):
            raise ValueError('Abgeschnittenes Paket: vollständige Bytes erforderlich')
        yield sec * 1_000_000_000 + fraction * scale, data[pos:pos + captured], wire
        pos += captured


def reassemble(segments):
    """Sequenznummern sortieren; gleiche Retransmission nicht doppelt zählen."""
    octets = {}
    for seq, payload in segments:
        for offset, value in enumerate(payload, seq):
            if offset in octets and octets[offset] != value:
                raise ValueError('Widersprüchliche TCP-Überlappung')
            octets[offset] = value
    if not octets:
        return b''
    low, high = min(octets), max(octets)
    if high - low + 1 != len(octets):
        raise ValueError('Lücke oder Sequence-Wrap im TCP-Bytestrom')
    return bytes(octets[index] for index in range(low, high + 1))


def http_messages(data):
    """HTTP/1.x der Übungsdumps: GET, Content-Length oder chunked."""
    result = []
    while data:
        marker = data.find(b'\r\n\r\n')
        if marker < 0:
            raise ValueError('Unvollständiger HTTP-Header')
        lines = data[:marker].decode('iso-8859-1').split('\r\n')
        headers = {}
        for line in lines[1:]:
            name, value = line.split(':', 1)
            headers[name.lower()] = value.strip()
        rest = data[marker + 4:]
        if headers.get('transfer-encoding', '').lower() == 'chunked':
            body = bytearray()
            while True:
                size_line, rest = rest.split(b'\r\n', 1)
                size = int(size_line.split(b';', 1)[0], 16)
                if size == 0:
                    if not rest.startswith(b'\r\n'):
                        raise ValueError('Trailer werden nicht unterstützt')
                    rest = rest[2:]
                    break
                if len(rest) < size + 2 or rest[size:size + 2] != b'\r\n':
                    raise ValueError('Unvollständiger HTTP-Chunk')
                body.extend(rest[:size])
                rest = rest[size + 2:]
        else:
            if lines[0].startswith('GET '):
                size = 0
            elif 'content-length' in headers:
                size = int(headers['content-length'])
            else:
                raise ValueError('Antwort ohne unterstütztes Framing')
            if size < 0 or len(rest) < size:
                raise ValueError('Unvollständiger HTTP-Body')
            body, rest = rest[:size], rest[size:]
        result.append({'start_line': lines[0], 'headers': headers,
                       'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest()})
        data = rest
    return result


def analyse(path):
    counts, flows, current = Counter(), [], {}
    frame_bytes, captured_frames = 0, 0
    for timestamp, frame, wire in records(path):
        captured_frames += 1
        frame_bytes += wire
        counts['Ethernet'] += 1
        if len(frame) < 14:
            raise ValueError('Zu kurzer Ethernet-Frame')
        ethertype = struct.unpack_from('!H', frame, 12)[0]
        if ethertype == 0x0806:
            counts['ARP'] += 1
            continue
        if ethertype != 0x0800:
            raise ValueError('Nur Ethernet mit ARP/IPv4 unterstützt')
        counts['IPv4'] += 1
        ip = frame[14:]
        ihl, total = (ip[0] & 15) * 4, struct.unpack_from('!H', ip, 2)[0]
        if ip[0] >> 4 != 4 or ihl < 20 or total < ihl or len(ip) < total:
            raise ValueError('Ungültiger IPv4-Header')
        if struct.unpack_from('!H', ip, 6)[0] & 0x3fff:
            raise ValueError('IP-Fragmentierung nicht unterstützt')
        source, target = str(ipaddress.IPv4Address(ip[12:16])), str(ipaddress.IPv4Address(ip[16:20]))
        payload = ip[ihl:total]  # Ethernet-Padding gehört nicht zu TCP-Nutzdaten.
        protocol = ip[9]
        if protocol == 1:
            counts['ICMP'] += 1
        elif protocol == 17:
            counts['UDP'] += 1
            sport, dport = struct.unpack_from('!HH', payload)
            if 53 in (sport, dport):
                counts['DNS'] += 1
            elif {sport, dport} == {67, 68}:
                counts['DHCP'] += 1
        elif protocol == 6:
            counts['TCP'] += 1
            sport, dport, seq = struct.unpack_from('!HHI', payload)
            header_size, flags = (payload[12] >> 4) * 4, payload[13]
            if header_size < 20 or len(payload) < header_size:
                raise ValueError('Ungültiger TCP-Header')
            segment = payload[header_size:]
            endpoint, peer = (source, sport), (target, dport)
            key = tuple(sorted((endpoint, peer)))
            if flags & 2 and not flags & 16:
                if key not in current or current[key]['syn_sequence'] != seq:
                    flow = {'stream': len(flows), 'client': list(endpoint), 'server': list(peer),
                            'syn_sequence': seq, 'first_ns': timestamp, 'last_ns': timestamp,
                            'packets': [0, 0], 'frame_bytes': [0, 0], 'ip_bytes': [0, 0],
                            'tcp_payload_bytes': [0, 0], '_segments': [[], []], 'syn_ack': False}
                    flows.append(flow)
                    current[key] = flow
            if key not in current:
                raise ValueError('TCP-Verbindung ohne initiales SYN')
            flow = current[key]
            direction = 0 if list(endpoint) == flow['client'] else 1
            flow['last_ns'] = max(flow['last_ns'], timestamp)
            flow['packets'][direction] += 1
            flow['frame_bytes'][direction] += wire
            flow['ip_bytes'][direction] += total
            flow['tcp_payload_bytes'][direction] += len(segment)
            if direction == 1 and flags & 0x12 == 0x12:
                flow['syn_ack'] = True
            if segment:
                flow['_segments'][direction].append((seq + bool(flags & 2), segment))
        else:
            raise ValueError('Unbekanntes IPv4-Protokoll')
    for flow in flows:
        data = [reassemble(parts) for parts in flow.pop('_segments')]
        flow['unique_tcp_payload_bytes'] = [len(part) for part in data]
        flow['duration_seconds'] = f"{(flow['last_ns'] - flow['first_ns']) / 1_000_000_000:.9f}"
        if flow['server'][1] == 80:
            flow['http_requests'], flow['http_responses'] = [http_messages(part) for part in data]
        else:
            flow['http_requests'], flow['http_responses'] = [], []
    return {'file': Path(path).name, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'packets': captured_frames, 'frame_bytes': frame_bytes,
            'protocol_packets': dict(counts), 'tcp_connections': len(flows), 'streams': flows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pcap', type=Path)
    args = parser.parse_args()
    print(json.dumps(analyse(args.pcap), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
