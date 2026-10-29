# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: Fünf Offline-CLIs sowie Mininet-Routermodell und Cleanup mit ausdrücklich synthetischen Testdoubles prüfen.
"""Keine Mininet-Messung: Mocktests ergänzen die realen PCAP-Tests."""
import importlib.util
import ipaddress
import json
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from auswertung import report

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rn08lab", BASE / "ue8.4/lab.py")
assert spec is not None and spec.loader is not None
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def fake_net():
    net, nodes = MagicMock(), {}
    def add(name, **kwargs):
        node = MagicMock()
        node.name = name
        node.pexec.return_value = ("", "", 0)
        nodes[name] = node
        return node
    net.addHost.side_effect = add
    net.addSwitch.side_effect = add
    net.__getitem__.side_effect = nodes.__getitem__
    return net, nodes


class Tests(unittest.TestCase):
    def test_five_real_offline_clis(self):
        for part in range(1, 6):
            result = subprocess.run([sys.executable, "-B", str(BASE / f"ue8.{part}/auswerten.py")], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), report(f"8.{part}", BASE / "nachweise/run01"))
            help_result = subprocess.run([sys.executable, "-B", str(BASE / f"ue8.{part}/auswerten.py"), "--help"], capture_output=True, text=True, timeout=5)
            self.assertEqual(help_result.returncode, 0)
            self.assertIn("--belege", help_result.stdout)

    def test_address_plan(self):
        networks = {ipaddress.ip_interface(ip).network for _, ip, _, _ in lab.ROUTER}
        self.assertEqual(len(networks), 2)
        self.assertEqual(len({mac for _, mac, _, _ in lab.HOSTS.values()}), 4)
        for ip, _, switch, gateway in lab.HOSTS.values():
            own = ipaddress.ip_interface(ip)
            matching = [ipaddress.ip_interface(rip) for _, rip, _, rswitch in lab.ROUTER if rswitch == switch]
            self.assertEqual(len(matching), 1)
            self.assertEqual(own.network, matching[0].network)
            self.assertEqual(ipaddress.ip_address(gateway), matching[0].ip)
            self.assertNotEqual(own.ip, matching[0].ip)

    def test_successful_model_and_routes(self):
        net, nodes = fake_net()
        cli = MagicMock()
        with patch("builtins.print"):
            lab.run(net, cli)
        net.build.assert_called_once_with()
        net.start.assert_called_once_with()
        net.stop.assert_called_once_with()
        cli.assert_called_once_with(net)
        self.assertEqual(net.addLink.call_count, 6)
        for name, (ip, mac, _, gateway) in lab.HOSTS.items():
            calls = nodes[name].pexec
            calls.assert_any_call("ip", "addr", "add", ip, "dev", name + "-eth0")
            calls.assert_any_call("ip", "link", "set", name + "-eth0", "address", mac)
            calls.assert_any_call("ip", "route", "replace", "default", "via", gateway)
        nodes["router"].pexec.assert_any_call("sysctl", "-w", "net.ipv4.ip_forward=1")
        for interface, ip, mac, _ in lab.ROUTER:
            nodes["router"].pexec.assert_any_call("ip", "addr", "add", ip, "dev", interface)
            nodes["router"].pexec.assert_any_call("ip", "link", "set", interface, "address", mac)

    def test_failure_cleanup(self):
        for stage in ("addHost", "addLink", "build", "start", "configure", "cli"):
            net, nodes = fake_net()
            cli = MagicMock()
            if stage == "configure":
                original = net.addHost.side_effect
                def failing(name, **kwargs):
                    node = original(name, **kwargs)
                    node.pexec.return_value = ("", "synthetic failure", 1)
                    return node
                net.addHost.side_effect = failing
            elif stage == "cli":
                cli.side_effect = RuntimeError("synthetic CLI failure")
            else:
                getattr(net, stage).side_effect = RuntimeError("synthetic setup failure")
            with patch("builtins.print"), self.assertRaises(RuntimeError):
                lab.run(net, cli)
            net.stop.assert_called_once_with()
            if stage != "cli":
                cli.assert_not_called()
            if stage == "build":
                net.start.assert_not_called()

    def test_constructor_is_deferred(self):
        modules = {name: types.ModuleType(name) for name in ("mininet", "mininet.cli", "mininet.net", "mininet.node")}
        setattr(modules["mininet.cli"], "CLI", MagicMock())
        setattr(modules["mininet.node"], "OVSSwitch", object())
        constructor = MagicMock()
        setattr(modules["mininet.net"], "Mininet", constructor)
        with patch.dict(sys.modules, modules), patch.object(lab.os, "geteuid", return_value=0), patch.object(lab, "run") as runner:
            lab.main()
        self.assertEqual(constructor.call_args.kwargs, dict(controller=None, switch=getattr(modules["mininet.node"], "OVSSwitch"), build=False, autoSetMacs=False))
        runner.assert_called_once_with(constructor.return_value, getattr(modules["mininet.cli"], "CLI"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
