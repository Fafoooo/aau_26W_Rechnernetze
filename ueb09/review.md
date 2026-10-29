# Unabhängige Endprüfung – RN Blatt 09

**Stand:** 2026-10-29. KI-Kennzeichnung: Hermes Agent; OpenAI `gpt-6.1-sol`; ChatGPT or Codex Subscription.

## Urteil

**Fachliche Kernlösung und gespeicherte Ersatzmessungsbelege bestanden; kleinere Dokumentationskorrekturen offen.** Kein relevanter Fehler an Diagnose oder minimaler Reparatur gefunden. Die vollständige Testsuite war zum Prüfzeitpunkt wegen der parallel noch bearbeiteten Test-Zeilenerklärung **nicht vollständig grün**. Ein erfolgreicher Original-Mininet-Lauf ist ausdrücklich **nicht** nachgewiesen.

## Konkrete Befunde

1. **Kleine fachliche Ungenauigkeit, `ue9.6/antwort.md:19`:** „SYN und SYN-ACK bestätigen mit ihrer ACK-Nummer jeweils die Gegen-Sequenznummer plus eins“ ist falsch formuliert. Das initiale SYN hat kein gesetztes ACK-Flag und bestätigt keine Gegen-Sequenznummer. Richtig: **SYN-ACK bestätigt Client-ISN + 1; das dritte Handshake-ACK bestätigt Server-ISN + 1.** Die echten Mitschnitte und `auswertung.py:72–74` sind in diesem Punkt korrekt; nur die Erklärung ist zu ändern. Erneutes `tcpdump -nn -S` bestätigt für client1 SYN-Seq `48995888`, SYN-ACK-Ack `48995889` und drittes Ack `2371939755` zu Server-ISN `2371939754`.
2. **Veralteter Dokumentationsstand, `erklaerung_blatt09.md:28`:** Die Aussage über „acht eigene Python-Dateien“ und später ergänzte, nicht als Testnachweis behauptete `test_*.py` passt nicht mehr zum vorhandenen und ausführbaren `test_nachweise.py`. Nach Abschluss der parallel laufenden Zeilendokumentation aktualisieren.
3. **Fehlendes Linkziel, `README.md:26`:** `pruefung.md` war bei dieser Prüfung nicht vorhanden. Den Prüfbericht noch anlegen oder den Link bewusst auf den tatsächlich vorgesehenen Bericht ändern. Dieser Review legt ausschließlich `review.md` an.

## Tatsächlich ausgeführte Prüfungen

Arbeitsordner: `ueb09`. Keine privilegierten Befehle und keine Netzänderung.

- Original-PDF und vorhandenen Angabentext gelesen; alle sieben entpackten Vorlagendateien, eigene Programme und fünf Aufgabenantworten mit Aufgabenstellung und Belegen abgeglichen. Die Angabe enthält tatsächlich keine Ü9.2. Eine PDF-Layout-/Bildprüfung war nicht Teil dieser fachlichen Endprüfung.
- `python3 -B auswertung.py`: **Exit 0**. Bestätigt zehn PCAPs, zwölf erfolglose serverseitige ARP-Anfragen nach `.254`, SYNs beider Clients am Server, keine serverseitigen TCP-Rückpakete vor Reparatur; zehn zuordenbare TCP-Pakete vorher und achtzehn nachher. Danach je Client neun TCP-Pakete, 28 Bytes Originalbegrüßung, beidseitige bestätigte FINs und kein RST.
- `python3 -B -m unittest -v test_nachweise`: zweimal ausgeführt, jeweils **11 Tests, 10 erfolgreich, 1 Fehlschlag**. Ausschließlich `test_ai_labels_and_line_coverage` scheitert an der noch leeren Erklärungsliste für die parallel dokumentierte Testdatei. Dieser angekündigte Zwischenstand wurde nicht weiter untersucht und ist kein Paket-/Netzwerkfehler; nach Fertigstellung erneut ausführen.
- Erfolgreiche Tests umfassen Originalarchivvergleich, alle fünf Aufgaben-CLIs, Übereinstimmung mit gespeicherter Auswertung, unabhängige tcpdump-Paketzähler aller zehn PCAPs einschließlich dumpcap-Logs, ungültige PCAPs, beide Byteordnungen/Mikro- und Nanosekunden-Magics sowie gezielte TCP-Mutationen. Isolation vor Netzänderungen, Schutz bestehender Belege und Capture-Bereitschaft sind **Offline-Mocktests**, keine neue privilegierte Messung.
- `tcpdump -nn -S -r nachweise/run01/nachher-server.pcap`: **Exit 0**; absolute Handshake-/FIN-Bestätigungen, je drei passende Echo-Request/Reply-Paare und je 28 TCP-Nutzdatenbytes für beide Clients direkt im unabhängigen Decoder nachvollzogen.

## Fachliche Einordnung und Grenzen

- Diagnose korrekt: Server-Default-Gateway `10.10.2.254` statt vorhandenem Router `10.10.2.1`; Hinweg funktioniert, ARP-Auflösung des serverseitigen Rückweg-Next-Hops scheitert. Aktiver Routing-/Neighbor-Zustand und Paketverkehr sind unterschiedliche Beobachtungsarten. Die Diagnose wird im Runner vor der einzigen reparierenden Routenänderung gesichert.
- Der unveränderte Originalclient empfängt ausschließlich die Serverbegrüßung. Die Antworten grenzen das korrekt von der ungenauen Szenarioformulierung eines Client-Nutzdatenversands ab. Kein fehlendes Client-Payload als Programmfehler gewertet.
- Die gespeicherten Zustände belegen vor Reparatur beide fehlgeschlagenen Ping-/TCP-Versuche und nachher je 3/3 Ping-Antworten sowie erfolgreiche Original-TCP-Ausgaben. Die Wiederholungsprüfung hier liest diese Belege; sie erzeugt keine neue Live-Messung und kann die historische Ausführung nicht unabhängig erneut bezeugen.
- **Mininet, OVS, xterm und TCLink-Verzögerungen bleiben ungeprüft.** `messen.py` wurde nur gelesen/importiert und durch Offline-Tests angesprochen, nicht als Netzwerk-Messrunner gestartet. Die kursseitig vorgesehene Originalumgebung muss separat verifiziert werden. Keine Wireshark-GUI-Prüfung behauptet; tcpdump ist laut Angabe zulässig.

Nur diese Datei wurde durch die Review-Arbeit angelegt; keine Lösungskorrektur, kein Commit und kein Zugriff auf Umgebungs-Secrets. Zwei zusätzliche Hilfsprüfungen über beliebigen Python-Code wurden von der Ausführungsrichtlinie blockiert; sie liefen nicht und zählen nicht als bestandene Tests. Die oben genannten regulären Prüfprogramme und tcpdump wurden tatsächlich ausgeführt.
