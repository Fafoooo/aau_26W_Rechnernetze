#!/usr/bin/env python3
"""RN-Lab topology for ÜB8.

Infrastructure only:
- four hosts
- one Ethernet switch
- no router
- IP addresses are configured by start_lab.py

The switch is explicitly configured in standalone mode because the lab
does not use an SDN controller. This allows Open vSwitch to perform
normal Layer-2 forwarding without requiring a controller.
"""

from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.link import TCLink


class EthernetLabTopo(Topo):
    """Single Ethernet LAN with four hosts and one standalone switch."""

    def build(self):
        client1 = self.addHost("client1")
        client2 = self.addHost("client2")
        server1 = self.addHost("server1")
        server2 = self.addHost("server2")

        # No controller is used in this exercise. Explicit standalone
        # mode makes OVS perform ordinary Ethernet switching.
        s1 = self.addSwitch(
            "s1",
            cls=OVSSwitch,
            failMode="standalone"
        )

        self.addLink(
            client1, s1,
            intfName1="client1-eth0",
            cls=TCLink
        )
        self.addLink(
            client2, s1,
            intfName1="client2-eth0",
            cls=TCLink
        )
        self.addLink(
            server1, s1,
            intfName1="server1-eth0",
            cls=TCLink
        )
        self.addLink(
            server2, s1,
            intfName1="server2-eth0",
            cls=TCLink
        )


topos = {"ethernetlab": EthernetLabTopo}
