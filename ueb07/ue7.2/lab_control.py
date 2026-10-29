# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;
# lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.
"""Geprüfte Befehle und serialisierte Pfadtransaktionen; kein Mininet-Import nötig."""

import threading
from lab_config import DEFAULT_ROUTES, LINKS, NODES, PATH_ROUTES, R3_ROUTES, ROUTERS


def checked(node, *args):
    """Mininet.pexec liefert stdout, stderr, echten Exitstatus (kein Textvergleich)."""
    try:
        out, err, status = node.pexec(*args)
    except OSError as error:
        raise RuntimeError(f"{node.name}: {args!r}: Prozessstart fehlgeschlagen: {error}") from error
    if status != 0:
        raise RuntimeError(f"{node.name}: {args!r}: exit={status}\n{out}{err}")
    return out


def route_args(route, operation="replace"):
    _, prefix, gateway, interface = route
    return ("ip", "route", operation, prefix, "via", gateway, "dev", interface)


class LabControl:
    def __init__(self, net):
        self.net = net
        self.path = None
        self.fault = False
        self.lock = threading.RLock()

    def configure(self, path="A"):
        if path not in PATH_ROUTES:
            raise ValueError("Pfad muss A oder B sein")
        for left, right, il, ir, al, ar, _ in LINKS:
            for name, interface, address in ((left, il, al), (right, ir, ar)):
                node = self.net[name]
                checked(node, "ip", "addr", "flush", "dev", interface)
                checked(node, "ip", "addr", "add", address, "dev", interface)
                checked(node, "ip", "link", "set", interface, "up")
        for name in ROUTERS:
            checked(self.net[name], "sysctl", "-w", "net.ipv4.ip_forward=1")
        for name, gateway, interface in DEFAULT_ROUTES:
            checked(self.net[name], "ip", "route", "replace", "default",
                    "via", gateway, "dev", interface)
        for route in R3_ROUTES:
            checked(self.net[route[0]], *route_args(route))
        self.fault = False
        self.select_path(path)

    def select_path(self, path):
        """Zwei Router haben keine gemeinsame Kernel-Transaktion: bei Fehler zurückrollen."""
        if path not in PATH_ROUTES:
            raise ValueError("Pfad muss A oder B sein")
        with self.lock:
            previous = self.path
            changed = []
            try:
                for index, route in enumerate(PATH_ROUTES[path]):
                    checked(self.net[route[0]], *route_args(route))
                    changed.append(index)
            except RuntimeError as error:
                failures = []
                for index in reversed(changed):
                    route = PATH_ROUTES[previous][index] if previous else PATH_ROUTES[path][index]
                    operation = "replace" if previous else "del"
                    try:
                        checked(self.net[route[0]], *route_args(route, operation))
                    except RuntimeError as rollback_error:
                        failures.append(str(rollback_error))
                if failures:
                    self.path = None
                    raise RuntimeError(f"Pfadstatus unbekannt; Rollback fehlgeschlagen: {failures}") from error
                raise
            self.path = path

    def set_fault(self, enabled):
        """Nur r3s Serverroute löschen/wiederherstellen, nicht dessen Client-Rückroute."""
        with self.lock:
            if enabled == self.fault:
                return
            route = R3_ROUTES[0]
            checked(self.net["r3"], *route_args(route, "del" if enabled else "replace"))
            self.fault = enabled

    def ping(self, count=3):
        if not isinstance(count, int) or count < 1:
            raise ValueError("Ping-Anzahl muss eine positive Ganzzahl sein")
        with self.lock:
            for source, target in (("client", "10.0.2.2"), ("server", "10.0.1.2")):
                out = checked(self.net[source], "ping", "-n", "-c", str(count),
                              "-W", "2", "-w", str(count * 3 + 2), target)
                print(f"[{source} -> {target}]\n{out}", end="")

    def show(self):
        print(f"Pfad={self.path}, r3-Serverroute fehlt={self.fault}")
        for name in NODES:
            print(f"\n--- {name}: Adressen / Routen ---")
            print(checked(self.net[name], "ip", "-br", "addr"), end="")
            print(checked(self.net[name], "ip", "route", "show"), end="")
