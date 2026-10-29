# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: Jede Teilaufgabe von Blatt08 aus echten gesicherten PCAPs erneut auswertbar machen.
"""Unprivilegierte CLI; liest Belege, erzeugt keinen Netzwerkverkehr."""
import argparse
import json
from pathlib import Path
from messen import analyse

BASE = Path(__file__).resolve().parent


def report(number, directory):
    result = analyse(directory)[number]
    if number in ("8.2", "8.3"):
        state = json.loads((directory / "results.json").read_text())["state"]
        prefix = "82_" if number == "8.2" else "83_"
        result = {**result, "gesicherter_zustand": {k: v for k, v in state.items() if k.startswith(prefix)}}
    return {"aufgabe": number, "quelle": "Eigene Linux-Bridge-PCAPs; keine Mininet-/OVS-Messung", "ergebnis": result}


def main(number):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--belege", type=Path, default=BASE / "nachweise/run01")
    args = parser.parse_args()
    print(json.dumps(report(number, args.belege), indent=2, ensure_ascii=False))
