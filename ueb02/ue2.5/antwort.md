# Ü 2.5 – Transportschicht, TCP und UDP

**Aufgabe:** Die allgemeinen Aufgaben der Transportschicht, die wesentlichen Unterschiede zwischen TCP und UDP und typische Anwendungsprotokolle erläutern.

## 1. Funktion der Transportschicht

IP befördert Pakete zwischen Hosts, ohne eine zuverlässige Zustellung zu garantieren. Die **Transportschicht** stellt darüber einen Dienst für die Kommunikation zwischen Anwendungsendpunkten bereit. Dazu gehören je nach Protokoll:

- **Multiplexing und Demultiplexing:** Mehrere Anwendungen können gleichzeitig das Netz nutzen. Portnummern identifizieren lokale Transportendpunkte beziehungsweise Dienste. Eine TCP-Verbindung wird innerhalb ihres Transportprotokolls durch Quell-IP, Quellport, Ziel-IP und Zielport unterschieden.
- **Aufbereitung der Nutzdaten:** TCP zerlegt einen Anwendungsbytestrom in Segmente und setzt empfangene Bytes wieder zu einem Strom zusammen; UDP bewahrt die Grenzen einzelner Nachrichten.
- **Fehlererkennung:** Prüfsummen können beschädigte Übertragungen erkennen. Sie sind kein kryptographischer Authentizitätsnachweis.
- **Optionale Zuverlässigkeit, Reihenfolge und Steuerung:** TCP bietet Bestätigungen, Wiederholungen und Flusskontrolle sowie Überlaststeuerung. UDP bietet diese Mechanismen nicht selbst.

Nicht jede Funktion ist somit eine Zusage **jedes** Transportprotokolls. [RFC 1122, § 1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1.3), [RFC 9293, §§ 2.2, 3.1 und 3.3](https://www.rfc-editor.org/rfc/rfc9293#section-2.2), [RFC 768](https://www.rfc-editor.org/rfc/rfc768)

## 2. TCP – Transmission Control Protocol

TCP bietet einen **verbindungsorientierten, zuverlässigen und geordneten Bytestrom**, gleichzeitig in beide Richtungen (Full Duplex). Üblicherweise baut es eine Verbindung mit `SYN → SYN+ACK → ACK` auf. Sequenznummern, Bestätigungen, Prüfsummen und erneute Übertragungen erlauben es, fehlende oder fehlerhafte Daten zu behandeln und Duplikate auszusortieren. [RFC 9293, §§ 2.2, 3.4 und 3.5](https://www.rfc-editor.org/rfc/rfc9293#section-2.2)

Wichtige Eigenschaften:

- **Keine Nachrichtengrenzen:** Zweimaliges Senden bedeutet nicht zweimaliges Empfangen in denselben Portionen. Anwendungen müssen Nachrichten selbst einrahmen, beispielsweise mit einer Längenangabe oder einem Trennzeichen.
- **Geordnete Übergabe:** Fehlen frühere Bytes, hält TCP später eingetroffene Bytes normalerweise zurück. Dieses **Head-of-Line Blocking** kann Verzögerungen verursachen.
- **Flusskontrolle:** Das Empfangsfenster schützt den Empfänger davor, mehr Daten zwischenpuffern zu müssen, als er aufnehmen kann.
- **Überlaststeuerung:** Der Sender begrenzt seine Sendemenge entsprechend dem Zustand des Netzes. Das ist etwas anderes als die Aufnahmekapazität des Empfängers.
- **Header:** Mindestens 20 Byte, durch TCP-Optionen größer. Verbindungsverwaltung und Wiederholungen können zusätzlichen Aufwand und Wartezeit verursachen.

TCP ist **keine absolute Zustellgarantie trotz jedes Ausfalls**. Es liefert einen geordneten Strom, solange die Verbindung dies ermöglicht, oder signalisiert einen Fehler. Ein TCP-ACK bestätigt empfangene Bytes beim Gegenüber, nicht die erfolgreiche fachliche Verarbeitung, etwa eine abgeschlossene Bankbuchung. TCP allein verschlüsselt nichts. [RFC 9293, §§ 3.1, 3.8 und 3.9](https://www.rfc-editor.org/rfc/rfc9293#section-3.1), [RFC 5681, § 3](https://www.rfc-editor.org/rfc/rfc5681#section-3)

## 3. UDP – User Datagram Protocol

UDP bietet einen **verbindungslosen, nachrichtenorientierten Datagrammdienst**. Ein UDP-Datagramm besitzt Quellport, Zielport, Länge und Prüfsumme; sein Header ist 8 Byte lang. Ein auf UDP-Ebene vollständig empfangenes Datagramm bleibt als Nachricht abgegrenzt. Ist der Empfangspuffer der Anwendung zu klein, können Daten durch die Socket-Schnittstelle abgeschnitten werden – UDP ist kein Mechanismus, um beliebig große Nachrichten verlustfrei zu erzwingen. [RFC 768](https://www.rfc-editor.org/rfc/rfc768)

UDP führt selbst **keinen Handshake, keine Bestätigungen, keine Wiederholungen, keine Umordnung, keine Duplikatunterdrückung, keine Flusskontrolle und keine Überlaststeuerung** durch. Datagramme können verloren gehen, doppelt eintreffen oder ihre Reihenfolge ändern. Anwendungen können einzelne dieser Funktionen ergänzen und müssen insbesondere Überlastvermeidung berücksichtigen. „UDP ist immer schneller“ ist daher zu pauschal; es hat weniger eingebaute Mechanismen, aber keine garantierte Latenz oder Datenrate. [RFC 768](https://www.rfc-editor.org/rfc/rfc768), [RFC 8085, §§ 3.1–3.3](https://www.rfc-editor.org/rfc/rfc8085#section-3)

Bei IPv4 darf eine UDP-Prüfsumme fehlen; bei IPv6 ist sie grundsätzlich verpflichtend, abgesehen von eng begrenzten spezifizierten Ausnahmen. Auch UDP bietet selbst keine Verschlüsselung. [RFC 768](https://www.rfc-editor.org/rfc/rfc768), [RFC 8200, § 8.1](https://www.rfc-editor.org/rfc/rfc8200#section-8.1)

## 4. Typische Anwendungsprotokolle

### Häufig mit TCP

- **HTTP/1.1 und HTTP/2:** Webseiten, APIs und auch gespeicherte Videostreams; über HTTPS mit TLS gesichert. **HTTP/3 gehört nicht in diese TCP-Liste.** [RFC 9112, § 9](https://www.rfc-editor.org/rfc/rfc9112#section-9), [RFC 9113, § 2](https://www.rfc-editor.org/rfc/rfc9113#section-2)
- **SMTP, IMAP und POP3:** Mailübertragung und Mailzugriff. [RFC 5321, § 4.5.4.2](https://www.rfc-editor.org/rfc/rfc5321#section-4.5.4.2), [RFC 9051, § 2.1](https://www.rfc-editor.org/rfc/rfc9051#section-2.1), [RFC 1939, § 3](https://www.rfc-editor.org/rfc/rfc1939#section-3)
- **SSH:** gesicherte Fernanmeldung und Kanäle; **FTP:** klassische Dateiübertragung mit Steuer- und Datenverbindungen. [RFC 4253, § 4](https://www.rfc-editor.org/rfc/rfc4253#section-4), [RFC 959, § 2.3](https://www.rfc-editor.org/rfc/rfc959#section-2.3)
- **DNS über TCP:** regulär unterstützter Transport, unter anderem bei großen Antworten oder vollständigen Zonentransfers; nicht auf diese Fälle beschränkt. [RFC 7766, §§ 1 und 5](https://www.rfc-editor.org/rfc/rfc7766#section-1)

### Häufig mit UDP

- **Klassisches DNS:** viele einzelne Abfragen und Antworten, Serverport 53; bei Bedarf auch TCP. [RFC 1035, § 4.2](https://www.rfc-editor.org/rfc/rfc1035#section-4.2)
- **DHCPv4:** automatische IP-Konfiguration; **NTP:** Zeitsynchronisation. [RFC 2131, § 4.1](https://www.rfc-editor.org/rfc/rfc2131#section-4.1), [RFC 5905, § 1](https://www.rfc-editor.org/rfc/rfc5905#section-1)
- **SNMP:** Netzwerkmanagement, häufig mit UDP. [RFC 3417, § 3](https://www.rfc-editor.org/rfc/rfc3417#section-3)
- **RTP/RTCP:** häufig für Echtzeitaudio und -video. Bei solchen Anwendungen kann ein rechtzeitig eintreffender aktueller Wert wichtiger sein als die verspätete Wiederholung eines alten Werts. RTP liefert dafür unter anderem Sequenznummern und Zeitstempel, macht UDP aber nicht automatisch zuverlässig. [RFC 3550, §§ 2 und 5](https://www.rfc-editor.org/rfc/rfc3550#section-2)
- **TFTP:** einfache Dateiübertragung; dessen Bestätigungen und Wiederholungen liegen im Anwendungsprotokoll über UDP. [RFC 1350, §§ 2 und 5](https://www.rfc-editor.org/rfc/rfc1350#section-2)
- **HTTP/3 über QUIC über UDP:** QUIC ergänzt Verschlüsselung, zuverlässige Streams, Fluss- und Überlaststeuerung. **UDP als Unterbau bedeutet nicht, dass HTTP/3 unzuverlässig übertragen wird.** [RFC 9000, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9000#section-1), [RFC 9114, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9114#section-1)

**Fazit:** TCP liefert einen bereits weitgehend geregelten Bytestromdienst. UDP liefert einen kleinen Datagrammdienst und überlässt weitergehende Anforderungen höheren Protokollen. Die Wahl richtet sich nach benötigter Semantik und Verzögerungstoleranz, nicht nach dem Schlagwort „TCP langsam, UDP schnell“.

**Quellenstand:** Recherche und Abruf am 19.10.2026; keine eigenen Latenz- oder Durchsatzmessungen.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erstelle eine vollständige recherchierte Erklärung zu Ü 2.5 über Transportschicht, TCP gegenüber UDP und bekannte Anwendungsprotokolle beider Transportarten mit unmittelbaren Quellenbelegen.“
