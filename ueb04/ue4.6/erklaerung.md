# Zeilenerklärung zu Ü 4.6

Jede Zeile der vier ausgelieferten Python-Dateien ist unten mit ihrer tatsächlichen Zeilennummer aufgeführt, einschließlich Kommentaren und Leerzeilen.

Die allgemeinen Abläufe, Protokollregeln und CLI-Beispiele stehen in `antwort.md`. Die Test-Assertions sind ausführbare Sollwerte, keine erfundenen Ausgaben.

## protocol.py

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 2 | <code># Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 3 | <code># Auftrag: Ü4.6 TCP-Protokoll für einzelne und persistente UTF-8-Nachrichten</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 4 | <code># mit LF-Framing, Fragmentierung, Coalescing, EOF und Größenlimit implementieren.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 5 | <code>"""Kleines Echo-Protokoll: UTF-8-Text (maximal 4096 Bytes), dann ein LF-Byte."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 6 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 7 | <code>MAX_FRAME_BYTES = 4096</code> | Maximale UTF-8-Nutzlast pro Nachricht, ohne das LF-Trennbyte. |
| 8 | <code>RECV_BYTES = 1024</code> | Obergrenze jedes recv-Aufrufs; keine erwartete Nachrichtenlänge. |
| 9 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 10 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 11 | <code>class ProtocolError(ValueError):</code> | Eigener ValueError-Untertyp für klar unterscheidbare Protokollfehler. |
| 12 | <code>    """Der Peer oder die Eingabe verletzt das vereinbarte Nachrichtenformat."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 13 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 14 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 15 | <code>def encode_frame(text):</code> | Validiert ausgehenden Text und erzeugt die UTF-8-Bytes einschließlich LF. |
| 16 | <code>    """Prüfe ausgehenden Text und hänge genau einen Frame-Abschluss an."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 17 | <code>    if "\n" in text:</code> | Verbietet LF innerhalb einer Nachricht, damit das Trennzeichen eindeutig bleibt. |
| 18 | <code>        raise ProtocolError("Eingebettetes LF ist nicht erlaubt")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 19 | <code>    try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 20 | <code>        payload = text.encode("utf-8")</code> | Kodiert Unicode-Text in sendbare UTF-8-Bytes; dabei können ungültige Surrogate auffallen. |
| 21 | <code>    except UnicodeEncodeError as error:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 22 | <code>        raise ProtocolError("Text ist nicht als UTF-8 kodierbar") from error</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen. from error bewahrt die ursprüngliche Kodier-/Dekodierexception als Ursache. |
| 23 | <code>    if len(payload) &gt; MAX_FRAME_BYTES:</code> | Prüft die Bytezahl der kodierten Nutzlast, nicht die Anzahl der Zeichen. |
| 24 | <code>        raise ProtocolError("Frame überschreitet 4096 Nutzbytes")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 25 | <code>    return payload + b"\n"</code> | Hängt genau das LF-Abschlussbyte an und liefert den sendbaren Frame. |
| 26 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 27 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 28 | <code>def iter_frames(connection):</code> | Ein Generator: liest begrenzte Byteblöcke und liefert vollständige Texte einzeln mit yield. |
| 29 | <code>    """Liefere vollständige Texte; nur EOF zwischen Frames ist regulär."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 30 | <code>    pending = bytearray()</code> | Veränderbarer Puffer für noch nicht vollständig verarbeitete Empfangsbytes. |
| 31 | <code>    while True:</code> | Empfängt weiter, bis reguläres EOF ein return auslöst oder ein Fehler abbricht. |
| 32 | <code>        chunk = connection.recv(RECV_BYTES)</code> | Liest bis zu 1024 Streambytes; weniger Bytes und zusammengefasste Nachrichten sind erlaubt. |
| 33 | <code>        if not chunk:</code> | Nur b"" bedeutet EOF: die Gegenseite hat ihre Senderichtung beendet. |
| 34 | <code>            if pending:</code> | Verbleibende Bytes bei EOF wären ein nicht LF-abgeschlossener Frame. |
| 35 | <code>                raise ProtocolError("EOF in unvollständigem Frame (LF fehlt)")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 36 | <code>            return</code> | Beendet den Generator regulär ohne weiteres Ergebnis: EOF genau zwischen Frames. |
| 37 | <code>        pending.extend(chunk)</code> | Hängt neue Empfangsbytes an den Rest des vorigen recv an. |
| 38 | <code>        while b"\n" in pending:</code> | Verarbeitet alle vollständigen Frames, auch mehrere aus einem recv. |
| 39 | <code>            end = pending.index(b"\n")</code> | Bestimmt die erste Framegrenze; Bytes davor bilden genau eine Nutzlast. |
| 40 | <code>            if end &gt; MAX_FRAME_BYTES:</code> | Verwirft einen vollständigen, aber zu langen Frame vor der UTF-8-Dekodierung. |
| 41 | <code>                raise ProtocolError("Frame überschreitet 4096 Nutzbytes")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 42 | <code>            payload = bytes(pending[:end])</code> | Kopiert die Nutzbytes ohne das Trenn-LF in ein unveränderliches bytes-Objekt. |
| 43 | <code>            del pending[:end + 1]</code> | Entfernt den entnommenen Frame einschließlich LF; weitere Frames bleiben im Puffer. |
| 44 | <code>            try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 45 | <code>                text = payload.decode("utf-8", errors="strict")</code> | Dekodiert erst den vollständigen Frame; ungültige UTF-8-Sequenzen werden nicht ersetzt. |
| 46 | <code>            except UnicodeDecodeError as error:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 47 | <code>                raise ProtocolError("Frame enthält ungültiges UTF-8") from error</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen. from error bewahrt die ursprüngliche Kodier-/Dekodierexception als Ursache. |
| 48 | <code>            yield text</code> | Liefert genau einen vollständigen Text; beim nächsten next läuft der Generator hier weiter. |
| 49 | <code>        if len(pending) &gt; MAX_FRAME_BYTES:</code> | Begrenzt auch unvollständige Frames ohne LF, damit der Puffer nicht unbegrenzt wächst. |
| 50 | <code>            raise ProtocolError("Frame überschreitet 4096 Nutzbytes")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |

## server.py

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 2 | <code># Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 3 | <code># Auftrag: Ü4.6 TCP-Echo-Server auf 10.0.2.2:5000 mit persistenten Nachrichten,</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 4 | <code># READY-Ausgabe, CLI, begrenzten Verbindungen, Timeouts und sauberem Schließen.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 5 | <code>"""Sequentieller IPv4-TCP-Server; ein Client nach dem anderen, ohne Threads."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 6 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 7 | <code>import argparse</code> | Importiert argparse aus der Python-Standardbibliothek zum Parsen der Kommandozeile. |
| 8 | <code>import math</code> | Importiert math aus der Python-Standardbibliothek für die Prüfung auf endliche Timeout-Werte. |
| 9 | <code>import socket</code> | Importiert socket aus der Python-Standardbibliothek für echte IPv4-TCP-Sockets. |
| 10 | <code>import sys</code> | Importiert sys aus der Python-Standardbibliothek für Exitcodes und stderr. |
| 11 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 12 | <code>from protocol import ProtocolError, encode_frame, iter_frames</code> | Importiert ProtocolError, encode_frame, iter_frames aus dem gemeinsamen eigenen Protokollmodul. |
| 13 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 14 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 15 | <code>def serve(host, port, connections, timeout):</code> | Betreibt den sequentiellen Listener und zählt angenommene Verbindungen. |
| 16 | <code>    """Zähle angenommene Verbindungen; 0 bedeutet Betrieb bis Timeout/Abbruch."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 17 | <code>    failed = False</code> | Merkt, ob irgendeine angenommene Verbindung einen Fehler hatte. |
| 18 | <code>    accepted = 0</code> | Zähler für alle angenommenen Verbindungen, einschließlich fehlerhafter oder leerer. |
| 19 | <code>    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:</code> | Erzeugt einen echten IPv4-TCP-Socket im Kontextmanager; close erfolgt bei jedem Verlassen des Blocks. |
| 20 | <code>        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)</code> | Erleichtert den erneuten Serverstart nach früheren Verbindungen; ersetzt keinen laufenden Listener. |
| 21 | <code>        listener.settimeout(timeout)</code> | Begrenzt blockierendes accept auf dem Listener. |
| 22 | <code>        listener.bind((host, port))</code> | Bindet an die gewünschte lokale IPv4-Adresse und den Port; 0 lässt den Kernel wählen. |
| 23 | <code>        listener.listen(5)</code> | Aktiviert den TCP-Listener; 5 ist der gewünschte Backlog für wartende Verbindungen. |
| 24 | <code>        address, actual_port = listener.getsockname()</code> | Liest die tatsächliche Bindung aus, insbesondere den gewählten Port bei --port 0. |
| 25 | <code>        print(f"READY {address}:{actual_port}", flush=True)</code> | Meldet Bereitschaft erst nach listen und leert den Ausgabepuffer sofort. |
| 26 | <code>        while connections == 0 or accepted &lt; connections:</code> | Nimmt bis zur gewünschten Anzahl Verbindungen an; 0 hebt nur das Zähllimit auf. |
| 27 | <code>            connection, peer = listener.accept()</code> | Liefert einen neuen verbundenen Socket und die Clientadresse; der Listener bleibt bestehen. |
| 28 | <code>            accepted += 1</code> | Zählt die gerade angenommene Verbindung genau einmal. |
| 29 | <code>            with connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 30 | <code>                connection.settimeout(timeout)</code> | Begrenzt blockierende Socket-Operationen; beim Client auch connect, anschließend recv und sendall. |
| 31 | <code>                try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 32 | <code>                    for text in iter_frames(connection):</code> | Verarbeitet bis EOF beliebig viele vollständige Nachrichten derselben Verbindung. |
| 33 | <code>                        print(f"RECEIVED {peer[0]}:{peer[1]} {text!r}", flush=True)</code> | Zeigt Client-IP, Clientport und Textrepräsentation; auch leerer Text bleibt erkennbar. |
| 34 | <code>                        connection.sendall(encode_frame(text))</code> | Sendet den geprüften Text unverändert als LF-kodiertes Echo; sendall behandelt partielle Sends. |
| 35 | <code>                    connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 36 | <code>                except (OSError, ProtocolError) as error:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 37 | <code>                    failed = True</code> | Merkt den Verbindungsfehler, ohne die gewünschte Annahme weiterer Clients abzubrechen. |
| 38 | <code>                    print(f"ERROR connection: {error}", file=sys.stderr, flush=True)</code> | Protokolliert den Fehler separat auf stderr und leert den Puffer sofort. |
| 39 | <code>    return 1 if failed else 0</code> | Erfolg nur, wenn keine angenommene Verbindung fehlgeschlagen ist. |
| 40 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 41 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 42 | <code>def main():</code> | CLI-Einstieg: Argumente auswerten, validieren, ausführen und passenden Exitcode zurückgeben. |
| 43 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erstellt den CLI-Parser; der Modul-Docstring wird zum Hilfetext. |
| 44 | <code>    parser.add_argument("--host", default="10.0.2.2")</code> | Definiert die lokale Bindeadresse beim Server bzw. die Zieladresse beim Client; Standard ist die Lab-Serveradresse 10.0.2.2. |
| 45 | <code>    parser.add_argument("--port", type=int, default=5000, help="0: freier Testport")</code> | Definiert den ganzzahligen TCP-Port; Standard ist 5000, die jeweilige Bereichsprüfung folgt nach parse_args. |
| 46 | <code>    parser.add_argument("--connections", type=int, default=0, help="0: unbegrenzt")</code> | Definiert die Zahl anzunehmender Serververbindungen; 0 bedeutet keine feste Anzahl. |
| 47 | <code>    parser.add_argument("--timeout", type=float, default=30.0, help="Sekunden pro Socket-Operation")</code> | Definiert den Fließkomma-Timeout in Sekunden pro Socket-Operation; Standard sind 30 Sekunden. |
| 48 | <code>    args = parser.parse_args()</code> | Liest und typisiert die tatsächlichen Kommandozeilenargumente. |
| 49 | <code>    if not 0 &lt;= args.port &lt;= 65535 or args.connections &lt; 0:</code> | Server erlaubt Port 0..65535 und nur nichtnegative Verbindungszahlen. |
| 50 | <code>        parser.error("Port muss 0..65535, connections muss &gt;= 0 sein")</code> | Bricht die CLI mit dieser Fehlermeldung und dem argparse-Exitcode 2 ab. |
| 51 | <code>    if not math.isfinite(args.timeout) or args.timeout &lt;= 0:</code> | Verwirft NaN, Unendlich, Null und negative Timeout-Werte. |
| 52 | <code>        parser.error("Timeout muss endlich und positiv sein")</code> | Bricht die CLI mit dieser Fehlermeldung und dem argparse-Exitcode 2 ab. |
| 53 | <code>    try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 54 | <code>        return serve(args.host, args.port, args.connections, args.timeout)</code> | Startet den Server mit den geprüften CLI-Werten und übernimmt dessen Exitcode. |
| 55 | <code>    except OSError as error:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 56 | <code>        print(f"ERROR server: {error}", file=sys.stderr)</code> | Meldet Listener-/Bind-/Accept-Fehler ohne Python-Traceback. |
| 57 | <code>        return 1</code> | Liefert den Fehler-Exitcode für Netzwerk-/Protokollprobleme. |
| 58 | <code>    except KeyboardInterrupt:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 59 | <code>        return 130</code> | Kennzeichnet den sauberen Tastaturabbruch; with-Kontexte schließen vorher offene Sockets. |
| 60 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 61 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 62 | <code>if __name__ == "__main__":</code> | Führt den Einstieg nur bei direktem Programmstart aus, nicht beim Import. |
| 63 | <code>    sys.exit(main())</code> | Gibt den von main zurückgelieferten Status an die aufrufende Shell weiter. |

## client.py

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 2 | <code># Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 3 | <code># Auftrag: Ü4.6 TCP-Client für eine oder mehrere CLI-Nachrichten implementieren;</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 4 | <code># Echo-Antworten prüfen, UTF-8/LF-Limits beachten und mit Half-Close/FIN schließen.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 5 | <code>"""Sende Nachrichten in einer TCP-Verbindung und prüfe jedes Echo exakt."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 6 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 7 | <code>import argparse</code> | Importiert argparse aus der Python-Standardbibliothek zum Parsen der Kommandozeile. |
| 8 | <code>import math</code> | Importiert math aus der Python-Standardbibliothek für die Prüfung auf endliche Timeout-Werte. |
| 9 | <code>import socket</code> | Importiert socket aus der Python-Standardbibliothek für echte IPv4-TCP-Sockets. |
| 10 | <code>import sys</code> | Importiert sys aus der Python-Standardbibliothek für Exitcodes und stderr. |
| 11 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 12 | <code>from protocol import ProtocolError, encode_frame, iter_frames</code> | Importiert ProtocolError, encode_frame, iter_frames aus dem gemeinsamen eigenen Protokollmodul. |
| 13 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 14 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 15 | <code>def exchange(host, port, messages, timeout=30.0):</code> | Validiert alle Nachrichten, verbindet sich einmal und prüft die Echo-Antworten. |
| 16 | <code>    """Request/Response vermeidet volle Sendepuffer bei vielen Nachrichten."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 17 | <code>    frames = [encode_frame(text) for text in messages]</code> | Validiert alle ausgehenden Nachrichten vor connect und merkt deren Sendebytes. |
| 18 | <code>    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:</code> | Erzeugt einen echten IPv4-TCP-Socket im Kontextmanager; close erfolgt bei jedem Verlassen des Blocks. |
| 19 | <code>        connection.settimeout(timeout)</code> | Begrenzt blockierende Socket-Operationen; beim Client auch connect, anschließend recv und sendall. |
| 20 | <code>        connection.connect((host, port))</code> | Baut die TCP-Verbindung zum Server auf; der Kernel erledigt den Three-Way Handshake. |
| 21 | <code>        replies = iter_frames(connection)</code> | Erstellt einen gemeinsamen Antwort-Generator, dessen Restpuffer über alle Nachrichten erhalten bleibt. |
| 22 | <code>        for expected, frame in zip(messages, frames):</code> | Ordnet jedem ursprünglichen Text seinen bereits geprüften Sendeframe zu. |
| 23 | <code>            connection.sendall(frame)</code> | Sendet alle Bytes genau dieser Anfrage oder meldet einen Fehler. |
| 24 | <code>            actual = next(replies, None)</code> | Liest genau einen vollständigen Antworttext; None steht für EOF ohne Antwort, nicht für leeren Text. |
| 25 | <code>            if actual != expected:</code> | Vergleicht Echo und Original exakt; fehlende und abweichende Antworten sind Fehler. |
| 26 | <code>                raise ProtocolError(f"Echo falsch/fehlend: erwartet {expected!r}, erhalten {actual!r}")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 27 | <code>            print(f"REPLY {actual!r}", flush=True)</code> | Zeigt nur eine bereits erfolgreich geprüfte Antwort. |
| 28 | <code>        connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 29 | <code>        if next(replies, None) is not None:</code> | Wartet nach dem Half-Close auf Server-EOF und verwirft jede zusätzliche Nachricht. |
| 30 | <code>            raise ProtocolError("Unerwartete zusätzliche Antwort")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 31 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 32 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 33 | <code>def main():</code> | CLI-Einstieg: Argumente auswerten, validieren, ausführen und passenden Exitcode zurückgeben. |
| 34 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erstellt den CLI-Parser; der Modul-Docstring wird zum Hilfetext. |
| 35 | <code>    parser.add_argument("messages", nargs="+", help="Ein Argument = eine Nachricht; leerer Text: ''")</code> | Verlangt mindestens ein Positionsargument; jedes Argument ist genau eine Nachricht, auch ein ausdrücklich übergebener leerer String. |
| 36 | <code>    parser.add_argument("--host", default="10.0.2.2")</code> | Definiert die lokale Bindeadresse beim Server bzw. die Zieladresse beim Client; Standard ist die Lab-Serveradresse 10.0.2.2. |
| 37 | <code>    parser.add_argument("--port", type=int, default=5000)</code> | Definiert den ganzzahligen TCP-Port; Standard ist 5000, die jeweilige Bereichsprüfung folgt nach parse_args. |
| 38 | <code>    parser.add_argument("--timeout", type=float, default=30.0, help="Sekunden pro Socket-Operation")</code> | Definiert den Fließkomma-Timeout in Sekunden pro Socket-Operation; Standard sind 30 Sekunden. |
| 39 | <code>    args = parser.parse_args()</code> | Liest und typisiert die tatsächlichen Kommandozeilenargumente. |
| 40 | <code>    if not 1 &lt;= args.port &lt;= 65535:</code> | Ein Clientziel benötigt einen tatsächlichen Port 1..65535, nicht den Reservierungswert 0. |
| 41 | <code>        parser.error("Port muss 1..65535 sein")</code> | Bricht die CLI mit dieser Fehlermeldung und dem argparse-Exitcode 2 ab. |
| 42 | <code>    if not math.isfinite(args.timeout) or args.timeout &lt;= 0:</code> | Verwirft NaN, Unendlich, Null und negative Timeout-Werte. |
| 43 | <code>        parser.error("Timeout muss endlich und positiv sein")</code> | Bricht die CLI mit dieser Fehlermeldung und dem argparse-Exitcode 2 ab. |
| 44 | <code>    try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 45 | <code>        exchange(args.host, args.port, args.messages, args.timeout)</code> | Führt den tatsächlichen Clientaustausch mit den geprüften CLI-Werten aus. |
| 46 | <code>        return 0</code> | Liefert den Erfolgs-Exitcode nach vollständigem geprüftem Austausch. |
| 47 | <code>    except (OSError, ProtocolError) as error:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 48 | <code>        print(f"ERROR client: {error}", file=sys.stderr)</code> | Meldet Empfangs-, Verbindungs- und Protokollfehler ohne Traceback. |
| 49 | <code>        return 1</code> | Liefert den Fehler-Exitcode für Netzwerk-/Protokollprobleme. |
| 50 | <code>    except KeyboardInterrupt:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 51 | <code>        return 130</code> | Kennzeichnet den sauberen Tastaturabbruch; with-Kontexte schließen vorher offene Sockets. |
| 52 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 53 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 54 | <code>if __name__ == "__main__":</code> | Führt den Einstieg nur bei direktem Programmstart aus, nicht beim Import. |
| 55 | <code>    sys.exit(main())</code> | Gibt den von main zurückgelieferten Status an die aufrufende Shell weiter. |

## test_tcp.py

| Zeile | Quelltext | Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung: Hermes Agent; OpenAI gpt-6.1-sol.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 2 | <code># Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 3 | <code># Auftrag: Eigene echte stdlib-unittest-Tests für Ü4.6 TCP erstellen und ausführen:</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 4 | <code># Fragmentierung, Coalescing, Limits, Fehler, Verbindungen, UTF-8, leerer Text, CLI/EOF.</code> | KI-Kennzeichnung: dokumentiert Tool/Modell, Provider/Datum bzw. den tatsächlichen Auftrag; keine Laufzeitwirkung. |
| 5 | <code>"""Deterministische Parser-Tests plus echte IPv4-TCP-Sockets und CLI-Prozesse."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 6 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 7 | <code>from pathlib import Path</code> | Importiert Path aus der Python-Standardbibliothek. |
| 8 | <code>import selectors</code> | Importiert selectors aus der Python-Standardbibliothek für ereignisgesteuertes Warten auf READY. |
| 9 | <code>import socket</code> | Importiert socket aus der Python-Standardbibliothek für echte IPv4-TCP-Sockets. |
| 10 | <code>import subprocess</code> | Importiert subprocess aus der Python-Standardbibliothek für echte Server-/Client-Unterprozesse. |
| 11 | <code>import sys</code> | Importiert sys aus der Python-Standardbibliothek für Exitcodes und stderr. |
| 12 | <code>import threading</code> | Importiert threading aus der Python-Standardbibliothek für die absichtlich fehlerhaften Test-Peers. |
| 13 | <code>import unittest</code> | Importiert unittest aus der Python-Standardbibliothek für Testklassen, Assertions und den Testläufer. |
| 14 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 15 | <code>from protocol import MAX_FRAME_BYTES, RECV_BYTES, ProtocolError, encode_frame, iter_frames</code> | Importiert MAX_FRAME_BYTES, RECV_BYTES, ProtocolError, encode_frame, iter_frames aus dem gemeinsamen eigenen Protokollmodul. |
| 16 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 17 | <code>HERE = Path(__file__).resolve().parent</code> | Bestimmt das Testverzeichnis relativ zur Testdatei; unabhängig vom aufrufenden Arbeitsverzeichnis. |
| 18 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 19 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 20 | <code>class ChunkSocket:</code> | Kleiner Testdouble zur deterministischen Kontrolle der recv-Grenzen. |
| 21 | <code>    """Erzwingt recv-Grenzen unabhängig von TCP-Segmentierung und Scheduling."""</code> | Docstring: beschreibt Zweck und Vertrag des Moduls, der Klasse oder Funktion im Quelltext. |
| 22 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 23 | <code>    def __init__(self, chunks):</code> | Initialisiert den deterministischen Empfangs-Testdouble mit vorgegebenen Blöcken. |
| 24 | <code>        self.chunks = iter(chunks)</code> | Speichert einen Iterator über die vorbereiteten recv-Blöcke. |
| 25 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 26 | <code>    def recv(self, limit):</code> | Imitiert recv: liefert den nächsten vorbereiteten Block und prüft das angeforderte Byte-Limit. |
| 27 | <code>        chunk = next(self.chunks, b"")</code> | Gibt den nächsten Testblock zurück; nach dem letzten Block wird EOF simuliert. |
| 28 | <code>        if len(chunk) &gt; limit or limit != RECV_BYTES:</code> | Der Testdouble prüft, dass keine recv-Obergrenze überschritten oder unerwartet geändert wurde. |
| 29 | <code>            raise AssertionError("recv-Limit nicht eingehalten")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 30 | <code>        return chunk</code> | Liefert den vorbereiteten Empfangsblock an den echten Protokollparser. |
| 31 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 32 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 33 | <code>class FramingTests(unittest.TestCase):</code> | unittest-Testklasse für den Protokollparser ohne Netzwerk-Scheduling. |
| 34 | <code>    def test_fragmentation_including_utf8_and_empty(self):</code> | Prüft byteweise Fragmentierung einschließlich Mehrbyte-UTF-8 und leerem Frame. |
| 35 | <code>        chunks = [bytes([byte]) for byte in "Grüße 🌍\n\nEnde\n".encode("utf-8")]</code> | Zerteilt die UTF-8-Übertragung in einzelne Bytes, sogar innerhalb von ü, ß und Emoji. |
| 36 | <code>        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["Grüße 🌍", "", "Ende"])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 37 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 38 | <code>    def test_coalescing_and_remaining_partial_frame(self):</code> | Prüft mehrere Frames in einem recv und die Übernahme des unvollständigen Rests. |
| 39 | <code>        chunks = [b"one\n\ntw", b"o\nthree", b"\n"]</code> | Drei Empfangsblöcke enthalten vier Frames, einen leeren Frame und zwei aufgeteilte Texte. |
| 40 | <code>        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["one", "", "two", "three"])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 41 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 42 | <code>    def test_exact_limit(self):</code> | Prüft die maximal erlaubte Nutzlast von 4096 Bytes mit Mehrbytezeichen. |
| 43 | <code>        wire = encode_frame("ä" * (MAX_FRAME_BYTES // 2))</code> | 2048 Zweibytezeichen ergeben genau 4096 Nutzbytes; LF kommt zusätzlich hinzu. |
| 44 | <code>        chunks = [wire[i:i + RECV_BYTES] for i in range(0, len(wire), RECV_BYTES)]</code> | Zerteilt den Grenzframe in erlaubte recv-Blockgrößen. |
| 45 | <code>        self.assertEqual(list(iter_frames(ChunkSocket(chunks))), ["ä" * 2048])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 46 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 47 | <code>    def test_outgoing_invalid(self):</code> | Prüft das Verwerfen von LF im Text, Überlänge und ungültigem Unicode-Surrogat. |
| 48 | <code>        for text in ("a\nb", "x" * 4097, "ä" * 2049, "\ud800"):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 49 | <code>            with self.subTest(text_kind=repr(text[:8])):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 50 | <code>                with self.assertRaises(ProtocolError):</code> | Dieser Testblock muss ProtocolError auslösen; ohne diese Ausnahme schlägt der Test fehl. |
| 51 | <code>                    encode_frame(text)</code> | Ruft den echten Encoder innerhalb von assertRaises auf; ungültiger Text muss ProtocolError auslösen. |
| 52 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 53 | <code>    def test_invalid_frames_and_truncated_eof(self):</code> | Prüft ungültiges UTF-8 und fehlendes Abschluss-LF bei EOF. |
| 54 | <code>        for chunks in ([b"\xff\n"], [b"\xc3\n"], [b"missing LF"], [b"\xc3"]):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 55 | <code>            with self.subTest(chunks=chunks):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 56 | <code>                with self.assertRaises(ProtocolError):</code> | Dieser Testblock muss ProtocolError auslösen; ohne diese Ausnahme schlägt der Test fehl. |
| 57 | <code>                    list(iter_frames(ChunkSocket(chunks)))</code> | Verbraucht den echten Framegenerator vollständig; der umgebende Test erwartet dabei einen Protokollfehler. |
| 58 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 59 | <code>    def test_oversized_with_and_without_lf(self):</code> | Prüft die Überschreitung des Byte-Limits mit und ohne abschließendes LF. |
| 60 | <code>        for ending in (b"", b"\n"):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 61 | <code>            chunks = [b"x" * RECV_BYTES] * 4 + [b"x" + ending]</code> | Vier volle Blöcke plus ein zusätzliches Nutzbyte überschreiten die erlaubten 4096 Bytes. |
| 62 | <code>            with self.subTest(ending=ending):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 63 | <code>                with self.assertRaises(ProtocolError):</code> | Dieser Testblock muss ProtocolError auslösen; ohne diese Ausnahme schlägt der Test fehl. |
| 64 | <code>                    list(iter_frames(ChunkSocket(chunks)))</code> | Verbraucht den echten Framegenerator vollständig; der umgebende Test erwartet dabei einen Protokollfehler. |
| 65 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 66 | <code>    def test_empty_stream_is_not_empty_message(self):</code> | Unterscheidet einen leeren Stream von einer leeren, LF-kodierten Nachricht. |
| 67 | <code>        self.assertEqual(list(iter_frames(ChunkSocket([]))), [])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 68 | <code>        self.assertEqual(encode_frame(""), b"\n")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 69 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 70 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 71 | <code>class TCPTests(unittest.TestCase):</code> | unittest-Testklasse mit echten lokalen IPv4-TCP-Verbindungen und CLI-Prozessen. |
| 72 | <code>    def start_server(self, count=1, timeout=2.0):</code> | Startet einen echten Serverprozess auf Port 0 und liest seine tatsächliche READY-Meldung. |
| 73 | <code>        command = [sys.executable, "-B", "server.py", "--host", "127.0.0.1",</code> | Baut die echte Server-CLI mit Loopback-Adresse, Kernel-Portwahl, Verbindungszahl und Timeout. |
| 74 | <code>                   "--port", "0", "--connections", str(count), "--timeout", str(timeout)]</code> | Fortsetzung der Anweisung aus Zeile 73: Baut die echte Server-CLI mit Loopback-Adresse, Kernel-Portwahl, Verbindungszahl und Timeout. |
| 75 | <code>        process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE,</code> | Startet den echten Server-Unterprozess mit getrennten stdout-/stderr-Pipes im Testverzeichnis. |
| 76 | <code>                                   stderr=subprocess.PIPE, text=True)</code> | Fortsetzung der Anweisung aus Zeile 75: Startet den echten Server-Unterprozess mit getrennten stdout-/stderr-Pipes im Testverzeichnis. |
| 77 | <code>        self.addCleanup(self.cleanup_process, process)</code> | Registriert Prozessbereinigung sofort nach Start, auch wenn später eine Assertion fehlschlägt. |
| 78 | <code>        assert process.stdout is not None</code> | PIPE garantiert stdout; die Assertion dokumentiert dies auch für statische Typprüfer. |
| 79 | <code>        with selectors.DefaultSelector() as selector:</code> | Öffnet einen Betriebssystem-Selector und schließt ihn am Blockende auch bei Fehlern. |
| 80 | <code>            selector.register(process.stdout, selectors.EVENT_READ)</code> | Wartet auf echte Ausgabeaktivität statt auf eine geschätzte Startverzögerung. |
| 81 | <code>            self.assertTrue(selector.select(5), "Keine READY-Ausgabe innerhalb von 5 s")</code> | Verlangt eine wahre Bedingung (hier echte READY-Bereitschaft); andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 82 | <code>        ready = process.stdout.readline().strip()</code> | Liest die erste vollständige READY-Zeile und entfernt deren Zeilenumbruch. |
| 83 | <code>        self.assertRegex(ready, r"^READY 127\.0\.0\.1:[1-9][0-9]*$")</code> | Prüft, dass die echte Ausgabe zum angegebenen regulären Ausdruck passt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 84 | <code>        return process, int(ready.rsplit(":", 1)[1])</code> | Gibt Prozess und den tatsächlich gebundenen Port für spätere Clientaufrufe zurück. |
| 85 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 86 | <code>    def cleanup_process(self, process):</code> | Beendet einen eventuell verbliebenen Server und schließt seine Prozess-Pipes. |
| 87 | <code>        if process.poll() is None:</code> | Nur ein noch laufender eigener Testprozess muss beendet werden. |
| 88 | <code>            process.kill()</code> | Notfallbereinigung eines hängen gebliebenen eigenen Testservers, kein normaler Protokollabbau. |
| 89 | <code>        process.communicate(timeout=5)</code> | Wartet begrenzt auf Prozessende und leert stdout/stderr, damit keine Pipes offen bleiben. |
| 90 | <code>        process.stdout.close()</code> | Schließt die lokale stdout-Pipe des Testprozesses. |
| 91 | <code>        process.stderr.close()</code> | Schließt die lokale stderr-Pipe des Testprozesses. |
| 92 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 93 | <code>    def finish_server(self, process, expected_code=0):</code> | Wartet begrenzt auf Serverende und prüft dessen tatsächlichen Exitcode. |
| 94 | <code>        stdout, stderr = process.communicate(timeout=5)</code> | Sammelt echte Prozessausgaben und wartet höchstens fünf Sekunden auf das Ende. |
| 95 | <code>        self.assertEqual(process.returncode, expected_code, stderr)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 96 | <code>        return stdout, stderr</code> | Gibt die tatsächlichen Ausgaben an den Test für zusätzliche Assertions weiter. |
| 97 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 98 | <code>    def connect(self, port):</code> | Öffnet eine echte lokale TCP-Verbindung und registriert close als Test-Aufräumaktion. |
| 99 | <code>        connection = socket.create_connection(("127.0.0.1", port), timeout=2)</code> | Baut eine echte Loopback-TCP-Verbindung mit begrenzter Wartezeit auf. |
| 100 | <code>        self.addCleanup(connection.close)</code> | Schließt den Testsocket auch beim Fehlschlagen des Tests. |
| 101 | <code>        return connection</code> | Gibt den bereits verbundenen Socket zurück. |
| 102 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 103 | <code>    def run_client(self, port, *messages, timeout="2"):</code> | Führt die echte Client-CLI mit den übergebenen Nachrichten und begrenzter Laufzeit aus. |
| 104 | <code>        return subprocess.run([sys.executable, "-B", "client.py", "--host", "127.0.0.1",</code> | Startet die echte Client-CLI im Testverzeichnis; -- trennt Nachrichten von Optionen. stdout/stderr und Exitcode werden erfasst, die Gesamtlaufzeit ist begrenzt. |
| 105 | <code>                               "--port", str(port), "--timeout", timeout, "--", *messages],</code> | Fortsetzung der Anweisung aus Zeile 104: Startet die echte Client-CLI im Testverzeichnis; -- trennt Nachrichten von Optionen. stdout/stderr und Exitcode werden erfasst, die Gesamtlaufzeit ist begrenzt. |
| 106 | <code>                              cwd=HERE, text=True, capture_output=True, timeout=5)</code> | Fortsetzung der Anweisung aus Zeile 104: Startet die echte Client-CLI im Testverzeichnis; -- trennt Nachrichten von Optionen. stdout/stderr und Exitcode werden erfasst, die Gesamtlaufzeit ist begrenzt. |
| 107 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 108 | <code>    def test_real_tcp_fragmented_writes(self):</code> | Prüft byteweise Schreibaufrufe über echte TCP-Sockets; TCP darf sie zusammenfassen. |
| 109 | <code>        process, port = self.start_server()</code> | Startet einen echten Server mit einer erwarteten Verbindung auf einem vom Kernel gewählten Port. |
| 110 | <code>        with self.connect(port) as connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 111 | <code>            for byte in "Grüße 🌍\n".encode("utf-8"):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 112 | <code>                connection.sendall(bytes([byte]))</code> | Schreibt ein einzelnes Byte auf TCP; der Kernel darf mehrere solcher Writes zusammenfassen. |
| 113 | <code>            connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 114 | <code>            self.assertEqual(list(iter_frames(connection)), ["Grüße 🌍"])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 115 | <code>            self.assertEqual(connection.recv(1), b"")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 116 | <code>        stdout, stderr = self.finish_server(process)</code> | Prüft erfolgreiches Serverende und übernimmt die tatsächlich erfassten Serverausgaben. |
| 117 | <code>        self.assertIn("'Grüße 🌍'", stdout)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 118 | <code>        self.assertEqual(stderr, "")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 119 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 120 | <code>    def test_real_tcp_coalesced_and_exact_limit(self):</code> | Prüft mehrere zusammen gesendete Frames einschließlich Grenzlänge über echte TCP-Sockets. |
| 121 | <code>        process, port = self.start_server()</code> | Startet einen echten Server mit einer erwarteten Verbindung auf einem vom Kernel gewählten Port. |
| 122 | <code>        messages = ["one", "", "ä" * 2048, "last"]</code> | Testdaten enthalten normalen Text, leeren Text, maximale Byte-Länge und einen folgenden Frame. |
| 123 | <code>        with self.connect(port) as connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 124 | <code>            connection.sendall(b"".join(encode_frame(text) for text in messages))</code> | Sendet mehrere vollständige Anwendungsframes in einem einzigen sendall-Aufruf. |
| 125 | <code>            connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 126 | <code>            self.assertEqual(list(iter_frames(connection)), messages)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 127 | <code>        self.finish_server(process)</code> | Prüft, dass der Server nach der geplanten Verbindungszahl erfolgreich endet. |
| 128 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 129 | <code>    def test_cli_single_persistent_and_multiple_connections(self):</code> | Prüft drei echte CLI-Verbindungen: Einzeltext, persistente Texte und abschließender Einzeltext. |
| 130 | <code>        process, port = self.start_server(count=3)</code> | Plant drei getrennte Verbindungen zu demselben Listener. |
| 131 | <code>        for messages in (("single",), ("eins", "Grüße 🌍", ""), ("last",)):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 132 | <code>            result = self.run_client(port, *messages)</code> | Startet die echte Client-CLI mit einem oder mehreren Textargumenten. |
| 133 | <code>            self.assertEqual(result.returncode, 0, result.stderr)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 134 | <code>            self.assertEqual(result.stdout.splitlines(), [f"REPLY {text!r}" for text in messages])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 135 | <code>        stdout, stderr = self.finish_server(process)</code> | Prüft erfolgreiches Serverende und übernimmt die tatsächlich erfassten Serverausgaben. |
| 136 | <code>        self.assertEqual(stdout.count("RECEIVED "), 5)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 137 | <code>        self.assertEqual(stderr, "")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 138 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 139 | <code>    def test_empty_connection_then_valid_connection(self):</code> | Prüft eine Verbindung ohne Frame und danach einen weiter funktionierenden Server. |
| 140 | <code>        process, port = self.start_server(count=2)</code> | Der Server soll zwei Verbindungen nacheinander annehmen und sich danach beenden. |
| 141 | <code>        with self.connect(port) as connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 142 | <code>            connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 143 | <code>            self.assertEqual(connection.recv(1), b"")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 144 | <code>        result = self.run_client(port, "still alive")</code> | Prüft eine gültige CLI-Anfrage nach einer vorherigen Verbindung ohne Frames. |
| 145 | <code>        self.assertEqual(result.returncode, 0, result.stderr)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 146 | <code>        self.finish_server(process)</code> | Prüft, dass der Server nach der geplanten Verbindungszahl erfolgreich endet. |
| 147 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 148 | <code>    def test_real_tcp_invalid_frames_and_recovery(self):</code> | Prüft echte fehlerhafte TCP-Frames und eine erfolgreiche Folgeverbindung. |
| 149 | <code>        payloads = [b"\xff\n", b"partial", b"\xc3\n", b"x" * 4097, b"x" * 4097 + b"\n"]</code> | Echte Fehlerdaten: defektes UTF-8, EOF ohne LF, abgeschnittenes UTF-8 und zwei Überlängenfälle. |
| 150 | <code>        for payload in payloads:</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 151 | <code>            with self.subTest(length=len(payload), prefix=repr(payload[:8])):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 152 | <code>                process, port = self.start_server(count=2)</code> | Der Server soll zwei Verbindungen nacheinander annehmen und sich danach beenden. |
| 153 | <code>                with self.connect(port) as connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 154 | <code>                    connection.sendall(payload)</code> | Sendet absichtlich fehlerhafte Bytes direkt, ohne den ausgehenden Validator. |
| 155 | <code>                    connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 156 | <code>                    try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 157 | <code>                        self.assertEqual(connection.recv(1), b"")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 158 | <code>                    except ConnectionResetError:</code> | Fängt genau die angegebenen Ausnahmetypen ab; andere Programmierfehler werden nicht verschluckt. |
| 159 | <code>                        pass</code> | Akzeptiert hier ausschließlich den erwarteten TCP-Reset nach einem absichtlich ungültigen Frame; reguläre Tests erwarten EOF. |
| 160 | <code>                result = self.run_client(port, "after error")</code> | Eine zweite echte Verbindung muss nach dem Protokollfehler weiterhin funktionieren. |
| 161 | <code>                self.assertEqual(result.returncode, 0, result.stderr)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 162 | <code>                stdout, stderr = self.finish_server(process, expected_code=1)</code> | Erwartet einen gemeldeten Serverfehler und erfasst dessen echte Diagnose. |
| 163 | <code>                self.assertIn("ERROR connection:", stderr)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 164 | <code>                self.assertIn("'after error'", stdout)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 165 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 166 | <code>    def test_server_accept_timeout(self):</code> | Prüft das begrenzte Warten des Listeners ohne eintreffenden Client. |
| 167 | <code>        process, unused_port = self.start_server(timeout=0.15)</code> | Startet einen Listener, der ohne Verbindungsversuch nach 0,15 Sekunden scheitern soll. |
| 168 | <code>        stdout, stderr = self.finish_server(process, expected_code=1)</code> | Erwartet einen gemeldeten Serverfehler und erfasst dessen echte Diagnose. |
| 169 | <code>        self.assertIn("ERROR server:", stderr)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 170 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 171 | <code>    def test_server_connection_timeout(self):</code> | Prüft den Empfangs-Timeout eines verbundenen, aber stillen Clients. |
| 172 | <code>        process, port = self.start_server(timeout=0.15)</code> | Startet einen Server mit kurzem Timeout für einen verbundenen, stillen Client. |
| 173 | <code>        with self.connect(port) as connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 174 | <code>            self.assertEqual(connection.recv(1), b"")</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 175 | <code>        stdout, stderr = self.finish_server(process, expected_code=1)</code> | Erwartet einen gemeldeten Serverfehler und erfasst dessen echte Diagnose. |
| 176 | <code>        self.assertIn("ERROR connection:", stderr)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 177 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 178 | <code>    def test_client_rejects_bad_missing_extra_or_silent_reply(self):</code> | Prüft den Client gegen falsche, zusätzliche, fehlende, defekte und ausbleibende Antworten. |
| 179 | <code>        for response in (b"wrong\n", b"first\nextra\n", b"", b"\xff\n", b"first", None):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 180 | <code>            with self.subTest(response=response):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 181 | <code>                errors = []</code> | Sammelt Exceptions des Test-Peer-Threads zur Prüfung im Hauptthread. |
| 182 | <code>                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:</code> | Erzeugt einen echten IPv4-TCP-Socket im Kontextmanager; close erfolgt bei jedem Verlassen des Blocks. |
| 183 | <code>                    listener.bind(("127.0.0.1", 0))</code> | Reserviert einen freien Port direkt im Listener; kein Rennen zwischen Portsuchen und Binden. |
| 184 | <code>                    listener.listen(1)</code> | Erwartet genau die eine Clientverbindung des jeweiligen Fehlertests. |
| 185 | <code>                    listener.settimeout(3)</code> | Begrenzt auch den Test-Peer, falls der Client gar keine Verbindung aufbaut. |
| 186 | <code>                    port = listener.getsockname()[1]</code> | Ermittelt den tatsächlichen freien Port des Test-Peers. |
| 187 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 188 | <code>                    def peer():</code> | Absichtlich fehlerhafter, aber echter TCP-Gegenpeer für die Client-Fehlerprüfungen. |
| 189 | <code>                        try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 190 | <code>                            connection, address = listener.accept()</code> | Nimmt die echte Verbindung der getesteten Client-CLI an. |
| 191 | <code>                            with connection:</code> | Verwaltet den verbundenen Socket im Kontextmanager; er wird bei normalem Ende und bei Fehlern geschlossen. |
| 192 | <code>                                connection.settimeout(3)</code> | Verhindert unbegrenztes Warten im fehlerhaften Test-Peer. |
| 193 | <code>                                request = bytearray()</code> | Sammelt den echten Request unabhängig vom zu testenden Frameparser. |
| 194 | <code>                                while not request.endswith(b"\n"):</code> | Liest den erwarteten einzelnen Request bis zu dessen LF-Abschluss. |
| 195 | <code>                                    data = connection.recv(1024)</code> | Liest echte TCP-Requestbytes in höchstens 1024 Byte großen Blöcken. |
| 196 | <code>                                    if not data:</code> | EOF vor dem Abschluss wäre ein unerwartet früh schließender Client. |
| 197 | <code>                                        raise AssertionError("Client sendete keinen vollständigen Request")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 198 | <code>                                    request.extend(data)</code> | Hängt das nächste Requestfragment an. |
| 199 | <code>                                if bytes(request) != b"first\n":</code> | Kontrolliert den Request mit einem unabhängigen, fest vorgegebenen Byte-Sollwert. |
| 200 | <code>                                    raise AssertionError("Falscher Request")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 201 | <code>                                if response is not None:</code> | None modelliert einen schweigenden Server; b"" modelliert dagegen EOF ohne Antwort. |
| 202 | <code>                                    connection.sendall(response)</code> | Sendet die absichtlich gewählte echte Fehlerantwort des Test-Peers. |
| 203 | <code>                                    connection.shutdown(socket.SHUT_WR)</code> | Schließt nur die eigene Senderichtung (normalerweise FIN); Empfang bleibt bis close möglich. |
| 204 | <code>                                if connection.recv(1) != b"":</code> | Prüft, dass der Client seine Senderichtung nach Erfolg oder Fehler tatsächlich beendet. |
| 205 | <code>                                    raise AssertionError("Client hat nicht geschlossen")</code> | Löst die hier benannte Ausnahme mit erklärender Diagnose aus; with-Kontexte schließen dabei Ressourcen.  |
| 206 | <code>                        except Exception as error:</code> | Fängt auch Assertions und Netzwerkfehler im Test-Thread ab; sie werden in errors gesammelt und anschließend im Hauptthread geprüft, nicht ignoriert. |
| 207 | <code>                            errors.append(error)</code> | Überträgt einen Threadfehler an die anschließende Assertion im Test-Hauptthread. |
| 208 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 209 | <code>                    thread = threading.Thread(target=peer)</code> | Erstellt den lokalen Test-Peer-Thread; der eigentliche Übungsserver bleibt sequentiell. |
| 210 | <code>                    thread.start()</code> | Startet den Test-Peer vor dem Client; der Listener ist bereits gebunden und aktiv. |
| 211 | <code>                    try:</code> | Beginnt den geschützten Abschnitt für die folgenden except-/finally-Zweige. |
| 212 | <code>                        result = self.run_client(port, "first", timeout="0.3")</code> | Startet die echte Client-CLI mit kurzem Timeout gegen den absichtlich fehlerhaften Peer. |
| 213 | <code>                    finally:</code> | Der folgende Aufräumabschnitt läuft unabhängig von Erfolg oder Ausnahme. |
| 214 | <code>                        thread.join(4)</code> | Wartet auch bei Clientfehlern begrenzt auf das Ende des Test-Peer-Threads. |
| 215 | <code>                    self.assertFalse(thread.is_alive(), "Test-Peer hängt")</code> | Verlangt eine falsche Bedingung (hier keinen noch lebenden Peer-Thread); andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 216 | <code>                    self.assertEqual(errors, [])</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 217 | <code>                    self.assertEqual(result.returncode, 1, result.stdout)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 218 | <code>                    self.assertIn("ERROR client:", result.stderr)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 219 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 220 | <code>    def test_cli_rejects_bad_arguments_and_payloads(self):</code> | Prüft CLI-Werte und das Verwerfen ungültiger ausgehender Texte noch vor connect. |
| 221 | <code>        for script, arguments in (("server.py", ["--connections", "-1"]),</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 222 | <code>                                  ("server.py", ["--port", "65536"]),</code> | Fortsetzung der Anweisung aus Zeile 221: Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 223 | <code>                                  ("client.py", ["--port", "0", "x"]),</code> | Fortsetzung der Anweisung aus Zeile 221: Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 224 | <code>                                  ("client.py", ["--timeout", "nan", "x"]),</code> | Fortsetzung der Anweisung aus Zeile 221: Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 225 | <code>                                  ("server.py", ["--timeout", "0"]),</code> | Fortsetzung der Anweisung aus Zeile 221: Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 226 | <code>                                  ("client.py", [])):</code> | Fortsetzung der Anweisung aus Zeile 221: Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 227 | <code>            with self.subTest(script=script, arguments=arguments):</code> | Markiert einen einzelnen Parameterfall, damit ein Fehlschlag mit seinen konkreten Testdaten benannt wird. |
| 228 | <code>                result = subprocess.run([sys.executable, "-B", script, *arguments], cwd=HERE,</code> | Führt einen echten CLI-Unterprozess aus und erfasst Exitcode und Ausgaben mit Gesamtlaufzeitlimit. |
| 229 | <code>                                        text=True, capture_output=True, timeout=3)</code> | Fortsetzung der Anweisung aus Zeile 228: Führt einen echten CLI-Unterprozess aus und erfasst Exitcode und Ausgaben mit Gesamtlaufzeitlimit. |
| 230 | <code>                self.assertEqual(result.returncode, 2)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 231 | <code>        for text in ("a\nb", "x" * 4097):</code> | Durchläuft die hier angegebenen Testdaten; jeder Fall prüft dieselbe Eigenschaft mit anderen Eingaben. |
| 232 | <code>            result = self.run_client(1, text)</code> | Ungültiger Text soll vor connect abgewiesen werden; Port 1 wird nicht kontaktiert. |
| 233 | <code>            self.assertEqual(result.returncode, 1)</code> | Prüft exakte Gleichheit der ersten beiden Argumente; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 234 | <code>            self.assertIn("ERROR client:", result.stderr)</code> | Verlangt, dass der erste Wert im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 235 | <code>            self.assertNotIn("Connection refused", result.stderr)</code> | Verlangt, dass der erste Wert nicht im zweiten vorkommt; andernfalls scheitert der Test. Der letzte optionale Wert ist die Fehlerdiagnose. |
| 236 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 237 | <code></code> | Leerzeile zur Gliederung; keine Laufzeitwirkung. |
| 238 | <code>if __name__ == "__main__":</code> | Führt den Einstieg nur bei direktem Programmstart aus, nicht beim Import. |
| 239 | <code>    unittest.main()</code> | Startet die unittest-Testentdeckung und setzt den passenden Prozess-Exitcode. |

## KI-Kennzeichnung

Hermes Agent; OpenAI gpt-6.1-sol; Provider laut Hermes-Status: ChatGPT or Codex Subscription; Datum 2026-10-29. Auftrag: alle eigenen Ü4.6-Codezeilen mit tatsächlichen Zeilennummern erklären und die Übungsprogramme mit echten lokalen Tests prüfen.
