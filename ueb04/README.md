# Übungsblatt 04 – Mininet und Python

## Stand und ehrliche Prüfgrenzen

Alle sechs Aufgaben sind mit Antworten und Code ausgearbeitet. UDP und TCP wurden tatsächlich mit echten Sockets und CLI-Prozessen getestet; Routing, Anwendungen und Paketmitschnitte zusätzlich in echten Linux-Netzwerk-Namespaces. Die beiden PCAPs wurden unabhängig byteweise geprüft und in der echten Wireshark-GUI geöffnet. Screenshots und Messdaten stehen unter [nachweise/run01/](nachweise/run01/).

**Noch in der bereitgestellten VM durchzuführen:** Mininet-/OVS-Lauf und die separaten xterm-Konsolen. Diese Labortools fehlen hier; entsprechend der Angabe wurde nichts nachinstalliert. Die Zusatztests mit Linux-Bridge und Netzwerk-Namespaces sind **kein Ersatznachweis für die verlangte Mininet-VM**. Keine Moodle-Abgabe vorgenommen. Keine vollständige persönliche Durchführung durch Fabio behauptet.

**Vor der Abgabe:** In der VM alle beschriebenen Schritte wiederholen, eigene Ergebnisse prüfen und jeden Codeabschnitt erklären können. Gruppennummer ist unbekannt; daher wurde kein `ueb04-gruppeyy.zip` erstellt.

## Einstieg

- [Erklärung und vollständiger Dateikatalog](erklaerung_blatt04.md)
- [Ü4.1 – Hosts, Einführung, Routen und Isolation](ue4.1/antwort.md)
- [Ü4.2 – Separate Konsolen](ue4.2/antwort.md)
- [Ü4.3 – UDP-Client und -Server](ue4.3/antwort.md)
- [Ü4.4 – UDP-Mitschnitt und TCP/IP-Schichten](ue4.4/antwort.md)
- [Ü4.5 – Routing über Linux-Router](ue4.5/antwort.md)
- [Ü4.6 – TCP, Framing und persistente Verbindung](ue4.6/antwort.md)
- [Prüfprotokoll](pruefung.md)

Originale: [Angabe-PDF](angabe_blatt04.pdf), [unverändertes Vorlagen-ZIP](Angabe/uebb4_template.zip) und sechs daraus extrahierte Dateien in `Angabe/`. Die im PDF genannte Original-README fehlt tatsächlich im ZIP. Diese README ist die Dokumentation unserer Lösung, keine nachgebildete Originaldatei.

## Tests ohne Mininet und ohne Root

Aus diesem Verzeichnis, mit Python 3 und Standardbibliothek:

```sh
python3 -B ue4.1/diagnose.py --self-test
python3 -B ue4.2/diagnose.py --self-test
python3 -B ue4.5/diagnose.py --self-test
(cd ue4.3 && python3 -B -W error::ResourceWarning -m unittest -v test_udp)
(cd ue4.6 && python3 -B -W error::ResourceWarning -m unittest -v test_tcp)
python3 -B ue4.4/analyse_pcap.py nachweise/run01/udp.pcap --kind udp
python3 -B ue4.4/analyse_pcap.py nachweise/run01/tcp.pcap --kind tcp
```

Der Captureprüfer verwendet Assertions; nicht mit `-O` starten. Die drei Diagnoseprogramme sammeln im normalen Modus lokale Systeminformationen: Ausgaben vor jeder Veröffentlichung prüfen. Im Repo werden keine privaten Hostdiagnosen mitgeliefert.

## Optionaler isolierter Zusatz-Integrationstest

Erfordert Linux, Python **3.12 oder neuer**, ausreichende Namespace-/Netzwerkrechte sowie bereits vorhandene Befehle `ip`, `unshare`, `nsenter`, `tc`, `sysctl`, `ping`, `dumpcap` und `/usr/bin/python3`. Keine Paketinstallation durch den Runner. Erklärung: [jede Runnerzeile](erklaerung_namespace.md).

```sh
sudo unshare --net python3 -B verify_namespaces.py --output nachweise/neuer-lauf
```

Nur einen neuen Ausgabeverzeichnisnamen verwenden. Der Runner erzeugt zusätzlich selbst einen frischen äußeren Netzwerk-Namespace **vor jeder Netzänderung**. Alle erzeugten Netzgeräte und Routen bleiben dort bzw. in seinen Kindern. Die Ausgabe ist bei Root-Ausführung zunächst möglicherweise nur für Root lesbar; die eigenen erzeugten Dateien anschließend gezielt dem eigenen VM-Benutzer übergeben. Vorhandene Belege nicht überschreiben.

Die Dateinamen der beiden PCAPs heißen `udp.pcap` und `tcp.pcap`; danach jeweils den Byteprüfer auf den neuen Pfad anwenden. Dynamische Ports und Paketnummern aus einem neuen Lauf nicht mit den dokumentierten run01-Werten vermischen.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, **OpenAI gpt-6.1-sol**, **2026-10-29**; Provideranzeige laut Hermes-Status: ChatGPT or Codex Subscription. Tatsächlicher Auftrag sinngemäß: Blatt04 vollständig ausarbeiten, Originalquellen und Kennzeichnungspflicht beachten, Code real testen, unabhängig überprüfen und jede eigene Codezeile für eine mündliche Erklärung dokumentieren. Die jeweilige Teilanfrage steht zusätzlich am Anfang jeder eigenen Python-Datei und in jeder `antwort.md`. `Angabe/` enthält unveränderte fremde Originaldateien.
