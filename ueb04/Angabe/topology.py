#!/usr/bin/env python3
"""RN-Lab topology for Assignment 04.

Infrastructure only:
    client -------- router -------- server
"""

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import Host


LINK_DELAY = "20ms"
LINK_LOSS = 0

CLIENT_IP = "10.0.1.2/24"
CLIENT_GW = "10.0.1.1"
ROUTER_LEFT_IP = "10.0.1.1/24"
ROUTER_RIGHT_IP = "10.0.2.1/24"
SERVER_IP = "10.0.2.2/24"
SERVER_GW = "10.0.2.1"


class LinuxRouter(Host):
    """A Mininet host configured to forward IPv4 packets."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class RNLabTopo(Topo):
    """Two IPv4 networks connected by a Linux router."""

    def build(self):
        client = self.addHost("client", cls=Host)
        router = self.addHost("router", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)

        self.addLink(
            client, router,
            intfName1="client-eth0",
            intfName2="router-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
            loss=LINK_LOSS,
        )

        self.addLink(
            router, server,
            intfName1="router-eth1",
            intfName2="server-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
            loss=LINK_LOSS,
        )


topos = {"rnlab": RNLabTopo}
