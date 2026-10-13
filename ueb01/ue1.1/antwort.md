# Ü 1.1 – Umgebung und Sprachgrundlagen

## Ausführung

Vom Ordner `ueb01` aus nach dem [venv-Setup](../README.md):

```bash
python -B ue1.1/hello.py
python -B ue1.1/hello.py --name Fabio
```

Das Programm gibt standardmäßig **Fabio**, die laufende Python-Version und
das mit `Path.cwd()` ermittelte Arbeitsverzeichnis aus. Zusätzlich zeigt es
den tatsächlichen Interpreter, ob eine virtuelle Umgebung aktiv ist und
ausführbare Beispiele aller geforderten Sprachkonstrukte. Die Umgebung wurde
mit `python3 -m venv --without-pip ueb01/.venv` tatsächlich angelegt und das
Programm nach Aktivierung darin ausgeführt: Python 3.14.7, virtuelle Umgebung
`True`. Die Arbeitsverzeichnisse der Ausführungen sind im Prüfprotokoll festgehalten.

## Erläuterung der geforderten Konzepte

1. **Variablen und Typen:** Eine Variable ist ein Name, der auf ein Objekt
   verweist. `count = 3` bindet ein `int`-Objekt; `factor = 1.5` ein `float`;
   `enabled = True` ein `bool`. Ein `str` enthält Unicode-Text. `None` ist der
   besondere Wert für „kein Wert“. Typannotationen wie `number: int` beschreiben
   die beabsichtigte Verwendung, erzwingen sie allein aber nicht zur Laufzeit.
2. **`if/elif/else`:** `classify_number` prüft zuerst `< 0`, danach `== 0`.
   Nur der erste passende Zweig läuft; `else` behandelt positive Zahlen.
   Die CLI demonstriert alle drei Zweige mit -1, 0 und 1.
3. **`for` und `while`:** `for` durchläuft die Themenliste. `enumerate`
   liefert gleichzeitig Nummer und Thema. `while` wiederholt, solange eine
   Bedingung wahr ist. Das Verringern von `remaining` sorgt für ein Ende.
4. **Funktionen und Rückgaben:** `def` definiert eine wiederverwendbare
   Funktion. `return` beendet sie und gibt dem Aufrufer einen Wert zurück.
   `classify_number` liefert einen Text, `language_demo` ein Dictionary,
   `main` den Prozessstatus. 0 bedeutet erfolgreiche Ausführung.
5. **Liste und Dictionary:** Eine `list` ist eine geordnete, veränderbare
   Sammlung. Hier enthält sie Themen beziehungsweise Countdownwerte.
   Ein `dict` ordnet Schlüssel Werten zu, etwa `1: "Text"`. Die CLI zeigt
   für die Beispiele sowohl Inhalt als auch den tatsächlichen Typ.
6. **Import:** `import` macht Funktionen und Objekte anderer Module nutzbar.
   `argparse` verarbeitet Argumente, `pathlib` Dateipfade, `platform` die
   Python-Version und `sys` Informationen zum laufenden Interpreter.
7. **Kommandozeilenargumente:** `--name` ist eine optionale CLI-Option.
   `argparse` übernimmt das Einlesen und `--help`. Ohne `--name` wird Fabio
   verwendet. Ein unbekanntes Argument führt zu Status 2.

Eine **virtuelle Umgebung** hat einen eigenen Interpreter-Einstieg und
getrennte Paketverzeichnisse. Aktivieren verändert den Suchpfad der Shell;
es verändert den Programmcode nicht. Für dieses Blatt werden keine Pakete
installiert. `sys.prefix != sys.base_prefix` erkennt die aktive venv.

Alle Zeilen und kleine Änderungsübungen stehen in
[erklaerung_blatt01.md](../erklaerung_blatt01.md).

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.1 zeige Fabio, Version, echtes cwd,
Sprachgrundlagen und führe das Programm in einer tatsächlich erstellten venv aus.
