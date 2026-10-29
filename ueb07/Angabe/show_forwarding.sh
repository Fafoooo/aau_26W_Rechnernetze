#!/bin/bash
set -e

echo "=== IPv4 forwarding ==="
sysctl net.ipv4.ip_forward

echo
echo "=== Interfaces ==="
ip -br addr

echo
echo "=== Routes ==="
ip route
