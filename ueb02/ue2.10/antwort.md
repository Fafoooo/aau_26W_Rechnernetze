# Ü 2.10 – Einführung zu Wireshark

## Angabe

> Installieren Sie Wireshark und machen Sie sich mit der Handhabung vertraut. Laden Sie dump_protocols.pcap aus dem Moodle-Kurs und öffnen Sie die Datei. Erklären Sie die Ansichten, nennen Sie Filtermöglichkeiten mit einem Beispiel, starten Sie selbst eine Aufzeichnung Ihres Netzwerkverkehrs und erklären Sie die Schritte. Wozu dient der promiscuous mode?

## Tatsächliche Durchführung und Nachweise

Am **19.10.2026** wurde die installierte **Wireshark-GUI 4.4.5** auf dem Linux-Übungsserver tatsächlich gestartet und die vorhandene Moodle-Datei `../Angabe/dump_protocols.pcap` geöffnet. Die GUI lief in einem virtuellen X11-Bildschirm (Xvfb), weil der Server keinen eigenen Desktop hat. Es handelt sich um Serverautomation durch Hermes, **nicht um eine Behauptung, Fabio hätte diese GUI-Schritte persönlich ausgeführt**. Die Screenshots zeigen die echte Anwendung, keine nachgezeichnete Oberfläche.

- [GUI mit dump_protocols.pcap](gui_dump_protocols.png): 39 Pakete, Paketliste, Protokollbaum und Rohbytes.
- [GUI der eigenen Aufzeichnung](gui_eigene_aufzeichnung.png): 10 Pakete ausschließlich zwischen `127.0.0.1` und `127.0.0.1`; HTTP `GET /rn-demo` und Antwort `200 OK`.
- [Tatsächlich angewendeter Anzeigefilter http](gui_filter_http.png): 2 von 10 Paketen sichtbar; die restlichen Pakete bleiben gespeichert.
- [Eigene echte Paketaufzeichnung](eigene_aufzeichnung.pcap), [Metadaten mit vollständigem dumpcap-Protokoll](eigene_aufzeichnung.json), [Testausgabe](test_ergebnis.txt), [Prüfprotokoll mit Hashes und Wiederholung](testprotokoll.md).

Die Installation ist mit `wireshark --version` geprüft. Auf einem eigenen Ubuntu-Rechner wäre die Installation z. B. `sudo apt install wireshark`; für Live-Aufzeichnungen sind zusätzlich passende Rechte für den Capture-Helfer `dumpcap` nötig. Hier ist Wireshark bereits installiert; **die GUI wurde nicht als root gestartet**. Nur der zeitlich begrenzte Capture-Helfer erhielt per `sudo -n` Aufzeichnungsrechte.

## 1. Ansichten und Bedienelemente

1. **Paketliste:** Jede Zeile ist ein aufgezeichnetes Paket bzw. ein erfasster Link-Layer-Frame. Die Spalten zeigen Nummer, Zeit relativ zum ersten Paket, Quelle, Ziel, höchstes erkanntes Protokoll, Frame-Länge und eine Zusammenfassung. In `dump_protocols.pcap` sind beispielsweise ARP, ICMP, DNS und HTTP sichtbar. Farben dienen der Orientierung nach konfigurierbaren Regeln; eine Farbe allein ist keine Fehlerdiagnose.
2. **Paketdetails / Protokollbaum:** Nach Auswahl einer Zeile erscheinen die enthaltenen Header in ihrer Schachtelung, z. B. Frame → Ethernet → IPv4 → TCP → HTTP. Aufklappen zeigt einzelne Felder wie Quell-/Zielport, TCP-Flags und HTTP-Header. `Frame` ist Wiresharks Metadatensatz, kein zusätzliches Netzwerkprotokoll.
3. **Paketbytes:** Hexadezimale Rohbytes und daneben eine Textdarstellung. Auswahl eines Headerfelds im Protokollbaum markiert die zugehörigen Bytes. Nichtdruckbare Bytes erscheinen als Punkte; auch Nutzdaten sind hier sichtbar. Deshalb keine vertraulichen Anfragen aufzeichnen.
4. **Filterleiste:** Hier steht ein **Anzeigefilter**, kein Aufnahmefilter. Mit Enter anwenden, mit dem X rechts löschen. Grün signalisiert eine syntaktisch gültige Eingabe, nicht automatisch einen inhaltlich sinnvollen Treffer.
5. **Werkzeugleiste / Menüs / Statusleiste:** Datei öffnen/speichern, Aufzeichnung starten/stoppen, navigieren; unten stehen unter anderem Dateiname und Gesamt-/angezeigte Paketanzahl. Das Layout kann in den Einstellungen verändert werden; weitere Ansichten wie Paketdiagramm und ein rekonstruiertes Stream-Fenster sind optional.
6. **Statistics → Protocol Hierarchy:** Hierarchische Übersicht erkannter Protokolle und deren Zähler. Ein Frame kann auf mehreren Ebenen vorkommen; die Paketanteile verschiedener Schichten dürfen deshalb nicht einfach addiert werden.
7. **Statistics → Conversations → TCP:** Gruppiert die Pakete nach TCP-Endpunktpaaren; zeigt Paket-/Bytezahlen pro Richtung und Zeitspanne. **Follow → TCP Stream** setzt zusammengehörige TCP-Nutzdaten für die Betrachtung zusammen. Das ist nicht dasselbe wie die Paketbytes eines einzelnen Frames.

## 2. Filtermöglichkeiten und konkrete Beispiele

### Aufnahmefilter (Capture Filter)

Wird **vor dem Start** in Capture → Options für das gewählte Interface eingestellt. Syntax: libpcap/BPF. Nicht passende Pakete werden gar nicht in die Aufzeichnung aufgenommen. Daher ist dies auch eine Datenschutzgrenze.

```text
tcp port 80 and host 192.168.1.215
```

Dieser Filter würde TCP-Verkehr mit Port 80 und dem angegebenen Host in einer dafür freigegebenen Übungsumgebung erfassen. **Er wurde hier nicht für eine Live-Aufzeichnung verwendet.** Ein Portfilter beweist nicht, dass die Nutzdaten tatsächlich HTTP sind.

Für unsere echte Aufnahme wurde ausschließlich **Interface `lo`** und der folgende enger gefasste Filter verwendet:

```text
ip and tcp and src host 127.0.0.1 and dst host 127.0.0.1 and ((src port 52599 and dst port 44625) or (src port 44625 and dst port 52599))
```

Beide Ports waren vorher durch die eigenen Sockets reserviert. Das erfasst nur beide Richtungen dieses eigenen lokalen TCP-Endpunktpaars. Bei einer Wiederholung wählt das Betriebssystem neue freie Ports; das Programm erzeugt dazu den passenden Filter automatisch. Kein `eth0`, kein `any`, kein DNS-Zugriff und kein öffentlicher Webserver werden benutzt.

### Anzeigefilter (Display Filter)

Wird auf eine bereits geladene/aufgezeichnete Datei angewendet. Verändert die Datei **nicht** und ist daher **keine Datenschutzmaßnahme für die Aufnahme**. Syntax und Protokoll-/Feldnamen unterscheiden sich vom Aufnahmefilter.

| Filter | Bedeutung |
|---|---|
| `http` | Pakete mit erkanntem HTTP; in unserer Aufnahme tatsächlich angewendet: 2/10 Pakete. |
| `arp || icmp || dns` | ARP-, ICMP- oder DNS-Pakete, z. B. in der bereitgestellten Datei. |
| `ip.addr == 192.168.1.215 && tcp.port == 80` | TCP-Pakete mit dieser IP und Port 80 in der vorhandenen Übungsdatei. |
| `tcp.stream == 0` | Alle Pakete des TCP-Streams mit Wireshark-Index 0; Index gilt nur innerhalb der geöffneten Datei. |
| `http.request.method == "GET"` | Erkannte HTTP-GET-Anfragen. |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | Initiale SYN-Pakete beim TCP-Verbindungsaufbau. |

Rechtsklick auf ein Feld → **Apply as Filter** erstellt einen passenden Anzeigefilter ohne Abtippen. HTTPS-Nutzdaten sind ohne geeignete Sitzungsschlüssel nicht als HTTP-Klartext sichtbar; die eigene Demo verwendet absichtlich ausschließlich harmloses unverschlüsseltes lokales HTTP.

## 3. Eigene Aufzeichnung: Ablauf, Sicherheit und Ergebnis

### Tatsächlich ausgeführte automatisierte Variante

`capture_demo.py` verwendet Python-Standardbibliothek und Wiresharks echten Capture-Helfer `dumpcap`. Es erzeugt keine PCAP-Pakete künstlich und schreibt keine erfundenen Messergebnisse.

1. Der Server-Socket wird an **127.0.0.1 und einen freien Port** gebunden; der Client reserviert ebenfalls einen freien lokalen Port. Es gibt keinen Listener auf `0.0.0.0` und keine externe Verbindung.
2. Aus diesen beiden bereits reservierten Ports wird der obige **bidirektionale Aufnahmefilter** aufgebaut.
3. Start von `sudo -n dumpcap -i lo -p -F pcap -f <Filter> -a duration:3 -w -`. `-i lo` wählt nur Loopback, `-p` deaktiviert Promiscuous Mode, `-F pcap` schreibt klassisches PCAP, `-f` setzt den Kernel-Aufnahmefilter, `-a duration:3` begrenzt die Aufzeichnung, `-w -` liefert Binärdaten auf Standardausgabe. Python öffnet die Zieldatei als normaler Benutzer und reicht deren Dateideskriptor an dumpcap weiter. Damit braucht der privilegierte Helfer die Datei im Home-Verzeichnis nicht selbst zu öffnen.
4. Das Programm wartet auf dumpcaps tatsächliche Bereitschaftsmeldung, startet einen einzelnen lokalen Server-Thread und sendet genau `GET /rn-demo HTTP/1.1` mit `Host: 127.0.0.1` und `Connection: close`.
5. Der Server prüft die Anfrage und sendet `HTTP/1.1 200 OK`, `Content-Type: text/plain`, die aus der Nutzlast berechnete `Content-Length` und ausschließlich `RN UE2.10: harmless loopback demo\n` als Antworttext.
6. Beide Seiten schließen ihre TCP-Verbindung. Das Programm wartet auf den automatischen Aufnahme-Stopp und auf das Ende des Server-Threads. Die `finally`-Bereinigung schließt die Sockets auch bei Fehlern; im Ausnahmefall wird zusätzlich auf den Capture-Helfer gewartet und nötigenfalls SIGINT gesendet.
7. Die echte Datei wird in der Wireshark-GUI geöffnet und mit `http` gefiltert; siehe Screenshots. Die Offline-Tests lesen anschließend die Binärdatei unabhängig von Wiresharks Anzeige.

**Gemessen:** 10 erfasste Pakete, laut dumpcap 0 verworfene Pakete; genau eine lokale TCP-Verbindung `127.0.0.1:52599 ↔ 127.0.0.1:44625`. Die HTTP-Anfrage hat 61 TCP-Nutzbytes, die HTTP-Antwort einschließlich Headern 118 TCP-Nutzbytes. Es sind SYN/SYN-ACK, Anfrage/Antwort und reguläres Schließen vorhanden. Das sind reale Laufwerte, keine für jede Plattform garantierten Paketanzahlen.

### Reproduzieren

Voraussetzungen: Linux mit `lo`, Python 3, Wireshark/dumpcap und erlaubtes `sudo -n dumpcap`. Das Skript selbst **nicht komplett mit sudo** starten. Vorhandene PCAP-Dateien werden bewusst nicht überschrieben.

```bash
# Aus dem Blattordner ueb02/:
cd ue2.10
python3 capture_demo.py --output neuer_lauf/eigene_aufzeichnung.pcap
RN_CAPTURE_DIR="$PWD/neuer_lauf" python3 test_capture.py
wireshark neuer_lauf/eigene_aufzeichnung.pcap
```

Die GUI-Zeile benötigt einen lokalen Desktop oder einen passenden X11-Bildschirm. Der erneute Live-Lauf benötigt keine GUI. Ein zweiter echter Durchlauf ist bereits in `wiederholung/` erhalten; dessen [Capture-Protokoll](wiederholung_capture.txt) und [Tests](wiederholung_tests.txt) bestätigen die Reproduzierbarkeit mit neuen Ports. Für die ursprüngliche Datei genügt `python3 test_capture.py`; alle **7 Tests bestehen**. [Jede eigene Python-Zeile wird hier erklärt](../erklaerung_capture.md).

### Entsprechende Bedienung direkt in der GUI

Dies ist eine Anleitung für die eigene Bedienung, nicht die Behauptung einer zusätzlich ausgeführten GUI-Live-Aufnahme:

1. Capture → Options öffnen, ausschließlich **Loopback `lo`** auswählen. Nicht `any`/Ethernet/WLAN auswählen.
2. Einen Aufnahmefilter für ein **vorher reserviertes eigenes** lokales Client-/Server-Endpunktpaar einstellen; beide IP-Adressen müssen `127.0.0.1` sein. Den Filter **nicht erst nach Start** als Anzeigefilter eingeben. Nur der Port eines fremden lokalen Dienstes wäre nicht ausreichend sicher.
3. Promiscuous Mode für das Interface und gegebenenfalls die globale Aktivierung ausschalten. Unter Options eine kurze automatische Stoppzeit setzen; ausreichend Snaplen für die vollständigen harmlosen Header/Nutzdaten wählen.
4. Start drücken, genau die vorbereitete eigene lokale HTTP-Anfrage auslösen. Mit dem roten Stoppsymbol stoppen bzw. die gesetzte Stoppzeit abwarten.
5. Datei → Speichern unter: `.pcapng` ist das normale Wireshark-Format; bei gewünschter klassischer `.pcap` das entsprechende Format wählen. Eine Umbenennung allein ändert das Dateiformat nicht.
6. Datei erneut öffnen, Endpunkte und Ports kontrollieren; `http` und `tcp.stream == 0` anwenden und die drei Ansichten vergleichen. Bei Zweifeln an der Abgrenzung keine Aufzeichnung starten. Für diese Aufgabe ist das geprüfte Skript der reproduzierbare sichere Weg.

## 4. Wozu dient Promiscuous Mode?

Im normalen Ethernet-Empfang werden im Wesentlichen Frames für die eigene MAC-Adresse sowie relevante Broadcasts/Multicasts an den Host weitergegeben. **Promiscuous Mode** lässt die Netzwerkkarte zusätzlich solche empfangenen Frames an die Aufzeichnungssoftware weiterreichen, deren Ziel-MAC nicht die eigene ist. Das hilft z. B. bei erlaubter Analyse an einem Mirror-/SPAN-Port oder einem gemeinsamen Übertragungsmedium.

Er macht ein geswitchtes Netz **nicht** automatisch vollständig sichtbar: Der Switch muss die betreffenden Frames überhaupt an den eigenen Port liefern. Er entschlüsselt weder TLS noch geschütztes WLAN. Bei WLAN ist **Monitor Mode** für rohe 802.11-Frames ein anderer Modus und nicht mit Promiscuous Mode gleichzusetzen. Die Sichtbarkeit hängt immer von Medium, Treiber und Betriebssystem ab.

Für die eigene **Loopback-Kommunikation ist Promiscuous Mode nicht erforderlich**; es gibt dort keinen fremden physischen Ethernet-Verkehr, der zusätzlich empfangen werden müsste. Daher ausdrücklich `dumpcap -p`.

## 5. Unabhängige GUI-Kontrolle für Ü2.11/Ü2.12

In der echten GUI wurden **Statistics → Protocol Hierarchy** und **Statistics → Conversations → TCP** jeweils ohne Anzeigefilter geöffnet. Die CSVs stammen direkt aus dem jeweiligen GUI-Dialog über **Copy → as CSV**; bei Conversations war **Save data as raw** aktiviert. Keine tshark-Ausgabe wurde hierfür benutzt. Die numerischen Werte sind in [gui_kontrolle.md](gui_kontrolle.md) zusammengefasst.

| Eingabedatei | Protocol Hierarchy | TCP Conversations |
|---|---|---|
| `dump_protocols.pcap` | [Screenshot](gui_protocol_hierarchy_protocols.png), [CSV](gui_protocol_hierarchy_protocols.csv) | [Screenshot](gui_tcp_conversations_protocols.png), [CSV](gui_tcp_conversations_protocols.csv) |
| `dump_http.pcap` | [Screenshot](gui_protocol_hierarchy_http.png), [CSV](gui_protocol_hierarchy_http.csv) | [Screenshot](gui_tcp_conversations_http.png), [CSV](gui_tcp_conversations_http.csv) |

## Quellen und Grenzen

Wireshark-Benutzerhandbuch, abgerufen am 19.10.2026:

- [Hauptfenster und Ansichten](https://www.wireshark.org/docs/wsug_html_chunked/ChUseMainWindowSection.html)
- [Capture Options einschließlich Promiscuous/Monitor Mode](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureOptions.html)
- [Aufnahmefilter](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureFilterSection.html)
- [Anzeigefilter](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkDisplayFilterSection.html)

Die bestehende AppArmor-Sicherheitskonfiguration wurde nicht verändert; das eingeschränkte tshark wurde nicht zur Analyse der Home-Dateien benutzt. Ein erster direkter dumpcap-Dateiöffnungsversuch erhielt `Permission denied`; die endgültige Variante verwendet die reguläre Ausgabe nach stdout und einen von Python als normalem Benutzer geöffneten Dateideskriptor. Wireshark und der nur für die Screenshots gestartete Xvfb wurden nach Abschluss beendet; es bleibt kein eigener HTTP-Dienst aktiv.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, Datum **19.10.2026**. Anfrage (sinngemäß): „Ü2.10 vollständig praktisch und textlich bearbeiten: echte Wireshark-GUI und Screenshots, ausschließlich harmlose eigene Loopback-HTTP-Aufzeichnung, reproduzierbares capture_demo.py mit Tests/Protokoll, jede Codezeile erklären und unabhängige GUI-Statistikwerte für Ü2.11/Ü2.12 liefern.“ Die Serverdurchführung erfolgte automatisiert; diese Dokumentation behauptet keine persönliche GUI-Nutzung durch Fabio.
