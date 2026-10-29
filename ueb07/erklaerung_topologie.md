# Erklärung der erweiterten Topologie (Ü 7.2–7.4)

## Entwurf und Abgrenzung

1. Die unveränderte Vorlage liegt in `Angabe/`; die eigenständige Erweiterung liegt in `ue7.2/`. Der Knoten heißt im Python-Original **client**, im Aufgabenblatt **client1**. Gemeint ist derselbe Endhost.
2. Pfad A bleibt `client — r1 — r2 — server`. Pfad B lautet `client — r1 — r3 — r2 — server`. Die Skizze kann auch als direkte Verbindung r3–Server gelesen werden. Hier wird bewusst **r3–r2 als Router-zu-Router-Verbindung** verwendet: Das entspricht dem Text zu Router-zu-Router-Kommunikation, erhält das Server-LAN und vermeidet zwei geroutete Ports im gleichen Subnetz. Es gibt keinen zusätzlichen Server-Port und keine L2-Brücke.
3. Die vorhandenen Anschlüsse bleiben: `client-eth0 10.0.1.2/24 ↔ r1-eth0 10.0.1.1/24`; `r1-eth1 10.0.12.1/30 ↔ r2-eth0 10.0.12.2/30`; `r2-eth1 10.0.2.1/24 ↔ server-eth0 10.0.2.2/24`.
4. Neu sind `r1-eth2 10.0.13.1/30 ↔ r3-eth0 10.0.13.2/30` sowie `r3-eth1 10.0.23.1/30 ↔ r2-eth2 10.0.23.2/30`. Jedes dieser Netze liegt auf genau einem Router-Router-Link; kein Router besitzt zwei Ports im gleichen Netz.
5. In A verwendet r1 für `10.0.2.0/24` den Next Hop `10.0.12.2 dev r1-eth1`, r2 für `10.0.1.0/24` den Next Hop `10.0.12.1 dev r2-eth0`. In B sind es `10.0.13.2 dev r1-eth2` beziehungsweise `10.0.23.1 dev r2-eth2`.
6. r3 hat immer die statischen Routen `10.0.2.0/24 via 10.0.23.2 dev r3-eth1` und `10.0.1.0/24 via 10.0.13.1 dev r3-eth0` (außer beim absichtlichen Fehler). r1 kennt sein Client-LAN, r2 sein Server-LAN direkt; die Kernel-Connected-Routen entstehen beim Setzen der Adressen. Router erhalten **keine Default-Route**. Die Endhosts behalten `default via 10.0.1.1 dev client-eth0` beziehungsweise `default via 10.0.2.1 dev server-eth0`.
7. Alle Links bleiben physisch aktiv, aber pro Zielpräfix existiert genau eine ausgewählte statische Route: `ip route replace`, keine A/B-Routen mit mehreren Metriken, keine `nexthop`-Liste und kein ECMP. Die Wahl gilt für Hin- und Rückweg. `path` wird durch einen Lock gegen andere Helper-Aktionen serialisiert. Zwei unabhängige Router besitzen **keine gemeinsame atomare Kernel-Transaktion**: Zwischen den beiden Änderungen kann kurz ein asymmetrischer Pfad entstehen. Schlägt die zweite Änderung fehl, wird die erste zurückgerollt; schlägt auch das fehl, ist der gemeldete Pfadstatus unbekannt. Keine Pakete während eines Wechsels als Beweis eines stabilen Pfads verwenden. Vor Messungen `path` vollständig beenden lassen. Manuelle Änderungen außerhalb des Helpers werden nicht als Transaktionszustand nachgeführt; dann Labor neu starten.
8. `TCLink` setzt pro Richtung auf client–r1 und r2–server je 1 ms, auf r1–r2 5 ms, auf r1–r3 und r3–r2 je 30 ms. Das Modell ergibt als reine Hin-und-zurück-Verzögerung A: 14 ms, B: 124 ms. Das sind **berechnete Budgets, keine gemessenen RTTs**. Scheduler, Warteschlangen, qdisc-/Timerauflösung, Verarbeitung und ARP beim ersten Paket können die Messwerte beeinflussen; eine RTT enthält beide Richtungen.

## Schritt für Schritt in der vorbereiteten Mininet-VM

1. In dieses Unterverzeichnis wechseln: `cd ueb07/ue7.2`. Ohne Privilegien zuerst `python3 test_lab.py` ausführen. Dafür genügt die Python-Standardbibliothek; es werden keine Interfaces, Routen, Namespaces oder sysctls des Rechners verändert.
2. Hilfe: `python3 start_lab.py --help`. Für echte Netze **nur in der vorgesehenen Labor-VM** `sudo python3 start_lab.py --path A` starten. Dies erzeugt alle fünf Knoten, setzt Adressen und Forwarding, installiert die Routen, zeigt den Zustand und prüft beide E2E-Richtungen. Ohne Root oder ohne Mininet endet der Starter mit Status 2. Es wird nichts installiert.
3. Nach erfolgreicher Prüfung öffnet sich eine echte Mininet-CLI, kein bloßes `input()`-Fenster. `state` zeigt alle Adressen und Routen; normale Befehle wie `r1 ip route`, `r3 ip route` und `client ip route get 10.0.2.2` funktionieren ebenfalls.
4. In A: `check`, danach beispielsweise `client ping -n -c 5 10.0.2.2` und `client tracepath -n 10.0.2.2` oder `client traceroute -n 10.0.2.2`. `tracepath`/`traceroute` müssen bereits in der VM vorhanden sein. Fehlende Diagnoseprogramme werden nicht automatisch installiert. Die numerischen Hop-Adressen können je nach ICMP-Quelladresswahl variieren; der Routerpfad soll r1–r2 sein.
5. In derselben CLI `path B`, `state`, `check` ausführen. Ping und Trace wiederholen; der Routerpfad soll jetzt r1–r3–r2 sein. Beide Varianten erhalten symmetrische Hin-/Rückrouten. Der integrierte Check wertet **echte Ping-Exitcodes** aus und bricht beim ersten Fehler ab. Die optionale Kombination `sudo python3 start_lab.py --path B --check-only` prüft B, räumt auf und gibt bei einem Ping-Fehler Status 1 statt eines Erfolgs zurück. Für vollständige Verluststatistik die Ping-Ausgabe zusätzlich ansehen.
6. In B mit `fault on` ausschließlich r3s Serverroute löschen. `check` muss nun scheitern. Erst `client ping -c 1 10.0.1.1` zur lokalen Gateway-Erreichbarkeit, dann `r1 ping -c 1 10.0.13.2`, `r3 ip -br addr`, `r3 ip route` und `r3 ip route get 10.0.2.2` prüfen. Interfaces und verbundene Netze sind vorhanden; die fehlende Route betrifft das entfernte Server-/24. `client traceroute -n 10.0.2.2` grenzt den Abbruch auf r3 ein. Ein ICMP-Unreachable von r3 ist möglich, ein Timeout allein beweist die Ursache noch nicht.
7. Falls nötig in einem separaten, auf dieses Labor beschränkten Capture auf `r3-eth0` und `r3-eth1` nach ICMP/Serververkehr sehen: Eingang auf r3, aber keine Weiterleitung über den erwarteten Ausgang, zusammen mit der fehlenden Route und ggf. ICMP Destination Unreachable. Wireshark unterstützt die Diagnose, ersetzt aber die Routingtabellenprüfung nicht. Keine Capture-Dateien oder GUI-Beweise wurden durch diese Implementierung erzeugt.
8. `fault off`, `state`, `check` stellen die Serverroute wieder her und prüfen die Kommunikation. Wiederholtes `fault on` oder `fault off` ist idempotent. `path A` während des Fehlers repariert r3 nicht; A umgeht r3 lediglich. Zum tatsächlichen Reparieren `fault off` verwenden.
9. `exit` beendet die CLI; `finally` ruft `net.stop()` auf, auch wenn der explizite Aufbau mit `net.build()` oder der spätere Start fehlschlägt. Dafür unterbindet `build=False` den automatischen Aufbau im Mininet-Konstruktor: Die Variable `net` ist bereits zugewiesen, bevor Ressourcen aufgebaut werden. Grafische Fenster werden nicht automatisch geöffnet; bei Bedarf ist der normale Mininet-Befehl `xterm client r1 r2 r3 server` möglich, wenn X11/xterm vorhanden sind.

## Prüfung hier und Aussagegrenzen

Die lokale Umgebung enthält kein Mininet. `python3 start_lab.py --path B --check-only` wurde tatsächlich ausgeführt und lieferte die verständliche Fehlermeldung `No module named 'mininet'` mit **Exitcode 2**; `--help` funktioniert mit Exitcode 0. Es wurde nichts installiert. Die unprivilegierten Tests laufen wirklich, aber ihre Netzknoten sind **synthetische Fake-Objekte**: Sie prüfen Modell, exakte Mininet-API-Aufrufe, Exitcode-Handling, Routenersatz/Rollback, Fehlersteuerung, CLI und Aufräumen. Sie beweisen weder echte Paketweiterleitung noch Mininet-, TC-, RTT-, Trace- oder Wireshark-Ausführung. Eventuelle Linux-Namespace-Nachweise in anderen Dateien sind separat und nicht als Mininet-Nachweis zu lesen. Aktueller Testlauf: [synthetic_tests.txt](ue7.2/synthetic_tests.txt).

## Leseschlüssel zur zeilenweisen Erklärung

Jede nichtleere Quellzeile steht unten genau einmal mit originaler Zeilennummer und Originaltext (HTML-escaped für `<`, `>` und `&`). Einrückung gehört zum Originaltext. Einträge sind nummerierte Listen, keine Tabellen. Zusammenhängende Datenzeilen werden durch die Feldreihenfolge im jeweiligen Abschnitt erklärt; Abschlussklammern beenden die im vorangehenden Eintrag beschriebene Struktur. Der Dokumentationstest vergleicht Reihenfolge, Nummer und HTML-dekodierten Quelltext mit allen fünf aktuellen Python-Dateien; veraltete Zeilen oder fehlende Einträge führen zum Fehler.

## Datei: `lab_config.py`

Datenvertrag: LINKS enthält links/rechts, Interface links/rechts, IPv4 links/rechts und Delay. PATH_ROUTES und R3_ROUTES enthalten Router, Zielpräfix, Gateway und Ausgang. DEFAULT_ROUTES enthält Endhost, Gateway und Ausgang. Alle Daten sind reine Standardbibliothek-kompatible Tupel/Dicts; Import verändert kein Netz.

1. Zeile **1**: <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).</code> — Kennzeichnet den KI-Einsatz einschließlich Tool, Provider und genauem Modell.
2. Zeile **2**: <code># Datum: 2026-10-29</code> — Dokumentiert das vorgegebene Erstellungsdatum der KI-Unterstützung.
3. Zeile **3**: <code># Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;</code> — Dokumentiert den tatsächlichen Arbeitsauftrag für diesen übernommenen Code.
4. Zeile **4**: <code># lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.</code> — Setzt den Auftrag mit Laufbarkeit, Tests und ausdrücklicher Kennzeichnung synthetischer Ergebnisse fort.
5. Zeile **5**: <code>"""Mininet-unabhängiger Adressplan; alle bestehenden Interfaces bleiben erhalten."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
6. Zeile **7**: <code>NODES = ("client", "r1", "r2", "server", "r3")</code> — Legt die fünf tatsächlichen Mininet-Namen fest; client entspricht client1 im Aufgabenblatt.
7. Zeile **8**: <code>ROUTERS = ("r1", "r2", "r3")</code> — Wählt genau die drei Knoten aus, die IP-Pakete zwischen ihren Interfaces weiterleiten dürfen.
8. Zeile **9**: <code># Link: Knoten links/rechts, Interface links/rechts, IPv4 links/rechts, Verzögerung pro Richtung.</code> — Erläuternder Kommentar zur direkt folgenden Datenstruktur; hat keine Laufzeitwirkung.
9. Zeile **10**: <code>LINKS = (</code> — Beginnt die fünf Linkdatensätze; jeder enthält beide Endpunkte, feste Interfacenamen, zwei Adressen und den pro Richtung geltenden TC-Delay.
10. Zeile **11**: <code>    ("client", "r1", "client-eth0", "r1-eth0", "10.0.1.2/24", "10.0.1.1/24", "1ms"),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
11. Zeile **12**: <code>    ("r1", "r2", "r1-eth1", "r2-eth0", "10.0.12.1/30", "10.0.12.2/30", "5ms"),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
12. Zeile **13**: <code>    ("r2", "server", "r2-eth1", "server-eth0", "10.0.2.1/24", "10.0.2.2/24", "1ms"),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
13. Zeile **14**: <code>    ("r1", "r3", "r1-eth2", "r3-eth0", "10.0.13.1/30", "10.0.13.2/30", "30ms"),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
14. Zeile **15**: <code>    ("r3", "r2", "r3-eth1", "r2-eth2", "10.0.23.1/30", "10.0.23.2/30", "30ms"),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
15. Zeile **16**: <code>)</code> — Schließt die zuvor begonnene Argumentliste, Tupel-, Dict- oder Listenstruktur ab.
16. Zeile **17**: <code># Route: Router, Zielpräfix, Next Hop, Ausgangsinterface; nie gleichzeitige A/B-Routen.</code> — Erläuternder Kommentar zur direkt folgenden Datenstruktur; hat keine Laufzeitwirkung.
17. Zeile **18**: <code>PATH_ROUTES = {</code> — Beginnt die beiden alternativen Paare statischer Fernnetz-Routen für r1 und r2; jeweils nur ein Paar wird installiert.
18. Zeile **19**: <code>    "A": (("r1", "10.0.2.0/24", "10.0.12.2", "r1-eth1"),</code> — Ordnet dieser Pfadvariante ihre exakt festgelegten Routerrouten bzw. Knotensequenz zu; Hin- und Rückweg gehören zusammen.
19. Zeile **20**: <code>          ("r2", "10.0.1.0/24", "10.0.12.1", "r2-eth0")),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
20. Zeile **21**: <code>    "B": (("r1", "10.0.2.0/24", "10.0.13.2", "r1-eth2"),</code> — Ordnet dieser Pfadvariante ihre exakt festgelegten Routerrouten bzw. Knotensequenz zu; Hin- und Rückweg gehören zusammen.
21. Zeile **22**: <code>          ("r2", "10.0.1.0/24", "10.0.23.1", "r2-eth2")),</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
22. Zeile **23**: <code>}</code> — Schließt die zuvor begonnene Argumentliste, Tupel-, Dict- oder Listenstruktur ab.
23. Zeile **24**: <code>R3_ROUTES = (("r3", "10.0.2.0/24", "10.0.23.2", "r3-eth1"),</code> — Legt r3s Server-/24-Route über r2 fest; genau dieser Eintrag wird beim absichtlichen Fehler gelöscht.
24. Zeile **25**: <code>             ("r3", "10.0.1.0/24", "10.0.13.1", "r3-eth0"))</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
25. Zeile **26**: <code>DEFAULT_ROUTES = (("client", "10.0.1.1", "client-eth0"),</code> — Legt die unveränderte Client-Default-Route über r1 fest; der nächste Datensatz enthält die Server-Default-Route über r2.
26. Zeile **27**: <code>                  ("server", "10.0.2.1", "server-eth0"))</code> — Weiterer Datensatz im darüber eingeführten Schema; die konkreten Endpunkte/Präfixe und Werte bleiben unverändert als Tupel gespeichert.
27. Zeile **28**: <code>PATH_NODES = {"A": ("client", "r1", "r2", "server"),</code> — Legt die Soll-Knotensequenz A für den synthetischen Routen-/Delay-Abgleich fest; dies installiert selbst keine Route.
28. Zeile **29**: <code>              "B": ("client", "r1", "r3", "r2", "server")}</code> — Ordnet dieser Pfadvariante ihre exakt festgelegten Routerrouten bzw. Knotensequenz zu; Hin- und Rückweg gehören zusammen.

## Datei: `lab_control.py`

checked übersetzt einen von null verschiedenen pexec-Exitcode in eine Exception mit stdout/stderr. route_args liefert argumentgetrennte iproute2-Aufrufe ohne Shell-Interpolation. configure setzt die gesamte Ausgangskonfiguration. select_path ersetzt genau zwei Routen mit Rollback bereits erfolgreicher Änderungen. set_fault ändert ausschließlich die r3-Serverroute. ping prüft beide Richtungen; show liest den Zustand. Der RLock erlaubt nur eine Helper-Transaktion zur Zeit.

1. Zeile **1**: <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).</code> — Kennzeichnet den KI-Einsatz einschließlich Tool, Provider und genauem Modell.
2. Zeile **2**: <code># Datum: 2026-10-29</code> — Dokumentiert das vorgegebene Erstellungsdatum der KI-Unterstützung.
3. Zeile **3**: <code># Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;</code> — Dokumentiert den tatsächlichen Arbeitsauftrag für diesen übernommenen Code.
4. Zeile **4**: <code># lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.</code> — Setzt den Auftrag mit Laufbarkeit, Tests und ausdrücklicher Kennzeichnung synthetischer Ergebnisse fort.
5. Zeile **5**: <code>"""Geprüfte Befehle und serialisierte Pfadtransaktionen; kein Mininet-Import nötig."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
6. Zeile **7**: <code>import threading</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
7. Zeile **8**: <code>from lab_config import DEFAULT_ROUTES, LINKS, NODES, PATH_ROUTES, R3_ROUTES, ROUTERS</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
8. Zeile **11**: <code>def checked(node, *args):</code> — Führt genau einen Knotenbefehl aus und akzeptiert ausschließlich Exitstatus null.
9. Zeile **12**: <code>    """Mininet.pexec liefert stdout, stderr, echten Exitstatus (kein Textvergleich)."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
10. Zeile **13**: <code>    try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
11. Zeile **14**: <code>        out, err, status = node.pexec(*args)</code> — Entpackt stdout, stderr und echten Prozess-Exitstatus aus Mininet.pexec.
12. Zeile **15**: <code>    except OSError as error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
13. Zeile **16**: <code>        raise RuntimeError(f"{node.name}: {args!r}: Prozessstart fehlgeschlagen: {error}") from error</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
14. Zeile **17**: <code>    if status != 0:</code> — Akzeptiert ausschließlich Exitcode 0; auch ein Fehlertext mit dem Teilstring 0% packet loss kann so keinen Erfolg vortäuschen.
15. Zeile **18**: <code>        raise RuntimeError(f"{node.name}: {args!r}: exit={status}\n{out}{err}")</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
16. Zeile **19**: <code>    return out</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
17. Zeile **22**: <code>def route_args(route, operation="replace"):</code> — Baut die vollständige IPv4-Routenoperation aus den vier Route-Feldern.
18. Zeile **23**: <code>    _, prefix, gateway, interface = route</code> — Entpackt die Route: der Routername wird hier ignoriert; Zielpräfix, Next Hop und Ausgang werden für ip route benötigt.
19. Zeile **24**: <code>    return ("ip", "route", operation, prefix, "via", gateway, "dev", interface)</code> — Gibt einzelne argv-Argumente für replace oder del zurück; via bestimmt den benachbarten Gateway, dev das feste Ausgangsinterface.
20. Zeile **27**: <code>class LabControl:</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
21. Zeile **28**: <code>    def __init__(self, net):</code> — Initialisiert die in dieser Klasse gespeicherten Zustandsfelder.
22. Zeile **29**: <code>        self.net = net</code> — Speichert die Abbildung der Knotennamen auf die zu steuernden Node-Objekte.
23. Zeile **30**: <code>        self.path = None</code> — Merkt den zuletzt vollständig ausgewählten Pfad; None bedeutet nicht initialisiert oder nach Rollbackfehler unbekannt.
24. Zeile **31**: <code>        self.fault = False</code> — Merkt, ob der Helper die r3-Serverroute absichtlich entfernt hat.
25. Zeile **32**: <code>        self.lock = threading.RLock()</code> — Erzeugt einen reentranten Thread-Lock für serialisierte Kontrollaktionen.
26. Zeile **34**: <code>    def configure(self, path="A"):</code> — Validiert zuerst den Pfad und richtet danach Interfaces, Forwarding, Gateways und statische Routen ein.
27. Zeile **35**: <code>        if path not in PATH_ROUTES:</code> — Verwirft alle Werte außer den definierten Pfadschlüsseln A/B vor jeder Routen- oder Interfaceänderung.
28. Zeile **36**: <code>            raise ValueError("Pfad muss A oder B sein")</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
29. Zeile **37**: <code>        for left, right, il, ir, al, ar, _ in LINKS:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
30. Zeile **38**: <code>            for name, interface, address in ((left, il, al), (right, ir, ar)):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
31. Zeile **39**: <code>                node = self.net[name]</code> — Löst den Knotennamen zu dem Mininet-Node auf, in dessen Netzwerknamespace die nächsten Befehle laufen.
32. Zeile **40**: <code>                checked(node, "ip", "addr", "flush", "dev", interface)</code> — Entfernt vorhandene Adressen nur von diesem Lab-Interface, damit keine Mininet-Vorgabe mit dem expliziten Adressplan konkurriert.
33. Zeile **41**: <code>                checked(node, "ip", "addr", "add", address, "dev", interface)</code> — Setzt genau die IPv4-Adresse samt Präfix aus dem Modell; der Kernel erzeugt dadurch die direkt verbundene Netzroute.
34. Zeile **42**: <code>                checked(node, "ip", "link", "set", interface, "up")</code> — Aktiviert den Linkzustand dieses Lab-Interfaces nach der Adressvergabe.
35. Zeile **43**: <code>        for name in ROUTERS:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
36. Zeile **44**: <code>            checked(self.net[name], "sysctl", "-w", "net.ipv4.ip_forward=1")</code> — Aktiviert IPv4-Weiterleitung in genau diesem Router-Node; auf Endhosts wird dieser Befehl nicht ausgeführt.
37. Zeile **45**: <code>        for name, gateway, interface in DEFAULT_ROUTES:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
38. Zeile **46**: <code>            checked(self.net[name], "ip", "route", "replace", "default",</code> — Ersetzt die Endhost-Default-Route; die nächste Zeile ergänzt den unveränderten Gateway und das passende Hostinterface.
39. Zeile **47**: <code>                    "via", gateway, "dev", interface)</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
40. Zeile **48**: <code>        for route in R3_ROUTES:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
41. Zeile **49**: <code>            checked(self.net[route[0]], *route_args(route))</code> — Führt den sichtbaren, argumentgetrennten Knotenbefehl mit strikter Exitcode-Prüfung aus.
42. Zeile **50**: <code>        self.fault = False</code> — Merkt, ob der Helper die r3-Serverroute absichtlich entfernt hat.
43. Zeile **51**: <code>        self.select_path(path)</code> — Installiert zuletzt das ausgewählte Paar von r1-/r2-Routen über die transaktionale Kontrollmethode.
44. Zeile **53**: <code>    def select_path(self, path):</code> — Wechselt Hin- und Rückweg gemeinsam als serialisierte Helper-Transaktion mit bestmöglichem Rollback.
45. Zeile **54**: <code>        """Zwei Router haben keine gemeinsame Kernel-Transaktion: bei Fehler zurückrollen."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
46. Zeile **55**: <code>        if path not in PATH_ROUTES:</code> — Verwirft alle Werte außer den definierten Pfadschlüsseln A/B vor jeder Routen- oder Interfaceänderung.
47. Zeile **56**: <code>            raise ValueError("Pfad muss A oder B sein")</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
48. Zeile **57**: <code>        with self.lock:</code> — Hält den reentranten Lock bis zum Ende des Blocks, auch bei Exceptions; andere Helper-Aktionen warten.
49. Zeile **58**: <code>            previous = self.path</code> — Merkt den vorherigen, vom Helper bekannten Pfad als Rollback-Ziel.
50. Zeile **59**: <code>            changed = []</code> — Beginnt eine Liste ausschließlich erfolgreich ersetzter Routerrouten.
51. Zeile **60**: <code>            try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
52. Zeile **61**: <code>                for index, route in enumerate(PATH_ROUTES[path]):</code> — Bearbeitet zuerst die r1-Serverroute und dann die r2-Clientroute; der Index verknüpft jede Änderung mit ihrer alten Gegenroute.
53. Zeile **62**: <code>                    checked(self.net[route[0]], *route_args(route))</code> — Führt den sichtbaren, argumentgetrennten Knotenbefehl mit strikter Exitcode-Prüfung aus.
54. Zeile **63**: <code>                    changed.append(index)</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
55. Zeile **64**: <code>            except RuntimeError as error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
56. Zeile **65**: <code>                failures = []</code> — Sammelt Fehler, die beim Rückgängigmachen bereits erfolgter Routenänderungen auftreten.
57. Zeile **66**: <code>                for index in reversed(changed):</code> — Nimmt nur bereits erfolgreiche Teilschritte in umgekehrter Reihenfolge zurück; der fehlgeschlagene Befehl wurde nicht als Änderung vorgemerkt.
58. Zeile **67**: <code>                    route = PATH_ROUTES[previous][index] if previous else PATH_ROUTES[path][index]</code> — Wählt bei bekanntem alten Pfad dessen entsprechende Route für die Wiederherstellung, sonst die gerade installierte Route zum Entfernen.
59. Zeile **68**: <code>                    operation = "replace" if previous else "del"</code> — Wählt für das Rollback replace eines alten Pfads oder del bei erstmaliger Teilkonfiguration.
60. Zeile **69**: <code>                    try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
61. Zeile **70**: <code>                        checked(self.net[route[0]], *route_args(route, operation))</code> — Führt den sichtbaren, argumentgetrennten Knotenbefehl mit strikter Exitcode-Prüfung aus.
62. Zeile **71**: <code>                    except RuntimeError as rollback_error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
63. Zeile **72**: <code>                        failures.append(str(rollback_error))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
64. Zeile **73**: <code>                if failures:</code> — Erkennt einen gescheiterten Rollback; dann darf kein vollständig wiederhergestellter Pfad behauptet werden.
65. Zeile **74**: <code>                    self.path = None</code> — Merkt den zuletzt vollständig ausgewählten Pfad; None bedeutet nicht initialisiert oder nach Rollbackfehler unbekannt.
66. Zeile **75**: <code>                    raise RuntimeError(f"Pfadstatus unbekannt; Rollback fehlgeschlagen: {failures}") from error</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
67. Zeile **76**: <code>                raise</code> — Reicht den ursprünglichen Fehler nach dem Rollback erneut an den Aufrufer weiter.
68. Zeile **77**: <code>            self.path = path</code> — Merkt den zuletzt vollständig ausgewählten Pfad; None bedeutet nicht initialisiert oder nach Rollbackfehler unbekannt.
69. Zeile **79**: <code>    def set_fault(self, enabled):</code> — Löscht oder repariert nur die Serverroute von r3; Flag wird erst nach Erfolg aktualisiert.
70. Zeile **80**: <code>        """Nur r3s Serverroute löschen/wiederherstellen, nicht dessen Client-Rückroute."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
71. Zeile **81**: <code>        with self.lock:</code> — Hält den reentranten Lock bis zum Ende des Blocks, auch bei Exceptions; andere Helper-Aktionen warten.
72. Zeile **82**: <code>            if enabled == self.fault:</code> — Überspringt wiederholtes Ein-/Ausschalten des gleichen Fehlers, sodass del nicht bei bereits fehlender Route erneut ausgeführt wird.
73. Zeile **83**: <code>                return</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
74. Zeile **84**: <code>            route = R3_ROUTES[0]</code> — Wählt ausschließlich r3s erste Route, also das Server-/24, nicht die weiterhin benötigte Client-Rückroute.
75. Zeile **85**: <code>            checked(self.net["r3"], *route_args(route, "del" if enabled else "replace"))</code> — Entfernt die Serverroute bei fault on oder setzt den festgelegten Next Hop bei fault off zurück; Fehler verhindern die folgende Flagänderung.
76. Zeile **86**: <code>            self.fault = enabled</code> — Merkt, ob der Helper die r3-Serverroute absichtlich entfernt hat.
77. Zeile **88**: <code>    def ping(self, count=3):</code> — Prüft eine positive Anzahl begrenzter ICMP-Versuche in beiden E2E-Richtungen anhand der Exitcodes.
78. Zeile **89**: <code>        if not isinstance(count, int) or count &lt; 1:</code> — Verlangt eine positive Python-Ganzzahl; null, negative Zahlen oder Strings werden nicht als Ping-Anzahl akzeptiert.
79. Zeile **90**: <code>            raise ValueError("Ping-Anzahl muss eine positive Ganzzahl sein")</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
80. Zeile **91**: <code>        with self.lock:</code> — Hält den reentranten Lock bis zum Ende des Blocks, auch bei Exceptions; andere Helper-Aktionen warten.
81. Zeile **92**: <code>            for source, target in (("client", "10.0.2.2"), ("server", "10.0.1.2")):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
82. Zeile **93**: <code>                out = checked(self.net[source], "ping", "-n", "-c", str(count),</code> — Startet ping im Quellknoten: -n vermeidet DNS-Namen, -c begrenzt die Anzahl; checked verlangt den echten Erfolgsstatus.
83. Zeile **94**: <code>                              "-W", "2", "-w", str(count * 3 + 2), target)</code> — Begrenzt die Antwortwartezeit mit -W auf 2 Sekunden und die Gesamtdauer mit -w auf 3*count+2 Sekunden; anschließend folgt die Ziel-IP.
84. Zeile **95**: <code>                print(f"[{source} -&gt; {target}]\n{out}", end="")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
85. Zeile **97**: <code>    def show(self):</code> — Liest Adressen und Haupt-Routingtabellen aller Laborknoten und zeigt den gewählten Zustand.
86. Zeile **98**: <code>        print(f"Pfad={self.path}, r3-Serverroute fehlt={self.fault}")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
87. Zeile **99**: <code>        for name in NODES:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
88. Zeile **100**: <code>            print(f"\n--- {name}: Adressen / Routen ---")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
89. Zeile **101**: <code>            print(checked(self.net[name], "ip", "-br", "addr"), end="")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
90. Zeile **102**: <code>            print(checked(self.net[name], "ip", "route", "show"), end="")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.

## Datei: `start_lab.py`

make_cli erzeugt eine Unterklasse der echten Mininet-CLI. do_path/do_fault/do_check/do_state sind Mininet-Befehle und action zeigt deren Fehler, ohne die interaktive Sitzung abzubrechen. main parst die Argumente vor den optionalen Imports, verlangt Root erst für den echten Start, konfiguriert und prüft vor der CLI und räumt im finally auf. main liefert 0 für Erfolg, 1 für Laufzeit-/Pingfehler und 2 für fehlendes Mininet/Root.

1. Zeile **1**: <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).</code> — Kennzeichnet den KI-Einsatz einschließlich Tool, Provider und genauem Modell.
2. Zeile **2**: <code># Datum: 2026-10-29</code> — Dokumentiert das vorgegebene Erstellungsdatum der KI-Unterstützung.
3. Zeile **3**: <code># Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;</code> — Dokumentiert den tatsächlichen Arbeitsauftrag für diesen übernommenen Code.
4. Zeile **4**: <code># lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.</code> — Setzt den Auftrag mit Laufbarkeit, Tests und ausdrücklicher Kennzeichnung synthetischer Ergebnisse fort.
5. Zeile **5**: <code>"""Start: sudo python3 start_lab.py --path A; Hilfe ohne Mininet/Root verfügbar."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
6. Zeile **7**: <code>import argparse</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
7. Zeile **8**: <code>import os</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
8. Zeile **9**: <code>import sys</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
9. Zeile **10**: <code>from lab_control import LabControl</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
10. Zeile **13**: <code>def make_cli(base):</code> — Erzeugt die spezialisierte CLI-Klasse erst, wenn eine echte oder synthetische CLI-Basisklasse vorliegt.
11. Zeile **14**: <code>    class LabCLI(base):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
12. Zeile **15**: <code>        def do_path(self, line):</code> — Normalisiert A/B-Eingabe und ruft den Pfadwechsel über den gemeinsamen Fehlerbehandler auf.
13. Zeile **16**: <code>            """path A|B: gemeinsamen Hin-/Rückpfad auswählen (Rollback bei Fehler)."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
14. Zeile **17**: <code>            self.action(lambda: self.mn.lab.select_path(line.strip().upper()))</code> — Bindet path an den Controller des aktuellen Mininet-Netzes; A/B wird normalisiert und der Fehlerhandler fängt ungültige Eingaben ab.
15. Zeile **19**: <code>        def do_fault(self, line):</code> — Akzeptiert nur on/off, übersetzt den Wert zu einem booleschen Fehlerzustand und steuert r3.
16. Zeile **20**: <code>            """fault on|off: r3-Serverroute entfernen bzw. wiederherstellen."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
17. Zeile **21**: <code>            value = line.strip().lower()</code> — Entfernt Rand-Leerzeichen und normalisiert on/off auf Kleinschreibung für die CLI-Validierung.
18. Zeile **22**: <code>            if value not in ("on", "off"):</code> — Verwirft ungültige Fehlerbefehle ohne irgendeine Routenänderung.
19. Zeile **23**: <code>                print("Verwendung: fault on|off")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
20. Zeile **24**: <code>                return</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
21. Zeile **25**: <code>            self.action(lambda: self.mn.lab.set_fault(value == "on"))</code> — Übersetzt on zu True und off zu False und lässt den Controller die r3-Serverroute ändern.
22. Zeile **27**: <code>        def do_check(self, line):</code> — Startet die bidirektionale Ping-Prüfung über den interaktiven Fehlerbehandler.
23. Zeile **28**: <code>            """check: beide Ende-zu-Ende-Pings mit echtem Exitstatus prüfen."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
24. Zeile **29**: <code>            self.action(self.mn.lab.ping)</code> — Delegiert die jeweilige CLI-Aktion an den gemeinsamen Handler für verständliche Fehlermeldungen.
25. Zeile **31**: <code>        def do_state(self, line):</code> — Startet die vollständige Zustandsanzeige über denselben Fehlerbehandler.
26. Zeile **32**: <code>            """state: Adressen und Routingtabellen aller Knoten anzeigen."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
27. Zeile **33**: <code>            self.action(self.mn.lab.show)</code> — Delegiert die jeweilige CLI-Aktion an den gemeinsamen Handler für verständliche Fehlermeldungen.
28. Zeile **35**: <code>        def action(self, function):</code> — Fängt erwartete Kontrollfehler ab und zeigt FEHLER, statt die CLI zu beenden.
29. Zeile **36**: <code>            try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
30. Zeile **37**: <code>                function()</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
31. Zeile **38**: <code>            except (RuntimeError, ValueError) as error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
32. Zeile **39**: <code>                print(f"FEHLER: {error}")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
33. Zeile **40**: <code>    return LabCLI</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
34. Zeile **43**: <code>def main(argv=None):</code> — Parst den Startmodus, kontrolliert Abhängigkeiten/Root und verwaltet Aufbau, Prüfungen, CLI und Cleanup.
35. Zeile **44**: <code>    parser = argparse.ArgumentParser(description=__doc__)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
36. Zeile **45**: <code>    parser.add_argument("--path", choices=("A", "B"), default="A")</code> — Beschränkt die Startauswahl auf A/B und verwendet ohne Angabe den Originalpfad A.
37. Zeile **46**: <code>    parser.add_argument("--check-only", action="store_true", help="prüfen und ohne CLI beenden")</code> — Schaltet einen automatisierbaren Start-/Ping-/Cleanup-Lauf ohne interaktive CLI ein.
38. Zeile **47**: <code>    args = parser.parse_args(argv)</code> — Parst die Kommandozeile vor den Mininet-Imports; --help funktioniert dadurch auch ohne installiertes Mininet.
39. Zeile **48**: <code>    try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
40. Zeile **49**: <code>        from mininet.net import Mininet</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
41. Zeile **50**: <code>        from mininet.cli import CLI</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
42. Zeile **51**: <code>        from mininet.link import TCLink</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
43. Zeile **52**: <code>        from mininet.log import setLogLevel</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
44. Zeile **53**: <code>        from topology import RoutingTopo</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
45. Zeile **54**: <code>    except ImportError as error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
46. Zeile **55**: <code>        print(f"Mininet nicht verfügbar: {error}. Keine Installation durchgeführt.", file=sys.stderr)</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
47. Zeile **56**: <code>        return 2</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
48. Zeile **57**: <code>    if os.geteuid() != 0:</code> — Prüft nach den Imports, ob die für Mininet erforderlichen Root-Rechte vorliegen, bevor das Netz angelegt wird.
49. Zeile **58**: <code>        print("Mininet benötigt root: sudo python3 start_lab.py", file=sys.stderr)</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
50. Zeile **59**: <code>        return 2</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
51. Zeile **60**: <code>    setLogLevel("info")</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
52. Zeile **61**: <code>    net = None</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
53. Zeile **62**: <code>    try:</code> — Beginnt einen Bereich, dessen Fehler im folgenden except behandelt bzw. dessen Ressourcen im finally aufgeräumt werden.
54. Zeile **63**: <code>        net = Mininet(topo=RoutingTopo(), controller=None, link=TCLink, autoSetMacs=True, build=False)</code> — Erzeugt das Laborobjekt ohne automatischen Netzaufbau: build=False ermöglicht die Zuweisung an net vor dem ersten Aufbauversuch und damit Cleanup bei Build-Fehlern; Controller bleibt deaktiviert, Links TC-fähig, MAC-Vergabe reproduzierbar.
55. Zeile **64**: <code>        net.build()</code> — Baut das bereits zugewiesene Mininet-Netz ausdrücklich innerhalb des try/finally auf; bei Teilaufbaufehlern erreicht der Cleanup dasselbe Objekt.
56. Zeile **65**: <code>        net.start()</code> — Startet das erzeugte Mininet-Netz; im Test wird der entsprechende Lebenszyklusaufruf simuliert.
57. Zeile **66**: <code>        net.lab = LabControl(net)</code> — Hängt den Controller an genau dieses Netz, sodass sowohl der Starter als auch die CLI denselben Pfad-/Fehlerzustand verwenden.
58. Zeile **67**: <code>        net.lab.configure(args.path)</code> — Richtet den ausgewählten A/B-Pfad samt sämtlichen IP-Adressen und Routen ein.
59. Zeile **68**: <code>        net.lab.show()</code> — Zeigt den realen Zustand der Laborknoten vor der Startprüfung.
60. Zeile **69**: <code>        net.lab.ping()</code> — Verlangt erfolgreiche bidirektionale Ping-Exitcodes, bevor die CLI oder Erfolg zugelassen wird.
61. Zeile **70**: <code>        if not args.check_only:</code> — Öffnet die interaktive CLI nur nach erfolgreichem Startcheck und nur ohne --check-only.
62. Zeile **71**: <code>            print("CLI: path A|B, fault on|off, check, state; exit beendet und räumt auf.")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
63. Zeile **72**: <code>            make_cli(CLI)(net)</code> — Instanziiert die erweiterte echte Mininet-CLI für das aktuelle Netz und blockiert bis zu deren Ende.
64. Zeile **73**: <code>        return 0</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
65. Zeile **74**: <code>    except (RuntimeError, OSError) as error:</code> — Fängt ausschließlich den sichtbaren Fehlertyp ab und bindet ihn ggf. an die angegebene Variable.
66. Zeile **75**: <code>        print(f"Labor fehlgeschlagen: {error}", file=sys.stderr)</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
67. Zeile **76**: <code>        return 1</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
68. Zeile **77**: <code>    finally:</code> — Dieser Cleanup-Block läuft unabhängig von Erfolg, return oder Exception nach Eintritt in try.
69. Zeile **78**: <code>        if net is not None:</code> — Stoppt im finally nur ein zugewiesenes Laborobjekt; dank build=False ist dieses auch bei Fehlern im expliziten build vorhanden.
70. Zeile **79**: <code>            net.stop()</code> — Stoppt das erzeugte Mininet-Netz im Cleanup; im Fake wird nur das entsprechende Flag gesetzt.
71. Zeile **82**: <code>if __name__ == "__main__":</code> — Führt den folgenden Programmstart nur beim direkten Aufruf aus, nicht beim Import im Test.
72. Zeile **83**: <code>    sys.exit(main())</code> — Übergibt den von main gelieferten Integer als Prozess-Exitcode an den aufrufenden Prozess.

## Datei: `test_lab.py`

FakeNode zeichnet Aufrufe auf und verwaltet nur ein Python-Dict synthetischer Routen. Der absichtlich widersprüchliche Fake-Pingtext „100% packet loss“ hat keine Messbedeutung: Das Testobjekt liefert frei eingestellte Exitcodes, damit kein Substring die Auswertung beeinflusst. FakeNet erzeugt keine Namespaces. FakeTopo zeichnet Host-/Link-Parameter auf. synthetic_modules ersetzt Imports vorübergehend; load_topology lädt die echte eigene Topologie gegen diese API-Doubles. ModelTests prüfen Adressen, Subnetze, Hin-/Rückpfad und Delay-Rechnung; ControlTests prüfen Konfiguration, Fehler/Rollback und Exitcode-Logik; StartupTests prüfen Starter-Lebenszyklus und CLI. DocumentationTests sichern jede erklärte Quellzeile sowie Bytegleichheit der Vorlagen mit dem gelieferten ZIP. Assertions laufen auch ohne Root und ohne Mininet.

1. Zeile **1**: <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).</code> — Kennzeichnet den KI-Einsatz einschließlich Tool, Provider und genauem Modell.
2. Zeile **2**: <code># Datum: 2026-10-29</code> — Dokumentiert das vorgegebene Erstellungsdatum der KI-Unterstützung.
3. Zeile **3**: <code># Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;</code> — Dokumentiert den tatsächlichen Arbeitsauftrag für diesen übernommenen Code.
4. Zeile **4**: <code># lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.</code> — Setzt den Auftrag mit Laufbarkeit, Tests und ausdrücklicher Kennzeichnung synthetischer Ergebnisse fort.
5. Zeile **5**: <code>"""Nur synthetische API-/Modelltests: KEINE Netzwerk-, Ping- oder RTT-Messungen."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
6. Zeile **7**: <code>import contextlib</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
7. Zeile **8**: <code>import importlib.util</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
8. Zeile **9**: <code>import io</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
9. Zeile **10**: <code>import html</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
10. Zeile **11**: <code>import re</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
11. Zeile **12**: <code>import zipfile</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
12. Zeile **13**: <code>import ipaddress</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
13. Zeile **14**: <code>from pathlib import Path</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
14. Zeile **15**: <code>import sys</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
15. Zeile **16**: <code>import types</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
16. Zeile **17**: <code>import unittest</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
17. Zeile **18**: <code>from unittest import mock</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
18. Zeile **19**: <code>from lab_config import DEFAULT_ROUTES, LINKS, NODES, PATH_NODES, PATH_ROUTES, R3_ROUTES</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
19. Zeile **20**: <code>from lab_control import LabControl, checked, route_args</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
20. Zeile **21**: <code>import start_lab</code> — Bindet die angegebenen Python-Module für die unten sichtbaren Aufrufe ein.
21. Zeile **24**: <code>class FakeNode:</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
22. Zeile **25**: <code>    def __init__(self, name):</code> — Initialisiert die in dieser Klasse gespeicherten Zustandsfelder.
23. Zeile **26**: <code>        self.name = name</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
24. Zeile **27**: <code>        self.calls = []</code> — Beginnt das Argumentprotokoll aller synthetischen pexec-Aufrufe.
25. Zeile **28**: <code>        self.routes = {}</code> — Beginnt ein leeres Python-Dict für synthetische statische Routen, keine Kernel-Routingtabelle.
26. Zeile **29**: <code>        self.failures = []</code> — Beginnt die Liste gezielt einmalig fehlschlagender Fake-Kommandos.
27. Zeile **30**: <code>        self.ping_status = 0</code> — Setzt den frei steuerbaren synthetischen Ping-Exitcode, ohne Netzwerkverkehr zu erzeugen.
28. Zeile **32**: <code>    def config(self, **params):</code> — Delegiert die Basiskonfiguration; beim echten LinuxRouter kommt geprüfter Forwarding-sysctl hinzu.
29. Zeile **33**: <code>        return params</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
30. Zeile **35**: <code>    def pexec(self, *args):</code> — Simuliert pexec nur in Python: protokolliert Argumente, injiziert Fehler oder ändert das Routendict.
31. Zeile **36**: <code>        self.calls.append(args)</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
32. Zeile **37**: <code>        if args in self.failures:</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
33. Zeile **38**: <code>            self.failures.remove(args)</code> — Verbraucht den einmaligen injizierten Befehlsfehler, damit ein späterer Aufruf wieder anders reagieren kann.
34. Zeile **39**: <code>            return "", "synthetic command failure", 7</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
35. Zeile **40**: <code>        if args[0] == "ping":</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
36. Zeile **41**: <code>            return "SYNTHETISCH: 100% packet loss\n", "", self.ping_status</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
37. Zeile **42**: <code>        if args[:2] == ("ip", "route") and args[2] in ("replace", "del"):</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
38. Zeile **43**: <code>            operation, prefix = args[2:4]</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
39. Zeile **44**: <code>            if operation == "del":</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
40. Zeile **45**: <code>                if prefix not in self.routes:</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
41. Zeile **46**: <code>                    return "", "synthetic missing route", 2</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
42. Zeile **47**: <code>                del self.routes[prefix]</code> — Entfernt ausschließlich diesen Eintrag aus dem synthetischen Routendict.
43. Zeile **48**: <code>            else:</code> — Führt den alternativen Zweig aus, wenn die unmittelbar zugehörige Bedingung falsch war.
44. Zeile **49**: <code>                self.routes[prefix] = args[4:]</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
45. Zeile **50**: <code>        return "", "", 0</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
46. Zeile **53**: <code>class FakeNet(dict):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
47. Zeile **54**: <code>    def __init__(self, **kwargs):</code> — Initialisiert die in dieser Klasse gespeicherten Zustandsfelder.
48. Zeile **55**: <code>        super().__init__((name, FakeNode(name)) for name in NODES)</code> — Ruft die Basisklasseninitialisierung mit den sichtbaren Argumenten auf.
49. Zeile **56**: <code>        self.built = False</code> — Markiert das Fake-Netz als noch nicht aufgebaut; erzeugt keine echten Ressourcen.
50. Zeile **57**: <code>        self.started = False</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
51. Zeile **58**: <code>        self.stopped = False</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
52. Zeile **60**: <code>    def build(self):</code> — Baut in RoutingTopo die modellierten Knoten und Links; FakeNet markiert den synthetischen Aufbau, FakeTopo stellt einen leeren Basishook bereit.
53. Zeile **61**: <code>        self.built = True</code> — Markiert den erfolgreichen synthetischen build-Aufruf, damit start die Reihenfolge prüfen kann.
54. Zeile **63**: <code>    def start(self):</code> — Markiert das synthetische Netz als gestartet; erzeugt keine echten Ressourcen.
55. Zeile **64**: <code>        if not self.built:</code> — Verhindert im Fake einen Start ohne vorher erfolgreichen expliziten Aufbau.
56. Zeile **65**: <code>            raise RuntimeError("synthetic start before build")</code> — Bricht mit der sichtbaren Exception samt Diagnose ab; „from error“ erhält zusätzlich die ursprüngliche Ursache.
57. Zeile **66**: <code>        self.started = True</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
58. Zeile **68**: <code>    def stop(self):</code> — Markiert das synthetische Netz als gestoppt; prüfbarer Cleanup-Nachweis auf API-Ebene.
59. Zeile **69**: <code>        self.stopped = True</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
60. Zeile **72**: <code>class FakeTopo:</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
61. Zeile **73**: <code>    def __init__(self):</code> — Initialisiert die in dieser Klasse gespeicherten Zustandsfelder.
62. Zeile **74**: <code>        self.hosts = {}</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
63. Zeile **75**: <code>        self.links = []</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
64. Zeile **76**: <code>        self.build()</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
65. Zeile **78**: <code>    def build(self):</code> — Baut in RoutingTopo die modellierten Knoten und Links; FakeNet markiert den synthetischen Aufbau, FakeTopo stellt einen leeren Basishook bereit.
66. Zeile **79**: <code>        pass</code> — Leerer Fake-Basishook; erlaubt Aufruf ohne jede echte Netzoperation.
67. Zeile **81**: <code>    def addHost(self, name, **params):</code> — Speichert die übergebenen Hostparameter im Fake statt einen Mininet-Knoten anzulegen.
68. Zeile **82**: <code>        self.hosts[name] = params</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
69. Zeile **83**: <code>        return name</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
70. Zeile **85**: <code>    def addLink(self, left, right, **params):</code> — Speichert die Linkparameter im Fake statt veth/qdisc anzulegen.
71. Zeile **86**: <code>        self.links.append((left, right, params))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
72. Zeile **89**: <code>def synthetic_modules(net):</code> — Erzeugt isolierte Modulobjekte mit genau den hier benötigten Mininet-Namen.
73. Zeile **90**: <code>    modules = {name: types.ModuleType(name) for name in</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
74. Zeile **91**: <code>               ("mininet", "mininet.net", "mininet.cli", "mininet.link",</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
75. Zeile **92**: <code>                "mininet.log", "mininet.topo", "mininet.node")}</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
76. Zeile **93**: <code>    modules["mininet.net"].Mininet = mock.Mock(return_value=net)</code> — Ersetzt den Mininet-Konstruktor durch einen aufrufprotokollierenden Mock, der das vorbereitete Fake-Netz liefert.
77. Zeile **94**: <code>    modules["mininet.cli"].CLI = lambda network: None</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
78. Zeile **95**: <code>    modules["mininet.link"].TCLink = object</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
79. Zeile **96**: <code>    modules["mininet.log"].setLogLevel = lambda level: None</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
80. Zeile **97**: <code>    modules["mininet.topo"].Topo = FakeTopo</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
81. Zeile **98**: <code>    modules["mininet.node"].Host = object</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
82. Zeile **99**: <code>    modules["mininet.node"].Node = FakeNode</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
83. Zeile **100**: <code>    return modules</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
84. Zeile **103**: <code>def load_topology():</code> — Lädt den eigenen topology.py-Quelltext per importlib gegen die gerade injizierten Module.
85. Zeile **104**: <code>    path = Path(__file__).with_name("topology.py")</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
86. Zeile **105**: <code>    spec = importlib.util.spec_from_file_location("synthetic_topology", path)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
87. Zeile **106**: <code>    assert spec is not None and spec.loader is not None</code> — Sichert die erwartete Loader-Voraussetzung für das dynamische Laden der eigenen Topologiedatei.
88. Zeile **107**: <code>    module = importlib.util.module_from_spec(spec)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
89. Zeile **108**: <code>    spec.loader.exec_module(module)</code> — Führt den eigenen Topologie-Modulcode mit den temporär injizierten Mininet-Modulen aus.
90. Zeile **109**: <code>    return module</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
91. Zeile **112**: <code>class ModelTests(unittest.TestCase):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
92. Zeile **113**: <code>    def test_unique_interfaces_and_distinct_routed_subnets(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: unique interfaces and distinct routed subnets.
93. Zeile **114**: <code>        interfaces = []</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
94. Zeile **115**: <code>        networks = []</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
95. Zeile **116**: <code>        for left, right, il, ir, al, ar, delay in LINKS:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
96. Zeile **117**: <code>            interfaces.extend(((left, il), (right, ir)))</code> — Ergänzt die Sammlung um beide Interface-Endpunkte dieses Links.
97. Zeile **118**: <code>            a, b = ipaddress.ip_interface(al), ipaddress.ip_interface(ar)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
98. Zeile **119**: <code>            self.assertEqual(a.network, b.network)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
99. Zeile **120**: <code>            self.assertNotEqual(a.ip, b.ip)</code> — Prüft, dass die beiden sichtbaren Werte verschieden sind, insbesondere die Endadressen eines Links.
100. Zeile **121**: <code>            self.assertIn(delay, ("1ms", "5ms", "30ms"))</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
101. Zeile **122**: <code>            networks.append(a.network)</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
102. Zeile **123**: <code>        self.assertEqual(len(interfaces), len(set(interfaces)))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
103. Zeile **124**: <code>        self.assertEqual(len(networks), len(set(networks)))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
104. Zeile **125**: <code>        for index, network in enumerate(networks):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
105. Zeile **126**: <code>            self.assertFalse(any(network.overlaps(other) for other in networks[index + 1:]))</code> — Verlangt einen falschen Zustand für die sichtbare Prüfung.
106. Zeile **128**: <code>    def test_original_addresses_and_new_links(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: original addresses and new links.
107. Zeile **129**: <code>        self.assertEqual(LINKS[0][2:6], ("client-eth0", "r1-eth0", "10.0.1.2/24", "10.0.1.1/24"))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
108. Zeile **130**: <code>        self.assertEqual(LINKS[1][2:6], ("r1-eth1", "r2-eth0", "10.0.12.1/30", "10.0.12.2/30"))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
109. Zeile **131**: <code>        self.assertEqual(LINKS[2][2:6], ("r2-eth1", "server-eth0", "10.0.2.1/24", "10.0.2.2/24"))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
110. Zeile **132**: <code>        self.assertEqual(LINKS[3][2:6], ("r1-eth2", "r3-eth0", "10.0.13.1/30", "10.0.13.2/30"))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
111. Zeile **133**: <code>        self.assertEqual(LINKS[4][2:6], ("r3-eth1", "r2-eth2", "10.0.23.1/30", "10.0.23.2/30"))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
112. Zeile **135**: <code>    def test_symmetric_model_walk_and_delay_budget(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: symmetric model walk and delay budget.
113. Zeile **136**: <code>        for path, expected in PATH_NODES.items():</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
114. Zeile **137**: <code>            for nodes, target in ((expected, "10.0.2.2"), (expected[::-1], "10.0.1.2")):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
115. Zeile **138**: <code>                total = 0</code> — Initialisiert die Summe der einseitigen Linkverzögerungen für die Modellrechnung.
116. Zeile **139**: <code>                for source, destination in zip(nodes, nodes[1:]):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
117. Zeile **140**: <code>                    link = next(link for link in LINKS if {source, destination} == set(link[:2]))</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
118. Zeile **141**: <code>                    total += int(link[-1][:-2])</code> — Addiert den numerischen Millisekundenanteil des aktuellen Link-Delays zur einseitigen Modellsumme.
119. Zeile **142**: <code>                    side = 0 if source == link[0] else 1</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
120. Zeile **143**: <code>                    neighbor_address = ipaddress.ip_interface(link[5 - side]).ip</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
121. Zeile **144**: <code>                    if source in ("r1", "r2", "r3"):</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
122. Zeile **145**: <code>                        routes = PATH_ROUTES[path] + R3_ROUTES</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
123. Zeile **146**: <code>                        relevant = [r for r in routes if r[0] == source and</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
124. Zeile **147**: <code>                                    ipaddress.ip_address(target) in ipaddress.ip_network(r[1])]</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
125. Zeile **148**: <code>                        if relevant:</code> — Prüft diese Bedingung; nur bei wahrem Ergebnis wird der folgende eingerückte Zweig ausgeführt.
126. Zeile **149**: <code>                            self.assertEqual(len(relevant), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
127. Zeile **150**: <code>                            self.assertEqual(relevant[0][2], str(neighbor_address))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
128. Zeile **151**: <code>                            self.assertEqual(relevant[0][3], link[2 + side])</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
129. Zeile **152**: <code>                        else:</code> — Führt den alternativen Zweig aus, wenn die unmittelbar zugehörige Bedingung falsch war.
130. Zeile **153**: <code>                            self.assertIn(ipaddress.ip_address(target), ipaddress.ip_interface(link[4 + side]).network)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
131. Zeile **154**: <code>                    else:</code> — Führt den alternativen Zweig aus, wenn die unmittelbar zugehörige Bedingung falsch war.
132. Zeile **155**: <code>                        self.assertIn((source, str(neighbor_address), link[2 + side]), DEFAULT_ROUTES)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
133. Zeile **156**: <code>                self.assertEqual(2 * total, {"A": 14, "B": 124}[path])</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
134. Zeile **158**: <code>    def test_router_forwarding_config_and_failure(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: router forwarding config and failure.
135. Zeile **159**: <code>        with mock.patch.dict(sys.modules, synthetic_modules(FakeNet())):</code> — Ersetzt nur während dieses Blocks Module/Funktionen durch Testdoubles; beim Verlassen werden die Originale wiederhergestellt.
136. Zeile **160**: <code>            topology = load_topology()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
137. Zeile **161**: <code>        router = topology.LinuxRouter("r3")</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
138. Zeile **162**: <code>        self.assertEqual(router.config(ip=None), {"ip": None})</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
139. Zeile **163**: <code>        command = ("sysctl", "-w", "net.ipv4.ip_forward=1")</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
140. Zeile **164**: <code>        self.assertIn(command, router.calls)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
141. Zeile **165**: <code>        router.failures.append(command)</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
142. Zeile **166**: <code>        with self.assertRaises(RuntimeError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
143. Zeile **167**: <code>            router.config()</code> — Prüft den Konfigurationshook des eigenen Routers gegen einen simulierten pexec-Befehl.
144. Zeile **169**: <code>    def test_topology_calls(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: topology calls.
145. Zeile **170**: <code>        with mock.patch.dict(sys.modules, synthetic_modules(FakeNet())):</code> — Ersetzt nur während dieses Blocks Module/Funktionen durch Testdoubles; beim Verlassen werden die Originale wiederhergestellt.
146. Zeile **171**: <code>            topology = load_topology()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
147. Zeile **172**: <code>            topo = topology.RoutingTopo()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
148. Zeile **173**: <code>        self.assertEqual(set(topo.hosts), set(NODES))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
149. Zeile **174**: <code>        self.assertTrue(all(host["ip"] is None for host in topo.hosts.values()))</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
150. Zeile **175**: <code>        self.assertEqual(len(topo.links), 5)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
151. Zeile **176**: <code>        for actual, expected in zip(topo.links, LINKS):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
152. Zeile **177**: <code>            left, right, params = actual</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
153. Zeile **178**: <code>            self.assertEqual((left, right, params["intfName1"], params["intfName2"], params["delay"]),</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
154. Zeile **179**: <code>                             (expected[0], expected[1], expected[2], expected[3], expected[6]))</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
155. Zeile **182**: <code>class ControlTests(unittest.TestCase):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
156. Zeile **183**: <code>    def setUp(self):</code> — Erzeugt vor jedem Kontrolltest frische Fake-Knoten und konfiguriert den Ausgangspfad A.
157. Zeile **184**: <code>        self.net = FakeNet()</code> — Speichert die Abbildung der Knotennamen auf die zu steuernden Node-Objekte.
158. Zeile **185**: <code>        self.lab = LabControl(self.net)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
159. Zeile **186**: <code>        self.lab.configure()</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
160. Zeile **188**: <code>    def assert_path(self, path):</code> — Prüft Pfadflag, Next-Hop-/Interface-Argumente und genau eine verwaltete Fernroute pro r1/r2.
161. Zeile **189**: <code>        self.assertEqual(self.lab.path, path)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
162. Zeile **190**: <code>        for route in PATH_ROUTES[path]:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
163. Zeile **191**: <code>            self.assertEqual(self.net[route[0]].routes[route[1]], route_args(route)[4:])</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
164. Zeile **192**: <code>        self.assertEqual(len(self.net["r1"].routes), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
165. Zeile **193**: <code>        self.assertEqual(len(self.net["r2"].routes), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
166. Zeile **195**: <code>    def test_configuration_and_path_round_trip(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: configuration and path round trip.
167. Zeile **196**: <code>        self.assert_path("A")</code> — Prüft zusätzlich zum Flag die tatsächlichen synthetischen Routendicts und ihre Anzahl für diesen Pfad.
168. Zeile **197**: <code>        for left, right, il, ir, al, ar, _ in LINKS:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
169. Zeile **198**: <code>            for node, interface, address in ((left, il, al), (right, ir, ar)):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
170. Zeile **199**: <code>                self.assertIn(("ip", "addr", "add", address, "dev", interface), self.net[node].calls)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
171. Zeile **200**: <code>        for path in ("B", "A", "B"):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
172. Zeile **201**: <code>            self.lab.select_path(path)</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
173. Zeile **202**: <code>            self.assert_path(path)</code> — Prüft zusätzlich zum Flag die tatsächlichen synthetischen Routendicts und ihre Anzahl für diesen Pfad.
174. Zeile **203**: <code>        for node, gateway, interface in DEFAULT_ROUTES:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
175. Zeile **204**: <code>            self.assertEqual(self.net[node].routes["default"], ("via", gateway, "dev", interface))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
176. Zeile **206**: <code>    def test_invalid_path_has_no_side_effects(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: invalid path has no side effects.
177. Zeile **207**: <code>        before = sum(len(node.calls) for node in self.net.values())</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
178. Zeile **208**: <code>        for operation in (self.lab.configure, self.lab.select_path):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
179. Zeile **209**: <code>            with self.assertRaises(ValueError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
180. Zeile **210**: <code>                operation("C")</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
181. Zeile **211**: <code>        self.assertEqual(before, sum(len(node.calls) for node in self.net.values()))</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
182. Zeile **213**: <code>    def test_switch_rolls_back_after_second_router_failure(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: switch rolls back after second router failure.
183. Zeile **214**: <code>        self.net["r2"].failures.append(route_args(PATH_ROUTES["B"][1]))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
184. Zeile **215**: <code>        with self.assertRaises(RuntimeError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
185. Zeile **216**: <code>            self.lab.select_path("B")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
186. Zeile **217**: <code>        self.assert_path("A")</code> — Prüft zusätzlich zum Flag die tatsächlichen synthetischen Routendicts und ihre Anzahl für diesen Pfad.
187. Zeile **219**: <code>    def test_rollback_failure_marks_state_unknown(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: rollback failure marks state unknown.
188. Zeile **220**: <code>        self.net["r2"].failures.append(route_args(PATH_ROUTES["B"][1]))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
189. Zeile **221**: <code>        self.net["r1"].failures.append(route_args(PATH_ROUTES["A"][0]))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
190. Zeile **222**: <code>        with self.assertRaisesRegex(RuntimeError, "Rollback fehlgeschlagen"):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
191. Zeile **223**: <code>            self.lab.select_path("B")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
192. Zeile **224**: <code>        self.assertIsNone(self.lab.path)</code> — Verlangt explizit None als unbekannten/nicht initialisierten Pfadstatus.
193. Zeile **226**: <code>    def test_initial_failure_removes_partial_route(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: initial failure removes partial route.
194. Zeile **227**: <code>        net = FakeNet()</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
195. Zeile **228**: <code>        net["r2"].failures.append(route_args(PATH_ROUTES["A"][1]))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
196. Zeile **229**: <code>        lab = LabControl(net)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
197. Zeile **230**: <code>        with self.assertRaises(RuntimeError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
198. Zeile **231**: <code>            lab.select_path("A")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
199. Zeile **232**: <code>        self.assertEqual(net["r1"].routes, {})</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
200. Zeile **233**: <code>        self.assertIsNone(lab.path)</code> — Verlangt explizit None als unbekannten/nicht initialisierten Pfadstatus.
201. Zeile **235**: <code>    def test_fault_delete_restore_and_idempotency(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: fault delete restore and idempotency.
202. Zeile **236**: <code>        self.lab.select_path("B")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
203. Zeile **237**: <code>        self.lab.set_fault(True)</code> — Schaltet den modellierten r3-Serverroutenfehler gezielt ein oder aus.
204. Zeile **238**: <code>        self.assertNotIn("10.0.2.0/24", self.net["r3"].routes)</code> — Prüft, dass der bezeichnete Wert nicht in der sichtbaren Sammlung enthalten ist.
205. Zeile **239**: <code>        self.assertIn("10.0.1.0/24", self.net["r3"].routes)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
206. Zeile **240**: <code>        count = len(self.net["r3"].calls)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
207. Zeile **241**: <code>        self.lab.set_fault(True)</code> — Schaltet den modellierten r3-Serverroutenfehler gezielt ein oder aus.
208. Zeile **242**: <code>        self.assertEqual(len(self.net["r3"].calls), count)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
209. Zeile **243**: <code>        self.lab.select_path("A")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
210. Zeile **244**: <code>        self.assertTrue(self.lab.fault)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
211. Zeile **245**: <code>        self.lab.set_fault(False)</code> — Schaltet den modellierten r3-Serverroutenfehler gezielt ein oder aus.
212. Zeile **246**: <code>        self.assertFalse(self.lab.fault)</code> — Verlangt einen falschen Zustand für die sichtbare Prüfung.
213. Zeile **247**: <code>        self.assertEqual(self.net["r3"].routes["10.0.2.0/24"], route_args(R3_ROUTES[0])[4:])</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
214. Zeile **249**: <code>    def test_failed_fault_command_does_not_change_flag(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: failed fault command does not change flag.
215. Zeile **250**: <code>        self.net["r3"].failures.append(route_args(R3_ROUTES[0], "del"))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
216. Zeile **251**: <code>        with self.assertRaises(RuntimeError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
217. Zeile **252**: <code>            self.lab.set_fault(True)</code> — Schaltet den modellierten r3-Serverroutenfehler gezielt ein oder aus.
218. Zeile **253**: <code>        self.assertFalse(self.lab.fault)</code> — Verlangt einen falschen Zustand für die sichtbare Prüfung.
219. Zeile **255**: <code>    def test_ping_uses_exit_status_not_loss_substring(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: ping uses exit status not loss substring.
220. Zeile **256**: <code>        for status in (1, 2):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
221. Zeile **257**: <code>            self.net["client"].ping_status = status</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
222. Zeile **258**: <code>            with self.assertRaisesRegex(RuntimeError, f"exit={status}"):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
223. Zeile **259**: <code>                self.lab.ping()</code> — Ruft die echte Kontrolllogik gegen Fake-Knoten auf, ohne ICMP-Pakete zu senden.
224. Zeile **260**: <code>        self.net["client"].ping_status = 0</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
225. Zeile **261**: <code>        self.net["server"].ping_status = 1</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
226. Zeile **262**: <code>        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
227. Zeile **263**: <code>            self.lab.ping()</code> — Ruft die echte Kontrolllogik gegen Fake-Knoten auf, ohne ICMP-Pakete zu senden.
228. Zeile **264**: <code>        self.net["server"].ping_status = 0</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
229. Zeile **265**: <code>        with contextlib.redirect_stdout(io.StringIO()):</code> — Lenkt stdout/stderr nur für diesen Testblock in Speicher um, statt Testausgaben zu vermischen.
230. Zeile **266**: <code>            self.lab.ping(4)</code> — Ruft die echte Kontrolllogik gegen Fake-Knoten auf, ohne ICMP-Pakete zu senden.
231. Zeile **267**: <code>        self.assertIn(("ping", "-n", "-c", "4", "-W", "2", "-w", "14", "10.0.2.2"), self.net["client"].calls)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
232. Zeile **268**: <code>        for count in (0, -1, "3"):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
233. Zeile **269**: <code>            with self.assertRaises(ValueError):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
234. Zeile **270**: <code>                self.lab.ping(count)</code> — Ruft die echte Kontrolllogik gegen Fake-Knoten auf, ohne ICMP-Pakete zu senden.
235. Zeile **272**: <code>    def test_spawn_error_also_rolls_back(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: spawn error also rolls back.
236. Zeile **273**: <code>        with mock.patch.object(self.net["r2"], "pexec", side_effect=OSError("synthetic spawn failure")):</code> — Ersetzt nur während dieses Blocks Module/Funktionen durch Testdoubles; beim Verlassen werden die Originale wiederhergestellt.
237. Zeile **274**: <code>            with self.assertRaisesRegex(RuntimeError, "Prozessstart fehlgeschlagen"):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
238. Zeile **275**: <code>                self.lab.select_path("B")</code> — Führt den sichtbaren Pfadwechsel aus; im Test wird dessen Erfolg oder Fehler gezielt überprüft.
239. Zeile **276**: <code>        self.assert_path("A")</code> — Prüft zusätzlich zum Flag die tatsächlichen synthetischen Routendicts und ihre Anzahl für diesen Pfad.
240. Zeile **278**: <code>    def test_reconfigure_restores_fault_flag_and_route(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: reconfigure restores fault flag and route.
241. Zeile **279**: <code>        self.lab.set_fault(True)</code> — Schaltet den modellierten r3-Serverroutenfehler gezielt ein oder aus.
242. Zeile **280**: <code>        self.lab.configure("B")</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
243. Zeile **281**: <code>        self.assertFalse(self.lab.fault)</code> — Verlangt einen falschen Zustand für die sichtbare Prüfung.
244. Zeile **282**: <code>        self.assertIn("10.0.2.0/24", self.net["r3"].routes)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
245. Zeile **283**: <code>        self.assert_path("B")</code> — Prüft zusätzlich zum Flag die tatsächlichen synthetischen Routendicts und ihre Anzahl für diesen Pfad.
246. Zeile **285**: <code>    def test_checked_reports_stderr(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: checked reports stderr.
247. Zeile **286**: <code>        node = self.net["r1"]</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
248. Zeile **287**: <code>        node.failures.append(("bad",))</code> — Fügt den sichtbaren Wert dem Protokoll, den erfolgreichen Teilschritten oder den gezielt injizierten Testfehlern hinzu.
249. Zeile **288**: <code>        with self.assertRaisesRegex(RuntimeError, "synthetic command failure"):</code> — Erwartet im folgenden Block den angegebenen Exception-Typ, ggf. mit passender Fehlermeldung; Ausbleiben lässt den Test scheitern.
250. Zeile **289**: <code>            checked(node, "bad")</code> — Führt den sichtbaren, argumentgetrennten Knotenbefehl mit strikter Exitcode-Prüfung aus.
251. Zeile **292**: <code>class StartupTests(unittest.TestCase):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
252. Zeile **293**: <code>    def run_main(self, net, args):</code> — Führt den echten Starter mit temporären Fake-Modulen und simuliertem Root aus; fängt nur Textausgabe ab.
253. Zeile **294**: <code>        modules = synthetic_modules(net)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
254. Zeile **295**: <code>        with mock.patch.dict(sys.modules, modules):</code> — Ersetzt nur während dieses Blocks Module/Funktionen durch Testdoubles; beim Verlassen werden die Originale wiederhergestellt.
255. Zeile **296**: <code>            modules["topology"] = load_topology()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
256. Zeile **297**: <code>        with mock.patch.dict(sys.modules, modules), mock.patch.object(start_lab.os, "geteuid", return_value=0):</code> — Ersetzt nur während dieses Blocks Module/Funktionen durch Testdoubles; beim Verlassen werden die Originale wiederhergestellt.
257. Zeile **298**: <code>            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):</code> — Lenkt stdout/stderr nur für diesen Testblock in Speicher um, statt Testausgaben zu vermischen.
258. Zeile **299**: <code>                status = start_lab.main(args)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
259. Zeile **300**: <code>        modules["mininet.net"].Mininet.assert_called_once_with(</code> — Prüft genau einen Konstruktoraufruf mit sämtlichen erwarteten Argumenten, insbesondere dem Cleanup-relevanten build=False.
260. Zeile **301**: <code>            topo=mock.ANY, controller=None, link=object, autoSetMacs=True, build=False)</code> — Erwartet eine Topologie, keinen Controller, den synthetischen TCLink-Platzhalter, automatische MACs und ausdrücklich deaktivierten Konstruktoraufbau.
261. Zeile **302**: <code>        return status</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
262. Zeile **304**: <code>    def test_check_only_starts_stops_both_paths(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: check only starts stops both paths.
263. Zeile **305**: <code>        for path in ("A", "B"):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
264. Zeile **306**: <code>            net = FakeNet()</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
265. Zeile **307**: <code>            self.assertEqual(self.run_main(net, ["--path", path, "--check-only"]), 0)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
266. Zeile **308**: <code>            self.assertTrue(net.built and net.started and net.stopped)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
267. Zeile **309**: <code>            self.assertEqual(net.lab.path, path)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
268. Zeile **311**: <code>    def test_ping_failure_is_nonzero_and_cleans_up(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: ping failure is nonzero and cleans up.
269. Zeile **312**: <code>        net = FakeNet()</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
270. Zeile **313**: <code>        net["client"].ping_status = 1</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
271. Zeile **314**: <code>        self.assertEqual(self.run_main(net, ["--check-only"]), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
272. Zeile **315**: <code>        self.assertTrue(net.stopped)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
273. Zeile **317**: <code>    def test_build_exception_still_stops_without_starting(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: build exception still stops without starting.
274. Zeile **318**: <code>        for error_type in (RuntimeError, OSError):</code> — Prüft beide vom Starter behandelten Fehlerklassen beim partiellen Netzaufbau.
275. Zeile **319**: <code>            with self.subTest(error_type=error_type):</code> — Kennzeichnet die beiden Build-Fehlervarianten separat, ohne beim ersten fehlgeschlagenen Teiltest abzubrechen.
276. Zeile **320**: <code>                net = FakeNet()</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
277. Zeile **321**: <code>                net.build = mock.Mock(side_effect=error_type("synthetic partial build failure"))</code> — Injiziert einen Fehler genau beim expliziten Aufbau des bereits existierenden Fake-Netzes.
278. Zeile **322**: <code>                net.start = mock.Mock(wraps=net.start)</code> — Protokolliert Startversuche und behält für erlaubte Aufrufe das ursprüngliche Fake-Verhalten bei.
279. Zeile **323**: <code>                net.stop = mock.Mock(wraps=net.stop)</code> — Protokolliert Cleanup-Aufrufe und setzt dabei weiterhin das prüfbare Fake-stop-Flag.
280. Zeile **324**: <code>                self.assertEqual(self.run_main(net, ["--check-only"]), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
281. Zeile **325**: <code>                net.build.assert_called_once_with()</code> — Verlangt genau einen expliziten Aufbauversuch ohne Zusatzargumente.
282. Zeile **326**: <code>                net.start.assert_not_called()</code> — Belegt, dass nach fehlgeschlagenem Aufbau kein Start versucht wurde.
283. Zeile **327**: <code>                net.stop.assert_called_once_with()</code> — Belegt genau einen Cleanup-Aufruf trotz Build-Exception.
284. Zeile **328**: <code>                self.assertTrue(net.stopped)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
285. Zeile **329**: <code>                self.assertFalse(hasattr(net, "lab"))</code> — Belegt, dass nach dem Build-Fehler keine Laborkonfiguration begonnen wurde.
286. Zeile **331**: <code>    def test_start_exception_still_stops(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: start exception still stops.
287. Zeile **332**: <code>        net = FakeNet()</code> — Merkt das Laborobjekt bzw. initialisiert dessen Referenz vor dem ressourcengeschützten Start.
288. Zeile **333**: <code>        net.start = mock.Mock(side_effect=RuntimeError("synthetic startup failure"))</code> — Startet das erzeugte Mininet-Netz; im Test wird der entsprechende Lebenszyklusaufruf simuliert.
289. Zeile **334**: <code>        self.assertEqual(self.run_main(net, []), 1)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
290. Zeile **335**: <code>        self.assertTrue(net.stopped)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
291. Zeile **337**: <code>    def test_cli_commands_and_error_messages(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: cli commands and error messages.
292. Zeile **338**: <code>        cli = start_lab.make_cli(object)()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
293. Zeile **339**: <code>        cli.mn = FakeNet()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
294. Zeile **340**: <code>        cli.mn.lab = LabControl(cli.mn)</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
295. Zeile **341**: <code>        cli.mn.lab.configure()</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
296. Zeile **342**: <code>        with contextlib.redirect_stdout(io.StringIO()) as output:</code> — Lenkt stdout/stderr nur für diesen Testblock in Speicher um, statt Testausgaben zu vermischen.
297. Zeile **343**: <code>            cli.do_path("b")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
298. Zeile **344**: <code>            self.assertEqual(cli.mn.lab.path, "B")</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
299. Zeile **345**: <code>            cli.do_fault("on")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
300. Zeile **346**: <code>            self.assertTrue(cli.mn.lab.fault)</code> — Verlangt einen wahren Zustand für die sichtbare Prüfung.
301. Zeile **347**: <code>            cli.do_fault("off")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
302. Zeile **348**: <code>            self.assertFalse(cli.mn.lab.fault)</code> — Verlangt einen falschen Zustand für die sichtbare Prüfung.
303. Zeile **349**: <code>            cli.do_fault("invalid")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
304. Zeile **350**: <code>            cli.do_path("C")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
305. Zeile **351**: <code>            cli.do_check("")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
306. Zeile **352**: <code>            cli.do_state("")</code> — Ruft den sichtbaren interaktiven CLI-Befehl direkt gegen das synthetische Testnetz auf.
307. Zeile **353**: <code>        self.assertIn("Verwendung: fault on|off", output.getvalue())</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
308. Zeile **354**: <code>        self.assertIn("FEHLER:", output.getvalue())</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
309. Zeile **355**: <code>        self.assertIn("Pfad=B", output.getvalue())</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
310. Zeile **358**: <code>class DocumentationTests(unittest.TestCase):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
311. Zeile **359**: <code>    def test_every_nonempty_source_line_is_explained_exactly_once(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: every nonempty source line is explained exactly once.
312. Zeile **360**: <code>        root = Path(__file__).resolve().parent</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
313. Zeile **361**: <code>        document = (root.parent / "erklaerung_topologie.md").read_text()</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
314. Zeile **362**: <code>        for source in sorted(root.glob("*.py")):</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
315. Zeile **363**: <code>            heading = f"## Datei: `{source.name}`\n"</code> — Bildet die exakt gesuchte Markdown-Abschnittsüberschrift für diese Python-Datei.
316. Zeile **364**: <code>            self.assertIn(heading, document)</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
317. Zeile **365**: <code>            section = document.split(heading, 1)[1].split("\n## ", 1)[0]</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
318. Zeile **366**: <code>            found = [(int(number), html.unescape(code)) for number, code in</code> — Sammelt die im Markdown erklärten (Zeilennummer, dekodierter Quelltext)-Paare für den exakten Vergleich.
319. Zeile **367**: <code>                     re.findall(r"^\d+\. Zeile \*\*(\d+)\*\*: &lt;code&gt;(.*?)&lt;/code&gt; — .+$", section, re.MULTILINE)]</code> — Setzt den begonnenen Ausdruck bzw. Aufruf mit den sichtbaren Argumenten oder Datensatzfeldern fort; gehört zur unmittelbar darüber beschriebenen Operation.
320. Zeile **368**: <code>            expected = [(number, line) for number, line in enumerate(source.read_text().splitlines(), 1) if line.strip()]</code> — Berechnet die erwarteten Originalquellzeilen oder die aktuelle Soll-Knotensequenz aus dem Modell.
321. Zeile **369**: <code>            self.assertEqual(found, expected, source.name)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
322. Zeile **370**: <code>            self.assertIn("KI-Kennzeichnung", source.read_text().splitlines()[0])</code> — Prüft Mitgliedschaft bzw. Teilstring des ersten Arguments im zweiten; die konkreten Sollwerte stehen in der Quellzeile.
323. Zeile **372**: <code>    def test_supplied_files_equal_original_archive(self):</code> — Definiert einen automatisch von unittest ausgeführten Testfall: supplied files equal original archive.
324. Zeile **373**: <code>        supplied = Path(__file__).resolve().parent.parent / "Angabe"</code> — Weist der sichtbaren Variablen bzw. dem Objektfeld den rechts berechneten Wert zu; dieser Wert wird im folgenden Block verwendet.
325. Zeile **374**: <code>        with zipfile.ZipFile(supplied / "uebb7_template.zip") as archive:</code> — Öffnet das gelieferte Originalarchiv lesend und schließt es nach dem Bytevergleich automatisch.
326. Zeile **375**: <code>            for name in archive.namelist():</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
327. Zeile **376**: <code>                self.assertEqual((supplied / name).read_bytes(), archive.read(name), name)</code> — Vergleicht die beiden angegebenen Werte auf Gleichheit; Abweichungen lassen diesen Test scheitern.
328. Zeile **379**: <code>if __name__ == "__main__":</code> — Führt den folgenden Programmstart nur beim direkten Aufruf aus, nicht beim Import im Test.
329. Zeile **380**: <code>    print("SYNTHETISCHE Tests: keine Mininet-Ausführung, keine echten Pings oder RTTs.")</code> — Gibt den sichtbaren Diagnose-/Statuswert aus; end="" vermeidet zusätzliche Leerzeilen, file=sys.stderr kennzeichnet Fehler.
330. Zeile **381**: <code>    unittest.main(verbosity=2)</code> — Findet und führt die Testmethoden aus; verbosity=2 zeigt Namen und Einzelresultate, Fehler führen zu Exitcode ungleich null.

## Datei: `topology.py`

LinuxRouter ist ein Node mit geprüft aktiviertem IPv4-Forwarding. Die Host-IP-Vorgabe None verhindert automatisch zugewiesene Mininet-/8-Adressen. Der Starter setzt danach jede Adresse explizit. addLink verwendet feste Interface-Namen und TCLink-Delays aus dem gemeinsamen Modell. Die topos-Registry ist zusätzlich für Mininet-Topologie-Loader bestimmt; die eigentliche vollständige IP-/Routingkonfiguration erfolgt im Starter.

1. Zeile **1**: <code># KI-Kennzeichnung (RN WS26): Hermes Agent, OpenAI / gpt-6.1-sol (ChatGPT or Codex Subscription).</code> — Kennzeichnet den KI-Einsatz einschließlich Tool, Provider und genauem Modell.
2. Zeile **2**: <code># Datum: 2026-10-29</code> — Dokumentiert das vorgegebene Erstellungsdatum der KI-Unterstützung.
3. Zeile **3**: <code># Anfrage: RN Blatt07 um r3, alternative Routerstrecke, A/B-Auswahl und Fehlersteuerung erweitern;</code> — Dokumentiert den tatsächlichen Arbeitsauftrag für diesen übernommenen Code.
4. Zeile **4**: <code># lauffähige Mininet-Dateien und unprivilegierte, ausdrücklich synthetische Tests erstellen.</code> — Setzt den Auftrag mit Laufbarkeit, Tests und ausdrücklicher Kennzeichnung synthetischer Ergebnisse fort.
5. Zeile **5**: <code>"""Originalkette plus r1-r3-r2; Server-LAN bleibt unverändert."""</code> — Dokumentationsstring beschreibt Zweck, Bedienung oder Aussagegrenze dieses Moduls bzw. dieser Methode.
6. Zeile **7**: <code>from mininet.topo import Topo</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
7. Zeile **8**: <code>from mininet.node import Host, Node</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
8. Zeile **9**: <code>from mininet.link import TCLink</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
9. Zeile **10**: <code>from lab_config import LINKS, NODES, ROUTERS</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
10. Zeile **11**: <code>from lab_control import checked</code> — Importiert die ausdrücklich genannten Klassen, Funktionen oder Konstanten aus dem bezeichneten Modul.
11. Zeile **14**: <code>class LinuxRouter(Node):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
12. Zeile **15**: <code>    def config(self, **params):</code> — Delegiert die Basiskonfiguration; beim echten LinuxRouter kommt geprüfter Forwarding-sysctl hinzu.
13. Zeile **16**: <code>        result = super().config(**params)</code> — Erhält die normale Mininet-Node-Konfiguration und merkt deren Rückgabewert, statt den Basishook zu überspringen.
14. Zeile **17**: <code>        checked(self, "sysctl", "-w", "net.ipv4.ip_forward=1")</code> — Aktiviert Weiterleitung bereits im LinuxRouter-Konfigurationshook und meldet einen sysctl-Fehler sofort.
15. Zeile **18**: <code>        return result</code> — Gibt den sichtbaren Wert zurück bzw. beendet bei leerem return die Methode ohne weitere Änderung.
16. Zeile **21**: <code>class RoutingTopo(Topo):</code> — Definiert diese Klasse mit der angegebenen Basisklasse; eingerückte Methoden gehören zu ihr.
17. Zeile **22**: <code>    def build(self):</code> — Baut in RoutingTopo die modellierten Knoten und Links; FakeNet markiert den synthetischen Aufbau, FakeTopo stellt einen leeren Basishook bereit.
18. Zeile **23**: <code>        for name in NODES:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
19. Zeile **24**: <code>            self.addHost(name, cls=LinuxRouter if name in ROUTERS else Host, ip=None)</code> — Erzeugt Router als LinuxRouter und Endhosts als Host; ip=None unterdrückt automatische /8-Vorgaben zugunsten des expliziten Modells.
20. Zeile **25**: <code>        for left, right, il, ir, _, _, delay in LINKS:</code> — Iteriert über die genannte Sammlung und entpackt deren Werte in die sichtbaren Variablen.
21. Zeile **26**: <code>            self.addLink(left, right, intfName1=il, intfName2=ir, cls=TCLink, delay=delay)</code> — Erzeugt einen direkten Link mit unveränderten/fest gewählten Interfacenamen und TC-Verzögerung auf beiden Richtungen.
22. Zeile **29**: <code>topos = {"routingtopo": RoutingTopo}</code> — Registriert die Topologie unter routingtopo für Mininet-Loader; Adressen und Routen richtet weiterhin der separate Starter ein.

## KI-Kennzeichnung

Erstellt mit Hermes Agent, Modell **gpt-6.1-sol**, Provider **ChatGPT or Codex Subscription (OpenAI)**, Datum **2026-10-29**. Auftrag: lauffähige Mininet-Erweiterung für RN Blatt07 mit r3, statischer A/B-Routenauswahl, Fehlersteuerung, unprivilegierten Tests und schrittweiser/zeilenweiser Erklärung; Originale unverändert lassen, nichts installieren, keine Commits oder Pushes. Die fünf Python-Dateien enthalten diese Kennzeichnung ebenfalls am Anfang.
