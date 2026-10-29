# Ü 7.1 – Routingpfad analysieren

## Grundlage und Adressierung

Die Antwort leitet den Pfad aus den bereitgestellten Dateien `Angabe/topology.py`, `Angabe/start_lab.py` und `Angabe/route_reference.txt` ab. Sie ist keine Behauptung eines durchgeführten Mininet-Laufs. Die Angabe nennt den Endhost `client1`; die ausführbare Vorlage verwendet tatsächlich den Knotennamen **`client`** und das Interface **`client-eth0`**. Im Folgenden bezeichnet `client` diesen Client.

```text
client                 r1                         r2                  server
10.0.1.2/24 -- 10.0.1.1/24 | 10.0.12.1/30 -- 10.0.12.2/30 | 10.0.2.1/24 -- 10.0.2.2/24
client-eth0     r1-eth0       r1-eth1          r2-eth0         r2-eth1      server-eth0
```

| Knoten | Interface | IPv4-Adresse | Direkt angeschlossenes Netz |
|---|---|---|---|
| client | `client-eth0` | `10.0.1.2/24` | `10.0.1.0/24` |
| r1 | `r1-eth0` | `10.0.1.1/24` | `10.0.1.0/24` |
| r1 | `r1-eth1` | `10.0.12.1/30` | `10.0.12.0/30` |
| r2 | `r2-eth0` | `10.0.12.2/30` | `10.0.12.0/30` |
| r2 | `r2-eth1` | `10.0.2.1/24` | `10.0.2.0/24` |
| server | `server-eth0` | `10.0.2.2/24` | `10.0.2.0/24` |

## Welche Routingtabellen werden verwendet?

Jeder Knoten hat im eigenen Netzwerk-Namespace eigene Interfaces und eigene Routingtabellen. Die Vorlage konfiguriert kein besonderes Policy Routing. Die normalen verbundenen und statischen Unicast-Routen stehen daher in der Linux-Tabelle **`main` (ID 254)**; `ip route` zeigt standardmäßig diese Tabelle.

Genauer entscheidet zunächst die Routing Policy Database (`ip rule`). Mit den üblichen Standardregeln wird zuerst **`local` (ID 255, Regelpriorität 0)** geprüft. Dort stehen unter anderem die eigenen IP-Adressen. Ein Paket an eine eigene Routeradresse wird lokal zugestellt und nicht weitergeroutet. Für das hier betrachtete fremde Ziel `10.0.2.2` folgt auf r1 und r2 die Abfrage von **`main` (Regelpriorität 32766)**. Die danach üblicherweise vorhandene Tabelle `default` (ID 253) ist nicht mit einer Default-Route `0.0.0.0/0` zu verwechseln; die Default-Routen der Endhosts stehen hier in `main`.

Innerhalb der ausgewählten Tabelle gilt der **längste passende Zielpräfix** (Longest Prefix Match). Eine passende `/24`-Route ist spezifischer als eine Default-Route `/0`. Der Router muss nicht den gesamten weiteren Weg kennen, sondern nur den nächsten erreichbaren Hop. Auf beiden Routern aktiviert `LinuxRouter.config()` aus der Vorlage IPv4-Forwarding (`net.ipv4.ip_forward=1`).

Die folgenden Einträge sind die **aus der Konfiguration abgeleiteten relevanten Routen**, kein kopiertes Laufzeitprotokoll:

```text
client:
  10.0.1.0/24 dev client-eth0
  default via 10.0.1.1 dev client-eth0

r1:
  10.0.1.0/24 dev r1-eth0
  10.0.12.0/30 dev r1-eth1
  10.0.2.0/24 via 10.0.12.2 dev r1-eth1

r2:
  10.0.12.0/30 dev r2-eth0
  10.0.2.0/24 dev r2-eth1
  10.0.1.0/24 via 10.0.12.1 dev r2-eth0

server:
  10.0.2.0/24 dev server-eth0
  default via 10.0.2.1 dev server-eth0
```

## Vollständiger Hinweg und Entscheidungen

IP-Quelle ist `10.0.1.2`, IP-Ziel ist `10.0.2.2`.

| Entscheidender Knoten | Eingangsinterface | Gewählte Route | Ausgangsinterface | Nächster Hop |
|---|---|---|---|---|
| client | lokal erzeugt | `default via 10.0.1.1` | `client-eth0` | r1, `10.0.1.1` |
| r1 | `r1-eth0` | `10.0.2.0/24 via 10.0.12.2` | `r1-eth1` | r2, `10.0.12.2` |
| r2 | `r2-eth0` | direkt verbundenes `10.0.2.0/24` | `r2-eth1` | Zielhost selbst, `10.0.2.2` |
| server | `server-eth0` | eigene Adresse in `local` | lokale Zustellung | kein weiterer Hop |

1. **Client:** Das Ziel gehört nicht zu seinem direkt angeschlossenen `10.0.1.0/24`. Deshalb verwendet er die Default-Route zu `10.0.1.1`. Per ARP ermittelt er bei Bedarf die MAC-Adresse des Gateways, **nicht** die MAC-Adresse des entfernten Servers.
2. **r1:** Das Paket ist nicht an r1 selbst adressiert. In `main` passt die statische Route `10.0.2.0/24 via 10.0.12.2 dev r1-eth1`. r1 leitet an r2 weiter; der Next Hop ist durch `10.0.12.0/30` direkt erreichbar. Falls erforderlich löst r1 dessen MAC-Adresse per ARP auf.
3. **r2:** `10.0.2.2` liegt im direkt verbundenen `10.0.2.0/24`. r2 benötigt für dieses Ziel keinen weiteren Router als Gateway. Er ermittelt die MAC-Adresse von `10.0.2.2` und sendet über `r2-eth1` direkt an `server-eth0`.
4. **Server:** Das Ziel entspricht seiner eigenen Adresse; er nimmt das Paket lokal an, beispielsweise für ICMP Echo oder eine TCP-Anwendung.

Die IP-Adressen von Quelle und Ziel bleiben ohne NAT gleich. An jedem Router wird die IPv4-TTL um eins vermindert und die IPv4-Headerprüfsumme angepasst. Die Ethernet-Frames werden für jede Teilstrecke neu aufgebaut: Quell- und Ziel-MAC-Adressen gehören jeweils zum aktuellen Link und zum dortigen Next Hop. Die IP-Zieladresse wird **nicht** durch die Gatewayadresse ersetzt.

## Rückweg

Eine erfolgreiche Anfrage reicht für `ping` oder TCP nicht aus: Auch die Antwort muss zurückfinden.

| Knoten | Ausgangsinterface | Nächster Hop zum Client |
|---|---|---|
| server | `server-eth0` | Default-Gateway r2, `10.0.2.1` |
| r2 | `r2-eth0` | statische Route `10.0.1.0/24 via 10.0.12.1` zu r1 |
| r1 | `r1-eth0` | direkt erreichbarer Client `10.0.1.2` |
| client | lokale Zustellung über `client-eth0` | kein weiterer Hop |

## Warum keine eigene Route für jedes Zielgerät?

Routingtabellen enthalten **Netzpräfixe**, nicht zwingend einzelne Hostadressen. Die verbundene `/24`-Route deckt die lokalen Ziele ab; die Default-Route `/0` übergibt alle nicht spezifischer erfassten entfernten Ziele an r1. Die weitere Wegwahl übernehmen die Router. Damit braucht der Client weder eine eigene `/32`-Route pro Server noch Kenntnis aller Netze hinter r1. Die Default-Route garantiert allerdings keine Erreichbarkeit: Der Gateway und alle folgenden Router benötigen weiterhin passende Hin- und Rückrouten.

## Nachprüfen in der vorgesehenen Mininet-Umgebung

Die folgenden Befehle sind **Prüfanweisungen**, keine hier erzeugten Messergebnisse. Zuerst im Verzeichnis der Vorlagen starten:

```bash
sudo python3 start_lab.py
```

Anschließend an der Mininet-CLI; der Knotenname vor dem Befehl sorgt für die Ausführung im richtigen Namespace:

```text
client ip -br addr
client ip route
r1 ip -br addr
r1 ip rule show
r1 ip route show table main
r1 ip route show table local
r1 ip route get 10.0.2.2 from 10.0.1.2 iif r1-eth0
r2 ip -br addr
r2 ip route
r2 ip route get 10.0.2.2 from 10.0.1.2 iif r2-eth0
server ip -br addr
server ip route
client ping -n -c 4 10.0.2.2
server ping -n -c 4 10.0.1.2
client tracepath -n 10.0.2.2
```

In einem bereits geöffneten Knotenterminal entfällt das vorangestellte `client`, `r1` usw. Ein `ip route` im normalen Hostterminal würde dagegen die falsche Routingtabelle untersuchen. Das Startskript öffnet tatsächlich `CLI(net)`; seine automatische Ping-Textprüfung allein ist kein zuverlässiger Erfolgsnachweis, weil der Teilstring `0% packet loss` auch in `100% packet loss` vorkommt. Tatsächliche empfangene Antworten und Paketstatistiken sind zu prüfen.

## Tatsächlicher Zusatznachweis

Die unveränderte Ausgangsadressierung und statischen Routen wurden mit echten Linux-Netzwerk-Namespaces nachgebildet, separat von der erweiterten Topologie. Dies ist kein Mininet-Lauf. [Clientzustand](../nachweise/run01/original-client-state.txt), [r1](../nachweise/run01/original-r1-state.txt), [r2](../nachweise/run01/original-r2-state.txt) und [Server](../nachweise/run01/original-server-state.txt) enthalten Interfaces, vollständige `main`-Routen, `ip rule`, Forwarding und TC.

[Tracepath vorwärts](../nachweise/run01/original-client-tracepath.txt) und [rückwärts](../nachweise/run01/original-server-tracepath.txt) erreichen das Ziel. [Ping Client](../nachweise/run01/original-client-ping.txt) sowie [Ping Server](../nachweise/run01/original-server-ping.txt) liefern je 10/10 Antworten. Die drei ursprünglichen 10-ms-Links wirken jeweils in beide Richtungen; das ist vom später veränderten Verzögerungsplan A/B getrennt.

**Quellen:** bereitgestellte Originalvorlagen; [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html), [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html).

## KI-Kennzeichnung

Tool: Hermes Agent; Modell: OpenAI `gpt-6.1-sol`; Provider/Zugang laut Auftragskontext: `ChatGPT or Codex Subscription`; Datum: 2026-10-29. Anfrage: „Erstelle deutsche fachlich vollständige Antworten für RN Blatt07 Aufgaben 7.1 und 7.5 in den jeweiligen antwort.md sowie konzeptionelle Antworten zu 7.3 und 7.4 mit Platz für tatsächliche Messwerte; keine Messungen erfinden, keine Commits/Pushes.“
