# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 und umfangreiche unittest-Tests;
# prüfe 1.3 mit Original-ZIP, echten CLI-/Permission-Fehlern und klar bezeichneten Mocks.

import contextlib
import io
import os
from pathlib import Path
import unittest
from unittest import mock
from zipfile import ZipFile

from support import ROOT, load_module, run_cli, temporary_directory

convert = load_module("ue1.3/convert.py", "ueb01_convert")


class ConvertTests(unittest.TestCase):
    def test_actual_zip_members_via_cli(self):
        with ZipFile(ROOT / "Angabe/utf8files.zip") as archive, temporary_directory() as directory:
            self.assertEqual(set(archive.namelist()), {"file1.txt", "file2.txt"})
            for name in archive.namelist():
                with self.subTest(member=name):
                    original = archive.read(name)
                    source = Path(directory) / name
                    target = Path(directory) / (name + ".out")
                    source.write_bytes(original)
                    process = run_cli("ue1.3/convert.py", source, target)
                    self.assertEqual(process.returncode, 0, process.stderr)
                    expected = original.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                    self.assertEqual(target.read_bytes(), expected)
                    self.assertEqual(source.read_bytes(), original)
                    self.assertEqual((ROOT / "Angabe" / name).read_bytes(), original)

    def test_mixed_line_endings_and_unicode(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes("ä\r\nb\rc\nd\r\n🌍".encode("utf-8"))
            count = convert.convert_file(source, target)
            self.assertEqual(target.read_bytes(), "ä\nb\nc\nd\n🌍".encode("utf-8"))
            self.assertEqual(count, 9)

    def test_empty_file(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"")
            self.assertEqual(convert.convert_file(source, target), 0)
            self.assertEqual(target.read_bytes(), b"")

    def test_existing_output_is_replaced(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"new")
            target.write_bytes(b"old longer text")
            convert.convert_file(source, target)
            self.assertEqual(target.read_bytes(), b"new")

    def test_invalid_utf8_preserves_existing_output(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"\xff\r\n")
            target.write_bytes(b"must stay intact")
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertIn("Ungültiges UTF-8", process.stderr)
            self.assertEqual(target.read_bytes(), b"must stay intact")

    def test_missing_input_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "missing", Path(directory) / "out"
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertIn("Dateifehler", process.stderr)
            self.assertFalse(target.exists())

    def test_same_path_cli_is_safe(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"preserved\r\n")
            process = run_cli("ue1.3/convert.py", source, source)
            self.assertEqual(process.returncode, 1)
            self.assertIn("verschieden", process.stderr)
            self.assertEqual(source.read_bytes(), b"preserved\r\n")

    def test_symlink_to_input_is_rejected(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "link"
            source.write_bytes(b"unchanged")
            try:
                target.symlink_to(source)
            except OSError as error:
                self.skipTest(f"Symlinks hier nicht möglich: {error}")
            with self.assertRaises(ValueError):
                convert.convert_file(source, target)
            self.assertEqual(source.read_bytes(), b"unchanged")

    def test_hardlink_to_input_is_rejected(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "hardlink"
            source.write_bytes(b"unchanged")
            try:
                target.hardlink_to(source)
            except OSError as error:
                self.skipTest(f"Hardlinks hier nicht möglich: {error}")
            process = run_cli("ue1.3/convert.py", source, target)
            self.assertEqual(process.returncode, 1)
            self.assertEqual(source.read_bytes(), b"unchanged")

    def test_missing_output_parent_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"abc")
            process = run_cli("ue1.3/convert.py", source, Path(directory) / "missing/out")
            self.assertEqual(process.returncode, 1)
            self.assertIn("Dateifehler", process.stderr)

    def test_directories_are_not_text_files_cli(self):
        with temporary_directory() as directory:
            source = Path(directory) / "in"
            source.write_bytes(b"abc")
            for infile, outfile in [(directory, source), (source, directory)]:
                with self.subTest(infile=infile):
                    process = run_cli("ue1.3/convert.py", infile, outfile)
                    self.assertEqual(process.returncode, 1)

    def test_missing_and_extra_parameters(self):
        for arguments in [(), ("in",), ("in", "out", "extra")]:
            with self.subTest(arguments=arguments):
                process = run_cli("ue1.3/convert.py", *arguments)
                self.assertEqual(process.returncode, 2)
                self.assertTrue(process.stderr)

    def test_real_unreadable_input_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"abc")
            source.chmod(0o000)
            try:
                if os.access(source, os.R_OK):
                    self.skipTest("Dieser Benutzer kann chmod(000)-Dateien trotzdem lesen.")
                process = run_cli("ue1.3/convert.py", source, target)
                self.assertEqual(process.returncode, 1)
                self.assertIn("Dateifehler", process.stderr)
                self.assertFalse(target.exists())
            finally:
                source.chmod(0o600)

    def test_real_unwritable_output_file_cli(self):
        with temporary_directory() as directory:
            source, target = Path(directory) / "in", Path(directory) / "out"
            source.write_bytes(b"new")
            target.write_bytes(b"preserved")
            target.chmod(0o400)
            try:
                if os.access(target, os.W_OK):
                    self.skipTest("Dieser Benutzer kann chmod(400)-Dateien trotzdem schreiben.")
                process = run_cli("ue1.3/convert.py", source, target)
                self.assertEqual(process.returncode, 1)
                self.assertEqual(target.read_bytes(), b"preserved")
            finally:
                target.chmod(0o600)

    def test_real_unwritable_output_directory_cli(self):
        with temporary_directory() as directory:
            source, parent = Path(directory) / "in", Path(directory) / "readonly"
            source.write_bytes(b"abc")
            parent.mkdir()
            parent.chmod(0o500)
            try:
                if os.access(parent, os.W_OK):
                    self.skipTest("Dieser Benutzer kann im chmod(500)-Ordner trotzdem schreiben.")
                process = run_cli("ue1.3/convert.py", source, parent / "out")
                self.assertEqual(process.returncode, 1)
                self.assertFalse((parent / "out").exists())
            finally:
                parent.chmod(0o700)

    def test_controlled_mock_read_permission_error(self):
        error_output = io.StringIO()
        with mock.patch.object(Path, "open", side_effect=PermissionError("MOCK: Lesen verweigert")):
            with contextlib.redirect_stderr(error_output):
                result = convert.main(["mock-in", "mock-out"])
        self.assertEqual(result, 1)
        self.assertIn("MOCK: Lesen verweigert", error_output.getvalue())

    def test_controlled_mock_write_error_closes_input(self):
        input_stream = io.StringIO("gültiger Text\n")
        error_output = io.StringIO()
        with mock.patch.object(Path, "open", side_effect=[input_stream, PermissionError("MOCK: Schreiben verweigert")]):
            with contextlib.redirect_stderr(error_output):
                result = convert.main(["mock-in", "mock-out"])
        self.assertEqual(result, 1)
        self.assertTrue(input_stream.closed)
        self.assertIn("MOCK: Schreiben verweigert", error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
