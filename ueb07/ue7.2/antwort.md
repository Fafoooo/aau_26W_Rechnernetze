# Ü 7.2 – Topologie um r3 erweitern

## Aufbau und Interpretation der Skizze

```text
                 10.0.13.0/30     10.0.23.0/30
              +------ r3 ------+
              |                 |
client ------ r1 -------------- r2 ------ server
10.0.1.0/24      10.0.12.0/30       10.0.2.0/24
```

- A: `client → r1 → r2 → server`.
- B: `client → r1 → r3 → r2 → server`.

Die Angabe fordert zusätzliche Router-zu-Router-Verbindungen, lässt deren Netzadressen offen und zeigt eine vereinfachte Skizze mit r3 in Richtung Server. Hier wird B durch **r1–r3 und r3–r2** realisiert. Damit bleibt das vorhandene Server-LAN mit genau einem Routeranschluss unverändert; r2 ist gemeinsamer letzter Router. Dies ist eine explizite Interpretation der schematischen Zeichnung, nicht die Behauptung eines direkten Kabels von r3 zum Server. Ein direkter zweiter Routeranschluss am selben Server-LAN würde einen gemeinsamen Switch beziehungsweise eine andere, ausdrücklich dokumentierte Netzstruktur erfordern.

Die Originaldateien in `Angabe/` sind unverändert archiviert. Die erweiterte Arbeitskopie ist [topology.py](topology.py); [start_lab.py](start_lab.py) konfiguriert sämtliche Adressen und Routen. Die Angabe nennt den Client `client1`, die Vorlage tatsächlich `client`.

## Vollständiger Adressplan

- Client-LAN `10.0.1.0/24`: `client-eth0 = 10.0.1.2/24`, `r1-eth0 = 10.0.1.1/24`.
- Ursprünglicher Transfer `10.0.12.0/30`: `r1-eth1 = 10.0.12.1/30`, `r2-eth0 = 10.0.12.2/30`.
- Server-LAN `10.0.2.0/24`: `r2-eth1 = 10.0.2.1/24`, `server-eth0 = 10.0.2.2/24`.
- **Neu** `10.0.13.0/30`: `r1-eth2 = 10.0.13.1/30`, `r3-eth0 = 10.0.13.2/30`.
- **Neu** `10.0.23.0/30`: `r3-eth1 = 10.0.23.1/30`, `r2-eth2 = 10.0.23.2/30`.

Die beiden neuen /30-Netze sind getrennt; `.0` ist jeweils Netzadresse, `.3` Broadcast. Es gibt keine doppelt auf getrennten gerouteten Ports konfigurierte LAN-Präfixe. Alle bisherigen Adressen und Interface-Namen bleiben erhalten. IPv4-Forwarding ist auf allen drei Routern aktiviert. Default-Gateway des Clients ist `10.0.1.1`, des Servers `10.0.2.1`; kein Router bekommt eine Default-Route.

## Routingtabellen von r1 und r3

Relevante `main`-Einträge; tatsächlich gespeicherte Kernel-Ausgaben enthalten zusätzliche Attribute wie `proto`, `scope` und `src`:

```text
r1, Variante A:
  10.0.1.0/24  dev r1-eth0
  10.0.12.0/30 dev r1-eth1
  10.0.13.0/30 dev r1-eth2
  10.0.2.0/24 via 10.0.12.2 dev r1-eth1

r1, Variante B:
  10.0.1.0/24  dev r1-eth0
  10.0.12.0/30 dev r1-eth1
  10.0.13.0/30 dev r1-eth2
  10.0.2.0/24 via 10.0.13.2 dev r1-eth2

r3, beide Varianten:
  10.0.13.0/30 dev r3-eth0
  10.0.23.0/30 dev r3-eth1
  10.0.1.0/24 via 10.0.13.1 dev r3-eth0
  10.0.2.0/24 via 10.0.23.2 dev r3-eth1
```

Für symmetrischen Rückverkehr bekommt r2 in A `10.0.1.0/24 via 10.0.12.1 dev r2-eth0`, in B stattdessen `via 10.0.23.1 dev r2-eth2`. Sein Servernetz bleibt direkt verbunden. Alle Route-Operationen verwenden `replace`, keine gleichzeitigen ECMP-Wege. Der direkte Link bleibt bei B physisch bestehen, wird aber für diesen Ende-zu-Ende-Verkehr nicht gewählt.

**Umschaltung:** Zwei Router teilen keine atomare Kernel-Transaktion. Der Helper serialisiert seine Aktionen und rollt bei einem Fehler die schon geänderte Route zurück. Während der kurzen Umstellung wird nicht gemessen; erst nach vollständig installiertem Hin- und Rückweg. Ein fehlgeschlagenes Rollback kennzeichnet den Pfadstatus als unbekannt.

## Ausführen in der vorbereiteten Mininet-VM

```sh
cd ueb07/ue7.2
python3 -B test_lab.py
sudo python3 -B start_lab.py --path A
```

Danach in der **Mininet-CLI**:

```text
state
check
client tracepath -n 10.0.2.2
server tracepath -n 10.0.1.2
path B
state
check
client tracepath -n 10.0.2.2
server tracepath -n 10.0.1.2
fault on
client ping -n -c 2 10.0.2.2
fault off
check
exit
```

`check` prüft beide Richtungen über den echten Prozess-Exitstatus, nicht über einen irreführenden Textteilstring. `fault on` ist für 7.4 vorgesehen und wirkt auf B; bei A ist r3 kein Transitrouter. Der Starter öffnet die CLI direkt; bei Bedarf können in einer grafischen Labor-VM über deren normale `xterm`-Funktion separate Knotenterminals geöffnet werden. Ein reiner Check ohne CLI: `sudo python3 -B start_lab.py --path B --check-only`. `finally` stoppt das Netz auch bei Fehlern während des expliziten `build()`.

## Tatsächliche Prüfung und Grenzen

**Mininet ist hier nicht installiert.** Der Starter liefert dafür verständlich Exitcode 2; Hilfe funktioniert ohne Mininet. Kein Paket wurde nachinstalliert. Die **23 unprivilegierten Tests** prüfen mit synthetischen API-Doubles unter anderem Interface-/Linkparameter, Routen, Pfadwechsel, Fehler/Reparatur, Rollback, Build-Cleanup und exakte Zeilenerklärungen. Sie sind kein Netzlauf. [Protokoll](synthetic_tests.txt).

Separat wurden **echte Linux-Netzwerk-Namespaces mit veth und TC/Netem** aufgebaut und derselbe `LabControl` tatsächlich gegen Linux-Befehle ausgeführt:

- [A-r1](../nachweise/run01/A-r1-state.txt) und [A-r3](../nachweise/run01/A-r3-state.txt) dokumentieren die Routingtabellen von A.
- [B-r1](../nachweise/run01/B-r1-state.txt), [B-r2](../nachweise/run01/B-r2-state.txt) und [B-r3](../nachweise/run01/B-r3-state.txt) dokumentieren B.
- Ping A und B: **je zehn Antworten auf zehn Anfragen, in beiden Richtungen**. [Zusammenfassung](../nachweise/run01/results.json).
- [Tracepath A](../nachweise/run01/A-client-tracepath.txt): Ziel mit drei Hops erreicht.
- [Tracepath B](../nachweise/run01/B-client-tracepath.txt): Ziel mit vier Hops erreicht, Hop 3 antwortete nicht. Die Lücke wird nicht erfunden ergänzt; Routing-Lookups und TTL 61 stützen den zusätzlichen Router. [Gegenrichtung](../nachweise/run01/B-server-tracepath.txt).

Die vollständige Auswertung mit Delays steht in [7.3](../ue7.3/antwort.md); alle eigenen Codezeilen werden in [erklaerung_topologie.md](../erklaerung_topologie.md) erklärt. Ein echter Mininet-/xterm-Abnahmelauf in der vorgesehenen VM bleibt offen.

## KI-Kennzeichnung

Hermes Agent, OpenAI `gpt-6.1-sol`; Zugang laut `hermes status`: ChatGPT or Codex Subscription; Datum: 2026-10-29. Anfrage: „Löse Blatt07 vollständig, erweitere die bereitgestellte Topologie um r3 mit statischen A/B-Hin- und Rückwegen, teste Code und tatsächliche Pakete, dokumentiere Adressen, Routingtabellen, Ergebnisse und jede Codezeile.“ Keine menschliche Eigenleistung wird behauptet.
