# POP3 verstehen: Dateien, Funktionen und jede Codezeile

> **KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent; Modell: OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). **Datum:** 2026-10-19. **Auftrag:** Ü3.1–3.3 vollständig implementieren, wirklich testen und jede Datei, Funktion und Codezeile der POP3-Lösung didaktisch erklären. Keine echten Mail-Zugangsdaten, keine Originaländerungen, kein gesondertes KI-PDF.

## 1. Lernweg und Dateien

1. [`ue3.1/antwort.md`](ue3.1/antwort.md) beantwortet die Theoriefragen: drei Zustände, Klartext-Risiken, Single-/Multi-Line und IMAP-Vergleich. Es enthält keine ausführbare Logik.
2. [`ue3.2/pop3_client.py`](ue3.2/pop3_client.py) ist der eigene Socket-Client. Seine Aufgabe ist nicht, „ein TCP-Paket“ zu lesen, sondern vollständige POP3-Antworten aus einem Bytestrom zusammenzusetzen.
3. [`ue3.2/test_pop3_client.py`](ue3.2/test_pop3_client.py) erzeugt ein unabhängiges TCP-Gegenüber mit vorgegebenem Dialog. Es kontrolliert die wirklich gesendeten Befehle und liefert absichtlich fragmentierte/fehlerhafte Antworten. Zusätzlich prüft es den eigenen Server und CLI-Unterprozesse.
4. [`ue3.2/antwort.md`](ue3.2/antwort.md) erklärt Startparameter, Clientfehler, API und nachgewiesene Ergebnisse.
5. [`ue3.3/pop3_server.py`](ue3.3/pop3_server.py) implementiert Server, Worker-Threads, Postfachsperren und Zustandsautomat. Die Originaldatenbank wird dynamisch geladen, nicht nachgebaut.
6. [`ue3.3/test_pop3_server.py`](ue3.3/test_pop3_server.py) prüft den Server unabhängig mit stdlib `poplib` und Rohsockets: Abruf, Fehler, Bytes, Parallelität, Rollback und getrennte CLI-Prozesse.
7. [`ue3.3/antwort.md`](ue3.3/antwort.md) dokumentiert Serverarchitektur, Zustandstabelle, Tests, Mailclient-Einstellungen und die API für die separate native GUI.
8. Diese Datei verbindet den Überblick mit der untenstehenden zeilenweisen Erklärung. Originale `Angabe/SampleDataBase.py` und `Angabe/README.md` sind Eingaben, keine bearbeiteten Lösungsdateien. Ihre beiden Funktionen sind: `authenticate` prüft Benutzer/Passwort, `get_messages` liefert die lebende Liste aus `id`-/`raw`-Datensätzen. Das Originalkonto lautet **alice / secret**; `alice123` in README-Beispielen ist widersprüchlich und falsch.

## 2. Was im Netzwerk tatsächlich passiert

```text
Client                                     Server-Worker
TCP-Verbindung --------------------------> akzeptieren, eigenen Thread starten
                 <------------------------ +OK ... CRLF
USER alice CRLF -------------------------> Kandidaten merken (noch kein Login)
                 <------------------------ +OK send PASS CRLF
PASS secret CRLF ------------------------> Passwort prüfen, Lock holen, Snapshot
                 <------------------------ +OK ... CRLF
LIST CRLF -------------------------------> nicht markierte Nachrichten auflisten
                 <------------------------ +OK ... CRLF, Datenzeilen, Punkt CRLF
RETR 1 CRLF -----------------------------> komplette kanonische Nachricht senden
                 <------------------------ +OK ... CRLF, Stuffing-Daten, Punkt CRLF
QUIT CRLF -------------------------------> UPDATE (falls DELE), Lock freigeben
                 <------------------------ +OK goodbye CRLF, TCP-Ende
```

**Bytes statt Zeichen:** `str` ist Unicode-Text, `bytes` ist der tatsächlich übertragene Datenstrom. UTF-8 kann für ein Zeichen mehrere Bytes benötigen. Darum wird erst kodiert und dann `len(bytes)` für STAT/LIST verwendet. CRLF sind die zwei Bytes `b"\r\n"`; ein einzelnes LF genügt nicht.

**Puffer statt Paketdenken:** `makefile("rb").readline()` sammelt, bis ein Zeilenende gefunden wird; danach prüfen wir ausdrücklich CRLF. Es darf mit einem TCP-Lesevorgang nur ein Bruchstück oder bereits eine Folge mehrerer Protokollzeilen eintreffen. Die Tests schreiben jedes Byte einzeln bzw. mehrere Befehle hintereinander. Sie behaupten nicht, TCP würde die Schreibgrenzen erhalten.

**Dot-Stuffing:** Ein echter Punkt am Zeilenanfang wird auf dem Draht verdoppelt. Ein Datenpunkt `.` wird `..`; nur die einzelne Punktzeile beendet die Antwort. Die Listen-/Mailgrößen schließen zusätzliche Stuffing-Punkte und die Endmarke aus. Der Client liest nach `-ERR` keine Datenzeilen.

**Zustand und Transaktion:** `candidate` ist nur der letzte USER-Vorschlag, `user` steht erst nach erfolgreichem PASS und Lock fest. `deleted` speichert nur lokale Nummern. `RSET` leert diese Menge. Erst QUIT schreibt die Löschung in die ursprüngliche In-Memory-Liste. Ein Socket-Abbruch ist gerade **kein** QUIT und löst deshalb keinen UPDATE aus.

**Thread und Lock sind verschiedene Dinge:** Jeder Client bekommt einen eigenen Thread und kann daher unabhängig warten/arbeiten. Zwei Threads dürfen aber nicht gleichzeitig denselben Maildrop verändern. Der kurze Verwaltungslock schützt nur die Lock-Tabelle; der benutzerspezifische Lock bleibt während der Sitzung gehalten. Verschiedene Benutzer haben verschiedene Locks.

**UID und Nummer sind nicht dasselbe:** Die Sitzungsnummer wird bei jeder neuen Anmeldung ab 1 vergeben. Die UID basiert auf stabiler Datenbank-ID und unverändertem Inhalt und bleibt bei Neunummerierung erhalten. SHA-256 dient hier der Kennungsbildung, nicht der Verschlüsselung.

**Aufräumen trotz Fehler:** `try/finally` garantiert Aufräumen beim Verlassen des Blocks. Der Client trennt bewusst `quit()` (Protokollabschluss mit UPDATE) von `close()` (nur Transportabbruch). Der Server gibt seinen Maildrop-Lock in `finally` frei. `shutdown()` beendet die Accept-Schleife aus einem anderen Thread; `server_close()` beendet offene Sitzungen und wartet auf Worker.

## 3. Ergebnisse und ehrliche Grenzen

Die ausgeführten Tests verwenden echte lokale TCP-Verbindungen. Der Testbericht nennt **11 Clienttests und 15 Servertests**, beide erfolgreich; ein Servertest startet Server und Client zusätzlich als separate Prozesse. Synthetischer Bob und leeres Postfach existieren nur in Testinstanzen. Der normale Server lädt ausschließlich das unveränderte Originalkonto. Es gibt keinen Ersatz durch vorgetäuschte Netzwerkresultate.

Die Klasse ist ein lokaler Lernserver ohne TLS, SMTP, dauerhafte Speicherung oder Schutz gegen unbegrenzt viele Verbindungen. Ein Neustart lädt wieder die vier Originalmails. Kürzere Timeouts als 600 Sekunden werden nur für beschleunigte Tests gesetzt. Der tatsächliche Thunderbird-GUI-Lauf mit Screenshots ist im [GUI-Bericht](ue3.3/gui_testbericht.md) belegt; der zusätzlich ausgeführte Go-Referenzserverlauf steht im [Gesamtprotokoll](testprotokoll_blatt03.md).

Quellen: [RFC 1939](https://www.rfc-editor.org/rfc/rfc1939.html) §§ 3–7, 11, 13; [RFC 2449](https://www.rfc-editor.org/rfc/rfc2449.txt) §§ 3–6, 8.1.2; [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051.html) §§ 2.2, 4.3, 7. Abruf: 2026-10-19. Exakte Start-/Testbefehle stehen in den beiden Implementierungsantworten.

## 4. Zeilenweise Erklärung der vier Python-Dateien

Die Zeilennummern beziehen sich auf die tatsächlichen Dateien dieser Fassung. **Jede physische Zeile**, einschließlich Kommentar, Docstring, Fortsetzungs- und Leerzeile, hat einen Eintrag. Fortsetzungszeilen werden dem zugehörigen Python-Ausdruck zugeordnet; eine Umbruchzeile führt nicht noch einen eigenen Netzwerkvorgang aus. Die Funktionsübersichten erklären jeweils den Gesamtzweck, die Tabellen die konkrete Ausführung. Einrückung bestimmt in Python den Block. Die Quelltextspalte ist HTML-escaped, damit `<`, `>` und `|` nicht die Tabelle zerlegen.

### `ue3.2/pop3_client.py`

Quellstand SHA-256: `56e62dccc1f8c48f5391e8661c1bc656155ddb34cf741c3866d9a0c6f5f91b53`.

#### Funktionen und Methoden

- **`__init__` (Zeilen 25–33):** Initialisiert den Lebenszyklus: beim Client Verbindung/Begrüßung, beim Server Datenbank, Verwaltungsstrukturen und Listener.
- **`read_line` (Zeilen 35–40):** Gepufferte CRLF-Zeile: TCP-Paketgrenzen sind keine Zeilengrenzen.
- **`status` (Zeilen 42–49):** Statuszeile von höchstens 512 Bytes inklusive CRLF prüfen.
- **`command` (Zeilen 52–52):** Erste reine Typüberladung: Ohne mehrzeilige Antwort ist das Ergebnis eine Statuszeile als `bytes`. Diese Signatur sendet selbst nichts.
- **`command` (Zeilen 55–55):** Zweite reine Typüberladung: Mit `multiline=True` ist das Ergebnis eine `list[bytes]` von Datenzeilen. Die echte Implementierung folgt ab Zeile 57.
- **`command` (Zeilen 57–87):** Einen Befehl senden und Status bzw. dot-entstuffte Daten lesen.
- **`login` (Zeilen 89–94):** USER und PASS nacheinander; Passwort nie protokollieren.
- **`list_messages` (Zeilen 96–111):** LIST ohne Argument liefert alle (Nummer, Oktettzahl)-Paare.
- **`retrieve` (Zeilen 113–118):** Eine Mail als Bytes inklusive wiederhergestellter CRLF zurückgeben.
- **`quit` (Zeilen 120–127):** QUIT bestätigen lassen und auch bei Fehlern lokale Ressourcen schließen.
- **`close` (Zeilen 129–136):** Nur Transport schließen; ohne QUIT gibt es keinen UPDATE-Auftrag.
- **`__enter__` (Zeilen 138–139):** Gibt das Clientobjekt für den with-Block zurück; die Verbindung besteht bereits.
- **`__exit__` (Zeilen 141–145):** Erfolgreicher Block: QUIT. Ausnahme: nur close, damit kein ungewollter UPDATE bestätigt wird.
- **`main` (Zeilen 148–181):** Testkonto anmelden, alle Nachrichten auflisten und genau eine abrufen.

#### Jede physische Codezeile

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)</code> | Kommentar/KI-Nachweis: KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). Kein ausführbarer Python-Befehl. |
| 2 | <code># Datum: 2026-10-19</code> | Kommentar/KI-Nachweis: Datum: 2026-10-19. Kein ausführbarer Python-Befehl. |
| 3 | <code># Anfrage: Ü3.2 als reinen Socket-POP3-Client mit USER/PASS, LIST, RETR, QUIT und echten Fehler-/Fragmentierungstests implementieren.</code> | Kommentar/KI-Nachweis: Anfrage: Ü3.2 als reinen Socket-POP3-Client mit USER/PASS, LIST, RETR, QUIT und echten Fehler-/Fragmentierungstests implementieren.. Kein ausführbarer Python-Befehl. |
| 4 | <code>"""Einfacher unverschlüsselter POP3-Client für lokale Laborkonten, ohne poplib."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 5 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 6 | <code>import argparse</code> | Standard-/Modulimport: liest und prüft Kommandozeilenoptionen. |
| 7 | <code>import getpass</code> | Standard-/Modulimport: fragt ein Passwort ohne Terminal-Echo ab. |
| 8 | <code>import ipaddress</code> | Standard-/Modulimport: erkennt numerische Loopback-Adressen für die lokale Voreinstellung. |
| 9 | <code>import socket</code> | Standard-/Modulimport: stellt TCP-Verbindungen, Socketoptionen und Shutdown bereit. |
| 10 | <code>import sys</code> | Standard-/Modulimport: liefert stderr und den aktuellen Python-Interpreter für echte CLI-Unterprozesse. |
| 11 | <code>from typing import Literal, overload</code> | Standard-/Modulimport: dokumentiert unterschiedliche Rückgabetypen von ein-/mehrzeiligen Aufrufen. |
| 12 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 13 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 14 | <code>class POP3Error(Exception):</code> | Definiert die Klasse und ihre Basisklassen. Negative Antwort des Servers (-ERR). |
| 15 | <code>    """Negative Antwort des Servers (-ERR)."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 16 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 17 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 18 | <code>class ProtocolError(Exception):</code> | Definiert die Klasse und ihre Basisklassen. Ungültige, zu lange oder unvollständige Serverantwort. |
| 19 | <code>    """Ungültige, zu lange oder unvollständige Serverantwort."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 20 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 21 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 22 | <code>class POP3Client:</code> | Definiert die Klasse und ihre Basisklassen. Synchrone Socket-API; ein Objekt entspricht einer TCP-Sitzung. |
| 23 | <code>    """Synchrone Socket-API; ein Objekt entspricht einer TCP-Sitzung."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 24 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 25 | <code>    def __init__(self, host="127.0.0.1", port=11110, timeout=10):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Initialisiert den Lebenszyklus: beim Client Verbindung/Begrüßung, beim Server Datenbank, Verwaltungsstrukturen und Listener. |
| 26 | <code>        self.socket = socket.create_connection((host, port), timeout=timeout)</code> | Setzt den verbundenen TCP-Socket; darüber laufen sendall und close. Rechte Seite: socket.create_connection((host, port), timeout=timeout). |
| 27 | <code>        self.reader = self.socket.makefile("rb")</code> | Setzt den binären Lesepuffer auf diesem Socket; er behält überschüssige Bytes. Rechte Seite: self.socket.makefile('rb'). |
| 28 | <code>        self.closed = False</code> | Setzt den lokalen Lebenszykluszustand, damit mehrfaches close sicher ist. Rechte Seite: False. |
| 29 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 30 | <code>            self.greeting = self.status()</code> | Setzt die bereits validierte positive Serverbegrüßung. Rechte Seite: self.status(). |
| 31 | <code>        except Exception:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 32 | <code>            self.close()</code> | Führt den Aufruf/Ausdruck self.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 33 | <code>            raise</code> | Bricht diesen Pfad mit der ursprünglichen Ausnahme ab; Aufrufer/Test muss den Fehler behandeln. |
| 34 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 35 | <code>    def read_line(self, limit=1024 * 1024):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Gepufferte CRLF-Zeile: TCP-Paketgrenzen sind keine Zeilengrenzen. |
| 36 | <code>        """Gepufferte CRLF-Zeile: TCP-Paketgrenzen sind keine Zeilengrenzen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 37 | <code>        line = self.reader.readline(limit + 1)</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: self.reader.readline(limit + 1). |
| 38 | <code>        if not line or len(line) &gt; limit or not line.endswith(b"\r\n"):</code> | Prüft die Bedingung not line or len(line) &gt; limit or (not line.endswith(b'\r\n')). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 39 | <code>            raise ProtocolError("Fehlende CRLF-Zeile, EOF oder Zeilenlimit überschritten")</code> | Bricht diesen Pfad mit ProtocolError('Fehlende CRLF-Zeile, EOF oder Zeilenlimit überschritten') ab; Aufrufer/Test muss den Fehler behandeln. |
| 40 | <code>        return line[:-2]</code> | Beendet diesen Funktionsaufruf und liefert line[:-2] an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 41 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 42 | <code>    def status(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Statuszeile von höchstens 512 Bytes inklusive CRLF prüfen. |
| 43 | <code>        """Statuszeile von höchstens 512 Bytes inklusive CRLF prüfen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 44 | <code>        line = self.read_line(512)</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: self.read_line(512). |
| 45 | <code>        if line == b"-ERR" or line.startswith(b"-ERR "):</code> | Prüft die Bedingung line == b'-ERR' or line.startswith(b'-ERR '). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 46 | <code>            raise POP3Error(line.decode("ascii", errors="replace"))</code> | Bricht diesen Pfad mit POP3Error(line.decode('ascii', errors='replace')) ab; Aufrufer/Test muss den Fehler behandeln. |
| 47 | <code>        if line != b"+OK" and not line.startswith(b"+OK "):</code> | Prüft die Bedingung line != b'+OK' and (not line.startswith(b'+OK ')). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 48 | <code>            raise ProtocolError(f"Ungültiger Status: {line!r}")</code> | Bricht diesen Pfad mit ProtocolError(f'Ungültiger Status: {line!r}') ab; Aufrufer/Test muss den Fehler behandeln. |
| 49 | <code>        return line</code> | Beendet diesen Funktionsaufruf und liefert line an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 50 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 51 | <code>    @overload</code> | Dekorator: ergänzt den folgenden Funktionsvertrag. overload beschreibt nur Rückgabetypen; contextmanager steuert Öffnen und garantiertes Aufräumen eines Generator-Kontexts. |
| 52 | <code>    def command(self, text: str, multiline: Literal[False] = False) -&gt; bytes: ...</code> | Reine Typbeschreibung für den einzeiligen Fall: text ist str, multiline ist exakt False, der Rückgabewert ist bytes. Die drei Punkte ersetzen nur den Körper dieser Überladung; die ausführbare Implementierung folgt in Zeile 57. |
| 53 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 54 | <code>    @overload</code> | Dekorator: ergänzt den folgenden Funktionsvertrag. overload beschreibt nur Rückgabetypen; contextmanager steuert Öffnen und garantiertes Aufräumen eines Generator-Kontexts. |
| 55 | <code>    def command(self, text: str, multiline: Literal[True]) -&gt; list[bytes]: ...</code> | Reine Typbeschreibung für den mehrzeiligen Fall: Bei multiline=True ist der Rückgabewert eine Liste binärer Datenzeilen. overload hilft der statischen Prüfung, führt aber keinen zweiten Netzwerkdialog aus. |
| 56 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 57 | <code>    def command(self, text: str, multiline: bool = False) -&gt; bytes &#124; list[bytes]:</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Einen Befehl senden und Status bzw. dot-entstuffte Daten lesen. |
| 58 | <code>        """Einen Befehl senden und Status bzw. dot-entstuffte Daten lesen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 59 | <code>        if self.closed:</code> | Prüft die Bedingung self.closed. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 60 | <code>            raise ProtocolError("Verbindung bereits geschlossen")</code> | Bricht diesen Pfad mit ProtocolError('Verbindung bereits geschlossen') ab; Aufrufer/Test muss den Fehler behandeln. |
| 61 | <code>        if any(ord(character) &lt; 32 or ord(character) &gt; 126 for character in text):</code> | Prüft die Bedingung any((ord(character) &lt; 32 or ord(character) &gt; 126 for character in text)). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 62 | <code>            raise ValueError("Befehle müssen druckbares ASCII ohne CR/LF sein")</code> | Bricht diesen Pfad mit ValueError('Befehle müssen druckbares ASCII ohne CR/LF sein') ab; Aufrufer/Test muss den Fehler behandeln. |
| 63 | <code>        wire = text.encode("ascii") + b"\r\n"</code> | Setzt die tatsächlich gesendeten Befehlsbytes einschließlich CRLF. Rechte Seite: text.encode('ascii') + b'\r\n'. |
| 64 | <code>        if len(wire) &gt; 255:</code> | Prüft die Bedingung len(wire) &gt; 255. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 65 | <code>            raise ValueError("POP3-Befehl länger als 255 Bytes")</code> | Bricht diesen Pfad mit ValueError('POP3-Befehl länger als 255 Bytes') ab; Aufrufer/Test muss den Fehler behandeln. |
| 66 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 67 | <code>            self.socket.sendall(wire)</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. self.socket.sendall(wire). |
| 68 | <code>            result = self.status()</code> | Wertet self.status() aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 69 | <code>            if not multiline:</code> | Prüft die Bedingung not multiline. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 70 | <code>                return result</code> | Beendet diesen Funktionsaufruf und liefert result an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 71 | <code>            lines = []</code> | Setzt die gesammelten/auszugebenden Datenzeilen, getrennt von Status und Endmarke. Rechte Seite: []. |
| 72 | <code>            size = 0</code> | Setzt die bisherige Datenlänge in Bytes zur Ressourcenbegrenzung. Rechte Seite: 0. |
| 73 | <code>            while True:</code> | Wiederholt den eingerückten Empfangs-/Verarbeitungsblock solange True gilt; break oder return beendet die Schleife. |
| 74 | <code>                line = self.read_line()</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: self.read_line(). |
| 75 | <code>                if line == b".":</code> | Prüft die Bedingung line == b'.'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 76 | <code>                    return lines</code> | Beendet diesen Funktionsaufruf und liefert lines an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 77 | <code>                if line.startswith(b".."):</code> | Prüft die Bedingung line.startswith(b'..'). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 78 | <code>                    line = line[1:]</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: line[1:]. |
| 79 | <code>                elif line.startswith(b"."):</code> | Prüft die Bedingung line.startswith(b'.'). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 80 | <code>                    raise ProtocolError("Nicht dot-gestuffte Datenzeile")</code> | Bricht diesen Pfad mit ProtocolError('Nicht dot-gestuffte Datenzeile') ab; Aufrufer/Test muss den Fehler behandeln. |
| 81 | <code>                size += len(line) + 2</code> | Aktualisiert size mit dem zusätzlichen Wert len(line) + 2; hier wird insbesondere die Ressourcen-/Bytezählung fortgeführt. |
| 82 | <code>                if size &gt; 20 * 1024 * 1024:</code> | Prüft die Bedingung size &gt; 20 * 1024 * 1024. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 83 | <code>                    raise ProtocolError("Labordatenlimit von 20 MiB überschritten")</code> | Bricht diesen Pfad mit ProtocolError('Labordatenlimit von 20 MiB überschritten') ab; Aufrufer/Test muss den Fehler behandeln. |
| 84 | <code>                lines.append(line)</code> | Führt den Aufruf/Ausdruck lines.append(line) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 85 | <code>        except (ProtocolError, OSError):</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 86 | <code>            self.close()  # Nach Framing-/Transportfehlern keine weitere Synchronität annehmen.</code> | Führt den Aufruf/Ausdruck self.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 87 | <code>            raise</code> | Bricht diesen Pfad mit der ursprünglichen Ausnahme ab; Aufrufer/Test muss den Fehler behandeln. |
| 88 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 89 | <code>    def login(self, user, password):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. USER und PASS nacheinander; Passwort nie protokollieren. |
| 90 | <code>        """USER und PASS nacheinander; Passwort nie protokollieren."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 91 | <code>        if not user or " " in user or not password:</code> | Prüft die Bedingung not user or ' ' in user or (not password). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 92 | <code>            raise ValueError("Benutzer ohne Leerzeichen und nichtleeres Passwort erforderlich")</code> | Bricht diesen Pfad mit ValueError('Benutzer ohne Leerzeichen und nichtleeres Passwort erforderlich') ab; Aufrufer/Test muss den Fehler behandeln. |
| 93 | <code>        self.command(f"USER {user}")</code> | Führt den Aufruf/Ausdruck self.command(f'USER {user}') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 94 | <code>        return self.command(f"PASS {password}")</code> | Beendet diesen Funktionsaufruf und liefert self.command(f'PASS {password}') an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 95 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 96 | <code>    def list_messages(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. LIST ohne Argument liefert alle (Nummer, Oktettzahl)-Paare. |
| 97 | <code>        """LIST ohne Argument liefert alle (Nummer, Oktettzahl)-Paare."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 98 | <code>        lines = self.command("LIST", multiline=True)</code> | Setzt die gesammelten/auszugebenden Datenzeilen, getrennt von Status und Endmarke. Rechte Seite: self.command('LIST', multiline=True). |
| 99 | <code>        result = []</code> | Wertet [] aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 100 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 101 | <code>            for line in lines:</code> | Durchläuft lines; pro Element wird line gesetzt und der eingerückte Körper ausgeführt. |
| 102 | <code>                number, size = line.split()</code> | Wertet line.split() aus und speichert das Ergebnis in (number, size); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 103 | <code>                if not number.isdigit() or not size.isdigit() or int(number) &lt; 1:</code> | Prüft die Bedingung not number.isdigit() or not size.isdigit() or int(number) &lt; 1. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 104 | <code>                    raise ValueError("invalid listing")</code> | Bricht diesen Pfad mit ValueError('invalid listing') ab; Aufrufer/Test muss den Fehler behandeln. |
| 105 | <code>                result.append((int(number), int(size)))</code> | Führt den Aufruf/Ausdruck result.append((int(number), int(size))) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 106 | <code>            if len({number for number, _ in result}) != len(result):</code> | Prüft die Bedingung len({number for number, _ in result}) != len(result). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 107 | <code>                raise ValueError("duplicate message number")</code> | Bricht diesen Pfad mit ValueError('duplicate message number') ab; Aufrufer/Test muss den Fehler behandeln. |
| 108 | <code>        except ValueError as error:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 109 | <code>            self.close()</code> | Führt den Aufruf/Ausdruck self.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 110 | <code>            raise ProtocolError("Ungültige LIST-Daten") from error</code> | Bricht diesen Pfad mit ProtocolError('Ungültige LIST-Daten') ab; Aufrufer/Test muss den Fehler behandeln. |
| 111 | <code>        return result</code> | Beendet diesen Funktionsaufruf und liefert result an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 112 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 113 | <code>    def retrieve(self, number):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Eine Mail als Bytes inklusive wiederhergestellter CRLF zurückgeben. |
| 114 | <code>        """Eine Mail als Bytes inklusive wiederhergestellter CRLF zurückgeben."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 115 | <code>        if not isinstance(number, int) or number &lt; 1:</code> | Prüft die Bedingung not isinstance(number, int) or number &lt; 1. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 116 | <code>            raise ValueError("Positive Nachrichtennummer erforderlich")</code> | Bricht diesen Pfad mit ValueError('Positive Nachrichtennummer erforderlich') ab; Aufrufer/Test muss den Fehler behandeln. |
| 117 | <code>        lines = self.command(f"RETR {number}", multiline=True)</code> | Setzt die gesammelten/auszugebenden Datenzeilen, getrennt von Status und Endmarke. Rechte Seite: self.command(f'RETR {number}', multiline=True). |
| 118 | <code>        return b"".join(line + b"\r\n" for line in lines)</code> | Beendet diesen Funktionsaufruf und liefert b''.join((line + b'\r\n' for line in lines)) an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 119 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 120 | <code>    def quit(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. QUIT bestätigen lassen und auch bei Fehlern lokale Ressourcen schließen. |
| 121 | <code>        """QUIT bestätigen lassen und auch bei Fehlern lokale Ressourcen schließen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 122 | <code>        if self.closed:</code> | Prüft die Bedingung self.closed. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 123 | <code>            return None</code> | Beendet diesen Funktionsaufruf und liefert None an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 124 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 125 | <code>            return self.command("QUIT")</code> | Beendet diesen Funktionsaufruf und liefert self.command('QUIT') an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 126 | <code>        finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 127 | <code>            self.close()</code> | Führt den Aufruf/Ausdruck self.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 128 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 129 | <code>    def close(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Nur Transport schließen; ohne QUIT gibt es keinen UPDATE-Auftrag. |
| 130 | <code>        """Nur Transport schließen; ohne QUIT gibt es keinen UPDATE-Auftrag."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 131 | <code>        if not self.closed:</code> | Prüft die Bedingung not self.closed. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 132 | <code>            self.closed = True</code> | Setzt den lokalen Lebenszykluszustand, damit mehrfaches close sicher ist. Rechte Seite: True. |
| 133 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 134 | <code>                self.reader.close()</code> | Führt den Aufruf/Ausdruck self.reader.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 135 | <code>            finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 136 | <code>                self.socket.close()</code> | Führt den Aufruf/Ausdruck self.socket.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 137 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 138 | <code>    def __enter__(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Gibt das Clientobjekt für den with-Block zurück; die Verbindung besteht bereits. |
| 139 | <code>        return self</code> | Beendet diesen Funktionsaufruf und liefert self an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 140 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 141 | <code>    def __exit__(self, exception_type, exception, traceback):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Erfolgreicher Block: QUIT. Ausnahme: nur close, damit kein ungewollter UPDATE bestätigt wird. |
| 142 | <code>        if exception_type is None:</code> | Prüft die Bedingung exception_type is None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 143 | <code>            self.quit()</code> | Führt den Aufruf/Ausdruck self.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 144 | <code>        else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 145 | <code>            self.close()  # Fehlerpfad bricht ab, statt mögliche Löschungen zu bestätigen.</code> | Führt den Aufruf/Ausdruck self.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 146 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 147 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 148 | <code>def main(argv=None):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Testkonto anmelden, alle Nachrichten auflisten und genau eine abrufen. |
| 149 | <code>    """Testkonto anmelden, alle Nachrichten auflisten und genau eine abrufen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 150 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Wertet argparse.ArgumentParser(description=__doc__) aus und speichert das Ergebnis in parser; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 151 | <code>    parser.add_argument("--host", default="127.0.0.1")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--host', default='127.0.0.1'). |
| 152 | <code>    parser.add_argument("--port", type=int, default=11110)</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--port', type=int, default=11110). |
| 153 | <code>    parser.add_argument("--user", default="alice")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--user', default='alice'). |
| 154 | <code>    parser.add_argument("--password", help="Nur für Testdaten; sonst verdeckte Abfrage")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--password', help='Nur für Testdaten; sonst verdeckte Abfrage'). |
| 155 | <code>    parser.add_argument("--message", type=int, default=1)</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--message', type=int, default=1). |
| 156 | <code>    parser.add_argument("--timeout", type=float, default=10)</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--timeout', type=float, default=10). |
| 157 | <code>    parser.add_argument("--allow-remote-plaintext", action="store_true")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--allow-remote-plaintext', action='store_true'). |
| 158 | <code>    args = parser.parse_args(argv)</code> | Setzt die mit einzelnen Leerzeichen getrennten Argumente für Syntaxprüfung. Rechte Seite: parser.parse_args(argv). |
| 159 | <code>    try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 160 | <code>        local = ipaddress.ip_address(args.host).is_loopback</code> | Wertet ipaddress.ip_address(args.host).is_loopback aus und speichert das Ergebnis in local; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 161 | <code>    except ValueError:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 162 | <code>        local = args.host == "localhost"</code> | Wertet args.host == 'localhost' aus und speichert das Ergebnis in local; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 163 | <code>    if not local and not args.allow_remote_plaintext:</code> | Prüft die Bedingung not local and (not args.allow_remote_plaintext). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 164 | <code>        parser.error("Nicht-Loopback benötigt --allow-remote-plaintext; keine echten Passwörter!")</code> | Führt den Aufruf/Ausdruck parser.error('Nicht-Loopback benötigt --allow-remote-plaintext; keine echten Passwörter!') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 165 | <code>    password = args.password if args.password is not None else getpass.getpass("POP3-Testpasswort: ")</code> | Wertet args.password if args.password is not None else getpass.getpass('POP3-Testpasswort: ') aus und speichert das Ergebnis in password; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 166 | <code>    try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 167 | <code>        with POP3Client(args.host, args.port, args.timeout) as client:</code> | Öffnet die Kontexte POP3Client(args.host, args.port, args.timeout). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 168 | <code>            print(client.greeting.decode("ascii"))</code> | Führt den Aufruf/Ausdruck print(client.greeting.decode('ascii')) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 169 | <code>            client.login(args.user, password)</code> | Führt den Aufruf/Ausdruck client.login(args.user, password) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 170 | <code>            listing = client.list_messages()</code> | Wertet client.list_messages() aus und speichert das Ergebnis in listing; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 171 | <code>            print("LIST (Nummer, Oktette):", listing)</code> | Führt den Aufruf/Ausdruck print('LIST (Nummer, Oktette):', listing) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 172 | <code>            if listing:</code> | Prüft die Bedingung listing. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 173 | <code>                print(f"RETR {args.message}:")</code> | Führt den Aufruf/Ausdruck print(f'RETR {args.message}:') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 174 | <code>                print(client.retrieve(args.message).decode("utf-8", errors="replace"), end="")</code> | Führt den Aufruf/Ausdruck print(client.retrieve(args.message).decode('utf-8', errors='replace'), end='') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 175 | <code>            else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 176 | <code>                print("Maildrop leer; keine Nachricht abrufbar.")</code> | Führt den Aufruf/Ausdruck print('Maildrop leer; keine Nachricht abrufbar.') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 177 | <code>        print("QUIT bestätigt; Verbindung geschlossen.")</code> | Führt den Aufruf/Ausdruck print('QUIT bestätigt; Verbindung geschlossen.') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 178 | <code>    except (OSError, POP3Error, ProtocolError, ValueError) as error:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 179 | <code>        print(f"POP3-Fehler: {error}", file=sys.stderr)</code> | Führt den Aufruf/Ausdruck print(f'POP3-Fehler: {error}', file=sys.stderr) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 180 | <code>        return 1</code> | Beendet diesen Funktionsaufruf und liefert 1 an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 181 | <code>    return 0</code> | Beendet diesen Funktionsaufruf und liefert 0 an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 182 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 183 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 184 | <code>if __name__ == "__main__":</code> | Startet main/unittest nur bei direktem Skriptaufruf, nicht beim Import durch GUI oder Tests. |
| 185 | <code>    raise SystemExit(main())</code> | Bricht diesen Pfad mit SystemExit(main()) ab; Aufrufer/Test muss den Fehler behandeln. |

### `ue3.2/test_pop3_client.py`

Quellstand SHA-256: `4c278d782060081fe00398dab125998b886182fa883012f2f987a7216a0d6530`.

#### Funktionen und Methoden

- **`scripted_server` (Zeilen 19–54):** Ein echtes TCP-Gegenüber; (erwarteter Befehl, Antwort), None = Begrüßung.
- **`run` (Zeilen 27–42):** Führt den erwarteten Testdialog im Gegenüber-Thread aus; sammelt Fehler zur Weitergabe im Testthread.
- **`load_server` (Zeilen 57–65):** Server aus Nachbarverzeichnis laden; keine Änderung am Originalpaket.
- **`test_fragmented_full_session_and_dot_unstuffing` (Zeilen 69–81):** Prüft den gesamten Dialog mit byteweise gesendeten Antworten und Punktdaten.
- **`test_negative_list_is_single_line_and_session_stays_usable` (Zeilen 83–89):** Beweist, dass -ERR keine Punkt-Endmarke benötigt und die Sitzung synchron bleibt.
- **`test_rejected_login_cli_does_not_leak_password` (Zeilen 91–101):** Startet die Client-CLI mit falschem künstlichem Passwort und prüft Exitcode/Geheimnisfreiheit der Ausgabe.
- **`test_greeting_errors_close_connection` (Zeilen 103–112):** Prüft Ablehnung, falschen Status, nacktes LF und zu lange Begrüßung samt Ressourcenfreigabe.
- **`test_truncated_multiline_and_invalid_dot_stuffing` (Zeilen 114–121):** Prüft EOF vor Terminator und unerlaubte einzelne Anfangspunkte.
- **`test_malformed_listing_rejected` (Zeilen 123–131):** Prüft fehlende Felder, ungültige Nummern/Größen und doppelte Nummern.
- **`test_injection_length_and_invalid_message_blocked_locally` (Zeilen 133–146):** Beweist, dass manipulierte/zu lange Befehle und ungültige RETR-Nummern gar nicht gesendet werden.
- **`test_context_exception_aborts_without_quit` (Zeilen 148–153):** Beweist, dass eine Ausnahme den Transport schließt, statt mit QUIT UPDATE anzufordern.
- **`test_quit_error_still_closes` (Zeilen 155–160):** Ein QUIT-Fehler muss sichtbar bleiben, aber trotzdem Socket und Reader freigeben.
- **`test_full_socket_client_against_own_server_and_cli` (Zeilen 162–184):** Prüft echte gemeinsame TCP-Sitzung und separaten Clientprozess gegen die laufende Serverinstanz.
- **`test_empty_mailbox_cli_quits_without_retr` (Zeilen 186–196):** Prüft, dass leeres LIST zum sauberen QUIT und nicht zu ungültigem RETR führt.

#### Jede physische Codezeile

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)</code> | Kommentar/KI-Nachweis: KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). Kein ausführbarer Python-Befehl. |
| 2 | <code># Datum: 2026-10-19</code> | Kommentar/KI-Nachweis: Datum: 2026-10-19. Kein ausführbarer Python-Befehl. |
| 3 | <code># Anfrage: Ü3.2 mit unabhängigem skriptgesteuertem TCP-Gegenüber und dem Ü3.3-Server inklusive Fehler- und Fragmentierungspfaden testen.</code> | Kommentar/KI-Nachweis: Anfrage: Ü3.2 mit unabhängigem skriptgesteuertem TCP-Gegenüber und dem Ü3.3-Server inklusive Fehler- und Fragmentierungspfaden testen.. Kein ausführbarer Python-Befehl. |
| 4 | <code>"""Socket-Tests ohne poplib im eigenen Client und ohne Fremdpakete."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 5 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 6 | <code>from contextlib import contextmanager</code> | Standard-/Modulimport: macht aus einem Generator einen sicher aufräumenden Kontextmanager. |
| 7 | <code>import importlib.util</code> | Standard-/Modulimport: lädt Originaldatenbank oder Nachbarserver anhand eines absoluten Dateipfads. |
| 8 | <code>from pathlib import Path</code> | Standard-/Modulimport: konstruiert Dateipfade unabhängig vom aktuellen Arbeitsverzeichnis. |
| 9 | <code>import socket</code> | Standard-/Modulimport: stellt TCP-Verbindungen, Socketoptionen und Shutdown bereit. |
| 10 | <code>import subprocess</code> | Standard-/Modulimport: startet echte, getrennte Python-Prozesse für CLI-Integration. |
| 11 | <code>import sys</code> | Standard-/Modulimport: liefert stderr und den aktuellen Python-Interpreter für echte CLI-Unterprozesse. |
| 12 | <code>import threading</code> | Standard-/Modulimport: stellt Threads, Locks, Barrier und Event zur Synchronisation bereit. |
| 13 | <code>import unittest</code> | Standard-/Modulimport: führt überprüfbare Tests und Assertions aus. |
| 14 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 15 | <code>from pop3_client import POP3Client, POP3Error, ProtocolError</code> | Standard-/Modulimport: importiert den eigenen Client und dessen beide unterscheidbaren Fehlerklassen. |
| 16 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 17 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 18 | <code>@contextmanager</code> | Dekorator: ergänzt den folgenden Funktionsvertrag. overload beschreibt nur Rückgabetypen; contextmanager steuert Öffnen und garantiertes Aufräumen eines Generator-Kontexts. |
| 19 | <code>def scripted_server(steps, fragmented=True):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Ein echtes TCP-Gegenüber; (erwarteter Befehl, Antwort), None = Begrüßung. |
| 20 | <code>    """Ein echtes TCP-Gegenüber; (erwarteter Befehl, Antwort), None = Begrüßung."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 21 | <code>    listener = socket.socket()</code> | Wertet socket.socket() aus und speichert das Ergebnis in listener; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 22 | <code>    listener.bind(("127.0.0.1", 0))</code> | Führt den Aufruf/Ausdruck listener.bind(('127.0.0.1', 0)) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 23 | <code>    listener.listen(1)</code> | Führt den Aufruf/Ausdruck listener.listen(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 24 | <code>    listener.settimeout(3)</code> | Führt den Aufruf/Ausdruck listener.settimeout(3) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 25 | <code>    errors = []</code> | Wertet [] aus und speichert das Ergebnis in errors; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 26 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 27 | <code>    def run():</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Führt den erwarteten Testdialog im Gegenüber-Thread aus; sammelt Fehler zur Weitergabe im Testthread. |
| 28 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 29 | <code>            with listener.accept()[0] as connection:</code> | Öffnet die Kontexte listener.accept()[0]. Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 30 | <code>                connection.settimeout(3)</code> | Führt den Aufruf/Ausdruck connection.settimeout(3) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 31 | <code>                connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)</code> | Führt den Aufruf/Ausdruck connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 32 | <code>                with connection.makefile("rb") as reader:</code> | Öffnet die Kontexte connection.makefile('rb'). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 33 | <code>                    for expected, reply in steps:</code> | Durchläuft steps; pro Element wird (expected, reply) gesetzt und der eingerückte Körper ausgeführt. |
| 34 | <code>                        if expected is not None:</code> | Prüft die Bedingung expected is not None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 35 | <code>                            actual = reader.readline()</code> | Wertet reader.readline() aus und speichert das Ergebnis in actual; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 36 | <code>                            if actual != expected:</code> | Prüft die Bedingung actual != expected. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 37 | <code>                                raise AssertionError(f"Erwartet {expected!r}, erhalten {actual!r}")</code> | Bricht diesen Pfad mit AssertionError(f'Erwartet {expected!r}, erhalten {actual!r}') ab; Aufrufer/Test muss den Fehler behandeln. |
| 38 | <code>                        chunks = (bytes([octet]) for octet in reply) if fragmented else [reply]</code> | Wertet (bytes([octet]) for octet in reply) if fragmented else [reply] aus und speichert das Ergebnis in chunks; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 39 | <code>                        for chunk in chunks:</code> | Durchläuft chunks; pro Element wird chunk gesetzt und der eingerückte Körper ausgeführt. |
| 40 | <code>                            connection.sendall(chunk)</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(chunk). |
| 41 | <code>        except BaseException as error:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 42 | <code>            errors.append(error)</code> | Führt den Aufruf/Ausdruck errors.append(error) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 43 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 44 | <code>    worker = threading.Thread(target=run)</code> | Wertet threading.Thread(target=run) aus und speichert das Ergebnis in worker; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 45 | <code>    worker.start()</code> | Führt den Aufruf/Ausdruck worker.start() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 46 | <code>    try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 47 | <code>        yield listener.getsockname()</code> | Gibt dem with-Aufrufer die Listeneradresse; nach dem Test wird am Generator weitergemacht und in finally aufgeräumt. |
| 48 | <code>    finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 49 | <code>        worker.join(5)</code> | Wartet begrenzt auf den gestarteten Thread; die nachfolgende Prüfung muss ein Hängen sichtbar machen. worker.join(5). |
| 50 | <code>        listener.close()</code> | Führt den Aufruf/Ausdruck listener.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 51 | <code>        if worker.is_alive():</code> | Prüft die Bedingung worker.is_alive(). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 52 | <code>            raise AssertionError("Testgegenüber hängt")</code> | Bricht diesen Pfad mit AssertionError('Testgegenüber hängt') ab; Aufrufer/Test muss den Fehler behandeln. |
| 53 | <code>        if errors:</code> | Prüft die Bedingung errors. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 54 | <code>            raise errors[0]</code> | Bricht diesen Pfad mit errors[0] ab; Aufrufer/Test muss den Fehler behandeln. |
| 55 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 56 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 57 | <code>def load_server():</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Server aus Nachbarverzeichnis laden; keine Änderung am Originalpaket. |
| 58 | <code>    """Server aus Nachbarverzeichnis laden; keine Änderung am Originalpaket."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 59 | <code>    path = Path(__file__).resolve().parents[1] / "ue3.3" / "pop3_server.py"</code> | Wertet Path(__file__).resolve().parents[1] / 'ue3.3' / 'pop3_server.py' aus und speichert das Ergebnis in path; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 60 | <code>    spec = importlib.util.spec_from_file_location("rn_pop3_integration_server", path)</code> | Wertet importlib.util.spec_from_file_location('rn_pop3_integration_server', path) aus und speichert das Ergebnis in spec; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 61 | <code>    if spec is None or spec.loader is None:</code> | Prüft die Bedingung spec is None or spec.loader is None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 62 | <code>        raise ImportError(path)</code> | Bricht diesen Pfad mit ImportError(path) ab; Aufrufer/Test muss den Fehler behandeln. |
| 63 | <code>    module = importlib.util.module_from_spec(spec)</code> | Wertet importlib.util.module_from_spec(spec) aus und speichert das Ergebnis in module; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 64 | <code>    spec.loader.exec_module(module)</code> | Führt den Aufruf/Ausdruck spec.loader.exec_module(module) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 65 | <code>    return module</code> | Beendet diesen Funktionsaufruf und liefert module an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 66 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 67 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 68 | <code>class ClientTests(unittest.TestCase):</code> | Definiert die Klasse und ihre Basisklassen. Bündelt die zugehörigen Testmethoden; unittest erzeugt für jeden Test einen frischen Ablauf. |
| 69 | <code>    def test_fragmented_full_session_and_dot_unstuffing(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft den gesamten Dialog mit byteweise gesendeten Antworten und Punktdaten. |
| 70 | <code>        steps = [(None, b"+OK ready\r\n"),</code> | Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 71 | <code>                 (b"USER alice\r\n", b"+OK user\r\n"),</code> | Fortsetzungszeile der Anweisung ab Zeile 70. Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 72 | <code>                 (b"PASS secret\r\n", b"+OK pass\r\n"),</code> | Fortsetzungszeile der Anweisung ab Zeile 70. Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 73 | <code>                 (b"LIST\r\n", b"+OK list\r\n1 29\r\n2 12\r\n.\r\n"),</code> | Fortsetzungszeile der Anweisung ab Zeile 70. Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 74 | <code>                 (b"RETR 1\r\n", b"+OK data\r\nSubject: Dots\r\n\r\n..a\r\n..\r\n...b\r\n.\r\n"),</code> | Fortsetzungszeile der Anweisung ab Zeile 70. Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 75 | <code>                 (b"QUIT\r\n", b"+OK bye\r\n")]</code> | Fortsetzungszeile der Anweisung ab Zeile 70. Wertet [(None, b'+OK ready\r\n'), (b'USER alice\r\n', b'+OK user\r\n'), (b'PASS secret\r\n', b'+OK pass\r\n'), (b'LIST\r\n', b'+OK list\r\n1 29\r\n2 12\r\n.\r\n'), (b'RETR 1\r\n', b'+OK data\r\n… aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 76 | <code>        with scripted_server(steps) as address:</code> | Öffnet die Kontexte scripted_server(steps). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 77 | <code>            with POP3Client(*address) as client:</code> | Öffnet die Kontexte POP3Client(*address). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 78 | <code>                client.login("alice", "secret")</code> | Führt den Aufruf/Ausdruck client.login('alice', 'secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 79 | <code>                self.assertEqual(client.list_messages(), [(1, 29), (2, 12)])</code> | Testassertion: self.assertEqual(client.list_messages(), [(1, 29), (2, 12)]). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 80 | <code>                self.assertEqual(client.retrieve(1), b"Subject: Dots\r\n\r\n.a\r\n.\r\n..b\r\n")</code> | Testassertion: self.assertEqual(client.retrieve(1), b'Subject: Dots\r\n\r\n.a\r\n.\r\n..b\r\n'). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 81 | <code>            self.assertTrue(client.closed)</code> | Testassertion: self.assertTrue(client.closed). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 82 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 83 | <code>    def test_negative_list_is_single_line_and_session_stays_usable(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Beweist, dass -ERR keine Punkt-Endmarke benötigt und die Sitzung synchron bleibt. |
| 84 | <code>        steps = [(None, b"+OK\r\n"), (b"LIST\r\n", b"-ERR not logged in\r\n"),</code> | Wertet [(None, b'+OK\r\n'), (b'LIST\r\n', b'-ERR not logged in\r\n'), (b'NOOP\r\n', b'+OK\r\n'), (b'QUIT\r\n', b'+OK\r\n')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 85 | <code>                 (b"NOOP\r\n", b"+OK\r\n"), (b"QUIT\r\n", b"+OK\r\n")]</code> | Fortsetzungszeile der Anweisung ab Zeile 84. Wertet [(None, b'+OK\r\n'), (b'LIST\r\n', b'-ERR not logged in\r\n'), (b'NOOP\r\n', b'+OK\r\n'), (b'QUIT\r\n', b'+OK\r\n')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 86 | <code>        with scripted_server(steps) as address, POP3Client(*address) as client:</code> | Öffnet die Kontexte scripted_server(steps), POP3Client(*address). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 87 | <code>            with self.assertRaises(POP3Error):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(POP3Error). |
| 88 | <code>                client.list_messages()</code> | Führt den Aufruf/Ausdruck client.list_messages() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 89 | <code>            self.assertEqual(client.command("NOOP"), b"+OK")</code> | Testassertion: self.assertEqual(client.command('NOOP'), b'+OK'). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 90 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 91 | <code>    def test_rejected_login_cli_does_not_leak_password(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Startet die Client-CLI mit falschem künstlichem Passwort und prüft Exitcode/Geheimnisfreiheit der Ausgabe. |
| 92 | <code>        steps = [(None, b"+OK\r\n"), (b"USER alice\r\n", b"+OK\r\n"),</code> | Wertet [(None, b'+OK\r\n'), (b'USER alice\r\n', b'+OK\r\n'), (b'PASS lab-only-sensitive\r\n', b'-ERR bad login\r\n'), (b'', b'')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 93 | <code>                 (b"PASS lab-only-sensitive\r\n", b"-ERR bad login\r\n"), (b"", b"")]</code> | Fortsetzungszeile der Anweisung ab Zeile 92. Wertet [(None, b'+OK\r\n'), (b'USER alice\r\n', b'+OK\r\n'), (b'PASS lab-only-sensitive\r\n', b'-ERR bad login\r\n'), (b'', b'')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 94 | <code>        with scripted_server(steps) as address:</code> | Öffnet die Kontexte scripted_server(steps). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 95 | <code>            result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),</code> | Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--host', address[0], '--port', str(address[1]), '--password', 'lab-only-sensitive'], capture_output=True,… aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 96 | <code>                                     "--host", address[0], "--port", str(address[1]),</code> | Fortsetzungszeile der Anweisung ab Zeile 95. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--host', address[0], '--port', str(address[1]), '--password', 'lab-only-sensitive'], capture_output=True,… aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 97 | <code>                                     "--password", "lab-only-sensitive"],</code> | Fortsetzungszeile der Anweisung ab Zeile 95. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--host', address[0], '--port', str(address[1]), '--password', 'lab-only-sensitive'], capture_output=True,… aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 98 | <code>                                    capture_output=True, text=True, timeout=5)</code> | Fortsetzungszeile der Anweisung ab Zeile 95. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--host', address[0], '--port', str(address[1]), '--password', 'lab-only-sensitive'], capture_output=True,… aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 99 | <code>        self.assertEqual(result.returncode, 1)</code> | Testassertion: self.assertEqual(result.returncode, 1). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 100 | <code>        self.assertIn("bad login", result.stderr)</code> | Testassertion: self.assertIn('bad login', result.stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 101 | <code>        self.assertNotIn("lab-only-sensitive", result.stdout + result.stderr)</code> | Testassertion: self.assertNotIn('lab-only-sensitive', result.stdout + result.stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 102 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 103 | <code>    def test_greeting_errors_close_connection(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft Ablehnung, falschen Status, nacktes LF und zu lange Begrüßung samt Ressourcenfreigabe. |
| 104 | <code>        for greeting, error in [(b"-ERR unavailable\r\n", POP3Error),</code> | Durchläuft [(b'-ERR unavailable\r\n', POP3Error), (b'HELLO\r\n', ProtocolError), (b'+OKX\r\n', ProtocolError), (b'+OK\n', ProtocolError), (b'+OK ' + b'x' * 510 + b'\r\n', ProtocolError)]; pro Element wird (greeting, error) gesetzt und der eingerückte Körper ausgeführt. |
| 105 | <code>                                (b"HELLO\r\n", ProtocolError),</code> | Fortsetzungszeile der Anweisung ab Zeile 104. Durchläuft [(b'-ERR unavailable\r\n', POP3Error), (b'HELLO\r\n', ProtocolError), (b'+OKX\r\n', ProtocolError), (b'+OK\n', ProtocolError), (b'+OK ' + b'x' * 510 + b'\r\n', ProtocolError)]; pro Element wird (greeting, error) gesetzt und der eingerückte Körper ausgeführt. |
| 106 | <code>                                (b"+OKX\r\n", ProtocolError),</code> | Fortsetzungszeile der Anweisung ab Zeile 104. Durchläuft [(b'-ERR unavailable\r\n', POP3Error), (b'HELLO\r\n', ProtocolError), (b'+OKX\r\n', ProtocolError), (b'+OK\n', ProtocolError), (b'+OK ' + b'x' * 510 + b'\r\n', ProtocolError)]; pro Element wird (greeting, error) gesetzt und der eingerückte Körper ausgeführt. |
| 107 | <code>                                (b"+OK\n", ProtocolError),</code> | Fortsetzungszeile der Anweisung ab Zeile 104. Durchläuft [(b'-ERR unavailable\r\n', POP3Error), (b'HELLO\r\n', ProtocolError), (b'+OKX\r\n', ProtocolError), (b'+OK\n', ProtocolError), (b'+OK ' + b'x' * 510 + b'\r\n', ProtocolError)]; pro Element wird (greeting, error) gesetzt und der eingerückte Körper ausgeführt. |
| 108 | <code>                                (b"+OK " + b"x" * 510 + b"\r\n", ProtocolError)]:</code> | Fortsetzungszeile der Anweisung ab Zeile 104. Durchläuft [(b'-ERR unavailable\r\n', POP3Error), (b'HELLO\r\n', ProtocolError), (b'+OKX\r\n', ProtocolError), (b'+OK\n', ProtocolError), (b'+OK ' + b'x' * 510 + b'\r\n', ProtocolError)]; pro Element wird (greeting, error) gesetzt und der eingerückte Körper ausgeführt. |
| 109 | <code>            with self.subTest(greeting=greeting[:20]):</code> | Öffnet die Kontexte self.subTest(greeting=greeting[:20]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 110 | <code>                with scripted_server([(None, greeting), (b"", b"")], fragmented=False) as address:</code> | Öffnet die Kontexte scripted_server([(None, greeting), (b'', b'')], fragmented=False). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 111 | <code>                    with self.assertRaises(error):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(error). |
| 112 | <code>                        POP3Client(*address)</code> | Führt den Aufruf/Ausdruck POP3Client(*address) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 113 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 114 | <code>    def test_truncated_multiline_and_invalid_dot_stuffing(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft EOF vor Terminator und unerlaubte einzelne Anfangspunkte. |
| 115 | <code>        for response in (b"+OK\r\nSubject: x\r\n", b"+OK\r\n.bad\r\n"):</code> | Durchläuft (b'+OK\r\nSubject: x\r\n', b'+OK\r\n.bad\r\n'); pro Element wird response gesetzt und der eingerückte Körper ausgeführt. |
| 116 | <code>            with self.subTest(response=response):</code> | Öffnet die Kontexte self.subTest(response=response). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 117 | <code>                with scripted_server([(None, b"+OK\r\n"), (b"RETR 1\r\n", response)], fragmented=False) as address:</code> | Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'RETR 1\r\n', response)], fragmented=False). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 118 | <code>                    client = POP3Client(*address)</code> | Wertet POP3Client(*address) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 119 | <code>                    with self.assertRaises(ProtocolError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(ProtocolError). |
| 120 | <code>                        client.retrieve(1)</code> | Führt den Aufruf/Ausdruck client.retrieve(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 121 | <code>                    self.assertTrue(client.closed)</code> | Testassertion: self.assertTrue(client.closed). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 122 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 123 | <code>    def test_malformed_listing_rejected(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft fehlende Felder, ungültige Nummern/Größen und doppelte Nummern. |
| 124 | <code>        for data in (b"1\r\n", b"0 12\r\n", b"1 -4\r\n", b"one 4\r\n", b"1 4\r\n1 4\r\n"):</code> | Durchläuft (b'1\r\n', b'0 12\r\n', b'1 -4\r\n', b'one 4\r\n', b'1 4\r\n1 4\r\n'); pro Element wird data gesetzt und der eingerückte Körper ausgeführt. |
| 125 | <code>            with self.subTest(data=data):</code> | Öffnet die Kontexte self.subTest(data=data). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 126 | <code>                with scripted_server([(None, b"+OK\r\n"),</code> | Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'LIST\r\n', b'+OK\r\n' + data + b'.\r\n')]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 127 | <code>                                      (b"LIST\r\n", b"+OK\r\n" + data + b".\r\n")]) as address:</code> | Fortsetzungszeile der Anweisung ab Zeile 126. Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'LIST\r\n', b'+OK\r\n' + data + b'.\r\n')]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 128 | <code>                    client = POP3Client(*address)</code> | Wertet POP3Client(*address) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 129 | <code>                    with self.assertRaises(ProtocolError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(ProtocolError). |
| 130 | <code>                        client.list_messages()</code> | Führt den Aufruf/Ausdruck client.list_messages() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 131 | <code>                    self.assertTrue(client.closed)</code> | Testassertion: self.assertTrue(client.closed). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 132 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 133 | <code>    def test_injection_length_and_invalid_message_blocked_locally(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Beweist, dass manipulierte/zu lange Befehle und ungültige RETR-Nummern gar nicht gesendet werden. |
| 134 | <code>        with scripted_server([(None, b"+OK\r\n"), (b"QUIT\r\n", b"+OK\r\n")]) as address:</code> | Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'QUIT\r\n', b'+OK\r\n')]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 135 | <code>            with POP3Client(*address) as client:</code> | Öffnet die Kontexte POP3Client(*address). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 136 | <code>                for command in ("USER alice\r\nDELE 1", "USER ä", "X" * 254, "NOOP\t"):</code> | Durchläuft ('USER alice\r\nDELE 1', 'USER ä', 'X' * 254, 'NOOP\t'); pro Element wird command gesetzt und der eingerückte Körper ausgeführt. |
| 137 | <code>                    with self.subTest(command=command), self.assertRaises(ValueError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.subTest(command=command), self.assertRaises(ValueError). |
| 138 | <code>                        client.command(command)</code> | Führt den Aufruf/Ausdruck client.command(command) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 139 | <code>                for number in (0, -1, "1"):</code> | Durchläuft (0, -1, '1'); pro Element wird number gesetzt und der eingerückte Körper ausgeführt. |
| 140 | <code>                    with self.subTest(number=number), self.assertRaises(ValueError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.subTest(number=number), self.assertRaises(ValueError). |
| 141 | <code>                        client.retrieve(number)</code> | Führt den Aufruf/Ausdruck client.retrieve(number) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 142 | <code>                with self.assertRaises(ValueError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(ValueError). |
| 143 | <code>                    client.login("alice bob", "secret")</code> | Führt den Aufruf/Ausdruck client.login('alice bob', 'secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 144 | <code>        with self.assertRaises(ProtocolError):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(ProtocolError). |
| 145 | <code>            client.command("NOOP")</code> | Führt den Aufruf/Ausdruck client.command('NOOP') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 146 | <code>        self.assertIsNone(client.quit())</code> | Testassertion: self.assertIsNone(client.quit()). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 147 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 148 | <code>    def test_context_exception_aborts_without_quit(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Beweist, dass eine Ausnahme den Transport schließt, statt mit QUIT UPDATE anzufordern. |
| 149 | <code>        with scripted_server([(None, b"+OK\r\n"), (b"", b"")]) as address:</code> | Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'', b'')]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 150 | <code>            with self.assertRaisesRegex(RuntimeError, "abort"):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaisesRegex(RuntimeError, 'abort'). |
| 151 | <code>                with POP3Client(*address) as client:</code> | Öffnet die Kontexte POP3Client(*address). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 152 | <code>                    raise RuntimeError("abort")</code> | Bricht diesen Pfad mit RuntimeError('abort') ab; Aufrufer/Test muss den Fehler behandeln. |
| 153 | <code>            self.assertTrue(client.closed)</code> | Testassertion: self.assertTrue(client.closed). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 154 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 155 | <code>    def test_quit_error_still_closes(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Ein QUIT-Fehler muss sichtbar bleiben, aber trotzdem Socket und Reader freigeben. |
| 156 | <code>        with scripted_server([(None, b"+OK\r\n"), (b"QUIT\r\n", b"-ERR update failed\r\n")]) as address:</code> | Öffnet die Kontexte scripted_server([(None, b'+OK\r\n'), (b'QUIT\r\n', b'-ERR update failed\r\n')]). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 157 | <code>            client = POP3Client(*address)</code> | Wertet POP3Client(*address) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 158 | <code>            with self.assertRaises(POP3Error):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(POP3Error). |
| 159 | <code>                client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 160 | <code>            self.assertTrue(client.closed)</code> | Testassertion: self.assertTrue(client.closed). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 161 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 162 | <code>    def test_full_socket_client_against_own_server_and_cli(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft echte gemeinsame TCP-Sitzung und separaten Clientprozess gegen die laufende Serverinstanz. |
| 163 | <code>        module = load_server()</code> | Wertet load_server() aus und speichert das Ergebnis in module; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 164 | <code>        with module.create_server(port=0) as server:</code> | Öffnet die Kontexte module.create_server(port=0). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 165 | <code>            worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})</code> | Wertet threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}) aus und speichert das Ergebnis in worker; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 166 | <code>            worker.start()</code> | Führt den Aufruf/Ausdruck worker.start() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 167 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 168 | <code>                with POP3Client(*server.server_address) as client:</code> | Öffnet die Kontexte POP3Client(*server.server_address). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 169 | <code>                    client.login("alice", "secret")</code> | Führt den Aufruf/Ausdruck client.login('alice', 'secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 170 | <code>                    listing = client.list_messages()</code> | Wertet client.list_messages() aus und speichert das Ergebnis in listing; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 171 | <code>                    self.assertEqual(len(listing), 4)</code> | Testassertion: self.assertEqual(len(listing), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 172 | <code>                    for number, size in listing:</code> | Durchläuft listing; pro Element wird (number, size) gesetzt und der eingerückte Körper ausgeführt. |
| 173 | <code>                        self.assertEqual(len(client.retrieve(number)), size)</code> | Testassertion: self.assertEqual(len(client.retrieve(number)), size). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 174 | <code>                result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),</code> | Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(server.server_address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 175 | <code>                                         "--port", str(server.server_address[1]), "--password", "secret"],</code> | Fortsetzungszeile der Anweisung ab Zeile 174. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(server.server_address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 176 | <code>                                        capture_output=True, text=True, timeout=5)</code> | Fortsetzungszeile der Anweisung ab Zeile 174. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(server.server_address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 177 | <code>                self.assertEqual(result.returncode, 0, result.stderr)</code> | Testassertion: self.assertEqual(result.returncode, 0, result.stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 178 | <code>                self.assertIn("Welcome to the POP3 lab", result.stdout)</code> | Testassertion: self.assertIn('Welcome to the POP3 lab', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 179 | <code>                self.assertIn("QUIT bestätigt", result.stdout)</code> | Testassertion: self.assertIn('QUIT bestätigt', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 180 | <code>                self.assertNotIn("secret", result.stdout)</code> | Testassertion: self.assertNotIn('secret', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 181 | <code>            finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 182 | <code>                server.shutdown()</code> | Beendet die angegebene Socket-/Accept-Aktivität und weckt blockierendes Warten; bei BaseServer erfolgt der Aufruf aus einem anderen Thread. server.shutdown(). |
| 183 | <code>                worker.join(3)</code> | Wartet begrenzt auf den gestarteten Thread; die nachfolgende Prüfung muss ein Hängen sichtbar machen. worker.join(3). |
| 184 | <code>                self.assertFalse(worker.is_alive())</code> | Testassertion: self.assertFalse(worker.is_alive()). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 185 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 186 | <code>    def test_empty_mailbox_cli_quits_without_retr(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft, dass leeres LIST zum sauberen QUIT und nicht zu ungültigem RETR führt. |
| 187 | <code>        steps = [(None, b"+OK\r\n"), (b"USER alice\r\n", b"+OK\r\n"),</code> | Wertet [(None, b'+OK\r\n'), (b'USER alice\r\n', b'+OK\r\n'), (b'PASS secret\r\n', b'+OK\r\n'), (b'LIST\r\n', b'+OK\r\n.\r\n'), (b'QUIT\r\n', b'+OK\r\n')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 188 | <code>                 (b"PASS secret\r\n", b"+OK\r\n"), (b"LIST\r\n", b"+OK\r\n.\r\n"),</code> | Fortsetzungszeile der Anweisung ab Zeile 187. Wertet [(None, b'+OK\r\n'), (b'USER alice\r\n', b'+OK\r\n'), (b'PASS secret\r\n', b'+OK\r\n'), (b'LIST\r\n', b'+OK\r\n.\r\n'), (b'QUIT\r\n', b'+OK\r\n')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 189 | <code>                 (b"QUIT\r\n", b"+OK\r\n")]</code> | Fortsetzungszeile der Anweisung ab Zeile 187. Wertet [(None, b'+OK\r\n'), (b'USER alice\r\n', b'+OK\r\n'), (b'PASS secret\r\n', b'+OK\r\n'), (b'LIST\r\n', b'+OK\r\n.\r\n'), (b'QUIT\r\n', b'+OK\r\n')] aus und speichert das Ergebnis in steps; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 190 | <code>        with scripted_server(steps) as address:</code> | Öffnet die Kontexte scripted_server(steps). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 191 | <code>            result = subprocess.run([sys.executable, str(Path(__file__).with_name("pop3_client.py")),</code> | Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 192 | <code>                                     "--port", str(address[1]), "--password", "secret"],</code> | Fortsetzungszeile der Anweisung ab Zeile 191. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 193 | <code>                                    capture_output=True, text=True, timeout=5)</code> | Fortsetzungszeile der Anweisung ab Zeile 191. Wertet subprocess.run([sys.executable, str(Path(__file__).with_name('pop3_client.py')), '--port', str(address[1]), '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 194 | <code>        self.assertEqual(result.returncode, 0, result.stderr)</code> | Testassertion: self.assertEqual(result.returncode, 0, result.stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 195 | <code>        self.assertIn("Maildrop leer", result.stdout)</code> | Testassertion: self.assertIn('Maildrop leer', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 196 | <code>        self.assertIn("QUIT bestätigt", result.stdout)</code> | Testassertion: self.assertIn('QUIT bestätigt', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 197 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 198 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 199 | <code>if __name__ == "__main__":</code> | Startet main/unittest nur bei direktem Skriptaufruf, nicht beim Import durch GUI oder Tests. |
| 200 | <code>    unittest.main(verbosity=2)</code> | Führt den Aufruf/Ausdruck unittest.main(verbosity=2) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |

### `ue3.3/pop3_server.py`

Quellstand SHA-256: `9ee43eadcab08b4bec575b8428b091dc9999a5853c48b8d9154ae351a8083e96`.

#### Funktionen und Methoden

- **`load_database` (Zeilen 19–27):** Originaldatei relativ zum Skript laden, ohne sie zu ändern/kopieren.
- **`canonical_message` (Zeilen 30–34):** Mail in Bytes mit CRLF und genau einem hinzugefügten End-CRLF umwandeln.
- **`message_uid` (Zeilen 37–40):** Stabile, druckbare UID unabhängig von der Sitzungs-Nachrichtennummer.
- **`__init__` (Zeilen 50–57):** Initialisiert den Lebenszyklus: beim Client Verbindung/Begrüßung, beim Server Datenbank, Verwaltungsstrukturen und Listener.
- **`maildrop_lock` (Zeilen 59–62):** Lock-Erzeugung ist selbst gegen gleichzeitige Logins geschützt.
- **`server_close` (Zeilen 64–74):** Offene Sitzungen abbrechen (Rollback), dann auf Worker-Ende warten.
- **`handle` (Zeilen 82–121):** Definiert die nachfolgend im Code erklärte Funktion.
- **`reply` (Zeilen 123–126):** Genau eine Statuszeile senden.
- **`multiline` (Zeilen 128–133):** Status, dot-gestuffte Datenzeilen und Punkt-Endmarke senden.
- **`active_messages` (Zeilen 135–138):** Nummern bleiben während der Sitzung trotz DELE unverändert.
- **`message` (Zeilen 140–147):** Nur positive dezimale Nummern nicht gelöschter Nachrichten zulassen.
- **`login` (Zeilen 149–167):** Authentifizieren, exklusiven Lock holen und konsistenten Snapshot bilden.
- **`dispatch` (Zeilen 169–233):** Befehl ausführen; True bedeutet Sitzungsende, False Weiterarbeiten.
- **`create_server` (Zeilen 236–238):** GUI-API: gebundenen Server erzeugen; port=0 wählt einen freien Testport.
- **`main` (Zeilen 241–262):** CLI: bewusst nur lokale Testkonten über unverschlüsseltes POP3 verwenden.

#### Jede physische Codezeile

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)</code> | Kommentar/KI-Nachweis: KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). Kein ausführbarer Python-Befehl. |
| 2 | <code># Datum: 2026-10-19</code> | Kommentar/KI-Nachweis: Datum: 2026-10-19. Kein ausführbarer Python-Befehl. |
| 3 | <code># Anfrage: Ü3.3 als Socket-POP3-Threadserver mit Originaldatenbank, Zuständen, Maildrop-Sperren und GUI-API implementieren und testen.</code> | Kommentar/KI-Nachweis: Anfrage: Ü3.3 als Socket-POP3-Threadserver mit Originaldatenbank, Zuständen, Maildrop-Sperren und GUI-API implementieren und testen.. Kein ausführbarer Python-Befehl. |
| 4 | <code>"""Lokaler, unverschlüsselter POP3-Lernserver; keine produktiven Zugangsdaten."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 5 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 6 | <code>import argparse</code> | Standard-/Modulimport: liest und prüft Kommandozeilenoptionen. |
| 7 | <code>import hashlib</code> | Standard-/Modulimport: berechnet SHA-256-Kennungen; das verschlüsselt keine Nachricht. |
| 8 | <code>import importlib.util</code> | Standard-/Modulimport: lädt Originaldatenbank oder Nachbarserver anhand eines absoluten Dateipfads. |
| 9 | <code>import ipaddress</code> | Standard-/Modulimport: erkennt numerische Loopback-Adressen für die lokale Voreinstellung. |
| 10 | <code>from pathlib import Path</code> | Standard-/Modulimport: konstruiert Dateipfade unabhängig vom aktuellen Arbeitsverzeichnis. |
| 11 | <code>import socket</code> | Standard-/Modulimport: stellt TCP-Verbindungen, Socketoptionen und Shutdown bereit. |
| 12 | <code>import socketserver</code> | Standard-/Modulimport: übernimmt Accept-Schleife, Stream-Handler und ThreadingMixIn. |
| 13 | <code>import threading</code> | Standard-/Modulimport: stellt Threads, Locks, Barrier und Event zur Synchronisation bereit. |
| 14 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 15 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 16 | <code>CRLF = b"\r\n"</code> | Setzt die verbindlichen zwei Zeilenabschlussbytes des POP3-Protokolls. Rechte Seite: b'\r\n'. |
| 17 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 18 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 19 | <code>def load_database():</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Originaldatei relativ zum Skript laden, ohne sie zu ändern/kopieren. |
| 20 | <code>    """Originaldatei relativ zum Skript laden, ohne sie zu ändern/kopieren."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 21 | <code>    path = Path(__file__).resolve().parents[1] / "Angabe" / "SampleDataBase.py"</code> | Wertet Path(__file__).resolve().parents[1] / 'Angabe' / 'SampleDataBase.py' aus und speichert das Ergebnis in path; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 22 | <code>    spec = importlib.util.spec_from_file_location("rn_sample_database", path)</code> | Wertet importlib.util.spec_from_file_location('rn_sample_database', path) aus und speichert das Ergebnis in spec; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 23 | <code>    if spec is None or spec.loader is None:</code> | Prüft die Bedingung spec is None or spec.loader is None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 24 | <code>        raise ImportError(f"Originaldatenbank nicht ladbar: {path}")</code> | Bricht diesen Pfad mit ImportError(f'Originaldatenbank nicht ladbar: {path}') ab; Aufrufer/Test muss den Fehler behandeln. |
| 25 | <code>    module = importlib.util.module_from_spec(spec)</code> | Wertet importlib.util.module_from_spec(spec) aus und speichert das Ergebnis in module; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 26 | <code>    spec.loader.exec_module(module)</code> | Führt den Aufruf/Ausdruck spec.loader.exec_module(module) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 27 | <code>    return module.SampleDataBase()</code> | Beendet diesen Funktionsaufruf und liefert module.SampleDataBase() an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 28 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 29 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 30 | <code>def canonical_message(raw):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Mail in Bytes mit CRLF und genau einem hinzugefügten End-CRLF umwandeln. |
| 31 | <code>    """Mail in Bytes mit CRLF und genau einem hinzugefügten End-CRLF umwandeln."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 32 | <code>    data = raw.encode("utf-8") if isinstance(raw, str) else bytes(raw)</code> | Wertet raw.encode('utf-8') if isinstance(raw, str) else bytes(raw) aus und speichert das Ergebnis in data; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 33 | <code>    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", CRLF)</code> | Wertet data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', CRLF) aus und speichert das Ergebnis in data; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 34 | <code>    return data if data.endswith(CRLF) else data + CRLF</code> | Beendet diesen Funktionsaufruf und liefert data if data.endswith(CRLF) else data + CRLF an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 35 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 36 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 37 | <code>def message_uid(user, record):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Stabile, druckbare UID unabhängig von der Sitzungs-Nachrichtennummer. |
| 38 | <code>    """Stabile, druckbare UID unabhängig von der Sitzungs-Nachrichtennummer."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 39 | <code>    identity = f"{user}\0{record['id']}\0".encode("utf-8")</code> | Wertet f"{user}\x00{record['id']}\x00".encode('utf-8') aus und speichert das Ergebnis in identity; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 40 | <code>    return hashlib.sha256(identity + canonical_message(record["raw"])).hexdigest()</code> | Beendet diesen Funktionsaufruf und liefert hashlib.sha256(identity + canonical_message(record['raw'])).hexdigest() an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 41 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 42 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 43 | <code>class POP3Server(socketserver.ThreadingMixIn, socketserver.TCPServer):</code> | Definiert die Klasse und ihre Basisklassen. Ein Worker pro TCP-Verbindung; ein exklusiver Maildrop-Lock pro Benutzer. |
| 44 | <code>    """Ein Worker pro TCP-Verbindung; ein exklusiver Maildrop-Lock pro Benutzer."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 45 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 46 | <code>    allow_reuse_address = True</code> | Wertet True aus und speichert das Ergebnis in allow_reuse_address; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 47 | <code>    daemon_threads = False</code> | Wertet False aus und speichert das Ergebnis in daemon_threads; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 48 | <code>    block_on_close = True</code> | Wertet True aus und speichert das Ergebnis in block_on_close; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 49 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 50 | <code>    def __init__(self, address, database=None, client_timeout: float = 600):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Initialisiert den Lebenszyklus: beim Client Verbindung/Begrüßung, beim Server Datenbank, Verwaltungsstrukturen und Listener. |
| 51 | <code>        self.database = load_database() if database is None else database</code> | Setzt die injizierte oder frisch geladene Originaldatenbank. Rechte Seite: load_database() if database is None else database. |
| 52 | <code>        self.client_timeout = client_timeout</code> | Setzt die maximale Wartezeit für blockierende Client-Socketoperationen. Rechte Seite: client_timeout. |
| 53 | <code>        self._guard = threading.Lock()</code> | Setzt den kurzen Verwaltungslock für gemeinsam genutzte Strukturen. Rechte Seite: threading.Lock(). |
| 54 | <code>        self._maildrop_locks = {}</code> | Setzt das Benutzer-zu-Lock-Verzeichnis für exklusive Postfächer. Rechte Seite: {}. |
| 55 | <code>        self._connections = set()</code> | Setzt die Menge aktiver Sockets, damit Serverstopp sie aufwecken kann. Rechte Seite: set(). |
| 56 | <code>        self._closing = False</code> | Setzt das Schließflag, das Rennen mit gerade gestarteten Workern abfängt. Rechte Seite: False. |
| 57 | <code>        super().__init__(address, POP3Handler)</code> | Führt den Aufruf/Ausdruck super().__init__(address, POP3Handler) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 58 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 59 | <code>    def maildrop_lock(self, user):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Lock-Erzeugung ist selbst gegen gleichzeitige Logins geschützt. |
| 60 | <code>        """Lock-Erzeugung ist selbst gegen gleichzeitige Logins geschützt."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 61 | <code>        with self._guard:</code> | Betritt einen kurz gesperrten Verwaltungsbereich; der Kontextmanager gibt den Lock auch bei Ausnahmen frei. |
| 62 | <code>            return self._maildrop_locks.setdefault(user, threading.Lock())</code> | Beendet diesen Funktionsaufruf und liefert self._maildrop_locks.setdefault(user, threading.Lock()) an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 63 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 64 | <code>    def server_close(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Offene Sitzungen abbrechen (Rollback), dann auf Worker-Ende warten. |
| 65 | <code>        """Offene Sitzungen abbrechen (Rollback), dann auf Worker-Ende warten."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 66 | <code>        with self._guard:</code> | Betritt einen kurz gesperrten Verwaltungsbereich; der Kontextmanager gibt den Lock auch bei Ausnahmen frei. |
| 67 | <code>            self._closing = True</code> | Setzt das Schließflag, das Rennen mit gerade gestarteten Workern abfängt. Rechte Seite: True. |
| 68 | <code>            connections = list(self._connections)</code> | Wertet list(self._connections) aus und speichert das Ergebnis in connections; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 69 | <code>        for connection in connections:</code> | Durchläuft connections; pro Element wird connection gesetzt und der eingerückte Körper ausgeführt. |
| 70 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 71 | <code>                connection.shutdown(socket.SHUT_RDWR)</code> | Beendet die angegebene Socket-/Accept-Aktivität und weckt blockierendes Warten; bei BaseServer erfolgt der Aufruf aus einem anderen Thread. connection.shutdown(socket.SHUT_RDWR). |
| 72 | <code>            except OSError:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 73 | <code>                pass</code> | Tut bewusst nichts: entweder markiert die leere Fehlerklasse einen eigenen Typ oder der dokumentierte Transportfehler wird beim Aufräumen toleriert. |
| 74 | <code>        super().server_close()</code> | Führt den Aufruf/Ausdruck super().server_close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 75 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 76 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 77 | <code>class POP3Handler(socketserver.StreamRequestHandler):</code> | Definiert die Klasse und ihre Basisklassen. Zustandsautomat: AUTHORIZATION -&gt; TRANSACTION -&gt; UPDATE nur durch QUIT. |
| 78 | <code>    """Zustandsautomat: AUTHORIZATION -&gt; TRANSACTION -&gt; UPDATE nur durch QUIT."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 79 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 80 | <code>    server: POP3Server</code> | Typannotation für server; dokumentiert die Spezialisierung, erzeugt keinen neuen Server. |
| 81 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 82 | <code>    def handle(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Definiert die nachfolgend im Code erklärte Funktion. |
| 83 | <code>        self.request.settimeout(self.server.client_timeout)</code> | Führt den Aufruf/Ausdruck self.request.settimeout(self.server.client_timeout) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 84 | <code>        self.user = None</code> | Setzt den authentifizierten Benutzer; None bedeutet AUTHORIZATION. Rechte Seite: None. |
| 85 | <code>        self.candidate = None</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 86 | <code>        self.lock = None</code> | Setzt den exklusiven Maildrop-Lock dieser Sitzung oder None. Rechte Seite: None. |
| 87 | <code>        self.messages = []</code> | Setzt den sitzungslokalen Snapshot; seine Reihenfolge definiert die POP3-Nummern. Rechte Seite: []. |
| 88 | <code>        self.deleted = set()</code> | Setzt die sitzungslokalen Löschmarkierungen, noch keine Datenbankänderung. Rechte Seite: set(). |
| 89 | <code>        with self.server._guard:</code> | Betritt einen kurz gesperrten Verwaltungsbereich; der Kontextmanager gibt den Lock auch bei Ausnahmen frei. |
| 90 | <code>            if self.server._closing:</code> | Prüft die Bedingung self.server._closing. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 91 | <code>                return</code> | Beendet diesen Funktionsaufruf und liefert keinen zusätzlichen Wert an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 92 | <code>            self.server._connections.add(self.request)</code> | Führt den Aufruf/Ausdruck self.server._connections.add(self.request) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 93 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 94 | <code>            self.reply(True, "RN POP3 ready (local plaintext lab)")</code> | Führt den Aufruf/Ausdruck self.reply(True, 'RN POP3 ready (local plaintext lab)') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 95 | <code>            while True:</code> | Wiederholt den eingerückten Empfangs-/Verarbeitungsblock solange True gilt; break oder return beendet die Schleife. |
| 96 | <code>                line = self.rfile.readline(256)</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: self.rfile.readline(256). |
| 97 | <code>                if not line:</code> | Prüft die Bedingung not line. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 98 | <code>                    break</code> | Verlässt nur die nächste umgebende Schleife, etwa bei EOF, QUIT oder ungültigem Framing; finally-Aufräumen bleibt wirksam. |
| 99 | <code>                if len(line) &gt; 255 or not line.endswith(CRLF):</code> | Prüft die Bedingung len(line) &gt; 255 or not line.endswith(CRLF). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 100 | <code>                    self.reply(False, "command too long or missing CRLF; closing")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'command too long or missing CRLF; closing') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 101 | <code>                    break</code> | Verlässt nur die nächste umgebende Schleife, etwa bei EOF, QUIT oder ungültigem Framing; finally-Aufräumen bleibt wirksam. |
| 102 | <code>                command = line[:-2]</code> | Wertet line[:-2] aus und speichert das Ergebnis in command; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 103 | <code>                if not command or any(octet &lt; 32 or octet &gt; 126 for octet in command):</code> | Prüft die Bedingung not command or any((octet &lt; 32 or octet &gt; 126 for octet in command)). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 104 | <code>                    self.candidate = None</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 105 | <code>                    self.reply(False, "invalid command encoding")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'invalid command encoding') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 106 | <code>                    continue</code> | Springt zum nächsten Schleifendurchlauf; die ungültige aktuelle Eingabe wird nicht als regulärer Befehl ausgeführt. |
| 107 | <code>                name, separator, argument = command.decode("ascii").partition(" ")</code> | Wertet command.decode('ascii').partition(' ') aus und speichert das Ergebnis in (name, separator, argument); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 108 | <code>                name = name.upper()</code> | Setzt das normalisierte POP3-Schlüsselwort für die Befehlsauswahl. Rechte Seite: name.upper(). |
| 109 | <code>                args = argument.split(" ") if separator else []</code> | Setzt die mit einzelnen Leerzeichen getrennten Argumente für Syntaxprüfung. Rechte Seite: argument.split(' ') if separator else []. |
| 110 | <code>                try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 111 | <code>                    if self.dispatch(name, argument, args):</code> | Prüft die Bedingung self.dispatch(name, argument, args). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 112 | <code>                        break</code> | Verlässt nur die nächste umgebende Schleife, etwa bei EOF, QUIT oder ungültigem Framing; finally-Aufräumen bleibt wirksam. |
| 113 | <code>                except ValueError:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 114 | <code>                    self.reply(False, "invalid arguments or no such message")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'invalid arguments or no such message') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 115 | <code>        except (OSError, TimeoutError):</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 116 | <code>            pass  # Kein QUIT: insbesondere keine Löschungen übernehmen.</code> | Tut bewusst nichts: entweder markiert die leere Fehlerklasse einen eigenen Typ oder der dokumentierte Transportfehler wird beim Aufräumen toleriert. |
| 117 | <code>        finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 118 | <code>            if self.lock is not None:</code> | Prüft die Bedingung self.lock is not None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 119 | <code>                self.lock.release()</code> | Gibt die zuvor erworbene Sperre frei, damit eine andere Sitzung das Postfach öffnen kann. self.lock.release(). |
| 120 | <code>            with self.server._guard:</code> | Betritt einen kurz gesperrten Verwaltungsbereich; der Kontextmanager gibt den Lock auch bei Ausnahmen frei. |
| 121 | <code>                self.server._connections.discard(self.request)</code> | Führt den Aufruf/Ausdruck self.server._connections.discard(self.request) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 122 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 123 | <code>    def reply(self, success, text):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Genau eine Statuszeile senden. |
| 124 | <code>        """Genau eine Statuszeile senden."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 125 | <code>        prefix = b"+OK " if success else b"-ERR "</code> | Wertet b'+OK ' if success else b'-ERR ' aus und speichert das Ergebnis in prefix; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 126 | <code>        self.wfile.write(prefix + text.encode("ascii") + CRLF)</code> | Schreibt die angegebenen Antwortbytes auf den Clientstream. CRLF und eventuell der zusätzliche Stuffing-Punkt sind Teil des Drahtformats. self.wfile.write(prefix + text.encode('ascii') + CRLF). |
| 127 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 128 | <code>    def multiline(self, text, lines):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Status, dot-gestuffte Datenzeilen und Punkt-Endmarke senden. |
| 129 | <code>        """Status, dot-gestuffte Datenzeilen und Punkt-Endmarke senden."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 130 | <code>        self.reply(True, text)</code> | Führt den Aufruf/Ausdruck self.reply(True, text) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 131 | <code>        for line in lines:</code> | Durchläuft lines; pro Element wird line gesetzt und der eingerückte Körper ausgeführt. |
| 132 | <code>            self.wfile.write((b"." if line.startswith(b".") else b"") + line + CRLF)</code> | Schreibt die angegebenen Antwortbytes auf den Clientstream. CRLF und eventuell der zusätzliche Stuffing-Punkt sind Teil des Drahtformats. self.wfile.write((b'.' if line.startswith(b'.') else b'') + line + CRLF). |
| 133 | <code>        self.wfile.write(b".\r\n")</code> | Schreibt die angegebenen Antwortbytes auf den Clientstream. CRLF und eventuell der zusätzliche Stuffing-Punkt sind Teil des Drahtformats. self.wfile.write(b'.\r\n'). |
| 134 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 135 | <code>    def active_messages(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Nummern bleiben während der Sitzung trotz DELE unverändert. |
| 136 | <code>        """Nummern bleiben während der Sitzung trotz DELE unverändert."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 137 | <code>        return [(number, message) for number, message in enumerate(self.messages, 1)</code> | Beendet diesen Funktionsaufruf und liefert [(number, message) for number, message in enumerate(self.messages, 1) if number not in self.deleted] an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 138 | <code>                if number not in self.deleted]</code> | Fortsetzungszeile der Anweisung ab Zeile 137. Beendet diesen Funktionsaufruf und liefert [(number, message) for number, message in enumerate(self.messages, 1) if number not in self.deleted] an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 139 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 140 | <code>    def message(self, token):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Nur positive dezimale Nummern nicht gelöschter Nachrichten zulassen. |
| 141 | <code>        """Nur positive dezimale Nummern nicht gelöschter Nachrichten zulassen."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 142 | <code>        if not token.isascii() or not token.isdecimal():</code> | Prüft die Bedingung not token.isascii() or not token.isdecimal(). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 143 | <code>            raise ValueError("not a message number")</code> | Bricht diesen Pfad mit ValueError('not a message number') ab; Aufrufer/Test muss den Fehler behandeln. |
| 144 | <code>        number = int(token)</code> | Setzt die positive sitzungsbezogene Nachrichtennummer, nicht die Datenbank-ID. Rechte Seite: int(token). |
| 145 | <code>        if not 1 &lt;= number &lt;= len(self.messages) or number in self.deleted:</code> | Prüft die Bedingung not 1 &lt;= number &lt;= len(self.messages) or number in self.deleted. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 146 | <code>            raise ValueError("no such message")</code> | Bricht diesen Pfad mit ValueError('no such message') ab; Aufrufer/Test muss den Fehler behandeln. |
| 147 | <code>        return number, self.messages[number - 1]</code> | Beendet diesen Funktionsaufruf und liefert (number, self.messages[number - 1]) an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 148 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 149 | <code>    def login(self, password):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Authentifizieren, exklusiven Lock holen und konsistenten Snapshot bilden. |
| 150 | <code>        """Authentifizieren, exklusiven Lock holen und konsistenten Snapshot bilden."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 151 | <code>        if self.candidate is None:</code> | Prüft die Bedingung self.candidate is None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 152 | <code>            self.reply(False, "send USER first")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'send USER first') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 153 | <code>            return</code> | Beendet diesen Funktionsaufruf und liefert keinen zusätzlichen Wert an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 154 | <code>        user = self.candidate</code> | Wertet self.candidate aus und speichert das Ergebnis in user; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 155 | <code>        self.candidate = None</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 156 | <code>        if not self.server.database.authenticate(user, password):</code> | Prüft die Bedingung not self.server.database.authenticate(user, password). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 157 | <code>            self.reply(False, "authentication failed")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'authentication failed') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 158 | <code>            return</code> | Beendet diesen Funktionsaufruf und liefert keinen zusätzlichen Wert an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 159 | <code>        lock = self.server.maildrop_lock(user)</code> | Wertet self.server.maildrop_lock(user) aus und speichert das Ergebnis in lock; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 160 | <code>        if not lock.acquire(blocking=False):</code> | Prüft die Bedingung not lock.acquire(blocking=False). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 161 | <code>            self.reply(False, "[IN-USE] maildrop locked")</code> | Führt den Aufruf/Ausdruck self.reply(False, '[IN-USE] maildrop locked') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 162 | <code>            return</code> | Beendet diesen Funktionsaufruf und liefert keinen zusätzlichen Wert an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 163 | <code>        self.lock = lock</code> | Setzt den exklusiven Maildrop-Lock dieser Sitzung oder None. Rechte Seite: lock. |
| 164 | <code>        self.messages = [dict(record, raw=canonical_message(record["raw"]))</code> | Setzt den sitzungslokalen Snapshot; seine Reihenfolge definiert die POP3-Nummern. Rechte Seite: [dict(record, raw=canonical_message(record['raw'])) for record in self.server.database.get_messages(user)]. |
| 165 | <code>                         for record in self.server.database.get_messages(user)]</code> | Fortsetzungszeile der Anweisung ab Zeile 164. Setzt den sitzungslokalen Snapshot; seine Reihenfolge definiert die POP3-Nummern. Rechte Seite: [dict(record, raw=canonical_message(record['raw'])) for record in self.server.database.get_messages(user)]. |
| 166 | <code>        self.user = user</code> | Setzt den authentifizierten Benutzer; None bedeutet AUTHORIZATION. Rechte Seite: user. |
| 167 | <code>        self.reply(True, "maildrop locked and ready")</code> | Führt den Aufruf/Ausdruck self.reply(True, 'maildrop locked and ready') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 168 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 169 | <code>    def dispatch(self, name, argument, args):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Befehl ausführen; True bedeutet Sitzungsende, False Weiterarbeiten. |
| 170 | <code>        """Befehl ausführen; True bedeutet Sitzungsende, False Weiterarbeiten."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 171 | <code>        if name not in ("USER", "PASS"):</code> | Prüft die Bedingung name not in ('USER', 'PASS'). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 172 | <code>            self.candidate = None  # PASS darf nur unmittelbar auf erfolgreiches USER folgen.</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 173 | <code>        if name == "CAPA" and not args:</code> | Prüft die Bedingung name == 'CAPA' and (not args). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 174 | <code>            self.multiline("capabilities", [b"USER", b"TOP", b"UIDL", b"RESP-CODES",</code> | Führt den Aufruf/Ausdruck self.multiline('capabilities', [b'USER', b'TOP', b'UIDL', b'RESP-CODES', b'EXPIRE NEVER', b'IMPLEMENTATION RN-POP3']) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 175 | <code>                                           b"EXPIRE NEVER", b"IMPLEMENTATION RN-POP3"])</code> | Fortsetzungszeile der Anweisung ab Zeile 174. Führt den Aufruf/Ausdruck self.multiline('capabilities', [b'USER', b'TOP', b'UIDL', b'RESP-CODES', b'EXPIRE NEVER', b'IMPLEMENTATION RN-POP3']) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 176 | <code>        elif name == "QUIT" and not args:</code> | Prüft die Bedingung name == 'QUIT' and (not args). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 177 | <code>            if self.user is not None:</code> | Prüft die Bedingung self.user is not None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 178 | <code>                # UPDATE: Original-API liefert die lebende, veränderbare Nachrichtenliste.</code> | Kommentar/KI-Nachweis: UPDATE: Original-API liefert die lebende, veränderbare Nachrichtenliste.. Kein ausführbarer Python-Befehl. |
| 179 | <code>                records = self.server.database.get_messages(self.user)</code> | Wertet self.server.database.get_messages(self.user) aus und speichert das Ergebnis in records; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 180 | <code>                removed = {self.messages[n - 1]["id"] for n in self.deleted}</code> | Setzt die Original-IDs der nur in dieser Sitzung markierten Nachrichten. Rechte Seite: {self.messages[n - 1]['id'] for n in self.deleted}. |
| 181 | <code>                records[:] = [record for record in records if record["id"] not in removed]</code> | Setzt die gesamte lebende Originalliste; Slice-Zuweisung erhält deren Identität. Rechte Seite: [record for record in records if record['id'] not in removed]. |
| 182 | <code>            self.reply(True, "goodbye")</code> | Führt den Aufruf/Ausdruck self.reply(True, 'goodbye') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 183 | <code>            return True</code> | Beendet diesen Funktionsaufruf und liefert True an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 184 | <code>        elif self.user is None:</code> | Prüft die Bedingung self.user is None. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 185 | <code>            if name == "USER":</code> | Prüft die Bedingung name == 'USER'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 186 | <code>                self.candidate = None</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 187 | <code>                if len(args) != 1 or not args[0]:</code> | Prüft die Bedingung len(args) != 1 or not args[0]. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 188 | <code>                    raise ValueError("USER requires one name")</code> | Bricht diesen Pfad mit ValueError('USER requires one name') ab; Aufrufer/Test muss den Fehler behandeln. |
| 189 | <code>                self.candidate = args[0]</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: args[0]. |
| 190 | <code>                self.reply(True, "send PASS")</code> | Führt den Aufruf/Ausdruck self.reply(True, 'send PASS') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 191 | <code>            elif name == "PASS":</code> | Prüft die Bedingung name == 'PASS'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 192 | <code>                if not argument:</code> | Prüft die Bedingung not argument. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 193 | <code>                    self.candidate = None</code> | Setzt den noch nicht authentifizierten USER-Kandidaten. Rechte Seite: None. |
| 194 | <code>                    raise ValueError("PASS requires a password")</code> | Bricht diesen Pfad mit ValueError('PASS requires a password') ab; Aufrufer/Test muss den Fehler behandeln. |
| 195 | <code>                self.login(argument)  # Ein Passwort darf Leerzeichen enthalten (RFC 1939).</code> | Führt den Aufruf/Ausdruck self.login(argument) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 196 | <code>            else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 197 | <code>                self.reply(False, "authenticate with USER and PASS first")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'authenticate with USER and PASS first') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 198 | <code>        elif name in ("STAT", "NOOP", "RSET") and not args:</code> | Prüft die Bedingung name in ('STAT', 'NOOP', 'RSET') and (not args). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 199 | <code>            if name == "RSET":</code> | Prüft die Bedingung name == 'RSET'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 200 | <code>                self.deleted.clear()</code> | Entfernt nur sitzungslokale Löschmarkierungen: RSET macht DELE rückgängig, ohne Originalmails zu ändern. |
| 201 | <code>            active = self.active_messages()</code> | Wertet self.active_messages() aus und speichert das Ergebnis in active; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 202 | <code>            self.reply(True, f"{len(active)} {sum(len(m['raw']) for _, m in active)}")</code> | Führt den Aufruf/Ausdruck self.reply(True, f"{len(active)} {sum((len(m['raw']) for _, m in active))}") aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 203 | <code>        elif name in ("LIST", "UIDL") and len(args) &lt;= 1:</code> | Prüft die Bedingung name in ('LIST', 'UIDL') and len(args) &lt;= 1. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 204 | <code>            if args:</code> | Prüft die Bedingung args. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 205 | <code>                number, record = self.message(args[0])</code> | Wertet self.message(args[0]) aus und speichert das Ergebnis in (number, record); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 206 | <code>                value = len(record["raw"]) if name == "LIST" else message_uid(self.user, record)</code> | Wertet len(record['raw']) if name == 'LIST' else message_uid(self.user, record) aus und speichert das Ergebnis in value; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 207 | <code>                self.reply(True, f"{number} {value}")</code> | Führt den Aufruf/Ausdruck self.reply(True, f'{number} {value}') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 208 | <code>            else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 209 | <code>                lines = []</code> | Setzt die gesammelten/auszugebenden Datenzeilen, getrennt von Status und Endmarke. Rechte Seite: []. |
| 210 | <code>                for number, record in self.active_messages():</code> | Durchläuft self.active_messages(); pro Element wird (number, record) gesetzt und der eingerückte Körper ausgeführt. |
| 211 | <code>                    value = len(record["raw"]) if name == "LIST" else message_uid(self.user, record)</code> | Wertet len(record['raw']) if name == 'LIST' else message_uid(self.user, record) aus und speichert das Ergebnis in value; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 212 | <code>                    lines.append(f"{number} {value}".encode("ascii"))</code> | Führt den Aufruf/Ausdruck lines.append(f'{number} {value}'.encode('ascii')) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 213 | <code>                self.multiline("listing follows", lines)</code> | Führt den Aufruf/Ausdruck self.multiline('listing follows', lines) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 214 | <code>        elif name in ("RETR", "DELE") and len(args) == 1:</code> | Prüft die Bedingung name in ('RETR', 'DELE') and len(args) == 1. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 215 | <code>            number, record = self.message(args[0])</code> | Wertet self.message(args[0]) aus und speichert das Ergebnis in (number, record); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 216 | <code>            if name == "DELE":</code> | Prüft die Bedingung name == 'DELE'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 217 | <code>                self.deleted.add(number)</code> | Führt den Aufruf/Ausdruck self.deleted.add(number) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 218 | <code>                self.reply(True, "message marked")</code> | Führt den Aufruf/Ausdruck self.reply(True, 'message marked') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 219 | <code>            else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 220 | <code>                self.multiline(f"{len(record['raw'])} octets", record["raw"][:-2].split(CRLF))</code> | Führt den Aufruf/Ausdruck self.multiline(f"{len(record['raw'])} octets", record['raw'][:-2].split(CRLF)) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 221 | <code>        elif name == "TOP" and len(args) == 2:</code> | Prüft die Bedingung name == 'TOP' and len(args) == 2. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 222 | <code>            _, record = self.message(args[0])</code> | Wertet self.message(args[0]) aus und speichert das Ergebnis in (_, record); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 223 | <code>            if not args[1].isascii() or not args[1].isdecimal():</code> | Prüft die Bedingung not args[1].isascii() or not args[1].isdecimal(). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 224 | <code>                raise ValueError("invalid body line count")</code> | Bricht diesen Pfad mit ValueError('invalid body line count') ab; Aufrufer/Test muss den Fehler behandeln. |
| 225 | <code>            count = int(args[1])</code> | Wertet int(args[1]) aus und speichert das Ergebnis in count; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 226 | <code>            header, separator, body = record["raw"].partition(CRLF + CRLF)</code> | Wertet record['raw'].partition(CRLF + CRLF) aus und speichert das Ergebnis in (header, separator, body); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 227 | <code>            if not separator:</code> | Prüft die Bedingung not separator. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 228 | <code>                header, body = record["raw"][:-2], b""</code> | Wertet (record['raw'][:-2], b'') aus und speichert das Ergebnis in (header, body); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 229 | <code>            body_lines = body[:-2].split(CRLF) if body.endswith(CRLF) else []</code> | Wertet body[:-2].split(CRLF) if body.endswith(CRLF) else [] aus und speichert das Ergebnis in body_lines; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 230 | <code>            self.multiline("top follows", header.split(CRLF) + [b""] + body_lines[:count])</code> | Führt den Aufruf/Ausdruck self.multiline('top follows', header.split(CRLF) + [b''] + body_lines[:count]) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 231 | <code>        else:</code> | Alternativer Zweig: läuft, wenn die vorherige if/elif-Bedingung falsch war. |
| 232 | <code>            self.reply(False, "unknown command, wrong state or invalid arguments")</code> | Führt den Aufruf/Ausdruck self.reply(False, 'unknown command, wrong state or invalid arguments') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 233 | <code>        return False</code> | Beendet diesen Funktionsaufruf und liefert False an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 234 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 235 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 236 | <code>def create_server(host="127.0.0.1", port=11110, database=None, client_timeout: float = 600):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. GUI-API: gebundenen Server erzeugen; port=0 wählt einen freien Testport. |
| 237 | <code>    """GUI-API: gebundenen Server erzeugen; port=0 wählt einen freien Testport."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 238 | <code>    return POP3Server((host, port), database, client_timeout)</code> | Beendet diesen Funktionsaufruf und liefert POP3Server((host, port), database, client_timeout) an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 239 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 240 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 241 | <code>def main(argv=None):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. CLI: bewusst nur lokale Testkonten über unverschlüsseltes POP3 verwenden. |
| 242 | <code>    """CLI: bewusst nur lokale Testkonten über unverschlüsseltes POP3 verwenden."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 243 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Wertet argparse.ArgumentParser(description=__doc__) aus und speichert das Ergebnis in parser; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 244 | <code>    parser.add_argument("--host", default="127.0.0.1")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--host', default='127.0.0.1'). |
| 245 | <code>    parser.add_argument("--port", type=int, default=11110)</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--port', type=int, default=11110). |
| 246 | <code>    parser.add_argument("--timeout", type=float, default=600)</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--timeout', type=float, default=600). |
| 247 | <code>    parser.add_argument("--allow-remote-plaintext", action="store_true")</code> | Registriert genau diese CLI-Option samt Typ/Default/Hilfe; argparse verarbeitet sie später beim Programmstart. parser.add_argument('--allow-remote-plaintext', action='store_true'). |
| 248 | <code>    args = parser.parse_args(argv)</code> | Setzt die mit einzelnen Leerzeichen getrennten Argumente für Syntaxprüfung. Rechte Seite: parser.parse_args(argv). |
| 249 | <code>    try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 250 | <code>        local = ipaddress.ip_address(args.host).is_loopback</code> | Wertet ipaddress.ip_address(args.host).is_loopback aus und speichert das Ergebnis in local; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 251 | <code>    except ValueError:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 252 | <code>        local = args.host == "localhost"</code> | Wertet args.host == 'localhost' aus und speichert das Ergebnis in local; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 253 | <code>    if not local and not args.allow_remote_plaintext:</code> | Prüft die Bedingung not local and (not args.allow_remote_plaintext). Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 254 | <code>        parser.error("Nicht-Loopback benötigt --allow-remote-plaintext; nur Testdaten!")</code> | Führt den Aufruf/Ausdruck parser.error('Nicht-Loopback benötigt --allow-remote-plaintext; nur Testdaten!') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 255 | <code>    with create_server(args.host, args.port, client_timeout=args.timeout) as server:</code> | Öffnet die Kontexte create_server(args.host, args.port, client_timeout=args.timeout). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 256 | <code>        print(f"POP3 plaintext lab: {server.server_address[0]}:{server.server_address[1]}", flush=True)</code> | Führt den Aufruf/Ausdruck print(f'POP3 plaintext lab: {server.server_address[0]}:{server.server_address[1]}', flush=True) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 257 | <code>        print("Testkonto alice / secret; keine echten Zugangsdaten verwenden.", flush=True)</code> | Führt den Aufruf/Ausdruck print('Testkonto alice / secret; keine echten Zugangsdaten verwenden.', flush=True) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 258 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 259 | <code>            server.serve_forever(poll_interval=0.1)</code> | Führt den Aufruf/Ausdruck server.serve_forever(poll_interval=0.1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 260 | <code>        except KeyboardInterrupt:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 261 | <code>            pass</code> | Tut bewusst nichts: entweder markiert die leere Fehlerklasse einen eigenen Typ oder der dokumentierte Transportfehler wird beim Aufräumen toleriert. |
| 262 | <code>    return 0</code> | Beendet diesen Funktionsaufruf und liefert 0 an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 263 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 264 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 265 | <code>if __name__ == "__main__":</code> | Startet main/unittest nur bei direktem Skriptaufruf, nicht beim Import durch GUI oder Tests. |
| 266 | <code>    raise SystemExit(main())</code> | Bricht diesen Pfad mit SystemExit(main()) ab; Aufrufer/Test muss den Fehler behandeln. |

### `ue3.3/test_pop3_server.py`

Quellstand SHA-256: `3887f98b90b90691814c51fc04e5e9c92c4d0131b5eff5729a725e98e9cca4fc`.

#### Funktionen und Methoden

- **`setUp` (Zeilen 20–32):** Erzeugt für jeden Test eine frische Datenbank/Serverinstanz auf freiem Port und registriert garantiertes Aufräumen.
- **`stop_server` (Zeilen 34–39):** Stoppt Accept-Schleife, aktive Sitzungen und Serverthread und prüft, dass keine Verbindung übrig bleibt.
- **`connect` (Zeilen 41–46):** Verbindet einen unabhängigen poplib-Client, meldet ihn an und registriert dessen Cleanup.
- **`raw` (Zeilen 48–54):** Liefert echten TCP-Socket und Binärreader nach geprüfter Begrüßung für Drahtformat-Tests.
- **`test_original_data_and_readme_password_discrepancy` (Zeilen 56–62):** Verifiziert die Originaldaten und belegt secret statt alice123.
- **`test_poplib_full_session_sizes_capa_uidl_top_noop` (Zeilen 64–81):** Prüft Abruf aller Originalmails und Nebenbefehle unabhängig mit poplib.
- **`test_wire_dot_stuffing_crlf_and_unicode_octets` (Zeilen 83–107):** Vergleicht Nachrichtenbytes und beobachtet tatsächliche doppelte Punkte/CRLF auf dem Rohsocket.
- **`test_dele_rset_update_and_uid_stability_after_renumber` (Zeilen 109–126):** Prüft Markierung, Unsichtbarkeit, RSET, tatsächliches QUIT-UPDATE und stabile UID bei neuer Nummer.
- **`test_disconnect_rolls_back_and_unlocks` (Zeilen 128–138):** Simuliert Client-Absturz ohne QUIT; Mailbestand und freie Sperre müssen erhalten bleiben.
- **`test_concurrent_users_and_same_maildrop_rejected` (Zeilen 140–168):** Synchronisiert Alice/Bob mit Barrier und hält beide offen, während ein weiterer Alice-Login abgewiesen wird.
- **`session` (Zeilen 144–151):** Hält eine echte angemeldete Benutzersitzung bis zur gemeinsamen Freigabe offen und beendet sie danach mit QUIT.
- **`test_authorization_wrong_states_and_syntax` (Zeilen 170–201):** Prüft Authentifizierungsreihenfolge, falsche Zustände und viele fehlerhafte Befehle ohne Bestandsänderung.
- **`test_fragmentation_multiple_commands_and_lowercase` (Zeilen 203–210):** Sendet jeden Befehlsbyte einzeln und liest mehrere korrekte Antworten in Reihenfolge.
- **`test_command_length_limit_and_invalid_framing` (Zeilen 212–228):** Prüft die 255-Byte-Grenze und Verbindungsende nach überlangem Befehl/nacktem LF.
- **`test_empty_mailbox_and_quit_in_authorization` (Zeilen 230–242):** Prüft positive leere Listen und QUIT ohne vorheriges Öffnen eines Maildrops.
- **`test_timeout_rolls_back_and_releases_lock` (Zeilen 244–253):** Wartet auf den echten Server-Timeout statt blind zu schlafen und prüft Rollback/Sperrfreigabe.
- **`test_server_close_aborts_active_session_without_update` (Zeilen 255–262):** Stoppt den Server bei offener DELE-Sitzung; es darf keine Löschung erfolgen.
- **`test_password_with_spaces` (Zeilen 264–268):** Prüft die PASS-Sonderregel: Das gesamte Restargument ist das Passwort.
- **`test_canonicalization_preserves_trailing_blank_lines` (Zeilen 270–274):** Prüft CR/LF-Normalisierung, Erhalt leerer Endzeilen und Unterscheidung verschiedener IDs.
- **`test_real_server_cli_and_client_cli_subprocesses` (Zeilen 276–308):** Startet beide Programme als echte Prozesse, prüft Client-Ausgabe und danach denselben Server mit poplib.

#### Jede physische Codezeile

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription)</code> | Kommentar/KI-Nachweis: KI-Kennzeichnung (RN WS26): erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). Kein ausführbarer Python-Befehl. |
| 2 | <code># Datum: 2026-10-19</code> | Kommentar/KI-Nachweis: Datum: 2026-10-19. Kein ausführbarer Python-Befehl. |
| 3 | <code># Anfrage: Ü3.3 unabhängig mit poplib und Rohsockets auf Zustände, Parallelität, CRLF, Dot-Stuffing und transaktionale Löschungen testen.</code> | Kommentar/KI-Nachweis: Anfrage: Ü3.3 unabhängig mit poplib und Rohsockets auf Zustände, Parallelität, CRLF, Dot-Stuffing und transaktionale Löschungen testen.. Kein ausführbarer Python-Befehl. |
| 4 | <code>"""Echte TCP-Tests; poplib ist nur unabhängiger Testclient, nicht Implementierung."""</code> | Docstring: beschreibt Zweck/Vertrag in Textform; sendet keine Bytes und verändert keine Daten. |
| 5 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 6 | <code>from concurrent.futures import ThreadPoolExecutor</code> | Standard-/Modulimport: führt zwei unabhängige Benutzersitzungen zeitgleich aus. |
| 7 | <code>import poplib</code> | Standard-/Modulimport: ist ausschließlich der unabhängige Standardbibliotheks-Testclient. |
| 8 | <code>from pathlib import Path</code> | Standard-/Modulimport: konstruiert Dateipfade unabhängig vom aktuellen Arbeitsverzeichnis. |
| 9 | <code>import signal</code> | Standard-/Modulimport: liefert SIGINT für geordnetes Beenden wie bei Strg+C. |
| 10 | <code>import socket</code> | Standard-/Modulimport: stellt TCP-Verbindungen, Socketoptionen und Shutdown bereit. |
| 11 | <code>import subprocess</code> | Standard-/Modulimport: startet echte, getrennte Python-Prozesse für CLI-Integration. |
| 12 | <code>import sys</code> | Standard-/Modulimport: liefert stderr und den aktuellen Python-Interpreter für echte CLI-Unterprozesse. |
| 13 | <code>import threading</code> | Standard-/Modulimport: stellt Threads, Locks, Barrier und Event zur Synchronisation bereit. |
| 14 | <code>import unittest</code> | Standard-/Modulimport: führt überprüfbare Tests und Assertions aus. |
| 15 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 16 | <code>from pop3_server import canonical_message, create_server, load_database, message_uid</code> | Standard-/Modulimport: importiert die tatsächlich zu prüfende Serverimplementierung. |
| 17 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 18 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 19 | <code>class ServerTests(unittest.TestCase):</code> | Definiert die Klasse und ihre Basisklassen. Bündelt die zugehörigen Testmethoden; unittest erzeugt für jeden Test einen frischen Ablauf. |
| 20 | <code>    def setUp(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Erzeugt für jeden Test eine frische Datenbank/Serverinstanz auf freiem Port und registriert garantiertes Aufräumen. |
| 21 | <code>        self.db = load_database()</code> | Wertet load_database() aus und speichert das Ergebnis in self.db; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 22 | <code>        # Nur diese frische Instanz ergänzen; Originaldateien bleiben unverändert.</code> | Kommentar/KI-Nachweis: Nur diese frische Instanz ergänzen; Originaldateien bleiben unverändert.. Kein ausführbarer Python-Befehl. |
| 23 | <code>        self.db.users["bob"] = {</code> | Wertet {'password': 'bob-test', 'messages': [{'id': 99, 'raw': 'Subject: Dots\n\n.first\n.\n..third\nGrüße\n'}]} aus und speichert das Ergebnis in self.db.users['bob']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 24 | <code>            "password": "bob-test",</code> | Fortsetzungszeile der Anweisung ab Zeile 23. Wertet {'password': 'bob-test', 'messages': [{'id': 99, 'raw': 'Subject: Dots\n\n.first\n.\n..third\nGrüße\n'}]} aus und speichert das Ergebnis in self.db.users['bob']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 25 | <code>            "messages": [{"id": 99, "raw": "Subject: Dots\n\n.first\n.\n..third\nGrüße\n"}],</code> | Fortsetzungszeile der Anweisung ab Zeile 23. Wertet {'password': 'bob-test', 'messages': [{'id': 99, 'raw': 'Subject: Dots\n\n.first\n.\n..third\nGrüße\n'}]} aus und speichert das Ergebnis in self.db.users['bob']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 26 | <code>        }</code> | Fortsetzungszeile der Anweisung ab Zeile 23. Wertet {'password': 'bob-test', 'messages': [{'id': 99, 'raw': 'Subject: Dots\n\n.first\n.\n..third\nGrüße\n'}]} aus und speichert das Ergebnis in self.db.users['bob']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 27 | <code>        self.db.users["empty"] = {"password": "empty-test", "messages": []}</code> | Wertet {'password': 'empty-test', 'messages': []} aus und speichert das Ergebnis in self.db.users['empty']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 28 | <code>        self.server = create_server(port=0, database=self.db, client_timeout=2)</code> | Wertet create_server(port=0, database=self.db, client_timeout=2) aus und speichert das Ergebnis in self.server; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 29 | <code>        self.thread = threading.Thread(target=self.server.serve_forever,</code> | Wertet threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.01}) aus und speichert das Ergebnis in self.thread; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 30 | <code>                                       kwargs={"poll_interval": 0.01})</code> | Fortsetzungszeile der Anweisung ab Zeile 29. Wertet threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.01}) aus und speichert das Ergebnis in self.thread; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 31 | <code>        self.thread.start()</code> | Führt den Aufruf/Ausdruck self.thread.start() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 32 | <code>        self.addCleanup(self.stop_server)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(self.stop_server). |
| 33 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 34 | <code>    def stop_server(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Stoppt Accept-Schleife, aktive Sitzungen und Serverthread und prüft, dass keine Verbindung übrig bleibt. |
| 35 | <code>        self.server.shutdown()</code> | Beendet die angegebene Socket-/Accept-Aktivität und weckt blockierendes Warten; bei BaseServer erfolgt der Aufruf aus einem anderen Thread. self.server.shutdown(). |
| 36 | <code>        self.server.server_close()</code> | Führt den Aufruf/Ausdruck self.server.server_close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 37 | <code>        self.thread.join(3)</code> | Wartet begrenzt auf den gestarteten Thread; die nachfolgende Prüfung muss ein Hängen sichtbar machen. self.thread.join(3). |
| 38 | <code>        self.assertFalse(self.thread.is_alive())</code> | Testassertion: self.assertFalse(self.thread.is_alive()). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 39 | <code>        self.assertFalse(self.server._connections)</code> | Testassertion: self.assertFalse(self.server._connections). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 40 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 41 | <code>    def connect(self, user="alice", password="secret"):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Verbindet einen unabhängigen poplib-Client, meldet ihn an und registriert dessen Cleanup. |
| 42 | <code>        client = poplib.POP3(*self.server.server_address, timeout=2)</code> | Wertet poplib.POP3(*self.server.server_address, timeout=2) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 43 | <code>        self.addCleanup(client.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(client.close). |
| 44 | <code>        client.user(user)</code> | Führt den Aufruf/Ausdruck client.user(user) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 45 | <code>        client.pass_(password)</code> | Führt den Aufruf/Ausdruck client.pass_(password) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 46 | <code>        return client</code> | Beendet diesen Funktionsaufruf und liefert client an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 47 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 48 | <code>    def raw(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Liefert echten TCP-Socket und Binärreader nach geprüfter Begrüßung für Drahtformat-Tests. |
| 49 | <code>        connection = socket.create_connection(self.server.server_address, timeout=2)</code> | Wertet socket.create_connection(self.server.server_address, timeout=2) aus und speichert das Ergebnis in connection; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 50 | <code>        reader = connection.makefile("rb")</code> | Wertet connection.makefile('rb') aus und speichert das Ergebnis in reader; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 51 | <code>        self.addCleanup(connection.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(connection.close). |
| 52 | <code>        self.addCleanup(reader.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(reader.close). |
| 53 | <code>        self.assertTrue(reader.readline().startswith(b"+OK "))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK ')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 54 | <code>        return connection, reader</code> | Beendet diesen Funktionsaufruf und liefert (connection, reader) an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 55 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 56 | <code>    def test_original_data_and_readme_password_discrepancy(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Verifiziert die Originaldaten und belegt secret statt alice123. |
| 57 | <code>        self.assertTrue(self.db.authenticate("alice", "secret"))</code> | Testassertion: self.assertTrue(self.db.authenticate('alice', 'secret')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 58 | <code>        self.assertFalse(self.db.authenticate("alice", "alice123"))</code> | Testassertion: self.assertFalse(self.db.authenticate('alice', 'alice123')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 59 | <code>        self.assertEqual(len(load_database().get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(load_database().get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 60 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 61 | <code>        self.assertEqual(client.stat()[0], 4)</code> | Testassertion: self.assertEqual(client.stat()[0], 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 62 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 63 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 64 | <code>    def test_poplib_full_session_sizes_capa_uidl_top_noop(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft Abruf aller Originalmails und Nebenbefehle unabhängig mit poplib. |
| 65 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 66 | <code>        expected = [canonical_message(record["raw"]) for record in self.db.get_messages("alice")]</code> | Wertet [canonical_message(record['raw']) for record in self.db.get_messages('alice')] aus und speichert das Ergebnis in expected; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 67 | <code>        self.assertEqual(client.stat(), (len(expected), sum(map(len, expected))))</code> | Testassertion: self.assertEqual(client.stat(), (len(expected), sum(map(len, expected)))). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 68 | <code>        self.assertEqual(set(client.capa()), {"USER", "TOP", "UIDL", "RESP-CODES", "EXPIRE", "IMPLEMENTATION"})</code> | Testassertion: self.assertEqual(set(client.capa()), {'USER', 'TOP', 'UIDL', 'RESP-CODES', 'EXPIRE', 'IMPLEMENTATION'}). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 69 | <code>        listing = client.list()[1]</code> | Wertet client.list()[1] aus und speichert das Ergebnis in listing; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 70 | <code>        self.assertEqual(listing, [f"{n} {len(mail)}".encode() for n, mail in enumerate(expected, 1)])</code> | Testassertion: self.assertEqual(listing, [f'{n} {len(mail)}'.encode() for n, mail in enumerate(expected, 1)]). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 71 | <code>        for number, mail in enumerate(expected, 1):</code> | Durchläuft enumerate(expected, 1); pro Element wird (number, mail) gesetzt und der eingerückte Körper ausgeführt. |
| 72 | <code>            self.assertEqual(client.list(number).split()[1:], [str(number).encode(), str(len(mail)).encode()])</code> | Testassertion: self.assertEqual(client.list(number).split()[1:], [str(number).encode(), str(len(mail)).encode()]). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 73 | <code>            _, lines, _ = client.retr(number)</code> | Wertet client.retr(number) aus und speichert das Ergebnis in (_, lines, _); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 74 | <code>            self.assertEqual(b"\r\n".join(lines) + b"\r\n", mail)</code> | Testassertion: self.assertEqual(b'\r\n'.join(lines) + b'\r\n', mail). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 75 | <code>            uid = client.uidl(number).split()[-1]</code> | Setzt die stabile UID der Nachricht für Vergleich nach neuer Anmeldung. Rechte Seite: client.uidl(number).split()[-1]. |
| 76 | <code>            self.assertEqual(uid.decode(), message_uid("alice", self.db.get_messages("alice")[number - 1]))</code> | Testassertion: self.assertEqual(uid.decode(), message_uid('alice', self.db.get_messages('alice')[number - 1])). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 77 | <code>        self.assertEqual(len(client.uidl()[1]), 4)</code> | Testassertion: self.assertEqual(len(client.uidl()[1]), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 78 | <code>        _, top_lines, _ = client.top(1, 0)</code> | Wertet client.top(1, 0) aus und speichert das Ergebnis in (_, top_lines, _); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 79 | <code>        self.assertEqual(b"\r\n".join(top_lines) + b"\r\n", expected[0].partition(b"\r\n\r\n")[0] + b"\r\n\r\n")</code> | Testassertion: self.assertEqual(b'\r\n'.join(top_lines) + b'\r\n', expected[0].partition(b'\r\n\r\n')[0] + b'\r\n\r\n'). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 80 | <code>        self.assertTrue(client.noop().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(client.noop().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 81 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 82 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 83 | <code>    def test_wire_dot_stuffing_crlf_and_unicode_octets(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Vergleicht Nachrichtenbytes und beobachtet tatsächliche doppelte Punkte/CRLF auf dem Rohsocket. |
| 84 | <code>        client = self.connect("bob", "bob-test")</code> | Wertet self.connect('bob', 'bob-test') aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 85 | <code>        expected = canonical_message(self.db.get_messages("bob")[0]["raw"])</code> | Wertet canonical_message(self.db.get_messages('bob')[0]['raw']) aus und speichert das Ergebnis in expected; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 86 | <code>        self.assertEqual(client.stat(), (1, len(expected)))</code> | Testassertion: self.assertEqual(client.stat(), (1, len(expected))). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 87 | <code>        self.assertEqual(b"\r\n".join(client.retr(1)[1]) + b"\r\n", expected)</code> | Testassertion: self.assertEqual(b'\r\n'.join(client.retr(1)[1]) + b'\r\n', expected). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 88 | <code>        self.assertEqual(client.top(1, 2)[1], [b"Subject: Dots", b"", b".first", b"."])</code> | Testassertion: self.assertEqual(client.top(1, 2)[1], [b'Subject: Dots', b'', b'.first', b'.']). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 89 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 90 | <code>        connection, reader = self.raw()</code> | Wertet self.raw() aus und speichert das Ergebnis in (connection, reader); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 91 | <code>        connection.sendall(b"USER bob\r\nPASS bob-test\r\nRETR 1\r\n")</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(b'USER bob\r\nPASS bob-test\r\nRETR 1\r\n'). |
| 92 | <code>        self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 93 | <code>        self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 94 | <code>        self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 95 | <code>        lines = []</code> | Setzt die gesammelten/auszugebenden Datenzeilen, getrennt von Status und Endmarke. Rechte Seite: []. |
| 96 | <code>        while True:</code> | Wiederholt den eingerückten Empfangs-/Verarbeitungsblock solange True gilt; break oder return beendet die Schleife. |
| 97 | <code>            line = reader.readline()</code> | Setzt die nächste gepufferte Protokollzeile beziehungsweise ihre Nutzbytes. Rechte Seite: reader.readline(). |
| 98 | <code>            self.assertTrue(line.endswith(b"\r\n"))</code> | Testassertion: self.assertTrue(line.endswith(b'\r\n')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 99 | <code>            if line == b".\r\n":</code> | Prüft die Bedingung line == b'.\r\n'. Nur bei Wahr wird der eingerückte Zweig ausgeführt; sonst folgt ein alternativer Zweig oder der nächste Befehl. |
| 100 | <code>                break</code> | Verlässt nur die nächste umgebende Schleife, etwa bei EOF, QUIT oder ungültigem Framing; finally-Aufräumen bleibt wirksam. |
| 101 | <code>            lines.append(line)</code> | Führt den Aufruf/Ausdruck lines.append(line) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 102 | <code>        self.assertIn(b"..first\r\n", lines)</code> | Testassertion: self.assertIn(b'..first\r\n', lines). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 103 | <code>        self.assertIn(b"..\r\n", lines)</code> | Testassertion: self.assertIn(b'..\r\n', lines). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 104 | <code>        self.assertIn(b"...third\r\n", lines)</code> | Testassertion: self.assertIn(b'...third\r\n', lines). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 105 | <code>        connection.sendall(b"QUIT\r\n")</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(b'QUIT\r\n'). |
| 106 | <code>        self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 107 | <code>        self.assertEqual(reader.readline(), b"")</code> | Testassertion: self.assertEqual(reader.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 108 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 109 | <code>    def test_dele_rset_update_and_uid_stability_after_renumber(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft Markierung, Unsichtbarkeit, RSET, tatsächliches QUIT-UPDATE und stabile UID bei neuer Nummer. |
| 110 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 111 | <code>        uid = client.uidl(2).split()[-1]</code> | Setzt die stabile UID der Nachricht für Vergleich nach neuer Anmeldung. Rechte Seite: client.uidl(2).split()[-1]. |
| 112 | <code>        client.dele(1)</code> | Führt den Aufruf/Ausdruck client.dele(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 113 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 114 | <code>        self.assertEqual(client.stat()[0], 3)</code> | Testassertion: self.assertEqual(client.stat()[0], 3). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 115 | <code>        self.assertTrue(client.list()[1][0].startswith(b"2 "))</code> | Testassertion: self.assertTrue(client.list()[1][0].startswith(b'2 ')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 116 | <code>        for command in ("RETR 1", "LIST 1", "UIDL 1", "TOP 1 0", "DELE 1"):</code> | Durchläuft ('RETR 1', 'LIST 1', 'UIDL 1', 'TOP 1 0', 'DELE 1'); pro Element wird command gesetzt und der eingerückte Körper ausgeführt. |
| 117 | <code>            with self.subTest(command=command), self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.subTest(command=command), self.assertRaises(poplib.error_proto). |
| 118 | <code>                client._shortcmd(command)</code> | Führt den Aufruf/Ausdruck client._shortcmd(command) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 119 | <code>        client.rset()</code> | Führt den Aufruf/Ausdruck client.rset() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 120 | <code>        self.assertEqual(client.stat()[0], 4)</code> | Testassertion: self.assertEqual(client.stat()[0], 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 121 | <code>        client.dele(1)</code> | Führt den Aufruf/Ausdruck client.dele(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 122 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 123 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 3)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 3). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 124 | <code>        second = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in second; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 125 | <code>        self.assertEqual(second.uidl(1).split()[-1], uid)</code> | Testassertion: self.assertEqual(second.uidl(1).split()[-1], uid). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 126 | <code>        second.quit()</code> | Führt den Aufruf/Ausdruck second.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 127 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 128 | <code>    def test_disconnect_rolls_back_and_unlocks(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Simuliert Client-Absturz ohne QUIT; Mailbestand und freie Sperre müssen erhalten bleiben. |
| 129 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 130 | <code>        client.dele(2)</code> | Führt den Aufruf/Ausdruck client.dele(2) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 131 | <code>        client.close()  # Kein QUIT: simulierter Client-Absturz.</code> | Führt den Aufruf/Ausdruck client.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 132 | <code>        lock = self.server.maildrop_lock("alice")</code> | Wertet self.server.maildrop_lock('alice') aus und speichert das Ergebnis in lock; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 133 | <code>        self.assertTrue(lock.acquire(timeout=2))</code> | Testassertion: self.assertTrue(lock.acquire(timeout=2)). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 134 | <code>        lock.release()</code> | Gibt die zuvor erworbene Sperre frei, damit eine andere Sitzung das Postfach öffnen kann. lock.release(). |
| 135 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 136 | <code>        next_client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in next_client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 137 | <code>        self.assertEqual(next_client.stat()[0], 4)</code> | Testassertion: self.assertEqual(next_client.stat()[0], 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 138 | <code>        next_client.quit()</code> | Führt den Aufruf/Ausdruck next_client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 139 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 140 | <code>    def test_concurrent_users_and_same_maildrop_rejected(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Synchronisiert Alice/Bob mit Barrier und hält beide offen, während ein weiterer Alice-Login abgewiesen wird. |
| 141 | <code>        barrier = threading.Barrier(3)</code> | Wertet threading.Barrier(3) aus und speichert das Ergebnis in barrier; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 142 | <code>        release = threading.Event()</code> | Wertet threading.Event() aus und speichert das Ergebnis in release; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 143 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 144 | <code>        def session(user, password):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Hält eine echte angemeldete Benutzersitzung bis zur gemeinsamen Freigabe offen und beendet sie danach mit QUIT. |
| 145 | <code>            client = self.connect(user, password)</code> | Wertet self.connect(user, password) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 146 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 147 | <code>                barrier.wait(timeout=3)</code> | Führt den Aufruf/Ausdruck barrier.wait(timeout=3) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 148 | <code>                self.assertTrue(release.wait(timeout=3))</code> | Testassertion: self.assertTrue(release.wait(timeout=3)). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 149 | <code>                return client.stat()[0]</code> | Beendet diesen Funktionsaufruf und liefert client.stat()[0] an den Aufrufer; nachfolgender Code dieser Funktion läuft nicht. |
| 150 | <code>            finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 151 | <code>                client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 152 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 153 | <code>        with ThreadPoolExecutor(max_workers=2) as pool:</code> | Öffnet die Kontexte ThreadPoolExecutor(max_workers=2). Deren __exit__ sorgt anschließend auch im Fehlerfall für Freigabe/QUIT/Join. |
| 154 | <code>            first = pool.submit(session, "alice", "secret")</code> | Wertet pool.submit(session, 'alice', 'secret') aus und speichert das Ergebnis in first; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 155 | <code>            second = pool.submit(session, "bob", "bob-test")</code> | Wertet pool.submit(session, 'bob', 'bob-test') aus und speichert das Ergebnis in second; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 156 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 157 | <code>                barrier.wait(timeout=3)</code> | Führt den Aufruf/Ausdruck barrier.wait(timeout=3) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 158 | <code>                self.assertGreaterEqual(len(self.server._connections), 2)</code> | Testassertion: self.assertGreaterEqual(len(self.server._connections), 2). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 159 | <code>                blocked = poplib.POP3(*self.server.server_address, timeout=2)</code> | Wertet poplib.POP3(*self.server.server_address, timeout=2) aus und speichert das Ergebnis in blocked; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 160 | <code>                self.addCleanup(blocked.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(blocked.close). |
| 161 | <code>                blocked.user("alice")</code> | Führt den Aufruf/Ausdruck blocked.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 162 | <code>                with self.assertRaisesRegex(poplib.error_proto, "IN-USE"):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaisesRegex(poplib.error_proto, 'IN-USE'). |
| 163 | <code>                    blocked.pass_("secret")</code> | Führt den Aufruf/Ausdruck blocked.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 164 | <code>                blocked.quit()</code> | Führt den Aufruf/Ausdruck blocked.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 165 | <code>            finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 166 | <code>                release.set()</code> | Führt den Aufruf/Ausdruck release.set() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 167 | <code>            self.assertEqual(first.result(timeout=3), 4)</code> | Testassertion: self.assertEqual(first.result(timeout=3), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 168 | <code>            self.assertEqual(second.result(timeout=3), 1)</code> | Testassertion: self.assertEqual(second.result(timeout=3), 1). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 169 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 170 | <code>    def test_authorization_wrong_states_and_syntax(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft Authentifizierungsreihenfolge, falsche Zustände und viele fehlerhafte Befehle ohne Bestandsänderung. |
| 171 | <code>        client = poplib.POP3(*self.server.server_address, timeout=2)</code> | Wertet poplib.POP3(*self.server.server_address, timeout=2) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 172 | <code>        self.addCleanup(client.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(client.close). |
| 173 | <code>        self.assertIn("USER", client.capa())</code> | Testassertion: self.assertIn('USER', client.capa()). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 174 | <code>        for command in ("STAT", "PASS secret", "RETR 1", "DELE 1", "NOOP", "RSET", "LIST", "UIDL", "TOP 1 0", "BOGUS", "CAPA x", "QUIT x"):</code> | Durchläuft ('STAT', 'PASS secret', 'RETR 1', 'DELE 1', 'NOOP', 'RSET', 'LIST', 'UIDL', 'TOP 1 0', 'BOGUS', 'CAPA x', 'QUIT x'); pro Element wird command gesetzt und der eingerückte Körper ausgeführt. |
| 175 | <code>            with self.subTest(command=command), self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.subTest(command=command), self.assertRaises(poplib.error_proto). |
| 176 | <code>                client._shortcmd(command)</code> | Führt den Aufruf/Ausdruck client._shortcmd(command) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 177 | <code>        client.user("alice")</code> | Führt den Aufruf/Ausdruck client.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 178 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 179 | <code>            client.pass_("alice123")</code> | Führt den Aufruf/Ausdruck client.pass_('alice123') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 180 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 181 | <code>            client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 182 | <code>        client.user("alice")</code> | Führt den Aufruf/Ausdruck client.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 183 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 184 | <code>            client.noop()</code> | Führt den Aufruf/Ausdruck client.noop() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 185 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 186 | <code>            client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 187 | <code>        client.user("alice")</code> | Führt den Aufruf/Ausdruck client.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 188 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 189 | <code>            client._shortcmd("PASS")</code> | Führt den Aufruf/Ausdruck client._shortcmd('PASS') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 190 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 191 | <code>            client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 192 | <code>        client.user("nobody")</code> | Führt den Aufruf/Ausdruck client.user('nobody') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 193 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 194 | <code>            client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 195 | <code>        client.user("alice")</code> | Führt den Aufruf/Ausdruck client.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 196 | <code>        client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 197 | <code>        for command in ("USER bob", "PASS secret", "STAT x", "NOOP x", "RSET x", "LIST 0", "LIST -1", "LIST +1", "LIST abc", "LIST 99", "LIST 1 2", "RETR", "TOP 1 -1", "TOP 1 nope", "DELE 2 3", "AUTH", "STLS", "APOP a b"):</code> | Durchläuft ('USER bob', 'PASS secret', 'STAT x', 'NOOP x', 'RSET x', 'LIST 0', 'LIST -1', 'LIST +1', 'LIST abc', 'LIST 99', 'LIST 1 2', 'RETR', 'TOP 1 -1', 'TOP 1 nope', 'DELE 2 3', 'AUTH', 'STLS', …; pro Element wird command gesetzt und der eingerückte Körper ausgeführt. |
| 198 | <code>            with self.subTest(command=command), self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.subTest(command=command), self.assertRaises(poplib.error_proto). |
| 199 | <code>                client._shortcmd(command)</code> | Führt den Aufruf/Ausdruck client._shortcmd(command) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 200 | <code>        self.assertEqual(client.stat()[0], 4)</code> | Testassertion: self.assertEqual(client.stat()[0], 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 201 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 202 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 203 | <code>    def test_fragmentation_multiple_commands_and_lowercase(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Sendet jeden Befehlsbyte einzeln und liest mehrere korrekte Antworten in Reihenfolge. |
| 204 | <code>        connection, reader = self.raw()</code> | Wertet self.raw() aus und speichert das Ergebnis in (connection, reader); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 205 | <code>        wire = b"user alice\r\npass secret\r\nstat\r\nnoop\r\nquit\r\n"</code> | Setzt die tatsächlich gesendeten Befehlsbytes einschließlich CRLF. Rechte Seite: b'user alice\r\npass secret\r\nstat\r\nnoop\r\nquit\r\n'. |
| 206 | <code>        for octet in wire:</code> | Durchläuft wire; pro Element wird octet gesetzt und der eingerückte Körper ausgeführt. |
| 207 | <code>            connection.sendall(bytes([octet]))</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(bytes([octet])). |
| 208 | <code>        for _ in range(5):</code> | Durchläuft range(5); pro Element wird _ gesetzt und der eingerückte Körper ausgeführt. |
| 209 | <code>            self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 210 | <code>        self.assertEqual(reader.readline(), b"")</code> | Testassertion: self.assertEqual(reader.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 211 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 212 | <code>    def test_command_length_limit_and_invalid_framing(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft die 255-Byte-Grenze und Verbindungsende nach überlangem Befehl/nacktem LF. |
| 213 | <code>        connection, reader = self.raw()</code> | Wertet self.raw() aus und speichert das Ergebnis in (connection, reader); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 214 | <code>        maximum = b"USER " + b"x" * (255 - len(b"USER \r\n")) + b"\r\n"</code> | Wertet b'USER ' + b'x' * (255 - len(b'USER \r\n')) + b'\r\n' aus und speichert das Ergebnis in maximum; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 215 | <code>        self.assertEqual(len(maximum), 255)</code> | Testassertion: self.assertEqual(len(maximum), 255). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 216 | <code>        connection.sendall(maximum)</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(maximum). |
| 217 | <code>        self.assertTrue(reader.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 218 | <code>        connection.sendall(b"USER " + b"x" * 249 + b"\r\n")</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. connection.sendall(b'USER ' + b'x' * 249 + b'\r\n'). |
| 219 | <code>        self.assertTrue(reader.readline().startswith(b"-ERR"))</code> | Testassertion: self.assertTrue(reader.readline().startswith(b'-ERR')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 220 | <code>        self.assertEqual(reader.readline(), b"")</code> | Testassertion: self.assertEqual(reader.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 221 | <code>        other, output = self.raw()</code> | Wertet self.raw() aus und speichert das Ergebnis in (other, output); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 222 | <code>        other.sendall(b"USER alice\n")</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. other.sendall(b'USER alice\n'). |
| 223 | <code>        self.assertTrue(output.readline().startswith(b"-ERR"))</code> | Testassertion: self.assertTrue(output.readline().startswith(b'-ERR')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 224 | <code>        self.assertEqual(output.readline(), b"")</code> | Testassertion: self.assertEqual(output.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 225 | <code>        third, result = self.raw()</code> | Wertet self.raw() aus und speichert das Ergebnis in (third, result); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 226 | <code>        third.sendall(b"USER \xff\r\nCAPA\r\n")</code> | Sendet alle angegebenen Bytes über den echten TCP-Socket; einzelne sendall-Aufrufe erzeugen keine garantierten Paketgrenzen. third.sendall(b'USER \xff\r\nCAPA\r\n'). |
| 227 | <code>        self.assertTrue(result.readline().startswith(b"-ERR"))</code> | Testassertion: self.assertTrue(result.readline().startswith(b'-ERR')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 228 | <code>        self.assertTrue(result.readline().startswith(b"+OK"))</code> | Testassertion: self.assertTrue(result.readline().startswith(b'+OK')). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 229 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 230 | <code>    def test_empty_mailbox_and_quit_in_authorization(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft positive leere Listen und QUIT ohne vorheriges Öffnen eines Maildrops. |
| 231 | <code>        client = self.connect("empty", "empty-test")</code> | Wertet self.connect('empty', 'empty-test') aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 232 | <code>        self.assertEqual(client.stat(), (0, 0))</code> | Testassertion: self.assertEqual(client.stat(), (0, 0)). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 233 | <code>        self.assertEqual(client.list()[1], [])</code> | Testassertion: self.assertEqual(client.list()[1], []). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 234 | <code>        self.assertEqual(client.uidl()[1], [])</code> | Testassertion: self.assertEqual(client.uidl()[1], []). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 235 | <code>        client.rset()</code> | Führt den Aufruf/Ausdruck client.rset() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 236 | <code>        with self.assertRaises(poplib.error_proto):</code> | Erwartet gezielt die angegebene Ausnahme; fehlt sie, schlägt der Test fehl. self.assertRaises(poplib.error_proto). |
| 237 | <code>            client.retr(1)</code> | Führt den Aufruf/Ausdruck client.retr(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 238 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 239 | <code>        anonymous = poplib.POP3(*self.server.server_address, timeout=2)</code> | Wertet poplib.POP3(*self.server.server_address, timeout=2) aus und speichert das Ergebnis in anonymous; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 240 | <code>        self.addCleanup(anonymous.close)</code> | Registriert garantiertes Aufräumen bei unittest, auch wenn später eine Assertion fehlschlägt. self.addCleanup(anonymous.close). |
| 241 | <code>        anonymous.quit()</code> | Führt den Aufruf/Ausdruck anonymous.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 242 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 243 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 244 | <code>    def test_timeout_rolls_back_and_releases_lock(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Wartet auf den echten Server-Timeout statt blind zu schlafen und prüft Rollback/Sperrfreigabe. |
| 245 | <code>        self.server.client_timeout = 0.1</code> | Wertet 0.1 aus und speichert das Ergebnis in self.server.client_timeout; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 246 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 247 | <code>        client.dele(1)</code> | Führt den Aufruf/Ausdruck client.dele(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 248 | <code>        # Blockierendes Lesen wartet auf den echten Server-Timeout, kein blindes sleep.</code> | Kommentar/KI-Nachweis: Blockierendes Lesen wartet auf den echten Server-Timeout, kein blindes sleep.. Kein ausführbarer Python-Befehl. |
| 249 | <code>        self.assertEqual(client.file.readline(), b"")</code> | Testassertion: self.assertEqual(client.file.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 250 | <code>        lock = self.server.maildrop_lock("alice")</code> | Wertet self.server.maildrop_lock('alice') aus und speichert das Ergebnis in lock; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 251 | <code>        self.assertTrue(lock.acquire(timeout=2))</code> | Testassertion: self.assertTrue(lock.acquire(timeout=2)). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 252 | <code>        lock.release()</code> | Gibt die zuvor erworbene Sperre frei, damit eine andere Sitzung das Postfach öffnen kann. lock.release(). |
| 253 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 254 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 255 | <code>    def test_server_close_aborts_active_session_without_update(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Stoppt den Server bei offener DELE-Sitzung; es darf keine Löschung erfolgen. |
| 256 | <code>        client = self.connect()</code> | Wertet self.connect() aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 257 | <code>        client.dele(1)</code> | Führt den Aufruf/Ausdruck client.dele(1) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 258 | <code>        self.server.shutdown()</code> | Beendet die angegebene Socket-/Accept-Aktivität und weckt blockierendes Warten; bei BaseServer erfolgt der Aufruf aus einem anderen Thread. self.server.shutdown(). |
| 259 | <code>        self.server.server_close()</code> | Führt den Aufruf/Ausdruck self.server.server_close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 260 | <code>        self.assertEqual(client.file.readline(), b"")</code> | Testassertion: self.assertEqual(client.file.readline(), b''). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 261 | <code>        self.assertEqual(len(self.db.get_messages("alice")), 4)</code> | Testassertion: self.assertEqual(len(self.db.get_messages('alice')), 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 262 | <code>        self.assertFalse(self.server._connections)</code> | Testassertion: self.assertFalse(self.server._connections). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 263 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 264 | <code>    def test_password_with_spaces(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft die PASS-Sonderregel: Das gesamte Restargument ist das Passwort. |
| 265 | <code>        self.db.users["bob"]["password"] = "test with spaces"</code> | Wertet 'test with spaces' aus und speichert das Ergebnis in self.db.users['bob']['password']; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 266 | <code>        client = self.connect("bob", "test with spaces")</code> | Wertet self.connect('bob', 'test with spaces') aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 267 | <code>        self.assertEqual(client.stat()[0], 1)</code> | Testassertion: self.assertEqual(client.stat()[0], 1). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 268 | <code>        client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 269 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 270 | <code>    def test_canonicalization_preserves_trailing_blank_lines(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Prüft CR/LF-Normalisierung, Erhalt leerer Endzeilen und Unterscheidung verschiedener IDs. |
| 271 | <code>        self.assertEqual(canonical_message("a\rb\nc\r\n\r\n"), b"a\r\nb\r\nc\r\n\r\n")</code> | Testassertion: self.assertEqual(canonical_message('a\rb\nc\r\n\r\n'), b'a\r\nb\r\nc\r\n\r\n'). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 272 | <code>        self.assertEqual(canonical_message(b"header\n\nbody"), b"header\r\n\r\nbody\r\n")</code> | Testassertion: self.assertEqual(canonical_message(b'header\n\nbody'), b'header\r\n\r\nbody\r\n'). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 273 | <code>        self.assertNotEqual(message_uid("alice", {"id": 1, "raw": "x"}),</code> | Testassertion: self.assertNotEqual(message_uid('alice', {'id': 1, 'raw': 'x'}), message_uid('alice', {'id': 2, 'raw': 'x'})). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 274 | <code>                            message_uid("alice", {"id": 2, "raw": "x"}))</code> | Fortsetzungszeile der Anweisung ab Zeile 273. Testassertion: self.assertNotEqual(message_uid('alice', {'id': 1, 'raw': 'x'}), message_uid('alice', {'id': 2, 'raw': 'x'})). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 275 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 276 | <code>    def test_real_server_cli_and_client_cli_subprocesses(self):</code> | Definiert die Funktion/Methode und ihre Parameter; der Körper läuft erst beim Aufruf. Startet beide Programme als echte Prozesse, prüft Client-Ausgabe und danach denselben Server mit poplib. |
| 277 | <code>        root = Path(__file__).resolve().parents[1]</code> | Wertet Path(__file__).resolve().parents[1] aus und speichert das Ergebnis in root; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 278 | <code>        process = subprocess.Popen([sys.executable, str(root / "ue3.3" / "pop3_server.py"),</code> | Wertet subprocess.Popen([sys.executable, str(root / 'ue3.3' / 'pop3_server.py'), '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) aus und speichert das Ergebnis in process; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 279 | <code>                                    "--port", "0"], stdout=subprocess.PIPE,</code> | Fortsetzungszeile der Anweisung ab Zeile 278. Wertet subprocess.Popen([sys.executable, str(root / 'ue3.3' / 'pop3_server.py'), '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) aus und speichert das Ergebnis in process; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 280 | <code>                                   stderr=subprocess.PIPE, text=True)</code> | Fortsetzungszeile der Anweisung ab Zeile 278. Wertet subprocess.Popen([sys.executable, str(root / 'ue3.3' / 'pop3_server.py'), '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) aus und speichert das Ergebnis in process; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 281 | <code>        try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 282 | <code>            banner = process.stdout.readline().strip()</code> | Wertet process.stdout.readline().strip() aus und speichert das Ergebnis in banner; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 283 | <code>            self.assertTrue(banner.startswith("POP3 plaintext lab: 127.0.0.1:"), banner)</code> | Testassertion: self.assertTrue(banner.startswith('POP3 plaintext lab: 127.0.0.1:'), banner). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 284 | <code>            port = int(banner.rsplit(":", 1)[1])</code> | Wertet int(banner.rsplit(':', 1)[1]) aus und speichert das Ergebnis in port; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 285 | <code>            self.assertIn("alice / secret", process.stdout.readline())</code> | Testassertion: self.assertIn('alice / secret', process.stdout.readline()). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 286 | <code>            result = subprocess.run([sys.executable, str(root / "ue3.2" / "pop3_client.py"),</code> | Wertet subprocess.run([sys.executable, str(root / 'ue3.2' / 'pop3_client.py'), '--port', str(port), '--user', 'alice', '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 287 | <code>                                     "--port", str(port), "--user", "alice", "--password", "secret"],</code> | Fortsetzungszeile der Anweisung ab Zeile 286. Wertet subprocess.run([sys.executable, str(root / 'ue3.2' / 'pop3_client.py'), '--port', str(port), '--user', 'alice', '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 288 | <code>                                    capture_output=True, text=True, timeout=5)</code> | Fortsetzungszeile der Anweisung ab Zeile 286. Wertet subprocess.run([sys.executable, str(root / 'ue3.2' / 'pop3_client.py'), '--port', str(port), '--user', 'alice', '--password', 'secret'], capture_output=True, text=True, timeout=5) aus und speichert das Ergebnis in result; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 289 | <code>            self.assertEqual(result.returncode, 0, result.stderr)</code> | Testassertion: self.assertEqual(result.returncode, 0, result.stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 290 | <code>            self.assertIn("QUIT bestätigt", result.stdout)</code> | Testassertion: self.assertIn('QUIT bestätigt', result.stdout). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 291 | <code>            print("\nEchter CLI-Lauf (separater Server- und Clientprozess):\n" + result.stdout)</code> | Führt den Aufruf/Ausdruck print('\nEchter CLI-Lauf (separater Server- und Clientprozess):\n' + result.stdout) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 292 | <code>            client = poplib.POP3("127.0.0.1", port, timeout=2)</code> | Wertet poplib.POP3('127.0.0.1', port, timeout=2) aus und speichert das Ergebnis in client; die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 293 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 294 | <code>                client.user("alice")</code> | Führt den Aufruf/Ausdruck client.user('alice') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 295 | <code>                client.pass_("secret")</code> | Führt den Aufruf/Ausdruck client.pass_('secret') aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 296 | <code>                self.assertEqual(client.stat()[0], 4)</code> | Testassertion: self.assertEqual(client.stat()[0], 4). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 297 | <code>                client.quit()</code> | Führt den Aufruf/Ausdruck client.quit() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 298 | <code>            finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 299 | <code>                client.close()</code> | Führt den Aufruf/Ausdruck client.close() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 300 | <code>        finally:</code> | Dieser Aufräumblock läuft beim Verlassen von try immer, auch nach Fehler, return oder break. |
| 301 | <code>            process.send_signal(signal.SIGINT)</code> | Führt den Aufruf/Ausdruck process.send_signal(signal.SIGINT) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 302 | <code>            try:</code> | Beginnt einen geschützten Ablauf. except behandelt die unten genannten Fehler; finally wird beim Verlassen auch nach return/Ausnahme ausgeführt. |
| 303 | <code>                _, stderr = process.communicate(timeout=5)</code> | Wertet process.communicate(timeout=5) aus und speichert das Ergebnis in (_, stderr); die Zuweisung wird beim nächsten Schritt weiterverwendet. |
| 304 | <code>            except subprocess.TimeoutExpired:</code> | Fängt genau die genannten Ausnahmetypen des vorigen try-Blocks ab; andere Fehler werden nicht stillschweigend verschluckt. |
| 305 | <code>                process.kill()</code> | Führt den Aufruf/Ausdruck process.kill() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 306 | <code>                process.communicate()</code> | Führt den Aufruf/Ausdruck process.communicate() aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |
| 307 | <code>                raise</code> | Bricht diesen Pfad mit der ursprünglichen Ausnahme ab; Aufrufer/Test muss den Fehler behandeln. |
| 308 | <code>            self.assertEqual(process.returncode, 0, stderr)</code> | Testassertion: self.assertEqual(process.returncode, 0, stderr). Vergleicht die tatsächliche Ausführung mit der Erwartung; eine Abweichung ist ein fehlgeschlagener Test. |
| 309 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 310 | <code>∅</code> | Leerzeile: trennt logische Abschnitte; keine Laufzeitwirkung. |
| 311 | <code>if __name__ == "__main__":</code> | Startet main/unittest nur bei direktem Skriptaufruf, nicht beim Import durch GUI oder Tests. |
| 312 | <code>    unittest.main(verbosity=2)</code> | Führt den Aufruf/Ausdruck unittest.main(verbosity=2) aus. Seine Wirkung gehört zum oben beschriebenen Funktionszweck; Fehler laufen in die umgebenden Fehler-/Cleanup-Blöcke. |

## Vollständigkeit

Die Tabellen decken **963 physische Zeilen** der vier angegebenen Python-Dateien ab. Die vier SHA-256-Werte kennzeichnen den erklärten Quellstand; bei Änderungen müssen Zeilenbezug und Erklärung gemeinsam aktualisiert werden. Die Zahl ist aus den tatsächlich gelesenen Dateien berechnet.
