# Ü4.3 – UDP verstehen und live ändern

Die Tabellen erklären jede nichtleere Quellzeile einzeln; die Nummer links ist die Zeilennummer **im jeweiligen Python-Programm**, nicht in dieser Dokumentation. Auch Kommentare, Docstrings und Fortsetzungen sind enthalten. Leerzeilen dienen nur der Übersicht. Quelltexte: [server.py](server.py), [client.py](client.py), [test_udp.py](test_udp.py). Einordnung aller Aufgaben: [Lernweg](../erklaerung_blatt04.md).

## Ablauf und typische Änderungen

1. Server zuerst starten und auf `READY` warten: `python3 -B ue4.3/server.py --host 127.0.0.1 --port 5000 --count 1 --timeout 30` (aus `ueb04`, eigenes Terminal).
2. Danach im zweiten Terminal: `python3 -B ue4.3/client.py --host 127.0.0.1 --message 'Grüße 🌍'`. Beide Prozesse benutzen beim lokalen Test denselben Netzwerk-Namespace. In der Standard-Labortopologie läuft der Server dagegen auf h2 und der Client auf h1; dort ist das Ziel `10.0.0.2`, nicht localhost.
3. Danach Tests: `python3 -B ue4.3/test_udp.py`. Die vorhandene Ausgabe ist [test_udp.txt](test_udp.txt); sie ist von [echten Namespace-Läufen](../nachweise/run01/results.json) zu unterscheiden.

Zum Vorführen zuerst `--message`, `--count` oder `--timeout` ändern, nicht den Code. Portänderungen müssen auf beiden Seiten zusammenpassen. `--port 0` ist beim **Server** eine freie Portwahl; dessen READY-Port beim Client einsetzen. `--local-port` setzt den Quellport, nicht den Zielport. Ein Empfangslimit im Server und das Sendelimit im Client müssen bei einer Codeänderung gemeinsam angepasst und erneut getestet werden. Das Limit zählt UTF-8-Bytes. Bei UDP ist auch ein Datagramm mit leerer Nutzlast eine Nachricht: kein EOF wie bei TCP.

Der eigene Server folgt dem **PDF-Beispiel ohne Antwort**. Die bereitgestellten Dateien `Angabe/udp_server.py` und `Angabe/udp_client.py` sind ein anderes Paar: RN-Lab-Adresse `10.0.2.2`, ACK-Antwort bzw. Warten auf diese Antwort. Die beiden Varianten nicht unbemerkt mischen. UDP-`connect()` unten ist **kein TCP-Verbindungsaufbau**. Erfolgreiches Senden beweist allein noch keinen Empfang.

## server.py

| Zeile | Was geschieht und warum? |
|---:|---|
| 1 | Kommentar mit KI-Werkzeug, Modell und Datum; macht die Herkunft sichtbar, führt nichts aus. |
| 2 | Kommentar nennt den Auftrag: den UDP-Server des Blatts bedienbar und testbar machen. |
| 3 | Kommentar nennt die Ergänzungen und das Standardziel; er konfiguriert den Socket nicht selbst. |
| 4 | Modulbeschreibung: Der Empfänger antwortet absichtlich nicht; dieser Text erscheint später auch in der CLI-Hilfe. |
| 6 | Lädt argparse, damit Host, Port, Anzahl und Timeout als Optionen statt durch Quelltextänderung wählbar sind. |
| 7 | Lädt math für die Prüfung, dass ein Timeout weder NaN noch unendlich ist. |
| 8 | Lädt socket für den echten IPv4-UDP-Endpunkt des Linux-Kernels. |
| 9 | Lädt sys für Fehlerausgabe auf stderr und den Prozess-Exitcode. |
| 12 | Definiert serve mit Bindeadresse, Port, Datagrammzahl und Wartezeit; erst ein Aufruf öffnet den Server. |
| 13 | Erzeugt einen IPv4-Datagrammsocket; with schließt ihn auch bei Timeout oder Ausnahme. UDP braucht kein listen oder accept. |
| 14 | Begrenzt blockierende Socketoperationen auf timeout Sekunden; besonders recvfrom kann dadurch nicht endlos still warten. Kein Gesamtzeitlimit des Servers. |
| 15 | Bindet den Socket an eine im aktuellen Namespace vorhandene Adresse und den lokalen Port. Ein nicht vorhandenes 10.0.0.2 würde fehlschlagen. |
| 16 | Fragt die tatsächliche Bindung ab; bei Port 0 erfährt man hier den vom Kernel gewählten Port. |
| 17 | Meldet erst nach erfolgreichem bind die Bereitschaft; flush macht die Zeile sofort für Menschen und Tests lesbar. |
| 18 | Setzt den Zähler tatsächlich empfangener Datagramme auf null; READY wird nicht mitgezählt. |
| 19 | Empfängt bei count=0 ohne Zähllimit, sonst bis zur gewünschten Anzahl. Timeout und Tastaturabbruch bleiben auch bei null wirksam. |
| 20 | Holt genau ein UDP-Datagramm mit höchstens 4096 Nutzbytes und dessen Absender-IP/Port. Größere Datagramme können abgeschnitten werden; diese Grenze garantiert nicht der Kernel für fremde Sender. |
| 21 | Zeigt Absender und Byte-Repräsentation der Nutzlast; !r macht auch leere Daten und nicht-ASCII-Bytes sichtbar. Es wird nichts zurückgesendet. |
| 22 | Zählt das Datagramm nach der Ausgabe; auch b'' erhöht den Zähler. |
| 23 | Liefert nach dem regulären Ende und Socket-Schließen Erfolgscode 0; eine vorherige Ausnahme erreicht diese Zeile nicht. |
| 26 | Definiert die CLI-Einstiegsfunktion, die Eingaben prüft und serve aufruft. |
| 27 | Erstellt den Optionsparser mit der Modulbeschreibung als Hilfetext. |
| 28 | Bietet --host als lokale Bindeadresse an; Standard 10.0.0.2 gehört zur Standardtopologie des PDFs. |
| 29 | Liest --port als ganze Zahl; 5000 ist Standard, die Bereichsprüfung erfolgt später. |
| 30 | Liest --count als ganze Zahl; Standard null bedeutet bis Timeout oder Abbruch, nicht null Nachrichten. |
| 31 | Liest --timeout als Fließkommazahl in Sekunden; Standard ist 300 Sekunden pro Socketoperation. |
| 32 | Wertet die echte Kommandozeile aus; unbekannte Optionen und falsche Typen ergeben bereits argparse-Fehler. |
| 33 | Verwirft Ports außerhalb 0..65535 und negative Empfangszahlen; Serverport null bleibt für Tests erlaubt. |
| 34 | Beendet bei diesem Eingabefehler mit Erklärung und argparse-Status 2, bevor ein Socket erzeugt wird. |
| 35 | Verwirft NaN, Unendlich, null und negative Timeouts, damit das Warten definiert und begrenzt bleibt. |
| 36 | Meldet den ungültigen Timeout als CLI-Fehler mit Status 2. |
| 37 | Beginnt den Bereich, in dem erwartete Socketfehler und Tastaturabbruch in kurze Exitcodes übersetzt werden. |
| 38 | Ruft serve mit genau den geprüften CLI-Werten auf und reicht dessen Erfolgscode weiter. |
| 39 | Fängt Betriebssystem-/Socketfehler ab, einschließlich Bindefehlern und des TimeoutError-Untertyps. |
| 40 | Schreibt die echte Fehlerursache auf stderr, getrennt von READY und Empfangsmeldungen. |
| 41 | Liefert Fehlerstatus 1; ein Server-Timeout ist hier kein normaler Erfolg. |
| 42 | Fängt Strg+C gesondert ab, statt dafür einen langen Python-Traceback zu zeigen. |
| 43 | Gibt für diesen Tastaturabbruch Status 130 zurück; der with-Block hat den Socket bereits geschlossen. |
| 46 | Startet die CLI nur bei direktem Aufruf, nicht beim Import durch andere Python-Dateien. |
| 47 | Führt main aus und übergibt dessen Rückgabewert als echten Prozessstatus an die Shell. |

## client.py

| Zeile | Was geschieht und warum? |
|---:|---|
| 1 | Kommentar dokumentiert KI-Werkzeug, Modell und Datum; keine Netzwerkaktion. |
| 2 | Kommentar benennt die gewünschte frei wählbare UTF-8-Nachricht als Implementierungsauftrag. |
| 3 | Kommentar nennt Standardziel und Diagnoseausgabe; tatsächliche Werte werden erst später gesetzt bzw. gemessen. |
| 4 | Modulbeschreibung stellt klar: Es wird ein Datagramm gesendet, keine Antwort erwartet. |
| 6 | Lädt argparse für Ziel, Nachricht und optionale Quellbindung über die Kommandozeile. |
| 7 | Lädt socket für den wirklichen IPv4-UDP-Socket. |
| 8 | Lädt sys für stderr und die Rückgabe des Exitcodes an die Shell. |
| 11 | Definiert send; 0.0.0.0 erlaubt freie lokale Adresswahl und Quellport 0 lässt den Kernel einen Port wählen. |
| 12 | Kodiert den Unicode-Text ausdrücklich in UTF-8; ein Socket sendet Bytes, keine Python-str-Objekte. |
| 13 | Vergleicht die kodierte Bytezahl mit dem Empfangslimit des eigenen Servers, nicht die Zeichenanzahl. |
| 14 | Verwirft zu große Nutzlast mit ValueError vor dem Öffnen eines Sockets; verhindert stilles Abschneiden beim eigenen Empfänger. |
| 15 | Öffnet einen IPv4-UDP-Socket und lässt ihn beim Verlassen des with-Blocks automatisch schließen. |
| 16 | Setzt drei Sekunden Timeout für blockierende Socketoperationen; es folgt trotzdem kein Warten auf eine Serverantwort. |
| 17 | Reserviert die gewünschte lokale Adresse/Port-Kombination. Nichtlokale Adressen oder belegte Ports führen zu Fehlern. |
| 18 | Legt bei UDP den Standardpartner fest und lässt die Route/Quelladresse wählen; send kann dadurch ohne erneutes Ziel arbeiten. Es gibt keinen Handshake oder Erreichbarkeitsbeweis. |
| 19 | Sendet die Nutzbytes als ein Datagramm an den zuvor festgelegten Partner und merkt die gemeldete Bytezahl. |
| 20 | Vergleicht gesendete und gewünschte Bytezahl; auch null Bytes sind für eine leere Nachricht korrekt. |
| 21 | Behandelt eine unerwartet unvollständige Sendemeldung als Fehler, statt Erfolg zu behaupten. |
| 22 | Fragt die nach bind/connect tatsächlich verwendete lokale Adresse und den Quellport ab; das sind keine geratenen Sollwerte. |
| 23 | Gibt Quelle, Ziel, Bytezahl und Byte-Repräsentation aus; flush macht die Meldung sofort sichtbar. SENT bedeutet nicht, dass der entfernte Server schon empfangen hat. |
| 24 | Liefert Erfolgscode 0, nachdem der eigene Socket geschlossen wurde und send keinen Fehler meldete. |
| 27 | Definiert den CLI-Einstieg, getrennt von send, damit die Sendefunktion direkt testbar ist. |
| 28 | Erzeugt die CLI mit der Modulbeschreibung als Hilfe. |
| 29 | Bietet --host als entferntes Ziel an, standardmäßig h2 mit 10.0.0.2; beim lokalen Test ausdrücklich überschreiben. |
| 30 | Bietet den ganzzahligen Zielport an, standardmäßig 5000 passend zum Server. |
| 31 | Bietet die Textnachricht an; die Standardzeichenfolge ist noch Unicode und wird erst in send kodiert. |
| 32 | Bietet --local-host für die Quellbindung an; 0.0.0.0 bindet nicht an einen bestimmten lokalen IPv4-Endpunkt. |
| 33 | Bietet --local-port an; null fordert einen dynamischen Quellport an und ist kein UDP-Zielport. |
| 34 | Liest Optionen und Werte der tatsächlichen Kommandozeile ein. |
| 35 | Erlaubt Zielports 1..65535, Quellports 0..65535; der Sonderwert null ist nur für die lokale Auswahl erlaubt. |
| 36 | Stoppt bei falschen Portwerten mit erklärender argparse-Meldung und Exitcode 2. |
| 37 | Beginnt die Fehlerbehandlung um die echte Sendefunktion. |
| 38 | Übergibt Ziel, Text und Quellbindung in der richtigen Reihenfolge an send und reicht dessen Status weiter. |
| 39 | Fängt Netzwerk-/Betriebssystemfehler und ValueError ab; auch UnicodeEncodeError ist ein ValueError-Untertyp. |
| 40 | Meldet den konkreten Fehler auf stderr, statt eine erfolgreiche SENT-Meldung zu erfinden. |
| 41 | Liefert bei diesen Fehlern Status 1 an den Aufrufer zurück. |
| 44 | Verhindert einen automatischen CLI-Aufruf beim Import, etwa in test_udp.py. |
| 45 | Führt main beim direkten Start aus und setzt den Prozess-Exitcode auf dessen Ergebnis. |

## test_udp.py

| Zeile | Was geschieht und warum? |
|---:|---|
| 1 | Herkunftskommentar mit KI-Werkzeug, Modell und Datum; keine Testausführung. |
| 2 | Kommentar nennt echte lokale UDP-Sockets als Testgegenstand, nicht Mininet. |
| 3 | Kommentar listet die Grenzfälle, die die nachfolgenden Tests tatsächlich untersuchen. |
| 4 | Modulbeschreibung beschränkt die Tests auf selbst erzeugten lokalen UDP-Verkehr. |
| 6 | Lädt contextlib, um Sendefunktionsausgaben während eines Tests gezielt umzuleiten. |
| 7 | Lädt io für StringIO, also einen Textpuffer statt sichtbarer Konsolenausgabe. |
| 8 | Lädt Path, damit Server-/Client-Dateien relativ zur Testdatei gefunden werden. |
| 9 | Lädt selectors zum begrenzten Warten auf Serverausgabe statt einer geratenen Startpause. |
| 10 | Lädt socket für einen echten unabhängigen UDP-Testempfänger auf Loopback. |
| 11 | Lädt subprocess zum Start der tatsächlichen Server- und Client-CLIs als eigene Prozesse. |
| 12 | Lädt sys, um dafür denselben Pythoninterpreter wie im Test zu verwenden. |
| 13 | Lädt unittest für Testentdeckung, Vergleiche und den Testläufer. |
| 15 | Importiert den eigenen Client; wegen dessen __main__-Schutz wird dabei kein Datagramm gesendet. |
| 17 | Bestimmt den Ordner der aufgelösten Testdatei, damit Unterprozesse die richtigen Programme finden. |
| 20 | Definiert eine unittest-Testklasse; ihre test_-Methoden sind getrennte Prüffälle. |
| 21 | Definiert den Nutzlasttest für ASCII, Mehrbyte-UTF-8, leeren Text und die exakt erlaubte Bytegrenze. |
| 22 | Öffnet einen echten UDP-Empfänger unabhängig vom eigenen server.py; with sorgt für das Schließen. |
| 23 | Bindet nur auf Loopback und lässt Port 0 direkt vom Kernel reservieren; vermeidet Portkollisionen. |
| 24 | Begrenzt den späteren Empfang auf zwei Sekunden, damit ein defekter Client den Test nicht endlos blockiert. |
| 25 | Liest den tatsächlich reservierten Port für den folgenden Aufruf des Clients aus. |
| 26 | Durchläuft vier Nachrichten: Normaltext, Umlaute/Emoji, leerer String und 4096 ASCII-Bytes. Die letzte Nachricht liegt genau am Limit. |
| 27 | Leitet die Diagnoseausgabe von client.send in einen Wegwerfpuffer um, damit die Testausgabe lesbar bleibt. |
| 28 | Sendet tatsächlich an den Testempfänger und verlangt Rückgabewert 0; das allein ersetzt die folgenden Empfangsprüfungen nicht. |
| 29 | Empfängt ein echtes Datagramm mit großem Puffer und dessen Absender; prüft nicht bloß einen Mock-Aufruf. |
| 30 | Vergleicht alle empfangenen Bytes mit der unabhängigen UTF-8-Kodierung des Textes; erfasst auch leere und maximale Nutzlast. |
| 31 | Verlangt Loopback als tatsächliche Absenderadresse; der dynamische Quellport muss nicht einen festen Wert haben. |
| 33 | Definiert den Überlängentest; sein Name nennt die beabsichtigte Ablehnung vor der Socketerzeugung. |
| 34 | Verlangt ValueError aus dem folgenden Aufruf; ohne diese Ausnahme schlägt der Test fehl. |
| 35 | Versucht 2049 ä-Zeichen zu senden; jedes braucht zwei UTF-8-Bytes, deshalb übersteigt die Nutzlast das Limit. Die Reihenfolge vor socket ist im Quelltext sichtbar, nicht zusätzlich durch Mock geprüft. |
| 37 | Definiert einen Integrationstest der beiden echten Kommandozeilen mit drei Datagrammen. |
| 38 | Beginnt den Serverprozess mit demselben Interpreter und -B gegen Bytecode-Dateien; bindet ausdrücklich auf Loopback, nicht auf eine Laboradresse. |
| 39 | Ergänzt Kernel-Portwahl, drei erwartete Datagramme und drei Sekunden Empfangstimeout, damit der Server automatisch endet. |
| 40 | Erfasst stdout und stderr getrennt als Text; dadurch kann der Test READY und Fehlerursachen untersuchen. |
| 41 | Beginnt einen try/finally-Bereich, damit der gestartete Server auch bei Testfehlern beendet wird. |
| 42 | Sichert ab, dass die ausdrücklich angeforderte stdout-Pipe existiert, bevor sie verwendet wird. |
| 43 | Öffnet einen Selector als kurzlebige Ressource für das Bereitschaftswarten. |
| 44 | Registriert die Serverausgabe als lesbares Ereignis; wartet auf tatsächliche Ausgabe statt einer festen Pause. |
| 45 | Verlangt innerhalb von drei Sekunden ein Leseereignis; das kann auch EOF sein, weshalb danach noch der Inhalt geprüft wird. |
| 46 | Liest die erste Ausgabezeile und entfernt Rand-Leerraum; erwartet anschließend die READY-Meldung. |
| 47 | Prüft den READY-Präfix samt Loopback-Adresse; eine Fehlermeldung oder leere Ausgabe genügt nicht. |
| 48 | Trennt am letzten Doppelpunkt den realen Port ab; bleibt als Text direkt für die Client-CLI verwendbar. |
| 49 | Sendet nacheinander Normaltext, UTF-8 und leeren Text über drei eigenständige Clientprozesse. |
| 50 | Beginnt den echten Clientaufruf mit demselben Interpreter, -B und Loopback-Ziel. |
| 51 | Übergibt den zuvor gelesenen Port und genau einen Nachrichtentext; erfasst Ausgabe und begrenzt die Gesamtlaufzeit auf drei Sekunden. |
| 52 | Verlangt Client-Exitcode 0; bei Fehlschlag erscheint dessen echtes stderr als Diagnose. |
| 53 | Verlangt die erwartete UTF-8-Byte-Repräsentation in SENT, damit die ausgegebenen Nutzbytes überprüft werden. |
| 54 | Wartet höchstens vier Sekunden auf das selbstständige Serverende und sammelt dessen restliche Ausgaben. READY wurde zuvor schon gelesen. |
| 55 | Verlangt Server-Exitcode 0 und zeigt sonst dessen Fehlerkanal als Diagnose. |
| 56 | Verlangt genau drei Empfangsmeldungen in der restlichen Serverausgabe; nicht nur drei erfolgreiche Clientstarts. |
| 57 | Prüft, dass das leere Datagramm als b'' sichtbar war und nicht wie TCP-EOF behandelt wurde. |
| 58 | Beginnt die garantierte Prozessbereinigung, auch wenn vorher eine Assertion fehlgeschlagen ist. |
| 59 | Fragt ab, ob der Server noch läuft; bereits beendete Prozesse sollen nicht erneut signalisiert werden. |
| 60 | Sendet dem noch laufenden eigenen Testserver eine normale Beendigungsanforderung. |
| 61 | Wartet begrenzt auf sein Ende und leert/schließt die Pipes; bei weiterem Hängen wird ein Timeout sichtbar, es gibt hier keinen kill-Fallback. |
| 63 | Definiert die Prüfung ungültiger CLI-Werte ohne erfolgreichen Netzwerkbetrieb. |
| 64 | Startet die Fallliste mit verbotenem Zielport 0 des Clients und negativem Client-Quellport. |
| 65 | Ergänzt negative Empfangszahl und NaN-Timeout des Servers; NaN lässt sich zwar als float parsen, ist aber unzulässig. |
| 66 | Ergänzt Timeout null und schließt die Fallliste; alle Fälle durchlaufen denselben Prozess-/Statuscheck. |
| 67 | Startet für den jeweiligen Fall das reale Skript; *arguments entfaltet die Optionen als einzelne Argumente, ohne Shell. |
| 68 | Erfasst Textausgaben und begrenzt jeden Fehlerfall auf drei Sekunden, damit auch fehlerhafte Validierung nicht hängt. |
| 69 | Verlangt argparse-Status 2; ein späterer Netzwerkfehler mit Status 1 würde den Test nicht bestehen. |
| 71 | Definiert die Prüfung, dass ein bereiter Server ohne eingehendes Datagramm wirklich in den Empfangstimeout läuft. |
| 72 | Startet dafür einen echten Server mit Loopback-Adresse und demselben Pythoninterpreter. |
| 73 | Verlangt einen freien Port, ein Datagramm und nur 0.05 Sekunden Wartezeit; es wird absichtlich kein Client gestartet. |
| 74 | Erfasst stdout/stderr und begrenzt die gesamte Unterprozesslaufzeit auf drei Sekunden. |
| 75 | Verlangt Fehlerstatus 1, den main bei einem Sockettimeout zurückgeben soll. |
| 76 | Prüft vorherige READY-Ausgabe; ein Bindefehler wäre sonst fälschlich als erfolgreicher Timeouttest interpretierbar. |
| 77 | Verlangt die tatsächliche Timeoutdiagnose auf stderr, nicht irgendeinen beliebigen Serverfehler. |
| 80 | Startet die Tests nur bei direktem Aufruf der Datei, nicht beim Import. |
| 81 | Lässt unittest die Testmethoden ausführen und zeigt mit verbosity=2 jeden Testnamen sowie den echten Gesamterfolg/-fehlschlag. |

## Nachweise und Grenzen

[test_udp.txt](test_udp.txt) dokumentiert lokale Tests. [udp-clients.txt](../nachweise/run01/udp-clients.txt), [udp-server.txt](../nachweise/run01/udp-server.txt) und [udp.pcap](../nachweise/run01/udp.pcap) gehören zum zusätzlichen echten Namespace-/Linux-Bridge-Lauf. [Die Capture-Erklärung](../ue4.4/erklaerung.md) beschreibt dessen Byteprüfung. Das sind keine Mininet-, OVS- oder xterm-Läufe; diese bleiben nicht ausgeführt. Wireshark wurde dagegen tatsächlich für die gespeicherten PCAPs verwendet. Tests, gespeicherte Messung und Anleitung sind drei verschiedene Dinge.

## KI-Kennzeichnung

Hermes Agent / OpenAI gpt-6.1-sol / 2026-10-29. Tatsächliche Anfrage: jede nichtleere Quellzeile von server.py, client.py und test_udp.py anhand ihrer echten Semantik in einfacher Sprache erklären; nur Dokumentation ändern, originale Programme und Nachweise unverändert lassen.
