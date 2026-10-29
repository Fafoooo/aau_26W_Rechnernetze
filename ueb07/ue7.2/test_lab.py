# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;
# lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.
"""Nur synthetische API-/Modelltests: KEINE Netzwerk-, Ping- oder RTT-Messungen."""

import contextlib
import importlib.util
import io
import html
import re
import zipfile
import ipaddress
from pathlib import Path
import sys
import types
import unittest
from unittest import mock
from lab_config import DEFAULT_ROUTES, LINKS, NODES, PATH_NODES, PATH_ROUTES, R3_ROUTES
from lab_control import LabControl, checked, route_args
import start_lab


class FakeNode:
    def __init__(self, name):
        self.name = name
        self.calls = []
        self.routes = {}
        self.failures = []
        self.ping_status = 0

    def config(self, **params):
        return params

    def pexec(self, *args):
        self.calls.append(args)
        if args in self.failures:
            self.failures.remove(args)
            return "", "synthetic command failure", 7
        if args[0] == "ping":
            return "SYNTHETISCH: 100% packet loss\n", "", self.ping_status
        if args[:2] == ("ip", "route") and args[2] in ("replace", "del"):
            operation, prefix = args[2:4]
            if operation == "del":
                if prefix not in self.routes:
                    return "", "synthetic missing route", 2
                del self.routes[prefix]
            else:
                self.routes[prefix] = args[4:]
        return "", "", 0


class FakeNet(dict):
    def __init__(self, **kwargs):
        super().__init__((name, FakeNode(name)) for name in NODES)
        self.built = False
        self.started = False
        self.stopped = False

    def build(self):
        self.built = True

    def start(self):
        if not self.built:
            raise RuntimeError("synthetic start before build")
        self.started = True

    def stop(self):
        self.stopped = True


class FakeTopo:
    def __init__(self):
        self.hosts = {}
        self.links = []
        self.build()

    def build(self):
        pass

    def addHost(self, name, **params):
        self.hosts[name] = params
        return name

    def addLink(self, left, right, **params):
        self.links.append((left, right, params))


def synthetic_modules(net):
    modules = {name: types.ModuleType(name) for name in
               ("mininet", "mininet.net", "mininet.cli", "mininet.link",
                "mininet.log", "mininet.topo", "mininet.node")}
    modules["mininet.net"].Mininet = mock.Mock(return_value=net)
    modules["mininet.cli"].CLI = lambda network: None
    modules["mininet.link"].TCLink = object
    modules["mininet.log"].setLogLevel = lambda level: None
    modules["mininet.topo"].Topo = FakeTopo
    modules["mininet.node"].Host = object
    modules["mininet.node"].Node = FakeNode
    return modules


def load_topology():
    path = Path(__file__).with_name("topology.py")
    spec = importlib.util.spec_from_file_location("synthetic_topology", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModelTests(unittest.TestCase):
    def test_unique_interfaces_and_distinct_routed_subnets(self):
        interfaces = []
        networks = []
        for left, right, il, ir, al, ar, delay in LINKS:
            interfaces.extend(((left, il), (right, ir)))
            a, b = ipaddress.ip_interface(al), ipaddress.ip_interface(ar)
            self.assertEqual(a.network, b.network)
            self.assertNotEqual(a.ip, b.ip)
            self.assertIn(delay, ("1ms", "5ms", "30ms"))
            networks.append(a.network)
        self.assertEqual(len(interfaces), len(set(interfaces)))
        self.assertEqual(len(networks), len(set(networks)))
        for index, network in enumerate(networks):
            self.assertFalse(any(network.overlaps(other) for other in networks[index + 1:]))

    def test_original_addresses_and_new_links(self):
        self.assertEqual(LINKS[0][2:6], ("client-eth0", "r1-eth0", "10.0.1.2/24", "10.0.1.1/24"))
        self.assertEqual(LINKS[1][2:6], ("r1-eth1", "r2-eth0", "10.0.12.1/30", "10.0.12.2/30"))
        self.assertEqual(LINKS[2][2:6], ("r2-eth1", "server-eth0", "10.0.2.1/24", "10.0.2.2/24"))
        self.assertEqual(LINKS[3][2:6], ("r1-eth2", "r3-eth0", "10.0.13.1/30", "10.0.13.2/30"))
        self.assertEqual(LINKS[4][2:6], ("r3-eth1", "r2-eth2", "10.0.23.1/30", "10.0.23.2/30"))

    def test_symmetric_model_walk_and_delay_budget(self):
        for path, expected in PATH_NODES.items():
            for nodes, target in ((expected, "10.0.2.2"), (expected[::-1], "10.0.1.2")):
                total = 0
                for source, destination in zip(nodes, nodes[1:]):
                    link = next(link for link in LINKS if {source, destination} == set(link[:2]))
                    total += int(link[-1][:-2])
                    side = 0 if source == link[0] else 1
                    neighbor_address = ipaddress.ip_interface(link[5 - side]).ip
                    if source in ("r1", "r2", "r3"):
                        routes = PATH_ROUTES[path] + R3_ROUTES
                        relevant = [r for r in routes if r[0] == source and
                                    ipaddress.ip_address(target) in ipaddress.ip_network(r[1])]
                        if relevant:
                            self.assertEqual(len(relevant), 1)
                            self.assertEqual(relevant[0][2], str(neighbor_address))
                            self.assertEqual(relevant[0][3], link[2 + side])
                        else:
                            self.assertIn(ipaddress.ip_address(target), ipaddress.ip_interface(link[4 + side]).network)
                    else:
                        self.assertIn((source, str(neighbor_address), link[2 + side]), DEFAULT_ROUTES)
                self.assertEqual(2 * total, {"A": 14, "B": 124}[path])

    def test_router_forwarding_config_and_failure(self):
        with mock.patch.dict(sys.modules, synthetic_modules(FakeNet())):
            topology = load_topology()
        router = topology.LinuxRouter("r3")
        self.assertEqual(router.config(ip=None), {"ip": None})
        command = ("sysctl", "-w", "net.ipv4.ip_forward=1")
        self.assertIn(command, router.calls)
        router.failures.append(command)
        with self.assertRaises(RuntimeError):
            router.config()

    def test_topology_calls(self):
        with mock.patch.dict(sys.modules, synthetic_modules(FakeNet())):
            topology = load_topology()
            topo = topology.RoutingTopo()
        self.assertEqual(set(topo.hosts), set(NODES))
        self.assertTrue(all(host["ip"] is None for host in topo.hosts.values()))
        self.assertEqual(len(topo.links), 5)
        for actual, expected in zip(topo.links, LINKS):
            left, right, params = actual
            self.assertEqual((left, right, params["intfName1"], params["intfName2"], params["delay"]),
                             (expected[0], expected[1], expected[2], expected[3], expected[6]))


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.net = FakeNet()
        self.lab = LabControl(self.net)
        self.lab.configure()

    def assert_path(self, path):
        self.assertEqual(self.lab.path, path)
        for route in PATH_ROUTES[path]:
            self.assertEqual(self.net[route[0]].routes[route[1]], route_args(route)[4:])
        self.assertEqual(len(self.net["r1"].routes), 1)
        self.assertEqual(len(self.net["r2"].routes), 1)

    def test_configuration_and_path_round_trip(self):
        self.assert_path("A")
        for left, right, il, ir, al, ar, _ in LINKS:
            for node, interface, address in ((left, il, al), (right, ir, ar)):
                self.assertIn(("ip", "addr", "add", address, "dev", interface), self.net[node].calls)
        for path in ("B", "A", "B"):
            self.lab.select_path(path)
            self.assert_path(path)
        for node, gateway, interface in DEFAULT_ROUTES:
            self.assertEqual(self.net[node].routes["default"], ("via", gateway, "dev", interface))

    def test_invalid_path_has_no_side_effects(self):
        before = sum(len(node.calls) for node in self.net.values())
        for operation in (self.lab.configure, self.lab.select_path):
            with self.assertRaises(ValueError):
                operation("C")
        self.assertEqual(before, sum(len(node.calls) for node in self.net.values()))

    def test_switch_rolls_back_after_second_router_failure(self):
        self.net["r2"].failures.append(route_args(PATH_ROUTES["B"][1]))
        with self.assertRaises(RuntimeError):
            self.lab.select_path("B")
        self.assert_path("A")

    def test_rollback_failure_marks_state_unknown(self):
        self.net["r2"].failures.append(route_args(PATH_ROUTES["B"][1]))
        self.net["r1"].failures.append(route_args(PATH_ROUTES["A"][0]))
        with self.assertRaisesRegex(RuntimeError, "Rollback fehlgeschlagen"):
            self.lab.select_path("B")
        self.assertIsNone(self.lab.path)

    def test_initial_failure_removes_partial_route(self):
        net = FakeNet()
        net["r2"].failures.append(route_args(PATH_ROUTES["A"][1]))
        lab = LabControl(net)
        with self.assertRaises(RuntimeError):
            lab.select_path("A")
        self.assertEqual(net["r1"].routes, {})
        self.assertIsNone(lab.path)

    def test_fault_delete_restore_and_idempotency(self):
        self.lab.select_path("B")
        self.lab.set_fault(True)
        self.assertNotIn("10.0.2.0/24", self.net["r3"].routes)
        self.assertIn("10.0.1.0/24", self.net["r3"].routes)
        count = len(self.net["r3"].calls)
        self.lab.set_fault(True)
        self.assertEqual(len(self.net["r3"].calls), count)
        self.lab.select_path("A")
        self.assertTrue(self.lab.fault)
        self.lab.set_fault(False)
        self.assertFalse(self.lab.fault)
        self.assertEqual(self.net["r3"].routes["10.0.2.0/24"], route_args(R3_ROUTES[0])[4:])

    def test_failed_fault_command_does_not_change_flag(self):
        self.net["r3"].failures.append(route_args(R3_ROUTES[0], "del"))
        with self.assertRaises(RuntimeError):
            self.lab.set_fault(True)
        self.assertFalse(self.lab.fault)

    def test_ping_uses_exit_status_not_loss_substring(self):
        for status in (1, 2):
            self.net["client"].ping_status = status
            with self.assertRaisesRegex(RuntimeError, f"exit={status}"):
                self.lab.ping()
        self.net["client"].ping_status = 0
        self.net["server"].ping_status = 1
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):
            self.lab.ping()
        self.net["server"].ping_status = 0
        with contextlib.redirect_stdout(io.StringIO()):
            self.lab.ping(4)
        self.assertIn(("ping", "-n", "-c", "4", "-W", "2", "-w", "14", "10.0.2.2"), self.net["client"].calls)
        for count in (0, -1, "3"):
            with self.assertRaises(ValueError):
                self.lab.ping(count)

    def test_spawn_error_also_rolls_back(self):
        with mock.patch.object(self.net["r2"], "pexec", side_effect=OSError("synthetic spawn failure")):
            with self.assertRaisesRegex(RuntimeError, "Prozessstart fehlgeschlagen"):
                self.lab.select_path("B")
        self.assert_path("A")

    def test_reconfigure_restores_fault_flag_and_route(self):
        self.lab.set_fault(True)
        self.lab.configure("B")
        self.assertFalse(self.lab.fault)
        self.assertIn("10.0.2.0/24", self.net["r3"].routes)
        self.assert_path("B")

    def test_checked_reports_stderr(self):
        node = self.net["r1"]
        node.failures.append(("bad",))
        with self.assertRaisesRegex(RuntimeError, "synthetic command failure"):
            checked(node, "bad")


class StartupTests(unittest.TestCase):
    def run_main(self, net, args):
        modules = synthetic_modules(net)
        with mock.patch.dict(sys.modules, modules):
            modules["topology"] = load_topology()
        with mock.patch.dict(sys.modules, modules), mock.patch.object(start_lab.os, "geteuid", return_value=0):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                status = start_lab.main(args)
        modules["mininet.net"].Mininet.assert_called_once_with(
            topo=mock.ANY, controller=None, link=object, autoSetMacs=True, build=False)
        return status

    def test_check_only_starts_stops_both_paths(self):
        for path in ("A", "B"):
            net = FakeNet()
            self.assertEqual(self.run_main(net, ["--path", path, "--check-only"]), 0)
            self.assertTrue(net.built and net.started and net.stopped)
            self.assertEqual(net.lab.path, path)

    def test_ping_failure_is_nonzero_and_cleans_up(self):
        net = FakeNet()
        net["client"].ping_status = 1
        self.assertEqual(self.run_main(net, ["--check-only"]), 1)
        self.assertTrue(net.stopped)

    def test_build_exception_still_stops_without_starting(self):
        for error_type in (RuntimeError, OSError):
            with self.subTest(error_type=error_type):
                net = FakeNet()
                net.build = mock.Mock(side_effect=error_type("synthetic partial build failure"))
                net.start = mock.Mock(wraps=net.start)
                net.stop = mock.Mock(wraps=net.stop)
                self.assertEqual(self.run_main(net, ["--check-only"]), 1)
                net.build.assert_called_once_with()
                net.start.assert_not_called()
                net.stop.assert_called_once_with()
                self.assertTrue(net.stopped)
                self.assertFalse(hasattr(net, "lab"))

    def test_start_exception_still_stops(self):
        net = FakeNet()
        net.start = mock.Mock(side_effect=RuntimeError("synthetic startup failure"))
        self.assertEqual(self.run_main(net, []), 1)
        self.assertTrue(net.stopped)

    def test_cli_commands_and_error_messages(self):
        cli = start_lab.make_cli(object)()
        cli.mn = FakeNet()
        cli.mn.lab = LabControl(cli.mn)
        cli.mn.lab.configure()
        with contextlib.redirect_stdout(io.StringIO()) as output:
            cli.do_path("b")
            self.assertEqual(cli.mn.lab.path, "B")
            cli.do_fault("on")
            self.assertTrue(cli.mn.lab.fault)
            cli.do_fault("off")
            self.assertFalse(cli.mn.lab.fault)
            cli.do_fault("invalid")
            cli.do_path("C")
            cli.do_check("")
            cli.do_state("")
        self.assertIn("Verwendung: fault on|off", output.getvalue())
        self.assertIn("FEHLER:", output.getvalue())
        self.assertIn("Pfad=B", output.getvalue())


class DocumentationTests(unittest.TestCase):
    def test_every_nonempty_source_line_is_explained_exactly_once(self):
        root = Path(__file__).resolve().parent
        document = (root.parent / "erklaerung_topologie.md").read_text()
        for source in sorted(root.glob("*.py")):
            heading = f"## Datei: `{source.name}`\n"
            self.assertIn(heading, document)
            section = document.split(heading, 1)[1].split("\n## ", 1)[0]
            found = [(int(number), html.unescape(code)) for number, code in
                     re.findall(r"^\d+\. Zeile \*\*(\d+)\*\*: <code>(.*?)</code> — .+$", section, re.MULTILINE)]
            expected = [(number, line) for number, line in enumerate(source.read_text().splitlines(), 1) if line.strip()]
            self.assertEqual(found, expected, source.name)
            self.assertIn("KI-Kennzeichnung", source.read_text().splitlines()[0])

    def test_supplied_files_equal_original_archive(self):
        supplied = Path(__file__).resolve().parent.parent / "Angabe"
        with zipfile.ZipFile(supplied / "uebb7_template.zip") as archive:
            for name in archive.namelist():
                self.assertEqual((supplied / name).read_bytes(), archive.read(name), name)


if __name__ == "__main__":
    print("SYNTHETISCHE Tests: keine Mininet-Ausführung, keine echten Pings oder RTTs.")
    unittest.main(verbosity=2)
