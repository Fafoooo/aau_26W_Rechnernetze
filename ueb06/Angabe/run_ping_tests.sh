#!/bin/bash
echo "=== Client -> Router 1 ==="
ping -c 3 10.0.1.1

echo
echo "=== Client -> Server ==="
ping -c 3 10.0.2.2
