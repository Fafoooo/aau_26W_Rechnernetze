# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Starte die erweiterte Topologie, ohne den Originalstarter oder TCP-Code zu ändern.
"""In der vorbereiteten Mininet/OVS-VM: sudo python3 -B start_erweitert.py."""
from pathlib import Path
import importlib.util
import re
import sys

from mininet.cli import CLI
from mininet.net import Mininet
from topology import RoutingTopo

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("original_start_lab", BASE / "Angabe/start_lab.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def ping_ok(node, target):
    out, err, code = node.pexec(["ping", "-c", "3", "-W", "2", target], env={"LC_ALL": "C", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
    counts = re.search(r"(\d+) packets transmitted, (\d+) (?:packets )?received", out)
    if code != 0 or not counts or counts.groups() != ("3", "3"):
        raise RuntimeError(out + err)
    print(out)


def main():
    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True)
    try:
        net.start()
        original.configure_base_network(net)
        original.set_interface(net["client2"], "client2-eth0", "10.0.1.3/24")
        out, err, code = net["client2"].pexec(["ip", "route", "replace", "default", "via", "10.0.1.1", "dev", "client2-eth0"])
        if code:
            raise RuntimeError(out + err)
        original.show_state(net)
        print(net["client2"].cmd("ip -br addr; ip route"))
        for source, target in (("client", "10.0.2.2"), ("client2", "10.0.2.2"), ("server", "10.0.1.3")):
            ping_ok(net[source], target)
        CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    main()
