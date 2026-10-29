#!/usr/bin/env python3
# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Anfrage: Implementiere 6.1: Adresstabelle, Plan oder ip -j addr, mit Tests.
"""Adressplan oder explizit übergebene IPv4-Interface-Messdaten auswerten."""
import argparse
import ipaddress
import json
import sys
from pathlib import Path

PLAN = {
    "client": [("client-eth0", "10.0.1.2/24")],
    "r1": [("r1-eth0", "10.0.1.1/24"), ("r1-eth1", "10.0.12.1/30")],
    "r2": [("r2-eth0", "10.0.12.2/30"), ("r2-eth1", "10.0.2.1/24")],
    "server": [("server-eth0", "10.0.2.2/24")],
}


def rows(host, interfaces):
    for name, address in interfaces:
        interface = ipaddress.IPv4Interface(address)
        yield host, name, str(interface.ip), f"/{interface.network.prefixlen}", str(interface.network)


def measured(host, data):
    for interface in data:
        for address in interface.get("addr_info", []):
            if address.get("family") == "inet":
                yield from rows(host, [(interface["ifname"], f"{address['local']}/{address['prefixlen']}")])


def self_test():
    result = [row for host, interfaces in PLAN.items() for row in rows(host, interfaces)]
    assert len(result) == 6
    assert {row[4] for row in result} == {"10.0.1.0/24", "10.0.12.0/30", "10.0.2.0/24"}
    fixture = [{"ifname": "probe", "addr_info": [
        {"family": "inet", "local": "10.0.12.2", "prefixlen": 30}, {"family": "inet6"}]}]
    assert list(measured("r2", fixture)) == [("r2", "probe", "10.0.12.2", "/30", "10.0.12.0/30")]
    assert list(measured("r1", [{"ifname": "leer"}])) == []
    assert list(rows("x", [("lo", "127.0.0.1/8")]))[0][4] == "127.0.0.0/8"
    print("Selbsttest: Plan, Präfix, IPv4-Filter, leeres Interface und Loopback OK.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", metavar="DATEI", help="ip -j addr; - liest stdin")
    parser.add_argument("--host", choices=tuple(PLAN), help="Knotenlabel der JSON-Aufnahme")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        self_test()
        return
    if args.json:
        if not args.host:
            parser.error("--json verlangt --host; der JSON-Inhalt nennt den Mininet-Knoten nicht")
        data = json.load(sys.stdin) if args.json == "-" else json.loads(Path(args.json).read_text())
        result = list(measured(args.host, data))
        print(f"Quelle: übergebenes ip-JSON für {args.host}; Herkunft vom Aufnehmenden zu prüfen.")
    else:
        if args.host:
            parser.error("--host ist nur zusammen mit --json sinnvoll")
        result = [row for host, interfaces in PLAN.items() for row in rows(host, interfaces)]
        print("Quelle: deterministischer Sollplan aus Angabe/start_lab.py; KEINE Messung.")
    print("| Hostname/Knoten | Interface | IPv4-Adresse | Präfix | Netzwerk |")
    print("|---|---|---|---|---|")
    for row in result:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
