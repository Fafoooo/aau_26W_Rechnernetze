# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts,
# mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
"""Unittest-Treiber: Reproduktion, unabhängige Proben und vollständige Zeilenerklärung."""
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = tuple(ROOT / relative for relative in ("ue6.4/subnetting.py", "ue6.5/dijkstra.py", "ue6.6/distance_vector.py"))
SUBNET, DIJKSTRA, DV = (runpy.run_path(str(script)) for script in SCRIPTS)

class ExerciseTests(unittest.TestCase):
    def test_all_embedded_verifications(self):
        SUBNET["verify"](SUBNET["allocate"]())
        graph = DIJKSTRA["graph_from"](DIJKSTRA["EDGES"])
        DIJKSTRA["verify"](graph, *DIJKSTRA["dijkstra"](graph, "A"))
        DV["verify"](DV["asynchronous"](), DV["synchronous"]())

    def test_generated_answers(self):
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout, script.with_name("antwort.md").read_text(encoding="utf-8"))

    def test_sources_compile_and_marked(self):
        for script in SCRIPTS + (Path(__file__),):
            source = script.read_text(encoding="utf-8")
            compile(source, str(script), "exec")
            self.assertTrue(source.startswith("# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol"))
            self.assertIn("Datum: 2026-10-29", source)
        for script in SCRIPTS:
            notice = script.with_name("antwort.md").read_text(encoding="utf-8").rsplit("## KI-Kennzeichnung", 1)[1]
            self.assertIn("Tatsächliche Anfrage:", notice)
            self.assertIn("2026-10-29", notice)

    def test_explanation_line_coverage(self):
        text = (ROOT / "erklaerung_algorithmen.md").read_text(encoding="utf-8")
        headings = ("## 6.4 –", "## 6.5 –", "## 6.6 –", "## Tests –")
        for index, script in enumerate(SCRIPTS + (Path(__file__),)):
            section = text.split(headings[index], 1)[1].split("\n## ", 1)[0]
            documented = [int(number) for number in re.findall(r"^- \*\*Z\. (\d+):\*\*", section, re.MULTILINE)]
            expected = [number for number, line in enumerate(script.read_text().splitlines(), 1) if line.strip()]
            self.assertEqual(documented, expected, script.name)

    def test_mutation_detection(self):
        graph = DIJKSTRA["graph_from"](DIJKSTRA["EDGES"])
        distance, predecessor, trace = DIJKSTRA["dijkstra"](graph, "A")
        distance["F"] += 1
        with self.assertRaises(AssertionError):
            DIJKSTRA["verify"](graph, distance, predecessor, trace)

    def test_dv_schedule_and_intermediates(self):
        asynchronous = DV["asynchronous"]()
        synchronous = DV["synchronous"]()
        self.assertEqual(asynchronous[2][1][3]["D"], 17)
        self.assertEqual(asynchronous[2][2][3]["D"], 11)
        self.assertEqual(len(asynchronous[3]), 42)
        self.assertEqual(len(synchronous[2]) - 1, 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)
