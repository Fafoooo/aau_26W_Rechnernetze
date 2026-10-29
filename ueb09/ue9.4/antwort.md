# Ü 9.4 – Hypothese mit Evidenz prüfen

## Hypothese

Die Default Route des Servers zeigt auf `10.10.2.254`, obwohl der vorhandene Router im Server-LAN `10.10.2.1` hat. Die Hinpakete erreichen den Server. Serverantworten an `10.10.1.0/24` scheitern, weil der Server die MAC-Adresse des falschen Next Hops nicht auflösen kann.

## Unabhängige Beobachtung 1: aktiver Routingzustand

Am Server zeigt `ip route`:

```text
default via 10.10.2.254 dev server-eth0
10.10.2.0/24 dev server-eth0 proto kernel scope link src 10.10.2.10
```

`ip route get 10.10.1.10` wählt tatsächlich `via 10.10.2.254 dev server-eth0`. Der Router besitzt dagegen `10.10.2.1/24` auf `router-eth1`. Das ist nicht nur ein Kommentar im Starter, sondern der aktive Kernelzustand: [results.json](../nachweise/run01/results.json), `fault_state`.

## Unabhängige Beobachtung 2: Pakete auf dem Serverlink

[vorher-server.pcap](../nachweise/run01/vorher-server.pcap) zeigt SYNs **beider** Clients an `10.10.2.10:5000` und 12 ARP Requests `who-has 10.10.2.254 tell 10.10.2.10`, ohne ARP Reply für `.254`. Kein TCP-Rückpaket verlässt den Server auf diesem Link. Damit ist die Ursache auf dem Rückweg lokalisierbar; ein fehlgeschlagener Connect allein wäre kein solcher Nachweis.

## Zusätzliche Gegenproben

- Server-Neighbor-Eintrag `10.10.2.254 dev server-eth0 FAILED` stützt die fehlende Auflösung.
- `10.10.2.1` wird mit MAC `02:00:00:00:02:01` aufgelöst; Server → echter Router funktioniert 3/3.
- Beide Clients erreichen ihr Gateway 3/3; Router → Server funktioniert 3/3. Deshalb erklären ein vollständig ausgefallener Switch, ausgeschaltetes Forwarding und ein nicht erreichbarer Server-LAN-Port die Gesamtevidenz nicht.
- Der Originalserver war vor den TCP-Tests gestartet und meldete den Listener auf Port 5000. Nach **nur** dem Gatewaywechsel liefern dieselben Programme beiden Clients ihre Begrüßung. Das ist die kausale Gegenprobe, kein Anlass für eine Anwendungscodeänderung.

Die Diagnose wurde vor der Reparatur gespeichert: [diagnose-vor-reparatur.txt](../nachweise/run01/diagnose-vor-reparatur.txt). `messen.py` ruft vorher bereits `check_fault()` für die vollständigen Vorher-PCAPs auf.

**Ergebnis: falsches Default Gateway am Server; keine Störung im Client-Hinweg.**

```sh
python3 ue9.4/pruefen.py
```

Alle Messbelege sind aus echten Linux-Network-Namespaces mit veth und Linux-Bridges; Mininet/OVS/xterm bleiben ungeprüft.

## KI-Kennzeichnung

Hermes Agent; OpenAI `gpt-6.1-sol`; ChatGPT or Codex Subscription laut `hermes status`; 2026-10-29. Anfrage: Ü9.4 mit mindestens zwei unabhängigen Zustands-/Paketbeobachtungen diagnostizieren, Gegenhypothesen abgrenzen und Diagnose vor Reparatur festhalten.
