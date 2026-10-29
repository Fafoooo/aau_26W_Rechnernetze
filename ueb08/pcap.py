# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Reale isolierte Blatt08-Messungen, PCAP-Auswertung und negative Tests implementieren.
"""Strikter Standardbibliothek-Parser für die eigenen Ethernet-PCAPs; kein PCAPNG."""
import ipaddress
import struct
from collections import Counter
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


def mac(data):
    return ":".join(f"{byte:02x}" for byte in data)


def ipv4(data):
    return str(ipaddress.IPv4Address(data))


def frame(data, number):
    require(len(data) >= 14, "Ethernet-Header abgeschnitten")
    packet: dict[str, Any] = dict(frame=number, dst_mac=mac(data[:6]), src_mac=mac(data[6:12]))
    packet["ethertype"] = struct.unpack("!H", data[12:14])[0]
    body = data[14:]
    if packet["ethertype"] == 0x0806:
        require(len(body) >= 28, "ARP abgeschnitten")
        require(body[:6] == b"\x00\x01\x08\x00\x06\x04", "Nicht Ethernet/IPv4-ARP")
        packet.update(arp_op=struct.unpack("!H", body[6:8])[0], arp_sha=mac(body[8:14]))
        packet.update(arp_spa=ipv4(body[14:18]), arp_tha=mac(body[18:24]), arp_tpa=ipv4(body[24:28]))
    elif packet["ethertype"] == 0x0800:
        require(len(body) >= 20 and body[0] >> 4 == 4, "IPv4-Header fehlt")
        ihl, length = (body[0] & 15) * 4, struct.unpack("!H", body[2:4])[0]
        require(20 <= ihl <= length <= len(body), "IPv4-Längen inkonsistent")
        require(struct.unpack("!H", body[6:8])[0] & 0x3fff == 0, "Fragmentierung nicht unterstützt")
        header, transport = body[:ihl], body[ihl:length]
        packet.update(src_ip=ipv4(body[12:16]), dst_ip=ipv4(body[16:20]), ttl=body[8], proto=body[9])
        packet.update(ip_id=struct.unpack("!H", body[4:6])[0], ip_length=length, ip_ihl=ihl)
        packet.update(ip_checksum=struct.unpack("!H", body[10:12])[0], ip_checksum_valid=checksum(header) == 0)
        packet["transport_hex"] = transport.hex()
        if body[9] == 1:
            require(len(transport) >= 8, "ICMP abgeschnitten")
            kind, code, _, ident, seq = struct.unpack("!BBHHH", transport[:8])
            packet.update(icmp_type=kind, icmp_code=code, icmp_id=ident, icmp_seq=seq)
            packet["icmp_checksum_valid"] = checksum(transport) == 0
        elif body[9] == 6:
            require(len(transport) >= 20, "TCP abgeschnitten")
            sport, dport, seq, ack = struct.unpack("!HHII", transport[:12])
            offset = (transport[12] >> 4) * 4
            require(20 <= offset <= len(transport), "TCP-Headerlänge ungültig")
            pseudo = body[12:20] + struct.pack("!BBH", 0, 6, len(transport))
            packet.update(src_port=sport, dst_port=dport, tcp_seq=seq, tcp_ack=ack, tcp_flags=transport[13])
            packet.update(tcp_header_length=offset, tcp_window=struct.unpack("!H", transport[14:16])[0])
            packet.update(tcp_checksum_valid=checksum(pseudo + transport) == 0, payload_hex=transport[offset:].hex())
    return packet


def read_pcap(path):
    raw = Path(path).read_bytes()
    require(len(raw) >= 24, "PCAP-Dateikopf fehlt")
    magics = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">", b"\x4d\x3c\xb2\xa1": "<", b"\xa1\xb2\x3c\x4d": ">"}
    require(raw[:4] in magics, "Kein klassisches PCAP")
    endian = magics[raw[:4]]
    major, minor, _, _, snaplen, linktype = struct.unpack(endian + "HHIIII", raw[4:24])
    require((major, minor, linktype) == (2, 4, 1) and snaplen > 0, "PCAP-Version oder Linktyp ungültig")
    packets, position = [], 24
    while position < len(raw):
        require(position + 16 <= len(raw), "PCAP-Recordkopf abgeschnitten")
        _, _, captured, original = struct.unpack(endian + "IIII", raw[position:position + 16])
        position += 16
        require(captured == original and captured <= snaplen, "Verkürzter PCAP-Record")
        require(position + captured <= len(raw), "PCAP-Recorddaten abgeschnitten")
        packets.append(frame(raw[position:position + captured], len(packets) + 1))
        position += captured
    return packets


def select(packets, field, value):
    return [packet for packet in packets if packet.get(field) == value]


def echo_pairs(before, after):
    left, right = select(before, "icmp_type", 8), select(after, "icmp_type", 8)
    key = lambda p: (p["src_ip"], p["dst_ip"], p["icmp_id"], p["icmp_seq"])
    require(left and len({key(p) for p in left}) == len(left), "Echo-Requests fehlen oder sind mehrdeutig")
    require(Counter(map(key, left)) == Counter(map(key, right)), "Echo-Zuordnung vor/nach Router fehlt")
    pairs = [(p, next(q for q in right if key(p) == key(q))) for p in left]
    for p, q in pairs:
        require(p["ttl"] == q["ttl"] + 1, "Router-TTL nicht um eins vermindert")
        require(p["transport_hex"] == q["transport_hex"], "ICMP durch Router verändert")
        require(p["ip_checksum_valid"] and q["ip_checksum_valid"], "IPv4-Prüfsumme falsch")
        require(p["ip_checksum"] != q["ip_checksum"], "IPv4-Prüfsumme unverändert")
        require(p["icmp_checksum_valid"] and q["icmp_checksum_valid"] and p["ip_id"] == q["ip_id"], "ICMP-Prüfsumme oder IP-ID falsch")
        require((p["src_mac"], p["dst_mac"]) == ("00:00:00:00:00:01", "02:00:00:00:01:01"), "Echo-MACs in LAN A falsch")
        require((q["src_mac"], q["dst_mac"]) == ("02:00:00:00:02:01", "00:00:00:00:00:03"), "Echo-MACs in LAN B falsch")
    return [{"before": p, "after": q} for p, q in pairs]


def tcp_stream(packets, source):
    segments = [p for p in packets if p.get("src_ip") == source and p.get("payload_hex")]
    require(segments, "TCP-Nutzdaten fehlen")
    start = min(p["tcp_seq"] for p in segments)
    octets = {}
    for p in segments:
        for offset, byte in enumerate(bytes.fromhex(p["payload_hex"])):
            pos = p["tcp_seq"] - start + offset
            require(pos not in octets or octets[pos] == byte, "Widersprüchliche TCP-Retransmission")
            octets[pos] = byte
    require(set(octets) == set(range(len(octets))), "Lücke im TCP-Datenstrom")
    return bytes(octets[i] for i in range(len(octets)))


def tcp_flow(before, after, request, response):
    a, b = select(before, "proto", 6), select(after, "proto", 6)
    require(a and b, "TCP-Aufzeichnung fehlt")
    allowed = {("10.0.1.2", "10.0.2.10", 40080, 8080), ("10.0.2.10", "10.0.1.2", 8080, 40080)}
    require(all((p["src_ip"], p["dst_ip"], p["src_port"], p["dst_port"]) in allowed for p in a + b), "TCP-Verbindungsendpunkte falsch")
    key = lambda p: (p["src_ip"], p["dst_ip"], p["ip_id"], p["transport_hex"])
    require(Counter(map(key, a)) == Counter(map(key, b)), "TCP-Pakete vor/nach Router verschieden")
    for p in a:
        q = next(q for q in b if key(p) == key(q))
        upstream = p["src_ip"] == "10.0.1.2"
        require(p["ttl"] - q["ttl"] == (1 if upstream else -1), "TCP-TTL-Änderung falsch")
        require(p["ip_checksum_valid"] and q["ip_checksum_valid"] and p["tcp_checksum_valid"] and q["tcp_checksum_valid"], "TCP/IP-Prüfsumme falsch")
        require(p["ip_checksum"] != q["ip_checksum"], "TCP-IPv4-Prüfsumme unverändert")
        expected_a = ("00:00:00:00:00:01", "02:00:00:00:01:01")
        expected_b = ("02:00:00:00:02:01", "00:00:00:00:00:03")
        require((p["src_mac"], p["dst_mac"]) == expected_a[::1 if upstream else -1], "LAN-A-MACs falsch")
        require((q["src_mac"], q["dst_mac"]) == expected_b[::1 if upstream else -1], "LAN-B-MACs falsch")
    syn = [p for p in a if p["tcp_flags"] & 0x12 == 0x02]
    require(len(syn) == 1, "Genau ein initiales SYN erwartet")
    opening = syn[0]
    synack = [p for p in a if p["tcp_flags"] & 0x12 == 0x12 and p["tcp_ack"] == opening["tcp_seq"] + 1]
    require(len(synack) == 1, "Passendes SYN/ACK fehlt")
    require(any(p["src_ip"] == opening["src_ip"] and p["tcp_flags"] & 16 and p["tcp_ack"] == synack[0]["tcp_seq"] + 1 for p in a), "Handshake-ACK fehlt")
    require(not any(p["tcp_flags"] & 4 for p in a), "Unerwartetes TCP-RST")
    fins = [p for p in a if p["tcp_flags"] & 1]
    require(len(fins) == 2 and len({p["src_ip"] for p in fins}) == 2, "Beidseitiger FIN-Abschluss fehlt")
    for p in fins:
        end = p["tcp_seq"] + len(bytes.fromhex(p["payload_hex"])) + 1
        require(any(q["src_ip"] == p["dst_ip"] and q["tcp_flags"] & 16 and q["tcp_ack"] == end for q in a), "FIN nicht bestätigt")
    observed_request, observed_response = tcp_stream(a, "10.0.1.2"), tcp_stream(a, "10.0.2.10")
    require(observed_request == request and observed_response == response, "HTTP-Nutzdaten stimmen nicht")
    return dict(packets=len(a), syn=opening, synack=synack[0], fins=fins, request=observed_request.decode("ascii"), response=observed_response.decode("ascii"), request_bytes=len(request), response_bytes=len(response), all_checksums_valid=True, router_packets_matched=len(a))
