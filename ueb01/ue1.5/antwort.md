# Ü 1.5 – Nebenläufigkeit mit Threads

## Ausführung

Vom Ordner `ueb01` aus:

```bash
python -B ue1.5/threads.py ue1.5/werte.txt --threads 4 --iterations 50000
python -B ue1.5/threads.py ue1.5/werte.txt --threads 12 --iterations 1000
```

Die Datei enthält durch Leerraum getrennte endliche Floats. Leere Dateien
sind erlaubt. Die Rechnung ist deterministisch: Für jeden Wert wird
`seed = sin(value)` gebildet und anschließend die Funktion
`state = sin(state) + 0.5 * cos(state + seed)` wiederholt. Trigonometrie
und Schleife erzeugen tatsächlich CPU-Arbeit; es gibt kein künstliches
Warten in der Berechnung. `calculation.py` wird unverändert auch in 1.6 verwendet.

Bei neun Werten und vier Threads entstehen `[0,3)`, `[3,5)`, `[5,7)` und
`[7,9)`. Das Ende eines **halboffenen Bereichs** gehört nicht dazu.
`divmod` verteilt den Rest auf die ersten Threads. Bei mehr Threads als
Werten erhalten einige Threads leere Slices; bei leerer Eingabe sind alle
Slices leer. Jeder Thread schreibt nur in seinen eigenen Ergebnisplatz.
Nach allen `join()`-Aufrufen werden diese Plätze in ursprünglicher
Reihenfolge zusammengefügt. Worker-Ausnahmen werden an den Hauptthread
weitergegeben, nicht als stillschweigend fehlende Ergebnisse verwendet.

## Antworten auf alle vier Fragen

**1. Unterschied zwischen Erzeugen und Starten eines Threads?**

`threading.Thread(target=..., args=...)` erzeugt und konfiguriert zunächst
nur ein Threadobjekt. Die Zielfunktion läuft dadurch noch nicht.
Erst `thread.start()` startet den eigenen Ausführungsablauf und ruft dort
die Zielfunktion auf. Ein direktes `worker(...)` wäre ein gewöhnlicher
Funktionsaufruf im aktuellen Thread. Dasselbe Threadobjekt darf nur einmal
gestartet werden.

**2. Welche Funktion hat `Thread.join()`?**

Der aufrufende Thread wartet auf das Ende des betreffenden gestarteten
Threads. Ohne Timeout wartet er bis zu dessen tatsächlichem Ende.
Erst nach dem Warten darf der Hauptthread vollständige Ergebnisse
voraussetzen. `join()` führt die Berechnung nicht selbst aus und leitet
Worker-Ausnahmen nicht automatisch an den aufrufenden Thread weiter;
daher gibt es hier separate Fehlerplätze.

**3. Warum möglichst ein eigener Bereich pro Thread?**

Eigene Bereiche machen die Zuständigkeit eindeutig und vermeiden
doppelte oder ausgelassene Berechnungen. Jeder Worker verwendet einen
Listenslice und einen eigenen Result-Slot. Die ursprüngliche Liste wird
nur gelesen; Floats sind unveränderbare Objekte. Weil kein anderer
Worker denselben Ergebnisplatz schreibt, ist hier kein Lock für diese
Plätze nötig. Bei gemeinsam veränderbaren Elementen wäre ein Slice allein
keine vollständige Isolation, da Listen-Kopien solche Elemente weiterhin
referenzieren könnten.

**4. Probleme beim gleichzeitigen Verändern derselben Variable?**

Eine **Race Condition** ist ein Fehler, dessen Auftreten vom zeitlichen
Ineinandergreifen mehrerer Ausführungen abhängt. Mehrere Threads können
denselben alten Wert lesen und sich gegenseitig überschreiben; das heißt
**Lost Update**. Weitere Probleme sind inkonsistente Zwischenzustände
und nichtdeterministische Ergebnisse. Geeignete Locks oder ausschließlich
getrennte Ergebnisplätze verhindern diese ungeschützten Konflikte.

## GIL und tatsächlich gemessene Zeiten

Der **Global Interpreter Lock (GIL)** lässt auf gewöhnlichem CPython nur
einen Thread gleichzeitig Python-Code ausführen. Diese Rechnung hält
Python-Schleifen und kurze `math`-Aufrufe beschäftigt; n Threads bedeuten
deshalb keine automatische Beschleunigung der CPU-Arbeit. Threads können
dennoch etwa bei I/O-Wartezeiten sinnvoll sein. Andere Interpreter und
CPython-Builds ohne GIL sind gesondert zu betrachten.

Im aufgezeichneten uninstrumentierten Lauf mit 50000 Iterationen und vier
Threads betrug die Zeit sequentiell **0.040455 s**, mit Threads **0.039749 s**.
Die Einzelwerte waren identisch; beide ausgegebenen Summen waren
**6.610597757912**. Dieser einzelne kleine Zeitunterschied beweist keine
allgemeine Beschleunigung. Der geprüfte Interpreter meldete GIL aktiv.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.5 berechne deterministisch mit n Threads,
behandle Rest/n>len/leer, zeige Bereiche und Zeiten und beantworte alle vier Fragen.
