# Ü 9.5 – Ursache beheben

## Fehlerhafte Konfiguration

Am Server steht `default via 10.10.2.254 dev server-eth0`. Im bereitgestellten `start_lab.py` setzen Zeilen 49–51 absichtlich genau diese Route. Die Datei bleibt zur forensischen Wiederholung unverändert; im Nachbau wurde der aktive Zustand erst untersucht und dann repariert.

## Kleinste sinnvolle Änderung

**Nur im Netzwerk-Namespace/Terminal des Servers:**

```sh
ip route replace default via 10.10.2.1 dev server-eth0
```

Im von der Vorlage geöffneten Server-xterm läuft die Shell bereits im richtigen Namespace. Nicht blind im Terminal des echten Rechners ausführen. Falls eine eigene Mininet-CLI geöffnet wurde, wäre das Präfix `server` möglich; die Originalvorlage öffnet aber **keine** solche CLI, sondern xterms und anschließend einen einfachen ENTER-Warteprompt. Dieser nimmt keine Mininet-Hostbefehle entgegen.

Es wird genau eine Default Route ersetzt. Keine IP, Netzmaske, Clientroute, Switchkonfiguration, Firewall, Forwarding-Einstellung oder Python-Anwendung wird zur Reparatur verändert. Ein Löschen des ARP-Caches war ebenfalls nicht nötig.

## Warum das hilft

1. Die Antwort an `10.10.1.10` oder `10.10.1.11` gehört nicht ins lokale Servernetz `10.10.2.0/24`.
2. Die neue Default Route wählt den existierenden Next Hop `10.10.2.1`.
3. Für diesen kann der Server die MAC `02:00:00:00:02:01` verwenden.
4. Der Router besitzt eine direkt angeschlossene Route zu `10.10.1.0/24` und leitet die Antwort weiter.
5. Die ursprüngliche TCP-Verbindung kann dadurch SYN-ACK, Daten und Abschluss in beiden Richtungen austauschen.

Der alte Neighbor-Eintrag `.254 FAILED` bleibt in `repaired_state` noch sichtbar. Er schadet nicht, weil die aktive Route ihn nicht mehr auswählt. Er muss nicht für ein „sauberes“ Ergebnis gelöscht werden.

## Alternativen

- Eine spezifische Serverroute `ip route replace 10.10.1.0/24 via 10.10.2.1 dev server-eth0` würde beide Clients dank längstem Präfixmatch erreichen, ließe aber die falsche Default Route für andere Netze bestehen.
- Hostrouten zu `.10/32` und `.11/32` wären unnötig eng und aufwendiger.
- Dem Router zusätzlich `10.10.2.254/24` geben könnte den bisherigen Next Hop erreichbar machen, verändert aber den Router und verdeckt den Konfigurationsfehler; schlechter als die Ein-Zeilen-Korrektur am Server.
- Für einen dauerhaft reparierten VM-Start könnte man später eine ausdrücklich separate korrigierte Kopie des Starters erstellen. Die Originalvorlage selbst wird hier nicht überschrieben, damit der Vorherzustand wiederholbar bleibt.

Belege: [Diagnose vor Änderung](../nachweise/run01/diagnose-vor-reparatur.txt), [Befehle](../nachweise/run01/befehle.txt), [Zustand](../nachweise/run01/results.json). Im Ersatzaufbau ist zwischen den Vorher-/Nachher-Phasen genau der oben genannte `route replace` zur Reparatur ausgeführt worden.

```sh
python3 ue9.5/pruefen.py
```

Die CLI zeigt lesend beide Zustände und führt keine Reparatur am Rechner aus. Mininet-/OVS-/xterm-Ausführung selbst bleibt unbestätigt.

## KI-Kennzeichnung

Hermes Agent; OpenAI `gpt-6.1-sol`; ChatGPT or Codex Subscription laut `hermes status`; 2026-10-29. Anfrage: Ü9.5 durch genau eine begründete serverseitige Gatewaykorrektur lösen, Originalvorlage erhalten und Alternativen erläutern.
