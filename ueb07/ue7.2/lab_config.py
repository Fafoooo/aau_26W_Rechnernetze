# KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).
# Datum: 2026-10-29
# Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;
# lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.
"""Mininet-unabhängiger Adressplan; alle bestehenden Interfaces bleiben erhalten."""

NODES = ("client", "r1", "r2", "server", "r3")
ROUTERS = ("r1", "r2", "r3")
# Link: Knoten links/rechts, Interface links/rechts, IPv4 links/rechts, Verzögerung pro Richtung.
LINKS = (
    ("client", "r1", "client-eth0", "r1-eth0", "10.0.1.2/24", "10.0.1.1/24", "1ms"),
    ("r1", "r2", "r1-eth1", "r2-eth0", "10.0.12.1/30", "10.0.12.2/30", "5ms"),
    ("r2", "server", "r2-eth1", "server-eth0", "10.0.2.1/24", "10.0.2.2/24", "1ms"),
    ("r1", "r3", "r1-eth2", "r3-eth0", "10.0.13.1/30", "10.0.13.2/30", "30ms"),
    ("r3", "r2", "r3-eth1", "r2-eth2", "10.0.23.1/30", "10.0.23.2/30", "30ms"),
)
# Route: Router, Zielpräfix, Next Hop, Ausgangsinterface; nie gleichzeitige A/B-Routen.
PATH_ROUTES = {
    "A": (("r1", "10.0.2.0/24", "10.0.12.2", "r1-eth1"),
          ("r2", "10.0.1.0/24", "10.0.12.1", "r2-eth0")),
    "B": (("r1", "10.0.2.0/24", "10.0.13.2", "r1-eth2"),
          ("r2", "10.0.1.0/24", "10.0.23.1", "r2-eth2")),
}
R3_ROUTES = (("r3", "10.0.2.0/24", "10.0.23.2", "r3-eth1"),
             ("r3", "10.0.1.0/24", "10.0.13.1", "r3-eth0"))
DEFAULT_ROUTES = (("client", "10.0.1.1", "client-eth0"),
                  ("server", "10.0.2.1", "server-eth0"))
PATH_NODES = {"A": ("client", "r1", "r2", "server"),
              "B": ("client", "r1", "r3", "r2", "server")}
