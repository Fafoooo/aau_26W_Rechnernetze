# Unabhängige Endprüfung – Übungsblatt 06

## Ergebnis und Freigabegrenze

**Keine fachliche Must-fix-Korrektur an den Lösungen 6.1–6.7 festgestellt.** Adressierung, Forwarding, statische Routen, VLSM, Dijkstra und die ausdrücklich definierte DV-Nachrichtenfolge sind mit der Originalangabe vereinbar. Die vorhandenen Namespace-Protokolle sind untereinander und mit dem ausführenden Code konsistent; synthetische Tests werden nicht als echte Paketmessungen ausgegeben.

**Noch offen / vor einer Behauptung „vollständig in Mininet verifiziert“ zwingend nachzuholen:** Ausführung in der vorbereiteten Mininet-/OVS-VM. Die Linux-Namespace-Messungen ersetzen diesen Nachweis nicht. Das ist eine reale Verifikationslücke, kein hier nachgewiesener Fehler der Topologie. Die Antworten benennen diese Grenze bereits.

## Geprüfter Umfang

- `angabe_blatt06.pdf`: Originaltext und alle drei gerenderten Seiten einschließlich Ausgangstopologie, beider gewichteter Graphen, Erweiterungsbild und Anhang gelesen; Dijkstra-Graph zusätzlich vergrößert betrachtet.
- Alle sieben `ue6.*/antwort.md`, sämtlicher zugehöriger Python-Lösungscode und die Tests zu 6.3, 6.4–6.6 und 6.7 gelesen.
- Alle elf im Vorlagenarchiv enthaltenen Infrastrukturdateien gelesen; bytegenaue Übereinstimmung der ausgepackten Originaldateien mit `Angabe/uebb6_template.zip` durch einen vorhandenen Test bestätigt. Insbesondere beide TCP-Programme sind unverändert.
- `verify_namespaces.py`, `nachweise/run01/results.json` sowie sämtliche dortigen Interface-/JSON-, Routen-, Ping- und TCP-Protokolle gelesen und miteinander abgeglichen.
- `erklaerung_routing.md`, `erklaerung_algorithmen.md` und bisherige Testprotokolle gelesen. KI-Kennzeichnung gegen die bereitgestellte Kursregel geprüft.
- Den neu hinzugekommenen Gesamttreiber `checks.py` gelesen und gezielt dessen sieben bereits ausführbare, rein lesende Tests gestartet. Ein vollständiger Aufruf von `checks.py` wurde in dieser Prüfung **nicht** behauptet: Er enthält außerdem eine Git-Abfrage, während der Reviewauftrag Git ausschließt, sowie eine Prüfung der noch parallel entstehenden Gesamterklärung. Die parallel erstellten Dokumente `erklaerung_blatt06.md` und `prüfung.md` sind daher nicht Gegenstand dieser Freigabe.

Der Namespace-Lauf `run01` wurde in dieser Endprüfung **nicht erneut ausgeführt oder überschrieben**. Geprüft wurden die gespeicherten Messdaten und ihr tatsächlicher Ausführungspfad. Archivierte Ausgaben allein sind kein kryptografischer Herkunftsnachweis; es wurden aber keine Widersprüche oder als Messungen ausgegebene Test-Double-Werte gefunden.

## Befunde nach Schwere

### [HOCH / OFFENE ABNAHME] Mininet-/OVS-Ausführung fehlt weiterhin

**Stellen:** `ue6.7/antwort.md:52–64`, `ue6.1/antwort.md:5`, `ue6.3/antwort.md:97–106`; tatsächlicher Startpfad `ue6.7/start_erweitert.py:27–42`.

Die hier ausgeführten API-Tests prüfen Struktur und Aufrufkonventionen mit Doubles. `verify_namespaces.py:107–112` erzeugt ausdrücklich eine Linux-Bridge, keine OVSBridge; es importiert und startet die Mininet-Topologie nicht. Es prüft auch keine TCLink-Verzögerungen oder xterms. Der echte Versuch `python3 -B ueb06/ue6.3/static_routes.py --mininet` endete erneut mit **Status 2** und `Mininet-Start nicht verfügbar: No module named 'mininet'`. `command -v` fand auch `mn`, `ovs-vsctl` und `xterm` nicht.

**Must-finish vor vollständiger Mininet-Abnahme:** Basis-Lab und Erweiterungsstarter in der vorbereiteten VM starten; dort Interface-/Routingausgaben, Routenzyklus mit abschließendem Dreier-Ping und Verbindungen beider unveränderter TCP-Clients dokumentieren. Keine Installation auf diesem Rechner vorgenommen. Die ehrlichen Warnungen in den Antworten dürfen bis dahin nicht entfernt werden.

### [NIEDRIG] Erweiterter Starter zeigt im Statuskopf die Basistopologie

**Stellen:** `ue6.7/start_erweitert.py:36` ruft `Angabe/start_lab.py:74–101` auf; dort steht in Zeile 79 fest `Topology: client -- r1 -- r2 -- server`.

Beim erweiterten Lauf nennt dieser Kopf weder `s1` noch `client2`. Die zusätzliche Ausgabe in `start_erweitert.py:37` zeigt client2 zwar separat, beseitigt den falschen Topologiekopf aber nicht. Kein Routingfehler, jedoch eine irreführende Diagnoseanzeige. Optional im **eigenen** Starter klar als Basis-Status beschriften oder einen ergänzenden vollständigen Topologiehinweis ausgeben; Originaldatei nicht ändern.

### [NIEDRIG / ROBUSTHEIT] Wiederherstellung verarbeitet nicht jede Adapter-Ausnahme weiter

**Stellen:** `ue6.3/static_routes.py:75–83`, Zusicherung in `ue6.3/antwort.md:84`; Namespace-Adapter `verify_namespaces.py:29–30,52–54`.

Der Wiederherstellungsloop sammelt nur `RuntimeError`. Der Namespace-Adapter kann dagegen bei einem hängenden Kommando `subprocess.TimeoutExpired` auslösen. Geschieht das bei r1s Wiederherstellung, wird r2 nicht mehr bearbeitet. Der dokumentierte erfolgreiche Normalablauf ist davon nicht betroffen; die allgemeine Aussage, beide Router würden auch nach einem Wiederherstellungsfehler weiter bearbeitet, ist für diesen Adapter zu weit. Optional dokumentierte Ausnahmearten präzisieren oder auch gewöhnliche Adapterfehler sammeln und durch einen gezielten Fehlertest absichern. Keine pauschale Fangregel für SIGKILL/Stromausfall versprechen.

### [NIEDRIG / TESTAUSSAGE] client2-JSON wird im Gesamttest als „client“ gelabelt

**Stellen:** `checks.py:118`, erlaubte Labels in `ue6.1/adressen.py:48`.

Für die client2-Aufnahme wird beim CLI-Test ersatzweise `--host client` angegeben. Der exakte Adressvergleich davor (`checks.py:113–114`) bleibt korrekt; dieser zusätzliche CLI-Aufruf bestätigt aber **nicht** die richtige Herkunftsbeschriftung des neuen Clients. Er prüft lediglich die JSON-Verarbeitung unter einem fremden Label. Optional den begrenzten Testzweck benennen oder getrennt die Adapterfunktion mit echtem Label testen. Kein Fehler der eigentlichen Adress-/Routenlösung.

## Fachliche Einzelprüfung

| Aufgabe | Geprüftes Ergebnis |
|---|---|
| **6.1** | Alle sechs Dateninterfaces stimmen mit `Angabe/start_lab.py:23–33,50–58` überein: Client/r1 links `/24`, r1/r2 Transit `/30`, r2/Server rechts `/24`. Die drei Netze sind `10.0.1.0/24`, `10.0.12.0/30`, `10.0.2.0/24`, nicht ein gemeinsames `/8`. Die vorhandenen Namespace-Aufnahmen enthalten zusätzlich `lo`; der JSON-Adapter gibt es korrekt aus. Tabelle, Netzzuordnung und Trennung durch Router vollständig. |
| **6.2** | r1s Serverroute geht über `10.0.12.2` auf `r1-eth1`, r2s Rückroute über `10.0.12.1` auf `r2-eth0`. Endgeräte haben lokale Defaultgateways, Router keine Default Route. Hin-/Rückweg, ARP-Ziel je Link, LPM, TTL und Forwarding sind korrekt erklärt. Die Tabellen sind als Sollplan markiert und stimmen mit den archivierten Kernelrouten überein. |
| **6.3** | Nur die zwei entfernten LAN-Routen werden gelöscht; direkt angeschlossene Routen bleiben erhalten. Alle manuellen Delete-/Add-Schritte sind dokumentiert. `ping3()` verlangt exakte gesendete/empfangene Zähler und passenden Exitstatus; insbesondere wird 100 % Verlust nicht wegen des Teilstrings `0% packet loss` akzeptiert. Der Originalfehler bleibt zu Recht unverändert in der Vorlage und wird im eigenen Code nicht übernommen. |
| **6.4** | `/24`, `/26`, `/27`, `/30` liefern 254, 62, 30 und 2 klassische Hostadressen. Masken, erste/letzte Hosts und Broadcasts stimmen. `10.10.0.0/24`, `10.10.1.0/26`, `10.10.1.64/27`, `10.10.1.96/30` liegen ausgerichtet und überschneidungsfrei im gewählten `/23`. 356 belegte und 156 freie Adressen sind richtig. Selbst mit je einem zusätzlichen LAN-Gateway bleibt genug Kapazität. `/31` ist zutreffend als gesonderte P2P-Konvention abgegrenzt. |
| **6.5** | Alle zehn Kanten stimmen mit dem Originalbild überein; insbesondere kein erfundener B–G-Link. Auswahl `A,B,C,G,F,D,E`; Distanzen in Reihenfolge A–G `(0,1,3,8,9,6,4)`. Beide gleich kurzen Wege nach F und daraus nach E sind vollständig angegeben; ein einzelner Vorgängerbaum darf bei F den zuerst gefundenen Weg über B behalten. |
| **6.6** | Alle sieben Kanten stimmen mit dem Originalbild überein. Anfangsvektor B `(8,0,7,∞,3)`, Fixpunkt `(5,0,7,11,3)`. Die Angabe legt keinen vollständigen Zustellplan fest. Die gewählte kostenaufsteigende asynchrone Reihenfolge ist ausdrücklich eine Zusatzannahme, keine aus der Angabe abgelesene Messung. Global beginnt sie mit A→E bei Kosten 2; B empfängt E,C,A bei Kosten 3,7,8. Der Zwischenwert nach D=17 ist korrekt, weil E zuvor A→E verarbeitet und D bereits mit 14 kennt. Erst C→B verbessert auf 11. Initialtabelle, jede B-Zustellung, Änderungen und Vektoren sind angegeben; für fremde Empfänger gilt ausdrücklich die letzte B-Tabelle weiter. Die synchrone Alternative trennt alte Rundendaten korrekt ab. Netzweite, nicht nur bei B beobachtete Konvergenz wird geprüft. |
| **6.7** | `s1` verbindet client, client2 und `r1-eth0` zu einem gemeinsamen L2-LAN. Dadurch funktioniert `10.0.1.3/24` mit Gateway `10.0.1.1`, ohne zwei geroutete r1-Ports im selben Subnetz zu erzeugen. Alle bisherigen Routerinterfacenamen bleiben passend zur Originalkonfiguration. r2s `/24`-Rückroute deckt beide Clients ab. `OVSBridge` und `controller=None` sind strukturell passend; tatsächliche OVS-Laufzeit bleibt offen. Der Zusatzstarter ruft die originale Basiskonfiguration auf, konfiguriert client2, prüft Pings streng und öffnet wirklich `CLI(net)`. Die Arbeitskopie löst den Widerspruch zwischen ausdrücklichem Auftrag 6.7, Anhang „nicht verändern“ und Vorlagekommentar „6.8“ ohne Änderung der Originale. |

### Eigene rechnerische Gegenproben

Shell-Arithmetik, unabhängig von den Ergebnisliteralen der Lösung, bestätigte unter anderem:

```text
VLSM capacities: 254 62 30 2
VLSM next-smaller: 126 30 14 0; used=356 free=156
VLSM offsets modulo block size: 0 0 0 0
A-B-F=6 A-C-G-F=6 A-B-D=8 A-B-F-E=9 A-B-D-E=10
B-E-A=5 B-C-D=11 B-E-C-D=12 async-initial-D=17
```

Zusätzlich wurden die vorhandenen vollständigen Pfadenumerationen und die synchronen/asynchronen DV-Vergleiche tatsächlich ausgeführt. Damit wird nicht allein auf hart codierte Endvektoren vertraut.

## Vorhandene echte Namespace-Nachweise

- `basis-routen-und-ping.txt` und `erweitert-routen-und-ping.txt`: je **3/3 vor Löschung**, **0/3 ohne statische Routen**, **3/3 nach Wiederanlage**; zugehörige Pingstatus **0,1,0**. Beide Router zeigen nach Delete `Network is unreachable` mit Status 2; Delete/Add selbst Status 0. Vollständige Echo-Sequenzen 1,2,3 sind vorhanden, nicht nur Prozentangaben.
- Rückpings Server→client, Server→client2 sowie client2→client: jeweils 3/3. TTL 64 im gemeinsamen Client-LAN und 62 über zwei Router sind mit dem Aufbau vereinbar; die sehr kurzen Laufzeiten werden nicht als TCLink-Messung ausgegeben.
- Drei Client-TCP-Protokolle enthalten jeweils exakt die drei Original-Echo-Nutzdaten. Der Basisserver protokolliert eine Verbindung von `10.0.1.2`; der erweiterte Server nacheinander Verbindungen von `10.0.1.2` und `10.0.1.3`, jeweils drei empfangene Nachrichten zu 21 Bytes. Die Quellports werden als Messwerte, nicht als feste Vorgaben behandelt.
- Die Aussage, dass die unveränderten Anwendungen beide Clients bedienen können, ist damit auf Namespace-Ebene belegt. Die dokumentierte Einschränkung bleibt richtig: TCP ist ein Bytestrom; diese drei gelungenen Echos beweisen keine allgemeine Nachrichtengrenzengarantie von `recv(4096)`.
- Sicherheitsprüfung des Runners: `verify_namespaces.py:176` erzeugt vor allen Links, Bridges, Adressen oder sysctls einen neuen äußeren Netzwerk-Namespace. Weitere Knoten bekommen eigene Netznamespaces. Das Original-Hostnetz wird nicht anhand einer bloß leeren Routingtabelle für „isoliert“ erklärt. Vorhandenes `run01` wird nicht überschrieben.

## In dieser Prüfung tatsächlich ausgeführte Tests

Alle folgenden Aufrufe liefen ohne Bytecode-Erzeugung mit `PYTHONDONTWRITEBYTECODE=1` und `python3 -B`:

| Aufruf / Umfang | Tatsächliches Ergebnis |
|---|---|
| `ueb06/ue6.1/adressen.py --test` | Status 0; Plan, Präfix, IPv4-Filter, leeres Interface, Loopback OK |
| `ueb06/ue6.2/routing.py --test` | Status 0; Hin-/Rückweg, LPM, fehlende Route, Forwarding OK |
| `-m unittest discover -s ueb06/ue6.3 -p 'test_*.py' -v` | 4 Tests, OK, Status 0 |
| `-m unittest discover -s ueb06/ue6.6 -p 'test_*.py' -v` | 6 Tests, OK, Status 0; einschließlich exakter Reproduktion aller Antworten 6.4–6.6 und Erklärungsvollständigkeit |
| `-m unittest discover -s ueb06/ue6.7 -p 'test_*.py' -v` | 7 Tests, OK, Status 0; ausdrücklich API-Doubles, keine echten Mininet-Pakete |
| `ueb06/ue6.4/subnetting.py`, `ueb06/ue6.5/dijkstra.py`, `ueb06/ue6.6/distance_vector.py` | Alle Status 0; sämtliche eingebauten Assertions aktiv und bestanden; keine `--write`-Option verwendet |
| `ueb06/ue6.1/adressen.py --host r1 --json ueb06/nachweise/run01/basis-r1-addr.json` | Status 0; korrektes Loopback, Client-LAN und Transitnetz aus vorhandener Aufnahme |
| Sieben ausgewählte Methoden aus `ueb06.checks.SheetChecks` | 7 Tests, OK, Status 0: `test_all_exercises_and_old_suites`, `test_original_archive_byte_equality`, `test_syntax_headers_and_shell_syntax`, `test_relative_markdown_links`, `test_namespace_addresses_and_provenance`, `test_exact_ping_counts_statuses_and_route_cycle`, `test_original_tcp_echo_content_and_server_connections` |
| `-m zipfile -t ueb06/Angabe/uebb6_template.zip` | Status 0, `Done testing`; zusätzlich zum bytegenauen Originalvergleich |
| `ueb06/ue6.3/static_routes.py --mininet` | Erwarteter Blocker: Status 2, fehlendes Modul `mininet`; kein Lab gestartet |

Python laut Werkzeugausgabe: `python3` **3.14.7**, `/usr/bin/python3` **3.13.3**. Der Namespace-Runner verlangt mindestens Python 3.12; der fest eingetragene Systeminterpreter erfüllt diese Voraussetzung.

## Werkzeug- und Änderungsgrenze

`execute_code`, ein zusätzlicher Python-`-c`-Prüfversuch und ein Python-stdin-Skript wurden von der Richtlinie der unbeaufsichtigten Sitzung blockiert und **nicht ausgeführt**. Stattdessen liefen die vorhandenen regulären Testdateien, gezielte unittest-Methoden und Shell-Gegenrechnungen. `unzip` war nicht installiert; Archivtest und Bytevergleich gelangen ohne Installation über vorhandenen Python-Code. Keine Ersatzresultate für blockierte Aufrufe erfunden.

Durch diesen Review wurde ausschließlich **`ueb06/review.md`** neu erstellt. Keine Lösungsdatei, Originaldatei, Messdatei, parallele Dokumentation oder Git-Daten verändert; keine neue Netzwerkmessung erzeugt und kein Paket installiert.

**Nachtrag des Elternlaufs:** Die Antworten6.1–6.3 verlinken inzwischen zusätzlich die tatsächlich ausgeführten Namespace-Nachweise. Die Wiederherstellungszusage in6.3 ist auf `RuntimeError` präzisiert; die dokumentierte Adaptergrenze ist damit nicht länger überzogen. Der vollständige Gesamttest einschließlich der inzwischen fertigen Gesamterklärung lief danach erfolgreich (9 Testgruppen). Das ist eine nachträgliche Elternprüfung, keine Behauptung über den ursprünglichen unabhängigen Reviewumfang.

## KI-Kennzeichnung

Hermes Agent, OpenAI gpt-6.1-sol; Datum der Bearbeitung: 2026-10-29. Tatsächliche Anfrage: Unabhängige fachliche und technische Endprüfung der Original-PDF einschließlich Bilder, Antworten/Code 6.1–6.7 und echter Namespace-Nachweise; vorhandene Tests ausführen, Must-fix-Befunde und verbleibende Mininet-Grenze ausschließlich in `ueb06/review.md` dokumentieren.
