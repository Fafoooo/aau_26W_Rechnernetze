# Ü 8.3 – Switch Learning

## Vorbereitung und Abgrenzung

Die Originaldatei `Angabe/start_lab_monitor.py` startet zuerst sechs Connectivity-Pings. Dadurch sind FDB und Host-Nachbarcaches vorgewärmt. Anschließend leert sie mit `ovs-appctl fdb/flush s1` **nur die FDB**, nicht die ARP-Caches. In der PDF steht `ocs-appctl`; korrekt ist **`ovs-appctl`**, wie in der Vorlage.

Für einen kontrollierten ARP-Kaltstart müssen zusätzlich auf allen vier Hosts die Nachbartabellen geleert werden. Die gesicherten Messungen tun dies und leeren die dynamischen FDB-Einträge der eigenen Linux Bridge. **Diese FDB wurde mit `bridge -j fdb show br brA` ausgelesen, nicht mit OVS.** Mininet-/OVS-Ausführung und das Monitor-xterm bleiben in der Kurs-VM nachzuprüfen.

## Start, nach Ping1, nach Ping2

Beleg: [Zustand mit drei FDB-Snapshots](../nachweise/run01/zustand.txt). Die Portnamen `p1` bis `p4` sind die Linux-Bridge-Ports dieses Nachweises, keine gemessenen OVS-Portnummern.

- **Start:** Keine dynamisch gelernten MACs. Permanente Eigen-/Multicast-Einträge sind nicht Teil dieser Betrachtung.
- **Ping1, client1 → server1 (`10.0.1.10`):** client1 sendet einen ARP-Broadcast. Beim Empfang lernt die Bridge Source-MAC `00:00:00:00:00:01` → `p1`. Sie verteilt den Broadcast an die übrigen Ports. server1 antwortet mit Source-MAC `00:00:00:00:00:03`; die Bridge lernt → `p3` und erreicht client1 bereits gezielt über `p1`. Nach dem Ping sind genau client1→p1 und server1→p3 dynamisch bekannt.
- **Ping2, client2 → server1:** client2 löst nach dem Kaltstart server1 per ARP auf. Sein Broadcast lernt Source-MAC `00:00:00:00:00:02` → `p2`. Der ARP-Reply und die folgenden ICMP-Unicasts werden zu den bekannten Zielports weitergeleitet. Danach sind client1→p1, client2→p2, server1→p3 bekannt.
- **server2:** Kein eigener gesendeter Frame, daher kein dynamischer Eintrag für `...:04`. Ein empfangener Broadcast allein bringt den Switch nicht dazu, dessen Empfänger-MAC zu lernen.

[PCAP am unbeteiligten server2](../nachweise/run01/83_server2_zeuge.pcap): genau **zwei ARP Requests als Broadcast**, **kein ICMP-Frame**. Damit sind Broadcast-Flooding und gezieltes ICMP-Forwarding im kontrollierten Lauf unterschieden.

`83_ping1.pcap` hat fünf Frames, nicht nur vier: Die Aufzeichnungen überlappen zeitlich; der spätere client2-ARP-Broadcast erreicht auch client1. [tcpdump-Dekodierung](../nachweise/run01/83_ping1.pcap.decodiert.txt) zeigt dessen Sender `10.0.1.3`. FDB-Snapshots sind jeweils unmittelbar nach ihrem Ping aufgenommen.

## Lernregel

1. Ethernet-Frame kommt auf einem Port an.
2. **Quell-MAC** plus Eingangsport werden gespeichert bzw. aktualisiert; der Timer wird erneuert.
3. Bei bekannter Unicast-Ziel-MAC wird nur zum zugehörigen Ausgangsport weitergeleitet; liegt das Ziel am Eingangsport, wird der Frame nicht dorthin zurückgesendet.
4. Unbekannter Unicast wird im VLAN an alle übrigen zulässigen Ports geflutet. Ein Broadcast wird unabhängig davon geflutet, ob die Zielhost-MAC anderweitig bekannt ist.
5. Einträge altern, damit umgezogene oder verschwundene Hosts nicht dauerhaft am alten Port stehen.

Ein Ping muss **nicht zuerst als ICMP geflutet werden**: Beim ARP-Kaltstart hat der Switch die relevanten MACs bereits aus ARP Request/Reply gelernt. Wenn der ARP-Cache dagegen warm und nur die FDB leer ist, kann der erste ICMP-Unicast zunächst unbekannt sein und geflutet werden.

## OVS-Monitor in der Kurs-VM

```sh
# ab ueb08/Angabe in der vorbereiteten Kurs-VM mit grafischer Sitzung
sudo /usr/bin/python3 start_lab_monitor.py
# das zusätzliche Switch-Monitor-Terminal führt aus:
watch -n 0.5 'sudo ovs-appctl fdb/show s1'
```

Vor dem Experiment `ovs-ofctl show s1` zur Zuordnung der OVS-Portnummern lesen. Für kontrolliert kalte Hosts jeweils `ip neigh flush all`, am Switch erneut `ovs-appctl fdb/flush s1`; danach client1 `ping -c 1 10.0.1.10`, Snapshot, anschließend client2 denselben Ping, Snapshot. Für den Warm-ARP-Sonderfall die IP/MAC-Zuordnung vor dem FDB-Leeren sichern oder gezielt setzen. Keine Linux-Portnummern als OVS-Messung übernehmen.

Offline: `python3 -B ue8.3/auswerten.py` ab `ueb08`.

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Source-MAC-Learning und Flooding bei zwei realen Pings untersuchen; Unterschiede zwischen OVS-Vorlage und isolierter Linux-Bridge-Messung ausdrücklich dokumentieren. Keine Eigenleistung des Studierenden behauptet.
