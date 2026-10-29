# Übungsblatt 07 – Routing, Topologieänderung und Wireshark

[Originalangabe](angabe_blatt07.pdf) · [Erklärung](erklaerung_blatt07.md) · [Prüfung](pruefung.md) · [Unabhängige Prüfung](review.md)

**⚠️ Echter Mininet-/xterm-Lauf in der vorbereiteten Labor-VM steht aus.** Mininet ist hier nicht vorhanden; es wurde nichts installiert. Die Lösung enthält getesteten Mininet-Code, **echte Linux-Namespace-/TC-Messungen** als Ersatzverifikation, eine echte Fehler-PCAP und einen authentischen Wireshark-GUI-Screenshot. Diese Nachweise sind kein Mininet-Nachweis.

## Aufgaben

- [7.1 Routingpfad](ue7.1/antwort.md): ursprüngliche Interfaces, Next Hops, Tabellen und Hin-/Rückweg.
- [7.2 Erweiterung](ue7.2/antwort.md): r3, zusätzliche /30-Netze, statische A/B-Routen und ausführbare Mininet-CLI.
- [7.3 Verzögerungen](ue7.3/antwort.md): Sollwerte A 14 ms/B 124 ms; echte Client-Mittelwerte 14.577/124.557 ms.
- [7.4 Fehlerdiagnose](ue7.4/antwort.md): fehlende r3-Serverroute, ICMP-Netzfehler, Reparatur, PCAP und GUI.
- [7.5 CSMA](ue7.5/antwort.md): Kanalzugriff, Kollisionen, CSMA/CD und CSMA/CA.

Der Client heißt in der Vorlage `client`, in der Angabe `client1`. Der alternative Routerpfad wird als `r1–r3–r2` realisiert, damit nur Router-zu-Router-Verbindungen hinzukommen und das Server-LAN unverändert bleibt. Die Interpretation der schematischen Skizze ist ausdrücklich in 7.2 dokumentiert.

## Gefahrlos reproduzierbare Tests

Vom Repository-Stamm, ohne Root/Mininet und ohne Netzänderungen:

```sh
python3 -B ueb07/ue7.2/test_lab.py
python3 -B ueb07/ue7.4/test_pcap.py
python3 -B ueb07/ue7.3/auswerten.py ueb07/nachweise/run01/A-client-ping.txt
python3 -B ueb07/ue7.3/auswerten.py ueb07/nachweise/run01/B-client-ping.txt
python3 -B ueb07/ue7.4/pcap_pruefen.py ueb07/nachweise/run01/fault.pcap
```

Ergebnis: **23 synthetische Modell-/API-/Dokumentationstests und 18 Offline-PCAP-/Readiness-Tests bestanden**. Synthetische Bytevarianten sind keine gemessenen Netzwerkpakete. Parser-Testbedingungen benötigen Python ohne `-O`.

Echter Laborstart nur in der vorbereiteten Mininet-VM:

```sh
cd ueb07/ue7.2
sudo python3 -B start_lab.py --path A
```

Bedienung: `path A`, `path B`, `state`, `check`, `fault on`, `fault off`, `exit`. Umschaltung erst abschließen, dann messen. Vollständige Anweisungen in 7.2.

## Belege

[nachweise/run01/results.json](nachweise/run01/results.json) und zugehörige unveränderte Textprotokolle dokumentieren die erfolgreiche Ausgangsstruktur, beide erweiterten Wege in beiden Richtungen, Routen/TC, Fehler und Reparatur. Der zusätzliche [Runner](verify_namespaces.py) erzeugt isolierte Netze erst nach `os.unshare(CLONE_NEWNET)` und beendet seine Halteprozesse. `run01` wird absichtlich nicht überschrieben; für neue Messungen muss ein neuer Laufname verwendet werden.

[Fehler-PCAP](nachweise/run01/fault.pcap) · [Wireshark-GUI-Screenshot](nachweise/run01/wireshark-fehler.png). Aufzeichnung nur am eigenen isolierten Clientinterface, kein fremder Verkehr.

`Angabe/uebb7_template.zip` und alle zwölf daraus extrahierten Dateien sind unverändert. Eigene Änderungen liegen außerhalb `Angabe/`. Gruppennummer unbekannt: kein Abgabe-ZIP erstellt. Nichts in Moodle abgegeben.

## KI-Kennzeichnung

Hermes Agent, OpenAI `gpt-6.1-sol`; Provider laut `hermes status`: ChatGPT or Codex Subscription; Datum: 2026-10-29. Auftrag: RN-Blatt07 mit Originalvorlagen vollständig bearbeiten, KI-Kennzeichnung beachten, lauffähigen Code, Antworten, zeilenweise Erklärungen sowie echte, klar abgegrenzte Tests und Messbelege erstellen. Keine menschliche Eigenleistung behauptet.
