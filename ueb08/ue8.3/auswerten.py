# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: Ü8.3 aus den gesicherten eigenen Ethernet-/ARP-/Router-/HTTP-Belegen auswerten.
"""Offline-Einstieg zu Ü8.3; Einzelheiten in antwort.md."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from auswertung import main

if __name__ == "__main__":
    main("8.3")
