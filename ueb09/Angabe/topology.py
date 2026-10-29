#!/usr/bin/env python3
"""
RN-Lab ÜB09 – Network Forensics

Initial forensic topology:

    client1 --\
               sw1 -- router -- sw2 -- server
    client2 --/

The server contains an intentional routing fault configured by
start_lab.py. The topology itself must provide normal Layer-2
forwarding; therefore both Open vSwitch instances are explicitly
configured in standalone mode. No controller is required.
"""

from mininet.topo import Topo
from mininet.node import Node, OVSSwitch
from mininet.link import TCLink


class LinuxRouter(Node):
    """Linux router with IPv4 forwarding enabled."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class ForensicsTopo(Topo):
    def build(self):
        client1 = self.addHost("client1")
        client2 = self.addHost("client2")
        router = self.addHost("router", cls=LinuxRouter)
        server = self.addHost("server")

        # Explicit standalone OVS switches.
        # The lab does not use an SDN controller.
        sw1 = self.addSwitch(
            "sw1",
            cls=OVSSwitch,
            failMode="standalone"
        )
        sw2 = self.addSwitch(
            "sw2",
            cls=OVSSwitch,
            failMode="standalone"
        )

        # Client LAN.
        self.addLink(
            client1, sw1,
            intfName1="client1-eth0",
            cls=TCLink,
            delay="2ms"
        )
        self.addLink(
            client2, sw1,
            intfName1="client2-eth0",
            cls=TCLink,
            delay="2ms"
        )
        self.addLink(
            sw1, router,
            intfName2="router-eth0",
            cls=TCLink,
            delay="5ms"
        )

        # Server LAN.
        self.addLink(
            router, sw2,
            intfName1="router-eth1",
            cls=TCLink,
            delay="5ms"
        )
        self.addLink(
            server, sw2,
            intfName1="server-eth0",
            cls=TCLink,
            delay="2ms"
        )


topos = {"forensics": ForensicsTopo}
