# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts,
# mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
"""Echtes Distance Vector: Nachbarvektoren, asynchrone Zustellung und synchrone Runden."""
from math import inf
from pathlib import Path
from argparse import ArgumentParser

NODES = tuple("ABCDE")
EDGES = (("A", "D", 12), ("D", "C", 4), ("C", "E", 5), ("A", "E", 2), ("A", "B", 8), ("B", "C", 7), ("B", "E", 3))
GRAPH = {node: {} for node in NODES}
for left, right, cost in EDGES:
    GRAPH[left][right] = cost
    GRAPH[right][left] = cost
VIA = tuple(sorted(GRAPH["B"], key=lambda node: (GRAPH["B"][node], node)))
TARGETS = tuple(node for node in NODES if node != "B")
SCHEDULE = tuple(sorted((cost, sender, receiver) for sender in NODES for receiver, cost in GRAPH[sender].items()))
NOTICE = "\n## KI-Kennzeichnung\n\nKI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.\n"

def initial_vectors():
    return {node: {target: (0 if node == target else GRAPH[node].get(target, inf)) for target in NODES} for node in NODES}

def initial_tables():
    return {node: {via: {target: (cost if target == via else inf) for target in NODES} for via, cost in GRAPH[node].items()} for node in NODES}

def vector_from(node, table):
    return {target: (0 if target == node else min(column[target] for column in table.values())) for target in NODES}

def copy_table(table):
    return {via: column.copy() for via, column in table.items()}

def asynchronous():
    vectors, tables = initial_vectors(), initial_tables()
    trace: list[tuple] = [(0, "Initial", copy_table(tables["B"]), vectors["B"].copy(), None)]
    events = []
    for sweep in range(1, 21):
        changed = False
        for cost, sender, receiver in SCHEDULE:
            payload = vectors[sender].copy()
            tables[receiver][sender] = {target: cost + payload[target] for target in NODES}
            updated = vector_from(receiver, tables[receiver])
            changed_here = updated != vectors[receiver]
            changed |= changed_here
            vectors[receiver] = updated
            event = len(events) + 1
            events.append((event, sweep, sender, receiver, cost, changed_here))
            if receiver == "B":
                trace.append((event, f"Durchlauf {sweep}, {sender} → B (Kosten {cost})", copy_table(tables["B"]), updated.copy(), payload))
        if not changed:
            return vectors, tables, trace, events
    raise AssertionError("Asynchrone Konvergenzgrenze überschritten")

def synchronous():
    vectors, tables = initial_vectors(), initial_tables()
    trace: list[tuple] = [(0, "Initial", copy_table(tables["B"]), vectors["B"].copy(), None)]
    for round_number in range(1, 21):
        new_tables = {node: {via: {target: cost + vectors[via][target] for target in NODES} for via, cost in GRAPH[node].items()} for node in NODES}
        updated = {node: vector_from(node, new_tables[node]) for node in NODES}
        trace.append((round_number, f"Synchrone Runde {round_number}", copy_table(new_tables["B"]), updated["B"].copy(), None))
        if updated == vectors:
            return updated, new_tables, trace
        vectors = updated
    raise AssertionError("Synchrone Konvergenzgrenze überschritten")

def brute_force(source, target, visited=()):
    if source == target:
        return 0
    return min((cost + brute_force(neighbor, target, visited + (source,)) for neighbor, cost in GRAPH[source].items() if neighbor not in visited and neighbor != source), default=inf)

def verify(async_result, sync_result):
    vectors, tables, trace, events = async_result
    sync_vectors, sync_tables, sync_trace = sync_result
    assert VIA == ("E", "C", "A")
    assert SCHEDULE[0] == (2, "A", "E")
    assert [events[row[0] - 1][2] for row in trace[1:4]] == list(VIA)
    assert vectors["B"] == dict(zip(NODES, (5, 0, 7, 11, 3)))
    assert vectors == sync_vectors
    for source in NODES:
        for target in NODES:
            assert vectors[source][target] == brute_force(source, target)
        for via, cost in GRAPH[source].items():
            for target in NODES:
                assert tables[source][via][target] == cost + vectors[via][target]
                assert sync_tables[source][via][target] == cost + sync_vectors[via][target]
    assert not any(row[5] for row in events[-len(SCHEDULE):])
    assert sync_trace[-1][3] == sync_trace[-2][3]
    for snapshots in (trace, sync_trace):
        for before, after in zip(snapshots, snapshots[1:]):
            assert all(after[3][target] <= before[3][target] for target in NODES)
            assert vector_from("B", after[2]) == after[3]
    assert len(EDGES) == 7 and sum(map(len, GRAPH.values())) == 14

def fmt(value):
    return "∞" if value == inf else str(value)

def vector_text(vector):
    return "(" + ", ".join(fmt(vector[node]) for node in NODES) + ")"

def table_markdown(snapshot, previous=None):
    index, label, table, vector, payload = snapshot
    lines = [f"### {label} (Ereignis/Runde {index})", ""]
    if payload is not None:
        lines += [f"Empfangener Nachbarvektor, Reihenfolge A,B,C,D,E: {vector_text(payload)}.", ""]
    lines += ["| Ziel | über E: 3 + D_E | über C: 7 + D_C | über A: 8 + D_A | Minimum D_B |", "|---|---:|---:|---:|---:|"]
    for target in TARGETS:
        cells = []
        for via in VIA:
            cell = fmt(table[via][target])
            cells.append(f"**{cell}**" if previous is not None and table[via][target] != previous[2][via][target] else cell)
        minimum = fmt(vector[target])
        if previous is not None and vector[target] != previous[3][target]:
            minimum = f"**{minimum}**"
        lines.append(f"| {target} | " + " | ".join(cells) + f" | {minimum} |")
    lines += ["", f"Distanzvektor von B (A,B,C,D,E): **{vector_text(vector)}**. Eigenkosten D_B(B)=0; die B-Zeile entfällt deshalb in der Nachbartabelle.", ""]
    return lines

def render(async_result, sync_result):
    vectors, tables, trace, events = async_result
    _, _, sync_trace = sync_result
    lines = ["# 6.6 – Distance-Vector-Algorithmus", "", "## Eingabe, Formel und Initialisierung", "", "Ungerichtete Kanten aus Abbildung 2: " + ", ".join(f"{a}–{b}={c}" for a, b, c in EDGES) + ".", "", "B kennt anfangs nur seine direkten Kanten E=3, C=7 und A=8. Sein Vektor in der festen Reihenfolge (A,B,C,D,E) lautet (8,0,7,∞,3). Jeder andere Knoten startet ebenso mit Eigenkosten 0, direkten Linkkosten und ∞ für nicht bekannte Ziele. In B sind vor Nachrichtenempfang nur die Einträge zum jeweiligen direkten Nachbarn endlich. Die Spalten sind gespeicherte Kandidatenkosten über genau diesen Nachbarn, nicht die aktuellen Minima des Nachbarn selbst.", "", "Nach Empfang eines Vektors von v gilt für jede Zielzeile z: T_B(z,v)=c(B,v)+D_v(z); anschließend D_B(z)=min_v T_B(z,v), mit D_B(B)=0. Das ist die verteilte Bellman-Ford-Rekursion. Es werden ausschließlich Nachbarvektoren verarbeitet; es gibt weder eine Dijkstra-Auswahl noch endgültig fixierte Knoten. Auch scheinbar nutzlose Umwege dürfen in einer Spalte stehen, weil der Nachbar einen Weg zurück über B melden kann. Split Horizon/Poison Reverse wird hier nicht angewandt.", "", "## Ereignisreihenfolge – Bedeutung von ‚geringste Kosten zuerst‘", "", "Die Angabe legt Nachrichtenzeitpunkte und die Bedeutung eines Schritts nicht eindeutig fest. Hauptlösung: asynchrone Zustellung. Ein Schritt ist eine gerichtete Vektornachricht. In jedem vollständigen Durchlauf werden alle gerichteten Kanten nach (Kosten, Sender, Empfänger) sortiert bedient. Der Sender sendet seinen **zum Zustellzeitpunkt aktuellen** Vektor. So beginnt das gesamte Netz mit A→E und E→A (globale Minimalkante 2); die bei B eingehenden Nachrichten kommen in der geforderten Kostenreihenfolge **E→B (3), C→B (7), A→B (8)**. Dies erfüllt sowohl die globale als auch die lokale Lesart von ‚kleinste Kante‘. Vor Bs erster Nachricht hat A→E bereits D_E(D)=2+12=14 bekannt gemacht; deshalb sieht B zunächst den Kandidaten 3+14=17 nach D. Erst C→B liefert 7+4=11. Diese Zwischenwerte sind Folge der ausdrücklich gewählten Zustellreihenfolge. Andere faire Reihenfolgen können andere Zwischentabellen ergeben, aber denselben Fixpunkt.", "", "Konvergenz wird erst gemeldet, wenn ein **vollständiger Durchlauf bei keinem Knoten einen Vektor verändert**. Ein unveränderter Vektor von B allein wäre kein ausreichender Beleg. Alle Nachrichten werden zugestellt, auch wenn der gesendete Vektor unverändert ist; dadurch lassen sich die Konvergenzprüfung und die endgültigen Spalten vollständig prüfen.", "", "Fettdruck in Tabellen kennzeichnet gegenüber der vorigen B-Tabelle geänderte Zellen und Minima. Jede B-Nachricht erhält eine Tabelle, auch wenn B unverändert bleibt. Bei Nachrichten an andere Empfänger ändert sich Bs gespeicherte Tabelle nicht; für diese Schritte gilt ausdrücklich dieselbe letzte B-Tabelle weiter.", "", "### Vollständiger globaler Zustellplan", "", "| Ereignis | Durchlauf | Nachricht | Linkkosten | Vektor des Empfängers geändert? | B-Tabelle |", "|---:|---:|---|---:|---|---|"]
    for event, sweep, sender, receiver, cost, changed in events:
        lines.append(f"| {event} | {sweep} | {sender} → {receiver} | {cost} | {'ja' if changed else 'nein'} | {'neue Tabelle unten' if receiver == 'B' else 'vorige unverändert'} |")
    lines += ["", "## Asynchrone Distanztabellen von B", ""]
    for index, snapshot in enumerate(trace):
        lines.extend(table_markdown(snapshot, trace[index - 1] if index else None))
    lines += ["## Alternative: synchrone Interpretation", "", "In einer synchronen Runde senden alle Knoten den Vektor aus der vorigen Runde; keine Änderung derselben Runde darf wiederverwendet werden. Bs Spalten werden in der Reihenfolge E,C,A dargestellt; alle drei Nachrichten enthalten aber alte Vektoren, und erst danach wird der nächste Rundenvektor berechnet. Daher dürfen diese Runden nicht mit den obigen asynchronen Nachrichten verwechselt werden. Auch hier läuft die Prüfung bis zu einer netzweit unveränderten Runde.", ""]
    for index, snapshot in enumerate(sync_trace):
        lines.extend(table_markdown(snapshot, sync_trace[index - 1] if index else None))
    lines += ["## Endergebnis und Pfadprobe", "", "| Ziel | Kürzester Weg ab B | Kosten |", "|---|---|---:|", "| A | B → E → A | 3 + 2 = 5 |", "| B | B | 0 |", "| C | B → C | 7 |", "| D | B → C → D | 7 + 4 = 11 |", "| E | B → E | 3 |", "", "Damit lautet Bs konvergierter Vektor **(5,0,7,11,3)**. Die alternative Route nach D über E kostet 3+5+4=12 und ist schlechter als 11. Die Direktkante B–A=8 wird durch B–E–A=5 verbessert.", "", "## Reproduktion und echte Prüfungen", "", f"`python3 ueb06/ue6.6/distance_vector.py` (ab Repository-Wurzel). Asynchron: {len(events)} gerichtete Zustellungen in {events[-1][1]} vollständigen Durchläufen; synchron: {len(sync_trace) - 1} Runden einschließlich der unveränderten Abschlussrunde. Die eingebauten Assertions vergleichen beide vollständigen Ergebnismatrizen, prüfen alle **25 Start-Ziel-Paare unabhängig durch vollständige Enumeration einfacher Pfade**, alle konvergierten Spalten gegen Linkkosten plus Nachbarvektor, Bs Empfangsreihenfolge, die globale Minimalkante, monotone Vektoren und tatsächliche netzweite Konvergenz. Die zwei Algorithmen verwenden keine globale Kürzeste-Wege-Funktion; die globale Pfadsuche wird ausschließlich als unabhängiger Test ausgeführt."]
    return "\n".join(lines) + "\n" + NOTICE

if __name__ == "__main__":
    async_result = asynchronous()
    sync_result = synchronous()
    verify(async_result, sync_result)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Geprüfte antwort.md neben diesem Skript erzeugen")
    if parser.parse_args().write:
        destination = Path(__file__).with_name("antwort.md")
        destination.write_text(render(async_result, sync_result) + "\n", encoding="utf-8")
        print(f"Alle Prüfungen bestanden; erzeugt: {destination}")
    else:
        print(render(async_result, sync_result))
