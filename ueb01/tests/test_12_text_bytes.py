# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.2 mit Unicode, Eingabe/CLI, Längen, Roundtrip und falschen Kodierungen.

import unittest

from support import load_module, run_cli

text_bytes = load_module("ue1.2/text_bytes.py", "ueb01_text_bytes")


class TextBytesTests(unittest.TestCase):
    def test_fixed_utf8_vectors_and_roundtrip(self):
        vectors = [("", b""), ("ABC", b"ABC"), ("ä", b"\xc3\xa4"), ("🌍", b"\xf0\x9f\x8c\x8d"), ("e\u0301", b"e\xcc\x81")]
        for text, expected in vectors:
            with self.subTest(text=text):
                data, decoded = text_bytes.encode_and_decode(text)
                self.assertIs(type(data), bytes)
                self.assertIs(type(decoded), str)
                self.assertEqual(data, expected)
                self.assertEqual(decoded, text)

    def test_nonlatin_and_embedded_newlines(self):
        text = "漢字\nGrüße\x00🌍"
        data, decoded = text_bytes.encode_and_decode(text)
        self.assertEqual(decoded, text)
        self.assertGreater(len(data), len(text))

    def test_rejects_non_string(self):
        for value in [b"abc", None, 123, True]:
            with self.subTest(value=value), self.assertRaises(TypeError):
                text_bytes.encode_and_decode(value)

    def test_unpaired_surrogate_is_rejected(self):
        with self.assertRaises(UnicodeEncodeError):
            text_bytes.encode_and_decode("\ud800")

    def test_unicode_cli(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "Grüße 🌍")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Unicode-Codepoints: 7", process.stdout)
        self.assertIn("len(bytes), Bytes: 12", process.stdout)
        self.assertIn("Roundtrip identisch: True", process.stdout)

    def test_interactive_input(self):
        process = run_cli("ue1.2/text_bytes.py", input_text="Netzwerk ä\n")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Netzwerk ä", process.stdout)

    def test_explicit_empty_text_does_not_prompt(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("len(bytes), Bytes: 0", process.stdout)

    def test_eof_is_reported(self):
        process = run_cli("ue1.2/text_bytes.py", input_text="")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Eingabe-/Kodierungsfehler", process.stderr)

    def test_latin1_produces_mojibake(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "ä", "--decode-as", "latin-1")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Dekodiert mit latin-1: 'Ã¤'", process.stdout)
        self.assertIn("Auch damit identisch: False", process.stdout)

    def test_ascii_cannot_decode_umlaut(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "ä", "--decode-as", "ascii")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Dekodierungsfehler (ascii)", process.stderr)

    def test_unknown_encoding_is_reported(self):
        process = run_cli("ue1.2/text_bytes.py", "--text", "x", "--decode-as", "no-such-encoding")
        self.assertEqual(process.returncode, 1)
        self.assertIn("Dekodierungsfehler", process.stderr)

    def test_missing_text_option_value(self):
        process = run_cli("ue1.2/text_bytes.py", "--text")
        self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
