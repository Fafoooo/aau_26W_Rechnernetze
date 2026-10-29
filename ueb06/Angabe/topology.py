#!/usr/bin/env python3
"""RN-Lab Assignment 06 - multi-router topology.

Infrastructure only.

Base topology:
    client -- r1 -- r2 -- server

Students begin modifying this file at Ü 6.8.
"""

from mininet.topo import Topo
from mininet.node import Host, Node
from mininet.link import TCLink

LINK_DELAY = "10ms"


class LinuxRouter(Node):
    """Mininet node with IPv4 forwarding enabled."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class RoutingTopo(Topo):
    def build(self):
        client = self.addHost("client", cls=Host)
        r1 = self.addHost("r1", cls=LinuxRouter)
        r2 = self.addHost("r2", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)

        self.addLink(
            client, r1,
            intfName1="client-eth0",
            intfName2="r1-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )

        self.addLink(
            r1, r2,
            intfName1="r1-eth1",
            intfName2="r2-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )

        self.addLink(
            r2, server,
            intfName1="r2-eth1",
            intfName2="server-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )


topos = {"routingtopo": RoutingTopo}
