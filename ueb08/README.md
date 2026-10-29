# Blatt 08 – Ethernet, ARP und Switching

## Lösungen

- [Ü8.1 Ethernet-Frames](ue8.1/antwort.md)
- [Ü8.2 ARP](ue8.2/antwort.md)
- [Ü8.3 Switch Learning](ue8.3/antwort.md)
- [Ü8.4 Router und zwei LANs](ue8.4/antwort.md)
- [Ü8.5 Wireshark-Schichten](ue8.5/antwort.md)
- [Schritt-für-Schritt-Erklärung aller eigenen Programme](erklaerung_blatt08.md)
- [Prüfbericht mit Grenzen](pruefung.md), [tatsächliche Abschluss-Testausgaben](nachweise/abschluss-tests.txt)
- [Originalangabe](angabe_blatt08.pdf); Originalvorlagen in `Angabe/`, unverändert aus dem beigefügten Moodle-ZIP.

## Verifiziert und Grenzen

Echte Linux-Netzwerk-Namespaces, veth, Linux Bridges, Ping und eigene HTTP/TCP-Sockets; ausschließlich eigener isolierter Laborverkehr. Kein synthetisches PCAP. [Elf PCAPs](nachweise/run01/results.json), [gesicherter Zustand](nachweise/run01/zustand.txt), [Befehlsprotokoll](nachweise/run01/befehle.txt), [unabhängige Dekodierung und Tests](nachweise/run01/tests.txt). Die Tests trennen echte Messungen von ausdrücklich synthetischen Negativkontrollen.

[Wireshark-GUI-Nachweis](nachweise/gui/README.md) mit Screenshots der gespeicherten PCAPs: Ethernet, ARP, beide Routerseiten, HTTP und markierte Schichten. Wegen eingeschränktem direkten Dateizugriff wurden ausschließlich bereits vorhandene eigene PCAP-Bytes per stdin eingelesen. Keine Privilegienerhöhung für die GUI, kein Live-Capture in der realen Umgebung.

**Nicht ausgeführt:** Mininet-/OVS-Kurs-VM und xterm-Monitor; Mininet und OVS fehlen hier. Die reale Linux-Bridge-Messung ersetzt keinen OVS-Nachweis. Die Mininet-Routererweiterung ist mit Testdoubles auf Konstruktion, Adressierung und Fehler-Cleanup getestet, nicht unter Mininet. Die Aufgabe ist fachlich beantwortet und mit realen Paketen belegt; diese konkrete VM-Prüfung bleibt offen.

**Vorlagenfallen:** `.3` ist client2, server1 ist `.10`; `ocs-appctl` in der PDF muss `ovs-appctl` heißen. Der Originalstarter öffnet xterms und wartet auf Enter, bietet keine Mininet-CLI. Seine Vorab-Pings wärmen Caches vor. Der Monitor leert nur die Switch-FDB. Details in Ü8.3.

## Offline auswerten und testen (ohne root)

Ab `ueb08`:

```sh
python3 -B ue8.1/auswerten.py
python3 -B ue8.2/auswerten.py
python3 -B ue8.3/auswerten.py
python3 -B ue8.4/auswerten.py
python3 -B ue8.5/auswerten.py
python3 -B messen.py --analyse
python3 -B test_nachweise.py
python3 -B test_cli_lab.py
```

Jede Teilaufgaben-CLI berechnet PCAP-Befunde erneut; bei Ü8.2/8.3 werden die gesicherten Nachbar-/FDB-Snapshots zusätzlich gekennzeichnet ausgegeben. `--belege nachweise/run02` wählt einen anderen vollständigen Messordner.

## Neue reale Ersatzmessung

Nur auf einem Linux-Laborsystem mit Python ≥3.12, Namespace-/Bridge-Rechten und den vorhandenen Programmen `ip`, `bridge`, `nsenter`, `sysctl`, `ethtool`, `ping`, `dumpcap`:

```sh
sudo /usr/bin/python3 -B messen.py --out nachweise/run02
```

**`run01` nicht überschreiben.** Jeder neue Lauf braucht einen noch nicht vorhandenen Ordner. Der Runner erstellt zuerst einen äußeren privaten Netzwerk-Namespace und ändert erst danach das Netzwerk. Bei einem Fehler endet er statt ins reale Hostnetz auszuweichen. Alle eigenen Worker/Captures werden begrenzt und beendet. Es erfolgt keine Softwareinstallation.

Der HTTP-Server auf 8080 ist absichtlich ein Ein-Verbindungs-Laborserver, kein öffentlicher Dienst. Die Client-Quellportbindung 40080 macht Vergleiche eindeutig. Laufzeiten, IDs, Sequenzen und Prüfsummen können sich bei neuen Läufen ändern. Die Framezählung gilt für `run01`; insbesondere überlappen die beiden Ü8.3-Captures (Details in der Antwort).

## Mininet-Kurs-VM

Original-LAN: ab `Angabe`, `sudo /usr/bin/python3 start_lab_monitor.py` mit grafischer Sitzung. Routererweiterung: ab `ueb08`, `sudo /usr/bin/python3 -B ue8.4/lab.py`. Keine globale Mininet-Cleanup-Anweisung auf fremden Netzen ausführen.

Die Gruppennummer ist unbekannt; kein ZIP mit erfundener Gruppe. Nach eigener Durchsicht und Ergänzung der konkreten VM-Nachweise selbst im LV-Format `ueb08-gruppeyy.zip` verpacken. Nichts wurde in Moodle abgegeben.

**KI-Kennzeichnung:** Hermes Agent; OpenAI gpt-6.1-sol, Provider laut `hermes status`: ChatGPT or Codex Subscription; Datum 2026-10-29. Auftrag: Dieses Blatt vollständig lösen, reale Messungen und getestete Programme erstellen, die Originalvorlage bewahren und jede eigene Codezeile erklären. Keine Eigenleistung von Fabio behauptet. Kennzeichnung auch in allen eigenen Python-Dateien und jeder `antwort.md`; kein separater KI-Bericht verlangt.
