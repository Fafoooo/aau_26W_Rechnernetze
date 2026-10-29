# Ü 4.6 – TCP-Client und TCP-Server

## Umsetzung und Protokoll

`server.py` erzeugt einen IPv4-Stream-Socket (`AF_INET`, `SOCK_STREAM`), bindet
standardmäßig **10.0.2.2:5000**, startet `listen()`, nimmt Verbindungen mit
`accept()` an, empfängt Nachrichten, gibt sie aus und sendet den Text unverändert
als Echo zurück. `client.py` verwendet dieselbe Standard-Zieladresse, verbindet
sich mit `connect()`, sendet über `sendall()` und **prüft jedes Echo exakt**.
Der Server bedient bewusst einen Client nach dem anderen, ohne Threads oder
Framework. Mehrere nacheinander ankommende Verbindungen sind möglich.

Das Anwendungsprotokoll in `protocol.py` ist in beiden Richtungen identisch:

- Eine Nachricht ist streng UTF-8-kodierter Text mit anschließendem **LF-Byte
  `0a`**. Im Text selbst ist LF nicht erlaubt; CR wird nicht speziell behandelt.
- Eine Nachricht enthält höchstens **4096 Nutzbytes**, ohne das abschließende LF.
  Die Grenze zählt Bytes, nicht Unicode-Zeichen: `ä` benötigt zwei UTF-8-Bytes.
- Auch leerer Text ist erlaubt: `b"\n"` ist eine Nachricht mit Länge null.
  Hingegen bedeutet `recv()` mit Rückgabewert `b""` EOF, nicht eine leere Nachricht.
- `recv(1024)` liefert höchstens 1024 Bytes. Ein Puffer sammelt Fragmente,
  extrahiert **alle** vorhandenen LF-Frames und behält den unvollständigen Rest.
  Erst ein vollständiger Frame wird streng als UTF-8 dekodiert, sodass auch ein
  zwischen zwei `recv()`-Aufrufen aufgeteiltes Mehrbytezeichen funktioniert.
- Der Puffer wird pro Empfang um höchstens 1024 Bytes erweitert. Nach Extraktion
  vollständiger Frames darf der Rest höchstens 4096 Bytes groß sein. Auch ein
  vollständiger Frame wird vor dem Dekodieren auf seine Länge geprüft.
- Ungültiges UTF-8, zu große Frames und EOF mit einem unvollständigen Rest sind
  Protokollfehler. Der Server protokolliert sie auf stderr und schließt die
  betroffene Verbindung; er kann danach die nächste annehmen. Es gibt keinen
  speziellen Fehler-Antwortframe. Bei solchen Fehlerabbrüchen ist abhängig von
  noch ungelesenen Daten auch ein TCP-RST möglich; nur für den normalen Ablauf
  wird der geordnete FIN-Abbau beschrieben.

Der Client sendet eine Nachricht und liest das passende Echo, bevor er die nächste
sendet. Das vermeidet, dass bei sehr vielen Nachrichten beide Seiten gleichzeitig
mit vollen Sendepuffern blockieren. Nach dem letzten geprüften Echo ruft der Client
`shutdown(SHUT_WR)` auf: **Half-Close**, also keine weiteren eigenen Nutzdaten,
aber weiterhin Empfang. Der Server liest bis EOF, schließt dann ebenfalls seine
Senderichtung und beendet den Verbindungs-Socket. Der Client liest seinerseits
bis EOF; zusätzliche Antworten sind ein Fehler. Beide Programme verwenden
`with`-Blöcke, damit offene Sockets auch bei Exceptions geschlossen werden.

## Start und reproduzierbare lokale Tests

Alle folgenden Python-Befehle werden im Verzeichnis `ueb04/ue4.6` ausgeführt.
`-B` verhindert `__pycache__`-Dateien.

**Eine Nachricht pro Verbindung**, Serverterminal:

```sh
python3 -B server.py --host 127.0.0.1 --port 5000 --connections 1 --timeout 30
```

Nach `READY 127.0.0.1:5000`, Clientterminal:

```sh
python3 -B client.py --host 127.0.0.1 --port 5000 'Eine Nachricht'
```

**Mehrere Nachrichten in derselben Verbindung**, Server erneut starten:

```sh
python3 -B server.py --host 127.0.0.1 --port 5000 --connections 1 --timeout 30
python3 -B client.py --host 127.0.0.1 --port 5000 'eins' 'Grüße 🌍' ''
```

Die beiden Befehle gehören wieder in getrennte Terminals; der zweite wird erst
nach READY ausgeführt. Für zwei getrennte Clientläufe wird der Server mit
`--connections 2` gestartet. `--connections 0` (Standard) bedeutet unbegrenzt
viele Verbindungen, nicht unbegrenzte Wartezeit. `--timeout` ist eine positive,
endliche Zeit in Sekunden **pro blockierender Socket-Operation**, kein absoluter
Gesamtzeitgeber. Er gilt für `accept()`, Empfang und Senden; Standard: 30 Sekunden.
Der Client unterstützt dasselbe Timeout-Argument. Bei Timeouts wird beendet bzw.
die betroffene Verbindung geschlossen. Exitcodes: 0 Erfolg; 1 Netzwerk-, Timeout-
oder Protokollfehler; 2 ungültige CLI; 130 Tastaturabbruch. Hat eine angenommene
Verbindung einen Fehler, bedient der Server weitere verlangte Verbindungen und
liefert am Ende trotzdem Exitcode 1.

Mit `--port 0` wählt der **Server** einen freien temporären Port. Nach `listen()`
gibt er mit `flush=True` beispielsweise `READY 127.0.0.1:<echter-Port>` aus.
Diesen tatsächlichen Port anschließend beim Client mit `--port` einsetzen;
der Client akzeptiert keinen Zielport 0. Die Tests lesen READY automatisch,
statt einen freien Port vorher zu erraten oder mit festen Sleeps zu warten.
Nachrichten, die mit `-` beginnen, können nach `--` übergeben werden.

```sh
python3 -B -W error::ResourceWarning -m unittest -v test_tcp
```

Der tatsächliche Testlauf ist in `test_tcp.txt` festgehalten: **16 Tests erfolgreich,
Exitcode 0**. `cli_test.txt` enthält zusätzlich einen echten Serverlauf mit zwei
Verbindungen (Einzelnachricht und persistente Nachrichten einschließlich UTF-8 und
leerem Text), den tatsächlichen READY-Port sowie die Client-/Serverausgaben und
Exitcodes. Es werden Parser-Grenzfälle deterministisch mit einem kleinen
`recv()`-Testdouble erzwungen und
zusätzlich echte IPv4-TCP-Sockets auf Loopback sowie echte CLI-Unterprozesse
benutzt. Die Byte-für-Byte-Schreibvorgänge im Socket-Test garantieren nicht, dass
der Kernel dieselben `recv()`-Grenzen liefert; dafür gibt es ergänzend den
Fragmentierungstest mit vorgegebenen Empfangsblöcken. Kein Test behauptet eine
bestimmte TCP-Segmentzahl.

Geprüft werden: Fragmentierung einschließlich UTF-8, zusammengefasste Frames und
Pufferreste, leere Texte, EOF ohne Nachricht, EOF mitten im Frame, exakt 4096 Bytes,
4097 Bytes mit/ohne LF, ungültiges UTF-8, ausgehendes LF/Überlänge/Surrogat,
einzelne und persistente CLI-Nachrichten, mehrere Verbindungen, Weiterbetrieb nach
Protokollfehler, Accept-/Verbindungs-Timeouts, ungültige CLI-Argumente sowie falsche,
fehlende, zusätzliche, ungültige, abgeschnittene oder ausbleibende Antworten.
Die absichtlich fehlerhaften Test-Peers sind echte lokale TCP-Endpunkte, keine
angeblichen Mitschnitte. Reguläres Schließen wird durch tatsächlichen EOF-Empfang
auf den Sockets geprüft; Paket-Flags werden durch diese Tests nicht gemessen.

## Anleitung für die bereitgestellte RN-Lab-VM

Dieser Abschnitt ist eine **Ausführungsanleitung, kein behaupteter VM-Testlauf**.
Die Lab-Originaldateien bleiben unverändert. Mininet/OVS sind auf dem aktuellen
Ausführungshost nicht installiert; es wird nichts nachinstalliert. Bei Problemen
mit der vorbereiteten VM gemäß Angabe die Übungsleitung kontaktieren.

1. Repository in der bereitgestellten VM verfügbar machen. Dort im Verzeichnis
   `ueb04/Angabe` die vorgegebenen Prüfungen durchführen:

   ```sh
   sudo mn --version
   python3 --version
   python3 check_environment.py
   sudo python3 start_lab.py
   ```

2. `start_lab.py` öffnet Client-, Router- und Serverkonsolen. Anders als `sudo mn`
   wartet dieses Skript am Ende auf ENTER im Startterminal; deshalb dort erst
   ENTER drücken, wenn Server, Client und Capture beendet sind. In den jeweiligen
   Konsolen mit `ip addr`, `ip route` und `hostname` den tatsächlichen Kontext
   kontrollieren. Erwartet laut unveränderter Infrastruktur: Client `10.0.1.2/24`,
   Gateway `10.0.1.1`; Server `10.0.2.2/24`, Gateway `10.0.2.1`. Der Router hat
   beide Gateway-Adressen und aktiviertes IPv4-Forwarding.

3. In Client- und Serverkonsole ins Verzeichnis `ueb04/ue4.6` wechseln (absoluten
   VM-Checkoutpfad verwenden). Zuerst auf dem Client die Route prüfen:

   ```sh
   ping -c 4 10.0.2.2
   ```

4. In der Serverkonsole:

   ```sh
   python3 -B server.py --connections 2 --timeout 120
   ```

   READY muss `10.0.2.2:5000` melden. Bindung und tatsächlichen Port kontrollieren:
   `ss -ltn 'sport = :5000'`. `127.0.0.1` wäre hier nur der jeweilige eigene Host
   im eigenen Netzwerk-Namespace, nicht der entfernte Server.

5. Nach Start des unten beschriebenen Captures in der Clientkonsole:

   ```sh
   python3 -B client.py 'Einzelne Nachricht'
   python3 -B client.py 'eins' 'Grüße 🌍' ''
   ```

   Das sind zwei Verbindungen: eine mit einer Nachricht, eine mit drei Nachrichten.
   Die Clientausgaben zeigen `REPLY ...`, die Serverausgaben `RECEIVED ...`.
   Die beiden Verbindungen können unterschiedliche kurzlebige Clientports haben;
   der Serverport bleibt 5000. Der Server beendet sich nach beiden Verbindungen.

## Echten Mitschnitt erzeugen und in Wireshark untersuchen

Vor dem ersten Clientlauf im **Client-Namespace** auf `client-eth0` aufzeichnen,
nicht auf `any` und nicht auf einem fremden Netz. Nur selbst erzeugten Lab-Verkehr
mitschneiden. In der Clientkonsole nach Wahl eines neuen, noch nicht vorhandenen
Dateinamens (sonst anderen Namen verwenden):

```sh
tcpdump -i client-eth0 -n -s 0 -U -w tcp_ue46_vm.pcap 'tcp and host 10.0.1.2 and host 10.0.2.2 and port 5000' &
CAPTURE_PID=$!
```

Auf die echte Meldung `listening on client-eth0` warten. Dann die beiden oben
angegebenen Clientbefehle in derselben Konsole ausführen. **Nicht sofort danach
abbrechen:** `-U` leert den Dateiausgabepuffer, garantiert aber noch keine Übergabe
aller Pakete aus dem libpcap-Eingangspuffer. Erst wenn die FINs und Schluss-ACKs
tatsächlich angekommen sind, geordnet stoppen. Alternativ wie unser Zusatztest
einen begrenzten Capture regulär auslaufen lassen. Dann auf vollständiges Schreiben warten:

```sh
kill -INT "$CAPTURE_PID"
wait "$CAPTURE_PID"
```

Die Mininet-Hostkonsolen laufen bereits mit den nötigen Rechten. Falls das Capture
verweigert wird, die VM-Anleitung/Rechte prüfen lassen, nicht Schutzmechanismen
abschalten. Alternativ Wireshark im Client-Namespace öffnen und dort ausschließlich
`client-eth0` mit demselben Capture-Filter wählen. Einen gespeicherten Mitschnitt
kann man nach dem Capture mit Wireshark in der VM öffnen; alle Hosts teilen das
Dateisystem. Eine Untersuchung am Router müsste das dortige Interface wählen,
nicht den Interface-Namen des Clients.

In Wireshark zunächst Displayfilter `tcp.port == 5000` verwenden; dann für jede
Verbindung über **Analyze → Follow → TCP Stream** den konkreten Stream auswählen
und dessen `tcp.stream`-Nummer ablesen. Nicht annehmen, dass sie immer 0 ist.
Folgende **erwartete Muster am eigenen Mitschnitt verifizieren und die tatsächlichen
Paketnummern notieren**, nicht diese Anleitung als Messergebnis ausgeben:

| Phase | Filter / Beobachtung |
|---|---|
| Aufbau | `tcp.flags.syn == 1`; SYN vom Client und SYN/ACK vom Server suchen; danach das zugehörige Client-ACK anhand Stream, Richtung und Sequenz-/ACK-Nummern zuordnen. |
| Daten | `tcp.len > 0`; UTF-8-Nutzdaten und die LF-Abschlüsse in „Follow TCP Stream“ bzw. Packet Bytes prüfen. Ein Frame darf über mehrere Segmente verteilt sein. Nicht allein nach PSH suchen. |
| Abbau | `tcp.flags.fin == 1`; Client-FIN nach den Antworten, Server-ACK und Server-FIN sowie letztes Client-ACK zuordnen. ACK und FIN können kombiniert auftreten. |
| Fehlerkontrolle | `tcp.flags.reset == 1` zeigt RST; für den normalen eigenen Lauf keinen RST voraussetzen, sondern tatsächlich prüfen. |

Für den Einzelversuch einen Nachrichten-/Echo-Austausch und für den persistenten
Versuch mehrere über **denselben TCP-Stream mit demselben Vierertupel** nachweisen.
Die genaue Paketanzahl, Paketnummern, Zeitstempel und Clientports hängen vom echten
Lauf ab. Zusätzlich liegt jetzt ein **echter Linux-Namespace-Mitschnitt** vor:
`../nachweise/run01/tcp.pcap`, unabhängig byteweise geprüft in `tcp-analyse.json`
und in der echten Wireshark-GUI geöffnet (`wireshark-tcp.png`). Kein Mininet-/OVS-VM-Nachweis.

- Verbindung 10.0.1.2:**45216** → 10.0.2.2:5000: Handshake Pakete **1, 2, 3**;
  Nachricht **4**, Echo **6**; Client-FIN **8**, Server-FIN/ACK **9**, Schluss-ACK **10**.
- Verbindung 10.0.1.2:**45222** → 10.0.2.2:5000: Handshake **11, 12, 13**;
  drei Nachrichten **14, 18, 20**, Echos **16, 19, 21**;
  Client-FIN **22**, Server-FIN/ACK **23**, Schluss-ACK **24**.
- Die zweite Verbindung überträgt `eins`, `Grüße 🌍` und leeren Text jeweils mit LF.
  Der Parser rekonstruiert in beiden Richtungen den vollständigen identischen Bytestrom,
  prüft beide FIN-Bestätigungen und bestätigt: **kein RST**. Die dynamischen Ports sind
  nur Werte dieses Laufs. Die 24 Pakete stimmen mit dumpcaps tatsächlicher Zählung überein.

## Antworten auf die drei Fragen

### Welche drei Segmente bilden den TCP Three-Way Handshake?

1. **Client → Server: SYN**, mit initialer Client-Sequenznummer `x`.
2. **Server → Client: SYN + ACK**, eigene initiale Sequenznummer `y`,
   Bestätigung `ACK = x + 1`.
3. **Client → Server: ACK**, Bestätigung `ACK = y + 1` und im gewöhnlichen
   Fall Sequenznummer `x + 1`.

Ein SYN verbraucht jeweils eine Sequenznummer. Dadurch kennen beide Seiten die
Startsequenznummer der Gegenrichtung und bestätigen deren Empfang. Der Kernel
führt diesen Ablauf für `connect()` und den lauschenden Socket aus; Python muss
keine SYN-Segmente selbst bauen. `accept()` liefert einen **neuen verbundenen
Socket**; der Listener bleibt für weitere Verbindungen bestehen.

### Warum entspricht ein `recv()` nicht genau einer gesendeten Nachricht?

TCP transportiert einen zuverlässigen, geordneten **Bytestrom ohne
Anwendungs-Nachrichtengrenzen**. Eine `sendall()`-Operation kann in mehreren
`recv()`-Ergebnissen ankommen; umgekehrt kann ein `recv()` Bytes mehrerer
Sendeoperationen enthalten. Die angegebene Empfangsgröße ist eine Obergrenze,
keine Zusage, dass so viele Bytes geliefert werden. Selbst ein UTF-8-Zeichen kann
über Empfangsblöcke verteilt sein. Deshalb definiert diese Lösung LF-Framing und
sammelt Bytes bis zum Abschluss. Weitere Möglichkeiten wären ein Längenpräfix
oder ein festes Nachrichtenformat. EOF bezeichnet das Ende der Senderichtung;
ein nicht LF-abgeschlossener Rest bleibt in unserem Protokoll fehlerhaft.

### Welche Vorteile hat eine persistente Verbindung?

Mehrere Nachrichten benötigen nur **einen** Verbindungsaufbau und einen
Verbindungsabbau statt eines Handshakes und Abbaus pro Nachricht. Das reduziert
zusätzliche Roundtrips, Kontrollsegmente und Verwaltungsaufwand für Sockets und
TCP-Zustände. Eine bereits aufgebaute Verbindung kann außerdem ihre zuvor
gewachsene Congestion Window weiterverwenden. Das ist kein Versprechen einer
bestimmten Laufzeit oder Beschleunigung; unser einfacher Client wartet nach jeder
Nachricht weiterhin auf das Echo. Persistenz verlangt dafür klares Framing,
Fehlerbehandlung und eine Regel, wann der Stream endet. Ein lange wartender Client
blockiert in diesem absichtlich sequentiellen Beispiel andere Clients bis zum
Schließen oder Timeout; ein produktiver Mehrbenutzerserver bräuchte zusätzliche
Nebenläufigkeit und Ressourcenbegrenzungen.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**; Provider laut
Hermes-Status: **ChatGPT or Codex Subscription**. Datum: **2026-10-29**.
Tatsächlicher Auftrag, sinngemäß: „Implementiere Ü4.6 anhand der Originalangabe und
KI-Policy: einfach erklärbaren TCP-Server und -Client mit LF-framed UTF-8, einer
oder mehreren Nachrichten pro Verbindung, CLI, Timeouts, READY und sauberem
Half-Close; erstelle und führe eigene echte unittest-Tests aus. Beantworte alle
Fragen, dokumentiere VM-/Capture-Anleitung ohne erfundene Mitschnitte und erkläre
jede eigene Codezeile mit Zeilennummern. Keine Installation, kein Commit/Push,
keinen KI-Bericht als PDF.“
