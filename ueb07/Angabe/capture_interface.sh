#!/bin/bash
set -e

IFACE="${1:-eth0}"

echo "Capturing on interface: ${IFACE}"
echo "Press Ctrl+C to stop."
tcpdump -i "${IFACE}" -nn -s 0 -w /tmp/a07-${IFACE}.pcap
