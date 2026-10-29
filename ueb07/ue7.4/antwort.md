# Ü 7.4 – Fehler systematisch finden

## Ausgangslage und gezielt eingebauter Fehler

Ausgangspunkt ist die zuvor funktionierende **Variante B**:

```text
client (10.0.1.2) → r1 → r3 → r2 → server (10.0.2.2)
```

- r1 erreicht `10.0.2.0/24` ausschließlich über `10.0.13.2`, `r1-eth2`.
- r3 erreicht `10.0.2.0/24` über `10.0.23.2`, `r3-eth1`.
- r2 erreicht `10.0.1.0/24` über `10.0.23.1`, `r2-eth2`.
- r3 erreicht `10.0.1.0/24` über `10.0.13.1`, `r3-eth0`.
- Auf keinem Router existiert eine Default-Route. Es gibt keine zweite aktive Route und keinen automatischen Wechsel auf A. IPv4-Forwarding ist aktiviert.

In **r3s Namespace** wird ausschließlich die statische Route zum Servernetz entfernt:

```bash
ip route del 10.0.2.0/24 via 10.0.23.2 dev r3-eth1
```

Die Interfaces und ihre Adressen bleiben unverändert. Insbesondere bleiben `10.0.13.0/30` und `10.0.23.0/30` direkt verbunden. Das Zielnetz `10.0.2.0/24` liegt jedoch **nicht** direkt an r3. Die Route zum Nachbarlink `10.0.23.0/30` ersetzt keine Route zum Servernetz.

**Nachweisstatus:** Diagnose, Ausfall und Reparatur wurden in echten isolierten Linux-Netzwerk-Namespaces mit TC/Netem ausgeführt; die konkreten Belege stehen unten. Das ersetzt keinen Mininet-/xterm-Lauf, weil Mininet hier fehlt. Die gespeicherte Fehler-PCAP wurde zusätzlich tatsächlich in der Wireshark-GUI unter eigenem Xvfb geöffnet; dazu liegt ein authentischer Screenshot vor. Das ist automatisierte GUI-Bedienung, keine behauptete Eigenleistung von Fabio.

## 1. Zuerst den Fehler eingrenzen, nicht wahllos umkonfigurieren

Vor dem Löschen werden der funktionierende Pfad, Hin- und Rückrouten sowie ein erfolgreicher Ende-zu-Ende-Test gesichert. Danach wird nur die eine Route entfernt. So lässt sich die Zustandsänderung eindeutig dem Fehler zuordnen.

Anschließend prüfe ich schrittweise:

1. **Lokaler Zustand:** Sind die erwarteten Interfaces vorhanden und aktiv? Stimmen IP-Adressen und Präfixlängen? Hat der Client sein Default-Gateway? Sind beim Router Forwarding und die erwarteten Routen aktiv?
2. **Erster Nachbar:** Vom Client `10.0.1.1` anpingen. Falls schon das fehlschlägt, zuerst lokalen Link, Clientadresse, Präfix, ARP/Neighbor-Zustand und r1 untersuchen, statt beim entfernten Server zu beginnen.
3. **Nachbarlinks:** Von r1 `10.0.13.2`, von r3 `10.0.23.2` und von r2 `10.0.2.2` testen. Damit werden die drei Teilstrecken hinter dem Client getrennt überprüft.
4. **Ende-zu-Ende:** Vom Client `10.0.2.2` testen. Fehlerabsender und Meldung beachten, nicht nur „kein Erfolg“ notieren. Rückrouten sind ebenfalls zu prüfen.
5. **Pfad und konkrete Weiterleitung:** Mit `tracepath`/`traceroute` den Abbruch eingrenzen und auf dem verdächtigen Router `ip route get` für genau dieses Ziel verwenden.

Beispielbefehle an der Mininet-CLI; dies sind Prüfanweisungen, keine hier ausgeführten Tests:

```text
client ip -br addr
client ip route
client ping -n -c 3 10.0.1.1
r1 ping -n -c 3 10.0.13.2
r3 ping -n -c 3 10.0.23.2
r2 ping -n -c 3 10.0.2.2
client ping -n -c 3 10.0.2.2
```

Für direkte Nachbarpings ist eine passende Quelladresse auf dem jeweiligen Link hilfreich, falls die Quelladresswahl unklar ist. Ein erfolgreicher Nachbarping bestätigt **nicht**, dass r3 Pakete zum entfernten Servernetz weiterleiten kann: Der Nachbar ist über eine verbundene Route erreichbar, das Servernetz nach dem Löschen dagegen nicht mehr.

## 2. Was liefern `ip addr`, `ip route` und `ip route get`?

| Werkzeug | Information | Aussage beim eingebauten Fehler |
|---|---|---|
| `ip -br addr` bzw. `ip addr show` | Existierende Interfaces, administrativer/operativer Zustand, lokale Adressen und Präfixe | Erwartung: Adressen und Links bleiben korrekt; der Fehler ist kein absichtlich deaktivierter Link |
| `ip route show table main` | Verbundene, statische und gegebenenfalls Default-Routen | Auf r3 fehlt `10.0.2.0/24 via 10.0.23.2`; die direkt verbundenen Transfernetze sind noch vorhanden |
| `ip rule show` | Reihenfolge der Auswahl der Routingtabellen | Prüft, ob wirklich die erwarteten Standardregeln gelten oder eine andere Tabelle beteiligt ist |
| `ip route get ...` | Konkrete Route beziehungsweise Lookup-Fehler für ein einzelnes Ziel und optional ein bestimmtes eingehendes Paket | Auf r3 kann die Weiterleitung zum Server ohne passende Route nicht aufgelöst werden |
| `ip neigh` | ARP-/Neighbor-Zustand für direkt erreichbare Gegenstellen | Unterscheidet fehlende IP-Route von einem nicht auflösbaren Next Hop; ein ARP-Problem ist hier nicht der absichtlich eingebaute Fehler |
| `sysctl net.ipv4.ip_forward` | Ob IPv4-Weiterleitung aktiviert ist | Muss auf r1, r2 und r3 weiterhin `1` sein |

Konkrete Prüfungen an der Mininet-CLI:

```text
r3 ip -br addr
r3 ip route show table main
r3 ip rule show
r3 ip route show table local
r3 ip route get 10.0.2.2 from 10.0.1.2 iif r3-eth0
r3 ip route get 10.0.1.2
r3 ip neigh
r3 sysctl net.ipv4.ip_forward
```

Mit `from 10.0.1.2 iif r3-eth0` wird die ankommende Clientanfrage beschrieben, statt nur einen lokal von r3 erzeugten Datenstrom zu betrachten. Ein Lookup-Fehler wird lokal über Netlink gemeldet; das ist **nicht selbst schon ein auf dem Netz mitgeschnittenes ICMP-Paket**.

Die regulären Routen liegen hier in **`main` (254)**. Zuvor wird nach den Linux-Standardregeln **`local` (255)** geprüft. Das Serverziel ist keine eigene Adresse von r3, sodass die lokale Tabelle keine Zustellung ermöglicht. Ohne Servernetzroute und ohne Router-Default gibt es anschließend keinen passenden Weiterleitungsweg. Eine entfernte `/24`-Route zu löschen entfernt nicht die Adresse des Next Hops und auch nicht automatisch dessen verbundene `/30`-Route.

## 3. Wann verwende ich `ping`?

`ping` prüft die IP-Erreichbarkeit und misst bei Erfolg die RTT einer ICMP-Echo-Anfrage samt Antwort. Ich verwende es zuerst für den lokalen Gateway und direkte Nachbarn, danach für das eigentliche Ziel und abschließend nach der Reparatur erneut.

Für den gezielt erzeugten Fehler wird erwartet: Der Echo Request erreicht r3 über r1. r3 findet keinen Weg nach `10.0.2.2` und verwirft ihn. Bei normalem Linux-Verhalten, ohne ICMP-Unterdrückung durch Firewall oder Rate-Limiting, sendet r3 eine **ICMP Destination Unreachable, Type 3, Code 0: Network Unreachable** an den Client zurück. r3 hat dafür weiterhin seine Rückroute über r1. Eine typische Quelladresse wäre die zum Client gerichtete r3-Adresse `10.0.13.2`; die wirkliche Quelladresse ist am Mitschnitt nachzuweisen, nicht zu erfinden.

Eine Unreachable-Meldung ist ein stärkerer Hinweis als bloßes Schweigen. Trotzdem gilt: Das Ausbleiben einer Echo-Antwort beweist für sich allein weder einen Serverausfall noch eine fehlende Route. Firewall, ARP, Rückweg oder ICMP-Regeln können ebenfalls beteiligt sein. Deshalb werte ich die Fehlerart und den Absender zusammen mit Routingzustand und Mitschnitt aus.

## 4. Wann verwende ich `tracepath` bzw. `traceroute`?

Sobald lokale Verbindung und erste Nachbarn plausibel sind, zeigt die Pfadverfolgung, **bis zu welchem Router** Proben gelangen. Die Programme verwenden schrittweise erhöhte TTL-Werte; Transitrouter antworten beim Ablaufen der TTL normalerweise mit ICMP Time Exceeded.

```text
client tracepath -n 10.0.2.2
client traceroute -n 10.0.2.2
```

Die beiden Befehle sind Alternativen; ihre Probetypen und Ausgabeformate unterscheiden sich. Für B liegt r1 vor r3. Beim Routefehler ist ein Abbruch mit einer Netz-unerreichbar-Meldung von r3 zu erwarten, etwa als `!N`, falls das jeweilige Programm dies so darstellt. **Die genaue Hop-Ausgabe wird erst aus dem realen Protokoll übernommen.** Die nicht mehr erreichten r2-/Server-Hops sind nicht automatisch defekt; die Weiterleitung scheitert bereits vorher.

Sterne oder fehlende Antworten allein lokalisieren einen Fehler nicht eindeutig, weil Router ICMP-Antworten unterdrücken oder begrenzen können. Auch können bei Traceroute mehrere Adressen eines Routers sichtbar werden. Mit Routingtabellen und gezielten Nachbarpings werden diese Beobachtungen abgesichert. `tracepath` kann zusätzlich Hinweise zur Pfad-MTU liefern; hier wird aber absichtlich eine Route entfernt, nicht die MTU verändert.

## 5. Wann liefert Wireshark den entscheidenden Hinweis?

Wenn ein Programm nur eine allgemeine Fehlermeldung ausgibt oder zwischen fehlender Route, Filterung und Transportfehler unterschieden werden muss, zeigt der Mitschnitt die **tatsächlich übertragenen Pakete**. Besonders aussagekräftig ist eine Aufzeichnung an r3s clientseitigem Interface `r3-eth0`; ergänzend kann an `r3-eth1` kontrolliert werden, ob etwas in Richtung r2 weitergeleitet wurde.

Geeignete **Wireshark-Anzeigefilter**:

```text
icmp && ip.addr == 10.0.1.2
icmp.type == 3 && icmp.code == 0
icmp.type == 8 && ip.dst == 10.0.2.2
```

Die Filter sind Anzeigefilter, nicht unverändert als tcpdump-Capturefilter verwendbar. Beim Netz-unerreichbar-Paket sind zu dokumentieren:

1. **Äußerer IP-Header:** r3 als Fehlerabsender, Client `10.0.1.2` als Empfänger. Exakte Quelladresse und Frame-Nummer aus dem tatsächlichen PCAP übernehmen.
2. **ICMP-Header:** Type 3, Code 0 – Network Unreachable. Nicht mit „Host Unreachable“ (Code 1), „Port Unreachable“ (Code 3) oder „Time Exceeded“ (Type 11) verwechseln.
3. **Zitiertes ursprüngliches Paket:** Ursprüngliche IP-Quelle `10.0.1.2`, ursprüngliches IP-Ziel `10.0.2.2` und der enthaltene Beginn des ICMP Echo Requests. Damit lässt sich die Fehlermeldung der konkreten fehlgeschlagenen Anfrage zuordnen.
4. **Paketfolge und Aufzeichnungsort:** Anfrage erreicht r3; die Fehlermeldung wird in Gegenrichtung erzeugt. Eine vollständige zusätzliche Egress-Aufzeichnung kann belegen, dass dieser Request nicht zu r2 weitergeleitet wird. Das Fehlen eines Pakets in einem einzelnen unvollständigen Capture wäre dafür kein ausreichender Beweis.

Der entscheidende Zusammenhang ist: **r3 meldet das unerreichbare Zielnetz, obwohl seine direkten Nachbarn erreichbar sind; zugleich fehlt genau auf r3 die passende Servernetzroute.** Wireshark allein liest keine Routingtabelle aus. Erst Paketbefund und lokale Konfigurationsprüfung zusammen begründen die Diagnose.

## 6. Diagnose, Korrektur und Wiederholungsprüfung

**Diagnose:** Die statische Weiterleitungsroute `10.0.2.0/24 via 10.0.23.2 dev r3-eth1` fehlt auf r3. Die Router führen keine automatische Suche nach einem Ersatzpfad durch. Der physisch vorhandene direkte Link r1–r2 wird durch das Fehlen einer Route auf r3 nicht automatisch aktiviert.

**Korrektur ausschließlich im r3-Namespace:**

```bash
ip route replace 10.0.2.0/24 via 10.0.23.2 dev r3-eth1
```

Danach erneut Routing-Lookup, Ende-zu-Ende-Ping und Pfad in beiden Richtungen prüfen. Nicht lediglich eine pauschale Default-Route hinzufügen, den Client umadressieren oder auf A umschalten: Das würde den vorgesehenen B-Pfad beziehungsweise den Versuchsaufbau verändern, statt die nachgewiesene Ursache gezielt zu beheben.

```text
r3 ip route get 10.0.2.2 from 10.0.1.2 iif r3-eth0
client ping -n -c 4 10.0.2.2
server ping -n -c 4 10.0.1.2
client tracepath -n 10.0.2.2
server tracepath -n 10.0.1.2
```

## Tatsächlicher Fehlernachweis: run01

1. **Vorher:** [B-r3-state.txt](../nachweise/run01/B-r3-state.txt) enthält beide statischen Routen. [B-client-ping.txt](../nachweise/run01/B-client-ping.txt) bestätigt 10/10 Antworten; [B-server-ping.txt](../nachweise/run01/B-server-ping.txt) bestätigt den Rückweg ebenfalls mit 10/10 Antworten.
2. **Defekt:** [fault-r3-state.txt](../nachweise/run01/fault-r3-state.txt) zeigt unveränderte Adressen und die fehlende Servernetzroute. `ip route get 10.0.2.2` meldet tatsächlich `RTNETLINK answers: Network is unreachable`. [fault-client-ping.txt](../nachweise/run01/fault-client-ping.txt) zeigt zwei gesendete Anfragen, null Antworten und zwei Fehler `From 10.0.13.2 ... Destination Net Unreachable`. [tracepath](../nachweise/run01/fault-client-tracepath.txt) stoppt an Hop 2 bei `10.0.13.2` mit `!N`.
3. **Pakete:** [fault.pcap](../nachweise/run01/fault.pcap) wurde ausschließlich am isolierten `client-eth0` aufgenommen. Capturefilter: `icmp and (host 10.0.1.2) and (host 10.0.2.2 or host 10.0.13.2)`. Frame **1** ist Echo Request Client → Server, Frame **2** der passende ICMP-Netzfehler `10.0.13.2 → 10.0.1.2`, Type **3**, Code **0**. Frames **3/4** wiederholen dies für die zweite Anfrage. Beide Fehler zitieren `10.0.1.2 → 10.0.2.2` und den passenden Echo-Header; die Zuordnung wird durch Echo-ID/Sequenz geprüft. Der [dumpcap-Bericht](../nachweise/run01/fault-dumpcap.txt) meldet **4 Pakete, 0 verworfen**; der [unabhängige Byteparser](pcap_pruefen.py) findet ebenfalls genau vier Frames. [Auswertung](../nachweise/run01/fault-frames.json).
4. **GUI:** [Wireshark-Screenshot](../nachweise/run01/wireshark-fehler.png) zeigt den echten Mitschnitt mit Filter `icmp.type == 3`: sichtbar sind Frames 2 und 4; Frame 2 ist ausgewählt. [GUI-Protokoll](../nachweise/run01/gui-nachweis.txt). Wireshark liest die PCAP offline; der Screenshot beweist keine Aufzeichnung innerhalb Mininet.
5. **Repariert:** Die Route wird gezielt auf r3 wiederhergestellt. [repaired-r3-route.txt](../nachweise/run01/repaired-r3-route.txt) zeigt wieder `via 10.0.23.2 dev r3-eth1`. [repaired-client-ping.txt](../nachweise/run01/repaired-client-ping.txt) belegt **3/3 Antworten**, keinen Verlust und TTL 61. Ein zusätzlicher Rückwärts-/Tracepath-Messblock nach der Reparatur wurde nicht gespeichert; die entsprechenden Befehle oben bleiben Wiederholungsanweisungen für die VM, nicht behauptete Messungen.

Nachprüfen ohne Root aus dem Blattordner: `python3 -B ue7.4/pcap_pruefen.py nachweise/run01/fault.pcap` und `python3 -B ue7.4/test_pcap.py`. [Erklärung](../erklaerung_messung.md), [18 Offline- und Negativtests](../erklaerung_pcap_tests.md). Diese Parser sind absichtlich auf den konkreten Fehlerfall zugeschnitten, keine allgemeinen Netzwerkforensik-Werkzeuge.

## KI-Kennzeichnung

Tool: Hermes Agent; Modell: OpenAI `gpt-6.1-sol`; Provider/Zugang laut Auftragskontext: `ChatGPT or Codex Subscription`; Datum: 2026-10-29. Anfrage: „Erstelle deutsche fachlich vollständige Antworten für RN Blatt07 Aufgaben 7.1 und 7.5 in den jeweiligen antwort.md sowie konzeptionelle Antworten zu 7.3 und 7.4 mit Platz für tatsächliche Messwerte; keine Messungen erfinden, keine Commits/Pushes.“
