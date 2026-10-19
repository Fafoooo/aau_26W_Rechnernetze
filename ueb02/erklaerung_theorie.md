# Übungsblatt 02 – Theorie verstehen und erklären

Dieses Lernblatt ergänzt die Antworten zu **2.1, 2.2, 2.4, 2.5, 2.7, 2.8 und 2.9**. Die Nummer **2.3 fehlt tatsächlich in der Angabe**; es wurde keine Ersatzaufgabe erfunden. Die Quellen für fachliche Aussagen stehen unmittelbar in den verlinkten Antworten.

## 1. Internetarchitektur – zuerst den Weg einer Nachricht erklären

[Antwort 2.1](ue2.1/antwort.md)

Beginne nicht mit einer Aufzählung von Fachwörtern, sondern mit einer Nachricht: „Mein Notebook will einen Server erreichen. Zuerst muss es ins lokale Netz, dann zum Provider und gegebenenfalls über andere Netze zum Server.“

- **Endsystem:** Hier läuft die eigentliche Anwendung.
- **Access Point:** Verbindet das WLAN mit dem lokalen Netz. Ein AP ist nicht automatisch ein Internetprovider oder ein Router.
- **Router:** Verbindet IP-Netze und entscheidet über den nächsten Hop.
- **AS:** Ein administrativ zusammengehöriger Routingbereich. Ein AS ist weder ein einzelner Router noch automatisch ein ganzes Land.
- **Peering/Transit:** Beschreiben die Zusammenarbeit zwischen Netzen. Ein IXP ist ein Zusammenschaltungspunkt, kein zentraler Welt-Internetrouter.

**Wichtige Denkfalle:** „Glasfaser oder WLAN?“ ist häufig keine echte Alternative: Glasfaser kann den Hausanschluss bilden und WLAN die letzte Verbindung zum Notebook. Beides kann Bestandteil derselben Kommunikation sein.

**Tafelfrage:** Ist ein im WLAN verbundenes Handy sicher im Internet? – Nein. Der lokale Funklink kann funktionieren, während der externe Anschluss oder DNS ausfällt.

## 2. OSI – Dienst und Protokoll auseinanderhalten

[Antwort 2.2](ue2.2/antwort.md)

Merke die Aufgaben in dieser Reihenfolge: **Signale → Frames → Pakete/Routing → Transport → Dialog → Darstellung → Anwendungskommunikation**.

**Vertikal** ist das Verhältnis zu Nachbarschichten im selben Rechner. Eine Anwendung möchte Bytes transportieren und nutzt dazu einen angebotenen Dienst. **Horizontal** sind die Regeln zwischen gleichrangigen Instanzen auf verschiedenen Rechnern. Eine TCP-Instanz interpretiert beispielsweise eine Bestätigung der anderen TCP-Instanz.

Stelle dir die Kapselung wie beschriftete Umschläge vor:

1. Eine Schicht erhält Nutzdaten: ihre **SDU**.
2. Sie ergänzt Steuerinformation: ihre **PCI**.
3. Die daraus gebildete Einheit ist ihre **PDU**.
4. Diese Einheit kann für die nächste tiefere Schicht wieder bloßer Nutzinhalt sein.

Die Umschlagvorstellung erklärt Header, aber nicht jedes Detail: Eine Schicht kann Daten auch aufteilen oder zusammenfassen. Es gibt nicht zwangsläufig für jede OSI-Schicht einen eigenen zusätzlichen Header.

**Tafelfrage:** Spricht Schicht 4 direkt durch ein eigenes Kabel mit Schicht 4? – Nein. Das ist eine logische Peer-Beziehung. Die tatsächlichen Daten nutzen beim Sender die unteren Schichten und beim Empfänger deren Dienste in umgekehrter Richtung.

## 3. TCP/IP – ein Modell, nicht eine starre Schubladensammlung

[Antwort 2.4](ue2.4/antwort.md)

Das Grundbild hat **vier Schichten**. Die Internet-Anwendungsschicht übernimmt viele Funktionen, die OSI oben feiner trennt. Der Netzzugang fasst dagegen Sicherung und Physik zusammen.

Wichtig ist die Unterscheidung zweier Fragen:

- **Welche Aufgabe erfüllt das Protokoll?** BGP kümmert sich um Routinginformation.
- **Wie ist es gekapselt?** BGP-Nachrichten werden über TCP transportiert.

Deshalb darf man ein Protokoll nicht allein anhand seines Namens oder seiner fachlichen Aufgabe auf dem Draht einordnen. DHCP konfiguriert IP-Adressen, liegt aber über UDP. ICMP liegt in IP und erfüllt Kontrollaufgaben der Internetschicht. ARP arbeitet direkt im lokalen Linkbereich.

**QUIC-Sonderfall:** Zeichne `HTTP/3 → QUIC → UDP → IP`. QUIC liefert Transportfunktionen, obwohl es technisch über einem weiteren Transportformat implementiert ist. Eine funktionale Einordnung und ein Kapselungsdiagramm können daher unterschiedliche Aspekte zeigen, ohne sich zu widersprechen.

## 4. TCP und UDP – welche Zusage bekommt die Anwendung?

[Antwort 2.5](ue2.5/antwort.md)

**TCP:** „Du erhältst einen geordneten Bytestrom, oder die Verbindung scheitert.“ **UDP:** „Du kannst einzelne Nachrichten absenden; UDP selbst garantiert deren Ankunft und Reihenfolge nicht.“

Zwei wichtige Unterscheidungen:

- **Flusskontrolle** schützt den **Empfänger**. Er signalisiert, wie viele Daten er aufnehmen kann.
- **Überlaststeuerung** schützt das **Netz**. Der Sender darf nicht blind alles hineinsenden, nur weil der Empfänger viel Speicher hat.

TCP hat keine Nachrichtengrenzen. Wenn die Anwendung zwei fachliche Nachrichten sendet, kann eine Leseoperation beide oder nur einen Teil liefern. Ein Anwendungsprotokoll muss deswegen ein **Framing** festlegen, beispielsweise „erst Länge, dann Inhalt“.

Ein TCP-ACK ist keine Bestätigung „Bestellung bezahlt“ oder „Geld abgehoben“. Es bestätigt Transportdaten. Eine fachliche Transaktion braucht eine fachliche Antwort und gegebenenfalls Schutz vor Wiederholungen.

**Tafelfrage:** Ist HTTP/3 unzuverlässig, weil darunter UDP steht? – Nein. QUIC ergänzt die benötigten zuverlässigen Streams. Ebenso kann TFTP über UDP auf Anwendungsebene selbst bestätigen und wiederholen.

## 5. WLAN-Plan – Annahmen, Datenblatt und Messung trennen

[Antwort 2.7](ue2.7/antwort.md), [Preisnachweise](ue2.7/preisnachweise.md)

Der Entwurf beschreibt bewusst **nicht dein unbekanntes reales Haus**, sondern ein Referenzhaus. Er setzt vorhandenes ONT, vollständige Kabelwege und Endgeräte voraus. Ohne diese Voraussetzung wäre die ausgewiesene Hardware-Summe kein vollständiges Budget.

Die Rollen sind getrennt: **Gateway routet**, **Switch verbindet Kabelgeräte und liefert PoE**, **APs stellen Funkzellen bereit**. Der gewählte Router hat kein WLAN und kein eingebautes Anschlussmodem. Der Ethernet-Uplink eines APs ist kein zusätzlicher drahtloser Mesh-Hop.

Zwei APs werden nicht mit dem Argument „die beworbenen Quadratmeter addieren sich“ garantiert. Wände, Decken, Nachbarnetze und Endgeräte entscheiden mit. Deshalb sind die Kanäle ein **Startplan**, keine gemessene freie Kanalbelegung.

**Sicherheitsfrage:** Reicht eine Gast-SSID? – Nicht allein. Die Zuordnung zum getrennten VLAN und die Firewall müssen zusammenpassen. Die Isolation muss nach dem Aufbau mit absichtlich unerlaubten Zugriffen geprüft werden, auch bei IPv6.

### Die Kostenrechnung selbst ausführen

Im Repository-Hauptverzeichnis:

```bash
python3 ueb02/ue2.7/kosten.py
```

Tatsächlich ausgeführtes Ergebnis:

```text
1 x UCG-Ultra: 114.00 EUR = 114.00 EUR
1 x USW-Lite-8-PoE: 124.00 EUR = 124.00 EUR
2 x U6+: 111.90 EUR = 223.80 EUR
Warenwert inkl. MwSt.: 461.80 EUR
Versand laut ausgewählten Angeboten: 0.00 EUR
Geplante Anschaffung gesamt: 461.80 EUR
AP-Leistungsbedarf maximal: 18 W
Rechnerische PoE-Budgetreserve: 34 W
Planungsrechnung, keine Bestellung und keine Verbrauchsmessung.
```

Die Rechnung verwendet gespeicherte, recherchierte Angebotswerte. Sie fragt **keine Livepreise** ab. Bei neuen Preisen müssen Eingabewerte und die erwartete Summe überprüft werden. Die rechnerische PoE-Reserve ersetzt keine Berücksichtigung aller Leitungsverluste.

### Zeilenerklärung von `ue2.7/kosten.py`

- **1–3:** Verpflichtende KI-Angaben zu Tool/Modell, Datum und tatsächlich verwendetem Auftrag. Kommentare werden nicht ausgeführt.
- **4:** Importiert `Decimal`, um Geldbeträge dezimal statt als binäre Gleitkommazahlen zu behandeln.
- **5:** Leerzeile zur Gliederung.
- **6:** Erklärt ausdrücklich, dass die folgenden Preise gespeicherte Bruttopreise sind.
- **7:** Beginnt eine Liste von Einkaufspositionen.
- **8:** Tupel aus Routermodell, Stückzahl, Einzelpreis und Preisquellen-URL.
- **9:** Dasselbe Datenformat für den Switch.
- **10:** Dasselbe Datenformat für die beiden APs. Die Stückzahl steht getrennt vom Einzelpreis.
- **11:** Schließt die Liste.
- **12:** Leerzeile.
- **13:** Initialisiert den Warenwert mit einem dezimalen Nullbetrag.
- **14:** Durchläuft alle Tupel und entpackt ihre vier Felder. `quelle` dokumentiert die Herkunft, wird aber nicht über das Netz abgefragt.
- **15:** Multipliziert Stückzahl und Einzelpreis zur Positionssumme.
- **16:** Addiert die Positionssumme zum bisherigen Warenwert.
- **17:** Gibt die Position aus; `.2f` formatiert zwei Nachkommastellen.
- **18:** Leerzeile.
- **19:** Dokumentiert die recherchierte Voraussetzung für den Versandansatz.
- **20:** Setzt den Versand auf null, weil die ausgewählten Angebote Gratisversand nennen, nicht weil Versand allgemein kostenlos wäre.
- **21:** Addiert Warenwert und Versand.
- **22:** Gibt den Warenwert aus.
- **23:** Gibt den angesetzten Versand aus.
- **24:** Gibt die Gesamtsumme aus.
- **25:** Prüft, ob die ausgeführte Rechnung die dokumentierte Erwartung erfüllt. Bei einer Änderung muss die Erwartung unabhängig nachgerechnet werden.
- **26:** Leerzeile.
- **27:** Speichert die Anzahl der APs für die Leistungsrechnung.
- **28:** Übernimmt die maximale AP-Leistungsaufnahme aus dem Datenblatt.
- **29:** Übernimmt das PoE-Gesamtbudget aus dem Switch-Datenblatt.
- **30:** Berechnet den maximal angesetzten Bedarf beider APs.
- **31:** Zieht diesen Bedarf vom PoE-Budget ab.
- **32:** Prüft, dass der angesetzte Bedarf das Budget nicht überschreitet.
- **33:** Gibt den berechneten AP-Bedarf aus.
- **34:** Gibt die rechnerische Reserve aus.
- **35:** Verhindert die Fehlinterpretation des Ergebnisses als Bestellung oder Verbrauchsmessung.

`assert` ist hier eine einfache Plausibilitätsprüfung, kein Sicherheitsmechanismus für Produktionscode. Das Skript hat keine Fremdpakete und muss ohne Python-Optimierungsoption `-O` gestartet werden, wenn diese Prüfungen ausgeführt werden sollen.

## 6. VoD – Puffer statt „der Server drückt ständig Bilder hinein“

[Antwort 2.8](ue2.8/antwort.md)

Erkläre den Ablauf mit **vorbereiten → Manifest laden → Segmente abrufen → puffern → abspielen → Qualität anpassen**. Ein Video besteht bereits beim Anbieter; die Nutzer starten es unabhängig voneinander.

- **Codec:** Wie werden Bild oder Ton komprimiert?
- **Container:** Wie liegen die Medien und Metadaten strukturiert vor?
- **HLS/DASH:** Wie findet und lädt der Player geeignete Abschnitte?
- **CDN:** Von welchem günstig gelegenen Server kommen die Daten?
- **DRM:** Welche Voraussetzungen gelten für das Entschlüsseln und Abspielen geschützter Inhalte?

Ein Puffer ist wie ein kleiner Vorrat: Er kann kurzfristige Lieferprobleme ausgleichen. Wenn der Nachschub dauerhaft nicht zur gewählten Qualität passt, muss die Qualität sinken oder es kommt zu Unterbrechungen. Eine gute Anschlussrate beseitigt nicht jedes WLAN- oder Decodierproblem.

**Tafelfrage:** Braucht Streaming immer UDP? – Nein. Adaptives HTTP-Streaming nutzt häufig TCP/TLS; HTTP/3 nutzt QUIC/UDP. Das Wort Streaming legt den Transport nicht fest.

## 7. Anwendungsschicht – die prüfungsrelevanten Unterschiede

[Antwort 2.9](ue2.9/antwort.md)

### HTTP-Versionen

Lerne die Entwicklung anhand des jeweils gelösten Problems:

1. **0.9:** einfacher Abruf ohne Antwortheader/Statuszeile.
2. **1.0:** formatierte Nachrichten, Status und Medientypen.
3. **1.1:** persistente Verbindungen, Pflicht-Host und klarere Bodyabgrenzung; Pipelining bleibt an Antwortreihenfolge gebunden.
4. **2:** gleichzeitig mehrere binäre Streams in einer TCP-Verbindung, aber weiter Abhängigkeit vom einen TCP-Bytestrom.
5. **3:** zuverlässige QUIC-Streams über UDP; der Transport kennt jetzt die getrennten Streams.

**Head-of-Line-Frage:** Bei HTTP/1.1 kann eine langsame frühe Antwort spätere Antworten aufhalten. Bei HTTP/2 kann ein fehlendes TCP-Segment mehrere HTTP-Streams blockieren. HTTP/3 vermeidet diese streamübergreifende TCP-Lücke, aber nicht jeden gemeinsamen Engpass oder jede Headerabhängigkeit.

### E-Mail

**SMTP schickt**, **POP3 holt einfach ab**, **IMAP verwaltet und synchronisiert serverseitige Postfächer**. Ein Mailprogramm kann SMTP und IMAP gleichzeitig benötigen, weil Senden und Postfachzugriff verschiedene Aufgaben sind.

Gehe das SMTP-Beispiel in der Antwort zeilenweise durch: Begrüßung → Vorstellung → Envelope-Absender → Envelope-Empfänger → DATA-Erlaubnis → Nachrichtenheader → Leerzeile → Body → Punktabschluss → Annahme → Ende. `C:`/`S:` sind nur Lesemarkierungen.

Die doppelte Punktfolge am Zeilenbeginn ist **kein Tippfehler**, sondern Dot-Stuffing. Die alleinstehende Punktzeile beendet die DATA-Übertragung; deshalb muss ein echter Punkt am Anfang einer Inhaltszeile geschützt werden.

**POP3-Falle:** `RETR` lädt nur herunter. Erst `DELE` markiert und `QUIT` aus dem passenden Zustand bestätigt die Löschphase. „POP3 löscht immer sofort jede gelesene Mail“ stimmt nicht.

**IMAP-Falle:** Eine momentane Nachrichtennummer kann sich ändern. Für dauerhafte Zuordnung sind UID und UIDVALIDITY wichtig; allein dieselbe laufende Nummer ist kein stabiler Nachweis derselben Nachricht.

### DNS

DNS ist mehr als ein Telefonbuch für IP-Adressen. Es enthält auch Mailserver, Delegationen, Aliase und weitere Daten. Die Rollen **Stub**, **rekursiver Resolver** und **autoritatives System** erklären, warum nicht das Endgerät selbst immer Root, TLD und Zone abfragen muss.

**Rekursiv:** „Beschaffe mir die endgültige Antwort.“ **Iterativ:** „Hier ist mein Wissen oder ein Verweis; frage dort weiter.“ Der rekursive Resolver kann die iterative Arbeit für den Client übernehmen.

Drei wichtige Trennungen:

- **DNS-TTL:** Wie lange darf ein Cacheeintrag verwendet werden? Nicht: Wie viele Router darf ein Paket passieren?
- **DoT/DoH:** Schutz einer Transportstrecke, insbesondere zum Resolver.
- **DNSSEC:** Prüfung signierter DNS-Daten, keine Verschlüsselung ihrer Inhalte.

## 8. Recherchehilfen, Nachvollziehbarkeit und Grenzen

Für die Theorie gibt es **keine künstliche Protokollimplementierung**. Nur die von der Aufgabe zusätzlich gewünschte Kostenrechnung liegt als ausführbares Skript im Aufgabenordner. Alle SMTP- und DNS-Abläufe sind ausdrücklich Lehrbeispiele, nicht vorgetäuschte Mitschnitte.

Zur Recherche wurden zusätzlich temporäre Hilfsskripte im Hermes-Scratch-Verzeichnis benutzt; sie gehören nicht zur Abgabe:

- `rn02_quellen_lesen.py`, **1–2**: KI-Kennzeichnung; **3–7**: Importe für Parallelabruf, Pfade, Umgebung, Regex und HTTPS; **8**: Leerzeile; **9–10**: Scratch-Cache bestimmen/anlegen; **11–27**: RFC-Nummern und gewünschte Abschnitte; **28**: Leerzeile; **29–30**: Abruffunktion und Entpacken; **31–33**: Cachepfad und nötigenfalls vollständigen RFC-Text herunterladen; **34–35**: Text lesen und Ausgabeüberschrift bauen; **36–37**: bei fehlender Abschnittsauswahl den Textanfang ausgeben; **38–40**: Abschnittsüberschriften suchen und Inhaltsverzeichnis-Zeilen ausfiltern; **41–43**: gefundenen Textausschnitt aufnehmen; **44–45**: fehlende Treffer ausdrücklich melden; **46**: Ausgabe zurückgeben; **47**: Leerzeile; **48–50**: bei Direktstart RFCs parallel abarbeiten und Ausgabe anzeigen. Nicht gefundene ältere Überschriften wurden anschließend gezielt aus den gespeicherten RFCs gelesen, nicht als erfolgreich ausgewertet.
- `rn02_zusatzquellen.py`, **1–2**: KI-Kennzeichnung; **3–7**: dieselben Importrollen; **8**: Leerzeile; **9–10**: derselbe Cache; **11**: ergänzende RFC-/Abschnittsliste; **12**: Leerzeile; **13–14**: Funktion/Entpacken; **15–17**: nur fehlende RFCs abrufen; **18–19**: Text/Überschrift; **20**: Abschnittsschleife; **21**: abweichende Einrückung von RFC 1122 berücksichtigen; **22**: eigentliche Überschriften von Inhaltsverzeichnis und nummerierten Listen unterscheiden; **23–24**: gefundenen Ausschnitt aufnehmen; **25–26**: fehlenden Treffer melden; **27**: Ergebnis zurückgeben; **28**: Leerzeile; **29–31**: parallelen Direktstart ausführen. Der Headerfilter wurde nach Kontrolle korrigiert, weil nummerierte Listen sonst mit Abschnittsnummern verwechselt werden können.

Quellenabruf und Textprüfung beweisen nicht die Funkabdeckung eines unbekannten Hauses. Preisanzeigen beweisen keinen späteren Kaufpreis. Ein als Beispiel formulierter Ablauf beweist keinen tatsächlich beobachteten Netzverkehr. Diese Grenzen sind Teil einer korrekten Erklärung.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Ergänze ein deutsches Lernverständnis-Dokument zu den Theorieaufgaben Ü 2.1, 2.2, 2.4, 2.5, 2.7, 2.8 und 2.9 mit typischen Denkfehlern, mündlichen Prüffragen und Zeilenerklärung benutzter Skripte.“
