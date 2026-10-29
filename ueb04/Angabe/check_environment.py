#!/usr/bin/env python3
"""Check the software required by Assignment 04."""

import shutil
import sys

print("RN-Lab environment check")
print("------------------------")
print("Python:", sys.version.split()[0])

ok = True

for command in ("mn", "xterm", "ovs-vsctl", "tc"):
    found = shutil.which(command)
    print(f"{command:10s}:", found or "NOT FOUND")
    ok &= found is not None

try:
    import mininet
    print(f"{'mininet':10s}: available")
except ImportError:
    print(f"{'mininet':10s}: NOT FOUND")
    ok = False

print("\nEnvironment OK." if ok else "\nEnvironment incomplete.")
sys.exit(0 if ok else 1)
