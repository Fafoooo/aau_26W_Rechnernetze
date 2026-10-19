# Ü 3.3 – POP3-Threadserver

> **KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent; Modell: OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). **Datum:** 2026-10-19. **Auftrag:** POP3-Socket-Server mit einem Thread pro Verbindung, Originaldatenklasse, parallelen Benutzerkonten, GUI-relevanten Befehlen, Zustandsautomat, sicherem Löschablauf und realen Tests implementieren; Startbefehle und Integrations-API bereitstellen.

## Start und Testkonto

Alle Befehle im Repo `/home/ubuntu/uni/aau_26W_Rechnernetze` ausführen:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.3/pop3_server.py --host 127.0.0.1 --port 11110
```

Beenden mit **Strg+C**. Nur Python-Standardbibliothek; keine Installation, kein root und kein Port 110 erforderlich. Default: IPv4-Loopback `127.0.0.1`, Port `11110`, Socket-Timeout `600` Sekunden. `--port 0` lässt das Betriebssystem einen freien Port vergeben; die erste Ausgabe nennt ihn. Der Standard-Timeout erfüllt die Mindestdauer des Inaktivitätstimers aus RFC 1939 § 3. Kürzere Werte dienen ausschließlich beschleunigten Tests/Entwicklung.

**Originalkonto:** Benutzer `alice`, Passwort `secret`; vier Nachrichten. Das widersprüchliche `alice123` in den README-Beispielen wird nicht übernommen, denn die originale Datenklasse enthält `secret`. Der Server lädt `../Angabe/SampleDataBase.py` anhand seines eigenen Dateipfads, daher funktioniert der Start auch aus einem anderen Arbeitsverzeichnis. Originaldatenklasse und Original-README bleiben unverändert.

Passender eigener Client in einem zweiten Terminal:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.2/pop3_client.py --host 127.0.0.1 --port 11110 --user alice --password secret --message 1
```

## Architektur und Protokoll

`socketserver.TCPServer` verwendet echte TCP-Sockets. `ThreadingMixIn` startet **pro angenommener Verbindung einen Worker-Thread**; das akzeptierende Hauptprogramm bleibt frei für neue Verbindungen. Vor dem Login ist noch kein Benutzer bekannt. Nach erfolgreichem USER/PASS gehört die Sitzung genau einem Benutzer.

Die originale Datenbank wird einmal pro Serverinstanz erzeugt. Sie bietet `authenticate(user, password)` und `get_messages(user)`, wobei die zweite Methode eine lebende `list[dict]` mit `id` und `raw` zurückgibt. Weil keine Löschmethode existiert, erfolgt UPDATE als Slice-Zuweisung auf diese Liste. Das ist bewusst an den Vertrag der bereitgestellten Klasse gebunden und ändert **nicht deren Quelldatei**.

### Unterstützte Befehle

| Befehl | Zustand | Antwort / Wirkung |
|---|---|---|
| `CAPA` | AUTHORIZATION und TRANSACTION | Mehrzeilig: USER, TOP, UIDL, RESP-CODES, EXPIRE NEVER, IMPLEMENTATION |
| `USER name` | AUTHORIZATION | Benutzer merken; Existenz noch nicht verraten |
| `PASS password` | AUTHORIZATION, direkt nach USER | Passwort prüfen, Maildrop exklusiv sperren, Snapshot bilden; dann TRANSACTION |
| `STAT` | TRANSACTION | Anzahl und Summe der Oktettgrößen nicht markierter Mails |
| `LIST [n]` | TRANSACTION | Ohne Nummer mehrzeilige Größenliste; mit Nummer eine Statuszeile |
| `UIDL [n]` | TRANSACTION | Stabile UID statt veränderlicher Sitzungsnummer |
| `RETR n` | TRANSACTION | Komplette Nachricht, dot-gestufft und CRLF-normalisiert |
| `TOP n k` | TRANSACTION | Kopfzeilen, Leerzeile und erste `k` Body-Zeilen; `k=0` zulässig |
| `DELE n` | TRANSACTION | Nur Löschmarkierung für diese Sitzung setzen |
| `RSET` | TRANSACTION | Alle Löschmarkierungen zurücknehmen |
| `NOOP` | TRANSACTION | Positive Antwort, keine Änderung |
| `QUIT` | AUTHORIZATION | Nur Verbindung beenden |
| `QUIT` | TRANSACTION | UPDATE: markierte Nachrichten entfernen, dann Verbindung beenden |

Unbekannte, im falschen Zustand gesendete oder syntaktisch falsche Befehle erhalten `-ERR`. Der Parser akzeptiert groß-/kleingeschriebene Schlüsselwörter, druckbares ASCII und bis zu **255 Bytes inklusive CRLF** (RFC 2449). PASS behandelt den gesamten Rest der Zeile als Passwort, sodass auch Leerzeichen möglich sind. Nach fehlgeschlagenem PASS oder einem zwischen USER und PASS eingeschobenen anderen Befehl ist ein neues USER notwendig. Bei zu langen oder nicht CRLF-beendeten Befehlen wird nach `-ERR` geschlossen, um Restbytes nicht als neue Befehle misszuverstehen. Kontrollzeichen/nicht-ASCII werden abgewiesen.

### Parallelität, Locks und Löschung

- Ein kurzer globaler Verwaltungslock schützt die Erstellung der benutzerspezifischen Locks und die Menge offener Verbindungen. Er wird **nicht** während einer Sitzung gehalten.
- Jedes Postfach hat einen eigenen Lock. Alice und ein anderer Benutzer können gleichzeitig angemeldet sein; zwei gleichzeitige TRANSACTION-Sitzungen für Alice werden verhindert. Der zweite Login erhält nach erfolgreicher Passwortprüfung `-ERR [IN-USE] maildrop locked`, ohne den ersten zu blockieren.
- Erst nach Erwerb des Locks wird ein Snapshot aus Nachrichtendaten aufgebaut. `enumerate(..., 1)` weist die sitzungsbezogenen Nummern zu; Datenbank-IDs werden nicht als POP3-Nummern missverstanden.
- DELE verändert nur eine lokale Menge von Nummern. Markierte Nachrichten verschwinden aus STAT/LIST/UIDL und sind nicht mehr abrufbar. Die übrigen Nummern bleiben bis zum Ende der Sitzung erhalten.
- Nur QUIT führt zur Veränderung der Datenbankliste. RSET, EOF, TCP-Abbruch, Timeout und Serverstopp ohne QUIT bewirken kein UPDATE. Der `finally`-Block gibt den Lock unabhängig vom Ausgang frei.
- `server_close()` unterbricht offene Sitzungen, schließt den Listener und wartet auf die nicht-daemonisierten Worker. Ein Schließflag deckt dabei auch gerade gestartete Worker ab.
- UIDL verwendet einen SHA-256-Hexdigest aus Benutzer, ursprünglicher Datenbank-ID und kanonischen Mailbytes. Das ist eine stabile **Kennung**, keine Passwortspeicherung und keine Verschlüsselung. Nach Löschen einer vorherigen Mail ändert sich zwar die Sitzungsnummer, aber nicht die UID der verbliebenen unveränderten Mail.

Mailzeilen werden auf CRLF normalisiert; der letzte Zeilenabschluss wird ergänzt, vorhandene leere Endzeilen bleiben erhalten. Alle Größen basieren auf den **kanonischen Bytes vor Dot-Stuffing**. Ein zusätzlicher Punkt verhindert, dass punktbeginnende Datenzeilen als Endmarke erscheinen. Die Protokoll-Endmarke wird getrennt gesendet.

## Tatsächlich ausgeführte Prüfungen

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.3 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.2 -v
```

**Serversuite: 15 Tests, OK. Clientsuite: 11 Tests, OK.** Die Serverprüfung verwendet als unabhängigen Client stdlib `poplib` und zusätzlich Rohsockets, nicht nur die eigene Clientimplementierung. Beide Prozesse wurden zusätzlich über ihre echte CLI gestartet; der Test prüft den Exitcode und den sauberen Prozessabschluss mit SIGINT.

Nachgewiesen sind:

- Alle vier Originalmails abrufbar; LIST-Größen entsprechen RETR-Bytes; CAPA, TOP, NOOP und UIDL funktionieren.
- Groß-/Kleinschreibung, byteweise gesendete Befehle sowie mehrere Befehle im selben Bytestrom.
- 255-Byte-Grenze, überlange Befehle, nacktes LF, ungültige Kodierung, falsche Argumentanzahl, fehlende/negative/ungültige Nachrichtennummern und Zustandsfehler.
- Passwortrückweisung (`alice123`), unbekannter Benutzer, PASS ohne USER und ungültige USER/PASS-Sequenzen.
- Dot-Stuffing auf dem **Rohdraht** für `.first`, `.` und `..third`; unabhängiges Entstuffing durch poplib. UTF-8-Inhalte werden nach Byteanzahl gezählt.
- DELE bleibt vor QUIT unbestätigt, RSET stellt alles wieder her, QUIT entfernt genau die markierten Datensätze. UID bleibt bei anschließender Neunummerierung stabil.
- Client-Absturz simuliert durch Schließen ohne QUIT: keine Löschung, Lock wieder frei. Zusätzlich echter Server-Timeout und Serverstopp bei offener Sitzung: jeweils Rollback.
- Gleichzeitige, barrierensynchronisierte Sitzungen für Alice und einen synthetischen Bob; während beide geöffnet sind, wird ein dritter Alice-Login mit IN-USE abgewiesen. Bob und ein leeres Postfach existieren **nur in frischen Testinstanzen im Speicher**; keine Änderung an Originaldateien.

Die echte CLI lieferte die Größenliste `[(1, 184), (2, 185), (3, 154), (4, 164)]`, rief Nachricht 1 mit Betreff `Welcome to the POP3 lab` ab und meldete `QUIT bestätigt; Verbindung geschlossen.` Vollständiger Auszug: [`../ue3.2/antwort.md`](../ue3.2/antwort.md).

## GUI-Integration: stabile Server-API

Öffentlicher Einstiegspunkt in `pop3_server.py`:

```python
create_server(host="127.0.0.1", port=11110, database=None, client_timeout=600)
```

Rückgabe: bereits gebundene `POP3Server`-Instanz. `database=None` lädt das Originalkonto; für Tests kann eine frische Originalinstanz mit zusätzlichen ausschließlich synthetischen Benutzern injiziert werden. Benötigter Datenbankvertrag: `authenticate(user, password) -> bool`, `get_messages(user) -> mutable list` von eindeutigen `id`-/`raw`-Datensätzen. Externe Datenbankänderungen während einer Sitzung müssen dieselben Maildrop-Sperren respektieren; die Übungsdatenbank hat keinen separaten Zusteller.

Integration (schematischer API-Aufruf, kein zusätzliches Programm):

```python
# Modul über sys.path oder importlib aus ue3.3/pop3_server.py importieren.
server = create_server("127.0.0.1", 0)
worker = threading.Thread(target=server.serve_forever,
                          kwargs={"poll_interval": 0.1})
worker.start()
host, port = server.server_address
# GUI zeigt host/port an bzw. verbindet einen echten Mailclient damit.
# Nach dem GUI-Lauf aus einem ANDEREN Thread als serve_forever stoppen:
server.shutdown()
server.server_close()
worker.join()
```

`serve_forever()` blockiert und gehört daher nicht in den GUI-Ereignisthread. `shutdown()` muss aus einem anderen Thread aufgerufen werden; anschließend schließt `server_close()` offene Verbindungen und wartet auf Worker. Erst starten und danach stoppen; shutdown auf einer nie gestarteten Instanz ist kein gültiger Lebenszyklus. Alternativ darf die GUI den Server als CLI-Unterprozess starten und ihm zum geordneten Stoppen SIGINT senden; genau dieser Weg ist in den Tests ausgeführt worden.

### Einstellungen für einen tatsächlichen Mailclient

| Feld | Wert |
|---|---|
| Kontotyp | POP3, nicht IMAP |
| Adresse als Anzeige-/Kontofeld | `alice@example.com` (nur Testidentität) |
| Eingangsserver | `127.0.0.1` |
| Port | `11110` bzw. tatsächlich ausgegebener dynamischer Port |
| Verbindungssicherheit | Keine |
| Authentifizierung | Passwort, normal / USER-PASS |
| Benutzername | `alice` (nicht die ganze E-Mail-Adresse) |
| Passwort | `secret` |
| Nachrichten auf Server belassen | Für wiederholte Screenshots empfohlen |

Bei Thunderbird die Warnung zur unverschlüsselten Verbindung **nur für dieses Loopback-Testkonto** bestätigen. Dieser Server bietet keinen SMTP-Ausgang; nicht versuchen, damit Mails zu versenden. Eine gegebenenfalls erforderliche SMTP-Kontoeinstellung ist von der reinen Empfangsprüfung getrennt und darf nicht auf ein echtes Konto umgebogen werden. Abrufen muss die vier Originalbetreffzeilen in der Inbox anzeigen. UIDL und TOP unterstützen dabei die übliche Mailclient-Nachrichtenprüfung.

**Echter GUI-Nachweis:** Thunderbird 158.0 hat alle vier Originalmails per POP3 abgerufen, in der Inbox angezeigt und die Welcome-Mail geöffnet. Der [GUI-Bericht mit Screenshots](gui_testbericht.md), [Verifikationsdaten](screenshots/verifikation.json) und die [zeilenweise Erklärung](erklaerung_gui.md) liegen bei. Zusätzlich wurde der eigene Client gegen die echte Go-Referenzimplementierung getestet; siehe [Gesamtprotokoll](../testprotokoll_blatt03.md). Es wurden nur synthetische lokale Testkonten benutzt.

## Grenzen

Kein TLS/STLS, SASL/APOP, SMTP, produktives Authentifizierungssystem, Datenbank-Persistenz oder Ressourcenmanagement gegen beliebig viele Verbindungen. Die Zahl offener Clients entspricht der Zahl Worker-Threads und ist für einen Lehrserver gedacht. Standardmäßig bindet der Server nur Loopback; andere Bind-Adressen verlangen das bewusste Flag `--allow-remote-plaintext`. Es aktiviert keinen Schutz.

Die Originaldatenbank ist **In-Memory**. Bestätigte Löschungen gelten nur während des aktuellen Serverprozesses; ein Neustart erzeugt die ursprünglichen vier Mails wieder. „Absturz-Rollback“ bezieht sich auf den Ausfall/Abbruch einer Sitzung vor QUIT, nicht auf dauerhafte Transaktionssicherheit eines abstürzenden Datenbankprozesses. Keine vollständige Produktionsserver-Konformitäts- oder Sicherheitssuite wird behauptet.

Dateien: `pop3_server.py` (Server/CLI/API), `test_pop3_server.py` (TCP-/poplib-/Parallelitäts-/CLI-Tests), `antwort.md` (dieser Bericht). Datei-, Funktions- und Codezeilen-Erklärung: [`../erklaerung_pop3.md`](../erklaerung_pop3.md).

Quellen, abgerufen 2026-10-19: [RFC 1939 §§ 3–7, 11, 13](https://www.rfc-editor.org/rfc/rfc1939.html), [RFC 2449 §§ 3–6 und 8.1.2](https://www.rfc-editor.org/rfc/rfc2449.txt). IMAP-Vergleich anhand [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051.html) in [`../ue3.1/antwort.md`](../ue3.1/antwort.md).
