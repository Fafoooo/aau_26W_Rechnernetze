<!-- KI-Kennzeichnung: erstellt mit Hermes Agent / OpenAI gpt-6.1-sol; laut bereitgestelltem Laufkontext meldete hermes status „ChatGPT or Codex Subscription“. Datum: 2026-10-19. Auftrag: jede Zeile des fertigen integration_test.py erklären, reale Nachweise und Reproduktion dokumentieren; keinen Programmcode ändern. -->

# Erklärung des optionalen Integrationstests

## 1. Zweck und Abgrenzung

[integration_test.py](integration_test.py) prüft das Zusammenspiel fertiger Programme mit **echten Fremdimplementierungen**: Der eigene Socket-POP3-Client verbindet sich mit einem lokal gestarteten GoPop3Server; Chromium und Firefox laden die Original-Webseite vom eigenen HTTP/1.0-Server und versuchen anschließend einen Aufruf des strikt implementierten HTTP/0.9-Servers.

Ein erfolgreicher Integrationstest bedeutet hier ausdrücklich **nicht**, dass HTTP/0.9 im modernen Browser funktioniert. Der Test erwartet dessen Ablehnung. Die korrekte alte Anfrage `GET /\r\n` und die dazugehörige headerlose Dateiausgabe werden separat in [ue3.4/test_http09.py](ue3.4/test_http09.py) geprüft.

Die Produktivprogramme der Übung benötigen nur die Python-Standardbibliothek. Ausschließlich die optionalen Browserprüfungen benötigen Playwright und seine Browserdateien. Go ist nur zum lokalen Bauen des freiwilligen Fremdservers nötig. Der echte Thunderbird-Test ist ein **anderes Programm**, [ue3.3/gui_test.py](ue3.3/gui_test.py), und wird von `integration_test.py` nicht aufgerufen.

Alle Zeilen der hier erklärten Fassung wurden gelesen: **174 Zeilen**, SHA-256:

```text
d8c4a9771ffe83d88188d1d7015256c5d0a75678f446d57b3ec72735842c9a1f
```

Die folgenden Zeilenangaben beziehen sich ausschließlich auf diese Fassung. Leerzeilen trennen Blöcke und führen keine Operation aus.

## 2. Dateien und ihre Rolle

Alle lokalen Pfade in dieser Tabelle sind relativ zu `ueb03/`.

| Datei/Verzeichnis | Verwendung |
|---|---|
| [integration_test.py](integration_test.py) | Testtreiber; startet Prozesse, Serverthreads und Browser, prüft Ergebnisse und schreibt den Gesamtbericht. |
| [Angabe/document_root.zip](Angabe/document_root.zip) | Original-Testmaterial, wird bei jedem Browserlauf erneut geöffnet und in den vorgesehenen Ordner entpackt. |
| [Angabe/document_root/index.html](Angabe/document_root/index.html) | Originalseite mit Titel `Test`, zwei `img`-Elementen und `It works...!`; 162 Bytes. |
| [Angabe/document_root/images/logo.gif](Angabe/document_root/images/logo.gif) | Universitätslogo; 4.445 Bytes. |
| [Angabe/document_root/images/TechnikErleben.png](Angabe/document_root/images/TechnikErleben.png) | Grafik „TECHNIK studieren & erleben“; 27.065 Bytes. |
| [ue3.2/pop3_client.py](ue3.2/pop3_client.py) | Dynamisch importierte eigene Socket-Clientklasse `POP3Client`. |
| [ue3.4/server.py](ue3.4/server.py) | Dynamisch importierter sequenzieller HTTP/0.9-Server; akzeptiert bewusst keine moderne Versions-/Headeranfrage. |
| [ue3.5/server.py](ue3.5/server.py) | Dynamisch importierter HTTP/1.0-Server mit getrennten Request-Workern, eingeschränkter HTTP/1.1-Request-Kompatibilität und zentralem JSONL-Logger. |
| [integration_ergebnis.json](integration_ergebnis.json) | Bericht des vollständig erfolgreichen Laufs: Versionen, POP3-Ergebnis, Browserfehler, Dateigrößen/-Hashes und HTTP-Zugriffslog. Wird erst am Ende neu geschrieben. |
| [browser_nachweise/chromium_http10.png](browser_nachweise/chromium_http10.png) | Tatsächlich gerenderte Originalseite in Chromium. |
| [browser_nachweise/firefox_http10.png](browser_nachweise/firefox_http10.png) | Tatsächlich gerenderte Originalseite in Firefox. |
| [browser_nachweise/chromium_http09_fehler.png](browser_nachweise/chromium_http09_fehler.png) | Chromium-Fehlerseite nach dem HTTP/0.9-Versuch; in der vorliegenden Aufnahme ist `ERR_EMPTY_RESPONSE` sichtbar. |
| [browser_nachweise/firefox_http09_fehler.png](browser_nachweise/firefox_http09_fehler.png) | Firefox-Fehlerseite; sichtbar ist `NS_ERROR_NET_EMPTY_RESPONSE`, während die Automatisierungs-Exception `NS_ERROR_NET_RESET` lautet. |
| Extern gebautes Go-Binary | Vom Aufrufer mit `--go-server` angegeben; nicht Bestandteil der Abgabe. Das Skript lädt weder Git-Quellen herunter noch baut es Go selbst. |
| [ue3.3/screenshots/verifikation.json](ue3.3/screenshots/verifikation.json) | Separater Thunderbird-Nachweis, **nicht** vom Integrationstreiber erzeugt. |
| [ue3.3/gui_testbericht.md](ue3.3/gui_testbericht.md) | Bericht und Reproduktionshinweise des separaten echten Thunderbird-Tests. |
| [testprotokoll_blatt03.md](testprotokoll_blatt03.md) | Zusammenführung der tatsächlich belegten Unit-, Referenz-, Browser- und GUI-Ergebnisse mit Grenzen. |

Das ZIP enthält drei reguläre Dateien sowie den Verzeichniseintrag `images/`. Der Integrationscode läuft über **alle bereits vorhandenen Dateien** im ermittelten DocumentRoot, nicht ausschließlich über eine im Code festgeschriebene Dreierliste. Zusätzliche Altdateien würden daher mitgetestet; sie werden beim Entpacken nicht automatisch entfernt.

## 3. Ablauf in der richtigen Reihenfolge

1. Argumente lesen und ein zunächst nur im Speicher liegendes Berichts-Dictionary erzeugen.
2. Falls `--go-server` gesetzt ist: das ausdrücklich ausgewählte lokale Binary starten, auf seine POP3-Erreichbarkeit warten, anmelden, zwei Nachrichten auflisten, Nachricht 1 holen, mit `QUIT` schließen und den Fremdprozess beenden.
3. ZIP-Pfade kontrollieren, Originalmaterial entpacken und genau eine Startseite suchen.
4. Beide HTTP-Server auf Loopback und dynamischen freien Ports starten. Erst nach deren Bereitschaft mit den Browsern fortfahren.
5. Nacheinander Chromium und Firefox starten. Je Browser: Originalseite laden, Status und HTML-Bytes prüfen, Text und Bilddekodierung prüfen, Screenshot erstellen, jede Datei nochmals bytegenau abrufen und schließlich die erwartete HTTP/0.9-Inkompatibilität festhalten.
6. Browser schließen, Serverstopps auslösen, Threads einsammeln und den gepufferten HTTP-Zugriffslog übernehmen.
7. Nur wenn der gesamte normale Ablauf erfolgreich war: JSON-Datei schreiben und denselben Inhalt auf stdout ausgeben.

## 4. Jede Codezeile erklärt

### 4.1 Kennzeichnung, Imports und Basispfad – Zeilen 1–21

| Zeile(n) | Bedeutung |
|---|---|
| 1–3 | Kommentare zu KI-Herkunft, Datum und ursprünglichem Implementierungsauftrag; sie beeinflussen die Ausführung nicht. |
| 4–8 | Modul-Docstring: optionaler Integrationscharakter, Beispiel mit Go-Binary und Abgrenzung zu den Standardbibliotheksprogrammen. Dieser Text wird später auch in der CLI-Hilfe verwendet. |
| 9 | `argparse` verarbeitet die Kommandozeilenoption. |
| 10 | `hashlib` berechnet die SHA-256-Fingerabdrücke der geprüften Originaldateien. |
| 11 | `importlib.util` lädt Python-Dateien anhand ihres Pfads. Die Aufgabenordner mit Punkten im Namen müssen dadurch keine regulären Python-Pakete sein. |
| 12 | `io.StringIO` nimmt das HTTP/1.0-JSONL-Log im Speicher entgegen. |
| 13 | `json` liest die Logzeilen und serialisiert den Abschlussbericht. |
| 14 | `Path` kapselt Dateisystempfade und deren Auflösung. |
| 15 | `subprocess` startet und beendet den Go-Fremdprozess. |
| 16 | `sys` liefert die Python-Version und die Modultabelle für dynamische Imports. |
| 17 | `threading` stellt Threads und Bereitschafts-/Stop-Ereignisse bereit. |
| 18 | `time.monotonic` misst Fristen unabhängig von Uhrkorrekturen; `time.sleep` begrenzt die Startpolling-Frequenz. |
| 19 | `zipfile` liest und extrahiert das Originalarchiv. |
| 21 | `ROOT` ist der aufgelöste Ordner des Skripts, also `ueb03/`. Eingabe- und Ausgabepfade hängen deshalb nicht vom aktuellen Shell-Verzeichnis ab. |

### 4.2 Dynamischer Import `load` – Zeilen 24–31

| Zeile | Bedeutung und möglicher Fehler |
|---|---|
| 24 | Definiert die Hilfsfunktion mit einem frei gewählten Modulnamen und einem Dateipfad. |
| 25 | Erzeugt die Importbeschreibung für diese Datei. |
| 26 | Prüft, ob sowohl Beschreibung als auch ausführender Loader existieren. |
| 27 | Bei fehlendem Loader folgt `ImportError`, statt mit einem unbrauchbaren Import fortzufahren. |
| 28 | Erzeugt das Modulobjekt, führt seinen Inhalt aber noch nicht aus. |
| 29 | Registriert es in `sys.modules`. Das ist unter anderem für die `dataclass`-Verarbeitung im HTTP/1.0-Modul wichtig. |
| 30 | Führt den Modulcode aus. Datei-, Import- und Syntaxfehler werden nicht verschluckt. Der `if __name__ == '__main__'`-Block der importierten Datei wird dabei nicht ausgeführt. |
| 31 | Gibt das geladene Modul samt Klassen und Funktionen zurück. |

Diese Funktion importiert nur die eigenen lokalen Python-Dateien. Sie ist keine Sandbox: Importcode wird normal ausgeführt.

### 4.3 Originaldaten entpacken: `unpack` – Zeilen 34–46

| Zeile | Erklärung |
|---|---|
| 34 | Beginn der Funktion, die den nutzbaren DocumentRoot zurückgibt. |
| 35 | Legt das Ziel auf `Angabe/document_root` unterhalb von `ROOT` fest. |
| 36 | Erstellt diesen Ordner, wenn er fehlt. `exist_ok=True` erlaubt einen vorhandenen Ordner; fehlende Elternverzeichnisse oder ein gleichnamiger Nichtordner bleiben Fehler. |
| 37 | Öffnet `Angabe/document_root.zip` als Kontextmanager; das Archiv wird auch bei Ausnahmen geschlossen. Fehlende Datei oder defektes ZIP brechen den Lauf ab. |
| 38 | Durchläuft alle Archiveinträge einschließlich des Verzeichniseintrags. |
| 39 | Verknüpft Zielordner und Archivnamen und löst den tatsächlichen Pfad auf. |
| 40 | Prüft komponentenweise, ob das Ergebnis innerhalb des aufgelösten Zielordners liegt. Das ist nicht bloß ein unsicherer Zeichenketten-Präfixvergleich. |
| 41 | Ein ausbrechender Pfad, beispielsweise mit `..`, führt vor der Extraktion dieses Eintrags zu `ValueError('Unsicherer ZIP-Pfad')`. |
| 42 | Extrahiert den geprüften Eintrag. Bereits vorhandene gleichnamige Dateien können überschrieben werden. |
| 43 | Sucht nach allen `index.html` unterhalb des Zielordners, auch in Unterordnern. |
| 44 | Verlangt genau einen Treffer. |
| 45 | Kein Treffer oder mehrere Startseiten führen zu einem erklärenden `ValueError`. |
| 46 | Gibt das Elternverzeichnis dieser einen Startseite als DocumentRoot zurück. |

**Grenze der Absicherung:** Die aufgelösten Pfade verhindern den geprüften Verzeichnisausbruch. Die Funktion ist kein allgemeiner Entpacker für feindliche Archive: Sie begrenzt weder entpackte Gesamtgröße noch Dateianzahl, räumt nicht vorher auf und bietet keine transaktionale Rücknahme oder vollständige Absicherung gegen gleichzeitig manipulierte Dateisystempfade. Hier wird das bekannte Originalarchiv verwendet.

### 4.4 Go-Referenztest `go_test` – Zeilen 49–82

| Zeile(n) | Erklärung |
|---|---|
| 49 | Erwartet den Binarypfad und das gemeinsame Berichts-Dictionary. |
| 50 | Docstring: Es geht um eine fremde Implementierung und ausschließlich synthetische Zugangsdaten. |
| 51 | Lädt den eigenen Client unter dem separaten Namen `integration_pop3_client`. |
| 52 | Startet exakt das gewählte Programm ohne Shell und ohne zusätzliche Argumente. stdout wird gepuffert, stderr dorthin umgeleitet, Textmodus aktiviert. Fehlender Pfad oder fehlende Ausführungsrechte scheitern bereits hier. |
| 53 | Ab hier schützt `try/finally` das spätere Beenden des gestarteten Prozesses. |
| 54 | Setzt eine monotone Startfrist von zehn Sekunden. |
| 55 | Wiederholt den Bereitschaftsversuch. |
| 56 | Prüft zuerst, ob der Go-Prozess schon beendet ist. |
| 57 | Ein vorzeitig beendeter Prozess erzeugt `RuntimeError` mit seiner bisherigen Ausgabe. |
| 58–60 | Versucht eine echte Clientverbindung zu `127.0.0.1:11119` mit drei Sekunden Sockettimeout. Der Client liest bereits die POP3-Begrüßung. Bei Erfolg endet die Pollingschleife. |
| 61 | Nur `OSError` wird als möglicher vorübergehender Startfehler behandelt; POP3-/Framingfehler sind nicht automatisch „noch nicht bereit“. |
| 62–63 | Ist die Startfrist abgelaufen, wird der zuletzt gefangene Verbindungsfehler erneut ausgelöst. Die Frist wird zwischen Versuchen geprüft, nicht als harter Gesamttimer um alle Socketoperationen. |
| 64 | Wartet 0,05 Sekunden vor dem nächsten Versuch, statt eine CPU-Schleife zu erzeugen. |
| 65 | Betritt den Client-Kontextmanager. Bei normalem Verlassen sendet dieser `QUIT` und schließt lokal; bei einer Ausnahme wird nur der Transport geschlossen. |
| 66 | Meldet das öffentliche Testkonto `alice/secret` über `USER` und `PASS` an. Es gibt hier kein persönliches Mailkonto. |
| 67 | `LIST` liefert Nummer/Oktettzahl-Paare. |
| 68 | Verlangt genau zwei Listeneinträge; bei Abweichung wird die tatsächliche Liste als Assertion-Hinweis ausgegeben. |
| 69 | Ruft ausschließlich Nachricht 1 mit `RETR 1` ab. Nachricht 2 wird nicht heruntergeladen. |
| 70 | Verlangt die Headerzeile `Subject: Hello Alice` mit CRLF im erhaltenen Byteinhalt. Das ist kein Vergleich der gesamten Mail gegen eine unabhängige Referenzdatei. |
| 71 | Vergleicht die tatsächliche Länge der ersten Mail mit der Oktettangabe des ersten Listeneintrags. Die konkrete Zahl 151 steht nicht fest im Testcode, sondern ist das beobachtete Ergebnis. |
| 72–74 | Erst nach erfolgreichem Verlassen des Kontextmanagers werden Begrüßung, Liste, Mailbytes als Text, Oktettzahl und lokaler Geschlossen-Zustand gespeichert. `decode()` verwendet standardmäßig UTF-8 und kann bei anderen Testdaten scheitern. |
| 75–77 | Speichert Quelle, feste Revision und Beschreibung des Buildpatches. **Dies sind vom Testautor eingetragene Herkunftsangaben**, keine zur Laufzeit aus dem Binary ermittelten Git-/Go-Metadaten. |
| 78–79 | Der `finally`-Block sendet dem Fremdprozess ein Terminierungssignal, auch wenn zuvor eine Assertion fehlschlug. |
| 80 | Sammelt die Prozessausgabe und wartet höchstens zehn Sekunden. Es gibt hier keinen zusätzlichen `kill()`-Fallback; ein nicht reagierender Prozess kann `TimeoutExpired` auslösen. |
| 81–82 | Übernimmt den Go-Startlog und hält fest, ob der Prozess beendet ist. Ein bestimmter Go-Exitcode wird nicht verlangt; das Testprogramm wird absichtlich beendet. |

**Voraussetzung:** Port 11119 muss frei sein. Das Skript identifiziert einen dort eventuell bereits laufenden Server nicht durch PID. Ein fremder Prozess auf diesem Port ist kein zulässiger Testaufbau. Das Testbinary muss selbst genau an diese Loopback-Adresse gebunden werden; die CLI kann dessen Port nicht verändern.

`closed_after_quit: true` bezeichnet den lokalen Clientzustand. Dass der normale Kontextabschluss überhaupt erreicht wird, setzt eine erfolgreiche `QUIT`-Statusantwort voraus; es ist aber keine zusätzliche Paketaufzeichnung des TCP-Verbindungsendes.

### 4.5 Browser und lokale HTTP-Server – Zeilen 85–119

| Zeile(n) | Erklärung |
|---|---|
| 85–86 | Beginn und Docstring des Browserintegrationsteils. |
| 87 | Importiert die synchrone Playwright-API erst beim Browsertest. Das Zusatzpaket wird für reine Unittests nicht benötigt. |
| 88–89 | Lädt die beiden eigenen HTTP-Module mit unterschiedlichen Modulnamen. |
| 90 | Stop-Ereignis für den HTTP/0.9-Server. |
| 91 | Zwei getrennte Bereitschaftsereignisse verhindern Anfragen vor dem erfolgreichen Binden der Server. |
| 92 | Das Dictionary nimmt die tatsächlich zugewiesenen Socketadressen auf. |
| 93–97 | `ready(name, event)` erzeugt einen Callback als Closure. Der Callback speichert die Adresse unter `09` oder `10` und setzt **danach** das zugehörige Ereignis. Die äußere Funktion liefert diesen Callback zurück. |
| 98 | In-Memory-Ausgabestrom für den zentralen HTTP/1.0-Logger. |
| 99 | Erzeugt den HTTP/1.0-Server mit dem DocumentRoot, `port=0` und diesem Logstrom. Port 0 lässt das Betriebssystem einen freien Port auswählen; die Serverklasse bindet standardmäßig an Loopback. |
| 100–102 | Erzeugt den Thread für HTTP/0.9: DocumentRoot als Positionsargument, dynamischer Port, eigenes Stop-Ereignis und Bereitschafts-Callback als Schlüsselwortargumente. |
| 103 | Erzeugt den Thread für `server.serve`, diesmal mit dem HTTP/1.0-Callback als Argument. |
| 104–105 | Startet beide Threads. Die Threads sind nicht als Daemon markiert. |
| 106 | Beginn des Blocks mit abschließender Serverbereinigung. |
| 107 | Wartet je Bereitschaftsereignis bis zu zehn Sekunden; bei Nichterreichen folgt `AssertionError('Server nicht bereit')`. Wegen des kurzschließenden `and` wird bei erfolgloser erster Warteoperation die zweite nicht mehr ausgeführt. |
| 108 | Initialisiert die Ergebnisliste der Browser. |
| 109–110 | Bestimmt und erstellt `browser_nachweise/`; vorhandene Bilddateien gleichen Namens können später überschrieben werden. |
| 111 | Startet Playwright im Kontextmanager und räumt dessen Infrastruktur beim Verlassen auf. |
| 112 | Prüft nacheinander exakt `chromium` und `firefox`. Das ist kein Test von Safari/WebKit oder allen Browsern. |
| 113–114 | Startet Chromium headless mit `channel='chromium'`. Dieser explizite Kanal ist bei Reproduktion beizubehalten. |
| 115–116 | Startet den von Playwright bereitgestellten Firefox ebenfalls headless. |
| 117 | Ab hier wird das bereits gestartete Browserobjekt durch `finally` geschlossen. |
| 118 | Öffnet eine neue Seite mit Viewport 1280 × 900 Pixel. |
| 119 | Speichert Browsername und tatsächlich abgefragte `browser.version`; initialisiert die Liste der Dateiprüfungen. |

### 4.6 HTTP/1.0 erfolgreich laden, rendern und Bytes vergleichen – Zeilen 120–139

| Zeile | Erklärung |
|---|---|
| 120 | Baut die URL aus Loopback und dem tatsächlich gebundenen HTTP/1.0-Port. |
| 121 | Navigiert auf `/` und wartet auf `networkidle`. Damit sind typische Nachladeanfragen abgeklungen; ein separater Bildtest folgt trotzdem. |
| 122 | Verlangt Status 200 der Hauptnavigation. |
| 123 | Vergleicht den HTTP-Response-Body **bytegenau** mit der Original-`index.html`. Header gehören nicht zu diesem Bytevergleich. |
| 124 | Verlangt nichtleeren sichtbaren Text im `body`. Das prüft mehr als bloß einen HTTP-Status. |
| 125 | Kommentar zur Trennung von Rendering- und Rohbyteprüfungen. |
| 126 | Führt JavaScript über alle `img`-Elemente aus: notiert das ursprüngliche `src` und verlangt pro Bild später `complete` sowie `naturalWidth > 0`. Letzteres unterscheidet erfolgreich dekodierte Bilder von fertig beendeten, aber kaputten Ladevorgängen. |
| 127 | Die Assertion verlangt für alle gefundenen Bilder `ok=true`. **Grenze:** `all([])` wäre auch wahr; die Zahl zwei wird hier nicht fest geprüft, ist aber in der Originalseite und im echten Bericht vorhanden. |
| 128 | Speichert die Bildzustände. |
| 129 | Liest und speichert den Seitentitel. Der Test vergleicht ihn nicht hart mit `Test`; das ist der beobachtete Wert. |
| 130 | Speichert den sichtbaren Bodytext einschließlich der vom Browser gelieferten Leerzeichen/Zeilenumbrüche. |
| 131 | Erstellt die echte gerenderte Ganzseitenaufnahme `<browser>_http10.png`. `full_page=True` kann bei anderer Seite über die Viewporthöhe hinausgehen. |
| 132 | Durchläuft alle DocumentRoot-Pfade in sortierter Reihenfolge, damit der Bericht stabil geordnet ist. |
| 133 | Verzeichnisse werden übersprungen; nur Dateien werden abgerufen. |
| 134 | Macht den Pfad relativ zum DocumentRoot und verwendet URL-taugliche `/` als Trenner. Eine allgemeine Prozentkodierung beliebiger Dateinamen findet hier nicht statt; die gelieferten Dateinamen benötigen sie nicht. |
| 135 | Ruft jede Datei mit Playwrights `page.request`-HTTP-Client ab. Das ist ein zusätzlicher API-Rohbytecheck im Browserkontext, **keine weitere gerenderte Navigation**. |
| 136 | Liest die erwarteten Originalbytes von der Platte. |
| 137 | Verlangt für diese Datei Status 200 und exakt dieselben Antwortbytes. Bei einem Fehler wird der relative Dateipfad angezeigt. |
| 138–139 | Speichert relativen Pfad, Bytezahl und SHA-256 der lokalen Erwartungsdatei. Da unmittelbar zuvor Antwort und Datei auf Gleichheit geprüft wurden, identifiziert dieser Hash zugleich die erfolgreich übertragenen Bytes. |

Der Server heißt HTTP/1.0, sendet HTTP/1.0-Antworten und akzeptiert einen begrenzten HTTP/1.1-Request-Teilumfang für moderne Browser. Der Browsertest erzwingt **keine** HTTP/1.0-Requestzeile und behauptet keinen vollständigen HTTP/1.1-Server.

### 4.7 Erwartete HTTP/0.9-Ablehnung und Bereinigung – Zeilen 140–157

| Zeile(n) | Erklärung |
|---|---|
| 140–141 | Versucht mit demselben Browser eine normale Navigation auf den dynamischen HTTP/0.9-Port; Navigationsfrist 15.000 Millisekunden. |
| 142–143 | Jede dabei geworfene `Exception` wird als `displayed=false` mit ihrem genauen Text gespeichert. Der tatsächliche Fehlertext muss im Bericht kontrolliert werden: Ein beliebiger Timeout wäre nicht automatisch derselbe Protokollbefund. |
| 144–145 | Wenn `goto` unerwartet ohne Ausnahme zurückkehrt, schlägt der Test bewusst fehl. Die Meldung ist eine Erwartungsprüfung; der Code untersucht in diesem Zweig nicht zusätzlich den Seiteninhalt. |
| 146 | Nimmt die tatsächliche Seite nach dem Fehler auf. Wegen asynchroner browserinterner Fehlerseiten ist der Screenshot nicht allein die maßgebliche Quelle für den genauen Navigationsfehler. |
| 147 | Fügt erst den abgeschlossenen Browserdurchlauf in die gemeinsame Liste ein. |
| 148–149 | Schließt den Browser auch nach einem fehlgeschlagenen Assert oder Screenshot. |
| 150–152 | Äußerer `finally`-Block setzt das HTTP/0.9-Stop-Ereignis und das eigene Stop-Ereignis des HTTP/1.0-Servers. |
| 153–155 | Wartet pro Serverthread bis zu zehn Sekunden und verlangt anschließend, dass dieser nicht mehr lebt. Ein hängender Thread wird nicht als erfolgreicher Abschluss ausgegeben. |
| 156 | Liest die vollständig eingesammelten JSONL-Zeilen aus `StringIO` und wandelt jede mit `json.loads` in ein Dictionary um. Der HTTP/1.0-Server beendet zuvor seine Leser/Worker und flusht den Logger. Fehlerhaftes JSON würde den Test ebenfalls abbrechen. |
| 157 | Kennzeichnet erfolgreich beendete HTTP-Server. Diese Zeile wird erst nach bestandenen Threadprüfungen erreicht. |

### 4.8 Einstieg und Bericht – Zeilen 160–174

| Zeile | Erklärung |
|---|---|
| 160 | Definiert den Kommandozeileneinstieg. |
| 161 | Erzeugt den Parser und verwendet den Modul-Docstring als Beschreibung. |
| 162 | Definiert das **optionale** `--go-server` als `Path`; es gibt dafür keinen Standardbinarypfad. |
| 163 | Verarbeitet Argumente. Unbekannte Optionen führen zur argparse-Fehlermeldung. `--help` beendet sich vor den eigentlichen Tests. |
| 164 | Initialisiert Bericht mit tatsächlichem `sys.version`, fest eingetragenem `testdate='2026-10-19'` und einer Modusbeschreibung. **Wichtig:** Das Datum wird nicht zur Laufzeit ermittelt und wäre bei einer späteren Wiederholung ohne Codeänderung veraltet. |
| 165–166 | Führt den Go-Test nur bei angegebener Option aus; der Binarypfad wird vorher absolut aufgelöst. Ohne Option fehlen die Go-Felder im späteren Bericht. |
| 167 | Wertet zuerst `unpack()` aus und übergibt dessen Ergebnis an `browser_tests`. Der Browserteil ist nicht optional abschaltbar. |
| 168 | Bestimmt `integration_ergebnis.json` als festes Ausgabeziel. |
| 169 | Schreibt UTF-8-JSON mit lesbaren Unicodezeichen, Einrückung und abschließendem Zeilenumbruch. Eine vorhandene Ergebnisdatei wird überschrieben; der Schreibvorgang ist nicht atomar. |
| 170 | Gibt den gleichen Berichtsinhalt auf stdout aus. |
| 173–174 | Ruft `main()` nur beim direkten Skriptstart auf. Normaler Abschluss ergibt Exitcode 0; ungefangene Ausnahmen einen Fehlerexit. |

## 5. Die tatsächlich beobachteten Browserergebnisse

Der gespeicherte Lauf vom 19.10.2026 verwendete **Chromium 156.0.8078.4** und **Firefox 157.0**. In beiden HTTP/1.0-Aufnahmen sind das Universitätslogo, die Technikgrafik und `It works...!` tatsächlich sichtbar. Beide Berichte enthalten zwei erfolgreich dekodierte Bilder und dieselben drei bytegenau geprüften Dateien.

| Browser | HTTP/1.0 | HTTP/0.9: exakte Automatisierungsbeobachtung | Sichtbare Fehlerseite |
|---|---|---|---|
| Chromium 156.0.8078.4 | Status 200, HTML und Bilder erfolgreich | `Page.goto: net::ERR_EMPTY_RESPONSE` | „This page isn’t working“, „127.0.0.1 didn’t send any data.“, `ERR_EMPTY_RESPONSE` |
| Firefox 157.0 | Status 200, HTML und Bilder erfolgreich | `Page.goto: NS_ERROR_NET_RESET` | „sent back an empty page“, `NS_ERROR_NET_EMPTY_RESPONSE` |

Die Codes aus Firefox-Exception und Firefox-Seiteninhalt sind **unterschiedlich und werden nicht vereinheitlicht**. Die vorliegenden vier PNGs wurden zusätzlich visuell geprüft. Der Chromium-Fehlercode ist in dieser vorhandenen Aufnahme sichtbar; eine pauschale Behauptung, das Bild sei nur weiß, trifft auf diese Datei nicht zu.

Warum ist die Ablehnung plausibel? Der HTTP/0.9-Server akzeptiert exakt eine zweigliedrige `GET /pfad`-Zeile und keine moderne Requestversion oder Header. Ein normaler aktueller Browser schickt keine solche historische Anfrage. Der Server schließt bei unzulässiger Syntax ohne Status/Fehlertext. Das erklärt den lokalen Befund; der Test beweist **nicht**, dass jede heutige Engine jede mögliche HTTP/0.9-Antwort unter allen Umständen ablehnt.

Der HTTP/1.0-Zugriffslog enthält 12 Status-200- und zwei Status-404-Einträge. Der Bericht speichert keine angefragten Pfade im Log. Die beiden 404 können deshalb nicht allein daraus sicher einem Favicon zugeordnet werden. Die explizit geprüften Originaldateien hatten dagegen alle Status 200.

## 6. Reproduktion ohne versteckte Installationspfade

Die folgenden Befehle sind eine Anleitung, kein automatisch ausgeführter Download-/Buildauftrag. Vom Repository-Hauptverzeichnis ausgehen. Kein `python -O` und kein `PYTHONOPTIMIZE` verwenden: Der Test nutzt `assert`; Optimierung würde wesentliche Prüfungen abschalten.

### 6.1 Nur Standardbibliotheksprüfungen

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.2 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.3 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.4 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.5 -v
```

Das sind vier getrennte Discover-Aufrufe, weil mehrere Aufgaben eine `server.py` besitzen und Importnamen in einem gemeinsamen Prozess kollidieren könnten.

### 6.2 Browserabhängigkeiten getrennt vorbereiten

Getestet wurde Playwright **1.64.0**. Für eine neue Installation eine Python-Umgebung mit `venv` und `pip` sowie die erforderlichen Linux-Browserbibliotheken verwenden. Die konkrete System-Python-Installation muss `pip` nicht mitbringen; gegebenenfalls eine geeignete vorbereitete Testumgebung benutzen. `TEST_ENV` ist vom Benutzer auf ein Verzeichnis **außerhalb** der Abgabe zu setzen.

```sh
python3 -m venv "$TEST_ENV"
"$TEST_ENV/bin/python" -m pip install 'playwright==1.64.0'
"$TEST_ENV/bin/python" -m playwright install chromium firefox
PYTHONDONTWRITEBYTECODE=1 "$TEST_ENV/bin/python" ueb03/integration_test.py
```

Falls Playwright fehlende Betriebssystembibliotheken meldet, diese bewusst über die Systemadministration bereitstellen; Browserinstallation allein garantiert sie nicht. Ein Lauf ohne `--go-server` prüft nur die Browser, überschreibt aber trotzdem den Gesamtbericht und entfernt dadurch bisherige Go-Ergebnisfelder. Der Test entpackt außerdem das ZIP und überschreibt die vier gleichnamigen Browserscreenshots. Bestehende Nachweise vorher sichern oder in einer separaten Arbeitskopie reproduzieren.

### 6.3 Go-Referenz gezielt prüfen, bauen und dann freigeben

Quelle: [GoPop3Server in der verwendeten festen Revision](https://github.com/kurthorvath/GoPop3Server/tree/eae717dd98cb0a59e7afd3e857bc1c86660c530d). Dieser Link war bei der Dokumentationsprüfung erreichbar; die lokale Git-Revision und Remote-Adresse stimmen damit überein. Im Original steht in `main.go` die Bind-Adresse `:110`; entgegen einer ungenauen localhost-Formulierung in dessen README ist das keine ausdrückliche Loopback-Bindung.

`GO_SOURCE` ist ein eigener, noch nicht belegter Quellordner außerhalb der Abgabe; `GO_BINARY` ein **absoluter** gewünschter Binarypfad ebenfalls außerhalb der Abgabe. Beide Variablen selbst setzen.

```sh
git clone https://github.com/kurthorvath/GoPop3Server.git "$GO_SOURCE"
git -C "$GO_SOURCE" checkout --detach eae717dd98cb0a59e7afd3e857bc1c86660c530d
git -C "$GO_SOURCE" rev-parse HEAD
git -C "$GO_SOURCE" show HEAD:main.go
git -C "$GO_SOURCE" show HEAD:go.mod
```

**Vor Kompilierung und Ausführung den fremden Quellcode prüfen.** Danach in der externen Arbeitskopie ausschließlich folgende Bind-Adresse ändern:

```diff
- addr := ":110"
+ addr := "127.0.0.1:11119"
```

Der Patch betrifft nur die Bindung, nicht Authentifizierung oder Nachrichten. Er vermeidet den privilegierten Standardport und eine Bindung auf allen Interfaces. Nicht die im Fremdrepo mitgelieferten Binaries ungeprüft ausführen. Erst nach eigener Freigabe:

```sh
git -C "$GO_SOURCE" diff -- main.go
go version
go build -C "$GO_SOURCE" -o "$GO_BINARY" .
PYTHONDONTWRITEBYTECODE=1 "$TEST_ENV/bin/python" ueb03/integration_test.py --go-server "$GO_BINARY"
```

Der dokumentierte erfolgreiche Lauf nutzte Go **1.27.2**. Das Fremdprojekt nennt in `go.mod` `go 1.21.4`; das ist nicht die Behauptung, der Test sei mit genau dieser Toolchain gelaufen. Der aufgezeichnete Go-Startlog bestätigt `127.0.0.1:11119`. Herkunft und Buildpatch werden vom Test selbst lediglich als feste Angaben gespeichert; ein beliebiges anderes `--go-server`-Binary würde nicht automatisch auf diese Herkunft geprüft.

### 6.4 Separater Thunderbird-Nachweis

Voraussetzungen: Thunderbird, Xvfb, ffmpeg und `marionette_driver` in einer passenden separaten Python-Testumgebung. Details einschließlich Versionsgrenzen stehen in [ue3.3/gui_testbericht.md](ue3.3/gui_testbericht.md) und [ue3.3/erklaerung_gui.md](ue3.3/erklaerung_gui.md).

```sh
PYTHONDONTWRITEBYTECODE=1 python3 ueb03/ue3.3/gui_test.py --thunderbird "$THUNDERBIRD_BIN" --display :184 --output "$GUI_OUTPUT"
```

`THUNDERBIRD_BIN` auf das ausführbare Thunderbird und `GUI_OUTPUT` auf ein eigenes Nachweisverzeichnis setzen; das Display muss frei sein. Mit einer anderen Python-Testumgebung deren Interpreter statt `python3` aufrufen. Dieser Test startet seinen eigenen lokalen POP3-Server, legt ein temporäres Mailprofil an und prüft vier Originalnachrichten. Er verändert nicht den Programmcode. Der vorhandene belegte Lauf verwendete Thunderbird **158.0**, nicht einen nachgebauten Mailclient.

## 7. Fehlerdiagnose und ehrliche Grenzen

- **Fehlendes Playwright/Paket/Binary:** `ModuleNotFoundError` oder Launchfehler sind Umgebungsprobleme, kein bestandener Browsernachweis. Beide Browser müssen verfügbar sein; der Test überspringt keinen von ihnen stillschweigend.
- **Go startet nicht oder Port belegt:** Prozessausgabe und Fehler prüfen. Nicht auf einen anderen bereits laufenden Port-11119-Dienst ausweichen und dessen Ergebnis als neu gestartetes Testbinary ausgeben.
- **ZIP/DocumentRoot falsch:** Fehlendes Archiv, unsichere Pfade oder nicht genau eine Startseite brechen ab. Vorhandene zusätzliche Dateien können das Ergebnis beeinflussen.
- **HTTP/1.0-Assertion:** Status, Bytevergleich, sichtbarer Text oder dekodierte Bilder passen nicht. Die Prüfung ist erst bestanden, wenn alle Bedingungen erfüllt sind.
- **HTTP/0.9-Exception:** Die aktuelle Implementierung akzeptiert im Test jede Navigations-Exception. Deshalb müssen deren wirkliche Texte wie oben dokumentiert geprüft werden; ein reiner Timeout wäre kein gleichwertiger Nachweis der hier beobachteten Leerdaten-/Resetfehler.
- **Fehlerbericht nicht garantiert:** `integration_ergebnis.json` wird nur nach komplett erfolgreichem Durchlauf geschrieben. Bei Fehler kann ein alter Bericht liegen bleiben, während einzelne PNGs bereits neu sind. Ausgabezeitpunkte/Arbeitskopien auseinanderhalten; die bloße Existenz einer alten JSON-Datei beweist keinen aktuellen Erfolg.
- **Cleanup nicht beliebig robust:** Go hat keinen Kill-Fallback; die HTTP-Threads werden geprüft, aber nicht zwangsweise beendet. Prozess-/Threadstart vor dem jeweiligen `try` ist nicht durch jeden späteren Cleanup-Pfad abgedeckt. Ein Fehler beim Cleanup kann außerdem eine vorherige Exception überlagern.
- **Keine Vollständigkeitsbehauptung:** Der Integrationstreiber prüft beim Fremdserver weder Nachricht 2 per `RETR` noch negative Login-/Löschfälle. Er misst keine Lastgrenze, beweist keine Internet-/TLS-Sicherheit, erstellt keine Paketaufzeichnung und testet nicht sämtliche Browser-/Mailclientversionen. Diese Grenzen werden durch einen grünen Happy-Path-Lauf nicht aufgehoben.
