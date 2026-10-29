# Ü 9.3 – Den Paketfluss verfolgen

## Angabe

ARP, Ethernet, IPv4, TCP-Handshake, ICMP-Fehler und TTL an mehreren Interfaces vergleichen und die erste Abweichung bestimmen.

## Erwarteter Weg

1. Client entscheidet wegen der /24-Maske, dass `10.10.2.10` nicht lokal ist.
2. Client sendet ein IP-Paket mit Ziel-IP `10.10.2.10`, aber Ziel-MAC des Gateways `10.10.1.1`.
3. Router leitet ins Server-LAN weiter. IP-Quell-/Zieladresse und TCP-Segment bleiben erhalten, TTL sinkt von 64 auf 63, die IPv4-Prüfsumme wird angepasst und Ethernet wird neu aufgebaut.
4. Server müsste die Antwort an seinen eigenen Router `10.10.2.1` senden.

## Tatsächlicher fehlerhafter Weg, run01

Die PCAPs liegen in [nachweise/run01](../nachweise/run01/): `vorher-client1.pcap`, `vorher-client2.pcap`, `vorher-router0.pcap`, `vorher-router1.pcap`, `vorher-server.pcap`. Die Aufzeichnung wurde jeweils vor dem Test gestartet; es wurde nichts am fehlerhaften Zustand repariert.

Für client1:

- Am Client/router-eth0: Source-MAC `02:00:00:00:01:10`, Destination-MAC `02:00:00:00:01:01`; IP `10.10.1.10 → 10.10.2.10`, TTL 64.
- Am router-eth1/Server: Source-MAC `02:00:00:00:02:01`, Destination-MAC `02:00:00:00:02:10`; gleiche IPs, TTL 63.
- Frame 6 im `vorher-server.pcap`: erstes SYN von client1, Port `56518 → 5000`; anschließend wiederholte SYNs ohne SYN-ACK auf dem Link.
- Frame 2: Server sendet ARP-Broadcast `who-has 10.10.2.254 tell 10.10.2.10`. Dieser wird bereits durch den vorherigen ICMP-Echo-Versuch ausgelöst. Keine Antwort für `.254`.
- Frames 11/12: ARP für den tatsächlich existierenden Router `.1` und dessen Reply mit `02:00:00:00:02:01`. Der Server kann den richtigen Router erreichen, verwendet ihn aber nicht als Default Gateway.

Für client2:

- LAN1-MACs `02:00:00:00:01:11 → 02:00:00:00:01:01`, IP `10.10.1.11 → 10.10.2.10`, TTL 64.
- LAN2-MACs wieder Router `…02:01 → …02:10`, TTL 63.
- Frame 22 im `vorher-server.pcap`: erstes SYN, Port `42636 → 5000`, danach Wiederholungen und weiter erfolglose ARP-Suche des Servers nach `.254`.

Über beide Clients zusammen: 10 SYN-Pakete an beiden Routerinterfaces zugeordnet; 12 ARP-Anfragen nach `.254`, keine passende Antwort, kein vom Server ausgesendetes TCP-Paket. Der Fehler liegt **nicht im Hinweg**, sondern in der Next-Hop-Auflösung für den serverseitigen Rückweg.

## ICMP und TTL

Beide Clients senden je drei Echo Requests, die den Server erreichen. Kein Echo Reply kommt zurück. Im serverseitigen Vorher-Mitschnitt gibt es weder ICMP Destination Unreachable noch Time Exceeded. Das ist kein Routingloop: genau ein Router vermindert TTL um eins. Aus einem Timeout allein wäre diese Aussage nicht begründbar; Grundlage ist der Vergleich der Mitschnitte.

Ein SYN-ACK kann intern im Server-Kernel zur Übertragung anstehen; das PCAP belegt lediglich, dass **keines auf dem Ethernet-Link ausgesendet wird**, solange die Next-Hop-MAC fehlt. Ein RST als Hinweis auf einen geschlossenen TCP-Port wurde ebenfalls nicht beobachtet.

## Reproduzierbare Auswertung

```sh
python3 ue9.3/pruefen.py
tcpdump -nn -e -vv -r nachweise/run01/vorher-server.pcap
```

Die Frame-Nummern und dynamischen Ports gelten ausschließlich für `run01`, nicht für einen neuen Lauf. `tcpdump`-Ausgabe: [vorher-server-tcpdump.txt](../nachweise/run01/vorher-server-tcpdump.txt). Alle MACs stammen aus dem ausdrücklich gekennzeichneten Linux-Bridge-Nachbau; kein Mininet-/OVS-Nachweis.

## KI-Kennzeichnung

Hermes Agent; OpenAI `gpt-6.1-sol`; ChatGPT or Codex Subscription laut `hermes status`; 2026-10-29. Anfrage: Ü9.3 mit echten, isolierten Vorher-PCAPs lösen, MAC/IP/TTL und ARP-/TCP-Verlauf prüfen und die erste Abweichung belegen.
