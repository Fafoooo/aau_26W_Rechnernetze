# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Ü2.6: umfassende unittest-Tests für das didaktische Bankomatprotokoll,
# insbesondere Authentifizierung, Framing, Reservierungen, Retry und Fehlerfälle.
"""Offline-Tests, einschließlich konkurrierender Wiederholungen."""
import concurrent.futures
import struct
import unittest
import uuid

from protocol import (Bank, Decoder, Dispenser, Fault, MAX_FRAME, SESSION_TTL,
                      RESERVATION_TTL, encode, exchange, request)


def new_id():
    return str(uuid.uuid4())


class FramingTests(unittest.TestCase):
    def test_roundtrip_and_utf8(self):
        message = {"text": "Grüße €"}
        self.assertEqual(Decoder().feed(encode(message)), [message])
        self.assertEqual(struct.unpack("!I", encode(message)[:4])[0], len(encode(message)) - 4)

    def test_every_split_position(self):
        frame = encode({"v": 1, "text": "€"})
        for split in range(len(frame) + 1):
            decoder = Decoder()
            result = decoder.feed(frame[:split]) + decoder.feed(frame[split:])
            self.assertEqual(result, [{"v": 1, "text": "€"}])
            decoder.eof()

    def test_one_byte_at_a_time(self):
        decoder, messages = Decoder(), []
        for byte in encode({"ok": True}):
            messages.extend(decoder.feed(bytes([byte])))
        self.assertEqual(messages, [{"ok": True}])

    def test_coalesced_frames(self):
        self.assertEqual(Decoder().feed(encode({"a": 1}) + encode({"b": 2})),
                         [{"a": 1}, {"b": 2}])

    def test_invalid_lengths(self):
        for length in (0, MAX_FRAME + 1, 2**32 - 1):
            with self.subTest(length=length), self.assertRaises(ValueError):
                Decoder().feed(struct.pack("!I", length))

    def test_invalid_json(self):
        for raw in (b"{", b"[]", b"\xff", b'{"a":1,"a":2}', b'{"a":NaN}',
                    b'{"a":Infinity}', b'{"a":-Infinity}', b"null"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                Decoder().feed(struct.pack("!I", len(raw)) + raw)

    def test_truncated_eof(self):
        for data in (b"\x00", encode({"a": 1})[:-1]):
            decoder = Decoder()
            decoder.feed(data)
            with self.assertRaises(ValueError):
                decoder.eof()

    def test_encode_rejects_invalid_data(self):
        for message in ([], {"a": float("nan")}, {"a": "x" * MAX_FRAME}):
            with self.subTest(message_type=type(message)), self.assertRaises(ValueError):
                encode(message)

    def test_exact_maximum_frame(self):
        message = {"x": "a" * (MAX_FRAME - len(b'{"x":""}'))}
        self.assertEqual(len(encode(message)), MAX_FRAME + 4)
        self.assertEqual(Decoder().feed(encode(message)), [message])


class BankTests(unittest.TestCase):
    def setUp(self):
        self.now = 1000.0
        self.bank = Bank(clock=lambda: self.now, balance=10_000)
        self.sid = self.auth()
        self.txid = new_id()

    def auth(self, terminal="DEMO-ATM-1"):
        response = exchange(self.bank, request("AUTH", {"card": "DEMO-CARD-A", "pin": "1234"}), terminal)
        self.assertEqual(response["status"], "OK")
        return response["body"]["sid"]

    def call(self, op, body=None, sid=None, terminal="DEMO-ATM-1"):
        return exchange(self.bank, request(op, body, self.sid if sid is None else sid), terminal)

    def ok(self, op, body=None):
        response = self.call(op, body)
        self.assertEqual(response["status"], "OK", response)
        return response["body"]

    def reserve(self, amount=4000):
        return self.ok("RESERVE", {"tx": self.txid, "amount": amount})

    def begin(self):
        self.reserve()
        return self.ok("BEGIN", {"tx": self.txid})

    def finish(self, outcome):
        return self.ok("RESULT", {"tx": self.txid, "outcome": outcome})

    def test_successful_withdrawal(self):
        self.assertEqual(self.reserve()["state"], "RESERVED")
        self.assertEqual(self.ok("BALANCE"), {"booked": 10_000, "available": 6000, "currency": "EUR"})
        self.assertEqual(self.ok("BEGIN", {"tx": self.txid})["state"], "DISPENSING")
        self.assertEqual(self.finish("OK")["state"], "COMMITTED")
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_insufficient_funds(self):
        response = self.reserve(11_000)
        self.assertEqual(response["state"], "DECLINED")
        self.assertEqual(self.reserve(11_000), response)
        self.assertEqual(self.ok("BALANCE")["available"], 10_000)
        self.assertEqual(self.call("BEGIN", {"tx": self.txid})["status"], "INVALID_STATE")

    def test_exact_available_balance(self):
        self.reserve(10_000)
        self.ok("BEGIN", {"tx": self.txid})
        self.finish("OK")
        self.assertEqual(self.ok("BALANCE")["booked"], 0)

    def test_invalid_amounts(self):
        for amount in (True, False, 0, -1000, 1, 1500, 101_000, 1000.0, "1000", None):
            with self.subTest(amount=amount):
                response = self.call("RESERVE", {"tx": new_id(), "amount": amount})
                self.assertEqual(response["status"], "BAD_AMOUNT")
        self.assertEqual(self.bank.transactions, {})

    def test_maximum_amount(self):
        self.bank.accounts["DEMO-CARD-A"]["balance"] = 100_000
        self.assertEqual(self.reserve(100_000)["state"], "RESERVED")

    def test_reserve_and_begin_retries(self):
        first = self.reserve()
        for _ in range(5):
            self.assertEqual(self.reserve(), first)
        self.ok("BEGIN", {"tx": self.txid})
        self.assertEqual(self.reserve()["state"], "DISPENSING")
        self.assertEqual(self.ok("BEGIN", {"tx": self.txid})["state"], "DISPENSING")
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_transaction_amount_conflict(self):
        self.reserve()
        self.assertEqual(self.call("RESERVE", {"tx": self.txid, "amount": 5000})["status"], "TX_CONFLICT")
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_lost_result_reply_same_request(self):
        self.begin()
        message = request("RESULT", {"tx": self.txid, "outcome": "OK"}, self.sid)
        first = exchange(self.bank, message)
        self.assertEqual(exchange(self.bank, message), first)
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_result_retry_new_request_id(self):
        self.begin()
        self.finish("OK")
        self.finish("OK")
        self.assertEqual(self.reserve()["state"], "COMMITTED")
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_conflicting_result(self):
        self.begin()
        self.finish("OK")
        self.assertEqual(self.call("RESULT", {"tx": self.txid, "outcome": "FAIL"})["status"], "INVALID_STATE")
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_failure_releases_hold(self):
        self.begin()
        self.assertEqual(self.finish("FAIL")["state"], "CANCELLED")
        self.finish("FAIL")
        self.assertEqual(self.ok("BALANCE")["available"], 10_000)

    def test_unknown_keeps_hold_and_forbids_client_resolution(self):
        self.begin()
        self.assertEqual(self.finish("UNKNOWN")["state"], "UNKNOWN")
        self.finish("UNKNOWN")
        for op, body in (("CANCEL", {"tx": self.txid}),
                         ("RESULT", {"tx": self.txid, "outcome": "OK"}),
                         ("RESULT", {"tx": self.txid, "outcome": "FAIL"})):
            self.assertEqual(self.call(op, body)["status"], "INVALID_STATE")
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_reconciliation_delivered(self):
        self.begin()
        self.finish("UNKNOWN")
        self.bank.reconcile(self.txid, True)
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "COMMITTED")
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)
        with self.assertRaises(Fault):
            self.bank.reconcile(self.txid, True)
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_reconciliation_not_delivered(self):
        self.begin()
        self.bank.reconcile(self.txid, False)
        self.assertEqual(self.ok("BALANCE")["available"], 10_000)
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "CANCELLED")

    def test_cancel_and_retry(self):
        self.reserve()
        self.ok("CANCEL", {"tx": self.txid})
        self.ok("CANCEL", {"tx": self.txid})
        self.assertEqual(self.reserve()["state"], "CANCELLED")
        self.assertEqual(self.ok("BALANCE")["available"], 10_000)

    def test_cancel_after_begin_forbidden(self):
        self.begin()
        self.assertEqual(self.call("CANCEL", {"tx": self.txid})["status"], "INVALID_STATE")

    def test_result_before_begin_forbidden(self):
        self.reserve()
        self.assertEqual(self.call("RESULT", {"tx": self.txid, "outcome": "OK"})["status"], "INVALID_STATE")

    def test_reservation_timeout_at_boundary(self):
        self.reserve()
        self.now += RESERVATION_TTL
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "CANCELLED")
        self.assertEqual(self.ok("BALANCE")["available"], 10_000)
        self.assertEqual(self.call("BEGIN", {"tx": self.txid})["status"], "INVALID_STATE")

    def test_dispensing_never_expires_automatically(self):
        self.begin()
        self.now += SESSION_TTL + 1000
        self.sid = self.auth()
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "DISPENSING")
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_unknown_never_expires_automatically(self):
        self.begin()
        self.finish("UNKNOWN")
        self.now += SESSION_TTL + 1000
        self.sid = self.auth()
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "UNKNOWN")
        self.assertEqual(self.ok("BALANCE")["available"], 6000)

    def test_session_expiry_and_reauthentication(self):
        self.begin()
        self.now += SESSION_TTL
        self.assertEqual(self.call("BALANCE")["status"], "SESSION_EXPIRED")
        self.sid = self.auth()
        self.finish("OK")
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_session_binding_and_logout(self):
        self.assertEqual(self.call("BALANCE", terminal="OTHER-ATM")["status"], "UNAUTHORIZED")
        self.ok("LOGOUT")
        self.assertEqual(self.call("BALANCE")["status"], "UNAUTHORIZED")
        self.assertEqual(self.call("BALANCE", sid=new_id())["status"], "UNAUTHORIZED")

    def test_transaction_terminal_binding(self):
        self.reserve()
        other_sid = self.auth("OTHER-ATM")
        self.assertEqual(self.call("STATUS", {"tx": self.txid}, other_sid, "OTHER-ATM")["status"], "FORBIDDEN")

    def test_wrong_pin_and_lock(self):
        for _ in range(3):
            response = exchange(self.bank, request("AUTH", {"card": "DEMO-CARD-A", "pin": "9999"}))
            self.assertEqual(response["status"], "AUTH_FAILED")
        response = exchange(self.bank, request("AUTH", {"card": "DEMO-CARD-A", "pin": "1234"}))
        self.assertEqual(response["status"], "AUTH_FAILED")

    def test_unknown_card_and_invalid_pin(self):
        for card, pin, expected in (("MISSING", "1234", "AUTH_FAILED"),
                                    ("DEMO-CARD-A", "１２３４", "BAD_REQUEST"),
                                    ("DEMO-CARD-A", 1234, "BAD_REQUEST")):
            response = exchange(self.bank, request("AUTH", {"card": card, "pin": pin}))
            self.assertEqual(response["status"], expected)

    def test_success_resets_failed_attempts(self):
        exchange(self.bank, request("AUTH", {"card": "DEMO-CARD-A", "pin": "9999"}))
        self.auth()
        self.assertEqual(self.bank.accounts["DEMO-CARD-A"]["failures"], 0)

    def test_request_validation(self):
        cases = [(dict(request("BALANCE"), v=True), "BAD_VERSION"),
                 (dict(request("BALANCE"), v=2), "BAD_VERSION"),
                 (dict(request("BALANCE"), id="not-a-uuid"), "BAD_REQUEST"),
                 (dict(request("BALANCE"), extra=1), "BAD_REQUEST"),
                 (request("MISSING"), "UNKNOWN_OP"),
                 (request("BALANCE", {"extra": 1}, self.sid), "BAD_REQUEST"),
                 (request("BALANCE", [], self.sid), "BAD_REQUEST"),
                 (request("AUTH", {"card": "DEMO-CARD-A", "pin": "1234"}, self.sid), "BAD_REQUEST")]
        for message, expected in cases:
            with self.subTest(message=message):
                self.assertEqual(exchange(self.bank, message)["status"], expected)
        self.assertEqual(self.bank.handle([])["status"], "BAD_REQUEST")
        self.assertEqual(self.bank.handle({})["id"], None)

    def test_bad_transaction_ids_and_unknown_tx(self):
        for txid in (None, 123, "bad", "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"):
            self.assertEqual(self.call("STATUS", {"tx": txid})["status"], "BAD_REQUEST")
        self.assertEqual(self.call("STATUS", {"tx": new_id()})["status"], "NOT_FOUND")

    def test_invalid_outcome_is_atomic(self):
        self.begin()
        for outcome in (None, [], True, "MAYBE"):
            self.assertEqual(self.call("RESULT", {"tx": self.txid, "outcome": outcome})["status"], "BAD_REQUEST")
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "DISPENSING")
        self.assertEqual(self.ok("BALANCE")["booked"], 10_000)

    def test_multiple_reservations_cannot_overspend(self):
        self.reserve(7000)
        second = self.ok("RESERVE", {"tx": new_id(), "amount": 4000})
        self.assertEqual(second["state"], "DECLINED")
        self.assertEqual(self.ok("BALANCE")["available"], 3000)

    def test_concurrent_duplicate_commit(self):
        self.begin()
        message = request("RESULT", {"tx": self.txid, "outcome": "OK"}, self.sid)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: exchange(self.bank, message), range(40)))
        self.assertTrue(all(r["body"]["state"] == "COMMITTED" for r in results))
        self.assertEqual(self.ok("BALANCE")["booked"], 6000)

    def test_concurrent_distinct_reservations(self):
        def reserve_one(_):
            return self.call("RESERVE", {"tx": new_id(), "amount": 7000})["body"]["state"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            states = list(pool.map(reserve_one, range(20)))
        self.assertEqual(states.count("RESERVED"), 1)
        self.assertEqual(states.count("DECLINED"), 19)
        self.assertEqual(self.ok("BALANCE")["available"], 3000)

    def test_transaction_card_binding(self):
        self.reserve()
        self.bank.accounts["DEMO-CARD-B"] = {"pin": "5678", "balance": 10_000, "failures": 0}
        response = exchange(self.bank, request("AUTH", {"card": "DEMO-CARD-B", "pin": "5678"}))
        other_sid = response["body"]["sid"]
        self.assertEqual(self.call("STATUS", {"tx": self.txid}, other_sid)["status"], "FORBIDDEN")

    def test_logout_does_not_release_dispensing_hold(self):
        self.begin()
        self.ok("LOGOUT")
        self.sid = self.auth()
        self.assertEqual(self.ok("BALANCE")["available"], 6000)
        self.assertEqual(self.ok("STATUS", {"tx": self.txid})["state"], "DISPENSING")

    def test_declined_id_is_not_reactivated(self):
        self.reserve(11_000)
        self.bank.accounts["DEMO-CARD-A"]["balance"] = 20_000
        self.assertEqual(self.reserve(11_000)["state"], "DECLINED")
        self.assertEqual(self.ok("BALANCE")["available"], 20_000)

    def test_expired_id_is_not_reactivated(self):
        self.reserve()
        self.now += RESERVATION_TTL
        self.assertEqual(self.reserve()["state"], "CANCELLED")

    def test_missing_session_and_correlation(self):
        message = request("BALANCE")
        response = exchange(self.bank, message)
        self.assertEqual(response["id"], message["id"])
        self.assertEqual(response["status"], "BAD_REQUEST")
        self.assertEqual(self.bank.transactions, {})

    def test_invalid_initial_balance(self):
        for balance in (True, -1, 100_000_001, 1.5):
            with self.assertRaises(ValueError):
                Bank(balance=balance)  # pyright: ignore[reportArgumentType] -- absichtlich falscher Typ


class DispenserTests(unittest.TestCase):
    def test_duplicate_success_never_pays_twice(self):
        dispenser, txid = Dispenser(), new_id()
        self.assertEqual(dispenser.dispense(txid, 4000), "OK")
        self.assertEqual(dispenser.dispense(txid, 4000), "OK")
        self.assertEqual(dispenser.cash, 4000)
        with self.assertRaises(Fault):
            dispenser.dispense(txid, 5000)

    def test_failure_does_not_pay(self):
        dispenser, txid = Dispenser(), new_id()
        self.assertEqual(dispenser.dispense(txid, 4000, "FAIL"), "FAIL")
        self.assertEqual(dispenser.dispense(txid, 4000, "OK"), "FAIL")
        self.assertEqual(dispenser.cash, 0)

    def test_uncertainty_is_not_retried(self):
        dispenser, txid = Dispenser(), new_id()
        self.assertEqual(dispenser.dispense(txid, 4000, "UNKNOWN"), "UNKNOWN")
        self.assertEqual(dispenser.dispense(txid, 4000, "OK"), "UNKNOWN")
        self.assertEqual(dispenser.cash, 0)

    def test_concurrent_duplicate_payout(self):
        dispenser, txid = Dispenser(), new_id()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: dispenser.dispense(txid, 4000), range(40)))
        self.assertEqual(set(results), {"OK"})
        self.assertEqual(dispenser.cash, 4000)

    def test_invalid_dispenser_input(self):
        dispenser = Dispenser()
        for amount in (True, 0, -1, 1500, 101_000):
            with self.assertRaises(Fault):
                dispenser.dispense(new_id(), amount)
        with self.assertRaises(Fault):
            dispenser.dispense(new_id(), 4000, "MAYBE")
        self.assertEqual(dispenser.journal, {})


class ArtifactTests(unittest.TestCase):
    def base(self):
        from pathlib import Path
        return Path(__file__).resolve().parent.parent

    def test_svg_xml(self):
        import xml.etree.ElementTree as ET
        root = ET.parse(self.base() / "ue2.6/sequenz.svg").getroot()
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_local_markdown_links(self):
        import re
        for name in ("ue2.6/antwort.md", "erklaerung_bank.md"):
            path = self.base() / name
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link).exists(), link)

    def test_explanation_covers_all_code_lines(self):
        import re
        text = (self.base() / "erklaerung_bank.md").read_text()
        specs = (("protocol.py", "## 3.", "## 4."),
                 ("demo.py", "## 4.", "## 5."),
                 ("test_protocol.py", "## 5.", "## 6."))
        for filename, start, end in specs:
            section = text.split(start, 1)[1].split(end, 1)[0]
            covered = set(range(1, 6))
            for first, last in re.findall(r"^\| (\d+)(?:[–-](\d+))? \|", section, re.M):
                covered.update(range(int(first), int(last or first) + 1))
            lines = (self.base() / "ue2.6" / filename).read_text().splitlines()
            missing = [n for n, line in enumerate(lines, 1) if line.strip() and n not in covered]
            self.assertEqual(missing, [], filename)


if __name__ == "__main__":
    unittest.main(verbosity=2)
