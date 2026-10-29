#!/bin/bash
IFACE="${1:-eth0}"
OUT="${2:-/tmp/ub8-${IFACE}.pcap}"

echo "Capturing $IFACE -> $OUT"
tcpdump -i "$IFACE" -nn -s 0 -w "$OUT"
