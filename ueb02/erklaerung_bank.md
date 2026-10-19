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
