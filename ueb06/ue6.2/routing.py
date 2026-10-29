#!/usr/bin/env python3
# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Anfrage: Implementiere 6.2: Forwardingtabellen, beide Paketwege, LPM und Tests.
"""Deterministisches IPv4-Routingmodell; keine ausgelesenen Kernelrouten."""
import argparse
from ipaddress import IPv4Address, IPv4Network

TABLES = {
    "client": [("10.0.1.0/24", None, "client-eth0"), ("0.0.0.0/0", "10.0.1.1", "client-eth0")],
    "r1": [("10.0.1.0/24", None, "r1-eth0"), ("10.0.12.0/30", None, "r1-eth1"),
           ("10.0.2.0/24", "10.0.12.2", "r1-eth1")],
    "r2": [("10.0.12.0/30", None, "r2-eth0"), ("10.0.2.0/24", None, "r2-eth1"),
           ("10.0.1.0/24", "10.0.12.1", "r2-eth0")],
    "server": [("10.0.2.0/24", None, "server-eth0"), ("0.0.0.0/0", "10.0.2.1", "server-eth0")],
}
OWNERS = {"10.0.1.2": "client", "10.0.1.1": "r1", "10.0.12.1": "r1",
          "10.0.12.2": "r2", "10.0.2.1": "r2", "10.0.2.2": "server"}


def lookup(routes, destination):
    address = IPv4Address(destination)
    matches = [route for route in routes if address in IPv4Network(route[0])]
    if not matches:
        raise LookupError(f"Keine Route nach {destination}")
    return max(matches, key=lambda route: IPv4Network(route[0]).prefixlen)


def path(source, destination, tables=TABLES, forwarding=True):
    node, target = OWNERS[source], OWNERS[destination]
    steps, visited = [], set()
    while node != target:
        if node in visited:
            raise RuntimeError("Routing-Schleife")
        visited.add(node)
        if node in ("r1", "r2") and not forwarding:
            raise RuntimeError(f"IPv4-Forwarding auf {node} deaktiviert")
        network, gateway, interface = lookup(tables[node], destination)
        neighbor = gateway or destination
        steps.append((node, network, interface, neighbor))
        node = OWNERS[neighbor]
    return steps


def self_test():
    forward = path("10.0.1.2", "10.0.2.2")
    backward = path("10.0.2.2", "10.0.1.2")
    assert [step[0] for step in forward] == ["client", "r1", "r2"]
    assert [step[3] for step in forward] == ["10.0.1.1", "10.0.12.2", "10.0.2.2"]
    assert [step[0] for step in backward] == ["server", "r2", "r1"]
    assert [step[3] for step in backward] == ["10.0.2.1", "10.0.12.1", "10.0.1.2"]
    extra = TABLES["client"] + [("10.0.2.0/24", "10.0.1.8", "client-eth0"),
                                ("10.0.2.2/32", "10.0.1.9", "client-eth0")]
    assert lookup(extra, "10.0.2.2")[0] == "10.0.2.2/32"
    assert lookup(extra, "10.0.2.3")[0] == "10.0.2.0/24"
    assert lookup(extra, "192.0.2.1")[0] == "0.0.0.0/0"
    assert lookup(TABLES["client"], "10.0.1.1")[0] == "10.0.1.0/24"
    missing = {name: list(routes) for name, routes in TABLES.items()}
    missing["r1"] = [route for route in missing["r1"] if route[1] is None]
    for operation, error in [(lambda: path("10.0.1.2", "10.0.2.2", missing), LookupError),
                             (lambda: path("10.0.1.2", "10.0.2.2", forwarding=False), RuntimeError)]:
        try:
            operation()
        except error:
            continue
        raise AssertionError("Negativtest hätte fehlschlagen müssen")
    print("Selbsttest: Hin-/Rückweg, /32 vor /24 vor /0, fehlende Route, Forwarding OK.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true")
    if parser.parse_args().test:
        self_test()
        return
    print("SOLLPLAN, kein Livebefund. Haupttabelle, keine Policy-Regeln/ECMP/NAT.")
    for node in ("r1", "r2"):
        print(f"\n{node}: Zielpräfix | Next Hop | Interface")
        for network, gateway, interface in TABLES[node]:
            print(f"{network} | {gateway or 'direkt: Ziel-IP'} | {interface}")
    for source, destination in [("10.0.1.2", "10.0.2.2"), ("10.0.2.2", "10.0.1.2")]:
        print(f"\n{source} -> {destination}:")
        for node, network, interface, neighbor in path(source, destination):
            print(f"{node}: {network}, {interface}, ARP-Nachbar {neighbor}")
        print(f"{OWNERS[destination]}: lokale Zustellung an {destination}")


if __name__ == "__main__":
    main()
