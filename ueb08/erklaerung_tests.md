# Zeilenerklärung: test_nachweise.py

## Was hier wirklich geprüft wird

```sh
/usr/bin/python3 -B -m unittest -v test_nachweise
```

Die Offline-Tests benötigen keine Root-Rechte und erzeugen keine Netzwerkpakete.
Sie lesen die **realen** Captures von `nachweise/run01`, vergleichen ihre
Neuauswertung mit dem gespeicherten Ergebnis und lassen jede PCAP zusätzlich
von `tcpdump` lesen. Dateihashes belegen die Unverändertheit dieser lesenden Analyse.
Die fünf Originalvorlagen werden bytegenau gegen ihr geliefertes ZIP geprüft.

Absichtlich beschädigte PCAP-Kopien, Feldmutationen, kleine Segmentdatensätze
und Prozess-/Selector-Doubles sind ausdrücklich **synthetische Negativkontrollen**,
keine nachträglich hergestellten Messbelege. Sie prüfen Containerfehler,
Echo-Zuordnung, TTL/MAC/Checksumme, fehlende FINs/ACKs, andere Ports oder HTTP-Bytes,
Streamlücken und widersprüchliche Retransmissionsbytes. `tempfile` verwendet den
vorgegebenen temporären Bereich und räumt seine Kopien automatisch auf.

Der Readiness-Test übt exakt die produktive `ready`-Funktion: ein leeres
Selector-Intervall darf nicht scheitern, `Capturing on` ist noch nicht `File: -`,
EOF und die unveränderte absolute Deadline müssen scheitern. Die Sicherheits-
und Cleanup-Fälle ersetzen privilegierte Aufrufe gezielt, damit verweigertes
unshare, existierender Zielordner und ein SIGTERM nicht befolgender eigener Prozess
ohne zusätzliche Netzänderungen geprüft werden. Sie sind keine zweite reale
Namespace-Messung. Der reale erfolgreiche Messlauf liegt daneben als PCAP-Beleg vor.

Der Erklärungsprüfer vergleicht alle nichtleeren Quellzeilen als geordnete
Zeilennummer/Text-Paare nach HTML-Decodierung. Seine eigenen Negativkontrollen
entfernen eine Zeile, verdoppeln eine Tabelle und verändern Leerzeichen.
Die Testnummern für entfernte FIN/ACK-Segmente beziehen sich ausdrücklich auf
die zehn Frames dieses benannten run01, nicht auf beliebige spätere Captures.

## Jede nichtleere Originalzeile

| Zeile | Originalquelle | Individuelle Begründung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.</code> | Kennzeichnet das tatsächliche KI-Werkzeug und Modell auch für den übernommenen Testcode. |
| 2 | <code># Datum: 2026-10-29</code> | Verzeichnet das Erstellungsdatum der Tests. |
| 3 | <code># Anfrage: Gesicherte Blatt08-PCAPs offline prüfen; Format-, Routing-, TCP- und Erklärungsfehler testen.</code> | Nennt die konkrete Anfrage für Offline-Belegtests und Negativkontrollen. |
| 4 | <code>&quot;&quot;&quot;Offline-Tests: echte Belege lesen; mutierte/synthetische Fälle sind nur Negativkontrollen.&quot;&quot;&quot;</code> | Trennt reale Messbelege ausdrücklich von absichtlich mutierten Testfällen. |
| 5 | <code>import copy</code> | Ermöglicht Feldmutationen in Kopien, ohne gespeicherte Belege oder andere Tests zu verändern. |
| 6 | <code>import hashlib</code> | Berechnet Prüfsummen vor und nach rein lesender externer Decodierung. |
| 7 | <code>import html</code> | Dekodiert HTML-escaped Quelltexte aus den zeilengenaue Erklärtabellen. |
| 8 | <code>import json</code> | Liest die vom realen Runner gesicherten JSON-Befunde ein. |
| 9 | <code>import re</code> | Erkennt Paketzähler und die strukturierte Form der Erklärungszeilen. |
| 10 | <code>import struct</code> | Baut gezielt andere PCAP-Byteordnungen und defekte Binärheader für Formatprüfungen. |
| 11 | <code>import subprocess</code> | Startet den unabhängigen tcpdump-Leser mit begrenzter Laufzeit. |
| 12 | <code>import tempfile</code> | Legt ausschließlich flüchtige Testkopien in automatisch aufgeräumten temporären Ordnern an. |
| 13 | <code>import types</code> | Erstellt kleine benannte Prozess-/Pipe-Doubles ohne echte Netzverbindungen. |
| 14 | <code>import unittest</code> | Verwendet das eingebaute Testframework mit Assertions und Einzeltestausgabe. |
| 15 | <code>import zipfile</code> | Vergleicht die bereitgestellten Infrastrukturdateien bytegenau mit ihrem Originalarchiv. |
| 16 | <code>from pathlib import Path</code> | Behandelt Quell- und Belegpfade unabhängig vom aktuellen Arbeitsverzeichnis. |
| 17 | <code>from unittest.mock import Mock, patch</code> | Ersetzt im Fehlerpfadtest gezielt einzelne Systemaufrufe statt Root-Rechte zu benötigen. |
| 18 | <code>import messen</code> | Importiert den Runner, ohne dessen CLI-Messung zu starten. |
| 19 | <code>import pcap</code> | Importiert den tatsächlichen Parser und dessen Prüfmethoden. |
| 21 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert alle Testpfade am eigenen Aufgabenordner. |
| 22 | <code>EVIDENCE = BASE / &quot;nachweise/run01&quot;</code> | Bindet diese Regressionstests ausdrücklich an den dokumentierten ersten Messlauf. |
| 23 | <code>SOURCES = {&quot;messen.py&quot;: &quot;erklaerung_messung.md&quot;, &quot;pcap.py&quot;: &quot;erklaerung_pcap.md&quot;, &quot;test_nachweise.py&quot;: &quot;erklaerung_tests.md&quot;}</code> | Ordnet jede eigene ausgelieferte Python-Datei ihrer vollständigen Zeilenerklärung zu. |
| 26 | <code>def explanations(source, markdown):</code> | Validiert Quelltext und zugehörige Markdown-Erklärung unabhängig vom Erzeugungsverfahren. |
| 27 | <code>    expected = [(i, line) for i, line in enumerate(source.splitlines(), 1) if line.strip()]</code> | Erstellt das Soll aus allen nichtleeren Originalzeilen mit unveränderten Leerzeichen und Zeilennummern. |
| 28 | <code>    found = [(int(n), html.unescape(text)) for n, text in re.findall(r&quot;^\&#124; (\d+) \&#124; &lt;code&gt;(.*?)&lt;/code&gt; \&#124; .+ \&#124;$&quot;, markdown, re.M)]</code> | Extrahiert die Tabellenpaare in Reihenfolge und dekodiert deren HTML-Quelltextdarstellung. |
| 29 | <code>    pcap.require(found == expected, &quot;Erklärungszeilen fehlen, sind doppelt oder veraltet&quot;)</code> | Verlangt exakte Gleichheit, sodass fehlende, doppelte und inhaltlich veraltete Einträge auffallen. |
| 32 | <code>class EvidenceTests(unittest.TestCase):</code> | Gruppiert die Offline-Prüfungen für reale Belege und isolierte Fehlerkontrollen. |
| 33 | <code>    def load(self, filename):</code> | Bietet den Tests einen kurzen benannten Zugriff auf einen gesicherten Capture. |
| 34 | <code>        return pcap.read_pcap(EVIDENCE / filename)</code> | Liest den Capture mit genau dem unabhängig implementierten produktiven Parser. |
| 36 | <code>    def test_complete_saved_analysis(self):</code> | Prüft die vollständige Neuauswertung des real gesicherten Messlaufs. |
| 37 | <code>        saved = json.loads((EVIDENCE / &quot;results.json&quot;).read_text())</code> | Lädt die reale JSON-Ausgabe des privilegierten Runners. |
| 38 | <code>        self.assertEqual(messen.analyse(EVIDENCE), saved[&quot;analysis&quot;])</code> | Verlangt identische neu berechnete Analysewerte statt nur ähnliche Paketanzahlen. |
| 39 | <code>        self.assertEqual(len(saved[&quot;capture_packet_counts&quot;]), 11)</code> | Verlangt alle elf erwarteten Capture-Dateien im gesicherten Zählerverzeichnis. |
| 40 | <code>        for name, count in saved[&quot;capture_packet_counts&quot;].items():</code> | Bearbeitet jede einzeln benannte Aufzeichnung mit ihrem konkreten gespeicherten Sollzähler. |
| 41 | <code>            packets = self.load(name)</code> | Parst die betreffende PCAP frisch vom Datenträger. |
| 42 | <code>            self.assertEqual(len(packets), count)</code> | Vergleicht deren Recordzahl mit dem aufgezeichneten JSON-Zähler. |
| 43 | <code>            report = (EVIDENCE / (name + &quot;.txt&quot;)).read_text()</code> | Liest das originale dumpcap-Protokoll zu genau dieser Capture-Datei. |
| 44 | <code>            self.assertEqual(int(re.search(r&quot;Packets captured: (\d+)&quot;, report).group(1)), count)</code> | Prüft zusätzlich den unabhängigen dumpcap-Endzähler gegen denselben Paketbestand. |
| 45 | <code>            self.assertRegex(report, r&quot;received/dropped on interface .*: \d+/0 &quot;)</code> | Verlangt im realen Capture-Bericht null verworfene Pakete auf der beobachteten Schnittstelle. |
| 47 | <code>    def test_saved_neighbours_and_learning(self):</code> | Prüft die tatsächlich gesicherten ARP- und Switch-Learning-Zustände. |
| 48 | <code>        state = json.loads((EVIDENCE / &quot;results.json&quot;).read_text())[&quot;state&quot;]</code> | Extrahiert die Zustandsgruppe aus dem realen Ergebnis-JSON. |
| 49 | <code>        self.assertEqual(state[&quot;82_neigh_before&quot;], &quot;&quot;)</code> | Verlangt vor der ARP-Erstauflösung eine wirklich leere Nachbartabelle. |
| 50 | <code>        self.assertEqual(state[&quot;82_neigh_after_first&quot;], state[&quot;82_neigh_after_second&quot;])</code> | Verlangt denselben gespeicherten Nachbarzustand nach erstem und zweitem Ping. |
| 51 | <code>        self.assertIn(&quot;10.0.1.3 dev client1-eth0 lladdr 00:00:00:00:00:02&quot;, state[&quot;82_neigh_after_first&quot;])</code> | Prüft die konkrete IP-zu-MAC-Zuordnung und richtige Hostschnittstelle von client2. |
| 52 | <code>        self.assertEqual(state[&quot;83_fdb_start&quot;], [])</code> | Verlangt die leere dynamische Bridge-FDB als kontrollierten Start. |
| 53 | <code>        self.assertEqual([(e[&quot;mac&quot;], e[&quot;ifname&quot;]) for e in state[&quot;83_fdb_after_ping1&quot;]], [(&quot;00:00:00:00:00:01&quot;, &quot;p1&quot;), (&quot;00:00:00:00:00:03&quot;, &quot;p3&quot;)])</code> | Prüft nach Ping1 nicht nur zwei MACs, sondern deren richtige Bridge-Ports p1 und p3. |
| 54 | <code>        self.assertEqual([(e[&quot;mac&quot;], e[&quot;ifname&quot;]) for e in state[&quot;83_fdb_after_ping2&quot;]], [(&quot;00:00:00:00:00:01&quot;, &quot;p1&quot;), (&quot;00:00:00:00:00:02&quot;, &quot;p2&quot;), (&quot;00:00:00:00:00:03&quot;, &quot;p3&quot;)])</code> | Prüft nach Ping2 zusätzlich client2 auf p2 und erhält die vorherigen Portzuordnungen. |
| 56 | <code>    def test_templates_unchanged(self):</code> | Schützt alle gelieferten Originalvorlagen vor unbemerkter Veränderung. |
| 57 | <code>        with zipfile.ZipFile(BASE / &quot;Angabe/uebb8_template.zip&quot;) as archive:</code> | Öffnet das echte bereitgestellte ZIP-Archiv ohne es zu überschreiben oder neu zu packen. |
| 58 | <code>            for name in archive.namelist():</code> | Durchläuft sämtliche darin enthaltenen Einträge. |
| 59 | <code>                if not name.endswith(&quot;/&quot;):</code> | Überspringt reine Verzeichniseinträge, die keinen Dateibytevergleich benötigen. |
| 60 | <code>                    self.assertEqual((BASE / &quot;Angabe&quot; / Path(name).name).read_bytes(), archive.read(name))</code> | Vergleicht jede vorhandene Vorlagendatei exakt mit den Archivbytes. |
| 62 | <code>    def test_line_explanations(self):</code> | Prüft die vollständige und aktuelle Zeilendokumentation der eigenen Programme. |
| 63 | <code>        for name, document in SOURCES.items():</code> | Wählt jede eigene Python-Datei samt dem dazugehörigen Erklärungsdokument aus. |
| 64 | <code>            explanations((BASE / name).read_text(), (BASE / document).read_text())</code> | Vergleicht die tatsächlich gespeicherte Erklärung mit dem endgültigen Quelltext. |
| 65 | <code>        sample = &quot;x = 1\n\nprint(x)\n&quot;</code> | Definiert eine kleine synthetische Quelle mit absichtlicher Leerzeile als Prüferkontrolle. |
| 66 | <code>        valid = &quot;&#124; 1 &#124; &lt;code&gt;x = 1&lt;/code&gt; &#124; Wert setzen. &#124;\n&#124; 3 &#124; &lt;code&gt;print(x)&lt;/code&gt; &#124; Wert ausgeben. &#124;\n&quot;</code> | Erstellt deren gültige Erklärung mit den ursprünglichen Zeilennummern eins und drei. |
| 67 | <code>        explanations(sample, valid)</code> | Belegt zunächst, dass der eigenständige Erklärungsprüfer den gültigen Minimalfall akzeptiert. |
| 68 | <code>        for broken in (valid.splitlines()[0], valid + valid, valid.replace(&quot;x = 1&quot;, &quot;x  = 1&quot;)):</code> | Erzeugt getrennt fehlende Einträge, eine doppelte Tabelle und eine subtile Quell-Leerzeichenabweichung. |
| 69 | <code>            with self.assertRaises(ValueError):</code> | Verlangt für jede absichtlich beschädigte Erklärung einen Prüfungsfehler. |
| 70 | <code>                explanations(sample, broken)</code> | Führt die jeweilige Negativkontrolle tatsächlich mit dem produktiven Prüfalgorithmus aus. |
| 72 | <code>    def test_pcaps_readonly_and_independent_decoder(self):</code> | Verifiziert die Captures zusätzlich mit einem echten unabhängigen Binärformat-Leser. |
| 73 | <code>        for path in sorted(EVIDENCE.glob(&quot;*.pcap&quot;)):</code> | Wählt alle gespeicherten PCAP-Dateien in deterministischer Reihenfolge. |
| 74 | <code>            before = hashlib.sha256(path.read_bytes()).digest()</code> | Sichert den kryptografischen Dateiabdruck vor der externen Auswertung. |
| 75 | <code>            result = subprocess.run([&quot;tcpdump&quot;, &quot;-nn&quot;, &quot;-e&quot;, &quot;-r&quot;, str(path)], capture_output=True, text=True, timeout=5)</code> | Lässt tcpdump ohne Namensauflösung und mit Ethernet-Headern ausschließlich die gespeicherte Datei lesen. |
| 76 | <code>            self.assertEqual(result.returncode, 0)</code> | Verlangt den erfolgreichen Exitcode des unabhängigen Decoders. |
| 77 | <code>            self.assertEqual(len(result.stdout.splitlines()), len(self.load(path.name)))</code> | Vergleicht dessen eine Textzeile pro Frame mit der eigenen Parser-Recordzahl. |
| 78 | <code>            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)</code> | Belegt, dass die ausschließlich lesende Prüfung die Original-PCAP nicht verändert hat. |
| 80 | <code>    def test_byteorders_and_timestamp_magics(self):</code> | Testet alle vier klassischen PCAP-Magicvarianten mit denselben realen Framebytes. |
| 81 | <code>        raw = (EVIDENCE / &quot;82_erster_ping.pcap&quot;).read_bytes()</code> | Nimmt eine kleine echte Aufzeichnung als Ausgangspunkt der Formatkonvertierung. |
| 82 | <code>        with tempfile.TemporaryDirectory() as directory:</code> | Begrenzte Testkopien bleiben außerhalb der gesicherten Belegdateien und werden automatisch entfernt. |
| 83 | <code>            for endian, magic in ((&quot;&lt;&quot;, b&quot;\xd4\xc3\xb2\xa1&quot;), (&quot;&gt;&quot;, b&quot;\xa1\xb2\xc3\xd4&quot;), (&quot;&lt;&quot;, b&quot;\x4d\x3c\xb2\xa1&quot;), (&quot;&gt;&quot;, b&quot;\xa1\xb2\x3c\x4d&quot;)):</code> | Kombiniert beide Container-Byteordnungen mit Mikro- und Nanosekunden-Magics. |
| 84 | <code>                converted, position = magic + struct.pack(endian + &quot;HHIIII&quot;, *struct.unpack(&quot;&lt;HHIIII&quot;, raw[4:24])), 24</code> | Konvertiert den Dateikopf, während die semantischen Headerwerte gleich bleiben. |
| 85 | <code>                while position &lt; len(raw):</code> | Durchläuft jeden vorhandenen Record der echten Ausgangs-PCAP. |
| 86 | <code>                    header = struct.unpack(&quot;&lt;IIII&quot;, raw[position:position + 16])</code> | Liest dessen Recordheader in der ursprünglichen Little-Endian-Reihenfolge. |
| 87 | <code>                    converted += struct.pack(endian + &quot;IIII&quot;, *header) + raw[position + 16:position + 16 + header[2]]</code> | Schreibt nur den Recordheader in der Zielbyteordnung um und übernimmt die Ethernet-Bytes unverändert. |
| 88 | <code>                    position += 16 + header[2]</code> | Rückt exakt um Recordkopf und gespeicherte Framelänge weiter. |
| 89 | <code>                target = Path(directory) / &quot;converted.pcap&quot;</code> | Wählt einen flüchtigen Konvertierungsbeleg, nicht den Originalpfad. |
| 90 | <code>                target.write_bytes(converted)</code> | Speichert die synthetisch umverpackten Originalframes für einen realen Datei-Lesetest. |
| 91 | <code>                self.assertEqual(pcap.read_pcap(target), self.load(&quot;82_erster_ping.pcap&quot;))</code> | Verlangt unabhängig von Container-Magic und Byteordnung dieselben geparsten Frames. |
| 93 | <code>    def test_corrupt_pcap_and_packet_lengths(self):</code> | Prüft die Ablehnung beschädigter Container und unvollständiger Ethernet-/Protokollheader. |
| 94 | <code>        raw = (EVIDENCE / &quot;84_lanA.pcap&quot;).read_bytes()</code> | Lädt einen echten gerouteten Capture als Grundlage klar abgegrenzter Mutationen. |
| 95 | <code>        broken_link = bytearray(raw)</code> | Erstellt eine beschreibbare Kopie für einen falschen Linktyp. |
| 96 | <code>        broken_link[20:24] = struct.pack(&quot;&lt;I&quot;, 113)</code> | Ersetzt DLT_EN10MB absichtlich durch Linux-Cooked 113, den der Ethernet-Parser nicht akzeptieren darf. |
| 97 | <code>        truncated_record = bytearray(raw)</code> | Erstellt getrennt eine Kopie für eine inkonsistente Capturelänge. |
| 98 | <code>        truncated_record[32:36] = struct.pack(&quot;&lt;I&quot;, 1)</code> | Verkleinert die Captured-Length des ersten Records, ohne dessen Originallänge anzupassen. |
| 99 | <code>        with tempfile.TemporaryDirectory() as directory:</code> | Hält alle beschädigten Dateikopien in einem automatisch entfernten temporären Verzeichnis. |
| 100 | <code>            for value in (b&quot;&quot;, b&quot;BAD!&quot; + raw[4:], raw[:25], raw[:-1], bytes(broken_link), bytes(truncated_record)):</code> | Prüft leere Datei, falsches Magic, abgebrochenen Recordkopf, abgebrochene Daten und zwei gezielte Headerfehler. |
| 101 | <code>                target = Path(directory) / &quot;bad.pcap&quot;</code> | Verwendet einen eigenen Fehler-Testpfad statt einer gesicherten Capture-Datei. |
| 102 | <code>                target.write_bytes(value)</code> | Schreibt den jeweiligen defekten Kandidaten tatsächlich als Binärdatei. |
| 103 | <code>                with self.assertRaises(ValueError):</code> | Verlangt für jede beschädigte Dateiform einen klaren ValueError. |
| 104 | <code>                    pcap.read_pcap(target)</code> | Übt den produktiven PCAP-Leser mit dem defekten Dateikandidaten aus. |
| 105 | <code>        for value in (b&quot;&quot;, bytes(14)[:12] + b&quot;\x08\x06&quot;, bytes(12) + b&quot;\x08\x00&quot; + bytes(20)):</code> | Testet zusätzlich direkt leeres Ethernet, abgeschnittenes ARP und ungültiges IPv4. |
| 106 | <code>            with self.assertRaises(ValueError):</code> | Verlangt auch bei direkter Frameanalyse eine kontrollierte Formatfehlermeldung. |
| 107 | <code>                pcap.frame(value, 1)</code> | Führt die konkrete fehlerhafte Frameanalyse tatsächlich aus. |
| 109 | <code>    def test_echo_negative_attribution_ttl_mac_checksum(self):</code> | Prüft, dass Routerzuordnung und Headerinvarianten nicht bloß auf Paketanzahlen beruhen. |
| 110 | <code>        before, after = self.load(&quot;84_lanA.pcap&quot;), self.load(&quot;84_lanB.pcap&quot;)</code> | Lädt die echten Vorher-Nachher-Captures des gerouteten Pings. |
| 111 | <code>        for field, value in ((&quot;icmp_id&quot;, -1), (&quot;icmp_seq&quot;, 999), (&quot;ttl&quot;, 64), (&quot;src_mac&quot;, &quot;00:00:00:00:00:03&quot;), (&quot;ip_checksum_valid&quot;, False), (&quot;icmp_checksum_valid&quot;, False)):</code> | Mutiert getrennt Identität, Sequenz, TTL, Quell-MAC und beide Prüfsummenbefunde. |
| 112 | <code>            damaged = copy.deepcopy(after)</code> | Kopiert dazu die Nachher-Datensätze tief, um die Ausgangsdaten zu schützen. |
| 113 | <code>            pcap.select(damaged, &quot;icmp_type&quot;, 8)[0][field] = value</code> | Ändert ausschließlich den konkreten Echo Request des gewählten Prüffalls. |
| 114 | <code>            with self.assertRaises(ValueError):</code> | Verlangt das Ablehnen jeder absichtlich verletzten Routereigenschaft. |
| 115 | <code>                pcap.echo_pairs(before, damaged)</code> | Übt die echte Zuordnungs- und Headerprüfung mit der mutierten Kopie aus. |
| 116 | <code>        with self.assertRaises(ValueError):</code> | Verlangt auch bei mehrdeutigen identischen Request-Schlüsseln einen Fehler. |
| 117 | <code>            pcap.echo_pairs(before + pcap.select(before, &quot;icmp_type&quot;, 8), after)</code> | Verdoppelt nur im Speicher den Eingangsrequest und prüft die Eindeutigkeitsanforderung. |
| 119 | <code>    def test_tcp_negative_missing_fin_ack_and_payload(self):</code> | Prüft Vollständigkeit, Endpunkte und Inhalt des tatsächlichen TCP-Flusses mit gezielten Störungen. |
| 120 | <code>        before, after = self.load(&quot;85_lanA.pcap&quot;), self.load(&quot;85_lanB.pcap&quot;)</code> | Lädt beide realen HTTP-Captures als unveränderte Testgrundlage. |
| 121 | <code>        for removed in (8, 9):</code> | Wählt in diesem konkret dokumentierten Lauf das Server-FIN beziehungsweise dessen letztes ACK aus. |
| 122 | <code>            with self.assertRaises(ValueError):</code> | Verlangt die Ablehnung des jeweiligen unvollständigen TCP-Abschlusses. |
| 123 | <code>                pcap.tcp_flow(before[:removed] + before[removed + 1:], after[:removed] + after[removed + 1:], messen.REQUEST, messen.RESPONSE)</code> | Entfernt das Segment an beiden Messpunkten, damit erst die Abschlussprüfung und nicht bloß der Capture-Vergleich greift. |
| 124 | <code>        for field, value in ((&quot;ttl&quot;, 64), (&quot;tcp_checksum_valid&quot;, False), (&quot;src_port&quot;, 999)):</code> | Definiert unabhängige Fehler für TTL, TCP-Checksumme und Clientport. |
| 125 | <code>            damaged = copy.deepcopy(after)</code> | Erstellt jeweils eine frische tiefe Kopie des LAN-B-Captures. |
| 126 | <code>            damaged[0][field] = value</code> | Verändert das gewählte Feld am initialen SYN dieser Kopie. |
| 127 | <code>            with self.assertRaises(ValueError):</code> | Verlangt für jede gezielt falsche Transporteigenschaft einen Analysefehler. |
| 128 | <code>                pcap.tcp_flow(before, damaged, messen.REQUEST, messen.RESPONSE)</code> | Ruft den vollständigen produktiven TCP-Prüfpfad mit dem mutierten Kandidaten auf. |
| 129 | <code>        with self.assertRaises(ValueError):</code> | Verlangt die Ablehnung einer anderen als der tatsächlich übertragenen Anwendungsmeldung. |
| 130 | <code>            pcap.tcp_flow(before, after, b&quot;falsche Anfrage&quot;, messen.RESPONSE)</code> | Vergleicht den echten rekonstruierten Datenstrom absichtlich gegen einen falschen Anfrage-Sollwert. |
| 132 | <code>    def test_tcp_stream_reordering_retransmission_and_gaps(self):</code> | Testet TCP-Reassemblierung unabhängig von einer zufälligen Segmentierung des kleinen Live-Flusses. |
| 133 | <code>        part = lambda seq, payload: dict(src_ip=&quot;10.0.1.2&quot;, tcp_seq=seq, payload_hex=payload.hex())</code> | Erzeugt ausdrücklich synthetische minimale Segmentdatensätze mit vorgegebenen Sequenzpositionen. |
| 134 | <code>        self.assertEqual(pcap.tcp_stream([part(12, b&quot;cd&quot;), part(10, b&quot;ab&quot;), part(11, b&quot;bc&quot;)], &quot;10.0.1.2&quot;), b&quot;abcd&quot;)</code> | Verlangt korrekte Bytes bei vertauschter Reihenfolge und identischer überlappender Retransmission. |
| 135 | <code>        for segments in ([part(10, b&quot;a&quot;), part(12, b&quot;c&quot;)], [part(10, b&quot;ab&quot;), part(11, b&quot;x&quot;)], []):</code> | Erzeugt eine Sequenzlücke, eine widersprüchliche Überlappung und einen leeren Datenstrom. |
| 136 | <code>            with self.assertRaises(ValueError):</code> | Verlangt, dass alle drei ungültigen Reassemblierungsfälle zurückgewiesen werden. |
| 137 | <code>                pcap.tcp_stream(segments, &quot;10.0.1.2&quot;)</code> | Übt die tatsächliche Bytepositions-Rekonstruktion mit jedem negativen Segmentbestand aus. |
| 139 | <code>    def test_capture_readiness_idle_eof_and_timeout(self):</code> | Testet die heikle Capture-Bereitschaft mit deterministischen Uhr-, Selector- und Pipe-Doubles. |
| 140 | <code>        process = types.SimpleNamespace(stderr=types.SimpleNamespace(fileno=lambda: 9))</code> | Erstellt nur eine minimale stderr-Dateideskriptor-Schnittstelle, keinen echten Capture-Prozess. |
| 141 | <code>        selector = Mock()</code> | Baut den steuerbaren Selector-Ersatz für den Bereitschaftsalgorithmus. |
| 142 | <code>        selector.__enter__ = Mock(return_value=selector)</code> | Lässt den Mock im with-Block dasselbe steuerbare Selector-Objekt liefern. |
| 143 | <code>        selector.__exit__ = Mock(return_value=False)</code> | Verhindert, dass der Mock echte Ausnahmen aus dem Bereitschaftscode unterdrückt. |
| 144 | <code>        selector.select.side_effect = [[], [1], [1]]</code> | Simuliert erst einen leeren Wartezyklus und danach zwei lesbare Ereignisse. |
| 145 | <code>        with patch.object(messen.selectors, &quot;DefaultSelector&quot;, return_value=selector), patch.object(messen.time, &quot;monotonic&quot;, side_effect=[0, 0.1, 0.2, 0.3]), patch.object(messen.os, &quot;read&quot;, side_effect=[b&quot;Capturing on lab\n&quot;, b&quot;File: -\n&quot;]):</code> | Gibt Uhrzeiten und zwei echte Statuswortlaut-Stücke vor, sodass Capturing on allein noch nicht genügt. |
| 146 | <code>            self.assertIn(b&quot;File: -&quot;, messen.ready(process, b&quot;File: -&quot;))</code> | Verlangt erfolgreichen Start erst nach dem zweiten Read mit vollständigem File:-Token. |
| 147 | <code>        for chunks, times in (([b&quot;&quot;], [0, 0.1]), ([], [0, 6])):</code> | Definiert getrennte negative Abläufe für EOF und überschrittene absolute Deadline. |
| 148 | <code>            selector.select.side_effect = None</code> | Entfernt die frühere Ereignis-Sequenz, bevor der jeweilige Fehlerfall beginnt. |
| 149 | <code>            selector.select.return_value = [1]</code> | Signalisiert für den EOF-Fall ein lesbares Pipe-Ereignis. |
| 150 | <code>            with patch.object(messen.selectors, &quot;DefaultSelector&quot;, return_value=selector), patch.object(messen.time, &quot;monotonic&quot;, side_effect=times), patch.object(messen.os, &quot;read&quot;, side_effect=chunks), self.assertRaises(ValueError):</code> | Kombiniert den konkreten Fehlerablauf mit der Erwartung eines kontrollierten Bereitschaftsfehlers. |
| 151 | <code>                messen.ready(process, b&quot;File: -&quot;)</code> | Führt beide negativen Startpfade mit derselben produktiven ready-Funktion aus. |
| 153 | <code>    def test_isolation_failure_and_exclusive_output(self):</code> | Prüft die Sicherheitsreihenfolge und das Verbot, vorhandene Belegordner zu überschreiben. |
| 154 | <code>        with tempfile.TemporaryDirectory() as directory:</code> | Verwendet für diese Fehlerpfade einen flüchtigen eigenen Ordner statt run01. |
| 155 | <code>            target = Path(directory) / &quot;new&quot;</code> | Wählt einen noch nicht existierenden Zielpfad für den Isolation-Fehlversuch. |
| 156 | <code>            with patch.object(messen.os, &quot;geteuid&quot;, return_value=0), patch.object(messen.os, &quot;unshare&quot;, side_effect=PermissionError), patch.object(messen, &quot;Lab&quot;) as constructor, self.assertRaises(PermissionError):</code> | Simuliert verweigertes unshare trotz Rootkennung und überwacht, ob überhaupt ein Lab-Objekt angelegt wird. |
| 157 | <code>                messen.measure(target)</code> | Ruft die reale Mess-Einstiegsroutine bis zur erzwungenen Isolationssperre auf. |
| 158 | <code>            self.assertFalse(target.exists())</code> | Belegt, dass selbst der Ausgabeordner bei fehlgeschlagener Isolation noch nicht entsteht. |
| 159 | <code>            constructor.assert_not_called()</code> | Belegt, dass vor erfolgreichem unshare keine Laborverwaltung mit Netzwerkaktionen gestartet wird. |
| 160 | <code>            with patch.object(messen.os, &quot;geteuid&quot;, return_value=0), patch.object(messen.os, &quot;unshare&quot;), patch.object(messen, &quot;Lab&quot;) as constructor, self.assertRaises(FileExistsError):</code> | Simuliert erfolgreiche Isolation, aber einen bereits existierenden Zielordner als separaten Fehlerfall. |
| 161 | <code>                messen.measure(Path(directory))</code> | Übt den exklusiven mkdir-Pfad mit dem vorhandenen Testverzeichnis aus. |
| 162 | <code>            constructor.assert_not_called()</code> | Verlangt auch dort den Abbruch vor der ersten Laborkonfiguration. |
| 164 | <code>    def test_cleanup_escalation_and_nonzero_ping(self):</code> | Prüft robustes Prozess-Cleanup und die korrekte Bewertung eines fehlgeschlagenen Pingbefehls. |
| 165 | <code>        with tempfile.TemporaryDirectory() as directory:</code> | Hält das Test-Befehlsprotokoll in einem automatisch entfernten Verzeichnis. |
| 166 | <code>            lab = messen.Lab(Path(directory))</code> | Erzeugt eine echte Lab-Verwaltung ohne irgendeinen Netzwerkbefehl auszuführen. |
| 167 | <code>            process = Mock()</code> | Ersetzt ausschließlich den Prozess durch einen steuerbaren Cleanup-Fehlerkandidaten. |
| 168 | <code>            process.poll.return_value = None</code> | Kennzeichnet den Kandidaten zunächst als noch laufend. |
| 169 | <code>            process.communicate.side_effect = [subprocess.TimeoutExpired(&quot;own-worker&quot;, 3), (b&quot;&quot;, b&quot;&quot;)]</code> | Simuliert erst ein überschrittenes SIGTERM-Wartefenster und danach das eingesammelte Prozessende. |
| 170 | <code>            lab.processes.append(process)</code> | Registriert den Fehlerkandidaten genauso wie einen selbst gestarteten Worker. |
| 171 | <code>            lab.cleanup()</code> | Führt den tatsächlichen Cleanup-Algorithmus einschließlich dessen Protokollschreiben aus. |
| 172 | <code>            process.terminate.assert_called_once()</code> | Verlangt genau eine schonende Beendigungsanforderung. |
| 173 | <code>            process.kill.assert_called_once()</code> | Verlangt genau eine Eskalation für den nicht rechtzeitig beendeten eigenen Prozess. |
| 174 | <code>            self.assertEqual(process.communicate.call_count, 2)</code> | Belegt Warten und Pipe-Leeren vor und nach der Eskalation. |
| 175 | <code>            with patch.object(messen.subprocess, &quot;run&quot;, return_value=types.SimpleNamespace(returncode=1, stdout=&quot;100% packet loss&quot;, stderr=&quot;&quot;)), self.assertRaises(ValueError):</code> | Liefert einen fehlgeschlagenen Ping mit 100 Prozent Verlust und verlangt dessen Zurückweisung per Exitcode. |
| 176 | <code>                lab.ping(None, &quot;10.0.1.2&quot;)</code> | Ruft den echten Ping-Wrapper auf, dessen subprocess-Grenze für diesen Fehlerfall kontrolliert ersetzt ist. |
| 179 | <code>if __name__ == &quot;__main__&quot;:</code> | Verhindert den automatischen Teststart beim bloßen Import des Erklärungsprüfers. |
| 180 | <code>    unittest.main(verbosity=2)</code> | Startet bei direktem Aufruf alle Tests mit einzeln benannten Ergebnissen. |

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol, ChatGPT or Codex Subscription; 2026-10-29. Auftrag: eigene reale Messimplementierung und exakte Zeilenerklärung für RN Blatt08.
