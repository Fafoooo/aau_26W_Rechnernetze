# Ü 2.1 – Architektur des heutigen Internets und Zugangsmöglichkeiten

**Aufgabe:** Die allgemeine Architektur des heutigen Internets und seine Zugangsmöglichkeiten beschreiben.

## 1. Ein Netz aus selbstständig betriebenen Netzen

Das Internet ist kein einzelnes zentral verwaltetes Netz, sondern ein weltweiter Verbund von Netzen: etwa Heimnetzen, Unternehmens- und Hochschulnetzen, Internetprovidern und Netzen von Cloud- und Inhaltsanbietern. Seine gemeinsame Vermittlungsschicht ist **IP**: IPv4 und IPv6 erlauben die paketvermittelte Kommunikation über unterschiedliche Übertragungstechniken hinweg. Die Internetarchitektur trennt Anwendung, Transport, Internet- und Netzzugangsschicht. [RFC 1122, § 1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1.3), [RFC 8200, § 1](https://www.rfc-editor.org/rfc/rfc8200#section-1)

Man unterscheidet:

- **Netzrand:** Endsysteme wie Smartphones, Notebooks, Server und vernetzte Geräte führen Anwendungen aus. Ein Webbrowser und ein Webserver sind beispielsweise Kommunikationsendpunkte.
- **Zugangsnetz:** Es verbindet einen Haushalt, Betrieb oder ein mobiles Gerät mit dem Provider. WLAN beziehungsweise Ethernet kann dabei zunächst nur den lokalen Weg bis zum Heimrouter bilden.
- **Netzkern:** Router und leistungsfähige Verbindungen transportieren IP-Pakete zwischen Netzen. Ein Router entscheidet anhand von Zieladresse und Weiterleitungstabelle über den nächsten Hop; er muss nicht die gesamte Anwendung verstehen. [RFC 1122, §§ 1.1.1–1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1)

Ein mögliches Beispiel ist:

```text
Notebook → WLAN-Access-Point → Heimrouter → Glasfaser-Zugangsnetz
         → Provider-Router → Zusammenschaltung → Inhaltsanbieter/CDN
```

Das ist **ein Beispielpfad**, keine zwingende Reihenfolge verschiedener Provider. Liegt ein Inhaltscache bereits im eigenen Providernetz, kann der Verkehr dieses Netz gar nicht verlassen. Netflix dokumentiert solche lokal eingebetteten CDN-Server ausdrücklich. [Netflix Open Connect](https://openconnect.netflix.com/en/)

## 2. Zusammenschaltung und Routing

Größere Verwaltungs- und Routingbereiche werden als **Autonome Systeme (AS)** organisiert. Zwischen AS tauscht das **Border Gateway Protocol (BGP)** Informationen über erreichbare IP-Präfixe und AS-Pfade aus. Die Routenauswahl berücksichtigt technische und administrative Regeln; sie bedeutet nicht zwangsläufig den geographisch kürzesten Weg. Innerhalb eines AS werden unter anderem interne Routingprotokolle verwendet. [RFC 4271, §§ 1 und 9](https://www.rfc-editor.org/rfc/rfc4271#section-1)

Für die Zusammenschaltung gibt es insbesondere:

- **Transit:** Ein Netz bezahlt ein anderes für Erreichbarkeit über dessen Netz und weitere Verbindungen.
- **Peering:** Zwei Netze tauschen Verkehr direkt aus, privat über eine dedizierte Verbindung oder öffentlich an einem **Internet Exchange Point (IXP)**. Das kann Umwege und Transitkosten vermeiden.

Das Internet lässt sich daher nicht mehr angemessen als starre Pyramide aus ausschließlich lokalen, regionalen und globalen Providern beschreiben: Direkte Verbindungen, IXPs und große Inhaltsnetze bilden ein vielfältig vermaschtes System. [Internet Society: Peering und IXPs](https://www.internetsociety.org/our-work/connectivity/peering/), [Internet Society: Interconnection Policy Brief, 2026](https://www.internetsociety.org/wp-content/uploads/2026/10/Internet-Exchange-Points-and-Local-Interconnection-Ecosystems-Policy-Brief_EN.pdf)

## 3. Paketvermittlung und Ende-zu-Ende-Kommunikation

Daten werden in Paketen übertragen, die sich Leitungen und Router mit Paketen anderer Verbindungen teilen. **IP arbeitet nach dem Best-Effort-Prinzip:** Es garantiert weder Zustellung noch Reihenfolge noch eine feste Verzögerung. Warteschlangen und Überlast können Verzögerungen oder Verluste verursachen. Zuverlässigkeit kann eine höhere Schicht ergänzen, beispielsweise TCP durch Bestätigungen und Wiederholungen. [RFC 1122, § 1.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-1.1.3), [RFC 9293, § 2.2](https://www.rfc-editor.org/rfc/rfc9293#section-2.2)

**DNS** ermittelt beispielsweise zu einem Servernamen die passenden Adressdatensätze; **IP-Routing** transportiert anschließend Pakete zur gewählten Adresse. Das World Wide Web ist eine Anwendung auf dieser Infrastruktur, nicht mit dem Internet gleichzusetzen. [RFC 1034, §§ 3 und 5](https://www.rfc-editor.org/rfc/rfc1034#section-3), [RFC 9110, § 1](https://www.rfc-editor.org/rfc/rfc9110#section-1)

## 4. Heutige Zugangsmöglichkeiten

Die folgenden Technologien sind Zugangsmöglichkeiten, nicht automatisch Leistungszusagen. Die Verfügbarkeit muss am jeweiligen Standort geprüft werden. Eine Übersicht der grundlegenden Zugangsklassen liefern die [FCC-Breitbandinformationen](https://www.fcc.gov/consumers/guides/getting-broadband-qa) und die [FCC-Technologieklassifikation](https://www.fcc.gov/general/technology-codes-used-fixed-broadband-deployment-data).

- **DSL/VDSL:** Datenübertragung über Kupfer-Telefonleitungen. Das Modem verbindet sich mit der DSL-Infrastruktur des Providers. Leitungslänge, Leitungsqualität und eingesetzte DSL-Technik beeinflussen die erreichbare Datenrate.
- **Kabelinternet über DOCSIS:** Ein Kabelmodem nutzt das Koaxial- beziehungsweise Hybrid-Glasfaser-Koaxialnetz des Kabelanbieters. Ressourcen eines Anschlusssegments werden mit anderen Teilnehmern geteilt; Auslastung und Ausbau beeinflussen die Leistung.
- **Glasfaser, insbesondere FTTH:** Die Glasfaser reicht bis in das Haus beziehungsweise die Wohnung. Ein optischer Netzabschluss (ONT) beziehungsweise geeigneter Router verbindet das lokale Netz mit dem optischen Zugangsnetz. GPON ist eine mögliche gemeinsam genutzte Zugangsarchitektur, nicht die einzige Glasfasertechnik. [Broadband Forum TR-156, Issue 4](https://www.broadband-forum.org/pdfs/tr-156-4-0-0.pdf)
- **Mobilfunk, insbesondere LTE/4G und 5G:** Smartphone, Mobilfunkrouter oder Tethering stellen den Zugang über eine Funkzelle her. Empfang, Frequenzband, Zellenauslastung, Endgerät und Tarif beeinflussen Datenrate und Latenz. Ein als Festnetzersatz eingesetzter Funkanschluss wird häufig als Fixed Wireless Access bezeichnet. [FCC: feste und mobile Breitbandzugänge](https://help.bdc.fcc.gov/hc/en-us/articles/10467446103579-How-to-Use-the-FCC-s-National-Broadband-Map)
- **Fester Funkzugang/Richtfunk:** Eine ortsfeste Funkverbindung erschließt einen Haushalt oder Betrieb, häufig über eine Außenantenne. Eine geeignete Funkstrecke beziehungsweise Sichtverbindung kann erforderlich sein. [FCC-Breitbandinformationen](https://www.fcc.gov/consumers/guides/getting-broadband-qa)
- **Satelliteninternet:** Ein Terminal kommuniziert über Satelliten und Bodeninfrastruktur. Das ermöglicht Zugang auch ohne lokale Kabelversorgung; Sicht zum Himmel, Wetter, Auslastung und die konkrete Satellitenarchitektur beeinflussen die Leistung. Eine pauschale Aussage, jedes Satellitensystem habe dieselbe hohe Latenz, wäre unzutreffend. [FCC-Breitbandinformationen](https://www.fcc.gov/consumers/guides/getting-broadband-qa)
- **Ethernet und WLAN in LANs/Hotspots:** Zu Hause, an der Hochschule, im Betrieb oder an öffentlichen Hotspots erreicht ein Endgerät über Kabel oder IEEE 802.11 einen lokalen Router. **WLAN allein ist kein Internetanschluss:** Hinter dem Access Point muss ein funktionierender externer Zugang vorhanden sein. [FCC-Breitbandinformationen, Abschnitt Wireless](https://www.fcc.gov/consumers/guides/getting-broadband-qa)

**Fazit:** Über sehr unterschiedliche lokale und letzte Übertragungsstrecken gelangen Endgeräte in einen paketvermittelten IP-Verbund. Router, Routingprotokolle und die Zusammenschaltung autonomer Netze stellen die übergreifende Erreichbarkeit her.

**Quellenstand:** Recherche und Abruf am 19.10.2026; keine eigenen Netz- oder Geschwindigkeitsmessungen.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erstelle eine vollständig recherchierte deutsche Antwort zu Ü 2.1 über heutige Internetarchitektur und Zugangsmöglichkeiten mit Quellen direkt bei den Aussagen.“
