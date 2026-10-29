# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Unabhängige Paket- und Zustandsbelege für Ü9.1/9.3/9.4/9.5/9.6 aus echten PCAPs auswerten.
"""Nur lesende Analyse der Belege; keine Netzänderung, keine erfundenen Messwerte."""
import argparse
import json
from collections import Counter
from pathlib import Path
from pcap import read_pcap, require

BASE = Path(__file__).resolve().parent
CLIENTS = ("10.10.1.10", "10.10.1.11")
SERVER = "10.10.2.10"
GREETING = b"RN-Lab forensic test server\n"


def tcp(packets, source=None):
    return [p for p in packets if p.get("proto") == 6 and (source is None or p["src_ip"] == source)]


def check_fault(out):
    packets = read_pcap(out / "vorher-server.pcap")
    arp = [p for p in packets if p.get("arp_op") == 1 and p["arp_tpa"] == "10.10.2.254" and p["arp_spa"] == SERVER]
    require(arp, "Keine serverseitige ARP-Suche nach falschem Gateway")
    require(not any(p.get("arp_op") == 2 and p["arp_spa"] == "10.10.2.254" for p in packets), "Falsches Gateway hat geantwortet")
    require(not tcp(packets, SERVER), "Unerwartete TCP-Rückpakete vom Server")
    for client in CLIENTS:
        syns = [p for p in tcp(packets, client) if p["flags"] & 0x12 == 2]
        require(syns, "SYN erreicht Server nicht")
        require(all(p["dst_ip"] == SERVER and p["dst_mac"] == "02:00:00:00:02:10" and p["src_mac"] == "02:00:00:00:02:01" and p["ttl"] == 63 for p in syns), "Serverseitiger Hinweg unerwartet")
    errors = [p for p in packets if p.get("icmp_type") in (3, 11)]
    return {"server_arp_wrong_gateway": len(arp), "arp_reply_wrong_gateway": 0, "server_tcp_replies": 0, "icmp_errors_on_server_interface": errors, "syn_clients_reached_server": list(CLIENTS)}


def routed(before, after):
    key = lambda p: (p["src_ip"], p["dst_ip"], p["ip_id"], p["transport"])
    a, b = tcp(before), tcp(after)
    require(a and Counter(map(key, a)) == Counter(map(key, b)), "TCP-Pakete nicht über Router zuordenbar")
    for p in a:
        q = next(q for q in b if key(p) == key(q))
        outgoing = p["src_ip"] in CLIENTS
        require(p["ttl"] - q["ttl"] == (1 if outgoing else -1), "TTL-Änderung falsch")
        client_mac = "02:00:00:00:01:" + ("10" if (p["src_ip"] if outgoing else p["dst_ip"]) == CLIENTS[0] else "11")
        expected_a = (client_mac, "02:00:00:00:01:01")
        expected_b = ("02:00:00:00:02:01", "02:00:00:00:02:10")
        require((p["src_mac"], p["dst_mac"]) == expected_a[::1 if outgoing else -1], "LAN1-MACs falsch")
        require((q["src_mac"], q["dst_mac"]) == expected_b[::1 if outgoing else -1], "LAN2-MACs falsch")
    return len(a)


def stream(packets):
    data = [p for p in packets if p.get("payload")]
    require(data, "TCP-Nutzdaten fehlen")
    origin = min(p["seq"] for p in data)
    octets = {}
    for p in data:
        for i, byte in enumerate(bytes.fromhex(p["payload"])):
            index = p["seq"] - origin + i
            require(index not in octets or octets[index] == byte, "Widersprüchliche Retransmission")
            octets[index] = byte
    require(set(octets) == set(range(len(octets))), "Lücke im TCP-Strom")
    return bytes(octets[i] for i in range(len(octets)))


def check_flow(packets, client):
    flow = [p for p in tcp(packets) if {p["src_ip"], p["dst_ip"]} == {client, SERVER}]
    starts = [p for p in flow if p["src_ip"] == client and p["flags"] & 0x12 == 2]
    require(len(starts) == 1, "Genau ein initiales SYN erwartet")
    syn = starts[0]
    require(syn["dport"] == 5000, "Serverport falsch")
    require(all((p["sport"], p["dport"]) == ((syn["sport"], 5000) if p["src_ip"] == client else (5000, syn["sport"])) for p in flow), "Anderer TCP-Flow enthalten")
    synacks = [p for p in flow if p["src_ip"] == SERVER and p["flags"] & 0x12 == 0x12 and p["ack"] == syn["seq"] + 1]
    require(len(synacks) == 1, "Passendes SYN-ACK fehlt")
    require(any(p["src_ip"] == client and p["flags"] & 16 and p["ack"] == synacks[0]["seq"] + 1 for p in flow), "Drittes Handshake-ACK fehlt")
    require(not any(p["flags"] & 4 for p in flow), "Unerwartetes RST")
    fins = [p for p in flow if p["flags"] & 1]
    require(len(fins) == 2 and len({p["src_ip"] for p in fins}) == 2, "Beidseitiger FIN fehlt")
    for fin in fins:
        end = fin["seq"] + len(bytes.fromhex(fin["payload"])) + 1
        require(any(p["src_ip"] == fin["dst_ip"] and p["flags"] & 16 and p["ack"] == end for p in flow), "FIN nicht bestätigt")
    greeting = stream([p for p in flow if p["src_ip"] == SERVER])
    require(greeting == GREETING, "Originalserver-Begrüßung falsch")
    return dict(client=client, client_port=syn["sport"], server_port=5000, packets=len(flow), syn_frame=syn["frame"], synack_frame=synacks[0]["frame"], greeting=greeting.decode(), greeting_bytes=len(greeting), fin_frames=[p["frame"] for p in fins], rst_count=0)


def analyse(out):
    state = json.loads((out / "results.json").read_text())
    packets = {}
    for name, count in state["capture_counts"].items():
        packets[name] = read_pcap(out / name)
        require(len(packets[name]) == count, "Erfasste Paketzahl verändert")
    require(len(packets) == 10, "Zehn Mitschnitte erwartet")
    fault = check_fault(out)
    require("via 10.10.2.254" in state["fault_state"]["server"]["route_get"], "Routing-Evidenz fehlt")
    require("10.10.2.254" in state["fault_state"]["server"]["neigh"] and "FAILED" in state["fault_state"]["server"]["neigh"], "Neighbor-Evidenz fehlt")
    require("via 10.10.2.1 " in state["repaired_state"]["server"]["route_get"], "Reparierte Route fehlt")
    routed_before = routed(packets["vorher-router0.pcap"], packets["vorher-router1.pcap"])
    routed_after = routed(packets["nachher-router0.pcap"], packets["nachher-router1.pcap"])
    flows = [check_flow(packets["nachher-server.pcap"], client) for client in CLIENTS]
    for host in ("client1", "client2"):
        require(state["before"][host]["ping"]["rc"] != 0 and state["before"][host]["tcp"]["rc"] != 0, "Vorherige Störung fehlt")
        require(state["after"][host]["ping"]["rc"] == 0 and state["after"][host]["tcp"]["rc"] == 0, "Ende-zu-Ende-Reparatur fehlt")
        echo = [p for p in packets[f"nachher-{host}.pcap"] if p.get("icmp_type") == 0 and p["src_ip"] == SERVER]
        require(len(echo) == 3, "Drei Echo-Replies pro Client fehlen")
    return {"provenance": state["provenance"], "fault": fault, "routed_tcp_before": routed_before, "routed_tcp_after": routed_after, "flows": flows, "capture_counts": state["capture_counts"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=BASE / "nachweise/run01")
    parser.add_argument("--task", choices=("9.1", "9.3", "9.4", "9.5", "9.6"))
    args = parser.parse_args()
    result = analyse(args.out)
    state = json.loads((args.out / "results.json").read_text())
    sections = {"9.1": {"initial": state["initial"], "baseline": state["baseline"], "before": state["before"], "neighbors": state["fault_state"]}, "9.3": result, "9.4": {"fault": result["fault"], "route_get": state["fault_state"]["server"]["route_get"], "neigh": state["fault_state"]["server"]["neigh"]}, "9.5": {"before": state["fault_state"]["server"], "after": state["repaired_state"]["server"]}, "9.6": {"after": state["after"], "flows": result["flows"]}}
    print(json.dumps(sections[args.task] if args.task else result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
