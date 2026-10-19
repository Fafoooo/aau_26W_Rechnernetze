# Ü 3.2 – POP3-Client mit Python-Sockets

> **KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent; Modell: OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). **Datum:** 2026-10-19. **Auftrag:** Einfachen POP3-Socket-Client mit Anmeldung, vollständigem LIST, einem RETR und sauberem QUIT implementieren; echte TCP-, Fehler-, Fragmentierungs- und Integrationstests ausführen.

## Implementierung und Aufruf

`pop3_client.py` verwendet ausschließlich die Python-Standardbibliothek. Die eigene Implementierung importiert **kein poplib**: Verbindung über `socket.create_connection`, vollständiges Senden mit `sendall`, gepuffertes Lesen über `socket.makefile("rb")`. `poplib` wird ausschließlich in den unabhängigen Servertests eingesetzt.

Start im Repo `/home/ubuntu/uni/aau_26W_Rechnernetze` (Terminal 1):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.3/pop3_server.py --host 127.0.0.1 --port 11110
```

Client (Terminal 2; nur dieses künstliche Testpasswort darf als Argument sichtbar sein):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.2/pop3_client.py --host 127.0.0.1 --port 11110 --user alice --password secret --message 1
```

Ohne `--password` fragt der Client das Passwort verdeckt ab:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.2/pop3_client.py --port 11110 --user alice
```

**Korrektes Originalkonto: `alice` / `secret`.** `Angabe/SampleDataBase.py` enthält nur dieses Konto. Die Beispiele im Original-README verwenden widersprüchlich `alice123`; dieses Passwort ist laut tatsächlichem Datensatz **falsch**. Originaldateien wurden nicht berichtigt oder verändert.

Der erfolgreiche Normalablauf ist:

```text
TCP verbinden -> +OK-Begrüßung lesen -> USER alice -> PASS secret
             -> LIST -> alle Listeneinträge bis Punkt lesen
             -> RETR 1 -> Nachricht bis Punkt lesen und entstuffen
             -> QUIT -> +OK lesen -> Reader und Socket schließen
```

Ein leeres LIST wird korrekt akzeptiert; es folgt dann kein ungültiges `RETR 1`, sondern direkt QUIT. Bei einem Protokoll-/Transportfehler wird abgebrochen; ein Ausnahmefall wird nicht durch QUIT versehentlich als UPDATE bestätigt. Der Client selbst sendet nie DELE. Bei regulärem Abschluss erfolgt QUIT auch dann, wenn man die API als `with POP3Client(...)` verwendet.

## Antwortverarbeitung und Fehler

- Ein TCP-Paket ist keine vollständige POP3-Antwort. `readline` puffert Fragmentierung und mehrere zusammen eintreffende Zeilen.
- Statuszeilen benötigen CRLF und sind auf 512 Bytes inklusive CRLF begrenzt. `+OKX` ist kein gültiges `+OK`.
- Bei `-ERR` wird sofort `POP3Error` ausgelöst, auch wenn für den Befehl sonst eine mehrzeilige Antwort erwartet wäre. Der Client wartet dann nicht auf einen nicht existierenden Terminator.
- Bei erfolgreichem LIST/RETR wird die einzelne Punktzeile als Ende erkannt; `..` am Anfang einer Datenzeile wird zu `.`. CRLF wird beim Aufbau der Mail wiederhergestellt.
- EOF vor der Punktzeile, nacktes LF, ungültiger Status und falsches Stuffing werden als `ProtocolError` behandelt. Der Transport wird geschlossen, weil die Synchronität nicht mehr gewährleistet ist.
- CR/LF, Steuerzeichen und Nicht-ASCII in Befehlen werden lokal abgewiesen; ebenso Befehle über 255 Bytes. Das verhindert insbesondere eine Befehlsinjektion über Benutzername/Passwort.
- LIST-Einträge werden auf positive Nummern, nichtnegative Größen und doppelte Nummern geprüft. RETR erwartet eine positive Ganzzahl.
- Schutzgrenzen für das Lehrprogramm: maximal 1 MiB pro Datenzeile und 20 MiB pro mehrzeiliger Antwort. Diese lokalen Ressourcenlimits sind keine Behauptung allgemeiner POP3-Mailgrößenlimits.
- CLI-Fehler liefern Exitcode 1 und einen Fehlertext, regulärer Abschluss Exitcode 0. Der Client protokolliert das Passwort nicht; `--password` ist dennoch in der Prozesskommandozeile sichtbar und daher nur für künstliche Labordaten vorgesehen.

Standardziel ist Loopback. Ein nichtlokaler Zielname/eine nichtlokale Ziel-IP erfordert ausdrücklich `--allow-remote-plaintext`. Das Flag aktiviert **keine** Verschlüsselung. Es darf nur mit einem dafür vorgesehenen Testserver ohne vertrauliche Daten verwendet werden. Die Realimplementierungs-/GUI-Erprobung und weitere externe Serverprüfung werden separat dokumentiert; die folgenden Ergebnisse behaupten keinen externen Test.

## Tatsächlich ausgeführte Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.2 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.3 -v
```

- **Client: 11 Tests, OK.** Unabhängiges skriptgesteuertes TCP-Gegenüber prüft die tatsächlich übertragenen Befehle. Antworten werden byteweise geschrieben, einschließlich getrenntem CR und LF; der Test setzt keine TCP-Paketgrenzen voraus.
- Geprüft: Anmeldung/LIST/RETR/QUIT, mehrere LIST-Zeilen, Dot-Stuffing einschließlich echter Punktzeile, wiederverwendbare Sitzung nach `-ERR`, falsches Passwort ohne Passwortausgabe, fehlerhafte Begrüßung, EOF in Daten, ungültiges Stuffing, beschädigte/doppelte LIST-Einträge, lokale Injektions- und Längenprüfung, Abbruch ohne QUIT, QUIT-Fehler und leerer Maildrop.
- Integration gegen den eigenen Server prüft LIST-Größe gegen die tatsächlich abgerufenen Bytes **aller vier** Nachrichten. Ein zusätzlicher Client-Unterprozess prüft die CLI.
- Die Serversuite startet darüber hinaus **Server und Client als separate echte Prozesse**, liest den gebundenen dynamischen Port aus der Serverausgabe und prüft danach denselben Server unabhängig mit stdlib `poplib`.

Reale Ausgabe dieses separaten CLI-Laufs (die Textkonsole stellt CRLF als gewöhnlichen Zeilenwechsel dar):

```text
+OK RN POP3 ready (local plaintext lab)
LIST (Nummer, Oktette): [(1, 184), (2, 185), (3, 154), (4, 164)]
RETR 1:
From: bob@example.com
To: alice@example.com
Subject: Welcome to the POP3 lab
Date: Tue, 22 Sep 2026 09:00:00 +0200

Hello Alice,

Welcome to the POP3 laboratory.

Best,
Bob
QUIT bestätigt; Verbindung geschlossen.
```

## Dateien und API

- `pop3_client.py`: Implementierung und CLI. Öffentliche API: `POP3Client(host, port, timeout)`, `login(user, password)`, `list_messages() -> list[tuple[int, int]]`, `retrieve(number) -> bytes`, `command(text, multiline=False)`, `quit()`, `close()` sowie Kontextmanager.
- `test_pop3_client.py`: unabhängig antwortendes Socket-Testgegenüber und echte Server-/CLI-Integration. Keine Fremdpakete erforderlich.
- `antwort.md`: Ausführung, Ergebnisse und Grenzen.
- [`../erklaerung_pop3.md`](../erklaerung_pop3.md): didaktische Datei-, Funktions- und zeilenweise Codeerklärung.

Quellen: [RFC 1939 §§ 3–7, 11](https://www.rfc-editor.org/rfc/rfc1939.html), [RFC 2449 §§ 3–5](https://www.rfc-editor.org/rfc/rfc2449.txt), abgerufen 2026-10-19. Theorie und IMAP-Vergleich stehen in [`../ue3.1/antwort.md`](../ue3.1/antwort.md).
