# Ü 2.12 – Wireshark: HTTP(S)

## Angabe und Vorgehen

Die Originaldatei `dump_http.pcap` analysieren: angeforderte Objekte, Header-Felder, TCP-Verbindungszahl im Vergleich zu `dump_protocols.pcap`, Bytes und Dauer jeder Verbindung.

Die Original-PCAPs liegen unverändert unter `../Angabe/`. Auswertung mit tatsächlicher Wireshark-GUI 4.4.5, unabhängige Neuberechnung aus PCAP-, Ethernet-, IPv4- und TCP-Feldern mit Python-Standardbibliothek. Die GUI-CSV-Exporte liegen unter `../ue2.10/`, Rechenergebnisse unter `analyse_http.json` und `messbericht.txt`. Der Titel erwähnt HTTPS, die konkrete Aufnahme enthält jedoch **unverschlüsseltes HTTP auf TCP-Port 80, kein TLS**. Es wurde nichts entschlüsselt.

## 1. Welche Objekte werden angefordert?

Client `192.168.3.10`, Server `192.168.1.10:80`. Tatsächlich beobachtete Requests:

- `GET /test/ HTTP/1.0` → `http://192.168.1.10/test/`; Antwort `HTTP/1.1 200 OK`, `Content-Type: text/html`, **145 Body-Bytes**. Die HTML-Seite enthält den Titel „Test“, eine Überschrift „Welcome“ und zwei relative Bildreferenzen.
- `GET /test/logo.gif HTTP/1.0` → `http://192.168.1.10/test/logo.gif`; Antwort `HTTP/1.1 200 OK`, `image/gif`, **4445 Body-Bytes**.
- `GET /test/TechnikErleben.png HTTP/1.0` → `http://192.168.1.10/test/TechnikErleben.png`; Antwort `HTTP/1.1 200 OK`, `image/png`, **27065 Body-Bytes**. Groß-/Kleinschreibung des Pfads wird beibehalten.

`/test/` ist der beobachtete Ressourcenpfad. Die Aufnahme belegt **nicht**, welche Datei der Server intern dafür auswählt; ein Dateiname wie `index.html` wäre eine Vermutung. Auch ein Favicon wurde in dieser Aufnahme nicht angefordert.

## 2. Header-Felder: tatsächliche Werte und Bedeutung

Feldnamen sind nicht groß-/kleinschreibungssensitiv; der Parser normalisiert sie nur im JSON. Request-/Statuszeile gehören **nicht** zu den Header-Feldern. Die historische Aufnahme stammt von 2011; Softwareversionen und Zeitstempel beschreiben den damaligen Mitschnitt, nicht die aktuelle Umgebung.

### Anfrage

- **User-Agent:** `Mozilla/5.0 (X11; Linux i686; rv:6.0.2) Gecko/20100101 Firefox/6.0.2`. Selbstbeschreibung des Clients; nicht als vertrauenswürdiger Identitätsnachweis geeignet. RFC 9110 §10.1.5.
- **Accept:** `*/*`. Der Client signalisiert, dass alle Medientypen akzeptabel sind; es bezeichnet nicht den gesendeten Typ. RFC 9110 §12.5.1.
- **Host:** `192.168.1.10`. Zielhost der Ressource; ermöglicht etwa virtuelle Hosts auch auf einer gemeinsamen IP. Obwohl die Requests hier HTTP/1.0 verwenden, wird dieses Feld mitgesendet. RFC 9110 §7.2.

### Antwort

- **Date:** `Thu, 15 Sep 2011 12:32:08 GMT` bei HTML/GIF, `Thu, 15 Sep 2011 12:32:09 GMT` bei PNG. Zeitpunkt der Nachrichtenerzeugung nach Serveruhr, nicht das Dateierstellungsdatum und nicht die gemessene Verbindungsdauer. RFC 9110 §6.6.1.
- **Server:** `Apache/2.2.14 (Ubuntu)`. Selbstbeschreibung der Serversoftware; kein Beweis für unveränderte tatsächliche Installation. RFC 9110 §10.2.4.
- **Last-Modified:** HTML `Thu, 15 Sep 2011 11:58:32 GMT`; GIF `Thu, 01 Sep 2011 09:32:12 GMT`; PNG `Sun, 27 Mar 2011 21:01:39 GMT`. Vom Server angegebener letzter Änderungszeitpunkt der Repräsentation, etwa zur bedingten Cache-Validierung. RFC 9110 §8.8.2.
- **ETag:** HTML `"720063-91-4acf9987eb65e"`, GIF `"72004d-115d-4abddeb617f00"`, PNG `"72005d-69b9-49f7d221e92c0"`. Opaker Versionsvalidator der gewählten Repräsentation. Ohne `W/` als stark gekennzeichnet; nicht automatisch ein kryptographischer Hash und nicht als Dateipfad interpretieren. RFC 9110 §8.8.3.
- **Accept-Ranges:** `bytes`. Der Server signalisiert Unterstützung für Bereichsanfragen in Byte-Einheiten. Die drei hier beobachteten Requests verwenden **kein** `Range`; das Feld beweist also keinen Teilabruf. RFC 9110 §14.3.
- **Content-Length:** `145`, `4445`, `27065`. Jeweilige Länge des HTTP-Nachrichteninhalts in Bytes; bei diesen Antworten ohne Transfer-/Content-Coding genau die übertragenen HTML-/Bildbytes. HTTP-Header, TCP-/IP-/Ethernet-Header sind **nicht** enthalten. RFC 9110 §8.6 und RFC 9112 §6.2.
- **Vary:** `Accept-Encoding`, nur bei HTML. Die Auswahl der Repräsentation kann vom gleichnamigen Request-Feld abhängen; Caches müssen dies berücksichtigen. Es besagt **nicht**, dass dieser Body tatsächlich gzip-komprimiert ist; ein `Content-Encoding`-Feld fehlt hier. RFC 9110 §12.5.5.
- **Connection:** `close` in allen drei Antworten. Der Sender kündigt Schließen der aktuellen Verbindung nach der Antwort an; deshalb wird diese hier nicht für das nächste Objekt wiederverwendet. Hop-by-hop-Feld, kein dauerhaftes Attribut der Ressource. RFC 9110 §7.6.1, RFC 9112 §9.3.
- **Content-Type:** `text/html`, `image/gif`, `image/png`. Medientyp zur Interpretation der jeweiligen Repräsentation. Keine Längenangabe und keine Transportprotokollauswahl. RFC 9110 §8.3.
- **X-Pad:** `avoid browser bug`, in GIF-/PNG-Antworten. Historisches Apache-Padding, um einen Header-Parsingfehler alter Netscape-Navigator-Versionen zu vermeiden; kein standardisiertes semantisches HTTP-Steuerfeld. Der Apache-2.2-Quelltext `terminate_header()` fügt es bei bestimmten Headerlängen ein. Es gehört zum HTTP-Header, **nicht** zum GIF-/PNG-Inhalt.

**Zusätzliche Vergleichsfelder:** In `dump_protocols.pcap` lautet die Anfrage `Connection: Keep-Alive`, die Antwort trotzdem `Connection: close`; außerdem `Transfer-Encoding: chunked`. Chunked ist HTTP-Nachrichtenframing mit hexadezimalen Chunk-Längen, keine Kompression. Im freiwillig mitanalysierten `dump_http_persistent.pcap` kommen `Connection: Keep-Alive` und antwortseitig `Keep-Alive: timeout=15, max=100` beziehungsweise `max=99`, `max=98` vor. Das sind historische Angaben zu Wiederverwendung/Timeout, keine Zusage endloser Offenhaltung. Kein HTTP/2- oder HTTP/3-Verkehr.

## 3. Wie viele TCP-Verbindungen?

- **dump_http.pcap: drei Verbindungen.** Quellports **37184, 37185, 37186**, jeweils zu `192.168.1.10:80`. Jeweils ein aufgezeichneter Dreiwege-Handshake und ein HTTP-Objekt. Die Requests sind HTTP/1.0, der Server antwortet mit HTTP/1.1 und `Connection: close`. Die Verbindungen sind nicht rein zeitlich disjunkt: Der nächste Aufbau beginnt jeweils, während das letzte ACK des vorherigen Abbaus noch aussteht.
- **dump_protocols.pcap: eine Verbindung.** `192.168.1.215:54961 ↔ 192.168.1.1:80`, ein HTTP/1.1-Request `GET /` und eine chunked HTTP/1.1-Antwort. Kein Beispiel für mehrere Objekte auf einer persistenten Verbindung: Trotz Wunsch `Keep-Alive` schließt der Server.
- **Zusatz: dump_http_persistent.pcap: eine Verbindung**, Quellport **50776**, aber **drei Requests und drei Antworten mit denselben drei Bodies**. Keep-Alive-Erweiterung trotz HTTP/1.0-Requestzeilen; damit lässt sich der Nutzen der Wiederverwendung direkt am mitgelieferten Vergleichsmitschnitt zeigen. SHA-256 der reassemblierten Bodies bestätigt Bytegleichheit zu den drei Bodies des nichtpersistenten Dumps.

Gezählt werden TCP-Verbindungen anhand Endpunktpaar und initialem SYN, nicht HTTP-Requests, TCP-Segmente oder bloß verschiedene Portnummern ohne Kontext. Ein SYN-Retry mit derselben Sequenznummer wäre keine neue Verbindung.

## 4. Bytes und Dauer pro Verbindung

**Messdefinitionen:**

- **Frame-Bytes:** Summe der aufgezeichneten ursprünglichen Ethernet-Frame-Längen in beiden Richtungen, einschließlich ACK-/SYN-/FIN-Paketen, Headern und vorhandenem Padding. Entspricht hier **Statistics → Conversations → TCP → Bytes**. Nicht PCAP-Dateigröße, keine PCAP-Recordheader, kein Preamble/Inter-Frame-Gap; eine nicht aufgezeichnete FCS wird nicht hinzugezählt.
- **IPv4-Bytes:** Summe der IPv4-Gesamtlängen einschließlich IP-/TCP-Headern, ohne Ethernet-Header/-Padding.
- **TCP-Nutzbytes:** Summe `IPv4 total length − IPv4 header length − TCP header length`. Enthält HTTP-Header **und** HTTP-Inhalt. Bei Retransmissions würde die einfache Summe Wiederholungen mitzählen; die zusätzlich sequenzbasiert berechneten eindeutigen Nutzbytes stimmen in diesen Dumps mit der Summe überein.
- **HTTP-Body:** Nur die übertragenen HTML-/Bilddaten; oben separat angegeben.
- **Dauer:** Zeitstempel des letzten beobachteten TCP-Pakets minus Zeitstempel des ersten Pakets, hier initiales SYN bis letztes ACK. Kein RTT-Messwert, keine reine HTTP-Downloadzeit und keine Aussage über Pakete außerhalb der Aufnahme. Zeiten unten in Sekunden, neun Stellen im JSON; die Originaldumps haben Mikrosekundenauflösung.

### Stream 0 – HTML, Clientport 37184

- Pakete: **10**, davon 5 je Richtung.
- Frame-Bytes Client→Server **476**, Server→Client **760**, insgesamt **1236 B**.
- IPv4-Bytes **1096 B**.
- TCP-Nutzbytes **138 + 422 = 560 B**; die 422 Serverbytes enthalten **145 B HTML**.
- Erstes Paket **1316089928.530874**, letztes Paket **1316089928.832173** als Unixzeit.
- Dauer: **0.301299 s**.

### Stream 1 – GIF, Clientport 37185

- Pakete: **14**, davon 7 je Richtung.
- Frame-Bytes Client→Server **616**, Server→Client **5198**, insgesamt **5814 B**.
- IPv4-Bytes **5618 B**.
- TCP-Nutzbytes **146 + 4728 = 4874 B**; darin **4445 B GIF**.
- Erstes Paket **1316089928.732406**, letztes Paket **1316089929.033654**.
- Dauer: **0.301248 s**.

### Stream 2 – PNG, Clientport 37186

- Pakete: **44**, davon 22 je Richtung.
- Frame-Bytes Client→Server **1616**, Server→Client **28809**, insgesamt **30425 B**.
- IPv4-Bytes **29809 B**.
- TCP-Nutzbytes **156 + 27349 = 27505 B**; darin **27065 B PNG**.
- Erstes Paket **1316089928.933670**, letztes Paket **1316089929.435864**.
- Dauer: **0.502194 s**.

**Kontrolle:** Die drei Verbindungen umfassen alle **68 Frames und 37475 Frame-Bytes** des HTTP-Dumps. Die PCAP-Datei selbst ist größer, weil sie zusätzlich einen globalen Header und einen Recordheader pro Frame enthält. Alle oben verwendeten Summen und Differenzen wurden programmgesteuert nachgerechnet; siehe `messbericht.txt`, JSON und Tests.

### Vergleichswerte der anderen Dumps

- `dump_protocols.pcap`, einzige TCP-Verbindung: **16 Pakete**, **1763 Frame-Bytes** (567/1196 je Richtung), **855 TCP-Nutzbytes** (115/740), Dauer **0.007399 s**. Die gesamte Datei enthält zusätzlich ARP, DHCP, DNS und ICMP und darf nicht komplett als TCP-Bytes gezählt werden.
- `dump_http_persistent.pcap`, einzige TCP-Verbindung: **46 Pakete**, **36123 Frame-Bytes**, **33071 TCP-Nutzbytes**, Dauer **0.704626 s**, drei HTTP-Objekte. Dieser zusätzliche Mitschnitt ersetzt nicht den ausdrücklich verlangten Vergleich mit `dump_protocols.pcap`.

## Reproduzieren

Aus `ueb02/`:

```bash
python3 -B ue2.12/bericht.py
python3 -B ue2.11/analyse.py Angabe/dump_http.pcap
python3 -B -m unittest discover -s ue2.11 -p 'test_*.py' -v
python3 -B -m unittest discover -s ue2.12 -p 'test_*.py' -v
wireshark -r Angabe/dump_http.pcap
```

In Wireshark:

1. Anzeige `http.request`: die drei tatsächlichen Requestpfade ablesen.
2. HTTP-Zweig einer Anfrage/Antwort aufklappen; bei segmentierten Antworten TCP-Reassembly beachten. **Follow → TCP Stream** zeigt den zusammengesetzten Bytestrom.
3. **Statistics → Conversations → TCP** zeigt Verbindungszahl, Richtungsbytes und Dauer. Die mitgelieferten CSV-Dateien sind echte GUI-Exporte.
4. `tcp.flags.syn == 1 && tcp.flags.ack == 0` zeigt die initialen SYNs; `tcp.stream == 0`, `1`, `2` trennt Verbindungen. HTTP-Bodylänge nicht mit „Bytes“ der Conversations-Ansicht verwechseln.
5. **File → Export Objects → HTTP** erlaubt die drei Objekte separat zu speichern; fremde Inhalte nicht ausführen. Hier genügt die Offlineanalyse.

## Quellen

- Moodle-Original-PCAPs und daraus erzeugte JSON-/GUI-CSV-Ergebnisse im Repo.
- RFC 9110 mit den oben angegebenen Feldabschnitten: https://www.rfc-editor.org/rfc/rfc9110
- RFC 9112 §§6, 7.1, 9.3 und Appendix C.2.2: https://www.rfc-editor.org/rfc/rfc9112
- Apache-2.2-Quelltext, Funktion `terminate_header()`: https://github.com/apache/httpd/blob/2.2.x/modules/http/http_filters.c
- Wireshark Conversations: https://www.wireshark.org/docs/wsug_html_chunked/ChStatConversations.html

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, Datum **2026-10-19**. Anfrage sinngemäß: „Analysiere die originalen HTTP-PCAPs, recherchiere alle vorkommenden Header und verifiziere Objekte, TCP-Verbindungszahl, Bytearten und Dauern gegen Wireshark.“ Keine persönliche Eigenleistung des Studierenden wird behauptet.
