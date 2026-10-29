#!/bin/bash
set -e

echo "=== Ping router interfaces ==="
ping -c 4 10.0.1.1

echo
echo "=== Ping server ==="
ping -c 4 10.0.2.2
