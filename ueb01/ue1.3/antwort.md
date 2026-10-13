# Ü 1.3 – Datei-I/O und Kommandozeilenparameter

## Ausführung

Vom Ordner `ueb01` aus mit aktiviertem venv:

```bash
mkdir -p .tmp
python -B ue1.3/convert.py Angabe/file1.txt .tmp/file1_lf.txt
python -B ue1.3/convert.py Angabe/file2.txt .tmp/file2_lf.txt
```

Das Programm hat zwei erforderliche Positionsargumente `infile` und `outfile`.
Es verwendet ausdrücklich UTF-8 und `with` für beide geöffneten Dateien.
Die beiden Originaldateien aus `Angabe/utf8files.zip` wurden tatsächlich
konvertiert; die Tests lesen zusätzlich die Mitglieder direkt aus dem ZIP
und vergleichen Quell- und Ausgabebytes. Die Angabe wird nicht verändert.

## Entscheidungen und Fehlerbehandlung

Die Angabe stellt hier keine gesonderten Theoriefragen; folgende Punkte
erklären die verlangte Funktionalität:

- **Universelles Lesen:** `newline=None` erkennt LF (`\n`), CRLF (`\r\n`)
  und CR (`\r`) und gibt sie als `\n` im gelesenen Text zurück.
- **Einheitliche Ausgabe:** `newline="\n"` schreibt unabhängig vom
  Betriebssystem LF. Es wird kein zusätzlicher letzter Zeilenumbruch eingefügt.
- **UTF-8:** `errors="strict"` verwirft ungültige Bytes nicht. Eine
  `UnicodeDecodeError` wird sichtbar gemeldet; Status ist 1.
- **Fehlende Argumente:** `argparse` zeigt die Verwendung und beendet mit
  Status 2. Überzählige Argumente werden ebenfalls abgelehnt.
- **Fehlende oder nicht lesbare Eingabe:** `FileNotFoundError`,
  `PermissionError` und beispielsweise `IsADirectoryError` sind
  `OSError`-Unterklassen. Die CLI gibt die konkrete Ausnahme einschließlich
  betroffenem Pfad nach `stderr` aus und beendet mit Status 1.
- **Nicht beschreibbare Ausgabe:** Auch dieser tatsächliche Dateifehler
  wird gemeldet, etwa bei fehlendem Zielordner oder verweigerten Rechten.
- **Gleiche Datei:** `resolve()` erkennt gleiche Pfade und symbolische Links;
  `samefile()` erkennt zusätzlich Hardlinks auf dieselbe Datei. Solche
  Aufrufe werden vor dem Schreiben zurückgewiesen, damit die Eingabe
  nicht beim Öffnen der Ausgabe gelöscht wird.
- **Dateien schließen:** Der Kontextmanager `with` schließt seine Datei
  auch bei Ausnahmen. Zuerst wird die Eingabe vollständig gelesen und
  geschlossen; erst dann wird die Ausgabe geöffnet. Dadurch bleibt eine
  vorhandene Ausgabe bei ungültigem Eingabe-UTF-8 erhalten.

**Grenzen:** Der gesamte Text liegt im Speicher, was für die vorgegebenen
kleinen Dateien angemessen ist. Eine andere bestehende Zieldatei wird
überschrieben. Scheitert das Schreiben während der Ausgabe, kann diese
teilweise geschrieben bleiben. Die Lösung ist kein atomarer Dateiaustausch.
Die Identitätsprüfung setzt voraus, dass keine anderen Prozesse zwischen
Prüfung und Öffnen die Pfade austauschen.

## Tatsächliche Rechteprüfungen

Die Tests setzen auf echten temporären Dateien beziehungsweise Verzeichnissen
`chmod(000)`, `chmod(400)` und `chmod(500)` und starten separate CLI-Prozesse.
Unter UID 1000 wurden alle drei Rechteprüfungen ausgeführt und bestanden.
Privilegierte Benutzer könnten diese Sperren umgehen; dann melden die Tests
ausdrücklich `skipped`. Ergänzend existieren zwei als **kontrollierte Mocks**
benannte Tests für Lese-/Schreibfehler. Der Schreibfehler-Mock prüft außerdem,
dass die Eingabe bereits geschlossen ist. Mocks sind keine Messung realer
Betriebssystemrechte.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.3 konvertiere Original-UTF-8-Dateien mit
LF-Ausgabe, sicheren Dateikontexten und tatsächlich geprüften Fehlerfällen.
