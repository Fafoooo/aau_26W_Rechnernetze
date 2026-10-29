#!/bin/bash
echo "=== Interfaces ==="
ip -br addr
echo
echo "=== Routing table ==="
ip route
echo
echo "=== ARP/neighbor table ==="
ip neigh
