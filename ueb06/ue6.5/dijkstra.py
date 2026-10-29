# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts,
# mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
"""Dijkstra mit vollständiger Spur und unabhängiger Enumeration einfacher Pfade."""
from math import inf
from pathlib import Path
from argparse import ArgumentParser

EDGES = (("A", "B", 1), ("A", "C", 3), ("B", "C", 8), ("B", "D", 7), ("B", "F", 5), ("C", "G", 1), ("G", "F", 2), ("D", "F", 6), ("D", "E", 2), ("F", "E", 3))
NODES = tuple("ABCDEFG")
NOTICE = "\n## KI-Kennzeichnung\n\nKI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.\n"

def graph_from(edges):
    graph = {node: {} for node in NODES}
    for left, right, cost in edges:
        if cost < 0:
            raise ValueError("Dijkstra benötigt nichtnegative Kanten")
        graph[left][right] = cost
        graph[right][left] = cost
    return graph

def dijkstra(graph, source):
    distance = dict.fromkeys(graph, inf)
    predecessor = dict.fromkeys(graph)
    distance[source] = 0
    settled, trace = [], []
    while len(settled) < len(graph):
        node = min((v for v in graph if v not in settled), key=lambda v: (distance[v], v))
        if distance[node] == inf:
            break
        settled.append(node)
        reasons = []
        for neighbor, cost in sorted(graph[node].items()):
            if neighbor in settled:
                reasons.append(f"{neighbor} ist bereits fest; keine Relaxation.")
                continue
            candidate = distance[node] + cost
            old = distance[neighbor]
            if candidate < old:
                distance[neighbor], predecessor[neighbor] = candidate, node
                reasons.append(f"{neighbor}: {distance[node]} + {cost} = {candidate} < {fmt(old)}; Distanz und Vorgänger werden aktualisiert.")
            else:
                reasons.append(f"{neighbor}: {distance[node]} + {cost} = {candidate} ≥ {fmt(old)}; unverändert, auch bei Gleichstand.")
        trace.append((node, tuple(settled), distance.copy(), predecessor.copy(), reasons))
    return distance, predecessor, trace

def all_simple_paths(graph, source, target, visited=()):
    if source == target:
        return [(0, (source,))]
    result = []
    for neighbor, cost in graph[source].items():
        if neighbor not in visited and neighbor != source:
            for rest, path in all_simple_paths(graph, neighbor, target, visited + (source,)):
                result.append((cost + rest, (source,) + path))
    return result

def reconstruct(predecessor, target):
    path = [target]
    while predecessor[path[0]] is not None:
        path.insert(0, predecessor[path[0]])
    return tuple(path)

def verify(graph, distance, predecessor, trace):
    assert distance == dict(zip(NODES, (0, 1, 3, 8, 9, 6, 4)))
    assert [row[0] for row in trace] == list("ABCGFDE")
    assert predecessor["F"] == "B"
    assert set(path for cost, path in all_simple_paths(graph, "A", "F") if cost == 6) == {("A", "B", "F"), ("A", "C", "G", "F")}
    for source in NODES:
        actual, parents, _ = dijkstra(graph, source)
        for target in NODES:
            candidates = all_simple_paths(graph, source, target)
            assert actual[target] == min(cost for cost, _ in candidates)
            path = reconstruct(parents, target)
            assert path[0] == source and path[-1] == target
            assert sum(graph[a][b] for a, b in zip(path, path[1:])) == actual[target]
    disconnected = {"A": {}, "B": {}}
    assert dijkstra(disconnected, "A")[0]["B"] == inf
    try:
        graph_from((("A", "B", -1),))
    except ValueError:
        pass
    else:
        raise AssertionError("Negative Kante wurde akzeptiert")

def fmt(value):
    return "∞" if value == inf else str(value)

def render(graph, distance, predecessor, trace):
    lines = ["# 6.5 – Link-State: Dijkstra ab A", "", "## Eingabe und Regeln", "", "Ungerichtete Kanten aus Abbildung 1: " + ", ".join(f"{a}–{b}={c}" for a, b, c in EDGES) + ".", "", "D(v),p(v) bezeichnet aktuelle Distanz und Vorgänger; ∞,– ist noch unerreichbar. N′ enthält endgültig ausgewählte Knoten. Anfangs gilt D(A)=0, alle anderen ∞. Pro Schritt wird der nicht feste Knoten mit kleinster Distanz gewählt und dann jede ausgehende Kante relaxiert: D(v) ← min(D(v), D(u)+c(u,v)). Bei Gleichstand bleibt der zuerst gefundene Vorgänger erhalten; Knotenauswahl wäre alphabetisch. Wegen nichtnegativer Kanten kann kein noch nicht fest ausgewählter Umweg eine kleinere Distanz zum ausgewählten Minimum erzeugen.", "", "## Vollständige Dijkstra-Tabelle", "", "Alle Spalten bleiben sichtbar, auch für bereits feste Knoten. Die Zeile A enthält die Relaxationen der direkten Nachbarn, wie die übliche Initialzeile der Vorlesung.", "", "| Schritt / Auswahl | N′ | " + " | ".join(f"D({v}), p({v})" for v in NODES) + " |", "|---|---|" + "---|" * len(NODES)]
    lines.append("| vor Auswahl | ∅ | " + " | ".join("0,–" if v == "A" else "∞,–" for v in NODES) + " |")
    for index, (node, settled, dist, parents, _) in enumerate(trace, 1):
        lines.append(f"| {index}: {node} | {{{','.join(settled)}}} | " + " | ".join(f"{fmt(dist[v])},{parents[v] or '–'}" for v in NODES) + " |")
    lines += ["", "## Begründung jedes Schrittes", ""]
    for index, (node, settled, dist, _, reasons) in enumerate(trace, 1):
        lines.append(f"### Schritt {index}: {node} mit D({node})={dist[node]}")
        lines.append("A ist der Startknoten." if index == 1 else "Die vorherige Tabellenzeile zeigt: Dieser Knoten besitzt unter allen noch nicht festen Knoten die kleinste vorläufige Distanz.")
        lines.extend("- " + reason for reason in reasons)
        lines.append("")
    lines += ["## Alle kürzesten Pfade ab A", "", "| Ziel | Kosten | Alle kürzesten Pfade | Im Vorgängerbaum gewählter Pfad |", "|---|---:|---|---|"]
    for target in NODES:
        shortest = [path for cost, path in all_simple_paths(graph, "A", target) if cost == distance[target]]
        lines.append(f"| {target} | {distance[target]} | " + "; ".join(" → ".join(path) for path in shortest) + " | " + " → ".join(reconstruct(predecessor, target)) + " |")
    lines += ["", "**Gleichstand bei F:** A–B–F kostet 1+5=6, A–C–G–F kostet 3+1+2=6. Bei der Relaxation von G wird F nicht verändert, weil nur strikt kleinere Kandidaten den Vorgänger ersetzen. Das wirkt sich auch auf E aus: Beide kürzesten Wege nach E verwenden F und haben Kosten 9. Die Tabelle aller Pfade nennt beide Varianten, nicht nur den einen Vorgängerbaum.", "", "## Reproduktion und echte Prüfungen", "", "`python3 ueb06/ue6.5/dijkstra.py` (ab Repository-Wurzel). Die eingebaute Prüfung vergleicht Dijkstra unabhängig mit vollständiger Enumeration sämtlicher einfacher Pfade für **alle 49 Start-Ziel-Paare**. Bei positiven Kosten ist jeder kürzeste Weg einfach. Zusätzlich werden Auswahlreihenfolge, Ergebnisvektor, F-Gleichstand, Kosten und Endpunkte jedes rekonstruierten Pfades, ein unerreichbarer Knoten und die Zurückweisung negativer Kanten geprüft. Alle Prüfungen müssen vor der Markdown-Ausgabe bestehen."]
    return "\n".join(lines) + "\n" + NOTICE

if __name__ == "__main__":
    graph = graph_from(EDGES)
    distance, predecessor, trace = dijkstra(graph, "A")
    verify(graph, distance, predecessor, trace)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Geprüfte antwort.md neben diesem Skript erzeugen")
    if parser.parse_args().write:
        destination = Path(__file__).with_name("antwort.md")
        destination.write_text(render(graph, distance, predecessor, trace) + "\n", encoding="utf-8")
        print(f"Alle Prüfungen bestanden; erzeugt: {destination}")
    else:
        print(render(graph, distance, predecessor, trace))
