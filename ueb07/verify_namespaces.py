# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Blatt07 mit echten isolierten Linux-Netzen, A/B-Routen, TC, Ping und Fehler-PCAP prüfen.
# Korrekturauftrag: Readiness-Frist ohne vorzeitigen Idle-Abbruch reparieren; keine Netzänderungen ausführen.
"""Zusatznachweis, NICHT Mininet. Python>=3.12, sudo, iproute2, ping, tracepath, dumpcap.
Alle Netzwerkänderungen erst nach Erzeugung eines äußeren privaten Netzwerk-Namespace.
"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "ue7.2"))
from lab_config import LINKS, NODES
from lab_control import LabControl, checked
sys.path.insert(0, str(BASE / "ue7.3"))
from auswerten import budget, statistics
sys.path.insert(0, str(BASE / "ue7.4"))
from pcap_pruefen import inspect


def run(args, timeout=25):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, "LC_ALL": "C"})


class Node:
    def __init__(self, name):
        self.name = name
        original = os.readlink("/proc/self/ns/net")
        self.process = subprocess.Popen(["unshare", "--net", "sleep", "180"])
        deadline = time.monotonic() + 3
        try:
            while os.readlink(f"/proc/{self.process.pid}/ns/net") == original:
                if self.process.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Namespace nicht bereit")
                time.sleep(0.01)
            checked(self, "ip", "link", "set", "lo", "up")
        except BaseException:
            self.close()
            raise

    def prefix(self):
        return ["nsenter", "-t", str(self.process.pid), "-n"]

    def pexec(self, *args):
        result = run(self.prefix() + list(args))
        return result.stdout, result.stderr, result.returncode

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=5)


def link(nodes, item, delay):
    left, right, il, ir, _, _, _ = item
    result = run(["ip", "link", "add", il, "type", "veth", "peer", "name", ir])
    assert result.returncode == 0, result.stderr
    for name, interface in ((left, il), (right, ir)):
        result = run(["ip", "link", "set", interface, "netns", str(nodes[name].process.pid)])
        assert result.returncode == 0, result.stderr
        checked(nodes[name], "ip", "link", "set", interface, "up")
        checked(nodes[name], "tc", "qdisc", "replace", "dev", interface, "root", "netem", "delay", delay)


def save(output, name, text):
    (output / name).write_text(text)


def state(nodes, output, tag):
    for name, node in nodes.items():
        text = ""
        for args in (("ip", "-br", "addr"), ("ip", "route"), ("ip", "rule"),
                     ("sysctl", "net.ipv4.ip_forward"), ("tc", "-s", "qdisc", "show")):
            text += "$ " + " ".join(args) + "\n" + checked(node, *args)
        target = "10.0.1.2" if name in ("r2", "server") else "10.0.2.2"
        text += "$ ip route get " + target + "\n" + checked(node, "ip", "route", "get", target)
        save(output, f"{tag}-{name}-state.txt", text)


def measure(nodes, output, tag, ttl):
    result = {}
    for source, target in (("client", "10.0.2.2"), ("server", "10.0.1.2")):
        node = nodes[source]
        warm = checked(node, "ping", "-n", "-c", "2", "-i", "0.2", "-W", "2", target)
        save(output, f"{tag}-{source}-warmup.txt", warm)
        text = checked(node, "ping", "-n", "-c", "10", "-i", "0.2", "-s", "56", "-W", "2", target)
        save(output, f"{tag}-{source}-ping.txt", text)
        result[source] = statistics(text)
        observed = re.findall(r"ttl=(\d+)", text)
        assert observed == [str(ttl)] * 10, observed
        trace = checked(node, "tracepath", "-n", "-m", "8", target)
        assert "reached" in trace, trace
        save(output, f"{tag}-{source}-tracepath.txt", trace)
    return result


def capture_fault(nodes, output, control):
    control.set_fault(True)
    route = nodes["r3"].pexec("ip", "route", "get", "10.0.2.2")
    assert route[2] != 0 and "unreachable" in route[1].lower(), route
    save(output, "fault-r3-state.txt", checked(nodes["r3"], "ip", "-br", "addr") +
         checked(nodes["r3"], "ip", "route") + "$ ip route get 10.0.2.2\n" + route[1])
    target = output / "fault.pcap"
    with target.open("xb") as stream:
        process = subprocess.Popen(nodes["client"].prefix() + ["dumpcap", "-i", "client-eth0", "-p", "-F", "pcap",
            "-f", "icmp and (host 10.0.1.2) and (host 10.0.2.2 or host 10.0.13.2)",
            "-a", "duration:4", "-w", "-"], stdout=stream, stderr=subprocess.PIPE)
        try:
            start = b""
            with selectors.DefaultSelector() as selector:
                selector.register(process.stderr, selectors.EVENT_READ)
                deadline = time.monotonic() + 5
                while b"File: -" not in start:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise RuntimeError("Capture nicht bereit")
                    if not selector.select(min(1, remaining)):
                        continue
                    piece = os.read(process.stderr.fileno(), 4096)
                    if not piece:
                        raise RuntimeError(start.decode(errors="replace"))
                    start += piece
            out, err, status = nodes["client"].pexec("ping", "-n", "-c", "2", "-i", "0.3", "-W", "1", "10.0.2.2")
            assert status != 0 and "Destination Net Unreachable" in out, (out, err, status)
            save(output, "fault-client-ping.txt", out + err)
            rest = process.communicate(timeout=8)[1]
            assert process.returncode == 0
            log = (start + rest).decode(errors="replace")
            save(output, "fault-dumpcap.txt", log)
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
    parsed = inspect(target)
    counts = re.findall(r"Packets(?: captured)?:\s*(\d+)", log)
    assert counts and int(counts[-1]) == len(parsed["frames"]), log
    save(output, "fault-frames.json", json.dumps(parsed, indent=2) + "\n")
    trace = checked(nodes["client"], "tracepath", "-n", "-m", "8", "10.0.2.2")
    assert "!N" in trace, trace
    save(output, "fault-client-tracepath.txt", trace)
    control.set_fault(False)
    repaired = checked(nodes["client"], "ping", "-n", "-c", "3", "-i", "0.2", "10.0.2.2")
    statistics(repaired, 3)
    save(output, "repaired-client-ping.txt", repaired)
    save(output, "repaired-r3-route.txt", checked(nodes["r3"], "ip", "route", "get", "10.0.2.2"))
    return parsed


def original(nodes, output):
    for left, right, il, ir, al, ar, _ in LINKS[:3]:
        for name, interface, address in ((left, il, al), (right, ir, ar)):
            checked(nodes[name], "ip", "addr", "add", address, "dev", interface)
    for name in ("r1", "r2"):
        checked(nodes[name], "sysctl", "-w", "net.ipv4.ip_forward=1")
    for name, target, gateway, interface in (("client", "default", "10.0.1.1", "client-eth0"),
            ("server", "default", "10.0.2.1", "server-eth0"),
            ("r1", "10.0.2.0/24", "10.0.12.2", "r1-eth1"),
            ("r2", "10.0.1.0/24", "10.0.12.1", "r2-eth0")):
        checked(nodes[name], "ip", "route", "replace", target, "via", gateway, "dev", interface)
    state(nodes, output, "original")
    return measure(nodes, output, "original", 62)


def scenario(output, extended):
    nodes = {}
    try:
        for name in NODES if extended else NODES[:4]:
            nodes[name] = Node(name)
        for item in LINKS if extended else LINKS[:3]:
            link(nodes, item, item[-1] if extended else "10ms")
        if not extended:
            return {"original": original(nodes, output)}
        control = LabControl(nodes)
        control.configure("A")
        result = {"provenance": "Linux-Network-Namespaces + veth + TC/Netem; NICHT Mininet/OVS", "budget_ms": budget()}
        for path, ttl in (("A", 62), ("B", 61)):
            control.select_path(path)
            state(nodes, output, path)
            result[path] = measure(nodes, output, path, ttl)
        assert result["B"]["client"]["avg_ms"] > result["A"]["client"]["avg_ms"] + 80
        result["fault"] = capture_fault(nodes, output, control)
        return result
    finally:
        for node in reversed(list(nodes.values())):
            node.close()


def main():
    if os.geteuid() != 0:
        raise SystemExit("sudo /usr/bin/python3 -B verify_namespaces.py erforderlich")
    os.unshare(os.CLONE_NEWNET)
    output = BASE / "nachweise/run01"
    output.mkdir(parents=True, exist_ok=False)
    result = {**scenario(output, False), **scenario(output, True)}
    result["cleanup"] = "Alle eigenen Namespace-Halter beendet; private veth und qdisc verschwinden mit ihren Namespaces."
    save(output, "results.json", json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
