# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.5 berechne eigene Slices/Result-Slots mit n Threads und vergleiche sequentiell.

"""Ü 1.5: Eigene Eingabebereiche und Ergebnisplätze pro Thread."""

import argparse
import math
import sys
import threading
import time

from calculation import DEFAULT_ITERATIONS, complicated_calculation, load_values, positive_int
from calculation import split_ranges, validate_positive_integer


def worker(values, start, end, results, index, iterations, errors):
    try:
        results[index] = complicated_calculation(values[start:end], iterations)
    except Exception as error:
        errors[index] = error


def run_parallel(values: list[float], number_of_threads: int, iterations: int = DEFAULT_ITERATIONS):
    validate_positive_integer(iterations, "iterations")
    ranges = split_ranges(len(values), number_of_threads)
    results = [None] * number_of_threads
    errors = [None] * number_of_threads
    threads = []
    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=worker,
            args=(values, start, end, results, index, iterations, errors),
            name=f"Rechner-{index + 1}",
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    for error in errors:
        if error is not None:
            raise RuntimeError("Berechnung in einem Thread fehlgeschlagen.") from error
    ordered_results = []
    for partial in results:
        if partial is None:
            raise RuntimeError("Ein Thread hat kein Ergebnis geliefert.")
        ordered_results.extend(partial)
    return ordered_results, ranges


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", help="UTF-8-Datei: Floats durch Leerraum getrennt")
    parser.add_argument("--threads", type=positive_int, default=4)
    parser.add_argument("--iterations", type=positive_int, default=DEFAULT_ITERATIONS)
    args = parser.parse_args(argv)
    try:
        values = load_values(args.infile)
        started = time.perf_counter()
        expected = complicated_calculation(values, args.iterations)
        sequential_time = time.perf_counter() - started
        started = time.perf_counter()
        actual, ranges = run_parallel(values, args.threads, args.iterations)
        threaded_time = time.perf_counter() - started
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"Berechnungsfehler: {error}", file=sys.stderr)
        return 1
    print(f"Werte: {len(values)}; Threads: {args.threads}; Iterationen pro Wert: {args.iterations}")
    for index, (start, end) in enumerate(ranges, start=1):
        print(f"Thread {index}: [{start}, {end}) -> {end - start} Werte")
    print(f"Sequentiell: Summe={math.fsum(expected):.12f}; Zeit={sequential_time:.6f} s")
    print(f"Threads:     Summe={math.fsum(actual):.12f}; Zeit={threaded_time:.6f} s")
    print(f"Identische Einzelwerte: {actual == expected}")
    print("GIL: CPU-Arbeit mit Threads ist auf gewöhnlichem CPython nicht automatisch schneller.")
    return 0 if actual == expected else 1


if __name__ == "__main__":
    sys.exit(main())
