# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Blatt09 unverändert beobachten, Paketfluss sichern, Gateway minimal reparieren und beide Originalclients real testen.
"""Echte Linux-Bridge/veth-Ersatzmessung. KEIN Mininet-/OVS-/xterm-Nachweis. Python >=3.12."""
import argparse
import json
import os
import re
import selectors
import signal
import subprocess
import time
from pathlib import Path
from pcap import read_pcap, require
from auswertung import check_fault

BASE = Path(__file__).resolve().parent
PYTHON = "/usr/bin/python3"
HOSTS = {"client1": ("10.10.1.10", "02:00:00:00:01:10"), "client2": ("10.10.1.11", "02:00:00:00:01:11"), "server": ("10.10.2.10", "02:00:00:00:02:10")}


def wait_token(stream, token, timeout=5):
    deadline, seen = time.monotonic() + timeout, b""
    with selectors.DefaultSelector() as selector:
        selector.register(stream, selectors.EVENT_READ)
        while token not in seen:
            remaining = deadline - time.monotonic()
            require(remaining > 0, "Bereitschaft: Zeitlimit")
            if not selector.select(min(0.2, remaining)):
                continue
            chunk = os.read(stream.fileno(), 4096)
            require(chunk, "Prozess vor Bereitschaft beendet")
            seen += chunk
    return seen


class Lab:
    def __init__(self, out):
        self.out, self.hosts, self.processes, self.files = out, {}, [], []
        self.log, self.counts = [], {}

    def prefix(self, host):
        return ["nsenter", "-t", str(self.hosts[host].pid), "-n", "--"] if host else []

    def run(self, host, *args, success=True):
        result = subprocess.run(self.prefix(host) + list(args), capture_output=True, text=True, timeout=12)
        result.stdout = result.stdout.replace(str(BASE), "<ueb09>")
        result.stderr = result.stderr.replace(str(BASE), "<ueb09>")
        command = ' '.join(args).replace(str(BASE), "<ueb09>")
        self.log.append(f"[{host or 'switch'}] {command}\n{result.stdout}{result.stderr}RC={result.returncode}\n")
        if success:
            require(result.returncode == 0, f"Befehl fehlgeschlagen: {args[0]}")
        return dict(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)

    def spawn(self, host, args):
        process = subprocess.Popen(self.prefix(host) + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(process)
        return process

    def holder(self, name):
        process = self.spawn(None, [PYTHON, "-B", str(BASE / "messen.py"), "--holder"])
        self.hosts[name] = process
        wait_token(process.stdout, b"READY\n")
        self.run(name, "sysctl", "-qw", "net.ipv6.conf.all.disable_ipv6=1", "net.ipv6.conf.default.disable_ipv6=1")
        self.run(name, "ip", "link", "set", "lo", "up")

    def bridge(self, name):
        self.run(None, "ip", "link", "add", name, "type", "bridge", "stp_state", "0", "forward_delay", "0")
        self.run(None, "ip", "link", "set", name, "up")

    def attach(self, host, interface, port, bridge, address, mac):
        self.run(None, "ip", "link", "add", port, "type", "veth", "peer", "name", interface, "netns", str(self.hosts[host].pid))
        self.run(None, "ip", "link", "set", port, "master", bridge)
        self.run(None, "ip", "link", "set", port, "up")
        self.run(host, "ip", "link", "set", interface, "address", mac)
        self.run(host, "ip", "addr", "add", address + "/24", "dev", interface)
        self.run(host, "ip", "link", "set", interface, "up")
        for node, device in ((None, port), (host, interface)):
            self.run(node, "ethtool", "-K", device, "tx", "off", "rx", "off", "tso", "off", "gso", "off", "gro", "off")

    def setup(self):
        self.run(None, "sysctl", "-qw", "net.ipv6.conf.all.disable_ipv6=1", "net.ipv6.conf.default.disable_ipv6=1")
        for bridge in ("sw1", "sw2"):
            self.bridge(bridge)
        for host in (*HOSTS, "router"):
            self.holder(host)
        for number, (host, (address, mac)) in enumerate(HOSTS.items(), 1):
            self.attach(host, host + "-eth0", "p" + str(number), "sw2" if host == "server" else "sw1", address, mac)
        self.attach("router", "router-eth0", "pr0", "sw1", "10.10.1.1", "02:00:00:00:01:01")
        self.attach("router", "router-eth1", "pr1", "sw2", "10.10.2.1", "02:00:00:00:02:01")
        self.run("router", "sysctl", "-qw", "net.ipv4.ip_forward=1")
        for host in HOSTS:
            gateway = "10.10.2.254" if host == "server" else "10.10.1.1"
            self.run(host, "ip", "route", "replace", "default", "via", gateway, "dev", host + "-eth0")

    def state(self):
        result = {}
        for host in (*HOSTS, "router"):
            result[host] = {name: self.run(host, *args)["stdout"] for name, args in {
                "addr": ("ip", "-br", "addr"), "route": ("ip", "route"), "neigh": ("ip", "neigh"),
                "route_get": ("ip", "route", "get", "10.10.1.10" if host == "server" else "10.10.2.10")}.items()}
        return result

    def ping(self, host, target):
        return self.run(host, "ping", "-n", "-c", "3", "-i", "0.2", "-W", "1", target, success=False)

    def capture(self, host, interface, filename):
        output = (self.out / filename).open("xb")
        self.files.append(output)
        command = self.prefix(host) + ["dumpcap", "-P", "-i", interface, "-f", "arp or icmp or tcp port 5000", "-s", "65535", "-a", "duration:24", "-w", "-"]
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.PIPE)
        self.processes.append(process)
        startup = wait_token(process.stderr, b"File: -")
        return process, output, startup, filename

    def finish(self, capture):
        process, output, startup, filename = capture
        _, tail = process.communicate(timeout=30)
        output.close()
        text = (startup + tail).decode(errors="replace")
        (self.out / (filename + ".txt")).write_text(text)
        require(process.returncode == 0, "dumpcap fehlgeschlagen")
        match = re.search(r"Packets captured: (\d+)", text)
        if match is None:
            raise ValueError("dumpcap-Zähler fehlt")
        packets = read_pcap(self.out / filename)
        require(len(packets) == int(match.group(1)), "PCAP-/dumpcap-Zähler verschieden")
        self.counts[filename] = len(packets)

    def client(self, host):
        return self.run(host, PYTHON, "-B", str(BASE / "Angabe/tcp_client.py"), success=False)

    def phase(self, name):
        captures = [self.capture(host, interface, f"{name}-{label}.pcap") for host, interface, label in (
            ("client1", "client1-eth0", "client1"), ("client2", "client2-eth0", "client2"),
            ("router", "router-eth0", "router0"), ("router", "router-eth1", "router1"), ("server", "server-eth0", "server"))]
        results = {}
        for host in ("client1", "client2"):
            results[host] = {"ping": self.ping(host, "10.10.2.10"), "tcp": self.client(host)}
        for capture in captures:
            self.finish(capture)
        return results

    def cleanup(self):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
        for output in self.files:
            output.close()
        (self.out / "befehle.txt").write_text("\n".join(self.log))


def measure(out):
    require(os.geteuid() == 0, "Benötigt sudo und Python >=3.12")
    os.unshare(os.CLONE_NEWNET)
    out.mkdir(parents=True, exist_ok=False)
    lab = Lab(out)
    try:
        lab.setup()
        evidence = {"provenance": "Echte Linux-Netzwerk-Namespaces/veth/Linux Bridges; NICHT Mininet/OVS; keine künstlichen Pakete", "initial": lab.state()}
        evidence["baseline"] = {host: lab.ping(host, target) for host, target in (("client1", "10.10.1.1"), ("client2", "10.10.1.1"), ("router", "10.10.2.10"), ("server", "10.10.2.1"))}
        require(all(r["rc"] == 0 for r in evidence["baseline"].values()), "Lokale Infrastruktur fehlerhaft")
        server = lab.spawn("server", [PYTHON, "-u", "-B", str(BASE / "Angabe/tcp_server.py")])
        wait_token(server.stdout, b"Listening on 0.0.0.0:5000\n")
        evidence["before"] = lab.phase("vorher")
        require(all(r["ping"]["rc"] != 0 and r["tcp"]["rc"] != 0 for r in evidence["before"].values()), "Fehler nicht reproduziert")
        evidence["fault_state"] = lab.state()
        evidence["fault_packet_check_before_repair"] = check_fault(out)
        diagnosis = "Diagnose VOR Änderung: Serverroute über 10.10.2.254 statt vorhandenem Router 10.10.2.1; eingehende SYNs und erfolglose ARP-Auflösung im Server-PCAP; Rückweg blockiert."
        (out / "diagnose-vor-reparatur.txt").write_text(diagnosis + "\n" + json.dumps(evidence["fault_state"]["server"], indent=2))
        lab.run("server", "ip", "route", "replace", "default", "via", "10.10.2.1", "dev", "server-eth0")
        evidence["after"] = lab.phase("nachher")
        evidence["repaired_state"] = lab.state()
        require(all(r["ping"]["rc"] == 0 and r["tcp"]["rc"] == 0 and r["tcp"]["stdout"] == "RN-Lab forensic test server\n" for r in evidence["after"].values()), "Reparatur nicht bestätigt")
        evidence["capture_counts"] = lab.counts
        (out / "results.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
    finally:
        lab.cleanup()
        if "SUDO_UID" in os.environ:
            for path in (out, *out.rglob("*")):
                os.chown(path, int(os.environ["SUDO_UID"]), int(os.environ["SUDO_GID"]))
    print("Echte Vorher/Nachher-Messung abgeschlossen; 10 PCAPs. Mininet bleibt ungeprüft.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="nachweise/run01")
    parser.add_argument("--holder", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.holder:
        os.unshare(os.CLONE_NEWNET)
        print("READY", flush=True)
        while True:
            signal.pause()
    out = (BASE / args.out).resolve()
    require(out.is_relative_to(BASE / "nachweise") and out != BASE / "nachweise", "Nur neuer Ordner unter nachweise erlaubt")
    measure(out)


if __name__ == "__main__":
    main()
