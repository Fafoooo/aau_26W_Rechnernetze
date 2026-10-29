#!/usr/bin/env python3
# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.
# Anfrage: Vollständige Lösungen zu Ü4.1, Ü4.2, Ü4.5 mit ausführbarer,
# read-only Hostdiagnose, echten Selbsttests und zeilenweiser Erklärung erstellen;
# Quellen beachten, Mininet nicht installieren und Hostdaten nicht als Mininet ausgeben.
"""Nur lesende lokale Diagnose; identische Kopie in den drei Aufgabenordnern."""

import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import unittest
from unittest import mock


def commands(exercise):
    """Eine feste Argumentliste je Befehl, niemals Shell-Interpolation."""
    result = [
        ["ip", "addr"],
        ["ip", "route"],
        ["hostname"],
        [sys.executable, "--version"],
        ["pwd"],
        ["printenv", "PATH"],
        ["ip", "-details", "link", "show"],
    ]
    if exercise == "ue4.5":
        result.extend([
            ["ip", "-4", "route", "get", "10.0.2.2"],
            ["ip", "-4", "route", "get", "10.0.1.2"],
            ["ip", "neigh", "show"],
            ["sysctl", "net.ipv4.ip_forward", "net.ipv4.conf.all.forwarding",
             "net.ipv4.conf.default.forwarding"],
            ["sysctl", "net.ipv4.conf.router-eth0.forwarding",
             "net.ipv4.conf.router-eth1.forwarding"],
            ["tc", "-s", "qdisc", "show"],
        ])
    return result


def text(value):
    """Auch partielle Timeout-Ausgaben können bytes statt str sein."""
    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")


def run_command(argv):
    """Prozess begrenzen; Fehler und beide Ausgabekanäle erhalten."""
    try:
        process = subprocess.run(argv, capture_output=True, text=True, check=False,
                                 timeout=5, shell=False)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except FileNotFoundError as error:
        code, stdout, stderr = 127, "", str(error)
    except PermissionError as error:
        code, stdout, stderr = 126, "", str(error)
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr = 124, text(error.stdout), text(error.stderr) + "\nTIMEOUT"
    return {"argv": list(argv), "display": shlex.join(argv), "returncode": code,
            "stdout": text(stdout), "stderr": text(stderr)}


def namespace_ids():
    """Namespace-IDs belegen die Umgebung, nicht den behaupteten Hostnamen."""
    result = {}
    for name in ("net", "uts", "pid", "mnt"):
        try:
            result[name] = os.readlink(f"/proc/self/ns/{name}")
        except OSError as error:
            result[name] = f"nicht lesbar: {error}"
    return result


def collect(exercise, label):
    """Keine erwarteten IPs als Messwerte einsetzen und keine Pakete versenden."""
    return {
        "exercise": exercise,
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "context_label": label,
        "provenance": "Live-Diagnose im aktuellen Prozesskontext; Label ist kein Mininetbeweis.",
        "namespaces": namespace_ids(),
        "cwd": os.getcwd(),
        "availability": {name: shutil.which(name) for name in ("mn", "xterm", "ovs-vsctl", "tc")},
        "mininet_module_available": importlib.util.find_spec("mininet") is not None,
        "commands": [run_command(argv) for argv in commands(exercise)],
    }


def save_report(filename, report):
    """Nur neue Dateien direkt neben diesem Programm, nie vorhandene ersetzen."""
    if not filename or Path(filename).name != filename or filename in (".", ".."):
        raise ValueError("--output muss ein einfacher Dateiname ohne Verzeichnis sein")
    target = Path(__file__).resolve().parent / filename
    with target.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return target


class DiagnosisTests(unittest.TestCase):
    """Mocks prüfen Prozessargumente; sie sind keine Netzwerkmessungen."""

    def test_base_arguments(self):
        expected = [["ip", "addr"], ["ip", "route"], ["hostname"],
                    [sys.executable, "--version"], ["pwd"], ["printenv", "PATH"],
                    ["ip", "-details", "link", "show"]]
        self.assertEqual(commands("ue4.1"), expected)
        self.assertEqual(commands("ue4.2"), expected)

    def test_routing_arguments(self):
        expected = [
            ["ip", "-4", "route", "get", "10.0.2.2"],
            ["ip", "-4", "route", "get", "10.0.1.2"],
            ["ip", "neigh", "show"],
            ["sysctl", "net.ipv4.ip_forward", "net.ipv4.conf.all.forwarding",
             "net.ipv4.conf.default.forwarding"],
            ["sysctl", "net.ipv4.conf.router-eth0.forwarding",
             "net.ipv4.conf.router-eth1.forwarding"],
            ["tc", "-s", "qdisc", "show"],
        ]
        self.assertEqual(commands("ue4.5"), commands("ue4.1") + expected)

    def test_every_subprocess_argument(self):
        for exercise in ("ue4.1", "ue4.2", "ue4.5"):
            for argv in commands(exercise):
                with self.subTest(exercise=exercise, argv=argv):
                    with mock.patch("subprocess.run") as run:
                        run.return_value = subprocess.CompletedProcess(argv, 0, "ok\n", "")
                        result = run_command(argv)
                        run.assert_called_once_with(argv, capture_output=True, text=True,
                                                    check=False, timeout=5, shell=False)
                        self.assertEqual(result["argv"], argv)
                        self.assertEqual(result["stdout"], "ok\n")
                        self.assertEqual(result["returncode"], 0)

    def test_missing_and_denied(self):
        for error, code in ((FileNotFoundError("missing"), 127),
                            (PermissionError("denied"), 126)):
            with mock.patch("subprocess.run", side_effect=error):
                result = run_command(["ip", "addr"])
                self.assertEqual(result["returncode"], code)
                self.assertTrue(result["stderr"])

    def test_timeout_preserves_bytes(self):
        error = subprocess.TimeoutExpired(["ip", "addr"], 5, output=b"partial", stderr=b"err")
        with mock.patch("subprocess.run", side_effect=error):
            result = run_command(["ip", "addr"])
        self.assertEqual(result["returncode"], 124)
        self.assertEqual(result["stdout"], "partial")
        self.assertIn("TIMEOUT", result["stderr"])
        json.dumps(result)

    def test_nonzero_is_preserved(self):
        with mock.patch("subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(["ip"], 2, "", "error")
            result = run_command(["ip"])
        self.assertEqual(result["returncode"], 2)
        self.assertEqual(result["stderr"], "error")

    def test_report_restricts_path_and_uses_exclusive_open(self):
        for name in ("", "../outside.json", "/outside.json", ".", ".."):
            with self.assertRaises(ValueError):
                save_report(name, {})
        with mock.patch.object(Path, "open", mock.mock_open()) as opened:
            save_report("test.json", {"test": True})
            opened.assert_called_once_with("x", encoding="utf-8")
            self.assertIn('"test": true', opened().write.call_args.args[0])
        with mock.patch.object(Path, "open", side_effect=FileExistsError("exists")):
            with self.assertRaises(FileExistsError):
                save_report("test.json", {})

    def test_context_does_not_certify_mininet(self):
        with mock.patch(__name__ + ".run_command", return_value={"returncode": 0}):
            report = collect("ue4.1", "h1 (nur Label)")
        self.assertEqual(report["context_label"], "h1 (nur Label)")
        self.assertIn("kein Mininetbeweis", report["provenance"])
        self.assertEqual(set(report["namespaces"]), {"net", "uts", "pid", "mnt"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="nur stdlib-unittest ausführen")
    parser.add_argument("--context", default="lokaler Host; kein Mininetnachweis")
    parser.add_argument("--output", help="neue JSON-Datei im Aufgabenordner (kein Überschreiben)")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiagnosisTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    exercise = Path(__file__).resolve().parent.name
    if exercise not in ("ue4.1", "ue4.2", "ue4.5"):
        parser.error("Programm muss in ue4.1, ue4.2 oder ue4.5 liegen")
    report = collect(exercise, args.context)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        try:
            print(f"Gespeichert: {save_report(args.output, report)}", file=sys.stderr)
        except (ValueError, OSError) as error:
            parser.exit(2, f"Bericht nicht gespeichert: {error}\n")
    return 1 if any(item["returncode"] != 0 for item in report["commands"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
