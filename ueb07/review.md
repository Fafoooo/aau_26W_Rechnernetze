# Unabhängige Prüfung – Blatt 07

## Verfahren

Eine separate KI-Instanz erhielt Angabe und fertige Programme zur unabhängigen zeilenweisen Prüfung. Sie las die Originalvorlagen, Aufgabenantworten und gespeicherten realen Belege und führte unprivilegierte Tests sowie eine eigene `tcpdump`-Analyse der PCAP aus. Keine zusätzlichen Netzänderungen oder Installationen. Modell: OpenAI gpt-6.1-sol über Hermes Agent, Datum 2026-10-29. Keine menschliche Eigenprüfung wird behauptet.

## Befunde und Korrekturen der ersten Runde

1. **Cleanup beim Mininet-Konstruktor:** Aufbau im Konstruktor konnte fehlschlagen, bevor `net` zugewiesen war. Korrektur: `build=False`, danach explizites `net.build()` innerhalb des bestehenden `try/finally`. Regression prüft Build-Fehler als RuntimeError und OSError; kein Start und genau ein Cleanup.
2. **Zu frühe Readiness-Fehler:** Ein einzelner leerer Select-Zyklus brach vor der absoluten Fünfsekundenfrist ab. Korrektur: Leere Antwort setzt die Schleife fort; Restzeit begrenzt das nächste Warten. Tatsächlicher Bereitschaftsmarker bleibt `File: -`. Fünf netzfreie Regressionstests prüfen Idle, Deadline, EOF, aufgeteilte Marker und zu frühes `Capturing on`.
3. **ICMP-Zuordnung:** Der Parser verglich zunächst nur Adressen, Type/Code und Anzahlen. Korrektur: zitiertes Protokoll und Echo-Type/Code, Headergrenzen, Fragmentierung sowie ID/Sequenz prüfen; eindeutige Requests und gleiche Request-/Fehler-Multimengen verlangen. Tests verwerfen doppelte beziehungsweise fehlzugeordnete Fehler. Der bestehende reale Mitschnitt war bereits korrekt; seine JSON-Rückgabe bleibt unverändert.

Die Elterninstanz hat danach beide Testsuiten selbst erneut ausgeführt: 23 Modell-/API-/Dokumentations- und 18 Offline-PCAP-/Readiness-Tests erfolgreich. Die unabhängige `tcpdump`-Auswertung bestätigt für den echten Mitschnitt passende Fehler für die beiden Echo-Sequenzen.

## Nicht als erledigt bewertet

Ein echter Mininet-/xterm-Lauf in der vorgesehenen VM ist weiterhin nicht nachgewiesen. Die echten isolierten Linux-/TC-Messungen und die echte Wireshark-GUI sind separat ausgewiesen. Eine theoretisch plausible Konfiguration oder bestandene Mock-Tests werden nicht als Mininet-Abnahme bezeichnet.
