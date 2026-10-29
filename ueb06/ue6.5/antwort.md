# 6.5 – Link-State: Dijkstra ab A

## Eingabe und Regeln

Ungerichtete Kanten aus Abbildung 1: A–B=1, A–C=3, B–C=8, B–D=7, B–F=5, C–G=1, G–F=2, D–F=6, D–E=2, F–E=3.

D(v),p(v) bezeichnet aktuelle Distanz und Vorgänger; ∞,– ist noch unerreichbar. N′ enthält endgültig ausgewählte Knoten. Anfangs gilt D(A)=0, alle anderen ∞. Pro Schritt wird der nicht feste Knoten mit kleinster Distanz gewählt und dann jede ausgehende Kante relaxiert: D(v) ← min(D(v), D(u)+c(u,v)). Bei Gleichstand bleibt der zuerst gefundene Vorgänger erhalten; Knotenauswahl wäre alphabetisch. Wegen nichtnegativer Kanten kann kein noch nicht fest ausgewählter Umweg eine kleinere Distanz zum ausgewählten Minimum erzeugen.

## Vollständige Dijkstra-Tabelle

Alle Spalten bleiben sichtbar, auch für bereits feste Knoten. Die Zeile A enthält die Relaxationen der direkten Nachbarn, wie die übliche Initialzeile der Vorlesung.

| Schritt / Auswahl | N′ | D(A), p(A) | D(B), p(B) | D(C), p(C) | D(D), p(D) | D(E), p(E) | D(F), p(F) | D(G), p(G) |
|---|---|---|---|---|---|---|---|---|
| vor Auswahl | ∅ | 0,– | ∞,– | ∞,– | ∞,– | ∞,– | ∞,– | ∞,– |
| 1: A | {A} | 0,– | 1,A | 3,A | ∞,– | ∞,– | ∞,– | ∞,– |
| 2: B | {A,B} | 0,– | 1,A | 3,A | 8,B | ∞,– | 6,B | ∞,– |
| 3: C | {A,B,C} | 0,– | 1,A | 3,A | 8,B | ∞,– | 6,B | 4,C |
| 4: G | {A,B,C,G} | 0,– | 1,A | 3,A | 8,B | ∞,– | 6,B | 4,C |
| 5: F | {A,B,C,G,F} | 0,– | 1,A | 3,A | 8,B | 9,F | 6,B | 4,C |
| 6: D | {A,B,C,G,F,D} | 0,– | 1,A | 3,A | 8,B | 9,F | 6,B | 4,C |
| 7: E | {A,B,C,G,F,D,E} | 0,– | 1,A | 3,A | 8,B | 9,F | 6,B | 4,C |

## Begründung jedes Schrittes

### Schritt 1: A mit D(A)=0
A ist der Startknoten.
- B: 0 + 1 = 1 < ∞; Distanz und Vorgänger werden aktualisiert.
- C: 0 + 3 = 3 < ∞; Distanz und Vorgänger werden aktualisiert.

### Schritt 2: B mit D(B)=1
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- A ist bereits fest; keine Relaxation.
- C: 1 + 8 = 9 ≥ 3; unverändert, auch bei Gleichstand.
- D: 1 + 7 = 8 < ∞; Distanz und Vorgänger werden aktualisiert.
- F: 1 + 5 = 6 < ∞; Distanz und Vorgänger werden aktualisiert.

### Schritt 3: C mit D(C)=3
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- A ist bereits fest; keine Relaxation.
- B ist bereits fest; keine Relaxation.
- G: 3 + 1 = 4 < ∞; Distanz und Vorgänger werden aktualisiert.

### Schritt 4: G mit D(G)=4
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- C ist bereits fest; keine Relaxation.
- F: 4 + 2 = 6 ≥ 6; unverändert, auch bei Gleichstand.

### Schritt 5: F mit D(F)=6
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- B ist bereits fest; keine Relaxation.
- D: 6 + 6 = 12 ≥ 8; unverändert, auch bei Gleichstand.
- E: 6 + 3 = 9 < ∞; Distanz und Vorgänger werden aktualisiert.
- G ist bereits fest; keine Relaxation.

### Schritt 6: D mit D(D)=8
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- B ist bereits fest; keine Relaxation.
- E: 8 + 2 = 10 ≥ 9; unverändert, auch bei Gleichstand.
- F ist bereits fest; keine Relaxation.

### Schritt 7: E mit D(E)=9
Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.
- D ist bereits fest; keine Relaxation.
- F ist bereits fest; keine Relaxation.

## Alle kürzesten Pfade ab A

| Ziel | Kosten | Alle kürzesten Pfade | Im Vorgängerbaum gewählter Pfad |
|---|---:|---|---|
| A | 0 | A | A |
| B | 1 | A → B | A → B |
| C | 3 | A → C | A → C |
| D | 8 | A → B → D | A → B → D |
| E | 9 | A → B → F → E; A → C → G → F → E | A → B → F → E |
| F | 6 | A → B → F; A → C → G → F | A → B → F |
| G | 4 | A → C → G | A → C → G |

**Gleichstand bei F:** A–B–F kostet 1+5=6, A–C–G–F kostet 3+1+2=6. Bei der Relaxation von G wird F nicht verändert, weil nur strikt kleinere Kandidaten den Vorgänger ersetzen. Das wirkt sich auch auf E aus: Beide kürzesten Wege nach E verwenden F und haben Kosten 9. Die Tabelle aller Pfade nennt beide Varianten, nicht nur den einen Vorgängerbaum.

## Reproduktion und echte Prüfungen

`python3 ueb06/ue6.5/dijkstra.py` (ab Repository-Wurzel). Die eingebaute Prüfung vergleicht Dijkstra unabhängig mit vollständiger Enumeration sämtlicher einfacher Pfade für **alle 49 Start-Ziel-Paare**. Bei positiven Kosten ist jeder kürzeste Weg einfach. Zusätzlich werden Auswahlreihenfolge, Ergebnisvektor, F-Gleichstand, Kosten und Endpunkte jedes rekonstruierten Pfades, ein unerreichbarer Knoten und die Zurückweisung negativer Kanten geprüft. Alle Prüfungen müssen vor der Markdown-Ausgabe bestehen.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.

