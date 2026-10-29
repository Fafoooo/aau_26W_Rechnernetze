# Wireshark-GUI-Nachweis

Aufgenommen am 2026-10-29 mit Wireshark 4.4.5 auf einem privaten Xvfb-Display. **Keine neue Live-Netzwerkaufzeichnung**: Die unveränderten Bytes der eigenen gesicherten PCAPs aus `../run01/` wurden Wireshark als Standardeingabe zugeführt (`wireshark -n -k -i - -d tcp.port==8080,http`). Dies umgeht keinen Zugriffsschutz auf fremde Daten; der erlaubte Leser liest ausschließlich die eigenen Belege, Wireshark verarbeitet deren Bytefolge. Direkte `-r`-Zugriffe auf Dateien im Repository wurden von der lokalen Laufzeit verweigert; keine Schutzregeln geändert, keine GUI als root ausgeführt.

Der Eingangsname „Standard input“ bzw. `wireshark_Standard input…pcapng` in der Statuszeile ist eine lokale Wireshark-Zwischendatei, **kein anderer Messlauf**. Paketdaten, Zeitstempel, Reihenfolge und Anzahl entsprechen dem jeweiligen Original-PCAP. Screenshots enthalten nur Laboradressen, keine Umgebungskommandos. GUI und Xvfb nach der Aufnahme beendet.

- `81_echo.png`: `81_ethernet.pcap`, Frame 3, server1→client1 Echo Request; vier Echo-Paare, zehn Frames insgesamt.
- `82_arp.png`: `82_erster_ping.pcap`, Frame 1, ARP Request nach client2.
- `84_router_lanA.png`: `84_lanA.pcap`, Frame 3 vor dem Router.
- `84_router_lanB.png`: `84_lanB.pcap`, Frame 3 nach dem Router.
- `85_http.png`: `85_lanA.pcap`, Frame 4 mit Ethernet-/IPv4-Details.
- `85_schichten.png`: derselbe Frame 4, vier Protokollknoten zusammen sichtbar.
- `85_application.png`: derselbe Frame 4 mit geöffnetem HTTP-Header und markierten echten HTTP-Bytes.
- `85_schichten_markiert.png`: **nachträglich beschriftete Kopie** von `85_schichten.png`, vier zusätzliche Rahmen/Pfeile und Schichtnamen. Original liegt separat vor; Paketwerte wurden nicht verändert.

GUI-Screenshots belegen die Wireshark-Analyse der echten Ersatzmessung, **nicht** eine Mininet-/OVS-/xterm-Ausführung. ARP- und Routerprüfungen werden zusätzlich durch unabhängiges `tcpdump` und den Python-PCAP-Parser bestätigt.

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Die gesicherten eigenen PCAPs tatsächlich in Wireshark anzeigen und Schichten nachvollziehbar markieren.
