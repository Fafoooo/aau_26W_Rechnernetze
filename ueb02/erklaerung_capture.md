# Erklärung jeder eigenen Python-Zeile: Ü2.10

**KI-Kennzeichnung:** Hermes Agent, Modell OpenAI gpt-6.1-sol, 19.10.2026. Anfrage (sinngemäß): „Ü2.10 vollständig praktisch durchführen; reproduzierbares capture_demo.py für ausschließlich eigene harmlose Loopback-HTTP-Kommunikation mit echten Paketdaten, Tests und Protokoll erstellen und jede eigene Codezeile erklären.“

Die Zeilennummern beziehen sich auf `ue2.10/capture_demo.py` und `ue2.10/test_capture.py`. Auch Kommentare, Leerzeilen und Fortsetzungszeilen werden genannt. Es gibt keine versteckte Netzwerkbibliothek: Die Demo benutzt Python-Standardbibliothek und den installierten Wireshark-Capture-Helfer **dumpcap**. Der Testparser liest die tatsächlich erzeugte Binärdatei selbst.

## Grundidee und Grenzen

Ein **Socket** ist ein Betriebssystem-Endpunkt für Kommunikation. Hier sind beide Endpunkte ausschließlich IPv4-Loopback `127.0.0.1`. TCP sorgt für geordneten zuverlässigen Bytestrom; die Demo legt darauf eine kleine gültige HTTP/1.1-Anfrage und -Antwort. `\r\n` trennt HTTP-Zeilen, `\r\n\r\n` trennt Header und Body. `b"..."` ist eine Bytefolge, nicht ein Python-Unicode-Text.

**Ein Portpaar wird vor der Aufnahme reserviert.** Der Kernel-Aufnahmefilter lässt nur dieses eine bidirektionale IPv4/TCP-Endpunktpaar durch. Das ist stärker als „alles auf Loopback aufnehmen und danach wegfiltern“. Keine Schnittstelle `any`/`eth0` und keine externe Domain werden verwendet. Python reicht eine selbst geöffnete Ausgabedatei an dumpcaps stdout weiter; dumpcap benötigt keine eigenen Dateirechte auf Home-Dateien. Bestehende Sicherheitsprofile werden nicht verändert.

Die Tests sind ein bewusst kleiner Offline-Prüfer für die erzeugte unfragmentierte IPv4/TCP-Demo mit Ethernet-Linktyp, **kein allgemeiner Wireshark-Ersatz**. Sie prüfen die echten Nutzdaten bytegenau. Für die kurze verlustfreie lokale Übertragung wird Paketdateireihenfolge verwendet; beliebige umsortierte/retransmittierte Fernnetz-TCP-Streams müssten über Sequenznummern rekonstruiert werden. Ein solcher Fall würde hier eher einen Testfehler erzeugen als unbemerkt als richtig durchgehen.

## A. `ue2.10/capture_demo.py`

| Zeile | Erklärung |
|---:|---|
| 1 | Kommentar nennt KI-Werkzeug und tatsächlich eingesetztes Modell; wird nicht ausgeführt. |
| 2 | Kommentar dokumentiert das Bearbeitungsdatum. |
| 3 | Beginn der tatsächlich gestellten Anfrage als Herkunftsnachweis. |
| 4 | Fortsetzung: nur eigene harmlose Loopback-Kommunikation, mit Tests. |
| 5 | Modul-Docstring beschreibt den Zweck; später als Hilfe der Kommandozeile benutzt. Das 4-Tupel sind Quell-IP, Quellport, Ziel-IP, Zielport. |
| 6 | `argparse` verarbeitet Kommandozeilenoptionen wie `--output`. |
| 7 | `json` serialisiert Metadaten und Diagnoseausgabe in ein lesbares Format. |
| 8 | `os` wird für das unverpufferte Lesen aus einem Prozess-Dateideskriptor gebraucht. |
| 9 | `Path` behandelt Dateipfade ohne manuelles Zusammenbauen von `/`-Zeichen. |
| 10 | `select` wartet begrenzt darauf, dass dumpcaps stderr-Pipe lesbare Daten enthält. |
| 11 | `socket` stellt TCP-Sockets des Betriebssystems bereit. |
| 12 | `subprocess` startet dumpcap und wartet auf dessen Ende. |
| 13 | `threading` erlaubt dem lokalen Server, parallel zum Client zu laufen. |
| 14 | `time` liefert monotone Zeit für Fristen und eine kurze Startwartezeit. |
| 15 | Leerzeile trennt Imports von Konstanten. |
| 16 | `BODY` enthält ausschließlich einen festen harmlosen Antworttext plus Zeilenumbruch als Bytes. |
| 17 | `REQUEST` ist eine vollständige GET-Anfrage auf den fiktiven lokalen Pfad `/rn-demo`; es werden weder Dateien noch Geheimnisse gelesen. `Connection: close` verlangt Verbindungsende nach der Antwort. |
| 18 | Leerzeile für Lesbarkeit. |
| 19 | Leerzeile trennt Konstanten und Funktion. |
| 20 | Definiert `capture(output)`; sie führt eine echte Aufnahme durch und liefert Metadaten zurück. |
| 21 | Macht aus dem gewünschten Ziel einen absoluten Dateipfad. |
| 22 | Erstellt nötige Zielordner; schon existierende Ordner sind erlaubt. |
| 23 | Öffnet exklusiv binär (`x` = nur neu anlegen). Eine vorhandene Datei führt sofort zu `FileExistsError`, noch bevor ein Socket oder Capture-Helfer gestartet wird. |
| 24 | Leerer Blockkörper: Die Exklusivprüfung/Dateianlage war bereits die gewünschte Aktion. Der `with`-Block schließt die Datei danach wieder. |
| 25 | Erzeugt den Server-Socket: `AF_INET` = IPv4, `SOCK_STREAM` = TCP. |
| 26 | Erzeugt den getrennten TCP-Client-Socket. |
| 27 | Merkt: noch kein Capture-Prozess gestartet. Damit ist die Fehlerbereinigung auch vor dem Start möglich. |
| 28 | Merkt: noch kein Server-Thread gestartet. |
| 29 | Gemeinsame Liste für eventuelle Serverfehler; nach dem Thread-Ende vom Hauptthread geprüft. |
| 30 | Liste der empfangenen Antwort-Byteblöcke; TCP garantiert keine bestimmte recv-Blockgröße. |
| 31 | Beginn des geschützten Arbeitsblocks; der zugehörige `finally`-Teil läuft bei Erfolg und Fehler. |
| 32 | Bindet den Server nur an `127.0.0.1`; Port `0` lässt das Betriebssystem einen freien Port wählen. |
| 33 | Aktiviert das Annehmen von TCP-Verbindungen mit kleiner Warteschlange. |
| 34 | `accept` darf höchstens fünf Sekunden blockieren. |
| 35 | Reserviert auch für den Client einen freien Port nur auf Loopback. Damit steht das gesamte Endpunktpaar schon vor der Aufnahme fest. |
| 36 | Begrenzt blockierende Client-Operationen auf fünf Sekunden. |
| 37 | Liest den tatsächlich vergebenen Server-Port aus dem Socket. Index 1 des Adresstupels ist der Port. |
| 38 | Liest ebenso den reservierten Client-Port. |
| 39 | Beginnt den zusammengesetzten Aufnahmefilter als String. |
| 40 | Erlaubt ausschließlich IPv4-TCP mit Quell-IP und Ziel-IP `127.0.0.1`. Beide Richtungen bleiben damit lokal. |
| 41 | Erster Portfall: Client → Server. Das `f` vor dem String setzt die tatsächlichen Zahlen ein. |
| 42 | Zweiter Portfall nach `or`: Server → Client. Die Klammern verhindern eine falsche Bindung von `and` und `or`. |
| 43 | Schließt die mehrzeilige String-Zuweisung. |
| 44 | Beginnt eine Argumentliste ohne Shell-Auswertung. `sudo -n` darf nicht nach einem Passwort fragen; `dumpcap -i lo` wählt Loopback, `-p` schaltet Promiscuous Mode aus, `-F pcap` wählt das Dateiformat, `-f` kündigt den Filter an. |
| 45 | Ergänzt den Filter, automatischen Stopp nach drei Sekunden und Ausgabe nach stdout (`-w -`). Kein ungeschütztes dauerhaftes Capture. |
| 46 | Python öffnet die gerade exklusiv angelegte Zieldatei binär zum Schreiben; dumpcap muss den Home-Pfad nicht selbst öffnen. |
| 47 | Startet den echten Capture-Prozess; seine Standardausgabe geht direkt in den bereits geöffneten Dateideskriptor. Es werden keine Pakete von Python synthetisiert. |
| 48 | Leitet stderr als Pipe zum Hauptprozess um; Diagnosemeldungen landen nicht zwischen den binären PCAP-Daten. |
| 49 | Prüft die durch `PIPE` gewährleistete stderr-Pipe und macht ihre Existenz auch für Typprüfer sichtbar. |
| 50 | Veränderbarer Bytepuffer für die Startmeldungen. |
| 51 | Setzt eine Frist fünf Sekunden in die Zukunft; monotone Zeit wird durch Uhrzeitkorrekturen nicht zurückgestellt. |
| 52 | Wartet auf dumpcaps echte Bereitschaftsmeldung, nicht nur auf das erfolgreiche Erzeugen eines Prozessobjekts. |
| 53 | Prüft, ob dumpcap unerwartet beendet wurde oder die Frist überschritten ist. `poll()` ist nichtblockierend. |
| 54 | Bricht dann mit der tatsächlich gelesenen Diagnose ab; unlesbare Bytefolgen werden bei der Textkonvertierung ersetzt. |
| 55 | Wartet höchstens 0,1 Sekunden auf lesbare stderr-Daten; die leeren Listen bedeuten, dass nicht auf Schreibbarkeit/Fehlerereignisse anderer Deskriptoren gewartet wird. |
| 56 | Liest bis zu 4096 tatsächlich verfügbare Bytes unverpuffert und hängt sie an. |
| 57 | Kurzer Sicherheitsabstand nach der Bereitschaftsmeldung, bevor der eigene TCP-Verbindungsaufbau beginnt. |
| 58 | Leerzeile trennt Startlogik und Serverfunktion. |
| 59 | Definiert die lokale Serverfunktion; sie verwendet die äußeren Variablen für Listener und Fehlerliste. |
| 60 | Schützt die Serverarbeit, damit Fehler an den Hauptthread gemeldet werden. |
| 61 | Nimmt genau eine Verbindung an und erhält den neuen Verbindungssocket sowie die Clientadresse. |
| 62 | `with connection` schließt diesen Socket nach Antwort oder Fehler automatisch. |
| 63 | Begrenzt blockierende Operationen dieser angenommenen Verbindung auf drei Sekunden. |
| 64 | Beginnt einen leeren Bytepuffer für die Anfrage. |
| 65 | Liest, bis der komplette HTTP-Headerabschluss vorhanden ist; ein `recv` allein wäre bei TCP nicht allgemein ausreichend. |
| 66 | Empfängt höchstens 4096 Bytes pro Aufruf. |
| 67 | Erkennt vorzeitiges Verbindungsende oder einen unerwartet langen Headerpuffer. Die Längenprüfung ist eine kleine Demo-Grenze, kein vollständiger HTTP-Parser. |
| 68 | Meldet eine unvollständige/zu lange Anfrage als Fehler. |
| 69 | Hängt den empfangenen Teil an die bisherige Anfrage an. |
| 70 | Prüft, dass die Gegenstelle Loopback ist und die Anfrage exakt den selbst festgelegten Bytes entspricht. |
| 71 | Fremde/abweichende Anfragen werden nicht als Demo-Erfolg akzeptiert. |
| 72 | Beginnt die HTTP-Antwort: Status `200 OK` und Klartext-Inhaltstyp. |
| 73 | Berechnet `Content-Length` aus der Bytezahl von `BODY` und kodiert die Headerzeile als Bytes. Keine von Hand geratene Länge. |
| 74 | Ergänzt `Connection: close`, die Leerzeile zwischen Header und Body und den festen Text. |
| 75 | `sendall` sendet die vollständige Antwort oder meldet einen Fehler; anschließend schließt der `with`-Block die Verbindung. |
| 76 | Fängt Serverausnahmen ab. Ohne diese Behandlung wäre ein Threadfehler für den Hauptablauf nicht unmittelbar ein Fehlerwert. |
| 77 | Speichert die textuelle Ausnahme in der gemeinsamen Liste. |
| 78 | Leerzeile trennt Funktionsdefinition und tatsächlichen Start. |
| 79 | Baut den benannten Server-Thread; er ist nicht als dauerhaft weiterlaufender Daemon angelegt. |
| 80 | Startet die Serverfunktion parallel; sie wartet nun auf `accept`. |
| 81 | Der Client baut seine einzige Verbindung zum eigenen lokalen Server-Port auf. |
| 82 | Sendet die komplette feste HTTP-Anfrage genau einmal. |
| 83 | Beginnt die Schleife zum vollständigen Lesen der Antwort bis zum Verbindungsende. |
| 84 | Empfängt jeweils bis zu 4096 Bytes. |
| 85 | Eine leere Bytefolge bedeutet bei TCP, dass die Gegenstelle ihre Senderichtung geschlossen hat. |
| 86 | Beendet dann die Empfangsschleife. |
| 87 | Speichert sonst den tatsächlich empfangenen Antwortblock. |
| 88 | Schließt den Client-Socket; damit kann TCP regulär fertig schließen. |
| 89 | Wartet bis zu fünf Sekunden auf das Ende des Server-Threads. |
| 90 | Prüft sowohl einen hängen gebliebenen Thread als auch gemeldete Serverfehler. |
| 91 | Meldet einen solchen Serverfehler an den Aufrufer. |
| 92 | Fügt alle tatsächlich empfangenen Antwortblöcke zu einer Bytefolge zusammen. |
| 93 | Prüft Statuszeile und festen Antworttext als erste Plausibilitätsprüfung; der Offline-Test kontrolliert später zusätzlich Headertrennung, Content-Length und Bytes. |
| 94 | Verhindert eine Erfolgsmeldung bei falscher HTTP-Antwort. |
| 95 | Liest die restlichen Diagnosebytes und wartet auf das automatische dumpcap-Ende; maximal acht Sekunden. |
| 96 | Verbindet Start- und Restdiagnose zu einem lesbaren vollständigen Log. |
| 97 | Prüft den Exitcode und dass die Datei mehr als nur den 24-Byte-PCAP-Dateikopf enthält. Die detaillierte Inhaltsprüfung übernimmt der Test. |
| 98 | Bei Capture-Fehler wird die reale Diagnose ausgegeben, kein Erfolg erfunden. |
| 99 | Beginnt das Rückgabe-Dictionary mit Zielpfad und Server-Port. |
| 100 | Ergänzt Client-Port und den exakt verwendeten Aufnahmefilter. |
| 101 | Ergänzt empfangene HTTP-Antwortlänge und harmlosen Body als lesbaren Text. |
| 102 | Ergänzt die tatsächliche Kommando-Argumentliste und das echte dumpcap-Protokoll; beendet die Rückgabe. |
| 103 | Der `finally`-Block läuft auch bei Ausnahme oder unmittelbar vor der Rückgabe. |
| 104 | Schließt den Client auch dann, wenn vorher ein Fehler auftrat; mehrfaches Schließen ist hier unschädlich. |
| 105 | Schließt den Listener, damit kein eigener HTTP-Dienst zurückbleibt. |
| 106 | Prüft, ob überhaupt ein Threadobjekt erzeugt wurde. |
| 107 | Wartet gegebenenfalls erneut begrenzt auf dessen Ende; die Socket-Timeouts verhindern einen unbegrenzten normalen Wartezustand. |
| 108 | Prüft, ob der Capture-Prozess existiert und noch läuft. |
| 109 | Beginnt den begrenzten Bereinigungsversuch. |
| 110 | Wartet zunächst auf dessen bereits gesetzten automatischen Stopp und liest restliche Pipe-Ausgabe. |
| 111 | Nur bei Überschreiten dieser Frist ist zusätzliche Beendigung nötig. |
| 112 | Sendet dann mittels privilegiertem `kill` SIGINT an die eigene gestartete Prozess-ID. Die Argumentliste benutzt keine Shell. |
| 113 | Fehler beim Beenden werden sichtbar (`check=True`); auch dieser Aufruf hat eine kurze Frist. |
| 114 | Wartet auf die tatsächliche Prozessbeendigung und liest verbleibende Diagnosebytes. |
| 115 | Leerzeile nach der Capture-Funktion. |
| 116 | Leerzeile vor der Kommandozeilenfunktion. |
| 117 | Definiert den Kommandozeileneinstieg `main`. |
| 118 | Erstellt den Argumentparser; der Modul-Docstring erscheint in der Hilfe. |
| 119 | Definiert die optionale Ausgabedatei als `Path`-Objekt. |
| 120 | Standardziel ist `eigene_aufzeichnung.pcap` neben dem Skript, unabhängig vom aktuellen Arbeitsverzeichnis. |
| 121 | Liest und validiert die Kommandozeilenargumente. |
| 122 | Führt die echte Aufnahme mit diesem Ziel aus. |
| 123 | Wählt für die Metadaten denselben Dateinamen mit Endung `.json`. |
| 124 | Schreibt echte Metadaten als eingerücktes JSON mit lesbaren Umlauten und abschließendem Zeilenumbruch. |
| 125 | Gibt dieselben Metadaten im Terminal aus, damit eine protokollierte Ausführung nachvollziehbar ist. |
| 126 | Leerzeile vor dem Startschutz. |
| 127 | Leerzeile für Lesbarkeit. |
| 128 | Führt das Programm nur bei direktem Start aus, nicht beim Import durch die Tests. |
| 129 | Ruft dann `main()` auf. |

## B. `ue2.10/test_capture.py`

Für Netzwerkfelder gilt **Network Byte Order = Big Endian** (`!` in `struct`). Der PCAP-Dateikopf kann dagegen Little oder Big Endian sein; seine Magic Bytes bestimmen die Lesereihenfolge und ob der Bruchteil des Zeitstempels in Mikro- oder Nanosekunden gespeichert wurde. Die echte hier erzeugte Datei hat Nanosekunden-Zeitstempel.

| Zeile | Erklärung |
|---:|---|
| 1 | KI-Kommentar nennt Werkzeug und Modell. |
| 2 | Kommentar nennt das tatsächliche Datum. |
| 3 | Kommentar beginnt den tatsächlichen Auftrag für die Tests. |
| 4 | Fortsetzung: Inhalt und Sicherheitsgrenzen der eigenen Aufnahme offline prüfen. |
| 5 | Docstring beschreibt die Tests der echten klassischen PCAP-Datei. |
| 6 | Importiert den JSON-Leser für die Laufmetadaten. |
| 7 | Importiert `os`, um optional das Testverzeichnis aus einer Umgebungsvariable zu lesen. |
| 8 | Importiert `Path` für robuste Pfade. |
| 9 | Importiert `socket` für die Umwandlung vier roher IPv4-Bytes in eine Punktnotation. |
| 10 | Importiert `struct` zum Entpacken binärer Integerfelder. |
| 11 | Importiert das Standard-Testframework `unittest`. |
| 12 | Importiert die exakt erwarteten Anfrage-/Bodybytes und die Capture-Funktion. Deren Startschutz verhindert eine unbeabsichtigte Aufnahme beim Import. |
| 13 | Leerzeile trennt Imports und Konfiguration. |
| 14 | Testet standardmäßig die Dateien neben dem Testskript; `RN_CAPTURE_DIR` erlaubt denselben Test für einen erneuten Lauf in einem anderen Ordner. |
| 15 | Leerzeile für Lesbarkeit. |
| 16 | Leerzeile vor dem Parser. |
| 17 | Definiert den kleinen Offline-PCAP-Parser `read_packets`. |
| 18 | Liest die echte Datei als Bytes, ohne Wireshark/tshark aufzurufen. |
| 19 | Erste Magic-Variante: Little Endian mit Mikrosekunden-Auflösung. |
| 20 | Zweite Variante: Big Endian mit Mikrosekunden-Auflösung. |
| 21 | Dritte Variante: Little Endian mit Nanosekunden-Auflösung; diese wird bei der tatsächlichen Datei gebraucht. |
| 22 | Vierte Variante: Big Endian mit Nanosekunden-Auflösung; schließt die Zuordnung ab. |
| 23 | Prüft, ob die ersten vier Bytes eine unterstützte klassische PCAP-Signatur sind. |
| 24 | Lehnt andere Formate ab; insbesondere wird PCAPNG nicht bloß wegen einer `.pcap`-Endung als klassisches PCAP gelesen. |
| 25 | Liest Byteordnung und Zeitskala aus der Magic-Zuordnung. |
| 26 | Entpackt den restlichen 24-Byte-Dateikopf: zwei 16-Bit-Versionen, ein vorzeichenbehaftetes 32-Bit-Feld und drei vorzeichenlose 32-Bit-Felder; benötigt werden Snaplen und Linktyp. |
| 27 | Erwartet PCAP-Version 2.4 und Ethernet-Linktyp 1. Auch Linux-Loopback kann bei libpcap als synthetischer Ethernet-Header erscheinen. |
| 28 | Meldet ein nicht unterstütztes Format ausdrücklich. |
| 29 | Setzt den Lesezeiger direkt hinter den globalen 24-Byte-PCAP-Kopf. |
| 30 | Beginnt die Ergebnisliste der dekodierten Pakete. |
| 31 | Wiederholt das Lesen, bis das Dateiende erreicht ist. |
| 32 | Entpackt den 16-Byte-Paketdatensatzkopf: Sekunden, Sekundenbruchteil, gespeicherte Länge, ursprüngliche Länge. Der Name `usec` steht hier historisch für den Bruchteil; die tatsächliche Einheit bestimmt `resolution`. |
| 33 | Überspringt den Datensatzkopf. |
| 34 | Schneidet die laut Kopf enthaltenen Frame-Bytes aus. |
| 35 | Bewegt den Lesezeiger hinter den aktuellen Frame. |
| 36 | Prüft tatsächliche gespeicherte Länge, Gleichheit mit Originallänge und Snaplen-Grenze; abgeschnittene Pakete sind in dieser Demo nicht erlaubt. |
| 37 | Meldet ein solches abgeschnittenes Paket. Ein sehr kurzer defekter Datensatz kann auch bereits beim `unpack` scheitern; er wird damit ebenfalls nicht als gültig akzeptiert. |
| 38 | Prüft Ethernet-EtherType `0x0800`, also IPv4. VLAN/IPv6/ARP sind in dieser bewusst engen eigenen Aufnahme nicht erwartet. |
| 39 | Lehnt andere Netzwerkschichtformate ab. |
| 40 | Entfernt den 14-Byte-Ethernet-Kopf; der Rest beginnt mit IPv4. |
| 41 | Liest das IHL-Halboctet und multipliziert seine 32-Bit-Worte mit vier, um die IPv4-Headerlänge in Bytes zu erhalten. |
| 42 | Liest die IPv4-Gesamtlänge als 16-Bit-Wert in Netzwerk-Byteordnung. |
| 43 | Liest Flags und Fragmentoffset aus dem IPv4-Kopf. |
| 44 | Verlangt IPv4, mindestens 20 Headerbytes, Protokollnummer 6 für TCP und keine Fragmentierung. `0x3FFF` prüft MF und Offset, ohne das erlaubte DF-Bit abzulehnen. |
| 45 | Meldet Abweichungen vom erwarteten unfragmentierten IPv4/TCP. |
| 46 | Prüft, dass die IPv4-Gesamtlänge in den gespeicherten Daten liegt und mindestens einen TCP-Mindestheader enthält. |
| 47 | Meldet eine unmögliche IPv4-Längenangabe. |
| 48 | Isoliert TCP genau bis zum IPv4-Ende; Ethernet-Padding würde damit nicht als TCP-Nutzlast gelesen. |
| 49 | Entpackt Quellport, Zielport und Sequenznummer aus den ersten acht TCP-Bytes. |
| 50 | Das obere Halboctet von TCP-Byte 12 ist Data Offset in 32-Bit-Worten; Multiplikation mit vier ergibt die TCP-Headerlänge einschließlich Optionen. |
| 51 | Prüft Mindestgröße 20 und dass der Header in den TCP-Daten Platz hat. |
| 52 | Meldet eine ungültige TCP-Headerlänge. |
| 53 | Beginnt den Paket-Datensatz: Zeit in Sekunden aus Sekunden plus Bruchteil/Skala, dazu ursprüngliche Frame-Länge. Die nanosekundengenauen Quelldaten werden hier zur übersichtlichen Float-Zeit, nicht für genaue Differenzmessungen, verwendet. |
| 54 | Macht die Quell-IP aus vier Binärbytes lesbar. |
| 55 | Macht die Ziel-IP lesbar. |
| 56 | Speichert Quell- und Zielport. |
| 57 | Speichert Sequenznummer und das Flag-Byte (u. a. FIN, SYN, RST, ACK). |
| 58 | Speichert nur Bytes hinter dem TCP-Header als Nutzdaten und hängt das Dictionary an die Paketliste. |
| 59 | Gibt nach vollständigem Einlesen die Paketliste zurück. |
| 60 | Leerzeile nach der Parserfunktion. |
| 61 | Leerzeile vor der Testklasse. |
| 62 | Definiert eine `unittest.TestCase`-Klasse; Methoden mit `test_` werden als Tests erkannt. |
| 63 | Dekorator macht die Vorbereitung zur Klassenmethode, die einmal für alle Tests läuft. |
| 64 | Definiert diese gemeinsame Vorbereitung. |
| 65 | Liest die echte JSON-Metadatendatei aus dem gewählten Testordner. |
| 66 | Parst die zugehörige echte PCAP-Datei mit dem unabhängig geschriebenen Parser. |
| 67 | Leerzeile vor Test 1. |
| 68 | Definiert den Test auf eine tatsächlich gefüllte Aufnahme. |
| 69 | Erwartet mindestens sieben Pakete, nicht eine für alle Betriebssysteme starre Anzahl zehn. |
| 70 | Vergleicht die selbst gelesene Paketanzahl mit dumpcaps realer Abschlussmeldung. Das allein beweist nicht die Nutzdaten; dafür folgen weitere Tests. |
| 71 | Leerzeile vor Test 2. |
| 72 | Definiert den Datenschutz-/Endpunkttest. |
| 73 | Holt die tatsächlich reservierten Client- und Server-Ports aus den Metadaten. |
| 74 | Prüft jedes gespeicherte Paket, nicht nur eine Stichprobe. |
| 75 | Verlangt in beiden Richtungen ausschließlich `127.0.0.1` als IP-Adresse. |
| 76 | Verlangt genau das eigene Portpaar oder seine umgekehrte Richtung; andere lokale Verbindungen würden durchfallen. |
| 77 | Leerzeile vor Test 3. |
| 78 | Definiert den bytegenauen HTTP-Anfragetest. |
| 79 | Beginnt das Zusammenfügen aller Client-Nutzdaten in Aufzeichnungsreihenfolge. |
| 80 | Wählt dafür nur Pakete mit dem eigenen Client-Quellport aus. |
| 81 | Vergleicht die gesamten Client-Nutzdaten mit der vollständigen erwarteten Anfrage. Damit fallen zusätzliche Nutzdaten ebenfalls auf. |
| 82 | Leerzeile vor Test 4. |
| 83 | Definiert den bytegenauen HTTP-Antworttest. |
| 84 | Beginnt das Zusammenfügen aller Server-Nutzdaten. |
| 85 | Wählt die Pakete mit dem eigenen Server-Quellport aus. |
| 86 | Trennt beim ersten HTTP-Headerabschluss in Header und Body; ein fehlender Abschluss führt zum Testfehler. |
| 87 | Verlangt die richtige Statuszeile. |
| 88 | Prüft die aus der echten Bytezahl erwartete Content-Length-Headerzeile. |
| 89 | Verlangt exakt den harmlosen festen Body, ohne zusätzliche Daten. |
| 90 | Vergleicht die gesamte beobachtete Antwortgröße auch mit dem vom Client protokollierten Wert. |
| 91 | Leerzeile vor Test 5. |
| 92 | Definiert den Test auf TCP-Aufbau und reguläres Schließen. |
| 93 | Sammelt die TCP-Flagbytes aller Pakete. |
| 94 | Verlangt ein initiales SYN ohne ACK. Bit 1 hat Wert 2, ACK hat Wert 16. |
| 95 | Verlangt ein SYN mit ACK als Aufbauantwort. |
| 96 | Verlangt mindestens zwei Pakete mit FIN-Bit (Wert 1), also reguläres Schließen beider Richtungen. Das ist ein Strukturcheck, kein vollständiger TCP-Zustandsautomat. |
| 97 | Verbietet RST-Bit (Wert 4), also einen abrupten Verbindungsabbruch in der Demo. |
| 98 | Leerzeile vor Test 6. |
| 99 | Definiert den Test der sicherheitsrelevanten Capture-Optionen. |
| 100 | Holt die tatsächlich ausgeführte Argumentliste aus den Metadaten. |
| 101 | Verlangt Interface `lo`. |
| 102 | Verlangt `-p`, also deaktivierten Promiscuous Mode. |
| 103 | Verlangt die eingestellte kurze automatische Stoppzeit von drei Sekunden. |
| 104 | Prüft beide lokalen IP-Bedingungen im tatsächlichen Filtertext. Die reale Paketprüfung in Test 2 ist die zusätzliche Inhaltskontrolle und nicht durch diese Textprüfung ersetzt. |
| 105 | Leerzeile vor Test 7. |
| 106 | Definiert den Schutztest gegen Überschreiben existierender Ergebnisse. |
| 107 | Erwartet ausdrücklich die Ausnahme `FileExistsError`. |
| 108 | Versucht die schon vorhandene Originaldatei als Ausgabe zu verwenden. Der Fehler tritt vor Netzwerk-/Capture-Start auf; die Datei bleibt unverändert. |
| 109 | Leerzeile nach der Testklasse. |
| 110 | Leerzeile vor dem Startschutz. |
| 111 | Startet die Tests nur beim direkten Ausführen, nicht bei einem Import. |
| 112 | Führt alle Tests mit einzeln benannten Testresultaten aus (`verbosity=2`). |

## Ergebnisse, die man erklären können sollte

- Die eigentliche ursprüngliche Aufnahme enthält **10 Pakete**; beide IPs sind in jedem Paket `127.0.0.1`, beide Ports gehören zu den eigenen zuvor gebundenen Sockets.
- Der GET-Header ist **61 Bytes** lang; die HTTP-Antwort mit Header und Body **118 Bytes**. Das ist etwas anderes als die Summe der Frame-Längen einschließlich Ethernet-/IP-/TCP-Headern.
- Die sieben Offline-Tests bestehen für die ursprüngliche Aufnahme **und für einen zweiten tatsächlich ausgeführten Lauf** in `ue2.10/wiederholung/`.
- Unverschlüsseltes HTTP wurde bewusst nur lokal mit festen Übungsdaten verwendet; kein Browser, fremder Dienst oder vertrauliches Dokument war beteiligt.
- Linux-Loopback kann in libpcap einen synthetischen Ethernet-Header und ungültig wirkende Checksum-Anzeigen wegen Offloading liefern. Das bedeutet nicht, dass Frames über ein physisches Kabel liefen oder die lokale TCP-Verbindung fehlschlug.
- Keine GUI-Aktion als persönliche Benutzung durch Fabio ausgeben: Die Screenshots stammen von einer tatsächlich automatisiert geöffneten Server-GUI.
