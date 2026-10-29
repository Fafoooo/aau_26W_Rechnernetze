# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Tatsächliche Anfrage: Erstelle explizite Mininet-Test-Doubles für Struktur, Schnittstellen,
# OVSBridge, Routerforwarding und Starter mit robusten Ping-Zählern; teste ohne Installation.
"""Nur synthetische API-Test-Doubles: kein Mininet, kein OVS, keine echten Pakete."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

BASE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NodeDouble:
    def __init__(self):
        self.calls = []
        self.reply = ("3 packets transmitted, 3 received, 0% packet loss", "", 0)

    def config(self, **params):
        self.calls.append(("config", params))

    def cmd(self, command):
        self.calls.append(("cmd", command))
        return ""

    def pexec(self, argv, **kwargs):
        self.calls.append(("pexec", argv, kwargs))
        return self.reply if argv[0] == "ping" else ("", "", 0)

    def terminate(self):
        self.calls.append(("terminate",))


class TopoDouble:
    def __init__(self):
        self.hosts, self.switches, self.links = {}, {}, []
        self.build()

    def addHost(self, name, **params):
        self.hosts[name] = params
        return name

    def addSwitch(self, name, **params):
        self.switches[name] = params
        return name

    def addLink(self, left, right, **params):
        self.links.append((left, right, params))


class TopologyTests(unittest.TestCase):
    def setUp(self):
        definitions = {
            "mininet": {}, "mininet.topo": {"Topo": TopoDouble},
            "mininet.node": {"Node": NodeDouble, "Host": type("HostDouble", (), {}), "OVSBridge": type("OVSBridgeDouble", (), {})},
            "mininet.link": {"TCLink": type("TCLinkDouble", (), {})},
            "mininet.cli": {"CLI": Mock()}, "mininet.net": {"Mininet": Mock()},
            "mininet.log": {"setLogLevel": Mock(), "info": Mock()}, "mininet.term": {"makeTerm": Mock()},
        }
        modules = {name: types.ModuleType(name) for name in definitions}
        for name, attributes in definitions.items():
            modules[name].__dict__.update(attributes)
        self.addCleanup(patch.stopall)
        patch.dict(sys.modules, modules).start()
        self.topology = load("topology_double_subject", BASE / "topology.py")
        patch.dict(sys.modules, {"topology": self.topology}).start()
        self.starter = load("starter_double_subject", BASE / "start_erweitert.py")
        self.nodes = {name: NodeDouble() for name in ("client", "client2", "r1", "r2", "server")}
        self.net = Mock()
        self.net.__getitem__ = Mock(side_effect=self.nodes.__getitem__)
        self.starter.Mininet.return_value = self.net
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_structure_interfaces_bridge_and_delay(self):
        topo = self.topology.RoutingTopo()
        self.assertEqual(set(topo.hosts), set(self.nodes))
        self.assertEqual(topo.switches, {"s1": {"cls": sys.modules["mininet.node"].OVSBridge}})
        expected = [("client", "s1", "client-eth0", "s1-eth1"), ("client2", "s1", "client2-eth0", "s1-eth2"), ("s1", "r1", "s1-eth3", "r1-eth0"), ("r1", "r2", "r1-eth1", "r2-eth0"), ("r2", "server", "r2-eth1", "server-eth0")]
        actual = [(a, b, p["intfName1"], p["intfName2"]) for a, b, p in topo.links]
        self.assertEqual(actual, expected)
        for _, _, params in topo.links:
            self.assertIs(params["cls"], sys.modules["mininet.link"].TCLink)
            self.assertEqual(params["delay"], "10ms")
        for name, params in topo.hosts.items():
            self.assertIs(params["cls"], self.topology.LinuxRouter if name in ("r1", "r2") else sys.modules["mininet.node"].Host)
        self.assertEqual(self.topology.topos, {"routingtopo": self.topology.RoutingTopo})

    def test_forwarding_lifecycle(self):
        router = self.topology.LinuxRouter()
        router.config(ip=None)
        router.terminate()
        self.assertEqual(router.calls, [("config", {"ip": None}), ("cmd", "sysctl -w net.ipv4.ip_forward=1 >/dev/null"), ("cmd", "sysctl -w net.ipv4.ip_forward=0 >/dev/null"), ("terminate",)])

    def test_ping_accepts_both_counter_formats(self):
        node = self.nodes["client2"]
        for received in ("received", "packets received"):
            node.reply = (f"3 packets transmitted, 3 {received}", "", 0)
            self.starter.ping_ok(node, "10.0.2.2")
        self.assertEqual(node.calls[-1], ("pexec", ["ping", "-c", "3", "-W", "2", "10.0.2.2"], {"env": {"LC_ALL": "C", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}}))

    def test_ping_rejects_loss_bad_counts_missing_summary_and_status(self):
        for text, code in [("3 packets transmitted, 0 received, 100% packet loss", 1), ("3 packets transmitted, 0 received, 100% packet loss", 0), ("3 packets transmitted, 2 received", 0), ("2 packets transmitted, 2 received", 0), ("3 packets transmitted, 3 received", 1), ("0% packet loss", 0), ("3 packets transmitted, 30 received", 0)]:
            with self.subTest(text=text, code=code):
                self.nodes["client2"].reply = (text, "TEST-DOUBLE", code)
                with self.assertRaises(RuntimeError):
                    self.starter.ping_ok(self.nodes["client2"], "10.0.2.2")

    def test_starter_configures_original_base_and_extra_client(self):
        self.starter.main()
        self.starter.Mininet.assert_called_once_with(topo=unittest.mock.ANY, controller=None, autoSetMacs=True)
        for name, interface, address in [("client", "client-eth0", "10.0.1.2/24"), ("client2", "client2-eth0", "10.0.1.3/24"), ("r1", "r1-eth0", "10.0.1.1/24"), ("r1", "r1-eth1", "10.0.12.1/30"), ("r2", "r2-eth0", "10.0.12.2/30"), ("r2", "r2-eth1", "10.0.2.1/24"), ("server", "server-eth0", "10.0.2.2/24")]:
            self.assertIn(("cmd", f"ip addr add {address} dev {interface}"), self.nodes[name].calls)
        for name, command in [("r1", "ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1"), ("r2", "ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0"), ("client", "ip route replace default via 10.0.1.1 dev client-eth0"), ("server", "ip route replace default via 10.0.2.1 dev server-eth0")]:
            self.assertIn(("cmd", command), self.nodes[name].calls)
        self.assertIn(("pexec", ["ip", "route", "replace", "default", "via", "10.0.1.1", "dev", "client2-eth0"], {}), self.nodes["client2"].calls)
        for name, target in [("client", "10.0.2.2"), ("client2", "10.0.2.2"), ("server", "10.0.1.3")]:
            self.assertEqual([call[1][-1] for call in self.nodes[name].calls if call[0] == "pexec" and call[1][0] == "ping"], [target])
        self.starter.CLI.assert_called_once_with(self.net)
        self.net.start.assert_called_once_with()
        self.net.stop.assert_called_once_with()

    def test_cleanup_after_start_ping_or_cli_failure(self):
        for failure in ("start", "ping", "cli", "route"):
            with self.subTest(failure=failure):
                self.net.reset_mock()
                self.starter.CLI.reset_mock()
                self.net.start.side_effect = RuntimeError("TEST-DOUBLE") if failure == "start" else None
                self.starter.CLI.side_effect = RuntimeError("TEST-DOUBLE") if failure == "cli" else None
                self.nodes["client"].reply = ("3 packets transmitted, 0 received", "", 1) if failure == "ping" else ("3 packets transmitted, 3 received", "", 0)
                with patch.object(self.nodes["client2"], "pexec", side_effect=RuntimeError("TEST-DOUBLE") if failure == "route" else self.nodes["client2"].pexec):
                    with self.assertRaises(RuntimeError):
                        self.starter.main()
                self.net.stop.assert_called_once_with()
                if failure != "cli":
                    self.starter.CLI.assert_not_called()

    def test_nonzero_default_route_status_stops_before_cli(self):
        with patch.object(self.nodes["client2"], "pexec", return_value=("", "TEST-DOUBLE route failure", 2)):
            with self.assertRaisesRegex(RuntimeError, "route failure"):
                self.starter.main()
        self.net.stop.assert_called_once_with()
        self.starter.CLI.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
