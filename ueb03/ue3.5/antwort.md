# Ü 3.5 – HTTP/1.0, Request-Threads und zentraler Logger

**KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent, OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription).
**Datum:** 2026-10-19.
**Anfrage:** Implementiere und teste Ü3.4 HTTP/0.9 single-thread und Ü3.5 HTTP/1.0 Multi-thread samt persistent connections und zentralem 5s-Logger vollständig im gemeinsamen Repo; mit stdlib-Unittests und didaktischer Erklärung jeder Datei/Codezeile.

## CLI

Aus dem Repository-Hauptverzeichnis; das Original-Testverzeichnis liegt entpackt unter `ueb03/Angabe/document_root`:

```bash
python3 ueb03/ue3.5/server.py ueb03/Angabe/document_root --port 8080
python3 ueb03/ue3.5/server.py ueb03/Angabe/document_root --port 8080 --log-file ueb03/ue3.5/access.jsonl
```

Die Befehle sind alternative Starts, nicht gleichzeitig auszuführen. Das erste Beispiel schreibt Logs auf stdout; das zweite hängt JSON-Zeilen an die angegebene Datei an. Das Startbanner steht immer auf stdout.

| Option | Standard | Bedeutung |
|---|---:|---|
| `document_root` | Pflicht | Basisverzeichnis, dessen `index.html` und Dateien ausgeliefert werden |
| `--host` | `127.0.0.1` | IPv4-Bindadresse, bewusst nur lokal |
| `--port` | **80** | TCP-Port; 8080 für Tests ohne besondere Berechtigung, 0 für freie Testportwahl |
| `--timeout` | 5 | Endliche positive Sekunden; absolute Frist pro Request und Timeout pro Schreiboperation |
| `--max-requests` | 100 | Maximalzahl der Requests auf derselben Verbindung |
| `--max-clients` | 64 | Maximal gleichzeitig betreute Verbindungen |
| `--log-file` | stdout | Optionaler Append-Pfad für JSONL-Zugriffsprotokoll |

Python ab 3.10, POSIX/Linux und IANA-Zeitzonendaten für `Europe/Vienna` erforderlich; ausschließlich Standardbibliothek. Ü3.5 lädt die sichere `open_resource`-Funktion aus `../ue3.4/server.py` über einen von `__file__` abgeleiteten Pfad. **Beide Aufgabenverzeichnisse gehören zusammen**, auch wenn die Starts aus jedem Arbeitsverzeichnis möglich sind.

Beenden mit **Strg+C oder SIGTERM**: Annahme neuer Clients stoppen, aktive Sockets herunterfahren, sämtliche Reader und Request-Worker beenden, anschließend den Logger mit einem Queue-Sentinel stoppen und seinen Restpuffer flushen. Normale Signale werden in einen gesetzten Stop-Event umgesetzt. SIGKILL oder Stromausfall können naturgemäß keinen geordneten Flush garantieren.

## HTTP/1.0 und persistente Verbindungen

Jede Antwort auf einen HTTP/1.x-Request beginnt mit `HTTP/1.0 <Status> <Grund>` und enthält einen HTTP-Date-Header in GMT, **Content-Length in Bytes**, Content-Type sowie ein explizites `Connection: close` oder `Connection: keep-alive`. Die Header enden mit CRLF CRLF. GET liefert unveränderte Dateibytes, HEAD dieselbe Längeninformation ohne Body. Verzeichnisse liefern `index.html`, ohne Listing. MIME-Typen werden aus dem tatsächlich ausgewählten Dateinamen ermittelt, daher auch für `/unterverzeichnis` korrekt als HTML.

HTTP/1.0 schließt standardmäßig nach einer Antwort. Nur ein Request mit `Connection: keep-alive` hält offen. Enthält dieselbe Connection-Liste auch `close`, gewinnt `close`. Beim Requestlimit wird die letzte Antwort ausdrücklich mit `Connection: close` markiert. Bereits gepufferte weitere Requests werden danach nicht mehr verarbeitet.

Beispiel für zwei sequenzielle oder direkt hintereinander gepipelinete Requests:

```text
GET / HTTP/1.0\r\n
Connection: keep-alive\r\n
\r\n
HEAD /images/logo.gif HTTP/1.0\r\n
Connection: close\r\n
\r\n
```

Die Schreibweise zeigt die Steuerzeichen als sichtbare Escape-Sequenzen. Tatsächlich werden CRLF-Bytes gesendet. Das dauerhafte TCP-Lesepufferobjekt trennt Requests an CRLF CRLF und bewahrt nachfolgende Bytes auf. Der Client erkennt jeden Antwortkörper an Content-Length, **nicht** am Verbindungsende; bei HEAD wird trotz positivem Content-Length kein Body gelesen.

### HTTP/0.9-Rückwärtskompatibilität und gültige Header

[RFC 1945 §3.1 und §4.1](https://www.rfc-editor.org/rfc/rfc1945#section-3.1) verlangen die Unterstützung des älteren Simple-Request. Deshalb erkennt der Reader bereits die vollständige erste Zeile `GET /pfad\r\n` **ohne Versionsfeld**; er wartet dabei weder auf eine zweite Leerzeile noch auf EOF. Auch fragmentierte Zeilen und getrennt eintreffende CR-/LF-Bytes funktionieren. Das unveränderliche `Request`-Objekt markiert diesen Fall mit `legacy=True` (Standard: `False`).

Die Simple-Response besteht ausschließlich aus den unveränderten Dateibytes: **keine Statuszeile, keine Header, kein Keep-alive**, danach Close. Fehlende Dateien, verbotene Pfade und erkannte fehlerhafte Simple-Requests schließen ohne Antwortbytes; ihr interner Status erscheint nur im Log. Bereits mitgelieferte Header-/Pipelinebytes hinter einer Simple-Request-Zeile werden wie in Ü3.4 abgewiesen. Später eintreffende Bytes begründen keine weitere Anfrage, weil die Verbindung ohnehin endet. Ein explizites `HTTP/0.9`-Versionsfeld ist dagegen kein Simple-Request und erhält weiterhin eine gerahmte 505-Antwort. HTTP/1.0-/1.1-Zeilen bleiben bis CRLF CRLF unvollständig; es gibt keinen stillen Downgrade.

[RFC 1945 §2.2](https://www.rfc-editor.org/rfc/rfc1945#section-2.2) erlaubt ISO-8859-1-TEXT in Headerwerten. Der Parser dekodiert deshalb den Block verlustfrei mit Latin-1 und prüft die Requestzeile einschließlich URI separat auf ASCII. Headernamen bleiben ASCII-Token; verbotene Steuerzeichen und DEL bleiben Fehler, HTAB in Headerwerten ist erlaubt. UTF-8-Dateinamen werden weiterhin als Prozentkodierung in der ASCII-URI übertragen.

Nach [RFC 1945 §4.2](https://www.rfc-editor.org/rfc/rfc1945#section-4.2) werden wiederholte **kommalistenfähige** Felder in Empfangsreihenfolge mit `, ` verbunden: `Accept`, `Accept-Charset`, `Accept-Encoding`, `Accept-Language`, `Allow`, `Pragma` und die Persistenzerweiterung `Connection`. Headernamen sind dabei case-insensitiv. `close` gewinnt auch über mehrere Connection-Zeilen hinweg, unabhängig von deren Reihenfolge. **Host, Content-Length und andere nicht ausdrücklich freigegebene doppelte Felder werden weiterhin abgelehnt**; Transfer-Encoding bleibt verboten. Die Headeränderungen weichen weder Bodyframing noch Pfadsicherheit auf. Gefaltete Headerfortsetzungen werden in dieser bewusst strikten Untermenge weiterhin abgewiesen.

## „Jede Anfrage ein neuer Thread“ – wörtlich umgesetzt

- Hauptthread: `accept`, Zulassungsgrenze und Shutdown.
- Je Verbindung ein **Reader-Thread**, der die Requestgrenzen verwaltet und nachfolgende Bytes puffert.
- Für **jede einzelne Anfrage** ein **neues `threading.Thread`-Objekt als Request-Worker**. Auch Legacy-Requests, deren Fehler sowie der zweite und dritte Request derselben Verbindung bekommen jeweils neue Worker. Der Reader selbst erzeugt keine HTTP-Antwort.
- Der Reader wartet mit `worker.join()`, bevor er die nächste Antwort auf dieser Verbindung beginnen lässt. Dadurch bleiben Pipeline-Antworten in Request-Reihenfolge. Andere Verbindungen laufen unabhängig weiter.
- Ein einziger zusätzlicher **Logger-Thread** für alle Verbindungen.

Es ist ausdrücklich **kein** bloßer Thread-pro-Verbindung-Server, der dann alle Requests selbst abarbeitet. Pipeline bedeutet hier geordnetes Puffern und sequenzielle Bearbeitung pro Verbindung, nicht paralleles Antworten auf demselben TCP-Datenstrom. Standardmäßig begrenzen 64 Verbindungsslots die Anzahl gleichzeitig aktiver Reader und Worker; es gibt keinen unbegrenzt wachsenden Thread-Pool.

## Zentraler 5-Sekunden-Logger

Worker legen Datensätze in eine threadsichere `queue.Queue`. Ausschließlich der Logger schreibt und flusht die Zugriffseinträge. Er sammelt zwischen zwei monoton gemessenen 5-Sekunden-Terminen und gibt vorhandene Einträge gesammelt als JSONL aus. **Nicht** jeder einzelne Zugriff wird sofort ausgegeben. Leere Intervalle erzeugen keine künstlichen Zugriffe. Der Shutdown-Sentinel bewirkt auch vor Ablauf des nächsten Intervalls einen abschließenden Flush.

Jeder Datensatz enthält:

- `timestamp`: Zeitpunkt nach der Bearbeitung, ISO-8601 mit Millisekunden und tatsächlichem UTC-Offset für **Europe/Vienna**, inklusive Sommer-/Winterzeit;
- `method`: Request-Typ, z.B. GET oder HEAD; bei nicht ausreichend lesbaren Requests `INVALID`;
- `ip` und `port`: IP-Adresse und TCP-**Quellport des Clients**, nicht der Serverport;
- zusätzlich `status` und `worker` zur Diagnose und zum Test verschiedener Request-Threads. Bei abgebrochener Übertragung kann der Diagnose-Status 500 sein, obwohl zuvor bereits andere Statusbytes übertragen wurden; er ersetzt kein Wire-Capture.

Die Request-Verarbeitung wartet nicht auf die 5-Sekunden-Ausgabe. Queue statt nebenläufiger direkter `print`-Aufrufe verhindert vermischte Zugriffszeilen. Ein Lock schützt die Sets aktiver Verbindungen und Reader; ein `BoundedSemaphore` begrenzt die Clientzahl. Die Logqueue ist nicht begrenzt: Bei dauerhaft blockiertem Logziel oder extremem Traffic ist dies kein produktionsreifer Schutz gegen Speicherverbrauch.

## Fehler und bewusst beschränkter Umfang

- 400: ungültige Requestsyntax/Header, doppelte nicht kommalistenfähige Header, fehlender Host bei einem HTTP/1.1-Request, Request-Bodies oder Transfer-Encoding.
- 403: Traversal, Symlinks, Spezialdateien, verbotene oder nicht dekodierbare Dateipfade.
- 404: Datei oder Verzeichnisindex fehlt.
- 405 plus `Allow: GET, HEAD`: syntaktisch gültige, aber nicht unterstützte Methode.
- 408: Requestfrist überschritten, auch wenn ein Client tröpfchenweise weiter sendet.
- 414: Requestzeile über 8192 Bytes; 431: Headerblock über 16384 Bytes oder über 100 Headerfelder.
- 505: nicht unterstützte HTTP-Version.

HTTP/1.x-Fehlerantworten haben ebenfalls gültiges Framing; beim erkannten Legacy-Fall bleibt die Leitung bei Fehlern dagegen ohne Antwortbytes. Ein bereits vollständig geparster HTTP/1.x-Request darf mit 403/404/405 seine Keep-alive-Verbindung behalten; Parserfehler und Timeout schließen ausdrücklich. GET und HEAD unterstützen **keinen Requestbody**. Content-Length fehlt oder besteht ausschließlich aus Nullziffern; alle anderen Werte werden abgewiesen, ohne unbeschränkte Integer-Konvertierung. Chunked und Transfer-Encoding werden nicht unterstützt. Diese strenge Regel verhindert, dass ein ungelesener Body versehentlich als nächste Anfrage gilt.

Für heutige Browser werden einfache **HTTP/1.1-Requestzeilen mit Host-Header** zusätzlich akzeptiert; die Antwort und Persistenzregeln bleiben **HTTP/1.0**. Dies ist **keine vollständige HTTP/1.1-Implementierung**: kein Chunking, keine automatische 1.1-Persistenz, keine Range-, Cache-, TLS-, Proxy- oder Expect/Continue-Unterstützung. Eine Timeoutantwort auf einer vollständig inaktiven, bereits verbundenen Leitung wird als `INVALID` protokolliert; EOF ohne angefangenes Requestfragment erzeugt dagegen keinen Zugriff.

Sichere Dateiöffnung, reguläre Dateien, URL-Dekodierung und Symlink-Abwehr werden direkt aus Ü3.4 übernommen. Der Betreiber sollte den DocumentRoot während des Tests nicht ändern. Bei wachsender Datei wird höchstens die zuvor angekündigte Länge gesendet; bei verkürzter Datei wird die Verbindung abgebrochen statt die nächste Antwort mitten im Body zu beginnen.

## Wirklich ausgeführte Tests

```bash
python3 -m unittest discover -s ueb03/ue3.5 -v
```

**Verifiziert: 27 Tests in Ü3.5, alle erfolgreich.** Zusätzlich wurden alle **10 Tests aus Ü3.4** erneut erfolgreich ausgeführt: **37 HTTP-Tests insgesamt**. Der Logger-Test wartet tatsächlich auf die **reale 5-Sekunden-Frist**, nicht nur auf eine verkürzte Testkonstante.

Abgedeckt: GET/HEAD für Binär- und Indexdateien, leere Dateien, Content-Length/MIME, sequenzielle Keep-alive-Requests, HEAD-Fehlerframing, drei gepipelinete Requests mit drei verschiedenen Request-Workern, explizites Close und Requestlimit, Fragmentierung, 404/405/403, Traversal/Symlinks/FIFO, ungültige und doppelte Header, negative/positive/nichtnumerische und sehr große Content-Length-Werte, Header-/Zeilenlimits, HTTP/1.1-Kompatibilitäts-Untermenge, EOF und Timeout, Slowloris trotz fortlaufender Bytes, 16 parallele Abrufe trotz eines blockierten Readers, Clientlimit und anschließende Erholung, Shutdown aktiver Verbindungen und Logflushing, CLI-Fehlereingaben, echte CLI-Unterprozesse mit TCP und **SIGINT sowie SIGTERM**. Die drei Dateien der unveränderten Original-ZIP werden ebenfalls bytegenau per TCP geprüft.

Die **acht neuen Regressionstestmethoden** prüfen zusätzlich Legacy-Dateien/Index/Binärdaten/Close ohne Half-close, echte Fragmentierung mit ausbleibender vorzeitiger Antwort, stille Legacy-Datei-/Syntax-/Sicherheitsfehler, die Trennung von versionsloser und explizit versionierter Syntax einschließlich Übergang nach einem persistenten Request, eigene Legacy-Worker mit echten Loggerdatensätzen, Latin-1-TEXT bei weiterhin reiner ASCII-Requestzeile, wiederholte Listenheader mit Close-Vorrang in beiden Reihenfolgen sowie unverändert abgewiesene Steuerzeichen, doppelte Host-/Content-Length-Felder und Framing-Angriffe mit angehängter Folgeanfrage. Alle Antworten stammen aus echten lokalen TCP-Verbindungen, nicht aus Mock-Antworten.

## Browserbelege und Dateien

Die echten lokalen Läufe sind in [`../integration_ergebnis.json`](../integration_ergebnis.json) dokumentiert: **Chromium 156.0.8078.4 und Firefox 157.0** zeigen über den Ü3.5-Server den Titel `Test`, den Text `It works...!` sowie beide geladenen Bilder. Für `index.html`, `images/logo.gif` und `images/TechnikErleben.png` enthält der Nachweis die tatsächlichen Bytezahlen und SHA-256-Werte. Die Screenshots zeigen links das Alpen-Adria-Universitätslogo und daneben „TECHNIK studieren & erleben“:

- [Chromium: HTTP/1.0-Testseite](../browser_nachweise/chromium_http10.png)
- [Firefox: HTTP/1.0-Testseite](../browser_nachweise/firefox_http10.png)

Diese Browserbelege stammen aus dem bereits ausgeführten Integrationslauf; die oben genannten Socket-/Logger-Regressionstests wurden nach der RFC-Korrektur erneut ausgeführt. Die neuen Legacy-Fälle werden ausdrücklich durch Sockettests belegt, nicht durch eine behauptete HTTP/0.9-Browserunterstützung. Die Fehleraufnahmen für den strikt versionslosen **Ü3.4**-Server im selben Nachweis sind davon getrennte, tatsächlich beobachtete Browser-Kompatibilitätsfehler.

- `server.py`: HTTP/1.0-Server, Request-Reader/-Worker, Logger und CLI.
- `test_http10.py`: stdlib-Tests mit echter TCP-Kommunikation und echten Unterprozessen.
- `antwort.md`: diese Bedienungs- und Entscheidungsdokumentation.
- [`../erklaerung_http.md`](../erklaerung_http.md): Grundlagen, Architektur und **zeilenweise Erklärung aller vier Python-Dateien**, einschließlich Testcode.

Keine Moodle-Abgabe, Commits, Pushes oder Änderungen an einer Aufgabenqueue durch diesen Teilauftrag.
