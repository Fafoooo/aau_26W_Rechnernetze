# Übungsblatt 01 – Erklärung aller Python-Dateien

Diese Anleitung erklärt den vorhandenen Code vom 2026-10-13. Sie setzt keine
Kenntnis der verwendeten Python-Konstrukte voraus. Lies jeweils die genannte
Datei neben der Erklärung. Die Nummern sind die echten Zeilennummern der
Dateien; jede nichtleere Quellzeile gehört zu genau einer erklärten Gruppe.
Die Codeauszüge sind unveränderte Ausschnitte der genannten Dateien;
eingerückte Fragmente gehören in ihren ursprünglichen Funktions-/Blockkontext.
Leerzeilen trennen Funktionen beziehungsweise Abschnitte optisch und führen
keine Operation aus. Einrückung dagegen ist bedeutend: Vier zusätzliche
Leerzeichen kennzeichnen den Körper einer Funktion, Schleife oder Bedingung.
Ein Doppelpunkt eröffnet einen solchen Block; das Zurückrücken beendet ihn.

Die Erklärungen umfassen auch das gemeinsame Rechenmodul, die Testhilfen und
jede Testmethode. Die Originaldateien, Markdown-Dateien und `werte.txt` sind
keine Python-Code-Dateien; deren Verwendung wird zusätzlich erläutert.
Die Ausführungsbefehle stehen in [README.md](README.md), die tatsächlichen
Messungen in [testprotokoll_blatt01.md](testprotokoll_blatt01.md).

## Zuerst: lesen, ausführen und verstehen

1. Öffne die README und wechsle in den dort angegebenen Ordner `ueb01`.
   Das **Arbeitsverzeichnis** ist der Ordner, auf den sich relative Dateipfade
   beziehen. Es muss nicht der Ordner der gerade gestarteten Python-Datei sein.
2. `python3 -m venv --without-pip .venv` führt das Standardbibliotheksmodul
   `venv` als Programm aus und erzeugt eine isolierte Umgebung. Es lädt keine
   Zusatzpakete. `.venv` ist ein lokaler Hilfsordner und wird ignoriert.
3. `source .venv/bin/activate` verändert die aktuelle Shell, sodass `python`
   den venv-Interpreter verwendet. Die **Shell** interpretiert deine
   Kommandozeilenbefehle; der **Interpreter** führt den Python-Code aus.
4. `python -B ue1.1/hello.py` startet die Datei. `-B` verhindert Bytecode-
   Cache-Dateien. Bytecode sind interne Anweisungen für den Interpreter;
   der Quelltext bleibt die maßgebliche lesbare Fassung.
5. Jedes CLI hat `main(...)`, das einen Status zurückgibt. `sys.exit(main())`
   übergibt diesen an das Betriebssystem. Status 0 heißt Erfolg; 1 ein
   erkannter Ausführungsfehler; `argparse` verwendet 2 für falsche Argumente.
   Ein Status ist kein gedruckter Text. `stdout` ist der normale Ausgabekanal,
   `stderr` der Fehlerkanal; die Tests erfassen beide getrennt.

## Begriffe und Syntax, auf die die Zeilenerklärungen zurückgreifen

- **Objekt, Variable, Typ:** Ein Objekt hat Wert und Typ; eine Variable ist
  ein Name, der darauf verweist. `x = 3` weist zu; `x == 3` vergleicht Werte.
  `type(x)` liefert den konkreten Typ. `is` prüft Identität und wird für
  `None` oder exakt bestimmte Typobjekte verwendet. `isinstance` akzeptiert
  auch Unterklassen. `bool` ist eine Unterklasse von `int`; strikte Protokoll-
  und Parameterprüfungen schließen diese unbeabsichtigte Annahme aus.
- **Literal:** Ein direkt geschriebener Wert: `3`, `1.5`, `True`, `None`,
  `"Text"`, `b"Bytes"`, `[]` oder `{}`. `0x...` bezeichnet Hexadezimalzahlen,
  `0b...` Binärzahlen und `0o...` Oktalzahlen, letztere hier für Dateirechte.
- **Sammlungen:** Eine Liste ist geordnet und veränderbar; ein Tuple ist
  geordnet und unveränderbar; ein Dictionary ordnet Schlüsseln Werte zu.
  Ein NamedTuple ist ein Tuple mit zusätzlich benannten Feldern.
  `items()` liefert die Schlüssel-Wert-Paare eines Dictionarys.
- **Index und Slice:** Indizes zählen ab 0. `values[start:end]` enthält
  `start`, aber nicht `end`. Ein Slice erzeugt hier eine neue Liste von
  Referenzen; die referenzierten Floats sind unveränderbar.
  `append(x)` hängt ein Element an, `extend(xs)` alle Elemente einer Sammlung.
- **Funktion:** `def` definiert sie; erst ein Aufruf mit `(...)` führt ihren
  Körper aus. Parameter sind die Eingangsnamen, Argumente die beim Aufruf
  übergebenen Werte. `return` liefert einen Wert und beendet die Funktion.
  Mehrere zurückgegebene Werte bilden ein Tuple. Ein Standardparameter
  nach `=` gilt, wenn der Aufrufer keinen eigenen Wert angibt.
- **Typannotation:** `list[float]`, `tuple[bytes, str]`, `-> int` beschreiben
  erwartete Typen. `A | None` erlaubt außerdem `None`. Annotationen ersetzen
  keine Laufzeitvalidierung; deshalb gibt es ausdrückliche Prüfungen.
- **Modul und Import:** Eine Python-Datei oder Bibliothekseinheit heißt
  Modul. `import math` bindet das Modul, `from pathlib import Path` einen
  bestimmten Namen. Die hier verwendeten Bibliotheken gehören zu Python.
  Der Modul-Docstring ist ein Text in dreifachen Anführungszeichen am Anfang
  und wird über `__doc__` beispielsweise als CLI-Beschreibung verwendet.
- **Schleifen:** `for` durchläuft eine Sammlung; `range(n)` liefert 0 bis
  n-1. `enumerate(xs, start=1)` liefert nummerierte Paare. `while` wiederholt
  bei wahrer Bedingung. `_` bedeutet hier, dass ein Schleifenzähler nicht
  gebraucht wird. `divmod(a,b)` liefert ganzzahligen Quotienten und Rest.
- **Bedingung:** `if`, `elif`, `else` wählen einen Zweig. `and` verlangt
  beide Bedingungen, `or` mindestens eine, `not` negiert. `and` und `or`
  werten nur bis zur Entscheidung aus (**Kurzschlussauswertung**).
  `a if condition else b` ist eine bedingte Wahl innerhalb eines Ausdrucks.
- **Ausdruck und Generator:** `[x for x in xs]` erzeugt eine Liste.
  `(x for x in xs)` beziehungsweise ein solcher Ausdruck als Funktions-
  argument liefert Werte schrittweise. Mehrere `for`-Teile bedeuten
  geschachtelte Durchläufe, zum Beispiel das Abflachen von Ergebnislisten.
  `any` meldet mindestens einen wahren Wert; `all` verlangt alle.
- **Formatierter Text:** `f"Wert: {x}"` setzt den Wert ein. `!r` nutzt `repr`
  mit Anführungszeichen und Escape-Darstellung, sodass Leertext, Bytes und
  Sonderzeichen sichtbar bleiben. `:.12f` formatiert zwölf Nachkommastellen,
  `:.6f` sechs. Rundung in der Anzeige ist keine Veränderung des Rechenwerts.
- **Unicode, Byte, Kodierung:** Ein Byte hat 8 Bits. Unicode-Codepoints
  bezeichnen Zeichen/Bestandteile; ein sichtbares Graphemcluster kann mehrere
  Codepoints umfassen. UTF-8 kodiert pro Codepoint ein bis vier Bytes.
  `encode` erzeugt Bytes, `decode` interpretiert sie als Text. **Roundtrip**
  heißt Hin- und Rückumwandlung mit Vergleich. Falscher, aber dekodierbarer
  Text heißt **Mojibake**. `\n`, `\r` und `\x00` sind Escape-Schreibweisen
  für LF, CR und ein Nullzeichen. Das `b` vor einem Literal erzeugt Bytes.
- **Ausnahme und Kontextmanager:** `raise` signalisiert einen Fehler;
  `try/except` behandelt ausgewählte Klassen. `as error` bindet das konkrete
  Ausnahmeobjekt. `raise ... from error` erhält dessen Ursache sichtbar.
  Ein `with`-Kontextmanager führt beim Verlassen Aufräumarbeiten aus.
  Ein `finally`-Block läuft auch bei `return` oder einer Ausnahme.
- **Thread und Synchronisation:** Ein Thread ist ein Ausführungsablauf im
  selben Prozess mit gemeinsamem Speicher. **Nebenläufig** heißt zeitlich
  überlappend organisiert; **parallel** heißt tatsächlich gleichzeitig
  ausgeführt. `start()` startet, `join()` wartet auf das Ende. Ein **Lock**
  erlaubt nur einen gleichzeitigen Eintritt in einen kritischen Abschnitt.
  Eine **Barrier** lässt Teilnehmer erst weiter, wenn alle angekommen sind.
  Eine **Race Condition** hängt von konkurrierenden Abläufen ab;
  **Lost Update** heißt überschriebenes, verlorenes Update. Der **GIL**
  begrenzt auf gewöhnlichem CPython die gleichzeitige Python-Ausführung.
- **Zeit und Float:** `perf_counter()` misst eine monotone, hochauflösende
  verstrichene Zeit; Differenzen umfassen auch Warte- und Verwaltungszeit.
  Floats sind binäre Näherungen, weshalb Summationsreihenfolgen leicht
  unterschiedlich runden können. `math.fsum` summiert besonders genau.
  `math.isclose` vergleicht mit relativer und absoluter Toleranz.
- **Queue:** Ein synchronisierter FIFO-Puffer liefert zuerst eingelegte
  Elemente zuerst aus. Blockierendes `put/get` wartet ohne aktive
  Warteschleife. Ein **Sentinel** ist ein spezieller Endwert. **Backpressure**
  ist das Bremsen des Erzeugers durch einen vollen Puffer. `task_done`
  quittiert eine Aufgabe; `Queue.join()` wartet auf alle Quittierungen.
- **Test:** Ein `unittest.TestCase` sammelt `test_...`-Methoden. Eine
  **Assertion** verlangt eine Eigenschaft und macht Verletzungen zu Fehlern.
  `assertEqual` vergleicht Werte, `assertIs` Identität, `assertTrue/False`
  Wahrheitswerte, `assertRaises` erwartete Ausnahmen, `assertRaisesRegex`
  zusätzlich deren Meldung. `subTest` benennt einzelne Fälle einer Schleife,
  ohne bei einem Fehlschlag die restlichen Fälle wegzulassen. Ein **Mock**
  ersetzt gezielt eine Abhängigkeit im Test; er ist keine reale Rechte-
  oder Netzwerkprüfung. Ein **Timeout** macht aus endlosem Warten einen
  sichtbaren Fehler. `Counter` zählt, wie oft jeder Wert vorkommt.

## Wiederkehrender KI-Kopf: jede Datei, Zeilen 1-6

Zeile 1 kennzeichnet die KI-Erstellung und behauptet keine Eigenleistung.
Zeile 2 nennt die vorbereitende Hermes-Agent-Nutzung mit OpenAI / gpt-6.1-sol.
Zeile 3 nennt den im Auftrag angegebenen Provider „ChatGPT or Codex
Subscription“. Zeile 4 benennt die tatsächliche Implementierungsumgebung
Codex CLI 0.162.1, Modell gpt-6.1-sol, Datum 2026-10-13. Zeilen 5-6 geben
die konkrete Anfrage für diese Datei wieder. `#` macht diese Zeilen zu
Kommentaren: Python führt sie nicht aus. Sie bleiben trotzdem in jeder
einzelnen Datei stehen, damit auch eine getrennt weitergegebene Datei ihre
Kennzeichnung behält. Die nachfolgenden Einzelabschnitte beziehen den Kopf
ausdrücklich ein; er wird nicht als unbesprochener Schritt übersprungen.

## `ue1.1/hello.py`

**Zeilen 1-6:** Der oben erläuterte KI-Kopf nennt hier den Auftrag zur
Umgebung und zu den Sprachbeispielen; sein Zweck ist die Herkunftskennzeichnung.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.1 zeige Fabio, Python-Version, echtes cwd und die Sprachgrundlagen.
```

**Zeile 8:** Der Modul-Docstring beschreibt das Programm. Er ist zugleich
die Beschreibung für `argparse`, damit die Hilfe den Zweck kennt.

```python
"""Ü 1.1: Umgebung und kleine, ausführbare Beispiele der Sprachgrundlagen."""
```

**Zeilen 10-13:** `argparse` verarbeitet die CLI; `Path` ermittelt das
Arbeitsverzeichnis; `platform` die laufende Python-Version; `sys` den
Interpreter, venv-Status und Prozessabschluss. Jeder Import hat diesen Zweck.

```python
import argparse
from pathlib import Path
import platform
import sys
```

**Zeilen 16-17:** `classify_number` wird definiert, nimmt eine Ganzzahl
und soll einen Text zurückgeben. Der Docstring beschreibt die Entscheidung;
die Definition führt die Entscheidung noch nicht aus.

```python
def classify_number(number: int) -> str:
    """Zeige alle drei Zweige einer bedingten Entscheidung."""
```

**Zeilen 18-19:** Ist `number` kleiner als 0, liefert `return` sofort
`"negativ"`. So werden negative Zahlen eindeutig eingeordnet.

```python
    if number < 0:
        return "negativ"
```

**Zeilen 20-21:** Nur wenn der erste Vergleich falsch war, prüft `elif`
die Gleichheit mit 0 und gibt `"null"` zurück.

```python
    elif number == 0:
        return "null"
```

**Zeilen 22-23:** `else` behandelt alle verbleibenden Zahlen, also positive,
und gibt `"positiv"` zurück. Damit fehlt für Integer kein Fall.

```python
    else:
        return "positiv"
```

**Zeilen 26-27:** `language_demo` hat keine Eingabeparameter und gibt ein
Dictionary zurück. Der Docstring erklärt, warum Beispieldaten statt
erfundener persönlicher Angaben verwendet werden.

```python
def language_demo() -> dict:
    """Erzeuge Beispiele, ohne persönliche Angaben wie ein Alter zu erfinden."""
```

**Zeilen 28-31:** `count`, `factor`, `enabled`, `nothing` erhalten die
Literale 3, 1.5, True und None. Damit gibt es konkrete Werte für die vier
grundlegenden Typen, die die CLI später wirklich anzeigt.

```python
    count = 3
    factor = 1.5
    enabled = True
    nothing = None
```

**Zeilen 32-35:** Die Themen stehen in einer Liste. Das zunächst leere
Dictionary wird mit Nummern als Schlüsseln gefüllt. `enumerate(..., start=1)`
liefert 1/Text, 2/Bytes und 3/Threads; die Zuweisung pro Paar zeigt einen
praktischen `for`-Durchlauf und Dictionaryzugriff.

```python
    topics = ["Text", "Bytes", "Threads"]
    numbered_topics = {}
    for index, topic in enumerate(topics, start=1):
        numbered_topics[index] = topic
```

**Zeilen 36-40:** Eine neue Liste sammelt den Countdown. `remaining` startet
bei 3. Die `while`-Bedingung lässt positive Werte anhängen; `-=` verringert
nach jedem Durchlauf um 1. Ohne diese Veränderung wäre die Schleife endlos.
Das Ergebnis ist 3, 2, 1; 0 wird nicht angehängt.

```python
    countdown = []
    remaining = count
    while remaining > 0:
        countdown.append(remaining)
        remaining -= 1
```

**Zeilen 41-45:** `return {` beginnt das Rückgabe-Dictionary. Die Schlüssel
`int`, `float`, `bool`, `NoneType` werden mit den zuvor gebundenen Werten
belegt. Doppelpunkte trennen Schlüssel und Wert, Kommas die Einträge.

```python
    return {
        "int": count,
        "float": factor,
        "bool": enabled,
        "NoneType": nothing,
```

**Zeilen 46-50:** `topics[0]` liefert den ersten Text. Die gesamte
Themenliste, das nummerierte Dictionary und der Countdown werden ebenfalls
zurückgegeben. `}` schließt die Sammlung und beendet den Rückgabeausdruck;
der Aufrufer kann alle Beispiele über ein gemeinsames Ergebnis anzeigen.

```python
        "str": topics[0],
        "list": topics,
        "dict": numbered_topics,
        "while-Ergebnis": countdown,
    }
```

**Zeilen 53-56:** `main` nimmt optional eine Argumentliste für Tests.
`None` bedeutet, dass `argparse` die echten Prozessargumente liest.
`--name` ist optional mit Standard Fabio; `parse_args` liefert die
geprüften Werte als Namespace. `description=__doc__` verwendet Zeile 8.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Fabio", help="Name (Standard: Fabio)")
    args = parser.parse_args(argv)
```

**Zeilen 57-59:** Drei f-Strings drucken Namen, Version und `Path.cwd()`.
Das cwd wird beim Aufruf ermittelt, nicht aus dem Dateipfad oder einem
festgeschriebenen Beispiel abgeleitet; deshalb bleibt die Ausgabe ehrlich.

```python
    print(f"Name: {args.name}")
    print(f"Python-Version: {platform.python_version()}")
    print(f"Arbeitsverzeichnis: {Path.cwd()}")
```

**Zeilen 60-61:** `sys.executable` nennt den tatsächlich laufenden
Interpreter. Verschiedene `prefix`/`base_prefix` zeigen eine venv an.
Beide Angaben dienen zur überprüfbaren Umgebungsdiagnose.

```python
    print(f"Python-Interpreter: {sys.executable}")
    print(f"Virtuelle Umgebung: {sys.prefix != sys.base_prefix}")
```

**Zeilen 62-63:** `items()` liefert alle Beispielpaare. `!r` zeigt ihre
präzise Darstellung, `type(value).__name__` den realen Typnamen.
Die Bezeichnung des Dictionaryschlüssels wird damit überprüfbar.

```python
    for label, value in language_demo().items():
        print(f"{label}: {value!r} (Typ: {type(value).__name__})")
```

**Zeilen 64-66:** Die Werte -1, 0, 1 rufen die Funktion mit jedem Zweig
auf und geben dessen Rückgabe aus. Danach meldet `return 0` Erfolg.

```python
    for number in [-1, 0, 1]:
        print(f"if/elif/else für {number}: {classify_number(number)}")
    return 0
```

**Zeilen 69-70:** Bei direktem Start heißt das Modul `__main__` und ruft
`main()` auf. Beim Import heißt es anders, deshalb werden keine CLIs
unbeabsichtigt gestartet. `sys.exit` reicht den Status an die Shell weiter.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu hello.py

1. Starte mit `--name 'Fabio Test'` und aus einem anderen Ordner. Prüfe,
   dass nur der Name beziehungsweise das echte cwd passend variieren.
2. Ergänze ein viertes Thema. Die `for`-Nummerierung wächst automatisch;
   der Countdown bleibt wegen `count=3` absichtlich drei Schritte lang.
   Ändere anschließend `remaining = len(topics)` und passe den Test an.
3. Ergänze einen Zweig für Werte größer als 100 vor dem letzten `else`.
   Schreibe einen Test für 101 und behalte die Tests für -1, 0 und 1.

## `ue1.2/text_bytes.py`

**Zeilen 1-6:** Der KI-Kopf nennt speziell Texteingabe, Bytefolge, Längen,
Roundtrip und Fehlkodierung; er erklärt die Herkunft dieser Lösung.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.2 lies Text, zeige UTF-8-Bytes, Längen, Roundtrip und Fehlkodierung.
```

**Zeile 8:** Der Docstring beschreibt den Ablauf von Eingabe bis Dekodierung
und dient wieder als CLI-Beschreibung.

```python
"""Ü 1.2: Text eingeben, UTF-8 kodieren und wieder dekodieren."""
```

**Zeilen 10-11:** `argparse` ermöglicht reproduzierbare Texteingabe per
Option; `sys` erlaubt Fehlermeldungen und den korrekten Exitstatus.

```python
import argparse
import sys
```

**Zeilen 14-16:** Die Funktion verspricht ein Tuple aus Bytes und Text.
`isinstance` stellt sicher, dass `encode` auf einer Zeichenkette arbeitet;
andere Typen bekommen bewusst `TypeError` statt einer zufälligen Fehlermeldung.

```python
def encode_and_decode(text: str) -> tuple[bytes, str]:
    if not isinstance(text, str):
        raise TypeError("text muss eine Zeichenkette (str) sein.")
```

**Zeilen 17-19:** UTF-8 kodiert den Text in Bytes und dekodiert mit derselben
Kodierung zurück. Das Ergebnis-Tuple enthält beide Objekte zur Ausgabe
und zum Vergleich. Strikte Standardfehlerbehandlung erfindet keine Ersatzzeichen.

```python
    data = text.encode("utf-8")
    decoded = data.decode("utf-8")
    return data, decoded
```

**Zeilen 22-26:** `main` erstellt die CLI. `--text` hat ohne Angabe den Wert
None und löst Eingabe aus; `--decode-as` aktiviert nur einen zusätzlichen
Versuch. `parse_args` übernimmt Hilfe und Syntaxfehler.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Text; ohne dieses Argument wird input() verwendet")
    parser.add_argument("--decode-as", help="Zusätzlicher Versuch mit dieser Kodierung")
    args = parser.parse_args(argv)
```

**Zeilen 27-29:** Im `try` wird ausdrücklich `is not None` geprüft:
Ein absichtlich leerer CLI-Text ist gültig und soll nicht zur Eingabe führen.
`input` entfernt den abschließenden Eingabe-Zeilenumbruch. Danach werden
die beiden Funktionsrückgaben in `data` und `decoded` entpackt.

```python
    try:
        text = args.text if args.text is not None else input("Text: ")
        data, decoded = encode_and_decode(text)
```

**Zeilen 30-32:** EOF ohne Zeile oder ein Kodierungsfehler wird mit
Originalmeldung nach `stderr` ausgegeben. Status 1 zeigt dem Aufrufer,
dass der reguläre Ablauf nicht abgeschlossen wurde.

```python
    except (EOFError, UnicodeError) as error:
        print(f"Eingabe-/Kodierungsfehler: {error}", file=sys.stderr)
        return 1
```

**Zeilen 33-36:** `repr` zeigt Text beziehungsweise Bytes eindeutig.
Die zwei `len`-Aufrufe zählen unterschiedliche Einheiten: Codepoints und
Bytewerte. Die Beschriftung verhindert eine Verwechslung der Einheiten.

```python
    print(f"str: {text!r}")
    print(f"bytes: {data!r}")
    print(f"len(str), Unicode-Codepoints: {len(text)}")
    print(f"len(bytes), Bytes: {len(data)}")
```

**Zeilen 37-38:** Dekodierter Text wird angezeigt und über `==` mit der
ursprünglichen Zeichenkette verglichen. So wird der Roundtrip geprüft,
anstatt nur zwei scheinbar gleiche Anzeigen anzunehmen.

```python
    print(f"UTF-8 dekodiert: {decoded!r}")
    print(f"Roundtrip identisch: {decoded == text}")
```

**Zeilen 39-41:** Nur bei gewählter Zusatzkodierung läuft der zweite
`decode`. Die ursprünglichen UTF-8-Bytes bleiben dieselben; verändert wird
nur ihre Interpretation, um die Konsequenz einer falschen Kodierung zu zeigen.

```python
    if args.decode_as is not None:
        try:
            other = data.decode(args.decode_as)
```

**Zeilen 42-44:** Ungültige Bytes für diese Kodierung oder ein unbekannter
Kodierungsname werden sichtbar gemeldet. Beide Fälle sind Fehler mit Status 1.

```python
        except (UnicodeError, LookupError) as error:
            print(f"Dekodierungsfehler ({args.decode_as}): {error}", file=sys.stderr)
            return 1
```

**Zeilen 45-47:** Falls die Zusatzdekodierung möglich ist, werden ihr Text
und ein separater Gleichheitsvergleich ausgegeben. Falscher Text kann ohne
Ausnahme entstehen; Status 0 bezeichnet dann die gelungene Demonstration.

```python
        print(f"Dekodiert mit {args.decode_as}: {other!r}")
        print(f"Auch damit identisch: {other == text}")
    return 0
```

**Zeilen 50-51:** Der Startschutz startet nur beim direkten Datei-Aufruf
und übergibt den Rückgabestatus an die Shell.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu text_bytes.py

1. Vergleiche ASCII, `ä`, `🌍` und `e` mit kombinierendem Akzent.
   Notiere Codepoints/Bytes vor dem Ausführen; prüfe danach die Vorhersage.
2. Probiere `latin-1`, `ascii` und `no-such-encoding` für dieselben
   UTF-8-Bytes. Erkläre, weshalb ein Fehler und falscher Text verschiedene
   Ergebnisse sind. Verifiziere die Prozessstatuswerte.
3. Ergänze eine Hex-Ausgabe mit `data.hex(' ')`. Die Bytefolge muss
   dieselbe bleiben; der neue Text ist nur eine Darstellung.

## `ue1.3/convert.py`

**Zeilen 1-6:** Der KI-Kopf beschreibt die konkrete Datei-Konvertierungs-
anfrage und die Prüfung der Fehlerfälle.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.3 konvertiere UTF-8-Dateien mit LF-Ausgabe und geprüften Fehlerfällen.
```

**Zeile 8:** Der Docstring nennt UTF-8 und die Normalisierung aller drei
gängigen Zeilenenden zu LF, damit die Hilfebeschreibung diese Entscheidung zeigt.

```python
"""Ü 1.3: UTF-8 kopieren und CRLF/CR/LF zu LF normalisieren."""
```

**Zeilen 10-12:** `argparse` behandelt die erforderlichen Pfade; `Path`
ermöglicht Datei- und Linkprüfung; `sys` stellt `stderr` und `exit` bereit.

```python
import argparse
from pathlib import Path
import sys
```

**Zeilen 15-17:** Die Funktion akzeptiert Textpfade oder Path-Objekte.
Beide werden mit `Path(...)` vereinheitlicht, um dieselben Dateioperationen
zu verwenden. Die Rückgabe ist die Länge des normalisierten Texts.

```python
def convert_file(infile: str | Path, outfile: str | Path) -> int:
    source = Path(infile)
    destination = Path(outfile)
```

**Zeile 18:** `resolve()` macht Pfade absolut und löst symbolische Links
auf. Gleiche aufgelöste Namen werden vor jedem Schreibzugriff erkannt.

```python
    same_path = source.resolve() == destination.resolve()
```

**Zeile 19:** Wenn beide Dateien existieren, prüft `samefile`, ob sie
dasselbe Betriebssystem-Dateiobjekt sind. Das erkennt Hardlinks, obwohl
ihre Namen verschieden sind. Die vorangehenden `exists`-Prüfungen verhindern
eine Samefile-Abfrage bei einem noch gar nicht existierenden Ausgabeobjekt.

```python
    same_inode = source.exists() and destination.exists() and source.samefile(destination)
```

**Zeilen 20-21:** Jede festgestellte Identität führt zu `ValueError`.
Damit kann die Eingabe nicht durch Öffnen als Ausgabe abgeschnitten werden.

```python
    if same_path or same_inode:
        raise ValueError("Ein- und Ausgabedatei müssen verschieden sein (auch Links).")
```

**Zeilen 22-23:** Die Quelle wird in Text-Lesemodus `r` geöffnet.
UTF-8 ist explizit, `strict` verbietet stilles Verwerfen ungültiger Bytes.
`newline=None` übersetzt CRLF und CR beim Lesen zu LF. `read()` liest
alles; das Verlassen des `with` schließt die Datei auch bei Ausnahmen.

```python
    with source.open("r", encoding="utf-8", errors="strict", newline=None) as handle:
        text = handle.read()
```

**Zeilen 24-25:** Erst nach erfolgreichem Lesen wird die andere Zieldatei
in Modus `w` geöffnet. Er erzeugt sie oder ersetzt ihren Inhalt.
`newline='\n'` verhindert eine betriebssystemabhängige Umwandlung nach
CRLF. `write(text)` schreibt den normalisierten Text mit UTF-8; auch diese
Datei wird durch `with` geschlossen. Schreibfehler dürfen nach außen gehen.

```python
    with destination.open("w", encoding="utf-8", errors="strict", newline="\n") as handle:
        handle.write(text)
```

**Zeile 26:** Die Codepointanzahl des tatsächlich verwendeten Texts geht
zurück an `main`. Es ist keine Byteanzahl und wird auch nicht so beschriftet.

```python
    return len(text)
```

**Zeilen 29-33:** `main` deklariert beide Positionsargumente mit `type=Path`.
Fehlen Werte, beendet `argparse` vor der Dateiarbeit mit Status 2.
`argv` bleibt als Testmöglichkeit erhalten.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=Path, help="Eingabedatei mit UTF-8-Text")
    parser.add_argument("outfile", type=Path, help="Ausgabedatei mit UTF-8 und LF")
    args = parser.parse_args(argv)
```

**Zeilen 34-38:** Der Funktionsaufruf liegt in `try`. Ein Decodefehler
bekommt eine spezifische Meldung mit Eingabepfad und Status 1.
Weil noch keine Ausgabe geöffnet wurde, bleibt vorhandener Zielinhalt erhalten.

```python
    try:
        length = convert_file(args.infile, args.outfile)
    except UnicodeDecodeError as error:
        print(f"Ungültiges UTF-8 in {args.infile}: {error}", file=sys.stderr)
        return 1
```

**Zeilen 39-41:** Die übrigen Betriebssystem- oder Identitätsfehler werden
mit ihrer Originalmeldung ausgegeben und liefern ebenfalls Status 1.
Die Ausnahmen werden also an der CLI-Grenze übersetzt, nicht verschluckt.

```python
    except (OSError, ValueError) as error:
        print(f"Dateifehler: {error}", file=sys.stderr)
        return 1
```

**Zeilen 42-43:** Nur bei Erfolg werden Anzahl, Ziel und das Format
ausgegeben und Status 0 geliefert. Eine Erfolgsmeldung nach einem Fehler
ist durch die früheren `return 1` ausgeschlossen.

```python
    print(f"{length} Unicode-Codepoints nach {args.outfile} geschrieben (UTF-8, LF).")
    return 0
```

**Zeilen 46-47:** Der Startschutz trennt Import vom CLI-Aufruf und
`sys.exit` macht Fehler für Skripte und Tests erkennbar.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu convert.py

1. Erzeuge eine lokale Testdatei mit `a\r\nb\rc\n` und prüfe die Ausgabe
   als Bytes. Sie muss `a\nb\nc\n` enthalten, auch unter Windows.
2. Setze in einer Kopie der Funktion `errors='ignore'`. Beobachte bei
   `b'\xff'` den Datenverlust und erkläre, warum die Lösung `strict` nutzt.
   Behalte die Originalimplementierung unverändert und die Fehlertests grün.
3. Plane blockweises Kopieren für große Dateien. Überlege vor der Änderung,
   wie CRLF an Blockgrenzen und eine bereits existierende Ausgabe bei
   spätem Decodefehler behandelt werden. Ein blindes Byte-Kopieren würde
   die vereinbarte Zeilenendennormalisierung nicht erfüllen.

## `ue1.4/protocol.py`

**Zeilen 1-6:** Der Kopf nennt das konkrete Bitformat und den validierten
Roundtrip. Er dokumentiert die KI-Herkunft auch beim separaten Verteilen der Datei.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.4 nutze exakt !HHI, V=2, reserved=0, positive uint16 und validierten Roundtrip.
```

**Zeile 8:** Der Docstring beschreibt einen 8-Byte-Header plus variable
Nutzlast. Ein Header ist der feste Steuerteil vor den eigentlichen Nutzdaten.

```python
"""Ü 1.4: 8-Byte-Protokollheader und variable, nichtleere Nutzlast."""
```

**Zeilen 10-13:** `argparse` erstellt die Demo-CLI, `struct` kodiert
Integerfelder binär, `sys` verarbeitet CLI-Fehler und `NamedTuple` benennt
die vier extrahierten Felder ohne die Tuple-Eigenschaften zu verlieren.

```python
import argparse
import struct
import sys
from typing import NamedTuple
```

**Zeile 16:** Ein `Struct` speichert das wiederverwendbare Format `!HHI`.
`!` bedeutet Big Endian/Netzwerkbytefolge mit Standardgrößen ohne Padding;
die beiden `H` belegen je 2 Bytes, `I` 4 Bytes. Padding wäre zusätzlicher
Ausrichtungsspeicher und darf nicht unvereinbart im Protokoll stehen.

```python
HEADER = struct.Struct("!HHI")
```

**Zeilen 17-19:** Die Konstanten legen Version 2, maximale Sequenz 65535
und maximale Payload-Byteanzahl 4294967295 fest. Großbuchstaben markieren
beabsichtigte Konstanten; Python verbietet ihre Änderung nicht automatisch.

```python
VERSION = 2
MAX_SEQUENCE = 65535
MAX_PAYLOAD_LENGTH = 4294967295
```

**Zeilen 22-26:** Die Klasse definiert ein NamedTuple mit Datenflag,
Dringlichkeitsflag, Sequenz und Bytes. Die Reihenfolge entspricht den
Eingabeparametern, damit Tuple-Vergleich und später `create_message(*fields)`
einen direkten Roundtrip ermöglichen. Die Typen allein validieren nichts.

```python
class MessageFields(NamedTuple):
    is_data: bool
    is_urgent: bool
    sequence_number: int
    payload: bytes
```

**Zeilen 29-31:** Die gemeinsame Sequenzprüfung verlangt exakt `int`.
`isinstance(True, int)` wäre wahr und deshalb zu großzügig; echte bools
müssen als Sequenz abgelehnt werden. Bei falschem Typ folgt `TypeError`.

```python
def validate_sequence(sequence_number: int) -> None:
    if type(sequence_number) is not int:
        raise TypeError("sequence_number muss int sein; bool ist nicht erlaubt.")
```

**Zeilen 32-33:** Die verkettete Vergleichsprüfung verlangt 1..65535.
Unsigned erlaubt zwar technisch 0, aber die Angabe sagt positiv; deshalb
ist 0 nicht zulässig. Außerhalb des Bereichs folgt `ValueError`.

```python
    if not 1 <= sequence_number <= MAX_SEQUENCE:
        raise ValueError("sequence_number muss im Bereich 1..65535 liegen.")
```

**Zeilen 36-39:** Der Erzeuger ist exakt die geforderte Funktion.
Beide Flags müssen echte bools sein. Die Sequenzprüfung wird wiederverwendet,
damit Erzeuger und Parser dieselbe Grenze verwenden.

```python
def create_message(is_data: bool, is_urgent: bool, sequence_number: int, payload: bytes) -> bytes:
    if type(is_data) is not bool or type(is_urgent) is not bool:
        raise TypeError("is_data und is_urgent müssen echte bool-Werte sein.")
    validate_sequence(sequence_number)
```

**Zeilen 40-43:** Nur echte `bytes` sind Nutzlast. Text, Bytearray und
Memoryview werden nicht stillschweigend umgewandelt. Die Länge muss positiv
und in uint32 darstellbar sein; die Untergrenze verbietet leere Nutzlast.

```python
    if type(payload) is not bytes:
        raise TypeError("payload muss bytes sein.")
    if not 1 <= len(payload) <= MAX_PAYLOAD_LENGTH:
        raise ValueError("payload muss nichtleer sein und ihre Länge in uint32 passen.")
```

**Zeile 44:** Version 2 wird um elf Bits in die höchsten fünf Bitstellen
geschoben. D wird in lokales Bit 1, U in Bit 0 gesetzt. Bool-zu-Integer
liefert 0/1; `|` kombiniert die disjunkten Felder. Die neun dazwischen
liegenden Bits bleiben 0. Das Resultat ohne Flags ist `0x1000`, also `10 00`.

```python
    word = (VERSION << 11) | (int(is_data) << 1) | int(is_urgent)
```

**Zeile 45:** `pack` serialisiert Wort, Sequenz und Byteanzahl.
**Serialisieren** heißt Daten in ein vereinbartes Übertragungsformat
abbilden. `+ payload` hängt die ursprünglichen Bytes an. Die Länge wird
aus der tatsächlichen Payload bestimmt; keine fremde Längenangabe kann abweichen.

```python
    return HEADER.pack(word, sequence_number, len(payload)) + payload
```

**Zeilen 48-50:** Der Parser akzeptiert eine vollständige Byte-Nachricht,
sonst `TypeError`. **Parsen/Deserialisieren** heißt diese strukturierte
Bytefolge wieder in Felder zerlegen.

```python
def parse_message(message: bytes) -> MessageFields:
    if type(message) is not bytes:
        raise TypeError("message muss bytes sein.")
```

**Zeilen 51-53:** Ohne acht Headerbytes wird sofort abgelehnt, bevor
`unpack_from` lesen könnte. `unpack_from` liest ab Offset 0 genau den
Header, obwohl dahinter noch Nutzlast steht, und liefert drei Integer.

```python
    if len(message) < HEADER.size:
        raise ValueError("Nachricht ist kürzer als der 8-Byte-Header.")
    word, sequence_number, payload_length = HEADER.unpack_from(message)
```

**Zeilen 54-55:** `>> 11` entfernt die unteren elf Bits und isoliert V.
Für Reserved werden zuerst die beiden Flags entfernt, dann mit `0x1FF`
(neun Einsbits) genau neun Bits ausgeblendet. `&` ist das bitweise UND;
die Maske lässt nur die gewünschten Bitstellen übrig.

```python
    version = word >> 11
    reserved = (word >> 2) & 0x1FF
```

**Zeilen 56-59:** Nur Version 2 und Reserved gleich 0 sind gültig.
Jede Verletzung wird spezifisch gemeldet. So können unbekannte Formate
oder heimlich gesetzte Steuerbits nicht als gültige Nachricht passieren.

```python
    if version != VERSION:
        raise ValueError("Versionsnummer muss 2 sein.")
    if reserved != 0:
        raise ValueError("Reservierte Bits müssen 0 sein.")
```

**Zeilen 60-62:** Auch eingehende Sequenzen unterliegen der positiven
Grenze. Längenfeld 0 wird als leere Payload zurückgewiesen, selbst wenn
noch zusätzliche Bytes folgen würden.

```python
    validate_sequence(sequence_number)
    if payload_length == 0:
        raise ValueError("payload darf nicht leer sein.")
```

**Zeilen 63-65:** Die deklarierte Länge muss exakt den vorhandenen Bytes
nach dem Header entsprechen. Dadurch werden Trunkierung und angehängte
Zusatzbytes erkannt. Die Flags werden per Masken in bools verwandelt,
die Payload wird ab Byte 8 gesliced und alle Originalfelder zurückgegeben.
Es wird kein Textdecoder auf binäre Header oder Payload angewandt.

```python
    if payload_length != len(message) - HEADER.size:
        raise ValueError("Payload-Länge im Header stimmt nicht mit der Nachricht überein.")
    return MessageFields(bool(word & 0b10), bool(word & 0b1), sequence_number, message[HEADER.size:])
```

**Zeilen 68-71:** `main` erstellt die CLI; `store_true` macht beide Flags
standardmäßig False und bei Vorhandensein True. So kommen echte bools
bei der API an, ohne Integer-Flags als Sonderfall zu erlauben.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", action="store_true", help="D-Flag setzen")
    parser.add_argument("--urgent", action="store_true", help="U-Flag setzen")
```

**Zeilen 72-75:** Sequenz wird als int gelesen, Standard 42. Payloadtext
ist standardmäßig `hello`; alternativ kann eine vollständige Hexnachricht
angegeben werden. `parse_args` erzeugt die zugänglichen Optionswerte.

```python
    parser.add_argument("--sequence", type=int, default=42)
    parser.add_argument("--payload", default="hello", help="Als UTF-8 kodierte Nutzlast")
    parser.add_argument("--message-hex", help="Statt Erzeugen eine Hex-Nachricht parsen")
    args = parser.parse_args(argv)
```

**Zeilen 76-81:** Ohne Hexoption wird Payloadtext ausdrücklich mit UTF-8
kodiert und serialisiert. Mit Hexoption erzeugt `bytes.fromhex` die Bytes
direkt; Leerzeichen zwischen Hexbytes sind erlaubt. Beide Wege verwenden
danach denselben validierenden Parser.

```python
    try:
        if args.message_hex is None:
            message = create_message(args.data, args.urgent, args.sequence, args.payload.encode("utf-8"))
        else:
            message = bytes.fromhex(args.message_hex)
        fields = parse_message(message)
```

**Zeilen 82-84:** Eingabe- und Protokollfehler einschließlich ungültigem
Hextext führen zur konkreten Fehlermeldung und Status 1. Bei ungültiger
Nachricht werden keine angeblich gültigen Felder gedruckt.

```python
    except (ValueError, TypeError) as error:
        print(f"Protokollfehler: {error}", file=sys.stderr)
        return 1
```

**Zeilen 85-88:** Hexdarstellung, feste Headergröße, bereits geprüfte
Version/Reserved, Flags, Sequenz und Payload mit Byteanzahl werden
ausgegeben. `message.hex(' ')` ändert nicht die Nachricht selbst.

```python
    print(f"Nachricht (Hex): {message.hex(' ')}")
    print(f"Header: {HEADER.size} Bytes; Version: {VERSION}; Reserviert: 0")
    print(f"D: {fields.is_data}; U: {fields.is_urgent}; Sequenz: {fields.sequence_number}")
    print(f"Payload ({len(fields.payload)} Bytes): {fields.payload!r}")
```

**Zeilen 89-90:** `*fields` entpackt die vier Tuplefelder als einzelne
Argumente. Die erneute Serialisierung muss mit den ursprünglichen Bytes
übereinstimmen. Der Vergleich wird gezeigt; gültige Verarbeitung liefert 0.

```python
    print(f"Roundtrip identisch: {create_message(*fields) == message}")
    return 0
```

**Zeilen 93-94:** Der Startschutz macht das Modul als API importierbar
und sorgt beim CLI-Aufruf für den passenden Status.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Bitrechnung zum Nachvollziehen

Für False/False, Sequenz 42 und `b'hello'` gelten nacheinander:
`V=00010`, danach neun Nullbits und zwei Nullflags; als 16-Bit-Wort
`0001 0000 0000 0000`. Es wird zu `10 00`. Sequenz 42 wird `00 2a`, Länge 5
wird `00 00 00 05`. `h e l l o` wird `68 65 6c 6c 6f`.
Zusammen sind es acht Headerbytes plus fünf Payloadbytes, also 13 Bytes.
Die Netzwerkbitnummern im Bild zählen von links; lokale Shiftpositionen
zählen von rechts. Gerade dieser Unterschied erklärt die Verschiebung um 11.

### Änderungsübungen zu protocol.py

1. Setze D und U einzeln. Berechne vor dem Start `10 02` beziehungsweise
   `10 01`; vergleiche mit der Ausgabe und den festen Testvektoren.
2. Erzeuge eine gültige Nachricht, setze anschließend ein Reserved-Bit
   mit einer Bytearray-Kopie und parse wieder als bytes. Der Parser muss
   `ValueError` liefern, nicht neue Felder akzeptieren.
3. Ersetze probeweise `!` durch native Bytefolge und erkläre die dann
   gebrochenen unabhängigen Vektoren. Stelle das vereinbarte Format wieder
   her; ein neuer Protokollentwurf müsste beide Kommunikationsseiten ändern.

## `ue1.5/calculation.py`

**Zeilen 1-6:** Die Kennzeichnung nennt das gemeinsame Rechen- und
Eingabemodul für beide Threadaufgaben, damit keine getrennten Rechnungen driften.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# teile für 1.5/1.6 dieselbe deterministische Berechnung, Eingabe und Slice-Aufteilung.
```

**Zeile 8:** Der Docstring hält die gemeinsame Verantwortung des Moduls
fest. Es ist ein importiertes Hilfsmodul, kein zusätzliches Pflicht-CLI.

```python
"""Gemeinsame Berechnung und Eingabeprüfung für Ü 1.5 und Ü 1.6."""
```

**Zeilen 10-12:** `argparse` stellt den speziellen Argumentfehler bereit,
`math` die endliche Float-Prüfung und Trigonometrie, `Path` das sichere
Öffnen von Eingabedateien. Es wird kein externes Numerikpaket verwendet.

```python
import argparse
import math
from pathlib import Path
```

**Zeile 15:** 20000 Iterationen sind der gemeinsame Standard. Die CLI
kann ihn ersetzen; die Tests verwenden bewusst kleinere Zahlen, weil
sie Korrektheit und nicht die Geschwindigkeit prüfen.

```python
DEFAULT_ITERATIONS = 20000
```

**Zeilen 18-22:** Die Validatorfunktion nimmt einen Wert und dessen
Bezeichnung für Meldungen. Erst wird ein echter Integer verlangt, dann
mindestens 1. Null Threads wären keine Aufteilung, null Iterationen keine
gewählte Rechenarbeit. Das Label sagt, welcher Parameter falsch war.

```python
def validate_positive_integer(value: int, label: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{label} muss int sein, nicht bool oder ein anderer Typ.")
    if value < 1:
        raise ValueError(f"{label} muss mindestens 1 sein.")
```

**Zeilen 25-28:** `positive_int` passt den Validator an CLI-Text an.
`int(text)` wandelt eine Ganzzahl-Schreibweise um; danach gilt dieselbe
positive Grenze wie in der API. Ein Standardwert wird nicht heimlich aus
einem ungültigen Text erzeugt.

```python
def positive_int(text: str) -> int:
    try:
        value = int(text)
        validate_positive_integer(value, "Wert")
```

**Zeilen 29-31:** Konversions-/Bereichsfehler werden in
`ArgumentTypeError` mit bewahrter Ursache übersetzt, damit `argparse`
eine saubere Verwendungsfehlermeldung mit Status 2 liefert. Bei Erfolg
geht der geprüfte Integer zurück.

```python
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value
```

**Zeilen 34-38:** `load_values` sammelt Floats in einer neuen Liste.
Die Datei wird mit UTF-8 und universellen Zeilenenden im `with` geöffnet.
`enumerate(..., start=1)` merkt die echte Dateizeile; `split()` zerlegt
alle Leerraumtrennungen. Leere Zeilen ergeben keine Tokens und sind erlaubt.

```python
def load_values(filename: str | Path) -> list[float]:
    values = []
    with Path(filename).open("r", encoding="utf-8", newline=None) as handle:
        for line_number, line in enumerate(handle, start=1):
            for token in line.split():
```

**Zeilen 39-42:** Jeder Token wird mit `float()` konvertiert. Ein
fehlerhafter Token führt zu einer Meldung mit Zeilennummer und sichtbarer
`repr`-Darstellung. `from error` hält die eigentliche Ursache fest.
Dezimalpunkt und Exponentenschreibweise sind möglich, Dezimalkomma nicht.

```python
                try:
                    value = float(token)
                except ValueError as error:
                    raise ValueError(f"Zeile {line_number}: keine Gleitkommazahl: {token!r}") from error
```

**Zeilen 43-46:** `float()` akzeptiert auch `nan`, `inf` und überlaufende
Exponentenschreibweisen. `isfinite` lehnt sie hier bewusst ab, bevor sie
die Rechnung vergiften. Gültige Werte werden angehängt; die Liste wird
nach dem Schließen zurückgegeben. Eine Leerdatei ergibt `[]`.

```python
                if not math.isfinite(value):
                    raise ValueError(f"Zeile {line_number}: Wert muss endlich sein: {token!r}")
                values.append(value)
    return values
```

**Zeilen 49-54:** Die eigentliche Funktion nimmt Werte und Iterationszahl.
Sie validiert Iterationen auch bei leerer Eingabe. Für direkte API-Aufrufe
prüft sie zusätzlich jeden Wert auf Endlichkeit; die Dateiprüfung allein
würde diese Aufrufer nicht schützen.

```python
def complicated_calculation(values: list[float], iterations: int = DEFAULT_ITERATIONS) -> list[float]:
    validate_positive_integer(iterations, "iterations")
    results = []
    for value in values:
        if not math.isfinite(value):
            raise ValueError("Alle Eingabewerte müssen endlich sein.")
```

**Zeilen 55-56:** `seed = sin(value)` macht aus jedem endlichen Eingang
einen begrenzten Startwert und wahrt seinen Einfluss auf das Ergebnis.
`state` beginnt bei diesem Seed. Auch ein sehr großer endlicher Float
erzeugt damit keinen ungebremst anwachsenden Anfangszustand.

```python
        seed = math.sin(value)
        state = seed
```

**Zeilen 57-60:** Die innere Schleife führt echte sin/cos-Arbeit genau
`iterations`-mal aus. Sinus und Cosinus liegen in [-1,1], daher bleibt
der neue State zwischen -1.5 und 1.5. Nach der Schleife wird ein Ergebnis
pro Eingang angehängt und die geordnete Liste zurückgegeben. Kein Sleep,
Zufall oder Uhrzeitwert fließt in die Rechnung ein; sie ist deterministisch.

```python
        for _ in range(iterations):
            state = math.sin(state) + 0.5 * math.cos(state + seed)
        results.append(state)
    return results
```

**Zeilen 63-68:** `split_ranges` verlangt eine positive Threadzahl sowie
eine nichtnegative echte Integerlänge. Die Länge darf 0 sein, bools und
negative Zahlen sind keine sinnvollen Arraylängen.

```python
def split_ranges(length: int, number_of_threads: int) -> list[tuple[int, int]]:
    validate_positive_integer(number_of_threads, "number_of_threads")
    if type(length) is not int:
        raise TypeError("length muss int sein.")
    if length < 0:
        raise ValueError("length darf nicht negativ sein.")
```

**Zeilen 69-71:** `divmod` zerlegt Länge in Grundanteil und Rest.
Die Ergebnisliste beginnt leer, der erste Startindex ist 0. Bei weniger
Werten als Threads ist der Grundanteil 0, was später leere Slices erlaubt.

```python
    base, remainder = divmod(length, number_of_threads)
    ranges = []
    start = 0
```

**Zeilen 72-76:** Für jeden Thread wird ein Endindex berechnet.
Die ersten `remainder` Threads bekommen einen zusätzlichen Wert.
Das Paar wird angehängt; der nächste Start wird genau das vorige Ende.
Damit gibt es weder Überlappung noch Lücken, und am Schluss wird die Liste
aller n Bereiche zurückgegeben. Beim leeren Array sind alle Paare (0,0).

```python
    for index in range(number_of_threads):
        end = start + base + (1 if index < remainder else 0)
        ranges.append((start, end))
        start = end
    return ranges
```

### Änderungsübungen zu calculation.py

1. Rechne `split_ranges(10,3)` auf Papier aus: (0,4), (4,7), (7,10).
   Prüfe anschließend, dass jede Zahl 0..9 genau einmal in einem Bereich liegt.
2. Ändere in einer Übungskopie den Faktor 0.5 und beobachte die neuen
   Ergebnisse. Beide Aufgaben müssen weiterhin dieselbe importierte
   Funktion verwenden; passe die Ein-Schritt-Referenz gezielt an.
3. Ergänze einen Test für `1e999` und erkläre, weshalb dies zwar von
   `float` lesbar, aber für diese Eingabe ungültig ist. Entferne deshalb
   nicht die Endlichkeitsprüfung.

## `ue1.5/threads.py`

**Zeilen 1-6:** Der KI-Kopf nennt n Threads, eigene Bereiche und den
sequentiellen Vergleich als konkreten Auftrag.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.5 berechne eigene Slices/Result-Slots mit n Threads und vergleiche sequentiell.
```

**Zeile 8:** Der Docstring erklärt die Ownership: Jeder Thread hat
seinen Eingabebereich und schreibt genau einen Ergebnisplatz.

```python
"""Ü 1.5: Eigene Eingabebereiche und Ergebnisplätze pro Thread."""
```

**Zeilen 10-14:** Die Imports dienen CLI, genauer Summe, Fehlerausgabe,
echten Threads und Zeitmessung. `time` wird zum Messen, nicht zum
künstlichen Verlangsamen der Rechnung genutzt.

```python
import argparse
import math
import sys
import threading
import time
```

**Zeilen 16-17:** Beide Importzeilen holen ausschließlich die gemeinsame
Berechnung, Datei-/Integerprüfung und Aufteilung aus `calculation.py`.
Beim direkten Start liegt dieses Modul im selben Ordner wie das Skript.

```python
from calculation import DEFAULT_ITERATIONS, complicated_calculation, load_values, positive_int
from calculation import split_ranges, validate_positive_integer
```

**Zeilen 20-24:** `worker` erhält die gemeinsame lesbare Eingangsliste,
Slicegrenzen und seinen Index. Er berechnet nur den Slice und weist nur
`results[index]` zu. An der Threadgrenze fängt er gewöhnliche Ausnahmen
und legt sie im zugehörigen Fehlerplatz ab. So gehen Fehler nicht bloß
in einer Hintergrundausgabe verloren.

```python
def worker(values, start, end, results, index, iterations, errors):
    try:
        results[index] = complicated_calculation(values[start:end], iterations)
    except Exception as error:
        errors[index] = error
```

**Zeilen 27-29:** `run_parallel` validiert Iterationen und berechnet die
vollständige Bereichsliste. `split_ranges` prüft zugleich die Threadzahl,
bevor ein Thread gestartet wird.

```python
def run_parallel(values: list[float], number_of_threads: int, iterations: int = DEFAULT_ITERATIONS):
    validate_positive_integer(iterations, "iterations")
    ranges = split_ranges(len(values), number_of_threads)
```

**Zeilen 30-32:** `[None] * n` reserviert je n zunächst unbelegte
Ergebnis- und Fehlerplätze. None ist unveränderbar, daher teilt diese
Multiplikation keine veränderbaren inneren Listen. `threads` sammelt die
Objekte, auf die später gewartet werden muss.

```python
    results = [None] * number_of_threads
    errors = [None] * number_of_threads
    threads = []
```

**Zeilen 33-38:** `enumerate` liefert Platzindex und Bereichspaar.
`Thread(target=worker, args=(...), name=...)` konfiguriert den Worker.
Es wird die Funktion selbst übergeben, nicht ihr Aufruf. Das Argumenttuple
enthält alle Daten; ein lesbarer Name hilft bei Diagnosen.

```python
    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=worker,
            args=(values, start, end, results, index, iterations, errors),
            name=f"Rechner-{index + 1}",
        )
```

**Zeilen 39-42:** Jedes Threadobjekt wird gespeichert und gestartet.
Erst nachdem alle gestartet wurden, wartet die zweite Schleife auf alle
Enden. Würde man sofort nach jedem Start joinen, liefen die Worker
unnötig nacheinander.

```python
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
```

**Zeilen 43-45:** Nach den joins sind die Fehlerplätze vollständig.
Ein gespeicherter Fehler wird als `RuntimeError` mit ursprünglicher
Ursache wieder ausgelöst. Damit kann die CLI korrekt fehlschlagen.

```python
    for error in errors:
        if error is not None:
            raise RuntimeError("Berechnung in einem Thread fehlgeschlagen.") from error
```

**Zeilen 46-51:** Teilergebnisse werden in Platzreihenfolge gesammelt,
unabhängig von der Abschlussreihenfolge der Threads. Ein unerwartet
unbelegter Platz wird ausdrücklich abgelehnt. `extend` fügt dessen
Einzelwerte ein; Rückgabe ist das Paar aus Gesamtwerteliste und Bereichen.

```python
    ordered_results = []
    for partial in results:
        if partial is None:
            raise RuntimeError("Ein Thread hat kein Ergebnis geliefert.")
        ordered_results.extend(partial)
    return ordered_results, ranges
```

**Zeilen 54-59:** Die CLI verlangt die Datei, erlaubt positive Thread-
und Iterationsoptionen und verwendet Standards aus dem gemeinsamen Modul.
`positive_int` lässt unbrauchbare Größen bereits in `argparse` scheitern.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", help="UTF-8-Datei: Floats durch Leerraum getrennt")
    parser.add_argument("--threads", type=positive_int, default=4)
    parser.add_argument("--iterations", type=positive_int, default=DEFAULT_ITERATIONS)
    args = parser.parse_args(argv)
```

**Zeilen 60-64:** Die Werte werden einmal geladen. Danach markieren
zwei `perf_counter`-Messpunkte die reine sequentielle Referenzrechnung.
Einlesen ist nicht Teil dieser Rechenzeit; Ergebnis ist eine Einzelwerteliste.

```python
    try:
        values = load_values(args.infile)
        started = time.perf_counter()
        expected = complicated_calculation(values, args.iterations)
        sequential_time = time.perf_counter() - started
```

**Zeilen 65-67:** Ein neuer Zeitbeginn umfasst die komplette Thread-
Berechnung einschließlich Erzeugen, Starten und Warten. Beide Varianten
verwenden dieselben Eingaben und Iterationen, damit der Vergleich sinnvoll ist.

```python
        started = time.perf_counter()
        actual, ranges = run_parallel(values, args.threads, args.iterations)
        threaded_time = time.perf_counter() - started
```

**Zeilen 68-70:** Datei-, Unicode-, Validierungs- und weitergegebene
Workerfehler werden an der CLI mit Status 1 gemeldet. Es wird kein
zufällig unvollständiger Ergebnisvergleich als Erfolg ausgegeben.

```python
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"Berechnungsfehler: {error}", file=sys.stderr)
        return 1
```

**Zeilen 71-73:** Eingabegröße und Optionen werden sichtbar, danach
jeder nummerierte halboffene Bereich mit seiner Größe. Leere Bereiche
werden ebenfalls gezeigt und machen `n > len(values)` nachvollziehbar.

```python
    print(f"Werte: {len(values)}; Threads: {args.threads}; Iterationen pro Wert: {args.iterations}")
    for index, (start, end) in enumerate(ranges, start=1):
        print(f"Thread {index}: [{start}, {end}) -> {end - start} Werte")
```

**Zeilen 74-78:** `fsum` zeigt beide Summen, die Zeiten werden getrennt
ausgegeben. Gleichheit wird auf den ganzen Einzelwertelisten geprüft,
nicht nur auf möglicherweise gleichen Summen. Der GIL-Hinweis verhindert
eine unbegründete Geschwindigkeitsgarantie. Ungleiche Listen ergeben Status 1.

```python
    print(f"Sequentiell: Summe={math.fsum(expected):.12f}; Zeit={sequential_time:.6f} s")
    print(f"Threads:     Summe={math.fsum(actual):.12f}; Zeit={threaded_time:.6f} s")
    print(f"Identische Einzelwerte: {actual == expected}")
    print("GIL: CPU-Arbeit mit Threads ist auf gewöhnlichem CPython nicht automatisch schneller.")
    return 0 if actual == expected else 1
```

**Zeilen 81-82:** Der Startschutz ermöglicht Importtests ohne CLI und
liefert beim direkten Start einen tatsächlich prüfbaren Prozessstatus.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu threads.py

1. Verwende 1, 4 und 12 Threads für die neun Werte. Vergleiche die
   Bereiche und ordne die identischen Einzelwerte wieder den Eingaben zu.
2. Verschiebe in einer Kopie `join` unmittelbar hinter `start` und miss
   erneut. Erkläre, warum das Warten dann die geplante Nebenläufigkeit
   verhindert. Die Originalfassung muss alle Worker zuerst starten.
3. Füge einen ungültigen Wert wie NaN direkt per API ein. Verfolge den
   Fehler vom Workerplatz über `RuntimeError.__cause__` zum Hauptthread.

## `ue1.6/shared_sum.py`

**Zeilen 1-6:** Die Kennzeichnung nennt echte Wiederholungen und die
gesondert ausgewiesene erzwungene Demonstration. Sie behauptet keine eigenen
Messungen außerhalb der dokumentierten tatsächlichen Programmläufe.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.6 miss naive und Lock-Summen mehrfach; kennzeichne erzwungene Lost Updates separat.
```

**Zeile 8:** Der Docstring benennt die gemeinsame Summe, den kurzen
kritischen Abschnitt und das separate Interleaving-Experiment.

```python
"""Ü 1.6: Gemeinsame Summe, kurzer Lock und separate Interleaving-Demonstration."""
```

**Zeilen 10-15:** CLI, Float-Summe/Vergleich, Pfad zum Nachbarordner,
Suchpfad/Fehlerstatus, Threads/Lock/Barrier und Zeit/Sleep werden importiert.
Sleep wird allein im erzwungenen Konflikt eingesetzt.

```python
import argparse
import math
from pathlib import Path
import sys
import threading
import time
```

**Zeilen 17-19:** `__file__` ist der Pfad dieser Code-Datei; `resolve`
und `parents[1]` finden `ueb01`. Der Ordner `ue1.5` wird am Anfang von
`sys.path` eingetragen, damit das gemeinsame Modul auch bei anderem cwd
auffindbar ist. Es werden keine Dateien kopiert oder geändert. Anschließend
werden dieselben Funktionen wie in 1.5 importiert, um Rechendrift zu verhindern.

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ue1.5"))
from calculation import DEFAULT_ITERATIONS, complicated_calculation, load_values, positive_int
from calculation import split_ranges, validate_positive_integer
```

**Zeilen 22-24:** Die API legt Standards für Iterationen, Modus und
Sleepdauer fest. Sie validiert Iterationen und lässt die Bereichsfunktion
vor jedem Threadstart die positive Threadzahl prüfen.

```python
def run_shared(values, number_of_threads, iterations=DEFAULT_ITERATIONS, mode="naive", delay=0.001):
    validate_positive_integer(iterations, "iterations")
    ranges = split_ranges(len(values), number_of_threads)
```

**Zeilen 25-28:** Nur naive, lock und forced sind gültige API-Modi.
Die Verzögerung muss endlich und nichtnegativ sein; NaN, Unendlich und
negative Zeiten dürfen nicht erst in Worker-Sleeps scheitern.

```python
    if mode not in ("naive", "lock", "forced"):
        raise ValueError("mode muss naive, lock oder forced sein.")
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay muss endlich und mindestens 0 sein.")
```

**Zeilen 29-32:** Eine gemeinsame Ein-Element-Liste enthält 0.0 und
lässt Worker ihren Inhalt verändern, ohne `nonlocal` für einen neu gebundenen
Float zu brauchen. Alle verwenden denselben Lock. Nur forced benötigt
eine Barrier mit n Teilnehmern; 10 Sekunden Timeout verhindern endloses
Barrierwarten. Für jeden Worker wird ein Fehlerplatz angelegt.

```python
    shared = [0.0]
    lock = threading.Lock()
    barrier = threading.Barrier(number_of_threads, timeout=10) if mode == "forced" else None
    errors = [None] * number_of_threads
```

**Zeilen 34-36:** Die innere Workerfunktion hat Zugriff auf die äußeren
Objekte; das heißt **Closure**. Sie berechnet und summiert zuerst ausschließlich
ihren Slice. Dieser aufwendige Schritt liegt ausdrücklich außerhalb des Locks.

```python
    def worker(index, start, end):
        try:
            subtotal = math.fsum(complicated_calculation(values[start:end], iterations))
```

**Zeilen 37-39:** Im Lock-Modus wird nur der Summenupdate geschützt.
`with lock` erwirbt den Lock, `+=` liest/addiert/schreibt die gemeinsame
Summe, dann gibt das Verlassen den Lock automatisch frei.

```python
            if mode == "lock":
                with lock:
                    shared[0] += subtotal
```

**Zeilen 40-41:** Naive verwendet direkt dieselbe Addition ohne Lock,
Barrier oder Sleep. Damit wird die tatsächlich naive Variante untersucht;
eine Abweichung wird weder eingebaut noch garantiert.

```python
            elif mode == "naive":
                shared[0] += subtotal
```

**Zeilen 42-46:** Der verbleibende gültige Modus ist forced. Zuerst
wird der alte gemeinsame Wert gelesen. Die Barrier hält jeden Worker,
bis alle gelesen haben. Sleep lässt den Unterschied zu einem direkten
Update zusätzlich sichtbar werden. Danach schreibt jeder sein altes
Snapshot plus Teilsumme. Kein Worker berücksichtigt Updates seit seinem
Lesen; der letzte Schreibvorgang überschreibt die übrigen Summen.

```python
            else:
                snapshot = shared[0]
                barrier.wait()
                time.sleep(delay)
                shared[0] = snapshot + subtotal
```

**Zeilen 47-50:** Workerfehler werden in eigenen Slots abgelegt.
Bei vorhandener Barrier löst `abort()` wartende Teilnehmer mit einem
Barrierfehler, damit sie nicht auf einen ausgefallenen Teilnehmer warten.
Auch diese Fehler gelangen über die Ergebnisprüfung zum Aufrufer.

```python
        except Exception as error:
            errors[index] = error
            if barrier is not None:
                barrier.abort()
```

**Zeilen 52-56:** Ein Thread wird für jeden Bereich konfiguriert,
gespeichert und gestartet. Der Name gibt seine Nummer an; alle Threads
teilen die äußere Summe, behalten aber ihre eigenen lokalen Teilsummen.

```python
    threads = []
    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(index, start, end), name=f"Summe-{index + 1}")
        threads.append(thread)
        thread.start()
```

**Zeilen 57-62:** Erst wird auf alle Enden gewartet, dann werden Fehler
weitergegeben. Nur ohne Fehler wird der gemeinsame Float zurückgegeben.
Es wird keine erwartete Summe als scheinbar gemessener Wert eingesetzt.

```python
    for thread in threads:
        thread.join()
    for error in errors:
        if error is not None:
            raise RuntimeError("Gemeinsame Berechnung in einem Thread fehlgeschlagen.") from error
    return shared[0]
```

**Zeilen 65-70:** Die CLI deklariert Datei sowie positive Thread-,
Iterations- und Wiederholungszahlen. Standards sind vier Threads, die
gemeinsame Iterationszahl und fünf Läufe je ausgewähltem Modus.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", help="Dieselbe Float-Datei wie in Ü 1.5")
    parser.add_argument("--threads", type=positive_int, default=4)
    parser.add_argument("--iterations", type=positive_int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--runs", type=positive_int, default=5)
```

**Zeilen 71-73:** `choices` begrenzt den CLI-Modus und bietet zusätzlich
all. `--delay` wird als Float gelesen, später validiert. Hilfe erläutert,
dass diese Wartezeit nur forced beeinflusst.

```python
    parser.add_argument("--mode", choices=["naive", "lock", "forced", "all"], default="all")
    parser.add_argument("--delay", type=float, default=0.001, help="Sleep nur in forced, in Sekunden")
    args = parser.parse_args(argv)
```

**Zeilen 74-75:** all wird zu einem Tuple aus drei Modi erweitert;
ein einzelner Modus wird ein Ein-Element-Tuple, erkennbar am abschließenden
Komma. `locked_ok` merkt, ob sämtliche Lock-Ergebnisse korrekt bleiben.

```python
    modes = ("naive", "lock", "forced") if args.mode == "all" else (args.mode,)
    locked_ok = True
```

**Zeilen 76-81:** Einlesen und sequentielle Referenz erfolgen einmal.
Die Optionen werden ausgegeben. Beide Begleittexte legen offen, dass
naive nicht zwingend scheitert und forced absichtlich eingegriffen wird.

```python
    try:
        values = load_values(args.infile)
        expected = math.fsum(complicated_calculation(values, args.iterations))
        print(f"Werte: {len(values)}; Threads: {args.threads}; Iterationen: {args.iterations}")
        print("naive: direktes +=; eine Abweichung ist nicht garantiert.")
        print("forced: didaktisch erzwungenes read/barrier/sleep/write; keine naive +=-Messung.")
```

**Zeilen 82-87:** Die äußere Schleife wählt den Modus, die innere seine
echten Wiederholungsläufe. Jeder Aufruf erzeugt neue Threads und eine
neue gemeinsame Summe. Zeitdifferenz misst diesen Lauf. `isclose` mit
relativer und absoluter Toleranz 1e-12 trennt kleine Float-Rundung von
deutlicher Ergebnisabweichung.

```python
        for mode in modes:
            for run in range(1, args.runs + 1):
                started = time.perf_counter()
                actual = run_shared(values, args.threads, args.iterations, mode, args.delay)
                elapsed = time.perf_counter() - started
                matches = math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
```

**Zeilen 88-92:** Mehrere unmittelbar benachbarte f-Strings werden zu
einer einzigen Ausgabe zusammengesetzt. Die Zeile enthält Modus/Lauf,
Referenz, gemessenen Wert, gemessene Differenz, Vergleich und verstrichene
Zeit. Zwölf beziehungsweise sechs Nachkommastellen betreffen nur die Anzeige.

```python
                print(
                    f"{mode} Lauf {run}: erwartet={expected:.12f}; gemessen={actual:.12f}; "
                    f"Differenz={actual - expected:.12f}; {'OK' if matches else 'ABWEICHUNG'}; "
                    f"Zeit={elapsed:.6f} s"
                )
```

**Zeilen 93-94:** Nur ein abweichender geschützter Lauf macht den
abschließenden Erfolgsstatus falsch. Erwartete forced-Unterschiede und
mögliche naive Konflikte sind Untersuchungsergebnisse, keine versteckten CLI-Fehler.

```python
                if mode == "lock" and not matches:
                    locked_ok = False
```

**Zeilen 95-98:** Datei-/Kodierungs-/Validierungs-/Workerfehler bekommen
Status 1 mit Originalmeldung. Ohne solche Fehler wird anhand der Lock-
Prüfung 0 oder 1 zurückgegeben. Es wird kein falsches Lock-Ergebnis übergangen.

```python
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"Summenfehler: {error}", file=sys.stderr)
        return 1
    return 0 if locked_ok else 1
```

**Zeilen 101-102:** Der Startschutz trennt API und ausführbares Programm;
die Shell erhält den tatsächlichen Funktionsstatus.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu shared_sum.py

1. Führe naive mehrfach aus, etwa mit `--runs 20`, und dokumentiere
   nur echte Messwerte. Ein fehlerfreier Lauf ist eine Beobachtung und
   beweist keine allgemeine Atomarität des Quelltextoperators.
2. Stelle forced auf einen Thread oder leere Werte. Erkläre anhand der
   Lese-/Schreibschritte, warum der erwartete Lost-Update-Effekt dann entfällt.
3. Verschiebe in einer Kopie die Berechnung in den Lock und miss.
   Unterscheide korrekte Summe von unnötig großem kritischem Abschnitt.
   Belasse die tatsächliche Lösung beim Lock nur um die Addition.

## `ue1.7/producer_consumer.py`

**Zeilen 1-6:** Der Kopf nennt den eigenen Producer, mehrere Consumer,
begrenzte Queue und kontrolliertes Ende als konkreten KI-Auftrag.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.7 nutze begrenzte Queue, eigenen Producer, mehrere Consumer, Sentinels und joins.
```

**Zeile 8:** Der Docstring beschreibt blockierende Übergabe und Ende.
Er erklärt schon in der CLI-Hilfe, welches Muster demonstriert wird.

```python
"""Ü 1.7: Begrenzte Queue, blockierende Übergabe und kontrolliertes Ende."""
```

**Zeilen 10-14:** `argparse` verarbeitet Zählergrößen, `queue` die
synchronisierte FIFO-Struktur, `sys` Fehlerstatus, `threading` Ausführungs-
abläufe und `NamedTuple` geordnete, benannte individuelle Ergebnisse.

```python
import argparse
import queue
import sys
import threading
from typing import NamedTuple
```

**Zeilen 17-19:** Ein ConsumerResult besteht aus einem Tuple beliebig
vieler Integer und dessen Summe. `tuple[int, ...]` beschreibt beliebige
Länge. Die Wertaufzeichnung ermöglicht später eine genaue Duplikatprüfung;
die private Liste wird am Ende in ein unveränderbares Tuple gewandelt.

```python
class ConsumerResult(NamedTuple):
    values: tuple[int, ...]
    total: int
```

**Zeilen 22-24:** Der Producer erzeugt mit `range(1,count+1)` genau
1..count; bei count 0 keine Werte. `put(block=True)` wartet, wenn die
begrenzte Queue voll ist, und erzeugt damit tatsächliche Backpressure.

```python
def producer(work_queue, count, consumer_count):
    for value in range(1, count + 1):
        work_queue.put(value, block=True)
```

**Zeilen 25-26:** Nach allen Integern folgt ein None pro Consumer.
Die Sentinels stehen hinter den Daten in derselben FIFO-Queue. Mehrere
Consumer benötigen mehrere Endsignale, da jeder sein eigenes entnimmt.

```python
    for _ in range(consumer_count):
        work_queue.put(None, block=True)
```

**Zeilen 29-33:** Jeder Consumer hat eine eigene Liste und Summe.
`while True` wartet wiederholt in blockierendem `get` auf das nächste
Element. Die Endbedingung ist das Sentinel, keine unzuverlässige `empty`-Abfrage.

```python
def consumer(work_queue, results, index):
    values = []
    total = 0
    while True:
        item = work_queue.get(block=True)
```

**Zeilen 34-37:** Nach erfolgreichem get beginnt der `try/finally`-
Bereich. Bei None speichert der Consumer seinen fertigen Result-Slot
und kehrt zurück. Der Return führt trotzdem den finally-Block aus.

```python
        try:
            if item is None:
                results[index] = ConsumerResult(tuple(values), total)
                return
```

**Zeilen 38-41:** Reguläre Integer werden privat aufgezeichnet und
addiert. `finally` quittiert jedes entnommene Element exakt einmal,
auch None oder ein Verarbeitungsfehler. Damit passt die Aufgabenbuchhaltung
von Queue.join zu allen erfolgreichen put-Aufrufen.

```python
            values.append(item)
            total += item
        finally:
            work_queue.task_done()
```

**Zeilen 44-49:** Die API prüft alle drei Größen in einer gemeinsamen
Schleife mit passendem Mindestwert und Label. Echte Integer sind erforderlich.
Count darf 0 sein; Consumerzahl und maxsize müssen mindestens 1 sein.
Das verhindert die in Python sonst unbegrenzte Queue bei maxsize 0.

```python
def run_pipeline(count: int, consumers: int, maxsize: int) -> list[ConsumerResult]:
    for value, minimum, label in [(count, 0, "count"), (consumers, 1, "consumers"), (maxsize, 1, "maxsize")]:
        if type(value) is not int:
            raise TypeError(f"{label} muss int sein, nicht bool oder ein anderer Typ.")
        if value < minimum:
            raise ValueError(f"{label} muss mindestens {minimum} sein.")
```

**Zeilen 50-52:** Die Queue wird mit festgelegter positiver Kapazität
angelegt. Ein zunächst unbelegter Ergebnisplatz je Consumer und eine
Threadliste ermöglichen Zuständigkeit und späteres vollständiges Warten.

```python
    work_queue = queue.Queue(maxsize=maxsize)
    results = [None] * consumers
    threads = []
```

**Zeilen 53-56:** Alle Consumer werden mit jeweils eigenem Index
konfiguriert, gespeichert und gestartet. Sie dürfen auf eine leere Queue
warten; sie laufen bereits, bevor der Producer bei Kapazität 1 blockieren könnte.

```python
    for index in range(consumers):
        thread = threading.Thread(target=consumer, args=(work_queue, results, index), name=f"Consumer-{index + 1}")
        threads.append(thread)
        thread.start()
```

**Zeilen 57-58:** Der Producer erhält dieselbe Queue, die Anzahl Werte
und Consumer. Ein eigener Thread führt die Erzeugung wirklich nebenläufig aus.

```python
    producer_thread = threading.Thread(target=producer, args=(work_queue, count, consumers), name="Producer")
    producer_thread.start()
```

**Zeilen 59-62:** Erst wird auf den Producer gewartet, sodass alle
Aufgaben einschließlich Sentinels bereits eingereiht sind. Queue.join
wartet auf ihre Quittierungen. Danach wartet Thread.join auf das tatsächliche
Ende jedes Consumers. Ein frühes Queue.join vor abgeschlossener Produktion
könnte bei noch leerer Queue voreilig zurückkehren.

```python
    producer_thread.join()
    work_queue.join()
    for thread in threads:
        thread.join()
```

**Zeilen 63-65:** Falls irgendein Platz noch None ist, wird ein fehlendes
Ergebnis sichtbar abgelehnt. Sonst gehen die individuellen Ergebnisse
zurück; die Reihenfolge entspricht den Consumer-Indizes, nicht ihrem Tempo.

```python
    if any(result is None for result in results):
        raise RuntimeError("Ein Consumer hat kein Ergebnis geliefert.")
    return results
```

**Zeilen 68-73:** Die CLI erlaubt count, consumers und maxsize als
Integer und verwendet 100/3/8 als Standards. Die explizite API-Prüfung
übernimmt deren Bereichsregeln, `argparse` die gültige Ganzzahl-Schreibweise.

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100, help="Erzeuge 1 bis count (0: keine Zahlen)")
    parser.add_argument("--consumers", type=int, default=3)
    parser.add_argument("--maxsize", type=int, default=8, help="Positive Queue-Kapazität")
    args = parser.parse_args(argv)
```

**Zeilen 74-78:** Die Pipeline läuft innerhalb der Fehlerübersetzung.
Ungültige Eingaben oder fehlende Resultate erhalten Status 1 und eine
Fehlermeldung; keine nicht beendeten Ergebnisse werden als Erfolg gedruckt.

```python
    try:
        results = run_pipeline(args.count, args.consumers, args.maxsize)
    except (TypeError, ValueError, RuntimeError) as error:
        print(f"Queue-Fehler: {error}", file=sys.stderr)
        return 1
```

**Zeilen 79-80:** Nummer, konsumierte Anzahl und Summe werden je
Consumer ausgegeben. Die Verteilung ist schedulingabhängig; ein Consumer
mit null Werten ist ein mögliches korrektes Ergebnis.

```python
    for index, result in enumerate(results, start=1):
        print(f"Consumer {index}: Anzahl={len(result.values)}; Summe={result.total}")
```

**Zeilen 81-82:** Die Einzelsummen werden addiert. Die Formel
`count*(count+1)//2` berechnet die bekannte Integer-Referenz für 1..count.
`//` ist Ganzzahldivision; das Produkt ist hier immer durch 2 teilbar.

```python
    total = sum(result.total for result in results)
    expected = args.count * (args.count + 1) // 2
```

**Zeilen 83-84:** Ein geschachtelter Generator flacht alle aufgezeichneten
Werte ab; Sortieren beseitigt nur die Verteilungsreihenfolge. Der Vergleich
mit der vollständigen erwarteten Integerliste erkennt jedes fehlende
oder doppelte Vorkommen, auch wenn die Gesamtsumme zufällig gleich wäre.

```python
    observed = sorted(value for result in results for value in result.values)
    exactly_once = observed == list(range(1, args.count + 1))
```

**Zeilen 85-87:** Summe, Referenz und genau-einmal-Ergebnis werden
angezeigt. Nur wenn beide Prüfungen erfolgreich sind, wird Status 0
zurückgegeben; andernfalls 1.

```python
    print(f"Gesamtsumme: {total}; erwartet: {expected}")
    print(f"Alle Werte genau einmal: {exactly_once}")
    return 0 if total == expected and exactly_once else 1
```

**Zeilen 90-91:** Der Startschutz macht Importtests ohne Start der
Pipeline möglich und liefert bei direktem Aufruf einen Shellstatus.

```python
if __name__ == "__main__":
    sys.exit(main())
```

### Änderungsübungen zu producer_consumer.py

1. Variiere maxsize zwischen 1, 2 und 8. Welche Größe hat der Puffer,
   welche Größen haben die Ergebnislisten? Begründe, warum begrenzte
   Queue nicht automatisch begrenzten Gesamtspeicher bedeutet.
2. Ändere count auf 0 bei fünf Consumern. Zähle auf Papier die fünf
   Sentinels und die nötigen task_done-Aufrufe; alle joins müssen enden.
3. Untersuche in einer Kopie, was ein fehlendes task_done oder nur ein
   Sentinel bewirkt. Starte solche Experimente ausschließlich mit einem
   Prozess-Timeout, damit die absichtlichen Hänger kontrolliert bleiben.

## `tests/support.py`

**Zeilen 1-6:** Auch die Testhilfe trägt die Kennzeichnung. Die Anfrage
verlangt echte CLI-Prozesse und lokale, automatisch aufgeräumte Testdateien.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 mit umfangreichen Standardbibliothek-Tests;
# lade die Aufgabenmodule und führe echte CLIs mit lokalen, aufgeräumten Testdateien aus.
```

**Zeile 8:** Der Docstring erläutert die zwei Besonderheiten: Punkt-
verzeichnisse werden direkt geladen und CLIs in separaten Prozessen ausgeführt.

```python
"""Testhilfen: Verzeichnisse mit Punkten laden und CLIs als eigene Prozesse starten."""
```

**Zeilen 10-15:** `importlib.util` lädt Python-Dateien nach Pfad, `os`
kopiert die Umgebung, `Path` bestimmt sichere lokale Ziele, `subprocess`
startet CLIs, `sys` nennt den Interpreter und `tempfile` räumt Testordner auf.

```python
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
```

**Zeilen 18-19:** Aus dem absoluten Hilfsdateipfad wird der Ordner ueb01
bestimmt. SCRATCH liegt ausdrücklich darunter, sodass Tests nicht außerhalb
des erlaubten Aufgabenordners ihre Testdaten anlegen.

```python
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / ".tmp"
```

**Zeilen 22-24:** Bereits unter dem gewünschten Namen geladene Module
werden wiederverwendet. Das verhindert mehrere auseinanderlaufende
Instanzen des gemeinsamen Rechenmoduls in einem Testprozess.

```python
def load_module(relative_path: str, module_name: str):
    if module_name in sys.modules:
        return sys.modules[module_name]
```

**Zeilen 25-27:** Eine Importspezifikation benennt Modul und Quelldatei.
Falls kein Loader verfügbar ist, führt die Hilfe zu einem ausdrücklichen
Importfehler statt zu einem später schwer erklärbaren Attributfehler.

```python
    specification = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    if specification is None or specification.loader is None:
        raise ImportError(f"Modul nicht ladbar: {relative_path}")
```

**Zeilen 28-31:** Das Modulobjekt wird erzeugt und vor der Ausführung
in `sys.modules` registriert, wie bei normalen Imports. Der Loader führt
die Definitionen aus und gibt das Modul zurück. Der normale Startschutz
verhindert dabei die CLI; Paketnamen mit `ue1.5` müssen nicht erfunden werden.

```python
    module = importlib.util.module_from_spec(specification)
    sys.modules[module_name] = module
    specification.loader.exec_module(module)
    return module
```

**Zeilen 34-36:** Der lokale Scratchordner wird bei Bedarf erzeugt.
TemporaryDirectory erstellt darin einen eindeutigen Testordner; die Tests
verwenden ihn im with-Kontext, der ihn einschließlich Inhalt wieder entfernt.
Die äußere .tmp bleibt als ignorierter Hilfsordner bestehen.

```python
def temporary_directory():
    SCRATCH.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=SCRATCH)
```

**Zeilen 39-41:** `*arguments` sammelt beliebig viele CLI-Argumente.
Eingabetext, cwd und Timeout haben testbare Standards. Die Prozessumgebung
wird kopiert, nicht global verändert. Die drei lokalen Variablen verhindern
Bytecodecache und legen UTF-8 für Ein-/Ausgabe und den Python-UTF-8-Modus fest.
Es werden keine Umgebungsgeheimnisse ausgegeben oder geändert.

```python
def run_cli(relative_path: str, *arguments, input_text=None, cwd=ROOT, timeout=20):
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
```

**Zeilen 42-43:** `subprocess.run` erhält eine Argumentliste, keine
Shell-Zeichenkette. Derselbe Interpreter wie der Testprozess startet die
absolute Programmdatei. Alle Argumente werden als einzelne Strings
weitergegeben; Leerzeichen und Unicode bleiben korrekt, ohne Shellauswertung.

```python
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / relative_path), *(str(arg) for arg in arguments)],
```

**Zeilen 44-47:** `input` speist optionale interaktive Daten ein.
capture_output sammelt stdout/stderr getrennt. `text=True` mit UTF-8
dekodiert die Prozessausgaben für verständliche Testvergleiche.

```python
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
```

**Zeilen 48-52:** cwd testet das reale Arbeitsverzeichnis, env isoliert
die genannten Einstellungen. Timeout macht hängende CLIs zu Ausnahmen.
`check=False` lässt beabsichtigte Fehlerstatuswerte als CompletedProcess
zurückkommen; die Tests müssen sie ausdrücklich prüfen. Die schließende
Klammer beendet den Aufruf, dessen Ergebnis direkt zurückgegeben wird.

```python
        cwd=cwd,
        env=environment,
        timeout=timeout,
        check=False,
    )
```

### Änderungsübungen zu support.py

1. Starte hello mit einem temporären cwd und vergleiche die Ausgabe.
   Erkläre den Unterschied zwischen absolutem Programmpfad und cwd.
2. Übergib `--name` und einen Namen mit Leerzeichen als getrennte
   Argumente. Begründe, weshalb keine Shellquotierung nötig ist.
3. Schreibe eine kurze Übung, die absichtlich länger als einen kleinen
   Timeout läuft. Prüfe `subprocess.TimeoutExpired`; verwende das nicht
   als zusätzliche Wartezeit in der eigentlichen Rechenaufgabe.

## `tests/test_11_hello.py`

**Zeilen 1-6:** Der KI-Kopf benennt die Tests für Fabio, reale Umgebung
und Grundlagen. Testcode unterliegt derselben Kennzeichnung wie die Programme.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.1 einschließlich echtem cwd, Fabio, Name-CLI und allen Sprachbeispielen.
```

**Zeilen 8-13:** contextlib lenkt Ausgabe vorübergehend um, io liefert
einen Speicher-Textstrom, Path beschreibt Testpfade, platform die laufende
Version, sys den venv-Status und unittest die Teststruktur. Damit werden
Erwartungen aus der echten Umgebung abgeleitet statt festgeschrieben.

```python
import contextlib
import io
from pathlib import Path
import platform
import sys
import unittest
```

**Zeilen 15-17:** Die gemeinsamen Hilfen werden importiert und hello
nach Dateipfad unter einem eigenen Modulnamen geladen. Der Startschutz
führt bei diesem Import nicht die CLI aus.

```python
from support import load_module, run_cli, temporary_directory

hello = load_module("ue1.1/hello.py", "ueb01_hello")
```

**Zeile 20:** HelloTests erbt TestCase. unittest findet darin die
test_-Methoden; self ermöglicht den Aufruf der Assertions dieser Basisklasse.

```python
class HelloTests(unittest.TestCase):
```

**Zeilen 21-24:** Für -100, 0 und 100 wird jeweils der passende
Text verlangt. subTest benennt den Zahlenfall. Die Werte prüfen alle
Entscheidungszweige und sind nicht nur die drei CLI-Demowerte.

```python
    def test_all_conditional_branches(self):
        for number, expected in [(-100, "negativ"), (0, "null"), (100, "positiv")]:
            with self.subTest(number=number):
                self.assertEqual(hello.classify_number(number), expected)
```

**Zeilen 26-30:** Die Demo wird aufgerufen. Eine Liste von Label/Typ-
Paaren prüft für jede Variable mit assertIs den exakt erwarteten Typ.
So könnte ein irrtümlicher Float statt Integer nicht als „ähnlich genug“ gelten.

```python
    def test_types_and_loop_results(self):
        result = hello.language_demo()
        for label, expected_type in [("int", int), ("float", float), ("bool", bool), ("str", str), ("list", list), ("dict", dict)]:
            with self.subTest(label=label):
                self.assertIs(type(result[label]), expected_type)
```

**Zeilen 31-33:** None wird ausdrücklich erkannt. Die komplette
Nummerierung und der Countdown werden mit festen Ergebnissen verglichen;
das prüft die tatsächliche Wirkung der for- und while-Schleife.

```python
        self.assertIsNone(result["NoneType"])
        self.assertEqual(result["dict"], {1: "Text", 2: "Bytes", 3: "Threads"})
        self.assertEqual(result["while-Ergebnis"], [3, 2, 1])
```

**Zeilen 35-42:** Ein temporärer Ordner wird echtes Prozess-cwd.
Der CLI-Prozess muss erfolgreich sein und Fabio, laufende Python-Version,
diesen Ordner und den tatsächlichen venv-Status zeigen. Die stderr-Ausgabe
dient bei falschem Status als Assertionmeldung. Der Test erkennt daher
ein irrtümlich festgeschriebenes Arbeitsverzeichnis.

```python
    def test_default_name_version_and_actual_cwd(self):
        with temporary_directory() as directory:
            process = run_cli("ue1.1/hello.py", cwd=directory)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("Name: Fabio", process.stdout)
            self.assertIn(f"Python-Version: {platform.python_version()}", process.stdout)
            self.assertIn(f"Arbeitsverzeichnis: {Path(directory)}", process.stdout)
            self.assertIn(f"Virtuelle Umgebung: {sys.prefix != sys.base_prefix}", process.stdout)
```

**Zeilen 44-47:** Ein Name mit Unicode und Leerzeichen wird als ein
Argument übergeben. Erfolg und vollständige Name-Ausgabe beweisen,
dass --name den Standard ersetzt und das Argument nicht zerlegt wurde.

```python
    def test_name_override(self):
        process = run_cli("ue1.1/hello.py", "--name", "Fabio Grüß")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Name: Fabio Grüß", process.stdout)
```

**Zeilen 49-53:** StringIO sammelt Ausgabe im selben Prozess.
redirect_stdout gilt nur im with-Block. Der direkte main-Aufruf muss 0
liefern und den gewählten Namen zeigen; damit wird auch die API-Rückgabe geprüft.

```python
    def test_main_return_value(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(hello.main(["--name", "Test"]), 0)
        self.assertIn("Name: Test", output.getvalue())
```

**Zeilen 55-58:** Der echte Hilfeaufruf muss 0 liefern und --name
erwähnen. So ist die CLI selbstbeschreibend und Hilfe kein Fehlerfall.

```python
    def test_help(self):
        process = run_cli("ue1.1/hello.py", "--help")
        self.assertEqual(process.returncode, 0)
        self.assertIn("--name", process.stdout)
```

**Zeilen 60-63:** Ein unbekanntes Argument muss Status 2 und eine
nichtleere stderr-Meldung erzeugen. Es darf nicht stillschweigend akzeptiert werden.

```python
    def test_unknown_argument(self):
        process = run_cli("ue1.1/hello.py", "--unknown")
        self.assertEqual(process.returncode, 2)
        self.assertTrue(process.stderr)
```

**Zeilen 66-67:** unittest.main startet die Datei bei direktem Aufruf.
Bei Testdiscovery wird der Block nicht ausgeführt; die Klassen werden dort
vom übergeordneten Testlauf gesammelt.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_11_hello.py

1. Erweitere die bedingten Tests um -1 und 1. Alle Fälle müssen weiter
   laufen, auch wenn ein subTest scheitert.
2. Ändere in einer Kopie den CLI-Standardnamen und beobachte genau,
   welcher Test die Änderung bemerkt. Halte die Fabio-Vorgabe der Lösung ein.

## `tests/test_12_text_bytes.py`

**Zeilen 1-6:** Die Kennzeichnung nennt Unicode, Längen, Eingabe und
Fehlkodierungen als konkrete Testanfrage.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.2 mit Unicode, Eingabe/CLI, Längen, Roundtrip und falschen Kodierungen.
```

**Zeilen 8-12:** unittest liefert Assertions, die Hilfe lädt das
Modul und startet CLIs. Das geladene Modul wird unter einem eindeutigen
Namen gehalten, damit seine Funktionen direkt geprüft werden können.

```python
import unittest

from support import load_module, run_cli

text_bytes = load_module("ue1.2/text_bytes.py", "ueb01_text_bytes")
```

**Zeile 15:** Die TestCase-Klasse sammelt die zwölf Methoden für
Text-/Byteverhalten und CLI-Fehler.

```python
class TextBytesTests(unittest.TestCase):
```

**Zeilen 16-20:** Feste UTF-8-Vektoren umfassen Leertext, ASCII, Umlaut,
Vier-Byte-Emoji und kombinierenden Akzent. Jeder Text erhält einen subTest
und wird durch die echte Funktion in data/decoded umgewandelt. Die
erwarteten Bytes sind ausdrücklich festgelegt, nicht vom Erzeuger berechnet.

```python
    def test_fixed_utf8_vectors_and_roundtrip(self):
        vectors = [("", b""), ("ABC", b"ABC"), ("ä", b"\xc3\xa4"), ("🌍", b"\xf0\x9f\x8c\x8d"), ("e\u0301", b"e\xcc\x81")]
        for text, expected in vectors:
            with self.subTest(text=text):
                data, decoded = text_bytes.encode_and_decode(text)
```

**Zeilen 21-24:** Typen müssen genau bytes/str sein, Bytes dem Vektor
entsprechen und zurückgegebener Text dem Original. Alle drei Eigenschaften
sind nötig: Nur ein erfolgreicher Rückvergleich würde falsche Kodierung
im Hinweg nicht unabhängig erkennen.

```python
                self.assertIs(type(data), bytes)
                self.assertIs(type(decoded), str)
                self.assertEqual(data, expected)
                self.assertEqual(decoded, text)
```

**Zeilen 26-30:** Ein Text mit Han-Zeichen, Zeilenumbruch, Nullzeichen,
Umlauten und Emoji wird verlustfrei zurückgewandelt. Seine Byteanzahl muss
größer als die Codepointanzahl sein, was die Unterscheidung praktisch prüft.

```python
    def test_nonlatin_and_embedded_newlines(self):
        text = "漢字\nGrüße\x00🌍"
        data, decoded = text_bytes.encode_and_decode(text)
        self.assertEqual(decoded, text)
        self.assertGreater(len(data), len(text))
```

**Zeilen 32-35:** Bytes, None, Zahl und bool sind keine Texteingaben.
Die zwei with-Kontexte benennen den Fall und verlangen TypeError für
jeden Wert; eine automatische, unerwünschte Stringumwandlung würde scheitern.

```python
    def test_rejects_non_string(self):
        for value in [b"abc", None, 123, True]:
            with self.subTest(value=value), self.assertRaises(TypeError):
                text_bytes.encode_and_decode(value)
```

**Zeilen 37-39:** Ein isolierter Surrogat-Codepoint ist nicht gültig
UTF-8-kodierbar. Der Test verlangt UnicodeEncodeError statt stiller
Ersetzung; das prüft den strikten Encodepfad der API.

```python
    def test_unpaired_surrogate_is_rejected(self):
        with self.assertRaises(UnicodeEncodeError):
            text_bytes.encode_and_decode("\ud800")
```

**Zeilen 41-46:** Die echte CLI verarbeitet Grüße/Emoji. Erfolg,
7 Codepoints, 12 Bytes und True-Roundtrip werden explizit verlangt.
Diese festen Zahlen sind ein unabhängiger Unicode-Referenzfall.

```python
    def test_unicode_cli(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "Grüße 🌍")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Unicode-Codepoints: 7", process.stdout)
        self.assertIn("len(bytes), Bytes: 12", process.stdout)
        self.assertIn("Roundtrip identisch: True", process.stdout)
```

**Zeilen 48-51:** Ohne --text erhält der Prozess eine echte Eingabezeile
über stdin. Die Ausgabe muss den Umlauttext enthalten und Status 0 liefern;
somit wurde der input-Pfad und nicht bloß die CLI-Option geprüft.

```python
    def test_interactive_input(self):
        process = run_cli("ue1.2/text_bytes.py", input_text="Netzwerk ä\n")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Netzwerk ä", process.stdout)
```

**Zeilen 53-56:** Ein ausdrücklich leeres --text ist gültig und muss
0 Bytes ergeben. Würde der Code Wahrheit statt None prüfen, würde er
unbeabsichtigt nach interaktiver Eingabe verlangen und dieser Test fehlschlagen.

```python
    def test_explicit_empty_text_does_not_prompt(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("len(bytes), Bytes: 0", process.stdout)
```

**Zeilen 58-61:** Leeres stdin ohne --text erzeugt EOF. Erwartet werden
Status 1 und die Eingabefehlermeldung; kein unkontrollierter Traceback.

```python
    def test_eof_is_reported(self):
        process = run_cli("ue1.2/text_bytes.py", input_text="")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Eingabe-/Kodierungsfehler", process.stderr)
```

**Zeilen 63-67:** UTF-8-Bytes von ä werden zusätzlich als Latin-1
dekodiert. Der Prozess kann korrekt laufen, obwohl das Ergebnis Ã¤ und
der zweite Identitätsvergleich False sind. Mojibake wird getrennt von
einem eigentlichen Dekodierungsfehler geprüft.

```python
    def test_latin1_produces_mojibake(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "ä", "--decode-as", "latin-1")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Dekodiert mit latin-1: 'Ã¤'", process.stdout)
        self.assertIn("Auch damit identisch: False", process.stdout)
```

**Zeilen 69-72:** ASCII kann die Umlautbytes nicht dekodieren.
Status 1 und die konkrete ASCII-Fehlermeldung belegen den anderen möglichen
Ausgang einer falschen Kodierungswahl.

```python
    def test_ascii_cannot_decode_umlaut(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "ä", "--decode-as", "ascii")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Dekodierungsfehler (ascii)", process.stderr)
```

**Zeilen 74-77:** Ein unbekannter Kodierungsname muss ebenfalls sauber
als Fehler gemeldet werden. Das prüft LookupError neben UnicodeDecodeError.

```python
    def test_unknown_encoding_is_reported(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "x", "--decode-as", "no-such-encoding")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Dekodierungsfehler", process.stderr)
```

**Zeilen 79-81:** --text ohne zugehörigen Optionswert ist CLI-Syntaxfehler
und muss vor Texteingabe/Umwandlung mit Status 2 beendet werden.

```python
    def test_missing_text_option_value(self):
        process = run_cli("ue1.2/text_bytes.py", "--text")
        self.assertEqual(process.returncode, 2)
```

**Zeilen 84-85:** Der Startschutz erlaubt die separate Ausführung
dieser Testdatei, ohne beim Import einen zweiten Testlauf zu starten.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_12_text_bytes.py

1. Ergänze den festen Vektor für ß mit den Bytes c3 9f. Begründe,
   weshalb encode() zur Berechnung des Erwartungswerts hier schwächer wäre.
2. Vergleiche vorgefertigtes é und e plus Akzent. Beide können gleich
   aussehen, haben aber ohne Normalisierung unterschiedliche Codepoints.

## `tests/test_13_convert.py`

**Zeilen 1-6:** Der Kopf nennt tatsächliche ZIP- und CLI-Rechteprüfungen
sowie ausdrücklich benannte Mocks. Er trennt damit bereits die Beweisarten.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.3 mit Original-ZIP, echten CLI-/Permission-Fehlern und klar bezeichneten Mocks.
```

**Zeilen 8-14:** contextlib/io sammeln Meldungen und erzeugen einen
kontrollierten Textstrom. os prüft reale Zugriffsrechte, Path verwaltet
Dateien, unittest Assertions, mock ersetzt gezielt open und ZipFile liest
die Originaldateien. Keine dieser Hilfen installiert Zusatzpakete.

```python
import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest import mock
from zipfile import ZipFile
```

**Zeilen 16-18:** ROOT benennt ueb01. Lade-, CLI- und Temp-Hilfen werden
importiert und die Konvertierung als API geladen.

```python
from support import ROOT, load_module, run_cli, temporary_directory

convert = load_module("ue1.3/convert.py", "ueb01_convert")
```

**Zeile 21:** ConvertTests fasst alle 17 Testmethoden zusammen.
Dateirechte werden nur innerhalb lokaler temporärer Testordner verändert.

```python
class ConvertTests(unittest.TestCase):
```

**Zeilen 22-26:** Das echte ZIP und ein Tempordner werden im with
geöffnet. Die Mitgliedsnamen müssen exakt file1/file2 sein. Jeder
Archivtext wird in einem eigenen subTest verarbeitet, damit keiner entfällt.

```python
    def test_actual_zip_members_via_cli(self):
        with ZipFile(ROOT / "Angabe/utf8files.zip") as archive, temporary_directory() as directory:
            self.assertEqual(set(archive.namelist()), {"file1.txt", "file2.txt"})
            for name in archive.namelist():
                with self.subTest(member=name):
```

**Zeilen 27-31:** Die Originalbytes werden aus dem Archiv gelesen,
unter einem temporären Quellpfad gespeichert und an die echte CLI übergeben.
Das Ziel ist eine andere lokale Datei; Originale in Angabe bleiben unangetastet.

```python
                    original = archive.read(name)
                    source = Path(directory) / name
                    target = Path(directory) / (name + ".out")
                    source.write_bytes(original)
                    process = run_cli("ue1.3/convert.py", source, target)
```

**Zeilen 32-36:** Status 0 ist erforderlich. Die unabhängige Byte-
Normalisierung ersetzt erst CRLF, dann CR, damit nicht zwei LF entstehen.
Ausgabe muss diesem Referenzinhalt entsprechen; Quelle und schon vorhandene
Angabe-Datei müssen exakt die originalen Archivbytes enthalten.

```python
                    self.assertEqual(process.returncode, 0, process.stderr)
                    expected = original.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                    self.assertEqual(target.read_bytes(), expected)
                    self.assertEqual(source.read_bytes(), original)
                    self.assertEqual((ROOT / "Angabe" / name).read_bytes(), original)
```

**Zeilen 38-44:** Eine UTF-8-Quelle kombiniert CRLF, CR, LF und Emoji.
Der direkte API-Aufruf muss exakt LF-normalisierte Bytes und Länge 9
Codepoints liefern. Dies ergänzt die ZIP-Dateien, die bereits LF verwenden.

```python
    def test_mixed_line_endings_and_unicode(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes("ä\r\nb\rc\nd\r\n🌍".encode("utf-8"))
            count = convert.convert_file(source, target)
            self.assertEqual(target.read_bytes(), "ä\nb\nc\nd\n🌍".encode("utf-8"))
            self.assertEqual(count, 9)
```

**Zeilen 46-51:** Eine leere Quelldatei muss eine wirklich leere Ausgabe
erzeugen und 0 liefern. Leere Textdateien sind hier gültig, anders als
die Protokollpayload in 1.4.

```python
    def test_empty_file(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"")
            self.assertEqual(convert.convert_file(source, target), 0)
            self.assertEqual(target.read_bytes(), b"")
```

**Zeilen 53-59:** Das Ziel enthält absichtlich längeren alten Text.
Nach dem Konvertieren muss dort ausschließlich new stehen, ohne Restbytes.
Damit ist der dokumentierte Ersetzungsmodus w tatsächlich überprüft.

```python
    def test_existing_output_is_replaced(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"new")
            target.write_bytes(b"old longer text")
            convert.convert_file(source, target)
            self.assertEqual(target.read_bytes(), b"new")
```

**Zeilen 61-69:** Quelle enthält ungültiges UTF-8, Ziel einen Marker.
Die echte CLI muss Status 1 und die spezifische Meldung liefern;
der Marker muss erhalten bleiben. Das prüft die Reihenfolge erst lesen,
dann Ausgabe öffnen, nicht nur das Auftreten irgendeiner Ausnahme.

```python
    def test_invalid_utf8_preserves_existing_output(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"\xff\r\n")
            target.write_bytes(b"must stay intact")
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertIn("Ungültiges UTF-8", process.stderr)
            self.assertEqual(target.read_bytes(), b"must stay intact")
```

**Zeilen 71-77:** Eine nicht existierende Quelle wird an die CLI gegeben.
Status 1 und Dateifehlermeldung sind erforderlich, die Ausgabe darf
überhaupt nicht entstehen. Der Fehler wird also nicht als leere Quelle behandelt.

```python
    def test_missing_input_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "missing", Path(directory) / "out"
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertIn("Dateifehler", process.stderr)
            self.assertFalse(target.exists())
```

**Zeilen 79-86:** Quelle und Ziel sind derselbe Pfad. Die CLI muss die
Identität ablehnen, verschieden melden und sämtliche ursprünglichen
CRLF-Bytes unverändert lassen. Der Schutz wird vor Trunkierung nachgewiesen.

```python
    def test_same_path_cli_is_safe(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"preserved\r\n")
            process = run_cli("ue1.3/convert.py", source, source)
            self.assertEqual(process.returncode, 1)
            self.assertIn("verschieden", process.stderr)
            self.assertEqual(source.read_bytes(), b"preserved\r\n")
```

**Zeilen 88-93:** Eine echte Quelle und ein symbolischer Link darauf
werden angelegt. Der Link verweist auf denselben Inhalt unter anderem Namen,
wodurch ein bloßer Stringvergleich der Pfade nicht ausreichen würde.

```python
    def test_symlink_to_input_is_rejected(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "link"
            source.write_bytes(b"unchanged")
            try:
                target.symlink_to(source)
```

**Zeilen 94-98:** Unterstützt das System keine Links, wird ausdrücklich
übersprungen. Andernfalls wird ValueError verlangt und die unveränderte
Quelle geprüft. Ein übersprungener Test ist keine behauptete bestandene Linkprüfung.

```python
            except OSError as error:
                self.skipTest(f"Symlinks hier nicht möglich: {error}")
            with self.assertRaises(ValueError):
                convert.convert_file(source, target)
            self.assertEqual(source.read_bytes(), b"unchanged")
```

**Zeilen 100-105:** Ein echter Hardlink auf die Quelle wird erzeugt.
Er hat denselben Datei-Inode, obwohl resolve verschiedene Namen liefern kann.
Diese Vorbereitung prüft deshalb den zusätzlichen samefile-Pfad.

```python
    def test_hardlink_to_input_is_rejected(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "hardlink"
            source.write_bytes(b"unchanged")
            try:
                target.hardlink_to(source)
```

**Zeilen 106-110:** Fehlende Hardlink-Unterstützung wird explizit als
Skip gemeldet. Sonst wird die echte CLI gestartet; Status 1 und unveränderte
Quelldaten belegen die sichere Ablehnung auch ohne Symlinkauflösung.

```python
            except OSError as error:
                self.skipTest(f"Hardlinks hier nicht möglich: {error}")
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertEqual(source.read_bytes(), b"unchanged")
```

**Zeilen 112-118:** Eine gültige Quelle, aber fehlender Ziel-Elternordner
müssen Status 1 und Dateifehler auslösen. Die CLI erzeugt keine unvereinbarten
Verzeichnisse und behauptet keinen erfolgreichen Schreibvorgang.

```python
    def test_missing_output_parent_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"abc")
            process = run_cli("ue1.3/convert.py", source, Path(directory) / "missing/out")
            self.assertEqual(process.returncode, 1)
            self.assertIn("Dateifehler", process.stderr)
```

**Zeilen 120-127:** Ein Verzeichnis wird einmal als Quelle, einmal als
Ziel übergeben. Eigene subTests verlangen jeweils Status 1; Verzeichnisse
dürfen nicht als normale Textdateien verarbeitet werden.

```python
    def test_directories_are_not_text_files_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"abc")
            for infile, outfile in [(directory, source), (source, directory)]:
                with self.subTest(infile=infile):
                    process = run_cli("ue1.3/convert.py", infile, outfile)
                    self.assertEqual(process.returncode, 1)
```

**Zeilen 129-134:** Null, ein und drei Argumente werden getestet.
Alle müssen mit Status 2 und stderr scheitern, weil genau zwei erforderlich
sind. So wird CLI-Prüfung von späteren Dateifehlern unterschieden.

```python
    def test_missing_and_extra_parameters(self):
        for arguments in [(), ("in",), ("in", "out", "extra")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.3/convert.py", *arguments)
                self.assertEqual(process.returncode, 2)
                self.assertTrue(process.stderr)
```

**Zeilen 136-140:** Eine reale temporäre Quelle wird erzeugt und ihre
Rechte auf 000 gesetzt. Danach beginnt ein try/finally, damit die Rechte
auch bei Testfehler oder Skip für die Bereinigung wiederhergestellt werden.

```python
    def test_real_unreadable_input_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"abc")
            source.chmod(0o000)
```

**Zeilen 141-147:** os.access prüft, ob der aktuelle Benutzer die
Sperre wirklich erfährt. Falls nicht, wird ehrlich übersprungen. Andernfalls
läuft eine echte CLI; Status 1, Dateifehler und fehlende Ausgabe zeigen
tatsächliches verweigertes Lesen. Hier wurde dieser Pfad unter UID 1000 ausgeführt.

```python
            try:
                if os.access(source, os.R_OK):
                    self.skipTest("Dieser Benutzer kann chmod(000)-Dateien trotzdem lesen.")
                process = run_cli("ue1.3/convert.py", source, target)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Dateifehler", process.stderr)
                self.assertFalse(target.exists())
```

**Zeilen 148-149:** finally setzt auf 600 zurück, damit der Tempordner
ohne Rechteprobleme aufgeräumt werden kann. Dies verändert keine Originaldatei.

```python
            finally:
                source.chmod(0o600)
```

**Zeilen 151-156:** Gültige Quelle und vorhandenes Marker-Ziel werden
angelegt. Die Ausgabe wird mit 400 schreibgeschützt; try eröffnet wiederum
die unabhängig vom Testergebnis garantierte Rechtewiederherstellung.

```python
    def test_real_unwritable_output_file_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"new")
            target.write_bytes(b"preserved")
            target.chmod(0o400)
```

**Zeilen 157-162:** Privilegierter Schreibzugriff wird als Skip behandelt.
Sonst muss die tatsächliche CLI mit Status 1 scheitern und der ursprüngliche
Marker erhalten bleiben. Geprüft wird eine bestehende nicht schreibbare Datei.

```python
            try:
                if os.access(target, os.W_OK):
                    self.skipTest("Dieser Benutzer kann chmod(400)-Dateien trotzdem schreiben.")
                process = run_cli("ue1.3/convert.py", source, target)
                self.assertEqual(process.returncode, 1)
                self.assertEqual(target.read_bytes(), b"preserved")
```

**Zeilen 163-164:** Der Zielmodus wird im finally auf 600 zurückgesetzt,
damit Aufräumen und Folgetests nicht durch den Rechteversuch beeinträchtigt werden.

```python
            finally:
                target.chmod(0o600)
```

**Zeilen 166-171:** Eine gültige Quelle und ein echter Zielordner werden
angelegt. 500 erlaubt Lesen/Betreten, aber kein Erzeugen einer Datei im
Ordner. try garantiert auch für diesen Versuch die spätere Freigabe.

```python
    def test_real_unwritable_output_directory_cli(self):
        with temporary_directory() as directory:
            source, parent = Path(directory) / "in", Path(directory) / "readonly"
            source.write_bytes(b"abc")
            parent.mkdir()
            parent.chmod(0o500)
```

**Zeilen 172-177:** Falls Rechte umgangen werden können, meldet der Test
Skip. Andernfalls müssen CLI-Status 1 und nicht erzeugtes Ziel bestätigt
werden. Dieser Fall unterscheidet neue Ausgabe im geschützten Ordner vom
zuvor getesteten schreibgeschützten bestehenden Ziel.

```python
            try:
                if os.access(parent, os.W_OK):
                    self.skipTest("Dieser Benutzer kann im chmod(500)-Ordner trotzdem schreiben.")
                process = run_cli("ue1.3/convert.py", source, parent / "out")
                self.assertEqual(process.returncode, 1)
                self.assertFalse((parent / "out").exists())
```

**Zeilen 178-179:** finally gibt dem lokalen Ordner mit 700 wieder
alle Eigentümerrechte, sodass er zuverlässig gelöscht werden kann.

```python
            finally:
                parent.chmod(0o700)
```

**Zeilen 181-187:** Dieser Test ist ausdrücklich ein Mock. Path.open
wird nur im with-Block durch einen PermissionError mit MOCK-Marker ersetzt.
stderr wird erfasst, main direkt aufgerufen und Status 1 samt Marker verlangt.
Die Rechte des Betriebssystems werden dadurch nicht gemessen; die
Fehlerübersetzung wird kontrolliert geprüft und danach automatisch restauriert.

```python
    def test_controlled_mock_read_permission_error(self):
        error_output = io.StringIO()
        with mock.patch.object(Path, "open", side_effect=PermissionError("MOCK: Lesen verweigert")):
            with contextlib.redirect_stderr(error_output):
                result = convert.main(["mock-in", "mock-out"])
        self.assertEqual(result, 1)
        self.assertIn("MOCK: Lesen verweigert", error_output.getvalue())
```

**Zeilen 189-194:** Der zweite Mock gibt zuerst einen StringIO-
Eingabestrom zurück, dann einen Schreib-PermissionError. Der CLI-Einstieg
wird direkt aufgerufen; redirect_stderr sammelt seine Meldung. Die Folge
in side_effect simuliert getrennt gelungenes Lesen und verweigertes Schreiben.

```python
    def test_controlled_mock_write_error_closes_input(self):
        input_stream = io.StringIO("gültiger Text\n")
        error_output = io.StringIO()
        with mock.patch.object(Path, "open", side_effect=[input_stream, PermissionError("MOCK: Schreiben verweigert")]):
            with contextlib.redirect_stderr(error_output):
                result = convert.main(["mock-in", "mock-out"])
```

**Zeilen 195-197:** Status 1 und der MOCK-Marker sind erforderlich.
Zusätzlich muss der Eingabestrom closed sein, obwohl Schreiben scheitert:
Die with-Ressourcenverwaltung wird damit unabhängig vom Betriebssystem geprüft.

```python
        self.assertEqual(result, 1)
        self.assertTrue(input_stream.closed)
        self.assertIn("MOCK: Schreiben verweigert", error_output.getvalue())
```

**Zeilen 200-201:** Bei direktem Start führt unittest.main genau diese
Datei aus; Discovery übernimmt die Klasse ohne diesen zusätzlichen Start.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_13_convert.py

1. Ergänze eine CRLF-Datei ohne letzten Zeilenumbruch; die Ausgabe darf
   keinen zusätzlichen LF bekommen. Vergleiche Bytes statt nur angezeigten Text.
2. Erkläre das ehrliche Skip-Verhalten für root. Ersetze es nicht durch
   ein pauschales „Permissiontest bestanden“; ein Mock bleibt separat.
3. Ändere in einer Kopie die Reihenfolge des Öffnens und beobachte den
   fehlschlagenden Marker-Test bei ungültigem UTF-8. Stelle den Schutz wieder her.

## `tests/test_14_protocol.py`

**Zeilen 1-6:** Die Kennzeichnung nennt unabhängige Binärvektoren,
Flags, Grenzen und negative Parserfälle als konkreten Testauftrag.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.4 gegen feste Binärvektoren, alle Flags, Grenzen und ungültige Nachrichten.
```

**Zeilen 8-12:** itertools erzeugt systematisch Kombinationen,
unittest prüft sie und mock ermöglicht einen ausdrücklich begrenzten
Längengrenzen-Test. Die Testhilfe lädt die API und startet echte CLIs.

```python
import itertools
import unittest
from unittest import mock

from support import load_module, run_cli
```

**Zeilen 14-15:** Das Protokollmodul wird geladen. CANONICAL ist der
feste Hexvektor aus dem Arbeitsauftrag, ausdrücklich nicht durch
create_message erzeugt. Er liefert eine unabhängige Referenz für den Defaultfall.

```python
protocol = load_module("ue1.4/protocol.py", "ueb01_protocol")
CANONICAL = bytes.fromhex("10 00 00 2a 00 00 00 05 68 65 6c 6c 6f")
```

**Zeile 18:** Die Klasse enthält 18 Testmethoden einschließlich vieler
Subfälle. Der Parser wird auch mit Nachrichten geprüft, die nie vom
gültigen Erzeuger stammen können.

```python
class ProtocolTests(unittest.TestCase):
```

**Zeilen 19-25:** Vier festgeschriebene Feld/Hex-Paare decken alle
Flagkombinationen ab. Sequenzen 1, 42, 256 und 65535 machen sowohl kleine
als auch hohe Bytewerte sichtbar; Null-/ff-Payload prüft echte binäre Daten.

```python
    def test_independently_specified_binary_vectors(self):
        vectors = [
            ((False, False, 42, b"hello"), "10 00 00 2a 00 00 00 05 68 65 6c 6c 6f"),
            ((False, True, 1, b"x"), "10 01 00 01 00 00 00 01 78"),
            ((True, False, 256, b"x"), "10 02 01 00 00 00 00 01 78"),
            ((True, True, 65535, b"\x00\xff"), "10 03 ff ff 00 00 00 02 00 ff"),
        ]
```

**Zeilen 26-30:** Jeder Vektor erhält einen subTest. fromhex liest nur
die unabhängige Konstante. Erzeugung muss genau diese Bytes liefern und
Parsen derselben Konstante die ursprünglichen Felder. Ein gemeinsam falsch
implementierter Erzeuger/Parser würde daher nicht allein durch Roundtrip bestehen.

```python
        for fields, hexadecimal in vectors:
            with self.subTest(fields=fields):
                expected = bytes.fromhex(hexadecimal)
                self.assertEqual(protocol.create_message(*fields), expected)
                self.assertEqual(protocol.parse_message(expected), fields)
```

**Zeilen 32-37:** itertools.product bildet 2*2*3*3 = 36 Kombinationen
aus Flags, gültigen Sequenzgrenzen und drei Payloads. Das Feldtuple wird
als subTest-Kontext gespeichert; kein kombinatorischer Fall wird ausgelassen.

```python
    def test_all_flags_bounds_and_binary_payloads_roundtrip(self):
        for is_data, is_urgent, sequence, payload in itertools.product(
            (False, True), (False, True), (1, 42, 65535), (b"\x00", b"\x00\xffabc", "ä🌍".encode("utf-8"))
        ):
            fields = (is_data, is_urgent, sequence, payload)
            with self.subTest(fields=fields):
```

**Zeilen 38-44:** Jede Kombination wird erzeugt und geparst. Verlangt
werden ursprüngliche Felder, echte bool-Rückgaben, exakt 8 plus Byteanzahl
Gesamtlänge und identische erneute Serialisierung. So werden API-, Struktur-
und Roundtrip-Eigenschaften gemeinsam geprüft.

```python
                message = protocol.create_message(*fields)
                parsed = protocol.parse_message(message)
                self.assertEqual(parsed, fields)
                self.assertIs(type(parsed.is_data), bool)
                self.assertIs(type(parsed.is_urgent), bool)
                self.assertEqual(len(message), 8 + len(payload))
                self.assertEqual(protocol.create_message(*parsed), message)
```

**Zeilen 46-50:** Beide Flagpositionen werden separat mit Integern,
None, Text, Liste und Float gefüttert. TypeError ist für jeden Fall
erforderlich; auch 0/1 dürfen keine scheinbaren bool-Ersatzwerte sein.

```python
    def test_strict_flag_types(self):
        for bad in [0, 1, None, "True", [], 1.0]:
            for flags in [(bad, True), (False, bad)]:
                with self.subTest(flags=flags), self.assertRaises(TypeError):
                    protocol.create_message(*flags, 1, b"x")
```

**Zeilen 52-55:** Bool, None, Text und Float werden als Sequenz
zurückgewiesen. Dies prüft besonders die bool/int-Unterklassenfalle.

```python
    def test_strict_sequence_types(self):
        for bad in [True, False, None, "1", 1.0]:
            with self.subTest(sequence=bad), self.assertRaises(TypeError):
                protocol.create_message(False, False, bad, b"x")
```

**Zeilen 57-60:** -1, 0, 65536 und ein riesiger Integer sind echte
Integer, aber ungültige Werte. Deshalb verlangt der Test ValueError und
legt damit die positive unsigned16-Grenze unabhängig fest.

```python
    def test_positive_uint16_boundaries(self):
        for bad in [-1, 0, 65536, 2**80]:
            with self.subTest(sequence=bad), self.assertRaises(ValueError):
                protocol.create_message(False, False, bad, b"x")
```

**Zeilen 62-67:** Text, Bytearray, Memoryview, None und Integer bekommen
TypeError als Payload. Echte, aber leere Bytes bekommen separat ValueError.
Typfehler und Inhaltsfehler werden damit nicht vermischt.

```python
    def test_payload_types_and_empty_payload(self):
        for bad in ["x", bytearray(b"x"), memoryview(b"x"), None, 1]:
            with self.subTest(payload=bad), self.assertRaises(TypeError):
                protocol.create_message(False, False, 1, bad)
        with self.assertRaises(ValueError):
            protocol.create_message(False, False, 1, b"")
```

**Zeilen 69-72:** Ein kontrollierter Mock setzt die Maximalgrenze auf 2;
die Payload abc muss daran scheitern. Nach dem with gilt wieder uint32-Maximum.
Das prüft den Grenzpfad ohne behauptete oder tatsächlich teure 4-GiB-Allokation.

```python
    def test_uint32_length_guard_with_controlled_small_limit(self):
        with mock.patch.object(protocol, "MAX_PAYLOAD_LENGTH", 2):
            with self.assertRaises(ValueError):
                protocol.create_message(False, False, 1, b"abc")
```

**Zeilen 74-77:** Auch der Parser verlangt echte bytes. Text, None,
Bytearray, Memoryview und Zahl müssen TypeError erzeugen statt implizit
umgewandelt zu werden.

```python
    def test_parser_types(self):
        for bad in ["message", None, bytearray(CANONICAL), memoryview(CANONICAL), 123]:
            with self.subTest(message=bad), self.assertRaises(TypeError):
                protocol.parse_message(bad)
```

**Zeilen 79-82:** Alle Headerpräfixe der Längen 0..7 werden tatsächlich
geparst und müssen ValueError liefern. So wird nicht nur ein einziger
zufällig kurzer Header geprüft.

```python
    def test_all_truncated_header_lengths(self):
        for length in range(8):
            with self.subTest(length=length), self.assertRaises(ValueError):
                protocol.parse_message(CANONICAL[:length])
```

**Zeilen 84-88:** Versionen 0,1,3,31 werden direkt als neues erstes
Wort kodiert; der restliche gültige Vektor bleibt erhalten. Parser muss
ausdrücklich wegen Versionsnummer ablehnen. Die Mutation isoliert diesen Fehler.

```python
    def test_wrong_versions(self):
        for version in [0, 1, 3, 31]:
            message = (version << 11).to_bytes(2, "big") + CANONICAL[2:]
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "Versionsnummer"):
                protocol.parse_message(message)
```

**Zeilen 90-96:** Für jedes lokale Bit 2..10 wird eine Bytearray-Kopie
des Referenzvektors erstellt. Niedrige Bits werden im zweiten, höhere
im ersten Byte gesetzt; bit modulo 8 bestimmt die Byteposition.
Nach Rückwandlung zu bytes muss jede der neun Änderungen wegen Reserved
scheitern. `|=` setzt das Bit, ohne andere ursprüngliche Bits zu löschen.

```python
    def test_each_of_nine_reserved_bits(self):
        for bit in range(2, 11):
            message = bytearray(CANONICAL)
            byte_index = 1 if bit < 8 else 0
            message[byte_index] |= 1 << (bit % 8)
            with self.subTest(bit=bit), self.assertRaisesRegex(ValueError, "Reservierte"):
                protocol.parse_message(bytes(message))
```

**Zeilen 98-101:** Nur die beiden Sequenzbytes werden durch Null
ersetzt. Der Parser muss die 1..65535-Regel anwenden, obwohl das Binärfeld
0 technisch darstellen kann.

```python
    def test_parser_rejects_zero_sequence(self):
        message = CANONICAL[:2] + b"\x00\x00" + CANONICAL[4:]
        with self.assertRaisesRegex(ValueError, "1..65535"):
            protocol.parse_message(message)
```

**Zeilen 103-107:** Deklarierte Payloadlänge wird 0, einmal ohne und
einmal mit angehängten Daten. Beide müssen ausdrücklich wegen leerer
deklarierter Payload verworfen werden; zusätzliche Bytes heilen kein Nullfeld.

```python
    def test_zero_payload_length_with_and_without_data(self):
        for payload in [b"", b"hello"]:
            message = CANONICAL[:4] + b"\x00\x00\x00\x00" + payload
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "nicht leer"):
                protocol.parse_message(message)
```

**Zeilen 109-113:** Längen 1,4,6 und uint32-Maximum werden direkt
eingeschrieben, während tatsächlich fünf Bytes vorhanden sind.
ValueError mit Payload-Längenmeldung ist erforderlich. Der große deklarierte
Wert darf den Parser nicht zum Reservieren riesigen Speichers veranlassen.

```python
    def test_length_mismatch_small_and_uint32_max(self):
        for claimed_length in [1, 4, 6, 4294967295]:
            message = CANONICAL[:4] + claimed_length.to_bytes(4, "big") + CANONICAL[8:]
            with self.subTest(length=claimed_length), self.assertRaisesRegex(ValueError, "Payload-Länge"):
                protocol.parse_message(message)
```

**Zeilen 115-118:** Ein abgeschnittenes Payloadbyte, ein zusätzliches
Byte und ein Header ohne Payload sind drei weitere reale Strukturfälle.
Alle müssen ValueError liefern, auch wenn der Header selbst gültig aussieht.

```python
    def test_truncated_payload_extra_bytes_and_header_only(self):
        for message in [CANONICAL[:-1], CANONICAL + b"x", CANONICAL[:8]]:
            with self.subTest(message=message), self.assertRaises(ValueError):
                protocol.parse_message(message)
```

**Zeilen 120-124:** Der echte Default-CLI-Aufruf muss Status 0,
genau den Referenzhextext und True-Roundtrip zeigen. Die sichtbare Demo
wird damit unabhängig von den direkten API-Tests geprüft.

```python
    def test_default_cli_matches_canonical_vector(self):
        process = run_cli("ue1.4/protocol.py")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn(CANONICAL.hex(" "), process.stdout)
        self.assertIn("Roundtrip identisch: True", process.stdout)
```

**Zeilen 126-131:** Zunächst wird der Parser-CLI-Modus mit festem
Hexinput ausgeführt. Danach setzt die Erzeuger-CLI beide Flags, Sequenz
65535 und UTF-8-ä. Erwartete Bytes sind genau `10 03 ff ff 00 00 00 02 c3 a4`;
die Länge zählt die zwei UTF-8-Bytes, nicht den einen Codepoint.

```python
    def test_cli_binary_parser_and_utf8_payload(self):
        parsed = run_cli("ue1.4/protocol.py", "--message-hex", CANONICAL.hex())
        self.assertEqual(parsed.returncode, 0, parsed.stderr)
        generated = run_cli("ue1.4/protocol.py", "--data", "--urgent", "--sequence", 65535, "--payload", "ä")
        self.assertEqual(generated.returncode, 0, generated.stderr)
        self.assertIn("10 03 ff ff 00 00 00 02 c3 a4", generated.stdout)
```

**Zeilen 133-138:** Nullsequenz, Leerpayload, ungültiges Hex und
falsche Version werden als echte CLI-Aufrufe abgelehnt. Status 1 und
Protokollfehlermeldung sind für jeden Fall erforderlich.

```python
    def test_invalid_cli_inputs(self):
        for arguments in [("--sequence", "0"), ("--payload", ""), ("--message-hex", "xx"), ("--message-hex", "18 00 00 2a 00 00 00 01 78")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.4/protocol.py", *arguments)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Protokollfehler", process.stderr)
```

**Zeilen 141-142:** Der Startschutz ermöglicht die separat dokumentierte
Ausführung dieser Protokolltests mit unittest.main.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_14_protocol.py

1. Ergänze einen festen Vektor für Sequenz 258: die Sequenzbytes
   müssen 01 02 sein. Nutze keine Erzeugerfunktion für den Erwartungsvektor.
2. Ändere in einer Kopie die Bitverschiebung der Version. Beobachte,
   warum feste Vektoren den Fehler sofort zeigen, ein reiner Roundtrip
   dagegen bei zwei passend falschen Funktionen täuschen könnte.

## `tests/test_15_threads.py`

**Zeilen 1-6:** Die Kennzeichnung beschreibt sequentielle Referenz,
Rest, überzählige Threads sowie leere und fehlerhafte Eingaben.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.5 mit sequenzieller Referenz, Restslices, n>len, leerer und fehlerhafter Eingabe.
```

**Zeilen 8-14:** argparse liefert den erwarteten CLI-Konversionsfehler,
math Endlichkeit/NaN, Path Testdateien, sys den größten endlichen Float,
unittest die Assertions und support die lokalen Hilfen.

```python
import argparse
import math
from pathlib import Path
import sys
import unittest

from support import ROOT, load_module, run_cli, temporary_directory
```

**Zeilen 16-17:** calculation wird ausdrücklich unter seinem normalen
Importnamen geladen, bevor threads geladen wird. Dadurch kann dessen
Import dieselbe Modulinstanz verwenden und die Referenz bleibt gemeinsam.

```python
calculation = load_module("ue1.5/calculation.py", "calculation")
threads = load_module("ue1.5/threads.py", "ueb01_threads")
```

**Zeile 20:** CalculationTests prüft das gemeinsame Hilfsmodul
unabhängig davon, ob und wie Threads gestartet werden.

```python
class CalculationTests(unittest.TestCase):
```

**Zeilen 21-23:** Für Eingang 0 und eine Iteration ist das Ergebnis
unabhängig berechenbar: sin(0)+0.5*cos(0)=0.5. Zusätzlich wird die leere
Eingabeliste geprüft. Das sind feste Referenz- und Neutralfälle.

```python
    def test_first_iteration_reference(self):
        self.assertEqual(calculation.complicated_calculation([0.0], 1), [0.5])
        self.assertEqual(calculation.complicated_calculation([], 7), [])
```

**Zeilen 25-29:** Verschiedene Werte einschließlich des größten
endlichen Floats werden zweimal mit identischen 100 Iterationen berechnet.
Eine Eingangskopie merkt den ursprünglichen Zustand vor den Aufrufen.

```python
    def test_deterministic_finite_calculation(self):
        values = [-1.0, 0.0, 0.125, 4.5, sys.float_info.max]
        original = values[:]
        first = calculation.complicated_calculation(values, 100)
        second = calculation.complicated_calculation(values, 100)
```

**Zeilen 30-33:** Ergebnisse müssen deterministisch gleich sein,
Eingaben unverändert bleiben, Anzahl erhalten bleiben und alle Ergebnisse
endlich sein. Der große Eingabewert prüft den begrenzten sin-Startwert.

```python
        self.assertEqual(first, second)
        self.assertEqual(values, original)
        self.assertEqual(len(first), len(values))
        self.assertTrue(all(math.isfinite(value) for value in first))
```

**Zeilen 35-40:** 13 Längen mal 16 Threadzahlen erzeugen 208 subTests.
Jeder berechnet Bereiche und flacht deren enthaltene Indizes ab. So
werden Restfälle, leere Arrays und viele n>len-Fälle systematisch untersucht.

```python
    def test_all_small_range_partitions(self):
        for length in range(13):
            for count in range(1, 17):
                with self.subTest(length=length, threads=count):
                    ranges = calculation.split_ranges(length, count)
                    indices = [index for start, end in ranges for index in range(start, end)]
```

**Zeilen 41-46:** Bereichsgrößen werden bestimmt. Gefordert sind n
Bereiche, exakt alle Indizes ohne Duplikat/Lücke, Größenunterschied höchstens
1 und richtige Anfangs-/Endgrenzen. Diese Invarianten prüfen die Bedeutung
der Aufteilung, nicht bloß eine Kopie ihrer Formel.

```python
                    sizes = [end - start for start, end in ranges]
                    self.assertEqual(len(ranges), count)
                    self.assertEqual(indices, list(range(length)))
                    self.assertLessEqual(max(sizes) - min(sizes), 1)
                    self.assertEqual(ranges[0][0], 0)
                    self.assertEqual(ranges[-1][1], length)
```

**Zeilen 48-51:** Drei zusätzliche feste Bereichslisten konkretisieren
7/3 mit Rest, 2/4 mit leeren Slices und Länge 0. Der Erwartungswert wird
direkt angegeben und macht die gewählte Restverteilung anschaulich.

```python
    def test_explicit_remainder_empty_and_excess_threads(self):
        self.assertEqual(calculation.split_ranges(7, 3), [(0, 3), (3, 5), (5, 7)])
        self.assertEqual(calculation.split_ranges(2, 4), [(0, 1), (1, 2), (2, 2), (2, 2)])
        self.assertEqual(calculation.split_ranges(0, 2), [(0, 0), (0, 0)])
```

**Zeilen 53-59:** Null/negative Integer und falsche Typen prüfen den
positiven Validator; negative/falsche Arraylängen prüfen split_ranges.
Jeder Fall trägt seine erwartete Fehlerklasse, damit TypeError und
ValueError korrekt unterschieden werden.

```python
    def test_invalid_integer_inputs(self):
        for value, error in [(0, ValueError), (-1, ValueError), (True, TypeError), (1.5, TypeError), (None, TypeError)]:
            with self.subTest(value=value), self.assertRaises(error):
                calculation.validate_positive_integer(value, "test")
        for length, error in [(-1, ValueError), (True, TypeError), (1.5, TypeError)]:
            with self.subTest(length=length), self.assertRaises(error):
                calculation.split_ranges(length, 2)
```

**Zeilen 61-65:** CLI-Text 3 muss zum Integer 3 werden. 0, -1, 1.5
und Text müssen ArgumentTypeError liefern, den argparse in verständliche
Verwendungsfehler übersetzt. Die Text-/API-Grenze wird eigens geprüft.

```python
    def test_cli_integer_parser(self):
        self.assertEqual(calculation.positive_int("3"), 3)
        for value in ["0", "-1", "1.5", "text"]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                calculation.positive_int(value)
```

**Zeilen 67-73:** Ungültige Iterationen werden auch direkt an der
Rechenfunktion geprüft. NaN und beide Unendlichkeiten müssen als Werte
ValueError erzeugen. Die Schleifen testen unabhängig Iterations- und Werteprüfung.

```python
    def test_invalid_iterations_and_nonfinite_values(self):
        for iterations, error in [(0, ValueError), (-1, ValueError), (True, TypeError)]:
            with self.subTest(iterations=iterations), self.assertRaises(error):
                calculation.complicated_calculation([0.0], iterations)
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculation.complicated_calculation([value], 1)
```

**Zeilen 75-81:** Eine echte lokale Datei mischt Leerzeichen, Tab,
CRLF, CR, LF und Exponententext. load_values muss die vier erwarteten
Floats liefern; nur Leerraum muss danach eine leere Liste ergeben.
Es geht um echtes Dateilesen, keinen vorbereiteten Mock-String.

```python
    def test_load_whitespace_floats_and_universal_newlines(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            source.write_bytes(b"1.0 2.5\r\n\t-0.3\r1e2\n\n")
            self.assertEqual(calculation.load_values(source), [1.0, 2.5, -0.3, 100.0])
            source.write_bytes(b" \r\n\t")
            self.assertEqual(calculation.load_values(source), [])
```

**Zeilen 83-89:** Eine gültige erste und jeweils ungültige zweite
Zeile werden geschrieben. oops, nan, inf, -inf, 1e999 müssen mit
Zeile 2 gemeldet werden. Der letzte Token demonstriert Zahlenüberlauf
zu Unendlich statt eines reinen Parsingfehlers.

```python
    def test_invalid_file_values_include_line_number(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            for token in ["oops", "nan", "inf", "-inf", "1e999"]:
                source.write_text(f"1.0\n{token}\n", encoding="utf-8")
                with self.subTest(token=token), self.assertRaisesRegex(ValueError, "Zeile 2"):
                    calculation.load_values(source)
```

**Zeile 92:** ThreadTests prüft zusätzlich die echte nebenläufige
Organisation, geordnete Ergebnisse und CLI-Verwendung.

```python
class ThreadTests(unittest.TestCase):
```

**Zeilen 93-100:** Die neun Beispielwerte werden einmal sequentiell
berechnet. Für 1,2,4,20 Threads muss die vollständige geordnete Einzelwerteliste
identisch sein, und die Bereichszahl zur Threadzahl passen. Damit werden
auch mehr Threads als Werte ohne schwachen Summen-only-Vergleich geprüft.

```python
    def test_parallel_matches_sequential_and_preserves_order(self):
        values = calculation.load_values(ROOT / "ue1.5/werte.txt")
        expected = calculation.complicated_calculation(values, 100)
        for count in [1, 2, 4, 20]:
            with self.subTest(threads=count):
                actual, ranges = threads.run_parallel(values, count, 100)
                self.assertEqual(actual, expected)
                self.assertEqual(len(ranges), count)
```

**Zeilen 102-105:** Leere Eingabe mit drei Threads liefert leere
Ergebnisse und drei leere Bereiche. Die API darf weder dividieren durch
0 noch null Threads statt der gewünschten drei erzeugen.

```python
    def test_empty_array(self):
        actual, ranges = threads.run_parallel([], 3, 1)
        self.assertEqual(actual, [])
        self.assertEqual(ranges, [(0, 0)] * 3)
```

**Zeilen 107-111:** Ein Worker berechnet nur Indexbereich 1..2 und
schreibt Result-Slot 1. Die anderen Plätze müssen None bleiben, alle
Fehlerplätze None. Das überprüft die tatsächliche Zuständigkeit des Workers.

```python
    def test_worker_owns_one_result_slot(self):
        results, errors = [None, None, None], [None, None, None]
        threads.worker([0.0, 0.0, 0.0], 1, 2, results, 1, 1, errors)
        self.assertEqual(results, [None, [0.5], None])
        self.assertEqual(errors, [None, None, None])
```

**Zeilen 113-116:** Ein echter Thread erhält NaN. Die aufrufende
API muss RuntimeError mit ValueError als Ursache melden. Das verhindert,
dass ein Hintergrundfehler als fehlendes, aber erfolgreiches Resultat erscheint.

```python
    def test_worker_error_reaches_caller(self):
        with self.assertRaises(RuntimeError) as raised:
            threads.run_parallel([math.nan, 0.0], 2, 1)
        self.assertIsInstance(raised.exception.__cause__, ValueError)
```

**Zeilen 118-121:** Null/negative Threadzahl und null Iterationen
müssen vor brauchbarer Berechnung abgelehnt werden, auch bei leerer Eingabe.

```python
    def test_invalid_thread_count_and_iterations(self):
        for count, iterations in [(0, 1), (-1, 1), (1, 0)]:
            with self.subTest(count=count, iterations=iterations), self.assertRaises(ValueError):
                threads.run_parallel([], count, iterations)
```

**Zeilen 123-127:** Die echte CLI mit vier Threads und 50 Iterationen
muss 0 liefern und alle vier festen Bereiche, Zeiten, identische
Einzelwerte und GIL-Hinweis ausgeben. subtests sind hier unnötig, da
jedes verlangte Textelement einfach nacheinander geprüft wird.

```python
    def test_real_cli_reports_ranges_times_and_agreement(self):
        process = run_cli("ue1.5/threads.py", ROOT / "ue1.5/werte.txt", "--threads", 4, "--iterations", 50)
        self.assertEqual(process.returncode, 0, process.stderr)
        for text in ["[0, 3)", "[3, 5)", "[5, 7)", "[7, 9)", "Zeit=", "Identische Einzelwerte: True", "GIL"]:
            self.assertIn(text, process.stdout)
```

**Zeilen 129-136:** Eine tatsächlich leere Datei läuft mit fünf
Threads und einer Iteration. Erfolg, Wertanzahl 0 und Nullsumme zeigen
die sichtbare Behandlung des Leerfalls, nicht nur ein API-Ergebnis.

```python
    def test_empty_file_cli_with_more_threads(self):
        with temporary_directory() as directory:
            source = Path(directory) / "empty"
            source.write_bytes(b"")
            process = run_cli("ue1.5/threads.py", source, "--threads", 5, "--iterations", 1)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("Werte: 0", process.stdout)
            self.assertIn("Summe=0.000000000000", process.stdout)
```

**Zeilen 138-142:** Fehlende Dateioption und unbrauchbare Thread-/
Iterationsargumente müssen argparse-Status 2 liefern. Die CLIs werden
wirklich gestartet; ein späterer fehlender Dateiinhalt ist nicht gemeint.

```python
    def test_invalid_cli_parameters(self):
        for arguments in [(), ("file", "--threads", "0"), ("file", "--iterations", "0"), ("file", "--threads", "x")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.5/threads.py", *arguments)
                self.assertEqual(process.returncode, 2)
```

**Zeilen 144-150:** Eine Datei erhält nacheinander falschen Token,
NaN und ungültige UTF-8-Bytes. Jeder echte CLI-Aufruf muss mit Status 1
und Berechnungsfehler enden. Dies prüft drei unterschiedliche Fehlerquellen.

```python
    def test_file_errors_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            for raw in [b"oops", b"nan", b"\xff"]:
                source.write_bytes(raw)
                process = run_cli("ue1.5/threads.py", source, "--iterations", 1)
                self.assertEqual(process.returncode, 1)
```

**Zeilen 151-153:** Auch die Fehlermeldung wird geprüft. Anschließend
wird die Quelle entfernt und ein echter Missing-File-Aufruf verlangt.
Der temporäre Kontext räumt danach alle lokalen Überreste auf.

```python
                self.assertIn("Berechnungsfehler", process.stderr)
            source.unlink()
            self.assertEqual(run_cli("ue1.5/threads.py", source).returncode, 1)
```

**Zeilen 156-157:** Der Startschutz bietet einen separaten unittest-
Aufruf für dieses Modul, ohne die Discovery zu verdoppeln.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_15_threads.py

1. Ergänze Länge 100 mit 7 Threads in der Invariantenprüfung.
   Begründe jeden der fünf geprüften Aufteilungseigenschaften.
2. Ändere in einer Kopie die Zusammenfügung zur Abschlussreihenfolge.
   Wähle unterschiedlich rechenaufwendige Werte und erkläre, warum ein
   vollständiger Listenvergleich aussagekräftiger ist als nur die Summe.

## `tests/test_16_shared_sum.py`

**Zeilen 1-6:** Die KI-Kennzeichnung nennt tatsächliche Wiederholungen
und die getrennte didaktische Variante. Auch diese Tests erfinden keine
behaupteten Race-Ausgaben für naive.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.6 mit echten Wiederholungen, Lock, separatem erzwungenem Interleaving und Randfällen.
```

**Zeilen 8-12:** math ermöglicht präzise Summen und Vergleich,
Path lokale Dateien, unittest die Tests und support dieselben echten
Prozess-/Modulladehilfen wie für die übrigen Aufgaben.

```python
import math
from pathlib import Path
import unittest

from support import ROOT, load_module, run_cli, temporary_directory
```

**Zeilen 14-15:** Gemeinsames calculation und das Summenmodul werden
geladen. Beide sollen dieselbe Rechenfunktion verwenden, nicht bloß
zwei ähnlich aussehende Kopien.

```python
calculation = load_module("ue1.5/calculation.py", "calculation")
shared_sum = load_module("ue1.6/shared_sum.py", "ueb01_shared_sum")
```

**Zeile 18:** SharedSumTests sammelt die 13 Tests. Vor jeder Methode
ruft unittest automatisch setUp auf.

```python
class SharedSumTests(unittest.TestCase):
```

**Zeilen 19-21:** setUp liest die echten neun Werte und berechnet
die sequentielle fsum-Referenz mit 50 Iterationen. Jede Testmethode beginnt
mit frisch zugeordneten Eingaben und unabhängigem Erwartungswert.

```python
    def setUp(self):
        self.values = calculation.load_values(ROOT / "ue1.5/werte.txt")
        self.expected = math.fsum(calculation.complicated_calculation(self.values, 50))
```

**Zeilen 23-24:** assertIs verlangt exakt dasselbe Funktionsobjekt
aus dem gemeinsamen Modul. Das beweist die Wiederverwendung stärker
als ein Vergleich einiger zufällig gleicher Zahlen.

```python
    def test_exact_same_calculation_module_as_15(self):
        self.assertIs(shared_sum.complicated_calculation, calculation.complicated_calculation)
```

**Zeilen 26-30:** Zehn wirkliche Lock-Läufe erzeugen jeweils neue
Threads und gemeinsame Summe. Jeder muss innerhalb relativer/absoluter
1e-12-Toleranz zur Referenz liegen; subTest identifiziert den Lauf.

```python
    def test_lock_matches_reference_in_ten_real_runs(self):
        for run in range(10):
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "lock")
                self.assertTrue(math.isclose(actual, self.expected, rel_tol=1e-12, abs_tol=1e-12))
```

**Zeilen 32-36:** Zehn wirkliche naive Läufe werden ausgeführt.
Gefordert ist nur ein endlicher Messwert, keine künstlich erwartete
Abweichung und keine allgemeine Behauptung von Atomarität. Die konkreten
Ergebnisse werden zusätzlich in echten CLI-Messungen dokumentiert.

```python
    def test_naive_ten_real_runs_without_assuming_a_race(self):
        for run in range(10):
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "naive")
                self.assertTrue(math.isfinite(actual))
```

**Zeilen 38-41:** Für forced werden dieselben vier Slice-Teilsummen
unabhängig bestimmt. Jede ist ein möglicher letzter Schreibwert nach
dem bewusst gemeinsamen Lesen des alten Werts.

```python
    def test_forced_lost_updates_in_five_real_runs(self):
        ranges = calculation.split_ranges(len(self.values), 4)
        partials = [math.fsum(calculation.complicated_calculation(self.values[start:end], 50)) for start, end in ranges]
        for run in range(5):
```

**Zeilen 42-45:** Fünf tatsächliche forced-Läufe müssen deutlich von
der Referenz abweichen und exakt eine der ermittelten Teilsummen liefern.
So wird Lost Update durch altes Snapshot nachgewiesen, nicht bloß irgendein
unerklärter falscher Wert. Die Sleepdauer wird ausdrücklich gewählt.

```python
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "forced", 0.001)
                self.assertFalse(math.isclose(actual, self.expected, rel_tol=1e-12, abs_tol=1e-12))
                self.assertIn(actual, partials)
```

**Zeilen 47-50:** Alle drei Modi verarbeiten leere Eingabe mit drei
Threads. Sämtliche Teilsummen sind 0; auch forced muss daher 0 ergeben.
Der Test verhindert eine pauschale Behauptung, forced müsse immer abweichen.

```python
    def test_empty_arrays_in_all_modes(self):
        for mode in ["naive", "lock", "forced"]:
            with self.subTest(mode=mode):
                self.assertEqual(shared_sum.run_shared([], 3, 1, mode, 0), 0.0)
```

**Zeilen 52-56:** Mit genau einem Thread gibt es keinen konkurrierenden
Schreibvorgang. Alle drei Modi müssen die vollständige Referenz exakt
liefern; die forced-Barrier hat nur diesen einen Teilnehmer.

```python
    def test_one_thread_in_all_modes(self):
        for mode in ["naive", "lock", "forced"]:
            with self.subTest(mode=mode):
                actual = shared_sum.run_shared(self.values, 1, 50, mode, 0)
                self.assertEqual(actual, self.expected)
```

**Zeilen 58-60:** Ein Wert und fünf Lock-Threads erzeugen vier leere
Slices. Deren Nullsummen dürfen den einzigen echten Wert 0.5 nicht verändern.

```python
    def test_lock_with_more_threads_than_values(self):
        actual = shared_sum.run_shared([0.0], 5, 1, "lock")
        self.assertEqual(actual, 0.5)
```

**Zeilen 62-66:** Die Falltabelle variiert ungültige Threadzahl,
Iterationszahl, Modus und negative/NaN/unendliche Delaywerte. Jeder wird
vor einer brauchbaren Ausführung mit ValueError zurückgewiesen.

```python
    def test_invalid_modes_counts_iterations_and_delay(self):
        cases = [(0, 1, "lock", 0), (1, 0, "lock", 0), (1, 1, "bad", 0), (1, 1, "forced", -0.1), (1, 1, "forced", math.nan), (1, 1, "forced", math.inf)]
        for count, iterations, mode, delay in cases:
            with self.subTest(case=(count, iterations, mode, delay)), self.assertRaises(ValueError):
                shared_sum.run_shared([], count, iterations, mode, delay)
```

**Zeilen 68-71:** NaN lässt einen echten forced-Worker scheitern.
Die API muss RuntimeError mit ValueError-Ursache liefern. Die anderen
Teilnehmer müssen durch abort beendet werden, sodass kein endloses
Warten auf den fehlenden Barrierteilnehmer entsteht.

```python
    def test_worker_error_aborts_barrier_and_reaches_caller(self):
        with self.assertRaises(RuntimeError) as raised:
            shared_sum.run_shared([math.nan, 0.0], 4, 1, "forced", 0)
        self.assertIsInstance(raised.exception.__cause__, ValueError)
```

**Zeilen 73-78:** Die echte CLI führt drei Läufe pro Modus aus.
Status 0 und je drei Ergebniszeilen werden verlangt; die ausdrückliche
Kennzeichnung der Eingriffe muss in der Ausgabe stehen.

```python
    def test_cli_three_real_runs_of_each_mode(self):
        process = run_cli("ue1.6/shared_sum.py", ROOT / "ue1.5/werte.txt", "--iterations", 50, "--runs", 3)
        self.assertEqual(process.returncode, 0, process.stderr)
        for mode in ["naive", "lock", "forced"]:
            self.assertEqual(process.stdout.count(f"{mode} Lauf"), 3)
        self.assertIn("didaktisch erzwungenes", process.stdout)
```

**Zeilen 79-84:** Der zusätzliche Hinweis darf forced nicht als naive
Messung ausgeben. Jede Lock-Zeile muss OK enthalten und jede forced-Zeile
ABWEICHUNG. Für naive wird bewusst kein solcher Fehlerzwang formuliert.

```python
        self.assertIn("keine naive +=-Messung", process.stdout)
        for line in process.stdout.splitlines():
            if line.startswith("lock Lauf"):
                self.assertIn("; OK;", line)
            if line.startswith("forced Lauf"):
                self.assertIn("ABWEICHUNG", line)
```

**Zeilen 86-92:** Eine echte Leerdatei läuft mit fünf Threads und
zwei Wiederholungen je Modus. Erfolg und fehlendes ABWEICHUNG zeigen,
dass eine erzwungene Nullsumme korrekt als Nullsumme behandelt wird.

```python
    def test_empty_input_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "empty"
            source.write_bytes(b"")
            process = run_cli("ue1.6/shared_sum.py", source, "--threads", 5, "--iterations", 1, "--runs", 2)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertNotIn("ABWEICHUNG", process.stdout)
```

**Zeilen 94-97:** Fehlende Dateioption, null Läufe, null Threads und
unbekannter Modus sind argparse-Fehler mit Status 2. Alle Aufrufe starten
den echten CLI-Prozess.

```python
    def test_invalid_cli_arguments(self):
        for arguments in [(), ("file", "--runs", "0"), ("file", "--threads", "0"), ("file", "--mode", "bad")]:
            with self.subTest(arguments=arguments):
                self.assertEqual(run_cli("ue1.6/shared_sum.py", *arguments).returncode, 2)
```

**Zeilen 99-103:** Ein tatsächlich fehlender Eingabepfad muss Status 1
liefern. Negative Delay bei gültiger Datei wird ebenfalls mit Status 1
und delay-Meldung zurückgewiesen, statt im Worker-Sleep verborgen zu scheitern.

```python
    def test_cli_missing_file_and_invalid_delay(self):
        self.assertEqual(run_cli("ue1.6/shared_sum.py", ROOT / ".tmp/nonexistent-input").returncode, 1)
        process = run_cli("ue1.6/shared_sum.py", ROOT / "ue1.5/werte.txt", "--iterations", 1, "--delay", "-1")
        self.assertEqual(process.returncode, 1)
        self.assertIn("delay", process.stderr)
```

**Zeilen 106-107:** Der Startschutz ermöglicht das isolierte Ausführen
dieser unittest-Datei und vermeidet Nebenwirkungen beim Import.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_16_shared_sum.py

1. Erhöhe die naive Wiederholungszahl. Dokumentiere die beobachteten
   Messwerte und behalte die Aussage, dass ein sichtbarer Fehler nicht
   garantiert ist. Verändere den Test nicht zu einem erzwungenen naive-Race.
2. Entferne in einer Kopie barrier.abort und untersuche den Unterschied
   zum Timeout. Benutze dafür einen begrenzten separaten Prozess; die
   eigentliche Lösung muss Workerfehler ohne unnötiges Warten weitergeben.

## `tests/test_17_producer_consumer.py`

**Zeilen 1-6:** Die Kennzeichnung nennt genau-einmal-Verarbeitung,
begrenzten Puffer, Ende, finally und tatsächliche Hängerprüfung.

```python
# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.7 auf genau-einmal-Verarbeitung, bounded Queue, Sentinels, finally und Hänger.
```

**Zeilen 8-13:** Counter zählt Vorkommen, queue erstellt echte Puffer,
threading führt getrennte Abläufe/Events aus und unittest überprüft sie.
Die Testhilfe lädt das Modul und startet die CLI mit Timeout.

```python
from collections import Counter
import queue
import threading
import unittest

from support import load_module, run_cli
```

**Zeile 15:** Die Producer-Consumer-API wird direkt geladen. Das
Importieren startet wegen des Startschutzes noch keinen Producer.

```python
pipeline = load_module("ue1.7/producer_consumer.py", "ueb01_pipeline")
```

**Zeile 18:** ProducerConsumerTests enthält zehn Methoden mit vielen
Kombinationen. Korrektheit darf nicht von einer festen Consumerverteilung abhängen.

```python
class ProducerConsumerTests(unittest.TestCase):
```

**Zeilen 19-25:** Vier Wertanzahlen, drei Consumerzahlen und zwei
Queuegrößen bilden 24 Fälle. Jeder startet die echte Pipeline und flacht
die individuell aufgezeichneten Werte ab. count 0 und Kapazität 1 sind dabei.

```python
    def test_every_value_exactly_once_across_consumers(self):
        for count in [0, 1, 17, 257]:
            for consumers in [1, 2, 5]:
                for maxsize in [1, 4]:
                    with self.subTest(count=count, consumers=consumers, maxsize=maxsize):
                        results = pipeline.run_pipeline(count, consumers, maxsize)
                        values = [value for result in results for value in result.values]
```

**Zeilen 26-30:** Counter muss genau allen erzeugten Werten einmal
entsprechen. Resultatzahl, Gesamtsumme und jede individuelle Summe
werden zusätzlich geprüft. Eine gleiche Gesamtsumme allein könnte
ausgleichende Auslassungen/Duplikate übersehen.

```python
                        self.assertEqual(Counter(values), Counter(range(1, count + 1)))
                        self.assertEqual(len(results), consumers)
                        self.assertEqual(sum(result.total for result in results), count * (count + 1) // 2)
                        for result in results:
                            self.assertEqual(result.total, sum(result.values))
```

**Zeilen 32-35:** Zwei Werte mit sieben Consumern und Puffergröße 1
müssen insgesamt zwei konsumierte Werte und Summe 3 ergeben. Die meisten
Consumer dürfen leer ausgehen, müssen aber durch Sentinels enden.

```python
    def test_more_consumers_than_values(self):
        results = pipeline.run_pipeline(2, 7, 1)
        self.assertEqual(sum(len(result.values) for result in results), 2)
        self.assertEqual(sum(result.total for result in results), 3)
```

**Zeilen 37-40:** Eine Queue mit Kapazität 1 wird schon mit 99 gefüllt.
Zwei Events melden Thread-Eintritt und Produktionsabschluss. Dadurch ist
ein kontrolliert voller Puffer vorhanden, ohne eine zufällige hohe Last zu benötigen.

```python
    def test_producer_blocks_until_full_queue_is_drained(self):
        work_queue = queue.Queue(maxsize=1)
        work_queue.put(99)
        entered, finished = threading.Event(), threading.Event()
```

**Zeilen 42-45:** Die lokale Testfunktion setzt zuerst entered,
führt den echten Producer für einen Wert und ein Sentinel aus und setzt
erst nach dessen Rückkehr finished. Events sind thread-sichere Signale.

```python
        def run_producer():
            entered.set()
            pipeline.producer(work_queue, 1, 1)
            finished.set()
```

**Zeilen 47-51:** Der Thread wird erzeugt und gestartet. entered.wait
wartet höchstens zwei Sekunden auf Eintritt. finished darf nach 0.03
Sekunden noch nicht gesetzt sein, weil die Queue weiterhin voll ist.
Anschließend beginnt die kontrollierte Freigabe des Puffers.

```python
        thread = threading.Thread(target=run_producer)
        thread.start()
        self.assertTrue(entered.wait(2))
        self.assertFalse(finished.wait(0.03))
        for expected in [99, 1, None]:
```

**Zeilen 52-57:** Die Folge 99,1,None wird mit je höchstens zwei
Sekunden Wartezeit entnommen und quittiert. Queue.join wartet auf die
Quittierungen, Thread.join auf das Ende; der Thread darf nicht mehr leben
und finished muss gesetzt sein. So wird echtes blockierendes put überprüft.

```python
            self.assertEqual(work_queue.get(timeout=2), expected)
            work_queue.task_done()
        work_queue.join()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertTrue(finished.is_set())
```

**Zeilen 59-63:** Eine leere begrenzte Queue und ein Ergebnisplatz
werden angelegt. Ein echter Consumerthread wird gestartet, der ohne Daten
in get wartet. Es wird weder ein Test-Sleep im Consumer noch ein Mock verwendet.

```python
    def test_consumer_waits_for_data_and_stops_on_sentinel(self):
        work_queue = queue.Queue(maxsize=1)
        results = [None]
        thread = threading.Thread(target=pipeline.consumer, args=(work_queue, results, 0))
        thread.start()
```

**Zeilen 64-70:** Der noch laufende Thread erhält 7 und None über
zeitlich begrenzte put-Aufrufe. Nach Queue- und Thread-join muss er beendet
sein und genau die Werte (7,) mit Summe 7 gespeichert haben. Sentinel
und Wert werden gemeinsam korrekt quittiert.

```python
        self.assertTrue(thread.is_alive())
        work_queue.put(7, timeout=2)
        work_queue.put(None, timeout=2)
        work_queue.join()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(results[0], ((7,), 7))
```

**Zeilen 72-78:** Ein absichtlich nicht addierbares Objekt wird direkt
in eine Testqueue gelegt und der Consumer synchron aufgerufen. TypeError
wird erwartet, dennoch muss unfinished_tasks 0 sein und Queue.join sofort
enden. Das ist ein kontrollierter Fehlerpfadtest des finally, kein von der
gültigen Produktions-API erzeugter Fremdwert.

```python
    def test_task_done_even_when_processing_raises(self):
        work_queue = queue.Queue(maxsize=1)
        work_queue.put(object())
        with self.assertRaises(TypeError):
            pipeline.consumer(work_queue, [None], 0)
        self.assertEqual(work_queue.unfinished_tasks, 0)
        work_queue.join()
```

**Zeilen 80-86:** Negative count, null/negative Consumerzahl und
null/negative maxsize sind ValueErrors. Bool, Float, String und None
an den Integerpositionen sind TypeErrors. Die zwei Tabellen prüfen
sowohl Bereich als auch exakten Typ, bevor Threadressourcen gestartet werden.

```python
    def test_invalid_counts_consumers_and_queue_sizes(self):
        for arguments in [(-1, 1, 1), (0, 0, 1), (0, -1, 1), (0, 1, 0), (0, 1, -1)]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                pipeline.run_pipeline(*arguments)
        for arguments in [(True, 1, 1), (1, False, 1), (1, 1, True), (1.5, 1, 1), (1, "2", 1), (1, 1, None)]:
            with self.subTest(arguments=arguments), self.assertRaises(TypeError):
                pipeline.run_pipeline(*arguments)
```

**Zeilen 88-93:** Die echte CLI verarbeitet 257 Werte mit vier
Consumern und maxsize 1 unter zehn Sekunden Prozess-Timeout. Status 0,
Gesamtsumme 33153, True für genau-einmal und vier Consumerzeilen sind
erforderlich. Ein Hänger macht den Testfehler sichtbar statt endlos zu warten.

```python
    def test_cli_multiple_consumers_with_size_one_finishes(self):
        process = run_cli("ue1.7/producer_consumer.py", "--count", 257, "--consumers", 4, "--maxsize", 1, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Gesamtsumme: 33153; erwartet: 33153", process.stdout)
        self.assertIn("Alle Werte genau einmal: True", process.stdout)
        self.assertEqual(process.stdout.count("Consumer "), 4)
```

**Zeilen 95-99:** Die gleiche Hängerprüfung gilt für count 0, fünf
Consumer und maxsize 1. Alle fünf müssen Anzahl/Summe 0 ausgeben und
die genau-einmal-Prüfung des leeren erwarteten Bereichs bestehen.

```python
    def test_cli_zero_count_finishes_all_consumers(self):
        process = run_cli("ue1.7/producer_consumer.py", "--count", 0, "--consumers", 5, "--maxsize", 1, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.count("Anzahl=0; Summe=0"), 5)
        self.assertIn("Alle Werte genau einmal: True", process.stdout)
```

**Zeilen 101-104:** Der echte Standardaufruf muss 0 liefern und
die Summe 5050 für 1..100 zeigen. Damit sind die Defaults ebenfalls geprüft.

```python
    def test_cli_default(self):
        process = run_cli("ue1.7/producer_consumer.py")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Gesamtsumme: 5050; erwartet: 5050", process.stdout)
```

**Zeilen 106-112:** Negative count und null Consumer/Queuegröße müssen
als Laufzeitvalidierungsfehler Status 1 samt Queue-Fehler liefern.
Nichtnumerischer count ist dagegen argparse-Syntaxfehler mit Status 2.
Die Unterscheidung macht die CLI-Verträge überprüfbar.

```python
    def test_cli_invalid_numbers(self):
        for arguments in [("--count", "-1"), ("--consumers", "0"), ("--maxsize", "0")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.7/producer_consumer.py", *arguments)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Queue-Fehler", process.stderr)
        self.assertEqual(run_cli("ue1.7/producer_consumer.py", "--count", "x").returncode, 2)
```

**Zeilen 115-116:** Der Startschutz bietet die separate Testdatei-
Ausführung; die Discovery kann die Klasse ohne zusätzlichen Testlauf importieren.

```python
if __name__ == "__main__":
    unittest.main()
```

### Änderungsübungen zu test_17_producer_consumer.py

1. Ergänze den Fall count 1000, consumers 8, maxsize 1.
   Verlange weiterhin Counter-Gleichheit und keine bestimmte Einzelverteilung.
2. Erzeuge in einer Kopie doppelt konsumierte Werte mit gleicher
   Gesamtsumme. Erkläre, warum Counter-Vergleich beziehungsweise sortierte
   vollständige Liste diesen Fehler erkennen und ein Summentest allein nicht.

## Hilfsdateien und Abschluss des Lernwegs

`ue1.5/werte.txt` enthält je eine endliche Gleitkommazahl pro Zeile. Neun
Werte machen bei vier Threads den Rest sichtbar. Es sind lokale Beispieldaten,
keine behaupteten Messwerte. `Angabe/file1.txt` und `file2.txt` entsprechen
dem vorhandenen ZIP; die Konvertierung darf weder sie noch das ZIP verändern.

`.gitignore` schließt `.venv/`, `__pycache__/`, `*.py[cod]`, `.tmp/`,
`.verification/`, `*.cover` und `.coverage*` aus. Die Sternmuster erfassen
Dateinamensvarianten; der abschließende Schrägstrich bezeichnet Ordner.
Das Ignorieren verhindert ein versehentliches Erfassen der Hilfsartefakte,
löscht aber keine Dateien. Keine dieser Regeln verändert globale Gitkonfiguration.

Arbeite die Übungen in Reihenfolge durch: Umgebung, Textkodierung, Dateien,
Binärstruktur, getrennte Threadresultate, gemeinsame Updates und Queue-
Übergabe. Führe nach jeder eigenen Änderung den passenden Test aus und
zum Schluss `python -B -m unittest discover -s tests -v`. Eine grüne
Testsuite ist belegte Prüfung der gewählten Fälle, keine Garantie für
jede denkbare Eingabe, beliebig große Speicheranforderungen oder jedes Betriebssystem.

**KI-Kennzeichnung der Erklärung:** Mit KI erstellt; keine Eigenleistung
behauptet. Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut
hermes status: ChatGPT or Codex Subscription. Implementierung: Codex CLI
0.162.1; Modell gpt-6.1-sol; Datum 2026-10-13. Anfrage: Implementiere das
vollständige Blatt mit Standardbibliothek und erkläre für jede Code-Datei
jede Zeile oder kleine Gruppe, ihren Zweck, Fachbegriffe und Änderungsübungen.
