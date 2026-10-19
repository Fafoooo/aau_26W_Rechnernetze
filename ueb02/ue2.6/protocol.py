# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Ü2.6: fiktives Bankomatprotokoll RFC-artig entwerfen, didaktischen
# Python-Referenzcode mit sicherer Wiederholung und Tests erstellen und erklären.
"""FAP/1: reine In-Memory-Unterrichtssimulation, kein Bank- oder TLS-System."""
import hmac
import json
import struct
import threading
import time
import uuid

MAX_FRAME = 4096
MAX_AMOUNT = 100_000
SESSION_TTL = 300
RESERVATION_TTL = 60
HELD = {"RESERVED", "DISPENSING", "UNKNOWN"}


class Fault(Exception):
    """Ein erwartbarer Protokollfehler mit maschinenlesbarem Status."""


def require(condition, status="BAD_REQUEST"):
    if not condition:
        raise Fault(status)


def identifier(value):
    require(type(value) is str)
    try:
        require(str(uuid.UUID(value)) == value)
    except (ValueError, AttributeError):
        raise Fault("BAD_REQUEST") from None
    return value


def encode(message):
    """Ein JSON-Objekt als vier Byte Länge (Big Endian) plus UTF-8."""
    if type(message) is not dict:
        raise ValueError("object required")
    raw = json.dumps(message, ensure_ascii=False, allow_nan=False,
                     separators=(",", ":")).encode("utf-8")
    if not 1 <= len(raw) <= MAX_FRAME:
        raise ValueError("frame size")
    return struct.pack("!I", len(raw)) + raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("non-finite JSON constant: " + value)


class Decoder:
    """Beliebig fragmentierten oder zusammengefassten Bytestrom lesen."""
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)
        messages = []
        while len(self.buffer) >= 4:
            length = struct.unpack("!I", self.buffer[:4])[0]
            if not 1 <= length <= MAX_FRAME:
                raise ValueError("frame size; close connection")
            if len(self.buffer) < 4 + length:
                break
            raw = bytes(self.buffer[4:4 + length])
            del self.buffer[:4 + length]
            try:
                message = json.loads(raw.decode("utf-8"),
                                     object_pairs_hook=unique_object,
                                     parse_constant=invalid_constant)
            except (ValueError, RecursionError) as exc:
                raise ValueError("invalid JSON; close connection") from exc
            if type(message) is not dict:
                raise ValueError("object required; close connection")
            messages.append(message)
        return messages

    def eof(self):
        if self.buffer:
            raise ValueError("truncated frame")


class Bank:
    """Serialisierte Modellbank; alle Daten gehen bei Prozessende verloren."""
    def __init__(self, clock=time.monotonic, balance=100_000):
        if type(balance) is not int or not 0 <= balance <= 100_000_000:
            raise ValueError("balance outside model limits")
        self.clock = clock
        self.lock = threading.RLock()
        self.accounts = {"DEMO-CARD-A": {"pin": "1234", "balance": balance,
                                         "failures": 0}}
        self.sessions = {}
        self.transactions = {}

    def _expire(self):
        for tx in self.transactions.values():
            if tx["state"] == "RESERVED" and self.clock() >= tx["expires"]:
                tx["state"] = "CANCELLED"

    def _available(self, card):
        held = sum(tx["amount"] for tx in self.transactions.values()
                   if tx["card"] == card and tx["state"] in HELD)
        return self.accounts[card]["balance"] - held

    def _session(self, sid, terminal):
        identifier(sid)
        session = self.sessions.get(sid)
        if session is None:
            raise Fault("UNAUTHORIZED")
        require(session["terminal"] == terminal, "UNAUTHORIZED")
        require(self.clock() < session["expires"], "SESSION_EXPIRED")
        return session["card"]

    def _tx(self, txid, card, terminal):
        identifier(txid)
        tx = self.transactions.get(txid)
        if tx is None:
            raise Fault("NOT_FOUND")
        require((tx["card"], tx["terminal"]) == (card, terminal), "FORBIDDEN")
        return tx

    def _view(self, txid, tx):
        return {"tx": txid, "amount": tx["amount"], "currency": "EUR",
                "state": tx["state"]}

    def handle(self, request, terminal="DEMO-ATM-1"):
        """terminal ersetzt hier ausschließlich eine bereits geprüfte mTLS-Identität."""
        with self.lock:
            rid = None
            try:
                require(type(request) is dict)
                require(set(request) == {"v", "id", "op", "sid", "body"})
                rid = identifier(request["id"])
                require(type(request["v"]) is int and request["v"] == 1,
                        "BAD_VERSION")
                require(type(terminal) is str and 1 <= len(terminal) <= 64)
                op, body = request["op"], request["body"]
                require(type(op) is str and type(body) is dict)
                fields = {"AUTH": {"card", "pin"}, "BALANCE": set(),
                          "RESERVE": {"tx", "amount"}, "BEGIN": {"tx"},
                          "RESULT": {"tx", "outcome"}, "STATUS": {"tx"},
                          "CANCEL": {"tx"}, "LOGOUT": set()}
                require(op in fields, "UNKNOWN_OP")
                require(set(body) == fields[op])
                self._expire()
                if op == "AUTH":
                    require(request["sid"] is None)
                    result = self._auth(body, terminal)
                else:
                    card = self._session(request["sid"], terminal)
                    result = self._dispatch(op, body, card, terminal, request["sid"])
                return {"v": 1, "id": rid, "status": "OK", "body": result}
            except Fault as exc:
                return {"v": 1, "id": rid, "status": str(exc), "body": {}}

    def _auth(self, body, terminal):
        card, pin = body["card"], body["pin"]
        require(type(card) is str and 1 <= len(card) <= 64)
        require(type(pin) is str and len(pin) == 4 and pin.isascii() and pin.isdigit())
        account = self.accounts.get(card)
        if account is None:
            raise Fault("AUTH_FAILED")
        require(account["failures"] < 3, "AUTH_FAILED")
        if not hmac.compare_digest(pin, account["pin"]):
            account["failures"] += 1
            raise Fault("AUTH_FAILED")
        account["failures"] = 0
        sid = str(uuid.uuid4())
        self.sessions[sid] = {"card": card, "terminal": terminal,
                              "expires": self.clock() + SESSION_TTL}
        return {"sid": sid, "expires_in": SESSION_TTL}

    def _dispatch(self, op, body, card, terminal, sid):
        if op == "LOGOUT":
            del self.sessions[sid]
            return {}
        if op == "BALANCE":
            return {"booked": self.accounts[card]["balance"],
                    "available": self._available(card), "currency": "EUR"}
        txid = identifier(body["tx"])
        if op == "RESERVE":
            amount = body["amount"]
            require(type(amount) is int and 0 < amount <= MAX_AMOUNT
                    and amount % 1000 == 0, "BAD_AMOUNT")
            if txid in self.transactions:
                tx = self._tx(txid, card, terminal)
                require(tx["amount"] == amount, "TX_CONFLICT")
            else:
                state = "RESERVED" if amount <= self._available(card) else "DECLINED"
                tx = {"card": card, "terminal": terminal, "amount": amount,
                      "state": state, "expires": self.clock() + RESERVATION_TTL}
                self.transactions[txid] = tx
            return self._view(txid, tx)
        tx = self._tx(txid, card, terminal)
        state = tx["state"]
        if op == "BEGIN":
            require(state in {"RESERVED", "DISPENSING"}, "INVALID_STATE")
            tx["state"] = "DISPENSING"
        elif op == "CANCEL":
            require(state in {"RESERVED", "CANCELLED"}, "INVALID_STATE")
            tx["state"] = "CANCELLED"
        elif op == "RESULT":
            outcome = body["outcome"]
            require(type(outcome) is str and outcome in {"OK", "FAIL", "UNKNOWN"})
            target = {"OK": "COMMITTED", "FAIL": "CANCELLED", "UNKNOWN": "UNKNOWN"}[outcome]
            if state != target:
                require(state == "DISPENSING", "INVALID_STATE")
                if outcome == "OK":
                    self.accounts[card]["balance"] -= tx["amount"]
                tx["state"] = target
        return self._view(txid, tx)

    def reconcile(self, txid, cash_delivered):
        """Nur lokale, vertrauenswürdige Prüfinstanz; KEINE Client-Nachricht."""
        with self.lock:
            require(type(cash_delivered) is bool)
            require(txid in self.transactions, "NOT_FOUND")
            tx = self.transactions[txid]
            require(tx["state"] in {"DISPENSING", "UNKNOWN"}, "INVALID_STATE")
            if cash_delivered:
                self.accounts[tx["card"]]["balance"] -= tx["amount"]
            tx["state"] = "COMMITTED" if cash_delivered else "CANCELLED"


class Dispenser:
    """Simulierter Auszahler mit flüchtigem Journal; keine echte Hardware."""
    def __init__(self):
        self.journal = {}
        self.cash = 0
        self.lock = threading.Lock()

    def dispense(self, txid, amount, outcome="OK"):
        with self.lock:
            identifier(txid)
            require(type(amount) is int and 0 < amount <= MAX_AMOUNT
                    and amount % 1000 == 0, "BAD_AMOUNT")
            require(type(outcome) is str and outcome in {"OK", "FAIL", "UNKNOWN"})
            if txid in self.journal:
                previous_amount, previous_outcome = self.journal[txid]
                require(amount == previous_amount, "TX_CONFLICT")
                return previous_outcome
            self.journal[txid] = (amount, "UNKNOWN")
            if outcome == "OK":
                self.cash += amount
            self.journal[txid] = (amount, outcome)
            return outcome


def request(op, body=None, sid=None):
    return {"v": 1, "id": str(uuid.uuid4()), "op": op, "sid": sid,
            "body": {} if body is None else body}


def exchange(bank, message, terminal="DEMO-ATM-1"):
    """Beide Richtungen framen, aber KEINE Sockets und KEIN TLS vortäuschen."""
    incoming = Decoder().feed(encode(message))[0]
    response = bank.handle(incoming, terminal)
    return Decoder().feed(encode(response))[0]
