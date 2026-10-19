# Abschließendes tatsächliches Prüfprotokoll – Blatt 02

Zeitpunkt: 2026-10-19T14:00:13+02:00

Python: 3.14.7

## Tatsächlich gestartete Tests und Programme

### ue2.6

Befehl: `python3 -B -m unittest discover -s ue2.6 -p 'test_*.py' -v`

```text
test_explanation_covers_all_code_lines (test_protocol.ArtifactTests.test_explanation_covers_all_code_lines) ... ok
test_local_markdown_links (test_protocol.ArtifactTests.test_local_markdown_links) ... ok
test_svg_xml (test_protocol.ArtifactTests.test_svg_xml) ... ok
test_bad_transaction_ids_and_unknown_tx (test_protocol.BankTests.test_bad_transaction_ids_and_unknown_tx) ... ok
test_cancel_after_begin_forbidden (test_protocol.BankTests.test_cancel_after_begin_forbidden) ... ok
test_cancel_and_retry (test_protocol.BankTests.test_cancel_and_retry) ... ok
test_concurrent_distinct_reservations (test_protocol.BankTests.test_concurrent_distinct_reservations) ... ok
test_concurrent_duplicate_commit (test_protocol.BankTests.test_concurrent_duplicate_commit) ... ok
test_conflicting_result (test_protocol.BankTests.test_conflicting_result) ... ok
test_declined_id_is_not_reactivated (test_protocol.BankTests.test_declined_id_is_not_reactivated) ... ok
test_dispensing_never_expires_automatically (test_protocol.BankTests.test_dispensing_never_expires_automatically) ... ok
test_exact_available_balance (test_protocol.BankTests.test_exact_available_balance) ... ok
test_expired_id_is_not_reactivated (test_protocol.BankTests.test_expired_id_is_not_reactivated) ... ok
test_failure_releases_hold (test_protocol.BankTests.test_failure_releases_hold) ... ok
test_insufficient_funds (test_protocol.BankTests.test_insufficient_funds) ... ok
test_invalid_amounts (test_protocol.BankTests.test_invalid_amounts) ... ok
test_invalid_initial_balance (test_protocol.BankTests.test_invalid_initial_balance) ... ok
test_invalid_outcome_is_atomic (test_protocol.BankTests.test_invalid_outcome_is_atomic) ... ok
test_logout_does_not_release_dispensing_hold (test_protocol.BankTests.test_logout_does_not_release_dispensing_hold) ... ok
test_lost_result_reply_same_request (test_protocol.BankTests.test_lost_result_reply_same_request) ... ok
test_maximum_amount (test_protocol.BankTests.test_maximum_amount) ... ok
test_missing_session_and_correlation (test_protocol.BankTests.test_missing_session_and_correlation) ... ok
test_multiple_reservations_cannot_overspend (test_protocol.BankTests.test_multiple_reservations_cannot_overspend) ... ok
test_reconciliation_delivered (test_protocol.BankTests.test_reconciliation_delivered) ... ok
test_reconciliation_not_delivered (test_protocol.BankTests.test_reconciliation_not_delivered) ... ok
test_request_validation (test_protocol.BankTests.test_request_validation) ... ok
test_reservation_timeout_at_boundary (test_protocol.BankTests.test_reservation_timeout_at_boundary) ... ok
test_reserve_and_begin_retries (test_protocol.BankTests.test_reserve_and_begin_retries) ... ok
test_result_before_begin_forbidden (test_protocol.BankTests.test_result_before_begin_forbidden) ... ok
test_result_retry_new_request_id (test_protocol.BankTests.test_result_retry_new_request_id) ... ok
test_session_binding_and_logout (test_protocol.BankTests.test_session_binding_and_logout) ... ok
test_session_expiry_and_reauthentication (test_protocol.BankTests.test_session_expiry_and_reauthentication) ... ok
test_success_resets_failed_attempts (test_protocol.BankTests.test_success_resets_failed_attempts) ... ok
test_successful_withdrawal (test_protocol.BankTests.test_successful_withdrawal) ... ok
test_transaction_amount_conflict (test_protocol.BankTests.test_transaction_amount_conflict) ... ok
test_transaction_card_binding (test_protocol.BankTests.test_transaction_card_binding) ... ok
test_transaction_terminal_binding (test_protocol.BankTests.test_transaction_terminal_binding) ... ok
test_unknown_card_and_invalid_pin (test_protocol.BankTests.test_unknown_card_and_invalid_pin) ... ok
test_unknown_keeps_hold_and_forbids_client_resolution (test_protocol.BankTests.test_unknown_keeps_hold_and_forbids_client_resolution) ... ok
test_unknown_never_expires_automatically (test_protocol.BankTests.test_unknown_never_expires_automatically) ... ok
test_wrong_pin_and_lock (test_protocol.BankTests.test_wrong_pin_and_lock) ... ok
test_concurrent_duplicate_payout (test_protocol.DispenserTests.test_concurrent_duplicate_payout) ... ok
test_duplicate_success_never_pays_twice (test_protocol.DispenserTests.test_duplicate_success_never_pays_twice) ... ok
test_failure_does_not_pay (test_protocol.DispenserTests.test_failure_does_not_pay) ... ok
test_invalid_dispenser_input (test_protocol.DispenserTests.test_invalid_dispenser_input) ... ok
test_uncertainty_is_not_retried (test_protocol.DispenserTests.test_uncertainty_is_not_retried) ... ok
test_coalesced_frames (test_protocol.FramingTests.test_coalesced_frames) ... ok
test_encode_rejects_invalid_data (test_protocol.FramingTests.test_encode_rejects_invalid_data) ... ok
test_every_split_position (test_protocol.FramingTests.test_every_split_position) ... ok
test_exact_maximum_frame (test_protocol.FramingTests.test_exact_maximum_frame) ... ok
test_invalid_json (test_protocol.FramingTests.test_invalid_json) ... ok
test_invalid_lengths (test_protocol.FramingTests.test_invalid_lengths) ... ok
test_one_byte_at_a_time (test_protocol.FramingTests.test_one_byte_at_a_time) ... ok
test_roundtrip_and_utf8 (test_protocol.FramingTests.test_roundtrip_and_utf8) ... ok
test_truncated_eof (test_protocol.FramingTests.test_truncated_eof) ... ok

----------------------------------------------------------------------
Ran 55 tests in 0.020s

OK
```

### ue2.10

Befehl: `python3 -B -m unittest discover -s ue2.10 -p 'test_*.py' -v`

```text
test_01_real_nonempty_capture (test_capture.CaptureTests.test_01_real_nonempty_capture) ... ok
test_02_only_own_loopback_tuple (test_capture.CaptureTests.test_02_only_own_loopback_tuple) ... ok
test_03_exact_http_request (test_capture.CaptureTests.test_03_exact_http_request) ... ok
test_04_exact_http_response (test_capture.CaptureTests.test_04_exact_http_response) ... ok
test_05_tcp_open_close_no_reset (test_capture.CaptureTests.test_05_tcp_open_close_no_reset) ... ok
test_06_safe_capture_options (test_capture.CaptureTests.test_06_safe_capture_options) ... ok
test_07_refuse_to_overwrite (test_capture.CaptureTests.test_07_refuse_to_overwrite) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

### ue2.11

Befehl: `python3 -B -m unittest discover -s ue2.11 -p 'test_*.py' -v`

```text
test_big_endian (test_analyse.AnalysisTests.test_big_endian) ... ok
test_chunked_body (test_analyse.AnalysisTests.test_chunked_body) ... ok
test_gui_conversations (test_analyse.AnalysisTests.test_gui_conversations) ... ok
test_gui_hierarchy (test_analyse.AnalysisTests.test_gui_hierarchy) ... ok
test_incomplete_body (test_analyse.AnalysisTests.test_incomplete_body) ... ok
test_invalid_chunk (test_analyse.AnalysisTests.test_invalid_chunk) ... ok
test_invalid_pcap (test_analyse.AnalysisTests.test_invalid_pcap) ... ok
test_missing_header_terminator (test_analyse.AnalysisTests.test_missing_header_terminator) ... ok
test_padding_not_tcp_payload (test_analyse.AnalysisTests.test_padding_not_tcp_payload) ... ok
test_persistent_http (test_analyse.AnalysisTests.test_persistent_http) ... ok
test_protocol_counts (test_analyse.AnalysisTests.test_protocol_counts) ... ok
test_reassemble_conflict (test_analyse.AnalysisTests.test_reassemble_conflict) ... ok
test_reassemble_empty (test_analyse.AnalysisTests.test_reassemble_empty) ... ok
test_reassemble_gap (test_analyse.AnalysisTests.test_reassemble_gap) ... ok
test_reassemble_retransmission (test_analyse.AnalysisTests.test_reassemble_retransmission) ... ok
test_truncated_pcap (test_analyse.AnalysisTests.test_truncated_pcap) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.009s

OK
```

### ue2.12

Befehl: `python3 -B -m unittest discover -s ue2.12 -p 'test_*.py' -v`

```text
test_all_byte_metrics (test_bericht.HTTPTests.test_all_byte_metrics) ... ok
test_persistent_comparison (test_bericht.HTTPTests.test_persistent_comparison) ... ok
test_report_runs (test_bericht.HTTPTests.test_report_runs) ... ok
test_three_objects (test_bericht.HTTPTests.test_three_objects) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.025s

OK
```

**Summe: 82 Tests erfolgreich; keine Fehler, keine übersprungenen Tests.**

### ue2.6/demo.py

```text
FAP/1: In-Memory-Unterrichtssimulation, ohne TLS und ohne echte Bank.
AUTH OK (PIN und Sitzung werden nicht ausgegeben)
BALANCE OK {'booked': 10000, 'available': 10000, 'currency': 'EUR'}
RESERVE OK {'tx': '8be95089-e903-4d27-8b64-0f8cbb97c3c6', 'amount': 4000, 'currency': 'EUR', 'state': 'RESERVED'}
BEGIN OK {'tx': '8be95089-e903-4d27-8b64-0f8cbb97c3c6', 'amount': 4000, 'currency': 'EUR', 'state': 'DISPENSING'}
RESULT-Antwort absichtlich verworfen; dieselbe Nachricht erneut senden.
RESULT (Retry) OK {'tx': '8be95089-e903-4d27-8b64-0f8cbb97c3c6', 'amount': 4000, 'currency': 'EUR', 'state': 'COMMITTED'}
BALANCE OK {'booked': 6000, 'available': 6000, 'currency': 'EUR'}
RESERVE OK {'tx': '97092389-864a-40c0-97ed-7dfd507eacfd', 'amount': 7000, 'currency': 'EUR', 'state': 'DECLINED'}
Zu wenig Deckung: keine Reservierung, keine Ausgabe, keine Abbuchung.
LOGOUT OK {}
Demo-Prüfungen erfolgreich; ausgegebene Cent: 4000
```

### ue2.7/kosten.py

```text
1 x UCG-Ultra: 114.00 EUR = 114.00 EUR
1 x USW-Lite-8-PoE: 124.00 EUR = 124.00 EUR
2 x U6+: 111.90 EUR = 223.80 EUR
Warenwert inkl. MwSt.: 461.80 EUR
Versand laut ausgewählten Angeboten: 0.00 EUR
Geplante Anschaffung gesamt: 461.80 EUR
AP-Leistungsbedarf maximal: 18 W
Rechnerische PoE-Budgetreserve: 34 W
Planungsrechnung, keine Bestellung und keine Verbrauchsmessung.
```

### ue2.12/bericht.py

```text
Byteangaben dezimal; Dauer = letztes minus erstes Paket der Verbindung.

dump_http.pcap: 68 Pakete, 3 TCP-Verbindungen
Stream 0: ['192.168.3.10', 37184] → ['192.168.1.10', 80]
  Frame-Bytes C→S/S→C: [476, 760]; Summe 1236
  IPv4-Bytes C→S/S→C: [406, 690]; Summe 1096
  TCP-Nutzbytes C→S/S→C: [138, 422]; Summe 560
  Dauer: 0.301299000 s
  GET /test/ HTTP/1.0 → HTTP/1.1 200 OK
    Body: 145 B; Typ text/html
Stream 1: ['192.168.3.10', 37185] → ['192.168.1.10', 80]
  Frame-Bytes C→S/S→C: [616, 5198]; Summe 5814
  IPv4-Bytes C→S/S→C: [518, 5100]; Summe 5618
  TCP-Nutzbytes C→S/S→C: [146, 4728]; Summe 4874
  Dauer: 0.301248000 s
  GET /test/logo.gif HTTP/1.0 → HTTP/1.1 200 OK
    Body: 4445 B; Typ image/gif
Stream 2: ['192.168.3.10', 37186] → ['192.168.1.10', 80]
  Frame-Bytes C→S/S→C: [1616, 28809]; Summe 30425
  IPv4-Bytes C→S/S→C: [1308, 28501]; Summe 29809
  TCP-Nutzbytes C→S/S→C: [156, 27349]; Summe 27505
  Dauer: 0.502194000 s
  GET /test/TechnikErleben.png HTTP/1.0 → HTTP/1.1 200 OK
    Body: 27065 B; Typ image/png

dump_protocols.pcap: 39 Pakete, 1 TCP-Verbindungen
Stream 0: ['192.168.1.215', 54961] → ['192.168.1.1', 80]
  Frame-Bytes C→S/S→C: [567, 1196]; Summe 1763
  IPv4-Bytes C→S/S→C: [455, 1072]; Summe 1527
  TCP-Nutzbytes C→S/S→C: [115, 740]; Summe 855
  Dauer: 0.007399000 s
  GET / HTTP/1.1 → HTTP/1.1 200 OK
    Body: 577 B; Typ text/html

dump_http_persistent.pcap: 46 Pakete, 1 TCP-Verbindungen
Stream 0: ['192.168.3.10', 50776] → ['192.168.1.10', 80]
  Frame-Bytes C→S/S→C: [1774, 34349]; Summe 36123
  IPv4-Bytes C→S/S→C: [1508, 33971]; Summe 35479
  TCP-Nutzbytes C→S/S→C: [512, 32559]; Summe 33071
  Dauer: 0.704626000 s
  GET /test/ HTTP/1.0 → HTTP/1.1 200 OK
    Body: 145 B; Typ text/html
  GET /test/logo.gif HTTP/1.0 → HTTP/1.1 200 OK
    Body: 4445 B; Typ image/gif
  GET /test/TechnikErleben.png HTTP/1.0 → HTTP/1.1 200 OK
    Body: 27065 B; Typ image/png
```

## Artefaktprüfung

- Alle 11 im Original vorhandenen Aufgaben haben Antworten mit KI-Kennzeichnung; Ü2.3 fehlt absichtlich.
- Alle 10 Python-Dateien sind syntaktisch gültig und gekennzeichnet.
- Original-PDF und alle drei Moodle-PCAPs wurden bytegleich übernommen.
- SVGs als XML und PNG-Signaturen geprüft; Protokollhierarchie tatsächlich gerendert und visuell kontrolliert.
- Zusammengeführte Erklärung wurde aus den vier tatsächlichen Lernquellen erstellt.
- Bericht aus frischer Ausführung stimmt exakt mit dem gespeicherten Messbericht überein.
- Bank-, Capture- und Analyse-Zeilenerklärungen wurden zusätzlich auf vollständige Zeilenabdeckung geprüft.

## Originaldateien: Größen und echte SHA-256

- `angabe_blatt02.pdf`: 105876 Bytes; SHA-256 `b17ed8760282662e3cbb1ede8ebf7519a898a020adfa8f9a9488fe5deaa0b444`.
- `Angabe/dump_http.pcap`: 38587 Bytes; SHA-256 `d2d7195f15ba21e5952481e41e302adec96aee516fcc6256329cf896b33d2f3c`.
- `Angabe/dump_http_persistent.pcap`: 36883 Bytes; SHA-256 `a50377f3f14bcb8fcc763336f263e0ba921fd8daf4ae96be6506f33d49a68d48`.
- `Angabe/dump_protocols.pcap`: 4815 Bytes; SHA-256 `2db07f853d09621f21364a72612d0e1e0d951e0ade05a615eb17a69730b28c55`.

## Unabhängige Prüfung und Befundbehandlung

- Theorie und Bank wurden von einer getrennten Instanz gegen das Original gelesen; die Banktests und Kostenrechnung wurden unabhängig ausgeführt.
- Ein Befund zur RESULT-FAIL-Bestätigung nach CANCEL/Timeout wurde durch präzise Dokumentation der vorhandenen wirkungslosen Zielzustandsbestätigung behoben; keine neue Auszahlung oder Abbuchung.
- Wiresharks echte GUI-CSV-Exporte wurden gegen den getrennten Offlineparser geprüft. Der Dauervergleich verwendet Nanosekunden-Toleranz, weil der GUI-Export binäre Fließkomma-Rundungsreste enthalten kann; die Originalzeitstempel wurden nicht verändert.
- Eine weitere Instanz prüfte PCAP-/HTTP-Endwerte unabhängig mit Scapy und http.client.HTTPResponse, ohne den getesteten Parser zu importieren. Protokolle, Header, Bytes, Dauern und Body-Hashes stimmen überein.
- Die tatsächliche eigene Live-Aufnahme und ein zweiter eigener Durchlauf sind unter ue2.10 dokumentiert. Die finalen Offline-Tests erfinden oder regenerieren keine Messdaten.

## Offen / Grenzen

- Ü2.7 ist ein transparenter Referenzhaus-Entwurf. Die Anpassung an das tatsächliche eigene/elterliche Haus bleibt mangels Hausdaten offen; keine Funkmesswerte werden behauptet.
- Gruppennummer unbekannt: kein willkürlich benanntes Abgabe-ZIP. Keine Moodle-Abgabe durchgeführt.
- Unterrichts-Bankcode: kein implementiertes TLS, keine Persistenz, keine echte Auszahlung.

## KI-Kennzeichnung

Hermes Agent, OpenAI gpt-6.1-sol, 2026-10-19. Anfrage: fertige Aufgaben vollständig prüfen, vorhandene Tests und Demos tatsächlich ausführen und nur reale Ergebnisse protokollieren.
