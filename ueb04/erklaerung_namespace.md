# Zusatztest – verify_namespaces.py Zeile für Zeile

Quelltext: [verify_namespaces.py](verify_namespaces.py). Das ist ein **echter Linux-Netzwerk-Integrationstest**, weder Mininet noch eine Simulation des TCP/IP-Stacks. Die Tabelle erläutert jede nichtleere Quellzeile einzeln, auch Kommentare, Docstring-Text und Fortsetzungen. Nummern sind die Nummern in der Python-Datei. [Zentraler Lernweg und Dateikatalog](erklaerung_blatt04.md).

## Idee, Ablauf und sichere Einordnung

Ein äußerer, frisch erzeugter Netzwerk-Namespace enthält zuerst eine Linux-Bridge `s1` und zwei weitere Netzwerk-Namespaces als h1/h2. Zwischen ihnen läuft der echte UDP-Code. Anschließend entstehen client/router/server mit zwei IPv4-Netzen, Routen und netem-Warteschlangen; dort werden Ping und der echte TCP-Code geprüft. `dumpcap` zeichnet nur den gefilterten eigenen Verkehr auf. Python-Prozesse benutzen den echten Linux-Netzwerkstack.

Reihenfolge: `main()` → Voraussetzungen/Ausgabeordner → `Sandbox.standard()` → `Sandbox.routed()` → `results.json` → immer `Sandbox.close()`. Der Runner erzeugt PCAPs, Protokolle und Netzwerkansichten, **nicht** die beiden Analyse-JSONs oder Wireshark-Screenshots. Diese entstehen separat durch [analyse_pcap.py](ue4.4/analyse_pcap.py) bzw. echtes Öffnen in Wireshark. [Vorhandener Gesamtbefund](nachweise/run01/results.json).

Der vorgesehene Start aus `ueb04` ist `sudo unshare --net python3 -B verify_namespaces.py --output nachweise/run02`, falls `run02` noch nicht existiert. Das ist eine Anleitung; vorhandene Messwerte stehen unter `nachweise/run01/`. Zusätzlich erzeugt das Programm vor jeder Netzänderung **selbst** mit `os.unshare(os.CLONE_NEWNET)` einen frischen äußeren Netzwerk-Namespace. Damit ist selbst bei einem versehentlichen direkten sudo-Aufruf die Isolation erzwungen; scheitert unshare, wird abgebrochen. Eine leere IPv4-Routingtabelle allein wäre kein Frischenachweis und wird nur noch zusätzlich geprüft. Dateisystem und UTS-Namespace werden nicht isoliert.

Benötigt werden ausreichende Rechte und die tatsächlich verwendeten Linux-Befehle wie ip, unshare, nsenter, tc, sysctl, ping und dumpcap. Der Runner installiert nichts. Die Kindserver verwenden den festgelegten System-Python, nicht automatisch denselben Interpreter wie der Runner. Berechtigungs- oder Toolfehler sollen sichtbar bleiben; keine Schutzmechanismen umgehen.

### Typische Änderungen für die Vorführung

- Zuerst nur einen **neuen** `--output`-Ordner wählen, nie vorhandene Nachweise überschreiben.
- UDP-Nachrichten stehen in Zeile 138, TCP-Nachrichten in Zeile 174. Beim Ändern neue PCAPs erzeugen und die Sollfolgen des Analyseprogramms bewusst mit ändern. Ergebnisse eines alten Captures bleiben Ergebnisse des alten Laufs.
- Andere Adressen erfordern Linkadressen, Gateways, Server-/Clientoptionen, Capturefilter und Analyse-Sollwerte gemeinsam anzupassen. Das ist mehr als eine Änderung von `--host`.
- `20ms` und `0%` in Zeile 154 beeinflussen echte ausgehende Warteschlangen. Ein Paket überquert auf einem Hinweg zwei solche verzögerten Ausgänge; Roundtrip ist nicht einfach gleich 20 ms. Zeitmessungen sind keine garantiert konstanten Werte.
- Capture dauert fünf Sekunden. Mehr Nachrichten oder mehr Delay können die Aufzeichnung über dieses Fenster hinausschieben; dann Aufnahmezeit und Prozesszeitgrenzen abgestimmt erhöhen, statt fehlende Pakete zu erfinden.
- Bereinigung beendet Kindprozesse. Die Bridge im äußeren Namespace wird nicht ausdrücklich mit ip gelöscht; sie verschwindet mit dem Ende dieses eigens erzeugten äußeren Namespace. Bei Fehlern bleibt ein teilweise gefüllter Ausgabeordner erhalten. Das ist **kein** vollständiger erfolgreicher Lauf ohne results.json und passende Einzelnachweise.

## verify_namespaces.py

| Zeile | Was geschieht und warum? |
|---:|---|
| 1 | Herkunftskommentar nennt KI-Werkzeug, Modell und Datum; keine Laufzeitwirkung. |
| 2 | Kommentar beschreibt UDP/TCP und Routing in wirklichen isolierten Linux-Netzwerk-Namespaces als Auftrag. |
| 3 | Kommentar fordert eigene Captures und grenzt die Prüfung ausdrücklich von einem Mininet-Nachweis ab. |
| 4 | Beginnt die Modulbeschreibung mit der Einschränkung: Zusatztest, kein Ersatz für Mininet/OVS und das Arbeiten in der bereitgestellten VM. |
| 6 | Docstring-Zeile zeigt den vorgesehenen Start mit äußerem unshare-Namespace und Ausgabeordner; als Beschreibung wird der Befehl nicht ausgeführt. |
| 7 | Docstring nennt das Isolationsziel: keine Installation und keine Netzänderung am aufrufenden Host. Das gilt für den vorgesehenen unshare-Aufruf, nicht allein durch diesen Text. |
| 8 | Schließt die mehrzeilige Modulbeschreibung; sie wird später als CLI-Hilfe verwendet. |
| 10 | Lädt argparse für den verpflichtenden Ausgabeordner und verständliche CLI-Fehler. |
| 11 | Lädt json für den abschließenden strukturierten Gesamtbefund. |
| 12 | Lädt os für effektive Benutzer-ID und das Lesen echter Namespace-Symlinks in procfs. |
| 13 | Lädt Path, um Skriptort, Ausgabeordner und Belegdateien zu behandeln. |
| 14 | Lädt selectors für begrenztes Warten auf tatsächliche Bereitschaftsausgabe. |
| 15 | Importiert signal; der aktuelle Code benutzt dieses Modul danach nicht. Der Import selbst sendet kein Signal. |
| 16 | Lädt subprocess für echte Linux-Befehle, Server-/Clientprozesse und dumpcap. |
| 17 | Lädt time für monotone Zeitgrenzen und kurze Warteintervalle beim Namespace-Start. |
| 19 | Bestimmt den aufgelösten Ordner der Runnerdatei; Programm- und Nachweispfade werden daran ausgerichtet, nicht am Shell-Arbeitsverzeichnis. |
| 20 | Legt den System-Python für die Anwendungskinder fest; das kann ein anderer Interpreter als der des Runners sein. |
| 23 | Definiert einen Helfer für kurz laufende Befehle mit Argumentliste und optionalen Zusatzoptionen. |
| 24 | Führt den Befehl ohne Shell aus, verlangt Exitcode 0, erfasst stdout/stderr als Text, begrenzt auf 20 Sekunden und liefert nur stdout zurück. Fehler werden als Ausnahme sichtbar. |
| 27 | Definiert das Warten auf eine erwartete Teilzeichenfolge in der stdout-Ausgabe eines Prozesses bzw. Ausgabe-Proxys. |
| 28 | Beginnt einen Puffer für alle bis zur Bereitschaft gelesenen Zeilen, damit sie später im Protokoll erhalten bleiben. |
| 29 | Öffnet einen Selector und schließt ihn beim Verlassen automatisch. |
| 30 | Registriert den Ausgabekanal für Lesebereitschaft; der Aufrufer muss ihn als Pipe bereitstellen. |
| 31 | Setzt eine Zehn-Sekunden-Frist mit monotoner Zeit, unabhängig von einer verstellten Systemuhr. |
| 32 | Wartet nur weiter, solange die Frist noch nicht erreicht ist. |
| 33 | Wartet höchstens die verbleibende Zeit auf Lesbarkeit; max verhindert einen negativen Timeout durch verstrichene Zeit. |
| 34 | Verlässt die Schleife, wenn bis dahin kein neues Leseereignis kommt. |
| 35 | Liest eine ganze Ausgabezeile; die verwendeten Server und dumpcap geben ihre Bereitschaft zeilenweise aus. Das ist kein allgemeiner nichtblockierender Byteparser. |
| 36 | Erkennt EOF am leeren Rückgabewert; ohne weitere Ausgabe kann keine Bereitschaft mehr kommen. |
| 37 | Bricht beim geschlossenen Kanal die Warteschleife ab und führt zur Fehlerdiagnose. |
| 38 | Behält die gerade gelesene Zeile einschließlich ihres Zeilenumbruchs im Puffer. |
| 39 | Prüft, ob die erwartete Teilzeichenfolge enthalten ist; es muss nicht die gesamte Zeile exakt übereinstimmen. |
| 40 | Verbindet alle gelesenen Zeilen und liefert sie zurück; wählt bytes oder Text passend zum erwarteten Marker, damit dumpcap und Server beide funktionieren. |
| 41 | Meldet nach EOF oder Fristablauf einen RuntimeError mit erwartetem Marker und tatsächlich gelesenen Zeilen. |
| 44 | Definiert Sandbox als Verwaltung eigener Namespace-, Server- und Captureprozesse samt Ergebnisdateien. |
| 45 | Definiert den Konstruktor, der einen schon bestimmten Ausgabeordner übernimmt. |
| 46 | Merkt diesen Ordner für alle späteren Belegdateien. |
| 47 | Beginnt die Liste aller eigenen Kindprozesse, damit auch bei Fehlern aufgeräumt werden kann. |
| 48 | Beginnt die Liste der Captureprozesse mit ihren Datei-Handles und Dateinamen. |
| 49 | Beginnt eine Liste von Namespacehalter-PIDs; sie wird später befüllt, aber nicht für die eigentliche Bereinigung benutzt. Diese läuft über children. |
| 50 | Beginnt den Befund mit ehrlicher Herkunft und noch leerer Checkliste; der Text allein beweist noch keinen ausgeführten Test. |
| 52 | Definiert das Erzeugen eines neuen logischen Hosts als Prozess in einem eigenen Netzwerk-Namespace. |
| 53 | Liest die aktuelle net-Namespace-ID als Vergleichswert, um den erfolgreichen Wechsel des Kindes erkennen zu können. |
| 54 | Startet unshare --net mit sleep als Namespacehalter für 180 Sekunden; nur Netzwerk-, nicht UTS-/Dateisystem-/PID-Namespace wird neu erzeugt. |
| 55 | Registriert den Prozess sofort zur späteren Beendigung, auch wenn der Start nachher scheitert. |
| 56 | Setzt eine dreisekündige Grenze für die anfängliche Namespace-Umschaltung. |
| 57 | Liest die net-Namespace-ID des Kindes so lange erneut, wie sie noch der äußeren ID entspricht. Ein sehr früh verschwundener procfs-Eintrag kann dabei auch OSError auslösen. |
| 58 | Bricht die Wartephase bei Zeitüberschreitung oder schon beendetem Kind ab. |
| 59 | Meldet den fehlenden neuen Netzwerk-Namespace als echten Testfehler. |
| 60 | Wartet zwischen den Abfragen kurz, damit die Startprüfung nicht die CPU mit ständigem Abfragen auslastet. |
| 61 | Merkt die PID des Namespacehalters; nsenter verwendet später diese PID als Ziel. |
| 62 | Aktiviert das Loopbackinterface im neuen Host-Namespace, das anfangs noch heruntergefahren sein kann. |
| 63 | Liefert die PID als Hostkennung zurück; sie ist kein Hostname und keine IP-Adresse. |
| 65 | Kennzeichnet prefix als statische Methode; sie braucht keine Sandbox-Instanzdaten. |
| 66 | Definiert das Erzeugen eines Befehlspräfixes für den Namespace einer Host-PID. |
| 67 | Baut nsenter -t PID -n; -n betritt nur den Netzwerk-Namespace des Zielprozesses. Die Liste wird ohne Shell verwendet. |
| 69 | Definiert cmd für einen kurz laufenden Befehl im gewünschten Hostnetz; *argv nimmt einzelne Argumente auf. |
| 70 | Hängt die Befehlsargumente an das nsenter-Präfix und verwendet run mit Fehler- und Zeitkontrolle. |
| 72 | Definiert einen veth-Link mit je Host-PID, Interfacename und optionaler IP-Adresse pro Seite. |
| 73 | Erzeugt ein verbundenes Paar virtueller Ethernetinterfaces zunächst im äußeren isolierten Namespace. |
| 74 | Verschiebt das erste Interface in den Netzwerk-Namespace von a; der Name bleibt erhalten. |
| 75 | Prüft, ob auch die zweite Seite in einen eigenen Host-Namespace verschoben werden soll. None bedeutet hier: im äußeren Namespace lassen. |
| 76 | Verschiebt die zweite veth-Seite nach b, wenn b angegeben ist. |
| 77 | Durchläuft beide Seiten mit zugehörigem Host, Interface und Adresse, um gleiche Konfigurationsschritte wiederzuverwenden. |
| 78 | Erkennt die Seite, die bewusst im äußeren Namespace verblieben ist. |
| 79 | Überspringt deren IP-/UP-Konfiguration; im Bridgefall erledigt standard später das Einschalten ohne eigene IP-Adresse. |
| 80 | Fügt im jeweiligen Host die IPv4-Adresse samt Präfix dem betreffenden Interface hinzu. |
| 81 | Aktiviert das Interface, damit der gerade konfigurierte Link Pakete übertragen kann. |
| 83 | Definiert das Starten eines gefilterten Captures auf genau einem Interface eines Host-Namespace. |
| 84 | Öffnet die PCAP-Datei exklusiv neu und binär; bestehende Dateien werden nicht still ersetzt. |
| 85 | Startet dumpcap im Hostnetz, wählt das konkrete Interface, deaktiviert Promiscuous Mode mit -p und verlangt klassisches PCAP statt pcapng. |
| 86 | Setzt Capturefilter, automatisches Ende nach fünf Sekunden und binäre Ausgabe nach stdout; stdout schreibt direkt in die Datei, stderr bleibt als Statuspipe lesbar. |
| 87 | Belässt Ausgaben als Bytes und die Pipe ungepuffert auf Python-Seite; PCAP darf nicht als Text dekodiert werden. |
| 88 | Registriert dumpcap als eigenes Kind für die Fehlerbereinigung. |
| 89 | Merkt Prozess, geöffnetes PCAP-Handle und Namen für spätere Schließung und Statuslogdatei. |
| 90 | Kommentar erklärt die getrennten Kanäle: Status auf stderr, eigentliche Paketbytes auf stdout. |
| 91 | Baut ein kleines Proxyobjekt, dessen stdout auf dumpcaps stderr zeigt; so lässt sich wait_line unverändert verwenden. |
| 92 | Wartet auf dumpcaps binären File:-Marker, bevor Clients senden dürfen; die Bereitschaftszeilen werden hier nicht separat gespeichert. |
| 93 | Liefert das laufende Capture-Prozessobjekt zurück, um sein Ende später abzuwarten. |
| 95 | Definiert das geordnete Beenden der Aufnahme durch Abwarten ihres eigenen Timers, nicht durch sofortiges Signal. |
| 96 | Kommentar warnt vor zu frühem SIGINT: libpcap könnte noch erfasste Pakete puffern. |
| 97 | Kommentar erklärt, warum der zeitlich begrenzte Capture erst vollständig auslaufen soll. |
| 98 | Wartet bis zu zehn Sekunden auf dumpcap-Ende und liest dessen verbleibenden Fehler-/Statuskanal; stdout geht bereits in die Datei. |
| 99 | Prüft dumpcaps tatsächlichen Rückgabewert statt bloß das Vorhandensein einer PCAP-Datei. |
| 100 | Meldet bei Fehler den dekodierten dumpcap-Text; ungültige Textbytes werden nur in der Diagnose ersetzt, nicht im PCAP. |
| 101 | Sucht unter den registrierten Captures den zu diesem Prozess gehörenden Dateihalter. |
| 102 | Vergleicht die Prozessobjekte auf Identität, nicht lediglich Dateinamen oder gleiche PIDs als Text. |
| 103 | Schließt nach Prozessende das PCAP-Handle, damit die Aufnahme nicht mehr offen gehalten wird. |
| 104 | Speichert den noch aus communicate stammenden Status in einer .pcap.txt-Datei; die früher für READY gelesenen Zeilen sind darin nicht zwingend enthalten. |
| 105 | Beendet die Funktion nach dem passenden Capture; weitere Aufnahmen werden hier nicht verändert. |
| 107 | Definiert das Starten eines eigenen Anwendungsservers im angegebenen Hostnetz. |
| 108 | Baut nsenter plus System-Python, -B, skriptrelativen Programmpfad und zusätzliche CLI-Argumente; -B vermeidet Bytecode-Dateien. |
| 109 | Erfasst stdout und leitet stderr in denselben Textkanal um; im Serverlog bleiben dadurch auch Fehler sichtbar. |
| 110 | Registriert den neuen Server sofort als Kind zur späteren Bereinigung. |
| 111 | Wartet auf die tatsächliche READY-Ausgabe des Servers statt nach fester Zeit blind weiterzumachen. |
| 112 | Gibt Serverprozess und die bereits gelesenen Startzeilen zurück, damit das spätere Log vollständig zusammengesetzt wird. |
| 114 | Definiert das Einsammeln und Prüfen eines Servers, der sich nach seiner geplanten Arbeitsmenge selbst beenden soll. |
| 115 | Wartet maximal 15 Sekunden und sammelt die restliche kombinierte Ausgabe; der zweite Rückgabewert ist wegen stderr-Umleitung ungenutzt. |
| 116 | Schreibt bereits gelesene Bereitschaft und restliche Ausgabe zusammen ins angegebene Serverprotokoll. |
| 117 | Prüft den echten Exitcode nach dem Serverende; reine Logexistenz wäre kein Erfolgsbeweis. |
| 118 | Meldet bei Serverfehler die vollständige erfasste Ausgabe als Ausnahme. |
| 120 | Definiert das Standardtopologie-Szenario mit zwei Endpunkten und Linux-Bridge für UDP. |
| 121 | Erzeugt zwei getrennte Host-Netzwerk-Namespaces und merkt ihre Halter-PIDs als h1 und h2. |
| 122 | Erzeugt eine Linux-Bridge namens s1 im äußeren isolierten Namespace. Das ist ausdrücklich kein Open vSwitch. |
| 123 | Aktiviert diese Bridge, damit angeschlossene veth-Ports Ethernetframes weiterleiten können. |
| 124 | Beginnt die Endpunktbeschreibung mit h1, Interface h1-eth0, 10.0.0.1/24 und dem Bridge-seitigen Peer s1-h1. |
| 125 | Ergänzt h2 mit 10.0.0.2/24 und dessen Peer s1-h2; beide liegen im gleichen IPv4-Subnetz. |
| 126 | Erzeugt den veth-Link und verschiebt nur die Hostseite; None lässt die Peer-Seite ohne IP im äußeren Namespace. |
| 127 | Ordnet den dort verbliebenen Peer als Port der Bridge s1 zu. |
| 128 | Aktiviert diesen Bridgeport; die Hostseite wurde bereits durch link eingeschaltet. |
| 129 | Durchläuft die beiden Hosts mit ihren lesbaren Dateinamen h1 und h2. |
| 130 | Liest je Host echte Interfaceadressen und echte IPv4-Routen und verbindet beide Ausgaben als Text. |
| 131 | Speichert diese Netzwerkansicht in h1-network.txt bzw. h2-network.txt. |
| 132 | Vergleicht die echten net-Namespace-IDs beider Halterprozesse und verlangt unterschiedliche Werte als Isolationsprüfung. |
| 133 | Verlangt gleiche UTS-Namespace-IDs; unterschiedliche Netzwerkumgebungen bedeuten hier gerade keine getrennten Hostnamen-Namensräume. |
| 134 | Hängt den erst nach den Assertions erreichten Namespacebefund an die Checkliste an. Die IDs selbst werden hier nicht ins JSON übernommen. |
| 135 | Startet den eigenen UDP-Server auf h2 für genau drei Datagramme mit zehn Sekunden Empfangstimeout; Standardadresse/Port stammen aus server.py. |
| 136 | Startet die UDP-Aufnahme auf h1-eth0, beschränkt auf h1→h2 und Zielport 5000; keine breite Aufnahme fremden Verkehrs. |
| 137 | Beginnt eine Liste für die tatsächlichen Ausgaben der drei Clientaufrufe. |
| 138 | Legt die drei UDP-Sendetexte fest: Normaltext, geänderte Nachricht und UTF-8 mit Emoji. |
| 139 | Startet für jeden Text den echten UDP-Client in h1 mit --message und sammelt dessen stdout; Ziel bleibt dessen Standard 10.0.0.2:5000. |
| 140 | Wartet auf das reguläre Ende nach drei Empfängen und speichert den UDP-Serverlog. |
| 141 | Wartet auf den Capture-Timer und prüft/schließt die UDP-Aufnahme. |
| 142 | Speichert die drei Clientausgaben in ihrer Aufrufreihenfolge in udp-clients.txt. |
| 143 | Notiert das erfolgreich erreichte UDP-Szenario. Die exakten Paketbytes werden zusätzlich erst vom separaten Analyseprogramm geprüft. |
| 145 | Definiert das geroutete Szenario mit zwei Netzen für Ping und TCP. |
| 146 | Erzeugt drei neue Host-Netzwerk-Namespaces für Client, Router und Server; die bisherigen Kinder bleiben bis zur Bereinigung bestehen. |
| 147 | Verbindet Client 10.0.1.2/24 über veth mit dem linken Routerinterface 10.0.1.1/24. |
| 148 | Verbindet das rechte Routerinterface 10.0.2.1/24 mit dem Server 10.0.2.2/24; der Router verbindet dadurch zwei verschiedene Netze. |
| 149 | Trägt beim Client eine Default Route über das im eigenen Netz erreichbare Gateway 10.0.1.1 ein. |
| 150 | Trägt beim Server die Rückrichtung als Default Route über 10.0.2.1 ein; Antworten benötigen ebenfalls eine Route. |
| 151 | Aktiviert im Router-Namespace IPv4-Weiterleitung, damit Pakete zwischen seinen Interfaces passieren können. |
| 152 | Beginnt die Liste zu verzögernder ausgehender Interfaces mit Client und linker Routerseite. |
| 153 | Ergänzt rechte Routerseite und Server; damit werden beide Richtungen beider Links behandelt. |
| 154 | Fügt je Interface eine echte netem-qdisc mit 20 ms Delay und 0 Prozent künstlichem Verlust hinzu. Das verändert die Testnetze, nicht bloß eine Sollwertvariable. |
| 155 | Durchläuft Client, Router und Server, um deren tatsächlichen Netzwerkzustand zu sichern. |
| 156 | Liest Interfaceadressen und Routingtabelle des jeweiligen Namespace. |
| 157 | Ergänzt den lokalen Route-Lookup zum Serverziel 10.0.2.2; ip route get sendet dafür keine Probe-Pakete. |
| 158 | Ergänzt entsprechend den Route-Lookup zum Clientziel 10.0.1.2 für die Rückrichtung. |
| 159 | Ergänzt die wirklich vorhandenen qdiscs, damit Delaykonfiguration nicht nur behauptet wird. |
| 160 | Speichert je Knoten die zusammengestellte Ansicht in client-/router-/server-network.txt. |
| 161 | Sendet vom Client vier echte Echo-Requests zum Server mit zwei Sekunden Antwortwartezeit je ping-Option -W. |
| 162 | Verlangt die Textmeldung für vier empfangene Antworten; diese Prüfung setzt englische ping-Ausgabe voraus. |
| 163 | Speichert den echten Pingtext mit gemessenen Zeiten in ping.txt. |
| 164 | Kommentar begründet die folgende Negativprobe: gleiche Routen, aber keine Weiterleitung sollen nicht genügen. |
| 165 | Deaktiviert IPv4-Forwarding nur im Router-Namespace; Endpunktrouten und Links bleiben unverändert. |
| 166 | Startet einen einzelnen echten Client-Ping mit kurzer Antwortwartezeit; verwendet absichtlich nicht run(check=True), weil ein Fehler erwartet ist. |
| 167 | Erfasst die Ausgabe als Text und begrenzt den gesamten negativen Pingprozess auf fünf Sekunden. |
| 168 | Verlangt einen von null verschiedenen Exitcode als Gegenprobe; ein erfolgreicher Ping ohne Forwarding wäre unerwartet. |
| 169 | Speichert dessen tatsächliches stdout in ping-forwarding-off.txt; stderr wird bei diesem Schritt nicht mitgespeichert. |
| 170 | Aktiviert Router-Forwarding wieder, damit der folgende TCP-Test nicht absichtlich am Router scheitert. |
| 171 | Startet eine TCP-Aufnahme auf dem Clientinterface, beschränkt auf die beiden Testadressen und Port 5000 in beiden Richtungen. |
| 172 | Startet den eigenen TCP-Server im Servernetz für zwei Verbindungen mit 15 Sekunden Sockettimeout; wartet intern auf READY. |
| 173 | Beginnt die Liste der tatsächlichen TCP-Clientausgaben. |
| 174 | Beschreibt zwei Clientläufe: zuerst ein Text in einer Verbindung, dann drei Texte einschließlich UTF-8 und leerer Nachricht in einer zweiten. |
| 175 | Ruft je Lauf den echten TCP-Client im Clientnetz auf; *messages macht aus dem Tupel einzelne CLI-Nachrichtenargumente derselben Verbindung. |
| 176 | Wartet auf das Serverende nach zwei Verbindungen und speichert dessen Bereitschaft und Empfangsausgaben. |
| 177 | Wartet auf das Ende der TCP-Aufnahme und sichert deren Abschlussstatus. |
| 178 | Speichert die zusammengefügten Client-REPLY-Ausgaben in tcp-clients.txt; der Client prüft jedes Echo selbst. |
| 179 | Ergänzt die Checkliste um positives Routing und die negative Forwardingprobe, die vorher tatsächlich durchgelaufen sind. |
| 180 | Ergänzt das TCP-Szenario mit Einzel- und persistenten Nachrichten und schließt die Checklisten-Erweiterung. |
| 182 | Definiert die Bereinigung eigener Kindprozesse und Capture-Dateihalter; sie wird aus main auch bei Fehlern aufgerufen. |
| 183 | Durchläuft Kinder in umgekehrter Startreihenfolge, damit zuletzt gestartete Anwendungen zuerst beendet werden. |
| 184 | Prüft, ob der jeweilige Prozess noch lebt; ein schon beendeter braucht kein Beendigungssignal. |
| 185 | Fordert den lebenden Prozess mit terminate zur Beendigung auf; unter Linux ist das regulär SIGTERM. |
| 186 | Beginnt den Bereich, der ein nicht rechtzeitig beendetes Kind behandelt. |
| 187 | Wartet nach terminate höchstens drei Sekunden auf dessen Ende und räumt den Prozessstatus ab. |
| 188 | Fängt genau den Fall ab, dass dieses begrenzte Warten noch nicht genügt hat. |
| 189 | Beendet dann das weiterhin hängende eigene Kind zwangsweise mit kill; das ist Notfallbereinigung, nicht normaler TCP-Abbau. |
| 190 | Wartet erneut begrenzt auf das wirkliche Ende, damit kein bloß gesendetes Signal als fertige Bereinigung gilt. |
| 191 | Prüft, ob für dieses Kind eine stdout-Pipe vorhanden ist. Bei direkter Dateiumleitung ist process.stdout normalerweise None. |
| 192 | Schließt eine vorhandene stdout-Pipe auf der Elternseite. |
| 193 | Prüft entsprechend auf eine eigene stderr-Pipe; beim zusammengelegten Serverkanal gibt es keine separate. |
| 194 | Schließt diese stderr-Pipe, sofern vorhanden. |
| 195 | Durchläuft alle Capture-Einträge; Prozess und Name werden zum Schließen der Handles nicht mehr benötigt. |
| 196 | Schließt jedes PCAP-Handle, auch wenn ein früherer Fehler stop_capture verhindert hat; erneutes close ist erlaubt. |
| 199 | Definiert main als CLI-Einstieg und übergeordnete Reihenfolge der Szenarien. |
| 200 | Erstellt den Optionsparser mit der mehrzeiligen Modulbeschreibung. |
| 201 | Verlangt --output ausdrücklich, damit jeder Lauf einen bewusst gewählten Nachweisordner erhält. |
| 202 | Liest die tatsächlich übergebenen Optionen; fehlendes --output führt schon hier zu CLI-Status 2. |
| 203 | Prüft die effektive Benutzer-ID; der aktuelle Runner verlangt root für die privilegierten Namespace-/Netzoperationen. |
| 204 | Beendet ohne diese Rechte mit Hinweis auf den vorgesehenen sudo-unshare-Start. |
| 205 | Erzeugt im aktuellen Prozess zwingend einen frischen Netzwerk-Namespace, bevor Bridge, veth oder Routen angelegt werden; fehlende Rechte führen zum Abbruch. |
| 206 | Prüft zusätzlich, dass der neue Namespace keine IPv4-Routen hat. Die eigentliche Isolationsgarantie kommt aus dem unmittelbar vorherigen unshare, nicht aus dieser Assertion. |
| 207 | Verknüpft BASE mit --output; relative Angaben landen beim Runner. Ein absoluter zweiter Pfad würde BASE zunächst ersetzen und wird anschließend geprüft. |
| 208 | Löst den Zielpfad auf und verlangt, dass er innerhalb des Runnerverzeichnisses liegt; wirkt auch gegen vorhandene herausführende Symlinks. Kein allgemeiner Schutz gegen gleichzeitige Pfadmanipulation. |
| 209 | Meldet einen außerhalb liegenden Ausgabepfad als CLI-Fehler, statt dorthin zu schreiben. |
| 210 | Erzeugt den Ordner samt nötigen Elternordnern, verlangt aber einen noch nicht vorhandenen Zielordner. run01 kann so nicht erneut überschrieben werden. |
| 211 | Erstellt die Sandbox-Verwaltung für den neuen Ordner; noch keine Hostnetze durch den Konstruktor. |
| 212 | Beginnt den try/finally-Bereich, der auch bei Fehlern in einem Szenario die Kinder bereinigt. |
| 213 | Führt zuerst das h1/h2-UDP-Szenario mit Linux-Bridge vollständig aus. |
| 214 | Führt danach Router-, Ping-, Negativ- und TCP-Szenario aus; bei vorherigem Fehler wird diese Zeile nicht erreicht. |
| 215 | Schreibt erst nach beiden erfolgreichen Szenarien den Gesamtbefund als eingerücktes Unicode-JSON mit Abschlusszeile in results.json. |
| 216 | Gibt denselben Gesamtbefund auf stdout aus; die Paketanalysen werden davon getrennt durchgeführt. |
| 217 | Beginnt die garantierte Bereinigung nach Erfolg oder Ausnahme. Auch ein positives JSON ersetzt diese Ressourcenpflege nicht. |
| 218 | Beendet eigene Kinder und schließt Pipes/PCAP-Handles. Die äußere Bridge verschwindet erst mit dem äußeren Namespace, nicht durch einen ausdrücklichen Löschbefehl hier. |
| 221 | Startet main nur bei direkter Ausführung der Datei; ein Import erzeugt keine Testnetze. |
| 222 | Ruft den CLI-Einstieg auf; bei unbehandelten Test-/Befehlsfehlern bleibt die Ausnahme sichtbar und der Lauf ist nicht vollständig erfolgreich. |

## Tatsächliche Nachweise und verbleibende Grenzen

[results.json](nachweise/run01/results.json) nennt getrennte net-Namespaces bei gemeinsamem UTS, drei echte UDP-Datagramme, vier erfolgreiche Pingantworten, fehlgeschlagenen Ping bei ausgeschaltetem Forwarding und die TCP-Echotests. Die zugehörigen Netzwerkansichten, Logs, PCAPs, Byteanalysen und GUI-Screenshots sind im [zentralen Katalog](erklaerung_blatt04.md#nachweiskatalog) einzeln verlinkt. Assertions werden bei `python -O` deaktiviert; diesen Runner und den Analyseprüfer deshalb nicht optimiert starten.

**Nicht durchgeführt:** Mininet, Open vSwitch und xterm-Laborläufe. **Echte Zusatztests:** Linux-Bridge, Netzwerk-Namespaces, veth-Routing/netem, aufgezeichneter eigener UDP-/TCP-Verkehr, separate Python-PCAP-Prüfung und echtes Öffnen in der Wireshark-GUI. Ein Screenshot allein beweist weder den Runnercode noch einen Mininetlauf; er ergänzt die zugehörigen Rohdaten. TShark konnte die Repo-PCAPs wegen Dateizugriffsgrenzen nicht öffnen. Es werden dafür weder Ergebnisse erfunden noch Sicherheitsregeln abgeschaltet.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29. Tatsächliche Anfrage: den unveränderten echten Namespace-Runner einschließlich aller Testschritte vollständig zeilenweise in einfacher Sprache erklären und vorhandene Messbelege von weiterhin fehlenden Mininet-/OVS-/xterm-Läufen trennen. Nur Dokumentation, keine Änderung des Programms.
