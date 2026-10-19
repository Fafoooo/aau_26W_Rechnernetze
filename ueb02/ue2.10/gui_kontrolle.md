# Unabhängige Wireshark-GUI-Kontrolle

**Durchführung:** 19.10.2026, Wireshark 4.4.5, echte GUI unter Xvfb. Originale `../Angabe/dump_protocols.pcap` und `../Angabe/dump_http.pcap` geöffnet; je Datei Statistics → Protocol Hierarchy sowie Statistics → Conversations → TCP. Anzeigefilter leer; „Limit to display filter“ aus. CSV-Export direkt aus dem GUI-Dialog, Conversations mit „Save data as raw“. Die gespeicherten CSVs sind die Primärnachweise; die Screenshots zeigen dieselben Dialoge.

## dump_protocols.pcap – Protocol Hierarchy

| Hierarchieebene | Pakete/erkannte Einheiten in GUI | Bytes-Spalte in GUI |
|---|---:|---:|
| Frame | 39 | 4167 |
| └ Ethernet | 39 | 612 |
| 　 ├ IPv4 | 29 | 580 |
| 　 │ ├ UDP | 9 | 72 |
| 　 │ │ ├ DHCP | 3 | 934 |
| 　 │ │ └ DNS | 6 | 226 |
| 　 │ ├ TCP | 16 | 352 |
| 　 │ │ └ HTTP | 2 | 243 |
| 　 │ │ 　 └ Line-based text data | 1 | 577 |
| 　 │ └ ICMP | 4 | 256 |
| 　 └ ARP | 10 | 280 |

**Wichtige Unterscheidung:** „Frame“ ist Wiresharks Metadatensatz, „Line-based text data“ ist die Darstellung des HTTP-Inhalts. Beide sind keine zusätzlichen Protokollschichten des TCP/IP-Modells. Der Bytezähler von Wireshark 4.4.5 in Protocol Hierarchy zählt hier die der jeweiligen Ebene zugeordneten Bytes; er ist **nicht** die Summe kompletter Frame-Längen aller Pakete dieser Ebene. Beispielsweise TCP-Hierarchie 352 B, TCP-Conversation insgesamt 1763 B. Die CSV hält auch Prozentwerte, End-Packets und PDUs fest.

## dump_protocols.pcap – TCP Conversations

Genau **eine** TCP-Conversation, Stream-ID 0:

| Endpunkt A | Endpunkt B | Pakete | Bytes gesamt | A → B | B → A | Relativer Start | Dauer |
|---|---|---:|---:|---|---|---:|---:|
| 192.168.1.215:54961 | 192.168.1.1:80 | 16 | 1763 | 8 Pakete / 567 B | 8 Pakete / 1196 B | 16.998177 s | 0.007399 s |

Die GUI-CSV gibt die Dauer binärbedingt als `0.007399000000003042` aus; `0.007399 s` ist die passende Dezimaldarstellung der Zeitstempelauflösung. Die Zahl ist klein, aber der tatsächliche GUI-Wert, kein Sekunden/Millisekunden-Vertauschen.

## dump_http.pcap – Protocol Hierarchy

| Hierarchieebene | Pakete/erkannte Einheiten in GUI | Bytes-Spalte in GUI |
|---|---:|---:|
| Frame | 68 | 37475 |
| └ Ethernet | 68 | 952 |
| 　 └ IPv4 | 68 | 1360 |
| 　 　 └ TCP | 68 | 2224 |
| 　 　 　 └ HTTP | 6 | 1284 |
| 　 　 　 　 ├ Portable Network Graphics | 1 | 27065 |
| 　 　 　 　 ├ Line-based text data | 1 | 145 |
| 　 　 　 　 └ Compuserve GIF | 1 | 4445 |

HTTP kann sich über mehrere TCP-Segmente erstrecken; die hier gezählten HTTP-Dissektionen sind nicht gleichbedeutend mit allen TCP-Segmenten mit HTTP-Nutzbytes. PNG/GIF/Text sind HTTP-Inhalte, nicht neue Transportprotokolle. Die Reihenfolge der drei HTTP-Inhaltszeilen ist die der GUI.

## dump_http.pcap – TCP Conversations

Genau **drei** TCP-Conversations:

| Stream | Endpunkt A | Endpunkt B | Pakete | Bytes gesamt | A → B | B → A | Relativer Start | Dauer |
|---:|---|---|---:|---:|---|---|---:|---:|
| 0 | 192.168.3.10:37184 | 192.168.1.10:80 | 10 | 1236 | 5 Pakete / 476 B | 5 Pakete / 760 B | 0 s | 0.301299 s |
| 1 | 192.168.3.10:37185 | 192.168.1.10:80 | 14 | 5814 | 7 Pakete / 616 B | 7 Pakete / 5198 B | 0.201532 s | 0.301248 s |
| 2 | 192.168.3.10:37186 | 192.168.1.10:80 | 44 | 30425 | 22 Pakete / 1616 B | 22 Pakete / 28809 B | 0.402796 s | 0.502194 s |

Die Conversations-Bytezahlen zählen komplette aufgezeichnete Frame-Längen beider Richtungen, **nicht nur TCP-Nutzdaten oder HTTP-Objektgrößen**. Die Dauer ist der Zeitabstand zwischen erstem und letztem zur Conversation gehörendem aufgezeichneten Paket, nicht die Dauer des HTTP-Downloads allein und nicht notwendigerweise die Lebensdauer außerhalb des Mitschnitts.

## Dateien

- `gui_protocol_hierarchy_protocols.csv` / `.png`
- `gui_tcp_conversations_protocols.csv` / `.png`
- `gui_protocol_hierarchy_http.csv` / `.png`
- `gui_tcp_conversations_http.csv` / `.png`

Die Werte dienen als unabhängige Kontrolle neben der Scapy-Analyse des Hauptbearbeiters. Sie wurden aus der GUI extrahiert und nicht aus dessen Berechnung übernommen.

## KI-Kennzeichnung

Hermes Agent, OpenAI gpt-6.1-sol, 19.10.2026. Anfrage (sinngemäß): „Ü2.10 praktisch durchführen und, wenn möglich, Protocol Hierarchy und TCP Conversations der bereitgestellten Dumps aus der echten GUI als unabhängige Kontrolle für Ü2.11/Ü2.12 liefern.“
