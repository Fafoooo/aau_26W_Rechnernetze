# Ü 2.11/2.12 – geprüfte Auswertung und zeilengenaue Erklärung

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol, 2026-10-19. Auftrag: Originalblatt, Originalaufnahmen, echte Wireshark-Exporte, Antworten und Auswertung unabhängig prüfen; jede nichtleere Python-Zeile und jede DOT-Zeile erklären. Diese Erklärung behauptet keine persönliche Eigenleistung des Studierenden.

## 1. Was wurde unabhängig geprüft?

**PCAP** ist hier das klassische Dateiformat für aufgezeichnete Pakete mit Zeitstempeln und Längen; nicht das neuere PCAPNG. **Offline** bedeutet: gespeicherte Bytes lesen, ohne neue Netzwerkpakete zu senden. **Wireshark** ist der Protokollanalysator mit grafischer Oberfläche; seine vorhandenen CSV-Exporte sind tabellarische Textdateien mit Spaltenüberschriften. **Scapy** ist eine davon unabhängige Python-Bibliothek zur Paketdekodierung.

**IPv4** (Internet Protocol Version 4) transportiert adressierte Pakete, **TCP** (Transmission Control Protocol) einen geordneten zuverlässigen Bytestrom und **HTTP** (Hypertext Transfer Protocol) dessen hier untersuchte Anfragen und Antworten für Webressourcen. **UDP** (User Datagram Protocol) transportiert einzelne Datagramme ohne TCP-Verbindung. **TLS** (Transport Layer Security) schützt Anwendungsverkehr kryptographisch; **HTTPS** ist HTTP über einen solchen geschützten Kanal. **GUI** steht für grafische Benutzeroberfläche. **JSON** ist ein strukturiertes Textformat für benannte Datenfelder und Listen. **Python** ist die hier verwendete Programmiersprache; ein Test prüft eine zuvor festgelegte erwartete Eigenschaft.

Gelesen wurden das Originalblatt als Text und das Bild seiner zweiten Seite, beide `antwort.md`, alle vier Python-Dateien, `hierarchie.dot` sowie die vier GUI-CSV-Dateien. Auch die vier zugehörigen Hierarchie-/Conversation-Screenshots wurden visuell kontrolliert. Die Screenshots zeigen leere Anzeigefilter beziehungsweise ausgeschaltetes „Limit to display filter“. Die Herkunft als tatsächlich erzeugte GUI-Nachweise ist durch `ue2.10/gui_kontrolle.md` dokumentiert; hier wurden diese vorhandenen Nachweise geprüft, keine erneute GUI-Sitzung behauptet.

Die vorhandenen Tests wurden tatsächlich ausgeführt:

```bash
python3 -B -m unittest discover -s ue2.11 -p 'test_analyse.py' -v
python3 -B -m unittest discover -s ue2.12 -p 'test_bericht.py' -v
python3 -B ue2.12/bericht.py
python3 -B ue2.12/bericht.py | cmp - ue2.12/messbericht.txt
```

Ergebnis: **16 Analysetests und 4 Berichtstests erfolgreich**; der neu erzeugte Bericht stimmt bytegenau mit `messbericht.txt` überein. `-B` verhindert das Schreiben kompilierter Python-Cachedateien. `cmp` vergleicht Bytes und beendet sich bei Gleichheit erfolgreich ohne Ausgabe.

Für die folgenden Zahlen gilt: Ein **Frame** ist die Einheit der Netzzugangsschicht. Ein **TCP-Segment** ist die TCP-Einheit innerhalb eines IP-Pakets. Eine **PDU** (Protocol Data Unit) ist eine Einheit des jeweils betrachteten Protokolls. Ein **HTTP-Body** ist der Nachrichteninhalt hinter den HTTP-Kopfdaten. Diese vier Dinge sind nicht austauschbar.

Zusätzlich wurden alle drei Original-PCAPs separat mit Scapy gelesen, ohne `analyse.py` zu importieren. IPv4-Gesamtlängen, TCP-Headerlängen, Endpunkte, Richtungen und Zeitstempel lieferten eine unabhängige Nachrechnung. Die HTTP-Antworten wurden nach unabhängiger Zusammensetzung der TCP-Bytes mit `http.client.HTTPResponse` aus der Python-Standardbibliothek gelesen. Alle gespeicherten Protokollzahlen, Paket-/Bytezähler, Dauern, HTTP-Feldwerte, Bodylängen und Body-Prüfsummen wurden damit bestätigt. Das Kontrollprogramm meldete `INDEPENDENT SCAPY / HTTPResponse CROSS-CHECK OK`. Es liegt nur im aktiven Profil-Scratch, nicht als weitere Abgabedatei im Übungsordner. Ein anfänglicher Scapy-Aufruf mit einem `Path` statt einer Zeichenkette wurde ausschließlich in diesem Kontrollprogramm korrigiert.

| Originaldatei | Frames insgesamt | Frame-Bytes insgesamt | TCP-Verbindungen | TCP-Frames | TCP-Segmente mit Nutzbytes | HTTP-Nachrichten nach Zusammensetzen |
|---|---:|---:|---:|---:|---:|---|
| `dump_protocols.pcap` | 39 | 4167 | 1 | 16 | 6 | 1 Anfrage, 1 Antwort |
| `dump_http.pcap` | 68 | 37475 | 3 | 68 | 2 / 5 / 20 je Verbindung | insgesamt 3 Anfragen, 3 Antworten |
| `dump_http_persistent.pcap` | 46 | 36123 | 1 | 46 | 27 | 3 Anfragen, 3 Antworten |

### Bestätigte Endergebnisse

- Protokollaufnahme: Ethernet 39, ARP 10, IPv4 29, UDP 9, DHCP 3, DNS 6, TCP 16, ICMP 4. DHCP-Nachrichten sind Request, ACK und Release; kein vollständiger Discover–Offer–Request–ACK-Ablauf. Zwei ICMP-Echo-Anfragen und zwei Antworten; die genannten historischen DNS-Fragen und Antworten stimmen.
- HTTP-Aufnahme: genau `/test/`, `/test/logo.gif` und `/test/TechnikErleben.png`, Bodies von 145, 4445 und 27065 Bytes. Der HTML-Body enthält den Titel „Test“, „Welcome“ und die zwei relativen Bildverweise. Ein interner Dateiname `index.html` ist daraus nicht beweisbar.
- Die drei Verbindungen: 1236 / 5814 / 30425 Frame-Bytes; Dauer 0.301299 / 0.301248 / 0.502194 Sekunden. IPv4-Summen 1096 / 5618 / 29809 Bytes; TCP-Nutzbytes je Richtung `[138, 422]`, `[146, 4728]`, `[156, 27349]`.
- Protokollaufnahme, einzige TCP-Verbindung: 1763 Frame-Bytes, TCP-Nutzbytes `[115, 740]`, Dauer 0.007399 Sekunden; nach Entfernen des HTTP-Chunk-Framings 577 Body-Bytes.
- Persistente Vergleichsaufnahme: eine Verbindung, 36123 Frame-Bytes, 33071 TCP-Nutzbytes, Dauer 0.704626 Sekunden. Alle drei Bodies sind bytegleich zu denen der nichtpersistenten Aufnahme, unabhängig über SHA-256 bestätigt. **SHA-256** ist eine kryptographische Prüfsummenfunktion; hier dient sie zum Vergleich der rekonstruierten Inhalte, nicht als Herkunftsnachweis.
- Die Requestzeilen im HTTP-Dump nennen HTTP/1.0, die Statuszeilen HTTP/1.1. `Connection: close` erklärt die Nichtwiederverwendung; `Keep-Alive` im zusätzlichen Mitschnitt belegt Wiederverwendung trotz HTTP/1.0-Requestzeilen. Die zeitliche Überlappung des nächsten Verbindungsaufbaus mit dem vorherigen Abbau passt zu den Zeitstempeln.
- Alle tatsächlich vorkommenden Headerfelder und deren Werte sind in `ue2.12/antwort.md` erfasst. **Headerfelder** sind benannte Metadaten wie `Content-Length`; die Request-/Statuszeile ist kein solches Feld. `Content-Length` ist hier die Bodylänge, nicht die Frame-Länge; `Vary` beweist keine Kompression; `X-Pad` ist HTTP-Headerpadding und kein Bildinhalt. Der Titel HTTP(S) erzwingt keine erfundene TLS-Entschlüsselung: beobachtet wird unverschlüsseltes HTTP auf Port 80.

### HTTP-Zählung und Padding: die entscheidenden Fallen

Die GUI-Hierarchie zählt bei `dump_protocols.pcap` **2 HTTP-Packets und 2 HTTP-PDUs**, bei `dump_http.pcap` **6 und 6**. Das sind hier die Zuordnungen der fertig erkannten Nachrichten, **nicht** alle TCP-Segmente, die Teile von HTTP enthalten. Eine Antwort kann sich auf mehrere Segmente verteilen; ihre fertige Dissektion erscheint erst nach der Reassemblierung. **Reassemblierung** bedeutet, anhand der TCP-Sequenznummern den ursprünglichen geordneten Bytestrom wieder zusammenzusetzen. Allgemein können sich Packet- und PDU-Zahlen unterscheiden; ihre Gleichheit in diesen CSVs ist kein allgemeines Gesetz.

Die Hierarchie-Bytes sind ebenfalls keine Conversation-Bytes: HTTP hat in der Protokollaufnahme 243 zugeordnete Bytes und der HTML-Inhaltszweig 577; die ganze TCP-Verbindung umfasst dagegen 1763 Frame-Bytes. Im HTTP-Dump stehen 1284 zugeordnete HTTP-Bytes neben separaten Inhaltszweigen von 145, 4445 und 27065 Bytes. **Conversation** bezeichnet hier den bidirektionalen Verkehr einer TCP-Verbindung zwischen zwei Endpunkten.

**Ethernet-Padding** sind Füllbytes außerhalb der durch IPv4 `total length` begrenzten Daten. Scapy zeigte in der TCP-Verbindung des Protokolldumps insgesamt **12 solche zusätzlichen Bytes** hinter dem TCP/IP-Inhalt. Wer unbesehen `bytes(tcp.payload)` zählt, kann sie irrtümlich als TCP-Nutzdaten behandeln. `analyse.py` begrenzt deshalb zuerst auf `ip[ihl:total]`. Bei den beiden HTTP-Dumps wurden in dieser Kontrolle keine solchen zusätzlichen TCP-Payload-Anhängsel gefunden. `X-Pad` ist dagegen ein echtes HTTP-Headerfeld innerhalb der TCP-Nutzdaten; die beiden Arten von Padding nicht verwechseln.

### Urteil und Grenzen der Prüfung

**Keine fachliche Kritik an den berechneten Endwerten und den Interpretationen der beiden Antworten.** Die Originalaufgaben werden inhaltlich abgedeckt. Ein Artefakthinweis bleibt: Zum Zeitpunkt dieser Prüfung war `ue2.11/hierarchie.svg`, auf das die Antwort verlinkt, noch nicht vorhanden. Die DOT-Quelldatei und der Textbaum waren vorhanden. Die DOT-Datei wurde erfolgreich zu SVG und PNG ausschließlich im aktiven Scratch gerendert; das Bild wurde visuell auf Beschriftung, Kanten und Abschneiden geprüft. Für die grafische Abgabe muss der Hauptbearbeiter das SVG noch am verlinkten Produktpfad erzeugen. Diese Prüfung verändert vereinbarungsgemäß keine fremden Produktdateien.

Der Parser ist bewusst kein universeller oder sicherheitstechnisch gehärteter Protokollanalysator. Er unterstützt hier vollständige klassische Ethernet/IPv4-PCAPs, ARP, ICMP, portbasiert erkanntes DHCP/DNS und die gezeigten HTTP/1.x-Fälle. Er prüft nicht sämtliche Ethernet-/IP-/UDP-/TCP-Details oder Prüfsummen. Beliebige TCP-Verbindungswiederverwendung, Sequenznummernumlauf, vor dem Mitschnitt begonnene Streams, VLAN, IPv6, IP-Fragmente, PCAPNG und allgemeine HTTP-Semantik sind außerhalb des Vertrags. Beispielsweise werden wiederholte gleichnamige Header überschrieben; `HEAD`, bodylose Status-Sonderfälle, close-delimited Bodies, komplexe Transfer-Encoding-Listen und Trailer werden nicht allgemein behandelt. Bei manchen kaputten Binärdaten entsteht ein `struct.error` oder `IndexError` statt des bewusst formulierten `ValueError`; auch das ist ein Abbruch, aber keine umfassende Eingabevalidierung. Tests und Prüfergebnis besagen „für diese Originaldaten richtig“, nicht „für jede denkbare Aufnahme richtig“.

## 2. Leseschlüssel für den Code

Alle Zeilennummern beziehen sich auf den hier geprüften Stand: `analyse.py` 190, `test_analyse.py` 120, `bericht.py` 34, `test_bericht.py` 54 und `hierarchie.dot` 26 Zeilen. Jede nichtleere Python-Zeile wird unten einzeln zugeordnet; reine Leerzeilen trennen Abschnitte und führen nichts aus. Auch Kommentar- und mehrzeilige Stringzeilen werden ausdrücklich erfasst.

Ein **Byte** umfasst acht Bits; ein **Bit** ist eine binäre Stelle. `bytes` ist eine unveränderliche Bytefolge, `bytearray` eine veränderliche. Eine **Liste** hält eine geordnete Folge, ein **Tupel** eine unveränderliche geordnete Folge und ein **Dictionary** Schlüssel-Wert-Paare. `Counter` ist ein Dictionary zum Zählen; noch nicht vorhandene Zähler beginnen bei null. Eine **Funktion** bündelt aufrufbare Schritte; `def` definiert sie. Ein **Generator** liefert seine Werte mit `yield` nacheinander; seine Arbeit beginnt erst beim Iterieren. Ein **Slice** wie `[a:b]` nimmt Elemente ab `a` bis ausschließlich `b`.

Ein **Modul** ist eine importierbare Python-Datei beziehungsweise Bibliothek. Die **Standardbibliothek** wird mit Python ausgeliefert. Ein **Docstring** ist die dokumentierende Zeichenkette am Anfang eines Moduls/einer Funktion. Ein **Import** macht Namen eines Moduls verfügbar. Eine **Exception** ist ein Ausnahmezustand; `raise` löst sie aus. Die Einrückung legt in Python fest, welche Zeilen zu Schleifen oder Bedingungen gehören. Ein **Boolescher Wert** ist `True` oder `False`; rechnerisch lassen diese sich hier als eins beziehungsweise null verwenden.

**Netzwerk-Byteordnung** ist Big Endian, das höchstwertige Byte zuerst. Little Endian speichert das niedrigstwertige zuerst. `struct` liest/schreibt Binärfelder mit Formatzeichen: `H` ist eine vorzeichenlose 16-Bit-, `I` eine vorzeichenlose 32-Bit-Zahl. `<` und `>` wählen Little/Big Endian; `!` wählt Netzwerk-Byteordnung. `&` ist bitweises UND, `>>` eine Bitverschiebung. **CRLF** bezeichnet die Bytes `\r\n`, also Wagenrücklauf und Zeilenvorschub; `\r\n\r\n` beendet HTTP-Kopfdaten.

**IPv4** transportiert adressierte Pakete; **TCP** einen zuverlässigen geordneten Bytestrom, **UDP** einzelne Datagramme. **ARP** ordnet lokale IPv4- und MAC-Adressen zu; **ICMP** trägt Internet-Diagnose-/Fehlermeldungen; **DNS** dient Namensanfragen; **DHCP** der Netzkonfiguration. Ein **Port** kennzeichnet einen Transport-Endpunkt auf einem Rechner; hier ist ein Endpunkt das Paar `(IP-Adresse, Port)`. **SYN**, **ACK** und **FIN** sind TCP-Flags für Synchronisierung/Aufbau, Bestätigung und geordnetes Schließen. Eine **Sequenznummer** nummeriert Positionen im TCP-Bytestrom; eine **Retransmission** überträgt Bytes erneut. **Framing** legt fest, wo eine Nachricht endet. **Chunked** zerlegt den HTTP-Inhalt in Stücke mit hexadezimalen Längenangaben; das ist keine Kompression. **Hexadezimal** bedeutet Zahlendarstellung zur Basis 16.

## 3. `ue2.11/analyse.py` – jede nichtleere Zeile

### Herkunft, Bibliotheken und PCAP-Records

- **Z 1:** KI-Kennzeichnung mit Werkzeug und Modell; Kommentar, nicht ausführbar. Sie dokumentiert Herkunft, ersetzt keine Prüfung.
- **Z 2:** Entstehungsdatum als Kommentar; nicht das Aufnahmedatum der historischen Pakete.
- **Z 3:** Beginnt den dokumentierten Arbeitsauftrag: Original-PCAPs statt erfundener Beispielwerte.
- **Z 4:** Ergänzt die verlangten Messgrößen und unabhängige Prüfung; kein Parserparameter.
- **Z 5:** Öffnet den Modul-Docstring und nennt den engen Ethernet/IPv4-Offlinebereich sowie die Standardbibliothek.
- **Z 7:** Listet ausdrücklich nicht unterstützte Kapselungen und Sequenznummernumläufe auf; diese Einschränkung gehört zum Vertrag.
- **Z 8:** Beschreibt das Ziel des Abbruchs bei ungeeigneten Daten; keine Zusicherung vollständiger Validierung jeder denkbaren Fehlform.
- **Z 9:** Schließt den Docstring; ohne Abschluss wäre der folgende Code Teil einer Zeichenkette oder syntaktisch ungültig.
- **Z 10:** Importiert `argparse` für die Kommandozeilenargumente; vermeidet eigenes fehleranfälliges Argumentzerlegen.
- **Z 11:** Importiert nur `Counter` aus `collections`; das hält Protokollzähler kompakt.
- **Z 12:** Importiert `hashlib` für Datei- und Body-SHA-256; die Hashfunktion zählt keine Pakete.
- **Z 13:** Importiert `ipaddress` zur lesbaren Darstellung binärer IPv4-Adressen.
- **Z 14:** Importiert `json`, ein strukturiertes Textformat für das Ergebnis mit Zahlen, Listen und benannten Feldern.
- **Z 15:** Importiert `Path` für Dateipfade und Leseoperationen unabhängig von manueller Slash-Verkettung.
- **Z 16:** Importiert `struct` für fest formatierte Binärfelder; Netzwerk- und PCAP-Byteordnung bleiben getrennt.
- **Z 19:** Definiert `records(path)`; der Funktionsaufruf allein liest wegen `yield` noch nicht die ganze Generatorarbeit aus.
- **Z 20:** Dokumentiert das Dreier-Ergebnis eines Records: Nanosekundenzeit, gespeicherte Paketbytes, ursprüngliche Paketlänge.
- **Z 21:** Liest die komplette Datei als Bytes. Für kleine Übungsdumps bequem, für sehr große Dateien speicherintensiv.
- **Z 22:** Beginnt das Magic-Byte-Dictionary mit den beiden Mikrosekunden-PCAP-Varianten; der Faktor 1000 führt zu Nanosekunden.
- **Z 23:** Ergänzt die beiden Nanosekunden-Varianten mit Faktor 1. Bytefolgen exakt belassen, nicht als Text interpretieren.
- **Z 24:** Prüft Mindestlänge des globalen Headers und bekannte Magic Bytes; `or` verhindert bei zu kurzer Datei eine gültige Einstufung.
- **Z 25:** Bricht für diese ungültige Grundform mit `ValueError` ab; PCAPNG wird damit nicht versehentlich gelesen.
- **Z 26:** Holt Byteordnung und Zeit-Skalierungsfaktor passend zur Datei; falsche Ordnung würde Längen und Zeiten verfälschen.
- **Z 27:** Entpackt Version, zwei unbenutzte Felder, maximale Aufzeichnungslänge `snaplen` und Linktyp aus dem Rest des 24-Byte-Headers. `_` markiert bewusst nicht verwendete Werte.
- **Z 28:** Verlangt Version 2.4 und Linktyp 1, also Ethernet. Ein Loopback-Linktyp benötigt einen anderen Decoder.
- **Z 29:** Meldet diese Unterstützungsgrenze ausdrücklich als Fehler.
- **Z 30:** Setzt die aktuelle Byteposition direkt hinter den globalen Header.
- **Z 31:** Iteriert solange weitere Dateibytes vorhanden sind; jeder Durchlauf soll einen Record lesen.
- **Z 32:** Prüft, ob die nächsten 16 Bytes des Recordheaders vollständig vorhanden sind.
- **Z 33:** Verhindert das Entpacken eines angeschnittenen Recordheaders durch einen gezielten Abbruch.
- **Z 34:** Liest Sekunden, Sekundenbruchteil, erfasste Länge und ursprüngliche Länge direkt ab `pos`.
- **Z 35:** Überspringt den Recordheader, damit `pos` nun auf das Paket zeigt.
- **Z 36:** Verwirft Sekundenbruchteile außerhalb einer Sekunde, Längen über `snaplen` und erfasste Längen über der Originallänge.
- **Z 37:** Meldet inkonsistente Recordmetadaten statt mit unmöglichen Längen weiterzurechnen.
- **Z 38:** Verlangt ungekürzte Pakete und genügend tatsächliche Dateibytes; eine reduzierte Capture-Länge reicht für diese Rechnung nicht.
- **Z 39:** Bricht bei abgeschnittenem Paket ab. Man darf fehlende Bytes nicht als Nullbytes ergänzen.
- **Z 40:** Liefert ganzzahlige Nanosekunden, genau den Paket-Slice und `wire`; keine PCAP-Verwaltungsbytes gehen in die Frame-Summe ein.
- **Z 41:** Setzt die Position hinter die Paketbytes für den nächsten Record; falscher Vorschub zerstörte die Ausrichtung.

### TCP-Bytestrom zusammensetzen

- **Z 44:** Definiert `reassemble(segments)` für Paare aus Sequenznummer und Nutzbytes einer Richtung.
- **Z 45:** Beschreibt die logische Sortierung und das Vermeiden doppelter Retransmissionen. Implementiert wird dies über Bytepositionen, nicht durch `sorted(segments)`.
- **Z 46:** Legt ein Dictionary `Byteposition → Bytewert` an; dadurch hat jede Sequenzposition höchstens einen Wert.
- **Z 47:** Bearbeitet jedes Segmentpaar; die Ankunftsreihenfolge ist dadurch nicht die spätere Ausgabereihenfolge.
- **Z 48:** `enumerate(payload, seq)` erzeugt zu jedem Byte seine absolute Sequenzposition ab `seq`.
- **Z 49:** Prüft, ob eine bereits belegte Position einen abweichenden Bytewert erhält; gleiche Überlappung ist erlaubt.
- **Z 50:** Verwirft widersprüchliche Überlappung, statt willkürlich einen der beiden Inhalte auszuwählen.
- **Z 51:** Speichert den Bytewert an der Position; identische Wiederholungen ändern das Ergebnis nicht.
- **Z 52:** Erkennt, ob überhaupt Nutzdaten vorhanden sind; reine ACK-Verbindungen können einen leeren Datenstrom haben.
- **Z 53:** Liefert in diesem Fall leere Bytes, nicht `None`, sodass der Aufrufer dieselbe Datentype behält.
- **Z 54:** Bestimmt kleinste und größte belegte Sequenzposition. TCP-Nummern werden hier nicht modulo ihres Feldbereichs entrollt.
- **Z 55:** Vergleicht die Länge des gesamten Positionsintervalls mit der Anzahl belegter Positionen; bei Ungleichheit fehlen Bytes.
- **Z 56:** Meldet eine Lücke beziehungsweise einen nicht unterstützten Sequenzumlauf. Das prüft nicht verlorene Bytes vor der ersten oder nach der letzten sichtbaren Position.
- **Z 57:** Liest alle Bytepositionen lückenlos und aufsteigend in eine neue Bytefolge. Das `+ 1` schließt die höchste Position ein.

### HTTP-Nachrichten abgrenzen

- **Z 60:** Definiert `http_messages(data)` für einen bereits reassemblierten gerichteten Bytestrom.
- **Z 61:** Beschränkt den HTTP-Vertrag auf die gezeigten GET-, Content-Length- und Chunked-Fälle; kein allgemeiner Webbrowserparser.
- **Z 62:** Initialisiert die Liste der Nachrichten; eine persistente Verbindung kann mehrere Einträge liefern.
- **Z 63:** Arbeitet den noch nicht verbrauchten Rest ab; bei leerem Strom gibt es null Nachrichten.
- **Z 64:** Sucht das erste HTTP-Headerende als CRLF-CRLF; reine LF-Zeilen werden nicht stillschweigend akzeptiert.
- **Z 65:** Erkennt den Rückgabewert `-1` für „Trennzeichen fehlt“.
- **Z 66:** Bricht ab, statt einen unvollständigen Header als ganze Nachricht zu zählen.
- **Z 67:** Dekodiert nur die Kopfdaten mit ISO-8859-1 und zerlegt sie in Zeilen. Bildbytes dürfen nicht auf diese Weise als Text verarbeitet werden.
- **Z 68:** Legt ein Dictionary für normalisierte Feldnamen und Feldwerte an.
- **Z 69:** Überspringt die erste Zeile, weil diese Request-/Statuszeile und kein Headerfeld ist.
- **Z 70:** Trennt jede Feldzeile nur am ersten Doppelpunkt; weitere Doppelpunkte können zum Wert gehören.
- **Z 71:** Normalisiert den Feldnamen auf Kleinschreibung und entfernt äußere Leerzeichen des Werts. Wiederholte gleichnamige Felder würden überschrieben: bewusste Grenze.
- **Z 72:** Nimmt alle Bytes hinter dem Headerabschluss als vorläufigen Rest; `+ 4` entfernt genau das CRLF-CRLF.
- **Z 73:** Wählt Chunked nur für den normalisierten Wert exakt `chunked`. Eine Liste wie `gzip, chunked` wird hier nicht allgemein verarbeitet.
- **Z 74:** Legt einen veränderlichen Body-Puffer an, an den Nutzstücke angehängt werden können.
- **Z 75:** Wiederholt die Chunk-Verarbeitung bis zum Nullchunk; `while True` braucht den gezielten `break` weiter unten.
- **Z 76:** Trennt die nächste Chunk-Größenzeile vom Rest am ersten CRLF. Fehlt es, bricht `split`/Entpacken ab.
- **Z 77:** Ignoriert eine mögliche Erweiterung hinter `;` und liest die Größenangabe hexadezimal. Allgemeine Syntaxprüfung oder Größenlimits fehlen.
- **Z 78:** Erkennt den Nullchunk, der das Ende der Chunk-Daten markiert.
- **Z 79:** Verlangt unmittelbar eine leere Abschlusszeile; weitere Trailerfelder sind nicht unterstützt.
- **Z 80:** Meldet die ausgeschlossene Trailerform ausdrücklich.
- **Z 81:** Entfernt die beiden Abschlussbytes aus dem Rest, damit eine mögliche Folgemeldung korrekt beginnt.
- **Z 82:** Verlässt nur die innere Chunkschleife, nicht die Verarbeitung weiterer HTTP-Nachrichten.
- **Z 83:** Prüft sowohl die angekündigte Chunk-Länge als auch das CRLF direkt hinter dem Chunk.
- **Z 84:** Bricht bei fehlenden Chunkbytes oder falschem Stückabschluss ab.
- **Z 85:** Hängt ausschließlich die `size` Inhaltsbytes an; Größenzeilen und Chunkabschluss zählen nicht zum Body.
- **Z 86:** Überspringt das gerade gelesene Stück samt Abschluss, um die nächste Größenzeile zu erreichen.
- **Z 87:** Beginnt den alternativen Framingweg für nicht als Chunked erkannte Nachrichten.
- **Z 88:** Erkennt die hier unterstützten GET-Anfragen anhand der ersten Zeile.
- **Z 89:** Setzt deren Bodygröße hier auf null. Das ist ein dumpbezogener Vertrag, keine universelle Aussage über alle HTTP-Requests.
- **Z 90:** Prüft bei anderen Nachrichten auf das Feld `content-length`.
- **Z 91:** Wandelt die dezimale Längenangabe in eine Ganzzahl um; ungültiger Zahlentext führt zum Abbruch.
- **Z 92:** Behandelt den Fall ohne unterstützte explizite Längeninformation.
- **Z 93:** Verwirft diese Antwortform. „Bis TCP-Schluss lesen“, HEAD oder spezielle bodylose Statuscodes werden nicht allgemein implementiert.
- **Z 94:** Verwirft negative Länge oder einen kürzeren sichtbaren Rest als angekündigt.
- **Z 95:** Meldet den unvollständigen Body; ein Fragment wird nicht als erfolgreiches Objekt ausgegeben.
- **Z 96:** Trennt exakt `size` Bodybytes vom Rest für die nächste Nachricht; ein Slice-Ende ist exklusiv.
- **Z 97:** Beginnt den Ergebnisdatensatz mit Startzeile und Headerdictionary; Roh-Bodybytes werden nicht im JSON gespeichert.
- **Z 98:** Ergänzt Bodylänge und SHA-256 des tatsächlichen Bodys. Die Hashfunktion akzeptiert auch das `bytearray` des Chunked-Zweigs.
- **Z 99:** Ersetzt die Eingabe durch den noch nicht verbrauchten Rest; ohne diesen Schritt würde dieselbe Nachricht endlos wiederholt.
- **Z 100:** Liefert die geordnete Nachrichtenliste zurück; Nachrichtenzahl ist keine TCP-Segmentzahl.

### Ethernet, IPv4 und Transportprotokolle auswerten

- **Z 103:** Definiert die zentrale Analysefunktion mit dem Dateipfad als Eingabe.
- **Z 104:** Initialisiert Protokollzähler, chronologische Verbindungsliste und Zuordnung des aktuellen Streams je Endpunktpaar.
- **Z 105:** Startet die Summen aller Frame-Bytes und Frames bei null, unabhängig vom Transportprotokoll.
- **Z 106:** Iteriert über die vom Recordgenerator gelieferten Zeit-/Byte-/Längentupel.
- **Z 107:** Zählt jedes vollständig gelesene Paket genau einmal in der Aufnahmegesamtzahl.
- **Z 108:** Addiert die ursprüngliche Frame-Länge. Die PCAP-Recordheader gehören nicht dazu.
- **Z 109:** Zählt die als Ethernet vorausgesetzte Kapselung; der Linktyp wurde bereits im globalen Header geprüft.
- **Z 110:** Prüft die Mindestlänge des gewöhnlichen Ethernet-Headers ohne VLAN.
- **Z 111:** Bricht bei einem zu kurzen Frame ab.
- **Z 112:** Liest den EtherType ab Byteposition 12 als Netzwerk-16-Bit-Zahl; dieser bestimmt den nächsten Decoder.
- **Z 113:** Erkennt EtherType `0x0806` als ARP.
- **Z 114:** Erhöht den ARP-Zähler; der Parser zerlegt den ARP-Inhalt selbst nicht weiter.
- **Z 115:** Geht direkt zum nächsten Frame, weil ARP hier nicht in IPv4 steckt.
- **Z 116:** Prüft, ob der andere unterstützte EtherType `0x0800`, also IPv4, vorliegt.
- **Z 117:** Verwirft sonstige Kapselungen statt sie als IPv4 fehlzudeuten; VLAN und IPv6 fallen darunter.
- **Z 118:** Zählt die IPv4-Kapselung für diesen Frame.
- **Z 119:** Schneidet die 14 Ethernet-Headerbytes ab; der Slice kann noch Ethernet-Padding enthalten.
- **Z 120:** Gewinnt die IPv4-Headerlänge aus dem unteren Halbbyte in Vierbyteeinheiten und `total length` aus dem Zweibytefeld ab Position 2.
- **Z 121:** Prüft Version, minimale Headergröße, Gesamtlänge und vorhandene Bytes. Extrem kurze Eingaben können schon vorher mit einer Binärleseexception abbrechen.
- **Z 122:** Meldet die hier erkannten Headerinkonsistenzen.
- **Z 123:** Maskiert Fragmentoffset und More-Fragments-Bit mit `0x3fff`; das Don't-Fragment-Bit allein wird nicht verboten.
- **Z 124:** Verwirft Fragmente, weil der Code keine IP-Fragmentreassemblierung besitzt.
- **Z 125:** Wandelt die beiden Vierbyteadressen in lesbare IPv4-Zeichenketten um.
- **Z 126:** Begrenzt die Nutzdaten auf `ihl:total`. Genau dieser Schritt hält Ethernet-Füllbytes aus den TCP-Nutzdaten heraus.
- **Z 127:** Liest die IPv4-Protokollnummer aus dem Header; sie ist nicht der EtherType.
- **Z 128:** Wählt Protokollnummer 1, also ICMP.
- **Z 129:** Zählt ICMP, ohne die Nachrichtentypen hier auszuwerten; Echo-Details wurden separat mit Scapy kontrolliert.
- **Z 130:** Wählt alternativ Protokollnummer 17, also UDP.
- **Z 131:** Zählt ein UDP-Paket unabhängig davon, welche Anwendung es trägt.
- **Z 132:** Liest Quell- und Zielport aus den ersten vier UDP-Bytes; eine vollständige UDP-Prüfung findet nicht statt.
- **Z 133:** Ordnet Port 53 in einer Richtung hier DNS zu; das ist Portheuristik, kein vollwertiger DNS-Decoder.
- **Z 134:** Erhöht in diesem Fall zusätzlich den DNS-Zähler.
- **Z 135:** Erkennt das ungeordnete Portpaar 67/68 als DHCP-Verkehr dieser Aufnahme; die Mengenform ignoriert die Richtung.
- **Z 136:** Erhöht den DHCP-Zähler, ohne DHCP-Optionen im Produktparser zu zerlegen.
- **Z 137:** Wählt als weitere Alternative Protokollnummer 6, also TCP.
- **Z 138:** Erhöht den TCP-Frame-Zähler; auch reine Kontrollsegmente zählen.
- **Z 139:** Liest TCP-Quellport, Zielport und Sequenznummer in Netzwerk-Byteordnung.
- **Z 140:** Gewinnt die TCP-Headerlänge aus dem oberen Halbbyte von Byte 12 und liest die üblichen Flags aus Byte 13.
- **Z 141:** Verlangt mindestens den gewöhnlichen TCP-Header und genügend Bytes für eventuelle Optionen.
- **Z 142:** Meldet eine unplausible TCP-Headergröße.
- **Z 143:** Entfernt TCP-Header und Optionen; `segment` enthält jetzt nur TCP-Nutzbytes, nicht das ganze Segment.
- **Z 144:** Bildet gerichteten Sender- und Empfängerendpunkt aus IP-Adresse und Port.
- **Z 145:** Sortiert die zwei Endpunkte zu einem richtungsunabhängigen Dictionaryschlüssel. Hin- und Rückverkehr treffen so dieselbe Zuordnung.
- **Z 146:** Erkennt ein initiales SYN ohne ACK. `not flags & 16` meint, dass das ACK-Bit nicht gesetzt ist.
- **Z 147:** Legt nur bei unbekanntem Endpunktpaar oder neuer SYN-Sequenz einen neuen Stream an; identischer SYN-Retry bleibt derselbe Stream.
- **Z 148:** Beginnt den Streamdatensatz mit laufender ID und den anhand des SYN bestimmten Rollen Client und Server.
- **Z 149:** Speichert SYN-Sequenz und erste/letzte Nanosekundenzeit; am Anfang sind beide Zeiten gleich.
- **Z 150:** Initialisiert Richtungszähler für Pakete, komplette Frames und IPv4-Bytes; Index 0 ist Client→Server, Index 1 umgekehrt.
- **Z 151:** Initialisiert TCP-Nutzbytes, separate Segmentlisten für beide Richtungen und die SYN-ACK-Beobachtung. Listen werden für jeden neuen Stream neu angelegt.
- **Z 152:** Hängt den neuen Datensatz an die Ergebnisliste; ihre bisherige Länge war seine Stream-ID.
- **Z 153:** Setzt ihn als aktuellen Stream des Endpunktpaares. Komplexe Überlappung mehrfach wiederverwendeter Verbindungen ist damit nicht allgemein gelöst.
- **Z 154:** Erkennt TCP-Verkehr, dem kein initiales SYN in der Aufnahme zugeordnet werden konnte.
- **Z 155:** Bricht dafür bewusst ab; der Code errät keine Client-/Serverrollen für angeschnittene Verbindungen.
- **Z 156:** Holt den aktuell zugeordneten Streamdatensatz.
- **Z 157:** Wählt Richtungsindex 0 für den beim SYN erkannten Client, sonst 1. Die Listenumwandlung passt zum gespeicherten JSON-tauglichen Format.
- **Z 158:** Aktualisiert das späteste Paketdatum mit `max`; die erste Zeit bleibt die SYN-Zeit.
- **Z 159:** Zählt auch SYN, ACK und FIN in der jeweiligen Richtung.
- **Z 160:** Addiert die komplette Frame-Länge genau zu dieser TCP-Conversation und Richtung.
- **Z 161:** Addiert die IPv4-Gesamtlänge, also ohne Ethernet-Header und -Padding.
- **Z 162:** Addiert die Nutzlänge dieses Segments; Retransmissionen würden hier zunächst erneut mitgezählt.
- **Z 163:** Prüft in Serverrichtung, ob SYN und ACK beide gesetzt sind. Das bedeutet `(flags & 0x12) == 0x12`, nicht Vergleich nur eines Bits.
- **Z 164:** Merkt den beobachteten SYN-ACK. Es ist kein vollständiger TCP-Zustandsautomat und allein kein Beweis jedes Handshakeschritts.
- **Z 165:** Speichert nur Segmente mit tatsächlichen Nutzbytes für die spätere Reassemblierung.
- **Z 166:** Fügt Sequenzposition und Nutzbytes der passenden Richtung hinzu; SYN verbraucht eine Sequenznummer, deshalb gegebenenfalls `+ 1`.
- **Z 167:** Beginnt den Fehlerzweig für sonstige IPv4-Protokollnummern.
- **Z 168:** Verwirft unbekannte Transport-/Internetprotokolle, statt sie still zu unterschlagen.

### Ergebnisse aufbereiten und Kommandozeile

- **Z 169:** Verarbeitet nach dem letzten Frame jeden gefundenen TCP-Stream.
- **Z 170:** Entfernt mit `pop` die internen Segmentlisten aus dem späteren Ergebnis und reassembliert beide Richtungen getrennt.
- **Z 171:** Speichert die eindeutigen Nutzlängen der zusammengesetzten Ströme; Vergleich mit Z 162 zeigt mögliche Wiederholungen.
- **Z 172:** Bildet letztes minus erstes Datum, wandelt Nanosekunden in Sekunden und formatiert neun Nachkommastellen als Zeichenkette. Anzeigepräzision ist nicht gleich Messauflösung.
- **Z 173:** Versucht HTTP nur beim anhand des SYN erkannten Serverport 80; HTTP auf anderen Ports wird nicht automatisch erkannt.
- **Z 174:** Parst beide gerichteten Datenströme als Anfrage-/Antwortlisten. TCP-Paketgrenzen spielen für HTTP nun keine Rolle mehr.
- **Z 175:** Beginnt den Zweig für nicht als HTTP behandelte Streams.
- **Z 176:** Setzt dafür leere HTTP-Listen; die TCP-Zähler bleiben trotzdem erhalten.
- **Z 177:** Beginnt das Gesamtergebnis mit Dateiname und SHA-256 der Originaldatei; die Datei wird dafür nochmals vollständig gelesen.
- **Z 178:** Ergänzt Gesamtframezahl und Gesamtframebytes der Aufnahme, nicht nur des TCP-Anteils.
- **Z 179:** Ergänzt Protokollzähler, Verbindungszahl und Streamliste. `dict(counts)` macht aus dem spezialisierten Zähler ein gewöhnliches Dictionary.
- **Z 182:** Definiert den Einstieg für die Kommandozeilenbedienung getrennt von der importierbaren Rechenfunktion.
- **Z 183:** Erstellt den Argumentparser und nutzt den Modul-Docstring als Hilfetext.
- **Z 184:** Verlangt ein Positionsargument `pcap` und wandelt es direkt in ein `Path`-Objekt um.
- **Z 185:** Liest und validiert die tatsächlich übergebenen Argumente; fehlende Eingabe erzeugt einen Nutzungshinweis.
- **Z 186:** Gibt das Analyseergebnis als eingerücktes JSON mit lesbaren Nicht-ASCII-Zeichen aus; schreibt nicht selbst eine Ergebnisdatei.
- **Z 189:** Startschutz: führt den folgenden Aufruf nur beim direkten Programmstart aus, nicht beim Import durch Tests.
- **Z 190:** Ruft den Kommandozeileneinstieg auf; ohne diese Zeile würde direkter Start keine Analyse ausgeben.

## 4. `ue2.11/test_analyse.py` – jede nichtleere Zeile

Ein **Testfall** prüft eine konkrete erwartete Eigenschaft. Eine **Assertion** ist eine prüfende Bedingung; schlägt sie fehl, wird der Test als Fehler/Fehlschlag gemeldet. Eine **Testklasse** sammelt Fälle. `unittest.TestCase` liefert die Assertionmethoden. Ein **Kontextmanager** mit `with` sorgt auch bei Fehlern für Aufräumen, etwa das Schließen einer Datei. `assertRaises` besteht nur, wenn im eingerückten Block der erwartete Ausnahmetyp auftritt; `subTest` kennzeichnet Varianten eines Tests getrennt.

- **Z 1:** Dokumentiert KI-Werkzeug und Modell; beeinflusst keinen erwarteten Messwert.
- **Z 2:** Nennt das Entstehungsdatum der Tests, nicht der Aufnahmen.
- **Z 3:** Nennt den Prüfauftrag mit Originaldaten und echten GUI-Exporten; diese Referenzen sollen nicht aus dem zu testenden Code erzeugt werden.
- **Z 4:** Importiert den CSV-Leser, damit Feldnamen statt unsicherer Spaltennummern verwendet werden können.
- **Z 5:** Importiert `Path` für testdateibezogene Pfade.
- **Z 6:** Importiert `struct` zum Erzeugen des kleinen Big-Endian-Test-PCAPs.
- **Z 7:** Importiert `tempfile` für automatisch aufgeräumte temporäre Testdateien.
- **Z 8:** Importiert das Testframework `unittest`.
- **Z 9:** Importiert genau die vier zu prüfenden Funktionen aus dem Produktmodul; die Tests enthalten keinen zweiten Produktparser.
- **Z 11:** Bestimmt `ueb02` relativ zur Testdatei über absoluten Pfad und deren übergeordneten Übungsordner. Das vermeidet Abhängigkeit vom aktuellen Arbeitsverzeichnis.
- **Z 14:** Definiert die Testklasse als Unterklasse von `TestCase`; dadurch entdeckt `unittest` ihre `test_`-Methoden.
- **Z 15:** Beginnt den Test der Gesamt- und Protokollzähler.
- **Z 16:** Analysiert die echte Protokollaufnahme, nicht eine künstliche Ersatzdatei.
- **Z 17:** Verlangt genau 39 Frames; erkennt ausgelassene oder doppelt gezählte Records.
- **Z 18:** Verlangt 4167 Frame-Bytes; schützt unter anderem vor Zählen der PCAP-Dateigröße.
- **Z 19:** Verlangt genau eine TCP-Verbindung, nicht 16 Verbindungen für 16 TCP-Pakete.
- **Z 20:** Beginnt den Vergleich des gesamten Protokolldictionarys mit Ethernet- und IPv4-Sollwerten.
- **Z 21:** Ergänzt ARP, UDP, TCP, ICMP, DNS und DHCP und schließt den Vergleich; zusätzliche falsche Schlüssel würden ebenfalls auffallen.
- **Z 23:** Beginnt den Vergleich mit den GUI-TCP-Conversations.
- **Z 24:** Führt ihn für den Protokoll- und den HTTP-Dump aus; der persistente Zusatzdump hat hier keinen GUI-CSV-Vergleich.
- **Z 25:** Kennzeichnet jede Variante mit dem Dumpnamen für verständliche Fehlermeldungen.
- **Z 26:** Holt die frisch berechneten Streams der jeweiligen Originalaufnahme.
- **Z 27:** Öffnet die passende vorhandene GUI-CSV-Datei; `with` schließt sie zuverlässig.
- **Z 28:** Liest alle CSV-Zeilen als Dictionaries mit den originalen Spaltennamen.
- **Z 29:** Prüft die Verbindungszahl vor dem paarweisen Vergleich; wichtig, weil `zip` sonst am kürzeren Eingang endet.
- **Z 30:** Paart Parserstreams mit GUI-Zeilen in deren vorhandener übereinstimmender Reihenfolge. Bei anderer Sortierung müsste nach Endpunkten zugeordnet werden.
- **Z 31:** Vergleicht Clientadresse und ganzzahlig umgewandelten Clientport mit Endpunkt A.
- **Z 32:** Vergleicht Serveradresse und -port mit Endpunkt B.
- **Z 33:** Vergleicht die Gesamtpaketzahl aus beiden Richtungen mit der GUI-Spalte `Packets`.
- **Z 34:** Vergleicht komplette Frame-Bytes mit GUI-`Bytes`, nicht nur TCP- oder HTTP-Nutzbytes.
- **Z 35:** Prüft zusätzlich Client→Server-Bytes gegen `Bytes A → B`; vertauschte Richtungen würden auffallen.
- **Z 36:** Prüft getrennt Server→Client gegen `Bytes B → A`.
- **Z 37:** Vergleicht die Sekundenwerte auf neun Dezimalstellen. Dies toleriert den winzigen binären Darstellungsrest der GUI bei 0.007399 Sekunden.
- **Z 38:** Verlangt den beobachteten SYN-ACK-Merker; das allein testet keinen vollständigen TCP-Zustandsautomaten.
- **Z 40:** Beginnt den GUI-Abgleich der Protokollhierarchie.
- **Z 41:** Berechnet die Protokollzahlen erneut aus der Originalaufnahme.
- **Z 42:** Beginnt die Übersetzung ausgeschriebener GUI-Namen in interne Namen mit Ethernet und IPv4.
- **Z 43:** Ergänzt UDP und DHCP; DHCP wird nicht fälschlich als weiterer zusätzlicher BOOTP-Austausch gezählt.
- **Z 44:** Ergänzt DNS und TCP.
- **Z 45:** Ergänzt ICMP und ARP und schließt das Zuordnungsdictionary.
- **Z 46:** Öffnet die echte GUI-Hierarchie-CSV des Protokolldumps.
- **Z 47:** Liest deren Zeilen anhand der CSV-Feldnamen.
- **Z 48:** Beschränkt den Abgleich auf die acht vom Parser gezählten Protokolle. HTTP-PDU- und Inhaltszeilen sind nicht Teil dieses Tests.
- **Z 49:** Vergleicht jeden so zugeordneten Paketzähler mit der GUI-Spalte `Packets`, nicht mit `Bytes` oder `PDUs`.
- **Z 51:** Beginnt den gezielten Regressionstest gegen irrtümliches TCP-Zählen von Ethernet-Padding. Ein Regressionstest verhindert die Wiederkehr eines bekannten Fehlermusters.
- **Z 52:** Holt die einzige TCP-Verbindung der Original-Protokollaufnahme.
- **Z 53:** Prüft die einfachen TCP-Nutzbytes beider Richtungen auf 115 und 740.
- **Z 54:** Prüft dieselben Werte nach eindeutiger Reassemblierung; Füllbytes oder unnötige Wiederholungen dürfen das Ergebnis nicht ändern.
- **Z 55:** Prüft den de-chunkten Antwortbody auf 577 Bytes; Chunk-Framing gehört nicht zum Inhalt.
- **Z 57:** Beginnt einen kleinen isolierten Test für Chunked. Isoliert heißt: ohne PCAP-, Ethernet- oder TCP-Verarbeitung.
- **Z 58:** Baut die HTTP-Statuszeile samt Transfer-Encoding-Header und Headerabschluss als Bytekonstante.
- **Z 59:** Ergänzt Stücke der Längen zwei und eins sowie den Nullchunk. Benachbarte Bytekonstanten werden von Python zusammengefügt.
- **Z 60:** Erwartet drei Inhaltsbytes, also nur `abc`, nicht die Größenzeilen oder CRLFs.
- **Z 62:** Beginnt den isolierten Test mehrerer Antworten in einem Bytestrom.
- **Z 63:** Baut die erste Antwort mit expliziter Länge eins und Body `a`.
- **Z 64:** Hängt eine zweite Antwort mit Länge zwei und Body `bc` direkt an.
- **Z 65:** Verlangt die Bodylängenliste `[1, 2]`; der Parser darf den Rest nicht verschlucken oder als ersten Body zählen.
- **Z 67:** Beginnt den Negativtest für einen unvollständigen HTTP-Header.
- **Z 68:** Erwartet `ValueError` aus dem eingerückten Funktionsaufruf.
- **Z 69:** Übergibt nur eine Statuszeile mit einem CRLF, aber ohne Headerabschluss.
- **Z 71:** Beginnt den Negativtest eines zu kurzen HTTP-Bodys.
- **Z 72:** Verlangt dafür einen `ValueError` statt eines scheinbar erfolgreichen Objekts.
- **Z 73:** Kündigt drei Bytes an, liefert aber nur `a`; das muss als unvollständig erkannt werden.
- **Z 75:** Beginnt den Negativtest eines unvollständigen Chunks.
- **Z 76:** Legt den erwarteten Ausnahmetyp fest.
- **Z 77:** Kündigt drei Chunkbytes an, liefert aber nur `ab` und keinen Abschluss.
- **Z 79:** Beginnt den Test für ungeordnete und wiederholte TCP-Bytes.
- **Z 80:** Übergibt überlappende Segmente samt identischer Wiederholung und verlangt einmalig geordnetes `abcd`.
- **Z 82:** Beginnt den Test widersprüchlicher TCP-Überlappung.
- **Z 83:** Erwartet eine Ausnahme bei abweichenden Werten an derselben Sequenzposition.
- **Z 84:** Legt mit `abc` und `X` an Position 11 einen Konflikt auf dem ursprünglichen `b` an.
- **Z 86:** Beginnt den Test einer fehlenden Sequenzposition.
- **Z 87:** Verlangt bei der Lücke einen `ValueError`.
- **Z 88:** Belegt Position 10 und 12, lässt 11 frei; bloßes Aneinanderhängen wäre hier falsch.
- **Z 90:** Beginnt den Test ohne Nutzsegmente.
- **Z 91:** Erwartet für eine leere Eingabeliste exakt leere Bytes.
- **Z 93:** Beginnt den Test eines ungültigen Dateiformats.
- **Z 94:** Dokumentiert, dass temporäre Dateien den Projekt-/Scratch-TMPDIR nutzen sollen, nicht ungefragt fremde Verzeichnisse.
- **Z 95:** Erstellt ein automatisch zu löschendes temporäres Verzeichnis gemäß der Umgebung.
- **Z 96:** Bestimmt darin den Pfad `bad.pcap`; die Endung macht den Inhalt noch nicht gültig.
- **Z 97:** Schreibt bewusst Textbytes statt einer PCAP-Datei als negative Testeingabe.
- **Z 98:** Erwartet beim tatsächlichen Lesen einen `ValueError`.
- **Z 99:** Materialisiert den Generator mit `list`; nur `records(path)` aufzurufen würde seine Validierung noch nicht ausführen.
- **Z 101:** Beginnt den Test einer am Ende abgeschnittenen Original-PCAP-Datei.
- **Z 102:** Liest die unveränderte Originaldatei als Vorlage; das Original wird nicht bearbeitet.
- **Z 103:** Legt für die beschädigte Kopie ein temporäres Verzeichnis an.
- **Z 104:** Wählt dort `cut.pcap` als Ausgabepfad.
- **Z 105:** Schreibt alle Originalbytes außer dem letzten. Der Paketheader kündigt weiterhin die ursprüngliche Länge an.
- **Z 106:** Erwartet deshalb einen `ValueError` bei der Recordverarbeitung.
- **Z 107:** Erzwingt wieder die vollständige Generatoriteration mit `list`.
- **Z 109:** Beginnt den positiven Test der Big-Endian-PCAP-Variante.
- **Z 110:** Erzeugt 14 feste Testbytes. Sie müssen für `records` keine semantisch gültigen Ethernet-Inhalte sein, weil dieser Test nur das Dateiformat liest.
- **Z 111:** Baut Magic Bytes und globalen Header in Big Endian mit Version 2.4, passender Aufzeichnungslänge und Ethernet-Linktyp.
- **Z 112:** Baut einen Record mit Sekunde 1, Mikrosekundenbruchteil 123 und übereinstimmender erfasster/ursprünglicher Länge.
- **Z 113:** Erzeugt dafür ein temporäres Verzeichnis.
- **Z 114:** Bestimmt den Pfad `big.pcap` darin.
- **Z 115:** Schreibt globalen Header und Record samt Paketbytes zusammen.
- **Z 116:** Prüft das vollständige Ausgabetupel einschließlich Zeitumrechnung auf 1_000_123_000 Nanosekunden.
- **Z 119:** Verhindert den direkten Testrunnerstart beim Import durch Test-Discovery.
- **Z 120:** Startet `unittest` beim direkten Aufruf dieser Datei.

**Was diese Tests nicht beweisen:** Sie prüfen ausgewählte Fehlerfälle und die Originalaufnahmen, nicht jeden Binärdecoderzweig. Es fehlen etwa eigene Fälle für Nanosekunden-Magic, Trailer, IPv4-Fragmente und komplexe TCP-Neuverwendung. Der Hierarchietest iteriert vorhandene Referenzzeilen; er prüft nicht separat, dass jede gewünschte Referenzzeile in der CSV vorhanden ist. Die gelesene Original-CSV enthält diese Zeilen tatsächlich. Diese Grenzen beeinträchtigen die unabhängig bestätigten Originalergebnisse nicht.

## 5. `ue2.12/bericht.py` – jede nichtleere Zeile

`sys.path` ist die Liste der Suchverzeichnisse für Python-Imports. Ein **f-String** ist eine Zeichenkette mit eingesetzten Ausdrücken in `{...}`. `zip` paart Einträge positionsweise und stoppt am kürzeren Eingang; deshalb ist die vorherige Längenprüfung wichtig. **Client** ist hier der mit initialem SYN aktive Verbindungsinitiator, **Server** sein Gegenüber; C→S/S→C bezeichnet die Richtungen.

- **Z 1:** KI-Kennzeichnung des Berichtscodes; keine Angabe über die HTTP-Clients.
- **Z 2:** Entstehungsdatum, nicht historische Serverzeit.
- **Z 3:** Dokumentiert die Berichtsinhalte und die Beschränkung auf Original-PCAPs.
- **Z 4:** Modul-Docstring: nur gespeicherte Daten, keine Netzabfragen. Das gilt für dieses Programm, nicht für separat im Review gelesene Fachquellen.
- **Z 5:** Importiert die Pfadklasse für robuste relative Projektpfade.
- **Z 6:** Importiert `sys`, um das benachbarte Analysemodul auffindbar zu machen.
- **Z 8:** Ermittelt `ueb02` aus dem absoluten Speicherort der Berichtsdatei; `parents[1]` ist zwei Ebenen über der Datei selbst.
- **Z 9:** Stellt `ue2.11` an den Anfang der Importsuche, damit das lokale `analyse.py` verwendet wird. Dies ist eine einfache Lösung für die Übungsstruktur, keine allgemeine Paketinstallation.
- **Z 10:** Importiert die bereits getestete Analysefunktion statt einen zweiten, möglicherweise abweichenden Parser zu duplizieren.
- **Z 13:** Definiert `report()` als Funktion, die Berichtstext zurückgibt und dadurch testbar bleibt.
- **Z 14:** Startet die Textzeilenliste mit Einheiten- und Zeitdefinition; „dezimal“ meint hier Byteangaben, nicht KiB-Umrechnung.
- **Z 15:** Legt die Reihenfolge der drei vorhandenen Aufnahmen fest; der persistente Dump ist ein Zusatzvergleich.
- **Z 16:** Analysiert jede Datei frisch aus `Angabe`; es werden keine fertigen JSON-Sollwerte als Messwerte vorgelesen.
- **Z 17:** Fügt eine Dateizeile mit Gesamtpaketen und TCP-Verbindungszahl an; das führende `\n` trennt Abschnitte optisch.
- **Z 18:** Durchläuft die in dieser Aufnahme gefundenen TCP-Verbindungen.
- **Z 19:** Gibt Stream-ID sowie Client- und Serverendpunkt aus, damit die folgenden Messwerte eindeutig zugeordnet sind.
- **Z 20:** Gibt komplette Ethernet-Frame-Bytes beider Richtungen und deren Summe aus; ACKs und andere Kontrollpakete bleiben enthalten.
- **Z 21:** Gibt separat IPv4-Bytes aus; diese lassen sich nicht mit HTTP-Bodygrößen gleichsetzen.
- **Z 22:** Gibt separat TCP-Nutzbytes aus; sie enthalten HTTP-Kopfdaten und gegebenenfalls Chunk-Framing zusätzlich zum Body.
- **Z 23:** Gibt die bereits definierte beobachtete Verbindungsdauer in Sekunden aus.
- **Z 24:** Holt Anfrage- und Antwortlisten in zwei lokale Namen; keine zusätzliche Auswertung verändert sie.
- **Z 25:** Prüft gleiche Listenlänge vor dem paarweisen Ausgeben; ein fehlender Partner soll nicht durch `zip` verborgen werden.
- **Z 26:** Bricht bei nicht paarbaren Listen mit einem verständlichen Fehler ab. Allgemeine Zuordnung beliebiger HTTP-Sonderfälle ist nicht implementiert.
- **Z 27:** Paart Anfragen und Antworten in ihrer Bytestromreihenfolge, wie es für diese Mitschnitte passt.
- **Z 28:** Zeigt die tatsächliche GET-Zeile und Statuszeile, nicht einen angenommenen internen Dateinamen.
- **Z 29:** Zeigt Antwort-Bodybytes und den tatsächlich übertragenen Content-Type. Ein fehlender Content-Type würde hier einen Schlüsselzugriffsfehler auslösen; in allen Originalantworten ist er vorhanden.
- **Z 30:** Verbindet alle Textzeilen mit Zeilenumbrüchen und liefert einen einzigen String; diese Funktion druckt selbst nichts.
- **Z 33:** Schützt den direkten Programmeinstieg gegen Ausführung beim Testimport.
- **Z 34:** Druckt den von `report()` gelieferten Text; `print` ergänzt den abschließenden Zeilenumbruch der Berichtsdatei.

## 6. `ue2.12/test_bericht.py` – jede nichtleere Zeile

- **Z 1:** Dokumentiert KI-Herkunft des Testcodes.
- **Z 2:** Dokumentiert dessen Entstehungsdatum.
- **Z 3:** Nennt Objekt-, Header-, Byte- und Persistenzprüfung als Arbeitsauftrag.
- **Z 4:** Importiert das Testframework.
- **Z 5:** Importiert Projektwurzel, Analysefunktion und Berichtsfunktion über das Berichtsmodul; dessen Importpfadlogik wird dabei mitbenutzt.
- **Z 8:** Definiert die Klasse der HTTP-bezogenen Testfälle.
- **Z 9:** Beginnt den Test der drei HTTP-Objekte.
- **Z 10:** Analysiert den unveränderten nichtpersistenten HTTP-Dump.
- **Z 11:** Erwartet drei TCP-Verbindungen statt einer Verbindung pro Richtung.
- **Z 12:** Erwartet 68 Frames in der ganzen Aufnahme.
- **Z 13:** Erwartet 37475 Frame-Bytes inklusive Kontrollverkehr und Headern.
- **Z 14:** Beginnt die erwartete Objektliste mit tatsächlichem HTML-Requestpfad, Bodylänge und Medientyp.
- **Z 15:** Ergänzt den GIF-Pfad mit seiner Länge und seinem Typ.
- **Z 16:** Ergänzt den PNG-Pfad mit unveränderter Groß-/Kleinschreibung und schließt die Sollwertliste.
- **Z 17:** Paart jeden Stream mit dem erwarteten Objekttripel. Die zuvor geprüfte Verbindungszahl schützt hier vor einem unbemerkten fehlenden Stream.
- **Z 18:** Vergleicht die erste Requestzeile mit dem exakten beobachteten Text, einschließlich HTTP-Version.
- **Z 19:** Holt die erste Antwort dieses Streams zur weiteren Prüfung.
- **Z 20:** Erwartet die Statuszeile `HTTP/1.1 200 OK`; die Antwortversion muss nicht mit der HTTP/1.0-Anfrageversion identisch sein.
- **Z 21:** Vergleicht die tatsächlich ausgeschnittene Bodylänge mit dem objektbezogenen Sollwert.
- **Z 22:** Vergleicht zusätzlich die angegebene Content-Length als Ganzzahl mit demselben Sollwert; bloß den Header zu glauben wäre schwächer.
- **Z 23:** Prüft den Medientyp für genau das betreffende Objekt.
- **Z 24:** Verlangt in jeder dieser Antworten `Connection: close`, passend zur beobachteten Nichtwiederverwendung.
- **Z 25:** Prüft Gleichheit einfacher und eindeutiger TCP-Nutzbytes; für diese Daten wurden also keine Nutzbytes durch identische Wiederholungen doppelt gezählt.
- **Z 27:** Beginnt den Test sämtlicher ausgewiesener Bytearten und der Dauern im HTTP-Dump.
- **Z 28:** Holt dafür die drei Streams in ihrer Aufbaureihenfolge.
- **Z 29:** Prüft die Frame-Summen je Verbindung gegen 1236, 5814 und 30425.
- **Z 30:** Prüft getrennt die kleineren IPv4-Summen; dies würde eine Verwechslung mit Ethernet-Längen erkennen.
- **Z 31:** Prüft jede Richtung der TCP-Nutzbytes statt nur eine gemeinsame Summe; Richtungsfehler werden sichtbar.
- **Z 32:** Prüft die exakt formatierten Dauerzeichenketten mit neun Nachkommastellen; das ist keine Behauptung von Nanosekundenmessauflösung.
- **Z 34:** Beginnt den Vergleich mit dem persistenten Zusatzdump.
- **Z 35:** Analysiert die drei nichtpersistenten Verbindungen als Referenz für die übertragenen Inhalte.
- **Z 36:** Analysiert den zusätzlichen persistenten Mitschnitt separat.
- **Z 37:** Verlangt darin genau eine TCP-Verbindung.
- **Z 38:** Holt diese einzige Verbindung.
- **Z 39:** Verlangt drei HTTP-Anfragen in dieser einen Verbindung, also Wiederverwendung statt „ein Request gleich eine Verbindung“.
- **Z 40:** Prüft die gesamte Frame-Bytesumme dieser Verbindung auf 36123.
- **Z 41:** Prüft deren beobachtete Dauer auf 0.704626000 Sekunden.
- **Z 42:** Baut die Liste der Body-SHA-256-Werte aus den drei nichtpersistenten Antworten.
- **Z 43:** Vergleicht die vollständige Liste der persistenten Antwortprüfsummen damit; gleiche Größen allein würden Bytegleichheit nicht hinreichend belegen.
- **Z 44:** Verlangt `Keep-Alive` in jeder persistenten Anfrage. `all` ist nur wahr, wenn jede erzeugte Bedingung wahr ist; die Zahl der Requests wurde vorher separat geprüft.
- **Z 46:** Beginnt den Test, ob der Textbericht ausführbar ist und wichtige Inhalte zeigt.
- **Z 47:** Ruft die echte Berichtsfunktion auf; kein erfundener Mustertext wird eingesetzt.
- **Z 48:** Prüft die Dateizeile für 68 Pakete und drei Verbindungen als zusammenhängenden Text.
- **Z 49:** Prüft, dass der große PNG-Body mit Größe und Medientyp im Bericht vorkommt.
- **Z 50:** Prüft, dass TCP-Nutzbytes ausdrücklich benannt werden; ein Bericht nur mit unklaren „Bytes“ soll nicht genügen.
- **Z 53:** Startschutz für direkten Aufruf statt Import durch Test-Discovery.
- **Z 54:** Startet den Testrunner, wenn diese Datei selbst ausgeführt wird.

## 7. `ue2.11/hierarchie.dot` – jede Zeile

**DOT** ist die Beschreibungssprache von Graphviz für Graphen. Ein **Knoten** ist hier ein beschrifteter Kasten; eine **gerichtete Kante** `a -> b` ist ein Pfeil. `digraph` definiert einen gerichteten Graphen. **Kapselung** bedeutet, dass die Einheit eines Protokolls in einer anderen Einheit transportiert wird; ein Pfeil ist hier keine zusätzliche Schichtgrenze. Die Schichtnamen im Knoten beschreiben die funktionale Zuordnung zum vierstufigen TCP/IP-Modell.

- **Z 1:** `//` leitet den KI-Herkunftskommentar mit Modell und Datum ein; Graphviz zeichnet ihn nicht.
- **Z 2:** Dokumentiert als zweiten Kommentar den Auftrag und den Bezug zur tatsächlich beobachteten Aufnahme.
- **Z 3:** Öffnet den gerichteten Graphen mit dem internen Namen `Protokolle`; die geschweifte Klammer beginnt seinen Inhalt.
- **Z 4:** Setzt globale Grafikattribute: `rankdir=TB` ordnet von oben nach unten, `bgcolor` den weißen Hintergrund; `label` und `labelloc=t` setzen den Titel oben.
- **Z 5:** Definiert Standardattribute aller folgenden Knoten: Kästen, gerundete und gefüllte Darstellung, helle Füllfarbe und Schrift. Diese Attribute ändern keine Protokollzahlen.
- **Z 6:** Setzt die Standardfarbe der Pfeile; ebenfalls reine Darstellung.
- **Z 7:** Definiert den Knoten `ethernet` mit 39 Frames und Schicht Netzzugang. `\n` erzeugt einen Zeilenumbruch innerhalb der Beschriftung.
- **Z 8:** Definiert ARP mit zehn Frames ebenfalls auf der Netzzugangsschicht; es wird nicht fälschlich unter UDP oder IPv4 eingeordnet.
- **Z 9:** Definiert IPv4 mit 29 Frames und funktionaler Internetschicht.
- **Z 10:** Definiert ICMP mit vier Frames und ebenfalls Internetschicht; Kapselung unter IPv4 macht es nicht zum Transportprotokoll.
- **Z 11:** Definiert UDP mit neun Frames und Transportschicht.
- **Z 12:** Definiert TCP mit 16 Frames, aber nur einer Verbindung; Paket- und Verbindungszahl werden bewusst getrennt.
- **Z 13:** Definiert DHCP mit drei Frames und Anwendungsschicht; der Hinweis BOOTP-Format benennt das verwendete Nachrichtenformat, keinen zusätzlich gezählten Austausch.
- **Z 14:** Definiert DNS mit sechs Frames und Anwendungsschicht.
- **Z 15:** Definiert HTTP mit zwei GUI-Zuordnungen und Anwendungsschicht; nicht sechs Segmente mit HTTP-Teilbytes als sechs Nachrichten fehlzählen.
- **Z 16:** Definiert den anders gefärbten Inhaltsknoten für eine HTML/Text-Zuordnung. Die Beschriftung warnt ausdrücklich: kein eigenständiges weiteres Netzwerkprotokoll.
- **Z 17:** Zeichnet Ethernet→ARP, weil ARP direkt durch Ethernet transportiert wird.
- **Z 18:** Zeichnet Ethernet→IPv4 als zweiten tatsächlich beobachteten Ethernet-Zweig.
- **Z 19:** Zeichnet IPv4→ICMP; zeigt Kapselung trotz gleicher funktionaler Schicht.
- **Z 20:** Zeichnet IPv4→UDP; darin folgen die beobachteten UDP-Anwendungen.
- **Z 21:** Zeichnet IPv4→TCP für den anderen Transportzweig.
- **Z 22:** Zeichnet UDP→DHCP; keine direkte IP→DHCP-Kante, da UDP dazwischenliegt.
- **Z 23:** Zeichnet UDP→DNS; für diese Aufnahme ist kein DNS über TCP nachgewiesen.
- **Z 24:** Zeichnet TCP→HTTP; TLS wird mangels Nachweis nicht hinzugefügt.
- **Z 25:** Zeichnet HTTP→Textinhalt; das ist ein Inhaltszweig, keine fünfte TCP/IP-Schicht.
- **Z 26:** Schließt den Graphen. Ohne diese Klammer wäre die DOT-Datei syntaktisch unvollständig.

Das grafische Ziel entsteht normalerweise durch `dot -Tsvg ue2.11/hierarchie.dot -o ue2.11/hierarchie.svg`. **SVG** ist ein skalierbares Vektorgrafikformat. Weil diese Prüfung nur ihre eigene neue Erklärungsdatei im Produktordner schreiben darf, ist dieser Befehl hier eine Übergabe an den Hauptbearbeiter und keine Behauptung, die fehlende Produktgrafik bereits geschrieben zu haben.

## 8. Änderungen live verstehen und üben

Diese Übungen nur in einer **eigenen Kopie unter dem aktiven Scratch-Verzeichnis** durchführen, nicht in Original-PCAPs, GUI-Nachweisen oder fremden Produktdateien. Zuerst den unveränderten Stand mit den beiden Testbefehlen aus Abschnitt 1 ausführen. Dann je Versuch genau eine Änderung machen, den gezielten Test ausführen, die Fehlermeldung erklären und die Kopie zurücksetzen. Die folgenden Varianten sind Lernaufgaben, keine zusätzlich behaupteten ausgeführten Produkttests.

1. **Padding-Falle sichtbar machen.** In einer Kopie von `analyse.py`, Z 126, `ip[ihl:total]` absichtlich durch `ip[ihl:]` ersetzen. Den Test `test_padding_not_tcp_payload` gezielt ausführen: `python3 -B -m unittest test_analyse.AnalysisTests.test_padding_not_tcp_payload -v` im kopierten Analyseordner. Erwartung: Die bisher korrekte Trennung der zwölf TCP-angehängten Füllbytes geht verloren; Nutzbytes beziehungsweise HTTP-Verarbeitung stimmen nicht mehr. Warum nicht einfach die Sollwerte erhöhen? Weil das die Messdefinition beschädigen würde.
2. **Header und Body trennen.** Z 72 beobachten: Was passiert ohne `+ 4`? Die Trennbytes bleiben vor dem Body; Bodylänge/Hash oder Folgemeldung werden falsch. `test_chunked_body` und `test_persistent_http` sind geeignete kleine Fälle. Der Grund ist die exklusive Slice-Grenze und die Länge des HTTP-Headerabschlusses, nicht ein beliebiger „Offset-Trick“.
3. **Hexadezimale Chunklänge.** Im isolierten Chunked-Test ein Stück mit Größenzeile `a` und zehn Inhaltsbytes verwenden. Z 77 muss Basis 16 nutzen. Ein Wechsel auf Basis 10 würde diesen gültigen Größenwert nicht lesen. Vor dem Test die angekündigte Länge gegen die tatsächlichen Bytes prüfen.
4. **Retransmission nicht doppelt zählen.** Im Fall aus Z 80 von `test_analyse.py` ein identisches Segment erneut hinzufügen: Ergebnis bleibt `abcd`. Dann ein überlappendes Byte ändern: Der Konflikttest muss abbrechen. So unterscheidet man einfache Summen in Z 162 von eindeutigen Bytes in Z 171.
5. **Lücken nicht verstecken.** Das Beispiel aus Z 88 mit Position 10 und 12 ausführen; danach ein Segment für Position 11 ergänzen. Erst die vollständige Folge darf erfolgreich zusammengesetzt werden. Reihenfolge der Eingabeliste vertauschen: Die Ausgabe muss trotzdem nach Sequenzpositionen geordnet sein.
6. **Zeitauflösung und Formatierung.** In einer Kopie Z 172 nur die Zahl der ausgegebenen Nachkommastellen ändern. `test_all_byte_metrics` schlägt wegen der erwarteten Zeichenketten fehl, obwohl die zugrunde liegende Zeitdifferenz nicht geändert wurde. Daraus folgt: Ausgabeformat, Messauflösung und mathematischer Zeitabstand sind verschiedene Eigenschaften. Mikrosekundenstempel werden durch neun Dezimalstellen nicht genauer.
7. **Richtung kontrollieren.** In Z 157 die Indizes absichtlich vertauschen und `test_gui_conversations` ausführen. Eine gemeinsame Bytesumme kann weiter passen; getrennte Richtungsspalten müssen den Fehler aufdecken. Deshalb prüft der Test nicht bloß Gesamtsummen.
8. **`zip`-Abkürzung verstehen.** In einer eigenständigen kleinen Testkopie eine Antwortliste künstlich verkürzen. Die Längenprüfung in `bericht.py` Z 25/26 muss vor der Schleife abbrechen. Nur über die Paare zu laufen würde die fehlende Antwort still verlieren.
9. **Unterstützungsgrenze korrekt erweitern.** Nicht einfach IPv6 oder VLAN am Fehlerzweig vorbeileiten. Zuerst ein eigenes geeignetes Test-PCAP und Sollwerte festlegen, dann Ethernet-/IP-Offsets und Transportdecoder tatsächlich implementieren. Dieselben IPv4-Offsets auf andere Kapselungen anzuwenden liefert keine verlässliche Erweiterung.
10. **Grafik ohne neue Protokollbehauptung ändern.** In einer DOT-Kopie nur `rankdir=TB` auf `LR` ändern und im Scratch rendern. Die Richtung wechselt zu links→rechts; Knotenzahlen und Kanten bleiben gleich. Eine zusätzliche DNS→TCP-Kante wäre dagegen keine Stiländerung, sondern eine unbelegte Aussage über diese Aufnahme.

### Für eine mündliche Erklärung

- Warum sind 68 TCP-Pakete nicht 68 HTTP-Nachrichten? TCP transportiert einen Bytestrom; Segmentierung und Kontrollpakete sind unabhängig von HTTP-Nachrichtengrenzen.
- Warum stehen HTTP-Feldnamen im JSON klein? Feldnamen sind nicht groß-/kleinschreibungssensitiv; Pfade und Feldwerte werden dadurch nicht beliebig normalisierbar.
- Warum kann ARP neben IPv4 im Baum stehen? ARP wird direkt in Ethernet gekapselt, nicht durch IPv4 transportiert.
- Warum ist die TCP-Dauer keine reine Downloadzeit? Hier wird der erste bis letzte beobachtete TCP-Zeitstempel inklusive Aufbau/Abbau verwendet.
- Warum genügt die Content-Length allein nicht? Sie ist eine übertragene Behauptung; erst das tatsächliche Ausschneiden und Prüfen der vorhandenen Bytes bestätigt den vollständigen Body.
- Warum kein allgemeiner Wireshark-Ersatz? Der kleine Code hat einen absichtlich engen Datenvertrag, keine universellen Decoder und keinen vollständigen TCP-/HTTP-Zustandsautomaten.

## 9. Quellen und Nachweise

- Originalblatt `angabe_blatt02.pdf`, Seite 2, Aufgaben 2.11 und 2.12.
- Unveränderte Originalaufnahmen `Angabe/dump_protocols.pcap`, `dump_http.pcap`, `dump_http_persistent.pcap`.
- `ue2.10/gui_protocol_hierarchy_protocols.csv`, `gui_protocol_hierarchy_http.csv`, `gui_tcp_conversations_protocols.csv`, `gui_tcp_conversations_http.csv` und die jeweils gleichnamigen PNG-Screenshots; Durchführung beschrieben in `gui_kontrolle.md`.
- RFC 1122 für die funktionale Schichtzuordnung; RFC 9110 für HTTP-Feldsemantik; RFC 9112 für HTTP/1.x-Framing und Verbindungsmanagement. Quellenadressen und Feldabschnitte stehen in den geprüften Antworten: https://www.rfc-editor.org/rfc/rfc9110 und https://www.rfc-editor.org/rfc/rfc9112 .
- Apache-2.2-Quelle für den historischen `X-Pad`-Zusatz: https://github.com/apache/httpd/blob/2.2.x/modules/http/http_filters.c , Funktion `terminate_header()`.

Die AppArmor-Beschränkung für `tshark` wurde weder verändert noch umgangen. Die Prüfung benötigt kein `tshark`: vorhandene echte GUI-Nachweise und die unabhängige Scapy-/HTTPResponse-Auswertung reichen für die hier bestätigten Aussagen.
