#!/usr/bin/env python3
"""Start and verify the RN-Lab Assignment 06 environment.

The base infrastructure is configured explicitly here rather than relying on
implicit IP parameters in topology.py. This makes the environment deterministic
and makes the actual configuration visible to students.

Beginning with Ü 6.8, students modify the topology. At that point they may
also need to extend configure_base_network() and verify_connectivity() for
their new topology.
"""

import time

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.term import makeTerm

from topology import RoutingTopo, LINK_DELAY


# Base topology addresses
CLIENT_IP = "10.0.1.2/24"
CLIENT_GW = "10.0.1.1"

R1_LEFT_IP = "10.0.1.1/24"
R1_RIGHT_IP = "10.0.12.1/30"

R2_LEFT_IP = "10.0.12.2/30"
R2_RIGHT_IP = "10.0.2.1/24"

SERVER_IP = "10.0.2.2/24"
SERVER_GW = "10.0.2.1"


def set_interface(node, interface, address):
    """Flush and explicitly configure one interface."""
    node.cmd(f"ip addr flush dev {interface}")
    node.cmd(f"ip addr add {address} dev {interface}")
    node.cmd(f"ip link set {interface} up")


def configure_base_network(net):
    """Configure all addresses and routes for the supplied base topology."""
    client = net["client"]
    r1 = net["r1"]
    r2 = net["r2"]
    server = net["server"]

    set_interface(client, "client-eth0", CLIENT_IP)

    set_interface(r1, "r1-eth0", R1_LEFT_IP)
    set_interface(r1, "r1-eth1", R1_RIGHT_IP)

    set_interface(r2, "r2-eth0", R2_LEFT_IP)
    set_interface(r2, "r2-eth1", R2_RIGHT_IP)

    set_interface(server, "server-eth0", SERVER_IP)

    # End-host routes to the remote LAN.
    client.cmd(f"ip route replace default via {CLIENT_GW} dev client-eth0")
    server.cmd(f"ip route replace default via {SERVER_GW} dev server-eth0")

    # Static routes between the two LANs.
    r1.cmd("ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1")
    r2.cmd("ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0")

    # Directly connected routes are installed by `ip addr add`, but we
    # explicitly keep forwarding enabled.
    r1.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")
    r2.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")


def show_state(net):
    print()
    print("=" * 72)
    print("RN-Lab - Assignment 06")
    print("=" * 72)
    print("Topology: client -- r1 -- r2 -- server")
    print(f"Link delay: {LINK_DELAY}")
    print()
    print("Expected base addresses:")
    print(f"  client : {CLIENT_IP}       gateway {CLIENT_GW}")
    print(f"  r1     : {R1_LEFT_IP}, {R1_RIGHT_IP}")
    print(f"  r2     : {R2_LEFT_IP}, {R2_RIGHT_IP}")
    print(f"  server : {SERVER_IP}       gateway {SERVER_GW}")
    print()
    print("Actual interfaces:")
    for name in ("client", "r1", "r2", "server"):
        print(f"\n{name}:")
        print(net[name].cmd("ip -br addr").strip())

    print("\nActual routing tables:")
    for name in ("client", "r1", "r2", "server"):
        print(f"\n{name}:")
        print(net[name].cmd("ip route").strip())

    print("\nIPv4 forwarding:")
    print("r1:", net["r1"].cmd("sysctl -n net.ipv4.ip_forward").strip())
    print("r2:", net["r2"].cmd("sysctl -n net.ipv4.ip_forward").strip())
    print("=" * 72)
    print()


def ping_ok(node, address):
    result = node.cmd(f"ping -c 2 -W 1 {address}")
    return "0% packet loss" in result


def verify_connectivity(net):
    """Verify local links and complete end-to-end routed connectivity."""
    checks = [
        ("client -> r1", net["client"], "10.0.1.1"),
        ("r1 -> client", net["r1"], "10.0.1.2"),
        ("r1 -> r2", net["r1"], "10.0.12.2"),
        ("r2 -> r1", net["r2"], "10.0.12.1"),
        ("r2 -> server", net["r2"], "10.0.2.2"),
        ("server -> r2", net["server"], "10.0.2.1"),
        ("client -> server (routed)", net["client"], "10.0.2.2"),
        ("server -> client (routed)", net["server"], "10.0.1.2"),
    ]

    print("Connectivity check:")
    failures = []

    for label, node, address in checks:
        ok = ping_ok(node, address)
        print(f"  {'OK  ' if ok else 'FAIL'} {label}")
        if not ok:
            failures.append(label)

    if failures:
        print("\nERROR: connectivity verification failed.")
        print("The student terminals will not be opened.")
        print("Inspect the interface and route information above.")
        raise RuntimeError("Connectivity check failed: " + ", ".join(failures))

    print("  All connectivity checks passed.\n")


def main():
    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True)

    info("*** Starting RN-Lab Assignment 06\n")
    net.start()

    try:
        configure_base_network(net)
        time.sleep(0.2)
        show_state(net)
        verify_connectivity(net)

        info("*** Opening four Mininet terminals\n")
        for node, title in [
            (net["client"], "A06 Client"),
            (net["r1"], "A06 Router 1"),
            (net["r2"], "A06 Router 2"),
            (net["server"], "A06 Server"),
        ]:
            makeTerm(node, title=title)

        print("Four Mininet terminals are ready.")
        print()
        print("Client:  ping -c 4 10.0.2.2")
        print("Server:  ping -c 4 10.0.1.2")
        print("r1:      ip route")
        print("r2:      ip route")
        print()
        print("Press ENTER here to stop the lab.")

        try:
            input()
        except KeyboardInterrupt:
            pass
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
