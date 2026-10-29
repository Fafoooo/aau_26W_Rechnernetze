#!/bin/bash
echo "=== IPv4 forwarding ==="
sysctl net.ipv4.ip_forward
echo
echo "=== Routing table ==="
ip route
echo
echo "=== Interfaces ==="
ip -br addr
