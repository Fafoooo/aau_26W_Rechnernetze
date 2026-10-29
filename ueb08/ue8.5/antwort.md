# Ü 8.5 – Wireshark-Schichtenanalyse

## Gewählter vollständiger Fluss

Eigener HTTP/1.1-Abruf von client1 `10.0.1.2:40080` nach server1 `10.0.2.10:8080`, über den Router aus Ü8.4, ohne NAT/TLS. Diese echte Verbindung enthält **10 TCP-Pakete je LAN-Messpunkt**:

1. Frames 1–3: SYN, SYN/ACK, ACK (Verbindungsaufbau).
2. Frame 4: `GET /blatt08 HTTP/1.1`, `Host: server1.lab`, `Connection: close` (63 Anfragebytes).
3. Frame 5: ACK des Servers.
4. Frame 6: clientseitiges FIN/ACK. Der Client verwendet `shutdown(SHUT_WR)`; das schließt nur die Senderichtung, er kann die Antwort noch empfangen.
5. Frame 7: `HTTP/1.1 200 OK`, `Content-Type: text/plain; charset=utf-8`, `Content-Length: 49`, `Connection: close`, plus 49 Bodybytes. Die gesamte HTTP-Antwort umfasst 148 Bytes.
6. Frames 8–10: ACK, serverseitiges FIN/ACK, abschließendes ACK. Beide FINs sind bestätigt, kein RST.

Der Body lautet `RN Blatt08: echte Pakete, zwei LANs, ein Router.` plus Zeilenumbruch. Ein HTTP/1.1-Request mit `Host`-Header erfordert hier keine DNS-Abfrage: Der eigene Socket-Client verbindet direkt zur IP; `server1.lab` ist ein HTTP-Headerwert, kein öffentlich aufgelöster Name.

Belege: [LAN A](../nachweise/run01/85_lanA.pcap), [LAN B](../nachweise/run01/85_lanB.pcap), [vollständige tcpdump-Dekodierung LAN A](../nachweise/run01/85_lanA.pcap.decodiert.txt), [Testergebnisse](../nachweise/run01/tests.txt).

## Markierte Wireshark-Schichten

[Unveränderte GUI-Ansicht mit vier Schichten](../nachweise/gui/85_schichten.png), [zusätzlich beschriftete Kopie](../nachweise/gui/85_schichten_markiert.png), [geöffneter HTTP-Header](../nachweise/gui/85_application.png). Die Beschriftungen auf der Kopie ordnen echte GUI-Zeilen zu; Paketbytes und Werte wurden nicht verändert.

In Frame 4, unten links im Paketdetailbaum, von außen nach innen:
- **Link:** `Ethernet II`.
- **Network:** `Internet Protocol Version 4`.
- **Transport:** `Transmission Control Protocol`.
- **Application:** `Hypertext Transfer Protocol`.

`Frame` ist Wireshark-Aufzeichnungsmetadaten, keine zusätzliche Protokollschicht auf dem Draht. Für Ping wäre ICMP ein Kontrollprotokoll der Netzwerkschicht; Ping hätte hier **keinen TCP-/UDP-Transportheader und keinen HTTP-Header**. Deshalb wurde zusätzlich ein vollständiger HTTP/TCP-Fluss gemessen.

## Kurze Header-Tabelle

| Schicht | Wichtigste Information, Request Frame 4 | Am Router-Hop ohne NAT |
|---|---|---|
| Application, HTTP | `GET /blatt08 HTTP/1.1`; `Host: server1.lab`; `Connection: close` | HTTP-Header und Body unverändert |
| Transport, TCP | Source Port `40080`, Destination Port `8080`; relative Seq `1`, Ack `1`; 63 Nutzdatenbytes | Ports, Sequenz-/ACK-Nummern, Flags, Optionen, Window und TCP-Prüfsumme dieses Segments unverändert |
| Network, IPv4 | Source `10.0.1.2`, Destination `10.0.2.10`, Protokoll `6` | Endpunkt-IPs bleiben; TTL `64` → `63`, IPv4-Headerprüfsumme wird aktualisiert |
| Link, Ethernet II | Source `00:00:00:00:00:01`, Destination `02:00:00:00:01:01`, EtherType `0x0800` | Neuer Frame: Source `02:00:00:00:02:01`, Destination `00:00:00:00:00:03`; EtherType weiter IPv4 |

Relative TCP-Nummern werden von Wireshark zur Lesbarkeit auf den Verbindungsanfang bezogen. Die echten absoluten Nummern sind in den PCAPs und `results.json` enthalten. Sender und Empfänger senden unterschiedliche Segmente: Ende-zu-Ende erhalten bedeutet **dasselbe Segment vor/nach dem Router**, nicht dass alle Segmente der ganzen Verbindung identische Flags/Window/ACK-Werte hätten.

TCP prüft einen Pseudoheader mit Source-IP, Destination-IP, Protokoll und Länge, aber **ohne TTL**. Daher zwingt die TTL-Änderung nicht zur TCP-Prüfsummenänderung. Der Parser bestätigt die unveränderten TCP-Bytes beider Messpunkte sowie gültige IPv4- und TCP-Prüfsummen. Ohne Fragmentierung, NAT oder Mittelsysteme wie Proxies bleibt der Transportinhalt hier erhalten. Ethernet-FCS fehlt in diesen PCAPs; keine gemessene FCS behaupten.

## In Wireshark nachvollziehen

PCAP öffnen, `tcp.port == 8080` filtern. Falls HTTP nicht automatisch erkannt wird: „Analyze → Decode As…“, TCP-Port 8080 als HTTP setzen. Frame 4 auswählen; die vier genannten Baumknoten aufklappen. Frame 7 für den Response und „Follow → TCP Stream“ für den zusammengefügten HTTP-Text verwenden. Mit `tcp.flags.syn == 1 || tcp.flags.fin == 1 || tcp.flags.reset == 1` Aufbau/Abschluss kontrollieren. Framenummern gelten für die bereitgestellten Belege, nicht beliebige neue Läufe.

Offline: `python3 -B ue8.5/auswerten.py` ab `ueb08`.

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Vollständigen eigenen HTTP/TCP-Fluss auf beiden Routerseiten messen, in Wireshark vier Schichten markieren und Ende-zu-Ende-/Hop-Felder mit realen Belegen prüfen. Keine Eigenleistung des Studierenden behauptet.
