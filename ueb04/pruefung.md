# Prüfprotokoll – Blatt04

Datum: 2026-10-29. Prüfung durch Hermes Agent / OpenAI gpt-6.1-sol, keine behauptete Eigenleistung oder persönliche VM-Durchführung des Studierenden.

## Tatsächlich ausgeführt

- Original-PDF als Text **und als gerenderte Seiten** gelesen; Ü4.1 bis Ü4.6 vollständig erfasst.
- Moodle-Zusatzdatei heruntergeladen; alle sechs Originalprogramme gegen das ZIP byteweise verglichen. Unverändert. Die dort nicht enthaltene README wurde nicht erfunden.
- Bereitgestelltes `check_environment.py` ausgeführt: Mininet, OVS, xterm fehlen. Keine Systeminstallation geändert.
- Diagnoseprogramme: je acht erfolgreiche Selbsttests für Ü4.1, Ü4.2, Ü4.5; Befehlsargumente, Fehlerbehandlung und Ausgabepfadschutz getestet. Mocks sind Testdaten, keine Netzwerkbelege.
- UDP: fünf erfolgreiche Testmethoden mit echten Loopback-Sockets, echten Server-/Clientprozessen, UTF-8, Leertext, Größenlimit, CLI-Fehlern und Timeout. [Testausgabe](ue4.3/test_udp.txt).
- TCP: 16 erfolgreiche Tests für LF-Framing, Fragmentierung/Coalescing, UTF-8, EOF, Limits, Fehlerfälle, mehrere Verbindungen und Timeouts; zusätzlich echter CLI-Lauf. [Testausgabe](ue4.6/test_tcp.txt), [CLI-Ausgabe](ue4.6/cli_test.txt).
- Echte Namespace-Integration: h1/h2 mit Linux-Bridge `/24`, getrennte Netzsicht bei gemeinsamem UTS-Namespace; drei UDP-Datagramme einschließlich geänderter Nachricht. Drei Router-/Endpunkt-Namespaces mit den RN-Lab-IPs, Routen und 20-ms-netem-Eigenschaften. Vier erfolgreiche Pingantworten; Negativprobe ohne IP-Forwarding scheitert wie gefordert. Zwei echte TCP-Verbindungen, davon eine mit drei persistenten Nachrichten.
- Echte dumpcap-Aufnahmen auf jeweils dem eigenen virtuellen Labinterface, eng auf die selbst erzeugten IPs/Ports gefiltert. Kein Fremdverkehr erfasst. PCAP-Zählung stimmt mit dumpcaps Abschlusszählung überein: UDP drei, TCP 24 Pakete.
- Unabhängige stdlib-Byteprüfung beider PCAPs: UDP-Header, Payload und Längen, TCP-Handshakes, rekonstruierte Nachrichtendaten/Echos, FINs und ihre Bestätigungen; kein TCP-RST im regulären Lauf. Zusätzlich mit tcpdump als zweitem Parser bestätigt.
- Echte Wireshark-GUI unter isoliertem Xvfb gestartet, beide gespeicherten PCAPs geöffnet und Screenshots tatsächlich erzeugt und visuell geprüft. Keine synthetischen Screenshots. TShark-Dateizugriff scheiterte; es wurde nicht als Root umgangen und keine Sicherheitsrichtlinie geändert.
- Nach Härtung des Namespace-Runners erneut die gesamte Namespace-Integration samt beider PCAP-Prüfungen erfolgreich ausgeführt; dabei Aufruf ohne vorgelagertes unshare, um das nun interne Erzeugen des äußeren Namespace tatsächlich auszuüben. Zweite Laufartefakte nicht mit den unveränderten dokumentierten run01-Messwerten vermischt.
- Erklärungen decken jede nichtleere Zeile der eigenen Programme ab; Zeilennummern und lokale Dokumentlinks maschinell geprüft.

## Unabhängige technische Prüfung und Korrekturen

Eine zweite Instanz las die Originalangabe, Originaldateien, alle Programme, Antworten und echten Nachweise und führte die Tests erneut aus. Bestätigt: Aufgaben vollständig behandelt, Originaldateien unverändert, UDP-Payload **19 Bytes**, alle dokumentierten Ports/Frameverweise stimmen, keine weiteren fachlichen Codefehler gefunden. Zwei konkrete Hinweise wurden eingearbeitet:

1. **Capture zu früh stoppen:** Ein sofortiges SIGINT kann wegen libpcap-Pufferung Schlusssegmente verlieren. Der Runner lässt deshalb den begrenzten Capture regulär enden. Beide manuellen Anleitungen weisen auf den Eingangspuffer und das tatsächliche Eintreffen der Pakete hin. Vollständigkeit wird anschließend aus dem PCAP geprüft.
2. **Isolation erzwingen:** Eine leere IPv4-Routingtabelle beweist keinen frischen Namespace. Der Runner erzeugt jetzt vor Netzoperationen selbst mit `os.unshare(os.CLONE_NEWNET)` einen neuen äußeren Namespace; fehlende Berechtigungen führen zum Abbruch. Die zugehörige Zeilenerklärung wurde angepasst und ein echter erneuter Gesamtlauf erfolgreich durchgeführt.

## Verbleibende, ausdrücklich nicht als erledigt behauptete Punkte

- Mininet-/OVS-Lauf der **bereitgestellten VM** und die zwei xterm-Hostfenster fehlen. Linux-Namespace-Tests sind reale Zusatzbelege, aber kein Ersatz für diese Durchführung.
- Die im Original-ZIP fehlende README kann nicht gelesen werden; die sechs mitgelieferten Programme wurden vollständig gelesen.
- Gruppennummer unbekannt: kein Abgabe-ZIP erstellt. Keine Moodle-Abgabe vorgenommen.

Alle ausstehenden Schritte und VM-Befehle stehen in den jeweiligen `antwort.md` und der [README](README.md).
