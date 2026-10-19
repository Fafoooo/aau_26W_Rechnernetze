# Erklärung zu Übungsblatt 02

Zusammengeführte Lernfassung aus vier thematischen Quelldokumenten. Alle Angaben und Ergebnisse stehen bei den Aufgaben; hier werden Methode, jede eigene Codezeile, Tests und typische Fehler erklärt. Theorieaufgaben benötigen keinen künstlichen Programmcode.

## Lernreihenfolge

1. Internet, Schichten, Transport, WLAN, Streaming und Anwendungsprotokolle.
2. Bankomatprotokoll mit ausführlicher Referenz- und Testerklärung.
3. Sichere eigene Wireshark-Aufnahme.
4. Offline-PCAP- und HTTP-Analyse mit Diagramm und Tests.

**Grenzen:** Ü2.7 verwendet ein hypothetisches Referenzhaus, keine erfundenen persönlichen Hausdaten. Die Bankreferenz ist eine In-Memory-Simulation, kein produktives Banksystem. Die Capture-Nachweise belegen automatisierte Serverdurchführung, keine persönliche Bedienung durch Fabio.

**KI-Kennzeichnung:** Hermes Agent, OpenAI gpt-6.1-sol, 2026-10-19. Anfrage: Alle Aufgaben aus dem Originalblatt lösen, tatsächlich testen und jede eigene Codezeile zum Verstehen erläutern.

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


---

# Bankomatprotokoll Ü2.6 — schrittweise Codeerklärung

Diese Erklärung gehört zu [ue2.6/antwort.md](ue2.6/antwort.md). Sie erklärt **alle drei eigenen Python-Dateien**. Zeilennummern beziehen sich auf die hier ausgelieferten Dateien; mehrzeilige Ausdrücke werden als zusammengehörige Zeilen erklärt. **Alle nicht eigens aufgeführten Leerzeilen** trennen nur Abschnitte und werden nicht ausgeführt. Kommentare und Dokumentationszeichenketten werden ebenfalls erklärt. SVG und Mermaid sind Diagrammquellen, keine zusätzlich auszuführenden Python-Programme.

## 1. Zuerst das Modell verstehen

Ein Konto besitzt zwei verschiedene Zahlen:

- **Gebucht (`booked`):** der bisherige Kontosaldo.
- **Verfügbar (`available`):** gebucht minus noch offene Abhebungen.

Bei 10000 Cent und einer Reservierung über 4000 Cent bleiben zunächst 10000 Cent gebucht, aber nur 6000 Cent verfügbar. Erst nach eindeutiger Bestätigung wird der Buchsaldo auf 6000 Cent reduziert. Wenn sicher nichts ausgegeben wurde, wird stattdessen die Sperre aufgehoben. Wenn unklar ist, ob Geld herauskam, bleibt die Sperre bestehen.

Die Unterrichtssimulation benutzt nur Arbeitsspeicher. **Ein Lock ist keine Datenbank und kein dauerhaftes Journal.** Nach einem Prozessabsturz wären die Dictionaries weg. Es gibt keinen tatsächlichen Bankserver und keinen TLS-Handshake. Der Entwurf fordert TLS 1.3 mit gegenseitiger Prüfung; die lokale Referenz stellt diese Transportvoraussetzung nicht her.

### Python-Grundbausteine

- `def` definiert eine Funktion; `class` definiert einen Objekttyp. `self` bezeichnet das jeweilige Objekt.
- Einrückung bestimmt, welche Zeilen zu `if`, `for`, `with`, `try` oder einer Funktion gehören.
- `{}` ist ein Dictionary. `{"a", "b"}` ist eine Menge. `set()` ist eine leere Menge.
- `d["x"]` liest einen Dictionarywert; `d.get("x")` liefert bei fehlendem Schlüssel `None`.
- `=` weist zu, `==` vergleicht, `!=` prüft Ungleichheit. `is None` prüft den besonderen Leerwert.
- `and` und `or` werten von links nach rechts nur so weit wie nötig aus. Daher wird beispielsweise `len(pin)` erst aufgerufen, nachdem der Typ String bestätigt wurde.
- `type(x) is int` schließt Booleans aus. Das ist hier absichtlich strenger als `isinstance(True, int)`.
- `return` beendet eine Funktion mit einem Rückgabewert. `raise` löst eine Ausnahme aus.
- `with lock:` reserviert einen kritischen Abschnitt und gibt das Lock auch bei einer Ausnahme wieder frei.
- Ein `_` vor einem Methodennamen markiert eine interne Hilfsfunktion nach Python-Konvention, verhindert aber keinen Zugriff technisch.
- `100_000` ist dieselbe Zahl wie `100000`; der Unterstrich dient der Lesbarkeit.
- `amount % 1000 == 0` bedeutet: Der Centbetrag lässt sich ohne Rest durch 1000 teilen, ist also mit den angenommenen 10-EUR-Scheinen darstellbar.

## 2. Gemeinsamer Dateianfang

In **jeder** Python-Datei gilt:

| Zeile | Erklärung |
|---|---|
| 1 | Kommentar: verwendetes KI-Werkzeug Hermes Agent und Modell OpenAI gpt-6.1-sol. |
| 2 | Kommentar: Erstellungsdatum 2026-10-19. |
| 3–4 | Zusammengehöriger Kommentar: tatsächlicher Teilauftrag in eigenen Worten. Bei `protocol.py` der Protokollcode, bei `demo.py` die Vorführung und bei `test_protocol.py` die Tests. |
| 5 | Modul-Docstring: dokumentiert Zweck und Offline-/Unterrichtsgrenze der Datei. Er steht in dreifachen Anführungszeichen. |

## 3. `ue2.6/protocol.py` — jede Codezeile

### 3.1 Importe, Konstanten, Fehler und IDs

| Zeile | Was passiert und warum? |
|---|---|
| 6 | `hmac` liefert `compare_digest` zum Vergleich der Modell-PIN. Das ersetzt keine sichere PIN-Verarbeitung. |
| 7 | `json` wandelt Python-Daten in JSON und zurück um. |
| 8 | `struct` erzeugt und liest das binäre 4-Byte-Längenfeld. |
| 9 | `threading` liefert Locks gegen überlappende Zustandsänderungen. |
| 10 | `time` liefert die monotone Uhr für Zeitabstände ohne Wanduhrsprünge. |
| 11 | `uuid` erzeugt und prüft Identifikatoren. |
| 13 | Höchstens 4096 Nutzlastbytes pro Frame. |
| 14 | Höchstens 100000 Cent pro Abhebung. |
| 15 | Eine Sitzung lebt 300 Sekunden. |
| 16 | Eine noch nicht begonnene Reservierung lebt 60 Sekunden. |
| 17 | Die Menge HELD nennt genau die Zustände, deren Beträge weiterhin die verfügbare Deckung vermindern. |
| 20 | `Fault` erbt von `Exception` und unterscheidet erwartbare Fach-/Protokollfehler von Programmierfehlern. |
| 21 | Docstring der Fehlerklasse. Ein weiterer Klassenrumpf ist nicht nötig: Die geerbte Exception-Verwaltung speichert die übergebene Statuszeichenkette. |
| 24 | `require` erhält eine Bedingung und optional einen Fehlerstatus; Standard ist BAD_REQUEST. |
| 25 | Nur wenn die Bedingung falsch ist, wird der eingerückte Fehlerzweig ausgeführt. |
| 26 | Die Ausnahme enthält den Status. Ist die Bedingung wahr, endet die Funktion ohne Fehler. |
| 29 | `identifier` prüft eine übergebene ID. |
| 30 | Nur ein String ist zulässig; Zahlen oder `None` scheitern sofort. |
| 31 | Der folgende UUID-Konvertierungsversuch kann eine Bibliotheksausnahme auslösen. |
| 32 | `uuid.UUID` liest die ID; `str(...)` erzeugt ihre kanonische Schreibweise. Nur exakt gleiche, kleingeschriebene Schreibweise wird akzeptiert. |
| 33 | Fehler beim UUID-Parsen werden abgefangen. Ein durch `require` ausgelöster Fault bleibt dagegen ein Fault. |
| 34 | Die ungültige ID wird als BAD_REQUEST gemeldet; `from None` unterdrückt eine unnötige verkettete Bibliotheksfehlermeldung. |
| 35 | Bei Erfolg wird die unveränderte geprüfte ID zurückgegeben. Die Prüfung erzwingt Schreibweise und UUID-Syntax, nicht ausschließlich UUID-Version 4. |

### 3.2 Encoder und JSON-Hilfen

| Zeile | Erklärung |
|---|---|
| 38 | Definiert den Encoder für genau ein Nachrichtenobjekt. |
| 39 | Docstring: Längenpräfix plus UTF-8. |
| 40 | Prüft, ob das Wurzelelement ein Dictionary ist. |
| 41 | Andere Wurzeltypen werden vor dem Senden zurückgewiesen. |
| 42 | Serialisiert JSON. `ensure_ascii=False` lässt Unicodezeichen direkt zu; `allow_nan=False` verbietet nichtstandardkonforme Zahlenkonstanten. |
| 43 | Entfernt überflüssige Trenn-Leerzeichen und codiert den resultierenden String als UTF-8-Bytes. Diese Zeile beendet denselben Ausdruck wie Zeile 42. |
| 44 | Prüft die **Bytezahl** nach der Codierung. |
| 45 | Leere oder übergroße Nutzlasten werden zurückgewiesen. |
| 46 | `!I` bedeutet ein unsigned 32-Bit-Integer in Netzwerkbytefolge. Das Präfix wird mit den Nutzlastbytes verkettet. |
| 49 | JSON-Hilfsfunktion: bekommt die gelesenen Schlüssel-Wert-Paare eines Objekts. |
| 50 | Baut ein zunächst leeres Dictionary auf. |
| 51 | Geht jedes Paar einzeln durch. |
| 52 | Prüft vor dem Eintragen, ob der Schlüssel bereits vorhanden ist. |
| 53 | Ein doppelter Schlüssel ist ein Fehler; JSON darf ihn nicht stillschweigend überschreiben. |
| 54 | Ein bisher neuer Schlüssel wird mit seinem Wert gespeichert. |
| 55 | Liefert das vollständig geprüfte Dictionary. |
| 58 | Callback für von Python sonst akzeptierte Spezialkonstanten wie NaN. |
| 59 | Solche Konstanten lösen immer ValueError aus. Der Text nennt nur die Konstante, keine Bankdaten. |

### 3.3 Decoder: aus einem Bytestrom einzelne Nachrichten machen

| Zeile | Erklärung |
|---|---|
| 62 | Definiert einen Decoder mit eigenem Eingabepuffer. |
| 63 | Docstring: Fragmentierung und Zusammenfassung mehrerer Nachrichten sind erlaubt. |
| 64 | Konstruktor: läuft beim Erzeugen eines Decoders. |
| 65 | `bytearray` ist ein veränderbarer Bytepuffer. |
| 67 | `feed(data)` verarbeitet ein neues Stück des Bytestroms. |
| 68 | Hängt die neuen Bytes an vorhandene Restbytes an. |
| 69 | Sammelt alle in diesem Aufruf vollständig gelesenen Nachrichten. |
| 70 | Solange wenigstens die vier Präfixbytes vorliegen, kann eine Länge geprüft werden. |
| 71 | Liest die ersten vier Bytes mit derselben Bytefolge wie der Encoder. `[0]` holt den einen Integer aus dem von `unpack` gelieferten Tupel. |
| 72 | Prüft die angekündigte Länge, bevor auf die Nutzlast gewartet wird. |
| 73 | Eine unzulässige Länge beendet die Verarbeitung mit Fehler; ein echter Transportadapter muss die Verbindung schließen. |
| 74 | Prüft, ob Präfix **und** vollständige Nutzlast schon im Puffer liegen. |
| 75 | Falls nicht, verlässt `break` die Schleife; die Teilnachricht bleibt für den nächsten feed-Aufruf erhalten. |
| 76 | Kopiert genau die Nutzlast dieses Frames als unveränderbare Bytes. |
| 77 | Entfernt nur den vollständig entnommenen Frame aus dem Puffer; mögliche Folgeframes bleiben dort. |
| 78 | Beginnt den geschützten Decodier-/Parseversuch. |
| 79 | Decodiert UTF-8 und liest anschließend das JSON. |
| 80 | Übergibt `unique_object` als Objekthook, damit doppelte Schlüssel auffallen. |
| 81 | Übergibt `invalid_constant`, damit NaN und Infinity nicht akzeptiert werden; beendet den json.loads-Aufruf. |
| 82 | Fängt ungültiges UTF-8/JSON sowie zu tiefe Rekursion ab. UnicodeDecodeError ist eine ValueError-Unterklasse. |
| 83 | Meldet einen Verbindungsfehler und erhält mit `from exc` die Fehlerursache für die lokale Fehlersuche. |
| 84 | Auch syntaktisch gültiges JSON muss hier ein Objekt sein, nicht Array oder `null`. |
| 85 | Andernfalls ebenfalls abbrechen. |
| 86 | Nimmt ein vollständig gelesenes Objekt in die Ergebnisliste auf. |
| 87 | Gibt alle vollständigen Objekte zurück. Danach kann noch eine unvollständige Folgemeldung im Puffer stehen. |
| 89 | `eof` meldet, dass vom Transport keine Bytes mehr kommen werden. |
| 90 | Bei Restbytes ist mindestens ein Frame unvollständig. |
| 91 | Ein abgeschnittener Frame wird nicht stillschweigend als erfolgreich gelesen behandelt. |

**Beispiel zum Puffern:** Ein erster `feed` kann nur zwei Präfixbytes liefern und deshalb `[]` zurückgeben. Der nächste Aufruf ergänzt Präfix und Nutzlast. Erst dann erscheint das Objekt in der Rückgabeliste. Zwei ganze Frames im selben Aufruf erzeugen zwei Objekte. Im Fehlerfall darf der Decoder nicht weiterverwendet werden. Die Klasse ist ein Framing-Lehrbeispiel, keine umfassend gegen Speicher-/CPU-Angriffe gehärtete Netzwerkbibliothek.

### 3.4 Bankdaten, Zeit und Besitzprüfung

| Zeile | Erklärung |
|---|---|
| 94 | Definiert die Modellbank. |
| 95 | Docstring warnt ausdrücklich vor flüchtiger Speicherung. |
| 96 | Der Konstruktor erhält eine Uhrfunktion und einen Anfangssaldo. Eine injizierbare Uhr macht Zeitablauftests ohne Warten möglich. |
| 97 | Erlaubt nur echte Integer innerhalb der Anfangssaldogrenzen. |
| 98 | Ungültige lokale Konfiguration löst ValueError aus. |
| 99 | Speichert die Uhrfunktion, **nicht** nur einen einzelnen Zeitwert. |
| 100 | Erstellt ein wiedereintrittsfähiges Bank-Lock. Nur ein Thread bearbeitet zur selben Zeit den Bankzustand. |
| 101 | Beginnt das Dictionary mit einer ausdrücklich erfundenen Karte, Muster-PIN und Anfangssaldo. |
| 102 | Ergänzt den Fehlversuchszähler mit 0 und schließt den Kontodatensatz. |
| 103 | Zunächst gibt es keine Sitzungen. |
| 104 | Zunächst gibt es keine Transaktionsdatensätze. |
| 106 | Hilfsmethode für den Ablauf reiner Reservierungen. |
| 107 | Betrachtet jede bereits gespeicherte Transaktion. |
| 108 | Nur RESERVED und ein Zeitpunkt an oder nach `expires` erfüllen die Ablaufbedingung. |
| 109 | Dann wird der Zustand CANCELLED; ohne offene Sperre steigt die berechnete Verfügbarkeit wieder. DISPENSING und UNKNOWN werden nicht angerührt. |
| 111 | Berechnet die verfügbare Deckung einer bestimmten Karte. |
| 112 | Summiert Transaktionsbeträge mit einer Generator-Expression. |
| 113 | Der Generator zählt nur diese Karte und nur sperrende Zustände aus HELD. |
| 114 | Zieht die Gesamtsperre vom Buchsaldo ab. Es wird nichts am Buchsaldo geändert. |
| 116 | Prüft Sitzung und Terminalbindung. |
| 117 | Die Sitzungs-ID muss zuerst syntaktisch gültig sein. |
| 118 | Sucht den Sitzungsdatensatz oder erhält `None`. |
| 119 | Unterscheidet eine fehlende Sitzung ausdrücklich. |
| 120 | Meldet dann UNAUTHORIZED. |
| 121 | Eine Sitzung eines anderen Terminals darf nicht übernommen werden. |
| 122 | Die aktuelle Zeit muss **kleiner** als das Ablaufdatum sein. Gleichheit bedeutet bereits SESSION_EXPIRED. |
| 123 | Liefert die Karte, für die die Sitzung berechtigt ist. |
| 125 | Prüft die Besitzbindung einer Transaktion. |
| 126 | Prüft die Transaktions-ID syntaktisch. |
| 127 | Sucht den Transaktionsdatensatz. |
| 128 | Prüft, ob er überhaupt vorhanden ist. |
| 129 | Eine unbekannte Transaktion liefert NOT_FOUND. |
| 130 | Vergleicht Karte und Terminal gemeinsam; beide müssen zur Sitzung passen. |
| 131 | Gibt nur einen berechtigten Datensatz zurück. |
| 133 | Erzeugt die öffentliche Sicht einer Transaktion. |
| 134 | Enthält ID, Centbetrag und EUR. |
| 135 | Ergänzt den aktuellen Zustand; interne Karte, Terminal und Ablaufzeit werden nicht ausgegeben. |

### 3.5 Zentraler Nachrichtenverteiler `handle`

| Zeile | Erklärung |
|---|---|
| 137 | Definiert den Einstiegspunkt für bereits geparste Anfragen; der Terminalparameter ist ein lokaler Vertrauens-Stellvertreter. |
| 138 | Docstring: In einem echten Adapter dürfte hier nur eine durch mTLS bereits geprüfte Identität stehen. |
| 139 | Sperrt die gesamte Validierung und Zustandsänderung gegen parallele Bankoperationen. |
| 140 | Solange keine gültige Anfrage-ID bekannt ist, lautet die Antwort-ID `None` beziehungsweise JSON-null. |
| 141 | Erwartbare Fault-Ausnahmen werden im folgenden Block zu Protokollantworten umgewandelt. |
| 142 | Nur ein Dictionary darf als Anfrage verarbeitet werden. |
| 143 | Vergleicht die Menge der Schlüssel mit den exakt vorgeschriebenen Umschlagfeldern. |
| 144 | Prüft die Anfrage-ID und merkt sie für die Antwort vor. |
| 145–146 | Version muss ein Integer und gleich 1 sein, sonst BAD_VERSION. Ein Boolean scheitert am Typ. |
| 147 | Prüft die Modellgrenzen der bereits vom Adapter kommenden Terminalkennung. |
| 148 | Liest Operation und Nachrichtenkörper aus dem Umschlag. |
| 149 | Der Operationsname muss String und der Körper Dictionary sein. |
| 150 | Startet die Schemaübersicht: AUTH braucht Karte/PIN, BALANCE keine Körperfelder. |
| 151 | RESERVE braucht ID/Betrag, BEGIN nur ID. |
| 152 | RESULT braucht ID/Ergebnis, STATUS nur ID. |
| 153 | CANCEL braucht ID, LOGOUT hat einen leeren Körper. |
| 154 | Ein nicht definierter Operationsname wird mit UNKNOWN_OP abgelehnt. |
| 155 | Vergleicht die tatsächlichen Körperfelder exakt mit dem Schema dieser Operation. |
| 156 | Lässt abgelaufene reine Reservierungen auslaufen, bevor weitere Fachoperationen erfolgen. |
| 157 | AUTH besitzt einen eigenen Zweig, weil noch keine Sitzung existiert. |
| 158 | AUTH muss `sid=null` enthalten. |
| 159 | Führt die Benutzerprüfung aus. |
| 160 | Alle übrigen Operationen laufen durch den anderen Zweig. |
| 161 | Prüft die Sitzung und ermittelt ihre berechtigte Karte. |
| 162 | Übergibt ausschließlich den geprüften Kontext an den Fachverteiler. |
| 163 | Verpackt den erfolgreichen Fachinhalt in den Antwortumschlag. OK kann beispielsweise auch eine fachlich abgelehnte Abhebung mit DECLINED enthalten. |
| 164 | Fängt nur erwartbare Fault-Fehler ab, nicht pauschal jede Programmierausnahme. |
| 165 | Liefert den Fehlerstatus mit leerem Körper und der bislang validierten Anfrage-ID zurück. |

`_expire` ist eine erlaubte Wartungsaktion: Bei einer inzwischen abgelaufenen Reservierung kann ein späteres gültig aufgebautes Telegramm deren Zustand auf CANCELLED setzen, auch wenn seine Sitzung anschließend als abgelaufen erkannt wird. Das ist keine durch eine unberechtigte Sitzung ausgelöste Auszahlung oder Abbuchung.

### 3.6 Karte und PIN prüfen

| Zeile | Erklärung |
|---|---|
| 167 | Beginnt die Benutzerprüfung. |
| 168 | Entnimmt die beiden bereits als vorhanden geprüften Körperfelder. |
| 169 | Die Kartenkennung muss eine begrenzte Zeichenkette sein. |
| 170 | PIN muss String mit genau vier ASCII-Ziffern sein. Nicht-ASCII-Ziffern und Integer sind nicht erlaubt. |
| 171 | Sucht die fiktive Karte in der Kontotabelle. |
| 172 | Verzweigt bei unbekannter Karte. |
| 173 | Gibt bewusst denselben Fehler wie bei falscher/gesperrter PIN zurück. |
| 174 | Drei schon gespeicherte Fehler verhindern jede weitere erfolgreiche Anmeldung im Modell. |
| 175 | Vergleicht die übergebene PIN mit der Muster-PIN. `not` wählt den falschen-PIN-Fall. |
| 176 | Zählt einen syntaktisch gültigen Fehlversuch hinzu. |
| 177 | Verwirft die Anmeldung ohne Sitzung. |
| 178 | Nach erfolgreicher Anmeldung vor Sperrung wird der Zähler zurückgesetzt. |
| 179 | Erzeugt eine zufällige Sitzungs-UUID. |
| 180 | Speichert Karte und Terminal als Besitzbindung der Sitzung. |
| 181 | Ergänzt den absoluten Ablaufzeitpunkt anhand der injizierten monotonen Uhr. |
| 182 | Gibt die neue Sitzung und ihre relative Lebensdauer zurück. |

**Grenze:** Die PIN wird im Lehrcode im Klartext gespeichert. Die Vergleichsfunktion allein macht das nicht produktionssicher. Die Sperre betrifft neue Anmeldungen; bestehende Sitzungen werden hier nicht widerrufen.

### 3.7 Fachoperationen und Idempotenz

| Zeile | Erklärung |
|---|---|
| 184 | `_dispatch` erhält schon geprüfte Sitzung/Karte/Terminal. |
| 185 | Erkennt LOGOUT. |
| 186 | Entfernt genau diese Sitzung. |
| 187 | LOGOUT ist damit abgeschlossen und gibt einen leeren Antwortkörper zurück. |
| 188 | Erkennt die Kontostandsabfrage. |
| 189 | Liest den gebuchten Saldo. |
| 190 | Ergänzt den verfügbaren Saldo und die Währung; beendet BALANCE ohne Transaktionsänderung. |
| 191 | Alle verbleibenden Operationen benötigen eine geprüfte Transaktions-ID. |
| 192 | Erkennt RESERVE. |
| 193 | Liest den gewünschten Centbetrag. |
| 194 | Beginnt die Betragsprüfung: echter Integer, positiv, nicht über dem Einzellimit. |
| 195 | Verlangt zusätzlich 10-EUR-Stückelung; Verletzungen liefern BAD_AMOUNT. |
| 196 | Prüft, ob diese fachliche Transaktion schon bekannt ist. |
| 197 | Ein vorhandener Datensatz wird nur nach Besitzprüfung verwendet. |
| 198 | Der Betrag darf unter derselben ID nicht geändert werden. |
| 199 | Nur bei einer neuen ID wird eine neue Transaktion angelegt. |
| 200 | Vergleicht Betrag mit verfügbarer Deckung; entscheidet RESERVED oder DECLINED. |
| 201 | Beginnt den neuen Datensatz mit Besitzer, Terminal und Betrag. |
| 202 | Speichert Zustand und Ablaufzeit. Die Ablaufzeit wird nur im Zustand RESERVED benutzt. |
| 203 | Trägt den Datensatz unter der eindeutigen ID ein. Ein abgelehnter Versuch bleibt ebenfalls gespeichert. |
| 204 | Liefert die öffentliche Sicht. Beim Retry wird kein Betrag erneut reserviert. |
| 205 | Für alle anderen Transaktionsoperationen muss ein passender Datensatz existieren. |
| 206 | Merkt den Zustand vor einer möglichen Änderung. |
| 207 | Erkennt BEGIN. |
| 208 | Erlaubt nur den ersten Beginn aus RESERVED oder eine harmlose Wiederholung in DISPENSING. |
| 209 | Setzt DISPENSING; ab jetzt ist automatischer Reservierungsablauf ausgeschlossen. |
| 210 | Erkennt CANCEL als anderen Operationsfall. |
| 211 | Erlaubt Abbruch nur vor der Auszahlung oder Wiederholung eines schon abgebrochenen Vorgangs. |
| 212 | CANCELLED wird nicht mehr in die Sperrsumme eingerechnet. Es wird nichts vom Buchsaldo abgezogen. |
| 213 | Erkennt die Ergebnisnachricht RESULT. |
| 214 | Entnimmt das gemeldete Ergebnis. |
| 215 | Erlaubt nur die drei definierten Ergebniszeichenketten. |
| 216 | Übersetzt Ergebnis in Bankzielzustand: OK→COMMITTED, FAIL→CANCELLED, UNKNOWN→UNKNOWN. |
| 217 | **Entscheidende Deduplizierung:** Nur bei einem noch nicht erreichten Zielzustand wird der folgende Änderungsblock betreten. |
| 218 | Für einen neuen Ergebnisübergang muss der bisherige Zustand DISPENSING sein. UNKNOWN darf vom normalen Client nicht nachträglich aufgelöst werden. |
| 219 | Nur OK löst eine Buchung aus. |
| 220 | Zieht den Transaktionsbetrag genau beim ersten Übergang zum Erfolg ab. |
| 221 | Speichert danach den Zielzustand. Buchung und Zustand sind innerhalb desselben Locks geändert. |
| 222 | Gibt den aktuellen Zustand zurück. STATUS benötigt keinen eigenen Änderungszweig und gelangt direkt hierher. |

**Warum keine doppelte Abbuchung?** Das erste RESULT OK sieht DISPENSING, subtrahiert den Betrag und setzt COMMITTED. Das zweite RESULT OK findet bereits `state == target`; die Zeilen 218–221 werden nicht erneut ausgeführt. Widersprüchliches FAIL nach COMMITTED würde zwar ein anderes Ziel haben, scheitert aber an Zeile 218. Dasselbe Prinzip schützt den verbleibenden Buchsaldo auch bei konkurrierenden Threads.

**Feine Unterscheidung:** Ein RESULT FAIL in einem bereits CANCELLED genannten Endzustand ist finanziell wirkungslos, auch wenn CANCELLED ursprünglich durch CANCEL oder Ablauf erreicht wurde. Es stellt insbesondere keine Auszahlungserlaubnis her.

### 3.8 Unklare Auszahlung extern klären

| Zeile | Erklärung |
|---|---|
| 224 | Definiert eine lokale Modellfunktion, nicht eine neue Netzwerkoperation. |
| 225 | Docstring fordert eine vertrauenswürdige unabhängige Prüfinstanz. |
| 226 | Klärung und normale Bankanfragen benutzen dasselbe Lock. |
| 227 | Das Prüfergebnis muss ausdrücklich boolesch sein. |
| 228 | Die zu klärende Transaktion muss existieren. |
| 229 | Holt ihren Datensatz. |
| 230 | Nur noch offene/unklare Auszahlungen dürfen geklärt werden. Ein zweiter Aufruf nach einem Abschluss scheitert. |
| 231 | Wählt den nachgewiesenen-Auszahlung-Fall. |
| 232 | Bucht dann den noch nicht verbuchten Betrag ab. |
| 233 | Setzt COMMITTED bei belegter Ausgabe, andernfalls CANCELLED; in beiden Fällen entfällt die Sperre. |

Ein echtes Prüfsystem müsste unterscheiden können, wie viel tatsächlich ausgegeben wurde. Dieses Unterrichtsmodell kennt nur vollständig/nicht vollständig und parkt Teilzahlungen in UNKNOWN, bis außerhalb des Protokolls geklärt wurde.

### 3.9 Auszahler mit Journal

| Zeile | Erklärung |
|---|---|
| 236 | Definiert den simulierten Auszahler. Er ist bewusst getrennt von der Bank. |
| 237 | Docstring: Das Journal ist nur flüchtig und keine echte Hardwareansteuerung. |
| 238 | Konstruktor. |
| 239 | Speichert für jede ausprobierte `tx` Betrag und Ergebnis. |
| 240 | Zählt simuliert ausgegebene Cent, anfangs 0. Das ist kein Kontosaldo. |
| 241 | Verhindert parallele doppelte Hardwareversuche am selben Modellobjekt. |
| 243 | `dispense` simuliert einen Auszahlversuch; der Parameter `outcome` injiziert einen Testausgang und ist keine Benutzerentscheidung eines echten Automaten. |
| 244 | Journalprüfung und Ausgabe liegen im selben kritischen Abschnitt. |
| 245 | Prüft die Transaktions-ID. |
| 246–247 | Prüft Centbetrag, Höchstgrenze und angenommene Stückelung. |
| 248 | Akzeptiert nur einen der drei simulierten Hardwareausgänge. |
| 249 | Prüft zuerst, ob ein Versuch für dieselbe ID schon bekannt ist. |
| 250 | Zerlegt dessen gespeichertes Tupel in Betrag und Ergebnis. |
| 251 | Dieselbe ID mit anderem Betrag wäre eine widersprüchliche Anforderung. |
| 252 | Ein Wiederholungsaufruf liefert **nur** das alte Ergebnis; der folgende Ausgabeblock wird nicht erreicht. |
| 253 | Trägt vor jeder simulierten Wirkung zunächst UNKNOWN ein. In einer echten Implementierung müsste genau dieser Schritt dauerhaft und absturzfest sein. |
| 254 | Nur der simulierte eindeutige Erfolgsfall erzeugt Bargeldwirkung. |
| 255 | Erhöht den Ausgabenzähler einmal um den Betrag. |
| 256 | Speichert das simulierte Endergebnis des einen Versuchs. |
| 257 | Gibt dieses Ergebnis zur späteren RESULT-Nachricht zurück. |

Bei UNKNOWN erhöht die Simulation `cash` nicht; das ist lediglich ihre gewählte Testwelt. Ein realer unklarer Zustand sagt gerade **nicht**, dass sicher kein Geld geflossen ist. Deshalb darf aus `dispenser.cash == 0` in einem UNKNOWN-Test keine reale Sicherheitsbehauptung abgeleitet werden.

### 3.10 Nachrichten bauen und lokal austauschen

| Zeile | Erklärung |
|---|---|
| 260 | Komfortfunktion für einen vollständigen Anfrageumschlag; Körper und Sitzung sind optional. |
| 261 | Setzt Version 1, eine neue Anfrage-UUID, Operation und Sitzung. |
| 262 | Fehlender Körper wird `{}`; ein ausdrücklich angegebener anderer Körper bleibt unverändert, damit die Validierung ihn gegebenenfalls ablehnt. |
| 265 | Definiert den lokalen Austausch mit einer Bankinstanz. |
| 266 | Warnt ausdrücklich: Framing ist vorhanden, Netzwerk/TLS sind es nicht. |
| 267 | Encoder und neuer Decoder bilden die Hinrichtung nach. `[0]` liest das eine vollständige Objekt. |
| 268 | Übergibt die geparste Nachricht und den simulierten Transportkontext an die Bank. |
| 269 | Encodiert und decodiert auch die Antwort, sodass beide Richtungen das Nachrichtenformat tatsächlich durchlaufen. |

## 4. `ue2.6/demo.py` — jede Codezeile

Zeilen 1–5 sind unter Abschnitt 2 erklärt.

| Zeile | Erklärung |
|---|---|
| 6 | Importiert den UUID-Generator für Transaktions-IDs. |
| 8 | Importiert Bank, Auszahler und Nachrichtenhilfen aus der benachbarten Datei. |
| 11 | Definiert den vollständigen Vorführablauf. |
| 12 | Erstellt ein frisches Modellkonto mit 10000 Cent. |
| 13 | Erstellt einen frischen simulierten Auszahler. |
| 14 | Baut AUTH mit Musterkarte/PIN, führt den gerahmten lokalen Austausch aus und liest die neue Sitzung aus dem Antwortkörper. Diese Sitzung wird nicht ausgegeben. |
| 16 | Innere Hilfsfunktion für nachfolgende Anfragen; sie kennt `bank` und `sid` aus dem umgebenden main-Aufruf. |
| 17 | Erzeugt eine Anfrage mit der gültigen Sitzung und holt die Antwort. |
| 18 | Druckt Operation, Status und Antwortkörper; AUTH läuft absichtlich nicht über diese Druckfunktion. |
| 19 | Prüft den technischen/Fachaufrufstatus, nicht nur den zurückgegebenen Geldzustand. |
| 20 | Bricht bei einem unerwarteten Protokollfehler ab. |
| 21 | Gibt sonst den fachlichen Körper an den aufrufenden Ablauf weiter. |
| 23 | Kennzeichnet die Ausgabe klar als lokale Unterrichtssimulation ohne TLS. |
| 24 | Meldet den AUTH-Erfolg, ohne PIN oder Sitzungstoken auszugeben. |
| 25 | Fragt den anfänglichen Kontostand ab. |
| 26 | Erzeugt eine neue Transaktions-UUID, die nun für alle Schritte derselben Abhebung erhalten bleibt. |
| 27 | Reserviert 4000 Cent und verlangt als Vorbedingung den Zustand RESERVED. |
| 28 | Beginnt dieselbe Auszahlung und verlangt DISPENSING. |
| 29 | Führt genau einen simulierten Hardwareversuch für diese ID aus; Standardergebnis ist OK. |
| 30 | Speichert die vollständige RESULT-Nachricht einschließlich Anfrage-ID. |
| 31 | Sendet sie einmal; die Bank verarbeitet und bucht, aber der Rückgabewert wird absichtlich weggeworfen. Dies simuliert eine verlorene Antwort, nicht eine verlorene Anfrage. |
| 32 | Erklärt diesen künstlich erzeugten Fehler in der Konsolenausgabe. |
| 33 | Sendet exakt dieselbe Nachricht erneut. Der Auszahler wird **nicht** erneut aufgerufen. |
| 34 | Druckt den Ergebniszustand des Retries. |
| 35 | Kontrolliert, dass die Transaktion abgeschlossen ist. |
| 36 | Fragt den tatsächlichen Modell-Endsaldo ab. |
| 37 | Prüft beide Seiten: 6000 Cent gebucht und genau 4000 Cent ausgegeben. Eine zweite Abbuchung oder Ausgabe würde auffallen. |
| 38 | Startet einen anderen, ausdrücklich neuen Versuch über 7000 Cent unter einer anderen ID. Das ist mehr als die verfügbaren 6000 Cent. |
| 39 | Verlangt DECLINED und startet danach keinen BEGIN-/Auszahleraufruf. |
| 40 | Erklärt die Ablehnung ohne Bargeld- oder Buchungswirkung. |
| 41 | Beendet die Sitzung. |
| 42 | Druckt den erfolgreichen Abschluss der eingebauten Prüfungen und die simulierte Ausgabe. |
| 45 | `__name__ == "__main__"` erkennt den direkten Programmstart; beim Import soll die Demo nicht automatisch laufen. |
| 46 | Startet nur in diesem Fall main. |

Die `assert`-Prüfungen in der Demo sind zusätzliche Lernkontrollen. Mit Python-Optimierung (`-O`) wären sie deaktiviert. Die angegebenen Startbefehle benutzen deshalb kein `-O`; die eigentliche automatisierte Absicherung steht in unittest.

## 5. `ue2.6/test_protocol.py` — jede Codezeile

### 5.1 Wie die Tests funktionieren

`unittest.TestCase` bietet Assertions. `assertEqual(ist, soll)` vergleicht Werte, `assertTrue(...)` verlangt eine wahre Bedingung, `assertRaises(Typ)` erwartet eine Ausnahme. Ein fehlgeschlagenes Assertion markiert den Test als fehlgeschlagen. Jede `test_...`-Methode ist ein automatisch auffindbarer Test. **Die jeweilige `def test_...`-Zeile benennt und definiert genau den anschließend beschriebenen Fall.**

`subTest` nennt einzelne Eingaben bei Fehlern und erlaubt mehrere Unterfälle innerhalb einer Testmethode. `setUp` läuft vor **jeder** Testmethode von BankTests; dadurch beeinflussen sich die Konten und Sitzungen nicht gegenseitig. `ThreadPoolExecutor` führt Aufgaben auf mehreren Threads aus. Diese Tests prüfen Serialisierung innerhalb eines Prozesses, keine verteilte Datenbank und keinen Crash.

### 5.2 Imports und Framingtests

Zeilen 1–5 sind unter Abschnitt 2 erklärt.

| Zeile(n) | Erklärung, in Ausführungsreihenfolge |
|---|---|
| 6 | Importiert Thread-Pools für Paralleltests. |
| 7 | Importiert struct, um Präfixe unabhängig zu bauen/zu prüfen. |
| 8 | Importiert das Testframework. |
| 9 | Importiert UUID-Erzeugung. |
| 11–12 | Importieren die zu testenden Klassen, Grenzen und Nachrichtenfunktionen aus protocol.py; die Klammern erlauben den mehrzeiligen Import. |
| 15 | Definiert eine Hilfsfunktion für neue IDs. |
| 16 | Liefert eine neue UUID als String. |
| 19 | Gruppiert die Framingfälle in einer TestCase-Klasse. |
| 20 | Definiert den Unicode-/Roundtrip-Test. |
| 21 | Erzeugt Text mit Umlaut und Eurozeichen, dessen UTF-8-Länge von der Zeichenzahl abweicht. |
| 22 | Encodiert/decodiert und erwartet exakt die ursprüngliche Ein-Objekt-Liste. |
| 23 | Liest das Längenpräfix und vergleicht es mit der gesamten Framegröße minus vier Präfixbytes. |
| 25 | Definiert den Test jeder möglichen Aufteilung. |
| 26 | Erzeugt einen Frame mit Mehrbytezeichen. |
| 27 | Geht alle Schnittstellen von 0 bis einschließlich Frameende durch. |
| 28 | Beginnt pro Schnittstelle mit einem frischen Decoder. |
| 29 | Liefert erst den vorderen, dann den hinteren Teil und verbindet beide Ergebnislisten. |
| 30 | Fordert genau eine unveränderte Nachricht. |
| 31 | Fordert zusätzlich einen sauberen, restlosen Streamabschluss. |
| 33 | Definiert den streng byteweisen Test. |
| 34 | Legt Decoder und leere Gesamtergebnisliste an. |
| 35 | Iteriert über die Bytewerte eines gültigen Frames. |
| 36 | `bytes([byte])` macht aus dem Integer ein einzelnes Byte; neue vollständige Meldungen werden angehängt. |
| 37 | Trotz vieler Teilaufrufe muss genau eine korrekte Nachricht entstehen. |
| 39 | Definiert den Test zusammengefasster Frames. |
| 40–41 | Verkettet zwei komplette Frames und verlangt zwei getrennte, richtig geordnete Objekte. |
| 43 | Definiert den Test unzulässiger Längenpräfixe. |
| 44 | Prüft Null, die erste zu große Länge und den größten 32-Bit-Wert. |
| 45 | Benennt den Unterfall und verlangt ValueError. |
| 46 | Übergibt nur das präparierte Präfix; der Fehler muss schon ohne Warten auf Payload auftreten. |
| 48 | Definiert den Test ungültiger JSON-/UTF-8-Inhalte. |
| 49 | Enthält abgeschnittenes JSON, falschen Wurzeltyp, ungültiges UTF-8, doppelte Schlüssel und NaN. |
| 50 | Ergänzt positive/negative Infinity und null. Zusammen mit Zeile 49 ist das eine Schleifen-Eingabeliste. |
| 51 | Benennt jeden Rohdatenfall und erwartet ValueError. |
| 52 | Baut ein **korrektes** Präfix zur absichtlich falschen Nutzlast; der Fehler muss deshalb am Inhalt erkannt werden. |
| 54 | Definiert den Test für Verbindungsende mitten im Frame. |
| 55 | Prüft ein einzelnes Präfixbyte und einen sonst gültigen Frame mit fehlendem Schlussbyte. |
| 56 | Erzeugt einen frischen Decoder. |
| 57 | Liefert die unvollständigen Bytes; das darf zunächst nur puffern. |
| 58 | Ab dem ausdrücklichen Streamende wird ein Fehler erwartet. |
| 59 | `eof()` erkennt die übrig gebliebenen Bytes. |
| 61 | Definiert den Encoder-Fehlertest. |
| 62 | Probiert Array statt Objekt, nicht endliche Zahl und übergroßen JSON-Text. |
| 63 | Markiert den Fall und erwartet ValueError. |
| 64 | Führt die absichtlich ungültige Codierung aus. |
| 66 | Definiert den Test an der exakt zulässigen Maximalgrenze. |
| 67 | Zieht die festen JSON-Syntaxbytes von 4096 ab und füllt den Rest mit ASCII-Zeichen; damit ist die Nutzlast genau maximal lang. |
| 68 | Prüft die Framegröße: Nutzlast plus vier Präfixbytes. |
| 69 | Prüft, dass die gültige Grenzgröße nicht versehentlich abgelehnt wird. |

### 5.3 Bank-Testaufbau und Hilfsfunktionen

| Zeile | Erklärung |
|---|---|
| 72 | Definiert die Testgruppe für die Bankzustandsmaschine. |
| 73 | `setUp` bereitet jeden einzelnen Banktest neu vor. |
| 74 | Setzt die simulierte Uhr zunächst auf 1000 Sekunden. |
| 75 | `lambda: self.now` liest bei jedem Aufruf den aktuellen Testwert. Die neue Bank startet mit 10000 Cent. |
| 76 | Meldet die Musterkarte an und speichert ihre Sitzung. |
| 77 | Erzeugt die ID des Test-Abhebeversuchs. |
| 79 | Definiert die AUTH-Hilfe mit auswählbarem Terminal. |
| 80 | Führt die korrekte Musteranmeldung aus. |
| 81 | Verlangt AUTH-Erfolg; ein Fehler im Testaufbau wird dadurch sofort sichtbar. |
| 82 | Gibt die Sitzung an den jeweiligen Test zurück. |
| 84 | Definiert eine allgemeine Anfragehilfe mit optionaler Sitzung und Terminal. |
| 85 | Verwendet standardmäßig die Test-Sitzung; bei explizitem Parameter die andere Sitzung. Führt den gerahmten Austausch aus. |
| 87 | Definiert eine Hilfe für erwartete erfolgreiche Fachaufrufe. |
| 88 | Führt die Anfrage aus. |
| 89 | Prüft OK und gibt bei Fehlern die komplette Antwort als Testdiagnose mit. |
| 90 | Gibt nur den fachlichen Körper zurück. |
| 92 | Definiert die Reservierungshilfe mit Standardbetrag 4000 Cent. |
| 93 | Reserviert mit der bereits vorbereiteten Test-ID. |
| 95 | Definiert eine Hilfe für „reserviert und begonnen“. |
| 96 | Reserviert zunächst. |
| 97 | Sendet BEGIN für dieselbe ID und liefert den Antwortkörper. |
| 99 | Definiert die Ergebnishilfe. |
| 100 | Sendet RESULT mit dem vom Test vorgegebenen Ergebnis. |

### 5.4 Erfolgsfall, Beträge und Wiederholungen

| Zeile(n) | Erklärung |
|---|---|
| 102 | Definiert die vollständige erfolgreiche Bankabhebung. |
| 103 | Reservierung muss RESERVED ergeben. |
| 104 | Buchsaldo bleibt 10000, verfügbar ist nur 6000, Währung ist EUR. |
| 105 | BEGIN muss DISPENSING ergeben. |
| 106 | OK muss COMMITTED ergeben. |
| 107 | Genau 4000 Cent müssen abgebucht worden sein. |
| 108 | Es darf danach keine zusätzliche Sperre übrig bleiben: verfügbar ebenfalls 6000. |
| 110 | Definiert Ablehnung wegen fehlender Deckung. |
| 111 | Fordert 11000 Cent bei nur 10000 Cent Anfangsdeckung. |
| 112 | Ergebnis muss DECLINED sein. |
| 113 | Retry derselben ID und desselben Betrags muss denselben fachlichen Zustand liefern. |
| 114 | Verfügbarkeit muss unverändert 10000 sein. |
| 115 | Eine abgelehnte Transaktion darf nicht nach BEGIN wechseln. |
| 117 | Definiert die genau ausgeschöpfte Deckung. |
| 118 | Reserviert exakt 10000 Cent. |
| 119 | Beginnt die Ausgabe. |
| 120 | Bestätigt Erfolg. |
| 121 | Erwartet exakt Null, keine Überziehung. |
| 123 | Definiert ungültige Abhebebeträge. |
| 124 | Prüft Boolean, Null, negative Zahl, falsche Stückelung, Betrag über Grenze, Float, String und None. |
| 125 | Benennt den jeweiligen Unterfall. |
| 126 | Verwendet für jeden ungültigen Betrag eine frische Transaktions-ID. |
| 127 | Verlangt BAD_AMOUNT. |
| 128 | Kein ungültiger Versuch darf überhaupt einen Transaktionsdatensatz anlegen. |
| 130 | Definiert die zulässige Einzelbetragsobergrenze. |
| 131 | Erhöht nur den Testfixture-Saldo direkt auf die nötige Deckung; dies ist keine zusätzliche Protokolloperation. |
| 132 | Der Maximalbetrag 100000 muss zugelassen werden. |
| 134 | Definiert RESERVE-/BEGIN-Wiederholungen. |
| 135 | Speichert die erste Reservierungsantwort. |
| 136 | Wiederholt die nächste Prüfung fünfmal; `_` ist ein bewusst nicht benutzter Schleifenzähler. |
| 137 | Jedes erneute RESERVE muss dieselbe Reservierung zeigen. |
| 138 | Beginnt anschließend den einen Versuch. |
| 139 | Ein erneutes RESERVE darf nicht zurück auf RESERVED setzen, sondern muss DISPENSING zeigen. |
| 140 | BEGIN-Retry bleibt DISPENSING. |
| 141 | Es gibt trotz aller Wiederholungen nur eine 4000-Cent-Sperre. |
| 143 | Definiert denselben Versuch mit widersprüchlichem Betrag. |
| 144 | Legt zuerst 4000 Cent fest. |
| 145 | Fordert unter derselben ID 5000; verlangt TX_CONFLICT. |
| 146 | Die ursprüngliche Sperre bleibt unverändert. |
| 148 | Definiert den Fall „verlorene Antwort, identische Anfrage nochmals“. |
| 149 | Stellt DISPENSING her. |
| 150 | Baut eine bestimmte RESULT-OK-Nachricht mit fester Anfrage-ID. |
| 151 | Sendet sie einmal und speichert die Antwort nur als Vergleichswert; der gedachte Client hat sie nicht gesehen. |
| 152 | Exakter Retry muss exakt dieselbe Antwort ergeben. |
| 153 | Nur einmalige Abbuchung: 6000 Cent Rest. |
| 155 | Definiert einen fachlich gleichen Retry mit neuer Anfrage-ID. |
| 156 | Stellt DISPENSING her. |
| 157 | Erster RESULT-OK-Aufruf. |
| 158 | Zweiter Aufruf über `finish`; `request` erzeugt dabei eine **neue** Anfrage-ID. |
| 159 | Selbst ein späteres RESERVE derselben Transaktion zeigt COMMITTED. |
| 160 | Buchsaldo bleibt 6000; Transaktions-ID, nicht Anfrage-ID, schützt die Fachwirkung. |
| 162 | Definiert einen widersprüchlichen Ergebnis-Retry. |
| 163 | Beginnt den Versuch. |
| 164 | Schließt ihn erfolgreich ab. |
| 165 | Ein späteres FAIL darf COMMITTED nicht überschreiben. |
| 166 | Es findet insbesondere keine Rückerstattung oder erneute Abbuchung statt. |
| 168 | Definiert sicher fehlgeschlagene Ausgabe. |
| 169 | Beginnt die Abhebung. |
| 170 | FAIL muss CANCELLED ergeben. |
| 171 | Wiederholtes FAIL bleibt wirkungslos. |
| 172 | Die gesamte Deckung muss wieder verfügbar sein. |

### 5.5 Unklarheit, Klärung, Abbruch und Zeitgrenzen

| Zeile(n) | Erklärung |
|---|---|
| 174 | Definiert UNKNOWN einschließlich unzulässiger Client-Selbstklärung. |
| 175 | Beginnt die Ausgabe. |
| 176 | Erstes UNKNOWN wird gespeichert. |
| 177 | Wiederholtes UNKNOWN ist erlaubt. |
| 178 | Beginnt die Liste unzulässiger Fortsetzungen mit CANCEL. |
| 179 | Ergänzt nachträgliches RESULT OK. |
| 180 | Ergänzt nachträgliches RESULT FAIL und schließt die Schleifenliste. |
| 181 | Alle drei Versuche müssen INVALID_STATE ergeben. |
| 182 | Die 4000-Cent-Sperre bleibt vorhanden. |
| 184 | Definiert Klärung mit belegter tatsächlicher Auszahlung. |
| 185 | Beginnt den Versuch. |
| 186 | Markiert ihn als unklar. |
| 187 | Die unabhängige lokale Prüfinstanz bestätigt ausgegeben. |
| 188 | STATUS muss nun COMMITTED zeigen. |
| 189 | Buchsaldo ist 6000. |
| 190 | Eine erneute Klärung muss eine Fault-Ausnahme erzeugen. |
| 191 | Führt genau diesen verbotenen zweiten Klärungsaufruf aus. |
| 192 | Trotz Fehler bleibt der Saldo 6000. |
| 194 | Definiert Klärung mit belegter Nichtauszahlung. |
| 195 | Beginnt den Versuch; ein fehlendes RESULT kann schon DISPENSING offenlassen. |
| 196 | Die Prüfinstanz bestätigt sicher nicht ausgegeben. |
| 197 | Verfügbarkeit wird vollständig wiederhergestellt. |
| 198 | STATUS zeigt CANCELLED. |
| 200 | Definiert normalen Abbruch vor Ausgabe und dessen Wiederholung. |
| 201 | Reserviert zunächst. |
| 202 | Erster CANCEL löst die Sperre. |
| 203 | Zweiter CANCEL darf keine weitere Wirkung haben. |
| 204 | RESERVE mit alter ID darf den abgebrochenen Versuch nicht wiederbeleben. |
| 205 | Gesamte Deckung ist frei. |
| 207 | Definiert verbotenen Abbruch nach Beginn. |
| 208 | Stellt DISPENSING her. |
| 209 | CANCEL wird abgelehnt, da schon Bargeld geflossen sein könnte. |
| 211 | Definiert eine zu frühe Erfolgsmeldung. |
| 212 | Reserviert, beginnt aber nicht. |
| 213 | RESULT OK darf nicht direkt RESERVED→COMMITTED springen. |
| 215 | Definiert die genaue Reservierungsablaufgrenze. |
| 216 | Reserviert. |
| 217 | Verschiebt die Testuhr genau um die erlaubte Reservierungsdauer. Kein echtes Warten nötig. |
| 218 | Schon an der Grenze muss die reine Reservierung CANCELLED sein. |
| 219 | Deckung wird freigegeben. |
| 220 | Ein verspätetes BEGIN darf die alte ID nicht aktivieren. |
| 222 | Definiert, dass eine begonnene Auszahlung niemals automatisch abläuft. |
| 223 | Beginnt den Versuch. |
| 224 | Verschiebt die Uhr weit über Sitzungs- und Reservierungsfrist. |
| 225 | Meldet sich erneut an, weil die alte Sitzung abgelaufen ist. |
| 226 | Transaktion bleibt DISPENSING. |
| 227 | Die Deckung bleibt gebunden. |
| 229 | Definiert dieselbe Nichtablaufregel für UNKNOWN. |
| 230 | Beginnt. |
| 231 | Meldet UNKNOWN. |
| 232 | Verschiebt die Uhr deutlich nach vorn. |
| 233 | Holt eine neue Sitzung am gleichen Terminal. |
| 234 | Zustand bleibt UNKNOWN. |
| 235 | Sperre bleibt erhalten. |
| 237 | Definiert Sitzungsablauf mit erlaubter späterer Fortsetzung. |
| 238 | Beginnt einen Abhebeversuch. |
| 239 | Verschiebt die Zeit genau an die Sitzungsgrenze. |
| 240 | Alte Sitzung muss SESSION_EXPIRED erhalten. |
| 241 | Benutzer authentifiziert sich neu am gleichen Terminal. |
| 242 | Darf dann dieselbe offene Transaktion abschließen. |
| 243 | Es wird genau einmal abgebucht. |

### 5.6 Berechtigungen, Eingabeprüfung und Parallelität

| Zeile(n) | Erklärung |
|---|---|
| 245 | Definiert Sitzungsbesitz und Logout. |
| 246 | Die Sitzung kann nicht von einem anderen Terminal verwendet werden. |
| 247 | Löscht die eigene Sitzung regulär. |
| 248 | Danach ist sie unberechtigt. |
| 249 | Eine beliebige andere, syntaktisch gültige UUID ist ebenfalls keine Berechtigung. |
| 251 | Definiert die zusätzliche Terminalbindung der **Transaktion**. |
| 252 | Reserviert am ersten Terminal. |
| 253 | Meldet dieselbe Karte korrekt am anderen Terminal an. |
| 254 | Trotz gültiger zweiter Sitzung ist Zugriff auf die fremde Terminaltransaktion FORBIDDEN. |
| 256 | Definiert die dreifache PIN-Sperre. |
| 257 | Wiederholt drei Fehlversuche. |
| 258 | Jeder Versuch sendet eine gültig formatierte, aber falsche PIN. |
| 259 | Jeder muss AUTH_FAILED liefern. |
| 260 | Versucht danach sogar die richtige PIN. |
| 261 | Auch diese muss wegen der Sperre abgewiesen werden. |
| 263 | Definiert unbekannte Karte und falsche PIN-Datentypen. |
| 264 | Unbekannte Karte mit wohlgeformter PIN erwartet AUTH_FAILED. |
| 265 | Unicode-Vollbreitenziffern sind keine ASCII-PIN und erwarten BAD_REQUEST. |
| 266 | Ein Integer statt einer Zeichenkette erwartet ebenfalls BAD_REQUEST; beendet die Schleifenliste. |
| 267 | Führt jeweils die vorbereitete Anmeldung aus. |
| 268 | Vergleicht mit dem für diesen Fall festgelegten Status. |
| 270 | Definiert Rücksetzen des Fehlzählers bei rechtzeitigem Erfolg. |
| 271 | Erzeugt zunächst einen Fehlversuch. |
| 272 | Meldet sich anschließend vor einer Sperrung richtig an. |
| 273 | Der interne Zähler muss wieder Null sein. |
| 275 | Definiert die Prüfung des Anfrageumschlags und Operationsschemas. |
| 276 | Boolean als Version ist trotz Python-Verwandtschaft zu Integern BAD_VERSION. |
| 277 | Version 2 ist ebenfalls BAD_VERSION. |
| 278 | Ungültige Anfrage-UUID ist BAD_REQUEST. |
| 279 | Zusätzliches äußeres Feld ist BAD_REQUEST. |
| 280 | Unbekannte Operation ist UNKNOWN_OP. |
| 281 | Unerwartetes Körperfeld bei BALANCE ist BAD_REQUEST. |
| 282 | Array statt Körperobjekt ist BAD_REQUEST. |
| 283 | AUTH mit nichtleerer Sitzungs-ID ist BAD_REQUEST; beendet die Fallliste. |
| 284 | Geht alle vorbereiteten Nachricht-/Erwartungs-Paare durch. |
| 285 | Kennzeichnet den Unterfall mit der geprüften Nachricht. |
| 286 | Führt Austausch und Statusvergleich aus. |
| 287 | Prüft zusätzlich den direkten Bankeinstieg mit einem falschen Wurzeltyp, unabhängig vom Decoder. |
| 288 | Fehlt jede gültige Anfrage-ID, muss die Fehlerantwort id=null haben. |
| 290 | Definiert ungültige und unbekannte Transaktions-IDs. |
| 291 | Prüft None, Integer, beliebigen Text und eine UUID in nichtkanonischer Großschreibung. |
| 292 | Alle syntaktisch falschen IDs müssen BAD_REQUEST erzeugen. |
| 293 | Eine gültige, aber nicht gespeicherte neue UUID ergibt dagegen NOT_FOUND. |
| 295 | Definiert atomare Zurückweisung ungültiger Ergebnismeldungen. |
| 296 | Beginnt einen gültigen Versuch. |
| 297 | Prüft None, Liste, Boolean und unbekannten Ergebnistext. |
| 298 | Jede ungültige Nachricht muss BAD_REQUEST liefern. |
| 299 | Danach muss die ursprüngliche Transaktion immer noch DISPENSING sein. |
| 300 | Der Buchsaldo darf sich nicht verändert haben. |
| 302 | Definiert Deckungsschutz über zwei verschiedene Transaktionen. |
| 303 | Bindet 7000 der 10000 Cent. |
| 304 | Fordert unter anderer ID weitere 4000 Cent. |
| 305 | Die zweite Reservierung muss abgelehnt werden. |
| 306 | Nur die erste Sperre zählt, also sind noch 3000 Cent frei. |
| 308 | Definiert gleichzeitige doppelte Erfolgsbestätigungen. |
| 309 | Beginnt den Versuch. |
| 310 | Baut dieselbe RESULT-OK-Nachricht für alle Threads. |
| 311 | Startet einen Pool mit höchstens acht gleichzeitig arbeitenden Threads. |
| 312 | Übermittelt 40 Aufgaben, die alle dieselbe Nachricht senden. `list` wartet darauf, dass alle Ergebnisse vorliegen. |
| 313 | Alle Antworten müssen COMMITTED zeigen. |
| 314 | Trotz 40 Aufrufen wurde nur einmal abgebucht. |
| 316 | Definiert konkurrierende **verschiedene** Reservierungen. |
| 317 | Innere Hilfsfunktion für einen einzelnen Parallelaufruf; `_` ist ein unbenutzter Auftragsindex. |
| 318 | Jeder Aufruf erzeugt eine andere ID und versucht 7000 Cent zu reservieren; gibt nur den Zustand zurück. |
| 319 | Erstellt wieder einen Pool mit maximal acht Threads. |
| 320 | Startet 20 Reservierungsversuche und sammelt alle Zustände. |
| 321 | Genau einer darf RESERVED sein. |
| 322 | Die übrigen 19 müssen DECLINED sein. |
| 323 | Deckung nach Abschluss: 3000 Cent. Würde Deckungsprüfung getrennt vom Anlegen erfolgen, könnten mehrere Threads irrtümlich erfolgreich sein. |

### 5.7 Ergänzende Besitz-, Endzustands- und Konstruktorfälle

| Zeile(n) | Erklärung |
|---|---|
| 325 | Definiert die Bindung einer Transaktion an die Karte. |
| 326 | Reserviert für Karte A. |
| 327 | Ergänzt nur für diesen Test eine zweite erfundene Karte im Fixture, mit eigener Muster-PIN und eigenem Guthaben. |
| 328 | Meldet diese zweite Karte am selben Terminal an. |
| 329 | Liest deren eigene gültige Sitzung. |
| 330 | Diese Sitzung darf auf die Transaktion der ersten Karte trotzdem nicht zugreifen. |
| 332 | Definiert, dass Logout keinen begonnenen Bargeldvorgang freigibt. |
| 333 | Beginnt einen Vorgang. |
| 334 | Loggt aus. |
| 335 | Loggt korrekt neu ein. |
| 336 | Die 4000-Cent-Sperre muss noch vorhanden sein. |
| 337 | Der Zustand muss weiterhin DISPENSING sein. |
| 339 | Definiert die Endgültigkeit einer Ablehnung. |
| 340 | Lehnt 11000 bei 10000 Cent Deckung ab. |
| 341 | Erhöht den Testfixture-Saldo auf 20000, um später ausreichende Deckung nachzustellen. |
| 342 | Dieselbe alte ID bleibt dennoch DECLINED; ein Retry darf nicht plötzlich Geld sperren. |
| 343 | Das gesamte erhöhte Testguthaben ist frei. |
| 345 | Definiert die Endgültigkeit eines Reservierungsablaufs. |
| 346 | Reserviert. |
| 347 | Lässt genau die Reservierungsdauer vergehen. |
| 348 | Erneutes RESERVE der alten ID bleibt CANCELLED statt eine neue Frist zu beginnen. |
| 350 | Definiert fehlende Sitzung und Anfrage-/Antwortzuordnung. |
| 351 | Baut BALANCE absichtlich ohne Sitzung. |
| 352 | Führt den Austausch aus. |
| 353 | Trotz Fachfehler muss die gültige Anfrage-ID korrekt gespiegelt werden. |
| 354 | Fehlende Sitzungs-UUID ist ein Formatfehler BAD_REQUEST. |
| 355 | Es darf keine Transaktion entstehen. |
| 357 | Definiert ungültige Anfangssalden der lokalen Bankkonfiguration. |
| 358 | Prüft Boolean, negativen Wert, Überschreitung der Modellgrenze und Float. |
| 359 | Jeder Fall muss ValueError werfen. |
| 360 | Erzeugt absichtlich eine ungültig konfigurierte Bank. Der Kommentar unterdrückt nur die erwartete statische Typwarnung für diesen Negativtest, nicht die Laufzeitprüfung. |

### 5.8 Auszahlertests und Teststart

| Zeile(n) | Erklärung |
|---|---|
| 363 | Definiert die Testgruppe für das lokale Auszahljournal. |
| 364 | Definiert Schutz vor doppelter erfolgreicher Ausgabe. |
| 365 | Erstellt frischen Auszahler und ID. |
| 366 | Erster Versuch über 4000 muss OK liefern. |
| 367 | Wiederholung liefert weiterhin OK, ohne nochmals auszugeben. |
| 368 | Ausgabenzähler ist nur 4000. |
| 369 | Ein widersprüchlicher Betrag muss Fault werfen. |
| 370 | Versucht genau denselben Vorgang mit 5000 Cent. |
| 372 | Definiert die Wirkung eines sicher fehlgeschlagenen Versuchs. |
| 373 | Erstellt frischen Auszahler und ID. |
| 374 | Simuliert FAIL beim ersten Versuch. |
| 375 | Ein später mit OK parametrierter Aufruf darf den alten Versuch nicht wiederholen; gespeichertes FAIL wird zurückgegeben. |
| 376 | Kein Geld wurde simuliert ausgegeben. |
| 378 | Definiert die Sperre eines unklaren physischen Versuchs. |
| 379 | Frischer Auszahler und ID. |
| 380 | Erster Versuch endet UNKNOWN. |
| 381 | Späterer Aufruf darf den Versuch nicht in eine neue Ausgabe verwandeln; bleibt UNKNOWN. |
| 382 | In dieser konkreten Simulation wurden keine Cent gezählt; das ist **kein** Beweis über reale UNKNOWN-Fälle. |
| 384 | Definiert gleichzeitige doppelte Hardwareaufrufe. |
| 385 | Frischer Auszahler und gemeinsame ID. |
| 386 | Startet maximal acht Threads. |
| 387 | 40 Aufgaben versuchen dieselbe ID mit demselben Betrag; Ergebnisse werden gesammelt. |
| 388 | Die Menge aller Rückgaben darf nur OK enthalten. |
| 389 | Es wurde trotzdem nur ein Betrag von 4000 Cent ausgegeben. |
| 391 | Definiert ungültige Auszahlerparameter. |
| 392 | Erstellt ein leeres Auszahlobjekt. |
| 393 | Probiert Boolean, Null, negative Zahl, unpassende Stückelung und zu hohen Betrag. |
| 394 | Jeder muss Fault auslösen. |
| 395 | Führt den jeweiligen ungültigen Aufruf mit neuer ID aus. |
| 396 | Auch ein unzulässiger Ergebnisparameter muss Fault erzeugen. |
| 397 | Injiziert den nicht definierten Ausgang MAYBE. |
| 398 | Alle ungültigen Eingaben müssen vor dem ersten Journaleintrag abgewiesen worden sein. |
| 401 | Definiert zusätzliche Tests für die ausgelieferten Dokumentationsartefakte. |
| 402 | Definiert eine Hilfe zum Auffinden des Blattverzeichnisses. |
| 403 | Importiert Path für plattformunabhängige Dateipfade. |
| 404 | Geht vom absoluten Pfad dieser Testdatei zwei Verzeichnisebenen nach oben zu `ueb02`. |
| 406 | Definiert die XML-Strukturprüfung des SVG. |
| 407 | Importiert den XML-Parser der Standardbibliothek. |
| 408 | Liest die SVG-Datei und holt ihr Wurzelelement. Syntaxfehler würden den Test abbrechen lassen. |
| 409 | Verlangt ein SVG-Wurzelelement im korrekten XML-Namensraum. Das prüft Syntax und Typ, nicht allein die grafische Lesbarkeit. |
| 411 | Definiert die Prüfung lokaler Markdown-Verweise. |
| 412 | Importiert reguläre Ausdrücke für die Linksuche. |
| 413 | Durchläuft Antwort und Erklärung. |
| 414 | Bildet den absoluten Dokumentpfad. |
| 415 | Liest den Text und extrahiert Linkziele aus der Markdown-Linkschreibweise: Beschriftung in eckigen Klammern, Ziel in runden Klammern. |
| 416 | Überspringt externe URLs und reine Abschnittsanker. |
| 417 | Jedes lokale Linkziel muss relativ zum jeweiligen Dokument tatsächlich existieren. |
| 419 | Definiert die Vollständigkeitsprüfung der zeilenbezogenen Erklärung. |
| 420 | Importiert reguläre Ausdrücke zum Lesen der Tabellenzeilen. |
| 421 | Liest diese Erklärung als Text. |
| 422 | Legt Quelldatei und Begrenzungsüberschriften für den Protokollabschnitt fest. |
| 423 | Ergänzt den Demoabschnitt. |
| 424 | Ergänzt den Testabschnitt und schließt die Zuordnungsliste. |
| 425 | Verarbeitet jede der drei Dateien getrennt. |
| 426 | Schneidet den zugehörigen Erklärungsabschnitt zwischen seinen Überschriften aus. |
| 427 | Die gemeinsamen Anfangszeilen 1–5 sind bereits durch Abschnitt 2 abgedeckt. |
| 428 | Erkennt Tabellenzeilen mit einer Zeilennummer oder einem Nummernbereich; `re.M` lässt `^` an jeder Textzeile beginnen. |
| 429 | Fügt alle Nummern des jeweiligen Bereichs der Menge erklärter Zeilen hinzu. `last or first` behandelt Einzelnumerierungen. |
| 430 | Liest den Quelltext und zerlegt ihn in physische Zeilen. |
| 431 | Sammelt alle nichtleeren Quelltextzeilen, deren Nummer noch nicht erfasst wurde; enumerate beginnt hier bei 1. |
| 432 | Diese Lückenliste muss leer sein. Das prüft den vollständigen Zeilenbezug, ersetzt aber keine inhaltliche Qualitätsprüfung der Erklärungen. |
| 435 | Erkennt den direkten Start dieser Testdatei. Bei unittest-discover wird sie stattdessen importiert. |
| 436 | Führt bei Direktstart alle gefundenen Tests aus und zeigt mit verbosity=2 die einzelnen Testnamen. |

## 6. Diagramm lesen und bearbeiten

- `ue2.6/sequenz.svg` ist eine eigenständige XML-Grafik mit vier vertikalen Lebenslinien. Durchgezogene Pfeile sind Anforderungen/lokale Aufrufe, gestrichelte Pfeile Antworten beziehungsweise Ausgabeaktionen. Gelbe Kästen markieren Transportannahme und Journalpflicht.
- In `ue2.6/sequenz.mmd` benennt `sequenceDiagram` den Diagrammtyp. `actor` definiert den Benutzer, `participant` die drei technischen Rollen. `A->>B` sendet eine Nachricht, `B-->>A` eine Antwort, und `B->>B` beschreibt eine interne Aktion. `Note over` ergänzt die wichtige Transport-/Simulationsgrenze.
- Alle vorkommenden `T` meinen dieselbe UUID. Die Diagramme kürzen äußere JSON-Felder nur zur Lesbarkeit; im Code sind Version, Anfrage-ID, Sitzungsfeld und Body immer vorhanden.
- BEGIN ist die fachliche Freigabe, **nicht** schon die bestätigte Auszahlung. Erst das Hardwareergebnis und RESULT OK machen daraus COMMITTED.

## 7. Starten, nachprüfen und an der Tafel erklären

Aus dem Verzeichnis `ueb02/`:

```bash
python3 -B ue2.6/demo.py
python3 -B -m unittest discover -s ue2.6 -p 'test_*.py' -v
```

`-B` unterdrückt zusätzliche Bytecode-Cachedateien. Es wird keine Bibliothek installiert. Alle verwendeten Module gehören zur Standardbibliothek. Die eigene Datei `protocol.py` wird beim Direktstart aus dem Skriptverzeichnis gefunden; unittest-discover nimmt das angegebene Suchverzeichnis entsprechend auf.

**Tatsächlich geprüft:** 55 Testmethoden unter Python 3.14.7 erfolgreich; zusätzlich Demo ohne Assertionfehler. Der Demo-Erfolgsfall gibt 4000 Cent simuliert aus und hinterlässt 6000 Cent Buchsaldo. Die verlorene RESULT-Antwort wird wiederholt, ohne ein zweites Mal abzubuchen; die spätere 7000-Cent-Anforderung endet DECLINED. Testschleifen und subTest-Unterfälle liefern zusätzliche Eingaben innerhalb dieser 55 Methoden, werden aber nicht als weitere Testmethoden gezählt.

### Typische Fragen mit Antworten

1. **Warum Länge vor JSON?** TCP liefert Bytes ohne Nachrichtengrenzen. JSON allein sagt einem Streamleser nicht zuverlässig, wann genau eine vollständige Nachricht angekommen ist.
2. **Warum Bytezahl statt Zeichenanzahl?** Das Eurozeichen braucht in UTF-8 mehrere Bytes. Der Empfänger liest Bytes, nicht Python-Zeichen.
3. **Warum zwei IDs?** `id` ordnet eine Nachricht und ihre Antwort zu. `tx` bleibt die Identität der fachlichen Abhebung über beliebig viele Nachrichten hinweg.
4. **Warum reservieren und nicht sofort abbuchen?** Zwischen Freigabe und mechanischer Ausgabe kann noch ein Fehler liegen. Reservierung verhindert Überausgabe, ohne schon eine erfolgreiche Bargeldentnahme zu behaupten.
5. **Warum BEGIN?** Vor BEGIN darf die Reservierung ablaufen. Nach Freigabe könnte der Auszahler tätig sein; ab dann ist automatische Freigabe gefährlich.
6. **Warum reicht die Bank nicht für einmalige Ausgabe?** Die Bank sieht die physische Mechanik nicht. Deshalb braucht der Automat zusätzlich ein Journal, und bei Unklarheit muss er anhalten statt nochmals Geld auszugeben.
7. **Warum nicht nach Timeout einfach freigeben?** Die Antwort kann verloren sein, während das Geld schon ausgegeben wurde.
8. **Warum ein Lock?** Deckungsprüfung und Reservierung beziehungsweise Buchung und Statuswechsel müssen zusammengehören. Sonst könnten parallele Threads denselben alten Zustand lesen.
9. **Ist das jetzt sicherer Bankcode?** Nein. Keine echte Kartenprüfung, kein HSM, kein TLS-Transport, kein dauerhaftes Journal und keine Absturzfestigkeit. Es ist ein getestetes Unterrichtsmodell des Anwendungsablaufs.
10. **Was wurde nicht bewiesen?** Keine korrekte reale Bargeldausgabe, keine Sicherheit gegenüber einem böswilligen Automaten, kein Verhalten nach Datenverlust oder Neustart und keine Produktionsreife.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol; Datum 2026-10-19. Auftrag sinngemäß: Ü2.6 als RFC-artiges fiktives Bankomatprotokoll einschließlich grafischem Sequenzdiagramm, lauffähigem didaktischem Python-Referenzcode, umfassenden ausgeführten unittest-Tests und einer schrittweisen verständlichen Erklärung jeder eigenen Codezeile erstellen. Die Erklärung soll das eigenständige Nachvollziehen und Erklären unterstützen, nicht eine nicht vorhandene Eigenleistung behaupten.


---

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


---

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
