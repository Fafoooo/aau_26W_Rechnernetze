# Zeilengenaue Erklärung: Offline-CLIs, Routerstarter und Mocktests

**KI-Kennzeichnung:** Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription; Datum 2026-10-29.

**Tatsächlicher Auftrag, sinngemäß:** RN Blatt08 unabhängig anhand der Originalangabe, Originalvorlagen, fertigen Programme, Antworten und gesicherten echten Messbelege fachlich und technisch prüfen; zusätzlich jede nichtleere Originalzeile der neuen CLI-/Router-/Mocktest-Dateien auf Deutsch erläutern. Keine Änderung am Lösungscode, keine neue privilegierte Messung und kein Überschreiben von run01.

Die Zeilennummern beziehen sich auf die unveränderten Quelldateien. Die zweite Spalte enthält die vollständige Originalzeile mit unveränderter Einrückung, ausschließlich HTML-escaped. Leerzeilen sind ausgelassen, Kommentare und Abschlussklammern nicht. Relative Dateinamen gelten ab `ueb08`. Jede echte Anweisung wird nach Wirkung und Zweck erklärt.

**Nachweisgrenze:** Die Auswerte-CLIs lesen echte gespeicherte Linux-Bridge-/Namespace-PCAPs. Die Routertests mit MagicMock, gepatchten Modulen und simulierter root-ID sind ausdrücklich synthetische Kontrollfluss-/Argumenttests: Sie erzeugen keine Netzwerk-Namespaces, keinen OVS-Switch, keinen echten Mininet-Prompt und keinen Paketverkehr. Ein Mininet-/OVS-/xterm-Lauf wird dadurch nicht nachgewiesen.

## auswertung.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet die KI-Erstellung des gemeinsamen Auswertemoduls mit Werkzeug, Modell und Zugang; der Kommentar wird nicht ausgeführt. |
| 2 | <code># Datum: 2026-10-29</code> | Hält das Erstellungsdatum dieses Moduls fest; es ist kein zur Laufzeit ermitteltes Messdatum. |
| 3 | <code># Anfrage: Jede Teilaufgabe von Blatt08 aus echten gesicherten PCAPs erneut auswertbar machen.</code> | Dokumentiert den ursprünglichen Auftrag: Teilaufgaben aus bereits gesicherten echten PCAPs erneut berechnen statt neue Pakete zu erzeugen. |
| 4 | <code>&quot;&quot;&quot;Unprivilegierte CLI; liest Belege, erzeugt keinen Netzwerkverkehr.&quot;&quot;&quot;</code> | Beschreibt als Modul-Docstring den unprivilegierten Offline-Zweck; derselbe Text erscheint später als CLI-Beschreibung. |
| 5 | <code>import argparse</code> | Lädt argparse, damit die Auswerteprogramme den Belegordner als Option entgegennehmen und eine Hilfe anbieten können. |
| 6 | <code>import json</code> | Lädt JSON-Lesen und -Schreiben für gesicherte Zustandsdaten und die strukturierte Standardausgabe. |
| 7 | <code>from pathlib import Path</code> | Importiert Path für betriebssystemgerechte Dateipfade ohne manuelles Zusammensetzen von Schrägstrichen. |
| 8 | <code>from messen import analyse</code> | Übernimmt die gemeinsame PCAP-Analysefunktion aus messen; der Import startet dank dessen Hauptprogrammschutz keinen Messlauf. |
| 10 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert den Standardbelegordner am aufgelösten Speicherort dieses Moduls, unabhängig vom aktuellen Arbeitsverzeichnis. |
| 13 | <code>def report(number, directory):</code> | Definiert die wiederverwendbare Berichtsfunktion für eine Aufgabennummer und einen als Path übergebenen Belegordner. |
| 14 | <code>    result = analyse(directory)[number]</code> | Analysiert den vollständigen Messordner erneut und wählt danach das Ergebnis der angeforderten Teilaufgabe aus; auch eine einzelne CLI benötigt deshalb die zusammengehörigen Belege. |
| 15 | <code>    if number in (&quot;8.2&quot;, &quot;8.3&quot;):</code> | Beschränkt die Ergänzung historischer Zustandsaufnahmen auf ARP und Switch Learning, weil diese Aufgaben auch Nachbarcache beziehungsweise FDB benötigen. |
| 16 | <code>        state = json.loads((directory / &quot;results.json&quot;).read_text())[&quot;state&quot;]</code> | Liest die aufgezeichneten Zustände aus results.json; dies sind gesicherte damalige Snapshots, keine neu abgefragten Kernelzustände. |
| 17 | <code>        prefix = &quot;82_&quot; if number == &quot;8.2&quot; else &quot;83_&quot;</code> | Wählt das Schlüsselpräfix 82_ für die ARP-Aufgabe oder 83_ für die Switching-Aufgabe, damit deren Snapshots getrennt bleiben. |
| 18 | <code>        result = {**result, &quot;gesicherter_zustand&quot;: {k: v for k, v in state.items() if k.startswith(prefix)}}</code> | Erzeugt ein neues Ergebnis-Dictionary aus den PCAP-Befunden und den zum Präfix passenden Zuständen; die zusätzliche Bezeichnung macht deren gesicherte Herkunft sichtbar. |
| 19 | <code>    return {&quot;aufgabe&quot;: number, &quot;quelle&quot;: &quot;Eigene Linux-Bridge-PCAPs; keine Mininet-/OVS-Messung&quot;, &quot;ergebnis&quot;: result}</code> | Liefert Aufgabennummer, ausdrücklich als Linux-Bridge-Ersatzmessung bezeichnete Quelle und Befund zurück; es wird kein Mininet-/OVS-Erfolg behauptet. |
| 22 | <code>def main(number):</code> | Definiert den gemeinsamen CLI-Einstieg; die fünf kleinen Starter übergeben jeweils ihre feste Aufgabennummer. |
| 23 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erstellt den Argumentparser und verwendet den Modul-Docstring als Beschreibung im Hilfetext. |
| 24 | <code>    parser.add_argument(&quot;--belege&quot;, type=Path, default=BASE / &quot;nachweise/run01&quot;)</code> | Erlaubt --belege mit Umwandlung zum Path; ohne Option wird der vorhandene Ordner nachweise/run01 neben diesem Modul verwendet. |
| 25 | <code>    args = parser.parse_args()</code> | Liest und validiert die tatsächlichen Kommandozeilenargumente; argparse behandelt auch --help und unbekannte Optionen. |
| 26 | <code>    print(json.dumps(report(number, args.belege), indent=2, ensure_ascii=False))</code> | Berechnet den Bericht und gibt eingerücktes JSON mit lesbaren Umlauten aus; es wird ausschließlich gelesen und auf stdout geschrieben. |

## ue8.1/auswerten.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet den Starter zu Ü8.1 als KI-erstelltes Programm mit Werkzeug, Modell und Zugang; ohne Laufzeiteffekt. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Ü8.1-Starters und nicht den Zeitpunkt einer neuen Messung. |
| 3 | <code># Anfrage: Ü8.1 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.</code> | Hält den ursprünglichen Auftrag dieses Starters fest: Ü8.1 aus den eigenen gespeicherten Paketbelegen auswerten. |
| 4 | <code>&quot;&quot;&quot;Offline-Einstieg zu Ü8.1; Einzelheiten in antwort.md.&quot;&quot;&quot;</code> | Benennt das Modul als Offline-Einstieg für Ü8.1 und verweist für die fachliche Interpretation auf die Antwort im selben Aufgabenordner. |
| 5 | <code>import sys</code> | Lädt sys, um den Python-Importsuchpfad für den direkten Skriptstart aus dem Unterordner ergänzen zu können. |
| 6 | <code>from pathlib import Path</code> | Importiert Path, damit der übergeordnete Blattordner aus dem tatsächlichen Dateipfad bestimmt werden kann. |
| 7 | <code>sys.path.insert(0, str(Path(__file__).resolve().parents[1]))</code> | Setzt den Blattordner an den Anfang des Importsuchpfads: parents[1] geht von ue8.1/auswerten.py nach ueb08, wo das gemeinsame Modul liegt; der Programmstart hängt so nicht vom Arbeitsverzeichnis ab. |
| 8 | <code>from auswertung import main</code> | Importiert die gemeinsame main-Funktion, die --belege verarbeitet und den ausgewählten Bericht als JSON ausgibt. |
| 10 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt den CLI-Aufruf nur bei direktem Skriptstart aus; beim Import wird keine Auswertung gestartet. |
| 11 | <code>    main(&quot;8.1&quot;)</code> | Übergibt die feste Aufgabennummer 8.1 an den gemeinsamen Einstieg; dadurch erscheint genau dieser Aufgabenbericht, obwohl die zugrunde liegende Analyse den gesamten Belegordner prüft. |

## ue8.2/auswerten.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet den Starter zu Ü8.2 als KI-erstelltes Programm mit Werkzeug, Modell und Zugang; ohne Laufzeiteffekt. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Ü8.2-Starters und nicht den Zeitpunkt einer neuen Messung. |
| 3 | <code># Anfrage: Ü8.2 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.</code> | Hält den ursprünglichen Auftrag dieses Starters fest: Ü8.2 aus den eigenen gespeicherten Paketbelegen auswerten. |
| 4 | <code>&quot;&quot;&quot;Offline-Einstieg zu Ü8.2; Einzelheiten in antwort.md.&quot;&quot;&quot;</code> | Benennt das Modul als Offline-Einstieg für Ü8.2 und verweist für die fachliche Interpretation auf die Antwort im selben Aufgabenordner. |
| 5 | <code>import sys</code> | Lädt sys, um den Python-Importsuchpfad für den direkten Skriptstart aus dem Unterordner ergänzen zu können. |
| 6 | <code>from pathlib import Path</code> | Importiert Path, damit der übergeordnete Blattordner aus dem tatsächlichen Dateipfad bestimmt werden kann. |
| 7 | <code>sys.path.insert(0, str(Path(__file__).resolve().parents[1]))</code> | Setzt den Blattordner an den Anfang des Importsuchpfads: parents[1] geht von ue8.2/auswerten.py nach ueb08, wo das gemeinsame Modul liegt; der Programmstart hängt so nicht vom Arbeitsverzeichnis ab. |
| 8 | <code>from auswertung import main</code> | Importiert die gemeinsame main-Funktion, die --belege verarbeitet und den ausgewählten Bericht als JSON ausgibt. |
| 10 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt den CLI-Aufruf nur bei direktem Skriptstart aus; beim Import wird keine Auswertung gestartet. |
| 11 | <code>    main(&quot;8.2&quot;)</code> | Übergibt die feste Aufgabennummer 8.2 an den gemeinsamen Einstieg; dadurch erscheint genau dieser Aufgabenbericht, obwohl die zugrunde liegende Analyse den gesamten Belegordner prüft. |

## ue8.3/auswerten.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet den Starter zu Ü8.3 als KI-erstelltes Programm mit Werkzeug, Modell und Zugang; ohne Laufzeiteffekt. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Ü8.3-Starters und nicht den Zeitpunkt einer neuen Messung. |
| 3 | <code># Anfrage: Ü8.3 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.</code> | Hält den ursprünglichen Auftrag dieses Starters fest: Ü8.3 aus den eigenen gespeicherten Paketbelegen auswerten. |
| 4 | <code>&quot;&quot;&quot;Offline-Einstieg zu Ü8.3; Einzelheiten in antwort.md.&quot;&quot;&quot;</code> | Benennt das Modul als Offline-Einstieg für Ü8.3 und verweist für die fachliche Interpretation auf die Antwort im selben Aufgabenordner. |
| 5 | <code>import sys</code> | Lädt sys, um den Python-Importsuchpfad für den direkten Skriptstart aus dem Unterordner ergänzen zu können. |
| 6 | <code>from pathlib import Path</code> | Importiert Path, damit der übergeordnete Blattordner aus dem tatsächlichen Dateipfad bestimmt werden kann. |
| 7 | <code>sys.path.insert(0, str(Path(__file__).resolve().parents[1]))</code> | Setzt den Blattordner an den Anfang des Importsuchpfads: parents[1] geht von ue8.3/auswerten.py nach ueb08, wo das gemeinsame Modul liegt; der Programmstart hängt so nicht vom Arbeitsverzeichnis ab. |
| 8 | <code>from auswertung import main</code> | Importiert die gemeinsame main-Funktion, die --belege verarbeitet und den ausgewählten Bericht als JSON ausgibt. |
| 10 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt den CLI-Aufruf nur bei direktem Skriptstart aus; beim Import wird keine Auswertung gestartet. |
| 11 | <code>    main(&quot;8.3&quot;)</code> | Übergibt die feste Aufgabennummer 8.3 an den gemeinsamen Einstieg; dadurch erscheint genau dieser Aufgabenbericht, obwohl die zugrunde liegende Analyse den gesamten Belegordner prüft. |

## ue8.4/auswerten.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet den Starter zu Ü8.4 als KI-erstelltes Programm mit Werkzeug, Modell und Zugang; ohne Laufzeiteffekt. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Ü8.4-Starters und nicht den Zeitpunkt einer neuen Messung. |
| 3 | <code># Anfrage: Ü8.4 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.</code> | Hält den ursprünglichen Auftrag dieses Starters fest: Ü8.4 aus den eigenen gespeicherten Paketbelegen auswerten. |
| 4 | <code>&quot;&quot;&quot;Offline-Einstieg zu Ü8.4; Einzelheiten in antwort.md.&quot;&quot;&quot;</code> | Benennt das Modul als Offline-Einstieg für Ü8.4 und verweist für die fachliche Interpretation auf die Antwort im selben Aufgabenordner. |
| 5 | <code>import sys</code> | Lädt sys, um den Python-Importsuchpfad für den direkten Skriptstart aus dem Unterordner ergänzen zu können. |
| 6 | <code>from pathlib import Path</code> | Importiert Path, damit der übergeordnete Blattordner aus dem tatsächlichen Dateipfad bestimmt werden kann. |
| 7 | <code>sys.path.insert(0, str(Path(__file__).resolve().parents[1]))</code> | Setzt den Blattordner an den Anfang des Importsuchpfads: parents[1] geht von ue8.4/auswerten.py nach ueb08, wo das gemeinsame Modul liegt; der Programmstart hängt so nicht vom Arbeitsverzeichnis ab. |
| 8 | <code>from auswertung import main</code> | Importiert die gemeinsame main-Funktion, die --belege verarbeitet und den ausgewählten Bericht als JSON ausgibt. |
| 10 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt den CLI-Aufruf nur bei direktem Skriptstart aus; beim Import wird keine Auswertung gestartet. |
| 11 | <code>    main(&quot;8.4&quot;)</code> | Übergibt die feste Aufgabennummer 8.4 an den gemeinsamen Einstieg; dadurch erscheint genau dieser Aufgabenbericht, obwohl die zugrunde liegende Analyse den gesamten Belegordner prüft. |

## ue8.5/auswerten.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet den Starter zu Ü8.5 als KI-erstelltes Programm mit Werkzeug, Modell und Zugang; ohne Laufzeiteffekt. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Ü8.5-Starters und nicht den Zeitpunkt einer neuen Messung. |
| 3 | <code># Anfrage: Ü8.5 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.</code> | Hält den ursprünglichen Auftrag dieses Starters fest: Ü8.5 aus den eigenen gespeicherten Paketbelegen auswerten. |
| 4 | <code>&quot;&quot;&quot;Offline-Einstieg zu Ü8.5; Einzelheiten in antwort.md.&quot;&quot;&quot;</code> | Benennt das Modul als Offline-Einstieg für Ü8.5 und verweist für die fachliche Interpretation auf die Antwort im selben Aufgabenordner. |
| 5 | <code>import sys</code> | Lädt sys, um den Python-Importsuchpfad für den direkten Skriptstart aus dem Unterordner ergänzen zu können. |
| 6 | <code>from pathlib import Path</code> | Importiert Path, damit der übergeordnete Blattordner aus dem tatsächlichen Dateipfad bestimmt werden kann. |
| 7 | <code>sys.path.insert(0, str(Path(__file__).resolve().parents[1]))</code> | Setzt den Blattordner an den Anfang des Importsuchpfads: parents[1] geht von ue8.5/auswerten.py nach ueb08, wo das gemeinsame Modul liegt; der Programmstart hängt so nicht vom Arbeitsverzeichnis ab. |
| 8 | <code>from auswertung import main</code> | Importiert die gemeinsame main-Funktion, die --belege verarbeitet und den ausgewählten Bericht als JSON ausgibt. |
| 10 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt den CLI-Aufruf nur bei direktem Skriptstart aus; beim Import wird keine Auswertung gestartet. |
| 11 | <code>    main(&quot;8.5&quot;)</code> | Übergibt die feste Aufgabennummer 8.5 an den gemeinsamen Einstieg; dadurch erscheint genau dieser Aufgabenbericht, obwohl die zugrunde liegende Analyse den gesamten Belegordner prüft. |

## ue8.4/lab.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet die KI-Erstellung der zusätzlichen Routertopologie mit Hermes Agent, Modell und Zugang; der Kommentar verändert das Netz nicht. |
| 2 | <code># Datum: 2026-10-29</code> | Hält das Erstellungsdatum des Starters fest, nicht das Datum einer tatsächlich ausgeführten Mininet-Messung. |
| 3 | <code># Anfrage: Für Ü8.4 die Vorlage um zwei Ethernet-LANs und einen IPv4-Router erweitern; Mininet-CLI öffnen.</code> | Dokumentiert den Implementierungsauftrag: zwei Ethernet-LANs durch einen IPv4-Router verbinden und eine echte Mininet-CLI öffnen. |
| 4 | <code>&quot;&quot;&quot;Zusätzlicher Mininet-Starter für die Kurs-VM; Originalvorlagen bleiben unverändert.&quot;&quot;&quot;</code> | Grenzt den eigenen zusätzlichen Kurs-VM-Starter von den unverändert erhaltenen Originalvorlagen ab. |
| 5 | <code>import os</code> | Lädt os für die spätere Prüfung der effektiven Benutzer-ID; die reine Topologiebeschreibung bleibt ohne Mininet importierbar. |
| 7 | <code>HOSTS = {</code> | Beginnt das Hostmodell als Dictionary; pro Host folgen IPv4-Präfix, MAC, zuständiger Switch und Defaultgateway. |
| 8 | <code>    &quot;client1&quot;: (&quot;10.0.1.2/24&quot;, &quot;00:00:00:00:00:01&quot;, &quot;s1&quot;, &quot;10.0.1.1&quot;),</code> | Ordnet client1 im LAN A die Adresse 10.0.1.2/24, MAC ...:01, Switch s1 und Gateway 10.0.1.1 zu. |
| 9 | <code>    &quot;client2&quot;: (&quot;10.0.1.3/24&quot;, &quot;00:00:00:00:00:02&quot;, &quot;s1&quot;, &quot;10.0.1.1&quot;),</code> | Ordnet client2 demselben LAN A mit eigener IP .3 und MAC ...:02 zu; beide Clients teilen Switch und Gateway. |
| 10 | <code>    &quot;server1&quot;: (&quot;10.0.2.10/24&quot;, &quot;00:00:00:00:00:03&quot;, &quot;s2&quot;, &quot;10.0.2.1&quot;),</code> | Verschiebt server1 ins LAN B 10.0.2.0/24 mit MAC ...:03, Switch s2 und dem dort direkt erreichbaren Gateway 10.0.2.1. |
| 11 | <code>    &quot;server2&quot;: (&quot;10.0.2.11/24&quot;, &quot;00:00:00:00:00:04&quot;, &quot;s2&quot;, &quot;10.0.2.1&quot;),</code> | Legt server2 ebenfalls ins LAN B, aber mit eigener IP .11 und MAC ...:04, damit beide Server am gemeinsamen Ethernet-LAN hängen. |
| 12 | <code>}</code> | Schließt das Host-Dictionary ab; die vier vorherigen Einträge sind die gesamte Endhostkonfiguration. |
| 13 | <code>ROUTER = (</code> | Beginnt das Tupel der beiden Schnittstellen desselben Routers; jede enthält Name, IPv4-Präfix, eigene MAC und LAN-Switch. |
| 14 | <code>    (&quot;router-A&quot;, &quot;10.0.1.1/24&quot;, &quot;02:00:00:00:01:01&quot;, &quot;s1&quot;),</code> | Beschreibt router-A an s1 mit 10.0.1.1/24 und eigener lokal administrierter MAC als Next Hop der Clients. |
| 15 | <code>    (&quot;router-B&quot;, &quot;10.0.2.1/24&quot;, &quot;02:00:00:00:02:01&quot;, &quot;s2&quot;),</code> | Beschreibt router-B an s2 mit 10.0.2.1/24 und anderer MAC als Next Hop der Server; dies ist keine zweite Routerinstanz. |
| 16 | <code>)</code> | Schließt die Router-Schnittstellenliste ab; ihre beiden angeschlossenen Präfixe liefern später die direkten Routen. |
| 19 | <code>def checked(node, *args):</code> | Definiert einen Befehlshelfer für einen Mininet-Knoten; einzelne Argumente werden ohne selbst gebaute Shell-Zeichenkette übergeben. |
| 20 | <code>    stdout, stderr, status = node.pexec(*args)</code> | Führt den Befehl über node.pexec im Kontext des Knotens aus und übernimmt stdout, stderr und Prozessstatus getrennt. |
| 21 | <code>    if status:</code> | Behandelt einen von null verschiedenen Prozessstatus als Fehler; ein bloßer Ausgabetext wie 100% packet loss würde keinen Erfolg vortäuschen. |
| 22 | <code>        raise RuntimeError(f&quot;{node.name}: {args[0]} fehlgeschlagen: {stderr}&quot;)</code> | Bricht mit Knotenname, Programmname und stderr ab, statt nach einer misslungenen Netzkonfiguration unbemerkt weiterzulaufen. |
| 23 | <code>    return stdout</code> | Gibt bei erfolgreichem Prozess die Standardausgabe für die späteren Zustandsanzeigen zurück. |
| 26 | <code>def address(node, interface, ip, mac):</code> | Bündelt die explizite Konfiguration einer Schnittstelle, damit Hosts und Router nach derselben geprüften Reihenfolge eingerichtet werden. |
| 27 | <code>    checked(node, &quot;ip&quot;, &quot;addr&quot;, &quot;flush&quot;, &quot;dev&quot;, interface)</code> | Entfernt vorhandene Adressen der ausgewählten Schnittstelle, damit keine Mininet-Vorgabe oder alte IPv4-Konfiguration parallel bestehen bleibt. |
| 28 | <code>    checked(node, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, interface, &quot;address&quot;, mac)</code> | Setzt die im Modell definierte Ethernet-MAC der Schnittstelle über den statusgeprüften Helfer. |
| 29 | <code>    checked(node, &quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, ip, &quot;dev&quot;, interface)</code> | Vergibt die IPv4-Adresse einschließlich Präfixlänge; daraus erzeugt Linux die direkt angeschlossene Subnetzroute. |
| 30 | <code>    checked(node, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, interface, &quot;up&quot;)</code> | Schaltet die Schnittstelle administrativ ein, damit nach der Adresskonfiguration Verkehr möglich ist. |
| 33 | <code>def run(net, cli):</code> | Definiert den aufrufbaren Aufbau mit injizierter Netzinstanz und CLI-Funktion; diese Trennung ermöglicht ausdrücklich synthetische Modelltests. |
| 34 | <code>    try:</code> | Beginnt den geschützten Aufbauabschnitt, dessen finally auch bei Aufbau-, Konfigurations- oder CLI-Fehlern net.stop aufruft. |
| 35 | <code>        switches = {name: net.addSwitch(name, failMode=&quot;standalone&quot;) for name in (&quot;s1&quot;, &quot;s2&quot;)}</code> | Erstellt s1 und s2 im Standalone-Modus, damit OVS normales Ethernet-Learning ohne SDN-Controller leisten soll. |
| 36 | <code>        router = net.addHost(&quot;router&quot;, ip=None, inNamespace=True)</code> | Erstellt genau einen Routerhost ohne vorgegebene IP und mit eigenem Netzwerk-Namespace; beide Routerinterfaces werden dort eingehängt. |
| 37 | <code>        for name, (_, mac, switch, _) in HOSTS.items():</code> | Durchläuft die Endhosts und entnimmt hier nur MAC und Switch; IP und Gateway werden nach dem Netzstart eingerichtet. |
| 38 | <code>            host = net.addHost(name, ip=None, mac=mac)</code> | Erstellt jeden Endhost ohne automatisch zugewiesene IP, aber mit seiner explizit vorgesehenen MAC. |
| 39 | <code>            net.addLink(host, switches[switch], intfName1=name + &quot;-eth0&quot;)</code> | Verbindet den Host mit seinem LAN-Switch und fixiert den hostseitigen Namen auf beispielsweise client1-eth0 für spätere Befehle. |
| 40 | <code>        for interface, _, _, switch in ROUTER:</code> | Durchläuft die Routerinterfaces und deren Switchzuordnung, ohne bereits Adressen zu setzen. |
| 41 | <code>            net.addLink(router, switches[switch], intfName1=interface)</code> | Verbindet denselben Routerhost mit jedem LAN-Switch und erhält die expliziten Interface-Namen router-A und router-B. |
| 42 | <code>        net.build()</code> | Baut die vorbereitete Mininet-Topologie erst innerhalb des try-Blocks auf; ein Fehler lässt die zugewiesene Netzinstanz für Cleanup erreichbar. |
| 43 | <code>        net.start()</code> | Startet das gebaute Netz und seine Switches; erst danach werden die Laboradressen und Routen explizit gesetzt. |
| 44 | <code>        for name, (ip, mac, _, gateway) in HOSTS.items():</code> | Durchläuft nun die vollständigen Endhostdaten einschließlich IPv4-Adresse und lokalem Gateway. |
| 45 | <code>            address(net[name], name + &quot;-eth0&quot;, ip, mac)</code> | Konfiguriert die eindeutige Endhostschnittstelle mit Präfix und MAC aus dem Hostmodell. |
| 46 | <code>            checked(net[name], &quot;ip&quot;, &quot;route&quot;, &quot;replace&quot;, &quot;default&quot;, &quot;via&quot;, gateway)</code> | Setzt beziehungsweise ersetzt die Default-Route jedes Hosts zum Gateway seines eigenen LANs; damit ist auch der Rückweg der Server vorhanden. |
| 47 | <code>        for interface, ip, mac, _ in ROUTER:</code> | Durchläuft beide Routerinterface-Konfigurationen; eine Default-Route des Routers ist für diese zwei direkt angeschlossenen Netze nicht nötig. |
| 48 | <code>            address(router, interface, ip, mac)</code> | Vergibt Adresse und MAC jeder Routerseite im selben Router-Namespace; Linux erhält so je eine direkte Route nach LAN A und LAN B. |
| 49 | <code>        checked(router, &quot;sysctl&quot;, &quot;-w&quot;, &quot;net.ipv4.ip_forward=1&quot;)</code> | Aktiviert IPv4-Weiterleitung nur im Routerknoten, damit Pakete zwischen dessen beiden LAN-Interfaces geroutet werden. |
| 50 | <code>        for node in [net[name] for name in HOSTS] + [router]:</code> | Stellt vier Endhosts und den Router zu einer Liste zusammen, um die wirklich eingerichteten Adressen und Routen auszugeben. |
| 51 | <code>            print(node.name, checked(node, &quot;ip&quot;, &quot;-br&quot;, &quot;addr&quot;))</code> | Druckt Knotenname und kompakte Interface-/Adressausgabe; Fehler beim Lesen des Zustands werden ebenfalls nicht verschluckt. |
| 52 | <code>            print(checked(node, &quot;ip&quot;, &quot;route&quot;))</code> | Druckt die jeweilige Routingtabelle, damit direkte Routen und Host-Defaultgateways in der Kurs-VM kontrolliert werden können. |
| 53 | <code>        print(&quot;Mininet-CLI: client1 ping -c 1 10.0.1.3; client1 ping -c 1 10.0.2.10&quot;)</code> | Zeigt zwei konkrete Mininet-CLI-Kommandos für den Vergleich eines lokalen und eines gerouteten Pings an; diese Zeile führt die Pings noch nicht aus. |
| 54 | <code>        cli(net)</code> | Ruft die übergebene CLI mit genau dieser Netzinstanz auf und hält das Labor für interaktive Experimente offen. |
| 55 | <code>    finally:</code> | Beginnt den unabhängig von Erfolg oder Ausnahme auszuführenden Aufräumabschnitt des Netzbetriebs. |
| 56 | <code>        net.stop()</code> | Stoppt die zugehörige Netzinstanz nach Ende der CLI oder bei Fehlern; die synthetischen Tests prüfen diesen Aufruf, keine reale OVS-Bereinigung. |
| 59 | <code>def main():</code> | Definiert den tatsächlichen Kurs-VM-Einstieg und hält die Mininet-Imports aus dem reinen Modellimport heraus. |
| 60 | <code>    from mininet.cli import CLI</code> | Importiert die echte Mininet-CLI erst beim Einstieg; fehlt Mininet, scheitert der Start ausdrücklich statt durch ein Ersatzmodell zu laufen. |
| 61 | <code>    from mininet.net import Mininet</code> | Importiert den echten Mininet-Netzconstructor für die Kurs-VM, nicht den in Tests verwendeten MagicMock. |
| 62 | <code>    from mininet.node import OVSSwitch</code> | Importiert OVSSwitch als ausdrücklich gewünschte Switchimplementierung für die beiden Ethernet-LANs. |
| 63 | <code>    if os.geteuid() != 0:</code> | Prüft nach den Imports, ob die effektive Benutzer-ID root ist, weil Mininet die notwendigen Namespace-/Interface-Rechte braucht. |
| 64 | <code>        raise SystemExit(&quot;In der Kurs-VM mit sudo /usr/bin/python3 -B lab.py starten&quot;)</code> | Beendet einen unprivilegierten Start mit einem konkreten Kurs-VM-Aufrufhinweis, statt selbst Rechte zu erhöhen oder Software zu installieren. |
| 65 | <code>    net = Mininet(controller=None, switch=OVSSwitch, build=False, autoSetMacs=False)</code> | Erzeugt die Netzinstanz ohne Controller, mit OVS und ohne automatischen Aufbau oder MAC-Vergabe; build=False verschiebt den fehleranfälligen Aufbau in run samt finally. |
| 66 | <code>    run(net, CLI)</code> | Übergibt die bereits zugewiesene echte Netzinstanz und CLI an den aufräumgesicherten Aufbau. |
| 69 | <code>if __name__ == &quot;__main__&quot;:</code> | Startet das Labor nur beim direkten Skriptaufruf; ein Import für die Modelltests aktiviert kein Netz. |
| 70 | <code>    main()</code> | Ruft den Einstieg auf; der erfolgreiche Mininet-/OVS-Lauf ist hier weiterhin nicht gemessen und darf nicht aus Mock-Erfolg abgeleitet werden. |

## test_cli_lab.py

| Zeile | Unveränderte Originalzeile | Warum und was |
|---|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).</code> | Kennzeichnet die KI-Erstellung der zusätzlichen Tests mit Werkzeug, Modell und Zugang; keine Behauptung einer menschlichen Eigenprüfung. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum des Testprogramms, nicht einen automatisch ermittelten Zeitstempel jedes Testlaufs. |
| 3 | <code># Anfrage: Fünf Offline-CLIs sowie Mininet-Routermodell und Cleanup mit ausdrücklich synthetischen Testdoubles prüfen.</code> | Hält den Testauftrag fest und nennt synthetische Testdoubles ausdrücklich, damit Routermodelltests nicht mit Messverkehr verwechselt werden. |
| 4 | <code>&quot;&quot;&quot;Keine Mininet-Messung: Mocktests ergänzen die realen PCAP-Tests.&quot;&quot;&quot;</code> | Grenzt den Zweck als Mock-Ergänzung der echten PCAP-Tests ab: Dieses Modul misst keine Mininet-Verbindung. |
| 5 | <code>import importlib.util</code> | Importiert die Hilfen zum Laden des Routermoduls über dessen Dateipfad, da ue8.4 kein gewöhnlicher Python-Paketname ist. |
| 6 | <code>import ipaddress</code> | Lädt ipaddress zur semantischen Prüfung von IPv4-Adressen, Präfixen und Gateway-Zugehörigkeit. |
| 7 | <code>import json</code> | Lädt JSON, um echte CLI-Ausgaben als Strukturen statt durch empfindliche Textformatvergleiche zu prüfen. |
| 8 | <code>import subprocess</code> | Lädt subprocess für tatsächlich gestartete unprivilegierte Offline-Auswerteprogramme; dies sind keine simulierten CLI-Prozesse. |
| 9 | <code>import sys</code> | Lädt sys für denselben Python-Interpreter in Unterprozessen und für den später vorübergehend ersetzten Modulcache. |
| 10 | <code>import types</code> | Lädt types, damit der Constructortest ausdrücklich synthetische Mininet-Module bereitstellen kann. |
| 11 | <code>import unittest</code> | Lädt das unittest-Testgerüst einschließlich Assertions und Testentdeckung. |
| 12 | <code>from pathlib import Path</code> | Importiert Path für feste, vom Aufrufverzeichnis unabhängige Test- und Quellpfade. |
| 13 | <code>from unittest.mock import MagicMock, patch</code> | Importiert MagicMock und patch als Werkzeuge für synthetische Netzknoten, Fehlerfälle und zeitweiligen Austausch von Abhängigkeiten. |
| 14 | <code>from auswertung import report</code> | Importiert die reale gemeinsame Berichtsfunktion als Vergleich für die tatsächlich ausgeführten fünf Offline-CLIs; dies ist kein zweiter unabhängiger PCAP-Parser. |
| 16 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert Testpfade am Blattordner des vorliegenden Testskripts statt am zufälligen Arbeitsverzeichnis. |
| 17 | <code>spec = importlib.util.spec_from_file_location(&quot;rn08lab&quot;, BASE / &quot;ue8.4/lab.py&quot;)</code> | Erstellt eine Ladespezifikation für ue8.4/lab.py unter dem internen Modulnamen rn08lab, ohne Mininet zu benötigen. |
| 18 | <code>assert spec is not None and spec.loader is not None</code> | Prüft, dass eine Spezifikation samt Loader verfügbar ist, bevor daraus ein Modul erzeugt und ausgeführt wird. |
| 19 | <code>lab = importlib.util.module_from_spec(spec)</code> | Erzeugt das noch nicht ausgeführte Routermodul aus dieser Spezifikation. |
| 20 | <code>spec.loader.exec_module(lab)</code> | Führt nur die Moduldefinitionen aus; der Hauptprogrammschutz verhindert den echten Mininet-Einstieg beim Laden. |
| 23 | <code>def fake_net():</code> | Definiert eine Fabrik für ein ausdrücklich synthetisches Mininet-Netz samt Namensregister seiner Knotendoubles. |
| 24 | <code>    net, nodes = MagicMock(), {}</code> | Erzeugt ein MagicMock-Netz und ein leeres Knoten-Dictionary; weder Netzwerk-Namespaces noch Switches entstehen dabei. |
| 25 | <code>    def add(name, **kwargs):</code> | Definiert die gemeinsame synthetische Erzeugerfunktion für Hosts und Switches; zusätzliche API-Schlüsselwörter werden akzeptiert, aber hier nicht fachlich ausgewertet. |
| 26 | <code>        node = MagicMock()</code> | Erzeugt ein neues Knotendouble, das Aufrufe und Argumente speichert, ohne Linux-Befehle auszuführen. |
| 27 | <code>        node.name = name</code> | Gibt dem synthetischen Knoten den geforderten Namen, den run für Anzeigen und Fehlermeldungen verwendet. |
| 28 | <code>        node.pexec.return_value = (&quot;&quot;, &quot;&quot;, 0)</code> | Lässt jeden simulierten pexec-Aufruf zunächst leere Ausgaben und Status 0 liefern; dies ist künstlicher Erfolg, kein realer Netztest. |
| 29 | <code>        nodes[name] = node</code> | Registriert das Knotendouble unter seinem Namen für spätere net[name]-Zugriffe und Assertions. |
| 30 | <code>        return node</code> | Gibt den gerade erstellten synthetischen Knoten an den Aufbaucode zurück. |
| 31 | <code>    net.addHost.side_effect = add</code> | Bindet synthetische Host-Erzeugung an addHost; jeder Aufruf erstellt ein registriertes Knotendouble. |
| 32 | <code>    net.addSwitch.side_effect = add</code> | Verwendet dieselbe synthetische Fabrik für addSwitch, damit die Switchobjekte für Verknüpfungen vorhanden sind. |
| 33 | <code>    net.__getitem__.side_effect = nodes.__getitem__</code> | Leitet den indexartigen Netzzugriff an das Knotenregister weiter, sodass net[client1] das passende synthetische Hostobjekt liefert. |
| 34 | <code>    return net, nodes</code> | Liefert Netzdouble und Register gemeinsam zurück; Tests können danach Aufrufe aller Knoten gezielt untersuchen. |
| 37 | <code>class Tests(unittest.TestCase):</code> | Fasst die fünf zusätzlichen Prüffälle in einer unittest-Testklasse zusammen. |
| 38 | <code>    def test_five_real_offline_clis(self):</code> | Definiert den Integrationstest der fünf wirklichen Offline-CLI-Prozesse gegen die gesicherten eigenen Messdateien. |
| 39 | <code>        for part in range(1, 6):</code> | Durchläuft genau die fünf Teilaufgaben 8.1 bis 8.5, damit kein Starter ungetestet bleibt. |
| 40 | <code>            result = subprocess.run([sys.executable, &quot;-B&quot;, str(BASE / f&quot;ue8.{part}/auswerten.py&quot;)], capture_output=True, text=True, timeout=10)</code> | Startet jeden Auswerter wirklich mit demselben Python, deaktivierten Bytecode-Dateien, erfassten Textausgaben und zehn Sekunden Limit; dabei wird nur vorhandene Evidenz gelesen. |
| 41 | <code>            self.assertEqual(result.returncode, 0, result.stderr)</code> | Verlangt Prozessstatus 0 und zeigt bei einem Fehler stderr als Diagnose an. |
| 42 | <code>            self.assertEqual(json.loads(result.stdout), report(f&quot;8.{part}&quot;, BASE / &quot;nachweise/run01&quot;))</code> | Vergleicht das geparste CLI-JSON mit dem direkt berechneten gemeinsamen Bericht zur jeweiligen Aufgabe; prüft Verkabelung und Ausgabe, nicht unabhängig die Physik. |
| 43 | <code>            help_result = subprocess.run([sys.executable, &quot;-B&quot;, str(BASE / f&quot;ue8.{part}/auswerten.py&quot;), &quot;--help&quot;], capture_output=True, text=True, timeout=5)</code> | Startet außerdem jeden realen Auswerter mit --help und fünf Sekunden Limit, um den Argumentparser separat zu prüfen. |
| 44 | <code>            self.assertEqual(help_result.returncode, 0)</code> | Verlangt, dass die Hilfefunktion erfolgreich endet statt einen Messlauf oder Importfehler auszulösen. |
| 45 | <code>            self.assertIn(&quot;--belege&quot;, help_result.stdout)</code> | Prüft, dass die Hilfe die benutzbare Option --belege tatsächlich nennt. |
| 47 | <code>    def test_address_plan(self):</code> | Definiert die rein statische Prüfung des Router- und Endhostadressplans ohne Mininet oder Netzwerkprivilegien. |
| 48 | <code>        networks = {ipaddress.ip_interface(ip).network for _, ip, _, _ in lab.ROUTER}</code> | Leitet aus den zwei Routerinterface-Adressen die zugehörigen IPv4-Netze ab; eine Menge entfernt gleiche Präfixe. |
| 49 | <code>        self.assertEqual(len(networks), 2)</code> | Verlangt zwei verschiedene Routernetze, damit keine zwei gerouteten Ports fälschlich dasselbe Subnetz bilden. |
| 50 | <code>        self.assertEqual(len({mac for _, mac, _, _ in lab.HOSTS.values()}), 4)</code> | Verlangt vier unterschiedliche Endhost-MACs; Router-MAC-Eindeutigkeit wird an dieser Stelle nicht zusätzlich geprüft. |
| 51 | <code>        for ip, _, switch, gateway in lab.HOSTS.values():</code> | Durchläuft die Endhosts mit ihrer Adresse, Switchzuordnung und Gatewayadresse für die folgenden Adjazenzprüfungen. |
| 52 | <code>            own = ipaddress.ip_interface(ip)</code> | Zerlegt die Hostadresse in IPv4-Interfaceadresse und Subnetz, statt Zeichenkettenpräfixe zu vergleichen. |
| 53 | <code>            matching = [ipaddress.ip_interface(rip) for _, rip, _, rswitch in lab.ROUTER if rswitch == switch]</code> | Sucht die Routerinterfaces am selben modellierten LAN-Switch und zerlegt deren IPv4-Präfixe. |
| 54 | <code>            self.assertEqual(len(matching), 1)</code> | Verlangt genau eine Routerseite pro zugeordnetem Host-LAN, also ein eindeutiges lokales Gateway. |
| 55 | <code>            self.assertEqual(own.network, matching[0].network)</code> | Vergleicht Host- und Routernetz; damit muss das Gateway auf dem direkt angeschlossenen Host-LAN liegen. |
| 56 | <code>            self.assertEqual(ipaddress.ip_address(gateway), matching[0].ip)</code> | Prüft, dass die Defaultgatewayadresse exakt die IP der zugeordneten Routerseite ist. |
| 57 | <code>            self.assertNotEqual(own.ip, matching[0].ip)</code> | Verhindert eine identische Host- und Gateway-IP; die statische Prüfung ersetzt trotzdem keinen ARP- oder Ping-Lauf. |
| 59 | <code>    def test_successful_model_and_routes(self):</code> | Definiert den erfolgreichen synthetischen Aufbaupfad und prüft die daraus erzeugten API- und Befehlsaufrufe. |
| 60 | <code>        net, nodes = fake_net()</code> | Erstellt ein frisches synthetisches Netz mit Knotendoubles, damit vorherige Tests keine Aufrufhistorie einschleppen. |
| 61 | <code>        cli = MagicMock()</code> | Ersetzt die interaktive Mininet-CLI durch einen MagicMock; der Test öffnet keinen Prompt und kein Terminal. |
| 62 | <code>        with patch(&quot;builtins.print&quot;):</code> | Unterdrückt ausschließlich die Zustandsausgaben des Aufbauprogramms, damit die Testausgabe übersichtlich bleibt. |
| 63 | <code>            lab.run(net, cli)</code> | Führt den wirklichen Router-Aufbaualgorithmus gegen das synthetische Netz und die synthetische CLI aus. |
| 64 | <code>        net.build.assert_called_once_with()</code> | Verlangt genau einen expliziten build-Aufruf ohne Argumente; das prüft den vorgesehenen verzögerten Aufbau. |
| 65 | <code>        net.start.assert_called_once_with()</code> | Verlangt genau einen start-Aufruf auf dem synthetischen Netz. |
| 66 | <code>        net.stop.assert_called_once_with()</code> | Verlangt genau einen stop-Aufruf auch im erfolgreichen Pfad; eine echte Mininet-Bereinigung wird damit nicht bewiesen. |
| 67 | <code>        cli.assert_called_once_with(net)</code> | Prüft, dass die CLI genau einmal mit der aufgebauten Netzinstanz aufgerufen wurde. |
| 68 | <code>        self.assertEqual(net.addLink.call_count, 6)</code> | Verlangt sechs modellierte Links: vier Host-Switch-Verbindungen und zwei Router-Switch-Verbindungen. |
| 69 | <code>        for name, (ip, mac, _, gateway) in lab.HOSTS.items():</code> | Durchläuft die Sollkonfiguration aller vier Endhosts, um deren aufgezeichnete Konfigurationsaufrufe zu prüfen. |
| 70 | <code>            calls = nodes[name].pexec</code> | Greift auf die pexec-Aufrufhistorie des betreffenden synthetischen Knotens zu. |
| 71 | <code>            calls.assert_any_call(&quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, ip, &quot;dev&quot;, name + &quot;-eth0&quot;)</code> | Verlangt einen Aufruf zum Hinzufügen der korrekten Host-IP am explizit benannten Hostinterface. |
| 72 | <code>            calls.assert_any_call(&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name + &quot;-eth0&quot;, &quot;address&quot;, mac)</code> | Verlangt einen Aufruf zum Setzen der vorgesehenen Endhost-MAC an genau diesem Interface. |
| 73 | <code>            calls.assert_any_call(&quot;ip&quot;, &quot;route&quot;, &quot;replace&quot;, &quot;default&quot;, &quot;via&quot;, gateway)</code> | Verlangt den Default-Route-Aufruf zum passenden lokalen Gateway; die Assertion prüft Argumente, keinen wirklichen Kernelrouteeintrag. |
| 74 | <code>        nodes[&quot;router&quot;].pexec.assert_any_call(&quot;sysctl&quot;, &quot;-w&quot;, &quot;net.ipv4.ip_forward=1&quot;)</code> | Prüft den beabsichtigten sysctl-Aufruf zum IPv4-Forwarding am Routerdouble, ohne ein reales sysctl zu verändern. |
| 75 | <code>        for interface, ip, mac, _ in lab.ROUTER:</code> | Durchläuft die beiden Sollkonfigurationen der Routerinterfaces für dieselbe Art von Befehlsprüfung. |
| 76 | <code>            nodes[&quot;router&quot;].pexec.assert_any_call(&quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, ip, &quot;dev&quot;, interface)</code> | Prüft, dass die richtige IPv4-Adresse auf der richtigen Routerseite hinzugefügt werden sollte. |
| 77 | <code>            nodes[&quot;router&quot;].pexec.assert_any_call(&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, interface, &quot;address&quot;, mac)</code> | Prüft die explizite MAC-Konfiguration jeder Routerseite in der synthetischen pexec-Historie. |
| 79 | <code>    def test_failure_cleanup(self):</code> | Definiert synthetische Fehlerkontrollen für mehrere Aufbaustufen und das abschließende CLI-Verhalten. |
| 80 | <code>        for stage in (&quot;addHost&quot;, &quot;addLink&quot;, &quot;build&quot;, &quot;start&quot;, &quot;configure&quot;, &quot;cli&quot;):</code> | Durchläuft sechs absichtlich gestörte Stufen einschließlich build, damit Cleanup vor und nach dem Netzstart erfasst wird. |
| 81 | <code>            net, nodes = fake_net()</code> | Erstellt für jeden Fehlerfall ein neues synthetisches Netz und Knotenregister ohne alte Fehlerkonfiguration. |
| 82 | <code>            cli = MagicMock()</code> | Erzeugt für jeden Fehlerfall ein neues CLI-Double, dessen Aufruf beziehungsweise Nichtaufruf geprüft werden kann. |
| 83 | <code>            if stage == &quot;configure&quot;:</code> | Wählt die besondere Fehlerinjektion für die Konfigurationsphase: Ein Knotenbefehl soll einen Nichtnullstatus liefern. |
| 84 | <code>                original = net.addHost.side_effect</code> | Merkt sich die ursprüngliche synthetische Hostfabrik, damit weiterhin Knotendoubles registriert werden können. |
| 85 | <code>                def failing(name, **kwargs):</code> | Definiert eine ersetzende synthetische Hostfabrik mit absichtlich fehlschlagender Befehlsausführung. |
| 86 | <code>                    node = original(name, **kwargs)</code> | Erzeugt und registriert den Knotendouble zunächst unverändert durch die gemerkte Fabrik. |
| 87 | <code>                    node.pexec.return_value = (&quot;&quot;, &quot;synthetic failure&quot;, 1)</code> | Setzt dessen simuliertes pexec-Ergebnis auf Status 1 mit ausdrücklich synthetischer Fehlermeldung; kein echter Linux-Befehl schlägt hier fehl. |
| 88 | <code>                    return node</code> | Gibt den manipulierten Knotendouble zurück, damit checked beim späteren Aufbau seinen Fehlerpfad nehmen muss. |
| 89 | <code>                net.addHost.side_effect = failing</code> | Installiert die fehlerliefernde Fabrik nur für synthetische addHost-Aufrufe dieses Testfalls. |
| 90 | <code>            elif stage == &quot;cli&quot;:</code> | Behandelt als zweiten Sonderfall eine erst in der interaktiven CLI auftretende Ausnahme. |
| 91 | <code>                cli.side_effect = RuntimeError(&quot;synthetic CLI failure&quot;)</code> | Lässt das CLI-Double absichtlich eine als synthetisch bezeichnete RuntimeError auslösen. |
| 92 | <code>            else:</code> | Beginnt den allgemeinen Fehlerzweig für addHost, addLink, build oder start statt einer simulierten pexec-/CLI-Störung. |
| 93 | <code>                getattr(net, stage).side_effect = RuntimeError(&quot;synthetic setup failure&quot;)</code> | Ersetzt genau die jeweils ausgewählte synthetische Netzmethode durch eine sofortige RuntimeError, um ihre Cleanup-Wirkung zu testen. |
| 94 | <code>            with patch(&quot;builtins.print&quot;), self.assertRaises(RuntimeError):</code> | Unterdrückt Printausgaben und verlangt gleichzeitig, dass die injizierte Störung tatsächlich als RuntimeError nach außen gelangt. |
| 95 | <code>                lab.run(net, cli)</code> | Ruft den echten Aufbaualgorithmus auf den manipulierten Doubles auf; dies erzeugt keinen privilegierten Fehlerlauf. |
| 96 | <code>            net.stop.assert_called_once_with()</code> | Prüft nach jeder injizierten Störung genau einen stop-Aufruf und damit das Erreichen des finally-Blocks. |
| 97 | <code>            if stage != &quot;cli&quot;:</code> | Unterscheidet Fehler vor der CLI von dem absichtlich erst innerhalb der CLI erzeugten Fehler. |
| 98 | <code>                cli.assert_not_called()</code> | Verlangt bei jedem früheren Aufbau-/Konfigurationsfehler, dass die CLI gar nicht geöffnet wurde. |
| 99 | <code>            if stage == &quot;build&quot;:</code> | Wählt zusätzliche Assertions für die Störung beim expliziten build-Schritt aus. |
| 100 | <code>                net.start.assert_not_called()</code> | Verlangt, dass nach fehlgeschlagenem Aufbau kein Netzstart versucht wurde; ein realer Mininet-Start wird dabei nicht durchgeführt. |
| 102 | <code>    def test_constructor_is_deferred(self):</code> | Definiert den synthetischen Constructortest für main, besonders das für Fehler-Cleanup wichtige build=False. |
| 103 | <code>        modules = {name: types.ModuleType(name) for name in (&quot;mininet&quot;, &quot;mininet.cli&quot;, &quot;mininet.net&quot;, &quot;mininet.node&quot;)}</code> | Erzeugt vier ausdrücklich synthetische Module unter den Mininet-Importnamen; dadurch funktioniert der Test auch ohne installiertes Mininet. |
| 104 | <code>        setattr(modules[&quot;mininet.cli&quot;], &quot;CLI&quot;, MagicMock())</code> | Stellt dem synthetischen CLI-Modul ein MagicMock als CLI bereit, ohne interaktive Eingabe zu verlangen. |
| 105 | <code>        setattr(modules[&quot;mininet.node&quot;], &quot;OVSSwitch&quot;, object())</code> | Verwendet ein eindeutiges Platzhalterobjekt als synthetische OVSSwitch-Klasse; dessen Identität wird später verglichen. |
| 106 | <code>        constructor = MagicMock()</code> | Erzeugt einen synthetischen Mininet-Constructor, der Argumente protokolliert und ein Netzdouble zurückliefert. |
| 107 | <code>        setattr(modules[&quot;mininet.net&quot;], &quot;Mininet&quot;, constructor)</code> | Hängt diesen Constructor an das synthetische mininet.net-Modul, sodass der lokale Import in main ihn verwendet. |
| 108 | <code>        with patch.dict(sys.modules, modules), patch.object(lab.os, &quot;geteuid&quot;, return_value=0), patch.object(lab, &quot;run&quot;) as runner:</code> | Tauscht zeitweilig Modulcache, root-ID-Abfrage und run aus: main sieht synthetisches Mininet und scheinbare root-ID, ohne reale Privilegien oder Netzänderungen. |
| 109 | <code>            lab.main()</code> | Führt main mit diesen drei ersetzten Abhängigkeiten aus, um nur Import- und Constructorverdrahtung zu beobachten. |
| 110 | <code>        self.assertEqual(constructor.call_args.kwargs, dict(controller=None, switch=getattr(modules[&quot;mininet.node&quot;], &quot;OVSSwitch&quot;), build=False, autoSetMacs=False))</code> | Verlangt exakt controller=None, das Switch-Platzhalterobjekt, build=False und autoSetMacs=False; prüft damit die sicher verzögerte Bauphase und explizite MAC-Planung. |
| 111 | <code>        runner.assert_called_once_with(constructor.return_value, getattr(modules[&quot;mininet.cli&quot;], &quot;CLI&quot;))</code> | Verlangt die Weitergabe des Constructor-Rückgabeobjekts und der synthetischen CLI an run; dessen Netzbetrieb war hier bewusst vollständig ersetzt. |
| 114 | <code>if __name__ == &quot;__main__&quot;:</code> | Startet unittest nur bei direktem Aufruf; ein Import dieses Testmoduls startet keinen Testlauf automatisch. |
| 115 | <code>    unittest.main(verbosity=2)</code> | Führt alle Testmethoden mit ausführlichen Einzelergebnissen aus; echte Offline-Prozesse und synthetische Routertests bleiben im Text ausdrücklich getrennt. |
