# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: UDP/TCP-Code und Routing aus Blatt04 in echten isolierten Linux-
# Netzwerk-Namespaces prüfen, eigene PCAPs erfassen; kein Mininet behaupten.
"""Zusatzprüfung, KEIN Ersatz für Mininet/OVS/GUI in der bereitgestellten VM.

Start: sudo unshare --net python3 -B verify_namespaces.py --output nachweise/run01
Keine Installation, keine Änderung der Netzkonfiguration des aufrufenden Hosts.
"""

import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

BASE = Path(__file__).resolve().parent
PYTHON = "/usr/bin/python3"


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=20, **kwargs).stdout


def wait_line(process, expected):
    lines = []
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not selector.select(max(0, deadline - time.monotonic())):
                break
            line = process.stdout.readline()
            if not line:
                break
            lines.append(line)
            if expected in line:
                return (b"" if isinstance(expected, bytes) else "").join(lines)
    raise RuntimeError(f"Bereitschaft fehlt: {expected}: {lines!r}")


class Sandbox:
    def __init__(self, output):
        self.output = output
        self.children = []
        self.captures = []
        self.namespaces = []
        self.results = {"provenance": "Reale Linux-Netzwerk-Namespaces, NICHT Mininet", "checks": []}

    def host(self):
        original = os.readlink("/proc/self/ns/net")
        process = subprocess.Popen(["unshare", "--net", "sleep", "180"])
        self.children.append(process)
        deadline = time.monotonic() + 3
        while os.readlink(f"/proc/{process.pid}/ns/net") == original:
            if time.monotonic() > deadline or process.poll() is not None:
                raise RuntimeError("Netzwerk-Namespace nicht bereit")
            time.sleep(0.01)
        self.namespaces.append(process.pid)
        self.cmd(process.pid, "ip", "link", "set", "lo", "up")
        return process.pid

    @staticmethod
    def prefix(host):
        return ["nsenter", "-t", str(host), "-n"]

    def cmd(self, host, *argv):
        return run(self.prefix(host) + list(argv))

    def link(self, a, aname, aip, b, bname, bip):
        run(["ip", "link", "add", aname, "type", "veth", "peer", "name", bname])
        run(["ip", "link", "set", aname, "netns", str(a)])
        if b is not None:
            run(["ip", "link", "set", bname, "netns", str(b)])
        for host, name, address in ((a, aname, aip), (b, bname, bip)):
            if host is None:
                continue
            self.cmd(host, "ip", "addr", "add", address, "dev", name)
            self.cmd(host, "ip", "link", "set", name, "up")

    def capture(self, host, interface, filename, filter_text):
        handle = (self.output / filename).open("xb")
        process = subprocess.Popen(self.prefix(host) + ["dumpcap", "-i", interface, "-p", "-F", "pcap",
                                   "-f", filter_text, "-a", "duration:5", "-w", "-"], stdout=handle, stderr=subprocess.PIPE,
                                   text=False, bufsize=0)
        self.children.append(process)
        self.captures.append((process, handle, filename))
        # dumpcap schreibt Status auf stderr, Pakete binär auf stdout.
        proxy = type("Readiness", (), {"stdout": process.stderr})()
        wait_line(proxy, b"File:")
        return process

    def stop_capture(self, process):
        # Nicht sofort SIGINT senden: libpcap kann noch Pakete gepuffert haben.
        # Der begrenzte Capture-Timer lässt sie vollständig zur Datei abfließen.
        _, error = process.communicate(timeout=10)
        if process.returncode != 0:
            raise RuntimeError(error.decode(errors="replace"))
        for proc, handle, filename in self.captures:
            if proc is process:
                handle.close()
                (self.output / (filename + ".txt")).write_text(error.decode(errors="replace"))
                return

    def server(self, host, relative, *argv):
        process = subprocess.Popen(self.prefix(host) + [PYTHON, "-B", str(BASE / relative), *argv],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.children.append(process)
        ready = wait_line(process, "READY")
        return process, ready

    def finish_server(self, process, ready, filename):
        rest, _ = process.communicate(timeout=15)
        (self.output / filename).write_text(ready + rest)
        if process.returncode != 0:
            raise RuntimeError(ready + rest)

    def standard(self):
        h1, h2 = self.host(), self.host()
        run(["ip", "link", "add", "s1", "type", "bridge"])
        run(["ip", "link", "set", "s1", "up"])
        for host, name, address, peer in ((h1, "h1-eth0", "10.0.0.1/24", "s1-h1"),
                                           (h2, "h2-eth0", "10.0.0.2/24", "s1-h2")):
            self.link(host, name, address, None, peer, None)
            run(["ip", "link", "set", peer, "master", "s1"])
            run(["ip", "link", "set", peer, "up"])
        for host, name in ((h1, "h1"), (h2, "h2")):
            report = self.cmd(host, "ip", "addr") + self.cmd(host, "ip", "route")
            (self.output / (name + "-network.txt")).write_text(report)
        assert os.readlink(f"/proc/{h1}/ns/net") != os.readlink(f"/proc/{h2}/ns/net")
        assert os.readlink(f"/proc/{h1}/ns/uts") == os.readlink(f"/proc/{h2}/ns/uts")
        self.results["checks"].append("h1/h2: getrennte net-Namespaces, gleicher UTS-Namespace")
        process, ready = self.server(h2, "ue4.3/server.py", "--count", "3", "--timeout", "10")
        capture = self.capture(h1, "h1-eth0", "udp.pcap", "udp and src host 10.0.0.1 and dst host 10.0.0.2 and dst port 5000")
        logs = []
        for message in ("Hello from Mininet!", "Geänderte Nachricht", "Grüße 🌍"):
            logs.append(self.cmd(h1, PYTHON, "-B", str(BASE / "ue4.3/client.py"), "--message", message))
        self.finish_server(process, ready, "udp-server.txt")
        self.stop_capture(capture)
        (self.output / "udp-clients.txt").write_text("".join(logs))
        self.results["checks"].append("UDP: drei echte Datagramme von 10.0.0.1 an 10.0.0.2:5000")

    def routed(self):
        client, router, server = self.host(), self.host(), self.host()
        self.link(client, "client-eth0", "10.0.1.2/24", router, "router-eth0", "10.0.1.1/24")
        self.link(router, "router-eth1", "10.0.2.1/24", server, "server-eth0", "10.0.2.2/24")
        self.cmd(client, "ip", "route", "add", "default", "via", "10.0.1.1")
        self.cmd(server, "ip", "route", "add", "default", "via", "10.0.2.1")
        self.cmd(router, "sysctl", "-w", "net.ipv4.ip_forward=1")
        for host, interface in ((client, "client-eth0"), (router, "router-eth0"),
                                (router, "router-eth1"), (server, "server-eth0")):
            self.cmd(host, "tc", "qdisc", "add", "dev", interface, "root", "netem", "delay", "20ms", "loss", "0%")
        for host, name in ((client, "client"), (router, "router"), (server, "server")):
            report = self.cmd(host, "ip", "addr") + self.cmd(host, "ip", "route")
            report += self.cmd(host, "ip", "route", "get", "10.0.2.2")
            report += self.cmd(host, "ip", "route", "get", "10.0.1.2")
            report += self.cmd(host, "tc", "qdisc", "show")
            (self.output / (name + "-network.txt")).write_text(report)
        ping = self.cmd(client, "ping", "-c", "4", "-W", "2", "10.0.2.2")
        assert "4 received" in ping
        (self.output / "ping.txt").write_text(ping)
        # Negativprobe: dieselbe Route ohne Forwarding muss scheitern.
        self.cmd(router, "sysctl", "-w", "net.ipv4.ip_forward=0")
        failed = subprocess.run(self.prefix(client) + ["ping", "-c", "1", "-W", "1", "10.0.2.2"],
                                capture_output=True, text=True, timeout=5)
        assert failed.returncode != 0
        (self.output / "ping-forwarding-off.txt").write_text(failed.stdout)
        self.cmd(router, "sysctl", "-w", "net.ipv4.ip_forward=1")
        capture = self.capture(client, "client-eth0", "tcp.pcap", "tcp and host 10.0.1.2 and host 10.0.2.2 and port 5000")
        process, ready = self.server(server, "ue4.6/server.py", "--connections", "2", "--timeout", "15")
        logs = []
        for messages in (("Eine Nachricht",), ("eins", "Grüße 🌍", "")):
            logs.append(self.cmd(client, PYTHON, "-B", str(BASE / "ue4.6/client.py"), *messages))
        self.finish_server(process, ready, "tcp-server.txt")
        self.stop_capture(capture)
        (self.output / "tcp-clients.txt").write_text("".join(logs))
        self.results["checks"].extend(["Routing: 4/4 Ping-Antworten über Router", "Forwarding aus: Ping scheitert",
                                        "TCP: einzelne und drei persistente Nachrichten einschließlich UTF-8 und Leertext"])

    def close(self):
        for process in reversed(self.children):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
        for _, handle, _ in self.captures:
            handle.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("sudo unshare --net erforderlich")
    os.unshare(os.CLONE_NEWNET)
    assert not run(["ip", "route"]), "Frischer Netzwerk-Namespace erwartet"
    output = BASE / args.output
    if not output.resolve().is_relative_to(BASE):
        parser.error("Ausgabeverzeichnis muss innerhalb von ueb04 liegen")
    output.mkdir(parents=True, exist_ok=False)
    sandbox = Sandbox(output)
    try:
        sandbox.standard()
        sandbox.routed()
        (output / "results.json").write_text(json.dumps(sandbox.results, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(sandbox.results, ensure_ascii=False, indent=2))
    finally:
        sandbox.close()


if __name__ == "__main__":
    main()
