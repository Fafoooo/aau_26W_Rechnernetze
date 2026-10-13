# Ü 1.7 – Producer-Consumer

## Ausführung

Vom Ordner `ueb01` aus:

```bash
python -B ue1.7/producer_consumer.py --count 17 --consumers 3 --maxsize 2
python -B ue1.7/producer_consumer.py --count 257 --consumers 4 --maxsize 1
python -B ue1.7/producer_consumer.py --count 0 --consumers 5 --maxsize 1
```

Ein eigener Producer-Thread erzeugt die Integer `1..count`. Mindestens
ein Consumer verarbeitet sie. Jeder Consumer hat eine private Werteliste
und Summe und schreibt sein Ergebnis in einen eigenen Platz. Die Queue
ist begrenzt. Erst werden die Consumer gestartet, dann der Producer.
Der Hauptthread wartet zuerst mit `producer_thread.join()` auf alle
eingereihten Werte und Sentinels, dann mit `Queue.join()` auf deren
Quittierung und schließlich mit `Thread.join()` auf alle Consumer.
Damit kann `Queue.join()` nicht voreilig bei einer noch nicht befüllten
Queue zurückkehren.

## Antworten auf alle vier Fragen

**1. Warum ist `queue.Queue` geeigneter als eine normale Liste?**

Die Queue koordiniert mehrere Threads mit interner Synchronisation.
Sie bietet thread-sichere Einfüge-/Entnahmeoperationen, eine Kapazitätsgrenze,
blockierendes Warten und Aufgabenquittierung. Eine normale Liste bietet
diese zusammengesetzten Eigenschaften nicht. Man müsste Locks,
Wartebedingungen und Aufgabenbuchhaltung selbst implementieren. Eine
FIFO-Queue liefert die zuerst eingelegten Werte zuerst aus; die Reihenfolge,
in der verschiedene Consumer ihre Verarbeitung beenden, muss dennoch
nicht dieselbe sein.

**2. Wie wird ein Zugriff auf eine leere Queue verhindert?**

`get(block=True)` wartet intern, bis ein Element verfügbar ist. Der
Consumer schläft dabei, statt laufend nachzusehen. Es ist kein getrenntes
`empty()`-Prüfen nötig: Zwischen einer solchen Prüfung und der Entnahme
könnte ein anderer Consumer die Queue bereits verändert haben.

**3. Wie wird eine volle Queue behandelt?**

`Queue(maxsize=...)` hat hier immer positive Kapazität.
`put(block=True)` wartet bei voller Queue, bis ein Consumer Platz schafft.
Diese Rückwirkung auf den Producer heißt **Backpressure**. Der Producer
kann damit die ausstehenden Aufgaben nicht unbegrenzt im Queue-Puffer
ansammeln. `maxsize=0` wäre bei Python eine unbegrenzte Queue und wird
hier ausdrücklich als ungültige Eingabe zurückgewiesen.

**4. Wie erkennt ein Consumer das Produktionsende?**

Der Producer legt nach allen Zahlen für **jeden Consumer genau ein
`None`-Sentinel** ein. Ein Sentinel ist ein besonderer Kontrollwert;
`None` kann nicht mit einer erzeugten Integerzahl verwechselt werden.
Wer ihn entnimmt, speichert seine private Summe und beendet sich.
Ein einziges Sentinel würde bei mehreren Consumern nur einen beenden;
die anderen könnten dauerhaft in `get()` warten.

Nach jedem erfolgreichen `get()` ruft der Consumer `task_done()` in
einem `finally`-Block auf, **auch für das Sentinel**. `finally` läuft bei
normalem Ende, `return` und Ausnahmen. `Queue.join()` wartet darauf, dass
jeder eingelegte Eintrag so quittiert wurde. Es wartet auf die Aufgaben,
während `Thread.join()` auf das Ende des Threads wartet. Beides ist nötig.

## Ergebnisse und Grenzen

Bei 257 Werten ist die Gesamtsumme tatsächlich **33153**, bei 17 Werten
**153**. Für `count=0` enden auch fünf Consumer mit Summe 0, einschließlich
Queue-Kapazität 1. Die Tests vergleichen alle konsumierten Werte per
`Counter` mit `1..count` und prüfen jede individuelle Summe. Damit werden
sowohl ausgelassene als auch doppelt verarbeitete Werte erkannt. CLI-Tests
haben Timeouts und dürfen nicht hängen.

Die Verteilung auf Consumer hängt vom Scheduling ab; ein Consumer darf
auch keinen Wert erhalten. Die Ergebnislisten speichern für die Prüfung
alle konsumierten Werte. Diese Aufzeichnung ist nicht größenbeschränkt;
nur die gemeinsame Queue ist begrenzt. Die Verarbeitung der vom Programm
erzeugten gültigen Integerwerte ist abgedeckt; es wird kein allgemeiner
fehlertoleranter Jobserver mit fremden Workerfunktionen implementiert.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.7 nutze begrenzte Queue, eigenen Producer,
mehrere Consumer, Sentinels, task_done/finally und beide joins und prüfe Randfälle.
