# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.7 auf genau-einmal-Verarbeitung, bounded Queue, Sentinels, finally und Hänger.

from collections import Counter
import queue
import threading
import unittest

from support import load_module, run_cli

pipeline = load_module("ue1.7/producer_consumer.py", "ueb01_pipeline")


class ProducerConsumerTests(unittest.TestCase):
    def test_every_value_exactly_once_across_consumers(self):
        for count in [0, 1, 17, 257]:
            for consumers in [1, 2, 5]:
                for maxsize in [1, 4]:
                    with self.subTest(count=count, consumers=consumers, maxsize=maxsize):
                        results = pipeline.run_pipeline(count, consumers, maxsize)
                        values = [value for result in results for value in result.values]
                        self.assertEqual(Counter(values), Counter(range(1, count + 1)))
                        self.assertEqual(len(results), consumers)
                        self.assertEqual(sum(result.total for result in results), count * (count + 1) // 2)
                        for result in results:
                            self.assertEqual(result.total, sum(result.values))

    def test_more_consumers_than_values(self):
        results = pipeline.run_pipeline(2, 7, 1)
        self.assertEqual(sum(len(result.values) for result in results), 2)
        self.assertEqual(sum(result.total for result in results), 3)

    def test_producer_blocks_until_full_queue_is_drained(self):
        work_queue = queue.Queue(maxsize=1)
        work_queue.put(99)
        entered, finished = threading.Event(), threading.Event()

        def run_producer():
            entered.set()
            pipeline.producer(work_queue, 1, 1)
            finished.set()

        thread = threading.Thread(target=run_producer)
        thread.start()
        self.assertTrue(entered.wait(2))
        self.assertFalse(finished.wait(0.03))
        for expected in [99, 1, None]:
            self.assertEqual(work_queue.get(timeout=2), expected)
            work_queue.task_done()
        work_queue.join()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertTrue(finished.is_set())

    def test_consumer_waits_for_data_and_stops_on_sentinel(self):
        work_queue = queue.Queue(maxsize=1)
        results = [None]
        thread = threading.Thread(target=pipeline.consumer, args=(work_queue, results, 0))
        thread.start()
        self.assertTrue(thread.is_alive())
        work_queue.put(7, timeout=2)
        work_queue.put(None, timeout=2)
        work_queue.join()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(results[0], ((7,), 7))

    def test_task_done_even_when_processing_raises(self):
        work_queue = queue.Queue(maxsize=1)
        work_queue.put(object())
        with self.assertRaises(TypeError):
            pipeline.consumer(work_queue, [None], 0)
        self.assertEqual(work_queue.unfinished_tasks, 0)
        work_queue.join()

    def test_invalid_counts_consumers_and_queue_sizes(self):
        for arguments in [(-1, 1, 1), (0, 0, 1), (0, -1, 1), (0, 1, 0), (0, 1, -1)]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                pipeline.run_pipeline(*arguments)
        for arguments in [(True, 1, 1), (1, False, 1), (1, 1, True), (1.5, 1, 1), (1, "2", 1), (1, 1, None)]:
            with self.subTest(arguments=arguments), self.assertRaises(TypeError):
                pipeline.run_pipeline(*arguments)

    def test_cli_multiple_consumers_with_size_one_finishes(self):
        process = run_cli("ue1.7/producer_consumer.py", "--count", 257, "--consumers", 4, "--maxsize", 1, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Gesamtsumme: 33153; erwartet: 33153", process.stdout)
        self.assertIn("Alle Werte genau einmal: True", process.stdout)
        self.assertEqual(process.stdout.count("Consumer "), 4)

    def test_cli_zero_count_finishes_all_consumers(self):
        process = run_cli("ue1.7/producer_consumer.py", "--count", 0, "--consumers", 5, "--maxsize", 1, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.count("Anzahl=0; Summe=0"), 5)
        self.assertIn("Alle Werte genau einmal: True", process.stdout)

    def test_cli_default(self):
        process = run_cli("ue1.7/producer_consumer.py")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Gesamtsumme: 5050; erwartet: 5050", process.stdout)

    def test_cli_invalid_numbers(self):
        for arguments in [("--count", "-1"), ("--consumers", "0"), ("--maxsize", "0")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.7/producer_consumer.py", *arguments)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Queue-Fehler", process.stderr)
        self.assertEqual(run_cli("ue1.7/producer_consumer.py", "--count", "x").returncode, 2)


if __name__ == "__main__":
    unittest.main()
