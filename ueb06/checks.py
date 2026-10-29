# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Tatsächliche Anfrage: Erstelle Gesamttest für Blatt06, alte Tests, Original-ZIPgleichheit,
# Syntax, KI-Header, Markdownlinks, echte Messwerte, Ping/Echo und vollständige Zeilenerklärung.
"""Read-only Gesamttest; vorhandene Namespace-Messungen, niemals Mininet-Livebehauptung."""
import ast
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit
import zipfile

BASE = Path(__file__).resolve().parent
EXPLAIN = ("verify_namespaces.py", "ue6.7/topology.py", "ue6.7/start_erweitert.py", "ue6.7/test_topology.py", "checks.py")
PING = re.compile(r"(\d+) packets transmitted, (\d+) (?:packets )?received")
PLAN = {"client": {"client-eth0": ("10.0.1.2", 24)}, "client2": {"client2-eth0": ("10.0.1.3", 24)}, "r1": {"r1-eth0": ("10.0.1.1", 24), "r1-eth1": ("10.0.12.1", 30)}, "r2": {"r2-eth0": ("10.0.12.2", 30), "r2-eth1": ("10.0.2.1", 24)}, "server": {"server-eth0": ("10.0.2.2", 24)}}


def run(relative, *arguments):
    result = subprocess.run([sys.executable, "-B", str(BASE / relative), *arguments], cwd=BASE, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise AssertionError(f"{relative}: Status {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr


def snapshot():
    paths = list((BASE / "Angabe").rglob("*")) + list((BASE / "nachweise").rglob("*"))
    paths += [BASE / "erklaerung_routing.md", BASE / "erklaerung_algorithmen.md", BASE / "angabe_blatt06.pdf"]
    return {str(path.relative_to(BASE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.is_file()}


class SheetChecks(unittest.TestCase):
    def test_all_exercises_and_old_suites(self):
        for relative in ("ue6.1/adressen.py", "ue6.2/routing.py"):
            self.assertIn("Selbsttest", run(relative, "--test"))
            self.assertTrue(run(relative).strip())
        for relative, count in (("ue6.3/test_static_routes.py", 4), ("ue6.6/test_algorithmen.py", 6), ("ue6.7/test_topology.py", 7)):
            output = run(relative)
            self.assertRegex(output, rf"Ran {count} tests? in")
            self.assertIn("\nOK\n", output)
        for relative in ("ue6.4/subnetting.py", "ue6.5/dijkstra.py", "ue6.6/distance_vector.py"):
            self.assertEqual(run(relative), (BASE / relative).with_name("antwort.md").read_text())
        self.assertTrue(run("ue6.3/static_routes.py", "--help").strip())
        for number in range(1, 8):
            self.assertTrue((BASE / f"ue6.{number}/antwort.md").read_text().strip())

    def test_original_archive_byte_equality(self):
        directory = BASE / "Angabe"
        with zipfile.ZipFile(directory / "uebb6_template.zip") as archive:
            members = [item for item in archive.infolist() if not item.is_dir()]
            self.assertEqual(len(members), len({item.filename for item in members}))
            self.assertEqual({item.filename for item in members}, {p.name for p in directory.iterdir() if p.is_file() and p.suffix != ".zip"})
            for item in members:
                self.assertEqual(Path(item.filename).name, item.filename)
                self.assertEqual(archive.read(item), (directory / item.filename).read_bytes(), item.filename)

    def test_syntax_headers_and_shell_syntax(self):
        for path in sorted(BASE.rglob("*.py")):
            source = path.read_text()
            compile(source, str(path), "exec")
            if "Angabe" not in path.relative_to(BASE).parts:
                header = "\n".join(source.splitlines()[:6])
                for required in ("KI-Kennzeichnung RN WS26", "Hermes Agent", "OpenAI gpt-6.1-sol", "2026-10-29", "Anfrage:"):
                    self.assertIn(required, header, str(path))
        for path in (BASE / "Angabe").glob("*.sh"):
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_relative_markdown_links(self):
        for path in BASE.rglob("*.md"):
            for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", re.sub(r"<code>.*?</code>|```.*?```|`[^`\n]*`", "", path.read_text(), flags=re.DOTALL)):
                parsed = urlsplit(html.unescape(target.strip("<>")))
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                self.assertTrue(resolved.is_relative_to(BASE), f"Link außerhalb Blatt06: {path}: {target}")
                self.assertTrue(resolved.exists(), f"Fehlender Link: {path}: {target}")

    def test_explanation_every_nonempty_line_and_exact_source(self):
        text = (BASE / "erklaerung_blatt06.md").read_text()
        for relative in EXPLAIN:
            heading = f"## [{relative}]({relative})\n"
            self.assertEqual(text.count(heading), 1, relative)
            section = text.split(heading, 1)[1].split("\n## ", 1)[0]
            rows = re.findall(r"^\| (\d+) \| <code>(.*?)</code> \| (.+) \|$", section, re.MULTILINE)
            expected = [(number, line) for number, line in enumerate((BASE / relative).read_text().splitlines(), 1) if line.strip()]
            self.assertEqual([(int(number), html.unescape(code)) for number, code, _ in rows], expected, relative)
            self.assertTrue(all(len(description.strip()) >= 20 for _, _, description in rows), relative)
        routing = (BASE / "erklaerung_routing.md").read_text()
        for relative in ("ue6.1/adressen.py", "ue6.2/routing.py", "ue6.3/static_routes.py", "ue6.3/test_static_routes.py"):
            section = routing.split(f"## [{relative}]({relative})", 1)[1].split("\n## ", 1)[0]
            numbers = [int(value) for value in re.findall(r"^\| (\d+) \|", section, re.MULTILINE)]
            self.assertEqual(numbers, [i for i, line in enumerate((BASE / relative).read_text().splitlines(), 1) if line.strip()])
        self.assertIn("erklaerung_routing.md", text)
        self.assertIn("erklaerung_algorithmen.md", text)

    def test_namespace_addresses_and_provenance(self):
        evidence = BASE / "nachweise/run01"
        results = json.loads((evidence / "results.json").read_text())
        self.assertEqual([item["fall"] for item in results], ["basis", "erweitert"])
        for item in results:
            self.assertIn("NICHT Mininet/OVS", item["messung"])
            self.assertIn("keine TC-Verzögerung", item["messung"])
            names = ["client", "r1", "r2", "server"] + (["client2"] if item["fall"] == "erweitert" else [])
            self.assertEqual(item["tcp_clients"], ["client", "client2"] if item["fall"] == "erweitert" else ["client"])
            for name in names:
                data = json.loads((evidence / f"{item['fall']}-{name}-addr.json").read_text())
                addresses = {interface["ifname"]: (address["local"], address["prefixlen"]) for interface in data if interface["ifname"] != "lo" for address in interface.get("addr_info", []) if address["family"] == "inet"}
                self.assertEqual(addresses, PLAN[name])
                report = (evidence / f"{item['fall']}-{name}.txt").read_text()
                for command in ("$ ip -br addr", "$ ip addr", "$ bash Angabe/inspect_network.sh", "=== Routing table ==="):
                    self.assertIn(command, report)
                run("ue6.1/adressen.py", "--json", str(evidence / f"{item['fall']}-{name}-addr.json"), "--host", "client" if name == "client2" else name)

    def test_exact_ping_counts_statuses_and_route_cycle(self):
        evidence = BASE / "nachweise/run01"
        for tag in ("basis", "erweitert"):
            text = (evidence / f"{tag}-routen-und-ping.txt").read_text()
            self.assertEqual(PING.findall(text), [("3", "3"), ("3", "0"), ("3", "3")])
            blocks = re.findall(r"\[client\] \$ .*?ping[^\n]*\n(.*?)\[Exitstatus (\d+)\]", text, re.DOTALL)
            self.assertEqual([status for _, status in blocks], ["0", "1", "0"])
            self.assertEqual([re.findall(r"^64 bytes from .*?icmp_seq=(\d+)", block, re.MULTILINE) for block, _ in blocks], [["1", "2", "3"], [], ["1", "2", "3"]])
            for router, network, gateway, interface in (("r1", "10.0.2.0/24", "10.0.12.2", "r1-eth1"), ("r2", "10.0.1.0/24", "10.0.12.1", "r2-eth0")):
                for operation in ("del", "add"):
                    self.assertIn(f"[{router}] $ ip route {operation} {network} via {gateway} dev {interface}\n[Exitstatus 0]", text)
                self.assertIn(f"[{router}] $ sysctl -n net.ipv4.ip_forward\n1\n[Exitstatus 0]", text)
            self.assertEqual(text.count("RTNETLINK answers: Network is unreachable\n[Exitstatus 2]"), 2)
        expected = {"basis-server-ping-10.0.1.2.txt", "erweitert-server-ping-10.0.1.2.txt", "erweitert-client2-ping-10.0.1.2.txt", "erweitert-server-ping-10.0.1.3.txt"}
        self.assertEqual({path.name for path in evidence.glob("*-ping-*.txt")}, expected)
        for name in expected:
            text = (evidence / name).read_text()
            self.assertEqual(PING.findall(text), [("3", "3")])
            self.assertEqual(re.findall(r"^64 bytes from .*?icmp_seq=(\d+)", text, re.MULTILINE), ["1", "2", "3"])

    def test_original_tcp_echo_content_and_server_connections(self):
        tree = ast.parse((BASE / "Angabe/tcp_client.py").read_text())
        messages = next(node.iter.elts for node in ast.walk(tree) if isinstance(node, ast.For) and isinstance(node.iter, ast.List))
        payloads = [ast.literal_eval(node) for node in messages]
        self.assertEqual(payloads, [f"Network layer test {i}\n".encode() for i in (1, 2, 3)])
        for tag, clients in (("basis", ["client"]), ("erweitert", ["client", "client2"])):
            server = (BASE / f"nachweise/run01/{tag}-server-tcp.txt").read_text().splitlines()
            self.assertEqual(server[0], "Listening on 10.0.2.2:5000")
            connections = [ast.literal_eval(line.removeprefix("Connection from ")) for line in server if line.startswith("Connection from ")]
            self.assertEqual([address for address, _ in connections], ["10.0.1.2", "10.0.1.3"][:len(clients)])
            self.assertTrue(all(isinstance(port, int) and 0 < port <= 65535 for _, port in connections))
            self.assertEqual([line for line in server if line.startswith("Received ")], [f"Received {len(payload)} bytes" for _ in clients for payload in payloads])
            self.assertEqual(len(server), 1 + len(clients) * (1 + len(payloads)))
            for client in clients:
                lines = (BASE / f"nachweise/run01/{tag}-{client}-tcp.txt").read_text().splitlines()
                self.assertEqual(lines[0], "Connected to 10.0.2.2:5000")
                self.assertEqual([ast.literal_eval(line.removeprefix("Reply: ")) for line in lines[1:]], payloads)
        self.assertEqual({p.name for p in (BASE / "nachweise/run01").glob("*-tcp.txt")}, {"basis-client-tcp.txt", "basis-server-tcp.txt", "erweitert-client-tcp.txt", "erweitert-client2-tcp.txt", "erweitert-server-tcp.txt"})

    def test_no_helper_files_in_tree_or_staging(self):
        def unwanted(path):
            return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo", ".tmp", ".log", ".bak", ".swp"} or path.name in {".DS_Store", "generate_explanation.py"}
        self.assertEqual([str(path.relative_to(BASE)) for path in BASE.rglob("*") if unwanted(path)], [])
        result = subprocess.run(["git", "diff", "--cached", "--name-only", "-z", "--", "ueb06"], cwd=BASE.parent, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(any(unwanted(Path(os.fsdecode(name))) for name in result.stdout.split(b"\0") if name))


if __name__ == "__main__":
    before = snapshot()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SheetChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    unchanged = before == snapshot()
    print(f"Originale, alte Erklärungen und run01 unverändert: {unchanged}")
    print("Grenze: API-Test-Doubles + archivierte echte Linux-Namespace-Messungen; Mininet/OVS/xterm NICHT live verifiziert.")
    raise SystemExit(0 if result.wasSuccessful() and unchanged else 1)
