# Ü 9.1 – Erst beobachten, dann verändern

## Angabe

Umgebung unverändert starten; Hosts, Interfaces, IP-Adressen/Netze, Default Routes, Erreichbarkeit und Neighbor-Einträge erfassen.

## Herkunft und Grenze

Die Originalvorlage liegt unverändert in [Angabe](../Angabe/). Der Originalstart mit `/usr/bin/python3 -B start_lab.py` endet hier bei `ModuleNotFoundError: No module named 'mininet'`. Mininet, Open vSwitch und xterm sind daher **nicht verifiziert**. Gemessen wurde stattdessen ein eigenständiger echter Linux-Namespace-/veth-/Linux-Bridge-Nachbau mit denselben IPs, Interface-Namen, Routen und unveränderten TCP-Programmen. Keine simulierten Pakete. Die TCLink-Verzögerungen der Vorlage sind nicht nachgebildet; gemessene Laufzeiten gelten nur für den Ersatzaufbau.

## Bestandsaufnahme

- `client1`: `client1-eth0`, `10.10.1.10/24`, Default via `10.10.1.1`.
- `client2`: `client2-eth0`, `10.10.1.11/24`, Default via `10.10.1.1`.
- `router`: `router-eth0`, `10.10.1.1/24`; `router-eth1`, `10.10.2.1/24`; direkt verbundene Routen zu beiden /24-Netzen, keine Default Route nötig; IPv4-Forwarding eingeschaltet.
- `server`: `server-eth0`, `10.10.2.10/24`, Default via **`10.10.2.254`**.
- Jeder Host hat zusätzlich `lo` mit `127.0.0.1/8`.
- `sw1`: verbindet client1, client2 und router-eth0. `sw2`: verbindet router-eth1 und server. Im Ersatzaufbau sind dies IP-lose Linux-Bridges mit Ports `p1`, `p2`, `pr0` bzw. `pr1`, `p3`; in der Originalvorlage sind es OVS-Switches im Standalone-Modus.
- Netze: `10.10.1.0/24` (Client-LAN) und `10.10.2.0/24` (Server-LAN).

## Erreichbarkeit ohne Reparatur

- client1 → Gateway `10.10.1.1`: 3/3 Antworten.
- client2 → Gateway `10.10.1.1`: 3/3 Antworten.
- router → Server `10.10.2.10`: 3/3 Antworten; dieses Ziel liegt direkt am router-eth1.
- server → echter Router `10.10.2.1`: 3/3 Antworten.
- client1 → Server: 0/3 Antworten; Original-TCP-Client läuft in Timeout.
- client2 → Server: 0/3 Antworten; Original-TCP-Client läuft in Timeout.

Die initialen Neighbor-Caches sind im Nachbau leer. Nach den Tests:

- client1 kennt `10.10.1.1 → 02:00:00:00:01:01` (STALE).
- client2 kennt dasselbe Gateway (REACHABLE).
- server kennt `10.10.2.1 → 02:00:00:00:02:01` (REACHABLE), aber `10.10.2.254` ist **FAILED**, ohne aufgelöste MAC.
- router kennt beide Clients `…01:10`, `…01:11` und Server `…02:10`.

STALE bedeutet eine vorhandene, aktuell nicht frisch bestätigte Zuordnung, nicht automatisch einen Fehler. Die MACs sind ausdrücklich für den Nachbau festgelegt, nicht aus einem Mininet-Lauf übernommen. Die Originalstart-Routine führt bereits Pings aus; deshalb können deren Caches beim interaktiven Einstieg schon gefüllt sein.

## Belege und Aufruf

[results.json](../nachweise/run01/results.json): `initial`, `baseline`, `before`, `fault_state`; [Befehlsprotokoll](../nachweise/run01/befehle.txt).

```sh
python3 ue9.1/pruefen.py
```

Dieser Aufruf liest nur vorhandene Belege. Auf dem Server wurde zu diesem Zeitpunkt noch keine Reparatur vorgenommen.

## KI-Kennzeichnung

Erstellt mit Hermes Agent; OpenAI, Modell `gpt-6.1-sol`, Provider laut `hermes status`: ChatGPT or Codex Subscription; 2026-10-29. Anfrage: Ü9.1 anhand unveränderter Originalvorlage beobachten und echte, klar als Ersatzaufbau gekennzeichnete Zustands- und Erreichbarkeitsbelege erstellen. Keine eigene studentische Durchführung behauptet.
