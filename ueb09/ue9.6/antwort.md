# Ü 9.6 – Reparatur verifizieren

## Wiederholte Tests

Nach der serverseitigen Korrektur wurden dieselben Original-TCP-Programme und Pingtests verwendet; keine Anwendung wurde ersetzt.

- client1 → `10.10.2.10`: 3 gesendet, 3 empfangen, 0 % Verlust, Antwort-TTL 63; Original-TCP-Client Exit 0 und Ausgabe `RN-Lab forensic test server` mit abschließendem Zeilenumbruch.
- client2 → `10.10.2.10`: ebenfalls 3/3, 0 % Verlust, TTL 63; Original-TCP-Client Exit 0 und dieselbe Ausgabe.
- Beide Verbindungen erhalten je **28 Bytes** Original-Begrüßung vom Server. Vollständiger Inhalt wird zusätzlich aus den TCP-Sequenznummern der PCAPs rekonstruiert, nicht nur aus der Terminalausgabe abgelesen.

## Zweiter Mitschnitt und Vergleich

Unter [nachweise/run01](../nachweise/run01/) liegen fünf `nachher-*.pcap`, an denselben Interfaces wie vorher. Es gibt 18 erfolgreich geroutete TCP-Pakete, neun je Verbindung, in beiden Router-PCAPs inhaltlich zugeordnet. Ein Routerhop ändert MACs und TTL, nicht die IP-Endpunkte oder TCP-Nutzdaten. IPv4-, ICMP- und TCP-Prüfsummen werden vom unabhängigen Parser geprüft.

Frame-Nummern gelten für `nachher-server.pcap`:

- client1 `10.10.1.10:54918 → 10.10.2.10:5000`: Frame 7 SYN, Frame 8 SYN-ACK, Frame 9 ACK; Frame 10 überträgt die Begrüßung; Frames 12/13 FINs, anschließend bestätigter Abschluss. Kein RST.
- client2 `10.10.1.11:52262 → 10.10.2.10:5000`: Frame 22 SYN, Frame 23 SYN-ACK, Frame 24 ACK; Frame 25 überträgt die Begrüßung; Frames 27/28 FINs, anschließend bestätigter Abschluss. Kein RST.
- Das SYN-ACK bestätigt die Client-Sequenznummer plus eins; das dritte Handshake-ACK bestätigt die Server-Sequenznummer plus eins. Das initiale SYN bestätigt noch keine Gegen-Sequenznummer. FINs werden ebenfalls einzeln bestätigt. `auswertung.py` prüft dies anhand der tatsächlichen Headerwerte.
- Antworten gehen auf dem Server-LAN an MAC `02:00:00:00:02:01`, nicht an `.254`. Im Client-LAN gehen sie vom Router-MAC `…01:01` an den jeweiligen Client-MAC `…01:10` oder `…01:11`.
- Vorher: SYN-Wiederholungen, kein SYN-ACK auf dem Link, ARP-Suche nach `.254`. Nachher: vollständiger Handshake, Begrüßung, beidseitiger FIN-Abschluss, erfolgreiche Echo-Replies. Kein ICMP Time Exceeded erforderlich; es liegt kein Loop vor.

[Maschinelle Auswertung](../nachweise/run01/auswertung.json), [unabhängiges tcpdump-Decoding](../nachweise/run01/nachher-server-tcpdump.txt), [Original-Testausgaben](../nachweise/run01/results.json).

## Wichtige Abgrenzung zur Szenariobeschreibung

Das Szenario spricht von einer kleinen Nachricht vom Client zum Server. Die tatsächlich bereitgestellten Programme tun etwas anderes: `tcp_client.py` verbindet und empfängt nur; `tcp_server.py` sendet die Begrüßung. Deshalb wird hier **kein Client-Nutzdatenversand behauptet**. Nachgewiesen ist die Originalanwendung mit TCP-Handshake und Servernachricht für beide Clients. Soll darüber hinaus ein anwendungsseitiger Client-Payload gefordert sein, müsste eine getrennte Anwendungserweiterung vereinbart werden; für die Netzwerkreparatur ist sie nicht erforderlich.

## Wiederholen

```sh
python3 ue9.6/pruefen.py
python3 -B auswertung.py
python3 -B -m unittest -v test_nachweise
```

Für **neue echte Ersatzmessungen** mit installiertem `ip`, `nsenter`, `dumpcap`, `ethtool`, `ping`, `sysctl` und Python ≥3.12, nur bei erlaubten Rootrechten:

```sh
sudo -n /usr/bin/python3 -B messen.py --out nachweise/run02
python3 -B auswertung.py --out nachweise/run02
```

Der Ausgabeordner muss neu sein; `run01` wird absichtlich nicht überschrieben. Ein frischer äußerer Netzwerk-Namespace isoliert jede Netzänderung vom echten Rechner. Alle eigenen Prozesse werden im `finally` beendet und eingesammelt. Mininet/OVS/xterm sind damit trotzdem **nicht** verifiziert; VM-Wiederholung bleibt offen. Die PCAPs lassen sich ohne GUI mit tcpdump prüfen; Wireshark ist laut Aufgabe eine Alternative, nicht vorgeschrieben.

## KI-Kennzeichnung

Hermes Agent; OpenAI `gpt-6.1-sol`; ChatGPT or Codex Subscription laut `hermes status`; 2026-10-29. Anfrage: Ü9.6 mit beiden Originalclients und einem zweiten echten Mitschnitt prüfen, Handshake/Daten/FINs und Vorher-Nachher-Unterschiede maschinell verifizieren; Grenzen klar ausweisen.
