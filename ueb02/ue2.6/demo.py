# KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol
# Datum: 2026-10-19
# Anfrage: Ü2.6: lauffähige lokale Demonstration des fiktiven Bankomatprotokolls
# inklusive erfolgreicher Abhebung, verlorener Antwort und fehlender Deckung.
"""Offline-Demo; keine Netzwerkverbindungen, nur erfundene Daten."""
import uuid

from protocol import Bank, Dispenser, exchange, request


def main():
    bank = Bank(balance=10_000)
    dispenser = Dispenser()
    sid = exchange(bank, request("AUTH", {"card": "DEMO-CARD-A", "pin": "1234"}))["body"]["sid"]

    def call(op, body=None):
        response = exchange(bank, request(op, body, sid))
        print(op, response["status"], response["body"])
        if response["status"] != "OK":
            raise RuntimeError(response["status"])
        return response["body"]

    print("FAP/1: In-Memory-Unterrichtssimulation, ohne TLS und ohne echte Bank.")
    print("AUTH OK (PIN und Sitzung werden nicht ausgegeben)")
    call("BALANCE")
    txid = str(uuid.uuid4())
    assert call("RESERVE", {"tx": txid, "amount": 4000})["state"] == "RESERVED"
    assert call("BEGIN", {"tx": txid})["state"] == "DISPENSING"
    outcome = dispenser.dispense(txid, 4000)
    message = request("RESULT", {"tx": txid, "outcome": outcome}, sid)
    exchange(bank, message)
    print("RESULT-Antwort absichtlich verworfen; dieselbe Nachricht erneut senden.")
    retried = exchange(bank, message)
    print("RESULT (Retry)", retried["status"], retried["body"])
    assert retried["body"]["state"] == "COMMITTED"
    final = call("BALANCE")
    assert final["booked"] == 6000 and dispenser.cash == 4000
    denied = call("RESERVE", {"tx": str(uuid.uuid4()), "amount": 7000})
    assert denied["state"] == "DECLINED"
    print("Zu wenig Deckung: keine Reservierung, keine Ausgabe, keine Abbuchung.")
    call("LOGOUT")
    print("Demo-Prüfungen erfolgreich; ausgegebene Cent:", dispenser.cash)


if __name__ == "__main__":
    main()
