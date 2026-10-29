# 6.6 – Distance-Vector-Algorithmus

## Eingabe, Formel und Initialisierung

Ungerichtete Kanten aus Abbildung 2: A–D=12, D–C=4, C–E=5, A–E=2, A–B=8, B–C=7, B–E=3.

B kennt anfangs nur seine direkten Kanten E=3, C=7 und A=8. Sein Vektor in der festen Reihenfolge (A,B,C,D,E) lautet (8,0,7,∞,3). Jeder andere Knoten startet ebenso mit Eigenkosten 0, direkten Linkkosten und ∞ für nicht bekannte Ziele. In B sind vor Nachrichtenempfang nur die Einträge zum jeweiligen direkten Nachbarn endlich. Die Spalten sind gespeicherte Kandidatenkosten über genau diesen Nachbarn, nicht die aktuellen Minima des Nachbarn selbst.

Nach Empfang eines Vektors von v gilt für jede Zielzeile z: T_B(z,v)=c(B,v)+D_v(z); anschließend D_B(z)=min_v T_B(z,v), mit D_B(B)=0. Das ist die verteilte Bellman-Ford-Rekursion. Es werden ausschließlich Nachbarvektoren verarbeitet; es gibt weder eine Dijkstra-Auswahl noch endgültig fixierte Knoten. Auch scheinbar nutzlose Umwege dürfen in einer Spalte stehen, weil der Nachbar einen Weg zurück über B melden kann. Split Horizon/Poison Reverse wird hier nicht angewandt.

## Ereignisreihenfolge – Bedeutung von ‚geringste Kosten zuerst‘

Die Angabe legt Nachrichtenzeitpunkte und die Bedeutung eines Schritts nicht eindeutig fest. Hauptlösung: asynchrone Zustellung. Ein Schritt ist eine gerichtete Vektornachricht. In jedem vollständigen Durchlauf werden alle gerichteten Kanten nach (Kosten, Sender, Empfänger) sortiert bedient. Der Sender sendet seinen **zum Zustellzeitpunkt aktuellen** Vektor. So beginnt das gesamte Netz mit A→E und E→A (globale Minimalkante 2); die bei B eingehenden Nachrichten kommen in der geforderten Kostenreihenfolge **E→B (3), C→B (7), A→B (8)**. Dies erfüllt sowohl die globale als auch die lokale Lesart von ‚kleinste Kante‘. Vor Bs erster Nachricht hat A→E bereits D_E(D)=2+12=14 bekannt gemacht; deshalb sieht B zunächst den Kandidaten 3+14=17 nach D. Erst C→B liefert 7+4=11. Diese Zwischenwerte sind Folge der ausdrücklich gewählten Zustellreihenfolge. Andere faire Reihenfolgen können andere Zwischentabellen ergeben, aber denselben Fixpunkt.

Konvergenz wird erst gemeldet, wenn ein **vollständiger Durchlauf bei keinem Knoten einen Vektor verändert**. Ein unveränderter Vektor von B allein wäre kein ausreichender Beleg. Alle Nachrichten werden zugestellt, auch wenn der gesendete Vektor unverändert ist; dadurch lassen sich die Konvergenzprüfung und die endgültigen Spalten vollständig prüfen.

Fettdruck in Tabellen kennzeichnet gegenüber der vorigen B-Tabelle geänderte Zellen und Minima. Jede B-Nachricht erhält eine Tabelle, auch wenn B unverändert bleibt. Bei Nachrichten an andere Empfänger ändert sich Bs gespeicherte Tabelle nicht; für diese Schritte gilt ausdrücklich dieselbe letzte B-Tabelle weiter.

### Vollständiger globaler Zustellplan

| Ereignis | Durchlauf | Nachricht | Linkkosten | Vektor des Empfängers geändert? | B-Tabelle |
|---:|---:|---|---:|---|---|
| 1 | 1 | A → E | 2 | ja | vorige unverändert |
| 2 | 1 | E → A | 2 | ja | vorige unverändert |
| 3 | 1 | B → E | 3 | nein | vorige unverändert |
| 4 | 1 | E → B | 3 | ja | neue Tabelle unten |
| 5 | 1 | C → D | 4 | ja | vorige unverändert |
| 6 | 1 | D → C | 4 | ja | vorige unverändert |
| 7 | 1 | C → E | 5 | ja | vorige unverändert |
| 8 | 1 | E → C | 5 | ja | vorige unverändert |
| 9 | 1 | B → C | 7 | nein | vorige unverändert |
| 10 | 1 | C → B | 7 | ja | neue Tabelle unten |
| 11 | 1 | A → B | 8 | nein | neue Tabelle unten |
| 12 | 1 | B → A | 8 | nein | vorige unverändert |
| 13 | 1 | A → D | 12 | nein | vorige unverändert |
| 14 | 1 | D → A | 12 | nein | vorige unverändert |
| 15 | 2 | A → E | 2 | nein | vorige unverändert |
| 16 | 2 | E → A | 2 | ja | vorige unverändert |
| 17 | 2 | B → E | 3 | nein | vorige unverändert |
| 18 | 2 | E → B | 3 | nein | neue Tabelle unten |
| 19 | 2 | C → D | 4 | ja | vorige unverändert |
| 20 | 2 | D → C | 4 | nein | vorige unverändert |
| 21 | 2 | C → E | 5 | nein | vorige unverändert |
| 22 | 2 | E → C | 5 | nein | vorige unverändert |
| 23 | 2 | B → C | 7 | nein | vorige unverändert |
| 24 | 2 | C → B | 7 | nein | neue Tabelle unten |
| 25 | 2 | A → B | 8 | nein | neue Tabelle unten |
| 26 | 2 | B → A | 8 | nein | vorige unverändert |
| 27 | 2 | A → D | 12 | nein | vorige unverändert |
| 28 | 2 | D → A | 12 | nein | vorige unverändert |
| 29 | 3 | A → E | 2 | nein | vorige unverändert |
| 30 | 3 | E → A | 2 | nein | vorige unverändert |
| 31 | 3 | B → E | 3 | nein | vorige unverändert |
| 32 | 3 | E → B | 3 | nein | neue Tabelle unten |
| 33 | 3 | C → D | 4 | nein | vorige unverändert |
| 34 | 3 | D → C | 4 | nein | vorige unverändert |
| 35 | 3 | C → E | 5 | nein | vorige unverändert |
| 36 | 3 | E → C | 5 | nein | vorige unverändert |
| 37 | 3 | B → C | 7 | nein | vorige unverändert |
| 38 | 3 | C → B | 7 | nein | neue Tabelle unten |
| 39 | 3 | A → B | 8 | nein | neue Tabelle unten |
| 40 | 3 | B → A | 8 | nein | vorige unverändert |
| 41 | 3 | A → D | 12 | nein | vorige unverändert |
| 42 | 3 | D → A | 12 | nein | vorige unverändert |

## Asynchrone Distanztabellen von B

### Initial (Ereignis/Runde 0)

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | ∞ | ∞ | 8 | 8 |
| C | ∞ | 7 | ∞ | 7 |
| D | ∞ | ∞ | ∞ | ∞ |
| E | 3 | ∞ | ∞ | 3 |

Distanzvektor von B (A,B,C,D,E): **(8, 0, 7, ∞, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 1, E → B (Kosten 3) (Ereignis/Runde 4)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (2, 3, 5, 14, 0).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | **5** | ∞ | 8 | **5** |
| C | **8** | 7 | ∞ | 7 |
| D | **17** | ∞ | ∞ | **17** |
| E | 3 | ∞ | ∞ | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 17, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 1, C → B (Kosten 7) (Ereignis/Runde 10)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (7, 7, 0, 4, 5).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | **14** | 8 | 5 |
| C | 8 | 7 | ∞ | 7 |
| D | 17 | **11** | ∞ | **11** |
| E | 3 | **12** | ∞ | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 1, A → B (Kosten 8) (Ereignis/Runde 11)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (0, 5, 7, 12, 2).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | **15** | 7 |
| D | 17 | 11 | **20** | 11 |
| E | 3 | 12 | **10** | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 2, E → B (Kosten 3) (Ereignis/Runde 18)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (2, 3, 5, 9, 0).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | **12** | 11 | 20 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 2, C → B (Kosten 7) (Ereignis/Runde 24)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (7, 7, 0, 4, 5).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | 20 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 2, A → B (Kosten 8) (Ereignis/Runde 25)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (0, 5, 7, 11, 2).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | **19** | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 3, E → B (Kosten 3) (Ereignis/Runde 32)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (2, 3, 5, 9, 0).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | 19 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 3, C → B (Kosten 7) (Ereignis/Runde 38)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (7, 7, 0, 4, 5).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | 19 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Durchlauf 3, A → B (Kosten 8) (Ereignis/Runde 39)

Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: (0, 5, 7, 11, 2).

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | 19 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

## Alternative: synchrone Interpretation

In einer synchronen Runde senden alle Knoten den Vektor aus der vorigen Runde; keine Änderung derselben Runde darf wiederverwendet werden. Bs Spalten werden in der Reihenfolge E,C,A dargestellt; alle drei Nachrichten enthalten aber alte Vektoren, und erst danach wird der nächste Rundenvektor berechnet. Daher dürfen diese Runden nicht mit den obigen asynchronen Nachrichten verwechselt werden. Auch hier läuft die Prüfung bis zu einer netzweit unveränderten Runde.

### Initial (Ereignis/Runde 0)

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | ∞ | ∞ | 8 | 8 |
| C | ∞ | 7 | ∞ | 7 |
| D | ∞ | ∞ | ∞ | ∞ |
| E | 3 | ∞ | ∞ | 3 |

Distanzvektor von B (A,B,C,D,E): **(8, 0, 7, ∞, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Synchrone Runde 1 (Ereignis/Runde 1)

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | **5** | ∞ | 8 | **5** |
| C | **8** | 7 | ∞ | 7 |
| D | ∞ | **11** | **20** | **11** |
| E | 3 | **12** | **10** | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Synchrone Runde 2 (Ereignis/Runde 2)

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | **14** | 8 | 5 |
| C | 8 | 7 | **15** | 7 |
| D | **12** | 11 | 20 | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

### Synchrone Runde 3 (Ereignis/Runde 3)

| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |
|---|---:|---:|---:|---:|
| A | 5 | 14 | 8 | 5 |
| C | 8 | 7 | 15 | 7 |
| D | 12 | 11 | **19** | 11 |
| E | 3 | 12 | 10 | 3 |

Distanzvektor von B (A,B,C,D,E): **(5, 0, 7, 11, 3)**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.

## Endergebnis und Pfadprobe

| Ziel | Kürzester Weg ab B | Kosten |
|---|---|---:|
| A | B → E → A | 3 + 2 = 5 |
| B | B | 0 |
| C | B → C | 7 |
| D | B → C → D | 7 + 4 = 11 |
| E | B → E | 3 |

Damit lautet Bs konvergierter Vektor **(5,0,7,11,3)**. Die alternative Route nach D über E kostet 3+5+4=12 und ist schlechter als 11. Die Direktkante B–A=8 wird durch B–E–A=5 verbessert.

## Reproduktion und echte Prüfungen

`python3 ueb06/ue6.6/distance_vector.py` (ab Repository-Wurzel). Asynchron: 42 gerichtete Zustellungen in 3 vollständigen Durchläufen; synchron: 3 Runden einschließlich der unveränderten Abschlussrunde. Die eingebauten Assertions vergleichen beide vollständigen Ergebnismatrizen, prüfen alle **25 Start-Ziel-Paare unabhängig durch vollständige Enumeration einfacher Pfade**, alle konvergierten Spalten gegen Linkkosten plus Nachbarvektor, Bs Empfangsreihenfolge, die globale Minimalkante, monotone Vektoren und tatsächliche netzweite Konvergenz. Die zwei Algorithmen verwenden keine globale Kürzeste-Wege-Funktion; die globale Pfadsuche wird ausschließlich als unabhängiger Test ausgeführt.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.

