# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Eigene Ethernet-PCAPs für Blatt09 streng mit Python-Standardbibliothek prüfen.
"""Klassisches Ethernet-PCAP; bewusst kein PCAPNG, VLAN oder fragmentiertes IPv4."""
import ipaddress
import struct
from pathlib import Path
from typing import Any


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checksum(data):
    data += b"\0" * (len(data) % 2)
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 65535) + (total >> 16)
    return (~total) & 65535


def mac(raw):
    return ":".join(f"{byte:02x}" for byte in raw)


def ip(raw):
    return str(ipaddress.IPv4Address(raw))


def frame(raw, number):
    require(len(raw) >= 14, "Ethernet abgeschnitten")
    p: dict[str, Any] = dict(frame=number, dst_mac=mac(raw[:6]), src_mac=mac(raw[6:12]))
    kind = struct.unpack("!H", raw[12:14])[0]
    body = raw[14:]
    if kind == 0x0806:
        require(len(body) >= 28 and body[:6] == b"\x00\x01\x08\x00\x06\x04", "Ungültiges Ethernet/IPv4-ARP")
        p.update(arp_op=struct.unpack("!H", body[6:8])[0], arp_sha=mac(body[8:14]), arp_spa=ip(body[14:18]), arp_tpa=ip(body[24:28]))
    if kind == 0x0800:
        require(len(body) >= 20 and body[0] >> 4 == 4, "IPv4 abgeschnitten")
        ihl, length = (body[0] & 15) * 4, struct.unpack("!H", body[2:4])[0]
        require(20 <= ihl <= length <= len(body), "IPv4-Längen falsch")
        require(struct.unpack("!H", body[6:8])[0] & 0x3fff == 0, "IPv4-Fragmente nicht unterstützt")
        segment = body[ihl:length]
        p.update(src_ip=ip(body[12:16]), dst_ip=ip(body[16:20]), ttl=body[8], proto=body[9], ip_id=struct.unpack("!H", body[4:6])[0], transport=segment.hex())
        require(checksum(body[:ihl]) == 0, "IPv4-Prüfsumme falsch")
        if p["proto"] == 1:
            require(len(segment) >= 8 and checksum(segment) == 0, "ICMP falsch")
            p.update(icmp_type=segment[0], icmp_code=segment[1], icmp_id=struct.unpack("!H", segment[4:6])[0], icmp_seq=struct.unpack("!H", segment[6:8])[0])
        if p["proto"] == 6:
            require(len(segment) >= 20, "TCP abgeschnitten")
            offset = (segment[12] >> 4) * 4
            require(20 <= offset <= len(segment), "TCP-Offset falsch")
            pseudo = body[12:20] + struct.pack("!BBH", 0, 6, len(segment))
            require(checksum(pseudo + segment) == 0, "TCP-Prüfsumme falsch; Offloading prüfen")
            sport, dport, seq, ack = struct.unpack("!HHII", segment[:12])
            p.update(sport=sport, dport=dport, seq=seq, ack=ack, flags=segment[13], payload=segment[offset:].hex())
    return p


def read_pcap(path):
    raw = Path(path).read_bytes()
    require(len(raw) >= 24, "PCAP-Kopf fehlt")
    magics = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">", b"\x4d\x3c\xb2\xa1": "<", b"\xa1\xb2\x3c\x4d": ">"}
    require(raw[:4] in magics, "Kein klassisches PCAP")
    endian = magics[raw[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack(endian + "HHIIII", raw[4:24])
    require((major, minor, linktype) == (2, 4, 1) and snaplen > 0, "Kein Ethernet-PCAP 2.4")
    packets, position = [], 24
    while position < len(raw):
        require(position + 16 <= len(raw), "Recordkopf fehlt")
        _, _, captured, original = struct.unpack(endian + "IIII", raw[position:position + 16])
        position += 16
        require(captured == original and captured <= snaplen and position + captured <= len(raw), "Record verkürzt")
        packets.append(frame(raw[position:position + captured], len(packets) + 1))
        position += captured
    return packets
