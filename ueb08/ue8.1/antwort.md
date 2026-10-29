# Ü 8.1 – Ethernet-Frames beobachten

## Durchführung und Beleg

Die Originalvorlage konfiguriert client1 als `10.0.1.2/24`, client2 als `10.0.1.3/24`, server1 als `10.0.1.10/24` und server2 als `10.0.1.11/24`. Insbesondere ist `.3` **client2**, nicht server1. Die MACs sind mit `autoSetMacs=True` in der Hostreihenfolge `...:01` bis `...:04` vorgesehen; vor Ort mit `ip link` kontrollieren.

Die gespeicherten Messungen stammen von vier echten Linux-Netzwerk-Namespaces an einer Linux Bridge, **nicht** von Mininet/OVS. Adressen und MACs entsprechen der Vorlage. Aufzeichnung nur am eigenen `client1-eth0`, vier Pings von server1 nach client1. Belege:
- [PCAP](../nachweise/run01/81_ethernet.pcap), [tcpdump-Ausgabe](../nachweise/run01/81_ethernet.pcap.decodiert.txt).
- [Wireshark-Screenshot, Echo Request Frame 3](../nachweise/gui/81_echo.png).
- Erneut auswerten, ab `ueb08`: `python3 -B ue8.1/auswerten.py`.

## Identifizierter Echo Request

Frame 3 in `81_ethernet.pcap`:
- Source MAC: `00:00:00:00:00:03` (server1).
- Destination MAC: `00:00:00:00:00:01` (client1).
- Source IP: `10.0.1.10`.
- Destination IP: `10.0.1.2`.
- EtherType: `0x0800` = IPv4; darin IP-Protokoll `1` = ICMP und ICMP Type `8`, Code `0` = Echo Request.

Die Datei enthält zwei ARP-Frames und acht ICMP-Frames: vier Echo Requests, vier Echo Replies. Der Switch ist **nicht** die Destination MAC dieses Host-zu-Host-Frames; er leitet ihn weiter, ohne Source/Destination MAC umzuschreiben.

## Warum MAC und IP?

Ethernet überträgt einen Frame im lokalen Layer-2-Netz. Der Switch verwendet dessen Ziel-MAC zur Auswahl des Ausgangsports. Die Quell-MAC zeigt ihm, über welchen Eingangsport der Sender erreichbar ist.

IPv4 bezeichnet die logischen Kommunikationsendpunkte. Die Netzmaske entscheidet zusammen mit der Routingtabelle, ob die Ziel-IP direkt erreichbar ist oder ein Gateway benötigt wird. Innerhalb dieses LANs gehört die Ethernet-Ziel-MAC zum Zielhost; über einen Router gehört sie zum lokalen Next Hop. Die IP-Zieladresse bleibt dabei die des entfernten Endpunkts, sofern kein NAT verwendet wird.

## Nachstellen in der Kurs-VM

`Angabe/start_lab.py` öffnet Hostterminals, keine Mininet-CLI. In client1 zunächst die Aufzeichnung starten, in server1 danach den Ping:

```sh
# client1-Terminal; eigenen Ausgabeordner vorher anlegen
tcpdump -i client1-eth0 -nn -e -s 0 -w ethernet.pcap 'arp or icmp'
# server1-Terminal
ping -c 4 10.0.1.2
```

Nach dem letzten Reply die Aufzeichnung mit Strg+C beenden. In Wireshark `icmp.type == 8` filtern, Ethernet II und Internet Protocol Version 4 öffnen. Für den bereitgestellten Beleg ist der erste Request Frame 3; neue Messungen können andere Framenummern haben.

**KI-Kennzeichnung:** Erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (Provider laut Status: ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Blatt08 vollständig lösen, echte Ethernet-/ARP-/Switch-/Router-Pakete messen, testen und erklären. Keine Eigenleistung des Studierenden behauptet.
