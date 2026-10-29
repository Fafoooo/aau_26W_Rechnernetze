# Prüfbericht Blatt06

**KI-Kennzeichnung RN WS26:** Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29. Tatsächliche Anfrage: Erstelle nur Gesamttest, explizite Mininet-Test-Doubles, vollständige Einzelzeilenerklärung und Prüfbericht; prüfe alte Aufgaben, Originalgleichheit, Syntax, Kennzeichnung, Links und vorhandene echte Ping-/TCP-Messwerte, ohne Originale zu verändern.

## Reproduzierbarer ungefährlicher Gesamttest

Vom Repositoryverzeichnis:

```sh
/usr/bin/python3 -B ueb06/checks.py
/usr/bin/python3 -B ueb06/ue6.7/test_topology.py
```

Der verwendete Systeminterpreter meldet **Python 3.13.3**. Kein `sudo`, keine Installation und keine neue Messung sind für diese beiden Testbefehle erforderlich. Kindprozesse erhalten zusätzlich `PYTHONDONTWRITEBYTECODE=1`; Syntaxprüfungen kompilieren ausschließlich im Speicher.

**Abschlussstatus:** Beide oben genannten Befehle wurden tatsächlich mit Exitstatus **0** ausgeführt. Der Gesamttest meldete **9 Testgruppen, alle erfolgreich**; darin wurden die **4** alten Routingtests, **6** alten Algorithmustests und **7** neuen Topologie-API-Tests als separate Prozesse erneut ausgeführt. Der separat gestartete Topologietreiber meldete ebenfalls **7 Tests, OK**.

Auszug aus dem tatsächlichen Gesamtlauf vom 2026-10-29:

```text
Ran 9 tests in 0.729s

OK
Originale, alte Erklärungen und run01 unverändert: True
Grenze: API-Test-Doubles + archivierte echte Linux-Namespace-Messungen; Mininet/OVS/xterm NICHT live verifiziert.
```

`git diff --check` wurde ebenfalls ausgeführt und lieferte keine Beanstandung. Es wurden ausschließlich die vier beauftragten Repositorydateien neu angelegt: `checks.py`, `ue6.7/test_topology.py`, `erklaerung_blatt06.md` und `pruefung.md`. Keine vorhandene Aufgaben-, Original- oder Messdatei wurde geändert.

## Was tatsächlich geprüft wird

| Bereich | Tatsächlicher Prüfumfang |
|---|---|
| 6.1 | `adressen.py --test`, normaler Planmodus und JSON-Modus auf allen vorhandenen Basis-/Erweiterungs-Interfaceaufnahmen; die Client2-Aufnahme bekommt im Altprogramm nur dessen zulässiges Label `client`, ihre Adressen werden davor unabhängig exakt geprüft. |
| 6.2 | `routing.py --test` und normaler Modellmodus; kein Modelloutput wird als ausgelesene Kernelroute ausgegeben. |
| 6.3 | Alle **4** alten `test_static_routes.py`-Tests, CLI-Hilfemodus und zusätzlich vorhandene echte Namespace-Dialoge mit Löschen, Nichterreichbarkeit und Wiederherstellen beider statischer Routen. |
| 6.4–6.6 | Alle **6** alten `test_algorithmen.py`-Tests, tatsächlicher Einzelstart von Subnetting, Dijkstra und Distance Vector sowie exakte Übereinstimmung der generierten Ausgaben mit den abgelegten Antworten. Alte Tests prüfen zusätzlich unabhängige Rechenproben, Zwischenstände, Mutationserkennung und die vollständige ältere Algorithmenerklärung. |
| 6.7 | **7** neue Tests gegen ausdrücklich gekennzeichnete Mininet-API-Doubles: fünf Hosts, genau eine OVSBridge-Deklaration, fünf Links, alle Interfacepaare, Host-/Routerklassen, TCLink und nomineller Delay-Parameter, Forwarding-Lebenszyklus, Original-Basiskonfiguration und Client2-Adresse/Default-Route, drei Pingpaare, echte Starterfunktionen, CLI-Aufruf und Aufräumen in mehreren Fehlerpfaden. |
| Robuste Pingprüfung | Beide englischen Statistikformate, Paketverlust auch bei irreführendem Status null, falsche Sende-/Empfangszahlen, fehlende Statistik und Nichtnullstatus trotz 3/3. Der vorhandene fehleranfällige Original-Teilstringtest wird nicht verändert und nicht als eigener Erfolgstest verwendet. |
| Originale | Exakte Dateinamenmenge und vollständige Bytes aller gelieferten extrahierten Dateien gegen [uebb6_template.zip](Angabe/uebb6_template.zip); keine bloße Größen-/Zeitstempelprüfung. |
| Syntax / KI | Kompilieren aller Python-Dateien ohne Ausführung ihrer Modulrümpfe; `bash -n` für alle Original-Shellhelfer; Tool, Modell, Datum und Anfrage im Header jeder eigenen Pythondatei. Originaldateien bleiben von eigenen KI-Headern ausgenommen. |
| Links | Alle hier verwendeten lokalen Inline-Markdown-Dateiverweise: URL-/HTML-Decodierung, existierendes Ziel und Begrenzung auf das Blattverzeichnis. Keine Behauptung über externe Erreichbarkeit, allgemeines Markdown-Parsing oder Überschriftenanker. |
| Einzelzeilenerklärungen | **519 nichtleere eigene Zeilen** in fünf Dateien werden als geordnete Paare aus physischer Zeilennummer und vollständig identischem Quelltext gegen [erklaerung_blatt06.md](erklaerung_blatt06.md) geprüft. Jede Zeile hat außerdem einen eigenen Erklärungstext. Alte Routing-Erklärungsnummern und die vorhandene Algorithmensuite werden ebenfalls geprüft. |
| Artefakthygiene | Keine Bytecode-, temporären, Sicherungs-, Log- oder Generator-Hilfsdateien im Blattbaum; gleiche Prüfung für den gegenwärtigen Git-Index. Keine Dateien werden gestagt; es erfolgen kein Commit, Push oder neues Abgabe-ZIP. Eine spätere manuelle Auswahl muss erneut geprüft werden. |
| Unverändertheit | SHA-256-Schnappschuss vor/nach dem Test von Originalverzeichnis, Original-PDF, beiden alten Erklärungen und gesamten Nachweisen; der Gesamtlauf scheitert bei Änderungen. |

Die vollständigen neuen Einzelzeilenerklärungen verteilen sich auf `verify_namespaces.py` (**162**), `ue6.7/topology.py` (**28**), `ue6.7/start_erweitert.py` (**38**), `ue6.7/test_topology.py` (**133**) und `checks.py` (**158**). Die Zuordnung ist maschinell gegen die endgültigen Quellen abgesichert, einschließlich Kommentar-/Docstringzeilen und schließender Klammern. Das beweist Vollständigkeit und Aktualität, nicht automatisch fachliches Verständnis.

Die beiden gewichteten Graphen wurden zusätzlich in der gerenderten Originalaufgabenstellung angesehen und mit den vorhandenen Kantenlisten abgeglichen. Die alten [Routing-Erklärungen](erklaerung_routing.md) und [Algorithmen-Erklärungen](erklaerung_algorithmen.md) wurden nicht geändert.

## Vorhandene reale Messwerte: ausschließlich `nachweise/run01`

Der Elternlauf hat [verify_namespaces.py](verify_namespaces.py) bereits erfolgreich mit `sudo -n /usr/bin/python3 -B verify_namespaces.py` ausgeführt. Dieser Prüfauftrag führt ihn **nicht erneut** aus und überschreibt keine Nachweise. Die jetzigen Tests lesen die **30 vorhandenen Dateien** und prüfen ihren Inhalt. [results.json](nachweise/run01/results.json) bezeichnet die Messmethode ausdrücklich als **Linux-Network-Namespaces, Linux-Bridge; NICHT Mininet/OVS; keine TC-Verzögerung**.

### Exakte Pingzählung

| Nachweis | Statistikfolge / erfolgreicher Empfang |
|---|---|
| [Basis: Routendialog](nachweise/run01/basis-routen-und-ping.txt) | Client → Server: **3 gesendet / 3 empfangen**, danach ohne beide statischen Routen **3 / 0**, nach Wiederherstellung **3 / 3**; protokollierte Ping-Exitstatus **0, 1, 0**. |
| [Erweitert: Routendialog](nachweise/run01/erweitert-routen-und-ping.txt) | Dieselbe exakte Statistikfolge **3/3, 3/0, 3/3**, dieselben Status **0, 1, 0**. |
| [Basis: Server → Client](nachweise/run01/basis-server-ping-10.0.1.2.txt) | **3/3**. |
| [Erweitert: Server → Client](nachweise/run01/erweitert-server-ping-10.0.1.2.txt) | **3/3**. |
| [Erweitert: Client2 → Client](nachweise/run01/erweitert-client2-ping-10.0.1.2.txt) | **3/3** im gemeinsamen LAN. |
| [Erweitert: Server → Client2](nachweise/run01/erweitert-server-ping-10.0.1.3.txt) | **3/3** über beide Router. |

Über sämtliche tatsächlichen Pingstatistiken des Laufs sind das **10 Pingaufrufe, 30 gesendete und 24 erfolgreich empfangene Echo-Replies**. Die sechs fehlenden Antworten gehören ausschließlich zu den zwei ausdrücklich erwarteten Negativtests ohne statische Routen. Die Tests prüfen nicht bloß den String `0% packet loss`, sondern exakte Zähler und bei jedem erfolgreichen Block genau die Reply-Sequenznummern **1, 2, 3**. Die zwei positiven Einzel-Pingdateien aus dem Server sowie die Client2-LAN-Probe und der Server-Client2-Ping tragen im Rohtext keinen gesondert angehängten Prozessstatus; für sie werden daher nur die tatsächlichen Statistiken/Sequenzen geprüft. Die Routendialoge enthalten explizite Exitstatus und werden entsprechend strenger geprüft.

Pro Routendialog werden ferner beide exakten Lösch- und Add-Kommandos samt Status null, je Router `ip_forward=1` und genau zwei fehlgeschlagene `ip route get`-Abfragen mit Status zwei geprüft. Die IPv4-JSON-Aufnahmen müssen exakt alle erwarteten Interfaces, Adressen und Präfixe enthalten.

### Unveränderte TCP-Echos

Die Originaldateien [tcp_client.py](Angabe/tcp_client.py) und [tcp_server.py](Angabe/tcp_server.py) bleiben archivgleich. In [Basis-Client](nachweise/run01/basis-client-tcp.txt), [erweitertem Client](nachweise/run01/erweitert-client-tcp.txt) und [Client2](nachweise/run01/erweitert-client2-tcp.txt) müssen jeweils genau diese drei vollständigen Antwortbytes in dieser Reihenfolge stehen:

```text
b'Network layer test 1\n'
b'Network layer test 2\n'
b'Network layer test 3\n'
```

Das `\n` bezeichnet jeweils ein tatsächliches Newlinebyte im Nutzinhalt. `ast.literal_eval` liest die protokollierte Bytesdarstellung und vergleicht die vollständigen Bytes mit den Literalen des Originalclients. Nur eine Teilzeichenfolge oder drei `Reply:`-Vorkommen würden nicht reichen.

Der [Basis-Servernachweis](nachweise/run01/basis-server-tcp.txt) enthält genau eine Verbindung von `10.0.1.2`; der [erweiterte Servernachweis](nachweise/run01/erweitert-server-tcp.txt) genau zwei nacheinander von `10.0.1.2` und `10.0.1.3`. Pro Verbindung sind drei Empfangslängen von jeweils **21 Bytes** gespeichert. Dynamische Quellports werden auf gültige Portwerte geprüft, nicht durch erfundene feste Ports ersetzt. Auch die exakte Anzahl der Serverausgabezeilen und die genaue Menge der fünf TCP-Nachweisdateien werden geprüft.

**Begrenzung des Original-TCP-Codes:** TCP ist ein Bytestrom; ein einzelnes `recv(4096)` garantiert grundsätzlich nicht eine komplette Anwendungsnachricht. Die unveränderte Übungsvorlage verwendet dies trotzdem für ihre kleinen Testnachrichten. Der vorliegende Nachweis bestätigt die konkreten gespeicherten Echos, keine allgemeine Fragmentierungs-/Framingrobustheit und keine gleichzeitige Bearbeitung beider Clients.

## Finaler Elternlauf und Git-Prüfung

Nach Fertigstellung der übrigen Dateien lief `python3 -B ueb06/checks.py` erneut erfolgreich: neun Testgruppen, alle bestanden. Die Antworten6.1–6.3 verlinken jetzt die echten Namespace-Messungen, und die Ausnahmegrenze bei der Routenreparatur ist präzisiert.

Der erste **gestagte** `git diff --cached --check` meldete ausschließlich nachgestellte Leerzeichen in unveränderten Kernel-Rohprotokollen und abschließende Leerzeilen der drei exakt reproduzierbaren Algorithmusantworten. Das frühere unstaged `git diff --check` hatte ungetrackte Dateien nicht umfasst. Die Messdateien werden deshalb nicht kosmetisch verändert. Für den finalen Git-Check werden nur diese beiden Whitespace-Regeln auf dem Kommandoaufruf deaktiviert: `git -c core.whitespace=-blank-at-eol,-blank-at-eof diff --cached --check`. Das ist keine Änderung der Git-Konfiguration oder der gemessenen Inhalte.

## Was ausdrücklich offen bleibt

- **Mininet, Open vSwitch und xterm sind hier nicht verfügbar; nichts wurde installiert.** Der echte Start von [start_erweitert.py](ue6.7/start_erweitert.py) in der vorbereiteten Mininet-/OVS-VM sowie tatsächliche OVSBridge-Ports, TCLink-Verzögerung, GUI-Terminals und Mininet-spezifische Isolation sind **nicht live verifiziert**.
- Ein bestandener API-Double-Test belegt ausschließlich die programmierte Struktur und die angeforderten API-/Kommandoaufrufe. Er ersetzt weder eine Root-/OVS-Ausführung noch echte Pingmessungen. Die vorhandenen echten Linux-Namespace-Messungen sind ein getrennter zusätzlicher Nachweis für Adressierung, Routing und unveränderte Anwendungen.
- Shell-Capture- und Traceroute-Helfer wurden nur auf Syntax geprüft. Es werden keine neuen PCAPs, Screenshots oder Traceroute-Messergebnisse behauptet.
- Der originale Starter zeigt eine Basis-Topologieüberschrift und hat nur einen `input()`-Wartedialog. Der eigene Erweiterungsstarter ergänzt den Client2-Zustand und öffnet eine Mininet-CLI. Diese Abweichung ist dokumentiert, kein stilles Ändern der Originaldatei.
- Es wurde keine Abgabe-ZIP gebaut; die Gruppennummer und abschließende manuelle Abgabeauswahl sind nicht Gegenstand dieses Tests.
