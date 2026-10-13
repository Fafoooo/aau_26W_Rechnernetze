# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.1 zeige Fabio, Python-Version, echtes cwd und die Sprachgrundlagen.

"""Ü 1.1: Umgebung und kleine, ausführbare Beispiele der Sprachgrundlagen."""

import argparse
from pathlib import Path
import platform
import sys


def classify_number(number: int) -> str:
    """Zeige alle drei Zweige einer bedingten Entscheidung."""
    if number < 0:
        return "negativ"
    elif number == 0:
        return "null"
    else:
        return "positiv"


def language_demo() -> dict:
    """Erzeuge Beispiele, ohne persönliche Angaben wie ein Alter zu erfinden."""
    count = 3
    factor = 1.5
    enabled = True
    nothing = None
    topics = ["Text", "Bytes", "Threads"]
    numbered_topics = {}
    for index, topic in enumerate(topics, start=1):
        numbered_topics[index] = topic
    countdown = []
    remaining = count
    while remaining > 0:
        countdown.append(remaining)
        remaining -= 1
    return {
        "int": count,
        "float": factor,
        "bool": enabled,
        "NoneType": nothing,
        "str": topics[0],
        "list": topics,
        "dict": numbered_topics,
        "while-Ergebnis": countdown,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Fabio", help="Name (Standard: Fabio)")
    args = parser.parse_args(argv)
    print(f"Name: {args.name}")
    print(f"Python-Version: {platform.python_version()}")
    print(f"Arbeitsverzeichnis: {Path.cwd()}")
    print(f"Python-Interpreter: {sys.executable}")
    print(f"Virtuelle Umgebung: {sys.prefix != sys.base_prefix}")
    for label, value in language_demo().items():
        print(f"{label}: {value!r} (Typ: {type(value).__name__})")
    for number in [-1, 0, 1]:
        print(f"if/elif/else für {number}: {classify_number(number)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
