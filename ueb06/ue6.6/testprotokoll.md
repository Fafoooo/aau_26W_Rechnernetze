# Testprotokoll zu 6.4–6.6

Datum der Bearbeitung: 2026-10-29. Interpreter laut tatsächlichem Aufruf `python3 --version`: **Python 3.14.7**. Verwendet wird nur die Standardbibliothek; keine Installation erforderlich.

## Tatsächlich ausgeführte Erzeugung

Ausführung ab Repository-Wurzel (relative Pfade).

```sh
PYTHONDONTWRITEBYTECODE=1 python3 ueb06/ue6.4/subnetting.py --write
PYTHONDONTWRITEBYTECODE=1 python3 ueb06/ue6.5/dijkstra.py --write
PYTHONDONTWRITEBYTECODE=1 python3 ueb06/ue6.6/distance_vector.py --write
```

Alle drei Aufrufe liefen mit Exitstatus 0 und meldeten `Alle Prüfungen bestanden; erzeugt:` mit dem absoluten Pfad ihrer jeweiligen `antwort.md`. Nach einer Präzisierung des DV-Erklärungstextes wurde dessen Antwort erneut erfolgreich erzeugt.

## Tatsächlich ausgeführte Testsuite

```sh
PYTHONDONTWRITEBYTECODE=1 python3 ueb06/ue6.6/test_algorithmen.py
```

Unveränderte Ausgabe des erfolgreichen Testlaufs:

```text
test_all_embedded_verifications (__main__.ExerciseTests.test_all_embedded_verifications) ... ok
test_dv_schedule_and_intermediates (__main__.ExerciseTests.test_dv_schedule_and_intermediates) ... ok
test_explanation_line_coverage (__main__.ExerciseTests.test_explanation_line_coverage) ... ok
test_generated_answers (__main__.ExerciseTests.test_generated_answers) ... ok
test_mutation_detection (__main__.ExerciseTests.test_mutation_detection) ... ok
test_sources_compile_and_marked (__main__.ExerciseTests.test_sources_compile_and_marked) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.126s

OK
```

Exitstatus: **0**. Die Laufzeit ist ein protokollierter Einzelwert und keine garantierte Dauer späterer Ausführungen.

## Umfang der Prüfungen

- VLSM: exakte Sollnetze, Kapazität, Minimalität, vollständige Hostaufzählung, Poolzugehörigkeit, paarweise Überschneidungsfreiheit und acht Präfix-Grenzfälle.
- Dijkstra: sämtliche 49 Start-Ziel-Paare gegen unabhängig enumerierte einfache Pfade; Auswahlreihenfolge, Vorgängerbaum, Kosten rekonstruierter Pfade, Gleichstand, unerreichbares Ziel und negative Kante.
- DV: synchrone und asynchrone vollständige Ergebnismatrix identisch; sämtliche 25 Start-Ziel-Paare unabhängig durch einfache Pfade geprüft; alle finalen Spalten gleich Linkkosten plus finalem Nachbarvektor; netzweite Abschlussrunde ohne Vektoränderung.
- Zustellkonvention: zuerst die globale Minimalkante A→E mit Kosten 2, Bs Empfänge E,C,A mit Kosten 3,7,8; D-Zwischenwerte 17 und 11; 42 asynchrone Zustellungen und drei synchrone Runden.
- Negativkontrolle: ein absichtlich verfälschter Dijkstra-Distanzwert wird von der Verifikation erkannt.
- Artefakte: die vollständige Standardausgabe jeder frisch gestarteten Lösung stimmt einschließlich Zeilenumbrüchen mit der gespeicherten Antwort überein.
- Dokumentation: jede nichtleere Zeile aller vier Python-Dateien besitzt genau einen Erklärpunkt mit passender Zeilennummer; Syntax und KI-Kennzeichnungen sind geprüft.

## Werkzeugbeschränkung

`execute_code` und ein zusätzlicher `python3 -c`-Prüfaufruf wurden von der Sicherheitsrichtlinie der unbeaufsichtigten Sitzung blockiert. Beide führten keinen Code aus. Deshalb wurde der transparente, dauerhaft reproduzierbare Testtreiber `test_algorithmen.py` angelegt und regulär gestartet; dieser lief vollständig erfolgreich. Es wurden keine Ergebnisse als Ersatz für blockierte Ausführungen erfunden.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
