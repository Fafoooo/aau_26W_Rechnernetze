#!/usr/bin/env python3
"""RN-Lab Assignment 07 - student starting point.

Starting topology:
    client -- r1 -- r2 -- server

Students add r3 and the alternative path during the exercise.
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.term import makeTerm
from mininet.log import setLogLevel, info

from topology import RoutingTopo


CLIENT_IP = "10.0.1.2/24"
CLIENT_GW = "10.0.1.1"

R1_LEFT_IP = "10.0.1.1/24"
R1_RIGHT_IP = "10.0.12.1/30"

R2_LEFT_IP = "10.0.12.2/30"
R2_RIGHT_IP = "10.0.2.1/24"

SERVER_IP = "10.0.2.2/24"
SERVER_GW = "10.0.2.1"


def configure_interface(node, intf, ip):
    """Configure and enable one interface."""
    node.cmd(f"ip addr flush dev {intf}")
    node.cmd(f"ip addr add {ip} dev {intf}")
    node.cmd(f"ip link set {intf} up")


def show_state(node):
    info(f"\n--- {node.name}: interfaces ---\n")
    info(node.cmd("ip -br addr"))
    info(f"--- {node.name}: routes ---\n")
    info(node.cmd("ip route"))


def main():
    net = Mininet(
        topo=RoutingTopo(),
        controller=None,
        autoSetMacs=True,
        link=TCLink,
    )

    net.start()

    client = net["client"]
    r1 = net["r1"]
    r2 = net["r2"]
    server = net["server"]

    # Configure all supplied interfaces.
    configure_interface(client, "client-eth0", CLIENT_IP)
    configure_interface(r1, "r1-eth0", R1_LEFT_IP)
    configure_interface(r1, "r1-eth1", R1_RIGHT_IP)
    configure_interface(r2, "r2-eth0", R2_LEFT_IP)
    configure_interface(r2, "r2-eth1", R2_RIGHT_IP)
    configure_interface(server, "server-eth0", SERVER_IP)

    # Configure end-host default routes.
    client.cmd(f"ip route replace default via {CLIENT_GW} dev client-eth0")
    server.cmd(f"ip route replace default via {SERVER_GW} dev server-eth0")

    # Configure the existing r1 -> r2 -> server path.
    r1.cmd("ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1")
    r2.cmd("ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0")

    # Show actual interface and routing state.
    info("\n=== Network state ===\n")
    for node in (client, r1, r2, server):
        show_state(node)

    # Verify the supplied infrastructure before opening terminals.
    info("\n=== Connectivity checks ===\n")

    checks = [
        ("client -> r1", client.cmd("ping -c 1 -W 1 10.0.1.1")),
        ("r1 -> r2", r1.cmd("ping -c 1 -W 1 10.0.12.2")),
        ("r2 -> server", r2.cmd("ping -c 1 -W 1 10.0.2.2")),
        ("client -> server", client.cmd("ping -c 2 -W 1 10.0.2.2")),
        ("server -> client", server.cmd("ping -c 2 -W 1 10.0.1.2")),
    ]

    failed = False
    for name, result in checks:
        info(f"\n[{name}]\n{result}")
        if "0% packet loss" not in result:
            failed = True

    if failed:
        info("\nConnectivity check failed. Terminals will not be opened.\n")
        net.stop()
        return

    info("\n=== Starting point ===\n")
    info("Active path: client -> r1 -> r2 -> server\n")
    info("Students must add r3 and configure an alternative path.\n")

    # Open one graphical terminal per supplied Mininet node.
    # r3 is intentionally NOT present in the starting point.
    for node in (client, r1, r2, server):
        makeTerm(node, title=f"RN-Lab UE7 - {node.name}")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
