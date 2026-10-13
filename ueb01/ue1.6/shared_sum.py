# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.6 miss naive und Lock-Summen mehrfach; kennzeichne erzwungene Lost Updates separat.

"""Ü 1.6: Gemeinsame Summe, kurzer Lock und separate Interleaving-Demonstration."""

import argparse
import math
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ue1.5"))
from calculation import DEFAULT_ITERATIONS, complicated_calculation, load_values, positive_int
from calculation import split_ranges, validate_positive_integer


def run_shared(values, number_of_threads, iterations=DEFAULT_ITERATIONS, mode="naive", delay=0.001):
    validate_positive_integer(iterations, "iterations")
    ranges = split_ranges(len(values), number_of_threads)
    if mode not in ("naive", "lock", "forced"):
        raise ValueError("mode muss naive, lock oder forced sein.")
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay muss endlich und mindestens 0 sein.")
    shared = [0.0]
    lock = threading.Lock()
    barrier = threading.Barrier(number_of_threads, timeout=10) if mode == "forced" else None
    errors = [None] * number_of_threads

    def worker(index, start, end):
        try:
            subtotal = math.fsum(complicated_calculation(values[start:end], iterations))
            if mode == "lock":
                with lock:
                    shared[0] += subtotal
            elif mode == "naive":
                shared[0] += subtotal
            else:
                snapshot = shared[0]
                barrier.wait()
                time.sleep(delay)
                shared[0] = snapshot + subtotal
        except Exception as error:
            errors[index] = error
            if barrier is not None:
                barrier.abort()

    threads = []
    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(index, start, end), name=f"Summe-{index + 1}")
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    for error in errors:
        if error is not None:
            raise RuntimeError("Gemeinsame Berechnung in einem Thread fehlgeschlagen.") from error
    return shared[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", help="Dieselbe Float-Datei wie in Ü 1.5")
    parser.add_argument("--threads", type=positive_int, default=4)
    parser.add_argument("--iterations", type=positive_int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--runs", type=positive_int, default=5)
    parser.add_argument("--mode", choices=["naive", "lock", "forced", "all"], default="all")
    parser.add_argument("--delay", type=float, default=0.001, help="Sleep nur in forced, in Sekunden")
    args = parser.parse_args(argv)
    modes = ("naive", "lock", "forced") if args.mode == "all" else (args.mode,)
    locked_ok = True
    try:
        values = load_values(args.infile)
        expected = math.fsum(complicated_calculation(values, args.iterations))
        print(f"Werte: {len(values)}; Threads: {args.threads}; Iterationen: {args.iterations}")
        print("naive: direktes +=; eine Abweichung ist nicht garantiert.")
        print("forced: didaktisch erzwungenes read/barrier/sleep/write; keine naive +=-Messung.")
        for mode in modes:
            for run in range(1, args.runs + 1):
                started = time.perf_counter()
                actual = run_shared(values, args.threads, args.iterations, mode, args.delay)
                elapsed = time.perf_counter() - started
                matches = math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
                print(
                    f"{mode} Lauf {run}: erwartet={expected:.12f}; gemessen={actual:.12f}; "
                    f"Differenz={actual - expected:.12f}; {'OK' if matches else 'ABWEICHUNG'}; "
                    f"Zeit={elapsed:.6f} s"
                )
                if mode == "lock" and not matches:
                    locked_ok = False
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"Summenfehler: {error}", file=sys.stderr)
        return 1
    return 0 if locked_ok else 1


if __name__ == "__main__":
    sys.exit(main())
