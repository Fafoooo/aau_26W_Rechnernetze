# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.5 mit sequenzieller Referenz, Restslices, n>len, leerer und fehlerhafter Eingabe.

import argparse
import math
from pathlib import Path
import sys
import unittest

from support import ROOT, load_module, run_cli, temporary_directory

calculation = load_module("ue1.5/calculation.py", "calculation")
threads = load_module("ue1.5/threads.py", "ueb01_threads")


class CalculationTests(unittest.TestCase):
    def test_first_iteration_reference(self):
        self.assertEqual(calculation.complicated_calculation([0.0], 1), [0.5])
        self.assertEqual(calculation.complicated_calculation([], 7), [])

    def test_deterministic_finite_calculation(self):
        values = [-1.0, 0.0, 0.125, 4.5, sys.float_info.max]
        original = values[:]
        first = calculation.complicated_calculation(values, 100)
        second = calculation.complicated_calculation(values, 100)
        self.assertEqual(first, second)
        self.assertEqual(values, original)
        self.assertEqual(len(first), len(values))
        self.assertTrue(all(math.isfinite(value) for value in first))

    def test_all_small_range_partitions(self):
        for length in range(13):
            for count in range(1, 17):
                with self.subTest(length=length, threads=count):
                    ranges = calculation.split_ranges(length, count)
                    indices = [index for start, end in ranges for index in range(start, end)]
                    sizes = [end - start for start, end in ranges]
                    self.assertEqual(len(ranges), count)
                    self.assertEqual(indices, list(range(length)))
                    self.assertLessEqual(max(sizes) - min(sizes), 1)
                    self.assertEqual(ranges[0][0], 0)
                    self.assertEqual(ranges[-1][1], length)

    def test_explicit_remainder_empty_and_excess_threads(self):
        self.assertEqual(calculation.split_ranges(7, 3), [(0, 3), (3, 5), (5, 7)])
        self.assertEqual(calculation.split_ranges(2, 4), [(0, 1), (1, 2), (2, 2), (2, 2)])
        self.assertEqual(calculation.split_ranges(0, 2), [(0, 0), (0, 0)])

    def test_invalid_integer_inputs(self):
        for value, error in [(0, ValueError), (-1, ValueError), (True, TypeError), (1.5, TypeError), (None, TypeError)]:
            with self.subTest(value=value), self.assertRaises(error):
                calculation.validate_positive_integer(value, "test")
        for length, error in [(-1, ValueError), (True, TypeError), (1.5, TypeError)]:
            with self.subTest(length=length), self.assertRaises(error):
                calculation.split_ranges(length, 2)

    def test_cli_integer_parser(self):
        self.assertEqual(calculation.positive_int("3"), 3)
        for value in ["0", "-1", "1.5", "text"]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                calculation.positive_int(value)

    def test_invalid_iterations_and_nonfinite_values(self):
        for iterations, error in [(0, ValueError), (-1, ValueError), (True, TypeError)]:
            with self.subTest(iterations=iterations), self.assertRaises(error):
                calculation.complicated_calculation([0.0], iterations)
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculation.complicated_calculation([value], 1)

    def test_load_whitespace_floats_and_universal_newlines(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            source.write_bytes(b"1.0 2.5\r\n\t-0.3\r1e2\n\n")
            self.assertEqual(calculation.load_values(source), [1.0, 2.5, -0.3, 100.0])
            source.write_bytes(b" \r\n\t")
            self.assertEqual(calculation.load_values(source), [])

    def test_invalid_file_values_include_line_number(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            for token in ["oops", "nan", "inf", "-inf", "1e999"]:
                source.write_text(f"1.0\n{token}\n", encoding="utf-8")
                with self.subTest(token=token), self.assertRaisesRegex(ValueError, "Zeile 2"):
                    calculation.load_values(source)


class ThreadTests(unittest.TestCase):
    def test_parallel_matches_sequential_and_preserves_order(self):
        values = calculation.load_values(ROOT / "ue1.5/werte.txt")
        expected = calculation.complicated_calculation(values, 100)
        for count in [1, 2, 4, 20]:
            with self.subTest(threads=count):
                actual, ranges = threads.run_parallel(values, count, 100)
                self.assertEqual(actual, expected)
                self.assertEqual(len(ranges), count)

    def test_empty_array(self):
        actual, ranges = threads.run_parallel([], 3, 1)
        self.assertEqual(actual, [])
        self.assertEqual(ranges, [(0, 0)] * 3)

    def test_worker_owns_one_result_slot(self):
        results, errors = [None, None, None], [None, None, None]
        threads.worker([0.0, 0.0, 0.0], 1, 2, results, 1, 1, errors)
        self.assertEqual(results, [None, [0.5], None])
        self.assertEqual(errors, [None, None, None])

    def test_worker_error_reaches_caller(self):
        with self.assertRaises(RuntimeError) as raised:
            threads.run_parallel([math.nan, 0.0], 2, 1)
        self.assertIsInstance(raised.exception.__cause__, ValueError)

    def test_invalid_thread_count_and_iterations(self):
        for count, iterations in [(0, 1), (-1, 1), (1, 0)]:
            with self.subTest(count=count, iterations=iterations), self.assertRaises(ValueError):
                threads.run_parallel([], count, iterations)

    def test_real_cli_reports_ranges_times_and_agreement(self):
        process = run_cli("ue1.5/threads.py", ROOT / "ue1.5/werte.txt", "--threads", 4, "--iterations", 50)
        self.assertEqual(process.returncode, 0, process.stderr)
        for text in ["[0, 3)", "[3, 5)", "[5, 7)", "[7, 9)", "Zeit=", "Identische Einzelwerte: True", "GIL"]:
            self.assertIn(text, process.stdout)

    def test_empty_file_cli_with_more_threads(self):
        with temporary_directory() as directory:
            source = Path(directory) / "empty"
            source.write_bytes(b"")
            process = run_cli("ue1.5/threads.py", source, "--threads", 5, "--iterations", 1)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("Werte: 0", process.stdout)
            self.assertIn("Summe=0.000000000000", process.stdout)

    def test_invalid_cli_parameters(self):
        for arguments in [(), ("file", "--threads", "0"), ("file", "--iterations", "0"), ("file", "--threads", "x")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.5/threads.py", *arguments)
                self.assertEqual(process.returncode, 2)

    def test_file_errors_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "values"
            for raw in [b"oops", b"nan", b"\xff"]:
                source.write_bytes(raw)
                process = run_cli("ue1.5/threads.py", source, "--iterations", 1)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Berechnungsfehler", process.stderr)
            source.unlink()
            self.assertEqual(run_cli("ue1.5/threads.py", source).returncode, 1)


if __name__ == "__main__":
    unittest.main()
