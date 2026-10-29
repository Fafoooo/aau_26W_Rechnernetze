#!/usr/bin/env python3
# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Anfrage: Teste 6.3 mit klar benannten Test-Doubles, auch Fehler und Ping-Zähler.
"""Synthetische Test-Doubles: KEIN Mininet, KEINE echten Pakete oder Routen."""
import unittest
from static_routes import ROUTES, apply, exercise, ping3


class NodeDouble:
    def __init__(self, name, world):
        self.name, self.world = name, world
        self.static, self.forward, self.reply = True, "1\n", None
        self.commands = []

    def pexec(self, argv):
        command = " ".join(argv)
        self.commands.append(command)
        if command == "sysctl -n net.ipv4.ip_forward":
            return self.forward, "", 0
        if command == "ip route":
            return f"TEST-DOUBLE: connected bleibt; explizite Route vorhanden={self.static}\n", "", 0
        if command.startswith("ip route del ") or command.startswith("ip route add "):
            network, gateway, interface, _ = ROUTES[self.name]
            operation = "del" if command.startswith("ip route del ") else "add"
            assert command == f"ip route {operation} {network} via {gateway} dev {interface}"
            if self.static == (operation == "add"):
                return "", "TEST-DOUBLE: Route fehlt oder existiert bereits\n", 2
            self.static = operation == "add"
            return "", "", 0
        if command == f"ip route get {ROUTES.get(self.name, ('', '', '', ''))[3]}":
            return ("TEST-DOUBLE: Weg vorhanden\n", "", 0) if self.static else ("", "TEST-DOUBLE: unreachable\n", 2)
        if command == "env LC_ALL=C ping -n -c 3 -W 1 10.0.2.2":
            count = 3 if all(self.world[name].static for name in ROUTES) else 0
            return self.reply or (f"3 packets transmitted, {count} received\n", "", 0 if count == 3 else 1)
        raise AssertionError(f"Nicht modellierter Befehl: {command}")


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.net = {}
        for name in ("r1", "r2", "client"):
            self.net[name] = NodeDouble(name, self.net)

    def test_complete_exercise(self):
        exercise(self.net)
        self.assertTrue(all(self.net[name].static for name in ROUTES))
        self.assertEqual(len(self.net["client"].commands), 2)

    def test_apply_and_duplicate_delete(self):
        for name in ROUTES:
            apply(self.net[name])
        apply(self.net["r1"], "remove")
        with self.assertRaises(RuntimeError):
            apply(self.net["r1"], "remove")
        apply(self.net["r1"], "restore")

    def test_ping_requires_status_and_exact_counts(self):
        for text, status in [("3 packets transmitted, 0 received, 100% packet loss", 1),
                             ("3 packets transmitted, 2 received", 0),
                             ("3 packets transmitted, 3 received", 1), ("0% packet loss", 0)]:
            self.net["client"].reply = (text, "", status)
            with self.subTest(text=text, status=status), self.assertRaises(RuntimeError):
                ping3(self.net["client"])
        self.net["client"].reply = ("3 packets transmitted, 3 packets received", "", 0)
        self.assertEqual(ping3(self.net["client"]), (3, 3))

    def test_cleanup_and_forwarding_guard(self):
        self.net["client"].reply = ("defekter Testoutput", "", 2)
        with self.assertRaises(RuntimeError):
            exercise(self.net)
        self.assertTrue(all(self.net[name].static for name in ROUTES))
        self.net["r1"].forward = "0\n"
        with self.assertRaises(RuntimeError):
            exercise(self.net)
        with self.assertRaises(ValueError):
            apply(self.net["client"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
