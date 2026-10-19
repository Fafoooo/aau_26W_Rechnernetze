# Ü 2.4 – TCP/IP- und OSI-Referenzmodell

**Aufgabe:** Das TCP/IP-Modell mit dem OSI-Modell vergleichen und eine umfassende Liste von Protokollbeispielen je Schicht angeben.

## 1. Grundlegende Zuordnung

Das klassische **TCP/IP-Modell** unterscheidet vier Schichten: **Anwendung, Transport, Internet und Netzzugang/Link**. So beschreibt es RFC 1122; das OSI-Modell unterscheidet sieben funktionale Schichten. TCP/IP ist nicht bloß OSI mit anderen Namen: Es beschreibt die Internetprotokollfamilie, und die funktionale Zuordnung ist stellenweise nur näherungsweise. [RFC 1122, § 1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1.3), [ISO/IEC 7498-1, §§ 6–7](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

- **TCP/IP-Anwendung** umfasst praktisch Funktionen der **OSI-Schichten 7, 6 und 5**: Anwendungskommunikation, Datendarstellung und Sitzungsfunktionen. In TCP/IP sind dafür keine drei getrennten generischen Schichten vorgeschrieben. RFC 1122 betont insbesondere die Zusammenfassung von Darstellungs- und Anwendungsschicht; die Zuordnung sämtlicher Sitzungsfunktionen ist eine didaktische Näherung.
- **TCP/IP-Transport** entspricht weitgehend **OSI 4**: Kommunikation zwischen Anwendungsendpunkten.
- **TCP/IP-Internet** entspricht weitgehend **OSI 3**: IP-Adressierung und Weiterleitung über Netze hinweg.
- **TCP/IP-Netzzugang** umfasst funktional **OSI 2 und 1**: Linkzugang, Frames und physische Übertragung.

Das häufig verwendete **Fünfschichtenmodell** trennt die TCP/IP-Netzzugangsschicht zusätzlich in Sicherung und Bitübertragung. Es ist eine verbreitete Lehrdarstellung, keine fünfte zusätzliche Schicht zwischen IP und TCP. [RFC 1122, § 1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1.3)

## 2. TCP/IP-Anwendungsschicht – OSI 5–7

Sie legt die Bedeutung anwendungsspezifischer Nachrichten fest und nutzt einen geeigneten Transportdienst. Eine breit gefächerte Auswahl:

- **HTTP/1.1, HTTP/2, HTTP/3:** Webressourcen und APIs; HTTP/1.1 und HTTP/2 verwenden typischerweise TCP, HTTP/3 QUIC über UDP. **HTTPS** bezeichnet HTTP mit gesicherter Kommunikation, nicht eine eigene OSI-Schicht. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110), [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112), [RFC 9113](https://www.rfc-editor.org/rfc/rfc9113), [RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)
- **DNS:** Namens- und weitere Ressourcenabfragen, klassisch UDP und TCP. [RFC 1034](https://www.rfc-editor.org/rfc/rfc1034), [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
- **SMTP:** E-Mail-Übertragung; **POP3** und **IMAP**: Zugriff auf empfangene E-Mails. [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321), [RFC 1939](https://www.rfc-editor.org/rfc/rfc1939), [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051)
- **FTP:** Dateiübertragung; **TFTP:** vereinfachte Dateiübertragung; **SSH:** gesicherte Fernzugriffe und Kanäle, die unter anderem Dateiübertragung unterstützen. [RFC 959](https://www.rfc-editor.org/rfc/rfc959), [RFC 1350](https://www.rfc-editor.org/rfc/rfc1350), [RFC 4251](https://www.rfc-editor.org/rfc/rfc4251)
- **DHCPv4/DHCPv6:** automatische Netzkonfiguration. Trotz ihrer Nähe zur Netzkonfiguration laufen sie über UDP und werden in diesem Modell der Anwendungsschicht zugeordnet. [RFC 2131](https://www.rfc-editor.org/rfc/rfc2131), [RFC 8415](https://www.rfc-editor.org/rfc/rfc8415)
- **SNMP:** Netzwerkmanagement; **NTP:** Zeitsynchronisation; **Syslog:** Übertragung von Ereignismeldungen. [RFC 3411](https://www.rfc-editor.org/rfc/rfc3411), [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905), [RFC 5424](https://www.rfc-editor.org/rfc/rfc5424)
- **SIP:** Signalisierung von Kommunikationssitzungen; **RTP/RTCP:** zeitbezogene Medienübertragung und Rückmeldungen, häufig über UDP; **RTSP:** Steuerung von Medienwiedergabe. Die Wörter „Transport“ im Namen RTP und „Session“ in SIP ändern nicht automatisch ihre TCP/IP-Einordnung oberhalb des Transportdienstes. [RFC 3261](https://www.rfc-editor.org/rfc/rfc3261), [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550), [RFC 7826](https://www.rfc-editor.org/rfc/rfc7826)
- **MQTT:** nachrichtenorientiertes Publish/Subscribe-Protokoll für Anwendungen, häufig im IoT. [OASIS MQTT 5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)

**TLS** liegt funktional zwischen Anwendung und Transport und stellt gesicherte Kanäle bereit. Im vierstufigen TCP/IP-Lehrmodell wird es gewöhnlich dem Bereich oberhalb der Transportschicht zugerechnet. Die Zuordnung „TLS = exakt OSI 6“ wäre zu streng. [RFC 8446, § 1](https://www.rfc-editor.org/rfc/rfc8446#section-1)

## 3. TCP/IP-Transportschicht – OSI 4

- **TCP:** zuverlässiger, geordneter, verbindungsorientierter Bytestrom mit Ports, Fluss- und Überlaststeuerung. [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293)
- **UDP:** verbindungsloser Datagrammdienst mit Ports und Prüfsumme, ohne eingebaute Wiederholungen oder Reihenfolgegarantie. [RFC 768](https://www.rfc-editor.org/rfc/rfc768)
- **SCTP:** zuverlässiger, nachrichtenorientierter Transport mit mehreren Streams und Unterstützung mehrerer Netzadressen. [RFC 9260](https://www.rfc-editor.org/rfc/rfc9260)
- **DCCP:** Datagrammtransport mit Überlaststeuerung, aber ohne zuverlässige Datenzustellung. [RFC 4340](https://www.rfc-editor.org/rfc/rfc4340)
- **QUIC:** verschlüsselter, zuverlässiger Multiplex-Transport mit mehreren Streams, auf UDP aufgebaut. **Funktional Transport**, auf dem Draht aber `QUIC → UDP → IP`; die Implementierung oberhalb von UDP erklärt die Abweichung vom einfachen Schichtenbild. [RFC 9000, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9000#section-1)

## 4. TCP/IP-Internetschicht – OSI 3

- **IPv4 und IPv6:** logische Adressierung und paketvermittelte Weiterleitung. [RFC 791](https://www.rfc-editor.org/rfc/rfc791), [RFC 8200](https://www.rfc-editor.org/rfc/rfc8200)
- **ICMPv4 und ICMPv6:** Fehlermeldungen und Diagnose; ICMP ist trotz seiner Kapselung in IP kein Anwendungsprotokoll. [RFC 792](https://www.rfc-editor.org/rfc/rfc792), [RFC 4443](https://www.rfc-editor.org/rfc/rfc4443)
- **IGMP und MLD:** Verwaltung von IPv4- beziehungsweise IPv6-Multicast-Mitgliedschaften; MLD verwendet ICMPv6. [RFC 3376](https://www.rfc-editor.org/rfc/rfc3376), [RFC 3810](https://www.rfc-editor.org/rfc/rfc3810)
- **IPv6 Neighbor Discovery (NDP):** Nachbar- und Routererkennung, einschließlich Adressauflösung, auf ICMPv6 aufgebaut. Es hat linklokale Aufgaben, wird hier wegen seiner IP/ICMPv6-Basis der Internetschicht zugeordnet. [RFC 4861](https://www.rfc-editor.org/rfc/rfc4861)
- **IPsec mit AH und ESP:** Authentizitäts-/Integritätsschutz beziehungsweise geschützter IP-Verkehr; die konkreten Eigenschaften hängen vom gewählten Protokoll und Modus ab. [RFC 4301](https://www.rfc-editor.org/rfc/rfc4301), [RFC 4302](https://www.rfc-editor.org/rfc/rfc4302), [RFC 4303](https://www.rfc-editor.org/rfc/rfc4303)

**Routingprotokolle muss man nach Aufgabe und Kapselung unterscheiden:** OSPF arbeitet direkt über IP und wird häufig dieser Steuerungsebene zugeordnet; BGP erfüllt ebenfalls eine Routingaufgabe, verwendet aber TCP und liegt kapselungstechnisch oberhalb der Transportschicht. RIP verwendet UDP. „Alle Routingprotokolle sind auf dem Draht Schicht 3“ wäre deshalb falsch. [RFC 2328, Anhang A.1](https://www.rfc-editor.org/rfc/rfc2328#appendix-A.1), [RFC 4271, § 1](https://www.rfc-editor.org/rfc/rfc4271#section-1), [RFC 2453, § 3.1](https://www.rfc-editor.org/rfc/rfc2453#section-3.1)

Die [IANA-Protokollnummern](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml) dokumentieren unter anderem TCP, UDP, ICMP, OSPF, AH und ESP als direkt von IP identifizierbare Protokolle. **Gleiche Kapselungstiefe heißt nicht gleiche funktionale Aufgabe.**

## 5. TCP/IP-Netzzugangsschicht – OSI 1–2

Für die Sicherungs-/Linkfunktionen sind Beispiele:

- **Ethernet (IEEE 802.3):** Rahmen, MAC-Adressen und Linkübertragung im LAN.
- **WLAN (IEEE 802.11, einschließlich n/ac/ax/be):** drahtloser Medienzugriff und Rahmenübertragung.
- **PPP:** Punkt-zu-Punkt-Verbindungen; **PPPoE:** PPP über Ethernet. [RFC 1661](https://www.rfc-editor.org/rfc/rfc1661), [RFC 2516](https://www.rfc-editor.org/rfc/rfc2516)
- **IEEE 802.1Q:** VLAN-Kennzeichnung beziehungsweise gebrückte Netze; **STP/RSTP:** Schleifenvermeidung in gebrückten LANs, historisch IEEE 802.1D und heute in der entsprechenden Bridge-Normenfamilie weitergeführt.
- **ARP:** Zuordnung einer IPv4-Adresse zur Linkadresse des nächsten Nachbarn; RFC 1122 behandelt ARP in der Linkschicht. Die Bezeichnung „Schicht 2½“ ist nur eine informelle Eselsbrücke. [RFC 826](https://www.rfc-editor.org/rfc/rfc826), [RFC 1122, § 2.3.2](https://www.rfc-editor.org/rfc/rfc1122#section-2.3.2)

IEEE 802.3 und 802.11 enthalten auch **physische Spezifikationen**. Beispiele für OSI 1 sind 1000BASE-T über Kupfer, 10GBASE-SR über Glasfaser und die jeweiligen 802.11-Funk-PHYs. Ein Kabel, eine Frequenz oder ein Stecker allein ist dagegen kein vollständiges Kommunikationsprotokoll. [IEEE 802: LAN/MAN Standards Committee](https://www.ieee802.org/), [IEEE 802.3](https://www.ieee802.org/3/), [IEEE 802.11](https://www.ieee802.org/11/)

## 6. Beispiel einer Kapselung

```text
HTTP/2 → TLS → TCP → IPv6 → WLAN-Frame → Funksignal
HTTP/3 → QUIC mit TLS-1.3-Sicherheit → UDP → IPv6 → WLAN → Funk
```

HTTP bleibt jeweils ein Anwendungsprotokoll. QUIC übernimmt Transportfunktionen, UDP bleibt das darunterliegende Transportformat. Ein Access Point kann WLAN-Frames in Ethernet überführen, ohne den HTTP-Inhalt zu interpretieren. [RFC 9113, § 2](https://www.rfc-editor.org/rfc/rfc9113#section-2), [RFC 9114, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9114#section-1)

**Quellenstand:** Abruf am 19.10.2026. Die Liste ist umfassend, aber keine vollständige Aufzählung aller Internet- oder IEEE-Protokolle. Historische Grund-RFCs können durch weitere RFCs aktualisiert sein.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erstelle die recherchierte deutsche Antwort zu Ü 2.4 mit TCP/IP–OSI-Zuordnung und einer umfassenden, fachlich sauber eingeordneten Protokollliste je Schicht.“
