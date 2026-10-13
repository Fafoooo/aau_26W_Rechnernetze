# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.3 konvertiere UTF-8-Dateien mit LF-Ausgabe und geprüften Fehlerfällen.

"""Ü 1.3: UTF-8 kopieren und CRLF/CR/LF zu LF normalisieren."""

import argparse
from pathlib import Path
import sys


def convert_file(infile: str | Path, outfile: str | Path) -> int:
    source = Path(infile)
    destination = Path(outfile)
    same_path = source.resolve() == destination.resolve()
    same_inode = source.exists() and destination.exists() and source.samefile(destination)
    if same_path or same_inode:
        raise ValueError("Ein- und Ausgabedatei müssen verschieden sein (auch Links).")
    with source.open("r", encoding="utf-8", errors="strict", newline=None) as handle:
        text = handle.read()
    with destination.open("w", encoding="utf-8", errors="strict", newline="\n") as handle:
        handle.write(text)
    return len(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=Path, help="Eingabedatei mit UTF-8-Text")
    parser.add_argument("outfile", type=Path, help="Ausgabedatei mit UTF-8 und LF")
    args = parser.parse_args(argv)
    try:
        length = convert_file(args.infile, args.outfile)
    except UnicodeDecodeError as error:
        print(f"Ungültiges UTF-8 in {args.infile}: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"Dateifehler: {error}", file=sys.stderr)
        return 1
    print(f"{length} Unicode-Codepoints nach {args.outfile} geschrieben (UTF-8, LF).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
