# Übungsblatt 02 – Anwendungsschicht, Referenzmodelle und Wireshark

Rechnernetze und Netzwerkprogrammierung, WS 2026/27. [Originalangabe](angabe_blatt02.pdf).

## Einstieg

- **Antworten:** die jeweilige `antwort.md` unter den unten verlinkten Aufgabennummern.
- **Zum Verstehen:** [erklaerung_blatt02.md](erklaerung_blatt02.md), eine zusammengeführte Lernhilfe mit Erklärungen zu jeder eigenen Codezeile, den Tests und den Diagrammen. Die vier thematischen Quelldokumente bleiben zusätzlich einzeln verfügbar.
- **Prüfungen:** [testprotokoll_blatt02.md](testprotokoll_blatt02.md) enthält tatsächliche Ausgaben der abschließenden Testläufe und Nachprüfungen, keine Beispielausgaben.
- **Moodle-Zusatzmaterial:** [Angabe/](Angabe/) enthält alle drei originalen PCAPs, einschließlich des freiwillig ausgewerteten Persistenzvergleichs.

## Aufgaben – Originalnummern beibehalten

- [Ü2.1 Internetarchitekturen](ue2.1/antwort.md)
- [Ü2.2 ISO/OSI-Referenzmodell](ue2.2/antwort.md)
- **Ü2.3 existiert auf dem Originalblatt nicht.**
- [Ü2.4 OSI und TCP/IP, Protokollbeispiele](ue2.4/antwort.md)
- [Ü2.5 TCP und UDP](ue2.5/antwort.md)
- [Ü2.6 RFC-artiger Bankomat-Protokollentwurf](ue2.6/antwort.md), [Sequenzdiagramm](ue2.6/sequenz.svg), [Referenzcode](ue2.6/protocol.py), [Demo](ue2.6/demo.py)
- [Ü2.7 WLAN-Heimnetz mit belegten Modellpreisen](ue2.7/antwort.md), [Kostenrechnung](ue2.7/kosten.py)
- [Ü2.8 Streaming gespeicherter Videos](ue2.8/antwort.md)
- [Ü2.9 HTTP-Versionen, Mailprotokolle, SMTP-Beispiel und DNS](ue2.9/antwort.md)
- [Ü2.10 Wireshark und eigene echte Aufzeichnung](ue2.10/antwort.md), [GUI-/Statistiknachweise](ue2.10/gui_kontrolle.md), [Live-Capture-Skript](ue2.10/capture_demo.py)
- [Ü2.11 Protokollanalyse](ue2.11/antwort.md), [gerenderte Hierarchie](ue2.11/hierarchie.svg), [Offlineparser](ue2.11/analyse.py)
- [Ü2.12 HTTP-Objekte, Header, Verbindungen, Bytes und Dauer](ue2.12/antwort.md), [reproduzierbarer Bericht](ue2.12/messbericht.txt)

Das Blatt ist überwiegend theoretisch und analytisch. Für reine Beschreibungsaufgaben wird kein sinnloses Programm erfunden. Referenzcode und Tests stehen bei den praktischen Aufgaben; die Bankimplementierung ergänzt den verlangten Protokollentwurf didaktisch.

## Reproduzieren – offline ohne zusätzliche Python-Pakete

Voraussetzung: Python 3.10 oder neuer, geprüft mit Python 3.14.7. Die Offlineprogramme verwenden ausschließlich die Standardbibliothek. Aus diesem Blattordner:

```bash
python3 -B -m unittest discover -s ue2.6 -p 'test_*.py' -v
python3 -B ue2.6/demo.py
python3 -B ue2.7/kosten.py
python3 -B -m unittest discover -s ue2.10 -p 'test_*.py' -v
python3 -B -m unittest discover -s ue2.11 -p 'test_*.py' -v
python3 -B -m unittest discover -s ue2.12 -p 'test_*.py' -v
python3 -B ue2.11/analyse.py Angabe/dump_protocols.pcap
python3 -B ue2.11/analyse.py Angabe/dump_http.pcap
python3 -B ue2.12/bericht.py
```

`-B` vermeidet neue Bytecode-Caches. Die vier Testsuiten werden getrennt gestartet, da die Aufgabennamen Punkte enthalten und keine Python-Pakethierarchie bilden. Die Offline-Capturetests benötigen keine privilegierten Netzwerkrechte.

Für GUI-Wiederholung Wireshark installieren; getestet wurde Version 4.4.5. Für eine **neue eigene Live-Aufnahme** zusätzlich Linux-Loopback und ausdrücklich erlaubte dumpcap-Capture-Rechte verwenden; die vollständige, eng gefilterte Anleitung steht in Ü2.10. Kein Fremdverkehr wird benötigt. Die tatsächlich ausgeführte Server-GUI wurde unter Xvfb bedient; dies behauptet keine persönliche Bedienung durch Fabio.

Das gerenderte Protokolldiagramm ist bereits enthalten. Bei einer Bearbeitung mit Graphviz neu bauen:

```bash
dot -Tsvg ue2.11/hierarchie.dot -o ue2.11/hierarchie.svg
```

## Grenzen und vor der persönlichen Verwendung

- **Ü2.7:** Der Heimnetzplan verwendet ein **ausdrücklich hypothetisches Referenzhaus**, weil echte Hausdaten fehlen. Er muss für den persönlichen Hausbezug noch an tatsächlichen Grundriss, Verkabelung und Anschluss angepasst werden. Funk-/Durchsatzmessungen wurden nicht erfunden. Preise sind belegte Angebotsmomentaufnahmen, keine Bestellung oder Preisgarantie.
- **Ü2.6:** Die Python-Referenz ist eine flüchtige In-Memory-Unterrichtssimulation. TLS/mTLS, Persistenz, echte Karten-/PIN-Infrastruktur und Bankomat-Hardware werden nicht implementiert oder als getestet behauptet. Der RFC-artige Entwurf beschreibt diese Transport-/Betriebsanforderungen gesondert.
- **Ü2.11/12:** Der Offlineparser ist gezielt auf die gelieferten vollständigen Ethernet/IPv4-PCAPs begrenzt. Kein vollständiger Ersatz für Wireshark, kein beliebiger Live-Netzwerkscanner.
- **Abgabe:** Die LV verlangt `uebxx-gruppeyy.zip`. Die Gruppennummer ist unbekannt; deshalb wurde kein willkürlich benanntes ZIP erzeugt. Bei eigener Verwendung das verlangte Paket selbst mit korrekter Gruppe zusammenstellen und die Lösung erklären können. Es wurde **nichts in Moodle abgegeben**.

## KI-Kennzeichnung

Dieses Blatt wurde mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19** anhand des originalen Aufgabenblatts, der Moodle-Zusatzdateien und recherchierter Quellen erstellt. Der tatsächliche Auftrag war sinngemäß, alle Teilaufgaben zu lösen, Code auszuführen, die Ergebnisse unabhängig zu prüfen und die Lösung zeilenweise zu erklären. Die aufgabenspezifischen Anfragen stehen zusätzlich in den Python-Dateien und den Antworten. Die Kursregel erlaubt KI mit Kennzeichnung und Eigenverantwortung; es wird keine Eigenleistung Fabios behauptet. Ein gesondertes KI-Bericht-PDF war für dieses Blatt nicht angefordert.
