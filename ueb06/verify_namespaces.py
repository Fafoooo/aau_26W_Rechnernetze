# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Prüfe Blatt06 mit echten isolierten Netzwerk-Namespaces, Routenlöschung und unverändertem TCP-Code.
"""Zusatznachweis, NICHT Mininet/OVS. sudo /usr/bin/python3 -B verify_namespaces.py

Python >=3.12; iproute2, ping, unshare, nsenter. Keine Installation.
Alle Netzwerkänderungen erfolgen erst nach os.unshare(CLONE_NEWNET).
"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import selectors
import subprocess
import time

BASE = Path(__file__).resolve().parent
PYTHON = "/usr/bin/python3"


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, BASE / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv, **kwargs):
    return subprocess.run(argv, capture_output=True, text=True, timeout=20, **kwargs)


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
        except BaseException:
            self.close()
            raise
        self.checked(["ip", "link", "set", "lo", "up"])

    def prefix(self):
        return ["nsenter", "-t", str(self.process.pid), "-n"]

    def pexec(self, argv):
        result = run(self.prefix() + argv, env={**os.environ, "LC_ALL": "C"})
        return result.stdout, result.stderr, result.returncode

    def checked(self, argv):
        out, err, status = self.pexec(argv)
        if status:
            raise RuntimeError(f"{self.name}: {argv}: {out}{err}")
        return out

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=5)


def checked(argv):
    result = run(argv)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def link(a, aname, address_a, b, bname, address_b):
    checked(["ip", "link", "add", aname, "type", "veth", "peer", "name", bname])
    for node, name, address in ((a, aname, address_a), (b, bname, address_b)):
        if node:
            checked(["ip", "link", "set", name, "netns", str(node.process.pid)])
            if address:
                node.checked(["ip", "addr", "add", address, "dev", name])
            node.checked(["ip", "link", "set", name, "up"])
        else:
            checked(["ip", "link", "set", name, "master", "s1"])
            checked(["ip", "link", "set", name, "up"])


def ready(process):
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        if not selector.select(5):
            raise RuntimeError("TCP-Server wurde nicht bereit")
        line = process.stdout.readline()
    if "Listening on 10.0.2.2:5000" not in line:
        raise RuntimeError(line)
    return line


def scenario(extended, output):
    nodes = {}
    server = None
    try:
        for name in ("client", "r1", "r2", "server") + (("client2",) if extended else ()):
            nodes[name] = Node(name)
        c, r1, r2, s = (nodes[x] for x in ("client", "r1", "r2", "server"))
        if extended:
            checked(["ip", "link", "add", "s1", "type", "bridge"])
            checked(["ip", "link", "set", "s1", "up"])
            for node, interface, address, peer in ((c, "client-eth0", "10.0.1.2/24", "s1-eth1"),
                    (nodes["client2"], "client2-eth0", "10.0.1.3/24", "s1-eth2"),
                    (r1, "r1-eth0", "10.0.1.1/24", "s1-eth3")):
                link(node, interface, address, None, peer, None)
        else:
            link(c, "client-eth0", "10.0.1.2/24", r1, "r1-eth0", "10.0.1.1/24")
        link(r1, "r1-eth1", "10.0.12.1/30", r2, "r2-eth0", "10.0.12.2/30")
        link(r2, "r2-eth1", "10.0.2.1/24", s, "server-eth0", "10.0.2.2/24")
        for name, gateway in (("client", "10.0.1.1"), ("server", "10.0.2.1")) + ((("client2", "10.0.1.1"),) if extended else ()):
            nodes[name].checked(["ip", "route", "add", "default", "via", gateway])
        routes = load("static_routes", "ue6.3/static_routes.py")
        for router in (r1, r2):
            router.checked(["sysctl", "-w", "net.ipv4.ip_forward=1"])
            network, gateway, interface, _ = routes.ROUTES[router.name]
            router.checked(["ip", "route", "add", network, "via", gateway, "dev", interface])
        tag = "erweitert" if extended else "basis"
        output.mkdir(parents=True, exist_ok=True)
        for name, node in nodes.items():
            report = "$ ip -br addr\n" + node.checked(["ip", "-br", "addr"])
            report += "$ ip addr\n" + node.checked(["ip", "addr"])
            report += "$ bash Angabe/inspect_network.sh\n" + node.checked(["bash", str(BASE / "Angabe/inspect_network.sh")])
            (output / f"{tag}-{name}.txt").write_text(report)
            raw = node.checked(["ip", "-j", "addr"])
            (output / f"{tag}-{name}-addr.json").write_text(raw)
            for interface in json.loads(raw):
                for item in interface.get("addr_info", []):
                    if item["family"] == "inet" and interface["ifname"] != "lo":
                        expected = {"client-eth0": "10.0.1.2", "client2-eth0": "10.0.1.3", "r1-eth0": "10.0.1.1", "r1-eth1": "10.0.12.1", "r2-eth0": "10.0.12.2", "r2-eth1": "10.0.2.1", "server-eth0": "10.0.2.2"}
                        assert item["local"] == expected[interface["ifname"]]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            routes.ping3(c)
            routes.exercise(nodes)
        (output / f"{tag}-routen-und-ping.txt").write_text(buffer.getvalue())
        targets = [(s, "10.0.1.2")]
        if extended:
            targets.extend([(nodes["client2"], "10.0.1.2"), (s, "10.0.1.3")])
        for source, target in targets:
            result = source.checked(["ping", "-c", "3", "-W", "2", target])
            assert "3 received" in result
            (output / f"{tag}-{source.name}-ping-{target}.txt").write_text(result)
        server = subprocess.Popen(s.prefix() + [PYTHON, "-u", "-B", str(BASE / "Angabe/tcp_server.py")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        server_start = ready(server)
        for name in ("client", "client2") if extended else ("client",):
            result = nodes[name].checked([PYTHON, "-B", str(BASE / "Angabe/tcp_client.py")])
            assert result.count("Reply:") == 3
            for number in (1, 2, 3):
                assert f"Reply: b'Network layer test {number}\\n'" in result
            (output / f"{tag}-{name}-tcp.txt").write_text(result)
        server.terminate()
        rest, _ = server.communicate(timeout=5)
        (output / f"{tag}-server-tcp.txt").write_text(server_start + rest)
        assert rest.count("Connection from") == (2 if extended else 1)
        return {"fall": tag, "routing": "3/3 vor und nach Wiederherstellung; 0/3 ohne Routen", "tcp_clients": ["client", "client2"] if extended else ["client"], "messung": "Linux-Network-Namespaces, Linux-Bridge; NICHT Mininet/OVS; keine TC-Verzögerung"}
    finally:
        if server and server.poll() is None:
            server.terminate()
            server.wait(timeout=5)
        for node in reversed(list(nodes.values())):
            node.close()
        if extended:
            checked(["ip", "link", "del", "s1"])


def main():
    if os.geteuid() != 0:
        raise SystemExit("Nur für isolierte Zusatztests: sudo /usr/bin/python3 -B verify_namespaces.py")
    os.unshare(os.CLONE_NEWNET)
    output = BASE / "nachweise/run01"
    if output.exists():
        raise SystemExit("run01 existiert bereits; nicht mit anderem Messlauf mischen")
    results = [scenario(False, output), scenario(True, output)]
    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
