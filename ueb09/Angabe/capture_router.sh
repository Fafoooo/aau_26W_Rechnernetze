#!/bin/bash
OUT="${1:-/tmp/ub09-router.pcap}"
echo "Capturing router traffic -> $OUT"
tcpdump -i any -nn -e -s 0 -w "$OUT"
