#!/bin/bash
set -e

echo "=== Interfaces ==="
ip -br addr

echo
echo "=== Routing table ==="
ip route

echo
echo "=== Neighbors ==="
ip neigh
