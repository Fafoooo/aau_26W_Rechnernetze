# Ü4.5 – Routing in der RN-Lab-Topologie

## Quellen, Grenzen und Originaldateien

Grundlage: `../angabe_blatt04.pdf`, Abschnitt „Die RN-Lab-Topologie“ und Ü4.5; sämtliche sechs Python-Dateien in `../Angabe/`, insbesondere `topology.py` und `start_lab.py`. Alle nachstehenden Laborkonfigurationen sind aus diesen Originalquellen abgeleitete **Sollwerte**, keine hier gemessenen Mininet-Ausgaben.

Mininet fehlt; der bereitgestellte Umgebungstest wurde ausgeführt. Nichts wurde nachinstalliert, die Originaldateien bleiben unverändert. Die drei Mininet-Laborkonsolen wurden **nicht geöffnet**. Zusätzlich wurde die Konfiguration in drei echten, isolierten Linux-Netzwerk-Namespaces nachgebildet: gleiche IPs, Routen und 20-ms-Linkverzögerungen; **kein Mininet-Nachweis**. Unter `../nachweise/run01/` liegen reale Interface-/Routenausgaben, ein erfolgreicher Ping mit vier Antworten und eine erfolglose Negativprobe bei deaktiviertem Forwarding. Die Netzkonfiguration des aufrufenden Hosts blieb unverändert; private Hostdiagnosen werden nicht veröffentlicht.

Das Original-ZIP `../Angabe/uebb4_template.zip` wurde mit der Python-Standardbibliothek gelistet: Es enthält sechs Python-Dateien, jedoch **keine README.md**, obwohl der PDF-Anhang sie nennt.

## Infrastruktur im Originalcode identifizieren

Die Zeilenangaben beziehen sich auf die unveränderten Dateien in `../Angabe/`:

| Datei/Stelle | Bedeutung |
|---|---|
| `topology.py` Z.13–14 | `LINK_DELAY = "20ms"`, `LINK_LOSS = 0`. Die Verzögerung/Verlustoptionen werden an die TCLinks weitergegeben, nicht im Anwendungscode simuliert. |
| Z.16–21 | Client-IP/Gateway, beide Router-IPs und Server-IP/Gateway als Konstanten. Eine Konstante alleine konfiguriert noch kein Interface. |
| Z.24–33 | `LinuxRouter(Host)` aktiviert in `config()` IPv4-Forwarding; `terminate()` deaktiviert es vor dem Beenden dieses Knotens wieder. |
| Z.40–42 | Drei Hosts `client`, `router` mit Klasse `LinuxRouter`, `server`; hier gibt es keinen zusätzlichen L2-Switch. |
| Z.44–51 | Link `client-eth0` ↔ `router-eth0`, `TCLink`, Delay und Loss aus den Konstanten. |
| Z.53–60 | Link `router-eth1` ↔ `server-eth0`, ebenfalls `TCLink`, gleiche vorgegebene Eigenschaften. |
| `start_lab.py` Z.23–52, `configure_network(net)` | Führt die eigentliche deterministische Netzkonfiguration aus. |
| Z.29–32 | Löscht die bisherigen IP-Adressen der vier beteiligten Interfaces innerhalb der Laborknoten. |
| Z.34–37 | Setzt die vier IPv4-Adressen aus den Konstanten. |
| Z.39–45 | Aktiviert die Interfaces. |
| Z.47–48 | Setzt Client- und Server-Default-Routen über ihre jeweiligen Router-Nachbarn. |
| Z.50–51 | Setzt/ersetzt die beiden direkt angeschlossenen Netzrouten im Router. |
| Z.52 | Aktiviert IPv4-Forwarding auf dem Router nochmals explizit. |
| Z.55–82 | Gibt erwartete Konfiguration und tatsächlich abgefragte Interface-/Routenausgaben getrennt aus. |
| Z.86–111 | Vorgesehene Pingprüfungen in beiden Richtungen. Der konkrete Prüfausdruck hat einen Fallstrick, siehe unten. |
| Z.116–129 | Baut Mininet ohne Controller auf, startet es, ruft Konfiguration, Status und Verbindungstest auf. |
| Z.132–144,147–148 | Öffnet drei Terminals, wartet im Startterminal auf Enter, stoppt anschließend das Lab im `finally`-Block. Auch hier keine Mininet-CLI. |

**Wichtig beim Prüfskript:** `start_lab.py` Z.104 prüft mit `"0% packet loss" in result`. Diese Zeichenfolge ist auch in `"100% packet loss"` enthalten. Ein gedrucktes `OK` ist daher für sich allein kein verlässlicher Erfolgsbeleg. Die wirklichen Pingstatistiken und Rückgabewerte separat kontrollieren; das Originalskript wird deshalb nicht geändert.

## Solltopologie und Routingtabellen

```text
client-eth0                    router-eth0      router-eth1                    server-eth0
10.0.1.2/24  ----------------  10.0.1.1/24      10.0.2.1/24  ----------------  10.0.2.2/24
                 Netz 10.0.1.0/24                     Netz 10.0.2.0/24
```

Die folgenden Zeilen sind eine **schematische Sollwertdarstellung**, keine kopierte Live-Ausgabe. Zusätze wie Protokoll, Metrik oder Cachehinweise können versionsabhängig abweichen.

```text
client:
  10.0.1.0/24 dev client-eth0 scope link src 10.0.1.2
  default via 10.0.1.1 dev client-eth0

router:
  10.0.1.0/24 dev router-eth0 scope link src 10.0.1.1
  10.0.2.0/24 dev router-eth1 scope link src 10.0.2.1

server:
  10.0.2.0/24 dev server-eth0 scope link src 10.0.2.2
  default via 10.0.2.1 dev server-eth0
```

Der Router braucht **keine Default Route**, um diese beiden direkt angeschlossenen Netze zu verbinden. Die Adresszuweisung erzeugt normalerweise bereits passende verbundene Routen; `configure_network()` setzt sie zusätzlich ausdrücklich. Eine Router-Quelladresse in einer Route ist die bevorzugte Quelle für **lokal erzeugte** Pakete. Sie ersetzt nicht die Client-Quelladresse eines weitergeleiteten Pakets.

## Genaue Hinroute von 10.0.1.2 nach 10.0.2.2

1. **Routenwahl auf client:** `10.0.2.2` liegt nicht im direkt angeschlossenen `10.0.1.0/24`. Ohne spezifischere Fernnetzroute wählt Linux nach längstem passenden Präfix die Default Route über **10.0.1.1**, Ausgang **client-eth0**. Die IP-Quelle ist hier **10.0.1.2**, IP-Ziel bleibt **10.0.2.2**.
2. **ARP auf dem linken Link:** Client ermittelt bei noch fehlendem Nachbareintrag die MAC von **10.0.1.1**, also dem nächsten Hop, **nicht** die MAC von 10.0.2.2. Der Ethernetframe trägt Client-MAC → Router-linke-MAC. Das eingeschlossene IPv4-Paket trägt 10.0.1.2 → 10.0.2.2.
3. **Weiterleitung im Router:** Der Frame kommt über **router-eth0** an. Die Ziel-IP ist keine lokale Routeradresse. Bei aktiviertem IPv4-Forwarding und erlaubendem Filter-/Firewallzustand wird das Paket über die direkt angeschlossene Route **10.0.2.0/24 dev router-eth1** weitergeleitet. Auf diesem Schritt gibt es keinen weiteren IP-Gateway: der Server ist am rechten Routerinterface direkt erreichbar. Der Router reduziert die TTL und aktualisiert die IPv4-Headerprüfsumme; er führt laut Originalskript kein NAT aus.
4. **ARP auf dem rechten Link:** Der Router ermittelt gegebenenfalls die MAC von **10.0.2.2**. Neuer Ethernetframe: Router-rechte-MAC → Server-MAC. Die IP-Adressen bleiben **10.0.1.2 → 10.0.2.2**. Routerinterface-Adressen ersetzen keine Endpunkt-IP.
5. **Zustellung am Server:** **server-eth0** empfängt den Frame; 10.0.2.2 ist eine lokale IP. Der ICMP-Echo-Request wird lokal verarbeitet, sofern keine zusätzliche Filterregel ihn verwirft.

ARP ist auf den jeweiligen Link/Broadcastbereich begrenzt. Fehlen Nachbareinträge, entstehen ARP-Anfragen; bestehen sie bereits, werden die vorhandenen Einträge genutzt. Ein „leerer“ `ip neigh`-Befund vor einem Ping wäre daher nicht automatisch ein Konfigurationsfehler.

## Rückweg für den Echo-Reply

1. Server erzeugt eine Antwort mit **Quelle 10.0.2.2, Ziel 10.0.1.2**.
2. 10.0.1.2 ist außerhalb von 10.0.2.0/24; der Server nutzt **default via 10.0.2.1 dev server-eth0** und adressiert auf Ethernet die rechte Router-MAC.
3. Router empfängt auf **router-eth1**, findet **10.0.1.0/24 dev router-eth0** und leitet auf das linke Netz weiter; falls nötig ARP für **10.0.1.2**.
4. Der neue linke Ethernetframe erreicht client-eth0. Die IP-Endpunkte der Antwort bleiben Server → Client. Ein erfolgreicher Ping benötigt also **Hin- und Rückroute** sowie Weiterleitung in beiden Richtungen.

## Antworten auf die vier Fragen

### Warum benötigt der Router zwei IP-Adressen?

In dieser Topologie verbindet er zwei verschiedene IPv4-Subnetze über zwei Interfaces. **10.0.1.1/24** ist sein unmittelbar erreichbarer Gatewayendpunkt im Clientnetz, **10.0.2.1/24** im Servernetz. Ein Client kann daher seinen nächsten Hop im eigenen angeschlossenen Netz per ARP erreichen. Das ist die gewählte nummerierte Routerkonfiguration; es ist keine allgemeine Behauptung, jeder Router habe unter jeder Spezialkonfiguration exakt zwei IPs.

### Warum benötigt client eine Default Route?

Mit der hier vorgegebenen Tabelle kennt der Client sonst nur sein direktes Netz 10.0.1.0/24. Die **Default Route** ist der konfigurierte Weg zu unbekannten Zielnetzen, also auch zu 10.0.2.2. Ohne sie **und ohne andere passende Route** scheitert diese Weiterleitung.

Eine Default Route ist dafür **nicht mathematisch zwingend**: Eine spezifische Route `10.0.2.0/24 via 10.0.1.1 dev client-eth0` oder eine passende Hostroute würde für dieses Ziel ebenfalls genügen. Eine solche Route wäre wegen ihres längeren Präfixes sogar vor der Default Route auszuwählen. Es wird hier keine alternative Route installiert und keine Originalkonfiguration geändert. Auf der Serverseite gilt die entsprechende Rückroutenanforderung.

### Warum kann client 10.0.2.2 nicht direkt über sein eigenes Ethernet-Netz erreichen?

Client befindet sich mit `/24` in **10.0.1.0/24**, der Server in **10.0.2.0/24**. Die zwei TCLinks sind getrennte L2-Verbindungen; der Router ist keine transparente Bridge. Der Server ist daher kein direkter Ethernetnachbar des Clients, und eine linklokale ARP-Anfrage des Clients erreicht ihn nicht. Ein zu großzügiges falsches Präfix würde keine physische/L2-Verbindung herbeizaubern, sondern könnte zu erfolglosen direkten ARP-Versuchen führen. Der korrekte Weg ist über den lokalen Gateway und IP-Routing.

### Welche Aufgabe übernimmt IP-Forwarding?

Es erlaubt dem Linux-Router, ein auf einem Interface empfangenes, nicht an ihn selbst adressiertes IPv4-Paket anhand seiner Routingtabelle über ein anderes Interface weiterzuleiten. **client→server** benötigt Eingang router-eth0 und Ausgang router-eth1; **server→client** die umgekehrte Richtung. Beide Interfaces müssen aktiv sein und Forwarding zulassen; Filterregeln dürfen den Transit nicht sperren.

Das Original setzt `net.ipv4.ip_forward=1` (auch in `LinuxRouter.config()`); der globale IPv4-Forwarding-Schalter wirkt in diesem Router-Netzwerk-Namespace. Zur Diagnose werden der globale Wert sowie die per-Interface-Werte von **router-eth0 und router-eth1** gelesen, statt nur die Erreichbarkeit einer lokalen Router-IP zu testen. `net.ipv4.conf.default.forwarding` ist ein Vorgabewert für neu entstehende Interfaces und allein kein Beleg für den aktuellen Zustand beider vorhandenen Interfaces. Lokale Router-Pings können auch ohne erfolgreichen Transit funktionieren. Routen und ARP allein ersetzen aktiviertes Forwarding nicht; Forwarding erzeugt seinerseits keine fehlende Rückroute.

## Echte Laborprüfung – noch in der bereitgestellten VM auszuführen

```console
cd /pfad/zur/Angabe
sudo python3 start_lab.py
```

Das Skript braucht eine passende grafische Sitzung für die drei Terminals. Im ursprünglichen Startterminal noch nicht Enter drücken: Das würde das Lab stoppen. In den geöffneten Konsolen ohne Mininetpräfix:

```console
# client:
ip addr
ip route
hostname
ip -4 route get 10.0.2.2
ping -c 4 10.0.2.2
ip neigh show

# router:
ip addr
ip route
hostname
ip -4 route get 10.0.2.2
ip -4 route get 10.0.1.2
ip -4 route get 10.0.2.2 from 10.0.1.2 iif router-eth0
sysctl net.ipv4.ip_forward
sysctl net.ipv4.conf.router-eth0.forwarding net.ipv4.conf.router-eth1.forwarding
ip neigh show
tc -s qdisc show

# server:
ip addr
ip route
hostname
ip -4 route get 10.0.1.2
ping -c 4 10.0.1.2
ip neigh show
```

`route get` ohne `from`/`iif` untersucht einen lokalen Ausgangsweg; die ergänzte Routerabfrage macht den Bezug zum weiterzuleitenden Clientpaket explizit. Weder diese Abfrage noch der Wert `ip_forward=1` ersetzt den realen Ende-zu-Ende-Test. Erwartet sind bei funktionsfähigem unverändertem Lab erfolgreiche Antworten, aber **hier liegt dafür kein Mininet-Messergebnis vor**. Tatsächliche Paketverluste, RTTs, MACs und Namespace-IDs dürfen erst aus den realen Ausgaben übernommen werden. `hostname` ist UTS und bei normalem Mininet gewöhnlich auf allen drei Knoten gleich; es bestätigt nicht die Knotenzuordnung.

## Lokales Diagnoseprogramm und Verifikation

```console
./diagnose.py --self-test
./diagnose.py --output weiterer-hostlauf.json
```

`diagnose.py` ist ausführbar, nutzt nur stdlib und liest Interfaces, Routen einschließlich beider Zielabfragen, Nachbarn, Forwardingwerte und qdiscs. Es versendet bewusst **keine Pings**, verändert keine ARP-/Routen-/Interfacekonfiguration und führt kein `sudo` aus. Jede tatsächliche Argumentliste, stdout, stderr und der Exitcode werden im JSON dokumentiert; Namespace-IDs, Zeitpunkt und Verfügbarkeit der Werkzeuge ebenfalls. Die IPs in `route get` sind **Abfrageziele**, keine als vorhanden behaupteten Interfaceadressen.

Auf einem normalen Host fehlen `router-eth0` und `router-eth1` typischerweise. Der entsprechende Sysctl-Fehler ist ein erwartbar dokumentierter Befund dieses **Hosts**, kein gemessener RN-Lab-Fehler. Auch wenn seine Route zu 10.0.2.2 über einen ganz anderen Gateway führt, ist das keine Laborkonfiguration. Bei mindestens einem fehlgeschlagenen Diagnosebefehl ist der Skriptexitcode 1; fehlgeschlagene Einzelbefehle verhindern nicht den restlichen Bericht. Ausgabepfad-/Argumentfehler ergeben 2. Neue Berichte werden ausschließlich direkt im Aufgabenordner gespeichert und niemals überschrieben.

Für echte Laborbelege das Skript innerhalb jeder gestarteten Knoten-Konsole aufrufen, z.B. auf dem Router `python3 /pfad/zum/repo/ueb04/ue4.5/diagnose.py --context router --output router-diagnose.json`; je Knoten eigenen Dateinamen verwenden. Diagnoseausgaben vor einer Veröffentlichung auf lokale Systeminformationen prüfen. `--context` ist nur ein Label, kein Namespacewechsel. Die Routerinterface-Abfragen sind nur im Routerkontext sinnvoll; Client-/Serverberichte können dafür erwartete Fehler enthalten.

**Tatsächlich getestet:** Acht unittest-Testmethoden bestehen (`self-test.txt`). Geprüft sind Subprocess-Argumente und Sicherheitsoptionen, Fehlerfälle, Timeout, JSON und Ausgabepfadschutz. Mocks sind nur Testdaten. Reale Namespace-Belege: `../nachweise/run01/client-network.txt`, `router-network.txt`, `server-network.txt`, `ping.txt` und `ping-forwarding-off.txt`. Codezeilen erklärt `erklaerung.md`. Die unveränderten Mininet-Laborskripte müssen weiterhin in der bereitgestellten VM geprüft werden.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-29**. Tatsächliche Anfrage sinngemäß: vollständige, sachlich korrekte Lösungen für Ü4.1, Ü4.2 und Ü4.5 mit ausführbaren read-only Hostdiagnosen, echten Selbsttests und zeilenweisen Erklärungen erstellen; Originalquellen/Policy lesen, keine Mininetinstallation oder Originaländerung, keine Hostwerte als Mininetdaten ausgeben.
