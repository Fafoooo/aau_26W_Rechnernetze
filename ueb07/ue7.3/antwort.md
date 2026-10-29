# Ü 7.3 – Zwei Pfade, zwei Netzwerkeigenschaften

## Versuchsaufbau und Abgrenzung

Es werden nacheinander zwei **statisch ausgewählte Pfade** zwischen denselben Endhosts verglichen. Endpunkte sind `client` (`10.0.1.2`) und `server` (`10.0.2.2`). Die Angabe nennt den Client `client1`; in der Vorlage und in den folgenden Mininet-Kommandos heißt der Knoten `client`.

```text
A: client -- r1 -------- r2 -- server
B: client -- r1 -- r3 -- r2 -- server
```

Die Erweiterung verwendet nur zusätzliche Router-zu-Router-Verbindungen; das Servernetz bleibt an r2:

| Neues Netz | Linkseite 1 | Linkseite 2 |
|---|---|---|
| `10.0.13.0/30` | r1: `r1-eth2`, `10.0.13.1/30` | r3: `r3-eth0`, `10.0.13.2/30` |
| `10.0.23.0/30` | r3: `r3-eth1`, `10.0.23.1/30` | r2: `r2-eth2`, `10.0.23.2/30` |

Die ursprünglichen Netze bleiben `10.0.1.0/24`, `10.0.12.0/30` und `10.0.2.0/24`. Die Endhost-Default-Gateways bleiben `10.0.1.1` bzw. `10.0.2.1`. Jeder Router hat IPv4-Forwarding aktiviert, jedoch **keine Default-Route**.

**Nachweisstatus:** Die folgenden Ergebnisse stammen aus dem echten Lauf [run01](../nachweise/run01/results.json) mit Linux-Netzwerk-Namespaces, veth und TC/Netem. Das ist **Ersatzverifikation**, kein durchgeführter Mininet-/xterm-Lauf. Mininet fehlt hier und wurde nicht installiert; seine Ausführung in der vorgesehenen VM bleibt ungeprüft.

## Genau einen Pfad je Richtung auswählen

Die beiden Varianten werden nicht gleichzeitig als gleichwertige Routen eingerichtet. Vor jedem Messblock werden Hin- **und** Rückroute umgestellt; während der Umstellung wird nicht gemessen. Der direkte physische Link darf vorhanden bleiben, wird bei B aber nicht für den Endhostverkehr ausgewählt.

Befehle in den jeweiligen Routerterminals, nicht im normalen Hostterminal:

**Variante A:**

```bash
# Auf r1:
ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1
# Auf r2:
ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0
```

**Variante B:**

```bash
# Auf r1:
ip route replace 10.0.2.0/24 via 10.0.13.2 dev r1-eth2
# Auf r2:
ip route replace 10.0.1.0/24 via 10.0.23.1 dev r2-eth2
```

**Auf r3 in beiden Varianten:**

```bash
ip route replace 10.0.2.0/24 via 10.0.23.2 dev r3-eth1
ip route replace 10.0.1.0/24 via 10.0.13.1 dev r3-eth0
```

`replace` ersetzt die jeweilige vorhandene Route zum gleichen Zielpräfix; es wird keine zusätzliche ECMP-Alternative hinzugefügt. Die Route zum Server ist auf r2 direkt verbunden; die Route zum Client ist auf r1 direkt verbunden. Für den Vergleich sind die tatsächlich gewählten Routen mit `ip route`/`ip route get` und der Pfad mit `tracepath` oder `traceroute` zu kontrollieren. Ein bloßes Setzen von Metriken ohne Kontrolle wäre kein Nachweis, dass gerade der beabsichtigte Pfad benutzt wird.

## Linkverzögerungen und rechnerische RTT-Sollwerte

Die eigenen Verzögerungen **ersetzen** die ursprüngliche Vorgabe `LINK_DELAY = "10ms"`. Es werden nicht versehentlich weitere Netem-Verzögerungen auf bereits bestehende Warteschlangen addiert. Die hier angegebenen Werte gelten **pro Link und Übertragungsrichtung**:

| Verbindung | Egress-Interfaces an den beiden Linkenden | Verzögerung je Richtung |
|---|---|---:|
| client ↔ r1 | `client-eth0`, `r1-eth0` | 1 ms |
| r1 ↔ r2 | `r1-eth1`, `r2-eth0` | 5 ms |
| r1 ↔ r3 | `r1-eth2`, `r3-eth0` | 30 ms |
| r3 ↔ r2 | `r3-eth1`, `r2-eth2` | 30 ms |
| r2 ↔ server | `r2-eth1`, `server-eth0` | 1 ms |

Bei TC/Netem als **Egress-Verzögerung an beiden Linkenden** passiert ein Paket auf einem Link in einer Richtung nur die sendeseitige Verzögerungswarteschlange. Die Warteschlange am anderen Linkende verzögert erst die Gegenrichtung. Man zählt also nicht beide Interfacewerte für dieselbe einfache Linküberquerung. Beispiel für einen 30-ms-Link: `tc qdisc replace dev INTERFACE root netem delay 30ms` ist an beiden Enden im jeweils richtigen Namespace anzuwenden; `INTERFACE` ist dabei durch den tatsächlichen Interfacenamen zu ersetzen.

Für symmetrische Routen und Verzögerungen ergibt sich der **reine konfigurierte Verzögerungsanteil** der RTT:

```text
A, Hinweg:   1 + 5 + 1 = 7 ms
A, RTT:      2 × (1 + 5 + 1) = 14 ms

B, Hinweg:   1 + 30 + 30 + 1 = 62 ms
B, RTT:      2 × (1 + 30 + 30 + 1) = 124 ms

Differenz B − A: 110 ms
```

Die Soll-RTTs und ihre Differenz wurden mit Python berechnet; es handelt sich **nicht um Ping-Messwerte**. B enthält zwei verzögerte mittlere Links, nicht bloß einen Link mit 30 ms. Gegenüber A sind daher sowohl die Linkanzahl als auch deren Verzögerungen anders.

## Messverfahren

1. Variante A vollständig konfigurieren. Interfaces, Routen, Forwarding und `tc -s qdisc show dev ...` an **allen beteiligten Egress-Interfaces** protokollieren. Insbesondere prüfen, ob die laufende TC-Konfiguration tatsächlich obiger Tabelle entspricht.
2. Den ausgewählten Pfad in beiden Richtungen prüfen. Für A werden r1 und r2 als Transitrouter erwartet, für B zusätzlich r3 zwischen r1 und r2. Antworten von Routerinterfaces können abhängig von der Quelladresswahl andere lokale Interfaceadressen desselben Routers tragen.
3. Einen kurzen separaten Warmlauf ausführen, damit ARP-Auflösung und erste Scheduling-Effekte nicht mit dem eigentlichen Vergleich vermischt werden. Anschließend unter gleichen Bedingungen eine feste Anzahl Echo Requests mit gleichem Paketumfang senden und die vollständige Statistik sichern.
4. Auf B umschalten, den geänderten Hin- und Rückweg nachweisen und denselben Warmlauf sowie dieselbe Messung wiederholen. Die Messreihen nicht miteinander vermischen. Auch die Gegenrichtung prüfen.

Beispiel an der **Mininet-CLI**, als noch auszuführendes Messprotokoll:

```text
client tracepath -n 10.0.2.2
server tracepath -n 10.0.1.2
client ping -n -c 3 10.0.2.2
client ping -n -c 20 -i 0.2 -s 56 10.0.2.2
server ping -n -c 20 -i 0.2 -s 56 10.0.1.2
```

In einem Linux-Namespace-Ersatzlauf müssen die Befehle stattdessen mit dessen tatsächlichem Namespace-Runner ausgeführt werden. Das Präfix `client` ist dort nicht automatisch ein ausführbarer Shellbefehl.

## Warum entspricht die beobachtete RTT nicht einfach der Summe der Linkwerte?

- **Hin- und Rückweg:** `ping` misst die Zeit bis zur Echo-Antwort, nicht die einfache Laufzeit des Requests. Bei unterschiedlichen Rückrouten müssen die beiden Wege getrennt summiert werden.
- **Alle überquerten Links zählen:** Gemeinsame Randlinks tragen ebenfalls bei. B enthält zwei 30-ms-Verbindungen.
- **Weiterer Zeitbedarf:** Verarbeitung in den Hosts und Routern, Warteschlangen, Übertragungs-/Serialisierungszeiten und eventuelle echte Ausbreitungszeiten kommen grundsätzlich hinzu. Auf virtuellen Links bildet die konfigurierte Netem-Verzögerung eine künstliche Verzögerung ab, nicht eine reale Leitungslänge.
- **Emulation und Systemlast:** Timerauflösung, Kernel-Scheduling, Virtualisierung und konkurrierende Prozesse können Schwankungen verursachen. Der Sollwert ist daher eine Referenz, keine Garantie für einen auf die Millisekunde exakten Einzelwert.
- **ARP und Anlauf:** Noch fehlende Nachbareinträge können die ersten Pakete zusätzlich verzögern. Deshalb Warmlauf und Messblock getrennt dokumentieren.
- **Messgröße:** Hop-Zeiten aus `tracepath`/`traceroute` sind RTTs der jeweiligen Proben einschließlich ihres Rückwegs und möglicher ICMP-Verarbeitung. Man darf diese Zahlen nicht einfach zu einer Ende-zu-Ende-RTT addieren.

Beim Vergleich sind mindestens Paketverlust und `min/avg/max/mdev` zu dokumentieren. Unter geringer Last werden Werte in der Nähe von 14 ms bzw. 124 ms mit zusätzlichem Verarbeitungsaufwand erwartet; die tatsächliche Nähe muss erst die reale Messung zeigen. Starke Abweichungen verlangen eine Kontrolle von Route, Rückroute, TC-Richtung, doppelt eingerichteten Verzögerungen und Systemlast.

## Tatsächlicher Messnachweis: run01

Alle vier Messreihen: zunächst zwei Warmlaufpakete, dann zehn Echoanfragen mit 56 Byte Nutzlast und 0,2 Sekunden Abstand; **10/10 Antworten, kein Paketverlust**.

- **A, Client → Server:** min/avg/max/mdev = **14.085/14.577/15.089/0.405 ms**, [Rohmessung](../nachweise/run01/A-client-ping.txt).
- **A, Server → Client:** **14.079/14.505/15.197/0.327 ms**, [Rohmessung](../nachweise/run01/A-server-ping.txt).
- **B, Client → Server:** **124.082/124.557/125.446/0.407 ms**, [Rohmessung](../nachweise/run01/B-client-ping.txt).
- **B, Server → Client:** **124.482/124.811/125.116/0.227 ms**, [Rohmessung](../nachweise/run01/B-server-ping.txt).

Die gemessenen Mittelwerte passen zum theoretischen Verzögerungsanteil von 14 bzw. 124 ms; der kleine zusätzliche Zeitbedarf ist mit Verarbeitung und Scheduling vereinbar. B ist in beiden Richtungen deutlich langsamer. Die Werte sind keine universelle Laufzeitgarantie für eine andere VM.

**Pfadnachweise:** [A vorwärts](../nachweise/run01/A-client-tracepath.txt) zeigt `10.0.1.1 → 10.0.12.2 → 10.0.2.2 reached`, drei Hops. [B vorwärts](../nachweise/run01/B-client-tracepath.txt) zeigt `10.0.1.1 → 10.0.13.2 → no reply → 10.0.2.2 reached`, vier Hops. B lieferte an Hop 3 keine ICMP-Antwort; das Protokoll wird nicht zu einer vollständigen Hopliste umgedeutet. Routen, Zielerreichbarkeit und die beobachteten Antwort-TTLs (A 62, B 61, Ausgangs-TTL 64) bestätigen zusammen den zusätzlichen Transitrouter. [B rückwärts](../nachweise/run01/B-server-tracepath.txt) zeigt entsprechend `10.0.2.1 → 10.0.23.1 → no reply → 10.0.1.2 reached`.

Die vollständigen Routen und alle TC-Egress-Werte stehen je Knoten in den `A-*-state.txt` und `B-*-state.txt` desselben Laufs, etwa [A-r1](../nachweise/run01/A-r1-state.txt), [B-r1](../nachweise/run01/B-r1-state.txt), [B-r2](../nachweise/run01/B-r2-state.txt) und [B-r3](../nachweise/run01/B-r3-state.txt). Die unveränderte Ausgangstopologie wurde zusätzlich mit ihren ursprünglichen drei 10-ms-Links gemessen: Client-Mittelwert **60.441 ms**; diese Basismessung ist nicht Variante A.

Nachrechnen ohne Root: `python3 -B ue7.3/auswerten.py nachweise/run01/A-client-ping.txt` aus dem Blattordner; für B den Dateinamen entsprechend ersetzen. [Programm](auswerten.py), [Zeilenerklärung](../erklaerung_messung.md).

## KI-Kennzeichnung

Tool: Hermes Agent; Modell: OpenAI `gpt-6.1-sol`; Provider/Zugang laut Auftragskontext: `ChatGPT or Codex Subscription`; Datum: 2026-10-29. Anfrage: „Erstelle deutsche fachlich vollständige Antworten für RN Blatt07 Aufgaben 7.1 und 7.5 in den jeweiligen antwort.md sowie konzeptionelle Antworten zu 7.3 und 7.4 mit Platz für tatsächliche Messwerte; keine Messungen erfinden, keine Commits/Pushes.“
