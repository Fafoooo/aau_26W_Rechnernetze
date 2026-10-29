# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Erweitere RN-Blatt 6.7 um client2, mit gemeinsamem LAN, unveränderten TCP-Programmen.
"""Erweiterte Arbeitskopie: client und client2 teilen über s1 das linke LAN."""
from mininet.topo import Topo
from mininet.node import Host, Node, OVSBridge
from mininet.link import TCLink

LINK_DELAY = "10ms"


class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class RoutingTopo(Topo):
    def build(self):
        client = self.addHost("client", cls=Host)
        client2 = self.addHost("client2", cls=Host)
        r1 = self.addHost("r1", cls=LinuxRouter)
        r2 = self.addHost("r2", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)
        switch = self.addSwitch("s1", cls=OVSBridge)
        self.addLink(client, switch, intfName1="client-eth0", intfName2="s1-eth1", cls=TCLink, delay=LINK_DELAY)
        self.addLink(client2, switch, intfName1="client2-eth0", intfName2="s1-eth2", cls=TCLink, delay=LINK_DELAY)
        self.addLink(switch, r1, intfName1="s1-eth3", intfName2="r1-eth0", cls=TCLink, delay=LINK_DELAY)
        self.addLink(r1, r2, intfName1="r1-eth1", intfName2="r2-eth0", cls=TCLink, delay=LINK_DELAY)
        self.addLink(r2, server, intfName1="r2-eth1", intfName2="server-eth0", cls=TCLink, delay=LINK_DELAY)


topos = {"routingtopo": RoutingTopo}
