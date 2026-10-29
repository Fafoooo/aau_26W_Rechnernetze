# Blatt 09 – Erklärung und Vorführhilfe für Fabio

KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription. Datum: 2026-10-29.

## 1. Die Antwort, die du zuerst erklären können solltest

**Der Server hat das falsche Standardgateway `10.10.2.254`. Der vorhandene Router im Server-LAN heißt aber `10.10.2.1`. Der Hinweg funktioniert; die Antwort scheitert am Rückweg.** Beide Clients sind betroffen.

Das ist mehr als eine Vermutung aus einem fehlgeschlagenen Ping:

- Die gespeicherte Server-Routenentscheidung für `10.10.1.10` lautet vor der Reparatur `via 10.10.2.254`.
- Der Neighbor-Eintrag für `10.10.2.254` ist nach den Versuchen `FAILED`.
- Im Server-Mitschnitt kommen SYNs von beiden Clients an. Der Server sendet zwölf ARP-Anfragen nach `10.10.2.254`, erhält dazu keine Antwort und sendet auf diesem Interface keine TCP-Antwortpakete.
- Nach genau einer Änderung der Server-Default-Route funktionieren Ping und die unveränderte Originalanwendung für beide Clients.

Ein kurzer Vortragssatz: „Ich habe zunächst die unveränderte Fehlerkonfiguration beobachtet. Der Router liefert die SYNs beim Server ab. Der Server will seine Antwort aber an ein nicht vorhandenes Gateway schicken. Routingzustand und echte ARP-Pakete bestätigen dieselbe Ursache. Deshalb habe ich nur die Default-Route des Servers ersetzt und dieselben Tests wiederholt.“

## 2. Was wirklich gemessen wurde – und was nicht

Die Aufgabenstellung verlangt die vorbereitete Mininet-Umgebung. Hier sind Mininet und OVS nicht installiert; der berichtete echte Startversuch des Originals scheiterte an `ModuleNotFoundError: No module named 'mininet'`. Es wurde nichts nachinstalliert. **Es gibt hier keinen erfolgreichen Mininet-, OVS- oder xterm-Lauf.**

`messen.py` hat stattdessen eine echte Ersatzumgebung aus Linux-Netzwerk-Namespaces, veth-Paaren und Linux-Bridges aufgebaut. Darin liefen die unveränderten Dateien `Angabe/tcp_server.py` und `Angabe/tcp_client.py`. Die PCAPs stammen von echten Kernel-Paketen, nicht von erzeugten Beispielpaketen oder nachgebauten JSON-Antworten. Die gespeicherten Belege liegen ausschließlich in `nachweise/run01/`.

Die Ersatzmessung belegt Routing, ARP und TCP für dieses nachgebildete Netz. Sie belegt **nicht** die Funktion der Mininet-/OVS-APIs, der xterm-Fenster oder die `TCLink`-Verzögerungen der Originaltopologie. Feste MAC-Adressen der Ersatzmessung sind keine Behauptung über MAC-Adressen eines späteren Mininet-Laufs. Netzwerk-Namespaces isolieren Netzwerkzustand; daraus folgt keine vollständige VM mit getrenntem Dateisystem, Hostnamen oder PID-Raum.

Die Originalanwendung hat eine wichtige Eigenheit: Der Client öffnet eine TCP-Verbindung und empfängt eine Begrüßung. Er sendet selbst **keine Anwendungsnutzdaten**. Der Server sendet `RN-Lab forensic test server\n`. Die Szenarioformulierung „Client überträgt eine Nachricht“ ist deshalb ungenau. Gemessen wurde das tatsächliche Verhalten der Originale; der Anwendungscode wurde nicht passend zur Formulierung umgeschrieben.

Die aktuelle Dokumentation erklärt die acht eigenen Analyse-/Messprogramme und zusätzlich `test_nachweise.py`. Die genaue Zeilenerklärung steht in [zeilenerklaerung.md](zeilenerklaerung.md); ausgeführte Regressionen und Grenzen stehen in [pruefung.md](pruefung.md).

## 3. Netzaufbau ohne Tabellen

```text
client1 10.10.1.10/24 --\
                         sw1 -- router -- sw2 -- server 10.10.2.10/24
client2 10.10.1.11/24 --/         |      |
                        router-eth0    router-eth1
                        10.10.1.1/24   10.10.2.1/24
```

- `client1-eth0`: `10.10.1.10/24`, MAC `02:00:00:00:01:10`, Default via `10.10.1.1`.
- `client2-eth0`: `10.10.1.11/24`, MAC `02:00:00:00:01:11`, Default via `10.10.1.1`.
- `router-eth0`: `10.10.1.1/24`, MAC `02:00:00:00:01:01`, Verbindung zum Client-LAN.
- `router-eth1`: `10.10.2.1/24`, MAC `02:00:00:00:02:01`, Verbindung zum Server-LAN.
- `server-eth0`: `10.10.2.10/24`, MAC `02:00:00:00:02:10`, anfangs Default via `10.10.2.254`, danach via `10.10.2.1`.
- Jeder Endknoten und der Router haben zusätzlich ein aktives Loopback-Interface. Die Switches verbinden jeweils ein Ethernet-LAN; sie routen nicht zwischen den beiden `/24`-Netzen.
- Im äußeren, eigens erzeugten Netzwerk-Namespace liegen die Bridges `sw1`, `sw2` und ihre veth-Ports. Die Gegenenden liegen in den Netzwerk-Namespaces der vier Knoten.

`/24` bedeutet hier, dass die ersten drei IPv4-Oktette das Netz bestimmen. `10.10.1.10` und `10.10.1.11` sind lokal zueinander. `10.10.2.10` liegt aus Clientsicht in einem anderen Netz. Der Client braucht daher einen Router. Der Router hat beide Netze als direkt angeschlossene Routen und braucht für diesen Versuch keine Default-Route. `net.ipv4.ip_forward=1` erlaubt ihm, Pakete zwischen seinen Interfaces weiterzuleiten.

## 4. Was jede Datei macht

### Aufgabenstellung und unveränderte Originale

- `angabe_blatt09.pdf`: eigentliche Aufgabenstellung. Sie nummeriert **9.1, 9.3, 9.4, 9.5, 9.6**; eine Aufgabe 9.2 steht dort nicht.
- `Angabe/uebb9_tempplate.zip`: geliefertes Originalarchiv, Referenz für die Vorlagen. Der ungewöhnliche Dateiname ist unverändert.
- `Angabe/topology.py`: definiert zwei Clients, einen Linux-Router, den Server und zwei OVS-Switches im Standalone-Modus ohne SDN-Controller. `LinuxRouter.config()` aktiviert IPv4-Forwarding. Fünf `TCLink`-Verbindungen erhalten vorgegebene Interfacenamen und Verzögerungen. Beim Beenden wird Forwarding zurückgesetzt.
- `Angabe/start_lab.py`: erstellt Mininet, vergibt explizite `/24`-Adressen, setzt die Client-Gateways richtig und das Server-Gateway absichtlich falsch. Es druckt Adressen/Routen und prüft zunächst lokale Infrastruktur. Ende-zu-Ende-Fehler sind ausdrücklich erwartete Symptome, keine Startfehler. Danach würde es vier Terminals öffnen und auf ENTER warten. Es startet **keine Mininet-CLI**; in den abschließenden `input()`-Prompt gehören keine Befehle wie `client1 ping ...`. Der Text `ÜB10 forensic baseline` in einer Ausgabe ist nur ein Vorlagen-Tippfehler, kein anderes Blatt.
- `Angabe/tcp_server.py`: öffnet einen IPv4-TCP-Socket, erlaubt Wiederverwendung des lokalen Ports, bindet an alle lokalen IPv4-Adressen auf Port 5000, lauscht und nimmt Verbindungen nacheinander an. Für jede angenommene Verbindung sendet `sendall()` die Begrüßung. Das innere `with conn` schließt danach diese Verbindung; die äußere Schleife hält den Listener offen.
- `Angabe/tcp_client.py`: verwendet optional das erste Kommandozeilenargument als Server-IP, sonst `10.10.2.10`. `create_connection()` verbindet mit fünf Sekunden Timeout auf Port 5000. Ein einziges `recv(4096)` liest höchstens 4096 Bytes; das ist kein allgemeines Nachrichten-Framing. Für diesen Lauf zeigt die tatsächliche Ausgabe die vollständige Begrüßung. `decode(errors="replace")` ersetzt ungültige Textbytes; `end=""` vermeidet einen zusätzlichen Zeilenumbruch.
- `Angabe/capture_client.sh`, `Angabe/capture_router.sh`, `Angabe/capture_server.sh`: jeweils ein kurzer tcpdump-Starter mit unterschiedlichem Standard-Ausgabepfad. Ein erstes Argument überschreibt den Pfad. `-i any` wählt alle Interfaces des jeweiligen Netzwerk-Namespace, `-nn` verhindert Namensauflösung, `-e` verlangt Linklayer-Informationen, `-s 0` volle Pakete und `-w` eine Binärdatei. Unter Linux ist ein `any`-Mitschnitt typischerweise Cooked Capture, nicht der hier verlangte Ethernet-Linktyp des eigenen Parsers. Die Ersatzmessung benutzt deshalb explizite Ethernet-Interfaces und dumpcap, nicht diese Helfer. Originalpfade sind keine Aufforderung, Mitschnitte ungezielt auf dem realen Rechner zu starten.

### Eigene Programme

- `messen.py`: privilegierter, tatsächlich verwendeter Vorher-/Nachher-Messrunner. Baut das Ersatznetz isoliert auf, protokolliert echte Befehle, startet die Originalanwendungen, sichert zwei Phasen mit jeweils fünf Mitschnitten, prüft die Diagnose **vor** der einzigen Reparatur und räumt Prozesse auf.
- `pcap.py`: kleiner strenger Parser nur mit Python-Standardbibliothek. Liest klassisches PCAP mit Ethernet-Linktyp und zerlegt ARP, IPv4, ICMP und TCP. Prüft Grenzen und Prüfsummen. Kein universeller Wireshark-Ersatz: PCAPNG, VLAN und fragmentiertes IPv4 werden nicht unterstützt. Zeitstempel werden beim Lesen übersprungen.
- `auswertung.py`: liest ausschließlich gespeicherte Belege. Prüft den Fehler, Zuordnung von TCP-Paketen auf beiden Routerinterfaces, TTL/MAC-Wechsel, Handshake, Begrüßung und Verbindungsabbau nach der Reparatur. Es gibt JSON aus, ändert aber weder Routen noch Belegdateien.
- `ue9.1/pruefen.py`: zeigt Ausgangszustand, lokale Basistests, fehlgeschlagene Ende-zu-Ende-Versuche und Neighbor-Zustände.
- `ue9.3/pruefen.py`: zeigt die gesamte Paketflussauswertung mit Fehlerbelegen und erfolgreichen TCP-Flows.
- `ue9.4/pruefen.py`: zeigt Paketbelege zusammen mit fehlerhafter Server-Routenentscheidung und Neighbor-Eintrag.
- `ue9.5/pruefen.py`: zeigt Serverzustand vor und nach der Reparatur; dieser Starter repariert selbst nichts.
- `ue9.6/pruefen.py`: zeigt erfolgreiche Ende-zu-Ende-Tests und TCP-Details nach der Reparatur.
- `test_nachweise.py`: offline ausführbare Regressionen für echte Belege, Originalarchivtreue, unabhängiges tcpdump-Decoding, fünf CLIs, absichtlich beschädigte Paketdaten sowie simulierte Fehler vor Netzänderungen. Die Mocktests prüfen Schutzlogik, nicht eine neue Mininet-Ausführung. Der Test zur Zeilendokumentation vergleicht jede nichtleere Quelltextzeile und ihre Nummer, damit fehlende, doppelte oder veraltete Quellen auffallen.

Alle fünf kleinen Starter rufen dieselbe zentrale Auswertung mit einem anderen `--task` auf. Auch bei einer Teilansicht wird zuerst die komplette Analyse ausgeführt. Ein kaputter Nachher-Mitschnitt kann daher auch die Anzeige zu 9.1 abbrechen. Zusätzliche Argumente werden weitergereicht; ein späteres weiteres `--task` könnte die Auswahl überschreiben. Die Starter sind keine fünf unabhängig implementierten Parser.

### Gespeicherte Belege und Dokumentation

- `nachweise/run01/results.json`: Rohprotokoll des Messrunners mit Herkunft, Anfangszustand, Basistests, Vorher-/Nachher-Prozessausgaben und Rückgabecodes, Diagnoseprüfung, repariertem Zustand und Mitschnittzahlen.
- `nachweise/run01/auswertung.json`: gespeichertes Ergebnis der Paket- und Zustandsauswertung. Ein erneuter Aufruf von `auswertung.py` gibt die Analyse aus; er überschreibt diese Datei nicht automatisch.
- `nachweise/run01/befehle.txt`: protokollierte Befehle aus `Lab.run()` samt Standardausgabe, Fehlerausgabe und `RC`. Lang laufende per `spawn()` gestartete Prozesse und dumpcap sind nicht vollständig als Befehle in diesem Log aufgeführt; ihre Aufrufe stehen im Runner. Der lokale Projektpfad wird in Ausgaben als `<ueb09>` dargestellt.
- `nachweise/run01/diagnose-vor-reparatur.txt`: vor dem Route-Replace geschriebene Diagnose mit damaligen Serveradressen, Route und Neighbor-Einträgen. Die Reihenfolge ist zusätzlich in `messen.py` L172–176 nachvollziehbar.
- `vorher-client1.pcap` und `nachher-client1.pcap`: Sicht an `client1-eth0` vor beziehungsweise nach der Reparatur; 10 beziehungsweise 15 Frames.
- `vorher-client2.pcap` und `nachher-client2.pcap`: entsprechende Sicht an `client2-eth0`; 10 beziehungsweise 15 Frames.
- `vorher-router0.pcap` und `nachher-router0.pcap`: Router auf der Clientseite, `router-eth0`; 20 beziehungsweise 30 Frames.
- `vorher-router1.pcap` und `nachher-router1.pcap`: Router auf der Serverseite, `router-eth1`; jeweils 30 Frames.
- `vorher-server.pcap` und `nachher-server.pcap`: Sicht an `server-eth0`; jeweils 30 Frames. Gleiche Framezahl heißt ausdrücklich nicht gleicher Inhalt oder gleiches Ergebnis.
- Zu jedem dieser zehn PCAPs gehört `<dateiname>.pcap.txt`: dumpcap-Status und abschließender Paketzähler, kein textuell dekodierter Paketinhalt. Der Runner vergleicht den Zähler mit tatsächlich geparsten Records.
- `vorher-server-tcpdump.txt` und `nachher-server-tcpdump.txt`: lesbare tcpdump-Dekodierung der gespeicherten Servermitschnitte, hilfreich für MACs, TTL, Flags und Nutzdatenlängen. Das ist keine zusätzliche Messung und kein Wireshark-GUI-Nachweis.
- `erklaerung_blatt09.md`: dieses fachliche Hauptdokument mit Ablauf und Vorführung.
- `zeilenerklaerung.md`: Begründung jeder nichtleeren Zeile der jetzt vorhandenen eigenen Python-Dateien, ohne `Angabe/`. Leerzeilen haben keine Programmauswirkung und sind ausgelassen.

Alle genannten Belegdateien liegen, sofern kein anderer Ordner genannt ist, in `nachweise/run01/`.

## 5. Der tatsächliche Ablauf nach Aufgaben

### Ü9.1 – erst beobachten, dann verändern

Der Runner benötigt Rootrechte und Python ab 3.12 für `os.unshare()`. Noch **vor** Bridges, Links, Routen und sysctl-Aufrufen erzeugt `measure()` einen frischen äußeren Netzwerk-Namespace. Die Netzwerkänderungen betreffen damit das eigene Labor statt den ursprünglichen Netzwerk-Namespace des Rechners. Das ist eine Sicherheitsgrenze, kein optionaler Komfort.

Er legt einen **neuen** Belegordner an. `exist_ok=False` verhindert das Überschreiben eines vorhandenen Laufs. Anschließend entstehen die Bridges, vier Namespace-Halteprozesse, veth-Verbindungen, feste Adressen und die absichtlich falsche Serverroute. Offloading wird auf den veth-Enden abgeschaltet, damit die gespeicherten TCP-Prüfsummen als echte vollständige Prüfsummen ausgewertet werden können. IPv6 wird im isolierten Labor deaktiviert, um den untersuchten IPv4-Verkehr klar abzugrenzen.

`Lab.state()` liest `ip -br addr`, `ip route`, `ip neigh` und `ip route get`. Die anfänglichen Neighbor-Tabellen sind leer. Erst durch Verkehr werden MAC-Zuordnungen gelernt. `STALE` bedeutet ein gealterter, noch vorhandener Eintrag, nicht automatisch ein Verbindungsfehler. `FAILED` bedeutet hier eine erfolglose Neighbor-Auflösung.

Lokale Basistests funktionieren: beide Clients erreichen `10.10.1.1`, der Router erreicht `10.10.2.10`, und der Server erreicht `10.10.2.1`. Das widerspricht dem Fehler nicht: Antworten an Nachbarn im eigenen `/24`-Netz benutzen die direkt angeschlossene Netzroute, nicht die falsche Default-Route.

Der Server wird mit `-u` für ungepufferte Ausgabe gestartet. Erst wenn seine echte Meldung `Listening on 0.0.0.0:5000` gelesen wurde, beginnen die Versuche. Vor der Reparatur verlieren beide Clients alle drei Ping-Pakete und ihre Original-TCP-Clients enden mit Timeout und Rückgabecode 1.

### Ü9.3 – Paketfluss lokalisieren

Pro Phase laufen fünf dumpcap-Prozesse auf den genannten Ethernet-Interfaces. Der Capture-Filter lautet `arp or icmp or tcp port 5000`; es ist also kein beliebiger Gesamtmitschnitt. `-P` fordert klassisches PCAP statt PCAPNG. Die Aufzeichnung läuft zeitbegrenzt und endet regulär, damit Capture-Puffer entleert werden. Der Runner wartet auf das Bereitschaftssignal `File: -`, nicht nur auf eine frühere allgemeine Startmeldung.

Für ein SYN von client1 geschieht fachlich Folgendes:

1. Der Client entscheidet anhand seiner Route: Ziel `10.10.2.10` ist entfernt, nächster Hop ist `10.10.1.1`.
2. Auf dem Client-LAN geht der Ethernet-Frame von `02:00:00:00:01:10` an `02:00:00:00:01:01`. Die IP-Adressen bleiben `10.10.1.10` und `10.10.2.10`.
3. Der Router leitet über `router-eth1` weiter. Auf dem Server-LAN lautet das Ethernet-Paar nun `02:00:00:00:02:01` an `02:00:00:00:02:10`. Die IP-Adressen und der TCP-Inhalt bleiben gleich; die TTL sinkt durch den Router um eins, hier von 64 auf 63.
4. Das SYN kommt am Server an. Für die entfernte Client-IP wählt der Server aber die falsche Default-Route über `10.10.2.254`.
5. Der Server sucht per ARP nach der MAC dieses falschen nächsten Hops. ARP bleibt im Server-LAN; der Router leitet den ARP-Broadcast nicht ins andere Netz weiter. Niemand antwortet für `.254`.
6. Auf dem Serverinterface erscheint deshalb kein SYN-ACK. Die Clients wiederholen SYNs und laufen schließlich in den Timeout.

**Die erste belegte Abweichung liegt auf dem serverseitigen Rückweg, nicht auf dem Hinweg zwischen Client und Router.** Für client2 gilt derselbe Mechanismus. `routed()` ordnet die TCP-Pakete beider Routerinterfaces anhand von IP-Paar, IP-ID und Transportbytes zu. Es bestätigt vor der Reparatur zehn und danach achtzehn zuordenbare TCP-Pakete. Die allgemeine Routerprüfung ist dabei auf TCP begrenzt, nicht auf alle Protokolle.

Es wurden vor der Reparatur auf dem Serverinterface keine ICMP-Fehler vom Typ 3 oder 11 beobachtet. Das ist eine Aussage über diesen Mitschnitt, nicht über alle möglichen Interfaces oder spätere Ereignisse. Insbesondere wird kein erfundenes „Time Exceeded“ als Fehlerbeweis benutzt; die beobachtete TTL 63 ist kein Hinweis auf eine Routingschleife.

### Ü9.4 – Hypothese mit mehreren Belegen prüfen

Die unabhängigen Beobachtungsarten sind **Kernelzustand** und **tatsächlicher Paketverkehr**:

- `ip route get 10.10.1.10` am Server wählt `.254`; `ip neigh` zeigt dazu `FAILED`.
- `vorher-server.pcap` zeigt ankommende SYNs beider Clients, zwölf ARP-Anfragen des Servers nach `.254`, keine passende ARP-Antwort und keine TCP-Rückpakete des Servers.
- Die erfolgreichen lokalen Basistests grenzen zusätzlich einen allgemeinen Link-/Switch-Ausfall ein.

Das Fehlen eines SYN-ACK allein würde noch nicht zwischen Firewall, Serverproblem und Rückwegfehler unterscheiden. Erst mit der konkreten Routenentscheidung und der erfolglosen ARP-Suche wird die Gateway-Hypothese belastbar. Zwei JSON-Ausgaben desselben Paketparsers wären dagegen nicht zwei unabhängige Messungen.

Im Runner geschieht zuerst `lab.state()`, dann `check_fault(out)`, dann das Schreiben von `diagnose-vor-reparatur.txt`. **Erst danach** folgt der Reparaturbefehl. So wird die Diagnose nicht nachträglich aus einem schon reparierten Zustand konstruiert.

### Ü9.5 – kleinste sinnvolle Reparatur

Genau dieser Befehl wurde im Netzwerk-Namespace des Servers ausgeführt:

```sh
ip route replace default via 10.10.2.1 dev server-eth0
```

Es wurde nicht am Python-Socket, am Serverport oder an den Clientadressen gedreht. Der Befehl ersetzt die eine falsche Default-Route durch den tatsächlich vorhandenen Nachbarn. Das Betriebssystem wählt nun für Antworten an beide Clients denselben Router, über den diese erreichbar sind. Die direkt angeschlossene `10.10.2.0/24`-Route bleibt bestehen.

Mögliche, aber hier nicht ausgeführte Alternativen: eine spezifische Route `10.10.1.0/24 via 10.10.2.1` am Server würde das Testnetz erreichbar machen, ließe aber die falsche Default-Route zurück. Eine zusätzliche Routeradresse `.254` würde die fehlerhafte Annahme bedienen, änderte jedoch die Infrastruktur statt den falschen Eintrag zu korrigieren. Eine größere Netzmaske auf den Endgeräten wäre keine saubere Reparatur der gerouteten Topologie: Sie könnte ARP für entfernte Ziele im falschen LAN auslösen.

### Ü9.6 – denselben Versuch wiederholen

Nach der einen Routenänderung startet eine zweite Phase mit denselben fünf Capture-Punkten und denselben beiden Originalclients. Beide Pings empfangen drei Antworten, beide TCP-Clients beenden sich mit Rückgabecode 0 und geben exakt die Originalbegrüßung aus.

Im **`nachher-server.pcap` dieses Laufs**:

- client1 verwendet Quellport 54918: SYN in Frame 7, SYN-ACK in Frame 8, FIN-Pakete in Frames 12 und 13.
- client2 verwendet Quellport 52262: SYN in Frame 22, SYN-ACK in Frame 23, FIN-Pakete in Frames 27 und 28.
- Jeder der beiden TCP-Flows enthält neun Pakete, die Begrüßung hat 28 Bytes, und es gibt kein RST.

Framezahlen und dynamische Clientports gehören nur zu dieser Datei aus `run01`; sie sind keine Konstanten für einen späteren Lauf. Der Parser prüft passende Handshake-Bestätigungen, beide FINs und deren Bestätigung. `stream()` setzt Servernutzdaten anhand der Sequenznummern zusammen, akzeptiert identische Wiederholungen und verwirft Widersprüche oder Lücken. Es handelt sich dennoch um einen gezielten Labortest, nicht um eine vollständige TCP-Zustandsmaschine für beliebige Datenströme.

Auf dem Serverinterface haben ausgehende Antworten zunächst TTL 64; nach dem Router sehen die Clients TTL 63. Die alte Neighbor-Zeile `.254 FAILED` kann nach der Reparatur noch im Cache stehen. Das macht die Reparatur nicht unwirksam: Die aktuelle Routenentscheidung verwendet `.1`, nicht mehr `.254`.

Zum Schluss werden alle eigenen Kindprozesse beendet und abgewartet, offene Capture-Dateien geschlossen und die Befehle geschrieben. Mit dem Ende der Namespace-Halteprozesse werden deren Netzwerk-Namespaces freigegeben, sofern keine weiteren Referenzen bestehen. Unter `sudo` wird der Belegordner dem aufrufenden Benutzer zurückgegeben. Dieser Ressourcenabbau ist keine Reparatur des Netzwerkfehlers, sondern Aufräumen nach dem Versuch.

## 6. Sichere Live-Vorführung ohne erneute Netzänderung

Vom Repository-Hauptverzeichnis aus können diese Aufrufe die bereits vorhandenen Belege neu lesen:

```sh
python3 -B ueb09/ue9.1/pruefen.py
python3 -B ueb09/ue9.3/pruefen.py
python3 -B ueb09/ue9.4/pruefen.py
python3 -B ueb09/ue9.5/pruefen.py
python3 -B ueb09/ue9.6/pruefen.py
python3 -B ueb09/auswertung.py
```

Diese sechs Aufrufe wurden bei der Dokumentation tatsächlich ausgeführt und endeten erfolgreich. Sie brauchen kein Root und starten keine neue Messung. `-B` verhindert neue Python-Bytecode-Dateien. Ein Fehler führt über `require()` zu `ValueError`; die Starter reichen einen fehlerhaften Prozessstatus weiter. Erfolg bedeutet hier „vorhandene Belege bestehen diese Prüfungen“, nicht „das damalige Netz läuft gerade noch“.

Für eine neue Ersatzmessung wären Rootrechte, Python ab 3.12 und die externen Programme `ip`, `nsenter`, `sysctl`, `ethtool`, `ping` und `dumpcap` erforderlich. Dann muss ein **neuer** Unterordner von `nachweise/` gewählt werden. `nachweise/run01/` nicht löschen, überschreiben oder als Ziel wiederverwenden. In dieser Dokumentationsarbeit wurde kein privilegierter Messlauf gestartet.

In der vorgesehenen Kurs-VM ist der originale Start aus dem Ordner `Angabe/` vorgesehen:

```sh
sudo python3 start_lab.py
```

Die folgenden Hostbefehle gehören dann in das jeweilige tatsächlich geöffnete Hostterminal, nicht in den ENTER-Prompt des Starters: `ip -br addr`, `ip route`, `ip neigh`, zunächst Ping zum lokalen Gateway und danach Ping zum Server. Erst beobachten und Mitschnitt sichern, dann diagnostizieren, dann die Serverroute ändern. Dieser VM-Ablauf bleibt hier unbestätigt; auch echte Wireshark-GUI-Screenshots wurden mit diesen Dateien nicht nachgewiesen.

## 7. Welche Zeilen bei Live-Änderungen zusammengehören

Die folgenden Hinweise sind Lern- und Änderungsstellen, **keine** bereits durchgeführten Änderungen. Originale und `run01` bleiben als Referenz unangetastet. Neue Programmvarianten brauchen neue Messungen und passende aktualisierte Zeilenerklärungen.

- **Fehler demonstrieren:** `messen.py` L93–94 setzt beim Aufbau `.254`; L176 repariert auf `.1`. Wer schon L93 auf `.1` ändert, entfernt die beabsichtigte Vorher-Störung. Dann muss der Runner an L171 abbrechen. Nicht die Prüfung entfernen, um einen Erfolg vorzutäuschen.
- **Client- oder Server-IP ändern:** `messen.py` L19 und L89–94 betreffen Adressen, Netze und Gateways. Dazu passen `auswertung.py` L12–13, die MAC-/IP-Erwartungen L23–30 und L43–47 sowie die Zieladressen in `messen.py` L101, L139 und L166. Der Originalclient hat zusätzlich eine feste Standard-Server-IP. Nur eine Konstante zu ändern ergibt kein konsistentes neues Szenario.
- **MACs ändern:** die feste Hostliste in `messen.py` L19 und Routeranschlüsse L89–90 müssen zu den Erwartungen in `auswertung.py` L30 und L43–47 passen. MACs sind die lokalen Ethernet-Endpunkte, nicht die Ende-zu-Ende-IP-Adressen.
- **Mehr oder andere Ping-Versuche:** `messen.py` L105 setzt Anzahl und Wartezeiten. `auswertung.py` L104 erwartet aktuell genau drei Antworten je Client. Eine höhere Anzahl braucht entsprechend längere Capture-Zeit und angepasste Erwartung.
- **Mitschnittdauer oder Filter ändern:** `messen.py` L110 legt Interface, Filter, Snaplen und 24 Sekunden fest; L118 wartet maximal 30 Sekunden auf das Ende. Bei längerer Aufnahme muss auch diese Wartezeit passen. Zu enge Filter können ARP als entscheidenden Fehlerbeleg entfernen. Die Analyse erwartet weiterhin zehn Dateien und die bekannten Namen.
- **Bereitschaft und Zeitlimits:** `messen.py` L22–34 wartet bis zur unveränderten absoluten Frist. Ein leeres `select()`-Ergebnis heißt nur „noch keine Ausgabe“ und muss L30 erneut durchlaufen. L113 wartet auf `File: -`; L169 auf die Originalservermeldung. Das ist robuster als eine blind eingefügte Pause.
- **Serverport oder Begrüßung ändern:** Die Originale verwenden Port 5000 und die genannte Begrüßung. In einer getrennten Variante wären Capture-Filter L110, Listener-Bereitschaft L169, Erfolgskriterium L179 sowie `auswertung.py` L14, L70–71 und L83 anzupassen. Das wäre eine neue Anwendungsversion, nicht die vorliegende unveränderte Originalmessung.
- **Ausgabe auswählen oder Belegordner wechseln:** `auswertung.py` L110–116 bestimmt `--out`, `--task` und den ausgegebenen Abschnitt. Die fünf Starter wählen in ihrer jeweiligen L13 die Aufgabe und reichen weitere Optionen weiter. Beispiel für die vorhandenen Belege: `python3 -B ueb09/ue9.4/pruefen.py --out ueb09/nachweise/run01` vom Repository-Hauptverzeichnis.
- **Sicherheitsgrenzen nicht wegoptimieren:** `messen.py` L159–161 erzwingt Root, äußeren Netzwerk-Namespace und neuen Ordner; L200–201 begrenzt Ausgabeziele auf Unterordner von `nachweise/`. Diese Stellen sind gerade keine Kandidaten, um durch Auskommentieren eine Ausführung zu erzwingen.
- **Parser erweitern:** `pcap.py` L65–69 prüft PCAP-Format und Ethernet-Linktyp; L44 verwirft IPv4-Fragmente. Für PCAPNG, VLAN oder Cooked Capture reicht es nicht, diese Prüfungen zu löschen: Headeraufbau und Transportgrenzen müssten wirklich unterstützt und separat getestet werden.

## 8. Häufige Rückfragen in einfachen Worten

**Warum kommt das SYN an, wenn die Route falsch ist?** Weil die falsche Route auf dem Server liegt. Der Client und der Router können den Hinweg richtig entscheiden, während der Server für die Antwort einen falschen nächsten Hop wählt.

**Warum hilft ein vorhandener ARP-Eintrag für `.1` nicht automatisch?** Zuerst wählt IP-Routing den nächsten Hop, erst danach wird dessen MAC gebraucht. Der Server wählt `.254` und kann nicht einfach eine andere bekannte MAC nehmen.

**Warum sagt der Pingfehler nicht schon alles?** Ein Timeout hat viele mögliche Ursachen. Der Mitschnitt zeigt, wie weit der Versuch gelangt, und die Routen-/Neighbor-Ausgaben erklären den konkreten Fehler.

**Warum kein RST?** Ein RST wäre eine andere beobachtete Reaktion, etwa bei einem nicht bedienten Port mit funktionierendem Rückweg. Hier ist der Server gestartet, und vor der Reparatur fehlt auf seinem Interface überhaupt TCP-Rückverkehr. Nachher gibt es regulären Aufbau, Nutzdaten und FIN-Abbau ohne RST.

**Warum ARP für das Gateway und nicht für die entfernte Client-IP?** Der Client liegt außerhalb des lokalen `/24`-Netzes. Für entfernte Ziele muss der Server nur den lokalen nächsten Hop auf Ethernet erreichen; die IP-Zieladresse bleibt die Client-IP.

**Was wird wirklich an den Paketen geprüft?** Längen, IPv4-/ICMP-/TCP-Prüfsummen, gezielte ARP-Befunde, MAC-/TTL-Wechsel über den Router und die erwarteten TCP-Flows. Der Parser berechnet keine Ethernet-FCS, verwertet keine PCAP-Zeitstempel und ist kein allgemeiner TCP-Analysator. Die ICMP-Nachprüfung zählt hier die drei Echo-Replies je Client; sie implementiert keine vollständige Request/Reply-Zuordnung über alle ICMP-Felder.

**Was ist noch offen?** Der erfolgreiche Original-Mininet-/OVS-/xterm-Lauf in der Kursumgebung und gegebenenfalls dort verlangte GUI-Belege. Die erfolgreiche Namespace-Ersatzmessung darf diesen offenen Punkt nicht verdecken.
