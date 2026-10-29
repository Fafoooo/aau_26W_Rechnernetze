#!/usr/bin/env python3
"""Start the RN-Lab environment for ÜB8.

The assignment text and topology are unchanged. This script explicitly
configures the four host addresses, prints the actual network state,
verifies LAN connectivity, and opens terminals only after verification.
"""

import sys

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.term import makeTerm

from topology import EthernetLabTopo


HOST_ADDRESSES = {
    "client1": ("client1-eth0", "10.0.1.2/24"),
    "client2": ("client2-eth0", "10.0.1.3/24"),
    "server1": ("server1-eth0", "10.0.1.10/24"),
    "server2": ("server2-eth0", "10.0.1.11/24"),
}


def configure_addresses(net):
    for host_name, (interface, address) in HOST_ADDRESSES.items():
        host = net[host_name]
        host.cmd(f"ip addr flush dev {interface}")
        host.cmd(f"ip addr add {address} dev {interface}")
        host.cmd(f"ip link set dev {interface} up")


def print_network_state(net):
    info("\n" + "=" * 72 + "\n")
    info("*** ÜB9: actual Ethernet/LAN configuration\n")
    info("=" * 72 + "\n")

    for host in net.hosts:
        info(f"\n--- {host.name} ---\n")
        info(host.cmd("ip -br addr"))
        info(host.cmd("ip route"))
        info("\n")

    info("--- switch s1 ---\n")
    info(net["s1"].cmd("ovs-ofctl show s1 2>/dev/null || true"))
    info("\n")

    info("=" * 72 + "\n")


def check(node, command, description):
    """Run a command and evaluate its exit code portably."""
    marker = "__RN_LAB_RC__"
    output = node.cmd(f"{command}; printf '\\n{marker}%s\\n' $?")

    rc = None
    details = []

    for line in output.rstrip().splitlines():
        if line.startswith(marker):
            try:
                rc = int(line[len(marker):])
            except ValueError:
                rc = None
        else:
            details.append(line)

    success = rc == 0
    info(f"  [{'OK' if success else 'FAILED'}] {description}\n")

    if not success:
        detail = "\n".join(details).strip()
        if detail:
            info(f"       {detail}\n")

    return success


def verify_switch(net):
    """Verify that the standalone OVS switch is operational."""
    info("\n*** Verifying switch forwarding...\n")

    output = net["s1"].cmd(
        "ovs-vsctl get-fail-mode s1 2>/dev/null"
    ).strip()

    if output != "standalone":
        info(
            f"  [FAILED] switch s1 is not in standalone mode "
            f"(reported: {output or 'unknown'})\n"
        )
        return False

    info("  [OK] switch s1 is in standalone mode\n")

    ports = net["s1"].cmd(
        "ovs-ofctl show s1 2>/dev/null"
    )

    port_count = sum(
        1 for line in ports.splitlines()
        if "(s1-eth" in line
    )

    if port_count < 4:
        info(
            f"  [FAILED] switch s1 exposes only {port_count} host ports; "
            "expected 4\n"
        )
        return False

    info(f"  [OK] switch s1 has {port_count} host-facing ports\n")
    return True


def verify_connectivity(net):
    info("\n*** Verifying LAN connectivity before opening terminals...\n")

    tests = [
        (net["client1"], "ping -c 1 -W 1 10.0.1.3",
         "client1 -> client2"),
        (net["client1"], "ping -c 1 -W 1 10.0.1.10",
         "client1 -> server1"),
        (net["client1"], "ping -c 1 -W 1 10.0.1.11",
         "client1 -> server2"),
        (net["client2"], "ping -c 1 -W 1 10.0.1.2",
         "client2 -> client1"),
        (net["server1"], "ping -c 1 -W 1 10.0.1.2",
         "server1 -> client1"),
        (net["server2"], "ping -c 1 -W 1 10.0.1.3",
         "server2 -> client2"),
    ]

    failures = 0
    for node, command, description in tests:
        if not check(node, command, description):
            failures += 1

    if failures:
        info(
            f"\n*** ERROR: {failures} LAN connectivity test(s) failed.\n"
            "*** Terminals will not be opened.\n"
        )
        return False

    info("\n*** All LAN connectivity checks passed.\n")
    return True



def open_switch_monitor(net):
    """Open a dedicated ÜB8 switch-monitor terminal with a clean FDB."""
    info("\n*** Preparing ÜB8 switch monitor...\n")

    # Clear learned MAC addresses so students can observe learning from scratch.
    net["s1"].cmd("ovs-appctl fdb/flush s1")

    # The switch is in the root/VM namespace; continuously display its FDB.
    makeTerm(
        net["s1"],
        title="ÜB8 Switch Monitor",
        cmd="bash -c \"watch -n 0.5 'sudo ovs-appctl fdb/show s1'; exec bash\""
    )

def main():
    net = Mininet(
        topo=EthernetLabTopo(),
        controller=None,
        autoSetMacs=True
    )

    try:
        info("*** Starting ÜB8 Mininet environment...\n")
        net.start()

        configure_addresses(net)
        print_network_state(net)

        if not verify_switch(net):
            return 1

        if not verify_connectivity(net):
            return 1

        info("\n*** Opening ÜB8 terminals...\n")

        for host, title in [
            (net["client1"], "ÜB8 Client 1"),
            (net["client2"], "ÜB8 Client 2"),
            (net["server1"], "ÜB8 Server 1"),
            (net["server2"], "ÜB8 Server 2"),
        ]:
            makeTerm(host, title=title)

        # Ü8.3: dedicated live view of the switch MAC-learning table.
        open_switch_monitor(net)

        try:
            input("\nPress ENTER to stop ÜB8...")
        except KeyboardInterrupt:
            pass

        return 0

    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
