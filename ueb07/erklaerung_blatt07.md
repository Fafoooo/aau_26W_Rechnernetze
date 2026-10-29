# Erklärung zu Blatt 07

## Lesereihenfolge

1. [7.1](ue7.1/antwort.md) erklärt die Ausgangsadressen und für jeden Hop Interface, Next Hop und Routingentscheidung. Ein Router kennt nur den nächsten Schritt; die Default-Route entlastet den Client.
2. [7.2](ue7.2/antwort.md) ergänzt r3 mit getrennten /30-Transfernetzen. Der Hinweg allein genügt nicht: Die Rückroute auf r2 muss beim Pfadwechsel mit umgestellt werden.
3. [7.3](ue7.3/antwort.md) zählt Verzögerungen in beide Richtungen und vergleicht echte RTTs. Eine TC-Egress-Warteschlange verzögert nur Pakete, die dieses Interface verlassen.
4. [7.4](ue7.4/antwort.md) entfernt gezielt genau eine Route. Ein Link kann funktionieren, obwohl ein entferntes Zielnetz nicht erreichbar ist. ICMP-Fehlertyp, zitiertes Paket und Routingtabelle begründen zusammen die Diagnose.
5. [7.5](ue7.5/antwort.md) trennt Carrier Sense, Kollisionserkennung und Kollisionsvermeidung. Virtuelle veth-Links bilden keinen gemeinsam benutzten Halbduplex-Ethernetbus ab; die CSMA-Fragen sind Theorie.

## Jede eigene Codezeile verstehen

- [Topologie und Steuerung](erklaerung_topologie.md): `ue7.2/lab_config.py`, `lab_control.py`, `topology.py`, `start_lab.py`, `test_lab.py`. Exakte Quelle und Originalzeilennummer für jede nichtleere Zeile, einschließlich Imports und Tests.
- [Echte Messung und Auswertung](erklaerung_messung.md): `verify_namespaces.py`, `ue7.3/auswerten.py`, `ue7.4/pcap_pruefen.py`. Erzeugung und Cleanup der isolierten Netze, TC, echte Befehle, Capture-Bereitschaft, Ping-Auswertung und binäre PCAP-Felder.
- [PCAP- und Readiness-Regressionen](erklaerung_pcap_tests.md): `ue7.4/test_pcap.py`. Bewusste Negativfälle, synthetische Bytekopien und kontrollierte Zeit-/Selektor-Doubles.

Die Originalvorlagen sind fremde bereitgestellte Infrastruktur, keine selbst verfassten Programme; sie bleiben bytegenau unverändert. Zum Vergleich immer die Arbeitskopie gegen `Angabe/` betrachten. Es gibt keine undokumentierte Codegenerierung im Laufzeitpfad.

## Kleine Änderungen selbst begründen

- **Andere Verzögerung:** In `lab_config.LINKS` den Delay-Wert ändern; beide Linkenden erhalten in Mininet denselben Wert. Danach für jeden gewählten Hin-/Rückweg neu summieren und tatsächlich messen. Die gespeicherten run01-Zahlen gelten dann nicht für die geänderte Konfiguration.
- **Anderes Transfernetz:** Beide Interfaceadressen und die davon abhängigen Next Hops gemeinsam ändern. Gateway und Interface müssen dieselbe direkt verbundene Linkstrecke bezeichnen; Netz-/Broadcastadresse sind keine Hostadressen.
- **Anderer Pfad:** `PATH_ROUTES` enthält die servergerichtete Route auf r1 und die clientgerichtete Route auf r2. Nur einen Eintrag zu ändern produziert einen asymmetrischen Weg. Pfadwechsel sind zwischen zwei Kernelinstanzen nicht atomar.
- **Fehler demonstrieren:** Erst B wählen und erfolgreich prüfen, dann `fault on`. `fault off` stellt genau die entfernte Route wieder her. Eine pauschale Router-Default-Route würde den Versuch verändern.
- **Capture ändern:** Capture- und Anzeigefilter sind unterschiedliche Sprachen. Nur eigene isolierte Endpunkte aufzeichnen; echte Bereitschaft abwarten und die begrenzte Aufnahme regulär auslaufen lassen. Nicht denselben Dateinamen mit einem neuen Messlauf überschreiben.

## Was verifiziert ist – und was nicht

[Prüfbericht](pruefung.md) und [Review](review.md) trennen synthetische API-Tests, echte Linux-/TC-Pakete und echte Offline-Wireshark-GUI. **Mininet fehlt**; die eigentliche VM-Ausführung muss Fabio noch prüfen. Die Quellen erklären alle Zeilen, ersetzen aber weder eigenes Verständnis noch die persönliche Verantwortung im Abschlussgespräch.

## KI-Kennzeichnung

Hermes Agent, OpenAI `gpt-6.1-sol`; Provider ChatGPT or Codex Subscription; Datum: 2026-10-29. Anfrage: „Erkläre jede Datei und jeden Schritt der RN-Blatt07-Lösung so, dass Fabio den Code an der Tafel erläutern und live ändern kann; kennzeichne tatsächliche Tests und offene Grenzen.“
