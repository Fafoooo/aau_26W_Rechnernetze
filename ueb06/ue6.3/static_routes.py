#!/usr/bin/env python3
# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Anfrage: Implementiere 6.3: apply(node), Routen löschen/ergänzen, Ping3 prüfen.
"""Statische Routen im Lab; ohne --mininet keine Netzwerkänderungen."""
import argparse
import re
import shlex
import sys
from pathlib import Path

ROUTES = {
    "r1": ("10.0.2.0/24", "10.0.12.2", "r1-eth1", "10.0.2.2"),
    "r2": ("10.0.1.0/24", "10.0.12.1", "r2-eth0", "10.0.1.2"),
}


def run(node, command, check=True):
    stdout, stderr, status = node.pexec(shlex.split(command))
    print(f"[{node.name}] $ {command}\n{stdout}{stderr}[Exitstatus {status}]")
    if check and status != 0:
        raise RuntimeError(f"{node.name}: Befehl fehlgeschlagen: {command}")
    return stdout, stderr, status


def apply(node, phase="cycle"):
    if node.name not in ROUTES or phase not in ("cycle", "remove", "restore"):
        raise ValueError("Nur r1/r2 und cycle/remove/restore sind erlaubt")
    network, gateway, interface, target = ROUTES[node.name]
    route = f"{network} via {gateway} dev {interface}"
    if phase == "cycle":
        apply(node, "remove")
        apply(node, "restore")
        return
    run(node, "ip route")
    if phase == "remove":
        run(node, f"ip route del {route}")
        try:
            run(node, "ip route")
            _, _, status = run(node, f"ip route get {target}", check=False)
            if status == 0:
                raise RuntimeError("Trotz Löschung existiert ein Weg; Basis-Lab erwartet keine Defaultroute")
        except BaseException:
            run(node, f"ip route add {route}")
            raise
    else:
        run(node, f"ip route add {route}")
        run(node, "ip route")
        run(node, f"ip route get {target}")


def ping3(node, expect_success=True):
    output, _, status = run(node, "env LC_ALL=C ping -n -c 3 -W 1 10.0.2.2", check=False)
    match = re.search(r"(\d+) packets transmitted, (\d+) (?:packets )?received", output)
    counts = tuple(map(int, match.groups())) if match else None
    expected = (3, 3) if expect_success else (3, 0)
    if counts is None or counts != expected or status != (0 if expect_success else 1):
        raise RuntimeError(f"Pingnachweis ungültig: Status={status}, gesendet/empfangen={counts}")
    print(f"Ping geprüft: gesendet={counts[0]}, empfangen={counts[1]}, Status={status}.")
    return counts


def exercise(net):
    routers = [net["r1"], net["r2"]]
    for node in routers:
        output, _, _ = run(node, "sysctl -n net.ipv4.ip_forward")
        if output.strip() != "1":
            raise RuntimeError(f"IPv4-Forwarding auf {node.name} muss bereits 1 sein")
    removed = []
    try:
        for node in routers:
            apply(node, "remove")
            removed.append(node)
        ping3(net["client"], expect_success=False)
    finally:
        failures = []
        for node in removed:
            try:
                apply(node, "restore")
            except RuntimeError as error:
                failures.append(str(error))
        if failures:
            raise RuntimeError("Wiederherstellung prüfen: " + "; ".join(failures))
    ping3(net["client"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mininet", action="store_true", help="eigenes Basis-Lab starten; braucht Mininet/root")
    if not parser.parse_args().mininet:
        print("Kein Hosteingriff. Import: exercise(net) oder apply(net['r1']).")
        print("Test-Doubles: python3 -m unittest discover -s ueb06/ue6.3 -p 'test_*.py' -v")
        return
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Angabe"))
    try:
        from mininet.net import Mininet
        from start_lab import RoutingTopo, configure_base_network
    except ImportError as error:
        parser.exit(2, f"Mininet-Start nicht verfügbar: {error}\n")
    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True)
    try:
        net.start()
        configure_base_network(net)
        exercise(net)
    finally:
        net.stop()


if __name__ == "__main__":
    main()
