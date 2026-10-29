# 6.1 – IP-Adressen und Interfaces

## 1. Ausgangspunkt und Messgrenze

Die folgenden sechs Dateninterfaces sind der **deterministische Sollplan**, keine Messwerte. Adressen und Präfixe werden in `Angabe/start_lab.py`, Funktion `configure_base_network()`, explizit gesetzt; `Angabe/topology.py` legt die Links und Interfacenamen fest. Die Originals bleiben unverändert. Auf dieser Maschine fehlen Mininet/OVS/xterm; die vorgeschriebene Ausführung in deren VM ist hier nicht nachgewiesen. Lokale Python-Tests sind davon zu unterscheiden.

## 2. Interfaces im echten Lab untersuchen

1. Das unveränderte `start_lab.py` in der vorbereiteten VM starten.
2. In **jedem zugehörigen Knotenterminal** `ip -br addr` und anschließend `ip addr` ausführen. Der erste Befehl zeigt die Kurzform, der zweite unter anderem Status, MAC-Adresse, IPv4-Präfix und Broadcastadresse.
3. IPv4-Adresse und Präfix übernehmen; `Adresse AND Netzmaske` ergibt die Netzadresse. `adressen.py` berechnet sie mit `IPv4Interface(...).network` und nicht durch Abschneiden der letzten Ziffern.
4. Optionale maschinenlesbare Aufnahme: `ip -j addr > r1-addr.json` im **r1**-Terminal. Vom Repository-Stamm aus: `python3 ueb06/ue6.1/adressen.py --host r1 --json r1-addr.json`. Alternativ direkt dort: `ip -j addr | python3 ueb06/ue6.1/adressen.py --host r1 --json -`.
5. JSON enthält nicht zuverlässig den Mininet-Knotennamen. `--host` ist deshalb ein ausdrücklich angegebenes Label; der Benutzer muss die Herkunft der Aufnahme kontrollieren. Mininet-Name und Ausgabe von `hostname` sind nicht zwangsläufig identisch, weil der UTS-Namensraum geteilt sein kann.

`start_lab.py` öffnet xterms und wartet danach mit `input()` auf ENTER: Das Hauptterminal ist **keine Mininet-CLI**. Keine Befehle der Form `r1 ip addr` in diesen ENTER-Prompt schreiben. In den r1-/r2-xterms wird der jeweilige normale Linux-Befehl ohne vorangestellten Knotennamen ausgeführt.

## 3. Adresstabelle des Sollplans

| Hostname/Knotenlabel | Interface | IPv4-Adresse | Präfix | Zugehöriges Netzwerk |
|---|---|---|---|---|
| client | client-eth0 | 10.0.1.2 | /24 | 10.0.1.0/24 |
| r1 | r1-eth0 | 10.0.1.1 | /24 | 10.0.1.0/24 |
| r1 | r1-eth1 | 10.0.12.1 | /30 | 10.0.12.0/30 |
| r2 | r2-eth0 | 10.0.12.2 | /30 | 10.0.12.0/30 |
| r2 | r2-eth1 | 10.0.2.1 | /24 | 10.0.2.0/24 |
| server | server-eth0 | 10.0.2.2 | /24 | 10.0.2.0/24 |

Die Tabelle enthält die sechs vorgegebenen **Dateninterfaces**. Loopback `lo` wird vom Original nicht explizit adressiert; deshalb wird hier keine Loopback-Messung erfunden. Ein tatsächlich aufgenommenes `127.0.0.1/8` würde das Programm als `127.0.0.0/8` ausgeben. Der JSON-Modus nimmt alle IPv4-Einträge einschließlich Loopback und mehrerer Adressen pro Interface mit; IPv6 wird bewusst nicht als IPv4 ausgegeben. Linkstatus und MAC-Adressen müssen weiterhin aus den geforderten Linux-Ausgaben untersucht werden.

## 4. Welche Interfaces gehören zusammen?

1. **Client-LAN:** `client-eth0` und `r1-eth0` liegen in `10.0.1.0/24`, Netzmaske `255.255.255.0`. Sie erreichen einander direkt auf dem Link.
2. **Router-Transit:** `r1-eth1` und `r2-eth0` liegen in `10.0.12.0/30`, Netzmaske `255.255.255.252`. Die beiden nutzbaren Adressen sind `.1` und `.2`; `.0` ist Netzadresse, `.3` Broadcastadresse.
3. **Server-LAN:** `r2-eth1` und `server-eth0` liegen in `10.0.2.0/24`, Netzmaske `255.255.255.0`.
4. Client- und Server-LAN sind verschiedene IP-Netze und Broadcastdomänen. r1 und r2 verbinden sie über das dritte Netz. Router leiten IPv4-Pakete weiter, aber nicht einfach die ursprünglichen Ethernetframes oder ARP-Broadcasts über alle Links.
5. Dass alle Adressen mit `10.` anfangen, macht sie hier **nicht** zu einem gemeinsamen `/8`: Maßgeblich sind die ausdrücklich vergebenen `/24`- und `/30`-Präfixe.

## 5. Ausführbarer Code und Nachweise

Ab Repository-Stamm:

```sh
python3 ueb06/ue6.1/adressen.py
python3 ueb06/ue6.1/adressen.py --test
```

Ohne Optionen wird der Sollplan als Markdown-Tabelle mit deutlichem Herkunftshinweis ausgegeben. `--test` prüft Planumfang, alle drei Netzadressen, IPv4-/IPv6-Filterung, leere Interfaces und Loopback. Die tatsächlich ausgeführten Tests einschließlich Datei-/stdin-CLI und fehlendem `--host` stehen in [testprotokoll.txt](testprotokoll.txt). Die zeilenweise Erklärung steht in [erklaerung_routing.md](../erklaerung_routing.md).

## Ergänzender realer Namespace-Nachweis

Der anschließend ausgeführte isolierte Linux-Namespace-Lauf bestätigt sämtliche sechs Dateninterfaces des Sollplans. Die vollständigen `ip -br addr`, `ip addr` und Original-Inspector-Ausgaben stehen unter [nachweise/run01](../nachweise/run01); JSON-Aufnahmen enthalten auch das tatsächlich gesetzte Loopback. [checks.py](../checks.py) prüft alle Adressen und Präfixe exakt. Dies ist **kein Mininet-/OVS-Lauf**; dessen VM-Abnahme bleibt offen.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Implementiere ausschließlich ueb06/ue6.1, ue6.2, ue6.3 sowie ueb06/erklaerung_routing.md; je Aufgabe ausführbares Python, schrittweise Antworten und echte Tests.
