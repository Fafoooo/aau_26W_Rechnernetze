#!/usr/bin/env python3
"""Very small Mininet introduction: h1 -- s1 -- h2."""

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.log import setLogLevel


def main():
    net = Mininet(switch=OVSSwitch)

    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    s1 = net.addSwitch("s1")

    net.addLink(h1, s1)
    net.addLink(h2, s1)

    net.start()

    print("\nTopology: h1 -------- s1 -------- h2")
    print("Try:")
    print("  h1 ip addr")
    print("  h2 ip addr")
    print("  h1 ping -c 4 h2")
    print("  h1 ping -c 4 10.0.0.2")
    print()

    try:
        input("Press ENTER to stop the topology...")
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
