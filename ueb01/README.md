# Übungsblatt 01 – Rechnernetze

Sieben ausführbare Lösungen mit ausschließlich Python-Standardbibliothek,
95 `unittest`-Tests und deutscher Erklärung aller Python-Dateien einschließlich
der Tests. Benötigt wird Python **3.10 oder neuer**. Tatsächlich geprüft wurde
CPython 3.14.7 unter Linux am 2026-10-13.

## Übersicht

| Aufgabe | Einstieg | Inhalt |
|---|---|---|
| 1.1 | `ue1.1/hello.py` | Fabio, Python-Version, echtes Arbeitsverzeichnis und Sprachgrundlagen |
| 1.2 | `ue1.2/text_bytes.py` | Unicode, UTF-8, Bytes, Längen und Roundtrip |
| 1.3 | `ue1.3/convert.py` | UTF-8-Dateien mit universellem Lesen und LF-Ausgabe |
| 1.4 | `ue1.4/protocol.py` | Binärprotokoll, `create_message`, `parse_message`, Eingabeprüfung |
| 1.5 | `ue1.5/threads.py` | Rechenarbeit auf n Threads, eigene Bereiche und Ergebnisplätze |
| 1.6 | `ue1.6/shared_sum.py` | Gemeinsame Summe: naiv, Lock und separate Lost-Update-Demonstration |
| 1.7 | `ue1.7/producer_consumer.py` | Producer, mehrere Consumer, begrenzte Queue und kontrolliertes Ende |

Jeder Aufgabenordner enthält `antwort.md` mit Antworten und Ausführungsanleitung.
`ue1.5/calculation.py` ist das gemeinsame Hilfsmodul für 1.5 und 1.6;
`ue1.5/werte.txt` enthält neun Beispielwerte. Die Testhilfen stehen in
`tests/support.py`. Verzeichnisse wie `ue1.5` enthalten einen Punkt und sind
deshalb keine gewöhnlichen Python-Paketnamen; die Programme werden als Dateien
gestartet, die Tests laden sie mit `importlib`.

- [Vollständige Zeilenerklärung und Änderungsübungen](erklaerung_blatt01.md)
- [Tatsächliche Ausführungen, Messungen und Prüfergebnisse](testprotokoll_blatt01.md)
- [Originalangabe als Text](Angabe/angabe_blatt01.txt) und [PDF](angabe_blatt01.pdf)

## Setup einer virtuellen Umgebung

Alle folgenden Befehle sind **vom Ordner `ueb01` aus** angegeben. Eine virtuelle
Umgebung wurde tatsächlich hier angelegt und `hello.py` darin ausgeführt.
`--without-pip` vermeidet sogar eine unnötige pip-Installation: Es gibt nichts
nachzuinstallieren und keine `requirements.txt`.

```bash
cd /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01
python3 -m venv --without-pip .venv
source .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
python --version
mkdir -p .tmp
```

`source` aktiviert die Umgebung in der aktuellen Bash. `python` zeigt dann auf
`.venv/bin/python`. Ohne Aktivierung funktioniert beispielsweise
`.venv/bin/python -B ue1.1/hello.py`. `-B` und die Umgebungsvariable verhindern
`__pycache__`. Unter Windows ist die Aktivierung in PowerShell
`.venv\Scripts\Activate.ps1`; der Interpreter liegt dort unter
`.venv\Scripts\python.exe`. Die Programme selbst verwenden portable Pfade.

## Alle Programme ausführen

### 1.1 Umgebung und Grundlagen

```bash
python -B ue1.1/hello.py
python -B ue1.1/hello.py --name Fabio
```

Der Standardname ist Fabio. Das Arbeitsverzeichnis kommt von `Path.cwd()` und
hängt davon ab, von wo aus das Programm gestartet wurde.

### 1.2 Zeichenketten und Bytes

```bash
python -B ue1.2/text_bytes.py --text 'Grüße 🌍'
python -B ue1.2/text_bytes.py
python -B ue1.2/text_bytes.py --text ''
python -B ue1.2/text_bytes.py --text 'ä' --decode-as latin-1
python -B ue1.2/text_bytes.py --text 'ä' --decode-as ascii
```

Der zweite Aufruf wartet auf eine eingegebene Zeile. Der Latin-1-Versuch ergibt
verfälschten Text, jedoch keinen Dekodierungsfehler. Der ASCII-Versuch endet
erwartungsgemäß mit Status 1. UTF-8-Roundtrip und Originaltext werden zuvor
angezeigt.

### 1.3 Datei-I/O

```bash
python -B ue1.3/convert.py Angabe/file1.txt .tmp/file1_lf.txt
python -B ue1.3/convert.py Angabe/file2.txt .tmp/file2_lf.txt
```

Die beiden Originaldateien entsprechen den Mitgliedern von
`Angabe/utf8files.zip`; die Tests lesen das ZIP tatsächlich. Das Programm liest
mit `newline=None` CRLF, CR und LF und schreibt mit `newline="\n"` immer LF.
Unicode-Inhalt und ein fehlender letzter Zeilenumbruch bleiben erhalten.
Die Ausgabe wird erst nach vollständigem, erfolgreichem Lesen geöffnet.
Identische Dateien, auch über symbolische Links oder Hardlinks, werden abgelehnt.
Eine andere bestehende Ausgabedatei wird überschrieben.

Beispiele für absichtlich fehlschlagende Aufrufe:

```bash
python -B ue1.3/convert.py
python -B ue1.3/convert.py .tmp/fehlt.txt .tmp/fehlend_out.txt
python -B ue1.3/convert.py Angabe/file1.txt Angabe/file1.txt
```

Fehlende/überzählige Argumente haben Status 2, Datei- und Dekodierungsfehler
Status 1. Fehlermeldungen gehen nach `stderr`. Die Datei wird vollständig in
den Speicher gelesen; die Lösung ist für die kleinen Übungsdateien gedacht.
Ein Schreibfehler nach Öffnen einer anderen Zieldatei kann diese teilweise
geschrieben hinterlassen; es gibt keinen atomaren Austausch der Zieldatei.

### 1.4 Binäre Protokollnachrichten

```bash
python -B ue1.4/protocol.py
python -B ue1.4/protocol.py --data --urgent --sequence 65535 --payload 'ä'
python -B ue1.4/protocol.py --message-hex '10 00 00 2a 00 00 00 05 68 65 6c 6c 6f'
python -B ue1.4/protocol.py --sequence 0
```

Der erste Aufruf zeigt exakt den Referenzvektor aus dem Auftrag. Der letzte
Aufruf soll mit Status 1 scheitern. Das Headerformat ist `!HHI`, also 8 Bytes.
`parse_message` liefert ein `MessageFields`-NamedTuple mit den ursprünglichen
vier Feldern. `--message-hex` parst direkt eine vollständige Nachricht und
verwendet dabei die Erzeugungsoptionen nicht.

### 1.5 Threads mit eigenen Ergebnisplätzen

```bash
python -B ue1.5/threads.py ue1.5/werte.txt --threads 4 --iterations 50000
python -B ue1.5/threads.py ue1.5/werte.txt --threads 12 --iterations 1000
python -B -c "from pathlib import Path; Path('.tmp/leer.txt').write_bytes(b'')"
python -B ue1.5/threads.py .tmp/leer.txt --threads 3 --iterations 1000
```

Erwartet werden identische Einzelwerte zur sequentiellen Berechnung und eine
Ausgabe aller halboffenen Bereiche `[start, end)` einschließlich leerer
Bereiche. Das Eingabeformat sind durch Leerraum getrennte Floats mit Dezimalpunkt;
`NaN`, Unendlich und ungültige Tokens werden mit Zeilennummer abgelehnt.
Die Standardzahl der Iterationen ist 20000. Zeitmessungen enthalten den
Verwaltungsaufwand der Threads und sind keine garantierte Beschleunigung.

### 1.6 Gemeinsame Summe und Lock

```bash
python -B ue1.6/shared_sum.py ue1.5/werte.txt --threads 4 --iterations 50000 --runs 5 --mode all
python -B ue1.6/shared_sum.py .tmp/leer.txt --threads 5 --iterations 1 --runs 2
```

`all` führt `naive`, `lock` und `forced` jeweils mehrfach aus. Mit `--mode`
kann eine dieser Varianten allein gewählt werden. `--delay` (Standard 0.001 s)
gilt nur für die separate erzwungene Demonstration. Der Lock umfasst nur die
Addition der fertig berechneten Teilsumme. Erwartungswert, Messwert, Differenz
und Zeit stehen in jeder Ergebniszeile. Rundungsabweichungen werden mit
`math.isclose(rel_tol=1e-12, abs_tol=1e-12)` bewertet.

Eine naive Addition muss keinen beobachtbaren Fehler zeigen. `forced` liest die
Summe, synchronisiert die Threads mit einer Barrier, schläft und schreibt den
veralteten Wert zurück. Die dadurch erzeugten Lost Updates werden ausdrücklich
als didaktisches Experiment bezeichnet. Ein solcher erwarteter Unterschied
ist kein CLI-Fehler; eine falsche Lock-Summe ergibt Status 1.

### 1.7 Producer-Consumer

```bash
python -B ue1.7/producer_consumer.py
python -B ue1.7/producer_consumer.py --count 17 --consumers 3 --maxsize 2
python -B ue1.7/producer_consumer.py --count 257 --consumers 4 --maxsize 1
python -B ue1.7/producer_consumer.py --count 0 --consumers 5 --maxsize 1
```

Der Producer erzeugt `1..count`, danach ein `None`-Sentinel pro Consumer.
Die Queue-Kapazität muss positiv sein; `count=0` ist erlaubt. Individuelle
Summen können je nach Scheduling anders verteilt sein, die Gesamtsumme und
die Verarbeitung jedes Werts genau einmal bleiben gleich. Die Ergebnisse
bewahren zusätzlich die konsumierten Werte auf, um genau-einmal überprüfen
zu können: Die Queue ist begrenzt, die gesamte Ergebnisaufzeichnung benötigt
dennoch Speicher proportional zu `count`.

### Hilfe aller CLIs

```bash
python -B ue1.1/hello.py --help
python -B ue1.2/text_bytes.py --help
python -B ue1.3/convert.py --help
python -B ue1.4/protocol.py --help
python -B ue1.5/threads.py --help
python -B ue1.6/shared_sum.py --help
python -B ue1.7/producer_consumer.py --help
```

## Tests

```bash
python -B -m unittest discover -s tests -v
python -B tests/test_14_protocol.py
```

Der erste Befehl führt alle 95 Testmethoden mit vielen zusätzlichen Subtests
aus. Der zweite startet ausschließlich die Protokolltests. Keine Testdatei
benötigt pytest oder andere Pakete. CLI-Tests starten den aktuell verwendeten
Interpreter in eigenen Prozessen; Timeouts machen Hänger zu Testfehlern.
Testdateien, Messdaten, Coverage-Dateien und venv liegen in ignorierten
Unterordnern `.tmp`, `.verification` und `.venv`. Temporäre Testordner werden
automatisch entfernt.

Die Permission-Tests erzeugen echte Dateien mit `chmod` und starten echte
CLIs. Falls ein privilegierter Benutzer diese Rechte umgehen kann, melden
die Tests ausdrücklich `skipped`. Unter dem geprüften Benutzer UID 1000
wurde kein Test übersprungen. Zwei separat benannte Mock-Tests ergänzen die
Prüfung der Fehlerbehandlung und des Schließens der Eingabedatei.

## KI-Kennzeichnung und Arbeitsgrenzen

Die Lösung und Tests wurden mit KI erstellt; es wird keine Eigenleistung
behauptet. Vorbereitung: Hermes Agent, OpenAI / gpt-6.1-sol, Provider laut
`hermes status`: ChatGPT or Codex Subscription. Implementierung: Codex CLI
0.162.1, Modell gpt-6.1-sol, Datum 2026-10-13. Der konkrete Arbeitsauftrag
steht zusätzlich am Anfang jeder Python-Datei und am Ende jeder `antwort.md`.

Der Implementierungsagent arbeitete lokal auf `solver/ueb01` und führte selbst
keine Git-Veröffentlichung aus. Der Moodle-Solver prüft das Ergebnis unabhängig
und veröffentlicht den Ordner anschließend im Kurs-Repo. Es gibt keine
Moodle-Abgabe, kein neu erzeugtes Abgabe-ZIP und keine zusätzliche KI-Bericht-PDF.
Die Angabedateien bleiben unverändert; eine Gruppennummer wurde nicht erfunden.
