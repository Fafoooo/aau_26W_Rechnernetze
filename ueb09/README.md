# Übungsblatt 9 – Network Forensics

**Diagnose:** Server-Default-Gateway `10.10.2.254` statt `10.10.2.1`; der Hinweg funktioniert, der serverseitige Rückweg scheitert an der ARP-Auflösung.

**Verifikationsgrenze:** Original-Mininet-Start hier nicht möglich (`ModuleNotFoundError: No module named 'mininet'`). Stattdessen echte isolierte Linux-Netzwerk-Namespaces, veth und Linux-Bridges, mit denselben Routen und unveränderten Original-TCP-Programmen. Keine OVS-/Mininet-/xterm-Messung behauptet, keine TCLink-Verzögerungen nachgebildet. Kurs-VM-Wiederholung bleibt offen. Wireshark-GUI nicht nötig, da die Angabe tcpdump ausdrücklich zulässt.

## Aufgaben

- [Ü9.1: Bestandsaufnahme](ue9.1/antwort.md)
- [Ü9.3: Paketfluss](ue9.3/antwort.md)
- [Ü9.4: Hypothese und unabhängige Evidenz](ue9.4/antwort.md)
- [Ü9.5: minimale Reparatur und Alternativen](ue9.5/antwort.md)
- [Ü9.6: Verifikation und Vergleich](ue9.6/antwort.md)

Im Originalblatt gibt es **keine Ü9.2**. Die Nummerierung wurde nicht ergänzt oder umsortiert.

## Dateien und Belege

- [Originalangabe](angabe_blatt09.pdf), [unveränderte Vorlage samt ZIP](Angabe/).
- [Schritt-für-Schritt-Erklärung](erklaerung_blatt09.md), [individuelle Zeilenerklärungen](zeilenerklaerung.md).
- `messen.py`: echter isolierter Ersatzaufbau; ein neuer exklusiver Belegordner je Lauf.
- `pcap.py`: strikter Ethernet-PCAP-Parser; Prüfsummen, Headerlängen und fehlende Daten werden geprüft.
- `auswertung.py`: nur lesende Diagnose und Vorher-/Nachher-Analyse.
- `test_nachweise.py`: Offline-Regressionen einschließlich kaputter PCAPs, TCP-Mutationen und Isolation/Cleanup-Voraussetzungen.
- [run01](nachweise/run01/): zehn Original-PCAPs, dumpcap-Zähler, vollständiges Befehlsprotokoll, aktive Zustände, Ping-/TCP-Ausgaben, Diagnose **vor** Reparatur, maschinelle Auswertung und unabhängiges tcpdump-Decoding.
- [Prüfbericht](pruefung.md): tatsächlich ausgeführte Tests und Einschränkungen.

## Lesen und testen – ohne Root

Aus diesem Ordner, Python ≥3.12:

```sh
python3 -B auswertung.py
python3 ue9.1/pruefen.py
python3 ue9.3/pruefen.py
python3 ue9.4/pruefen.py
python3 ue9.5/pruefen.py
python3 ue9.6/pruefen.py
python3 -B -m unittest -v test_nachweise
```

`tcpdump` wird für die unabhängige Decoder-Gegenprobe im Test benötigt. Alle fünf Aufgaben haben einen eigenen ausführbaren Einstieg; diese teilen sich bewusst die Auswertung statt fünf widersprüchliche Parserkopien zu pflegen. Mit `--out <Belegordner>` lassen sie sich auf einen neuen Lauf anwenden.

## Neue echte Ersatzmessung

Erfordert Rootrechte, Linux, `/usr/bin/python3` ≥3.12 sowie `ip`, `nsenter`, `ping`, `sysctl`, `ethtool`, `dumpcap`. Keine Installation wird automatisch ausgeführt.

```sh
sudo -n /usr/bin/python3 -B messen.py --out nachweise/run02
python3 -B auswertung.py --out nachweise/run02
```

`run01` wird nicht überschrieben. Das Programm legt **vor allen Netzwerkänderungen** einen frischen äußeren Netzwerk-Namespace an; die vier Hosts erhalten eigene Netzwerk-Namespaces. Es ändert nicht die Netzkonfiguration des tatsächlichen Rechners. Anders als ein Mininet-Lauf benötigt der Ersatz keine benannten persistenten `ip netns`-Einträge. Alle eigenen Prozesse werden beendet und eingesammelt.

In der Kurs-VM stattdessen die Originaldateien in `Angabe/` starten und die im Aufgabenbericht beschriebenen Schritte in den geöffneten Host-xterms wiederholen. Der ENTER-Prompt des Originals ist keine Mininet-CLI.

## Abgabe und KI

Keine automatische Abgabe in Moodle. Kein Abgabe-ZIP, da die Gruppennummer nicht vorliegt. Fabio muss alles prüfen und die Ergebnisse selbst erklären können. Originalanwendung sendet nur eine Serverbegrüßung; ein clientseitiger Nutzdatenversand wird trotz ungenauer Szenarioformulierung nicht behauptet. Eine separate KI-Bericht-PDF ist laut Auftrag nicht verlangt.

**KI-Kennzeichnung:** Hermes Agent; OpenAI `gpt-6.1-sol`; Provider laut `hermes status`: ChatGPT or Codex Subscription; Datum 2026-10-29. Auftrag sinngemäß: RN Übungsblatt 9 vollständig anhand Originalangabe und Vorlage lösen, erst beobachten, dann mit unabhängiger Evidenz diagnostizieren, minimal reparieren, beide Clients und Paketfluss real testen und jede Datei erklären. Sämtliche eigenen Python-Dateien und Antworten tragen Kennzeichnung. Keine studentische Eigenleistung oder VM-Durchführung erfunden.
