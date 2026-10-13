# KI-Kennzeichnung: Mit KI erstellt; keine Eigenleistung behauptet.
# Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol;
# Provider laut hermes status: ChatGPT or Codex Subscription.
# Implementierung: Codex CLI 0.162.1; Modell gpt-6.1-sol; Datum: 2026-10-13.
# Anfrage: Implementiere Übungsblatt 01 vollständig mit Standardbibliothek;
# für 1.2 lies Text, zeige UTF-8-Bytes, Längen, Roundtrip und Fehlkodierung.

"""Ü 1.2: Text eingeben, UTF-8 kodieren und wieder dekodieren."""

import argparse
import sys


def encode_and_decode(text: str) -> tuple[bytes, str]:
    if not isinstance(text, str):
        raise TypeError("text muss eine Zeichenkette (str) sein.")
    data = text.encode("utf-8")
    decoded = data.decode("utf-8")
    return data, decoded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Text; ohne dieses Argument wird input() verwendet")
    parser.add_argument("--decode-as", help="Zusätzlicher Versuch mit dieser Kodierung")
    args = parser.parse_args(argv)
    try:
        text = args.text if args.text is not None else input("Text: ")
        data, decoded = encode_and_decode(text)
    except (EOFError, UnicodeError) as error:
        print(f"Eingabe-/Kodierungsfehler: {error}", file=sys.stderr)
        return 1
    print(f"str: {text!r}")
    print(f"bytes: {data!r}")
    print(f"len(str), Unicode-Codepoints: {len(text)}")
    print(f"len(bytes), Bytes: {len(data)}")
    print(f"UTF-8 dekodiert: {decoded!r}")
    print(f"Roundtrip identisch: {decoded == text}")
    if args.decode_as is not None:
        try:
            other = data.decode(args.decode_as)
        except (UnicodeError, LookupError) as error:
            print(f"Dekodierungsfehler ({args.decode_as}): {error}", file=sys.stderr)
            return 1
        print(f"Dekodiert mit {args.decode_as}: {other!r}")
        print(f"Auch damit identisch: {other == text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
