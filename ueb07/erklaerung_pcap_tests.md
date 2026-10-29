# PCAP- und Readiness-Tests: zeilenweise Erklärung

## Einordnung und Aufruf

[ue7.4/test_pcap.py](ue7.4/test_pcap.py) ergänzt die [Messprogramm-Erklärung](erklaerung_messung.md) und prüft ausschließlich offline. Es liest die echte [Fehleraufnahme](nachweise/run01/fault.pcap), vergleicht die unveränderte öffentliche Rückgabe mit [fault-frames.json](nachweise/run01/fault-frames.json) und dem fault-Eintrag in [results.json](nachweise/run01/results.json). Die übrigen Varianten sind ausdrücklich **synthetische Bytekopien**, keine neue Messung. Es werden keine Nachweise geschrieben, Sockets geöffnet, Prozesse gestartet oder Netze verändert.

```sh
python3 -B ue7.4/test_pcap.py
```

Die Suite enthält **18 Testmethoden**: 13 PCAP-Tests und fünf Readiness-Tests, teilweise mit mehreren Untertests. Die PCAP-Varianten ändern unter anderem zitiertes Protokoll, Typ/Code, ID/Sequenz, Duplikate, Fragmentierung, Headergrößen und Abschneidungsgrenzen. Positive Kontrollen umfassen die echte Datei, alle vier klassischen Magics, das erlaubte minimale Zitat und innere IPv4-Optionen. Die Varianten berechnen keine Prüfsummen neu: Der gezielte Parser prüft diese nicht, und die Testmutationen sollen ausschließlich Struktur und Zuordnung kontrollieren.

Die Readiness-Prüfungen wählen per Python-Syntaxbaum ausschließlich den Original-Selektorblock aus verify_namespaces.py. Der Runner wird nicht importiert oder gestartet. Kontrollierte Uhr-, Selektor- und Lese-Doubles ersetzen die Abhängigkeiten; sie sind kein Nachweis realer dumpcap-Laufzeiten. Geprüft werden stille Phasen, die Unzulänglichkeit von Capturing on, die absolute Deadline, ein restzeitbegrenztes Timeout, EOF und ein geteilter File: --Marker. Ein neuer privilegierter Netzlauf findet nicht statt.

## Zeilenweise Erklärung

Jeder Eintrag erklärt genau eine nichtleere physische Quellzeile mit exaktem Inhalt einschließlich Einrückung. Listennummer und Originalzeilennummer sind getrennt; ausgelassene Leerzeilen erklären die Sprünge. assert-Prüfungen des Parsers bleiben nur ohne Python-Option -O aktiv.

### `ue7.4/test_pcap.py`

1. Zeile 1 — `# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.`: Kennzeichnet die KI-Unterstützung mit Werkzeug, Modell und Datum. Der Kommentar erfüllt die Transparenzregel des Kurses, beeinflusst jedoch weder Paketbytes noch Testergebnisse.

2. Zeile 2 — `# Anfrage: Echte PCAP offline prüfen; Protokoll, Echo-Zuordnung, Header und Readiness-Frist negativ testen.`: Hält den tatsächlichen Testauftrag fest: gespeicherte PCAP offline prüfen und fehlerhafte Protokoll-, Zuordnungs-, Header- und Bereitschaftsfälle gezielt nachweisen.

3. Zeile 3 — `"""Nur Dateilesen und Bytekopien: keine Sockets, Netzänderungen oder neuen Messdaten."""`: Grenzt die Tests ausdrücklich von Netzwerkmessungen ab. Bytekopien sind synthetische Testeingaben und werden weder als reale Pakete versendet noch als neue Messbelege gespeichert.

4. Zeile 4 — `import ast`: Importiert den Python-Syntaxbaumleser. Damit lässt sich ausschließlich der vorhandene Readiness-Block auswählen, ohne den netzverändernden Runner zu importieren oder zu starten.

5. Zeile 5 — `import json`: Importiert JSON-Unterstützung für den Vergleich mit den aufbewahrten Ergebnisdateien. Das Soll wird so aus echten früheren Belegen statt aus erfundenen Antwortwerten gewonnen.

6. Zeile 6 — `from pathlib import Path`: Importiert Path für verlässlich zum Testskript relative Dateipfade. Der Testlauf hängt dadurch nicht vom gerade aktiven Arbeitsverzeichnis ab.

7. Zeile 7 — `import struct`: Importiert struct zum Lesen und Schreiben binärer Längen-, Header- und Identifierfelder. Netzwerkfelder und PCAP-Metadaten verwenden dabei bewusst unterschiedliche Byte-Reihenfolgen.

8. Zeile 8 — `import unittest`: Importiert das Testsystem aus der Python-Standardbibliothek. Es sammelt Testmethoden, meldet Fehler und liefert bei fehlgeschlagenen Prüfungen einen erfolglosen Prozessstatus.

9. Zeile 9 — `from unittest.mock import MagicMock, Mock, patch`: Importiert einfache und kontextmanagerfähige Test-Doubles sowie vorübergehende Ersetzungen. Diese kontrollieren Dateieingaben, Uhr und Selektor ohne echte Aufnahmeprozesse oder Netzwerkbefehle.

10. Zeile 11 — `from pcap_pruefen import inspect`: Übernimmt die tatsächlich zu prüfende inspect-Funktion aus dem benachbarten Parsermodul. Die Tests verwenden keine nachgebaute Alternative als vermeintlichen Produktivparser.

11. Zeile 13 — `BASE = Path(__file__).resolve().parents[1]`: Bestimmt den Übungsordner als übergeordneten Ordner von ue7.4. resolve macht den Dateipfad absolut, parents[1] geht vom Testskript zwei Ebenen nach oben.

12. Zeile 14 — `EVIDENCE = BASE / "nachweise/run01"`: Legt den Speicherort der bereits existierenden run01-Belege fest. Es wird kein neues Nachweisverzeichnis erzeugt und keine dieser Dateien überschrieben.

13. Zeile 17 — `def capture(packets, endian="<", nano=False):`: Definiert einen synthetischen PCAP-Container um vorliegende Framekopien. Standardmäßig werden Little Endian und Mikrosekunden verwendet; beide Einstellungen lassen sich für Formatprüfungen ändern.

14. Zeile 18 — `    magic = 0xa1b23c4d if nano else 0xa1b2c3d4`: Wählt die klassische Magic-Zahl für Nano- oder Mikrosekunden. Die anschließende struct-Kodierung erzeugt daraus entsprechend der gewählten Byte-Reihenfolge die tatsächlichen vier Headerbytes.

15. Zeile 19 — `    raw = struct.pack(endian + "IHHIIII", magic, 2, 4, 0, 0, 262144, 1)`: Erzeugt den 24-Byte-PCAP-Dateiheader mit Version 2.4, Ethernet-Linktyp eins und expliziter maximaler Aufnahmelänge. Die Nullwerte sind synthetische Metadaten und keine behaupteten Messzeitpunkte.

16. Zeile 20 — `    for packet in packets:`: Durchläuft die als Eingabe übergebenen Framebytes. Die Schleife verarbeitet ausschließlich Speicherkopien; sie nimmt keine Pakete von einer Schnittstelle entgegen.

17. Zeile 21 — `        raw += struct.pack(endian + "IIII", 0, 0, len(packet), len(packet)) + packet`: Hängt einen synthetischen 16-Byte-Recordheader und die unveränderten Framebytes an. Gespeicherte und ursprüngliche Länge werden ausdrücklich gleich gesetzt, damit gezielte Paketmutationen nicht an alten Containerlängen scheitern.

18. Zeile 22 — `    return raw`: Gibt den vollständigen synthetischen Container als Bytes zurück. Er wird für Parserprüfungen im Speicher verwendet, nicht als Ersatz eines echten PCAP-Belegs abgelegt.

19. Zeile 25 — `def positions(packet):`: Definiert einen unabhängigen Offsethelfer für die Testmutationen. Seine Rückgabewerte bezeichnen Positionen im kompletten Ethernet-Frame, nicht im PCAP-Dateiheader.

20. Zeile 26 — `    icmp = 14 + (packet[14] & 15) * 4`: Berechnet den äußeren ICMP-Beginn hinter 14 Ethernet-Bytes und dem durch IHL angegebenen IPv4-Header. Optionen würden damit auch beim Auffinden des äußeren ICMP berücksichtigt.

21. Zeile 27 — `    quoted = icmp + 8`: Berechnet den Beginn eines zitierten Pakets hinter dem acht Byte langen äußeren ICMP-Grundheader. Für reine Echoanfragen wird dieser Hilfswert nicht als echtes Zitat interpretiert.

22. Zeile 28 — `    return icmp, quoted, quoted + (packet[quoted] & 15) * 4`: Liefert äußeren ICMP-Beginn, Zitatbeginn und inneren Echo-Beginn. Der dritte Wert berücksichtigt die innere IHL; bei Requestframes verwenden die Tests ausschließlich den ersten Wert.

23. Zeile 31 — `class PcapTests(unittest.TestCase):`: Beginnt die Testklasse für echte Parseraufrufe und gezielt manipulierte Bytekopien. unittest erkennt darin Methoden mit dem Präfix test_ automatisch als einzelne Tests.

24. Zeile 32 — `    def setUp(self):`: Definiert den Aufbau, den unittest vor jeder Parser-Testmethode neu ausführt. Dadurch kann eine Mutation nicht unbeabsichtigt den Ausgangszustand einer anderen Methode verändern.

25. Zeile 33 — `        self.raw = (EVIDENCE / "fault.pcap").read_bytes()`: Liest die vorhandene echte Fehleraufnahme binär und unverändert ein. Diese Datei liefert die Ausgangspakete aller folgenden Varianten, wird selbst aber niemals geöffnet, um darin zu schreiben.

26. Zeile 34 — `        self.expected = json.loads((EVIDENCE / "fault-frames.json").read_text())`: Liest die gespeicherte unabhängige Ergebniszusammenfassung als Sollstruktur ein. Der Test kann dadurch erkennen, ob sich neben der Prüfung auch die öffentliche Rückgabeform verändert hat.

27. Zeile 35 — `        self.assertIn(self.raw[:4], (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"))`: Verlangt für diese konkrete Eingabefixture eine der beiden Little-Endian-Magics. Die echte run01-Aufnahme verwendet Nanosekunden; der folgende kleine Fixtureleser darf deshalb weiterhin Little Endian verwenden.

28. Zeile 36 — `        self.packets, offset = [], 24`: Startet die Liste veränderbarer Paketkopien leer und setzt den Lesecursor hinter den globalen 24-Byte-Header. Keine Länge aus einer vorherigen Testmethode wird wiederverwendet.

29. Zeile 37 — `        while offset < len(self.raw):`: Liest die Records bis zum vorhandenen Dateiende nacheinander aus. Diese Vorbereitung zerlegt nur die vertraute echte Fixture; die eigentlichen Abwehrprüfungen erfolgen anschließend im Produktivparser.

30. Zeile 38 — `            length = struct.unpack_from("<I", self.raw, offset + 8)[0]`: Liest die gespeicherte Framegröße aus dem aktuellen Little-Endian-Recordheader. Das Längenfeld beginnt acht Byte hinter dem Anfang dieses 16-Byte-Headers.

31. Zeile 39 — `            self.packets.append(bytearray(self.raw[offset + 16:offset + 16 + length]))`: Kopiert die Framebytes in ein veränderbares bytearray. Änderungen an dieser Kopie können weder die eingelesenen Originalbytes noch die aufbewahrte PCAP-Datei verändern.

32. Zeile 40 — `            offset += 16 + length`: Verschiebt den Cursor um den Recordheader und die aktuelle Framelänge. So beginnt die nächste Runde am nächsten Record und nicht innerhalb eines Ethernet-Pakets.

33. Zeile 41 — `        self.assertEqual(len(self.packets), 4)`: Verlangt genau vier Frames in der realen Testfixture. Ein irrtümlich ausgetauschter, leerer oder anders aufgebauter Mitschnitt scheitert damit bereits in der Vorbereitung.

34. Zeile 42 — `        self.assertEqual([packet[positions(packet)[0]] for packet in self.packets], [8, 3, 8, 3])`: Kontrolliert die bekannte Typfolge Echo, Fehler, Echo, Fehler. Die nachfolgenden gezielten Mutationen dürfen dadurch auf Index eins und drei als Fehlerframes zugreifen.

35. Zeile 44 — `    def parse(self, raw):`: Definiert den Parseraufruf für synthetische Containerbytes. Die Funktion liefert genau die inspect-Rückgabe und baut kein eigenes fachliches Ergebnis an deren Stelle.

36. Zeile 45 — `        with patch.object(Path, "read_bytes", return_value=bytes(raw)):`: Ersetzt Path.read_bytes nur innerhalb dieses Kontextes durch echte bytes des Testcontainers. Die Umwandlung ist wichtig, weil das reale Path-Verfahren bytes und kein veränderbares bytearray liefert.

37. Zeile 46 — `            return inspect("synthetische-bytekopie.pcap")`: Ruft den echten Parser mit einem ausdrücklich synthetisch benannten Dateipfad auf. Wegen des begrenzten Dateilesepatches wird dabei keine Datei mit diesem Namen angelegt oder vorausgesetzt.

38. Zeile 48 — `    def reject(self, packets, message=None):`: Definiert die gemeinsame Ablehnungsprüfung für manipulierte Frames. Optional kann ein erwarteter Ausschnitt des Fehlertexts sicherstellen, dass die fachlich passende Prüfung anschlägt.

39. Zeile 49 — `        with self.assertRaisesRegex(AssertionError, message or ".*"):`: Verlangt einen AssertionError mit passender Meldung. Ohne explizites Muster genügt jede Assertion; deshalb werden Zuordnungsfehler zusätzlich mit spezifischen Textmustern geprüft.

40. Zeile 50 — `            self.parse(capture(packets))`: Verpackt die manipulierten Frames zuerst mit konsistenten Recordlängen und prüft dann den Container. So bleibt der gezielte Protokollfehler von zufälliger PCAP-Abschneidung getrennt.

41. Zeile 52 — `    def test_real_capture_and_unchanged_result_shape(self):`: Beginnt den positiven Regressionstest der echten Datei und der bisherigen Rückgabeform. Diese Methode benutzt für die Originalaufnahme ausdrücklich keinen Dateilesepatch.

42. Zeile 53 — `        self.assertEqual(inspect(EVIDENCE / "fault.pcap"), self.expected)`: Vergleicht den vollständigen echten Parserbefund mit fault-frames.json. Auch zusätzliche unerwartete Ergebnisfelder würden diesen Gleichheitsvergleich scheitern lassen.

43. Zeile 54 — `        self.assertEqual(self.expected, json.loads((EVIDENCE / "results.json").read_text())["fault"])`: Vergleicht dieselbe Sollstruktur mit dem fault-Eintrag der vollständigen results.json. Die neue stärkere Zuordnung darf vorhandene korrekt dokumentierte Ergebnisse nicht nachträglich verändern.

44. Zeile 56 — `    def test_all_four_pcap_magics(self):`: Beginnt den positiven Formatvergleich aller vier klassischen PCAP-Magics. Die Paketbytes stammen weiterhin aus run01, nur der umgebende Container ist synthetisch erzeugt.

45. Zeile 57 — `        for endian in ("<", ">"):`: Durchläuft Little Endian und Big Endian als explizite Container-Byte-Reihenfolgen. Die Netzwerk-Byte-Reihenfolge innerhalb der Ethernet-Frames wird davon nicht geändert.

46. Zeile 58 — `            for nano in (False, True):`: Durchläuft innerhalb jeder Byte-Reihenfolge Mikro- und Nanosekundenkennungen. Die verschachtelten Schleifen bilden dadurch die vollständige Kombination beider Optionen.

47. Zeile 59 — `                with self.subTest(endian=endian, nano=nano):`: Kennzeichnet jede Kombination als benannten Untertest. Bei einem Fehler zeigt unittest damit unmittelbar an, welche Byte-Reihenfolge und Zeitauflösung betroffen ist.

48. Zeile 60 — `                    self.assertEqual(self.parse(capture(self.packets, endian, nano)), self.expected)`: Verlangt für alle vier Container denselben vollständigen fachlichen Parserbefund. Unterschiede in Aufnahme-Metadaten dürfen die ausgewerteten ICMP-Felder nicht beeinflussen.

49. Zeile 62 — `    def test_wrong_quoted_protocol(self):`: Beginnt den Negativtest eines falschen zitierten Transportprotokolls. Er prüft gerade die frühere Lücke, dass allein passende IP-Adressen als Fehlerzuordnung genügten.

50. Zeile 63 — `        _, quoted, _ = positions(self.packets[1])`: Ermittelt den tatsächlichen Zitatbeginn im ersten Fehlerframe. Die unbenutzten äußeren und inneren ICMP-Offsets werden mit Unterstrichen bewusst verworfen.

51. Zeile 64 — `        self.packets[1][quoted + 9] = 17`: Ändert nur das innere IPv4-Protokollfeld auf 17, also UDP. Die äußere Meldung und die zitierten Adressen bleiben passend, sodass die neue ICMP-Protokollprüfung entscheidend sein muss.

52. Zeile 65 — `        self.reject(self.packets, "Zitiertes Protokoll")`: Fordert die gezielte Ablehnung mit der Protokollfehlermeldung. Ein bloßer späterer Zählerfehler wäre kein ausreichender Nachweis für diese neue Prüfung.

53. Zeile 67 — `    def test_wrong_quoted_echo_type_or_code(self):`: Beginnt die Negativprüfung des inneren ICMP-Typs und Codes. Beide Felder müssen einen Echo Request kennzeichnen und dürfen nicht nur zufällig eine passende ID enthalten.

54. Zeile 68 — `        _, _, echo = positions(self.packets[1])`: Findet den inneren Echo-Header anhand der zitierten IHL. Der Test mutiert dadurch die fachlich richtige Position statt einen pauschalen, möglicherweise falschen Offset.

55. Zeile 69 — `        for offset, value in ((echo, 0), (echo + 1, 1)):`: Plant getrennte Varianten mit Echo Reply statt Echo Request und mit ungültigem Code eins. Jede Variante ändert genau eines der beiden relevanten Bytes.

56. Zeile 70 — `            with self.subTest(offset=offset):`: Kennzeichnet die jeweils veränderte Feldposition als Untertest. Ein Fehlschlag lässt sich dadurch dem Typ- oder Codefall zuordnen.

57. Zeile 71 — `                packets = [packet.copy() for packet in self.packets]`: Erstellt für diese Typ-/Codevariante frische Framekopien. Die beiden Varianten sollen sich nicht gegenseitig durch eine bereits vorgenommene Mutation beeinflussen.

58. Zeile 72 — `                packets[1][offset] = value`: Schreibt den geplanten falschen Typ beziehungsweise Code in den ersten Fehlerframe. Alle anderen Bytes bleiben gegenüber dem Ausgangsframe erhalten.

59. Zeile 73 — `                self.reject(packets, "Zitierter Echo Request")`: Verlangt die spezifische Meldung für einen unzulässigen zitierten Echo Request. Damit wird nachgewiesen, dass diese neue Inhaltsprüfung tatsächlich ausgeführt wird.

60. Zeile 75 — `    def test_error_for_unknown_id_or_sequence(self):`: Beginnt die Fehlzuordnungsprüfung für unbekannten Identifier oder unbekannte Sequenz. Gleiche Paketanzahl und passende Adressen dürfen einen solchen Fehler nicht verdecken.

61. Zeile 76 — `        _, _, echo = positions(self.packets[1])`: Ermittelt für die Zuordnungsvarianten den Beginn des ersten zitierten Echo-Headers. ID und Sequenz werden anschließend relativ zu diesem geprüften Testoffset verändert.

62. Zeile 77 — `        for offset in (echo + 4, echo + 6):`: Durchläuft getrennt das Identifierfeld ab Offset vier und das Sequenzfeld ab Offset sechs. Beide Felder müssen zur Anfrage gehören, nicht nur eines davon.

63. Zeile 78 — `            with self.subTest(offset=offset):`: Eröffnet je Identifier- oder Sequenzmutation einen Untertest. Das Testprotokoll unterscheidet dadurch eindeutig, welches Schlüsselteil nicht erkannt wurde.

64. Zeile 79 — `                packets = [packet.copy() for packet in self.packets]`: Kopiert alle Ausgangsframes erneut für die einzelne unbekannte Schlüsselvariante. Die andere Variante behält damit ihren unveränderten echten Ausgangsschlüssel.

65. Zeile 80 — `                packets[1][offset] ^= 1`: Kippt genau ein Bit im ausgewählten Identifier- oder Sequenzbyte. Der daraus entstandene Schlüssel ist bewusst eine synthetische Fehlzuordnung und kein gemessener neuer Ping.

66. Zeile 81 — `                self.reject(packets, "nicht eindeutig")`: Verlangt die abschließende eindeutige Zuordnungsfehlermeldung. Die Inhalte bleiben ansonsten so plausibel, dass die neue Schlüssellistenprüfung den entscheidenden Unterschied macht.

67. Zeile 83 — `    def test_duplicate_errors_do_not_cover_both_requests(self):`: Beginnt den Test zweier Fehler, die beide dieselbe Anfrage zitieren. Eine einfache Prüfung auf zwei Requests und zwei Fehler würde diesen fachlichen Mangel nicht erkennen.

68. Zeile 84 — `        first = positions(self.packets[1])[2]`: Bestimmt den inneren Echo-Offset im ersten Fehlerframe. Von dort werden anschließend die vier Identifier-/Sequenzbytes als Duplikatquelle genommen.

69. Zeile 85 — `        second = positions(self.packets[3])[2]`: Bestimmt unabhängig den inneren Echo-Offset im zweiten Fehlerframe. So funktioniert die Mutation auch dann, wenn die zitierten IP-Header unterschiedlich lang wären.

70. Zeile 86 — `        self.packets[3][second + 4:second + 8] = self.packets[1][first + 4:first + 8]`: Kopiert ID und Sequenz des ersten Fehlers in den zweiten. Nun fehlt ein Fehler zur anderen Anfrage, obwohl Anzahl, Adressen und Typen weiterhin stimmen.

71. Zeile 87 — `        self.reject(self.packets, "nicht eindeutig")`: Fordert die Ablehnung der doppelten Fehlerzuordnung. Dieser Test kontrolliert, dass zwei äußere Fehlermeldungen nicht als zwei erfolgreich zugeordnete Anfragen gelten, wenn beide denselben inneren Schlüssel zitieren.

72. Zeile 89 — `    def test_duplicate_request_keys_even_with_matching_errors(self):`: Beginnt die Eindeutigkeitsprüfung bei zugleich passend duplizierten Anfragen und Fehlern. Der reine Multimengenvergleich allein würde diese symmetrische Duplizierung akzeptieren.

73. Zeile 90 — `        for first, second, part in ((0, 2, 0), (1, 3, 2)):`: Plant die Duplizierung einmal für äußere Echo-Requests und einmal für innere Echozitate. part wählt dafür den ersten beziehungsweise dritten Rückgabewert des Offsethelfers.

74. Zeile 91 — `            a, b = positions(self.packets[first])[part], positions(self.packets[second])[part]`: Ermittelt Quell- und Zieloffset innerhalb der beiden betroffenen Frames. Die Mehrfachzuweisung hält die Zuordnung zwischen erstem und zweitem Datensatz ausdrücklich fest.

75. Zeile 92 — `            self.packets[second][b + 4:b + 8] = self.packets[first][a + 4:a + 8]`: Kopiert die vier Schlüsselbytes auf den zweiten Datensatz derselben Art. Nach beiden Schleifenrunden sind Requests und Fehler identisch dupliziert, aber nicht mehr einzeln unterscheidbar.

76. Zeile 93 — `        self.reject(self.packets, "Doppelte Echo-ID/Sequenz")`: Verlangt ausdrücklich die Meldung über doppelte Echo-ID/Sequenz. So ist belegt, dass die zusätzliche Anfrage-Einzigkeitsprüfung nicht bloß versehentlich durch den Multimengenvergleich ersetzt wurde.

77. Zeile 95 — `    def test_minimum_quote_is_valid_but_seven_echo_bytes_are_not(self):`: Beginnt den Grenztest einer regulär gekürzten ICMP-Zitierung. Acht Echo-Bytes müssen genügen; sieben Bytes dürfen nicht durch Padding oder ursprüngliche IP-Längen legitimiert werden.

78. Zeile 96 — `        _, _, echo = positions(self.packets[1])`: Bestimmt den inneren Echoanfang im ersten Fehlerframe als Bezugspunkt für die Kürzung. Der zitierte IPv4-Grundheader bleibt bei dieser Mutation vollständig erhalten.

79. Zeile 97 — `        for length in (8, 7):`: Durchläuft die erlaubte Mindestgröße acht und die zu kurze Größe sieben. Beide Container bekommen später passende äußere Längen, damit gerade die innere Mindestgrenze geprüft wird.

80. Zeile 98 — `            with self.subTest(echo_bytes=length):`: Kennzeichnet die Zahl vorhandener Echo-Bytes als Untertestparameter. Das trennt den positiven Grenzfall sichtbar von der erwarteten Ablehnung.

81. Zeile 99 — `                packets = [packet.copy() for packet in self.packets]`: Erzeugt für jeden Kürzungsfall neue Kopien der ursprünglichen Frames. So wird die Sieben-Byte-Variante nicht aus einer bereits gekürzten und anders veränderten Zwischenversion erzeugt.

82. Zeile 100 — `                packets[1] = packets[1][:echo + length]`: Schneidet den ersten Fehlerframe exakt nach den gewählten Echo-Bytes ab. Die ursprüngliche innere IP-Gesamtlänge bleibt absichtlich größer, wie es bei regulären ICMP-Zitaten zulässig ist.

83. Zeile 101 — `                struct.pack_into("!H", packets[1], 16, len(packets[1]) - 14)`: Passt die äußere IP-Gesamtlänge an die tatsächlich vorhandenen Framebytes an. Offset sechzehn ergibt sich aus Ethernet-Header plus dem IP-Längenoffset zwei.

84. Zeile 102 — `                if length == 8:`: Unterscheidet ausdrücklich den zulässigen Acht-Byte-Grenzfall. Dieser positive Zweig verhindert eine überstrenge Implementierung, die immer das vollständige zitierte Originalpaket verlangen würde.

85. Zeile 103 — `                    self.assertEqual(self.parse(capture(packets)), self.expected)`: Fordert für das minimale vollständige Echozitat weiterhin das bisherige Gesamtergebnis. Alle zur Zuordnung benötigten ICMP-Grundfelder sind darin bereits enthalten.

86. Zeile 104 — `                else:`: Öffnet den Gegenfall der unvollständigen Zitierung. Der alternative Zweig behandelt keinen normalen zweiten Messlauf, sondern nur die synthetische Sieben-Byte-Eingabe.

87. Zeile 105 — `                    self.reject(packets)`: Verlangt die Ablehnung eines unvollständigen inneren Echo-Headers. Dass die äußeren Record- und IP-Längen konsistent sind, darf diese inhaltliche Abschneidung nicht verbergen.

88. Zeile 107 — `    def test_quoted_options_shift_echo_header(self):`: Beginnt die positive und negative Prüfung verschobener innerer Echo-Header durch IP-Optionen. Sie soll einen Parser entlarven, der ID und Sequenz immer ab pauschalem Offset zwanzig liest.

89. Zeile 108 — `        packet = self.packets[1]`: Wählt die veränderbare Kopie des ersten Fehlerframes aus. Änderungen an packet wirken nur auf self.packets und nicht auf die gespeicherte Originalaufnahme.

90. Zeile 109 — `        _, quoted, _ = positions(packet)`: Liest den Zitatbeginn vor dem Einfügen von Optionen aus. Die Headeroptionen werden anschließend relativ zu diesem stabilen Zitatbeginn ergänzt.

91. Zeile 110 — `        packet[quoted + 20:quoted + 20] = b"\x01\x01\x01\x00"`: Fügt vier Optionsbytes nach dem zwanzig Byte langen IPv4-Grundheader ein. Die Folge verwendet einfache NOP- und Ende-Markierungen, verschiebt aber den eigentlichen Echo-Header.

92. Zeile 111 — `        packet[quoted] = 0x46`: Setzt IPv4-Version vier und IHL sechs, also einen 24-Byte-Header. Der Parser muss die eingefügten Optionen überspringen, bevor er die Echo-Felder interpretiert.

93. Zeile 112 — `        for offset in (16, quoted + 2):`: Wählt sowohl das äußere als auch das innere IP-Gesamtlängenfeld zur Anpassung. Beide Paketsichten haben durch die eingefügten Optionen vier zusätzliche Bytes.

94. Zeile 113 — `            struct.pack_into("!H", packet, offset, struct.unpack_from("!H", packet, offset)[0] + 4)`: Erhöht die jeweils vorhandene Netzwerk-Längenzahl um vier. Die Container-Recordlängen werden unabhängig davon später durch capture neu berechnet.

95. Zeile 114 — `        self.assertEqual(self.parse(capture(self.packets)), self.expected)`: Verlangt zunächst die erfolgreiche Zuordnung mit korrekt verschobenem innerem Echo. Die Testvariante ist synthetisch und überprüft Strukturgrenzen, nicht die hier nicht validierten Prüfsummen.

96. Zeile 115 — `        packet[positions(packet)[2] + 6] ^= 1`: Verändert danach ein Sequenzbyte an der nun durch IHL verschobenen Position. Die vorherige positive Optionsvariante wird so zu einer gezielten negativen Zuordnungsvariante.

97. Zeile 116 — `        self.reject(self.packets, "nicht eindeutig")`: Fordert auch hinter vorhandenen Optionen die Ablehnung des falschen Schlüssels. Damit wird geprüft, dass der positive Test nicht nur aufgrund zufällig passender Optionsbytes bestanden wurde.

98. Zeile 118 — `    def test_bad_ip_header_bytes(self):`: Beginnt die Sammlung falscher IPv4-Headerbytes. Geprüft werden innere und äußere Version/IHL, eine widersprüchliche innere Länge und nicht unterstützte Fragmentierung.

99. Zeile 119 — `        _, quoted, _ = positions(self.packets[1])`: Bestimmt den inneren Headerbeginn für die folgenden festen Feldmutationen. Die Fehlerframes bleiben dabei ansonsten vollständig im Speicher erhalten.

100. Zeile 120 — `        cases = ((0, 14, b"\x44"), (0, 14, b"\x65"), (1, quoted, b"\x44"),`: Legt Varianten für zu kurze äußere IHL, falsche äußere Version und zu kurze innere IHL an. Die Tupel nennen jeweils Frameindex, Byteoffset und die einzusetzende Bytefolge.

101. Zeile 121 — `                 (1, quoted, b"\x65"), (1, quoted + 2, b"\x00\x1b"),`: Ergänzt eine falsche innere IP-Version sowie eine innere Gesamtlänge von nur 27 Byte. Letztere kann nicht zugleich zwanzig Headerbytes und acht Echo-Bytes umfassen.

102. Zeile 122 — `                 (1, quoted + 6, b"\x20\x00"), (1, quoted + 6, b"\x00\x01"))`: Ergänzt zwei innere Fragmentierungsfälle: More-Fragments und einen Fragmentoffset. Beide widersprechen der im gezielten Parser vorausgesetzten unfragmentierten Echoanfrage.

103. Zeile 123 — `        for frame, offset, value in cases:`: Durchläuft alle ausdrücklich aufgelisteten Headerfehler. Jede Runde übernimmt die drei Tupelfelder in lokale Variablen für eine nachvollziehbare Mutation.

104. Zeile 124 — `            with self.subTest(frame=frame, offset=offset, value=value):`: Kennzeichnet Frame, Feldposition und falsche Bytes als Untertest. Dadurch bleibt bei mehreren strukturellen Grenzfällen sichtbar, welcher Fall fälschlich akzeptiert würde.

105. Zeile 125 — `                packets = [packet.copy() for packet in self.packets]`: Erstellt pro Headerfehler eine neue vollständige Kopie aller Frames. Die verschiedenen ungültigen Headerzustände werden nicht kumulativ miteinander vermischt.

106. Zeile 126 — `                packets[frame][offset:offset + len(value)] = value`: Ersetzt genau so viele Bytes, wie die jeweilige Variante vorgibt. Die Slicezuweisung verändert die Paketgröße hier nicht, sondern nur den ausgewählten Headerinhalt.

107. Zeile 127 — `                self.reject(packets)`: Verlangt für jede dieser strukturellen Fehlervarianten einen AssertionError. Ein beliebiger anderer Laufzeitfehler wäre dabei kein bestandener Test.

108. Zeile 129 — `    def test_claimed_quoted_options_must_be_present(self):`: Beginnt den Test einer nur behaupteten, aber nicht vollständig zitierten IP-Option. Eine vergrößerte IHL darf fehlende Echo-Bytes nicht verdecken.

109. Zeile 130 — `        _, quoted, _ = positions(self.packets[1])`: Ermittelt den Anfang des inneren IPv4-Headers im ersten Fehlerframe. Der spätere Kürzungsendpunkt wird von diesem Anfang aus berechnet.

110. Zeile 131 — `        self.packets[1] = self.packets[1][:quoted + 28]`: Begrenzt das Zitat auf 28 Byte, also den üblichen Minimalfall ohne Optionen. Danach sind nicht genug Bytes für 24 Headerbytes plus acht Echo-Bytes vorhanden.

111. Zeile 132 — `        struct.pack_into("!H", self.packets[1], 16, len(self.packets[1]) - 14)`: Korrigiert die äußere IP-Gesamtlänge nach der Kürzung. Damit soll die Ablehnung aus der inneren IHL-/Zitiergrenze und nicht aus einem kaputten äußeren Paket entstehen.

112. Zeile 133 — `        self.packets[1][quoted] = 0x46`: Behauptet einen 24-Byte-IPv4-Header durch IHL sechs. Das reale Zitat endet nun schon nach vier statt acht verfügbaren Folgebytes und muss als unvollständig gelten.

113. Zeile 134 — `        self.reject(self.packets)`: Fordert die Ablehnung der nicht ausreichend vorhandenen Header-/Echo-Kombination. Die bloße alte Mindestprüfung von 28 zitierten Bytes hätte diesen Fall nicht erkannt.

114. Zeile 136 — `    def test_truncated_records_and_packets(self):`: Beginnt die Prüfung abgeschnittener PCAP-Records und widersprüchlicher Aufnahmelängen. Diese Containerfehler sind von inneren IP-/ICMP-Inhaltsfehlern ausdrücklich getrennt.

115. Zeile 137 — `        for raw in (self.raw[:-1], self.raw[:30]):`: Plant eine um das letzte Paketbyte gekürzte Datei und eine Datei mit nur sechs Recordheaderbytes. Beide Varianten stammen als Speicherslices aus der vollständigen Originalaufnahme.

116. Zeile 138 — `            with self.subTest(length=len(raw)), self.assertRaisesRegex(AssertionError, "Abgeschnitten"):`: Verknüpft die benannte Längenvariante mit der Erwartung einer Abschneidungs-Assertion. Der Kontext verlangt eine fachlich passende Meldung statt eines zufälligen Indexfehlers.

117. Zeile 139 — `                self.parse(raw)`: Lässt die jeweilige gekürzte Bytefolge vom echten Parser lesen. Das temporäre Dateilesepatch schreibt dabei keine abgeschnittenen Dateien in die Nachweise.

118. Zeile 140 — `        raw = bytearray(self.raw)`: Kopiert die vollständigen Originalbytes erneut für den Fall widersprüchlicher Recordlängen. Dieser Fehler soll unabhängig von den vorherigen Dateikürzungen entstehen.

119. Zeile 141 — `        struct.pack_into("<I", raw, 36, struct.unpack_from("<I", raw, 36)[0] + 1)`: Erhöht die ursprüngliche Framelänge im ersten Record um eins, ohne captured anzupassen. Der Parser muss das unvollständige Snaplen-/Längenverhältnis unabhängig von vorhandenem Dateiinhalt ablehnen.

120. Zeile 142 — `        with self.assertRaisesRegex(AssertionError, "Abgeschnittenes Paket"):`: Verlangt die konkrete Meldung eines abgeschnittenen Pakets für die Längeninkonsistenz. Das kontrolliert die bereits vorhandene Gleichheitsprüfung von captured und original.

121. Zeile 143 — `            self.parse(raw)`: Übergibt den Container mit widersprüchlicher Originallänge an inspect. Die Konvertierung in parse stellt dabei den realen Rückgabetyp von Path.read_bytes wieder her.

122. Zeile 145 — `    def test_invalid_global_header_bytes(self):`: Beginnt die Prüfung unvollständiger oder falsch gekennzeichneter globaler PCAP-Header. Ein geöffnetes Byteobjekt allein ist noch keine gültige Aufnahme.

123. Zeile 146 — `        for raw in (self.raw[:23], b"BAD!" + self.raw[4:]):`: Plant einen nur 23 Byte langen Globalheader und eine unbekannte Magic. Beide Fälle sollen vor einer Interpretation der Ethernet- oder IP-Daten zurückgewiesen werden.

124. Zeile 147 — `            with self.subTest(length=len(raw)), self.assertRaises(ValueError):`: Kennzeichnet die Eingabelänge und erwartet ausdrücklich ValueError. Der Parser verwendet diesen Ausnahmetyp für eine ungültige klassische PCAP-Grundkennung.

125. Zeile 148 — `                self.parse(raw)`: Ruft die Grundheaderprüfung mit der jeweiligen fehlerhaften Bytefolge auf. Die übrigen Originalbytes bleiben für die Magic-Variante unverändert vorhanden.

126. Zeile 149 — `        raw = bytearray(self.raw)`: Erstellt eine neue veränderbare Gesamtdateikopie für den Linktypfehler. So ist dieser Fall nicht zugleich durch den vorherigen Magic-Fehler beschädigt.

127. Zeile 150 — `        struct.pack_into("<I", raw, 20, 113)`: Schreibt Linktyp 113 an Offset zwanzig des Globalheaders. Linux-Cooked-Capture ist kein Ethernet und darf nicht mit dem festen Ethernet-Offset interpretiert werden.

128. Zeile 151 — `        with self.assertRaisesRegex(AssertionError, "Ethernet erwartet"):`: Erwartet ausdrücklich die Assertion mit dem Hinweis auf benötigtes Ethernet. Damit ist belegt, dass der Parser die Linkschichtkennung vor dem Frameinhalt prüft.

129. Zeile 152 — `            self.parse(raw)`: Lässt den Container mit ungültigem Linktyp durch den normalen Parserpfad laufen. Das geschieht ausschließlich im Speicher und ohne Änderung des echten Mitschnitts.

130. Zeile 155 — `class ReadinessTests(unittest.TestCase):`: Beginnt die isolierten Readiness-Regressionstests. Diese prüfen echten ausgewählten Quellcode mit simulierten Abhängigkeiten und behaupten keine neue dumpcap-Aufnahme.

131. Zeile 156 — `    def setUp(self):`: Definiert die Vorbereitung jedes Bereitschaftstests. Für jeden Fall entstehen neue Uhr-, Selektor- und Lesedoubles ohne gemeinsam fortgeschriebene Zustände.

132. Zeile 157 — `        tree = ast.parse((BASE / "verify_namespaces.py").read_text())`: Liest den Runner nur als Text und zerlegt ihn in einen Syntaxbaum. Weder dessen Importe noch main oder netzverändernde Funktionen werden dadurch ausgeführt.

133. Zeile 158 — `        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "capture_fault")`: Wählt im Syntaxbaum die echte Funktion capture_fault anhand von Knotentyp und Namen aus. Fehlt sie, scheitert die Vorbereitung statt still einen Ersatzalgorithmus zu testen.

134. Zeile 159 — `        block = next(node for node in ast.walk(function) if isinstance(node, ast.With) and`: Sucht innerhalb dieser Funktion einen with-Block mit passender Kontextmanagerstruktur. Die Auswahl wird in der nächsten physischen Quellzeile auf den tatsächlichen Selektor eingegrenzt.

135. Zeile 160 — `                     ast.unparse(node.items[0].context_expr) == "selectors.DefaultSelector()")`: Fordert als Kontextausdruck genau selectors.DefaultSelector(). Dadurch wird der Bereitschaftsblock und nicht etwa der äußere Dateischreibkontext zum Testobjekt.

136. Zeile 161 — `        wrapper = ast.parse("def wait(process):\n    start = b''\n    return start\n")`: Erstellt eine minimale Funktionshülle mit leerem Startpuffer und Rückgabe des Puffers. Nur der ausgewählte Originalblock wird anschließend zwischen diese beiden Anweisungen eingefügt.

137. Zeile 162 — `        assert isinstance(wrapper.body[0], ast.FunctionDef)`: Kontrolliert die erwartete Syntaxknotenart der neu erzeugten Hülle. Neben der Testabsicherung erlaubt dies statischen Prüfwerkzeugen den sicheren Zugriff auf deren body-Liste.

138. Zeile 163 — `        wrapper.body[0].body.insert(1, block)`: Setzt den unveränderten Original-Selektorblock in die Hülle ein. Die Tests üben dadurch die aktuelle Implementierung statt einer manuell kopierten Wartealgorithmusversion aus.

139. Zeile 164 — `        self.clock, self.os, selectors = Mock(), Mock(), Mock()`: Erzeugt einfache Doubles für monotone Uhr, Betriebssystemlesen und Selektorfabrik. Ihre Werte werden in den einzelnen Tests ausdrücklich vorgegeben, nicht als reale Systembeobachtung ausgegeben.

140. Zeile 165 — `        manager = selectors.DefaultSelector.return_value = MagicMock()`: Stellt einen kontextmanagerfähigen Factory-Rückgabewert bereit. MagicMock besitzt die benötigten Methoden zum Betreten und Verlassen des with-Blocks.

141. Zeile 166 — `        self.selector = manager.__enter__.return_value`: Merkt sich den beim Betreten gelieferten Selektor als direkt steuerbares Double. Seine select-Methode erhält später Ereignisfolgen oder eine dauerhaft leere Antwort.

142. Zeile 167 — `        namespace = {"time": self.clock, "os": self.os, "selectors": selectors}`: Legt den Namensraum fest, den der ausgewählte Originalblock bei Ausführung sieht. Uhr-, Lese- und Selektorzugriffe gehen ausschließlich an die kontrollierten Testobjekte.

143. Zeile 168 — `        exec(compile(ast.fix_missing_locations(wrapper), "<original-readiness-block>", "exec"), namespace)`: Ergänzt Syntaxpositionen, kompiliert die Hülle und definiert sie im isolierten Namensraum. Die Ausführung definiert lediglich wait; der restliche Runner und seine Netzwerkoperationen sind nicht Bestandteil dieses Syntaxbaums.

144. Zeile 169 — `        self.wait = namespace["wait"]`: Übernimmt die neu definierte Wartefunktion als Testaufruf. Sie enthält den aktuellen Originalblock, ohne den ursprünglichen Programmeinstieg zu starten.

145. Zeile 170 — `        self.process = Mock()`: Erzeugt ein Prozessdouble für stderr und fileno. Es wird weder Popen noch ein Betriebssystemprozess erzeugt; die vermeintlichen Lesedaten stammen aus self.os.read.

146. Zeile 172 — `    def test_idle_and_capturing_message_are_not_readiness(self):`: Beginnt den Regressionstest einer stillen Phase und einer zu frühen Capturing-on-Meldung. Beides darf vor File: - nicht als Aufnahmebereitschaft interpretiert werden.

147. Zeile 173 — `        self.clock.monotonic.side_effect = [0, 0, 1, 2, 3]`: Gibt monotone Uhrwerte für Fristsetzung und vier Schleifenrunden vor. Die Werte liegen innerhalb der festen Fünfsekundenfrist und verursachen kein reales Schlafen.

148. Zeile 174 — `        self.selector.select.side_effect = [[], [True], [], [True]]`: Simuliert abwechselnd einen stillen Warteabschnitt und ein lesbares Ereignis. Die leeren Listen müssen fortgesetzt werden und dürfen nicht bereits einen RuntimeError auslösen.

149. Zeile 175 — `        self.os.read.side_effect = [b"Capturing on 'client-eth0'\n", b"File: -\n"]`: Liefert zuerst die unzureichende Capturing-on-Meldung und erst später File: -. Dadurch belegt die Methode zugleich, dass der spätere konkrete Bereitschaftsmarker erhalten bleibt.

150. Zeile 176 — `        self.assertIn(b"File: -", self.wait(self.process))`: Verlangt den tatsächlichen File-Marker im zurückgegebenen Puffer. Eine vorzeitige Rückkehr nach der ersten Diagnosemeldung würde diese Prüfung verfehlen.

151. Zeile 177 — `        self.assertEqual(self.selector.select.call_count, 4)`: Fordert vier Selektoraufrufe entsprechend der geplanten Ereignisfolge. Das würde sowohl einen Idle-Frühabbruch als auch einen vorzeitigen Erfolg nach Capturing on sichtbar machen.

152. Zeile 178 — `        self.assertEqual(self.os.read.call_count, 2)`: Fordert genau zwei Leseaufrufe, also nur bei den beiden Leseereignissen. Stille Warteantworten dürfen nicht in ein blockierendes blindes os.read übergehen.

153. Zeile 180 — `    def test_idle_only_fails_at_full_deadline(self):`: Beginnt den Test dauerhaft ausbleibender Ausgabe bis zum echten Fristende. Er unterscheidet den früheren Einsekundenabbruch vom korrekten Warten bis Sekunde fünf.

154. Zeile 181 — `        self.clock.monotonic.side_effect = [0, 0, 1, 2, 3, 4, 5]`: Simuliert Fristsetzung bei null und anschließende monotone Werte von null bis fünf. Dadurch lässt sich die gesamte Wartefrist deterministisch und ohne tatsächliche Verzögerung durchlaufen.

155. Zeile 182 — `        self.selector.select.return_value = []`: Lässt den Selektor in jeder Runde eine leere Ereignisliste liefern. Es steht also zu keinem Zeitpunkt eine zu lesende Bereitschaftsmeldung zur Verfügung.

156. Zeile 183 — `        with self.assertRaisesRegex(RuntimeError, "Capture nicht bereit"):`: Verlangt beim Ablauf der Gesamtfrist die konkrete Capture-nicht-bereit-Ausnahme. Eine ausbleibende Bereitschaft darf weder endlos warten noch als Erfolg zurückgegeben werden.

157. Zeile 184 — `            self.wait(self.process)`: Ruft den Originalblock mit dieser rein simulierten stillen Ereignisfolge auf. Die umgebende Ausnahmeprüfung behandelt das erwartete Fristende als bestandenen Negativtest.

158. Zeile 185 — `        self.assertEqual(self.selector.select.call_count, 5)`: Verlangt fünf vollständige Selektoraufrufe vor der Fristausnahme. Ein frühzeitiger Fehler schon nach der ersten leeren Antwort würde diese Anzahlprüfung scheitern lassen.

159. Zeile 186 — `        self.os.read.assert_not_called()`: Fordert, dass nie vom Betriebssystemdouble gelesen wurde. Ohne Leseereignis darf der Warteblock nicht versuchen, eine vermeintlich bereitliegende Pipe auszulesen.

160. Zeile 188 — `    def test_select_timeout_is_bounded_by_remaining_time(self):`: Beginnt den Grenztest eines letzten kurzen Wartefensters unmittelbar vor Fristende. Die Polling-Einsekunde darf die verbleibende Viertelsekunde nicht überschreiten.

161. Zeile 189 — `        self.clock.monotonic.side_effect = [0, 4.75, 5]`: Simuliert den Start bei null und die nächste Prüfung bei 4,75 Sekunden. Der folgende Uhrwert fünf löst dann die feste Fristausnahme aus.

162. Zeile 190 — `        self.selector.select.return_value = []`: Gibt auch für den letzten kurzen Warteabschnitt kein Leseereignis vor. Das Fristende folgt damit aus der Uhr und nicht aus EOF oder einer anderen Prozessmeldung.

163. Zeile 191 — `        with self.assertRaisesRegex(RuntimeError, "Capture nicht bereit"):`: Verlangt erneut die konkrete Ausnahme für eine nicht rechtzeitig bereite Aufnahme. Dieser Test prüft die zeitliche Begrenzung und nicht die Dekodierung von Fehlermeldungen.

164. Zeile 192 — `            self.wait(self.process)`: Durchläuft mit den vorgegebenen Restzeiten den ausgewählten Original-Wartecode. Eine reale Uhr oder ein echter Selektor werden dabei nicht verwendet.

165. Zeile 193 — `        self.selector.select.assert_called_once_with(0.25)`: Fordert genau einen Selektoraufruf mit einem Timeout von 0,25 Sekunden. Damit wird die Verwendung von min(1, remaining) statt eines pauschalen Einsekunden-Timeouts nachgewiesen.

166. Zeile 195 — `    def test_eof_is_not_readiness(self):`: Beginnt den EOF-Negativtest für eine geschlossene Diagnoseleitung. Eine lesbare Pipe mit null gelesenen Bytes ist keine verspätete Bereitschaft und muss abbrechen.

167. Zeile 196 — `        self.clock.monotonic.side_effect = [0, 0]`: Simuliert Fristsetzung und ersten Schleifendurchlauf beide bei null. Das folgende Scheitern kann daher nicht versehentlich aus einer abgelaufenen Zeitfrist stammen.

168. Zeile 197 — `        self.selector.select.return_value = [True]`: Meldet dem Wartecode einen lesbaren Selektorzustand. Erst so soll er die simulierte Pipe tatsächlich auslesen und deren EOF erkennen.

169. Zeile 198 — `        self.os.read.return_value = b""`: Liefert beim Lesen eine leere Bytefolge als End-of-File-Signal. Dieser Fall unterscheidet sich ausdrücklich von einer leeren Ereignisliste ohne Leseaufruf.

170. Zeile 199 — `        with self.assertRaises(RuntimeError):`: Fordert einen RuntimeError wegen des vorzeitigen Kanalendes. Der Inhalt der Diagnose kann hier leer sein, weil vor EOF noch keine Meldung geliefert wurde.

171. Zeile 200 — `            self.wait(self.process)`: Führt den EOF-Fall mit dem Originalblock aus. Ein fälschlicher Erfolg oder Weiterwarten würde die erwartete Ausnahme nicht liefern.

172. Zeile 202 — `    def test_readiness_marker_can_span_reads(self):`: Beginnt die positive Prüfung eines über zwei Lesevorgänge geteilten Markers. Die Schleife muss Diagnosebytes sammeln und darf nur vollständige Einzelstücke nicht voraussetzen.

173. Zeile 203 — `        self.clock.monotonic.side_effect = [0, 0, 1]`: Gibt Uhrwerte für Start und zwei rechtzeitige Leserunden vor. Das Aufteilen der Meldung bleibt damit klar innerhalb der absoluten Bereitschaftsfrist.

174. Zeile 204 — `        self.selector.select.return_value = [True]`: Lässt den Selektor für beide Runden Datenverfügbarkeit melden. Eine stille Phase ist hier nicht das Testziel, sondern ausschließlich die Pufferzusammensetzung.

175. Zeile 205 — `        self.os.read.side_effect = [b"Fi", b"le: -\n"]`: Zerlegt File: - absichtlich in Fi und le: - mit Zeilenumbruch. Keiner der beiden einzelnen Leseteile enthält den vollständigen gesuchten Marker.

176. Zeile 206 — `        self.assertEqual(self.wait(self.process), b"File: -\n")`: Verlangt die korrekt zusammengesetzte Gesamtmeldung als Rückgabe. So wird das fortlaufende Anhängen an start anhand des aktuellen Originalcodes geprüft.

177. Zeile 209 — `if __name__ == "__main__":`: Aktiviert den direkten Teststart nur beim Ausführen dieser Datei als Programm. Beim Import durch unittest bleibt die Testsammlung möglich, ohne einen zweiten Testlauf automatisch zu starten.

178. Zeile 210 — `    unittest.main(verbosity=2)`: Startet unittest mit ausführlichen Testnamen und Ergebnissen. Der Prozessstatus eignet sich zur automatischen Verifikation; für den Testlauf sind weder Rootrechte noch Mininet nötig.

## Maschinelle Abdeckung und Ergebnis

**178 von 178** nichtleeren Quellzeilen werden in Originalreihenfolge genau einmal erklärt. Ein unabhängiger Leser vergleicht alle Einträge nach Zeilennummer, vollständigem Quelltext und Einrückung; fehlende Einträge, doppelte Einträge und geänderte Leerzeichen werden als negative Kontrollen erkannt. Die lokalen Dokumentlinks werden geprüft.

Ausgeführtes Ergebnis: **18 Tests bestanden**. Die echte Vier-Frame-PCAP wird weiterhin mit zwei eindeutigen Requests und je einem zugehörigen ICMP-Netzfehler akzeptiert; ihre vollständige JSON-Auswertung bleibt identisch zu beiden gespeicherten Ergebnisdateien. Die Readiness-Tests führen keinen einzigen Netzwerkbefehl aus. Bestehende Belege werden nicht verändert.

## KI-Kennzeichnung

- **Tool:** Hermes Agent.
- **Anbieter/Modell:** OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
- **Datum:** 2026-10-29.
- **Auftrag:** Readiness-Frist korrigieren, PCAP-Request/Fehler-Zuordnung stärken, mit echter PCAP und synthetischen Negativfällen testen und alle geänderten oder neuen Quellen zeilengenau erklären; keine Netzänderungen, Commits oder Pushes.
- **Umfang:** KI-erstellte Standardbibliothekstests und vollständige Zeilenerklärung. Die Verantwortung für Verständnis und Abgabe bleibt beim Studierenden.
