#!/bin/bash

echo "=== Switch ports ==="
ovs-ofctl show s1 2>/dev/null || true

echo
echo "=== Switch forwarding database ==="
ovs-appctl fdb/show s1 2>/dev/null || true

echo
echo "=== OpenFlow flows ==="
ovs-ofctl dump-flows s1 2>/dev/null || true
