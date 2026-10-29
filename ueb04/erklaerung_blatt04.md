# Übungsblatt 04 – Lernweg, Code und echte Nachweise

Dieses Dokument ist der Einstieg für Fabio: erst das Netzwerkmodell verstehen, dann UDP senden, Pakete lesen, Routing prüfen und zuletzt TCP-Nachrichten sauber abgrenzen. Jede Codeänderung muss zu einer überprüfbaren Beobachtung passen. **Vorhandener Testbefund, erwartete Laborkonfiguration und noch auszuführende Anleitung sind nicht dasselbe.**

Grundlagen: [Original-PDF](angabe_blatt04.pdf) und die unveränderten Python-Originale in [Angabe/](Angabe/). Die eigenen Programme stehen in den Aufgabenordnern; der zusätzliche Integrationsrunner liegt im Wurzelordner dieses Blatts. Die folgenden Links verwenden relative Pfade.

## 1. Lernweg über alle sechs Aufgaben

### Ü4.1 – Welcher Prozess sieht welches Netz?

Zuerst [antwort.md](ue4.1/antwort.md), dann [diagnose.py](ue4.1/diagnose.py) mit [vollständiger Zeilenerklärung](ue4.1/erklaerung.md) lesen. Kernidee: Der Netzwerk-Namespace bestimmt sichtbare Interfaces und Routen. Ein virtuelles Ethernetinterface benutzt denselben echten Linux-IP-Stack wie andere Linux-Interfaces. Der Prozess auf h1 sieht deshalb nicht automatisch h2s Interfaces. Ein gewöhnlicher Hostname ist dagegen kein Beweis für einen eigenen Netzwerk-Namespace; UTS und net sind verschiedene Namespacearten.

In der vorgesehenen VM `sudo mn` und dann `nodes`, `net`, `links`, `dump`, `h1 ip addr`, `h2 ip addr`, `h1 ip route`, `h2 ip route` verwenden; das ist eine **Anleitung, kein hier belegter Mininetlauf**. Der eigene Diagnosecode liest nur seinen geerbten Kontext. Er erzeugt weder h1 noch h2. Die tatsächlichen Zusatzansichten [h1-network.txt](nachweise/run01/h1-network.txt) und [h2-network.txt](nachweise/run01/h2-network.txt) stammen vom Namespace-Runner mit Linux-Bridge.

Live erklären/ändern: zuerst zeigen, wo die Diagnose-Befehlslisten entstehen und warum `--context h1` nur ein Label ist. Danach die beiden Netzwerkansichten vergleichen. Keine Hostadresse als vermeintliche Laboradresse in einen Bericht schreiben.

### Ü4.2 – Zwei Terminals sind zwei Bedienwege, nicht zwei Rechner

[Antwort](ue4.2/antwort.md), [diagnose.py](ue4.2/diagnose.py), [Zeilenerklärung](ue4.2/erklaerung.md). Die Laboranweisung `xterm h1 h2` öffnet laut Angabe Konsolen in den jeweiligen Netzwerkumgebungen. Unterschiedliche IPs und Routen kommen vom Netzwerk-Namespace, nicht vom Fenstertitel; gleicher hostname ist bei gemeinsamem UTS möglich. Programme können bei gemeinsamem Dateisystem trotzdem dieselben Dateien lesen.

Live zuerst `ip addr`, `ip route` und `hostname` in den vorgesehenen Hostterminals vergleichen, dann den Diagnoseplan erklären. **Die xterm-Fenster wurden hier nicht ausgeführt oder aufgenommen.** Namespacebelege ersetzen diesen GUI-Arbeitsschritt nicht. Die echten Wireshark-Screenshots weiter unten sind eine andere GUI und keine xterm-Belege.

### Ü4.3 – Ein UDP-Datagramm vom Client zum Server

[Antwort](ue4.3/antwort.md), [server.py](ue4.3/server.py), [client.py](ue4.3/client.py), [test_udp.py](ue4.3/test_udp.py), [Erklärung aller drei Dateien](ue4.3/erklaerung.md). Reihenfolge: Server bindet → READY → Client kodiert Text in UTF-8 → ein Datagramm → Server zeigt Bytes und Absender. In der Standardtopologie ist das Ziel `10.0.0.2:5000`. `127.0.0.1` bezeichnet immer den lokalen Namespace, nicht den anderen Host. Die Portnummer identifiziert den lokalen UDP-Endpunkt innerhalb des Zielhosts.

Live zuerst nur `--message` ändern und erneut senden, dann leerer Text und Umlaute/Emoji. Die Bytezahl ist nicht allgemein die Zeichenanzahl. Danach `--count`, `--timeout`, Zielport und Quellport unterscheiden. Ein UDP-connect speichert den Partner und lässt die lokale Route wählen; es gibt keinen TCP-Handshake. SENT allein garantiert keine Zustellung. Der eigene Server sendet wie das PDF **keine Antwort**.

### Ü4.4 – Aus Pythonwerten werden sichtbare Paketfelder

[Antwort mit konkreten Paketwerten](ue4.4/antwort.md), [analyse_pcap.py](ue4.4/analyse_pcap.py), [Zeilenerklärung einschließlich aller Prüfungen](ue4.4/erklaerung.md). Zuerst [udp.pcap](nachweise/run01/udp.pcap) und [UDP-Screenshot](nachweise/run01/wireshark-udp.png) ansehen, dann die passenden Frames aus [udp-analyse.json](nachweise/run01/udp-analyse.json) vergleichen.

Layer-Zuordnung: Ethernet zur Netzzugangsschicht, IPv4 zur Internetschicht, UDP zur Transportschicht, Textbytes zur Anwendung. Der UDP-Header umfasst acht Bytes; die Nutzlastlänge wird an den wirklich kodierten Bytes gemessen. Die erste Standardnachricht umfasst laut vorhandener Auswertung 19 Nutzbytes. Ein 4096-Byte-Empfangspuffer oder ein Python-Variablenname wird nicht zu einem UDP-Headerfeld.

Live erst Quelle/Ziel, Ports, UDP-Länge und Payload im Paketbaum suchen; dann UTF-8-Nutzlast vergleichen. Danach die **Lesefunktion** und die **Sollprüfungen** im Analyseprogramm unterscheiden. Neue Nachrichten erfordern neue Captures und passende, ehrlich gewählte Sollwerte. Keine Tests mit `python -O` starten: assert darf nicht abgeschaltet werden.

### Ü4.5 – Zwei Netze brauchen Router und Rückweg

[Antwort](ue4.5/antwort.md), [diagnose.py](ue4.5/diagnose.py), [Zeilenerklärung](ue4.5/erklaerung.md). Erst die unveränderten Originale [topology.py](Angabe/topology.py) und [start_lab.py](Angabe/start_lab.py) lesen. Client `10.0.1.2/24` erreicht das Gateway `10.0.1.1`, Router erreicht den Server über `10.0.2.1/24`, Server selbst ist `10.0.2.2/24`. Client und Server liegen nicht im selben Ethernet-/IPv4-Subnetz. Der Router benötigt je eine Adresse pro angeschlossenem Netz und aktiviertes IPv4-Forwarding. Die Server-Default-Route liefert den Rückweg über `10.0.2.1`.

Dann [client-network.txt](nachweise/run01/client-network.txt), [router-network.txt](nachweise/run01/router-network.txt), [server-network.txt](nachweise/run01/server-network.txt) und [ping.txt](nachweise/run01/ping.txt) lesen. Die negative Probe [ping-forwarding-off.txt](nachweise/run01/ping-forwarding-off.txt) gehört zur selben realen Namespaceprüfung: ohne Routerforwarding scheitert der Ping. Sie ist kein erfundener Soll-Log.

Live zuerst die Ausgangsroute erklären, dann die Router-Interfaces und den Rückweg. `ip route get` liest die Routingentscheidung, sendet aber keinen Ping. Die eigene diagnose.py verändert nichts. Der Integrationsrunner dagegen erzeugt Netze und ändert Forwarding nur in den dafür isolierten Test-Namespaces. `20ms` bezeichnet die konfigurierte Verzögerung je behandeltem Ausgang, nicht pauschal die gesamte Ping-Roundtripzeit.

### Ü4.6 – TCP liefert Bytes, nicht automatisch Nachrichten

[Antwort mit Ablauf und Bedienung](ue4.6/antwort.md), [vollständige bestehende TCP-Zeilenerklärung](ue4.6/erklaerung.md). Lernreihenfolge: [protocol.py](ue4.6/protocol.py) → [server.py](ue4.6/server.py) → [client.py](ue4.6/client.py) → [test_tcp.py](ue4.6/test_tcp.py). Socket/Listener, accept-Socket und Anwendungsnachricht sind verschiedene Ebenen.

Der Kernel erledigt SYN, SYN/ACK, ACK; die Anwendung benötigt trotzdem Framing für mehrere Texte. Hier endet jeder UTF-8-Text mit LF. Ein recv kann einen Teil einer Nachricht oder mehrere Nachrichten enthalten. Erst vollständige Frames streng dekodieren, den Rest puffern. Leerer Text ist ein einzelnes LF; b'' von TCP-recv ist EOF. Nach den geprüften Echos beendet der Client seine Senderichtung mit Half-Close und liest bis Server-EOF. Persistenz spart wiederholten Verbindungsauf-/abbau, verlangt aber saubere Nachrichtengrenzen.

Live erst eine Nachricht pro Verbindung, dann mehrere über dieselbe Verbindung; danach die Tests zu Fragmentierung, zusammengefassten Nachrichten und EOF. [tcp.pcap](nachweise/run01/tcp.pcap), [tcp-analyse.json](nachweise/run01/tcp-analyse.json) und [TCP-Screenshot](nachweise/run01/wireshark-tcp.png) zeigen den realen Zusatzlauf mit zwei Verbindungen. Die Parser-Testdoubles erzwingen Empfangsgrenzen; ein echter sendall-Aufruf garantiert keine bestimmte Segment- oder recv-Aufteilung.

## 2. Originalquellen: alle sechs Python-Dateien

Die Originale bleiben unverändert. Ihr Quelltext ist maßgeblich dafür, was ein konkretes Originalskript tatsächlich macht; das PDF enthält daneben Arbeitsanweisungen und eigene Kurzbeispiele. Die Originale sind **nicht** die eigenen Lösungen und nicht die zusätzlichen Namespacebelege.

| Originaldatei | Zweck, Lesereihenfolge und Unterschied zum PDF | Umgang bei Änderungen |
|---|---|---|
| [Angabe/check_environment.py](Angabe/check_environment.py) | Vor dem Labor lesen/auf der vorgesehenen VM ausführen: zeigt Pythonversion, sucht mn/xterm/ovs-vsctl/tc und importiert mininet. Verfügbarkeit ist noch kein erfolgreicher Topologielauf. | Nicht als Installation verwenden und nicht ändern; fehlende Laborwerkzeuge gemäß PDF mit der Übungsleitung klären. |
| [Angabe/standard_mininet.py](Angabe/standard_mininet.py) | Einführung h1–s1–h2 mit OVSSwitch und 10.0.0.1/24 bzw. 10.0.0.2/24. **Es startet keine Mininet-CLI:** Die ausgegebenen Beispielbefehle werden nicht ausgewertet; das Skript wartet auf ENTER und stoppt dann im finally. Die PDF-Einführung verwendet dagegen `sudo mn` mit echter Mininet-Shell. | Nicht ändern; für die PDF-Shellbefehle den vorgesehenen `sudo mn`-Weg unterscheiden. Bloßes Abtippen eines h1-Kommandos bei input dieses Skripts würde die Topologie beenden, nicht den Befehl ausführen. |
| [Angabe/topology.py](Angabe/topology.py) | Als Nächstes für Ü4.5/4.6 lesen: definiert Konstanten für IPs/Gateways, LinuxRouter mit Forwarding und RNLabTopo mit zwei TCLinks, Delay 20ms und Verlust 0. Die Interface-Namen/Links entstehen in build; die tatsächliche IP-/Routenzuweisung übernimmt start_lab.py. | Laut PDF Infrastruktur nicht ändern. Für die Erklärung die Stellen zeigen, statt die erwarteten Adressen durch Hostmesswerte zu ersetzen. |
| [Angabe/start_lab.py](Angabe/start_lab.py) | Baut RNLabTopo mit Mininet, konfiguriert Adressen/Routen, zeigt echte Zustände, prüft mehrere Pingrichtungen, öffnet client/router/server mit makeTerm und wartet im Startterminal auf ENTER. Es bietet ebenfalls keine Mininet-CLI. | Nicht ändern. Erst nach den eigenen Anwendungen/Captures ENTER drücken. Gedruckte Expected-Werte und Actual-Ausgaben getrennt lesen. Dieser Originalablauf ist hier nicht ausgeführt. |
| [Angabe/udp_server.py](Angabe/udp_server.py) | Originalbeispiel für die **geroutete RN-Lab-Adresse 10.0.2.2:5000**; Host/Port sind Positionsargumente. Empfängt Datagramme und sendet `ACK: ` plus empfangene Bytes zurück. **Anders als der UDP-Code im PDF für Ü4.3:** Dort 10.0.0.2 und keine Antwort. | Original bewahren; Anpassungen nur in eigenen Dateien. Nicht unbeabsichtigt ACK-Verhalten in die antwortlose eigene Ü4.3 mischen. |
| [Angabe/udp_client.py](Angabe/udp_client.py) | Passender Originalclient mit Ziel 10.0.2.2:5000, optionalen Positionsargumenten für Ziel/Port/Text, UDP-sendto und anschließendem recvfrom mit zwei Sekunden Timeout auf die ACK-Antwort. Mehrere Textargumente werden mit Leerzeichen verbunden. Das PDF-Kurzbeispiel sendet dagegen nur einmal an 10.0.0.2 und wartet nicht. | Original bewahren. Beim Wechsel zu den eigenen --host/--message-Optionen auch den CLI-Vertrag wechseln; Positionsargumente des Originals sind nicht dieselbe Bedienung. |

Das [PDF](angabe_blatt04.pdf) ist die Aufgabenquelle mit sechs Teilaufgaben und dem antwortlosen UDP-Kurzbeispiel. Das vorhandene [Originalarchiv](Angabe/uebb4_template.zip) ist nur die gelieferte Vorlage, **kein neu erzeugtes Abgabe-ZIP**. Der PDF-Anhang nennt zusätzlich README.md; eine solche Datei liegt hier nicht unter Angabe/ und wird deshalb nicht als gelesene/verfügbare Originaldatei verlinkt. Die Originale starten keine der eigenen Testskripte automatisch.

## 3. Katalog aller eigenen Code-Dateien

Die Position in der Lernfolge ist in der zweiten Spalte genannt. Jede Datei hat eine konkrete Zeilenerklärung; Testcode gehört ausdrücklich dazu.

| Eigene Datei | Zweck und Reihenfolge | Typische bewusste Änderungen | Zeilenerklärung |
|---|---|---|---|
| [ue4.1/diagnose.py](ue4.1/diagnose.py) | Erst zum Kontextverständnis: lesende Befehle, Namespace-IDs, strukturierter Bericht; enthält auch eigene Mock-Selbsttests. Erzeugt keine Topologie. | Zuerst CLI-Label/optionale neue Berichtsdatei statt Netzwerte ändern; bei neuem Diagnosebefehl die erwartete Befehlsliste im Selbsttest mitprüfen. | [Ü4.1](ue4.1/erklaerung.md) |
| [ue4.2/diagnose.py](ue4.2/diagnose.py) | Danach für Konsolenkontexte; gleiche Implementierung wie Ü4.1, Aufgabenwahl über Ordnernamen. Label wechselt nicht den Namespace. | Nur im tatsächlich gewünschten Konsolenkontext ausführen; kein künstliches h1/h2 durch verschiedene Labels erzeugen. | [Ü4.2](ue4.2/erklaerung.md) |
| [ue4.3/server.py](ue4.3/server.py) | UDP-Empfänger vor dem Client starten; bind, READY, begrenzbare Anzahl recvfrom, keine Antwort. | --host, --port, --count, --timeout; Codeänderung des 4096-Byte-Empfangslimits mit Clientgrenze abstimmen. | [Server](ue4.3/erklaerung.md#serverpy) |
| [ue4.3/client.py](ue4.3/client.py) | Nach READY eine UTF-8-Nachricht senden; echte Quelladresse/Quellport anzeigen. | --message, --host/--port, optional --local-host/--local-port; Byte- statt Zeichengrenze beachten. | [Client](ue4.3/erklaerung.md#clientpy) |
| [ue4.3/test_udp.py](ue4.3/test_udp.py) | Nach Änderungen lokale echte UDP-/CLI-Tests: UTF-8, leer, Grenzlänge, zu groß, CLI und Timeout. | Neue Randfälle als konkrete Sende-/Empfangsassertions ergänzen; Fehler dürfen nicht durch Entfernen einer Assertion verschwinden. | [Tests](ue4.3/erklaerung.md#test_udppy) |
| [ue4.4/analyse_pcap.py](ue4.4/analyse_pcap.py) | Erst nach Capture: klassische Ethernet-PCAP-Datei dekodieren, eigene UDP-/TCP-Szenarien einschließlich Streams/FIN prüfen und JSON liefern. | CLI-Capturepfad/Prüfart zuerst; bei neuem Testlauf tatsächliche Sollfolge und Filter/Adressen konsistent ändern. Keine beliebigen PCAPs als automatisch unterstützt ausgeben. | [PCAP-Prüfer](ue4.4/erklaerung.md) |
| [ue4.5/diagnose.py](ue4.5/diagnose.py) | Nach Topologiestudium Routingdiagnose; identischer Code wie die anderen Diagnosekopien, aber dieser Ordner aktiviert weitere Route-/Forwarding-/qdisc-Leseabfragen. | In Client-, Router- oder Serverkontext ausführen; fehlende router-Interfaces bei Endpunkten als Fehlerbefund erhalten, nicht fiktiv ersetzen. | [Ü4.5](ue4.5/erklaerung.md) |
| [ue4.6/protocol.py](ue4.6/protocol.py) | Vor TCP-Server/Client lesen: UTF-8 + LF, 4096 Nutzbytes, Generator mit Restpuffer, definierte Protokollfehler. | Größenlimit nur gemeinsam für beide Seiten und Tests ändern; bei anderem Framing beide Encoder/Parser und Tests anpassen. | [TCP-Protokoll](ue4.6/erklaerung.md#protocolpy) |
| [ue4.6/server.py](ue4.6/server.py) | Danach: TCP-Listener, sequentielles accept, beliebig viele Frames je Verbindung, Echo, EOF/Half-Close und Fehlerstatus. | --connections/--timeout/--host/--port vor Quellcodeänderungen verwenden; Verbindungszahl ist nicht Nachrichtenzahl. | [TCP-Server](ue4.6/erklaerung.md#serverpy) |
| [ue4.6/client.py](ue4.6/client.py) | Nach Serverbereitschaft: eine Verbindung für ein oder mehrere Nachrichtenargumente, jedes Echo prüfen und geordnet schließen. | Ein vs. mehrere Nachrichtenargumente; -- vor mit Bindestrich beginnenden Texten verwenden; keine eingebetteten LF. | [TCP-Client](ue4.6/erklaerung.md#clientpy) |
| [ue4.6/test_tcp.py](ue4.6/test_tcp.py) | Nach TCP-Änderungen: deterministische recv-Testdoubles plus echte Loopback-Sockets und CLI-Peers einschließlich Fehlerfälle. | Erst Randfall beschreiben, dann reproduzierbaren Test ergänzen; gezielte Testdoubles sind keine Netzwerkmessungen. | [TCP-Tests](ue4.6/erklaerung.md#test_tcppy) |
| [verify_namespaces.py](verify_namespaces.py) | Abschließend echter Zusatz-Integrationstest: Linux-Bridge/h1/h2, geroutete Netns, Ping/Forwarding-Negativtest, Anwendungen, dumpcap, Cleanup. **Kein Mininet.** | Neuer --output-Ordner zuerst; andere Nachrichten/Adressen/Delay nur gemeinsam mit Laufzeitgrenzen, Capturefiltern und Analyse-Sollwerten ändern. Nur in frischem äußeren Netz-Namespace starten. | [Namespace-Runner](erklaerung_namespace.md) |

Die Diagnosekopien werden durch ihren Ordner ausgewählt. Kopieren in einen anders benannten Ordner ist keine beliebige Umbenennung, weil main unbekannte Aufgabennamen ablehnt. Für alle Programme sind Nutzlasten/Erwartungen im Testcode Sollwerte; nur ein ausgeführter Lauf und seine Ausgaben liefern Messbelege.

## 4. Dokumentationsdateien und Lesereihenfolge

- [ue4.1/antwort.md](ue4.1/antwort.md), [ue4.2/antwort.md](ue4.2/antwort.md), [ue4.3/antwort.md](ue4.3/antwort.md), [ue4.4/antwort.md](ue4.4/antwort.md), [ue4.5/antwort.md](ue4.5/antwort.md), [ue4.6/antwort.md](ue4.6/antwort.md): zuerst die fachlichen Antworten und Bedienabläufe der jeweiligen Aufgabe lesen. Bei einem neuen echten Lauf nur die dazugehörigen tatsächlichen Befunde aktualisieren; Anleitungen nicht in Vergangenheits-Messbehauptungen umformulieren.
- [ue4.1/erklaerung.md](ue4.1/erklaerung.md), [ue4.2/erklaerung.md](ue4.2/erklaerung.md), [ue4.3/erklaerung.md](ue4.3/erklaerung.md), [ue4.4/erklaerung.md](ue4.4/erklaerung.md), [ue4.5/erklaerung.md](ue4.5/erklaerung.md), [ue4.6/erklaerung.md](ue4.6/erklaerung.md): danach jede zugehörige Quellzeile verstehen. Nach Codeänderungen Zeilennummern und Semantik erneut gegen den echten Quelltext prüfen.
- [erklaerung_namespace.md](erklaerung_namespace.md): zuletzt den zusätzlichen Integrationsaufbau und seine Seiteneffekte lesen, bevor dieser privilegiert gestartet wird.
- [erklaerung_blatt04.md](erklaerung_blatt04.md): dieser Lernweg und Katalog; beim Ergänzen neuer eigener Programme oder Belege deren Zweck, Herkunft und Links hier mitpflegen.

## Nachweiskatalog

Die folgenden Dateien existieren im Repo. Sie sind keine noch zu erzeugenden Platzhalter. Gespeicherte Logs werden zum Lernen gelesen, **nicht nachträglich als scheinbar neue erfolgreiche Läufe bearbeitet**. Neue Messungen gehören in neue Dateien/Runordner. Eine Ausführung in der vorgesehenen Mininet-VM bleibt von den echten Zusatztests getrennt.

### Lokale Code-/CLI-Tests

| Datei | Zweck und wann lesen | Typische Fortführung |
|---|---|---|
| [ue4.1/self-test.txt](ue4.1/self-test.txt) | Vor normaler Diagnose: acht erfolgreiche Tests der Befehls-/Fehler-/Speicherlogik. Enthält kontrollierte Mocks, keine h1-Messung. | Nach Diagnoseänderung Selbsttests erneut ausführen, neue Ausgabe separat sichern. |
| [ue4.2/self-test.txt](ue4.2/self-test.txt) | Gleiche acht erfolgreichen Diagnose-Selbsttests für diesen Aufgabenordner; kein xterm-Start. | Nicht als Konsolenvergleich umdeuten; dazu echte Kontexte separat erfassen. |
| [ue4.5/self-test.txt](ue4.5/self-test.txt) | Acht erfolgreiche Tests einschließlich Routing-Befehlsplan; kein Pingmesswert. | Nach Änderung der Route-/Forwardingbefehle Testplan bewusst mitprüfen. |
| [ue4.3/test_udp.txt](ue4.3/test_udp.txt) | Fünf erfolgreiche lokale UDP-Testmethoden; nach dem Lesen von test_udp.py vergleichen. | Bei Nachrichtengrenzen-/CLI-Änderungen neu laufen lassen; kein Mininetbeleg. |
| [ue4.6/test_tcp.txt](ue4.6/test_tcp.txt) | 16 erfolgreiche Parser-/Socket-/CLI-Tests, dokumentierter Exitcode 0. | Vor Netzwerkdiagnose zuerst Codefehler mit diesen Tests eingrenzen. |
| [ue4.6/cli_test.txt](ue4.6/cli_test.txt) | Echter Loopback-CLI-Lauf mit READY-Port, zwei Verbindungen und Einzel-/persistenten UTF-8-/Leertext-Echos; Server/Clients erfolgreich. | Andere Nachrichten in neuem Lauf protokollieren; flüchtige Ports nicht als feste Konfiguration übernehmen. |

### nachweise/run01/ – echter Namespace-Integrationslauf

Erst den [Gesamtbefund](nachweise/run01/results.json), dann Netzwerkzustand, Anwendungsausgaben und zuletzt Pakete/GUI ansehen. Für einen neuen Lauf einen neuen Ordner verwenden. Dateien dieses Ordners nicht einzeln „korrigieren“, um einen anderen Lauf nachzustellen.

| Datei | Zweck und Zusammenhang | Typische nächste Untersuchung |
|---|---|---|
| [nachweise/run01/results.json](nachweise/run01/results.json) | Runner-Gesamtbefund mit ehrlicher Netns-Herkunft und erfolgreich erreichten Checks; kein Mininetlabel. | Jeden zusammengefassten Check mit dem passenden Rohbeleg unten abgleichen. |
| [nachweise/run01/h1-network.txt](nachweise/run01/h1-network.txt) | Tatsächliche h1-Interfaceadressen und Routen der Linux-Bridge-Topologie. | 10.0.0.1/24 und direkt erreichbares Subnetz suchen; mit h2 vergleichen. |
| [nachweise/run01/h2-network.txt](nachweise/run01/h2-network.txt) | Gegenstück für h2 mit Servernetz der UDP-Standardtopologie. | Bindeadresse 10.0.0.2 und Netzpräfix gegen den Serverstart prüfen. |
| [nachweise/run01/udp-clients.txt](nachweise/run01/udp-clients.txt) | Tatsächliche drei SENT-Ausgaben mit lokalen Quellports und Nutzbytes. | Die je Lauf dynamischen Quellports mit den jeweiligen PCAP-Frames vergleichen. |
| [nachweise/run01/udp-server.txt](nachweise/run01/udp-server.txt) | Bereitschaft und drei wirkliche Empfangsmeldungen des antwortlosen Servers. | Prüfen, ob alle gesendeten Texte tatsächlich beim Empfänger sichtbar sind. |
| [nachweise/run01/udp.pcap](nachweise/run01/udp.pcap) | Echte klassische Ethernet-PCAP mit den gefilterten UDP-Datagrammen auf h1-eth0. | Byteprüfer ausführen, danach Paketbaum in Wireshark lesen; nicht manuell ändern. |
| [nachweise/run01/udp.pcap.txt](nachweise/run01/udp.pcap.txt) | Erhaltene dumpcap-Statusausgabe zur UDP-Aufnahme, unter anderem Abschlusszählung. | Capturezustand mit tatsächlicher Recordanzahl abgleichen; kein Nutzlast-Ersatz. |
| [nachweise/run01/udp-analyse.json](nachweise/run01/udp-analyse.json) | Separate stdlib-Analyse der echten UDP-PCAP: Paketfelder, Hexnutzlasten und bestandene Szenarioprüfung. | Gegen Rohbytes und aktuelle Sollfolge vergleichen; nicht als vom Runner direkt erzeugt bezeichnen. |
| [nachweise/run01/wireshark-udp.png](nachweise/run01/wireshark-udp.png) | Screenshot der tatsächlich geöffneten Wireshark-GUI: drei UDP-Pakete, erstes Paket ausgewählt, Paketbaum/Bytes sichtbar. | In der GUI weitere Header aufklappen; Screenshot ist keine zusätzliche Paketerzeugung und kein Mininetbeleg. |
| [nachweise/run01/client-network.txt](nachweise/run01/client-network.txt) | Adressen, Routen, beide Route-Lookups und qdisc-Ansicht des gerouteten Clients. | Default-Gateway 10.0.1.1 und ausgehendes Interface zum Server begründen. |
| [nachweise/run01/router-network.txt](nachweise/run01/router-network.txt) | Tatsächliche zwei Routerinterfaces, direkt angeschlossene Netze, Route-Lookups und netem-qdiscs. | Linke/rechte Route und die beiden 20ms-Ausgangswarteschlangen zuordnen. |
| [nachweise/run01/server-network.txt](nachweise/run01/server-network.txt) | Serverzustand mit Adresse, Rückweg, Lookups und qdisc. | Rückroute zum Client über 10.0.2.1 erklären. |
| [nachweise/run01/ping.txt](nachweise/run01/ping.txt) | Vier tatsächlich beantwortete Client→Server-Pings über den Router mit gemessenen Laufzeiten. | Positive Erreichbarkeit von bloß vorhandenem Routingtabelleneintrag unterscheiden. |
| [nachweise/run01/ping-forwarding-off.txt](nachweise/run01/ping-forwarding-off.txt) | Echte negative Probe bei deaktiviertem Routerforwarding: ein Paket gesendet, keines empfangen. | Mit unveränderten Routen und dem vorherigen Erfolg vergleichen; nicht als künstliches Sollfixture behandeln. |
| [nachweise/run01/tcp-clients.txt](nachweise/run01/tcp-clients.txt) | Echte geprüfte Echos beider TCP-Clientläufe: Einzeltext und drei Texte in einer persistenten Verbindung. | Die vier Anwendungsantworten den zwei TCP-Flows zuordnen. |
| [nachweise/run01/tcp-server.txt](nachweise/run01/tcp-server.txt) | Tatsächliche READY-/RECEIVED-Ausgaben des gerouteten TCP-Servers. | Gemeinsamen Clientport der drei persistenten Nachrichten erkennen. |
| [nachweise/run01/tcp.pcap](nachweise/run01/tcp.pcap) | Echte Aufnahme auf client-eth0 mit beiden TCP-Flows einschließlich Auf-/Abbau; nicht aus Testfixtures synthetisiert. | Handshakes, Nutzbytes, FIN/ACK pro Flow statt nur globaler Paketliste betrachten. |
| [nachweise/run01/tcp.pcap.txt](nachweise/run01/tcp.pcap.txt) | dumpcap-Abschlussstatus/Zählung der TCP-Aufnahme. | Mit PCAP und Analyse vergleichen; erfolgreiche Aufzeichnung ist nicht allein aus einem Dateinamen abzuleiten. |
| [nachweise/run01/tcp-analyse.json](nachweise/run01/tcp-analyse.json) | Separate Prüfung beider Handshakes, rekonstruierter Echo-Streams und FIN-Bestätigungen; Framebezüge sind gespeichert. | In Wireshark die genannten Frame-Nummern nachschlagen; Voraussetzungen des spezialisierten Prüfers beachten. |
| [nachweise/run01/wireshark-tcp.png](nachweise/run01/wireshark-tcp.png) | Echte Wireshark-Ansicht mit 24 TCP-Paketen, SYN/SYN-ACK/ACK, Daten und FIN/ACK für beide Verbindungen. | Mit Follow TCP Stream Payload und LF-Framing lesen; die Ansicht belegt keinen xterm- oder Mininetstart. |

## 5. Schnellkarte für die Live-Erklärung

1. **Welche Umgebung?** net-Namespace bestimmt Interface-/Routingansicht; hostname allein genügt nicht. `--context` ist ein Label.
2. **Welche Adressen?** Standard-UDP: h1 10.0.0.1 → h2 10.0.0.2. Geroutetes RN-Lab/TCP: 10.0.1.2 → Router → 10.0.2.2. Original-UDP-Beispiele verwenden ebenfalls das geroutete Ziel, anders als der PDF-Kurzcode.
3. **Welche Daten?** Text zuerst UTF-8-kodieren; UDP bewahrt Datagrammgrenzen, TCP liefert einen Stream. Leere UDP-Nutzlast ist nicht TCP-EOF.
4. **Was zuerst starten?** Netzwerk → Server/READY → Capturebereitschaft → Client → Serverende → vollständiges Captureende → Analyse → GUI. Beim UDP-Runner beginnt der Server vor dem Capture, beim TCP-Runner das Capture vor dem Server; entscheidend ist, dass vor dem Client beides bereit ist.
5. **Was gemeinsam ändern?** Adressen/Ports auf passenden Seiten, Payload mit Solltests, Framing auf beiden TCP-Seiten, Capturefilter und Prüfannahmen. Neue Daten brauchen neue Nachweise.
6. **Woran erkennt man Erfolg?** Echte Empfängerausgabe, Prozessstatus und passende Rohpakete zusammen betrachten; bei TCP zusätzlich vollständige Streams und Abschluss. Eine gedruckte Erfolgsmeldung oder vorhandene Datei allein genügt nicht.

Reine Leseprüfung der vorhandenen Captures, aus `ueb04`, ohne neue Dateien:

```sh
python3 -B ue4.4/analyse_pcap.py nachweise/run01/udp.pcap --kind udp
python3 -B ue4.4/analyse_pcap.py nachweise/run01/tcp.pcap --kind tcp
```

Der vollständige privilegierte Runner wird hier nur erklärt, nicht zur Dokumentationsänderung erneut ausgeführt. Seine Startvoraussetzungen, sichere Isolation und Cleanup-Grenzen stehen in [erklaerung_namespace.md](erklaerung_namespace.md). Den vorhandenen Ordner run01 kann er aufgrund der Neuerzeugungsprüfung nicht noch einmal als frischen Zielordner verwenden.

## 6. Grenzen und Abgabestatus

**Tatsächlich vorhanden:** lokale Code-/CLI-Tests, echte Linux-Netzwerk-Namespaces, Linux-Bridge und veth-Links, reales Routing/netem, Ping mit positiver und negativer Forwardingprobe, echte UDP-/TCP-PCAPs, unabhängige Python-Byteanalyse und echte Wireshark-GUI-Screenshots. Das sind echte Zusatztests, keine simulierten Netzwerkantworten.

**Weiterhin nicht ausgeführt:** Mininet, OVS und xterm in der vorgesehenen Laborumgebung. Ein Linux-Bridge-Switch ist kein Open vSwitch. Ein Namespace-Runner mit passenden Adressen ist kein ausgeführtes Original-Mininet-Skript. Wireshark-Screenshots ersetzen keine zwei xterm-Hostterminals. Die jeweiligen VM-Anleitungen bleiben Anleitungen.

TShark konnte die Repo-PCAPs wegen Dateizugriffsbegrenzungen nicht öffnen. Es wird kein erfolgreicher TShark-Lauf behauptet; stattdessen liegen stdlib-Auswertung und echte Wireshark-GUI-Beobachtung vor. Keine Sicherheitsregeln wurden für einen solchen Workaround abgeschaltet. Ein lokaler Hostdiagnosebericht ist nicht veröffentlicht und wird hier nicht als Nachweisdatei erfunden.

Die Zeilenabdeckung wurde anhand der **tatsächlich abgelegten Quellen** durch ein echtes Python-Prüfskript im Scratch ausgeführt und bestätigt: server.py **40/40**, client.py **38/38**, test_udp.py **70/70** (jeweils Ü4.3), analyse_pcap.py **133/133**, verify_namespaces.py **198/198**; insgesamt **479/479 nichtleere Quellzeilen**, jede genau einmal erklärt, ohne fehlende, zusätzliche oder doppelte Nummern. Das Skript prüfte außerdem lokale Linkziele, vollständige Katalogisierung der Python-/Nachweisdateien und per SHA-256-Vergleich, dass nur die sieben erlaubten Markdown-Dateien geändert wurden. Bei Ü4.1, Ü4.2 und Ü4.5 wurde der unveränderte Text vor und nach dem vorgesehenen Schlussabsatz separat verglichen. Das beweist formale Vollständigkeit und eingehaltenen Änderungsspielraum, nicht automatisch die Richtigkeit jeder Formulierung; deshalb sind die Erklärungen zusätzlich semantisch am Code ausgerichtet. Das Prüfskript gehört nicht zur Abgabe und ändert keine Quellprogramme.

Es wurde weder ein KI-Bericht-PDF noch ein neues ZIP erzeugt; die Gruppennummer fehlt für eine entsprechend benannte Abgabe. Die gelieferte ZIP-Vorlage unter Angabe/ bleibt davon unberührt. Diese Dokumentation behauptet keine persönliche Durchführung durch Fabio.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29. Tatsächliche Anfrage: nur die benannten Markdown-Dateien ergänzen/korrigieren, alle nichtleeren Zeilen der UDP-Dateien, des PCAP-Prüfers und des Namespace-Runners einfach und konkret erklären, bestehende Nachweisgrenzen korrigieren, einen Lernweg über alle sechs Teilaufgaben samt vollständigem Code-/Belegkatalog erstellen und die neue Zeilenabdeckung mit einem echten externen Scratch-Skript prüfen. Programme, Originale, Belege und Git bleiben unverändert.
