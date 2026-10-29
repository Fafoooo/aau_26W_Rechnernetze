#!/usr/bin/env python3
"""Start and verify the RN-Lab environment for Assignment 04."""

import time

from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.term import makeTerm

from topology import (
    RNLabTopo,
    LINK_DELAY,
    LINK_LOSS,
    CLIENT_IP,
    CLIENT_GW,
    ROUTER_LEFT_IP,
    ROUTER_RIGHT_IP,
    SERVER_IP,
    SERVER_GW,
)


def configure_network(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    # Explicit configuration makes the actual lab state deterministic.
    client.cmd("ip addr flush dev client-eth0")
    router.cmd("ip addr flush dev router-eth0")
    router.cmd("ip addr flush dev router-eth1")
    server.cmd("ip addr flush dev server-eth0")

    client.cmd(f"ip addr add {CLIENT_IP} dev client-eth0")
    router.cmd(f"ip addr add {ROUTER_LEFT_IP} dev router-eth0")
    router.cmd(f"ip addr add {ROUTER_RIGHT_IP} dev router-eth1")
    server.cmd(f"ip addr add {SERVER_IP} dev server-eth0")

    for node, interface in [
        (client, "client-eth0"),
        (router, "router-eth0"),
        (router, "router-eth1"),
        (server, "server-eth0"),
    ]:
        node.cmd(f"ip link set {interface} up")

    client.cmd(f"ip route replace default via {CLIENT_GW} dev client-eth0")
    server.cmd(f"ip route replace default via {SERVER_GW} dev server-eth0")

    router.cmd("ip route replace 10.0.1.0/24 dev router-eth0 src 10.0.1.1")
    router.cmd("ip route replace 10.0.2.0/24 dev router-eth1 src 10.0.2.1")
    router.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")


def show_state(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    print()
    print("=" * 68)
    print("RN-Lab - Assignment 04")
    print("=" * 68)
    print("Topology: client -------- router -------- server")
    print()
    print("Expected:")
    print(f"  client : {CLIENT_IP}   gateway {CLIENT_GW}")
    print(f"  router : {ROUTER_LEFT_IP}, {ROUTER_RIGHT_IP}")
    print(f"  server : {SERVER_IP}   gateway {SERVER_GW}")
    print(f"  delay  : {LINK_DELAY}")
    print(f"  loss   : {LINK_LOSS}%")
    print()
    print("Actual interface configuration:")
    print("  CLIENT:", client.cmd("ip -br addr show dev client-eth0").strip())
    print("  ROUTER:", router.cmd("ip -br addr").strip())
    print("  SERVER:", server.cmd("ip -br addr show dev server-eth0").strip())
    print()
    print("Actual routing tables:")
    print("  CLIENT:\n" + client.cmd("ip route").strip())
    print("  ROUTER:\n" + router.cmd("ip route").strip())
    print("  SERVER:\n" + server.cmd("ip route").strip())
    print("=" * 68)
    print()


def verify_connectivity(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    checks = [
        ("client -> router", client, "10.0.1.1"),
        ("router -> client", router, "10.0.1.2"),
        ("router -> server", router, "10.0.2.2"),
        ("server -> router", server, "10.0.2.1"),
        ("client -> server (routed)", client, "10.0.2.2"),
        ("server -> client (routed)", server, "10.0.1.2"),
    ]

    print("Connectivity check:")
    all_ok = True
    for label, node, address in checks:
        result = node.cmd(f"ping -c 2 -W 1 {address}")
        ok = "0% packet loss" in result
        print(f"  {'OK  ' if ok else 'FAIL'} {label}")
        all_ok &= ok

    if not all_ok:
        raise RuntimeError("RN-Lab connectivity check failed")

    print("  All connectivity checks passed.")
    print()


def main():
    net = Mininet(
        topo=RNLabTopo(),
        controller=None,
        autoSetMacs=True,
    )

    info("*** Starting RN-Lab\n")
    net.start()

    try:
        configure_network(net)
        time.sleep(0.2)
        show_state(net)
        verify_connectivity(net)

        info("*** Opening three Mininet terminals\n")
        makeTerm(net["client"], title="RN-Lab Client")
        makeTerm(net["router"], title="RN-Lab Router")
        makeTerm(net["server"], title="RN-Lab Server")

        print("Three terminals are ready.")
        print("Client: ping 10.0.2.2")
        print("Server: ping 10.0.1.2")
        print("Router: ip addr / ip route")
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
