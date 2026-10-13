# Übungsblatt 01 – tatsächliches Testprotokoll

Datum: **2026-10-13**. Die nachfolgenden Ausgaben stammen aus ausgeführten
lokalen Programmen; es wurden keine gewünschten Ergebnisse als Logs eingesetzt.
Die Rohaufzeichnung der 34 direkten CLI-Aufrufe liegt lokal in
`.verification/cli_runs.json` (ignoriert). Dieses Dokument bewahrt die
Kommandos, Statuswerte, stdout/stderr und die wesentlichen Prüfnachweise.

## Umgebung und Arbeitsgrenzen

- Python: `3.14.7 (main, Sep  1 2026, 14:18:09) [Clang 22.1.3 ]`
- Interpreter: `/home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.venv/bin/python`
- Betriebssystem: `Linux-6.17.13-1-pve-x86_64-with-glibc2.41`
- Arbeitsverzeichnis der protokollierten CLI-Aufrufe: `/home/ubuntu/uni/aau_26W_Rechnernetze/ueb01`
- UID: `1000`
- GIL aktiv: `True`

- Branch: `solver/ueb01`; Ausgangscommit: `dc4fd89` (Initial commit).
- Nur Python-Standardbibliothek; kein pip-Aufruf und keine Paketinstallation.
- Die venv wurde tatsächlich mit `python3 -m venv --without-pip ueb01/.venv`
  vom Repositoryroot angelegt. Nach Aktivierung wurde `python --version`
  und `python -B ueb01/ue1.1/hello.py` tatsächlich ausgeführt.
- Dieser erste hello-Aufruf meldete `Virtuelle Umgebung: True`, Python 3.14.7
  und cwd `/home/ubuntu/uni/aau_26W_Rechnernetze`. Die unten erfassten
  späteren CLI-Aufrufe wurden dagegen aus dem Unterordner `ueb01` gestartet.
- Alle geschriebenen Aufgaben-, Test- und Hilfsartefakte liegen unter ueb01.
- Implementierungsphase durch Codex: keine Moodle-Abgabe, kein neu erzeugtes ZIP,
  kein Commit/Push/Merge. Die Git-Veröffentlichung erfolgt danach durch den
  Moodle-Solver gemäß Auftrag; eine Moodle-Abgabe erfolgt weiterhin nicht.

## Testsuite

Erster direkter vollständiger Lauf vom Repositoryroot:

```bash
ueb01/.venv/bin/python -B -m unittest discover -s ueb01/tests -v
```

Tatsächlicher Abschluss dieser ersten Ausführung:

```text
Ran 95 tests in 2.349s

OK
```

**95 bestanden, 0 fehlgeschlagen, 0 übersprungen.** Subtests kommen innerhalb
dieser 95 Methoden hinzu: unter anderem 208 kleine Aufteilungen, 36
Flag/Sequenz/Payload-Kombinationen und 24 Producer-Consumer-Kombinationen.
Die Angabe wurde vollständig als Text gelesen; `pdftotext -layout` las
auch die vierseitige PDF. Das Bitdiagramm und die beigefügten Bilder wurden
mit den konkreten Formatvorgaben abgeglichen.

Ein weiterer vollständiger Lauf diente der Standardbibliotheks-Zeilenmessung.
Er ist instrumentiert und deshalb keine Quelle der Rechenzeit-Messungen:

```bash
/home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.venv/bin/python -B -m trace --count --file /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.verification/trace_counts --coverdir /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.verification/coverage --ignore-dir /home/ubuntu/.hermes/tools/python-3.14.7+20260901-linux-x64/lib/python3.14 --module unittest discover -s tests -v
```

Seine unveränderte aufgezeichnete Ausgabe:

```text
test_all_conditional_branches (test_11_hello.HelloTests.test_all_conditional_branches) ... ok
test_default_name_version_and_actual_cwd (test_11_hello.HelloTests.test_default_name_version_and_actual_cwd) ... ok
test_help (test_11_hello.HelloTests.test_help) ... ok
test_main_return_value (test_11_hello.HelloTests.test_main_return_value) ... ok
test_name_override (test_11_hello.HelloTests.test_name_override) ... ok
test_types_and_loop_results (test_11_hello.HelloTests.test_types_and_loop_results) ... ok
test_unknown_argument (test_11_hello.HelloTests.test_unknown_argument) ... ok
test_ascii_cannot_decode_umlaut (test_12_text_bytes.TextBytesTests.test_ascii_cannot_decode_umlaut) ... ok
test_eof_is_reported (test_12_text_bytes.TextBytesTests.test_eof_is_reported) ... ok
test_explicit_empty_text_does_not_prompt (test_12_text_bytes.TextBytesTests.test_explicit_empty_text_does_not_prompt) ... ok
test_fixed_utf8_vectors_and_roundtrip (test_12_text_bytes.TextBytesTests.test_fixed_utf8_vectors_and_roundtrip) ... ok
test_interactive_input (test_12_text_bytes.TextBytesTests.test_interactive_input) ... ok
test_latin1_produces_mojibake (test_12_text_bytes.TextBytesTests.test_latin1_produces_mojibake) ... ok
test_missing_text_option_value (test_12_text_bytes.TextBytesTests.test_missing_text_option_value) ... ok
test_nonlatin_and_embedded_newlines (test_12_text_bytes.TextBytesTests.test_nonlatin_and_embedded_newlines) ... ok
test_rejects_non_string (test_12_text_bytes.TextBytesTests.test_rejects_non_string) ... ok
test_unicode_cli (test_12_text_bytes.TextBytesTests.test_unicode_cli) ... ok
test_unknown_encoding_is_reported (test_12_text_bytes.TextBytesTests.test_unknown_encoding_is_reported) ... ok
test_unpaired_surrogate_is_rejected (test_12_text_bytes.TextBytesTests.test_unpaired_surrogate_is_rejected) ... ok
test_actual_zip_members_via_cli (test_13_convert.ConvertTests.test_actual_zip_members_via_cli) ... ok
test_controlled_mock_read_permission_error (test_13_convert.ConvertTests.test_controlled_mock_read_permission_error) ... ok
test_controlled_mock_write_error_closes_input (test_13_convert.ConvertTests.test_controlled_mock_write_error_closes_input) ... ok
test_directories_are_not_text_files_cli (test_13_convert.ConvertTests.test_directories_are_not_text_files_cli) ... ok
test_empty_file (test_13_convert.ConvertTests.test_empty_file) ... ok
test_existing_output_is_replaced (test_13_convert.ConvertTests.test_existing_output_is_replaced) ... ok
test_hardlink_to_input_is_rejected (test_13_convert.ConvertTests.test_hardlink_to_input_is_rejected) ... ok
test_invalid_utf8_preserves_existing_output (test_13_convert.ConvertTests.test_invalid_utf8_preserves_existing_output) ... ok
test_missing_and_extra_parameters (test_13_convert.ConvertTests.test_missing_and_extra_parameters) ... ok
test_missing_input_cli (test_13_convert.ConvertTests.test_missing_input_cli) ... ok
test_missing_output_parent_cli (test_13_convert.ConvertTests.test_missing_output_parent_cli) ... ok
test_mixed_line_endings_and_unicode (test_13_convert.ConvertTests.test_mixed_line_endings_and_unicode) ... ok
test_real_unreadable_input_cli (test_13_convert.ConvertTests.test_real_unreadable_input_cli) ... ok
test_real_unwritable_output_directory_cli (test_13_convert.ConvertTests.test_real_unwritable_output_directory_cli) ... ok
test_real_unwritable_output_file_cli (test_13_convert.ConvertTests.test_real_unwritable_output_file_cli) ... ok
test_same_path_cli_is_safe (test_13_convert.ConvertTests.test_same_path_cli_is_safe) ... ok
test_symlink_to_input_is_rejected (test_13_convert.ConvertTests.test_symlink_to_input_is_rejected) ... ok
test_all_flags_bounds_and_binary_payloads_roundtrip (test_14_protocol.ProtocolTests.test_all_flags_bounds_and_binary_payloads_roundtrip) ... ok
test_all_truncated_header_lengths (test_14_protocol.ProtocolTests.test_all_truncated_header_lengths) ... ok
test_cli_binary_parser_and_utf8_payload (test_14_protocol.ProtocolTests.test_cli_binary_parser_and_utf8_payload) ... ok
test_default_cli_matches_canonical_vector (test_14_protocol.ProtocolTests.test_default_cli_matches_canonical_vector) ... ok
test_each_of_nine_reserved_bits (test_14_protocol.ProtocolTests.test_each_of_nine_reserved_bits) ... ok
test_independently_specified_binary_vectors (test_14_protocol.ProtocolTests.test_independently_specified_binary_vectors) ... ok
test_invalid_cli_inputs (test_14_protocol.ProtocolTests.test_invalid_cli_inputs) ... ok
test_length_mismatch_small_and_uint32_max (test_14_protocol.ProtocolTests.test_length_mismatch_small_and_uint32_max) ... ok
test_parser_rejects_zero_sequence (test_14_protocol.ProtocolTests.test_parser_rejects_zero_sequence) ... ok
test_parser_types (test_14_protocol.ProtocolTests.test_parser_types) ... ok
test_payload_types_and_empty_payload (test_14_protocol.ProtocolTests.test_payload_types_and_empty_payload) ... ok
test_positive_uint16_boundaries (test_14_protocol.ProtocolTests.test_positive_uint16_boundaries) ... ok
test_strict_flag_types (test_14_protocol.ProtocolTests.test_strict_flag_types) ... ok
test_strict_sequence_types (test_14_protocol.ProtocolTests.test_strict_sequence_types) ... ok
test_truncated_payload_extra_bytes_and_header_only (test_14_protocol.ProtocolTests.test_truncated_payload_extra_bytes_and_header_only) ... ok
test_uint32_length_guard_with_controlled_small_limit (test_14_protocol.ProtocolTests.test_uint32_length_guard_with_controlled_small_limit) ... ok
test_wrong_versions (test_14_protocol.ProtocolTests.test_wrong_versions) ... ok
test_zero_payload_length_with_and_without_data (test_14_protocol.ProtocolTests.test_zero_payload_length_with_and_without_data) ... ok
test_all_small_range_partitions (test_15_threads.CalculationTests.test_all_small_range_partitions) ... ok
test_cli_integer_parser (test_15_threads.CalculationTests.test_cli_integer_parser) ... ok
test_deterministic_finite_calculation (test_15_threads.CalculationTests.test_deterministic_finite_calculation) ... ok
test_explicit_remainder_empty_and_excess_threads (test_15_threads.CalculationTests.test_explicit_remainder_empty_and_excess_threads) ... ok
test_first_iteration_reference (test_15_threads.CalculationTests.test_first_iteration_reference) ... ok
test_invalid_file_values_include_line_number (test_15_threads.CalculationTests.test_invalid_file_values_include_line_number) ... ok
test_invalid_integer_inputs (test_15_threads.CalculationTests.test_invalid_integer_inputs) ... ok
test_invalid_iterations_and_nonfinite_values (test_15_threads.CalculationTests.test_invalid_iterations_and_nonfinite_values) ... ok
test_load_whitespace_floats_and_universal_newlines (test_15_threads.CalculationTests.test_load_whitespace_floats_and_universal_newlines) ... ok
test_empty_array (test_15_threads.ThreadTests.test_empty_array) ... ok
test_empty_file_cli_with_more_threads (test_15_threads.ThreadTests.test_empty_file_cli_with_more_threads) ... ok
test_file_errors_cli (test_15_threads.ThreadTests.test_file_errors_cli) ... ok
test_invalid_cli_parameters (test_15_threads.ThreadTests.test_invalid_cli_parameters) ... ok
test_invalid_thread_count_and_iterations (test_15_threads.ThreadTests.test_invalid_thread_count_and_iterations) ... ok
test_parallel_matches_sequential_and_preserves_order (test_15_threads.ThreadTests.test_parallel_matches_sequential_and_preserves_order) ... ok
test_real_cli_reports_ranges_times_and_agreement (test_15_threads.ThreadTests.test_real_cli_reports_ranges_times_and_agreement) ... ok
test_worker_error_reaches_caller (test_15_threads.ThreadTests.test_worker_error_reaches_caller) ... ok
test_worker_owns_one_result_slot (test_15_threads.ThreadTests.test_worker_owns_one_result_slot) ... ok
test_cli_missing_file_and_invalid_delay (test_16_shared_sum.SharedSumTests.test_cli_missing_file_and_invalid_delay) ... ok
test_cli_three_real_runs_of_each_mode (test_16_shared_sum.SharedSumTests.test_cli_three_real_runs_of_each_mode) ... ok
test_empty_arrays_in_all_modes (test_16_shared_sum.SharedSumTests.test_empty_arrays_in_all_modes) ... ok
test_empty_input_cli (test_16_shared_sum.SharedSumTests.test_empty_input_cli) ... ok
test_exact_same_calculation_module_as_15 (test_16_shared_sum.SharedSumTests.test_exact_same_calculation_module_as_15) ... ok
test_forced_lost_updates_in_five_real_runs (test_16_shared_sum.SharedSumTests.test_forced_lost_updates_in_five_real_runs) ... ok
test_invalid_cli_arguments (test_16_shared_sum.SharedSumTests.test_invalid_cli_arguments) ... ok
test_invalid_modes_counts_iterations_and_delay (test_16_shared_sum.SharedSumTests.test_invalid_modes_counts_iterations_and_delay) ... ok
test_lock_matches_reference_in_ten_real_runs (test_16_shared_sum.SharedSumTests.test_lock_matches_reference_in_ten_real_runs) ... ok
test_lock_with_more_threads_than_values (test_16_shared_sum.SharedSumTests.test_lock_with_more_threads_than_values) ... ok
test_naive_ten_real_runs_without_assuming_a_race (test_16_shared_sum.SharedSumTests.test_naive_ten_real_runs_without_assuming_a_race) ... ok
test_one_thread_in_all_modes (test_16_shared_sum.SharedSumTests.test_one_thread_in_all_modes) ... ok
test_worker_error_aborts_barrier_and_reaches_caller (test_16_shared_sum.SharedSumTests.test_worker_error_aborts_barrier_and_reaches_caller) ... ok
test_cli_default (test_17_producer_consumer.ProducerConsumerTests.test_cli_default) ... ok
test_cli_invalid_numbers (test_17_producer_consumer.ProducerConsumerTests.test_cli_invalid_numbers) ... ok
test_cli_multiple_consumers_with_size_one_finishes (test_17_producer_consumer.ProducerConsumerTests.test_cli_multiple_consumers_with_size_one_finishes) ... ok
test_cli_zero_count_finishes_all_consumers (test_17_producer_consumer.ProducerConsumerTests.test_cli_zero_count_finishes_all_consumers) ... ok
test_consumer_waits_for_data_and_stops_on_sentinel (test_17_producer_consumer.ProducerConsumerTests.test_consumer_waits_for_data_and_stops_on_sentinel) ... ok
test_every_value_exactly_once_across_consumers (test_17_producer_consumer.ProducerConsumerTests.test_every_value_exactly_once_across_consumers) ... ok
test_invalid_counts_consumers_and_queue_sizes (test_17_producer_consumer.ProducerConsumerTests.test_invalid_counts_consumers_and_queue_sizes) ... ok
test_more_consumers_than_values (test_17_producer_consumer.ProducerConsumerTests.test_more_consumers_than_values) ... ok
test_producer_blocks_until_full_queue_is_drained (test_17_producer_consumer.ProducerConsumerTests.test_producer_blocks_until_full_queue_is_drained) ... ok
test_task_done_even_when_processing_raises (test_17_producer_consumer.ProducerConsumerTests.test_task_done_even_when_processing_raises) ... ok

----------------------------------------------------------------------
Ran 95 tests in 2.642s

OK
```

Separat ausgeführter README-Befehl für Protokolltests, cwd ueb01:

```bash
python -B tests/test_14_protocol.py
```

```text
..................
----------------------------------------------------------------------
Ran 18 tests in 0.277s

OK
```

## Abgedeckte Fehler und Randfälle

| Aufgabe | Tatsächlich geprüfte Fälle |
|---|---|
| 1.1 | Fabio, Namensoption, Python-Version, geändertes reales cwd, Typen, Schleifen, alle if-Zweige, Hilfe, unbekanntes Argument |
| 1.2 | Leertext, ASCII, Umlaut, Emoji, kombinierender Akzent, Han-Zeichen, Nullzeichen, stdin, EOF, Surrogat, Latin-1-Mojibake, ASCII-Fehler, unbekannte Kodierung |
| 1.3 | beide echten ZIP-Mitglieder, gemischtes CRLF/CR/LF, Leerdatei, Ersetzen, ungültiges UTF-8 mit erhaltenem Ziel, fehlender Pfad, identischer Pfad, Symlink, Hardlink, Verzeichnisse, CLI-Parameter und reale Rechtefehler |
| 1.4 | feste unabhängige Vektoren, vier Flags, Sequenz 1/65535, Sequenz 0/Überlauf, echte bool/bytes/int, falsche Version, alle neun Reserved-Bits, Header 0..7 Bytes, Nullpayload, kurz/lang/mismatch, uint32-Maximum |
| 1.5 | endliche Floats, Zeilennummern bei fehlerhaften Werten, Leerraum/Leerdatei, 208 Aufteilungen, Rest, n>len, sequentielle Einzelwertreferenz, eigene Slots, Workerfehler, CLI-Zeiten/Bereiche |
| 1.6 | dieselbe importierte Berechnung, zehn naive und zehn Lock-Läufe, fünf erzwungene Läufe, ein Thread, leer, n>len, falsche Parameter, Barrier-Abbruch, drei CLI-Läufe je Variante |
| 1.7 | ein/mehrere Consumer, count 0, mehr Consumer als Werte, maxsize 1, echte blockierende Übergabe, ein Sentinel pro Consumer, task_done bei Fehler, Counter-genau-einmal, beide joins, CLI-Timeouts |

### Echte Rechteprüfung und ergänzende Mocks

Unter UID 1000 liefen alle drei OS-Rechteprüfungen tatsächlich, ohne Skip:

- `test_real_unreadable_input_cli`: Quelle `chmod(000)`, echte CLI Status 1.
- `test_real_unwritable_output_file_cli`: vorhandenes Ziel `chmod(400)`,
  echte CLI Status 1, ursprünglicher Zielinhalt erhalten.
- `test_real_unwritable_output_directory_cli`: Zielordner `chmod(500)`,
  echte CLI Status 1, keine Ausgabe erzeugt.

Die Tests kontrollieren mit `os.access`, ob der Benutzer die Sperre wirklich
erfährt. Bei privilegierten Benutzern wird ausdrücklich übersprungen. Die
Rechte temporärer Dateien werden immer in finally restauriert.

Die separat benannten `test_controlled_mock_read_permission_error` und
`test_controlled_mock_write_error_closes_input` prüfen mit simuliertem
PermissionError die CLI-Fehlerübersetzung und den geschlossenen Eingabestrom.
Sie ersetzen keine reale Rechteprüfung. Der kleine Max-Payload-Mock in 1.4
prüft die Erzeugungs-Grenzbedingung, ohne tatsächlich 4 GiB zu reservieren.

## Zeilenabdeckung mit der Standardbibliothek

Verwendet wurde `trace`, kein zusätzliches Coverage-Paket. Die Zähler des
instrumentierten Testlaufs wurden mit separat instrumentierten CLI-Aufrufen
zusammengeführt; bei diesen zusätzlichen Coverage-Aufrufen wurden vorhandene
`--iterations` und `--runs` auf 1 verkürzt. Diese Aufrufe wurden ausschließlich
für Abdeckung verwendet. Statuswerte und Zeiten in der folgenden CLI-Sektion
stammen dagegen aus unveränderten direkten Prozessen ohne trace.

Zählerdatei: `.verification/trace_counts`; Detaildateien:
`.verification/coverage/`; zusammengefasste Werte: `.verification/coverage.json`.
Die positiven ausführbaren Quellzeilen wurden mit der lokalen Python-3.14-
trace-Analyse ermittelt und je absolut aufgelöstem Quellpfad gegen die
Zähler verglichen. Synthetische Bytecodepositionen `None` und 0 sowie
Kommentar-/Leer-/Docstringzeilen zählen nicht als ausführbare Quellzeilen.
Die Tabelle umfasst nur die acht Aufgabenmodule; Tests sind nicht im Nenner.

| Datei | Erfasste / ausführbare Zeilen | Anteil | Nicht erfasste Quellzeilen |
|---|---:|---:|---|
| `ue1.1/hello.py` | 50 / 50 | 100.00 % | keine |
| `ue1.2/text_bytes.py` | 34 / 37 | 91.89 % | 30, 31, 32 |
| `ue1.3/convert.py` | 33 / 33 | 100.00 % | keine |
| `ue1.4/protocol.py` | 71 / 71 | 100.00 % | keine |
| `ue1.5/calculation.py` | 56 / 56 | 100.00 % | keine |
| `ue1.5/threads.py` | 57 / 64 | 89.06 % | 23, 24, 45, 49, 68, 69, 70 |
| `ue1.6/shared_sum.py` | 79 / 83 | 95.18 % | 94, 95, 96, 97 |
| `ue1.7/producer_consumer.py` | 66 / 70 | 94.29 % | 64, 76, 77, 78 |

**Gesamt: 446/464 = 96.12 % Zeilenabdeckung.**
Dies ist Zeilen-, keine Branch-Abdeckung. Einige Fehlerpfade werden bereits
von direkten CLI-/Threadtests geprüft, sind aber nicht sämtlich in den
kombinierten trace-Zählern erfasst. Abdeckung garantiert keine allgemeine
Korrektheit. Keine externen Linter oder Typprüfer wurden installiert.

### Korrektur an der Messhilfe

Beim ersten Instrumentierungsversuch wurde beobachtet, dass der trace-
Programmeinstieg `SystemExit` abfängt: Ein absichtlich fehlgeschlagener
ASCII-Decode-Aufruf erschien dadurch beim äußeren trace-Prozess als Status 0.
Dieser Versuch wurde als Status-/Zeitquelle verworfen. Alle 34 nachfolgenden
CLI-Aufrufe wurden direkt gestartet und ihre Statuswerte tatsächlich geprüft.
Bei der Auswertung relativer trace-Pfade wurde außerdem cwd auf ueb01 gesetzt;
synthetische None/0-Positionen wurden ausdrücklich ausgeschlossen. Diese
Korrekturen betreffen die Messhilfe, nicht die grünen Aufgaben-/CLI-Tests.

## Direkte CLI-Aufrufe: echte Statuswerte und Ausgaben

Alle Befehle dieser Sektion wurden aus ueb01 mit dessen venv-Interpreter
ausgeführt. Für Lesbarkeit steht im kurzen Befehl `python`; die vollständige
tatsächlich übergebene Interpreterdatei ist in der Umgebung oben angegeben.
Jeder Prozess hatte 30 Sekunden Timeout. Erwartete Fehlerstatuswerte wurden
ebenfalls geprüft und nicht als erfolgreiche Ausführungen ausgegeben.
Individuelle Consumerverteilungen und Laufzeiten können bei Wiederholung
variieren. Die unten stehenden Zahlen sind die tatsächliche Aufzeichnung.

### 1. 1.1 Fabio und Umgebung

```bash
python -B ue1.1/hello.py
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Name: Fabio
Python-Version: 3.14.7
Arbeitsverzeichnis: /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01
Python-Interpreter: /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.venv/bin/python
Virtuelle Umgebung: True
int: 3 (Typ: int)
float: 1.5 (Typ: float)
bool: True (Typ: bool)
NoneType: None (Typ: NoneType)
str: 'Text' (Typ: str)
list: ['Text', 'Bytes', 'Threads'] (Typ: list)
dict: {1: 'Text', 2: 'Bytes', 3: 'Threads'} (Typ: dict)
while-Ergebnis: [3, 2, 1] (Typ: list)
if/elif/else für -1: negativ
if/elif/else für 0: null
if/elif/else für 1: positiv
```

stderr: leer.

### 2. 1.1 Name optional

```bash
python -B ue1.1/hello.py --name Fabio
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Name: Fabio
Python-Version: 3.14.7
Arbeitsverzeichnis: /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01
Python-Interpreter: /home/ubuntu/uni/aau_26W_Rechnernetze/ueb01/.venv/bin/python
Virtuelle Umgebung: True
int: 3 (Typ: int)
float: 1.5 (Typ: float)
bool: True (Typ: bool)
NoneType: None (Typ: NoneType)
str: 'Text' (Typ: str)
list: ['Text', 'Bytes', 'Threads'] (Typ: list)
dict: {1: 'Text', 2: 'Bytes', 3: 'Threads'} (Typ: dict)
while-Ergebnis: [3, 2, 1] (Typ: list)
if/elif/else für -1: negativ
if/elif/else für 0: null
if/elif/else für 1: positiv
```

stderr: leer.

### 3. 1.2 Unicode

```bash
python -B ue1.2/text_bytes.py --text 'Grüße 🌍'
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
str: 'Grüße 🌍'
bytes: b'Gr\xc3\xbc\xc3\x9fe \xf0\x9f\x8c\x8d'
len(str), Unicode-Codepoints: 7
len(bytes), Bytes: 12
UTF-8 dekodiert: 'Grüße 🌍'
Roundtrip identisch: True
```

stderr: leer.

### 4. 1.2 Eingabe

```bash
python -B ue1.2/text_bytes.py
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

Tatsächlich über stdin übergebene Eingabe:

```text
Netzwerk ä
```

stdout:

```text
Text: str: 'Netzwerk ä'
bytes: b'Netzwerk \xc3\xa4'
len(str), Unicode-Codepoints: 10
len(bytes), Bytes: 11
UTF-8 dekodiert: 'Netzwerk ä'
Roundtrip identisch: True
```

stderr: leer.

### 5. 1.2 Leertext

```bash
python -B ue1.2/text_bytes.py --text ''
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
str: ''
bytes: b''
len(str), Unicode-Codepoints: 0
len(bytes), Bytes: 0
UTF-8 dekodiert: ''
Roundtrip identisch: True
```

stderr: leer.

### 6. 1.2 Latin-1 falsch

```bash
python -B ue1.2/text_bytes.py --text 'ä' --decode-as latin-1
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
str: 'ä'
bytes: b'\xc3\xa4'
len(str), Unicode-Codepoints: 1
len(bytes), Bytes: 2
UTF-8 dekodiert: 'ä'
Roundtrip identisch: True
Dekodiert mit latin-1: 'Ã¤'
Auch damit identisch: False
```

stderr: leer.

### 7. 1.2 ASCII Fehler

```bash
python -B ue1.2/text_bytes.py --text 'ä' --decode-as ascii
```

Tatsächlicher Status: **1**; erwarteter Status: 1.

stdout:

```text
str: 'ä'
bytes: b'\xc3\xa4'
len(str), Unicode-Codepoints: 1
len(bytes), Bytes: 2
UTF-8 dekodiert: 'ä'
Roundtrip identisch: True
```

stderr:

```text
Dekodierungsfehler (ascii): 'ascii' codec can't decode byte 0xc3 in position 0: ordinal not in range(128)
```

### 8. 1.3 Original file1

```bash
python -B ue1.3/convert.py Angabe/file1.txt .tmp/file1_lf.txt
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
183 Unicode-Codepoints nach .tmp/file1_lf.txt geschrieben (UTF-8, LF).
```

stderr: leer.

### 9. 1.3 Original file2

```bash
python -B ue1.3/convert.py Angabe/file2.txt .tmp/file2_lf.txt
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
621 Unicode-Codepoints nach .tmp/file2_lf.txt geschrieben (UTF-8, LF).
```

stderr: leer.

### 10. 1.3 Gemischte Umbrüche

```bash
python -B ue1.3/convert.py .tmp/zeilenenden.txt .tmp/zeilenenden_lf.txt
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
9 Unicode-Codepoints nach .tmp/zeilenenden_lf.txt geschrieben (UTF-8, LF).
```

stderr: leer.

### 11. 1.3 Fehlende Argumente

```bash
python -B ue1.3/convert.py
```

Tatsächlicher Status: **2**; erwarteter Status: 2.

stdout: leer.

stderr:

```text
usage: convert.py [-h] infile outfile
convert.py: error: the following arguments are required: infile, outfile
```

### 12. 1.3 Fehlende Eingabe

```bash
python -B ue1.3/convert.py .tmp/fehlt.txt .tmp/fehlend_out.txt
```

Tatsächlicher Status: **1**; erwarteter Status: 1.

stdout: leer.

stderr:

```text
Dateifehler: [Errno 2] No such file or directory: '.tmp/fehlt.txt'
```

### 13. 1.3 Ungültiges UTF-8

```bash
python -B ue1.3/convert.py .tmp/ungueltig.txt .tmp/invalid_out.txt
```

Tatsächlicher Status: **1**; erwarteter Status: 1.

stdout: leer.

stderr:

```text
Ungültiges UTF-8 in .tmp/ungueltig.txt: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

### 14. 1.3 Identischer Pfad

```bash
python -B ue1.3/convert.py Angabe/file1.txt Angabe/file1.txt
```

Tatsächlicher Status: **1**; erwarteter Status: 1.

stdout: leer.

stderr:

```text
Dateifehler: Ein- und Ausgabedatei müssen verschieden sein (auch Links).
```

### 15. 1.4 Referenzvektor

```bash
python -B ue1.4/protocol.py
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Nachricht (Hex): 10 00 00 2a 00 00 00 05 68 65 6c 6c 6f
Header: 8 Bytes; Version: 2; Reserviert: 0
D: False; U: False; Sequenz: 42
Payload (5 Bytes): b'hello'
Roundtrip identisch: True
```

stderr: leer.

### 16. 1.4 Flags und Grenze

```bash
python -B ue1.4/protocol.py --data --urgent --sequence 65535 --payload 'ä'
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Nachricht (Hex): 10 03 ff ff 00 00 00 02 c3 a4
Header: 8 Bytes; Version: 2; Reserviert: 0
D: True; U: True; Sequenz: 65535
Payload (2 Bytes): b'\xc3\xa4'
Roundtrip identisch: True
```

stderr: leer.

### 17. 1.4 Hex parsen

```bash
python -B ue1.4/protocol.py --message-hex '10 00 00 2a 00 00 00 05 68 65 6c 6c 6f'
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Nachricht (Hex): 10 00 00 2a 00 00 00 05 68 65 6c 6c 6f
Header: 8 Bytes; Version: 2; Reserviert: 0
D: False; U: False; Sequenz: 42
Payload (5 Bytes): b'hello'
Roundtrip identisch: True
```

stderr: leer.

### 18. 1.4 Nullsequenz ablehnen

```bash
python -B ue1.4/protocol.py --sequence 0
```

Tatsächlicher Status: **1**; erwarteter Status: 1.

stdout: leer.

stderr:

```text
Protokollfehler: sequence_number muss im Bereich 1..65535 liegen.
```

### 19. 1.5 Restaufteilung

```bash
python -B ue1.5/threads.py ue1.5/werte.txt --threads 4 --iterations 50000
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Werte: 9; Threads: 4; Iterationen pro Wert: 50000
Thread 1: [0, 3) -> 3 Werte
Thread 2: [3, 5) -> 2 Werte
Thread 3: [5, 7) -> 2 Werte
Thread 4: [7, 9) -> 2 Werte
Sequentiell: Summe=6.610597757912; Zeit=0.040455 s
Threads:     Summe=6.610597757912; Zeit=0.039749 s
Identische Einzelwerte: True
GIL: CPU-Arbeit mit Threads ist auf gewöhnlichem CPython nicht automatisch schneller.
```

stderr: leer.

### 20. 1.5 Mehr Threads als Werte

```bash
python -B ue1.5/threads.py ue1.5/werte.txt --threads 12 --iterations 1000
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Werte: 9; Threads: 12; Iterationen pro Wert: 1000
Thread 1: [0, 1) -> 1 Werte
Thread 2: [1, 2) -> 1 Werte
Thread 3: [2, 3) -> 1 Werte
Thread 4: [3, 4) -> 1 Werte
Thread 5: [4, 5) -> 1 Werte
Thread 6: [5, 6) -> 1 Werte
Thread 7: [6, 7) -> 1 Werte
Thread 8: [7, 8) -> 1 Werte
Thread 9: [8, 9) -> 1 Werte
Thread 10: [9, 9) -> 0 Werte
Thread 11: [9, 9) -> 0 Werte
Thread 12: [9, 9) -> 0 Werte
Sequentiell: Summe=6.610597757912; Zeit=0.000851 s
Threads:     Summe=6.610597757912; Zeit=0.003132 s
Identische Einzelwerte: True
GIL: CPU-Arbeit mit Threads ist auf gewöhnlichem CPython nicht automatisch schneller.
```

stderr: leer.

### 21. 1.5 Leerdatei

```bash
python -B ue1.5/threads.py .tmp/leer.txt --threads 3 --iterations 1000
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Werte: 0; Threads: 3; Iterationen pro Wert: 1000
Thread 1: [0, 0) -> 0 Werte
Thread 2: [0, 0) -> 0 Werte
Thread 3: [0, 0) -> 0 Werte
Sequentiell: Summe=0.000000000000; Zeit=0.000001 s
Threads:     Summe=0.000000000000; Zeit=0.000567 s
Identische Einzelwerte: True
GIL: CPU-Arbeit mit Threads ist auf gewöhnlichem CPython nicht automatisch schneller.
```

stderr: leer.

### 22. 1.6 Wiederholungsmessung

```bash
python -B ue1.6/shared_sum.py ue1.5/werte.txt --threads 4 --iterations 50000 --runs 5 --mode all
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Werte: 9; Threads: 4; Iterationen: 50000
naive: direktes +=; eine Abweichung ist nicht garantiert.
forced: didaktisch erzwungenes read/barrier/sleep/write; keine naive +=-Messung.
naive Lauf 1: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.041467 s
naive Lauf 2: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.049506 s
naive Lauf 3: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.043273 s
naive Lauf 4: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.044969 s
naive Lauf 5: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.041953 s
lock Lauf 1: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.046251 s
lock Lauf 2: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.043224 s
lock Lauf 3: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.056019 s
lock Lauf 4: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.045528 s
lock Lauf 5: erwartet=6.610597757912; gemessen=6.610597757912; Differenz=-0.000000000000; OK; Zeit=0.036528 s
forced Lauf 1: erwartet=6.610597757912; gemessen=1.367053015971; Differenz=-5.243544741941; ABWEICHUNG; Zeit=0.054690 s
forced Lauf 2: erwartet=6.610597757912; gemessen=1.367053015971; Differenz=-5.243544741941; ABWEICHUNG; Zeit=0.042499 s
forced Lauf 3: erwartet=6.610597757912; gemessen=-0.237067240001; Differenz=-6.847664997913; ABWEICHUNG; Zeit=0.039462 s
forced Lauf 4: erwartet=6.610597757912; gemessen=3.482690267771; Differenz=-3.127907490141; ABWEICHUNG; Zeit=0.041447 s
forced Lauf 5: erwartet=6.610597757912; gemessen=1.367053015971; Differenz=-5.243544741941; ABWEICHUNG; Zeit=0.042697 s
```

stderr: leer.

### 23. 1.6 Leerdatei

```bash
python -B ue1.6/shared_sum.py .tmp/leer.txt --threads 5 --iterations 1 --runs 2
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Werte: 0; Threads: 5; Iterationen: 1
naive: direktes +=; eine Abweichung ist nicht garantiert.
forced: didaktisch erzwungenes read/barrier/sleep/write; keine naive +=-Messung.
naive Lauf 1: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.000885 s
naive Lauf 2: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.000271 s
lock Lauf 1: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.000293 s
lock Lauf 2: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.000250 s
forced Lauf 1: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.001502 s
forced Lauf 2: erwartet=0.000000000000; gemessen=0.000000000000; Differenz=0.000000000000; OK; Zeit=0.001421 s
```

stderr: leer.

### 24. 1.7 Standardaufruf

```bash
python -B ue1.7/producer_consumer.py
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Consumer 1: Anzahl=8; Summe=420
Consumer 2: Anzahl=16; Summe=520
Consumer 3: Anzahl=76; Summe=4110
Gesamtsumme: 5050; erwartet: 5050
Alle Werte genau einmal: True
```

stderr: leer.

### 25. 1.7 Mehrere Consumer

```bash
python -B ue1.7/producer_consumer.py --count 17 --consumers 3 --maxsize 2
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Consumer 1: Anzahl=5; Summe=27
Consumer 2: Anzahl=4; Summe=54
Consumer 3: Anzahl=8; Summe=72
Gesamtsumme: 153; erwartet: 153
Alle Werte genau einmal: True
```

stderr: leer.

### 26. 1.7 Queue-Größe 1

```bash
python -B ue1.7/producer_consumer.py --count 257 --consumers 4 --maxsize 1
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Consumer 1: Anzahl=65; Summe=8385
Consumer 2: Anzahl=64; Summe=8192
Consumer 3: Anzahl=64; Summe=8256
Consumer 4: Anzahl=64; Summe=8320
Gesamtsumme: 33153; erwartet: 33153
Alle Werte genau einmal: True
```

stderr: leer.

### 27. 1.7 Keine Werte

```bash
python -B ue1.7/producer_consumer.py --count 0 --consumers 5 --maxsize 1
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
Consumer 1: Anzahl=0; Summe=0
Consumer 2: Anzahl=0; Summe=0
Consumer 3: Anzahl=0; Summe=0
Consumer 4: Anzahl=0; Summe=0
Consumer 5: Anzahl=0; Summe=0
Gesamtsumme: 0; erwartet: 0
Alle Werte genau einmal: True
```

stderr: leer.

### 28. 1.1 Hilfe

```bash
python -B ue1.1/hello.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: hello.py [-h] [--name NAME]

Ü 1.1: Umgebung und kleine, ausführbare Beispiele der Sprachgrundlagen.

options:
  -h, --help   show this help message and exit
  --name NAME  Name (Standard: Fabio)
```

stderr: leer.

### 29. 1.2 Hilfe

```bash
python -B ue1.2/text_bytes.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: text_bytes.py [-h] [--text TEXT] [--decode-as DECODE_AS]

Ü 1.2: Text eingeben, UTF-8 kodieren und wieder dekodieren.

options:
  -h, --help            show this help message and exit
  --text TEXT           Text; ohne dieses Argument wird input() verwendet
  --decode-as DECODE_AS
                        Zusätzlicher Versuch mit dieser Kodierung
```

stderr: leer.

### 30. 1.3 Hilfe

```bash
python -B ue1.3/convert.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: convert.py [-h] infile outfile

Ü 1.3: UTF-8 kopieren und CRLF/CR/LF zu LF normalisieren.

positional arguments:
  infile      Eingabedatei mit UTF-8-Text
  outfile     Ausgabedatei mit UTF-8 und LF

options:
  -h, --help  show this help message and exit
```

stderr: leer.

### 31. 1.4 Hilfe

```bash
python -B ue1.4/protocol.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: protocol.py [-h] [--data] [--urgent] [--sequence SEQUENCE]
                   [--payload PAYLOAD] [--message-hex MESSAGE_HEX]

Ü 1.4: 8-Byte-Protokollheader und variable, nichtleere Nutzlast.

options:
  -h, --help            show this help message and exit
  --data                D-Flag setzen
  --urgent              U-Flag setzen
  --sequence SEQUENCE
  --payload PAYLOAD     Als UTF-8 kodierte Nutzlast
  --message-hex MESSAGE_HEX
                        Statt Erzeugen eine Hex-Nachricht parsen
```

stderr: leer.

### 32. 1.5 Hilfe

```bash
python -B ue1.5/threads.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: threads.py [-h] [--threads THREADS] [--iterations ITERATIONS] infile

Ü 1.5: Eigene Eingabebereiche und Ergebnisplätze pro Thread.

positional arguments:
  infile                UTF-8-Datei: Floats durch Leerraum getrennt

options:
  -h, --help            show this help message and exit
  --threads THREADS
  --iterations ITERATIONS
```

stderr: leer.

### 33. 1.6 Hilfe

```bash
python -B ue1.6/shared_sum.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: shared_sum.py [-h] [--threads THREADS] [--iterations ITERATIONS]
                     [--runs RUNS] [--mode {naive,lock,forced,all}]
                     [--delay DELAY]
                     infile

Ü 1.6: Gemeinsame Summe, kurzer Lock und separate Interleaving-Demonstration.

positional arguments:
  infile                Dieselbe Float-Datei wie in Ü 1.5

options:
  -h, --help            show this help message and exit
  --threads THREADS
  --iterations ITERATIONS
  --runs RUNS
  --mode {naive,lock,forced,all}
  --delay DELAY         Sleep nur in forced, in Sekunden
```

stderr: leer.

### 34. 1.7 Hilfe

```bash
python -B ue1.7/producer_consumer.py --help
```

Tatsächlicher Status: **0**; erwarteter Status: 0.

stdout:

```text
usage: producer_consumer.py [-h] [--count COUNT] [--consumers CONSUMERS]
                            [--maxsize MAXSIZE]

Ü 1.7: Begrenzte Queue, blockierende Übergabe und kontrolliertes Ende.

options:
  -h, --help            show this help message and exit
  --count COUNT         Erzeuge 1 bis count (0: keine Zahlen)
  --consumers CONSUMERS
  --maxsize MAXSIZE     Positive Queue-Kapazität
```

stderr: leer.

## Interpretation der Messungen

Der direkte 1.5-Lauf mit vier Threads und 50000 Iterationen liefert dieselben
Einzelwerte wie die sequentielle Rechnung. Die beobachteten 0.040455 s und
0.039749 s sind einzelne lokale Laufzeiten, keine garantierte Beschleunigung.
Der GIL war aktiv. Der zwölf-Thread- und Leerdateifall lief ebenfalls durch.

Bei 1.6 waren alle fünf naiven und alle fünf Lock-Summen innerhalb 1e-12-
Toleranz zur Referenz 6.610597757912. Der gedruckte negative Nullwert der
Differenz ist eine auf zwölf Nachkommastellen gerundete minimale Floatabweichung.
Nur die getrennte read/barrier/sleep/write-Demonstration zeigte in allen fünf
aufgezeichneten Läufen Lost Updates. Sie wird nicht als gemessener Fehler
der direkten naiven +=-Variante dargestellt. Tabelle und Antworten stehen
zusätzlich in `ue1.6/antwort.md`.

Die 1.7-Läufe erreichten Gesamtsummen 5050 (100 Werte), 153 (17), 33153
(257) und 0 (leer). Alle Werte wurden genau einmal verarbeitet; mehrere
Consumer und maxsize 1 endeten ohne Timeout.

## Exakte neu erstellte Dateien

Die folgende Liste enthält genau die 28 durch diesen Auftrag neu erstellten
Lösungs-/Dokumentationsdateien. Die fünf Angabedateien waren vorher vorhanden.
Nichts wurde gestaged, committet oder veröffentlicht.

- `.gitignore`
- `README.md`
- `erklaerung_blatt01.md`
- `testprotokoll_blatt01.md`
- `tests/support.py`
- `tests/test_11_hello.py`
- `tests/test_12_text_bytes.py`
- `tests/test_13_convert.py`
- `tests/test_14_protocol.py`
- `tests/test_15_threads.py`
- `tests/test_16_shared_sum.py`
- `tests/test_17_producer_consumer.py`
- `ue1.1/antwort.md`
- `ue1.1/hello.py`
- `ue1.2/antwort.md`
- `ue1.2/text_bytes.py`
- `ue1.3/antwort.md`
- `ue1.3/convert.py`
- `ue1.4/antwort.md`
- `ue1.4/protocol.py`
- `ue1.5/antwort.md`
- `ue1.5/calculation.py`
- `ue1.5/threads.py`
- `ue1.5/werte.txt`
- `ue1.6/antwort.md`
- `ue1.6/shared_sum.py`
- `ue1.7/antwort.md`
- `ue1.7/producer_consumer.py`

### Unverändert verwendete Angabedateien

SHA-256 der bei der Prüfung unveränderten Eingaben:

| Datei | SHA-256 |
|---|---|
| `Angabe/angabe_blatt01.txt` | `3f550482385f1a212511060833c494ff7a506f5c606fc09b2cb5d8c462a7f2be` |
| `Angabe/file1.txt` | `8292cf5ace75258713eaa7a73a915dde0cc8f61dbc392802598366b5bde69db9` |
| `Angabe/file2.txt` | `363568e65d4b370942a619301af6a14cf5d0dc86902d4e4a67743bb918269f91` |
| `Angabe/utf8files.zip` | `79c10b30e38fab6e0851604e2636182d23fce1c32cfc31bd3af8883a3c74f6cf` |
| `angabe_blatt01.pdf` | `8bf8251943634b277bc03a5c0a43f8d1c117b4ac55b3c0758bad149d496e25eb` |

## Verifikation der Dokumentation und bekannte Grenzen

Jede der 16 Python-Dateien beginnt mit der KI-Kennzeichnung einschließlich
Tool/Modell/Version/Datum und konkreter Anfrage. Jede der sieben antwort.md
endet mit derselben Herkunft und ihrer Anfrage. Die Erklärungsgruppen wurden
gegen die realen Quellzeilen geprüft: jede nichtleere Zeile ist genau einmal
zugeordnet; es gibt keine Lücke oder Überlappung. Die Codeauszüge wurden
unverändert aus den genannten Quellgruppen übernommen.

Der Syntaxcheck kompiliert alle 16 Dateien im Speicher; er erzeugt keinen
Bytecodecache. Importprüfung erlaubt nur Standardbibliothek plus lokale
calculation/support. Git-Statusprüfung und Hilfsordnerprüfung erfolgen
lokal; .venv, .tmp, .verification und Coverage-Details sind ignoriert.

Tatsächlicher abschließender Prüfstand:

| Prüfung | Ergebnis |
|---|---|
| Syntax aller 16 Python-Dateien, Kompilieren im Speicher | PASS |
| Imports ausschließlich Standardbibliothek oder lokale calculation/support | PASS |
| KI-Kopf aller 16 Python-Dateien | PASS |
| KI-Schluss aller sieben antwort.md | PASS |
| Erklärung aller 16 Dateien in 320 Quellgruppen | PASS, 0 Lücken, 0 Überlappungen |
| Alle 320 Codeauszüge gleich den tatsächlichen Quellzeilen | PASS |
| Relative Markdown-Dateilinks | PASS |
| Angabe-Text und ZIP-/Textdateien: gespeicherte SHA-256-Werte | unverändert |
| file1/file2 gegenüber den echten ZIP-Mitgliedern | bytegleich |
| Branchkontrolle | solver/ueb01 |
| `git diff --name-only` | leer; keine Änderung an vorher getrackten Dateien |
| Untracked-Dateien | nur ueb01; fünf vorher vorhandene Angabedateien plus 28 neue Dateien |
| `git check-ignore` für venv, tmp, Messdaten und pyc | alle vier Proben ignoriert |

Bei der Abschlusskontrolle wurden lokal erzeugte, bereits ignorierte
`__pycache__`-Ordner aus den sieben Aufgabenordnern und tests entfernt.
Der abschließende Aufgaben-/Testbaum enthält keinen solchen Cache.
Die Rohdaten der statischen Prüfung stehen lokal in
`.verification/static_checks.json`; es wurde kein Quellcode verändert.

Verbleibende praktische Grenzen:

- Geprüfte Umgebung ist Linux/CPython 3.14.7; es wurde kein separater
  Windows- oder anderer-Interpreter-Test ausgeführt.
- convert liest vollständig in den Speicher und schreibt ein anderes
  Ziel ohne atomaren Austausch. Ein später Schreibfehler kann einen
  Teilinhalt hinterlassen; paralleler Pfadaustausch durch andere Prozesse
  wird nicht transaktional abgesichert.
- Ein 4-GiB-Payload wurde nicht alloziert; die Grenze wurde logisch und
  mit kontrolliert verkleinertem Limit geprüft.
- Threadzahl und Integercount sind nicht durch künstliche Obergrenzen
  limitiert; extrem große Eingaben können Speicher/Threadressourcen erschöpfen.
- Die Queue ist begrenzt, die Ergebnisaufzeichnung aller Werte ist es nicht.
- Es wurde keine reale Netzwerkverbindung implementiert oder als geprüft
  behauptet; dieses Blatt behandelt die Grundlagen.

## Unabhängige Prüfung durch den Moodle-Solver

Die unabhängige erste Prüfung bestätigte alle acht Programmdateien ohne
funktionalen Befund. Eine separat entwickelte Scratch-Testsuite bestand
16 Testgruppen; darunter die Prüfung aller 65536 möglichen ersten
16-Bit-Headerwörter, Partitionen, Dateirechte, Lock-/Race-Verhalten und
Queue-Lifecycle. Der Moodle-Solver führte diese Suite anschließend selbst
nochmals erfolgreich aus.

Die zweite unabhängige Prüfung bestätigte sämtliche Theorieantworten und
führte die Repository-Suite aus: 95 Tests, OK, keine Skips. Im damaligen
Zwischenstand fehlten noch vier Testdatei-Erklärungen und das Testprotokoll.
Beides wurde anschließend ergänzt. Der Moodle-Solver las die vier fehlenden
Abschnitte nach und prüfte die vollständige Erklärung mit einem separaten
Audit: 16 Dateien, keine nicht erklärten sinntragenden Quellzeilen.

Nach Abschluss von Codex führte der Moodle-Solver alle 95 Repository-Tests,
alle sieben Programm-CLIs sowie zusätzliche Leer-/Queue- und Dateifälle
nochmals aus. Alle vorgesehenen Erfolgsaufrufe endeten mit Status 0.
Ein automatischer Vergleich bestätigte zudem die stdout-/stderr-Ausgaben
aller 34 hier protokollierten CLI-Fälle gegen die tatsächliche Rohaufzeichnung.
Die ursprünglichen PDF- und ZIP-Dateien sind bytegleich zu den Moodle-Downloads.
Die Git-Veröffentlichung durch den Moodle-Solver folgt erst nach diesen Prüfungen.

**KI-Kennzeichnung:** Mit KI erstellt; keine Eigenleistung behauptet.
Vorbereitung: Hermes Agent; OpenAI / gpt-6.1-sol; Provider laut hermes status:
ChatGPT or Codex Subscription. Implementierung: Codex CLI 0.162.1;
Modell gpt-6.1-sol; Datum 2026-10-13. Anfrage: Implementiere Übungsblatt 01
vollständig mit Standardbibliothek, führe alle Tests und CLIs tatsächlich
aus und dokumentiere echte Kommandos, Umgebung, Ergebnisse und Grenzen.
