# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.6 mit echten Wiederholungen, Lock, separatem erzwungenem Interleaving und Randfällen.

import math
from pathlib import Path
import unittest

from support import ROOT, load_module, run_cli, temporary_directory

calculation = load_module("ue1.5/calculation.py", "calculation")
shared_sum = load_module("ue1.6/shared_sum.py", "ueb01_shared_sum")


class SharedSumTests(unittest.TestCase):
    def setUp(self):
        self.values = calculation.load_values(ROOT / "ue1.5/werte.txt")
        self.expected = math.fsum(calculation.complicated_calculation(self.values, 50))

    def test_exact_same_calculation_module_as_15(self):
        self.assertIs(shared_sum.complicated_calculation, calculation.complicated_calculation)

    def test_lock_matches_reference_in_ten_real_runs(self):
        for run in range(10):
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "lock")
                self.assertTrue(math.isclose(actual, self.expected, rel_tol=1e-12, abs_tol=1e-12))

    def test_naive_ten_real_runs_without_assuming_a_race(self):
        for run in range(10):
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "naive")
                self.assertTrue(math.isfinite(actual))

    def test_forced_lost_updates_in_five_real_runs(self):
        ranges = calculation.split_ranges(len(self.values), 4)
        partials = [math.fsum(calculation.complicated_calculation(self.values[start:end], 50)) for start, end in ranges]
        for run in range(5):
            with self.subTest(run=run):
                actual = shared_sum.run_shared(self.values, 4, 50, "forced", 0.001)
                self.assertFalse(math.isclose(actual, self.expected, rel_tol=1e-12, abs_tol=1e-12))
                self.assertIn(actual, partials)

    def test_empty_arrays_in_all_modes(self):
        for mode in ["naive", "lock", "forced"]:
            with self.subTest(mode=mode):
                self.assertEqual(shared_sum.run_shared([], 3, 1, mode, 0), 0.0)

    def test_one_thread_in_all_modes(self):
        for mode in ["naive", "lock", "forced"]:
            with self.subTest(mode=mode):
                actual = shared_sum.run_shared(self.values, 1, 50, mode, 0)
                self.assertEqual(actual, self.expected)

    def test_lock_with_more_threads_than_values(self):
        actual = shared_sum.run_shared([0.0], 5, 1, "lock")
        self.assertEqual(actual, 0.5)

    def test_invalid_modes_counts_iterations_and_delay(self):
        cases = [(0, 1, "lock", 0), (1, 0, "lock", 0), (1, 1, "bad", 0), (1, 1, "forced", -0.1), (1, 1, "forced", math.nan), (1, 1, "forced", math.inf)]
        for count, iterations, mode, delay in cases:
            with self.subTest(case=(count, iterations, mode, delay)), self.assertRaises(ValueError):
                shared_sum.run_shared([], count, iterations, mode, delay)

    def test_worker_error_aborts_barrier_and_reaches_caller(self):
        with self.assertRaises(RuntimeError) as raised:
            shared_sum.run_shared([math.nan, 0.0], 4, 1, "forced", 0)
        self.assertIsInstance(raised.exception.__cause__, ValueError)

    def test_cli_three_real_runs_of_each_mode(self):
        process = run_cli("ue1.6/shared_sum.py", ROOT / "ue1.5/werte.txt", "--iterations", 50, "--runs", 3)
        self.assertEqual(process.returncode, 0, process.stderr)
        for mode in ["naive", "lock", "forced"]:
            self.assertEqual(process.stdout.count(f"{mode} Lauf"), 3)
        self.assertIn("didaktisch erzwungenes", process.stdout)
        self.assertIn("keine naive +=-Messung", process.stdout)
        for line in process.stdout.splitlines():
            if line.startswith("lock Lauf"):
                self.assertIn("; OK;", line)
            if line.startswith("forced Lauf"):
                self.assertIn("ABWEICHUNG", line)

    def test_empty_input_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "empty"
            source.write_bytes(b"")
            process = run_cli("ue1.6/shared_sum.py", source, "--threads", 5, "--iterations", 1, "--runs", 2)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertNotIn("ABWEICHUNG", process.stdout)

    def test_invalid_cli_arguments(self):
        for arguments in [(), ("file", "--runs", "0"), ("file", "--threads", "0"), ("file", "--mode", "bad")]:
            with self.subTest(arguments=arguments):
                self.assertEqual(run_cli("ue1.6/shared_sum.py", *arguments).returncode, 2)

    def test_cli_missing_file_and_invalid_delay(self):
        self.assertEqual(run_cli("ue1.6/shared_sum.py", ROOT / ".tmp/nonexistent-input").returncode, 1)
        process = run_cli("ue1.6/shared_sum.py", ROOT / "ue1.5/werte.txt", "--iterations", 1, "--delay", "-1")
        self.assertEqual(process.returncode, 1)
        self.assertIn("delay", process.stderr)


if __name__ == "__main__":
    unittest.main()
