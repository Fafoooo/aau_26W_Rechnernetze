# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: Für Ü8.4 die Vorlage um zwei Ethernet-LANs und einen IPv4-Router erweitern; Mininet-CLI öffnen.
"""Zusätzlicher Mininet-Starter für die Kurs-VM; Originalvorlagen bleiben unverändert."""
import os

HOSTS = {
    "client1": ("10.0.1.2/24", "00:00:00:00:00:01", "s1", "10.0.1.1"),
    "client2": ("10.0.1.3/24", "00:00:00:00:00:02", "s1", "10.0.1.1"),
    "server1": ("10.0.2.10/24", "00:00:00:00:00:03", "s2", "10.0.2.1"),
    "server2": ("10.0.2.11/24", "00:00:00:00:00:04", "s2", "10.0.2.1"),
}
ROUTER = (
    ("router-A", "10.0.1.1/24", "02:00:00:00:01:01", "s1"),
    ("router-B", "10.0.2.1/24", "02:00:00:00:02:01", "s2"),
)


def checked(node, *args):
    stdout, stderr, status = node.pexec(*args)
    if status:
        raise RuntimeError(f"{node.name}: {args[0]} fehlgeschlagen: {stderr}")
    return stdout


def address(node, interface, ip, mac):
    checked(node, "ip", "addr", "flush", "dev", interface)
    checked(node, "ip", "link", "set", interface, "address", mac)
    checked(node, "ip", "addr", "add", ip, "dev", interface)
    checked(node, "ip", "link", "set", interface, "up")


def run(net, cli):
    try:
        switches = {name: net.addSwitch(name, failMode="standalone") for name in ("s1", "s2")}
        router = net.addHost("router", ip=None, inNamespace=True)
        for name, (_, mac, switch, _) in HOSTS.items():
            host = net.addHost(name, ip=None, mac=mac)
            net.addLink(host, switches[switch], intfName1=name + "-eth0")
        for interface, _, _, switch in ROUTER:
            net.addLink(router, switches[switch], intfName1=interface)
        net.build()
        net.start()
        for name, (ip, mac, _, gateway) in HOSTS.items():
            address(net[name], name + "-eth0", ip, mac)
            checked(net[name], "ip", "route", "replace", "default", "via", gateway)
        for interface, ip, mac, _ in ROUTER:
            address(router, interface, ip, mac)
        checked(router, "sysctl", "-w", "net.ipv4.ip_forward=1")
        for node in [net[name] for name in HOSTS] + [router]:
            print(node.name, checked(node, "ip", "-br", "addr"))
            print(checked(node, "ip", "route"))
        print("Mininet-CLI: client1 ping -c 1 10.0.1.3; client1 ping -c 1 10.0.2.10")
        cli(net)
    finally:
        net.stop()


def main():
    from mininet.cli import CLI
    from mininet.net import Mininet
    from mininet.node import OVSSwitch
    if os.geteuid() != 0:
        raise SystemExit("In der Kurs-VM mit sudo /usr/bin/python3 -B lab.py starten")
    net = Mininet(controller=None, switch=OVSSwitch, build=False, autoSetMacs=False)
    run(net, CLI)


if __name__ == "__main__":
    main()
