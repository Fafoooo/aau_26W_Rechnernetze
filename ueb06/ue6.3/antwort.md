# 6.3 – Statische Routen entfernen und wiederherstellen

## 1. Voraussetzungen und Ausgangslage

Nur im eigenen RN-Lab arbeiten. `Angabe/start_lab.py` und `Angabe/topology.py` bleiben unverändert. Vorher auf beiden Routern `ip route` und `sysctl -n net.ipv4.ip_forward` kontrollieren. Forwarding muss `1` sein. Der Client behält `default via 10.0.1.1 dev client-eth0`, der Server `default via 10.0.2.1 dev server-eth0`.

Zu entfernen sind **nur die ausdrücklich angelegten Routen zum entfernten LAN**, nicht die angeschlossenen Netzrouten. Insbesondere weder `ip route flush table main` noch Adress-/Interface-Löschungen verwenden: Sonst wären auch die Gateways nicht mehr korrekt erreichbar.

## 2. Vorher: Routen dokumentieren

Im r1-Terminal `ip route`, im r2-Terminal ebenfalls `ip route`. Erwartete Haupttabellen als **Sollplan**, keine Mininet-Messung:

| Router | Angeschlossene Netze, bleiben erhalten | Explizite Route, wird entfernt |
|---|---|---|
| r1 | 10.0.1.0/24 dev r1-eth0; 10.0.12.0/30 dev r1-eth1 | 10.0.2.0/24 via 10.0.12.2 dev r1-eth1 |
| r2 | 10.0.12.0/30 dev r2-eth0; 10.0.2.0/24 dev r2-eth1 | 10.0.1.0/24 via 10.0.12.1 dev r2-eth0 |

## 3. Beide entfernten LAN-Routen löschen

Auf **r1**:

```sh
ip route del 10.0.2.0/24 via 10.0.12.2 dev r1-eth1
ip route
ip route get 10.0.2.2
```

Auf **r2**:

```sh
ip route del 10.0.1.0/24 via 10.0.12.1 dev r2-eth0
ip route
ip route get 10.0.1.2
```

Die erneute Tabellenanzeige dokumentiert die Löschung. `ip route get` muss im unveränderten Basis-Lab jetzt mit Fehlerstatus scheitern, weil auf den Routern keine Default Route als Ersatz existiert. Die genaue Linux-Fehlermeldung kann variieren; der Code prüft den **Exitstatus**, nicht einen erfundenen Wortlaut. Unerwartet erfolgreiche Auflösung ist ein Hinweis auf eine abweichende Konfiguration; das Skript stellt die gerade entfernte Route dann wieder her und bricht ab.

Nun im **Client**-Terminal:

```sh
ping -n -c 3 -W 1 10.0.2.2
```

Erwartet werden drei gesendete, null empfangene Echo-Antworten und Pingstatus `1`. Der Client kann weiterhin sein eigenes Gateway erreichen. Aber r1 fehlt nun der Weg zum Server-LAN, und r2 fehlt zusätzlich der Rückweg zum Client-LAN. Eine ICMP-Unreachable-Meldung ist keine erfolgreiche Echo-Antwort. Das Fehlen einer Route deaktiviert weder das Interface noch IPv4-Forwarding.

## 4. Routen manuell wieder anlegen

Auf **r1**:

```sh
ip route add 10.0.2.0/24 via 10.0.12.2 dev r1-eth1
ip route
ip route get 10.0.2.2
```

Auf **r2**:

```sh
ip route add 10.0.1.0/24 via 10.0.12.1 dev r2-eth0
ip route
ip route get 10.0.1.2
```

`add` wird hier absichtlich statt eines pauschalen `replace` verwendet: Ein nicht gelöschter Eintrag soll als Fehler auffallen. Die Gateways liegen im angeschlossenen Transitnetz `10.0.12.0/30`. Die jeweiligen Interfaces werden explizit angegeben, um den gewählten Link eindeutig zu machen. Nachher müssen die ursprünglichen Solltabellen wieder vorliegen.

## 5. Abschließender Ping und belastbares Erfolgskriterium

Auf dem Client `ping -c 3 10.0.2.2` ausführen. Das Skript nutzt dieselben drei Probes mit zusätzlichen Anzeige-/Timeoutoptionen: `env LC_ALL=C ping -n -c 3 -W 1 10.0.2.2`. `-n` vermeidet Namensauflösung, `-W 1` begrenzt Wartezeiten; `LC_ALL=C` macht die Statistik für den Parser sprachunabhängig.

Erfolg wird nur anerkannt, wenn **alle** Kriterien erfüllt sind:

1. Prozess-Exitstatus ist **0**.
2. Die Abschlussstatistik meldet **3 gesendete** Pakete.
3. Die Abschlussstatistik meldet **tatsächlich 3 empfangene** Antworten.

Im Original `start_lab.py` prüft `ping_ok()` lediglich `"0% packet loss" in result`. Das ist unsicher: Die Zeichenfolge steckt auch in `"100% packet loss"`. Die Originaldatei wird **nicht** geändert; `ping3()` ersetzt diese Prüfung im eigenen Ablauf durch Status- und Zählerauswertung. Zwei von drei Antworten, ein Fehlerstatus trotz drei Antworten oder fehlende Statistik werden abgewiesen.

## 6. Wiederverwendbares Python und Anwendung

[static_routes.py](static_routes.py) bietet:

- **`apply(node)`**: Vorher-Tabelle anzeigen, auf dem übergebenen r1-/r2-Knoten dessen explizite Route löschen, fehlenden Weg prüfen und Route wieder anlegen. `node` muss ein Mininet-ähnliches Objekt mit `.name` und `.pexec(argv)` sein.
- **`apply(node, "remove")` / `apply(node, "restore")`**: Einzelne Phasen, um **beide** Router vor der Wiederanlage gleichzeitig ohne ihre statischen Routen prüfen zu können.
- **`exercise(net)`**: Forwarding prüfen, beide Routen entfernen, erwarteten Pingfehlschlag prüfen, beide Routen auch bei einem Testfehler im `finally`-Block wiederherstellen und den abschließenden Ping streng prüfen. Bei als `RuntimeError` gemeldeten Wiederherstellungsfehlern werden trotzdem beide betroffenen Router bearbeitet und die Fehler gesammelt. Andere Adapter-Ausnahmen wie `TimeoutExpired` können die Schleife vorzeitig beenden; dann die Reparaturbefehle aus Schritt 4 verwenden.
- **`run(...)`**: Befehl, stdout, stderr und Exitstatus jeder Operation ausgeben. Es wird `node.pexec()` mit Argumentliste verwendet, kein stiller Befehl auf dem Hostbetriebssystem.

Ohne Option ist ein eigenständiger Start unschädlich und zeigt nur die Nutzung. In der **vorbereiteten Mininet-VM** kann vom Repository-Stamm aus der separate Treiber ausgeführt werden:

```sh
sudo python3 ueb06/ue6.3/static_routes.py --mininet
```

Er importiert die unveränderte `RoutingTopo` und `configure_base_network()`, startet **ein eigenes** Basis-Lab ohne xterms, führt die Übung aus und ruft zum Schluss `net.stop()` auf. Nicht parallel zu einem bereits laufenden Basis-Lab mit gleich benannten Interfaces starten. Alternativ `static_routes` aus einem vorhandenen Python-Treiber importieren und `exercise(net)` bzw. `apply(net["r1"])` aufrufen. Der ENTER-Prompt des originalen `start_lab.py` ist keine Python- oder Mininet-CLI.

Das Skript setzt absichtlich keine neuen Hostadressen, Defaultrouten oder Forwardingwerte. Falls die Ausgangslage verändert wurde, muss sie zuerst diagnostiziert werden. Bei einem externen Abbruch oder einem echten Wiederherstellungsfehler dienen die expliziten Befehle aus Schritt 4 zur Reparatur; ein Prozess kann weder Stromausfall noch SIGKILL mit `finally` absichern.

## 7. Tatsächlich ausgeführte Tests, klare Grenze

```sh
python3 ueb06/ue6.3/static_routes.py
python3 -m unittest discover -s ueb06/ue6.3 -p 'test_*.py' -v
```

Die **vier unittest-Testmethoden** in [test_static_routes.py](test_static_routes.py) wurden wirklich ausgeführt und bestanden. `NodeDouble` ist ausdrücklich ein **synthetisches Test-Double**: Es ändert keine Kernelrouten und sendet keine Pakete. Es modelliert vorhandene/fehlende explizite Routen, kontrolliert die exakten Delete-/Add-Befehle und gibt markierte synthetische Antworten zurück. Geprüft werden der gesamte beidseitige Ablauf, `apply(node)`, Fehler bei doppelter Löschung, Ping-Fehlstatistiken einschließlich 100 % Verlust, Wiederherstellung nach Testfehler, Forwarding-Schutz und falsche Knotenauswahl.

Das echte Prozessprotokoll steht in [testprotokoll.txt](testprotokoll.txt). Dortige Pingzahlen aus `NodeDouble` sind **keine real empfangenen Netzwerkpakete**. Auch `--mininet` wurde auf dieser Maschine ausprobiert: Der Start endet mangels installiertem Modul mit Status `2`, bevor ein Lab erzeugt wird. Mininet, OVS und xterm wurden nicht installiert; der tatsächliche Mininet-Ping bleibt hier unverifiziert. Die Schnittstelle erlaubt davon getrennte echte Lab-/Namespace-Nachweise; solche Messungen müssen ausdrücklich mit ihrer Herkunft dokumentiert werden. Alle nichtleeren eigenen Pythonzeilen sind in [erklaerung_routing.md](../erklaerung_routing.md) erklärt.

## Ergänzender realer Namespace-Nachweis

Anschließend wurde `exercise(net)` zusätzlich mit echten, getrennten Linux-Netzwerk-Namespaces ausgeführt, nicht nur mit Test-Doubles. [Basisprotokoll](../nachweise/run01/basis-routen-und-ping.txt) und [Erweiterungsprotokoll](../nachweise/run01/erweitert-routen-und-ping.txt) enthalten die tatsächlichen Kommandos und Exitstatus: vor Löschung **3/3**, ohne beide Routen **0/3**, nach Wiederanlage **3/3**. Je Router ist nach Löschen auch `ip route get` mit Status 2 protokolliert. [checks.py](../checks.py) verifiziert diese Statistik und die Reply-Sequenznummern. **Die Mininet-/OVS-Ausführung selbst bleibt offen.**

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Implementiere ausschließlich ueb06/ue6.1, ue6.2, ue6.3 sowie ueb06/erklaerung_routing.md; je Aufgabe ausführbares Python, schrittweise Antworten und echte Tests.
