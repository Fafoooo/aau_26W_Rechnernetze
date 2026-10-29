# Ü 8.2 – ARP beobachten

## Durchführung

Im eigenen client1-Namespace `ip neigh flush all`, danach `ip neigh`: leer. Dann ein Ping auf `10.0.1.3` (client2), Nachbartabelle lesen; unmittelbar nach der ersten kurzen Aufzeichnung zweiter Ping ohne erneutes Leeren. PCAPs mit Ethernet-Headern:
- [Erster Ping](../nachweise/run01/82_erster_ping.pcap): vier Frames.
- [Zweiter Ping](../nachweise/run01/82_zweiter_ping.pcap): zwei Frames.
- [Zustand vorher/nachher](../nachweise/run01/zustand.txt), [Wireshark ARP Request](../nachweise/gui/82_arp.png).
- Offline: `python3 -B ue8.2/auswerten.py` ab `ueb08`.

Dies sind echte Messungen mit Linux Bridge, kein Mininet-/OVS-Nachweis.

## Request und Reply

Frame 1 des ersten PCAP:
- Ethernet Source `00:00:00:00:00:01`, Destination `ff:ff:ff:ff:ff:ff` (Broadcast).
- EtherType `0x0806` = ARP, Opcode `1` = Request.
- Sender-IP `10.0.1.2`, Sender-MAC `00:00:00:00:00:01`.
- Gesuchte Target-IP **`10.0.1.3`**, unbekannte Target-MAC `00:00:00:00:00:00`.
- Inhalt: „Wer hat 10.0.1.3? Antworte 10.0.1.2.“

Frame 2:
- Ethernet Source `00:00:00:00:00:02`, Destination `00:00:00:00:00:01` (Unicast).
- ARP Opcode `2` = Reply.
- Sender-IP `10.0.1.3`, zurückgelieferte Sender-MAC **`00:00:00:00:00:02`**.
- Target-IP `10.0.1.2`, Target-MAC `00:00:00:00:00:01`.

Danach folgen der ICMP Echo Request und Echo Reply. ARP ist kein IPv4-Paket: Die IP-Adressen stehen hier in den ARP-Feldern, nicht in einem IPv4-Header.

## Warum vor IP-Kommunikation?

Die Route sagt: `.3` ist im direkt angeschlossenen `/24`. Zum Verpacken des IPv4-Pakets in einen Ethernet-Frame fehlt dem Client die Ziel-MAC. ARP ermittelt diese aus der lokalen IPv4-Adresse; währenddessen kann der Kernel das IP-Paket zurückhalten. Nach der Antwort kann er den Unicast-Frame senden.

Nach dem ersten Ping lautet der gesicherte Cacheeintrag:

```text
10.0.1.3 dev client1-eth0 lladdr 00:00:00:00:00:02 REACHABLE
```

## Zweiter Ping

Beim unmittelbar folgenden Ping ist derselbe Eintrag noch gültig. Der Client sendet direkt ICMP; die zweite Datei enthält **keinen ARP-Frame**. Das bedeutet nicht, dass nie wieder ARP auftritt: Nach Ablauf/Änderung des Cachezustands kann Linux die Erreichbarkeit neu prüfen, gegebenenfalls zuerst per Unicast-Probe.

## Nachstellen in der Kurs-VM

Im client1-Terminal vor dem Ping einen Capture starten (zweites Terminal desselben Hosts oder Hintergrundprozess). `tcpdump -i client1-eth0 -nn -e arp` zeigt nur ARP; für die Reihenfolge einschließlich ICMP `arp or icmp` verwenden. Zum sicheren Vergleich beide Pings jeweils vollständig aufzeichnen und nicht dazwischen flushen. Wireshark-Filter: `arp`; Details: `arp.opcode`, `arp.src.proto_ipv4`, `arp.src.hw_mac`, `arp.dst.proto_ipv4`.

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: ARP-Auflösung und Cacheverwendung bei zwei realen Pings messen, auswerten und erklären. Keine Eigenleistung des Studierenden behauptet.
