# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.7 nutze begrenzte Queue, eigenen Producer, mehrere Consumer, Sentinels und joins.

"""Ü 1.7: Begrenzte Queue, blockierende Übergabe und kontrolliertes Ende."""

import argparse
import queue
import sys
import threading
from typing import NamedTuple


class ConsumerResult(NamedTuple):
    values: tuple[int, ...]
    total: int


def producer(work_queue, count, consumer_count):
    for value in range(1, count + 1):
        work_queue.put(value, block=True)
    for _ in range(consumer_count):
        work_queue.put(None, block=True)


def consumer(work_queue, results, index):
    values = []
    total = 0
    while True:
        item = work_queue.get(block=True)
        try:
            if item is None:
                results[index] = ConsumerResult(tuple(values), total)
                return
            values.append(item)
            total += item
        finally:
            work_queue.task_done()


def run_pipeline(count: int, consumers: int, maxsize: int) -> list[ConsumerResult]:
    for value, minimum, label in [(count, 0, "count"), (consumers, 1, "consumers"), (maxsize, 1, "maxsize")]:
        if type(value) is not int:
            raise TypeError(f"{label} muss int sein, nicht bool oder ein anderer Typ.")
        if value < minimum:
            raise ValueError(f"{label} muss mindestens {minimum} sein.")
    work_queue = queue.Queue(maxsize=maxsize)
    results = [None] * consumers
    threads = []
    for index in range(consumers):
        thread = threading.Thread(target=consumer, args=(work_queue, results, index), name=f"Consumer-{index + 1}")
        threads.append(thread)
        thread.start()
    producer_thread = threading.Thread(target=producer, args=(work_queue, count, consumers), name="Producer")
    producer_thread.start()
    producer_thread.join()
    work_queue.join()
    for thread in threads:
        thread.join()
    if any(result is None for result in results):
        raise RuntimeError("Ein Consumer hat kein Ergebnis geliefert.")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100, help="Erzeuge 1 bis count (0: keine Zahlen)")
    parser.add_argument("--consumers", type=int, default=3)
    parser.add_argument("--maxsize", type=int, default=8, help="Positive Queue-Kapazität")
    args = parser.parse_args(argv)
    try:
        results = run_pipeline(args.count, args.consumers, args.maxsize)
    except (TypeError, ValueError, RuntimeError) as error:
        print(f"Queue-Fehler: {error}", file=sys.stderr)
        return 1
    for index, result in enumerate(results, start=1):
        print(f"Consumer {index}: Anzahl={len(result.values)}; Summe={result.total}")
    total = sum(result.total for result in results)
    expected = args.count * (args.count + 1) // 2
    observed = sorted(value for result in results for value in result.values)
    exactly_once = observed == list(range(1, args.count + 1))
    print(f"Gesamtsumme: {total}; erwartet: {expected}")
    print(f"Alle Werte genau einmal: {exactly_once}")
    return 0 if total == expected and exactly_once else 1


if __name__ == "__main__":
    sys.exit(main())
