# KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.
# Datum: 2026-10-29
# Anfrage: Für Ü9.6 eine lesende CLI mit den verifizierten Originalbelegen bereitstellen.
"""Ü9.6: Belege ohne Rootrechte lesen; keine Konfiguration ändern."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-B", str(BASE / "auswertung.py"), "--task", "9.6", *sys.argv[1:]]))
