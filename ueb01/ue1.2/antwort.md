# Ü 1.2 – Text, Zeichenketten und Bytes

## Ausführung

Vom Ordner `ueb01` aus mit aktiviertem venv:

```bash
python -B ue1.2/text_bytes.py --text 'Grüße 🌍'
python -B ue1.2/text_bytes.py
python -B ue1.2/text_bytes.py --text 'ä' --decode-as latin-1
python -B ue1.2/text_bytes.py --text 'ä' --decode-as ascii
```

Ohne `--text` liest `input()` eine Zeile. Das Programm zeigt `str`, `bytes`,
beide Längen, die UTF-8-Dekodierung und den geprüften Roundtrip. Die optionale
zusätzliche Dekodierung zeigt entweder falschen Text oder einen echten Fehler.
Für `Grüße 🌍` wurden tatsächlich **7 Codepoints und 12 Bytes** ausgegeben.

## Antworten auf alle vier Fragen

**1. Was ist der Unterschied zwischen `str` und `bytes`?**

`str` ist eine unveränderbare Folge von Unicode-Codepoints und repräsentiert
Text. Ein Codepoint ist eine Nummer für ein Unicode-Zeichen oder einen
Zeichenbestandteil. `bytes` ist eine unveränderbare Folge von Bytewerten
zwischen 0 und 255; ein Byte besteht aus 8 Bits. Bytes haben für sich allein
keine Textkodierung. `encode("utf-8")` wandelt Text in Bytes um;
`decode("utf-8")` interpretiert Bytes als Text. Indexieren eines `str` ergibt
eine einstellige Zeichenkette, Indexieren von `bytes` eine Ganzzahl.

**2. Warum können die beiden Längen unterschiedlich sein?**

`len(text)` zählt Unicode-Codepoints. UTF-8 verwendet pro Codepoint ein bis
vier Bytes. Deshalb hat `"ä"` einen Codepoint, aber die Bytefolge `c3 a4`
hat zwei Bytes. `"🌍"` hat einen Codepoint und vier UTF-8-Bytes. Auch Codepoints
sind nicht immer sichtbare Zeichen: `"e\u0301"` enthält `e` und einen
kombinierenden Akzent, also zwei Codepoints, obwohl meist ein „é“ angezeigt
wird. Das sichtbare Gesamtzeichen heißt **Graphemcluster**.

**3. Was passiert bei einer falschen Dekodierung?**

Je nach Bytefolge und Kodierung entstehen falsch dargestellte Zeichen
(**Mojibake**) oder ein `UnicodeDecodeError`. Die UTF-8-Bytes von `ä`, `c3 a4`,
ergeben in Latin-1 den falschen Text `Ã¤`; Latin-1 kann jeden Bytewert abbilden
und meldet deshalb hier keinen Fehler. ASCII kann diese Werte nicht
dekodieren und wirft einen Fehler. Eine unbekannte Kodierungsbezeichnung
führt zu `LookupError`. Das Programm verwendet striktes Dekodieren und
meldet Fehler mit Status 1, anstatt Zeichen stillschweigend zu verwerfen.

**4. Warum ist die Unterscheidung für Netzwerkprogramme wichtig?**

Netzwerkfunktionen übertragen Bytes. Beide Kommunikationspartner müssen
vereinbaren, wie Text kodiert wird. Größenfelder und Übertragungslängen
müssen die **Byteanzahl** enthalten, nicht die Anzahl der Codepoints.
Binäre Header dürfen nicht beliebig als Text dekodiert werden. Bei einem
Bytestrom wie TCP können einzelne UTF-8-Zeichen außerdem auf mehrere
Empfangsvorgänge verteilt sein: Zunächst muss man eine vollständige
Nachricht zusammensetzen oder einen inkrementellen Decoder verwenden.
Der hier getestete Roundtrip verwendet jeweils eine vollständige Bytefolge.

---
**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Tool/Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut `hermes status`:
ChatGPT or Codex Subscription. Tool/Implementierung: Codex CLI **0.162.1**;
Modell: **gpt-6.1-sol**; Datum: **2026-10-13**.
Anfrage: Implementiere Übungsblatt 01 vollständig mit Python-Standardbibliothek,
Tests, Antworten und Erklärung; für 1.2 lies Text, prüfe Unicode/Fehlkodierung,
zeige UTF-8, beide Längen und den Roundtrip und beantworte alle vier Fragen.
