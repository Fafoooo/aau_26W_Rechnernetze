# Ü 1.4 – Binäre Daten und Protokollnachrichten

## Ausführung

Vom Ordner `ueb01` aus:

```bash
python -B ue1.4/protocol.py
python -B ue1.4/protocol.py --data --urgent --sequence 65535 --payload 'ä'
python -B ue1.4/protocol.py --message-hex '10 00 00 2a 00 00 00 05 68 65 6c 6c 6f'
```

Für den Zugriff aus Python gibt es exakt die verlangten Funktionen
`create_message(is_data, is_urgent, sequence_number, payload)` und
`parse_message(message)`. Letztere liefert ein NamedTuple mit den vier
ursprünglichen Feldern; es kann wie ein Tuple verglichen und entpackt werden.
Es gilt für gültige Felder: `parse_message(create_message(*fields)) == fields`.

## Format und Begründung

Die Angabe verlangt Implementierung und Tests, keine zusätzlichen
Fragen. Netzwerkbit 0 bezeichnet das **höchstwertige** Bit der ersten Zeile.

| Netzwerkbits | Größe | Feld | Speicherung |
|---|---:|---|---|
| 0..4 | 5 Bit | Version V | immer 2, in den höchsten fünf Bits des ersten Worts |
| 5..13 | 9 Bit | Reserved | immer 0 |
| 14 | 1 Bit | D | lokales Bit 1 im ersten 16-Bit-Wort |
| 15 | 1 Bit | U | lokales Bit 0 im ersten 16-Bit-Wort |
| 16..31 | 16 Bit | Sequenznummer | Big Endian |
| zweite Zeile | 32 Bit | Payload-Länge | Big Endian, Anzahl der Bytes |
| anschließend | variabel | Payload | unverändert angehängte Bytes |

**Big Endian / Network Byte Order** bedeutet, dass das höchstwertige Byte
zuerst gespeichert wird: 42 als uint16 ist `00 2a`, 256 ist `01 00`.
`struct.Struct("!HHI")` verwendet `!` für Netzwerkbytefolge und standardisierte
Größen ohne Füllbytes, zwei `H` für jeweils unsigned 16 Bit und `I` für
unsigned 32 Bit. Der Header ist damit genau 8 Bytes lang.

Das erste Wort wird so gebildet:

```python
word = (2 << 11) | (int(is_data) << 1) | int(is_urgent)
```

`<<` verschiebt Bits nach links, `|` setzt die getrennten Bitfelder zusammen.
Version 2 ist binär `00010`; mit elf Stellen Abstand zu den unteren Feldern
ergibt sie `0x1000`. Der Defaultaufruf erzeugt deshalb tatsächlich:

```text
10 00 00 2a 00 00 00 05 68 65 6c 6c 6f
```

Das Bild enthält auch eine schematische Beispiel-Bytefolge mit `40`. Für
Version 2 und das vorgegebene 5-Bit-Versionsfeld ist hier jedoch zwingend
`10 00` korrekt; die konkreten Formatregeln und der Referenzvektor aus dem
Arbeitsauftrag sind maßgeblich.

## Geprüfte Eingaben

- Die Flags müssen echte `bool` sein, keine Integer 0/1.
- Die Sequenznummer muss ein echter `int` sein. Python betrachtet `bool`
  auch als Integer-Unterklasse; deshalb wird mit `type(...) is int` geprüft.
- **Positive unsigned 16 Bit** wird als **1..65535** interpretiert. Ein
  unsigned 16-Bit-Feld kann technisch 0..65535 speichern; „positiv“ schließt
  0 aber aus. Sowohl Erzeuger als auch Parser lehnen 0 ab.
- Die Payload muss echte, nichtleere `bytes` sein. Ihre Byteanzahl muss in
  uint32 passen, also höchstens 4294967295 sein. `str` wird in der CLI
  ausdrücklich mit UTF-8 kodiert, nicht implizit in der API.
- Der Parser prüft zuerst Typ und Mindestheaderlänge, danach Version,
  Reserved, positive Sequenz und nichtleere Payload. Die gespeicherte
  Länge muss genau `len(message) - 8` sein. Zusätzliche Bytes,
  abgeschnittene Bytes und nur ein Header werden zurückgewiesen.

Es werden `TypeError` für falsche Python-Typen und `ValueError` für
ungültige Werte/Inhalte verwendet. Die CLI meldet diese Fehler mit Status 1.

Die Tests enthalten unabhängig festgelegte Hexvektoren für alle vier
Flagkombinationen, Randwerte 1 und 65535, alle neun Reserved-Bits,
mehrere falsche Versionen, kurze Header und Längenfehler bis uint32-Maximum.
Die obere Erzeugungsgrenze wird ergänzend mit einem **kontrollierten Mock
der Grenzkonstante** getestet; es wurden keine 4-GiB-Payloads alloziert.
Der Parser interpretiert eine vollständige Nachricht, keinen beliebig
fragmentierten Netzwerkstrom.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.4 beachte exakt die Bitpositionen und !HHI,
validiere alle Felder und prüfe Roundtrip und unabhängige Binärvektoren.
