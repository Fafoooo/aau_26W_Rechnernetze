# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.
# Anfrage: Reale Ping-Statistiken von Blatt07 auswerten und konfigurierte RTT-Anteile prüfen.
"""Keine simulierten Messwerte: Eingabe ist die unveränderte Ausgabe von iputils ping."""
import json
from pathlib import Path
import re
import sys


def statistics(text, expected=10):
    packets = re.search(r"(\d+) packets transmitted, (\d+) received", text)
    times = re.search(r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", text)
    if not packets or not times:
        raise ValueError("Vollständige Paket- und RTT-Statistik fehlt")
    sent, received = map(int, packets.groups())
    if sent != expected or received != expected:
        raise ValueError(f"Paketverlust oder falsche Anzahl: {sent}/{received}, erwartet {expected}")
    result = dict(zip(("min_ms", "avg_ms", "max_ms", "mdev_ms"), map(float, times.groups())))
    if not 0 <= result["min_ms"] <= result["avg_ms"] <= result["max_ms"]:
        raise ValueError("Ungültige Reihenfolge der RTT-Statistik")
    return {"sent": sent, "received": received, **result}


def budget():
    values = {"A": 2 * (1 + 5 + 1), "B": 2 * (1 + 30 + 30 + 1)}
    assert values == {"A": 14, "B": 124}
    assert values["B"] - values["A"] == 110
    return values


if __name__ == "__main__":
    print(json.dumps({"budget_ms": budget(), "ping": statistics(Path(sys.argv[1]).read_text())}, indent=2))
