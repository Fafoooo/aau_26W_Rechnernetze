# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: Ü4.4/4.6 echte PCAPs unabhängig mit stdlib auswerten;
# UDP-Felder, TCP-Handshake, Nutzdaten, FIN und geschlossene Testflows prüfen.
"""Liest klassische Ethernet-PCAPs, erzeugt keine künstlichen Pakete."""

import argparse
import ipaddress
import json
from pathlib import Path
import struct


def packets(filename):
    raw = Path(filename).read_bytes()
    formats = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">",
               b"\x4d\x3c\xb2\xa1": "<", b"\xa1\xb2\x3c\x4d": ">"}
    if len(raw) < 24 or raw[:4] not in formats:
        raise ValueError("Kein unterstütztes klassisches PCAP")
    endian = formats[raw[:4]]
    if struct.unpack_from(endian + "I", raw, 20)[0] != 1:
        raise ValueError("Nur Ethernet-Linktyp 1 unterstützt")
    offset, number = 24, 0
    result = []
    while offset < len(raw):
        if offset + 16 > len(raw):
            raise ValueError("Abgeschnittener PCAP-Recordheader")
        _, _, captured, original = struct.unpack_from(endian + "IIII", raw, offset)
        offset += 16
        frame = raw[offset:offset + captured]
        offset += captured
        number += 1
        if len(frame) != captured or captured != original:
            raise ValueError("Abgeschnittenes Paket")
        if len(frame) < 34 or frame[12:14] != b"\x08\x00":
            raise ValueError("Erwartet unge-taggetes Ethernet/IPv4")
        ip = frame[14:]
        ihl = (ip[0] & 15) * 4
        total = struct.unpack_from("!H", ip, 2)[0]
        fragment = struct.unpack_from("!H", ip, 6)[0]
        if ip[0] >> 4 != 4 or ihl < 20 or total > len(ip) or total < ihl or fragment & 0x3fff:
            raise ValueError("IPv4-Header/Fragmentierung nicht unterstützt")
        source = str(ipaddress.ip_address(ip[12:16]))
        target = str(ipaddress.ip_address(ip[16:20]))
        data = ip[ihl:total]  # Ethernet-Padding nie zur Transportnutzlast zählen.
        entry = {"frame": number, "source": source, "target": target,
                 "ipv4_length": total, "ipv4_header": ihl, "ttl": ip[8]}
        if ip[9] == 17:
            sport, dport, length, checksum = struct.unpack_from("!HHHH", data)
            if length != len(data) or length < 8:
                raise ValueError("Ungültige UDP-Länge")
            entry.update(protocol="UDP", sport=sport, dport=dport, header_bytes=8,
                         transport_length=length, payload_hex=data[8:].hex())
        elif ip[9] == 6:
            sport, dport, seq, ack = struct.unpack_from("!HHII", data)
            header = (data[12] >> 4) * 4
            if header < 20 or header > len(data):
                raise ValueError("Ungültige TCP-Headerlänge")
            entry.update(protocol="TCP", sport=sport, dport=dport, seq=seq, ack=ack,
                         flags=data[13], header_bytes=header, payload_hex=data[header:].hex())
        else:
            raise ValueError("Nicht erwartetes IP-Transportprotokoll")
        result.append(entry)
    return result


def reassemble(frames, start):
    # Relative Positionen deduplizieren auch identische Retransmissionsbytes.
    values = {}
    for frame in frames:
        payload = bytes.fromhex(frame["payload_hex"])
        first = (frame["seq"] - start) % (2 ** 32)
        for index, byte in enumerate(payload, first):
            if index in values and values[index] != byte:
                raise ValueError("Widersprüchliche überlappende TCP-Daten")
            values[index] = byte
    if sorted(values) != list(range(len(values))):
        raise ValueError("Lücke im TCP-Bytestrom")
    return bytes(values[index] for index in range(len(values)))


def verify_udp(frames):
    messages = ["Hello from Mininet!", "Geänderte Nachricht", "Grüße 🌍"]
    assert len(frames) == len(messages)
    for frame, message in zip(frames, messages):
        assert frame["protocol"] == "UDP"
        assert (frame["source"], frame["target"], frame["dport"]) == ("10.0.0.1", "10.0.0.2", 5000)
        assert 1 <= frame["sport"] <= 65535
        assert bytes.fromhex(frame["payload_hex"]) == message.encode("utf-8")
        assert frame["transport_length"] == len(message.encode("utf-8")) + 8
    return {"kind": "UDP", "frames": frames, "verified": True}


def verify_tcp(frames):
    connections = {}
    for frame in frames:
        assert frame["protocol"] == "TCP"
        assert not frame["flags"] & 4, "Unerwartetes RST"
        assert {frame["source"], frame["target"]} == {"10.0.1.2", "10.0.2.2"}
        assert 5000 in (frame["sport"], frame["dport"])
        port = frame["sport"] if frame["source"] == "10.0.1.2" else frame["dport"]
        connections.setdefault(port, []).append(frame)
    assert len(connections) == 2
    summaries = []
    expected = [b"Eine Nachricht\n", "eins\nGrüße 🌍\n\n".encode("utf-8")]
    for (port, flow), payload in zip(connections.items(), expected):
        outgoing = [f for f in flow if f["source"] == "10.0.1.2"]
        incoming = [f for f in flow if f["source"] == "10.0.2.2"]
        syn, synack, ack = flow[:3]
        assert syn["flags"] & 0x12 == 2
        assert synack["flags"] & 0x12 == 0x12
        assert ack["flags"] & 0x12 == 0x10
        assert synack["ack"] == (syn["seq"] + 1) % (2 ** 32)
        assert ack["ack"] == (synack["seq"] + 1) % (2 ** 32)
        assert reassemble(outgoing, (syn["seq"] + 1) % (2 ** 32)) == payload
        assert reassemble(incoming, (synack["seq"] + 1) % (2 ** 32)) == payload
        fins_out = [f for f in outgoing if f["flags"] & 1]
        fins_in = [f for f in incoming if f["flags"] & 1]
        assert fins_out and fins_in
        assert any(f["flags"] & 0x10 and f["ack"] == (fins_in[-1]["seq"] + 1) % (2 ** 32) for f in outgoing)
        assert any(f["flags"] & 0x10 and f["ack"] == (fins_out[-1]["seq"] + 1) % (2 ** 32) for f in incoming)
        summaries.append({"client_port": port, "handshake_frames": [f["frame"] for f in flow[:3]],
                          "client_data_frames": [f["frame"] for f in outgoing if f["payload_hex"]],
                          "server_data_frames": [f["frame"] for f in incoming if f["payload_hex"]],
                          "client_fin_frames": [f["frame"] for f in fins_out],
                          "server_fin_frames": [f["frame"] for f in fins_in],
                          "payload_utf8": payload.decode("utf-8")})
    return {"kind": "TCP", "connections": summaries, "frames": frames, "verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture")
    parser.add_argument("--kind", required=True, choices=("udp", "tcp"))
    parser.add_argument("--output")
    args = parser.parse_args()
    frames = packets(args.capture)
    report = verify_udp(frames) if args.kind == "udp" else verify_tcp(frames)
    result = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with Path(args.output).open("x", encoding="utf-8") as handle:
            handle.write(result)
    print(result)


if __name__ == "__main__":
    main()
