# 6.7 – Weiteren Client hinzufügen

## Änderung und Adressierung

Arbeitskopie: [`topology.py`](topology.py). Die Originale unter `../Angabe/` bleiben unverändert. Der explizite Auftrag 6.7 erlaubt die Änderung ab dieser Aufgabe; die pauschale Angabe „nicht verändern“ im Anhang und „Ü 6.8“ in den Vorlagekommentaren sind dazu widersprüchlich. Die Änderung beschränkt sich auf eine separate Arbeitskopie und einen zusätzlichen Starter.

```text
client 10.0.1.2/24 ──┐
                     s1 ── r1 ── r2 ── server 10.0.2.2/24
client2 10.0.1.3/24 ─┘
```

1. `client2 = addHost(...)` legt einen zusätzlichen Host mit eigenem Netzwerk-Namespace an.
2. `s1` ist eine `OVSBridge` (lokal lernender Ethernet-Switch ohne externen Controller). Er verbindet beide Clients und `r1-eth0` auf Layer 2. Eine zusätzliche direkt an r1 angeschlossene, geroutete Schnittstelle im selben /24 wäre **kein** gemeinsames LAN; ARP-Broadcasts werden nicht zwischen solchen Ports geroutet. Deshalb wird der bisherige einzelne Client-Link durch drei Switch-Links ersetzt.
3. Die ursprünglichen Host-Interface-Namen bleiben erhalten. `client2-eth0` ist neu; die Switchports heißen `s1-eth1`, `s1-eth2`, `s1-eth3`. Auf s1 liegt keine IP-Adresse und er ist kein zusätzlicher IP-Hop.
4. Der Zusatzstarter importiert die unveränderte Basiskonfiguration, setzt `client2-eth0` auf `10.0.1.3/24` und die Default Route auf `10.0.1.1`. Netzwerk `10.0.1.0`, Broadcast `10.0.1.255`; .3 ist frei und weder Netzadresse noch Broadcast noch Gateway.
5. r1 und r2 behalten ihre Transitadressen und statischen /24-Routen. Die Rückroute von r2 nach `10.0.1.0/24` deckt **beide** Clients ab. Keine /32-Zusatzroute ist nötig.
6. Der Starter prüft Pings von beiden Clients zum Server und vom Server zu client2 mit Exitstatus **und** genau drei empfangenen Paketen. Danach öffnet er eine echte Mininet-CLI.

## Start und Test in der vorbereiteten Mininet/OVS-VM

Vom Repository-Verzeichnis aus:

```sh
cd ueb06/ue6.7
sudo python3 -B start_erweitert.py
```

In der dann angezeigten **Mininet-CLI**:

```text
client2 ip -br addr
client2 ip route
client2 ping -c 3 10.0.2.2
server ping -c 3 10.0.1.3
server python3 -u -B ../Angabe/tcp_server.py > /dev/null 2>&1 &
client python3 -B ../Angabe/tcp_client.py
client2 python3 -B ../Angabe/tcp_client.py
exit
```

Der originale `start_lab.py` öffnet Konsolen und wartet nur mit `input()`; dort existiert keine Mininet-CLI. Der Zusatzstarter verwendet stattdessen `CLI(net)`. Der Originalstarter wird nicht geändert. Bei fehlender Mininet-/OVS-Installation muss die vorbereitete VM benutzt werden; die Musterbefehle sind kein Beleg für einen hier erfolgten Mininet-Lauf.

## Warum beide TCP-Anwendungen unverändert bleiben

- Der Client verbindet sich ausschließlich mit `10.0.2.2:5000`. Er bindet keine feste Quelladresse. Das Betriebssystem wählt beim zweiten Client automatisch `10.0.1.3` als Quelle und einen lokalen dynamischen Quellport.
- Der Server bindet unverändert an `10.0.2.2:5000`. Nach `accept()` verarbeitet er die ankommende Verbindung, unabhängig davon, welcher der beiden Clients sie aufgebaut hat.
- Das ursprüngliche Serverprogramm verarbeitet die Clients **nacheinander**, nicht parallel. Die drei Echo-Nachrichten des ersten Clients werden abgeschlossen, bevor der zweite gestartet wird.
- IP-Routing und Ethernet/ARP transportieren die TCP-Segmente. Die Anwendungen müssen über Zwischenrouter und Switch keine Kenntnis besitzen.
- Hinweis zur Vorlage: `sendall()` sendet alle Bytes, aber `recv(4096)` garantiert weder eine vollständige Nachricht noch eine bestimmte Anzahl Bytes. Für die drei kurzen sequentiellen Lab-Nachrichten wurde der tatsächliche Echo-Inhalt geprüft; eine allgemeine Framing-Garantie folgt daraus nicht. Die ausdrücklich unverändert zu lassende Vorlage wird nicht stillschweigend verbessert.

## Tatsächlich ausgeführte Prüfung und Grenze

[`../nachweise/run01/results.json`](../nachweise/run01/results.json) dokumentiert einen **realen Linux-Namespace-Zusatztest, nicht Mininet**. Die erweiterte LAN-Struktur wurde mit einer isolierten Linux-Bridge anstelle von OVS aufgebaut. Die unveränderten Originalprogramme aus `Angabe/` liefen als echte Prozesse:

- alter Client: alle drei Echo-Nachrichten korrekt;
- neuer Client: alle drei Echo-Nachrichten korrekt;
- beide TCP-Verbindungen am Server beobachtet;
- client2 zum alten Client sowie Server zu client2: je 3/3 Ping-Antworten;
- Routenlöschung: 0/3, nach Wiederherstellung: 3/3 beim alten Client.

Belege: [`erweitert-client2-tcp.txt`](../nachweise/run01/erweitert-client2-tcp.txt), [`erweitert-server-tcp.txt`](../nachweise/run01/erweitert-server-tcp.txt), [`erweitert-server-ping-10.0.1.3.txt`](../nachweise/run01/erweitert-server-ping-10.0.1.3.txt).

**⚠️ Mininet/OVS/GUI sowie TCLink-Verzögerungen sind auf diesem Rechner mangels vorhandener Programme nicht verifiziert.** Der Namespace-Lauf beweist Routing, gemeinsamen L2-Bereich und unveränderte Anwendungen; er ersetzt nicht den noch auszuführenden VM-Test. Topologie-API-Tests mit Test-Doubles prüfen nur Struktur, nicht OVS-Laufzeit.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter laut `hermes status`: ChatGPT or Codex Subscription. Datum: 2026-10-29. Anfrage: RN-Übungsblatt06 vollständig lösen; für 6.7 die Topologie um einen zweiten Client erweitern, Original-TCP-Anwendungen unverändert lassen und Verbindung samt Routen tatsächlich testen. Kein eigener menschlicher Bearbeitungsanteil behauptet.
