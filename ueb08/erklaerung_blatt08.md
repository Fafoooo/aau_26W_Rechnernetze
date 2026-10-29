# Erklärung zu Blatt 08

## Was Fabio erklären können sollte

1. **Route vor ARP:** Die Netzmaske und Routingtabelle entscheiden über den nächsten IP-Hop. ARP liefert nur dessen lokale Ethernet-MAC, nicht die MAC irgendeines entfernten Endpunkts.
2. **Zwei verschiedene Caches:** Der Host hält eine IP→MAC-Nachbartabelle; der Switch hält eine MAC→Port-FDB. `ip neigh flush all` und `ovs-appctl fdb/flush s1` betreffen unterschiedliche Geräte und lösen unterschiedliche Effekte aus.
3. **Source Learning:** Der Switch lernt den Absender am Eingangsport. Den Empfänger lernt er erst aus dessen eigener Antwort. Ein ARP-Broadcast wird auch dann verteilt, wenn die FDB den gesuchten Host schon kennt.
4. **Router-Hop:** IP-Endpunkte bleiben ohne NAT dieselben; die Ethernet-Endpunkte wechseln. Die TTL wird kleiner, deshalb muss die IPv4-Headerprüfsumme neu stimmen. TCP und ICMP ändern sich allein durch die TTL nicht.
5. **Vier Schichten:** Für HTTP lassen sich Application, Transport, Network und Link wirklich im selben Paket zeigen. ICMP/Ping allein hat hier keinen TCP-/UDP-Transportheader.

## Dateien und Ablauf

`Angabe/` enthält fremde Original-Infrastruktur unverändert aus Moodle; dafür gibt es keine nachträglich erfundene KI-Kennzeichnung im Quelltext. Die Originaldateien sind anhand des ZIPs getestet. `angabe_blatt08.pdf` ist das Originalblatt.

Die eigenen Programme sind nach Verantwortlichkeit getrennt:
- [messen.py – jede nichtleere Zeile und ihr Zweck](erklaerung_messung.md): Erst äußeren isolierten Netzwerk-Namespace erstellen, dann Host-Namespaces, Bridges und Links. Adressen setzen, Capture-Bereitschaft abwarten, echte Pings und eigene HTTP-Sockets ausführen, PCAPs auswerten und alles schließen. Der Namespace-Worker wartet auf Signale und hält sein privates Netz am Leben; der Server bedient genau eine eigene Verbindung.
- [pcap.py – jede nichtleere Zeile und ihr Zweck](erklaerung_pcap.md): PCAP-Dateikopf und Recordgrenzen, Ethernet und ARP, IPv4-Längen und -Checksumme, ICMP-ID/Sequenz und TCP. Die zwei Routerseiten werden anhand desselben Inhalts zugeordnet, nicht nur anhand gleicher Paketanzahl.
- [test_nachweise.py – jede nichtleere Zeile und ihr Zweck](erklaerung_tests.md): Reale gesicherte Belege erneut lesen; Formatfehler, falsche TTL/MAC/Prüfsummen, fehlende FIN-Bestätigungen, Lücken und widersprüchliche TCP-Retransmissionen als ausdrücklich synthetische Negativkontrollen einstreuen. Sie sind keine erzeugten Messergebnisse.
- [auswertung.py, fünf auswerten.py, ue8.4/lab.py und test_cli_lab.py – jede nichtleere Zeile](erklaerung_cli.md): Die Teilaufgaben-CLIs lesen nur vorhandene Belege. Der zusätzliche Routerstarter ist für die vorbereitete Kurs-VM bestimmt; die Mocktests prüfen seinen Ablauf ohne Mininet-Installation.

`nachweise/run01/` ist ein **abgeschlossener realer Lauf**, kein Ordner zum wiederholten Überschreiben. `results.json` enthält die ursprünglichen Auswertungen; Offline-Auswertung wird damit exakt verglichen. Die Nachbar-/FDB-Snapshots stammen vom tatsächlichen Linux-Kernel. Die elf PCAPs können unabhängig mit tcpdump/Wireshark betrachtet werden. Datei-Hashes schützen vor unbemerkter Änderung der Messbelege.

`nachweise/gui/` enthält echte Wireshark-Screenshots dieser gespeicherten Bytes. Nur `85_schichten_markiert.png` hat nachträglich beschriftete Rahmen; sein unverändertes Original ist daneben gespeichert.

## Gedanklich Schritt für Schritt durch die Messung

### Ü8.1

server1 möchte ein IPv4-Paket an `.1.2` senden. Es erkennt das lokale Subnetz, fragt bei fehlendem Cacheeintrag per ARP nach client1 und sendet danach den Ethernet-Unicast. Der Capture auf client1 sieht beide Richtungen. Ein Echo Request ist ICMP Type 8, der Reply Type 0; nicht nur die Source-IP prüfen, sonst verwechselt man sie.

### Ü8.2

Der geleerte Clientcache erzwingt eine Adressauflösung. Im ersten PCAP folgen Request, Reply, Echo Request, Echo Reply. Unmittelbar beim zweiten Ping reicht derselbe Cacheeintrag. Ein fehlender ARP-Frame ist hier ein überprüfter Befund des kurzen Intervalls, kein dauerhaftes Protokollversprechen.

### Ü8.3

Alle Hostcaches und die dynamische FDB werden kontrolliert geleert. Während client1 sendet, lernt die Bridge dessen Source-MAC; mit server1s Antwort dessen MAC. Bei client2 wiederholt sich die Hostauflösung, aber die Bridge kennt server1s Port bereits. server2 sieht beide ARP-Broadcasts, keinen ICMP-Unicast. Die überlappenden Captures erlauben einen zusätzlichen fremden Broadcast in `83_ping1.pcap`; nicht mechanisch „vier Frames pro Ping“ behaupten.

### Ü8.4

Die Serverlinks werden an eine zweite Bridge verschoben und Server-IPs ins zweite /24 gesetzt. Ein Router mit einer Schnittstelle je LAN vermittelt; beide Endseiten bekommen die passende Default-Route. Die routenden PCAPs gehören zum selben Request und zeigen TTL 64→63. Der lokale Vergleichsping client1→client2 braucht den Router nicht.

### Ü8.5

Der eigene Server meldet erst nach bind/listen Bereitschaft. Erst dann verbindet sich der Client. Er sendet den HTTP-Request vollständig mit `sendall`, schließt nur seine Schreibrichtung und liest bis EOF. Der Server antwortet und schließt ebenfalls geordnet. TCP transportiert einen Bytestrom: `recv` kann beliebige Stücke liefern; deshalb sammeln beide Programme Bytes in begrenzten Schleifen. Der Parser rekonstruiert Nutzdaten nach Sequenznummern und toleriert identische Wiederholungen, aber keine Lücken oder widersprüchliche Überlappungen.

## Kleine Live-Änderungen mit erwarteter Wirkung

- **Nur den zweiten ARP-Ping wiederholen:** Ohne erneutes Flush typischerweise kein frischer Broadcast, solange der Cache nutzbar ist. Nach erneutem Flush wieder ARP erwarten.
- **Nur die FDB leeren:** Ein vorhandener Hostcache kann einen zunächst unbekannten ICMP-Unicast auslösen. Nicht gleichzeitig das Cacheexperiment verändern, wenn genau dieser Effekt untersucht werden soll.
- **Ziel `.1.3` statt `.2.10`:** Direktes lokales Ziel; Client-MAC→client2-MAC, keine Router-TTL-Reduktion.
- **HTTP-Text ändern:** `BODY` ändern; `Content-Length` wird aus `len(BODY)` gebildet. PCAP-Byteprüfungen und gespeicherte Referenzwerte dürfen nicht als passend ausgegeben werden: Einen neuen exklusiven Messlauf und dessen Belege erzeugen.
- **LAN-B-Präfix ändern:** Beide Server, Router-B und Server-Gateways gemeinsam anpassen, danach Host-/Rückrouten prüfen. Die Offline-Modelltests vergleichen die Adressräume, aber ersetzen keinen echten Ping.

Bei einer Frage zu einer einzelnen Zeile zuerst in den verlinkten zeilengenauen Erklärungen nachschlagen. Es gibt keinen erfolgreichen Mininet-Lauf in dieser Umgebung; die echte Linux-Bridge-Messung und synthetischen API-Tests bleiben klar getrennt.

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Blatt08 und jede eigene Programmzeile verständlich und live änderbar erklären; keine Eigenleistung von Fabio behaupten.
