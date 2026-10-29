# ue4.5 – Erklärung aller eigenen Codezeilen

## Zweck, Bedienung und fachliche Grenzen

`diagnose.py` ist die einzige eigene, dauerhaft abgelegte Python-Datei dieses Aufgabenordners. Die drei Kopien in ue4.1, ue4.2 und ue4.5 sind identisch. Der Ordnername wählt den Plan: ue4.1/ue4.2 verwenden den gemeinsamen Plan, ue4.5 zusätzlich die Routingdiagnosen. Der Abschnitt unten erklärt **jede nichtleere Zeile** einschließlich Kommentare, Docstrings und Klammerfortsetzungen mit ihrer tatsächlichen Zeilennummer; Leerzeilen haben keine Programmwirkung.

Ablauf: `main()` liest Optionen → entweder unittest oder `collect()` → feste lesende Befehlsliste → jeder Befehl über `run_command()` → JSON auf stdout, optional neue Datei. Kein Namespace wird betreten/erzeugt, kein Netzinterface verändert. Der Prozess untersucht ausschließlich den bereits geerbten Netzwerk-Namespace. Ein Kontextlabel ist niemals ein Beweis. Erwartete Laboradressen stehen nicht als Messwerte im Code; die beiden 10.0.x.x-Adressen in ue4.5 sind nur Route-Lookup-Ziele.

`--self-test` führt acht stdlib-unittest-Testmethoden aus. Die Mocks liefern absichtlich künstliche **Testfixtures**, keine Messergebnisse. Der getrennte normale Lauf verwendet echte Subprocess-Ausgaben. Alle Aufrufe erhalten Argumentlisten, `shell=False`, `check=False`, `capture_output=True`, `text=True` und fünf Sekunden Timeout. Fehler bleiben sichtbar: 127 fehlender Befehl, 126 Berechtigungsfehler, 124 Timeout oder der echte sonstige Prozesscode. Der Skriptexitcode ist 1, wenn mindestens ein Befehl fehlschlägt, sonst 0; Argument-/Speicherfehler ergeben 2.

`--output neuer-name.json` schreibt ausschließlich eine neue Datei neben dem Skript; vorhandene Dateien und Symlinks werden mit Modus x nicht überschrieben. Das ist die einzige optionale Nutzdatenänderung; die Diagnosebefehle selbst sind read-only und erfordern weder sudo noch Netzpakete. Das Arbeitsverzeichnis bleibt geerbt. net-/uts-/pid-/mnt-IDs werden direkt über `/proc/self/ns/` gelesen.

## Zeilentabelle zu diagnose.py

| Zeile | Tatsächlicher Quelltext (ohne Einrückung) | Erklärung |
|---|---|---|
| 1 | `#!/usr/bin/env python3` | Shebang: Beim direkten Start wählt env das python3 aus PATH. |
| 2 | `# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29.` | KI-Werkzeug, Anbieter/Modell und tatsächliches Erstellungsdatum offenlegen. |
| 3 | `# Anfrage: Vollständige Lösungen zu Ü4.1, Ü4.2, Ü4.5 mit ausführbarer,` | Den tatsächlichen Auftrag zusammenfassen: vollständige Lösungen, read-only Diagnose, echte Tests, Quellen und ehrliche Herkunft; Kommentare führen nichts aus. |
| 4 | `# read-only Hostdiagnose, echten Selbsttests und zeilenweiser Erklärung erstellen;` | Den tatsächlichen Auftrag zusammenfassen: vollständige Lösungen, read-only Diagnose, echte Tests, Quellen und ehrliche Herkunft; Kommentare führen nichts aus. |
| 5 | `# Quellen beachten, Mininet nicht installieren und Hostdaten nicht als Mininet ausgeben.` | Den tatsächlichen Auftrag zusammenfassen: vollständige Lösungen, read-only Diagnose, echte Tests, Quellen und ehrliche Herkunft; Kommentare führen nichts aus. |
| 6 | `"""Nur lesende lokale Diagnose; identische Kopie in den drei Aufgabenordnern."""` | Moduldocstring: Aufgabe und identische Nutzung in drei Verzeichnissen; erscheint auch in der Hilfe. |
| 8 | `import argparse` | argparse verarbeitet die Kommandozeilenoptionen und meldet ungültige Argumente. |
| 9 | `import datetime` | datetime erzeugt den echten UTC-Zeitstempel für den Laufbericht. |
| 10 | `import importlib.util` | importlib.util.find_spec prüft die Auffindbarkeit des Mininetmoduls, ohne Mininet zu importieren. |
| 11 | `import json` | json serialisiert den Bericht einschließlich Unicode in ein standardisiertes Textformat. |
| 12 | `import os` | os stellt aktuelles Arbeitsverzeichnis und Lesen der Namespace-Symlinks bereit. |
| 13 | `from pathlib import Path` | Path kapselt Dateipfade, den Skriptort und das sichere Öffnen einer neuen Datei. |
| 14 | `import shlex` | shlex.join formatiert nur eine lesbare Befehlsdarstellung; diese Darstellung wird nicht als Shellkommando ausgeführt. |
| 15 | `import shutil` | shutil.which sucht die tatsächlich verfügbaren Labortools im aktuellen PATH. |
| 16 | `import subprocess` | subprocess startet lokale Befehle und liefert Exitcode sowie stdout/stderr. |
| 17 | `import sys` | sys liefert den laufenden Pythoninterpreter, stderr und Programmbeendigung. |
| 18 | `import unittest` | unittest stellt die Standardbibliotheks-Testsuite und Zusicherungen bereit. |
| 19 | `from unittest import mock` | mock ersetzt Prozesse/Dateiöffnungen nur innerhalb von Tests durch kontrollierte Testobjekte. |
| 22 | `def commands(exercise):` | Definiert den Befehlsplan; exercise entscheidet nur über zusätzliche Routingdiagnosen. |
| 23 | `"""Eine feste Argumentliste je Befehl, niemals Shell-Interpolation."""` | Funktionsdocstring erklärt, warum jedes Argument ein eigenes Listenelement ist. |
| 24 | `result = [` | Beginnt die Liste der auf allen drei Aufgaben verwendeten lesenden Befehle. |
| 25 | `["ip", "addr"],` | ip addr liest Interfaces und IP-Adressen des aktuellen Netzwerk-Namespace. |
| 26 | `["ip", "route"],` | ip route liest die IPv4-Hauptroutingtabelle des aktuellen Netzwerk-Namespace. |
| 27 | `["hostname"],` | hostname liest den UTS-Hostnamen; keine Änderung und kein Mininet-Knotennachweis. |
| 28 | `[sys.executable, "--version"],` | Fragt die Version genau des Interpreters ab, der dieses Programm ausführt. |
| 29 | `["pwd"],` | pwd als externer Befehl liest das geerbte Arbeitsverzeichnis. |
| 30 | `["printenv", "PATH"],` | printenv PATH liest die tatsächlichen Suchverzeichnisse, ohne $PATH durch eine Shell expandieren zu lassen. |
| 31 | `["ip", "-details", "link", "show"],` | Detaillierte Linkanzeige liefert zum Beispiel die veth-Interfaceart. |
| 32 | `]` | Schließt die gemeinsame Befehlsliste; erzeugt noch keinen Prozess. |
| 33 | `if exercise == "ue4.5":` | Nur ue4.5 erhält die folgenden Routing-/Forwarding-/qdisc-Abfragen. |
| 34 | `result.extend([` | extend hängt mehrere weitere Argumentlisten an den Plan an. |
| 35 | `["ip", "-4", "route", "get", "10.0.2.2"],` | Route zum Serverziel 10.0.2.2 lokal nachschlagen; keine Pakete versenden. |
| 36 | `["ip", "-4", "route", "get", "10.0.1.2"],` | Route zum Clientziel 10.0.1.2 lokal nachschlagen; keine Pakete versenden. |
| 37 | `["ip", "neigh", "show"],` | Liest die bestehende Nachbartabelle, ohne aktiv ARP-Anfragen auszulösen. |
| 38 | `["sysctl", "net.ipv4.ip_forward", "net.ipv4.conf.all.forwarding",` | Ein sysctl-Aufruf liest globales IPv4-Forwarding, all.forwarding und default.forwarding; kein -w und keine Zuweisung. |
| 39 | `"net.ipv4.conf.default.forwarding"],` | Ein sysctl-Aufruf liest globales IPv4-Forwarding, all.forwarding und default.forwarding; kein -w und keine Zuweisung. |
| 40 | `["sysctl", "net.ipv4.conf.router-eth0.forwarding",` | Ein weiterer sysctl-Aufruf liest beide tatsächlichen Routerinterface-Forwardingwerte; fehlende Interfaces erzeugen dokumentierte Fehler. |
| 41 | `"net.ipv4.conf.router-eth1.forwarding"],` | Ein weiterer sysctl-Aufruf liest beide tatsächlichen Routerinterface-Forwardingwerte; fehlende Interfaces erzeugen dokumentierte Fehler. |
| 42 | `["tc", "-s", "qdisc", "show"],` | tc zeigt qdiscs mit Statistiken; show liest, statt Delay oder Regeln zu ändern. |
| 43 | `])` | Schließt Liste und extend-Aufruf. |
| 44 | `return result` | Gibt den vollständigen Befehlsplan an den Aufrufer zurück. |
| 47 | `def text(value):` | Definiert eine Hilfsfunktion zur sicheren Umwandlung partieller Ausgaben in Text. |
| 48 | `"""Auch partielle Timeout-Ausgaben können bytes statt str sein."""` | Docstring erläutert den bytes-Sonderfall bei Subprocess-Timeouts. |
| 49 | `return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")` | bytes mit Ersatzzeichen decodieren; Text unverändert zurückgeben; None bzw. leerer Inhalt wird leerer String. |
| 52 | `def run_command(argv):` | Definiert die Ausführung genau einer bereits getrennten Argumentliste. |
| 53 | `"""Prozess begrenzen; Fehler und beide Ausgabekanäle erhalten."""` | Docstring: Jeder Prozess ist zeitlich begrenzt; stdout und stderr bleiben getrennt erhalten. |
| 54 | `try:` | Beginn des Blocks, dessen erwartete Betriebssystem-/Timeoutfehler abgefangen werden. |
| 55 | `process = subprocess.run(argv, capture_output=True, text=True, check=False,` | subprocess.run bekommt die unveränderte Argumentliste; capture_output erfasst beide Kanäle, text liefert Text, check=False erhält Fehlercodes, timeout=5 begrenzt Sekunden, shell=False verhindert Shellauswertung. |
| 56 | `timeout=5, shell=False)` | subprocess.run bekommt die unveränderte Argumentliste; capture_output erfasst beide Kanäle, text liefert Text, check=False erhält Fehlercodes, timeout=5 begrenzt Sekunden, shell=False verhindert Shellauswertung. |
| 57 | `code, stdout, stderr = process.returncode, process.stdout, process.stderr` | Übernimmt echten Exitcode, stdout und stderr des fertig gelaufenen Prozesses. |
| 58 | `except FileNotFoundError as error:` | Fehlendes ausführbares Programm: protokolliert Code 127, leeres stdout und die echte Ausnahmebeschreibung. |
| 59 | `code, stdout, stderr = 127, "", str(error)` | Fehlendes ausführbares Programm: protokolliert Code 127, leeres stdout und die echte Ausnahmebeschreibung. |
| 60 | `except PermissionError as error:` | Berechtigungsfehler: protokolliert Code 126 und die echte Ausnahmebeschreibung. |
| 61 | `code, stdout, stderr = 126, "", str(error)` | Berechtigungsfehler: protokolliert Code 126 und die echte Ausnahmebeschreibung. |
| 62 | `except subprocess.TimeoutExpired as error:` | Timeout: protokolliert Code 124, erhält partielles stdout/stderr und ergänzt eine TIMEOUT-Markierung. |
| 63 | `code, stdout, stderr = 124, text(error.stdout), text(error.stderr) + "\nTIMEOUT"` | Timeout: protokolliert Code 124, erhält partielles stdout/stderr und ergänzt eine TIMEOUT-Markierung. |
| 64 | `return {"argv": list(argv), "display": shlex.join(argv), "returncode": code,` | Gibt einen JSON-tauglichen Datensatz mit tatsächlichen Argumenten, nur zur Anzeige gequotetem Befehl und normalisierten Ausgaben zurück. |
| 65 | `"stdout": text(stdout), "stderr": text(stderr)}` | Gibt einen JSON-tauglichen Datensatz mit tatsächlichen Argumenten, nur zur Anzeige gequotetem Befehl und normalisierten Ausgaben zurück. |
| 68 | `def namespace_ids():` | Definiert die Erfassung der vier Namespace-IDs des aktuellen Diagnoseprozesses. |
| 69 | `"""Namespace-IDs belegen die Umgebung, nicht den behaupteten Hostnamen."""` | Docstring warnt, dass ein Name/Label den gemessenen Namespace nicht ersetzt. |
| 70 | `result = {}` | Beginnt ein leeres Wörterbuch für die IDs. |
| 71 | `for name in ("net", "uts", "pid", "mnt"):` | Durchläuft Netzwerk-, UTS-, PID- und Mount-Namespace einzeln. |
| 72 | `try:` | Fängt auch fehlendes oder gesperrtes procfs ab. |
| 73 | `result[name] = os.readlink(f"/proc/self/ns/{name}")` | Liest das Symlinkziel /proc/self/ns/<Typ>; self ist hier der Pythonprozess selbst. |
| 74 | `except OSError as error:` | Bei OSError die konkrete Ausnahme als lesbaren Befund speichern, keine ID erfinden. |
| 75 | `result[name] = f"nicht lesbar: {error}"` | Bei OSError die konkrete Ausnahme als lesbaren Befund speichern, keine ID erfinden. |
| 76 | `return result` | Gibt die tatsächlich gelesenen IDs oder Fehlermeldungen zurück. |
| 79 | `def collect(exercise, label):` | Definiert den vollständigen Laufbericht mit Aufgabenbezeichnung und freiwilligem Kontextlabel. |
| 80 | `"""Keine erwarteten IPs als Messwerte einsetzen und keine Pakete versenden."""` | Docstring trennt erwartete Konfiguration und Messung und schließt aktive Netzproben aus. |
| 81 | `return {` | Beginnt das als Bericht zurückgegebene Wörterbuch. |
| 82 | `"exercise": exercise,` | Speichert die vom Skriptordner bestimmte Aufgabenkennung. |
| 83 | `"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),` | Erfasst die aktuelle UTC-Uhrzeit mit Zeitzone im ISO-8601-Format. |
| 84 | `"context_label": label,` | Bewahrt das Benutzerlabel unverändert; es bestimmt keinen Namespace. |
| 85 | `"provenance": "Live-Diagnose im aktuellen Prozesskontext; Label ist kein Mininetbeweis.",` | Expliziter Herkunftshinweis verhindert die Gleichsetzung eines h1-Labels mit Mininetmessungen. |
| 86 | `"namespaces": namespace_ids(),` | Ergänzt die separat gemessenen vier Namespace-IDs. |
| 87 | `"cwd": os.getcwd(),` | Ergänzt das tatsächliche aktuelle Arbeitsverzeichnis des Diagnoseprozesses. |
| 88 | `"availability": {name: shutil.which(name) for name in ("mn", "xterm", "ovs-vsctl", "tc")},` | Dictionary-Comprehension: je Labortool den gefundenen Pfad oder None speichern; nichts installieren. |
| 89 | `"mininet_module_available": importlib.util.find_spec("mininet") is not None,` | Speichert einen booleschen Auffindbarkeitsbefund für das Pythonmodul mininet. |
| 90 | `"commands": [run_command(argv) for argv in commands(exercise)],` | List-Comprehension führt alle geplanten Befehle aus; jeder wird durch run_command einzeln begrenzt und dokumentiert. |
| 91 | `}` | Schließt das Berichtswörterbuch. |
| 94 | `def save_report(filename, report):` | Definiert optionales Speichern eines vorhandenen Berichts. |
| 95 | `"""Nur neue Dateien direkt neben diesem Programm, nie vorhandene ersetzen."""` | Docstring erklärt die Beschränkung auf neue Dateien im Aufgabenordner. |
| 96 | `if not filename or Path(filename).name != filename or filename in (".", ".."):` | Leere Namen, Verzeichnispfade sowie . und .. ablehnen; Fehler ausdrücklich als ValueError signalisieren. |
| 97 | `raise ValueError("--output muss ein einfacher Dateiname ohne Verzeichnis sein")` | Leere Namen, Verzeichnispfade sowie . und .. ablehnen; Fehler ausdrücklich als ValueError signalisieren. |
| 98 | `target = Path(__file__).resolve().parent / filename` | Ermittelt den wirklichen Skriptordner und hängt nur den validierten einfachen Dateinamen an. |
| 99 | `with target.open("x", encoding="utf-8") as handle:` | Öffnet mit x exklusiv neu und mit UTF-8; eine bestehende Datei oder ein vorhandener Symlink kann nicht überschrieben werden; with schließt das Handle. |
| 100 | `handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")` | Schreibt eingerücktes Unicode-JSON mit abschließendem Zeilenumbruch. |
| 101 | `return target` | Gibt den tatsächlich verwendeten Zielpfad zurück. |
| 104 | `class DiagnosisTests(unittest.TestCase):` | Definiert eine unittest-Testklasse; test_-Methoden werden automatisch entdeckt. |
| 105 | `"""Mocks prüfen Prozessargumente; sie sind keine Netzwerkmessungen."""` | Docstring kennzeichnet Mock-Ausgaben als Testdaten, nicht als reale Netzwerkausgaben. |
| 107 | `def test_base_arguments(self):` | Beginnt den Test der vollständigen gemeinsamen Befehlsargumente. |
| 108 | `expected = [["ip", "addr"], ["ip", "route"], ["hostname"],` | Unabhängig ausgeschriebene Sollargumente für Interfaces, Routen, UTS, Python, cwd, PATH und Linkdetails. |
| 109 | `[sys.executable, "--version"], ["pwd"], ["printenv", "PATH"],` | Unabhängig ausgeschriebene Sollargumente für Interfaces, Routen, UTS, Python, cwd, PATH und Linkdetails. |
| 110 | `["ip", "-details", "link", "show"]]` | Unabhängig ausgeschriebene Sollargumente für Interfaces, Routen, UTS, Python, cwd, PATH und Linkdetails. |
| 111 | `self.assertEqual(commands("ue4.1"), expected)` | Vergleicht den kompletten Plan für ue4.1 mit der Sollargumentliste. |
| 112 | `self.assertEqual(commands("ue4.2"), expected)` | Prüft separat den kompletten gemeinsamen Plan für ue4.2. |
| 114 | `def test_routing_arguments(self):` | Beginnt den Test der zusätzlich erwarteten Routingbefehle. |
| 115 | `expected = [` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 116 | `["ip", "-4", "route", "get", "10.0.2.2"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 117 | `["ip", "-4", "route", "get", "10.0.1.2"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 118 | `["ip", "neigh", "show"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 119 | `["sysctl", "net.ipv4.ip_forward", "net.ipv4.conf.all.forwarding",` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 120 | `"net.ipv4.conf.default.forwarding"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 121 | `["sysctl", "net.ipv4.conf.router-eth0.forwarding",` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 122 | `"net.ipv4.conf.router-eth1.forwarding"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 123 | `["tc", "-s", "qdisc", "show"],` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 124 | `]` | Schreibt alle zusätzlichen Sollargumente unabhängig aus: zwei Route-Lookups, Nachbartabelle, globale und beide Interface-Forwardingwerte sowie qdisc-Anzeige. |
| 125 | `self.assertEqual(commands("ue4.5"), commands("ue4.1") + expected)` | Prüft, dass ue4.5 genau aus gemeinsamem Plan plus diesen Zusätzen besteht, ohne fehlende oder zusätzliche Befehle. |
| 127 | `def test_every_subprocess_argument(self):` | Beginnt den Test jedes tatsächlich an subprocess.run übergebenen Aufrufs. |
| 128 | `for exercise in ("ue4.1", "ue4.2", "ue4.5"):` | Durchläuft alle Aufgaben und alle Argumentlisten, nicht nur ein einzelnes Beispiel. |
| 129 | `for argv in commands(exercise):` | Durchläuft alle Aufgaben und alle Argumentlisten, nicht nur ein einzelnes Beispiel. |
| 130 | `with self.subTest(exercise=exercise, argv=argv):` | subTest nennt Aufgabe und Argumente, damit ein Fehlschlag genau zuordenbar ist. |
| 131 | `with mock.patch("subprocess.run") as run:` | Ersetzt subprocess.run nur innerhalb dieses Testblocks durch einen Mock; kein echter Befehl läuft hier. |
| 132 | `run.return_value = subprocess.CompletedProcess(argv, 0, "ok\n", "")` | Konstruierter CompletedProcess ist explizites Testfixture mit Exitcode 0 und kontrolliertem stdout. |
| 133 | `result = run_command(argv)` | Ruft die echte Wrapperfunktion gegen den Mock auf. |
| 134 | `run.assert_called_once_with(argv, capture_output=True, text=True,` | Verlangt genau einen Aufruf mit sämtlichen originalen Argumenten und allen Sicherheits-/Capture-/Timeoutoptionen. |
| 135 | `check=False, timeout=5, shell=False)` | Verlangt genau einen Aufruf mit sämtlichen originalen Argumenten und allen Sicherheits-/Capture-/Timeoutoptionen. |
| 136 | `self.assertEqual(result["argv"], argv)` | Prüft, dass im Ergebnis dieselben Argumente dokumentiert werden. |
| 137 | `self.assertEqual(result["stdout"], "ok\n")` | Prüft, dass stdout nicht verändert oder verworfen wird. |
| 138 | `self.assertEqual(result["returncode"], 0)` | Prüft, dass der erfolgreiche Prozesscode erhalten bleibt. |
| 140 | `def test_missing_and_denied(self):` | Beginnt den Test für fehlende Programme und fehlende Ausführungsberechtigung. |
| 141 | `for error, code in ((FileNotFoundError("missing"), 127),` | Definiert zwei echte Ausnahmetypen und die dafür vorgesehenen Berichtscodes 127 bzw. 126. |
| 142 | `(PermissionError("denied"), 126)):` | Definiert zwei echte Ausnahmetypen und die dafür vorgesehenen Berichtscodes 127 bzw. 126. |
| 143 | `with mock.patch("subprocess.run", side_effect=error):` | Mock wirft beim Prozessstart jeweils die ausgewählte Ausnahme. |
| 144 | `result = run_command(["ip", "addr"])` | Führt die Fehlerbehandlung der echten Wrapperfunktion aus. |
| 145 | `self.assertEqual(result["returncode"], code)` | Vergleicht den dokumentierten Fehlercode mit dem erwarteten Mapping. |
| 146 | `self.assertTrue(result["stderr"])` | Prüft, dass eine Fehlerbeschreibung vorhanden ist. |
| 148 | `def test_timeout_preserves_bytes(self):` | Beginnt den Timeouttest einschließlich des bytes-Sonderfalls. |
| 149 | `error = subprocess.TimeoutExpired(["ip", "addr"], 5, output=b"partial", stderr=b"err")` | Definiert eine TimeoutExpired-Ausnahme mit teilweisen Byte-Ausgaben für beide Kanäle. |
| 150 | `with mock.patch("subprocess.run", side_effect=error):` | Lässt den Mock den Timeout werfen und führt die echte Fehlerbehandlung aus. |
| 151 | `result = run_command(["ip", "addr"])` | Lässt den Mock den Timeout werfen und führt die echte Fehlerbehandlung aus. |
| 152 | `self.assertEqual(result["returncode"], 124)` | Verlangt den dokumentierten Timeoutcode 124. |
| 153 | `self.assertEqual(result["stdout"], "partial")` | Prüft, dass teilweises stdout decodiert erhalten bleibt. |
| 154 | `self.assertIn("TIMEOUT", result["stderr"])` | Prüft die eindeutige TIMEOUT-Kennzeichnung im stderr-Feld. |
| 155 | `json.dumps(result)` | JSON-Serialisierung muss ohne TypeError gelingen; übrig gebliebene bytes würden den Test scheitern lassen. |
| 157 | `def test_nonzero_is_preserved(self):` | Beginnt den Test eines gestarteten, aber mit Fehlercode beendeten Prozesses. |
| 158 | `with mock.patch("subprocess.run") as run:` | Mock liefert einen CompletedProcess mit Code 2 und Fehlertext, ohne echte Ausführung. |
| 159 | `run.return_value = subprocess.CompletedProcess(["ip"], 2, "", "error")` | Mock liefert einen CompletedProcess mit Code 2 und Fehlertext, ohne echte Ausführung. |
| 160 | `result = run_command(["ip"])` | Ruft den realen Wrapper auf, der bei check=False das Ergebnis statt einer Ausnahme zurückbekommt. |
| 161 | `self.assertEqual(result["returncode"], 2)` | Prüft getrennt, dass der Originalfehlercode und der originale stderr-Text nicht verschluckt werden. |
| 162 | `self.assertEqual(result["stderr"], "error")` | Prüft getrennt, dass der Originalfehlercode und der originale stderr-Text nicht verschluckt werden. |
| 164 | `def test_report_restricts_path_and_uses_exclusive_open(self):` | Beginnt den Test für Verzeichnisbeschränkung und exklusives Speichern. |
| 165 | `for name in ("", "../outside.json", "/outside.json", ".", ".."):` | Jeder unzulässige Dateiname muss ValueError auslösen, bevor eine Datei geöffnet wird. |
| 166 | `with self.assertRaises(ValueError):` | Jeder unzulässige Dateiname muss ValueError auslösen, bevor eine Datei geöffnet wird. |
| 167 | `save_report(name, {})` | Jeder unzulässige Dateiname muss ValueError auslösen, bevor eine Datei geöffnet wird. |
| 168 | `with mock.patch.object(Path, "open", mock.mock_open()) as opened:` | Ersetzt Path.open durch mock_open, sodass der Test keine Datei schreibt. |
| 169 | `save_report("test.json", {"test": True})` | Prüft den echten Speicherpfadcode mit erlaubtem Namen und kleinem Testbericht. |
| 170 | `opened.assert_called_once_with("x", encoding="utf-8")` | Verlangt genau die exklusive Öffnungsart x und UTF-8; kein Überschreibmodus w. |
| 171 | `self.assertIn('"test": true', opened().write.call_args.args[0])` | Prüft, dass der geschriebene Text das tatsächlich serialisierte JSON-Testfeld enthält. |
| 172 | `with mock.patch.object(Path, "open", side_effect=FileExistsError("exists")):` | Simuliert bereits vorhandene Datei: FileExistsError muss durch save_report weitergegeben werden; kein stilles Überschreiben. |
| 173 | `with self.assertRaises(FileExistsError):` | Simuliert bereits vorhandene Datei: FileExistsError muss durch save_report weitergegeben werden; kein stilles Überschreiben. |
| 174 | `save_report("test.json", {})` | Simuliert bereits vorhandene Datei: FileExistsError muss durch save_report weitergegeben werden; kein stilles Überschreiben. |
| 176 | `def test_context_does_not_certify_mininet(self):` | Beginnt den Test des ehrlichen Herkunftshinweises. |
| 177 | `with mock.patch(__name__ + ".run_command", return_value={"returncode": 0}):` | Ersetzt nur die Einzelbefehlsausführung dieses Moduls; Namespace-IDs und Metadaten werden weiterhin lokal erhoben. |
| 178 | `report = collect("ue4.1", "h1 (nur Label)")` | Sammelt einen Testbericht mit absichtlich nicht als Beweis geeignetem h1-Label. |
| 179 | `self.assertEqual(report["context_label"], "h1 (nur Label)")` | Prüft unveränderte Speicherung des Labels. |
| 180 | `self.assertIn("kein Mininetbeweis", report["provenance"])` | Prüft den expliziten Hinweis, dass das Label kein Mininetbeweis ist. |
| 181 | `self.assertEqual(set(report["namespaces"]), {"net", "uts", "pid", "mnt"})` | Prüft die Präsenz exakt der vier erklärten Namespace-Typen. |
| 184 | `def main():` | Definiert den Einstiegspunkt für CLI-Auswertung, Testlauf oder reale Diagnose. |
| 185 | `parser = argparse.ArgumentParser(description=__doc__)` | Erzeugt den Argumentparser mit Modulbeschreibung als Hilfetext. |
| 186 | `parser.add_argument("--self-test", action="store_true", help="nur stdlib-unittest ausführen")` | --self-test ist ein boolescher Schalter und führt nur die Tests statt der normalen Diagnose aus. |
| 187 | `parser.add_argument("--context", default="lokaler Host; kein Mininetnachweis")` | --context bekommt standardmäßig einen ausdrücklich als lokal und nicht-Mininet bezeichneten Wert. |
| 188 | `parser.add_argument("--output", help="neue JSON-Datei im Aufgabenordner (kein Überschreiben)")` | --output ist optional; der Hilfetext nennt Dateiname, Zielordner und Überschreibverbot. |
| 189 | `args = parser.parse_args()` | Liest und validiert die tatsächlichen Kommandozeilenargumente. |
| 190 | `if args.self_test:` | Trennt Testmodus und Messmodus, sodass Fixtures nicht in Hostberichte geraten. |
| 191 | `suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiagnosisTests)` | Lädt alle test_-Methoden der Testklasse in die Testsuite. |
| 192 | `return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1` | Führt Tests wirklich mit ausführlicher Anzeige aus; liefert 0 bei vollständigem Erfolg, sonst 1. |
| 193 | `exercise = Path(__file__).resolve().parent.name` | Bestimmt die Aufgabe am tatsächlichen Elternordner dieser Kopie, nicht anhand eines frei behaupteten Kontextlabels. |
| 194 | `if exercise not in ("ue4.1", "ue4.2", "ue4.5"):` | Unbekannte Aufgabenordner führen zu einem argparse-Fehler statt zu einem versehentlich falschen Plan. |
| 195 | `parser.error("Programm muss in ue4.1, ue4.2 oder ue4.5 liegen")` | Unbekannte Aufgabenordner führen zu einem argparse-Fehler statt zu einem versehentlich falschen Plan. |
| 196 | `report = collect(exercise, args.context)` | Führt die echte lokale Diagnose mit Aufgabenplan und Kontextlabel aus. |
| 197 | `print(json.dumps(report, ensure_ascii=False, indent=2))` | Gibt den tatsächlichen Bericht als formatiertes JSON auf stdout aus. |
| 198 | `if args.output:` | Speichert nur bei ausdrücklich angeforderter --output-Option und behandelt dabei Fehler separat. |
| 199 | `try:` | Speichert nur bei ausdrücklich angeforderter --output-Option und behandelt dabei Fehler separat. |
| 200 | `print(f"Gespeichert: {save_report(args.output, report)}", file=sys.stderr)` | Speichert exklusiv und meldet den Zielpfad auf stderr; stdout bleibt reines JSON. |
| 201 | `except (ValueError, OSError) as error:` | Fängt ungültigen Namen, bestehende Datei oder andere Dateifehler ab und beendet mit Code 2 und ehrlicher Fehlermeldung. |
| 202 | `parser.exit(2, f"Bericht nicht gespeichert: {error}\n")` | Fängt ungültigen Namen, bestehende Datei oder andere Dateifehler ab und beendet mit Code 2 und ehrlicher Fehlermeldung. |
| 203 | `return 1 if any(item["returncode"] != 0 for item in report["commands"]) else 0` | Ein gescheiterter Einzelbefehl ergibt Skriptcode 1; nur vollständig erfolgreiche Einzelbefehle ergeben 0. |
| 206 | `if __name__ == "__main__":` | Der Einstieg läuft nur beim direkten Skriptstart, nicht beim Import als Modul. |
| 207 | `raise SystemExit(main())` | SystemExit macht den von main gelieferten Wert zum tatsächlichen Prozess-Exitcode. |

## Tatsächliche Verifikation und Grenzen

Die Tabelle umfasst 180 nichtleere Quellzeilen. Jede wurde genau einmal zugeordnet; die Nummern wurden programmatisch gegen die tatsächlich abgelegte 207-zeilige Datei geprüft. Die vorhandene Ausgabe der acht erfolgreichen Selbsttests steht in [self-test.txt](self-test.txt); Mockdaten daraus sind keine Netzwerkmessungen. Ein lokaler Hostbericht ist hier nicht veröffentlicht und wird nicht als Beleg verlinkt. Echte Zusatzbelege liegen jetzt unter [nachweise/run01/](../nachweise/run01/): [client-network.txt](../nachweise/run01/client-network.txt), [router-network.txt](../nachweise/run01/router-network.txt), [server-network.txt](../nachweise/run01/server-network.txt), [ping.txt](../nachweise/run01/ping.txt) und [ping-forwarding-off.txt](../nachweise/run01/ping-forwarding-off.txt) dokumentieren reale Routen, qdiscs, erfolgreiche Kommunikation sowie die negative Forwardingprobe in Linux-Netzwerk-Namespaces. [results.json](../nachweise/run01/results.json) fasst diese Checks zusammen; der [zentrale Katalog](../erklaerung_blatt04.md#nachweiskatalog) ordnet weitere PCAP-/Wireshark-Belege ein. Der Gesamtzusatztest verwendet auch eine Linux-Bridge für h1/h2, aber weder Mininet noch OVS oder xterm. Diese drei Laborläufe fehlen weiterhin; reale Namespacebelege dürfen nicht als ausgeführte RN-Lab-Mininet-VM ausgegeben werden.

Die drei Kopien haben bytegleichen Code; ein Wechsel des Skriptordners verändert den Befehlsplan nur über `exercise`. Die Ü4.5-Routerinterface-Abfrage kann auf einem gewöhnlichen Host oder auf client/server fehlschlagen, weil diese Interfaces dort nicht existieren. Das ist ein erfasster Befund, kein Grund für Installation oder Veränderung des Hosts.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29. Tatsächliche Anfrage sinngemäß: Lösungen für Ü4.1, Ü4.2, Ü4.5 mit read-only Hostdiagnosen, ausgeführten Selbsttests und Erklärung aller eigenen Codezeilen erstellen; Originalquellen und KI-Policy beachten, nichts installieren, Hostmessungen nicht als Mininetmessungen ausgeben.
