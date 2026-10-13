# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# teile für 1.5/1.6 dieselbe deterministische Berechnung, Eingabe und Slice-Aufteilung.

"""Gemeinsame Berechnung und Eingabeprüfung für Ü 1.5 und Ü 1.6."""

import argparse
import math
from pathlib import Path


DEFAULT_ITERATIONS = 20000


def validate_positive_integer(value: int, label: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{label} muss int sein, nicht bool oder ein anderer Typ.")
    if value < 1:
        raise ValueError(f"{label} muss mindestens 1 sein.")


def positive_int(text: str) -> int:
    try:
        value = int(text)
        validate_positive_integer(value, "Wert")
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value


def load_values(filename: str | Path) -> list[float]:
    values = []
    with Path(filename).open("r", encoding="utf-8", newline=None) as handle:
        for line_number, line in enumerate(handle, start=1):
            for token in line.split():
                try:
                    value = float(token)
                except ValueError as error:
                    raise ValueError(f"Zeile {line_number}: keine Gleitkommazahl: {token!r}") from error
                if not math.isfinite(value):
                    raise ValueError(f"Zeile {line_number}: Wert muss endlich sein: {token!r}")
                values.append(value)
    return values


def complicated_calculation(values: list[float], iterations: int = DEFAULT_ITERATIONS) -> list[float]:
    validate_positive_integer(iterations, "iterations")
    results = []
    for value in values:
        if not math.isfinite(value):
            raise ValueError("Alle Eingabewerte müssen endlich sein.")
        seed = math.sin(value)
        state = seed
        for _ in range(iterations):
            state = math.sin(state) + 0.5 * math.cos(state + seed)
        results.append(state)
    return results


def split_ranges(length: int, number_of_threads: int) -> list[tuple[int, int]]:
    validate_positive_integer(number_of_threads, "number_of_threads")
    if type(length) is not int:
        raise TypeError("length muss int sein.")
    if length < 0:
        raise ValueError("length darf nicht negativ sein.")
    base, remainder = divmod(length, number_of_threads)
    ranges = []
    start = 0
    for index in range(number_of_threads):
        end = start + base + (1 if index < remainder else 0)
        ranges.append((start, end))
        start = end
    return ranges
