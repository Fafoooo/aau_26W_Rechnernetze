# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.1 einschließlich echtem cwd, Fabio, Name-CLI und allen Sprachbeispielen.

import contextlib
import io
from pathlib import Path
import platform
import sys
import unittest

from support import load_module, run_cli, temporary_directory

hello = load_module("ue1.1/hello.py", "ueb01_hello")


class HelloTests(unittest.TestCase):
    def test_all_conditional_branches(self):
        for number, expected in [(-100, "negativ"), (0, "null"), (100, "positiv")]:
            with self.subTest(number=number):
                self.assertEqual(hello.classify_number(number), expected)

    def test_types_and_loop_results(self):
        result = hello.language_demo()
        for label, expected_type in [("int", int), ("float", float), ("bool", bool), ("str", str), ("list", list), ("dict", dict)]:
            with self.subTest(label=label):
                self.assertIs(type(result[label]), expected_type)
        self.assertIsNone(result["NoneType"])
        self.assertEqual(result["dict"], {1: "Text", 2: "Bytes", 3: "Threads"})
        self.assertEqual(result["while-Ergebnis"], [3, 2, 1])

    def test_default_name_version_and_actual_cwd(self):
        with temporary_directory() as directory:
            process = run_cli("ue1.1/hello.py", cwd=directory)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("Name: Fabio", process.stdout)
            self.assertIn(f"Python-Version: {platform.python_version()}", process.stdout)
            self.assertIn(f"Arbeitsverzeichnis: {Path(directory)}", process.stdout)
            self.assertIn(f"Virtuelle Umgebung: {sys.prefix != sys.base_prefix}", process.stdout)

    def test_name_override(self):
        process = run_cli("ue1.1/hello.py", "--name", "Fabio Grüß")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Name: Fabio Grüß", process.stdout)

    def test_main_return_value(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(hello.main(["--name", "Test"]), 0)
        self.assertIn("Name: Test", output.getvalue())

    def test_help(self):
        process = run_cli("ue1.1/hello.py", "--help")
        self.assertEqual(process.returncode, 0)
        self.assertIn("--name", process.stdout)

    def test_unknown_argument(self):
        process = run_cli("ue1.1/hello.py", "--unknown")
        self.assertEqual(process.returncode, 2)
        self.assertTrue(process.stderr)


if __name__ == "__main__":
    unittest.main()
