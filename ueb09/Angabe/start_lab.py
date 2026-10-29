#!/usr/bin/env python3
"""
RN-Lab ÜB09 – Network Forensics

The server's default gateway is intentionally wrong. This is the
forensic fault that students are expected to discover.

The startup script verifies only the infrastructure that must work.
It does not repair the intentional fault and does not abort because
client-to-server communication fails.
"""

import sys

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.term import makeTerm

from topology import ForensicsTopo


def configure_network(net):
    c1 = net["client1"]
    c2 = net["client2"]
    router = net["router"]
    server = net["server"]

    # Explicit addresses.
    for host, interface, address in [
        (c1, "client1-eth0", "10.10.1.10/24"),
        (c2, "client2-eth0", "10.10.1.11/24"),
        (router, "router-eth0", "10.10.1.1/24"),
        (router, "router-eth1", "10.10.2.1/24"),
        (server, "server-eth0", "10.10.2.10/24"),
    ]:
        host.cmd(f"ip addr flush dev {interface}")
        host.cmd(f"ip addr add {address} dev {interface}")
        host.cmd(f"ip link set dev {interface} up")

    # Correct client gateways.
    c1.cmd("ip route replace default via 10.10.1.1 dev client1-eth0")
    c2.cmd("ip route replace default via 10.10.1.1 dev client2-eth0")

    # Router forwarding.
    router.cmd("sysctl -w net.ipv4.ip_forward=1")

    # INTENTIONAL FORENSIC FAULT.
    # Do not fix this here. Students must discover it.
    server.cmd(
        "ip route replace default via 10.10.2.254 dev server-eth0"
    )


def print_state(net):
    info("\n" + "=" * 72 + "\n")
    info("*** ÜB10 forensic baseline - actual configuration\n")
    info("=" * 72 + "\n")

    for host in net.hosts:
        info(f"\n--- {host.name} ---\n")
        info(host.cmd("ip -br addr"))
        info(host.cmd("ip route"))
        info("\n")

    for switch in net.switches:
        info(f"--- {switch.name} ---\n")
        info(switch.cmd(f"ovs-vsctl get-fail-mode {switch.name}"))
        info("\n")


def ping_ok(node, destination):
    """
    Portable Mininet command-status check.

    Do not use Host.lastCmdWasOK(): that method is unavailable in the
    Mininet version used by the course VM.
    """
    marker = "__RN_PING_RC__"
    output = node.cmd(
        f"ping -c 1 -W 1 {destination}; echo {marker}$?"
    )

    for line in output.splitlines():
        if line.startswith(marker):
            try:
                return int(line[len(marker):]) == 0
            except ValueError:
                return False

    return False


def verify_baseline(net):
    info("*** Verifying the forensic baseline...\n")

    # These paths must work even with the intentional server fault.
    tests = [
        ("client1", "10.10.1.1", "client1 -> router"),
        ("client2", "10.10.1.1", "client2 -> router"),
        ("router", "10.10.2.10", "router -> server"),
    ]

    failures = 0

    for host_name, destination, description in tests:
        ok = ping_ok(net[host_name], destination)
        info(f"  [{'OK' if ok else 'FAILED'}] {description}\n")
        if not ok:
            failures += 1

    if failures:
        info(
            f"\n*** ERROR: {failures} baseline infrastructure test(s) failed.\n"
            "*** Check the switch configuration and local VM environment.\n"
            "*** The intentional server gateway fault is not the cause of these tests.\n"
        )
        return False

    # End-to-end failure is expected and is NOT a startup error.
    info("\n*** Checking intentional forensic symptom...\n")

    c1_ok = ping_ok(net["client1"], "10.10.2.10")
    s_ok = ping_ok(net["server"], "10.10.1.10")

    info(
        "  [{}] client1 -> server\n".format(
            "UNEXPECTED SUCCESS" if c1_ok else "EXPECTED FAILURE"
        )
    )
    info(
        "  [{}] server -> client1\n".format(
            "UNEXPECTED SUCCESS" if s_ok else "EXPECTED FAILURE"
        )
    )

    info(
        "\n*** Baseline accepted. The communication fault is intentional.\n"
    )
    return True


def main():
    # No SDN controller is used. Both switches are standalone OVS.
    net = Mininet(
        topo=ForensicsTopo(),
        controller=None,
        autoSetMacs=True
    )

    try:
        info("*** Starting ÜB09 Network Forensics environment...\n")
        net.start()

        configure_network(net)
        print_state(net)

        if not verify_baseline(net):
            return 1

        info("\n*** Opening ÜB09 terminals...\n")

        for host, title in [
            (net["client1"], "ÜB09 client1"),
            (net["client2"], "ÜB09 client2"),
            (net["router"], "ÜB09 router"),
            (net["server"], "ÜB09 server"),
        ]:
            makeTerm(host, title=title)

        try:
            input("\nPress ENTER to stop the Mininet environment...")
        except KeyboardInterrupt:
            pass

        return 0

    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
