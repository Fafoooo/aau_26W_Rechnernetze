# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Echte isolierte Linux-Namespace-Messungen für RN Blatt08 mit PCAPs, JSON und Cleanup.
"""Linux-Bridge-Ersatzmessung, ausdrücklich kein Mininet-/Open-vSwitch-Nachweis."""
import argparse
import json
import os
import re
import selectors
import signal
import socket
import subprocess

import time
from pathlib import Path
from pcap import echo_pairs, read_pcap, require, select, tcp_flow

BASE = Path(__file__).resolve().parent
PYTHON = "/usr/bin/python3"
REQUEST = b"GET /blatt08 HTTP/1.1\r\nHost: server1.lab\r\nConnection: close\r\n\r\n"
BODY = b"RN Blatt08: echte Pakete, zwei LANs, ein Router.\n"
RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: " + str(len(BODY)).encode() + b"\r\nConnection: close\r\n\r\n" + BODY
ADDRESSES = {"client1": ("10.0.1.2", "00:00:00:00:00:01"), "client2": ("10.0.1.3", "00:00:00:00:00:02"), "server1": ("10.0.1.10", "00:00:00:00:00:03"), "server2": ("10.0.1.11", "00:00:00:00:00:04")}


def worker(mode):
    if mode == "holder":
        os.unshare(os.CLONE_NEWNET)
        print("READY", flush=True)
        while True:
            signal.pause()
    if mode == "http-server":
        with socket.socket() as listener:
            listener.settimeout(8)
            listener.bind(("10.0.2.10", 8080))
            listener.listen(1)
            print("READY", flush=True)
            connection, _ = listener.accept()
            with connection:
                connection.settimeout(5)
                incoming = b""
                while b"\r\n\r\n" not in incoming:
                    chunk = connection.recv(1024)
                    require(chunk and len(incoming) + len(chunk) <= 4096, "HTTP-Anfrage fehlt/zu lang")
                    incoming += chunk
                require(incoming == REQUEST, "Andere HTTP-Anfrage")
                connection.sendall(RESPONSE)
                connection.shutdown(socket.SHUT_WR)
                require(connection.recv(1) == b"", "Client schließt nicht sauber")
            print("HTTP-Server: Anfrage korrekt, Antwort gesendet, EOF empfangen.")
    if mode == "http-client":
        with socket.socket() as connection:
            connection.settimeout(5)
            connection.bind(("10.0.1.2", 40080))
            connection.connect(("10.0.2.10", 8080))
            connection.sendall(REQUEST)
            connection.shutdown(socket.SHUT_WR)
            incoming = b""
            while chunk := connection.recv(4096):
                require(len(incoming) + len(chunk) <= 8192, "HTTP-Antwort zu groß")
                incoming += chunk
            require(incoming == RESPONSE, "Andere HTTP-Antwort")
            print(f"HTTP-Client: {len(REQUEST)} Anfragebytes, {len(incoming)} Antwortbytes, EOF empfangen.")


def ready(process, token, timeout=5):
    deadline, observed = time.monotonic() + timeout, b""
    with selectors.DefaultSelector() as selector:
        selector.register(process.stderr, selectors.EVENT_READ)
        while token not in observed:
            remaining = deadline - time.monotonic()
            require(remaining > 0, "Capture-Bereitschaft: Zeitlimit")
            if not selector.select(min(0.2, remaining)):
                continue
            chunk = os.read(process.stderr.fileno(), 4096)
            require(chunk, "Capture vor Bereitschaft beendet")
            observed += chunk
    return observed


class Lab:
    def __init__(self, out):
        self.out, self.hosts, self.processes, self.log = out, {}, [], []
        self.counts = {}
        self.outputs = []

    def prefix(self, host):
        return ["nsenter", "-t", str(self.hosts[host].pid), "-n", "--"] if host else []

    def run(self, host, *args):
        result = subprocess.run(self.prefix(host) + list(args), capture_output=True, text=True, timeout=8)
        self.log.append(f"[{host or 'switch'}] {' '.join(args)}\n{result.stdout}{result.stderr}RC={result.returncode}\n")
        require(result.returncode == 0, f"Laborbefehl fehlgeschlagen: {args[0]}")
        return result.stdout.strip()

    def spawn(self, host, mode):
        process = subprocess.Popen(self.prefix(host) + [PYTHON, "-B", str(BASE / "messen.py"), "--worker", mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(process)
        return process

    def holder(self, name):
        process = self.spawn(None, "holder")
        self.hosts[name] = process
        assert process.stdout is not None
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            require(selector.select(5) and process.stdout.readline() == b"READY\n", "Namespace-Halter nicht bereit")
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

    def capture(self, host, filename):
        output = (self.out / filename).open("xb")
        self.outputs.append(output)
        command = self.prefix(host) + ["dumpcap", "-P", "-i", host + "-eth0", "-f", "arp or icmp or tcp", "-s", "65535", "-a", "duration:2", "-w", "-"]
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.PIPE)
        self.processes.append(process)
        try:
            startup = ready(process, b"File: -")
        except BaseException:
            output.close()
            raise
        return process, output, startup, filename

    def finish(self, capture):
        process, output, startup, filename = capture
        try:
            _, tail = process.communicate(timeout=6)
        finally:
            output.close()
        text = (startup + tail).decode("utf8", errors="replace")
        (self.out / (filename + ".txt")).write_text(text)
        require(process.returncode == 0, "dumpcap fehlgeschlagen")
        count = re.search(r"Packets captured: (\d+)", text)
        if count is None:
            raise ValueError("dumpcap-Paketzähler fehlt")
        packets = read_pcap(self.out / filename)
        require(len(packets) == int(count.group(1)), "Parser-/Capture-Paketzahl verschieden")
        self.counts[filename] = len(packets)
        return packets

    def ping(self, host, target, count=1):
        return self.run(host, "ping", "-n", "-c", str(count), "-i", "0.2", "-W", "1", target)

    def fdb(self):
        entries = json.loads(self.run(None, "bridge", "-j", "fdb", "show", "br", "brA"))
        return sorted([e for e in entries if "master" in e and "permanent" not in e.get("state", "")], key=lambda e: e["mac"])

    def cleanup(self):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
        for output in self.outputs:
            output.close()
        (self.out / "befehle.txt").write_text("\n".join(self.log))


def analyse(out):
    load = lambda name: read_pcap(out / name)
    for path in sorted(out.glob("*.pcap")):
        packets = read_pcap(path)
        for packet in packets:
            require(packet.get("ip_checksum_valid", True) and packet.get("icmp_checksum_valid", True) and packet.get("tcp_checksum_valid", True), "Ungültige Paketprüfsumme")
    ethernet = load("81_ethernet.pcap")
    require(len(select(ethernet, "icmp_type", 8)) == 4 and len(select(ethernet, "icmp_type", 0)) == 4, "8.1: Vier Echo-Paare fehlen")
    first, second = load("82_erster_ping.pcap"), load("82_zweiter_ping.pcap")
    arp = select(first, "ethertype", 0x806)
    require(any(p["arp_op"] == 1 and p["arp_tpa"] == "10.0.1.3" for p in arp), "8.2: ARP-Request fehlt")
    require(any(p["arp_op"] == 2 and p["arp_sha"] == "00:00:00:00:00:02" for p in arp), "8.2: ARP-Reply fehlt")
    require(not select(second, "ethertype", 0x806), "8.2: Zweiter Ping erzeugte neues ARP")
    witness = load("83_server2_zeuge.pcap")
    require(len(select(witness, "arp_op", 1)) == 2 and not select(witness, "proto", 1), "8.3: Broadcast-/Unicast-Zeuge unerwartet")
    pairs = echo_pairs(load("84_lanA.pcap"), load("84_lanB.pcap"))
    local = select(load("84_lokal.pcap"), "icmp_type", 8)
    require(len(local) == 1 and local[0]["dst_mac"] == "00:00:00:00:00:02", "8.4: Lokales MAC-Ziel falsch")
    http = tcp_flow(load("85_lanA.pcap"), load("85_lanB.pcap"), REQUEST, RESPONSE)
    return {"8.1": {"echo_requests": 4, "echo_replies": 4, "request": select(ethernet, "icmp_type", 8)[0]}, "8.2": {"first_arp": arp, "second_arp_count": 0}, "8.3": {"witness_broadcast_requests": 2, "witness_icmp_count": 0}, "8.4": {"routed_echo_pairs": pairs, "local_request": local[0]}, "8.5": http}


def measure(out):
    require(os.geteuid() == 0, "Mit sudo -n /usr/bin/python3 -B messen.py starten")
    os.unshare(os.CLONE_NEWNET)
    out.mkdir(parents=True, exist_ok=False)
    lab, state = Lab(out), {}
    try:
        lab.run(None, "sysctl", "-qw", "net.ipv6.conf.all.disable_ipv6=1", "net.ipv6.conf.default.disable_ipv6=1")
        lab.bridge("brA")
        for number, (name, (address, mac)) in enumerate(ADDRESSES.items(), 1):
            lab.holder(name)
            lab.attach(name, name + "-eth0", "p" + str(number), "brA", address, mac)
        cap = lab.capture("client1", "81_ethernet.pcap")
        lab.ping("server1", "10.0.1.2", 4)
        lab.finish(cap)
        lab.run("client1", "ip", "neigh", "flush", "all")
        state["82_neigh_before"] = lab.run("client1", "ip", "neigh")
        cap = lab.capture("client1", "82_erster_ping.pcap")
        lab.ping("client1", "10.0.1.3")
        state["82_neigh_after_first"] = lab.run("client1", "ip", "neigh")
        lab.finish(cap)
        cap = lab.capture("client1", "82_zweiter_ping.pcap")
        lab.ping("client1", "10.0.1.3")
        state["82_neigh_after_second"] = lab.run("client1", "ip", "neigh")
        lab.finish(cap)
        for name in ADDRESSES:
            lab.run(name, "ip", "neigh", "flush", "all")
        for number in range(1, 5):
            lab.run(None, "bridge", "fdb", "flush", "dev", "p" + str(number), "master", "dynamic")
        state["83_fdb_start"] = lab.fdb()
        witness = lab.capture("server2", "83_server2_zeuge.pcap")
        capture1 = lab.capture("client1", "83_ping1.pcap")
        lab.ping("client1", "10.0.1.10")
        state["83_fdb_after_ping1"] = lab.fdb()
        capture2 = lab.capture("client2", "83_ping2.pcap")
        lab.ping("client2", "10.0.1.10")
        state["83_fdb_after_ping2"] = lab.fdb()
        for cap in (witness, capture1, capture2):
            lab.finish(cap)
        require(not state["83_fdb_start"], "8.3: FDB am Start nicht leer")
        require({e["mac"] for e in state["83_fdb_after_ping1"]} == {ADDRESSES[h][1] for h in ("client1", "server1")}, "8.3: FDB nach Ping1 falsch")
        require({e["mac"] for e in state["83_fdb_after_ping2"]} == {ADDRESSES[h][1] for h in ("client1", "client2", "server1")}, "8.3: FDB nach Ping2 falsch")
        lab.bridge("brB")
        for number, name in ((3, "server1"), (4, "server2")):
            lab.run(None, "ip", "link", "set", "p" + str(number), "master", "brB")
            lab.run(name, "ip", "addr", "flush", "dev", name + "-eth0")
            address = "10.0.2." + ("10" if number == 3 else "11")
            lab.run(name, "ip", "addr", "add", address + "/24", "dev", name + "-eth0")
        lab.holder("router")
        for side, number in (("A", 1), ("B", 2)):
            lab.attach("router", "router-" + side, "pr" + side, "br" + side, f"10.0.{number}.1", f"02:00:00:00:0{number}:01")
        lab.run("router", "sysctl", "-qw", "net.ipv4.ip_forward=1")
        for name in ADDRESSES:
            gateway = "10.0.1.1" if name.startswith("client") else "10.0.2.1"
            lab.run(name, "ip", "route", "add", "default", "via", gateway)
            lab.run(name, "ip", "neigh", "flush", "all")
        before, after = lab.capture("client1", "84_lanA.pcap"), lab.capture("server1", "84_lanB.pcap")
        lab.ping("client1", "10.0.2.10")
        lab.finish(before)
        lab.finish(after)
        cap = lab.capture("client1", "84_lokal.pcap")
        lab.ping("client1", "10.0.1.3")
        lab.finish(cap)
        before, after = lab.capture("client1", "85_lanA.pcap"), lab.capture("server1", "85_lanB.pcap")
        server = lab.spawn("server1", "http-server")
        assert server.stdout is not None
        with selectors.DefaultSelector() as selector:
            selector.register(server.stdout, selectors.EVENT_READ)
            require(selector.select(5) and server.stdout.readline() == b"READY\n", "HTTP-Server nicht bereit")
        client = lab.spawn("client1", "http-client")
        for name, process in (("client", client), ("server", server)):
            stdout, stderr = process.communicate(timeout=8)
            require(process.returncode == 0, "HTTP-Prozess fehlgeschlagen")
            (out / ("85_http_" + name + ".txt")).write_text((stdout + stderr).decode())
        lab.finish(before)
        lab.finish(after)
        results = {"provenance": "Echte Linux-Netzwerk-Namespaces, veth, Linux Bridge; NICHT Mininet/OVS", "date": time.strftime("%Y-%m-%d"), "state": state, "capture_packet_counts": lab.counts, "analysis": analyse(out)}
        (out / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
        (out / "zustand.txt").write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    finally:
        lab.cleanup()
        if "SUDO_UID" in os.environ:
            for item in [out, *out.rglob("*")]:
                os.chown(item, int(os.environ["SUDO_UID"]), int(os.environ["SUDO_GID"]))
    print(json.dumps({"output": str(out.relative_to(BASE)), "captures": lab.counts, "verified": True}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("holder", "http-server", "http-client"), help=argparse.SUPPRESS)
    parser.add_argument("--out", default="nachweise/run01", help="Neuer, exklusiver Belegordner relativ zu ueb08")
    parser.add_argument("--analyse", action="store_true", help="Nur gesicherte PCAPs auswerten, ohne sudo/Netzänderung")
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    out = (BASE / args.out).resolve()
    require(out.is_relative_to(BASE / "nachweise") and out != BASE / "nachweise", "Output muss unter nachweise liegen")
    if args.analyse:
        print(json.dumps(analyse(out), indent=2, ensure_ascii=False))
    else:
        measure(out)


if __name__ == "__main__":
    main()
