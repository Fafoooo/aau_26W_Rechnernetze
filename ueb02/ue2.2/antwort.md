# Ü 2.2 – ISO/OSI-Referenzmodell

**Aufgabe:** Das OSI-Modell, alle Schichten sowie ihre Funktionen und vertikalen und horizontalen Schnittstellen beschreiben.

## 1. Grundidee

Das **Open Systems Interconnection Reference Model** nach ISO/IEC 7498-1 zerlegt Kommunikation in sieben funktionale Schichten. Es ist ein **Referenzmodell**, keine Vorschrift, dass jede reale Anwendung sieben getrennte Programme oder sieben zusätzliche Header besitzen muss. Eine Schicht nutzt Dienste der darunterliegenden Schicht und bietet der darüberliegenden Schicht einen Dienst an. [ISO/IEC 7498-1, §§ 5, 6 und 7, öffentlich zugängliche Ausgabe](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

## 2. Die sieben Schichten – von unten nach oben

### 1 – Bitübertragungsschicht / Physical Layer

Sie überträgt eine Bitfolge über ein physisches Medium und definiert unter anderem elektrische, optische oder Funksignale, Timing, Codierung, Modulation und physische Anschlussbedingungen. Sie interpretiert keine IP-Adressen oder Webseiten. Übertragungsfehler sind möglich; ein zuverlässiger Ende-zu-Ende-Dienst ist hier nicht zugesichert. Beispiele für konkrete physische Techniken sind Ethernet-PHYs wie 1000BASE-T und Funk-PHYs von IEEE 802.11. [ISO/IEC 7498-1, § 7.7](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

### 2 – Sicherungsschicht / Data Link Layer

Sie macht aus der Bitübertragung einen Dienst zwischen Teilnehmern eines Links: Rahmenbildung (**Frames**), lokale Adressierung, Medienzugriff und Fehlererkennung gehören zu ihren wesentlichen Aufgaben. Manche Sicherungsverfahren bestätigen Frames und wiederholen verlorene Übertragungen; **das ist nicht bei allen Techniken vorgeschrieben**. Ethernet und WLAN verwenden beispielsweise MAC-Adressen und Prüfsummen; WLAN kennt zudem linklokale Bestätigungen und Wiederholungen. Eine Ethernet-Bridge beziehungsweise ein Switch leitet Frames anhand von MAC-Information weiter. [ISO/IEC 7498-1, § 7.6](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

### 3 – Vermittlungsschicht / Network Layer

Sie ermöglicht Kommunikation über mehrere Links beziehungsweise Teilnetze hinweg. Zu ihren Aufgaben gehören logische Adressierung, Routing, Paketweiterleitung und je nach Protokoll weitere Verfahren wie Fragmentierung. Im Internet sind IPv4 und IPv6 wichtige Beispiele; Router wählen den nächsten Hop. **Nicht jede Netzschicht fragmentiert unterwegs:** Bei IPv6 fragmentieren Router keine Pakete, sondern melden eine zu kleine MTU mit ICMPv6. [ISO/IEC 7498-1, § 7.5](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf), [RFC 8200, § 4.5](https://www.rfc-editor.org/rfc/rfc8200#section-4.5)

### 4 – Transportschicht / Transport Layer

Sie stellt den Anwendungen beziehungsweise höheren Schichten einen Ende-zu-Ende-Transportdienst bereit. Dazu können Multiplexing verschiedener Kommunikationsbeziehungen, Segmentierung, Wiederzusammensetzen, Fehlerbehandlung und Flusskontrolle gehören. Der konkrete Dienst hängt vom Protokoll ab: TCP bietet einen zuverlässigen geordneten Bytestrom, UDP einen datagrammorientierten Dienst ohne solche Zustellgarantien. Ports ordnen im Internet Transportdaten Diensten beziehungsweise Endpunkten zu. [ISO/IEC 7498-1, § 7.4](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf), [RFC 9293, § 2.2](https://www.rfc-editor.org/rfc/rfc9293#section-2.2), [RFC 768](https://www.rfc-editor.org/rfc/rfc768)

### 5 – Sitzungsschicht / Session Layer

Sie organisiert und synchronisiert den Dialog zwischen kommunizierenden Anwendungen, beispielsweise Sitzungsaufbau und -abbau, Dialogsteuerung und Synchronisationspunkte für die Wiederaufnahme einer längeren Interaktion. Ein Synchronisationspunkt dient dazu, nach einer Störung einen vereinbarten Zustand wiederzufinden. Eine solche **Sitzung ist nicht einfach dasselbe wie eine TCP-Verbindung**: Eine Anwendungssitzung kann mehrere Transportverbindungen überdauern. [ISO/IEC 7498-1, § 7.3](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

### 6 – Darstellungsschicht / Presentation Layer

Sie sorgt dafür, dass übertragene Informationen auf beiden Seiten gleich interpretiert werden: Auswahl beziehungsweise Aushandlung einer Transfersyntax und Umwandlung von Datendarstellungen. Typische zugehörige Funktionen sind Zeichencodierung, Serialisierung, Kompression und kryptographische Transformationen. JSON, UTF-8 und ASN.1 sind Beispiele für Darstellungsformen beziehungsweise Notationen, **nicht automatisch eigenständige OSI-Schicht-6-Netzprotokolle**. [ISO/IEC 7498-1, § 7.2](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

### 7 – Anwendungsschicht / Application Layer

Sie stellt anwendungsspezifische Kommunikationsfunktionen bereit: etwa Zugriff auf Webressourcen, E-Mail-Übertragung oder Namensauflösung. Im Internet erfüllen HTTP, SMTP und DNS solche Aufgaben. „Anwendungsschicht“ meint die kommunikationsbezogenen Funktionen, nicht jede Benutzeroberfläche oder interne Berechnung des gesamten Anwendungsprogramms. [ISO/IEC 7498-1, § 7.1](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf), [RFC 9110, § 1](https://www.rfc-editor.org/rfc/rfc9110#section-1), [RFC 5321, § 2](https://www.rfc-editor.org/rfc/rfc5321#section-2), [RFC 1034, § 2](https://www.rfc-editor.org/rfc/rfc1034#section-2)

## 3. Vertikale Schnittstellen – Dienste innerhalb eines Systems

**Vertikal** heißt: Eine Schicht kommuniziert innerhalb desselben Systems mit der benachbarten Schicht. Schicht N bietet Schicht N+1 an einem **Service Access Point (SAP)** einen Dienst an. Dabei beschreibt die Dienstschnittstelle, **was** verfügbar ist, nicht die interne Implementierung. Dienstprimitive lassen sich konzeptionell als `request`, `indication`, `response` und `confirm` beschreiben; nicht jeder Dienst verwendet alle vier. [ISO/IEC 7498-1, §§ 5.2, 5.5 und 5.7](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

Ein praktisches Internetbeispiel für eine solche Dienstnutzung ist eine Socket-Schnittstelle: Eine Anwendung übergibt Bytes an TCP. Der Socket ist eine konkrete Programmierschnittstelle; er ist **nicht die vollständige abstrakte OSI-Spezifikation eines SAP**. TCP übergibt wiederum seine Segmente zur Beförderung an IP. [RFC 9293, §§ 2.2 und 3.9](https://www.rfc-editor.org/rfc/rfc9293#section-3.9)

Zur Kapselung: Die von oben übernommenen Nutzdaten heißen aus Sicht einer Schicht **Service Data Unit (SDU)**. Zusammen mit der hinzugefügten **Protocol Control Information (PCI)** entsteht deren **Protocol Data Unit (PDU)**. Eine PDU kann zur SDU der darunterliegenden Schicht werden. Segmentierung und Zusammenfassung können dieses einfache Eins-zu-eins-Bild verändern. [ISO/IEC 7498-1, § 5.6](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

## 4. Horizontale Beziehungen – Protokolle zwischen Partnerinstanzen

**Horizontal** bedeutet die logische Kommunikation von Partnerinstanzen derselben Schicht in unterschiedlichen Systemen. Ihr **Protokoll** legt Nachrichtenformate, Bedeutung, Reihenfolge und Zustandsübergänge fest. So verarbeitet die TCP-Instanz des Empfängers Sequenznummern und Bestätigungen der TCP-Instanz des Senders. [ISO/IEC 7498-1, § 5.3](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf), [RFC 9293, § 3](https://www.rfc-editor.org/rfc/rfc9293#section-3)

```text
System A                           System B
Anwendung  ← logisches Protokoll →  Anwendung
    ↕ lokaler Dienst                   ↕ lokaler Dienst
Transport  ← logisches Protokoll →  Transport
    ↕                                  ↕
Netzwerk   ← über Router/Teilnetze → Netzwerk
    ↕                                  ↕
Sicherung  ← jeweils pro Link →     Sicherung
    ↕                                  ↕
Physik     ← Signale auf Medien →   Physik
```

Die horizontalen Pfeile sind **keine zusätzlichen direkten Leitungen**. Tatsächlich wandern Daten beim Sender die Dienste nach unten, über Medien und gegebenenfalls Zwischensysteme und beim Empfänger nach oben. Peer-Beziehungen reichen dabei je nach Schicht unterschiedlich weit: Die Sicherungsschicht gilt für einen Link, ein Transportprotokoll wie TCP verbindet Endsysteme. Router bearbeiten für die Weiterleitung typischerweise die unteren drei Schichten, nicht den gesamten Anwendungsdialog. [ISO/IEC 7498-1, §§ 5.3 und 6.5](https://www.ecma-international.org/wp-content/uploads/s020269e.pdf)

**Merksatz:** Vertikal = **Dienstnutzung zwischen Nachbarschichten**; horizontal = **Protokollregeln zwischen gleichrangigen Instanzen**.

**Quellenstand:** Abruf am 19.10.2026. Internetprotokolle dienen als funktionale Beispiele; damit wird keine exakte Eins-zu-eins-Implementierung des OSI-Modells behauptet.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erkläre Ü 2.2 vollständig auf Deutsch: alle OSI-Schichten mit Funktionen sowie vertikale Dienstschnittstellen und horizontale Protokollbeziehungen; recherchiere und belege die Aussagen.“
