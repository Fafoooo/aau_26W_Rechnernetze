#!/bin/bash
set -e

echo "Capturing on all interfaces."
echo "Press Ctrl+C to stop."
tcpdump -i any -nn -s 0 -w /tmp/a07-router.pcap
