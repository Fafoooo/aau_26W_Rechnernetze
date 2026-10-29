# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;
# lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.
"""Originalkette plus r1-r3-r2; Server-LAN bleibt unverändert."""

from mininet.topo import Topo
from mininet.node import Host, Node
from mininet.link import TCLink
from lab_config import LINKS, NODES, ROUTERS
from lab_control import checked


class LinuxRouter(Node):
    def config(self, **params):
        result = super().config(**params)
        checked(self, "sysctl", "-w", "net.ipv4.ip_forward=1")
        return result


class RoutingTopo(Topo):
    def build(self):
        for name in NODES:
            self.addHost(name, cls=LinuxRouter if name in ROUTERS else Host, ip=None)
        for left, right, il, ir, _, _, delay in LINKS:
            self.addLink(left, right, intfName1=il, intfName2=ir, cls=TCLink, delay=delay)


topos = {"routingtopo": RoutingTopo}
