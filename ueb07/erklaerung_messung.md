# Messung und Fehler-PCAP: zeilenweise Erklärung zu Blatt 07

## Zweck, Einordnung und Leseschlüssel

Diese Ergänzung erklärt ausschließlich die vorhandenen Dateien [verify_namespaces.py](verify_namespaces.py), [ue7.3/auswerten.py](ue7.3/auswerten.py) und [ue7.4/pcap_pruefen.py](ue7.4/pcap_pruefen.py). Die [Angabe](angabe_blatt07.pdf) fordert in Ü 7.2 jeweils einen aktiven Pfad mit dokumentierten Adressen/Routen und ping/tracepath, in Ü 7.3 einen RTT-Vergleich und in Ü 7.4 einen absichtlichen Routingfehler mit nachvollziehbarer Diagnose und Korrektur. Die vorhandene [Topologieerklärung](erklaerung_topologie.md) bleibt unverändert und erklärt andere Programme.

**Wichtig: echte Ersatzverifikation, aber kein Mininet-Nachweis.** Der Runner erzeugt wirkliche Linux-Netzwerk-Namespaces, verbindet sie durch veth und verzögert wirkliche Pakete mit Linux Traffic Control (TC)/Netem. ping, tracepath und dumpcap laufen als echte Prozesse darin. Mininet ist für diesen Nachweis nicht vorhanden und wurde dafür nicht installiert. Dieser Lauf belegt keine Ausführung der Mininet-/OVS-/xterm-Umgebung; eine solche darf man daraus nicht behaupten. Ein Netzwerk-Namespace besitzt eigene Interfaces, Adressen, Routen und Netzwerkparameter, aber hier keine getrennte Dateisystem- oder PID-Welt.

**Zusammenspiel:** lab_config liefert den gemeinsamen Adress-/Linkplan; lab_control führt geprüfte Routenoperationen aus. verify_namespaces baut das isolierte Netz auf, misst und sammelt Rohbelege. auswerten liest ping-Text und kontrolliert Paketzähler/RTT. pcap_pruefen liest unabhängig die tatsächlichen Bytes der Fehleraufnahme. Die Importpfade sind nötig, weil die Dateien in getrennten Übungsordnern liegen.

**Grundbegriffe:** RTT ist die Zeit einer Echoanfrage samt Echoantwort, also Hin- und Rückweg. Next Hop ist der direkt erreichbare nächste Router. Die TTL eines IPv4-Pakets sinkt bei jedem weiterleitenden Router um eins. Ein veth-Paar ist ein virtuelles Ethernet-Kabel. Eine qdisc ist die ausgehende Warteschlangenregel eines Interfaces; Netem kann dort Verzögerung einfügen. ICMP-Typ 8/Code 0 ist Echo Request; Typ 3/Code 0 bedeutet Network Unreachable. PCAP enthält aufgezeichnete Framebytes samt Aufnahmeheadern.

**Python lesen:** Einrückung legt zusammengehörige Blöcke fest; deshalb bleibt sie im angegebenen Quelltext erhalten. def definiert eine Funktion, class einen Objektbauplan, self das aktuelle Objekt. Eine Liste verwendet eckige Klammern, ein Tupel runde, ein Wörterbuch geschweifte mit Schlüssel/Wert. *args verteilt oder sammelt Positionsargumente; ** verteilt Wörterbucheinträge. return beendet die Funktion mit einem Ergebnis, raise meldet einen Fehler. try/finally dient dem Aufräumen auch bei Fehlern; with schließt Ressourcen automatisch. Kommentare beginnen mit #; dreifache Anführungszeichen begrenzen einen mehrzeiligen Beschreibungstext. Ein f vor einer Zeichenkette setzt Ausdrücke in geschweiften Klammern ein, ein r erhält Rückstriche für reguläre Ausdrücke. In den Quellen steht beispielsweise die Zeichenfolge \n für einen Zeilenumbruch im später erzeugten Text, nicht für einen echten Zeilenwechsel in dieser Quellzeile.

**Grenzen der Prüfungen:** assert ist eine interne Testbedingung und wird mit Python-Option -O abgeschaltet. Diese Prüfprogramme deshalb nicht mit -O ausführen. Eine bestandene Einzelprüfung ist nur so stark wie ihre ausdrücklich geprüften Felder. Der PCAP-Parser ist absichtlich auf diesen Ethernet/IPv4/ICMP-Fehlerfall zugeschnitten und validiert nicht sämtliche Protokollfelder oder Prüfsummen. Prozesse, Befehle oder Dateizugriffe können Ausnahmen auslösen; diese sind nicht automatisch ein fachlicher Beweis für einen bestimmten Netzfehler.

## Tatsächlich vorhandene Belege und gefahrloses Nachlesen

Die Datei [nachweise/run01/results.json](nachweise/run01/results.json) dokumentiert erfolgreiche echte Namespace-/TC-Messungen: Client-Mittelwert auf A **14.577 ms**, auf B **124.557 ms**, jeweils **10 gesendet und 10 empfangen**. Die Server-Mittelwerte sind 14.505 ms beziehungsweise 124.811 ms. Die Ausgangsstruktur mit drei Links à 10 ms pro Richtung ist eine getrennte Messung mit Client-Mittelwert 60.441 ms, nicht Pfad A.

Das reine Verzögerungsbudget beträgt auf A 2 × (1 + 5 + 1) = 14 ms, auf B 2 × (1 + 30 + 30 + 1) = 124 ms. Gemessene RTTs enthalten zusätzlich unter anderem Betriebssystem-Scheduling, Paketverarbeitung und Warteschlangen. Deshalb sind sie weder nur die einfache Summe einer Wegrichtung noch zwingend genau die verdoppelte Konfigurationssumme.

Die Fehlerdatei [fault.pcap](nachweise/run01/fault.pcap) enthält **vier Frames**: zwei Echoanfragen Client → Server und zwei ICMP-Netzfehler r3 → Client. [fault-frames.json](nachweise/run01/fault-frames.json) und [fault-dumpcap.txt](nachweise/run01/fault-dumpcap.txt) dokumentieren dieselbe Anzahl; letzteres meldet 4 empfangene und 0 verworfene Pakete. Das innere zitierte Fehlerziel ist jeweils 10.0.2.2. [repaired-client-ping.txt](nachweise/run01/repaired-client-ping.txt) dokumentiert den erfolgreichen Test nach Wiederherstellen der Route. Diese Belege stammen aus run01, nicht aus einem hier neu ausgeführten privilegierten Netzlauf.

Reine Dateiauswertung aus dem Ordner ueb07 benötigt weder sudo noch Mininet und verändert die Belege nicht:

```sh
python3 -B ue7.3/auswerten.py nachweise/run01/A-client-ping.txt
python3 -B ue7.3/auswerten.py nachweise/run01/B-client-ping.txt
python3 -B ue7.4/pcap_pruefen.py nachweise/run01/fault.pcap
```

Den Runner hier **nicht nochmals auf run01 starten**: Sein exklusives mkdir verweigert das absichtlich bereits vorhandene Nachweisverzeichnis. Ein neuer, ausdrücklich beauftragter Netzlauf bräuchte einen eigenen Laufnamen und passende Rechte/Werkzeuge. Vorhandene Belege nicht löschen, ersetzen oder mit einem neuen Lauf mischen.

## Offline-Korrektur und Regressionstests

Die Readiness-Schleife wartet weiterhin auf **File: -**, nicht auf das frühere **Capturing on**. Eine leere Selektorantwort führt zum Weiterwarten bis zur unveränderten absoluten Fünfsekundenfrist; die einzelne Wartezeit wird durch die Restzeit begrenzt. EOF bleibt ein eigener Fehlerfall.

Der Parser prüft jetzt das zitierte Protokoll ICMP, gültige innere Headergrenzen, unfragmentierte Originalpakete und den zitierten Echo-Typ 8/Code 0. ID und Sequenz werden intern gesammelt, Requests müssen eindeutig sein und beide Tupellisten als Multimengen übereinstimmen. Da Adressen und äußerer Fehlertyp bereits fest geprüft werden, ist diese Zuordnung für den vorgesehenen Labordatenstrom eindeutig. Die Rückgabeform bleibt unverändert; die vorhandenen JSON-Belege müssen nicht ersetzt werden. Prüfsummen und vollständige Payload-Gleichheit werden weiterhin nicht zugesagt.

Die [neuen Standardbibliothekstests](ue7.4/test_pcap.py) und ihre [eigene Zeilenerklärung](erklaerung_pcap_tests.md) trennen echte unveränderte PCAP-Belege von synthetischen Fehlervarianten. Aufruf ohne Rechte oder Netzoperationen: `python3 -B ue7.4/test_pcap.py`.

## Zeilenweise Erklärung

Jeder folgende nummerierte Eintrag nennt genau eine nichtleere physische Quellzeile mit ihrer Originalzeilennummer. Der Quelltext zwischen Backticks enthält auch die originale Einrückung; keine Zeilen werden verkürzt oder durch Auslassungspunkte ersetzt. Mehrzeilige Python-Anweisungen erhalten trotzdem für jede physische Zeile eine eigene Erklärung. Leerzeilen werden ausgelassen, daher sind Sprünge in den Quellzeilennummern beabsichtigt. Die Nummerierung der Liste beginnt pro Datei erneut und ist von der Quellzeilennummer zu unterscheiden.

### `verify_namespaces.py`

1. Zeile 1 — `# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.`: Dieser Kommentar dokumentiert Werkzeug, Modell und Erstellungsdatum des vorhandenen Programms. Python führt Kommentare nicht aus; sie machen die KI-Unterstützung nach den Kursregeln nachvollziehbar.

2. Zeile 2 — `# Anfrage: Blatt07 mit echten isolierten Linux-Netzen, A/B-Routen, TC, Ping und Fehler-PCAP prüfen.`: Der Kommentar hält den ursprünglichen Codeauftrag fest: echte Netzwerktests statt erfundener Messdaten. Der zusätzliche aktuelle Korrekturauftrag folgt in der nächsten Kommentarzeile; beide Angaben dienen der nachvollziehbaren KI-Kennzeichnung.

3. Zeile 3 — `# Korrekturauftrag: Readiness-Frist ohne vorzeitigen Idle-Abbruch reparieren; keine Netzänderungen ausführen.`: Dokumentiert den zusätzlichen tatsächlichen Korrekturauftrag: Die Bereitschaftsfrist soll stille Startphasen erlauben. Für diese Korrektur werden ausschließlich Code und gespeicherte Belege geprüft, keine Netzänderungen ausgeführt.

4. Zeile 4 — `"""Zusatznachweis, NICHT Mininet. Python>=3.12, sudo, iproute2, ping, tracepath, dumpcap.`: Hier beginnt die mehrzeilige Modulbeschreibung. Sie grenzt den Zusatztest von Mininet ab und nennt Voraussetzungen: Python ab 3.12 für os.unshare, erhöhte Rechte sowie die externen Netzwerk- und Aufnahmeprogramme.

5. Zeile 5 — `Alle Netzwerkänderungen erst nach Erzeugung eines äußeren privaten Netzwerk-Namespace.`: Die Beschreibung nennt die zentrale Sicherheitsbedingung: Erst ein neues äußeres Netzwerk schaffen, dann darin Interfaces, Routen und Verzögerungen verändern. Das betrifft Netzwerkisolation, nicht eine private Dateisystem- oder Prozesswelt.

6. Zeile 6 — `"""`: Die drei Anführungszeichen beenden den Beschreibungstext. Ohne diesen Abschluss würde Python nachfolgenden Programmtext als Text behandeln beziehungsweise einen Syntaxfehler melden.

7. Zeile 7 — `import contextlib`: Importiert Hilfen für Kontextmanager, die Ressourcen beim Verlassen eines with-Blocks schließen können. contextlib wird in dieser konkreten Datei allerdings nicht verwendet und ist für deren Ablauf nicht notwendig.

8. Zeile 8 — `import importlib.util`: Importiert Werkzeuge zum dynamischen Laden von Python-Modulen. Auch importlib.util bleibt hier unbenutzt: Die späteren normalen import-Anweisungen benötigen dieses importierte Hilfsmodul nicht.

9. Zeile 9 — `import io`: Importiert Werkzeuge für Ein-/Ausgabeobjekte im Speicher. io wird im vorliegenden Programm nicht verwendet; es erzeugt also weder Messdaten noch Dateien und wäre funktional entbehrlich.

10. Zeile 10 — `import json`: json wandelt Python-Datenstrukturen in das maschinenlesbare JSON-Textformat um. Das wird für die gespeicherten Messzusammenfassungen und die Ausgabe auf dem Terminal gebraucht.

11. Zeile 11 — `import os`: os ermöglicht Betriebssystemzugriffe: Umgebungsvariablen, Prozessrechte, Namespace-Verweise und das Erzeugen des äußeren Netzwerk-Namespace. Ohne diesen Import könnten diese Sicherheits- und Verwaltungsoperationen nicht aufgerufen werden.

12. Zeile 12 — `from pathlib import Path`: Path stellt Dateipfade als Objekte bereit. Damit lassen sich Ordner aneinanderhängen, Dateinamen ableiten und Textdateien lesen oder schreiben, ohne Pfadtrenner selbst zusammenzubauen.

13. Zeile 13 — `import re`: re stellt reguläre Ausdrücke bereit, also Suchmuster für Text. Hier werden damit die Antwort-TTLs aus ping und die Paketanzahl aus dem dumpcap-Protokoll herausgelesen.

14. Zeile 14 — `import selectors`: selectors wartet darauf, dass eine Prozessleitung lesbare Daten liefert. Das ist für die echte Bereitschaftsmeldung der Paketaufnahme nötig: Ein gestarteter Prozess allein garantiert noch keine aufnahmebereite Schnittstelle.

15. Zeile 15 — `import subprocess`: subprocess startet externe Programme wie ip, ping und dumpcap. Deren tatsächliche Betriebssystemausgaben sind die Grundlage des Nachweises; Python erfindet keine Antworten für diese Programme.

16. Zeile 16 — `import sys`: sys liefert unter anderem den Modulsuchpfad. Der Runner ergänzt ihn, damit eigene Module aus den Unterordnern ue7.2, ue7.3 und ue7.4 importiert werden können.

17. Zeile 17 — `import time`: time liefert eine monotone Uhr für Fristen und eine kurze Wartefunktion. Monotone Zeit läuft unabhängig von Korrekturen der Kalenderuhr weiter und eignet sich deshalb für Zeitlimits.

18. Zeile 19 — `BASE = Path(__file__).resolve().parent`: Bestimmt den Ordner dieser Python-Datei über deren absoluten, aufgelösten Dateipfad. Dadurch hängen spätere Pfade nicht davon ab, aus welchem Arbeitsordner das Programm gestartet wird.

19. Zeile 20 — `sys.path.insert(0, str(BASE / "ue7.2"))`: Setzt ue7.2 an den Anfang der Modulsuche. Dadurch findet Python lab_config und lab_control dort; an erster Stelle hätten solche lokalen Module auch Vorrang vor gleichnamigen anderen Modulen.

20. Zeile 21 — `from lab_config import LINKS, NODES`: Übernimmt den tatsächlichen Linkplan und die Knotennamen aus lab_config. LINKS enthält Endpunkte, Interfaces, Adressen und Verzögerungen; NODES ordnet client, r1, r2, server und r3.

21. Zeile 22 — `from lab_control import LabControl, checked`: Übernimmt die gemeinsame Steuerklasse und den geprüften Befehlsaufruf. checked erwartet eine pexec-Methode mit Ausgabe, Fehlerausgabe und Exitstatus und bricht bei einem fehlgeschlagenen Befehl ab; es setzt nicht zwingend Mininet voraus.

22. Zeile 23 — `sys.path.insert(0, str(BASE / "ue7.3"))`: Ergänzt den Suchpfad um ue7.3, damit das nachfolgende Modul für die RTT-Auswertung ohne Paketinstallation gefunden wird. str wandelt das Path-Objekt in den dafür erwarteten Pfadtext um.

23. Zeile 24 — `from auswerten import budget, statistics`: Importiert budget für die theoretischen Verzögerungsanteile und statistics für echte ping-Ausgaben. statistics ist hier die eigene Funktion aus auswerten, nicht das gleichnamige Python-Standardmodul.

24. Zeile 25 — `sys.path.insert(0, str(BASE / "ue7.4"))`: Ergänzt ue7.4 für den eigenen Parser. Die Reihenfolge ist wichtig: Erst muss der Ordner auffindbar sein, dann kann Python das darin liegende Modul importieren.

25. Zeile 26 — `from pcap_pruefen import inspect`: Importiert inspect zum unabhängigen Lesen der gespeicherten Fehler-PCAP. Die Funktion heißt so, ist aber nicht das Python-Standardmodul inspect; sie prüft die tatsächlichen Paketbytes.

26. Zeile 29 — `def run(args, timeout=25):`: Definiert eine Hilfsfunktion zum Ausführen eines externen Befehls. args ist eine Argumentliste, und ohne abweichende Angabe gilt ein Zeitlimit von 25 Sekunden, damit ein Befehl nicht endlos blockiert.

27. Zeile 30 — `    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,`: Startet den Befehl ohne zusätzliche Shell, sammelt beide Ausgabekanäle und liefert sie als Text im CompletedProcess zurück. Ein erfolgloser Exitstatus löst hier noch keine Ausnahme aus; der jeweilige Aufrufer muss ihn prüfen.

28. Zeile 31 — `                          env={**os.environ, "LC_ALL": "C"})`: Übernimmt die vorhandene Prozessumgebung und überschreibt nur LC_ALL mit C. So erscheinen Meldungen und Zahlen im erwarteten englischen Format; das ist für die späteren Textmuster entscheidend.

29. Zeile 34 — `class Node:`: Beginnt den Bauplan für ein eigenes Knotenobjekt. Jeder Node erhält einen echten Linux-Netzwerk-Namespace und eine Mininet-ähnliche pexec-Schnittstelle, ist aber kein Mininet-Host.

30. Zeile 35 — `    def __init__(self, name):`: Definiert den Konstruktor, der beim Erzeugen eines Node automatisch läuft. self bezeichnet das gerade entstehende Objekt; name ist sein Laborknotenname, etwa r1.

31. Zeile 36 — `        self.name = name`: Speichert den Namen am Objekt, damit Fehlermeldungen und Steuerbefehle den Knoten eindeutig bezeichnen können. Der Name ändert keinen Linux-Hostnamen und erzeugt allein noch keine Isolation.

32. Zeile 37 — `        original = os.readlink("/proc/self/ns/net")`: Liest die Kennung des aktuellen Netzwerk-Namespace aus dem Linux-Prozessdateisystem. Diese Vergleichskennung wird benötigt, um später festzustellen, dass der Kindprozess tatsächlich in einem anderen Netzwerk arbeitet.

33. Zeile 38 — `        self.process = subprocess.Popen(["unshare", "--net", "sleep", "180"])`: Startet einen Namespace-Halter: unshare erzeugt mit --net ein neues Netzwerk, sleep hält den Prozess bis zu 180 Sekunden am Leben. Sein PID wird später zum Betreten dieses Netzwerks verwendet; zu lange Tests könnten den Halter verlieren.

34. Zeile 39 — `        deadline = time.monotonic() + 3`: Setzt die Bereitschaftsfrist drei Sekunden in die Zukunft. Die Frist begrenzt das Warten auf den neuen Namespace, damit ein fehlgeschlagener Start nicht unbemerkt hängen bleibt.

35. Zeile 40 — `        try:`: Beginnt einen geschützten Initialisierungsblock. Scheitert eine der folgenden Operationen, übernimmt der except-Block die Bereinigung des bereits gestarteten Halteprozesses.

36. Zeile 41 — `            while os.readlink(f"/proc/{self.process.pid}/ns/net") == original:`: Wartet, solange der Kindprozess laut /proc noch denselben Netzwerk-Namespace wie der Aufrufer hat. Erst eine andere Kennung belegt den erfolgten Wechsel; bloßes Popen wäre dafür zu früh.

37. Zeile 42 — `                if self.process.poll() is not None or time.monotonic() >= deadline:`: Prüft während des Wartens zwei Abbruchbedingungen: Der Prozess ist schon beendet oder die Frist ist erreicht. poll liefert None für einen laufenden Prozess, sonst seinen Exitstatus.

38. Zeile 43 — `                    raise RuntimeError("Namespace nicht bereit")`: Meldet einen fehlgeschlagenen Namespace-Start als Laufzeitfehler. Damit wird nicht mit einem vermeintlich isolierten Knoten weitergearbeitet, dessen Isolation gar nicht nachgewiesen wurde.

39. Zeile 44 — `                time.sleep(0.01)`: Pausiert zehn Millisekunden zwischen zwei Prüfungen. Das vermeidet eine CPU-belastende Dauerschleife, ohne eine feste Gesamtschlafzeit als Ersatz für die Bereitschaftsprüfung zu verwenden.

40. Zeile 45 — `            checked(self, "ip", "link", "set", "lo", "up")`: Aktiviert das lokale Loopback-Interface im neuen Knoten. Neue Netzwerk-Namespaces haben lo zunächst nicht zwingend aktiv; checked prüft den wirklichen Erfolg dieses Befehls.

41. Zeile 46 — `        except BaseException:`: Fängt auch weitreichende Ausnahmen wie einen Tastaturabbruch während der Initialisierung ab. Das ist für Aufräumen sinnvoll, soll den Fehler aber nicht als erfolgreichen Start verschleiern.

42. Zeile 47 — `            self.close()`: Beendet beziehungsweise erwartet den Halteprozess auch nach einem Initialisierungsfehler. So bleibt ein teilweise erzeugter Knoten nicht absichtlich im Hintergrund bestehen.

43. Zeile 48 — `            raise`: Reicht die gerade behandelte Ausnahme weiter. Aufräumen bedeutet hier ausdrücklich nicht, den ursprünglichen Fehler zu ignorieren oder Erfolg zu melden.

44. Zeile 50 — `    def prefix(self):`: Definiert die Methode, die den Befehlsvorspann zum Betreten eines Knotennetzwerks liefert. Sie führt selbst noch keinen Netzwerkbefehl aus.

45. Zeile 51 — `        return ["nsenter", "-t", str(self.process.pid), "-n"]`: nsenter sucht über -t die PID des Halters und betritt mit -n dessen Netzwerk-Namespace. Es werden dabei weder ein privates Dateisystem noch andere Namespace-Arten angefordert.

46. Zeile 53 — `    def pexec(self, *args):`: Definiert die Befehlsmethode mit beliebig vielen Positionsargumenten. *args sammelt beispielsweise ip, route und show als einzelne Argumente, statt sie als Shelltext zu interpretieren.

47. Zeile 54 — `        result = run(self.prefix() + list(args))`: Hängt den gewünschten Befehl an den nsenter-Vorspann und führt die gesamte Liste aus. Dadurch laufen auch ganz normale Programme im Netzwerk des ausgewählten Knotens.

48. Zeile 55 — `        return result.stdout, result.stderr, result.returncode`: Liefert Standardausgabe, Fehlerausgabe und echten Exitstatus genau in der Reihenfolge zurück, die checked erwartet. Dieses gemeinsame Protokoll macht die Steuerklasse auch ohne Mininet wiederverwendbar.

49. Zeile 57 — `    def close(self):`: Definiert das Aufräumen eines Knotens. Der Halteprozess ist die eigene langfristige Referenz auf dessen Netzwerk-Namespace und muss nach den Tests beendet werden.

50. Zeile 58 — `        if self.process.poll() is None:`: Prüft, ob der Halteprozess noch läuft. Nur dann ist ein Beendigungssignal nötig; einen bereits beendeten Prozess kann man unmittelbar mit wait einsammeln.

51. Zeile 59 — `            self.process.terminate()`: Fordert das Ende des eigenen Prozesses mit SIGTERM an. Das ist keine pauschale Beendigung fremder Prozesse und verändert keine Hostrouten.

52. Zeile 60 — `        self.process.wait(timeout=5)`: Wartet bis zu fünf Sekunden auf dessen Ende und holt den Exitstatus ab. Eine Überschreitung würde eine Ausnahme auslösen; eine zusätzliche harte Kill-Eskalation implementiert diese Datei nicht.

53. Zeile 63 — `def link(nodes, item, delay):`: Definiert den Aufbau einer Verbindung zwischen zwei Knoten. item ist ein Linkdatensatz aus LINKS; delay bestimmt die ausgehende Verzögerung an beiden Enden dieses Links.

54. Zeile 64 — `    left, right, il, ir, _, _, _ = item`: Zerlegt den Linkdatensatz in Knotennamen und Interface-Namen. Die beiden Adressen und der ursprüngliche Verzögerungswert werden hier mit _ bewusst nicht verwendet; Adressen folgen später, delay kommt als eigener Parameter.

55. Zeile 65 — `    result = run(["ip", "link", "add", il, "type", "veth", "peer", "name", ir])`: Erzeugt ein veth-Paar: zwei virtuelle Ethernet-Enden, bei denen gesendete Frames am anderen Ende ankommen. Sie entstehen im äußeren privaten Netzwerk, nicht direkt im ursprünglichen Hostnetz.

56. Zeile 66 — `    assert result.returncode == 0, result.stderr`: Fordert einen erfolgreichen Exitstatus und zeigt bei einem Fehler dessen Fehlertext. assert ist eine Testprüfung; unter Python mit -O wäre diese Prüfung abgeschaltet.

57. Zeile 67 — `    for name, interface in ((left, il), (right, ir)):`: Durchläuft beide Linkenden als Paare aus Knotenname und dessen Interface. So werden beide Seiten symmetrisch in ihre jeweiligen Knotennetze verschoben und eingerichtet.

58. Zeile 68 — `        result = run(["ip", "link", "set", interface, "netns", str(nodes[name].process.pid)])`: Verschiebt das jeweilige Interface in den Netzwerk-Namespace des zugehörigen Halteprozesses. Die PID identifiziert hier ein Netzwerk, nicht eine IP-Adresse.

59. Zeile 69 — `        assert result.returncode == 0, result.stderr`: Kontrolliert, dass das Verschieben erfolgreich war. Ohne diese Prüfung könnte die folgende Interface-Konfiguration im falschen oder in einem unvollständigen Netz stattfinden.

60. Zeile 70 — `        checked(nodes[name], "ip", "link", "set", interface, "up")`: Schaltet das verschobene Interface im Zielknoten ein. Ein vorhandenes veth-Ende allein reicht nicht für Datenverkehr, solange sein administrativer Zustand noch down ist.

61. Zeile 71 — `        checked(nodes[name], "tc", "qdisc", "replace", "dev", interface, "root", "netem", "delay", delay)`: Ersetzt die ausgehende Warteschlangendisziplin durch Netem mit der angegebenen Verzögerung. Weil beide Linkenden so eingerichtet werden, verzögert jeder Durchlauf pro Richtung einmal; Hin- und Rückweg tragen beide zur RTT bei.

62. Zeile 74 — `def save(output, name, text):`: Definiert eine kleine Schreibfunktion für Nachweisdateien. output ist das Zielverzeichnis, name der relative Dateiname und text der zu speichernde Inhalt.

63. Zeile 75 — `    (output / name).write_text(text)`: Verbindet Ordner und Dateinamen und schreibt den Text. write_text würde eine gleichnamige Datei überschreiben; der Schutz vor alten Nachweisen kommt deshalb vom später exklusiv angelegten Laufverzeichnis.

64. Zeile 78 — `def state(nodes, output, tag):`: Definiert einen Zustandsschnappschuss aller Knoten. tag unterscheidet beispielsweise A, B und original, sodass die Dateien den jeweils gemessenen Zustand dokumentieren.

65. Zeile 79 — `    for name, node in nodes.items():`: Durchläuft die Knoten samt ihren Namen. items liefert aus dem Wörterbuch jeweils Schlüssel und Wert, hier also Laborknotenname und Node-Objekt.

66. Zeile 80 — `        text = ""`: Startet den Protokolltext für diesen Knoten leer. Die folgenden Befehlsüberschriften und echten Ausgaben werden nacheinander angehängt.

67. Zeile 81 — `        for args in (("ip", "-br", "addr"), ("ip", "route"), ("ip", "rule"),`: Beginnt die Liste der Diagnosebefehle: kurze Adressübersicht, Routingtabelle und Routingregeln. Letztere helfen zu erkennen, ob eine abweichende Policy-Routing-Regel die normale Routenentscheidung beeinflusst.

68. Zeile 82 — `                     ("sysctl", "net.ipv4.ip_forward"), ("tc", "-s", "qdisc", "show")):`: Ergänzt den Forwarding-Schalter und die Traffic-Control-Warteschlangen samt Statistik. So wird neben IP-Adressen und Routen auch festgehalten, ob Router weiterleiten und welche Verzögerung wirklich konfiguriert ist.

69. Zeile 83 — `            text += "$ " + " ".join(args) + "\n" + checked(node, *args)`: Hängt den lesbaren Befehl und seine geprüfte Ausgabe an. *args verteilt die Argumente des Tupels auf checked; die Dollarzeichenzeile dient nur als Protokollüberschrift.

70. Zeile 84 — `        target = "10.0.1.2" if name in ("r2", "server") else "10.0.2.2"`: Wählt ein entferntes Ziel für die konkrete Routenauskunft: r2 und server prüfen Richtung Client, die übrigen Knoten Richtung Server. Diese Auswahl ist ein Diagnosebeispiel, keine vollständige Prüfung aller Zieladressen.

71. Zeile 85 — `        text += "$ ip route get " + target + "\n" + checked(node, "ip", "route", "get", target)`: Fragt den Kernel nach der tatsächlichen Route zu diesem Ziel und protokolliert sie. ip route get zeigt eine konkrete Weiterleitungsentscheidung statt nur die Liste möglicher Tabelleneinträge.

72. Zeile 86 — `        save(output, f"{tag}-{name}-state.txt", text)`: Speichert den Zustand mit Pfadkennung und Knotennamen. Das verhindert, dass die Schnappschüsse von A, B und Ausgangstopologie innerhalb desselben Laufs verwechselt werden.

73. Zeile 89 — `def measure(nodes, output, tag, ttl):`: Definiert die Messung in beiden Richtungen. ttl ist die erwartete Restlebensdauer der empfangenen Echoantworten; sie dient zusätzlich zur RTT als Plausibilitätsprüfung der Routeranzahl.

74. Zeile 90 — `    result = {}`: Legt ein leeres Ergebniswörterbuch an. Darin werden anschließend getrennte Statistiken für den Client als Sender und den Server als Sender abgelegt.

75. Zeile 91 — `    for source, target in (("client", "10.0.2.2"), ("server", "10.0.1.2")):`: Prüft Client zu Server und anschließend Server zu Client. Zwei Richtungen sind wichtig, weil eine funktionierende Hinroute keine korrekt konfigurierte Rückroute garantiert.

76. Zeile 92 — `        node = nodes[source]`: Wählt das Node-Objekt des aktuellen Senders aus. Alle folgenden Befehle dieser Runde laufen dadurch im richtigen Knotennetzwerk.

77. Zeile 93 — `        warm = checked(node, "ping", "-n", "-c", "2", "-i", "0.2", "-W", "2", target)`: Sendet zwei Aufwärm-Pings ohne Namensauflösung, im Abstand von 0,2 Sekunden und mit zwei Sekunden Antwortfrist. Dadurch können ARP-Nachbarschaften vor der eigentlichen Messung entstehen; checked verlangt einen erfolgreichen Befehlsstatus, prüft aber hier noch nicht beide Empfangszähler.

78. Zeile 94 — `        save(output, f"{tag}-{source}-warmup.txt", warm)`: Bewahrt die Aufwärmausgabe getrennt auf. Diese Pakete sollen dokumentiert sein, werden aber nicht mit den zehn eigentlichen Messpaketen vermischt.

79. Zeile 95 — `        text = checked(node, "ping", "-n", "-c", "10", "-i", "0.2", "-s", "56", "-W", "2", target)`: Misst zehn Echoanfragen mit 56 Byte ICMP-Nutzdaten, numerischen Adressen, 0,2 Sekunden Abstand und zwei Sekunden Antwortfrist. Die 56 Byte sind nicht die gesamte Ethernet-Paketgröße; IP- und ICMP-Header kommen hinzu.

80. Zeile 96 — `        save(output, f"{tag}-{source}-ping.txt", text)`: Speichert die vollständige unveränderte ping-Ausgabe für eine spätere Kontrolle. Damit bleibt die Zusammenfassung auf echte Rohdaten zurückführbar.

81. Zeile 97 — `        result[source] = statistics(text)`: Lässt die eigene Auswertefunktion Paketanzahl und RTT-Werte prüfen und legt deren Ergebnis unter dem Sendernamen ab. Fehlende Antworten oder unvollständige Statistiken brechen die Messung ab.

82. Zeile 98 — `        observed = re.findall(r"ttl=(\d+)", text)`: Sammelt alle Zahlen direkt nach ttl= in den Antwortzeilen. Der rohe r-String erhält die Rückstriche des Suchmusters; die Klammergruppe liefert nur die Zahl als Text.

83. Zeile 99 — `        assert observed == [str(ttl)] * 10, observed`: Verlangt exakt zehn TTL-Einträge mit dem erwarteten Wert. Bei anfänglich 64 passen 62 zu zwei und 61 zu drei Routern; das ist eine Plausibilitätsprüfung unter dieser Start-TTL-Annahme, kein allgemeingültiger Pfadbeweis.

84. Zeile 100 — `        trace = checked(node, "tracepath", "-n", "-m", "8", target)`: Ermittelt den Weg zusätzlich mit tracepath, ohne DNS und mit höchstens acht Hops. tracepath nutzt andere Prüfpakete als ping und liefert damit ergänzende Hinweise zur Erreichbarkeit.

85. Zeile 101 — `        assert "reached" in trace, trace`: Verlangt die Ziel-erreicht-Meldung in dessen Ausgabe. Ein bloß gestartetes Diagnoseprogramm oder irgendeine Zwischenrouterantwort würde die Ende-zu-Ende-Erreichbarkeit noch nicht bestätigen.

86. Zeile 102 — `        save(output, f"{tag}-{source}-tracepath.txt", trace)`: Speichert auch den Pfadbericht mit Pfadkennung und Sender. So lässt sich die RTT-Messung mit der beobachteten Weglänge gemeinsam nachvollziehen.

87. Zeile 103 — `    return result`: Gibt die geprüften Werte beider Messrichtungen zurück. Der Aufrufer kann sie nun in das Gesamtergebnis übernehmen, statt nur Terminaltext zu besitzen.

88. Zeile 106 — `def capture_fault(nodes, output, control):`: Definiert den absichtlichen Fehlerfall samt Paketaufnahme und anschließender Reparatur. control steuert die bestehenden Routen; der Fehler wird hier nach den A/B-Messungen auf dem zuletzt gewählten Pfad B erzeugt.

89. Zeile 107 — `    control.set_fault(True)`: Entfernt über die Steuerklasse gezielt r3s statische Route zum Servernetz. Die Rückroute zum Client bleibt vorhanden, damit r3 eine aussagekräftige ICMP-Fehlermeldung zurücksenden kann.

90. Zeile 108 — `    route = nodes["r3"].pexec("ip", "route", "get", "10.0.2.2")`: Fragt auf r3 die Route zum Server ab, ohne checked zu verwenden. Ein Misserfolg ist diesmal beabsichtigt und muss als Ergebnis untersucht werden, statt sofort als unerwarteter Befehlsfehler abzubrechen.

91. Zeile 109 — `    assert route[2] != 0 and "unreachable" in route[1].lower(), route`: Verlangt sowohl einen Fehlerstatus als auch unreachable in der Fehlerausgabe. Damit wird der beabsichtigte Routingfehler von einem beliebigen anderen erfolglosen Befehl unterschieden; lower macht die Suche unabhängig von Großschreibung.

92. Zeile 110 — `    save(output, "fault-r3-state.txt", checked(nodes["r3"], "ip", "-br", "addr") +`: Beginnt das Fehlerprotokoll mit den weiterhin vorhandenen Interface-Adressen von r3. Das trennt einen fehlenden Routingtabelleneintrag von einem fehlenden oder falsch adressierten Interface.

93. Zeile 111 — `         checked(nodes["r3"], "ip", "route") + "$ ip route get 10.0.2.2\n" + route[1])`: Ergänzt die verbliebenen Routen und den gescheiterten konkreten Routenentscheid. Zusammen dokumentieren diese Ausgaben die Fehlerursache vor dem Mitschnitt.

94. Zeile 112 — `    target = output / "fault.pcap"`: Legt den Pfad der binären Aufnahmedatei fest. Eine PCAP enthält Paketbytes und Aufnahmemetadaten, nicht nur einen nachträglich formulierten Textbericht.

95. Zeile 113 — `    with target.open("xb") as stream:`: Öffnet die Datei exklusiv zum binären Schreiben. xb verweigert eine schon vorhandene Datei; der with-Block schließt den Dateideskriptor auch bei einer Ausnahme.

96. Zeile 114 — `        process = subprocess.Popen(nodes["client"].prefix() + ["dumpcap", "-i", "client-eth0", "-p", "-F", "pcap",`: Startet dumpcap im Clientnetz auf client-eth0; -p vermeidet Promiscuous-Modus und -F pcap erzwingt das klassische Dateiformat. Die fortgesetzte Argumentliste endet nun in Quellzeile 116; Paketdaten und Diagnosekanal bleiben getrennt.

97. Zeile 115 — `            "-f", "icmp and (host 10.0.1.2) and (host 10.0.2.2 or host 10.0.13.2)",`: Beschränkt den Aufnahmefilter auf ICMP zwischen dem eigenen Client und dem Server oder r3. Die Klammern halten die logische Gruppierung fest; fremder allgemeiner Netzwerkverkehr ist nicht das Aufnahmeziel.

98. Zeile 116 — `            "-a", "duration:4", "-w", "-"], stdout=stream, stderr=subprocess.PIPE)`: Begrenzt die Aufnahme auf vier Sekunden und schreibt die Paketbytes über Standardausgabe in die geöffnete Datei. Diagnosemeldungen gehen getrennt in eine Pipe, damit sie nicht die PCAP beschädigen.

99. Zeile 117 — `        try:`: Beginnt den Bereich, dessen finally-Block einen noch laufenden Aufnahmeprozess auf jeden Fall zu beenden versucht. Das gilt auch bei einem fehlgeschlagenen Test oder einer Ausnahme beim Lesen.

100. Zeile 118 — `            start = b""`: Sammelt Bereitschaftsmeldungen zunächst als leere Bytefolge. Die Pipe arbeitet hier binär; deshalb wird auch nach einer Bytefolge statt nach einem Python-Text gesucht.

101. Zeile 119 — `            with selectors.DefaultSelector() as selector:`: Öffnet einen Selektor mit automatischem Schließen. Er kann auf lesbare Daten warten, ohne mit einem blockierenden read unbeschränkt auf eine Meldung zu hoffen.

102. Zeile 120 — `                selector.register(process.stderr, selectors.EVENT_READ)`: Registriert die Fehlerausgabe des Aufnahmeprozesses für Leseereignisse. dumpcap meldet seinen Zustand dort, während die eigentlichen Paketdaten auf einem anderen Kanal in die Datei gehen.

103. Zeile 121 — `                deadline = time.monotonic() + 5`: Setzt eine maximale Bereitschaftsfrist von fünf Sekunden. Das ist getrennt von der viersekündigen Aufnahmedauer, die dumpcap selbst überwacht.

104. Zeile 122 — `                while b"File: -" not in start:`: Wartet auf die konkrete dumpcap-Meldung für die geöffnete Standardausgabe. Erst danach werden Fehler-Pings gestartet, damit deren erste Pakete nicht vor Aufnahmebeginn verloren gehen.

105. Zeile 123 — `                    remaining = deadline - time.monotonic()`: Berechnet die bis zur ursprünglichen absoluten Frist verbleibende Zeit. Die Frist wird bei einem stillen Selektor nicht neu gestartet; so können wiederholte leere Warteereignisse die gesamte Wartezeit nicht unbegrenzt verlängern.

106. Zeile 124 — `                    if remaining <= 0:`: Prüft allein den Ablauf der Gesamtfrist als zeitliche Abbruchbedingung. Eine ausgabefreie einzelne Sekunde ist kein Fehler mehr; bei null oder negativer Restzeit darf jedoch kein weiterer blockierender Warteaufruf folgen.

107. Zeile 125 — `                        raise RuntimeError("Capture nicht bereit")`: Meldet eine fehlende Bereitschaft als Fehler statt mit einer möglicherweise leeren Aufnahme fortzufahren. Der finally-Block übernimmt anschließend die Prozessbereinigung.

108. Zeile 126 — `                    if not selector.select(min(1, remaining)):`: Wartet höchstens eine Sekunde, aber nie länger als die berechnete Restzeit, auf lesbare Fehlerausgabe. Eine leere Ereignisliste bedeutet nur, dass in diesem Warteabschnitt noch keine Daten verfügbar wurden.

109. Zeile 127 — `                        continue`: Beginnt nach einem stillen Warteabschnitt den nächsten Schleifendurchlauf, statt vorzeitig einen Fehler auszulösen. Dabei wird die Restzeit erneut an derselben festen Deadline gemessen; das verhindert sowohl Frühabbruch als auch Fristverlängerung.

110. Zeile 128 — `                    piece = os.read(process.stderr.fileno(), 4096)`: Liest bis zu 4096 bereitliegende Bytes vom Fehlerausgabekanal. fileno liefert den Betriebssystem-Dateideskriptor, den os.read benötigt.

111. Zeile 129 — `                    if not piece:`: Prüft auf eine leere Leseantwort, also das Ende des Kanals. Ein bereits geschlossener Kanal darf nicht als noch ausstehende Bereitschaftsmeldung behandelt werden.

112. Zeile 130 — `                        raise RuntimeError(start.decode(errors="replace"))`: Gibt in diesem Fehlerfall die bisher gesammelten Meldungen als Ausnahme aus. Ungültige Textbytes werden beim Dekodieren ersetzt, damit wenigstens die Diagnose lesbar bleibt.

113. Zeile 131 — `                    start += piece`: Hängt den gelesenen Teil an die bisherige Bytefolge. Dadurch wird die gesuchte Meldung auch dann erkannt, wenn sie auf mehrere Lesevorgänge verteilt ankommt.

114. Zeile 132 — `            out, err, status = nodes["client"].pexec("ping", "-n", "-c", "2", "-i", "0.3", "-W", "1", "10.0.2.2")`: Sendet nach bestätigtem Aufnahmebeginn zwei Pings zum Server, mit kurzem Abstand und einer Sekunde Antwortfrist. pexec liefert auch den erwarteten Fehlerstatus, statt ihn wie checked sofort abzuweisen.

115. Zeile 133 — `            assert status != 0 and "Destination Net Unreachable" in out, (out, err, status)`: Verlangt einen erfolglosen Ping und ausdrücklich Destination Net Unreachable in dessen Ausgabe. Es geht um einen aktiven ICMP-Netzfehler, nicht nur um einen unspezifischen Timeout ohne Antwort.

116. Zeile 134 — `            save(output, "fault-client-ping.txt", out + err)`: Speichert die sichtbare Fehlermeldung des Clients einschließlich möglicher Fehlerausgabe. Damit lässt sich die Benutzerperspektive später den mitgeschnittenen Paketen gegenüberstellen.

117. Zeile 135 — `            rest = process.communicate(timeout=8)[1]`: Lässt dumpcap regulär enden und liest die restliche Fehlerausgabe ein; [1] wählt stderr aus dem Tupel von communicate. Die achtsekündige Frist verhindert endloses Warten und lässt der Aufnahme Zeit zum Entleeren ihrer Puffer.

118. Zeile 136 — `            assert process.returncode == 0`: Prüft den erfolgreichen Abschluss der Aufnahme selbst. Ein erwarteter Fehler beim Ping rechtfertigt keinen fehlgeschlagenen oder abgebrochenen Mitschnitt.

119. Zeile 137 — `            log = (start + rest).decode(errors="replace")`: Setzt anfängliche und restliche dumpcap-Meldungen zu einem lesbaren Protokoll zusammen. errors=replace vermeidet einen Dekodierabbruch wegen einzelner unlesbarer Bytes.

120. Zeile 138 — `            save(output, "fault-dumpcap.txt", log)`: Speichert das Aufnahmeprotokoll getrennt von der binären PCAP. Es enthält unter anderem die später zur Gegenprüfung verwendete dumpcap-Paketanzahl.

121. Zeile 139 — `        finally:`: Beginnt den Bereinigungsblock, der auch bei Fehlern im geschützten Bereich ausgeführt wird. Die normale Aufnahme wird nicht vorschnell abgebrochen; nur ein noch laufender Prozess wird behandelt.

122. Zeile 140 — `            if process.poll() is None:`: Prüft, ob dumpcap nach dem normalen Ablauf oder einer Ausnahme noch lebt. Bereits abgeschlossene Prozesse brauchen kein Beendigungssignal mehr.

123. Zeile 141 — `                process.terminate()`: Fordert nur im verbliebenen Fehlerfall das Ende des eigenen Aufnahmeprozesses an. Dadurch soll kein verwaister Mitschnittprozess weiterlaufen.

124. Zeile 142 — `                process.wait(timeout=5)`: Wartet bis zu fünf Sekunden auf dessen tatsächliches Ende. Auch hier gibt es keine zusätzliche Kill-Eskalation, falls der Prozess diese Aufforderung ignoriert.

125. Zeile 143 — `    parsed = inspect(target)`: Liest die fertig geschlossene PCAP mit dem eigenen Parser. Dieser kontrolliert reale Dateibytes unabhängig davon, welche Paketzahl dumpcap in seinem Textprotokoll gemeldet hat.

126. Zeile 144 — `    counts = re.findall(r"Packets(?: captured)?:\s*(\d+)", log)`: Sucht alle passenden Paketzahlmeldungen von dumpcap. Die optionale Gruppe berücksichtigt sowohl Packets: als auch Packets captured:; die letzte passende Zahl soll die Endsumme sein.

127. Zeile 145 — `    assert counts and int(counts[-1]) == len(parsed["frames"]), log`: Verlangt mindestens eine Zählermeldung und Gleichheit zwischen letzter Meldung und tatsächlich gelesenen Frames. So fällt eine leere, abgeschnittene oder mit einer anderen Aufnahme verwechselte Datei auf.

128. Zeile 146 — `    save(output, "fault-frames.json", json.dumps(parsed, indent=2) + "\n")`: Speichert die aus den Paketbytes gewonnenen Felder als eingerücktes JSON mit abschließendem Zeilenumbruch. Dieses JSON ist eine Auswertung der Aufnahme, kein Ersatz für die Original-PCAP.

129. Zeile 147 — `    trace = checked(nodes["client"], "tracepath", "-n", "-m", "8", "10.0.2.2")`: Führt tracepath im noch fehlerhaften Zustand aus. checked prüft nur dessen Prozessstatus; das fachliche Fehlermerkmal wird deshalb zusätzlich in der nächsten Zeile untersucht.

130. Zeile 148 — `    assert "!N" in trace, trace`: Verlangt !N als Kennzeichnung des nicht erreichbaren Netzes. Das ergänzt die Ping-Meldung und lokalisiert den Routingfehler entlang des Weges.

131. Zeile 149 — `    save(output, "fault-client-tracepath.txt", trace)`: Bewahrt diesen Fehler-Pfadbericht für die Diagnose auf. Er gehört zum Fehlerzustand vor der Reparatur, nicht zu einem später wieder funktionierenden Netzwerk.

132. Zeile 150 — `    control.set_fault(False)`: Stellt die zuvor entfernte Serverroute auf r3 wieder her. Die Reparatur ist damit das gezielte Rückgängigmachen der dokumentierten Ursache, nicht bloß ein Neustart der ganzen Topologie.

133. Zeile 151 — `    repaired = checked(nodes["client"], "ping", "-n", "-c", "3", "-i", "0.2", "10.0.2.2")`: Prüft nach der Reparatur drei echte Echoanfragen vom Client zum Server. Eine wieder vorhandene Route allein wäre noch kein Nachweis für tatsächlich erfolgreiche Ende-zu-Ende-Kommunikation.

134. Zeile 152 — `    statistics(repaired, 3)`: Wertet diese Ausgabe mit der ausdrücklich abweichenden Sollzahl drei aus. So müssen alle drei Antworten angekommen und vollständige RTT-Werte vorhanden sein, auch wenn die Statistik nicht zusätzlich im Gesamtergebnis gespeichert wird.

135. Zeile 153 — `    save(output, "repaired-client-ping.txt", repaired)`: Speichert die erfolgreichen Reparatur-Pings als Rohbeleg. Das erlaubt den direkten Vergleich von fehlgeschlagener und wieder funktionierender Kommunikation.

136. Zeile 154 — `    save(output, "repaired-r3-route.txt", checked(nodes["r3"], "ip", "route", "get", "10.0.2.2"))`: Speichert zusätzlich die wieder funktionierende konkrete Routenentscheidung von r3 zum Server. Damit sind sowohl die Konfigurationskorrektur als auch ihre Wirkung dokumentiert.

137. Zeile 155 — `    return parsed`: Gibt die bereits geprüfte Paketzusammenfassung an den Szenarioaufrufer zurück. Dieser fügt sie unter fault in die Ergebnisdatei ein.

138. Zeile 158 — `def original(nodes, output):`: Definiert die Prüfung der unveränderten linearen Ausgangsstruktur. Diese eigene Funktion verwendet nur die ersten vier Knoten und die ersten drei Verbindungen des gemeinsamen Plans.

139. Zeile 159 — `    for left, right, il, ir, al, ar, _ in LINKS[:3]:`: Durchläuft die ersten drei Links und übernimmt deren Interface- und Adressangaben. Das sind Client–r1, r1–r2 und r2–Server; die Links zu r3 gehören nicht zur Ausgangsstruktur.

140. Zeile 160 — `        for name, interface, address in ((left, il, al), (right, ir, ar)):`: Bearbeitet für jeden Link beide Enden mit dem jeweils dazugehörigen Knoten, Interface und Präfix. Adressen müssen an beiden Linkenden gesetzt werden, damit die benachbarten Geräte miteinander kommunizieren können.

141. Zeile 161 — `            checked(nodes[name], "ip", "addr", "add", address, "dev", interface)`: Fügt die IPv4-Adresse samt Netzpräfix am richtigen Interface hinzu. Direkt angeschlossene Netzrouten entstehen damit im Kernel; entfernte Netze benötigen zusätzlich die folgenden statischen Routen.

142. Zeile 162 — `    for name in ("r1", "r2"):`: Wählt die beiden Router der Ausgangsstrecke aus. Client und Server sollen Endgeräte bleiben und müssen für diesen Test keine Pakete anderer Geräte weiterleiten.

143. Zeile 163 — `        checked(nodes[name], "sysctl", "-w", "net.ipv4.ip_forward=1")`: Aktiviert IPv4-Weiterleitung in den beiden Router-Namespaces. Ohne diesen Schalter könnten ihre eigenen Adressen erreichbar sein, durchlaufende Client-Server-Pakete würden aber nicht normal geroutet.

144. Zeile 164 — `    for name, target, gateway, interface in (("client", "default", "10.0.1.1", "client-eth0"),`: Beginnt die vollständige Liste zusätzlicher Routen mit der Client-Standardroute zu r1. default deckt unbekannte entfernte Ziele ab, sodass der Client nicht für jedes einzelne Gerät eine eigene Route braucht.

145. Zeile 165 — `            ("server", "default", "10.0.2.1", "server-eth0"),`: Ergänzt die Standardroute des Servers zu r2. Auch Echoantworten benötigen einen Weg zum entfernten Clientnetz; funktionierendes Routing muss beide Richtungen berücksichtigen.

146. Zeile 166 — `            ("r1", "10.0.2.0/24", "10.0.12.2", "r1-eth1"),`: Ergänzt auf r1 die Route zum Servernetz über den benachbarten r2 und das r1-seitige Interface. Das Ziel ist ein Netzpräfix, der Next Hop dagegen eine direkt erreichbare Routeradresse.

147. Zeile 167 — `            ("r2", "10.0.1.0/24", "10.0.12.1", "r2-eth0")):`: Ergänzt die dazu passende Rückroute auf r2 zum Clientnetz über r1. Die Zeile schließt die Routendatenliste und öffnet mit dem Doppelpunkt den Schleifenrumpf.

148. Zeile 168 — `        checked(nodes[name], "ip", "route", "replace", target, "via", gateway, "dev", interface)`: Installiert jeden aufgelisteten Eintrag mit ip route replace. replace legt eine fehlende Route an oder ersetzt eine passende vorhandene Route; via und dev legen nächsten Router und Ausgangsinterface fest.

149. Zeile 169 — `    state(nodes, output, "original")`: Dokumentiert den eingerichteten Zustand vor dem Messen. Dadurch kann man die nachfolgenden Ausgangswerte auf Adressen, Routen und TC-Konfiguration zurückführen.

150. Zeile 170 — `    return measure(nodes, output, "original", 62)`: Misst die Ausgangsstruktur mit erwarteter Antwort-TTL 62 und gibt das Ergebnis zurück. Die Verzögerung wurde für deren drei Links separat auf 10 ms je Richtung gesetzt, also nicht auf das Budget von Pfad A.

151. Zeile 173 — `def scenario(output, extended):`: Definiert ein gesamtes isoliertes Testszenario. extended entscheidet zwischen Ausgangsstruktur und erweiterter A/B-Struktur; output bezeichnet deren gemeinsames neues Nachweisverzeichnis.

152. Zeile 174 — `    nodes = {}`: Startet mit einem leeren Knotenwörterbuch. Bereits erfolgreich erzeugte Knoten werden dort gesammelt, damit sie auch nach einem späteren Teilfehler gezielt aufgeräumt werden können.

153. Zeile 175 — `    try:`: Beginnt den durch finally abgesicherten Szenariobereich. Ein return oder eine Testausnahme überspringt die abschließende Knotenbereinigung nicht.

154. Zeile 176 — `        for name in NODES if extended else NODES[:4]:`: Wählt entweder alle Namen oder nur die ersten vier aus. Der bedingte Ausdruck steht hinter in und entscheidet über die durchlaufene Knotenmenge, nicht über einzelne Schleifendurchläufe.

155. Zeile 177 — `            nodes[name] = Node(name)`: Erzeugt für jeden Namen einen echten Node und speichert ihn. Ein fehlgeschlagener Konstruktor räumt seinen eigenen Halter auf; frühere erfolgreich angelegte Knoten bleiben für den finally-Block verzeichnet.

156. Zeile 178 — `        for item in LINKS if extended else LINKS[:3]:`: Wählt entsprechend alle Verbindungen oder nur die ersten drei. Damit werden in der Ausgangsstruktur keine Interfaces für den dort nicht vorhandenen r3 erzeugt.

157. Zeile 179 — `            link(nodes, item, item[-1] if extended else "10ms")`: Erzeugt jeden veth-Link samt TC: erweitert gilt die Verzögerung aus dem letzten Datenfeld, ursprünglich pauschal 10 ms. Ein geänderter Linkplan würde somit die erweiterte Prüfung, aber nicht diesen Ausgangswert automatisch ändern.

158. Zeile 180 — `        if not extended:`: Prüft, ob gerade nur die Ausgangsstruktur verlangt wurde. In diesem Fall folgen keine A/B-Umschaltung und keine absichtliche Fehleraufnahme.

159. Zeile 181 — `            return {"original": original(nodes, output)}`: Richtet die Ausgangsrouten ein und gibt deren Messung unter original zurück. Trotz dieses frühen return läuft anschließend der finally-Block und schließt die Knoten.

160. Zeile 182 — `        control = LabControl(nodes)`: Übergibt das Wörterbuch echter Namespace-Knoten an die wiederverwendbare Steuerklasse. Deren benötigte pexec-Schnittstelle ist vorhanden; ein Mininet-Netzobjekt wird hier nicht erzeugt.

161. Zeile 183 — `        control.configure("A")`: Konfiguriert die erweiterte Struktur mit allen Adressen, Router-Weiterleitung und genau den Routen von A. Die physischen Alternativlinks existieren zwar, aber ihre bloße Existenz erzeugt noch keinen ECMP-Parallelpfad.

162. Zeile 184 — `        result = {"provenance": "Linux-Network-Namespaces + veth + TC/Netem; NICHT Mininet/OVS", "budget_ms": budget()}`: Startet das Ergebnis mit eindeutiger Herkunftsangabe und den berechneten Verzögerungsbudgets. So bleibt maschinenlesbar festgehalten, dass echte Namespace-/TC-Tests und keine Mininet-/OVS-Ausführung vorliegen.

163. Zeile 185 — `        for path, ttl in (("A", 62), ("B", 61)):`: Plant zuerst A mit zwei Routern und dann B mit drei Routern. Die zugehörigen TTL-Sollwerte setzen die hier verwendete anfängliche Echoantwort-TTL 64 voraus.

164. Zeile 186 — `            control.select_path(path)`: Schaltet die statischen Hin- und Rückrouten auf den gewünschten Weg. LabControl führt die Routeränderungen nacheinander mit Rücksetzversuch bei Fehler aus; es gibt keine gemeinsame atomare Kernel-Transaktion über beide Router.

165. Zeile 187 — `            state(nodes, output, path)`: Speichert den Zustand nach der jeweiligen Umschaltung. Erst danach wird gemessen, damit die Belege den tatsächlich vorgesehenen Pfad dokumentieren.

166. Zeile 188 — `            result[path] = measure(nodes, output, path, ttl)`: Misst beide Kommunikationsrichtungen und speichert die geprüften Werte unter A oder B. Dieselbe Messmethode macht den Vergleich aussagekräftiger als unterschiedlich konfigurierte Einzeltests.

167. Zeile 189 — `        assert result["B"]["client"]["avg_ms"] > result["A"]["client"]["avg_ms"] + 80`: Verlangt für den Client mindestens mehr als 80 ms zusätzlichen Mittelwert auf B. Das ist ein großzügiger Plausibilitätstest gegenüber dem 110-ms-Budgetunterschied, keine Forderung nach exakt idealen RTTs.

168. Zeile 190 — `        result["fault"] = capture_fault(nodes, output, control)`: Erzeugt nach B den gezielten r3-Fehler, nimmt ihn auf und repariert ihn. Das Ergebnis enthält die aus der echten PCAP gelesenen Frames und Zähler.

169. Zeile 191 — `        return result`: Gibt die vollständige erweiterte Ergebnisstruktur zurück. Vor der tatsächlichen Rückkehr wird trotzdem der unmittelbar folgende finally-Block ausgeführt.

170. Zeile 192 — `    finally:`: Beginnt das garantierte Aufräumen bei Erfolg, return und Ausnahme. Es verhindert, dass ein normaler Testabbruch einfach alle bereits gespeicherten Knoten überspringt.

171. Zeile 193 — `        for node in reversed(list(nodes.values())):`: Durchläuft die erstellten Knoten in umgekehrter Reihenfolge ihrer Einfügung. list materialisiert die Werte, reversed dreht ihre Reihenfolge für den Abbau um.

172. Zeile 194 — `            node.close()`: Beendet und erwartet jeden Halteprozess. Wenn keine weiteren Referenzen bestehen, verschwinden dessen privates Netz und zugehörige virtuelle Interfaces; ein Fehler in close könnte allerdings den weiteren Schleifenabbau unterbrechen.

173. Zeile 197 — `def main():`: Definiert den Programmeinstieg, der Rechteprüfung, äußere Isolation und beide Testszenarien koordiniert. Er wird beim bloßen Import noch nicht ausgeführt.

174. Zeile 198 — `    if os.geteuid() != 0:`: Prüft die effektive Benutzerkennung auf root. Namespace-, veth-, Routen- und TC-Operationen dieses Runners benötigen hier entsprechende Rechte; die reine Dateiauswertung der anderen beiden Programme nicht.

175. Zeile 199 — `        raise SystemExit("sudo /usr/bin/python3 -B verify_namespaces.py erforderlich")`: Beendet den Start mit einer konkreten Aufrufhilfe bei fehlenden Rechten. /usr/bin/python3 muss die geforderte Funktion unterstützen; -B verhindert neu geschriebene Python-Bytecode-Dateien, ist aber kein Sicherheitsersatz für Isolation.

176. Zeile 200 — `    os.unshare(os.CLONE_NEWNET)`: Erzeugt vor sämtlichen Netzwerkänderungen einen äußeren privaten Netzwerk-Namespace für den Runner. Fehlt die Funktion oder Berechtigung, bricht der Ablauf hier ab; es gibt keinen stillen Rückfall auf Änderungen im ursprünglichen Hostnetz.

177. Zeile 201 — `    output = BASE / "nachweise/run01"`: Legt den festen Laufordner unterhalb des Programmordners fest. Dieses run01 ist bereits mit echten Belegen gefüllt; ein neuer Aufruf ist deshalb absichtlich kein Weg, diese Belege zu überschreiben.

178. Zeile 202 — `    output.mkdir(parents=True, exist_ok=False)`: Legt den Ordner einschließlich fehlender Eltern an und verweigert einen vorhandenen Zielordner. Für einen ausdrücklich gewünschten neuen Messlauf müsste man einen neuen Laufnamen verwenden, statt run01 zu löschen oder damit Messungen zu vermischen.

179. Zeile 203 — `    result = {**scenario(output, False), **scenario(output, True)}`: Führt nacheinander die Ausgangs- und die erweiterte Prüfung aus und führt deren Wörterbücher zusammen. ** entpackt die Einträge; erst vollständig zurückgegebene Szenarien gelangen in das Gesamtergebnis.

180. Zeile 204 — `    result["cleanup"] = "Alle eigenen Namespace-Halter beendet; private veth und qdisc verschwinden mit ihren Namespaces."`: Ergänzt die Aufräumaussage nach der Rückkehr beider Szenarien. Sie ist ein Programmbericht nach ausgeführten close-Aufrufen, keine zusätzliche unabhängige Messung des gesamten Systems.

181. Zeile 205 — `    save(output, "results.json", json.dumps(result, indent=2, ensure_ascii=False) + "\n")`: Schreibt das vollständige Ergebnis als gut lesbares JSON mit unveränderten Umlauten. Der abschließende Zeilenumbruch erleichtert die Betrachtung als Textdatei; bei früherem Testabbruch wird diese Erfolgsdatei nicht erreicht.

182. Zeile 206 — `    print(json.dumps(result, indent=2, ensure_ascii=False))`: Gibt dieselben Daten auf dem Terminal aus. Die gespeicherte results.json bleibt der dauerhafte Nachweis, auch wenn die Terminalausgabe später nicht mehr sichtbar ist.

183. Zeile 209 — `if __name__ == "__main__":`: Prüft, ob die Datei direkt als Programm gestartet wurde. Beim Import zum Wiederverwenden von Funktionen ist __name__ dagegen der Modulname, sodass keine privilegierte Netzprüfung automatisch losläuft.

184. Zeile 210 — `    main()`: Startet dann main und damit den tatsächlichen Prüfablauf. Diese Zeile allein benötigt keine Argumente, weil Laufordner und Szenarien im Programm festgelegt sind.

### `ue7.3/auswerten.py`

1. Zeile 1 — `# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.`: Dokumentiert als Kommentar Werkzeug, Modell und Datum der ursprünglichen Erstellung. Die Angabe ist Teil der KI-Transparenz, beeinflusst aber weder das Suchmuster noch die Messwerte.

2. Zeile 2 — `# Anfrage: Reale Ping-Statistiken von Blatt07 auswerten und konfigurierte RTT-Anteile prüfen.`: Hält den ursprünglichen Auftrag fest: reale Ping-Ergebnisse auswerten und mit konfigurierten Verzögerungsanteilen vergleichen. Das Programm selbst startet keinen Ping und erzeugt keine eigenen Messpakete.

3. Zeile 3 — `"""Keine simulierten Messwerte: Eingabe ist die unveränderte Ausgabe von iputils ping."""`: Die Modulbeschreibung grenzt Eingabedaten von simulierten Ergebnissen ab. Die Funktion verarbeitet ping-Text; dass dieser wirklich aus einer Messung stammt, muss durch aufbewahrte Rohdateien und deren Herkunft belegt werden.

4. Zeile 4 — `import json`: Importiert JSON-Unterstützung für die strukturierte Terminalausgabe. So können Budget und ausgelesene Messwerte gemeinsam ausgegeben und mit anderen Werkzeugen weiterverarbeitet werden.

5. Zeile 5 — `from pathlib import Path`: Importiert Path für das Lesen der per Kommandozeile angegebenen Textdatei. Der Pfad wird nicht fest eingebaut, damit unterschiedliche vorhandene Ping-Protokolle ausgewertet werden können.

6. Zeile 6 — `import re`: Importiert reguläre Ausdrücke zum Erkennen der Zähler- und RTT-Zeilen. Diese Muster erwarten das englische iputils-ping-Format mit Dezimalpunkt; der Runner stellt dafür LC_ALL=C ein.

7. Zeile 7 — `import sys`: Importiert sys für die Kommandozeilenargumente. sys.argv[0] ist das Programm selbst, sys.argv[1] später die gewünschte Eingabedatei.

8. Zeile 10 — `def statistics(text, expected=10):`: Definiert die Auswertung eines vollständigen Ping-Texts mit standardmäßig zehn erwarteten Paketen. Ein anderer Messumfang muss beim Funktionsaufruf über expected ausdrücklich passend angegeben werden.

9. Zeile 11 — `    packets = re.search(r"(\d+) packets transmitted, (\d+) received", text)`: Sucht zwei Gruppen ganzer Zahlen vor den englischen Angaben für gesendete und empfangene Pakete. Die tatsächlichen Zähler sind zuverlässiger als eine naive Suche nach 0% packet loss, die auch in 100% packet loss vorkommt.

10. Zeile 12 — `    times = re.search(r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", text)`: Erkennt die vier zusammengefassten RTT-Zahlen: Minimum, Mittelwert, Maximum und Streuung. Die Alternativen berücksichtigen rtt beziehungsweise round-trip und mdev beziehungsweise stddev; die Werte werden nicht aus einzelnen Antworten selbst neu berechnet.

11. Zeile 13 — `    if not packets or not times:`: Prüft, ob beide erforderlichen Suchergebnisse vorhanden sind. Ein re.search liefert None bei fehlendem Treffer; ein teilweise vorhandenes Protokoll reicht deshalb nicht als gültige Messung.

12. Zeile 14 — `        raise ValueError("Vollständige Paket- und RTT-Statistik fehlt")`: Bricht bei unvollständiger Eingabe mit einer verständlichen Ausnahme ab. So werden fehlende RTT-Werte nicht still durch Null oder erfundene Zahlen ersetzt.

13. Zeile 15 — `    sent, received = map(int, packets.groups())`: Wandelt die beiden gefundenen Zählertexte in ganze Zahlen um. map wendet int auf jede Treffergruppe an, die Mehrfachzuweisung verteilt sie auf sent und received.

14. Zeile 16 — `    if sent != expected or received != expected:`: Verlangt sowohl beim Senden als auch beim Empfangen genau die erwartete Anzahl. Damit fallen Paketverlust, unpassende Messlänge und unvollständige Versuchsreihen gleichermaßen auf.

15. Zeile 17 — `        raise ValueError(f"Paketverlust oder falsche Anzahl: {sent}/{received}, erwartet {expected}")`: Meldet Ist- und Sollzahlen im Fehlertext. Die f-Zeichenkette setzt die Zahlen ein, damit man bei einer abgebrochenen Auswertung die Ursache direkt erkennen kann.

16. Zeile 18 — `    result = dict(zip(("min_ms", "avg_ms", "max_ms", "mdev_ms"), map(float, times.groups())))`: Wandelt die vier RTT-Texte in Gleitkommazahlen um und ordnet sie festen Feldnamen zu. zip paart Schlüssel und Wert; mdev_ms übernimmt auch bei einem stddev-Eingabeformat dessen gemeldete vierte Zahl.

17. Zeile 19 — `    if not 0 <= result["min_ms"] <= result["avg_ms"] <= result["max_ms"]:`: Prüft mit einem verketteten Vergleich, dass die Zeitwerte nicht negativ und Minimum, Mittelwert und Maximum sinnvoll geordnet sind. Die vierte Streuungszahl wird hier nicht zusätzlich fachlich validiert.

18. Zeile 20 — `        raise ValueError("Ungültige Reihenfolge der RTT-Statistik")`: Bricht bei widersprüchlichen Zeitwerten ab. Das beweist keine völlige Unverfälschtheit der Eingabe, verhindert aber die Übernahme einer offensichtlich unmöglichen RTT-Zusammenfassung.

19. Zeile 21 — `    return {"sent": sent, "received": received, **result}`: Gibt ein Wörterbuch mit beiden Paketzählern und den vier Zeitwerten zurück. **result kopiert dessen Einträge hinein; alle Zeitfeldnamen tragen zur Vermeidung von Einheitenverwechslungen den Zusatz _ms.

20. Zeile 24 — `def budget():`: Definiert eine eigene Berechnung des geplanten Netem-Anteils. Das ist ein theoretisches Budget aus dem vorliegenden Linkplan, kein gemessener Ping-Mittelwert und kein automatisch eingelesener TC-Zustand.

21. Zeile 25 — `    values = {"A": 2 * (1 + 5 + 1), "B": 2 * (1 + 30 + 30 + 1)}`: Summiert auf A die Richtungswerte 1, 5 und 1 ms und auf B 1, 30, 30 und 1 ms und verdoppelt für Hin- und Rückweg. Es werden also auch die Endgeräte-Links berücksichtigt, nicht nur die Verbindung zwischen Routern.

22. Zeile 26 — `    assert values == {"A": 14, "B": 124}`: Verlangt die dazu passenden Summen 14 und 124 ms als Konsistenzprüfung. Bei bewusst geänderten Linkverzögerungen müssten sowohl die Rechnung als auch diese Sollwerte angepasst werden.

23. Zeile 27 — `    assert values["B"] - values["A"] == 110`: Kontrolliert zusätzlich den Budgetunterschied von 110 ms. Die Prüfung bezieht sich auf konfigurierte Verzögerung, nicht auf eine Behauptung, jeder echte Ping müsse exakt um diesen Betrag abweichen.

24. Zeile 28 — `    return values`: Gibt die geplanten Werte unter den Pfadnamen zurück. Weitere Laufzeitanteile durch Verarbeitung, Scheduling und Warteschlangen sind darin nicht als Messwerte enthalten.

25. Zeile 31 — `if __name__ == "__main__":`: Beschränkt den Kommandozeileneinstieg auf direkten Programmstart. Beim Import durch verify_namespaces bleiben statistics und budget nutzbar, ohne eine Eingabedatei aus sys.argv lesen zu wollen.

26. Zeile 32 — `    print(json.dumps({"budget_ms": budget(), "ping": statistics(Path(sys.argv[1]).read_text())}, indent=2))`: Liest die erste Argumentdatei, wertet sie mit der Standardsollzahl zehn aus und druckt Budget plus Messwerte als JSON. Ohne Argument gibt es einen IndexError; fehlende Dateien und ungültige Protokolle werden nicht durch eigene Hilfeausgaben abgefangen.

### `ue7.4/pcap_pruefen.py`

1. Zeile 1 — `# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.`: Kennzeichnet die ursprüngliche KI-Erstellung mit Werkzeug, Modell und Datum. Der Kommentar ist wichtig für Transparenz, gehört aber nicht zu den Paketbytes und beeinflusst das Prüfergebnis nicht.

2. Zeile 2 — `# Anfrage: Echte isolierte Fehler-PCAP unabhängig lesen, ICMP-Netzfehler und eingebettete Ziele prüfen.`: Nennt den ursprünglichen Parserauftrag: echte Fehler-PCAP lesen und ICMP-Netzfehler samt eingebettetem Ziel überprüfen. Die konkreten Labordaten machen diesen Parser gezielt, nicht zu einem beliebigen universellen Wireshark-Ersatz.

3. Zeile 3 — `# Korrekturauftrag: Requests und Netzfehler über Echo-ID/Sequenz eindeutig zuordnen; offline negativ testen.`: Nennt den zusätzlichen Korrekturauftrag: Echoanfragen und die zitierten Auslöser der Netzfehler müssen eindeutig anhand von ID und Sequenz zusammenpassen. Die Prüfung erfolgt offline mit echten Belegen und ausdrücklich synthetisch veränderten Bytekopien.

4. Zeile 4 — `"""Klassische PCAPs mit Ethernet; beide Bytefolgen und Zeitstempelauflösungen."""`: Beschreibt den unterstützten Eingabebereich: klassisches PCAP mit Ethernet, in beiden Byte-Reihenfolgen und beiden üblichen Zeitstempelauflösungen. PCAPNG, Linux-Cooked-Capture und VLAN-Auswertung sind damit nicht zugesagt.

5. Zeile 5 — `import json`: Importiert JSON zur Ausgabe des Prüfergebnisses. Es werden dabei nur ausgewählte Paketfelder in Text umgewandelt; die binäre Originalaufnahme bleibt die eigentliche Datenquelle.

6. Zeile 6 — `from pathlib import Path`: Importiert Path, damit ein übergebener Dateipfad unabhängig davon als Pfadobjekt behandelt und binär gelesen werden kann. Die Funktion akzeptiert damit auch bereits vorhandene Path-Objekte.

7. Zeile 7 — `import socket`: Importiert socket für die Umwandlung von vier IPv4-Adressbytes in die lesbare Punktnotation. Dafür ist kein eigener Netzwerkzugriff und keine DNS-Abfrage nötig.

8. Zeile 8 — `import struct`: Importiert struct zum Auslesen fest definierter Zahlenfelder aus Bytefolgen. Entscheidend sind deren Feldbreite, Position und Byte-Reihenfolge; bloßes Lesen der Datei als Text wäre hier falsch.

9. Zeile 9 — `import sys`: Importiert sys für das erste Kommandozeilenargument. Dieses liefert beim direkten Start den Namen der zu prüfenden PCAP-Datei.

10. Zeile 12 — `def inspect(path):`: Definiert die Prüffunktion für einen vorhandenen Mitschnitt. Sie schreibt nichts am Netzwerk um und benötigt für eine lesbare Datei keine Rootrechte.

11. Zeile 13 — `    raw = Path(path).read_bytes()`: Liest die ganze Datei unverändert als Bytes in den Speicher. Der kleine Fehler-Mitschnitt ist dafür geeignet; bei sehr großen Aufnahmen wäre ein schrittweises Lesen speichersparender.

12. Zeile 14 — `    formats = {b"\xd4\xc3\xb2\xa1": "<", b"\xa1\xb2\xc3\xd4": ">", b"\x4d\x3c\xb2\xa1": "<", b"\xa1\xb2\x3c\x4d": ">"}`: Ordnet die vier klassischen PCAP-Magic-Bytefolgen der jeweiligen Zahlenreihenfolge zu: < steht für Little Endian, > für Big Endian. Mikro- und Nanosekundenvarianten werden erkannt, obwohl die Zeitstempel später nicht ausgewertet werden.

13. Zeile 15 — `    if len(raw) < 24 or raw[:4] not in formats:`: Prüft die Mindestlänge des globalen Headers von 24 Byte und eine bekannte Anfangskennung. Die Kurzschlussauswertung von or verhindert hier unnötige weitere Auswertung bei einer schon zu kurzen Datei.

14. Zeile 16 — `        raise ValueError("Kein vollständiger klassischer PCAP-Header")`: Lehnt eine unvollständige oder anders formatierte Datei mit ValueError ab. Ein erfolgreicher Dateizugriff allein beweist schließlich noch kein passendes PCAP-Format.

15. Zeile 17 — `    endian = formats[raw[:4]]`: Wählt aus der erkannten Kennung die Byte-Reihenfolge für die PCAP-Zahlen aus. Das beeinflusst die Aufnahmeheader, nicht die Internet-Protokollfelder, die später eigene Netzwerk-Byte-Reihenfolge verwenden.

16. Zeile 18 — `    assert struct.unpack_from(endian + "I", raw, 20)[0] == 1, "Ethernet erwartet"`: Liest am Byteoffset 20 ein vorzeichenloses 32-Bit-Feld und verlangt Linktyp 1 für Ethernet. unpack_from liefert ein Tupel, daher [0]; ohne diese Prüfung könnte der Parser einen anders aufgebauten Linkheader falsch deuten.

17. Zeile 19 — `    frames, offset = [], 24`: Legt die Ergebnisliste leer an und setzt die Leseposition hinter den 24-Byte-Dateiheader. offset bezeichnet stets die nächste noch zu lesende Position in raw.

18. Zeile 20 — `    request_keys, error_keys = [], []`: Legt zwei interne Listen für die Tupel aus Echo-Identifier und Sequenznummer an. Sie werden nicht in frames oder das Rückgabewörterbuch aufgenommen, damit vorhandene Ergebnis-JSONs ohne Änderungen reproduzierbar bleiben.

19. Zeile 21 — `    while offset < len(raw):`: Durchläuft die Paketdatensätze bis zum tatsächlichen Dateiende. Jeder Datensatz hat einen eigenen Aufnahmeheader und danach die gespeicherten Framebytes.

20. Zeile 22 — `        assert offset + 16 <= len(raw), "Abgeschnittener Recordheader"`: Verlangt noch mindestens 16 Byte für den nächsten Datensatzheader. So wird ein abgebrochener Header nicht versehentlich als vollständiger Paketdatensatz verarbeitet.

21. Zeile 23 — `        _, _, captured, original = struct.unpack_from(endian + "IIII", raw, offset)`: Liest vier 32-Bit-Zahlen: zwei Zeitstempelteile, gespeicherte Länge und ursprüngliche Framegröße. Die Zeitteile werden mit _ verworfen; captured und original steuern die Vollständigkeitsprüfung.

22. Zeile 24 — `        offset += 16`: Überspringt den gerade gelesenen 16-Byte-Aufnahmeheader. Danach zeigt offset auf den Anfang des gespeicherten Ethernet-Frames.

23. Zeile 25 — `        packet = raw[offset:offset + captured]`: Schneidet genau die angekündigten gespeicherten Framebytes aus. Ein Python-Slice liefert bei zu wenig Daten nur einen kürzeren Ausschnitt statt selbst eine passende Vollständigkeitsausnahme auszulösen.

24. Zeile 26 — `        assert len(packet) == captured == original, "Abgeschnittenes Paket"`: Verlangt deshalb ausdrücklich die angekündigte Bytezahl und zusätzlich Gleichheit mit der ursprünglichen Framegröße. Das lehnt sowohl eine abgeschnittene Datei als auch absichtlich gekürzte Snaplen-Aufnahmen für diesen Nachweis ab.

25. Zeile 27 — `        offset += captured`: Rückt die Dateiposition um die gespeicherten Paketbytes weiter. Der nächste Schleifendurchlauf beginnt damit am nächsten Aufnahmeheader, nicht irgendwo innerhalb desselben Frames.

26. Zeile 28 — `        assert len(packet) >= 34 and packet[12:14] == b"\x08\x00", "IPv4 erwartet"`: Verlangt genug Bytes für Ethernet plus minimalen IPv4-Header und EtherType 0x0800. Die Position 12 bis 13 passt zu ungetaggtem Ethernet; VLAN-getaggte oder andere Protokollframes werden hier nicht unterstützt.

27. Zeile 29 — `        ip = packet[14:]`: Entfernt den 14-Byte-Ethernet-Header aus der Sicht auf das Paket. ip beginnt nun direkt mit dem IPv4-Header, kann am Ende aber noch Ethernet-Padding enthalten.

28. Zeile 30 — `        ihl = (ip[0] & 15) * 4`: Liest aus den unteren vier Bits des ersten IPv4-Bytes die Headerlänge und multipliziert mit vier. Das IHL-Feld zählt 32-Bit-Wörter; so würden auch vorhandene IPv4-Optionen beim Beginn des ICMP-Teils berücksichtigt.

29. Zeile 31 — `        total = struct.unpack_from("!H", ip, 2)[0]`: Liest die gesamte IPv4-Paketlänge als 16-Bit-Zahl ab Offset zwei. ! erzwingt Netzwerk-Byte-Reihenfolge, also Big Endian, unabhängig von der PCAP-Dateireihenfolge.

30. Zeile 32 — `        assert ip[0] >> 4 == 4 and 20 <= ihl <= total <= len(ip)`: Verlangt IPv4-Version 4 und sinnvolle Grenzen für Header- und Paketlänge. Insbesondere darf die angegebene IP-Länge nicht über die tatsächlich gespeicherten Bytes hinausreichen.

31. Zeile 33 — `        assert ip[9] == 1 and struct.unpack_from("!H", ip, 6)[0] & 0x3fff == 0`: Verlangt Protokollnummer 1 für ICMP und schließt fragmentierte IPv4-Pakete aus. Die Maske 0x3fff prüft More-Fragments-Bit und Fragmentoffset; Don't Fragment allein bleibt erlaubt, eine Fragmentzusammensetzung implementiert der Parser nicht.

32. Zeile 34 — `        src, dst = socket.inet_ntoa(ip[12:16]), socket.inet_ntoa(ip[16:20])`: Wandelt die IPv4-Quell- und Zieladressfelder aus ihren vier Bytes in Text um. Die festen Offsets dieser Felder gelten auch dann, wenn hinter dem Grundheader noch IP-Optionen stehen.

33. Zeile 35 — `        icmp = ip[ihl:total]`: Begrenzt ICMP auf den Bereich hinter dem IP-Header bis zur IP-Gesamtlänge. Das ist wichtig, damit eventuell aufgefüllte Ethernet-Bytes am Frameende nicht als ICMP-Nutzdaten fehlinterpretiert werden.

34. Zeile 36 — `        assert len(icmp) >= 8`: Verlangt den mindestens acht Byte langen ICMP-Grundbereich. Erst danach sind weitere ICMP-spezifische Felder und ein gegebenenfalls eingebettetes Originalpaket sinnvoll zu untersuchen.

35. Zeile 37 — `        item = {"frame": len(frames) + 1, "src": src, "dst": dst, "type": icmp[0], "code": icmp[1]}`: Erzeugt den Ergebnisdatensatz mit fortlaufender Framezahl, Adressen und ICMP-Typ/Code. Die Nummer beginnt bei eins wie in Wireshark; ICMP-Typ und -Code stehen in den ersten beiden ICMP-Bytes.

36. Zeile 38 — `        if icmp[0] == 8:`: Unterscheidet Echo Request über ICMP-Typ 8 vom Fehlerzweig. Echo Replies vom Typ 0 wären für diesen beabsichtigt nicht erreichbaren Server unerwartet und werden nicht als Erfolg umgedeutet.

37. Zeile 39 — `            assert (src, dst, icmp[1]) == ("10.0.1.2", "10.0.2.2", 0)`: Fordert für jede Echoanfrage genau Client als Quelle, Server als Ziel und Code 0. Damit werden nicht versehentlich fremde Ping-Pakete als Nachweis des gewünschten Versuchs akzeptiert.

38. Zeile 40 — `            request_keys.append(struct.unpack_from("!HH", icmp, 4))`: Liest Identifier und Sequenz der Echoanfrage als zwei vorzeichenlose 16-Bit-Netzwerkzahlen ab ICMP-Offset vier. Das Tupel wird unabhängig vom später ausgegebenen Frame-Datensatz für den abschließenden Zuordnungsbeweis gespeichert.

39. Zeile 41 — `        else:`: Behandelt alle anderen Typen als Kandidaten für den erwarteten Netzfehler. Das bedeutet nicht, dass beliebige ICMP-Nachrichten erlaubt wären: Die nächste Prüfung schränkt sie exakt ein.

40. Zeile 42 — `            assert (src, dst, icmp[0], icmp[1]) == ("10.0.13.2", "10.0.1.2", 3, 0)`: Verlangt r3s Adresse 10.0.13.2 als Fehlerquelle, den Client als Empfänger und Typ 3/Code 0. Diese Kombination bedeutet Destination Unreachable/Network Unreachable und passt zur auf r3 fehlenden Servernetzroute.

41. Zeile 43 — `            quoted = icmp[8:]`: Überspringt den acht Byte langen äußeren ICMP-Fehlergrundbereich. Danach liegt der zitierte Ausschnitt des auslösenden IP-Pakets, der erklärt, zu welchem ursprünglichen Verkehr die Fehlermeldung gehört.

42. Zeile 44 — `            assert len(quoted) >= 28 and quoted[0] >> 4 == 4`: Verlangt einen mindestens 28 Byte langen zitierten IPv4-Ausschnitt und Version vier. Das ist nur die erste Untergrenze; die folgenden Prüfungen berücksichtigen zusätzlich die tatsächliche Headerlänge einschließlich eventueller Optionen.

43. Zeile 45 — `            quoted_ihl = (quoted[0] & 15) * 4`: Berechnet die innere IPv4-Headerlänge aus dem IHL-Feld in Vier-Byte-Einheiten. Der zitierte ICMP-Header muss hinter diesem vollständigen Header beginnen, nicht pauschal an Byte zwanzig.

44. Zeile 46 — `            quoted_total = struct.unpack_from("!H", quoted, 2)[0]`: Liest die ursprünglich angegebene IP-Gesamtlänge des zitierten Pakets. Diese Länge darf größer als der zitierte Ausschnitt sein, weil ICMP-Netzfehler regulär nur den Header und mindestens acht Folgebytes zitieren müssen.

45. Zeile 47 — `            assert 20 <= quoted_ihl and quoted_ihl + 8 <= min(len(quoted), quoted_total)`: Verlangt einen mindestens zwanzig Byte langen inneren Header und acht anschließende Bytes innerhalb sowohl des vorhandenen Zitats als auch der ursprünglichen IP-Gesamtlänge. Dadurch können weder fehlende Optionen noch Padding einen fehlenden Echo-Header ersetzen.

46. Zeile 48 — `            assert quoted[9] == 1, "Zitiertes Protokoll muss ICMP sein"`: Fordert im inneren IPv4-Protokollfeld ausdrücklich die Nummer eins für ICMP. Identische Quell- und Zieladressen oder zufällig passende Bytes eines UDP-Pakets reichen damit nicht mehr als Echo-Nachweis.

47. Zeile 49 — `            assert struct.unpack_from("!H", quoted, 6)[0] & 0x3fff == 0`: Lehnt More-Fragments und einen Fragmentoffset auch im zitierten IPv4-Paket ab. Nur ein unfragmentierter Originaldatensatz wird als vollständig interpretierbarer Echoauslöser behandelt; Don't Fragment bleibt erlaubt.

48. Zeile 50 — `            assert socket.inet_ntoa(quoted[12:16]) == "10.0.1.2"`: Prüft im zitierten Originalheader den Client als ursprüngliche Quelle. Damit bezieht sich die Fehlermeldung nicht bloß zufällig an denselben Empfänger, sondern auf Verkehr dieses Clients.

49. Zeile 51 — `            assert socket.inet_ntoa(quoted[16:20]) == "10.0.2.2"`: Prüft den Server als ursprüngliches Ziel im eingebetteten IP-Paket. Gerade dieses innere Ziel zeigt, welches Zielnetz r3 nicht weiter erreichen konnte; das äußere Fehlerpaket selbst geht dagegen zum Client.

50. Zeile 52 — `            quoted_echo = quoted[quoted_ihl:quoted_ihl + 8]`: Schneidet exakt die ersten acht ICMP-Bytes hinter dem durch IHL bestimmten inneren IP-Header aus. Die vorangehende Längenprüfung stellt sicher, dass dieses Slice tatsächlich einen vollständigen Echo-Grundheader liefert.

51. Zeile 53 — `            assert quoted_echo[:2] == b"\x08\x00", "Zitierter Echo Request erwartet"`: Verlangt für den zitierten Auslöser Echo Request mit Typ acht und Code null. Ein Echo Reply oder eine anders codierte ICMP-Nachricht ist trotz passender Adressen kein zulässiger Auslöser dieser Fehleraufnahme.

52. Zeile 54 — `            error_keys.append(struct.unpack_from("!HH", quoted_echo, 4))`: Liest ID und Sequenz aus dem zitierten Echo-Grundheader und sammelt sie in der internen Fehlerliste. Damit lassen sich Fehler später auch dann zuordnen, wenn die Reihenfolge der Antwortframes nicht der Anfragereihenfolge entspricht.

53. Zeile 55 — `            item["quoted_dst"] = "10.0.2.2"`: Übernimmt das bereits aus den echten Bytes geprüfte innere Ziel in die Zusammenfassung. Der feste Text hier ist kein ausgedachtes Messergebnis, weil die vorherige Zeile genau diese Adresse verlangt hat.

54. Zeile 56 — `        frames.append(item)`: Hängt den vollständig geprüften Datensatz an die Frameliste an. Unzulässige Pakete würden zuvor eine Ausnahme auslösen und könnten daher nicht still in ein erfolgreiches Gesamtergebnis gelangen.

55. Zeile 57 — `    requests = [f for f in frames if f["type"] == 8]`: Filtert aus allen Frames die Echoanfragen mit Typ 8. Die List Comprehension erzeugt eine neue Liste der bereits geprüften Anfragen, ohne erneut die PCAP lesen zu müssen.

56. Zeile 58 — `    errors = [f for f in frames if f["type"] == 3]`: Filtert entsprechend die ICMP-Unreachable-Frames mit Typ 3. Ihre genauere Code- und Adressprüfung wurde bereits im Fehlerzweig vorgenommen.

57. Zeile 59 — `    assert len(requests) == len(errors) == 2, "Zwei Requests und zwei Netzfehler erwartet"`: Fordert weiterhin genau zwei Echoanfragen und zwei Netzfehler für den dokumentierten Zwei-Ping-Versuch. Diese reine Anzahlprüfung wird nun durch separate Eindeutigkeits- und Multisetprüfungen ergänzt, nicht mehr als Zuordnungsbeweis missverstanden.

58. Zeile 60 — `    assert len(set(request_keys)) == len(request_keys), "Doppelte Echo-ID/Sequenz"`: Vergleicht die Anzahl unterschiedlicher Anfrage-Tupel mit der gesamten Anfrageliste. Doppelte Echo-ID/Sequenz-Paare sind für diesen gezielten Nachweis unzulässig, selbst wenn zwei passend duplizierte Fehler die gleiche Multimenge ergäben.

59. Zeile 61 — `    assert sorted(request_keys) == sorted(error_keys), "Netzfehler passen nicht eindeutig zu Requests"`: Vergleicht die sortierten Tupellisten als Multimengen einschließlich ihrer Häufigkeiten. Zusammen mit der vorigen Einzigkeitsprüfung muss jeder der beiden Requests genau einmal zitiert werden; doppelte Fehler und unbekannte IDs oder Sequenzen scheitern.

60. Zeile 62 — `    return {"frames": frames, "requests": len(requests), "network_unreachable": len(errors)}`: Gibt die einzelnen geprüften Frames und die beiden Zähler zurück. Der Runner vergleicht die Framelänge zusätzlich mit dumpcaps Endzähler; diese zweite Quelle liegt außerhalb dieses Parsers.

61. Zeile 65 — `if __name__ == "__main__":`: Aktiviert den Kommandozeilenaufruf nur beim direkten Programmstart. Ein Import liefert lediglich die Funktion inspect und öffnet noch keine Datei.

62. Zeile 66 — `    print(json.dumps(inspect(sys.argv[1]), indent=2))`: Prüft die im ersten Argument angegebene PCAP und druckt das Ergebnis eingerückt als JSON. Ohne Argument oder bei unpassender Datei bricht das Programm mit einer Ausnahme ab; eine eigene Kommandozeilenhilfe ist nicht implementiert.

## Kontrollierte Änderungen: Was müsste gemeinsam angepasst werden?

1. **Andere Verzögerungen:** Linkwerte in lab_config, das theoretische budget und dessen Sollwerte sowie den groben RTT-Abstandstest gemeinsam betrachten. TC wird an beiden Linkenden eingerichtet. Nur die Budgetzahl zu ändern erzeugt keine andere Verzögerung im Netzwerk. Die Ausgangsstruktur verwendet zusätzlich ihren eigenen pauschalen Wert 10ms.
2. **Andere Paketanzahl:** Die Messoption -c, statistics mit seinem expected-Parameter und den TTL-Listenvergleich zusammen anpassen. Für den Fehlerfall kommen die Sollzahl im PCAP-Parser und die Aufnahmedauer hinzu. Sonst scheitert eine korrekte neue Messung nur an alten Erwartungen.
3. **Andere Adressen, Interfaces oder Pfade:** Nicht nur den Plan ändern: Auch Diagnoseziele, PCAP-Filter, erwartete Fehlerquelle, eingebettete Adressen und TTL-Sollwerte prüfen. Die harten Erwartungen sind Absicht für diesen konkreten Versuch, keine automatische Topologieerkennung.
4. **Anderer Fehler:** Der aktuelle Fehler entfernt ausschließlich r3s Servernetzroute auf B. Ein abgeschaltetes Interface, fehlende Rückroute oder Filterregel könnte statt Network Unreachable auch Host Unreachable, andere ICMP-Codes oder nur Zeitüberschreitungen ergeben. Die Diagnose und die Parsererwartungen müssten zum tatsächlich erzeugten Fehler passen.
5. **Neuer Nachweislauf:** Einen neuen Ordner statt run01 wählen und Rohdaten, JSON, Frames und Aussagen eindeutig diesem neuen Lauf zuordnen. Diese Hinweise betreffen mögliche künftige Versuche. Bei der aktuellen Offline-Korrektur wurden ausschließlich die Readiness-Frist und die Parserzuordnung geändert sowie Regressionstests ergänzt; kein neuer Netzlauf wurde gestartet.

## Maschinelle Abdeckungs- und Belegprüfung

- `verify_namespaces.py`: **184 von 184** nichtleeren Quellzeilen, in Originalreihenfolge und jeweils genau einmal.
- `ue7.3/auswerten.py`: **26 von 26** nichtleeren Quellzeilen, in Originalreihenfolge und jeweils genau einmal.
- `ue7.4/pcap_pruefen.py`: **62 von 62** nichtleeren Quellzeilen, in Originalreihenfolge und jeweils genau einmal.

Gesamt: **272 von 272** nichtleeren Quellzeilen. Die getrennte Testerklärung deckt zusätzlich jede nichtleere Zeile von `ue7.4/test_pcap.py` ab. Der unabhängige Leser vergleicht Zeilennummern, vollständigen Quelltext einschließlich Einrückung, Reihenfolge und Einmaligkeit; negative Kontrollen erkennen fehlende Einträge, Duplikate und veränderte Leerzeichen. Lokale Dokumentlinks werden separat geprüft.

Die vorhandenen A/B-Ping-Rohdaten und alle sechs Original-/A-/B-Ping-Statistiken werden erneut ohne Rootrechte mit `results.json` verglichen. Die gespeicherte Fehler-PCAP ergibt weiterhin bytegleich dieselbe JSON-Auswertung wie `fault-frames.json` und `results.json` und stimmt mit dumpcaps vier Frames überein. Die bestehenden Nachweise, `ue7.3/auswerten.py`, `erklaerung_topologie.md` und die Originalvorlagen bleiben unverändert. Das ist eine Offline-Regressionsprüfung vorhandener realer Belege, keine neue Netzwerkmessung oder Mininet-Ausführung.

## KI-Kennzeichnung

- **Tool:** Hermes Agent.
- **Anbieter/Modell:** OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
- **Datum:** 2026-10-29.
- **Ursprünglicher Dokumentauftrag:** Jede nichtleere Zeile der drei Messprogramme verständlich mit exaktem Quelltext und Zeilennummer erklären; Abdeckung maschinell prüfen.
- **Aktueller Auftrag:** „Fix Readiness-Frist im verify_namespaces.py und stärke PCAP Request/Fehler-Zuordnung in ue7.4/pcap_pruefen.py, teste mit echtemPCAP und Negativtests, aktualisiere zeilengenaue Erklärungen aller geänderten/neuenDateien. Keine Netzänderungen.“
- **Umfang:** KI-unterstützte Codekorrektur, Regressionstests und Aktualisierung der Zeilenerklärung; keine Commits oder Pushes. Die Verantwortung für Verständnis und Abgabe bleibt beim Studierenden; KI-Unterstützung wird nicht als Eigenleistung ausgegeben.
