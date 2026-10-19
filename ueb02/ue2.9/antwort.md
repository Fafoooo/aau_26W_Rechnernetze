# Ü 2.9 – HTTP, E-Mail-Protokolle und DNS

**Aufgabe:** Anhand der IETF-RFCs HTTP/0.9, HTTP/1.0, HTTP/1.1, HTTP/2 und HTTP/3 vergleichen, SMTP/POP3/IMAP mit konkretem SMTP-Beispiel beschreiben und DNS erklären.

## 1. HTTP – gemeinsame Grundidee

**Hypertext Transfer Protocol** ist ein zustandsloses Anwendungsprotokoll nach dem Anfrage-/Antwortprinzip. Ein Client adressiert eine Ressource mit einer URI und einer Methode; der Server antwortet mit einem Status und gegebenenfalls einer Repräsentation. Zustandslos bedeutet nicht, dass Webseiten keine Anmeldung kennen: Anwendungen können Zustand über Cookies, Token und serverseitige Sitzungen hinzufügen. Die modernen HTTP-Versionen teilen weitgehend dieselbe Semantik für Ressourcen, Methoden, Statuscodes und Felder; hauptsächlich ändern sich Nachrichtenformat und Transport. [RFC 9110, §§ 1, 3 und 6](https://www.rfc-editor.org/rfc/rfc9110#section-1)

### HTTP/0.9 – sehr einfaches historisches Format

HTTP/0.9 hat **keinen eigenen späteren HTTP/0.9-RFC**. RFC 1945 beschreibt das ursprüngliche Verfahren rückblickend als **Simple-Request/Simple-Response**:

```text
GET /index.html\r\n
```

Die Anfrage enthält nur `GET` und den Pfad, **keine Versionsangabe und keine Header**. Die Antwort enthält ausschließlich den Dokumentinhalt, **keine Statuszeile und keine Antwortheader**. Der Inhalt ist deshalb nicht ausdrücklich mit `Content-Type` gekennzeichnet; historisch ging es um HTML. Das Verbindungsende begrenzt die Antwort. Fehler können nur als Inhalt, nicht als numerischer HTTP-Status dargestellt werden. `HTTP/0.9` ist also eine nachträgliche Versionsbezeichnung, nicht der Text dieser Anfragezeile. [RFC 1945, §§ 1, 4.1 und 6.1](https://www.rfc-editor.org/rfc/rfc1945#section-4.1)

### HTTP/1.0 – Status, Header und verschiedene Inhalte

HTTP/1.0 führt vollständige textuelle Anfragen/Antworten ein: Methode, Ziel und Versionskennung, Header, Leerzeile und gegebenenfalls einen Body. Die Antwort beginnt beispielsweise mit `HTTP/1.0 200 OK`. `Content-Type` beschreibt den Medientyp; dadurch lassen sich außer HTML auch andere Inhalte übertragen. RFC 1945 definiert insbesondere **GET, HEAD und POST**. [RFC 1945, §§ 4–8 und 10.5](https://www.rfc-editor.org/rfc/rfc1945#section-4)

Im ursprünglichen Modell wird die TCP-Verbindung nach der Antwort geschlossen; mehrere Objekte können dadurch mehrere Verbindungsaufbauten benötigen. **Persistente Verbindungen waren nicht der Standard**, existierten aber als `Keep-Alive`-Erweiterung. Die Aussage „HTTP/1.0 kann grundsätzlich nie eine Verbindung wiederverwenden“ wäre daher falsch. [RFC 1945, § 1.3](https://www.rfc-editor.org/rfc/rfc1945#section-1.3), [RFC 9112, § 9.3 und Anhang C.2.2](https://www.rfc-editor.org/rfc/rfc9112#section-9.3)

### HTTP/1.1 – persistente Verbindungen und besseres Framing

Für HTTP/1.1 sind heute insbesondere **RFC 9110 (Semantik), RFC 9111 (Caching) und RFC 9112 (Nachrichten/Verbindungen)** maßgeblich; die oft zitierten RFCs 2616 beziehungsweise 7230 ff. gehören zur Spezifikationsgeschichte. [RFC 9112, § 1](https://www.rfc-editor.org/rfc/rfc9112#section-1)

Wesentliche Merkmale gegenüber HTTP/1.0:

- **Persistente Verbindungen sind Standard:** Mehrere Anfragen und Antworten können dieselbe TCP-Verbindung nutzen; `Connection: close` kündigt das Ende an.
- **`Host` ist in HTTP/1.1-Anfragen verpflichtend.** Dadurch kann der Server unter derselben IP verschiedene Zielhosts unterscheiden.
- **Chunked Transfer Coding** erlaubt einen korrekt abgegrenzten Body, dessen Gesamtlänge vorab unbekannt ist. Das ist eine HTTP/1.1-Übertragungscodierung und nicht dasselbe wie adaptive Videosegmente.
- **Pipelining** ist möglich: Der Client kann mehrere Anfragen senden, ohne alle Antworten abzuwarten. Die Antworten müssen aber in Anfragereihenfolge übertragen werden. Eine langsame erste Antwort kann folgende Antworten blockieren: **Head-of-Line Blocking auf HTTP-Ebene**.
- Die Semantik umfasst unter anderem Cachevalidierung und Bereichsanfragen, etwa `Range`; die Versionsunterschiede dürfen nicht auf die Anzahl der Methoden reduziert werden.

[RFC 9112, §§ 3.2, 7.1, 9.3 und 9.3.2](https://www.rfc-editor.org/rfc/rfc9112#section-3.2), [RFC 9110, §§ 13–14](https://www.rfc-editor.org/rfc/rfc9110#section-13)

### HTTP/2 – binäre Frames und Multiplexing über TCP

Die standardisierte Bezeichnung lautet **HTTP/2**, nicht üblicherweise „HTTP/2.0“. **RFC 9113** ersetzt RFC 7540. HTTP/2 überträgt dieselbe grundlegende HTTP-Semantik als **binäre Frames**, beispielsweise `HEADERS` und `DATA`, statt als HTTP/1.1-Textnachrichten. Mehrere Anfragen/Antworten besitzen eigene **Streams**, deren Frames sich auf einer TCP-Verbindung verschachteln können. [RFC 9113, §§ 1–2, 4–5 und 8](https://www.rfc-editor.org/rfc/rfc9113#section-2)

Weitere Merkmale sind **HPACK-Headerkompression**, Flusskontrolle für Streams und Verbindung sowie spezifiziertes, optionales Server Push. Ob ein bestimmter Browser Server Push tatsächlich nutzt, folgt daraus nicht. HTTP/2 verwendet kein HTTP/1.1-Chunked-Framing. In der Webpraxis wird es typischerweise über TLS ausgehandelt; die Spezifikation beschreibt auch nicht verschlüsselte Verbindungen. **HTTP/2 bedeutet nicht automatisch Verschlüsselung.** [RFC 9113, §§ 3, 4.3, 5.2, 8.1 und 8.4](https://www.rfc-editor.org/rfc/rfc9113#section-3)

Die Grenze: Alle Streams teilen weiterhin **einen geordneten TCP-Bytestrom**. Fehlt ein TCP-Segment, kann TCP spätere Bytes vorübergehend nicht an HTTP/2 übergeben; dadurch können auch andere Streams warten. Das HTTP/1.1-Antwortreihenfolgeproblem wird weitgehend beseitigt, **TCP-bedingtes Head-of-Line Blocking bleibt**. [RFC 9114, § 1.1](https://www.rfc-editor.org/rfc/rfc9114#section-1.1)

### HTTP/3 – HTTP-Semantik über QUIC statt TCP

**HTTP/3**, spezifiziert in **RFC 9114**, verwendet **QUIC** über UDP. QUIC liefert selbst zuverlässige, geordnete Übertragung **innerhalb eines Streams**, Multiplexing, Fluss-/Überlaststeuerung sowie integrierte **TLS-1.3-Sicherheit**. HTTP/3 ist daher nicht „unzuverlässiges HTTP, weil UDP benutzt wird“. [RFC 9114, §§ 1.2–2](https://www.rfc-editor.org/rfc/rfc9114#section-1.2), [RFC 9000, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9000#section-1)

Eine Anfrage/Antwort nutzt grundsätzlich einen eigenen bidirektionalen QUIC-Stream. Der Verlust von Daten eines Streams erzwingt nicht mehr wie bei TCP das Warten aller anderen Streams auf dieselbe Bytestromlücke. Paketverlust kann wegen gemeinsamer Überlaststeuerung trotzdem die gesamte Verbindung beeinflussen; außerdem können Abhängigkeiten, etwa bei der Headerdecodierung, weiterhin Wartezeiten verursachen. **„HTTP/3 beseitigt jede Art von Blockierung“ wäre zu stark.** [RFC 9114, §§ 1.2, 2, 4.1 und 4.2](https://www.rfc-editor.org/rfc/rfc9114#section-2)

HTTP/3 verwendet eigene Frames und **QPACK** statt HPACK, um Headerkompression mit den unabhängigen QUIC-Streams zu kombinieren. QUIC kann den Verbindungsaufbau und bei geeigneter Wiederaufnahme den Start weiterer Daten beschleunigen. Daraus folgt keine Garantie, dass HTTP/3 in jedem Netz schneller ist; blockiertes UDP oder andere Randbedingungen können Ausweichverfahren erforderlich machen. [RFC 9114, §§ 2 und 3](https://www.rfc-editor.org/rfc/rfc9114#section-2)

**Vergleich in einem Satz:** 0.9 liefert einen einfachen Dokumentabruf; 1.0 ergänzt strukturierte Nachrichten; 1.1 verbessert Wiederverwendung und Framing; 2 multiplexiert binäre Streams über TCP; 3 verschiebt den Streamtransport zu QUIC über UDP.

## 2. E-Mail: SMTP, POP3 und IMAP

### SMTP – Übertragen und Weiterleiten

**Simple Mail Transfer Protocol**, in **RFC 5321** beschrieben, überträgt E-Mails zwischen SMTP-Clients und SMTP-Servern. Ein SMTP-Server kann anschließend selbst als Client die Nachricht weiterleiten (**Store-and-Forward**). DNS-MX-Einträge helfen bei der Auswahl des Ziel-Mailservers. SMTP dient **nicht** zum Lesen oder Synchronisieren eines Postfachs. [RFC 5321, §§ 2.1 und 5](https://www.rfc-editor.org/rfc/rfc5321#section-2.1)

SMTP verwendet TCP, bei Server-zu-Server-Übertragung üblicherweise Zielport **25**. Die authentifizierte Einlieferung vom Mailprogramm erfolgt typischerweise als **Message Submission**, etwa auf **587** mit STARTTLS oder **465** mit implizitem TLS. Unverschlüsselte Anmeldung ist keine geeignete Produktionskonfiguration. TLS schützt dabei die jeweilige Transportstrecke, nicht automatisch die E-Mail Ende-zu-Ende bis zum Leser. [RFC 5321, § 4.5.4.2](https://www.rfc-editor.org/rfc/rfc5321#section-4.5.4.2), [RFC 6409, § 3.1](https://www.rfc-editor.org/rfc/rfc6409#section-3.1), [RFC 8314, § 3.3](https://www.rfc-editor.org/rfc/rfc8314#section-3.3)

Eine Sitzung enthält Serverbegrüßung, `EHLO` zur Vorstellung/Fähigkeitsermittlung, `MAIL FROM`, mindestens ein `RCPT TO`, `DATA`, Nachrichteninhalt, eine Punktzeile und schließlich etwa `QUIT`. **Envelope** (`MAIL FROM`/`RCPT TO`) und **Nachrichtenheader** (`From:`/`To:`) sind verschiedene Dinge; zum Beispiel stehen Bcc-Empfänger im Envelope, ohne im `To:`-Header erscheinen zu müssen. Antworten beginnen mit dreistelligen Codes: 2xx erfolgreich, 3xx weitere Eingabe erwartet, 4xx vorübergehender, 5xx dauerhafter Fehler. [RFC 5321, §§ 3.3, 4.1 und 4.2](https://www.rfc-editor.org/rfc/rfc5321#section-3.3)

### Konkretes SMTP-Beispiel

**Didaktisch entworfenes Beispiel, kein Mitschnitt und keine tatsächlich versandte E-Mail.** Es zeigt den Basisdialog einer Übertragung zwischen Mailservern; TLS-Aushandlung und zusätzliche Produktionsprüfungen werden nicht dargestellt. `C:` und `S:` markieren die Richtung und werden nicht mitgesendet. Jede Protokollzeile endet auf dem Draht mit **CRLF**. Die Beispielzeit im Nachrichtenheader ist gewählt, nicht gemessen.

```text
S: 220 mx.example.org ESMTP ready
C: EHLO mail.example.net
S: 250-mx.example.org
S: 250 SIZE 1000000
C: MAIL FROM:<alice@example.net>
S: 250 Sender accepted
C: RCPT TO:<bob@example.org>
S: 250 Recipient accepted
C: DATA
S: 354 End data with <CRLF>.<CRLF>
C: Date: Mon, 19 Oct 2026 10:00:00 +0200
C: From: Alice <alice@example.net>
C: To: Bob <bob@example.org>
C: Subject: Test fuer Uebungsblatt 02
C: Message-ID: <ueb02-20261019@mail.example.net>
C:
C: Hallo Bob,
C: das ist eine didaktische Beispielnachricht.
C: ..Diese Textzeile beginnt im Original mit einem Punkt.
C: Viele Gruesse, Alice
C: .
S: 250 Message accepted for delivery
C: QUIT
S: 221 Bye
```

**Erklärung:** `220` signalisiert Bereitschaft. Die mehrzeilige `EHLO`-Antwort verwendet `250-` für eine Fortsetzungszeile und `250 ` für die letzte Zeile. Der Envelope benennt Absender und Empfänger. Nach `354` folgen Header, **eine leere Zeile** und Body. Die ursprüngliche Bodyzeile `.Diese ...` wird auf dem Draht zu `..Diese ...`: **Dot-Stuffing** verhindert die Verwechslung mit der alleinstehenden Punktzeile. Der Empfänger entfernt den zusätzlichen Punkt. Das `250` nach dem Punkt bestätigt die Annahme zur weiteren Bearbeitung, nicht, dass Bob die Mail gelesen hat. [RFC 5321, §§ 3.3, 4.1.1.1, 4.2 und 4.5.2](https://www.rfc-editor.org/rfc/rfc5321#section-4.5.2)

Das Nachrichtenformat mit `Date`, `From`, weiteren Feldern und Body ist getrennt vom Transport in **RFC 5322** beschrieben; Anhänge und weitere Inhaltsarten benötigen MIME-Verfahren. [RFC 5322, § 3.6](https://www.rfc-editor.org/rfc/rfc5322#section-3.6)

### POP3 – einfaches Abrufen eines Maildrops

**Post Office Protocol Version 3**, **RFC 1939**, erlaubt einem Client das Abrufen gespeicherter Nachrichten aus einem Maildrop. Es läuft klassisch über TCP **110**, mit implizitem TLS über **995**. Seine Zustände sind **AUTHORIZATION**, **TRANSACTION** und beim ordentlichen Beenden nach erfolgreicher Anmeldung **UPDATE**. Typische Befehle sind `STAT`, `LIST`, `RETR`, `DELE`, `RSET` und `QUIT`; Antworten beginnen mit `+OK` oder `-ERR`. [RFC 1939, §§ 3–6](https://www.rfc-editor.org/rfc/rfc1939#section-3), [RFC 8314, § 3.1](https://www.rfc-editor.org/rfc/rfc8314#section-3.1)

`RETR` lädt eine Nachricht, **löscht sie aber nicht automatisch**. `DELE` markiert sie zunächst zum Löschen; das reguläre `QUIT` aus dem TRANSACTION-Zustand führt zur UPDATE-Phase, in der die markierten Nachrichten entfernt werden. Bei einem Verbindungsabbruch ohne dieses `QUIT` dürfen sie nicht wegen dieser Sitzung gelöscht werden. POP3 kann also Nachrichten auf dem Server belassen; es bietet aber nicht die Ordner-, Flag- und Synchronisationsfunktionen von IMAP. [RFC 1939, §§ 5–6](https://www.rfc-editor.org/rfc/rfc1939#section-5)

### IMAP – serverseitige Postfächer und Synchronisation

**Internet Message Access Protocol** verwaltet serverseitige Mailboxen und eignet sich für den Zugriff mehrerer Geräte. Die aktuelle hier konsultierte Grundspezifikation ist **IMAP4rev2, RFC 9051**, als Nachfolger von IMAP4rev1/RFC 3501. Es läuft über TCP **143** beziehungsweise mit implizitem TLS über **993**. [RFC 9051, §§ 1.3 und 2.1](https://www.rfc-editor.org/rfc/rfc9051#section-2.1), [RFC 8314, § 3.2](https://www.rfc-editor.org/rfc/rfc8314#section-3.2)

IMAP kann Mailboxen auflisten/auswählen, Nachrichten auf dem Server durchsuchen, vollständige Nachrichten oder einzelne Teile laden und Zustände wie `\Seen` oder `\Deleted` verwalten. Beispiele sind `LIST`, `SELECT`, `SEARCH`, `FETCH`, `STORE`, `COPY`, `MOVE` und `EXPUNGE`. **UIDs** zusammen mit **UIDVALIDITY** erlauben es, Nachrichten über Sitzungen hinweg korrekt zuzuordnen. Kommandos besitzen Tags wie `A001`; der Server kann zusätzlich ungetaggte Zustandsmeldungen senden. IMAP ist trotzdem **kein Ersatz für SMTP zum Versenden**. [RFC 9051, §§ 1.3, 2.2–2.4 und 6](https://www.rfc-editor.org/rfc/rfc9051#section-2)

**Zusammenspiel:** Mailprogramm → SMTP-Submission → Mailserver → SMTP → Empfängermailserver; danach liest das Empfängerprogramm das Postfach über IMAP oder POP3. Bei Webmail übernimmt der Webdienst diese Rollen im Hintergrund; der Browser spricht zunächst HTTP(S) mit ihm.

## 3. DNS – Domain Name System

### Zweck, Aufbau und Datensätze

DNS ist eine **hierarchisch verteilte Datenbank** samt Abfrageprotokoll. Es ordnet Namen nicht nur IP-Adressen zu, sondern hält verschiedene Ressourcendatensätze. Der Namensraum ist ein Baum aus Labels: bei `www.example.org.` steht rechts die Wurzel `.`, davor die Top-Level-Domain `org`, dann `example` und `www`. Verwaltungsbereiche werden als **Zonen** delegiert; ein autoritativer Nameserver beantwortet Fragen zu den von ihm verwalteten Zonendaten. Ein rekursiver Resolver beschafft Antworten für Clients und hält einen Cache. [RFC 1034, §§ 3.1, 4.2 und 5](https://www.rfc-editor.org/rfc/rfc1034#section-3.1)

Wichtige Resource Records:

- **A:** IPv4-Adresse; **AAAA:** IPv6-Adresse.
- **CNAME:** Alias auf einen kanonischen Namen; **MX:** Mailserver mit Präferenzwert, kleinere Werte bevorzugt.
- **NS:** autoritativer Nameserver beziehungsweise Delegation; **SOA:** grundlegende Verwaltungs-/Zeitinformationen einer Zone.
- **PTR:** Verweis, unter anderem für Reverse Lookup über `in-addr.arpa` beziehungsweise `ip6.arpa`.
- **TXT:** Textdaten, die verschiedene Anwendungen nach jeweils eigenen Regeln interpretieren.

Ein RR enthält unter anderem Name, Typ, Klasse, **TTL** und typspezifische Daten. Die TTL begrenzt die Cachelebensdauer; DNS-TTL ist **nicht** die Hop-Grenze eines IP-Pakets. [RFC 1034, § 3.6](https://www.rfc-editor.org/rfc/rfc1034#section-3.6), [RFC 1035, §§ 3.3–3.4 und 4.1.3](https://www.rfc-editor.org/rfc/rfc1035#section-3.3), [RFC 3596, § 2](https://www.rfc-editor.org/rfc/rfc3596#section-2)

### Beispiel einer Auflösung ohne passenden Cacheeintrag

1. Der **Stub Resolver** des Endgeräts fragt den konfigurierten rekursiven Resolver nach `www.example.org.`, beispielsweise Typ A.
2. Dieser fragt, sofern ihm auch passende Delegationen fehlen, einen **Root-Nameserver**. Er erhält eine Verweisung auf zuständige `.org`-Nameserver, nicht die gesamte Auflösung vom Root selbst.
3. Ein `.org`-Nameserver verweist auf autoritative Server für `example.org`.
4. Der Resolver fragt einen solchen autoritativen Server und erhält die Antwort beziehungsweise folgt gegebenenfalls einem CNAME.
5. Er liefert dem Client das Ergebnis und speichert zulässige Informationen gemäß TTL zwischen. Weitere Anfragen können aus dem Cache beantwortet werden; deshalb werden nicht bei jedem Zugriff alle Ebenen erneut abgefragt.

Der Auftrag des Clients an seinen Resolver ist typischerweise **rekursiv**; die schrittweise Nachverfolgung von Verweisungen zwischen Resolver und autoritativen Servern ist **iterativ**. Dies ist ein Ablaufbeispiel, **keine durchgeführte Abfrage und keine Behauptung einer konkreten aktuellen IP-Adresse**. [RFC 1034, §§ 4.3.1–4.3.2 und 5.3](https://www.rfc-editor.org/rfc/rfc1034#section-4.3.1)

### Nachrichten und Transport

Eine DNS-Nachricht enthält **Header, Question, Answer, Authority und Additional**. Der Header enthält unter anderem eine Transaktions-ID, Query/Response-Kennung, Rekursionsflags, Antwortcode und die Anzahl der Einträge je Abschnitt. In der Question stehen `QNAME`, `QTYPE` und `QCLASS`. Fehler wie **NXDOMAIN** bedeuten etwas anderes als ein vorübergehender Serverfehler (**SERVFAIL**). [RFC 1035, § 4.1](https://www.rfc-editor.org/rfc/rfc1035#section-4.1)

Klassisches DNS verwendet **UDP und TCP auf Serverport 53**. Häufig beginnt eine Abfrage mit UDP; TCP ist kein optionaler exotischer Sonderfall, sondern für vollständige Implementierungen erforderlich, unter anderem für vollständige Zonentransfers und bei abgeschnittenen Antworten. Das alte 512-Byte-UDP-Limit kann mit **EDNS(0)** erweitert werden; „jede DNS-Antwort über 512 Byte muss TCP sein“ wäre heute falsch. [RFC 1035, § 4.2](https://www.rfc-editor.org/rfc/rfc1035#section-4.2), [RFC 7766, § 1](https://www.rfc-editor.org/rfc/rfc7766#section-1), [RFC 6891, §§ 1 und 3](https://www.rfc-editor.org/rfc/rfc6891#section-1)

### Sicherheit

Klassisches DNS verschlüsselt die Übertragung nicht. **DNS over TLS (DoT)** und **DNS over HTTPS (DoH)** schützen die jeweilige Verbindung zum Resolver. **DNSSEC** ermöglicht dagegen die Überprüfung von Herkunft und Unverändertheit signierter DNS-Daten; es verschlüsselt die Abfragen oder Antworten nicht. Verschlüsselter Transport und validierte Daten sind unterschiedliche Sicherheitsziele, die kombiniert werden können. [RFC 7858, § 1](https://www.rfc-editor.org/rfc/rfc7858#section-1), [RFC 8484, § 1](https://www.rfc-editor.org/rfc/rfc8484#section-1), [RFC 4033, §§ 3 und 4](https://www.rfc-editor.org/rfc/rfc4033#section-3)

**Quellenstand und Methode:** Abruf am **19.10.2026**. Die genannten Grundprotokolle wurden in den RFC-Primärtexten konsultiert, insbesondere RFC 1945 §§ 4–8, RFC 9112 §§ 3/6/9, RFC 9113 §§ 2/4/5/8, RFC 9114 §§ 1/2/4, RFC 5321 §§ 2/3/4, RFC 1939 §§ 3–6, RFC 9051 §§ 2/6 sowie RFC 1034/1035 §§ 3–5/4. Es handelt sich um Erklärungen und ein konstruiertes SMTP-Lehrbeispiel, nicht um erfundene Beobachtungen einer Netzaufzeichnung.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erstelle Ü 2.9 vollständig auf Deutsch, lies tatsächlich die HTTP-, SMTP-, POP3-, IMAP- und DNS-RFCs, erkläre die Versionen und Unterschiede und liefere ein korrektes, ausdrücklich didaktisches SMTP-Beispiel mit unmittelbaren Quellenbelegen.“
