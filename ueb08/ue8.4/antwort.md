# Ü 8.4 – IP-Kommunikation über ein anderes Subnetz

## Erweiterung

```text
client1 10.0.1.2/24 --- s1 --- router-A 10.0.1.1/24
client2 10.0.1.3/24 ---/        router-B 10.0.2.1/24 --- s2 --- server1 10.0.2.10/24
                                                       \--- server2 10.0.2.11/24
```

Die Routerinterfaces befinden sich im **selben Router-Namespace**. IPv4-Forwarding ist aktiviert. Clients haben Defaultgateway `10.0.1.1`, Server `10.0.2.1`; der Router hat beide Netze als direkt angeschlossene Routen und benötigt für diesen Versuch keine Default- oder statische Zwischenroute. Kein NAT, keine VLANs, keine Tunnel.

Die Originalvorlagen bleiben erhalten; [lab.py](lab.py) baut diese Erweiterung als Mininet-/OVS-Lab mit echter CLI für die Kurs-VM:

```sh
# ab ueb08, nur in der vorbereiteten Mininet-/OVS-Kurs-VM
sudo /usr/bin/python3 -B ue8.4/lab.py
# am mininet>-Prompt
client1 ping -c 1 10.0.1.3
client1 ping -c 1 10.0.2.10
```

**Verifikationsgrenze:** Hier sind Mininet und OVS nicht installiert. Der Starter wurde offline mit Testdoubles geprüft, nicht erfolgreich unter Mininet ausgeführt. Reale Pakete wurden stattdessen mit derselben Adressierung in isolierten Linux-Namespaces und zwei Linux Bridges gemessen. Das beweist die Header-/ARP-/Routing-Eigenschaften, nicht das OVS-API oder xterm-Verhalten.

## Innerhalb eines LANs

[84_lokal.pcap](../nachweise/run01/84_lokal.pcap), Frame 3:
- IP: `10.0.1.2` → `10.0.1.3`.
- MAC: `00:00:00:00:00:01` → `00:00:00:00:00:02`.
- TTL `64`; kein Router beteiligt. Der Switch vermindert die TTL nicht.
- ARP fragt direkt nach `10.0.1.3`.

## Vor und nach dem Router

Zugeordnet ist **derselbe** ICMP Echo Request mit ID `28505`, Sequenz `1`; Transportbytes und IPv4-ID sind ebenfalls identisch. Nicht zwei unabhängig erzeugte Pings vergleichen.

| Feld | LAN A, client1 vor Router, Frame 3 | LAN B, server1 nach Router, Frame 3 |
|---|---|---|
| Source MAC | `00:00:00:00:00:01` | `02:00:00:00:02:01` (router-B) |
| Destination MAC | `02:00:00:00:01:01` (router-A) | `00:00:00:00:00:03` (server1) |
| Source IP | `10.0.1.2` | `10.0.1.2` |
| Destination IP | `10.0.2.10` | `10.0.2.10` |
| TTL | `64` | `63` |
| IPv4-Headerprüfsumme, dezimal | `55588`, gültig | `55844`, gültig |
| EtherType | `0x0800` | `0x0800` |

Belege: [LAN A PCAP](../nachweise/run01/84_lanA.pcap), [LAN B PCAP](../nachweise/run01/84_lanB.pcap), [GUI LAN A](../nachweise/gui/84_router_lanA.png), [GUI LAN B](../nachweise/gui/84_router_lanB.png). Die GUI zeigt genau diese gesicherten Bytes; kein neuer Netzverkehr.

## Antworten

- **Welche MAC-Adressen ändern sich?** Beide: Der Router beendet den eingehenden Ethernet-Frame und erzeugt für LAN B einen neuen Frame mit seiner Ausgangs-MAC als Source und der server1-MAC als Destination. Auf dem Rückweg sendet server1 auf LAN B an router-B (Source `00:00:00:00:00:03`, Destination `02:00:00:00:02:01`); anschließend sendet router-A auf LAN A an client1 (Source `02:00:00:00:01:01`, Destination `00:00:00:00:00:01`).
- **Welche IP-Adressen bleiben gleich?** Für den Request Source `10.0.1.2` und Destination `10.0.2.10`, da kein NAT konfiguriert ist. Für den Reply sind diese beiden Endpunkte vertauscht, bleiben aber über den Router hinweg ebenfalls erhalten. TTL und IPv4-Headerprüfsumme sind nicht Ende-zu-Ende unverändert.
- **Warum ARP für den Next Hop?** `/24` und Routingtabelle zeigen, dass `.2.10` nicht lokal ist. client1 fragt deshalb nach der MAC von **`10.0.1.1`**, nicht nach der MAC von `10.0.2.10`. Der Router fragt auf LAN B nach **`10.0.2.10`**, weil sein Next Hop dort der direkt angeschlossene Zielhost ist. Beide ARP-Request/Reply-Paare stehen in den jeweiligen PCAPs.
- **Warum nicht die entfernte Server-MAC im Client-Frame?** Ethernet-Forwarding endet an der Layer-3-Grenze; ARP-Broadcasts werden nicht in LAN B geroutet. Der Client muss zunächst seinen lokalen Router erreichen. Die entfernte Server-MAC ist erst beim letzten Ethernet-Hop relevant. IP führt das Paket bis zum logischen Ziel.

Die IPv4-Prüfsumme muss wegen der verminderten TTL aktualisiert werden. ICMP-Inhalt samt ICMP-Prüfsumme bleibt in diesem Versuch unverändert. Ethernet-FCS wird je physischem Link neu gebildet, ist in diesen veth-PCAPs aber **nicht enthalten** und daher kein gemessener Wert.

Offline: `python3 -B ue8.4/auswerten.py` ab `ueb08`.

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription), 2026-10-29. Auftrag: Zweites LAN und Router ergänzen, lokale/routende Pings real vergleichen, Headerpaare prüfen und Mininet-Erweiterung samt Tests erklären. Keine Eigenleistung des Studierenden behauptet.
