# Ü4.4 – UDP-Mitschnitt und TCP/IP-Schichten

## Herkunft

`../nachweise/run01/udp.pcap` ist ein **echter** Mitschnitt unserer Anwendung auf `h1-eth0` in isolierten Linux-Netzwerk-Namespaces (Linux-Bridge, kein Mininet/OVS). Die Adressen entsprechen `standard_mininet.py` mit `/24`. `../nachweise/run01/wireshark-udp.png` zeigt diese Datei in der tatsächlich gestarteten Wireshark-GUI, keine nachgebaute Oberfläche. Drei Pakete sind sichtbar; das erste ist ausgewählt. Die vorbereitete Mininet-VM und zwei xterm-Fenster wurden hier nicht ausgeführt. Das wird nicht durch den Zusatztest ersetzt.

## Alle Fragen, anhand des ersten Datagramms

- **Source IP:** `10.0.0.1` (h1).
- **Destination IP:** `10.0.0.2` (h2).
- **Source Port:** im vorliegenden ersten Paket **54538**, vom Kernel gewählt. Er steht nicht fest im Python-Code und kann sich beim nächsten Lauf ändern.
- **Destination Port:** **5000**, passend zum Server-`bind()` und Clientziel.
- **UDP-Header:** **8 Bytes**: Source Port 2, Destination Port 2, Length 2, Checksum 2.
- **Nutzlast:** `b"Hello from Mininet!"`, **19 Bytes**, ohne zusätzliches LF und ohne abschließendes NUL. UDP-Length ist daher **27 Bytes** (8 + 19); das IPv4-Paket enthält mit dem hier 20-Byte-IP-Header insgesamt **47 Bytes**.
- **Wiedererkennbare Programmwerte:** Zieladresse, Zielport und die gesendeten Bytes. Quelladresse und kurzlebiger Quellport werden beim Senden vom Betriebssystem festgelegt und mit `getsockname()` angezeigt. Die Buffergröße `4096`, Python-Variablennamen und Funktionsnamen stehen nicht als Protokollfelder im Paket.

Die Zahlen und exakten Paketbytes sind zusätzlich maschinell in `udp-analyse.json` bestätigt.

## Weitere echte Datagramme

Zweites Paket: Nachricht `Geänderte Nachricht`, Quellport **59071**. Drittes Paket: Nachricht `Grüße 🌍`, Quellport **55521**. Alle gehen von 10.0.0.1 an 10.0.0.2:5000. Die UTF-8-Nutzlasten stehen als Hex-Bytes in der JSON-Auswertung. Zeichenanzahl und Bytezahl bei Umlauten/Emoji nicht gleichsetzen.

## TCP/IP-Schichten in Wireshark

- **Application:** die Nutzlast `Hello from Mininet!` beziehungsweise die UTF-8-Nachricht; hier kein standardisiertes höheres Protokoll, deshalb zeigt Wireshark `Data`.
- **Transport:** UDP mit Quell-/Zielport, Länge und Checksumme.
- **Internet:** IPv4 mit Quell-/Ziel-IP, TTL und Protokollnummer für UDP.
- **Link/Network Access:** Ethernet II mit Quell-/Ziel-MAC und EtherType IPv4. MAC-Adressen sind nicht die IP-Adressen.
- **Frame** ist Wireshark-Metadaten zum erfassten Frame, keine zusätzliche TCP/IP-Schicht. Eine physische Leitung/Bitübertragung wird hier nicht als eigener Header aufgezeichnet. Ethernet-FCS ist in solchen virtuellen Mitschnitten häufig nicht vorhanden.

## In der bereitgestellten VM selbst aufzeichnen

Zuerst Standardtopologie und Server aus Ü4.3 starten. Der in der Angabe genannte Befehl wird in einer separaten Mininet-Konsole auf h1 ausgeführt, sonst blockiert er dort die weiteren Eingaben:

```text
mininet> h1 tcpdump -i h1-eth0 -n -vv
```

Für die **Payload** zusätzlich `-X` verwenden, da `-vv` allein keine vollständige Hex-/ASCII-Nutzlast verspricht. Zum Speichern eines neuen Mitschnitts im h1-Terminal:

```sh
tcpdump -i h1-eth0 -n -s 0 -U -w udp_vm.pcap 'udp and src host 10.0.0.1 and dst host 10.0.0.2 and dst port 5000' &
CAPTURE_PID=$!
```

Auf die Meldung `listening on h1-eth0` warten, in derselben h1-Konsole den Client ausführen. Danach Capture nicht direkt im selben Moment abbrechen: libpcap kann Pakete zwischenspeichern. Erst wenn das gesendete Paket im Capture angekommen ist, geordnet mit `kill -INT "$CAPTURE_PID"` und `wait "$CAPTURE_PID"` beenden. Unser automatischer Zusatztest verwendet dafür einen begrenzten 5-Sekunden-Capture und wartet dessen reguläres Ende ab. Nur eigenen Lab-Verkehr auf dem zugehörigen Interface erfassen, niemals `any` oder fremden Verkehr.

Die Datei in Wireshark öffnen; Filter `udp.port == 5000`. Erstes Paket anklicken, Ethernet-, IPv4-, UDP- und Data-Baum aufklappen. Ports, Length und Bytes mit der Programmausgabe vergleichen.

## Reproduzierbare unabhängige Byteprüfung

Aus `ueb04`:

```sh
python3 -B ue4.4/analyse_pcap.py nachweise/run01/udp.pcap --kind udp
python3 -B ue4.4/analyse_pcap.py nachweise/run01/tcp.pcap --kind tcp
```

Das Skript unterstützt klassische PCAPs mit Ethernet/unge-taggetem IPv4, keine pcapng/VLAN/IP-Fragmente. Es prüft die konkrete Testfolge, keine beliebigen Netzdumps. Alle Adressen/Ports, exakte Payloads und Längen werden geprüft; bei TCP zusätzlich beide Handshakes, rekonstruierte Byteströme und FIN-Bestätigungen. Es erzeugt keine Pakete. `assert`-Prüfungen nicht durch `python -O` deaktivieren.

TShark konnte hier wegen seiner Dateizugriffsbegrenzung die Repo-PCAPs nicht öffnen; es wurde **kein** Root-Workaround und keine Änderung seiner Sicherheitsregeln vorgenommen. Stattdessen erfolgten die unabhängige stdlib-Auswertung und das echte Öffnen in der Wireshark-GUI.

## KI-Kennzeichnung

Hermes Agent, OpenAI **gpt-6.1-sol**, **2026-10-29**. Anfrage sinngemäß: Ü4.4 vollständig beantworten, ausschließlich eigenen UDP-Verkehr echt erfassen, Felder unabhängig prüfen und den echten Mitschnitt in Wireshark öffnen. KI-gestützte Lösung, keine erfundene persönliche Durchführung durch Fabio.
