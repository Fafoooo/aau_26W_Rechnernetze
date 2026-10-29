# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Echte isolierte Fehler-PCAP unabhängig lesen, ICMP-Netzfehler und eingebettete Ziele prüfen.
# Korrekturauftrag: Requests und Netzfehler über Echo-ID/Sequenz eindeutig zuordnen; offline negativ testen.
"""Klassische PCAPs mit Ethernet; beide Bytefolgen und Zeitstempelauflösungen."""
import json
from pathlib import Path
import socket
import struct
import sys


def inspect(path):
    raw = Path(path).read_bytes()
    formats = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">", b"\x4d\x3c\xb2\xa1": "<", b"\xa1\xb2\x3c\x4d": ">"}
    if len(raw) < 24 or raw[:4] not in formats:
        raise ValueError("Kein vollständiger klassischer PCAP-Header")
    endian = formats[raw[:4]]
    assert struct.unpack_from(endian + "I", raw, 20)[0] == 1, "Ethernet erwartet"
    frames, offset = [], 24
    request_keys, error_keys = [], []
    while offset < len(raw):
        assert offset + 16 <= len(raw), "Abgeschnittener Recordheader"
        _, _, captured, original = struct.unpack_from(endian + "IIII", raw, offset)
        offset += 16
        packet = raw[offset:offset + captured]
        assert len(packet) == captured == original, "Abgeschnittenes Paket"
        offset += captured
        assert len(packet) >= 34 and packet[12:14] == b"\x08\x00", "IPv4 erwartet"
        ip = packet[14:]
        ihl = (ip[0] & 15) * 4
        total = struct.unpack_from("!H", ip, 2)[0]
        assert ip[0] >> 4 == 4 and 20 <= ihl <= total <= len(ip)
        assert ip[9] == 1 and struct.unpack_from("!H", ip, 6)[0] & 0x3fff == 0
        src, dst = socket.inet_ntoa(ip[12:16]), socket.inet_ntoa(ip[16:20])
        icmp = ip[ihl:total]
        assert len(icmp) >= 8
        item = {"frame": len(frames) + 1, "src": src, "dst": dst, "type": icmp[0], "code": icmp[1]}
        if icmp[0] == 8:
            assert (src, dst, icmp[1]) == ("10.0.1.2", "10.0.2.2", 0)
            request_keys.append(struct.unpack_from("!HH", icmp, 4))
        else:
            assert (src, dst, icmp[0], icmp[1]) == ("10.0.13.2", "10.0.1.2", 3, 0)
            quoted = icmp[8:]
            assert len(quoted) >= 28 and quoted[0] >> 4 == 4
            quoted_ihl = (quoted[0] & 15) * 4
            quoted_total = struct.unpack_from("!H", quoted, 2)[0]
            assert 20 <= quoted_ihl and quoted_ihl + 8 <= min(len(quoted), quoted_total)
            assert quoted[9] == 1, "Zitiertes Protokoll muss ICMP sein"
            assert struct.unpack_from("!H", quoted, 6)[0] & 0x3fff == 0
            assert socket.inet_ntoa(quoted[12:16]) == "10.0.1.2"
            assert socket.inet_ntoa(quoted[16:20]) == "10.0.2.2"
            quoted_echo = quoted[quoted_ihl:quoted_ihl + 8]
            assert quoted_echo[:2] == b"\x08\x00", "Zitierter Echo Request erwartet"
            error_keys.append(struct.unpack_from("!HH", quoted_echo, 4))
            item["quoted_dst"] = "10.0.2.2"
        frames.append(item)
    requests = [f for f in frames if f["type"] == 8]
    errors = [f for f in frames if f["type"] == 3]
    assert len(requests) == len(errors) == 2, "Zwei Requests und zwei Netzfehler erwartet"
    assert len(set(request_keys)) == len(request_keys), "Doppelte Echo-ID/Sequenz"
    assert sorted(request_keys) == sorted(error_keys), "Netzfehler passen nicht eindeutig zu Requests"
    return {"frames": frames, "requests": len(requests), "network_unreachable": len(errors)}


if __name__ == "__main__":
    print(json.dumps(inspect(sys.argv[1]), indent=2))
