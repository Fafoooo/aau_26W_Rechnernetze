# Ü 3.4 – HTTP/0.9 mit einem Thread

**KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription).
**Datum:** 2026-10-19.
**Anfrage:** Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 Multi-thread samt persistent connections und zentralem 5s-Logger vollständig im gemeinsamen Repo; mit stdlib-Unittests und didaktischer Erklärung jeder Datei/Codezeile.

## Start und Bedienung

Aus dem Repository-Hauptverzeichnis; die bereitgestellten Testdateien liegen bereits entpackt unter `ueb03/Angabe/document_root`:

```bash
python3 ueb03/ue3.4/server.py ueb03/Angabe/document_root --port 8089
```

- Python ab 3.10 und POSIX/Linux; ausschließlich Standardbibliothek. Keine Installation erforderlich.
- Pflichtparameter: DocumentRoot. `--port` hat den geforderten Standard **80**; zum Testen **8089** verwenden. Port 80 benötigt unter Linux gewöhnlich erhöhte Berechtigung oder eine passende Capability. Den Lernserver nicht als root öffentlich bereitstellen.
- Standardmäßig nur `127.0.0.1`; `--host 0.0.0.0` würde ihn auf allen IPv4-Schnittstellen erreichbar machen.
- `--port 0` wählt einen freien Testport, den der Server im Startbanner ausgibt.
- `--timeout 5` begrenzt die gesamte Anfrage-Lesephase; beim Senden gilt ein Socket-Timeout pro Schreiboperation.
- Beenden: **Strg+C**, ebenfalls sauber bei **SIGTERM**. Alle Sockets werden durch Kontextmanager geschlossen.
- `python3 ueb03/ue3.4/server.py --help` zeigt die vollständige CLI.

`nc` (falls lokal installiert) eignet sich als Rohclient:

```bash
printf 'GET /\r\n' | nc 127.0.0.1 8089
printf 'GET /images/logo.gif\r\n' | nc 127.0.0.1 8089 > /dev/null
```

Diese Befehle sind **Anleitungen**, keine zusätzlichen behaupteten Testausführungen. `curl --http0.9` erlaubt lediglich den Empfang einer HTTP/0.9-Antwort: curl sendet damit nicht automatisch eine echte headerlose HTTP/0.9-Anfrage. Daher sind die Socket-Unittests der verlässliche Protokollnachweis.

## Protokoll und Entscheidungen

Ein gültiger Request lautet exakt `GET /pfad\r\n`: zwei durch ein einzelnes Leerzeichen getrennte ASCII-Felder, **kein Versionsfeld, keine Header**. Fragmente einer TCP-Übertragung werden bis CRLF gesammelt. HTTP/0.9 kennt nur GET; HEAD und HTTP/1.x-Anfragen werden nicht als angeblich gültige 0.9-Anfragen umgedeutet.

Die Antwort enthält **ausschließlich die unveränderten Dateibytes**. Es gibt keine Statuszeile, keinen Content-Type und keinen Content-Length. Das Ende der TCP-Verbindung begrenzt die Antwort. Verzeichnisse mit und ohne abschließenden Slash liefern ihre `index.html`, ohne Redirect oder Verzeichnislisting. URL-Prozentkodierung wird einmal streng als UTF-8 dekodiert; Query-Parameter werden nicht als Teil des Dateinamens behandelt.

Der aufrufende Hauptthread führt `accept → Request lesen → Datei öffnen → senden → schließen` vollständig aus, bevor er den nächsten Client bearbeitet. `server.py` startet **keinen** zusätzlichen Thread. Die Testprogramme benutzen dagegen Hintergrundthreads, damit sie gleichzeitig Client und Server innerhalb eines Testprozesses betreiben können. Das verändert nicht die Serverarchitektur.

Fehler bei Requestprüfung, Pfadauflösung, Dateiöffnung oder Timeout **vor dem ersten Senden** schließen die Verbindung ohne ein einziges Antwortbyte. Bei einer ungültigen, überlangen Anfrage kann das Betriebssystem wegen ungelesener Eingangsdaten TCP-RST statt FIN senden; auch das ist eine Schließung ohne HTTP-Rückmeldung. Scheitert eine bereits laufende Dateiübertragung, kann der Server schon gesendete Bytes nicht zurücknehmen: Er schließt ohne zusätzlichen Fehlertext.

## Grenzen und Schutzmaßnahmen

- Höchstens 8192 Bytes Requestzeile und eine absolute Lesefrist gegen unbegrenztes Warten/Slowloris. Ein Client blockiert bis dahin absichtlich alle anderen; genau das demonstriert single-thread.
- `..`, NUL/Steuerzeichen, Backslash, fehlerhafte Prozentfolgen und ungültiges UTF-8 werden abgewiesen.
- `openat` über `os.open(..., dir_fd=...)` mit `O_NOFOLLOW` folgt **keinem Symlink**, auch nicht bei Zwischenverzeichnissen oder `index.html`. Prüfung und Öffnung fallen nicht als unsichere `resolve`-/`open`-Sequenz auseinander.
- Nur reguläre Dateien. `O_NONBLOCK` verhindert das Blockieren bereits beim Öffnen einer FIFO; danach wird sie abgelehnt.
- Das bewusst vom Betreiber angegebene DocumentRoot wird beim Start aufgelöst. Es ist kein allgemeiner Sicherheits-Sandboxserver: Hardlinks, Dateiveränderungen durch andere lokale Benutzer, Netzwerkverschlüsselung, Authentifizierung und Rate-Limiting sind nicht Gegenstand der Übung.
- Fehlerausgabe beim **Programmstart** geht an stderr; das ist keine HTTP-Rückmeldung an einen Client.

## Ausgeführte Tests

```bash
python3 -m unittest discover -s ueb03/ue3.4 -v
```

**Verifiziert: 10 Tests, alle erfolgreich** (letzter Entwicklungsdurchlauf: 2,273 s). Untertests erweitern die geprüften Fälle, werden von unittest aber nicht als eigene Testmethoden gezählt.

Getestet wurden bytegenaue Binärübertragung, headerlose Antworten, Root-/Unterverzeichnisindex und leere Dateien, Prozentkodierung/Query, fehlende Dateien, Traversal und Symlinks, FIFO, ungültige Requests, Fragmentierung, vorzeitiges EOF, sequenzielle Bedienung zweier Clients, CLI-Validierung sowie ein echter CLI-Unterprozess mit TCP-Abruf und sauberem SIGTERM-Ende. Die ZIP-Integrität wurde mit `ZipFile.testzip()` geprüft. Die drei enthaltenen Originaldateien `index.html`, `images/logo.gif`, `images/TechnikErleben.png` werden aus einer **temporären, sicheren Testkopie** per Socket abgerufen und bytegenau mit der ZIP verglichen. Die Originale bleiben unverändert.

## Browserbefund: ehrlich getrennt

Die Aufgabe wurde mit **Chromium 156.0.8078.4** und **Firefox 157.0** tatsächlich getestet. Beide zeigen die Seite dieses strikten HTTP/0.9-Servers **nicht**: Chromium meldet `ERR_EMPTY_RESPONSE`, Firefox im Navigationsaufruf `NS_ERROR_NET_RESET` (sichtbare Fehlerseite `NS_ERROR_NET_EMPTY_RESPONSE`). Die echten [Screenshots und der Bericht](../testprotokoll_blatt03.md) sowie [Rohdaten](../integration_ergebnis.json) liegen bei. Moderne Browser senden HTTP/1.x-Anfragen, die dieser Server gemäß seiner strikten alten Syntax ohne Antwort schließt. Das ist erwartete Protokollinkompatibilität, kein Hinweis auf beschädigte GIF-/PNG-Dateien. Die korrekte headerlose Übertragung aller Originaldateien ist separat durch echte HTTP/0.9-Sockettests belegt. Der ausgebaute Ü3.5-Server zeigt dieselbe Seite samt beiden Bildern in beiden Browsern korrekt an.

## Dateien und Erklärung

- `server.py`: ausführbarer HTTP/0.9-Server; seine sichere Dateiöffnung wird auch in Ü3.5 benutzt.
- `test_http09.py`: selbstständige stdlib-Testdatei mit lokalen TCP- und CLI-Tests; temporäre Daten werden automatisch entfernt.
- `antwort.md`: Bedienung, Protokollentscheidungen, verifizierte Tests und tatsächliche Browserbelege.
- [`../erklaerung_http.md`](../erklaerung_http.md): ausführliche Grundlagen, Ablauf und **jede physische Quelltextzeile aller vier Python-Dateien mit Erklärung**.

Keine Moodle-Abgabe, keine Commits und keine Pushes wurden durch diesen Teilauftrag ausgeführt.
