# Ü 1.6 – Thread Safety und gemeinsam genutzte Daten

## Ausführung

Vom Ordner `ueb01` aus:

```bash
python -B ue1.6/shared_sum.py ue1.5/werte.txt --threads 4 --iterations 50000 --runs 5 --mode all
```

Es werden dieselbe Dateieingabe, Slice-Aufteilung und Berechnung aus
`ue1.5/calculation.py` verwendet. Jeder Worker berechnet zuerst seine
Teilsumme ohne Lock. Eine Liste mit einem Element enthält die gemeinsam
genutzte Float-Summe; alle Worker referenzieren dieselbe Liste.

`naive` verändert sie direkt mit `shared[0] += subtotal`. `lock` schützt
exakt diesen Summenupdate mit `with lock`. `forced` ist ein separates
didaktisches Experiment: Alle Threads lesen zunächst den alten Wert,
warten an einer `Barrier`, schlafen mit `time.sleep(delay)` und schreiben
danach `snapshot + subtotal`. Dadurch überschreiben sie sich gezielt.
Die Barrier sorgt dafür, dass vor dem ersten Schreiben alle gelesen haben;
der zuletzt schreibende Thread bestimmt, welche Teilsumme übrig bleibt.
Bei Workerfehlern wird die Barrier abgebrochen und die Ausnahme an den
Hauptthread weitergegeben. Bei einem Thread oder nur leeren Slices muss
auch die erzwungene Variante keinen Unterschied zeigen.

## Antworten auf alle vier Fragen

**1. Was bedeutet Thread Safety?**

Thread Safety bedeutet, dass gemeinsam verwendete Daten oder Funktionen
auch bei gleichzeitigem Zugriff mehrerer Threads ihre definierten
Eigenschaften behalten. Für diese Summe bedeutet es: Jede berechnete
Teilsumme wird einmal vollständig addiert. Die Reihenfolge darf variieren;
aufgrund von Float-Rundung darf eine minimale Rundungsabweichung verbleiben.

**2. Warum kann `result += value` problematisch sein?**

Die logische Operation besteht aus Lesen, Addieren und Zurückschreiben.
Beispiel: Zwei Threads lesen beide 0. Einer addiert 3 und schreibt 3;
der andere addiert 5 zu seinem ebenfalls gelesenen 0 und schreibt 5.
Erwartet war 8, eine Aktualisierung ist verloren. Eine einzelne
Quelltextzeile ist deshalb keine allgemeine Atomaritätsgarantie.
**Atomar** bedeutet, dass eine Operation aus Sicht anderer beteiligter
Ausführungen unteilbar erscheint. Konkrete CPython-Version, GIL und
Scheduling können bei der naiven Float-Addition dazu führen, dass kein
Fehler beobachtet wird. Aus fehlerfreien Messungen folgt keine universelle
Thread-Safety-Garantie für beliebige Interpreter oder Datentypen.

**3. Welche Funktion hat ein Lock?**

Ein Lock ermöglicht **gegenseitigen Ausschluss**: Zu einem Zeitpunkt darf
nur ein Thread den geschützten kritischen Abschnitt ausführen. Die anderen
warten. `with lock` erwirbt den Lock und gibt ihn auch bei einer Ausnahme
wieder frei. Weil alle Summenupdates denselben Lock verwenden, werden
Lesen/Addieren/Schreiben eines Updates nicht von einem anderen Update
unterbrochen. Ein Lock schützt keine Zugriffe, die ihn nicht verwenden.

**4. Warum nur so lange wie notwendig halten?**

Während des Haltens blockieren andere Threads, die diesen Lock brauchen.
Würde man auch die gesamte rechenintensive Funktion einschließen, wären
die Worker unnötig nacheinander beschäftigt. Hier berechnen sie zuerst
ihre privaten Teilsummen; nur deren Addition wird geschützt. Kurze
kritische Abschnitte reduzieren Wartezeit und erschweren vermeidbare
Blockierungsprobleme. Der GIL erklärt weiterhin, warum diese CPU-Rechnung
auf gewöhnlichem CPython nicht automatisch schneller wird.

## Echte Wiederholungsmessung vom 2026-10-13

Umgebung: CPython 3.14.7, Linux, GIL aktiv; neun Werte, vier Threads,
50000 Iterationen pro Wert, fünf Durchläufe **je Variante**. Referenzwert
aus der sequentiellen Rechnung, auf zwölf Nachkommastellen angezeigt:
**6.610597757912**.

| Lauf | naive: gemessen | lock: gemessen | forced: gemessen | forced: Differenz |
|---:|---:|---:|---:|---:|
| 1 | 6.610597757912 | 6.610597757912 | 1.367053015971 | -5.243544741941 |
| 2 | 6.610597757912 | 6.610597757912 | 1.367053015971 | -5.243544741941 |
| 3 | 6.610597757912 | 6.610597757912 | -0.237067240001 | -6.847664997913 |
| 4 | 6.610597757912 | 6.610597757912 | 3.482690267771 | -3.127907490141 |
| 5 | 6.610597757912 | 6.610597757912 | 1.367053015971 | -5.243544741941 |

Die naive Variante zeigte in diesen fünf Läufen keine Lost Updates; die
Lock-Variante stimmte ebenfalls in allen fünf Läufen innerhalb der Toleranz.
Die ausgegebene Differenz `-0.000000000000` bezeichnet eine auf zwölf Stellen
gerundete minimale negative Abweichung, kein beobachtetes Lost Update.
Float-Additionen in anderer Reihenfolge können gegenüber `math.fsum`
geringfügig runden; verglichen wird mit relativer und absoluter Toleranz
`1e-12`. Die vollständigen tatsächlichen Logs einschließlich Zeiten stehen
im [Prüfprotokoll](../testprotokoll_blatt01.md).

In allen fünf **erzwungenen** Läufen waren Lost Updates sichtbar. Diese
Messung belegt den absichtlich hergestellten read/barrier/sleep/write-Konflikt;
sie ist kein Nachweis dafür, dass die direkte naive `+=`-Variante hier
denselben Fehler gezeigt hätte. Die Tests führen außerdem zehn echte naive
Läufe, zehn echte Lock-Läufe und fünf erzwungene Läufe aus. Nur für die
erzwungene Mehr-Thread-Variante wird eine Abweichung gefordert.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.6 verwende dieselbe Rechnung wie 1.5,
miss naive/Lock tatsächlich mehrfach und kennzeichne erzwungene Lost Updates separat.
