# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;
# lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.
"""Start: sudo python3 start_lab.py --path A; Hilfe ohne Mininet/Root verfügbar."""

import argparse
import os
import sys
from lab_control import LabControl


def make_cli(base):
    class LabCLI(base):
        def do_path(self, line):
            """path A|B: gemeinsamen Hin-/Rückpfad auswählen (Rollback bei Fehler)."""
            self.action(lambda: self.mn.lab.select_path(line.strip().upper()))

        def do_fault(self, line):
            """fault on|off: r3-Serverroute entfernen bzw. wiederherstellen."""
            value = line.strip().lower()
            if value not in ("on", "off"):
                print("Verwendung: fault on|off")
                return
            self.action(lambda: self.mn.lab.set_fault(value == "on"))

        def do_check(self, line):
            """check: beide Ende-zu-Ende-Pings mit echtem Exitstatus prüfen."""
            self.action(self.mn.lab.ping)

        def do_state(self, line):
            """state: Adressen und Routingtabellen aller Knoten anzeigen."""
            self.action(self.mn.lab.show)

        def action(self, function):
            try:
                function()
            except (RuntimeError, ValueError) as error:
                print(f"FEHLER: {error}")
    return LabCLI


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", choices=("A", "B"), default="A")
    parser.add_argument("--check-only", action="store_true", help="prüfen und ohne CLI beenden")
    args = parser.parse_args(argv)
    try:
        from mininet.net import Mininet
        from mininet.cli import CLI
        from mininet.link import TCLink
        from mininet.log import setLogLevel
        from topology import RoutingTopo
    except ImportError as error:
        print(f"Mininet nicht verfügbar: {error}. Keine Installation durchgeführt.", file=sys.stderr)
        return 2
    if os.geteuid() != 0:
        print("Mininet benötigt root: sudo python3 start_lab.py", file=sys.stderr)
        return 2
    setLogLevel("info")
    net = None
    try:
        net = Mininet(topo=RoutingTopo(), controller=None, link=TCLink, autoSetMacs=True, build=False)
        net.build()
        net.start()
        net.lab = LabControl(net)
        net.lab.configure(args.path)
        net.lab.show()
        net.lab.ping()
        if not args.check_only:
            print("CLI: path A|B, fault on|off, check, state; exit beendet und räumt auf.")
            make_cli(CLI)(net)
        return 0
    except (RuntimeError, OSError) as error:
        print(f"Labor fehlgeschlagen: {error}", file=sys.stderr)
        return 1
    finally:
        if net is not None:
            net.stop()


if __name__ == "__main__":
    sys.exit(main())
