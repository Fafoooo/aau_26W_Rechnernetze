#!/bin/bash
# Usage inside a Mininet terminal:
#   ./capture_interface.sh eth0 /tmp/capture.pcap

IFACE="${1:-eth0}"
OUT="${2:-/tmp/a06-${IFACE}.pcap}"

echo "Capturing $IFACE -> $OUT"
tcpdump -i "$IFACE" -nn -s 0 -w "$OUT"
