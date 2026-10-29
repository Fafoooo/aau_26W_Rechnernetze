# Ü4.4 – Echte PCAPs Byte für Byte prüfen

Quelltext: [analyse_pcap.py](analyse_pcap.py). Jede nichtleere Quellzeile erhält unten genau einen Eintrag, einschließlich Kommentar- und Fortsetzungszeilen. Die Nummer bezieht sich auf das Python-Programm. [Antworten und Paketwerte](antwort.md), [zentraler Lernweg](../erklaerung_blatt04.md).

## Reihenfolge und live veränderbare Stellen

Der Ablauf ist: vorhandene Datei lesen → Ethernet/IPv4/UDP oder TCP dekodieren → die **konkrete eigene Testfolge** prüfen → JSON ausgeben. Es werden keine Pakete erzeugt und keine Befunde erfunden. Von `ueb04` aus:

```sh
python3 -B ue4.4/analyse_pcap.py nachweise/run01/udp.pcap --kind udp
python3 -B ue4.4/analyse_pcap.py nachweise/run01/tcp.pcap --kind tcp
```

Ohne `--output` wird nichts gespeichert. Mit `--output neuer-bericht.json` muss die Zieldatei neu sein; x verhindert Überschreiben. Anders als verify_namespaces.py beschränkt dieses Skript den Ausgabepfad nicht auf einen Aufgabenordner. **Nicht mit `-O` starten:** Die assert-Prüfungen würden sonst ausgeschaltet, während der Bericht weiterhin `verified: true` setzen könnte.

Für eine andere UDP-Nachricht zuerst den Client ändern und neu aufzeichnen; danach die wirklich gesendete Folge in Zeile 82 anpassen. Niemals den Sollwert ändern, nur damit ein unbekannter Mitschnitt besteht. Andere Testadressen und Ports verlangen passende Änderungen in Zeile 86 bzw. 98–100. TCP-Sollnachrichten in Zeile 104 enthalten bereits die LF-Framingbytes. Die Zuordnung verwendet die Reihenfolge, in der die beiden Clientports im Mitschnitt erstmals vorkommen; das ist kein universeller Flow-Analysator.

Grenzen: nur klassisches PCAP, Ethernet-Linktyp 1, ungetaggtes IPv4, keine IP-Fragmente; kein pcapng, VLAN oder IPv6. Das Skript prüft keine Ethernet-/IP-/Transportchecksummen, wertet Zeitstempel nicht aus und validiert nicht jedes mögliche beschädigte Headerformat vollständig. Bei sehr kurzen Transportheadern können IndexError/struct.error entstehen. TCP-Prüfungen sind bewusst auf die eigenen kleinen vollständigen Testflows zugeschnitten, nicht auf beliebige Capture-Lücken, SYN-Retransmissionsfolgen oder mehrere Umläufe des Sequenzraums. `verified` bescheinigt nur die ausgeführten konkreten Zusicherungen.

## analyse_pcap.py

| Zeile | Was geschieht und warum? |
|---:|---|
| 1 | Herkunftskommentar nennt KI-Werkzeug, Modell und Datum; ändert keine Paketdaten. |
| 2 | Kommentar nennt unabhängiges Auswerten echter UDP-/TCP-PCAPs mit der Python-Standardbibliothek als Auftrag. |
| 3 | Kommentar nennt die zugesagten Prüfbereiche: UDP-Felder und TCP-Aufbau, Daten und geordneter Abschluss. |
| 4 | Modulbeschreibung begrenzt das Format auf klassische Ethernet-PCAPs und grenzt Lesen von Paketerzeugung ab. |
| 6 | Lädt argparse für Capturepfad, Prüfart und optionale neue JSON-Datei. |
| 7 | Lädt ipaddress, um die vier IPv4-Adressbytes als lesbare IP-Adressen darzustellen. |
| 8 | Lädt json für die strukturierte Ergebnisdarstellung statt unverbundener Konsolenmeldungen. |
| 9 | Lädt Path zum binären Einlesen und exklusiven Öffnen einer Ausgabedatei. |
| 10 | Lädt struct, um Zahlenfelder mit der richtigen Byte-Reihenfolge aus Rohbytes zu lesen. |
| 13 | Definiert packets als Leser, der aus einer Capturedatei eine Liste dekodierter Paketdatensätze macht. |
| 14 | Liest die ganze Datei als Bytes; das ist einfach für kleine Lab-Captures, aber kein Streaming großer Mitschnitte. |
| 15 | Beginnt die Zuordnung der beiden klassischen Mikrosekunden-Magicbytes zu Little-Endian (<) und Big-Endian (>). |
| 16 | Ergänzt die beiden Nanosekundenvarianten; die Zeitauflösung wird nicht gespeichert, da Zeitstempel später ignoriert werden. |
| 17 | Prüft Mindestgröße des globalen PCAP-Headers und bekannte Magicbytes; die kurze Datei wird vor weiterem Zugriff abgelehnt. |
| 18 | Bricht bei unbekanntem/zu kurzem Format ausdrücklich ab, statt es als klassisches PCAP zu interpretieren. |
| 19 | Wählt die Byte-Reihenfolge für PCAP-Zahlen anhand der erkannten Magicbytes; das sagt nichts über Netzwerkheader aus. |
| 20 | Liest das 32-Bit-Linktypfeld am globalen Offset 20 und verlangt Ethernet=1. [0] nimmt den einzigen Wert aus dem struct-Tupel. |
| 21 | Stoppt andere Linktypen, weil dann die folgenden Ethernet-Offsets falsch wären. |
| 22 | Beginnt hinter dem 24-Byte-Dateiheader und setzt die sichtbare Paketnummer auf null. |
| 23 | Legt die Liste für vollständig dekodierte Pakete an. |
| 24 | Läuft über Records, solange hinter dem aktuellen Offset noch Dateibytes vorhanden sind. |
| 25 | Prüft, ob der nächste vollständige 16-Byte-Recordheader noch in der Datei liegt. |
| 26 | Meldet einen abgeschnittenen Recordheader, statt unvollständige Zahlen auszulesen. |
| 27 | Liest zwei ignorierte Zeitstempelfelder sowie erfasste und ursprüngliche Framegröße; PCAP-Zahlen verwenden die Datei-Byteordnung. |
| 28 | Überspringt den Recordheader, damit offset auf den eigentlichen Ethernetframe zeigt. |
| 29 | Schneidet genau captured Bytes für diesen Frame aus der Datei aus. |
| 30 | Schiebt den Dateizeiger zum nächsten Record; die Plausibilität des Ausschnitts wird gleich geprüft. |
| 31 | Erhöht die Paketnummer, sodass der erste Frame später Nummer 1 wie in Wireshark hat. |
| 32 | Prüft sowohl fehlende Dateibytes als auch snaplen-Verkürzung gegenüber der ursprünglichen Paketgröße. |
| 33 | Lehnt beide Abschneidefälle ab; ein unvollständiger Mitschnitt soll nicht als vollständiger Nachweis gelten. |
| 34 | Verlangt mindestens Ethernet plus minimalen IPv4-Header und den EtherType 0x0800 an Position 12–13. VLAN-Tags würden diese Annahme verletzen. |
| 35 | Meldet ausdrücklich, dass der Leser nur ungetaggtes Ethernet/IPv4 erwartet. |
| 36 | Entfernt den 14-Byte-Ethernetheader; alle folgenden IP-Offsets beziehen sich auf dieses neue Byteobjekt. |
| 37 | Nimmt die unteren vier Bits des ersten IP-Bytes als Headerlänge in 32-Bit-Wörtern und rechnet in Bytes um. |
| 38 | Liest das IPv4-Gesamtlängenfeld als 16-Bit-Netzwerkzahl; ! bedeutet Big-Endian unabhängig vom PCAP-Format. |
| 39 | Liest Flags und Fragmentoffset zusammen aus dem IPv4-Header für die Fragmentierungsprüfung. |
| 40 | Prüft IPv4-Version, minimale Headerlänge, passende Gesamtgröße und mit 0x3fff das MF-Bit sowie den Fragmentoffset. DF allein ist erlaubt. |
| 41 | Verwirft ungültige Größen und Fragmente, weil keine IP-Wiederzusammensetzung implementiert ist. |
| 42 | Wandelt die Quell-IP-Bytes 12–15 in die punktierte IPv4-Schreibweise um. |
| 43 | Wandelt die Ziel-IP-Bytes 16–19 ebenso um; es werden gemessene Paketbytes statt Solladressen verwendet. |
| 44 | Schneidet die Transportdaten zwischen variablem IP-Headerende und IP-Gesamtlänge aus; Ethernet-Padding am Ende zählt dadurch nicht als Nutzlast. |
| 45 | Beginnt den Paketdatensatz mit laufender Framenummer und beiden ausgelesenen IP-Adressen. |
| 46 | Ergänzt IP-Gesamtlänge, IP-Headerlänge und TTL für den JSON-Nachweis. |
| 47 | Verzweigt bei IP-Protokollnummer 17 in die UDP-Auswertung. |
| 48 | Liest UDP-Quellport, Zielport, UDP-Länge und Checksumme als vier 16-Bit-Netzwerkzahlen. Die Checksumme wird hier nur gelesen, nicht geprüft/ausgegeben. |
| 49 | Verlangt Übereinstimmung von UDP-Länge und vorhandenen Transportbytes sowie mindestens acht Byte Header. |
| 50 | Bricht bei unpassender UDP-Länge ab, damit falsche Ausschnittgrenzen nicht unbemerkt bleiben. |
| 51 | Ergänzt Protokollname, Ports und die feste UDP-Headergröße acht zum Datensatz. |
| 52 | Ergänzt UDP-Gesamtlänge und alle Bytes nach dem UDP-Header als Hextext; so bleibt jede Nutzlast bytegenau JSON-fähig. |
| 53 | Verzweigt stattdessen bei IP-Protokollnummer 6 in die TCP-Auswertung. |
| 54 | Liest TCP-Ports und die 32-Bit-Sequenz-/Bestätigungsnummern aus den ersten zwölf Transportbytes. |
| 55 | Rechnet das obere Halbbyte an TCP-Offset 12, den Data Offset, von Vierbytewörtern in Headerbytes um. TCP-Optionen können den Header verlängern. |
| 56 | Prüft, dass der deklarierte TCP-Header mindestens 20 Bytes umfasst und nicht über die Transportdaten hinausgeht. |
| 57 | Verwirft eine unzulässige TCP-Headerlänge vor dem Ausschneiden der Nutzdaten. |
| 58 | Ergänzt TCP-Protokollname, Ports und rohe Sequenz-/ACK-Nummern zum Frame. |
| 59 | Ergänzt das Flagbyte, die variable Headergröße und die Nutzbytes als Hextext; TCP-Optionen werden so nicht als Nutzlast gezählt. |
| 60 | Fängt alle übrigen IP-Protokollnummern als nicht unterstützten Fall auf. |
| 61 | Bricht etwa bei ICMP oder anderen Transportprotokollen ab; die Captures müssen passend gefiltert sein. |
| 62 | Hängt das erfolgreich dekodierte Paket an die Ergebnisliste an. |
| 63 | Gibt nach dem letzten Record die vollständige Liste zurück, auch eine leere bei einer PCAP ohne Records. |
| 66 | Definiert die Rekonstruktion eines TCP-Nutzbytestroms relativ zur ersten erwarteten Datensequenznummer start. |
| 67 | Kommentar erklärt die Absicht: identische erneut übertragene Bytes sollen nicht doppelt in der Nachricht auftauchen. |
| 68 | Legt ein Wörterbuch Position → Bytewert an; die Position ist relativ zum Streamanfang. |
| 69 | Durchläuft die Frames einer Richtung; ACK-/FIN-Frames ohne Payload tragen später keine Bytewerte bei. |
| 70 | Wandelt die gespeicherte Hexnutzlast wieder in echte Bytes um. |
| 71 | Berechnet die erste relative Byteposition aus Sequenznummer minus start, modulo 2 hoch 32 gegen einen Sequenznummernüberlauf. |
| 72 | Durchläuft jedes Nutzbyte zusammen mit seiner relativen Streamposition, beginnend bei first statt null. |
| 73 | Erkennt eine schon belegte Position mit anderem Bytewert; identische Retransmissionen bleiben erlaubt. |
| 74 | Bricht bei widersprüchlicher Überlappung ab, statt willkürlich eine Version als Wahrheit zu wählen. |
| 75 | Speichert den Bytewert an seiner Position; identische Wiederholungen ersetzen nur denselben Wert. |
| 76 | Verlangt nach Sortieren genau die Positionen 0 bis Anzahl-minus-eins; fehlender Anfang und Lücken fallen so auf. |
| 77 | Meldet eine Lücke, statt eine nur teilweise Nachricht als vollständig rekonstruiert auszugeben. |
| 78 | Baut die Bytes in Positionsreihenfolge zusammen und liefert den fertigen Stream zurück; bei keinem Nutzbyte ergibt das b''. |
| 81 | Definiert die strenge UDP-Prüfung für genau den eigenen Drei-Nachrichten-Lauf. |
| 82 | Legt die drei wirklich erwarteten Nachrichten in ihrer Sendereihenfolge fest; das sind Test-Sollwerte, keine Messungen. |
| 83 | Verlangt genau so viele erfasste Frames wie Nachrichten; verhindert, dass zip still zusätzliche oder fehlende Pakete übersieht. |
| 84 | Ordnet jedem Paket den zugehörigen Solltext nach Reihenfolge zu. |
| 85 | Verlangt UDP als ausgelesenes Transportprotokoll, nicht nur zufällig passende Portfelder. |
| 86 | Prüft Quelle 10.0.0.1, Ziel 10.0.0.2 und Zielport 5000 gemeinsam für jedes Datagramm. |
| 87 | Verlangt einen nichtnulligen gültigen Quellport für den eigenen Clientlauf; legt keinen flüchtigen Portwert fest. |
| 88 | Vergleicht die tatsächlichen Payloadbytes exakt mit UTF-8 des Solltexts, einschließlich Umlauten und Emoji. |
| 89 | Verlangt UDP-Länge gleich UTF-8-Nutzbytezahl plus acht Headerbytes; die Länge ist nicht die Zeichenanzahl. |
| 90 | Gibt erst nach allen Zusicherungen den UDP-Bericht mit Frames und verified=true zurück; nur ohne deaktivierte asserts aussagekräftig. |
| 93 | Definiert die TCP-Prüfung für die beiden eigenen Testverbindungen. |
| 94 | Beginnt die Zuordnung Clientport → Frames dieser Verbindung. Für diese festen Endadressen genügt der Port als Schlüssel. |
| 95 | Durchläuft alle dekodierten Frames in Capture-Reihenfolge. |
| 96 | Verlangt ausschließlich TCP, damit die folgende Flag-/Sequenzprüfung zum Header passt. |
| 97 | Verlangt, dass das RST-Bit 4 nicht gesetzt ist; normaler Verbindungsabschluss soll hier ohne Reset geschehen. |
| 98 | Verlangt als ungeordnetes IP-Paar genau Client 10.0.1.2 und Server 10.0.2.2; erlaubt beide Verkehrsrichtungen. |
| 99 | Prüft, dass einer der beiden Ports 5000 ist; die genaue Richtung wird aus der Quelladresse abgeleitet. |
| 100 | Nimmt bei Clientquelle den Quellport und sonst den Zielport als Clientport, damit Hin- und Rückpakete zusammengehören. |
| 101 | Legt für einen neuen Clientport eine Liste an und hängt den Frame an; die erstmalige Portreihenfolge bleibt im Wörterbuch erhalten. |
| 102 | Verlangt genau zwei getrennte Clientports als die zwei geplanten Verbindungen. |
| 103 | Beginnt die Liste kompakter Verbindungszusammenfassungen für das spätere JSON. |
| 104 | Legt die erwarteten Streams fest: eine LF-abgeschlossene Nachricht, dann drei LF-Frames einschließlich UTF-8 und leerem Text. |
| 105 | Ordnet die zwei Flows in erstmaliger Erfassungsreihenfolge den zwei Sollstreams zu; nicht nach Portnummer sortiert. |
| 106 | Filtert die Client→Server-Pakete dieser Verbindung anhand der Quell-IP. |
| 107 | Filtert entsprechend die Server→Client-Pakete für das Echo. |
| 108 | Erwartet die ersten drei Frames als SYN, SYN/ACK, ACK; weniger Frames oder ein anderer Anfang führen zum Fehler. |
| 109 | Maskiert nur SYN und ACK des ersten Frames und verlangt SYN ohne ACK. Andere Flagbits werden hier nicht ausgeschlossen. |
| 110 | Verlangt beim zweiten Frame sowohl SYN als auch ACK mittels derselben Bitmaske. |
| 111 | Verlangt beim dritten Frame ACK ohne SYN; das ist keine Prüfung jedes möglichen sonstigen Flagbits. |
| 112 | Prüft, dass SYN/ACK die Client-SYN-Sequenz plus eins bestätigt; SYN verbraucht eine Sequenznummer, modulo 2 hoch 32. |
| 113 | Prüft entsprechend die Bestätigung des Server-SYN durch das dritte Segment. |
| 114 | Rekonstruiert Clientnutzbytes ab erster Sequenz nach SYN und verlangt exakt den Sollstream, unabhängig von Segmentgrenzen und identischen Retransmissionen. |
| 115 | Rekonstruiert den Serverstream ab dessen SYN plus eins und verlangt dasselbe Echo bytegenau. |
| 116 | Sammelt Clientframes mit FIN-Bit; diese markieren das Ende der Client-Senderichtung. |
| 117 | Sammelt Serverframes mit FIN-Bit für die Gegenrichtung. |
| 118 | Verlangt mindestens ein FIN je Richtung; ein erfolgreicher Datenaustausch allein wäre noch kein Abschlussnachweis. |
| 119 | Sucht ein Clientpaket mit ACK-Bit und ACK-Nummer Server-FIN-Sequenz plus eins; der eigene Test setzt FIN ohne zusätzliche Nutzlast voraus. |
| 120 | Sucht spiegelbildlich die Bestätigung des Client-FIN in den Serverpaketen; keine vollständige zeitliche Zustandsmaschinenprüfung. |
| 121 | Beginnt die Zusammenfassung mit Clientport und Nummern der drei als Handshake geprüften Frames. |
| 122 | Notiert alle Clientframe-Nummern mit tatsächlich nichtleerer Nutzlast, nicht einfach alle PSH-Pakete. |
| 123 | Notiert dieselben Datenframe-Nummern für die Serverrichtung. |
| 124 | Ergänzt die Nummern aller Client-FIN-Frames zur Nachkontrolle in Wireshark. |
| 125 | Ergänzt die Server-FIN-Frame-Nummern; FIN und ACK können im selben Paket vorkommen. |
| 126 | Ergänzt den geprüften Sollstream als lesbaren UTF-8-Text und schließt den Zusammenfassungsdatensatz ab. |
| 127 | Liefert den TCP-Bericht mit Zusammenfassungen, sämtlichen Frames und Erfolgsmarkierung erst nach allen Prüfungen zurück. |
| 130 | Definiert den Kommandozeileneinstieg; Lesen und Prüfen bleiben daneben einzeln aufrufbar. |
| 131 | Erstellt argparse mit der Modulbeschreibung als Hilfetext. |
| 132 | Verlangt einen Positionsparameter capture als Pfad zur vorhandenen Datei. |
| 133 | Verlangt ausdrücklich --kind udp oder tcp; wählt das Sollszenario, nicht die automatische Dateierkennung. |
| 134 | Bietet einen optionalen Ausgabe-Dateipfad an; ohne ihn bleibt es bei stdout. |
| 135 | Liest und prüft die tatsächlichen CLI-Argumente. |
| 136 | Dekodiert die vorhandene Capturedatei in gemessene Frame-Datensätze. |
| 137 | Führt passend zur gewählten Art die UDP- oder TCP-Sollprüfung aus; eine Ausnahme verhindert die nachfolgende Erfolgsausgabe. |
| 138 | Wandelt den Bericht in eingerücktes JSON mit echten Unicode-Zeichen und abschließendem Zeilenumbruch um. |
| 139 | Speichert nur, wenn --output ausdrücklich angegeben wurde; das Lesen selbst erzeugt keine Datei. |
| 140 | Öffnet die Ausgabedatei exklusiv neu mit UTF-8; vorhandene Dateien werden nicht überschrieben, with schließt das Handle. |
| 141 | Schreibt denselben schon geprüften Berichtstext in diese neue Datei. |
| 142 | Gibt das Ergebnis auch auf stdout aus, unabhängig davon, ob zusätzlich gespeichert wurde. print hängt einen weiteren Zeilenumbruch an. |
| 145 | Führt den CLI-Einstieg nur bei direktem Skriptstart aus; ein Import führt noch keine Captureanalyse durch. |
| 146 | Ruft main auf. Nicht abgefangene Format-/Datei-/Assertionfehler führen zu einem sichtbaren Fehler und nicht zu einem gefälschten Erfolgsbericht. |

## Vorhandene Belege und ehrliche Grenzen

Die gemessenen Daten liegen in [udp-analyse.json](../nachweise/run01/udp-analyse.json) und [tcp-analyse.json](../nachweise/run01/tcp-analyse.json), die zugehörigen echten Mitschnitte in [udp.pcap](../nachweise/run01/udp.pcap) und [tcp.pcap](../nachweise/run01/tcp.pcap). Die echte Wireshark-GUI ist durch [UDP-Screenshot](../nachweise/run01/wireshark-udp.png) und [TCP-Screenshot](../nachweise/run01/wireshark-tcp.png) dokumentiert. Die Byteprüfung ersetzt nicht das Lesen der Felder im Paketbaum.

TShark konnte die Repo-PCAPs wegen Dateizugriffsbegrenzungen nicht öffnen; daraus wird kein erfolgreicher TShark-Lauf gemacht. Python-Auswertung und Wireshark-GUI waren möglich. Der zugrunde liegende Verkehr stammt aus echten Linux-Netzwerk-Namespaces mit Linux-Bridge bzw. gerouteten veth-Links, nicht aus einem ausgeführten Mininet-/OVS-/xterm-Lauf. Diese drei Laborläufe fehlen weiterhin.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29. Tatsächlicher Auftrag: analyse_pcap.py vollständig zeilenweise und semantisch erklären, auch die eingebauten Testzusicherungen, und Messung, Anleitung sowie nicht ausgeführte Laborschritte sauber trennen. Nur Dokumentation wurde dafür geändert.
