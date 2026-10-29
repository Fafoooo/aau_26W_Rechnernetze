# Prüfbericht – Blatt 07

## Herkunft und Umfang

2026-10-29, Hermes Agent/OpenAI gpt-6.1-sol. Originalangabe als beide gerenderten Seiten und als Layouttext gelesen, zwölf Originalvorlagen aus dem echten Moodle-Archiv eingesehen. Kursregel erlaubt KI mit Kennzeichnung; Kennzeichnung einschließlich sinngemäßem Auftrag steht in allen eigenen Python-Dateien und jeder Aufgabenantwort. Kein Abgabe-ZIP mangels Gruppennummer, keine Moodle-Abgabe.

## Tatsächlich ausgeführte Prüfungen

1. **Originalerhalt:** Die zwölf extrahierten Dateien stimmen bytegenau mit `Angabe/uebb7_template.zip` überein. Die eigene Arbeitskopie liegt in `ue7.2/`, nicht im Originalordner. Originale CRLF-Zeilenenden und Leerzeichen in rohen Befehlsausgaben bleiben absichtlich erhalten; `git diff --check` wird für eigene Quellen und Texte unter Ausschluss von `Angabe/` und unveränderten `nachweise/` geprüft.
2. **23 unprivilegierte Tests** in `ue7.2/test_lab.py`: Adressplan, eindeutige Interfaces/Transfernetze, beidseitige Modellwege und Verzögerungsbudgets, synthetische Mininet-API, LinuxRouter-Konfiguration, Hin-/Rückrouten, Pfadwechsel, Fehler und Reparatur, Rollback bei Befehls- und Prozessstartfehlern, Cleanup bei Build-/Startfehlern, CLI und zeilenexakte Topologieerklärung. Alle bestanden. [Protokoll](ue7.2/synthetic_tests.txt). Fake-Pings sind keine Messungen.
3. **18 Offline-Tests** in `ue7.4/test_pcap.py`: 13 PCAP- und fünf Readiness-Testmethoden. Echte Aufnahme, vier Byteorder-/Zeitauflösungsvarianten, minimale ICMP-Zitate und IP-Optionen; Negativfälle mit falschen Protokollen, ID/Sequenz, Duplikaten, Fragmentierung, Headerlängen, Abschneidungen und falschen Bereitschaftssignalen. Alle bestanden. Synthetisch mutierte Bytefolgen sind explizit Testeingaben, keine neuen realen Aufnahmen.
4. **Echte Namespace-/TC-Messungen:** `verify_namespaces.py` wurde mit Linux-Netzwerk-Namespaces und veth ausgeführt. Ein äußerer privater Netzwerk-Namespace wird zwingend vor allen Netzänderungen erstellt. Für jede Variante wurden Adressen, Routen, `ip rule`, Forwarding und TC gesichert, beide Richtungen nach Warmlauf mit zehn Echoanfragen getestet und Tracepath ausgeführt. Ausgangsstruktur, A und B lieferten je Richtung 10/10 Antworten. [Unveränderte Rohbelege und Ergebnis-JSON](nachweise/run01/results.json).
5. **RTT:** Client-Mittelwerte Original 60.441 ms, A 14.577 ms, B 124.557 ms; Gegenrichtung 60.213/14.505/124.811 ms. Konfigurationsanteile A 14 ms, B 124 ms wurden programmatisch berechnet; gemessene und berechnete Werte werden nicht verwechselt.
6. **Absichtlicher Fehler:** B zunächst erfolgreich; ausschließlich r3s Servernetzroute gelöscht. Lokaler Lookup schlägt fehl, Ping erhält zwei Netzfehler, Tracepath stoppt mit `!N` bei r3. Nach gezielter Reparatur Lookup erfolgreich und Client-Ping 3/3 Antworten.
7. **Echte Fehler-PCAP:** dumpcap am eigenen isolierten `client-eth0`, enger ICMP-Filter, begrenzte Dauer. Erst auf `File: -` gewartet, dann zwei Anfragen gesendet; regulär auslaufen lassen. Vier Pakete, null verworfen. Eigener Byteparser und unabhängiges `tcpdump -nn -vv -r` bestätigen Echoanfragen und ICMP Type 3/Code 0 samt passender ID/Sequenz in den Zitaten. [PCAP](nachweise/run01/fault.pcap), [Frameauswertung](nachweise/run01/fault-frames.json).
8. **Authentische GUI:** PCAP tatsächlich in Wireshark unter eigenem Xvfb geöffnet und Bildschirm mit ffmpeg aufgenommen. Filter `icmp.type == 3`, Frames 2 und 4 sichtbar, Frame 2 ausgewählt. Screenshot visuell kontrolliert; keine privaten Hostpfade sichtbar. [Bild](nachweise/run01/wireshark-fehler.png), [GUI-Protokoll](nachweise/run01/gui-nachweis.txt). GUI- und Xvfb-Prozesse anschließend beendet.
9. **Erklärungen:** Für alle eigenen Programme existiert eine zeilenweise Erklärung mit exaktem Quelltext und Originalzeilennummer. Übereinstimmung, Reihenfolge und eindeutige Abdeckung maschinell geprüft; lokale Links geprüft. Originalvorlagen sind getrennt gekennzeichnete Fremddateien.

## Tatsächlicher iterativer Ablauf

Die ersten Netzläufe wurden nicht als fertige Nachweise übernommen: Ein Test erwartete zunächst einen anderen englischen Ping-Meldungstext; nach Korrektur zeigte ein erster Capture drei statt vier Pakete, weil `Capturing on` zu früh als Bereitschaft interpretiert worden war. Die Aufnahme wartet deshalb auf `File: -`. Nur der erfolgreiche vollständige Lauf liegt unter `nachweise/run01/`; fehlgeschlagene Teilaufzeichnungen werden nicht mit ihm gemischt.

Die unabhängige Prüfung fand anschließend eine Cleanup-Lücke beim Mininet-Aufbau, eine zu kurze Idle-Bereitschaftsfrist und eine unvollständige PCAP-Zuordnungsprüfung. Diese wurden korrigiert und durch Regressionstests abgesichert. Der gespeicherte Netzlauf bleibt unverändert; die nachträglichen Parser-/Readiness-Korrekturen wurden offline gegen diesen Lauf und kontrollierte Negativfälle getestet. Ein neuer privilegierter Netzlauf nach diesen kleinen Korrekturen wird nicht behauptet.

## Grenzen und offene Abnahme

- **Mininet fehlt**: echter Starter-Abhängigkeitstest endet nachvollziehbar mit Exitcode 2. `--help` ist ohne Mininet lauffähig. Es wurde nichts installiert. Modell-/API-Tests und echte Linux-Netze ersetzen keinen tatsächlichen Mininet-VM-/xterm-Lauf. Dieser bleibt offen.
- B-Tracepath erreicht das Ziel, aber Hop 3 antwortet in beiden Richtungen nicht. Kein Hop wurde erfunden ergänzt; Routingzustand, Enderreichbarkeit und TTL stützen den vorgesehenen Pfad.
- Nach der Fehlerreparatur ist ein Client-Ping belegt, kein zusätzlicher gespeicherter Rückwärts-/Tracepath-Block. Beide Richtungen waren vor dem gezielten Fehler erfolgreich.
- Der PCAP-Parser ist auf die kleine eigene Ethernet/IPv4/ICMP-Aufnahme zugeschnitten; er ist kein universeller Parser und prüft nicht sämtliche Prüfsummen. `assert`-Tests nicht mit `python -O` abschalten.
- Die zusätzlichen Links sind r1–r3–r2. Die schematische Zeichnung wurde im Sinn der expliziten Router-zu-Router-Anforderung umgesetzt; ein direkter r3–Server-Link wird nicht vorgetäuscht.
