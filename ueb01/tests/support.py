# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 mit umfangreichen Standardbibliothek-Tests;
# lade die Aufgabenmodule und führe echte CLIs mit lokalen, aufgeräumten Testdateien aus.

"""Testhilfen: Verzeichnisse mit Punkten laden und CLIs als eigene Prozesse starten."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / ".tmp"


def load_module(relative_path: str, module_name: str):
    if module_name in sys.modules:
        return sys.modules[module_name]
    specification = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    if specification is None or specification.loader is None:
        raise ImportError(f"Modul nicht ladbar: {relative_path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[module_name] = module
    specification.loader.exec_module(module)
    return module


def temporary_directory():
    SCRATCH.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=SCRATCH)


def run_cli(relative_path: str, *arguments, input_text=None, cwd=ROOT, timeout=20):
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / relative_path), *(str(arg) for arg in arguments)],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
        env=environment,
        timeout=timeout,
        check=False,
    )
