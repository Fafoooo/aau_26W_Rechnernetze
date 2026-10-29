#!/bin/bash
OUT="${1:-/tmp/ub09-server.pcap}"
echo "Capturing server traffic -> $OUT"
tcpdump -i any -nn -e -s 0 -w "$OUT"
