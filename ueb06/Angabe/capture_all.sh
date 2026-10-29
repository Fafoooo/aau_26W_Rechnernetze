#!/bin/bash
# Run inside a router terminal.
tcpdump -i any -nn -s 0 -w /tmp/a06-router.pcap
