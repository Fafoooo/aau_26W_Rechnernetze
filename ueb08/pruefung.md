# Prüfbericht Blatt 08

Stand: 2026-10-29. Keine Moodle-Abgabe, kein ZIP mit erfundener Gruppennummer.

## Echte Ausführung

`sudo -n /usr/bin/python3 -B messen.py` wurde erfolgreich ausgeführt. Netzwerkänderungen fanden ausschließlich nach Erzeugung eines äußeren privaten Netzwerk-Namespace statt; verwendet wurden Linux Bridges, veth und weitere eigene Host-/Router-Namespaces. Elf echte PCAPs mit insgesamt 59 Frames liegen in `nachweise/run01/`. Nachweise und Zähler sind in `results.json`, `pruefung.json`, Capture-Protokollen und unabhängigen tcpdump-Dekodierungen erhalten. Alle eigenen Worker wurden beendet.

- Ü8.1: vier Echo-Paare; Frame 3 server1→client1 mit IPv4-EtherType.
- Ü8.2: ARP-Kaltstart mit Request/Reply, beim unmittelbar folgenden zweiten Ping kein neuer ARP-Frame.
- Ü8.3: dynamische FDB leer → client1/server1 → zusätzlich client2; server2 sieht zwei Broadcasts und keinen ICMP-Unicast. Überlappender erster Clientcapture ausdrücklich dokumentiert.
- Ü8.4: derselbe Request auf beiden Routerseiten, korrektes MAC-Rewriting, unveränderte Endpunkt-IPs, TTL 64→63 und gültig aktualisierte IPv4-Checksumme; lokaler Vergleichsping ohne Router.
- Ü8.5: vollständiger HTTP/TCP-Fluss, zehn TCP-Segmente pro Messpunkt; Handshake, 63 Anfragebytes, 148 Antwortbytes mit 49 Bodybytes, beide FINs bestätigt, kein RST. TCP-Nutzdaten und Prüfsummen unabhängig geprüft.

## Wiederholte Offline-Prüfungen

Tatsächliche Abschlussausgaben: [nachweise/abschluss-tests.txt](nachweise/abschluss-tests.txt).

- `test_nachweise.py`: 13 Tests erfolgreich.
- `test_cli_lab.py`: 5 Tests erfolgreich.
- Alle fünf Teilaufgaben-CLIs mit Standardbelegen und explizitem `--belege` sowie `--help` erfolgreich.
- Offline-Analyse exakt gleich der beim Messlauf gesicherten Analyse.
- Originaldateien bytegenau gleich dem Moodle-ZIP.
- 38 Hash-Einträge im Laufmanifest erfolgreich geprüft; eigener Quellcode und PCAPs durch Offline-Prüfungen nicht verändert. Zwei nachgestellte Leerzeichen in der originalen `ip neigh`-Ausgabe von `befehle.txt` bleiben absichtlich als Rohbeleg erhalten; sie sind keine Quelltextfehler.
- Elf eigene Python-Dateien mit KI-Kommentar, Modell, Datum und sinngemäß tatsächlichem Auftrag; alle fünf Antworten ebenfalls gekennzeichnet.
- Alle nichtleeren eigenen Codezeilen einschließlich Tests individuell erklärt und gegen die echte Quelle abgeglichen; fehlende, doppelte oder veränderte Erklärungszeilen als Negativkontrollen erkannt.
- Lokale Markdown-Verweise vorhanden; keine Buildlogs, Python-Caches oder privaten Umgebungspfade im Blattordner.

## Unabhängige Prüfung

Eine zweite Instanz prüfte Originalangabe, Vorlagen, fertige Quellen, Antworten und gespeicherte Belege eigenständig. Sie führte beide Testsuiten, einen separaten PCAP-/Checksum-Prüfer und alle CLIs aus und kontrollierte GUI-Screenshots. Ein Dokumentationsbefund wurde übernommen: Die Rückwegrichtung in Ü8.4 ist jetzt explizit server1→router-B auf LAN B und router-A→client1 auf LAN A. Die unabhängige Paketprüfung bestätigt genau diese Richtungen. Keine weiteren fachlichen/technischen Befunde.

## GUI und offene Grenze

Echte [Wireshark-Screenshots](nachweise/gui/README.md) zeigen die gesicherten Pakete. Vier Protokollschichten sind im Original und einer getrennten, klar beschrifteten Kopie sichtbar. Die GUI lief unprivilegiert auf einem privaten Xvfb-Display; gespeicherte eigene Bytes wurden per stdin wiedergegeben, kein neuer Live-Capture auf realen Hostinterfaces. Eigene GUI-/Displayprozesse beendet.

**Offen:** erfolgreicher Lauf der Mininet-/OVS-Kurs-VM samt Switch-Monitor-xterm und der neuen Mininet-Routererweiterung. Mininet/OVS sind hier nicht vorhanden; echte Startversuche endeten mit `ModuleNotFoundError: No module named 'mininet'`. Keine Installation oder Schutzregeländerung vorgenommen. Mocktests prüfen Ablauf, Routeradressierung, Default-/Rückwege und Cleanup bei Fehlern, sind aber ausdrücklich kein Mininet-Lauf. Die Antworten trennen diese Grenze von den echten Linux-Bridge-Messungen.

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol (Provider laut Status: ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Vollständige Lösung und echte Tests von RN Blatt08, unabhängige Prüfung und verständliche Erklärung. Keine Eigenleistung von Fabio behauptet.
