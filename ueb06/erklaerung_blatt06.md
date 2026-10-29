# Blatt06: Schritt für Schritt durch den eigenen Prüf- und Erweiterungscode

**KI-Kennzeichnung RN WS26:** Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29. Tatsächliche Anfrage: Erstelle nur Gesamttest, explizite Mininet-Test-Doubles, vollständige Einzelzeilenerklärung und Prüfbericht; prüfe bestehende Aufgaben, Originalgleichheit und echte vorhandene Messwerte, ohne Originale zu verändern.

## Lesereihenfolge und Herkunft der Nachweise

1. Zuerst [Routingaufgaben 6.1–6.3](erklaerung_routing.md) und [Subnetting, Dijkstra und Distance Vector 6.4–6.6](erklaerung_algorithmen.md) lesen. Diese beiden älteren Erklärungen bleiben unverändert.
2. Die [Erweiterungsantwort 6.7](ue6.7/antwort.md) begründet das gemeinsame LAN. Beide Clients haben verschiedene IPv4-Adressen im selben /24, teilen r1 als Gateway und benutzen dieselbe unveränderte TCP-Anwendung. s1 ist eine Layer-2-Bridge, kein zusätzlicher IP-Router.
3. `topology.py` beschreibt die Struktur; `start_erweitert.py` konfiguriert Adressen und Routen und öffnet die CLI. Nur dieser zweite Starter ist für die echte vorbereitete VM bestimmt.
4. `test_topology.py` führt die echten Python-Funktionen gegen ausdrücklich synthetische Mininet-API-Doubles aus. Es prüft gewünschte Aufrufe, nicht echte OVS-Ports, Kernelrouten, sysctl-Wirkung oder Verzögerung.
5. `verify_namespaces.py` hat dagegen reale Pakete mit echten Linux-Netzwerk-Namespaces und Linux-Bridge gemessen. Der bestehende Lauf [run01](nachweise/run01/results.json) wird hier nur gelesen und niemals erneut ausgeführt oder überschrieben. Er ist kein Mininet-/OVS-/xterm-Nachweis; TC-Verzögerung wurde nicht eingerichtet.
6. Der [Gesamttest](checks.py) startet alle ungefährlichen Aufgaben-/Testprogramme wirklich und prüft die vorhandenen Messdateien. Ausführung: `/usr/bin/python3 -B checks.py` im Blattverzeichnis; ohne sudo und ohne Installation. Vollständige Ergebnisse und offene VM-Prüfung: [Prüfbericht](pruefung.md).

**So liest man die Tabellen:** Jede Tabellenzeile erklärt genau eine physische, nichtleere Zeile der verlinkten Datei. Die Quelltextspalte enthält den exakten Text einschließlich Einrückung; HTML-Entities dienen nur der Markdown-Darstellung. `checks.py` vergleicht Nummern, vollständige Quelltexte und Reihenfolge maschinell mit den echten Dateien. Auch Header, Docstrings, Fortsetzungen und schließende Klammern sind enthalten. Diese Vollständigkeitsprüfung ersetzt nicht das fachliche Verständnis der Erklärung.

**Sicherheit und Grenzen des Messrunners:** Python mindestens 3.12 wegen `os.unshare`; zuerst äußerer frischer Netzwerk-Namespace, danach erst veth, Bridge, Routen und Forwarding. Nur Netzwerk-Namespaces werden getrennt, nicht etwa Hostname, Prozesssicht oder Dateisystem. Der bereits existierende `run01` darf nicht erneut angelegt werden. Die einfachen zusätzlichen Teilstring-Assertions des Runners werden im Gesamttest durch exakte Pingzähler, erfolgreiche Sequenzen und vollständige Echo-Bytesvergleiche ergänzt. Die Originalclient-Implementierung setzt bei ihren kleinen Labnachrichten ein vollständiges Echo pro `recv` voraus; TCP garantiert generell keine solchen Nachrichtengrenzen. Sie wurde auftragsgemäß nicht verändert. Die gespeicherten konkreten Antworten werden vollständig überprüft, keine allgemeine Framingkorrektheit behauptet.

## [verify_namespaces.py](verify_namespaces.py)

| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.</code> | Kennzeichnet den KI-Anteil mit Kurs, Werkzeug Hermes Agent, exaktem Modell OpenAI gpt-6.1-sol und Erstellungsdatum 2026-10-29. |
| 2 | <code># Anfrage: Prüfe Blatt06 mit echten isolierten Netzwerk-Namespaces, Routenlöschung und unverändertem TCP-Code.</code> | Dokumentiert die tatsächliche Teilanfrage als Quelltextkommentar; der Text wird nicht als Programm ausgeführt. |
| 3 | <code>&quot;&quot;&quot;Zusatznachweis, NICHT Mininet/OVS. sudo /usr/bin/python3 -B verify_namespaces.py</code> | Beginnt den Modul-Docstring: Dieser privilegierte Zusatznachweis ist ausdrücklich kein Mininet/OVS-Lauf; nennt den Startbefehl. |
| 5 | <code>Python &gt;=3.12; iproute2, ping, unshare, nsenter. Keine Installation.</code> | Dokumentiert Python mindestens 3.12 und die notwendigen vorhandenen Linux-Werkzeuge; installiert nichts. |
| 6 | <code>Alle Netzwerkänderungen erfolgen erst nach os.unshare(CLONE_NEWNET).</code> | Dokumentiert die zentrale Sicherheitsbedingung: Vor jeder Netzwerkänderung muss ein neuer äußerer Netzwerk-Namespace bestehen. |
| 7 | <code>&quot;&quot;&quot;</code> | Schließt den mehrzeiligen Modul-Docstring ab; seine Textzeilen sind keine Shellbefehle. |
| 8 | <code>import contextlib</code> | Lädt das Standardbibliotheksmodul für zeitlich begrenzte Standardausgabeumleitung als Kontextmanager. |
| 9 | <code>import importlib.util</code> | Lädt das Standardbibliotheksmodul für dynamische Modulimporte aus den ausdrücklich angegebenen lokalen Dateien. |
| 10 | <code>import io</code> | Lädt das Standardbibliotheksmodul für Textpuffer im Arbeitsspeicher für aufgefangene Programmausgaben. |
| 11 | <code>import json</code> | Lädt das Standardbibliotheksmodul für Lesen und Schreiben maschinenlesbarer echter Adress- und Ergebnisdaten. |
| 12 | <code>import os</code> | Lädt das Standardbibliotheksmodul für Prozessumgebung, Dateisystemcodierung beziehungsweise privilegierte Namespace-Systemaufrufe. |
| 13 | <code>from pathlib import Path</code> | Importiert Path für explizite, vom Arbeitsverzeichnis unabhängige Projektpfade und Dateizugriffe. |
| 14 | <code>import selectors</code> | Lädt das Standardbibliotheksmodul für ereignisbasierte Bereitschaftskontrolle der echten Serverausgabe. |
| 15 | <code>import subprocess</code> | Lädt das Standardbibliotheksmodul für tatsächliche externe Prozessstarts mit Ausgaben und Exitstatus. |
| 16 | <code>import time</code> | Lädt das Standardbibliotheksmodul für monotone Zeitlimits und kurze Bereitschaftspausen. |
| 18 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert alle Projektpfade am Verzeichnis dieses Skripts, unabhängig vom aktuellen Arbeitsverzeichnis. |
| 19 | <code>PYTHON = &quot;/usr/bin/python3&quot;</code> | Wählt den vorhandenen Systeminterpreter für die unveränderten TCP-Programme; dieser ist vom Hermes-Interpreter getrennt. |
| 22 | <code>def load(name, relative):</code> | Definiert das dynamische Laden eines Projektmoduls unter einem frei gewählten Modulnamen. |
| 23 | <code>    spec = importlib.util.spec_from_file_location(name, BASE / relative)</code> | Erzeugt die Importspezifikation für die Datei unter BASE, ohne deren __main__-Block auszuführen. |
| 24 | <code>    module = importlib.util.module_from_spec(spec)</code> | Erzeugt aus der Spezifikation ein neues Modulobjekt. |
| 25 | <code>    spec.loader.exec_module(module)</code> | Führt den Modulrumpf aus und stellt dessen Konstanten und Funktionen bereit. |
| 26 | <code>    return module</code> | Gibt das geladene Modul an die aufrufende Stelle zurück. |
| 29 | <code>def run(argv, **kwargs):</code> | Kapselt externe Befehle mit einheitlicher Ausgabeerfassung und Zeitbegrenzung. |
| 30 | <code>    return subprocess.run(argv, capture_output=True, text=True, timeout=20, **kwargs)</code> | Startet argv ohne Shell, erfasst stdout/stderr als Text und begrenzt den Aufruf auf 20 Sekunden; kwargs ergänzt Optionen. |
| 33 | <code>class Node:</code> | Definiert den Adapter für einen echten separaten Linux-Netzwerk-Namespace; dies ist kein Mininet-Test-Double. |
| 34 | <code>    def __init__(self, name):</code> | Konstruktor: Erzeugt und initialisiert einen Namespace-Halter für das übergebene Knotenlabel. |
| 35 | <code>        self.name = name</code> | Speichert das fachliche Knotenlabel für Fehlermeldungen. |
| 36 | <code>        original = os.readlink(&quot;/proc/self/ns/net&quot;)</code> | Liest den Namespace-Bezeichner des aktuellen Prozesses als Vergleichswert vor dem Start. |
| 37 | <code>        self.process = subprocess.Popen([&quot;unshare&quot;, &quot;--net&quot;, &quot;sleep&quot;, &quot;180&quot;])</code> | Startet einen auf 180 Sekunden begrenzten Halterprozess in einem neuen Netzwerk-Namespace. |
| 38 | <code>        deadline = time.monotonic() + 3</code> | Setzt mit monotoner Uhr ein dreisekündiges Bereitschaftslimit, unabhängig von Änderungen der Wanduhr. |
| 39 | <code>        try:</code> | Beginnt den geschützten Ausführungsbereich; die zugehörige Fehler- oder finally-Behandlung verhindert unkontrolliertes Weiterlaufen beziehungsweise fehlendes Aufräumen. |
| 40 | <code>            while os.readlink(f&quot;/proc/{self.process.pid}/ns/net&quot;) == original:</code> | Wartet, solange der Halter noch denselben Netzwerk-Namespace wie der Aufrufer besitzt. |
| 41 | <code>                if self.process.poll() is not None or time.monotonic() &gt;= deadline:</code> | Erkennt einen vorzeitig beendeten Halter oder das Überschreiten des Bereitschaftslimits. |
| 42 | <code>                    raise RuntimeError(&quot;Namespace nicht bereit&quot;)</code> | Bricht ab, statt eine möglicherweise noch nicht isolierte Netzkonfiguration fortzusetzen. |
| 43 | <code>                time.sleep(0.01)</code> | Wartet zehn Millisekunden bis zur nächsten Bereitschaftskontrolle. |
| 44 | <code>        except BaseException:</code> | Fängt auch Abbruchsignale als Python-Ausnahmen ab, damit der gerade gestartete Halter aufgeräumt wird. |
| 45 | <code>            self.close()</code> | Beendet bei fehlgeschlagener Initialisierung den Halter und wartet auf dessen Ende. |
| 46 | <code>            raise</code> | Wirft den ursprünglichen Fehler nach dem Aufräumen erneut. |
| 47 | <code>        self.checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, &quot;lo&quot;, &quot;up&quot;])</code> | Aktiviert ausschließlich im neuen Knotennamespace das Loopback-Interface; checked prüft den Exitstatus. |
| 49 | <code>    def prefix(self):</code> | Liefert den Befehlspräfix zum Betreten genau dieses Knotennamespace. |
| 50 | <code>        return [&quot;nsenter&quot;, &quot;-t&quot;, str(self.process.pid), &quot;-n&quot;]</code> | Baut nsenter mit Halter-PID und -n auf; andere Namespace-Arten werden nicht getrennt. |
| 52 | <code>    def pexec(self, argv):</code> | Führt ein Argumentlistenkommando im zugeordneten Netzwerk-Namespace aus. |
| 53 | <code>        result = run(self.prefix() + argv, env={**os.environ, &quot;LC_ALL&quot;: &quot;C&quot;})</code> | Verkettet nsenter und argv; LC_ALL=C stabilisiert die englischen Ping- und Werkzeugausgaben. |
| 54 | <code>        return result.stdout, result.stderr, result.returncode</code> | Gibt stdout, stderr und numerischen Exitstatus in der von den Routingtests erwarteten Reihenfolge zurück. |
| 56 | <code>    def checked(self, argv):</code> | Erweitert pexec um eine strenge Erfolgskontrolle für Befehle, die gelingen müssen. |
| 57 | <code>        out, err, status = self.pexec(argv)</code> | Zerlegt die tatsächliche Prozessrückgabe in Standardausgabe, Fehlerausgabe und Status. |
| 58 | <code>        if status:</code> | Prüft auf einen von null verschiedenen Exitstatus, nicht auf bloße Ausgabeteilstrings. |
| 59 | <code>            raise RuntimeError(f&quot;{self.name}: {argv}: {out}{err}&quot;)</code> | Meldet Knoten, Argumente und beide Ausgaben bei fehlgeschlagenem Befehl. |
| 60 | <code>        return out</code> | Gibt bei Erfolg ausschließlich stdout zurück. |
| 62 | <code>    def close(self):</code> | Definiert das kontrollierte Beenden des Namespace-Halters. |
| 63 | <code>        if self.process.poll() is None:</code> | Prüft, ob der Halter noch läuft, bevor ein Signal geschickt wird. |
| 64 | <code>            self.process.terminate()</code> | Fordert mit terminate das Ende des eigenen Halterprozesses an. |
| 65 | <code>        self.process.wait(timeout=5)</code> | Wartet höchstens fünf Sekunden und verhindert so einen liegenbleibenden unbeachteten Kindprozess. |
| 68 | <code>def checked(argv):</code> | Definiert die statusgeprüfte Befehlsausführung im bereits isolierten äußeren Namespace. |
| 69 | <code>    result = run(argv)</code> | Führt den externen Befehl über den gemeinsamen run-Adapter aus. |
| 70 | <code>    if result.returncode:</code> | Erkennt Fehler anhand des tatsächlichen Prozessstatus. |
| 71 | <code>        raise RuntimeError(result.stdout + result.stderr)</code> | Wirft einen Fehler mit erfasster Standard- und Fehlerausgabe. |
| 72 | <code>    return result.stdout</code> | Liefert bei Erfolg die Standardausgabe als Text. |
| 75 | <code>def link(a, aname, address_a, b, bname, address_b):</code> | Definiert eine Verbindung zwischen zwei Knotennamespaces oder zwischen Knoten und äußerer Linux-Bridge. |
| 76 | <code>    checked([&quot;ip&quot;, &quot;link&quot;, &quot;add&quot;, aname, &quot;type&quot;, &quot;veth&quot;, &quot;peer&quot;, &quot;name&quot;, bname])</code> | Erzeugt zunächst ein veth-Paar im äußeren isolierten Namespace; die beiden Namen identifizieren die Enden. |
| 77 | <code>    for node, name, address in ((a, aname, address_a), (b, bname, address_b)):</code> | Bearbeitet nacheinander beide Enden mit Knotenobjekt, Interfacename und optionaler Adresse. |
| 78 | <code>        if node:</code> | Unterscheidet ein echtes Knotenende von einem Bridge-Ende, dessen node None ist. |
| 79 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name, &quot;netns&quot;, str(node.process.pid)])</code> | Verschiebt das betreffende veth-Ende in den Netzwerk-Namespace seines Halterprozesses. |
| 80 | <code>            if address:</code> | Konfiguriert eine IPv4-Adresse nur, wenn das Ende eine Adresse erhalten soll. |
| 81 | <code>                node.checked([&quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, address, &quot;dev&quot;, name])</code> | Vergibt die übergebene Adresse einschließlich Präfix am ausdrücklich benannten Interface. |
| 82 | <code>            node.checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name, &quot;up&quot;])</code> | Aktiviert das Interface innerhalb seines Knotennamespace. |
| 83 | <code>        else:</code> | Beginnt den Zweig für ein nicht adressiertes äußeres Bridge-Ende. |
| 84 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name, &quot;master&quot;, &quot;s1&quot;])</code> | Hängt dieses Ende als Port an die im äußeren Namespace angelegte Linux-Bridge s1. |
| 85 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name, &quot;up&quot;])</code> | Aktiviert den Bridge-Port; dies konfiguriert keine Open-vSwitch-Bridge. |
| 88 | <code>def ready(process):</code> | Definiert die Bereitschaftskontrolle für den tatsächlichen TCP-Serverprozess. |
| 89 | <code>    with selectors.DefaultSelector() as selector:</code> | Öffnet einen Selector als Kontextmanager und schließt ihn auch bei Fehlern wieder. |
| 90 | <code>        selector.register(process.stdout, selectors.EVENT_READ)</code> | Überwacht stdout des Serverprozesses auf Lesebereitschaft, ohne eine feste Startpause zu erraten. |
| 91 | <code>        if not selector.select(5):</code> | Wartet höchstens fünf Sekunden auf eine Serverausgabe. |
| 92 | <code>            raise RuntimeError(&quot;TCP-Server wurde nicht bereit&quot;)</code> | Bricht ab, wenn innerhalb des Limits keine Bereitschaftsausgabe eintrifft. |
| 93 | <code>        line = process.stdout.readline()</code> | Liest die erste verfügbare Serverzeile; -u beim Start verhindert Python-Ausgabepufferung. |
| 94 | <code>    if &quot;Listening on 10.0.2.2:5000&quot; not in line:</code> | Prüft die unveränderte originale Bereitschaftsmeldung mit Zieladresse und TCP-Port. |
| 95 | <code>        raise RuntimeError(line)</code> | Meldet unerwartete erste Serverausgaben als Fehler statt sie als Bereitschaft zu behandeln. |
| 96 | <code>    return line</code> | Gibt die erste Serverzeile zurück, damit sie später im vollständigen Nachweis erhalten bleibt. |
| 99 | <code>def scenario(extended, output):</code> | Definiert einen vollständigen Basis- oder Erweiterungsversuch mit eigenem Satz Knotennamespaces. |
| 100 | <code>    nodes = {}</code> | Initialisiert das Knotenregister, damit auch ein teilweise gestarteter Versuch aufgeräumt werden kann. |
| 101 | <code>    server = None</code> | Markiert, dass noch kein TCP-Serverprozess gestartet wurde. |
| 102 | <code>    try:</code> | Beginnt den geschützten Ausführungsbereich; die zugehörige Fehler- oder finally-Behandlung verhindert unkontrolliertes Weiterlaufen beziehungsweise fehlendes Aufräumen. |
| 103 | <code>        for name in (&quot;client&quot;, &quot;r1&quot;, &quot;r2&quot;, &quot;server&quot;) + ((&quot;client2&quot;,) if extended else ()):</code> | Durchläuft die vier Basisknoten und ergänzt client2 ausschließlich im erweiterten Fall. |
| 104 | <code>            nodes[name] = Node(name)</code> | Erzeugt pro Knoten einen echten separaten Linux-Netzwerk-Namespace und registriert ihn. |
| 105 | <code>        c, r1, r2, s = (nodes[x] for x in (&quot;client&quot;, &quot;r1&quot;, &quot;r2&quot;, &quot;server&quot;))</code> | Ordnet die vier Basisobjekte kurzen lokalen Variablen in festgelegter Reihenfolge zu. |
| 106 | <code>        if extended:</code> | Wählt für den erweiterten Versuch das gemeinsame linke Ethernet-LAN. |
| 107 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;add&quot;, &quot;s1&quot;, &quot;type&quot;, &quot;bridge&quot;])</code> | Erzeugt eine Linux-Bridge s1 im äußeren bereits isolierten Netzwerk-Namespace. |
| 108 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, &quot;s1&quot;, &quot;up&quot;])</code> | Aktiviert die Linux-Bridge, bevor die Ports angeschlossen werden. |
| 109 | <code>            for node, interface, address, peer in ((c, &quot;client-eth0&quot;, &quot;10.0.1.2/24&quot;, &quot;s1-eth1&quot;),</code> | Beginnt die Liste der Bridge-Anschlüsse mit client und seiner unveränderten Adresse 10.0.1.2/24. |
| 110 | <code>                    (nodes[&quot;client2&quot;], &quot;client2-eth0&quot;, &quot;10.0.1.3/24&quot;, &quot;s1-eth2&quot;),</code> | Ergänzt client2 mit eigener Adresse 10.0.1.3/24 und eigenem Bridge-Port. |
| 111 | <code>                    (r1, &quot;r1-eth0&quot;, &quot;10.0.1.1/24&quot;, &quot;s1-eth3&quot;)):</code> | Schließt die Anschlussliste mit r1s LAN-Interface 10.0.1.1/24; alle drei teilen ein IP-Netz. |
| 112 | <code>                link(node, interface, address, None, peer, None)</code> | Erzeugt für jeden LAN-Anschluss ein veth-Paar zwischen Knoten und Bridge. |
| 113 | <code>        else:</code> | Beginnt den Basisfall ohne Switch und ohne zweiten Client. |
| 114 | <code>            link(c, &quot;client-eth0&quot;, &quot;10.0.1.2/24&quot;, r1, &quot;r1-eth0&quot;, &quot;10.0.1.1/24&quot;)</code> | Verbindet client unmittelbar mit r1 und vergibt die beiden vorgegebenen /24-Adressen. |
| 115 | <code>        link(r1, &quot;r1-eth1&quot;, &quot;10.0.12.1/30&quot;, r2, &quot;r2-eth0&quot;, &quot;10.0.12.2/30&quot;)</code> | Verbindet die Router über das /30-Transitnetz 10.0.12.0/30. |
| 116 | <code>        link(r2, &quot;r2-eth1&quot;, &quot;10.0.2.1/24&quot;, s, &quot;server-eth0&quot;, &quot;10.0.2.2/24&quot;)</code> | Verbindet r2 und server im unveränderten Server-LAN 10.0.2.0/24. |
| 117 | <code>        for name, gateway in ((&quot;client&quot;, &quot;10.0.1.1&quot;), (&quot;server&quot;, &quot;10.0.2.1&quot;)) + (((&quot;client2&quot;, &quot;10.0.1.1&quot;),) if extended else ()):</code> | Durchläuft die Endhost-Gateways und ergänzt bei Erweiterung client2 mit demselben lokalen r1-Gateway. |
| 118 | <code>            nodes[name].checked([&quot;ip&quot;, &quot;route&quot;, &quot;add&quot;, &quot;default&quot;, &quot;via&quot;, gateway])</code> | Setzt pro Endhost eine Default Route zum jeweiligen LAN-Router. |
| 119 | <code>        routes = load(&quot;static_routes&quot;, &quot;ue6.3/static_routes.py&quot;)</code> | Lädt die vorhandene Routingübung, damit deren echte Lösch-/Wiederherstellungslogik erneut verwendet wird. |
| 120 | <code>        for router in (r1, r2):</code> | Bearbeitet die beiden echten Router-Knotennamespaces. |
| 121 | <code>            router.checked([&quot;sysctl&quot;, &quot;-w&quot;, &quot;net.ipv4.ip_forward=1&quot;])</code> | Aktiviert IPv4-Forwarding ausschließlich im jeweiligen Router-Namespace. |
| 122 | <code>            network, gateway, interface, _ = routes.ROUTES[router.name]</code> | Liest Zielnetz, Next Hop und Ausgangsinterface aus den bereits implementierten statischen Routen. |
| 123 | <code>            router.checked([&quot;ip&quot;, &quot;route&quot;, &quot;add&quot;, network, &quot;via&quot;, gateway, &quot;dev&quot;, interface])</code> | Installiert die eine explizite Route zum jeweils entfernten LAN. |
| 124 | <code>        tag = &quot;erweitert&quot; if extended else &quot;basis&quot;</code> | Wählt einen eindeutigen Dateipräfix für Basis- und Erweiterungsdaten. |
| 125 | <code>        output.mkdir(parents=True, exist_ok=True)</code> | Legt das Nachweisverzeichnis an; die globale main-Sperre verhindert das Überschreiben eines früheren run01. |
| 126 | <code>        for name, node in nodes.items():</code> | Durchläuft alle gerade erzeugten Knoten zum Sichern der tatsächlichen Interface- und Routenzustände. |
| 127 | <code>            report = &quot;$ ip -br addr\n&quot; + node.checked([&quot;ip&quot;, &quot;-br&quot;, &quot;addr&quot;])</code> | Beginnt den Textnachweis mit Kommandoangabe und echter kompakter Interfaceausgabe. |
| 128 | <code>            report += &quot;$ ip addr\n&quot; + node.checked([&quot;ip&quot;, &quot;addr&quot;])</code> | Ergänzt die vollständige Ausgabe von ip addr. |
| 129 | <code>            report += &quot;$ bash Angabe/inspect_network.sh\n&quot; + node.checked([&quot;bash&quot;, str(BASE / &quot;Angabe/inspect_network.sh&quot;)])</code> | Führt das unveränderte Original-Inspektionsskript im Knoten aus und ergänzt dessen Ausgabe. |
| 130 | <code>            (output / f&quot;{tag}-{name}.txt&quot;).write_text(report)</code> | Schreibt den knotenspezifischen Textnachweis mit fallbezogenem Dateinamen. |
| 131 | <code>            raw = node.checked([&quot;ip&quot;, &quot;-j&quot;, &quot;addr&quot;])</code> | Fragt die tatsächlichen Adressen zusätzlich im maschinenlesbaren ip-JSON-Format ab. |
| 132 | <code>            (output / f&quot;{tag}-{name}-addr.json&quot;).write_text(raw)</code> | Speichert die rohe JSON-Ausgabe ohne erfundene Messdaten. |
| 133 | <code>            for interface in json.loads(raw):</code> | Parst die gerade erfasste JSON-Ausgabe und durchläuft deren Interfaces. |
| 134 | <code>                for item in interface.get(&quot;addr_info&quot;, []):</code> | Durchläuft die vorhandenen Adresseinträge; fehlendes addr_info wird als leere Liste behandelt. |
| 135 | <code>                    if item[&quot;family&quot;] == &quot;inet&quot; and interface[&quot;ifname&quot;] != &quot;lo&quot;:</code> | Wählt IPv4-Adressen auf Dateninterfaces und lässt Loopback sowie IPv6 für diesen Sollvergleich aus. |
| 136 | <code>                        expected = {&quot;client-eth0&quot;: &quot;10.0.1.2&quot;, &quot;client2-eth0&quot;: &quot;10.0.1.3&quot;, &quot;r1-eth0&quot;: &quot;10.0.1.1&quot;, &quot;r1-eth1&quot;: &quot;10.0.12.1&quot;, &quot;r2-eth0&quot;: &quot;10.0.12.2&quot;, &quot;r2-eth1&quot;: &quot;10.0.2.1&quot;, &quot;server-eth0&quot;: &quot;10.0.2.2&quot;}</code> | Definiert die exakte erwartete IPv4-Adresse jedes benannten Dateninterfaces. |
| 137 | <code>                        assert item[&quot;local&quot;] == expected[interface[&quot;ifname&quot;]]</code> | Vergleicht die gemessene Adresse mit dem zum Interface gehörenden Sollwert; checks.py kontrolliert zusätzlich Präfixe und Vollständigkeit. |
| 138 | <code>        buffer = io.StringIO()</code> | Erzeugt einen Textpuffer für die dokumentierten Routingkommandos und Pings. |
| 139 | <code>        with contextlib.redirect_stdout(buffer):</code> | Lenkt ausschließlich die Python-Standardausgabe der nachfolgenden Routingaufrufe in diesen Puffer um. |
| 140 | <code>            routes.ping3(c)</code> | Prüft zunächst drei echte Client-Server-Pings bei vollständig vorhandenen Routen. |
| 141 | <code>            routes.exercise(nodes)</code> | Löscht und restauriert die Routen mit der vorhandenen Übung; erwartet 0/3 ohne und 3/3 nach Wiederherstellung. |
| 142 | <code>        (output / f&quot;{tag}-routen-und-ping.txt&quot;).write_text(buffer.getvalue())</code> | Speichert den vollständigen Routingdialog einschließlich Exitstatus und Pingstatistiken. |
| 143 | <code>        targets = [(s, &quot;10.0.1.2&quot;)]</code> | Beginnt die zusätzlichen positiven Verbindungsprüfungen mit server nach client. |
| 144 | <code>        if extended:</code> | Ergänzt nur beim erweiterten Netz weitere Testziele. |
| 145 | <code>            targets.extend([(nodes[&quot;client2&quot;], &quot;10.0.1.2&quot;), (s, &quot;10.0.1.3&quot;)])</code> | Testet client2 nach client im selben LAN sowie server nach client2 über beide Router. |
| 146 | <code>        for source, target in targets:</code> | Durchläuft diese Quelle-Ziel-Paare mit den echten Namespace-Knoten. |
| 147 | <code>            result = source.checked([&quot;ping&quot;, &quot;-c&quot;, &quot;3&quot;, &quot;-W&quot;, &quot;2&quot;, target])</code> | Sendet genau drei Pingproben mit je zwei Sekunden Antwortwartezeit; checked verlangt Status null. |
| 148 | <code>            assert &quot;3 received&quot; in result</code> | Prüft zusätzlich den Empfangsteilstring; die strengere nachträgliche Auswertung in checks.py verlangt exakte Zahlen und Sequenzen. |
| 149 | <code>            (output / f&quot;{tag}-{source.name}-ping-{target}.txt&quot;).write_text(result)</code> | Speichert jede zusätzliche reale Pingausgabe in einer eigenen eindeutig benannten Datei. |
| 150 | <code>        server = subprocess.Popen(s.prefix() + [PYTHON, &quot;-u&quot;, &quot;-B&quot;, str(BASE / &quot;Angabe/tcp_server.py&quot;)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)</code> | Startet den unveränderten TCP-Server im Servernamespace mit ungepufferter Ausgabe und erfasst stdout sowie stderr gemeinsam. |
| 151 | <code>        server_start = ready(server)</code> | Wartet ereignisbasiert auf dessen Listening-Meldung und bewahrt die erste Zeile auf. |
| 152 | <code>        for name in (&quot;client&quot;, &quot;client2&quot;) if extended else (&quot;client&quot;,):</code> | Lässt im Basisnetz client und im erweiterten Netz beide Clients nacheinander den Originalclient starten. |
| 153 | <code>            result = nodes[name].checked([PYTHON, &quot;-B&quot;, str(BASE / &quot;Angabe/tcp_client.py&quot;)])</code> | Führt jeweils die unveränderte TCP-Clientdatei im passenden Netzwerk-Namespace aus. |
| 154 | <code>            assert result.count(&quot;Reply:&quot;) == 3</code> | Verlangt genau drei Reply-Markierungen in der tatsächlichen Clientausgabe. |
| 155 | <code>            for number in (1, 2, 3):</code> | Durchläuft die drei erwarteten Nachrichtennummern des Originalprogramms. |
| 156 | <code>                assert f&quot;Reply: b&#x27;Network layer test {number}\\n&#x27;&quot; in result</code> | Prüft die erwartete Bytes-Darstellung jedes Echo-Inhalts einschließlich Newline; checks.py vergleicht später die kompletten Byteslisten. |
| 157 | <code>            (output / f&quot;{tag}-{name}-tcp.txt&quot;).write_text(result)</code> | Speichert die vollständige Ausgabe des jeweiligen echten TCP-Clientprozesses. |
| 158 | <code>        server.terminate()</code> | Beendet den eigenen TCP-Server nach den abgeschlossenen Clientversuchen. |
| 159 | <code>        rest, _ = server.communicate(timeout=5)</code> | Liest die verbleibende Serverausgabe und wartet höchstens fünf Sekunden auf Prozessende. |
| 160 | <code>        (output / f&quot;{tag}-server-tcp.txt&quot;).write_text(server_start + rest)</code> | Schreibt den Servernachweis einschließlich der zuvor abgefangenen Listening-Zeile. |
| 161 | <code>        assert rest.count(&quot;Connection from&quot;) == (2 if extended else 1)</code> | Verlangt genau eine Verbindung im Basisfall beziehungsweise zwei im erweiterten Fall. |
| 162 | <code>        return {&quot;fall&quot;: tag, &quot;routing&quot;: &quot;3/3 vor und nach Wiederherstellung; 0/3 ohne Routen&quot;, &quot;tcp_clients&quot;: [&quot;client&quot;, &quot;client2&quot;] if extended else [&quot;client&quot;], &quot;messung&quot;: &quot;Linux-Network-Namespaces, Linux-Bridge; NICHT Mininet/OVS; keine TC-Verzögerung&quot;}</code> | Liefert die Ergebniszusammenfassung mit ausdrücklicher Abgrenzung: echte Linux-Namespaces und Linux-Bridge, nicht Mininet/OVS oder TC-Verzögerung. |
| 163 | <code>    finally:</code> | Beginnt den Aufräumpfad, der sowohl nach normalem Ende als auch nach einer Ausnahme ausgeführt wird. |
| 164 | <code>        if server and server.poll() is None:</code> | Prüft im Aufräumpfad, ob ein Serverprozess existiert und noch läuft. |
| 165 | <code>            server.terminate()</code> | Fordert bei vorzeitigem Versuchsabbruch ebenfalls dessen Beendigung an. |
| 166 | <code>            server.wait(timeout=5)</code> | Wartet begrenzt auf das tatsächliche Ende des Serverprozesses. |
| 167 | <code>        for node in reversed(list(nodes.values())):</code> | Räumt alle angelegten Knoten in umgekehrter Erzeugungsreihenfolge auf. |
| 168 | <code>            node.close()</code> | Beendet den jeweiligen Namespace-Halter und wartet auf ihn. |
| 169 | <code>        if extended:</code> | Entfernt im erweiterten Fall auch die selbst angelegte äußere Bridge. |
| 170 | <code>            checked([&quot;ip&quot;, &quot;link&quot;, &quot;del&quot;, &quot;s1&quot;])</code> | Löscht s1 ausschließlich im isolierten äußeren Namespace, nicht im Hostnetz. |
| 173 | <code>def main():</code> | Definiert den privilegierten Einstieg; ein Import des Moduls führt keine Netzwerkänderungen aus. |
| 174 | <code>    if os.geteuid() != 0:</code> | Prüft die effektive Benutzerkennung vor dem Versuch, Netzwerknamespaces anzulegen. |
| 175 | <code>        raise SystemExit(&quot;Nur für isolierte Zusatztests: sudo /usr/bin/python3 -B verify_namespaces.py&quot;)</code> | Bricht ohne Rootrechte mit einem expliziten Startbeispiel ab. |
| 176 | <code>    os.unshare(os.CLONE_NEWNET)</code> | Erzeugt zuerst einen frischen äußeren Netzwerk-Namespace; bei Fehlschlag erfolgt keine Topologieänderung. |
| 177 | <code>    output = BASE / &quot;nachweise/run01&quot;</code> | Bestimmt den festen Nachweispfad run01 für diesen einzigen Messlauf. |
| 178 | <code>    if output.exists():</code> | Prüft vor dem Versuch, ob bereits ein Nachweisverzeichnis existiert. |
| 179 | <code>        raise SystemExit(&quot;run01 existiert bereits; nicht mit anderem Messlauf mischen&quot;)</code> | Verhindert das Überschreiben oder Vermischen bereits vorhandener Messwerte. |
| 180 | <code>    results = [scenario(False, output), scenario(True, output)]</code> | Führt Basis- und Erweiterungsversuch tatsächlich nacheinander aus und sammelt ihre Ergebnisobjekte. |
| 181 | <code>    (output / &quot;results.json&quot;).write_text(json.dumps(results, ensure_ascii=False, indent=2) + &quot;\n&quot;)</code> | Speichert die Zusammenfassung als UTF-8-lesbares, eingerücktes JSON mit abschließendem Zeilenumbruch. |
| 182 | <code>    print(json.dumps(results, ensure_ascii=False, indent=2))</code> | Gibt dieselbe Ergebniszusammenfassung an das aufrufende Terminal aus. |
| 185 | <code>if __name__ == &quot;__main__&quot;:</code> | Beschränkt den nachfolgenden Programmeinstieg auf direkten Skriptstart; ein Import allein führt ihn nicht aus. |
| 186 | <code>    main()</code> | Startet main ausschließlich beim direkten Skriptaufruf; beim jetzigen Gesamttest wird dieser Messlauf nicht erneut gestartet. |

## [ue6.7/topology.py](ue6.7/topology.py)

| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.</code> | Kennzeichnet den KI-Anteil mit Kurs, Werkzeug Hermes Agent, exaktem Modell OpenAI gpt-6.1-sol und Erstellungsdatum 2026-10-29. |
| 2 | <code># Anfrage: Erweitere RN-Blatt 6.7 um client2, mit gemeinsamem LAN, unveränderten TCP-Programmen.</code> | Dokumentiert die tatsächliche Teilanfrage als Quelltextkommentar; der Text wird nicht als Programm ausgeführt. |
| 3 | <code>&quot;&quot;&quot;Erweiterte Arbeitskopie: client und client2 teilen über s1 das linke LAN.&quot;&quot;&quot;</code> | Beschreibt die Erweiterung: Beide Clients teilen dasselbe linke LAN über s1; die Originalvorlage bleibt separat unverändert. |
| 4 | <code>from mininet.topo import Topo</code> | Importiert die genannte Mininet-API; im API-Test kommt sie ausdrücklich aus Test-Doubles, im echten Starter erst aus der vorbereiteten VM. |
| 5 | <code>from mininet.node import Host, Node, OVSBridge</code> | Importiert die genannte Mininet-API; im API-Test kommt sie ausdrücklich aus Test-Doubles, im echten Starter erst aus der vorbereiteten VM. |
| 6 | <code>from mininet.link import TCLink</code> | Importiert die genannte Mininet-API; im API-Test kommt sie ausdrücklich aus Test-Doubles, im echten Starter erst aus der vorbereiteten VM. |
| 8 | <code>LINK_DELAY = &quot;10ms&quot;</code> | Definiert die an alle TCLinks weitergegebene nominelle Verzögerung von zehn Millisekunden. |
| 11 | <code>class LinuxRouter(Node):</code> | Leitet einen Linuxrouter von Mininets Node-Klasse ab; erst der echte VM-Lauf würde Kernelwirkungen belegen. |
| 12 | <code>    def config(self, **params):</code> | Überschreibt die Mininet-Konfiguration und akzeptiert beliebige benannte Parameter. |
| 13 | <code>        super().config(**params)</code> | Führt zuerst die geerbte Knotenkonfiguration mit unveränderten Parametern aus. |
| 14 | <code>        self.cmd(&quot;sysctl -w net.ipv4.ip_forward=1 &gt;/dev/null&quot;)</code> | Aktiviert danach IPv4-Forwarding im Routernamespace; die Umleitung unterdrückt nur die normale sysctl-Ausgabe. |
| 16 | <code>    def terminate(self):</code> | Überschreibt das Beenden eines Routerknotens für den geordneten Forwarding-Rückbau. |
| 17 | <code>        self.cmd(&quot;sysctl -w net.ipv4.ip_forward=0 &gt;/dev/null&quot;)</code> | Schaltet IPv4-Forwarding vor dem Aufräumen des Routerknotens aus. |
| 18 | <code>        super().terminate()</code> | Ruft anschließend die geerbte Aufräumfunktion auf. |
| 21 | <code>class RoutingTopo(Topo):</code> | Definiert die erweiterte Topologie als Unterklasse der Mininet-Topo-API. |
| 22 | <code>    def build(self):</code> | Beschreibt Hosts, Switch und Links; die IP-Konfiguration erfolgt im Starter, nicht hier. |
| 23 | <code>        client = self.addHost(&quot;client&quot;, cls=Host)</code> | Erzeugt den bestehenden Client ausdrücklich als normalen Host, nicht als Router. |
| 24 | <code>        client2 = self.addHost(&quot;client2&quot;, cls=Host)</code> | Erzeugt client2 als zusätzlichen normalen Host im gleichen linken LAN. |
| 25 | <code>        r1 = self.addHost(&quot;r1&quot;, cls=LinuxRouter)</code> | Erzeugt r1 mit der selbst definierten forwardenden Routerklasse. |
| 26 | <code>        r2 = self.addHost(&quot;r2&quot;, cls=LinuxRouter)</code> | Erzeugt r2 ebenfalls mit der Routerklasse. |
| 27 | <code>        server = self.addHost(&quot;server&quot;, cls=Host)</code> | Erzeugt den unveränderten Server als normalen Host. |
| 28 | <code>        switch = self.addSwitch(&quot;s1&quot;, cls=OVSBridge)</code> | Erzeugt s1 als OVSBridge: Die Layer-2-Bridge benötigt keinen OpenFlow-Controller. |
| 29 | <code>        self.addLink(client, switch, intfName1=&quot;client-eth0&quot;, intfName2=&quot;s1-eth1&quot;, cls=TCLink, delay=LINK_DELAY)</code> | Verbindet client-eth0 mit s1-eth1 über einen TCLink mit der vorgegebenen Verzögerung. |
| 30 | <code>        self.addLink(client2, switch, intfName1=&quot;client2-eth0&quot;, intfName2=&quot;s1-eth2&quot;, cls=TCLink, delay=LINK_DELAY)</code> | Verbindet client2-eth0 mit eigenem Bridge-Port s1-eth2, statt ein zweites überlappendes Router-LAN zu erzeugen. |
| 31 | <code>        self.addLink(switch, r1, intfName1=&quot;s1-eth3&quot;, intfName2=&quot;r1-eth0&quot;, cls=TCLink, delay=LINK_DELAY)</code> | Verbindet s1-eth3 mit r1-eth0; so bleibt r1s bestehende LAN-Adressierung nutzbar. |
| 32 | <code>        self.addLink(r1, r2, intfName1=&quot;r1-eth1&quot;, intfName2=&quot;r2-eth0&quot;, cls=TCLink, delay=LINK_DELAY)</code> | Erhält die Transitverbindung r1-eth1 zu r2-eth0 samt TCLink-Parametern. |
| 33 | <code>        self.addLink(r2, server, intfName1=&quot;r2-eth1&quot;, intfName2=&quot;server-eth0&quot;, cls=TCLink, delay=LINK_DELAY)</code> | Erhält den Link von r2-eth1 zu server-eth0. |
| 36 | <code>topos = {&quot;routingtopo&quot;: RoutingTopo}</code> | Registriert den Topologienamen routingtopo für die Mininet-Custom-Topo-Schnittstelle. |

## [ue6.7/start_erweitert.py](ue6.7/start_erweitert.py)

| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.</code> | Kennzeichnet den KI-Anteil mit Kurs, Werkzeug Hermes Agent, exaktem Modell OpenAI gpt-6.1-sol und Erstellungsdatum 2026-10-29. |
| 2 | <code># Anfrage: Starte die erweiterte Topologie, ohne den Originalstarter oder TCP-Code zu ändern.</code> | Dokumentiert die tatsächliche Teilanfrage als Quelltextkommentar; der Text wird nicht als Programm ausgeführt. |
| 3 | <code>&quot;&quot;&quot;In der vorbereiteten Mininet/OVS-VM: sudo python3 -B start_erweitert.py.&quot;&quot;&quot;</code> | Nennt den echten VM-Startbefehl; dieser Starter ist hier nur mit expliziten API-Test-Doubles geprüft. |
| 4 | <code>from pathlib import Path</code> | Importiert Path für explizite, vom Arbeitsverzeichnis unabhängige Projektpfade und Dateizugriffe. |
| 5 | <code>import importlib.util</code> | Lädt das Standardbibliotheksmodul für dynamische Modulimporte aus den ausdrücklich angegebenen lokalen Dateien. |
| 6 | <code>import re</code> | Lädt das Standardbibliotheksmodul für reguläre Ausdrücke für exakte Pingzähler, Linkziele oder Erklärungszeilen. |
| 7 | <code>import sys</code> | Lädt das Standardbibliotheksmodul für aktuellen Interpreter und Modulregister; dies installiert keine Bibliotheken. |
| 9 | <code>from mininet.cli import CLI</code> | Importiert die genannte Mininet-API; im API-Test kommt sie ausdrücklich aus Test-Doubles, im echten Starter erst aus der vorbereiteten VM. |
| 10 | <code>from mininet.net import Mininet</code> | Importiert die genannte Mininet-API; im API-Test kommt sie ausdrücklich aus Test-Doubles, im echten Starter erst aus der vorbereiteten VM. |
| 11 | <code>from topology import RoutingTopo</code> | Importiert die eigene erweiterte RoutingTopo; sie ersetzt nicht die separat aufbewahrte Originalvorlage unter Angabe. |
| 13 | <code>BASE = Path(__file__).resolve().parents[1]</code> | Bestimmt das Blattverzeichnis oberhalb von ue6.7 als Basis für die unangetastete Originalinfrastruktur. |
| 14 | <code>spec = importlib.util.spec_from_file_location(&quot;original_start_lab&quot;, BASE / &quot;Angabe/start_lab.py&quot;)</code> | Erstellt eine separate Importspezifikation für Angabe/start_lab.py; die Originaldatei wird nicht kopiert oder geändert. |
| 15 | <code>original = importlib.util.module_from_spec(spec)</code> | Erzeugt das Modulobjekt für den Originalstarter. |
| 16 | <code>spec.loader.exec_module(original)</code> | Führt den Original-Modulrumpf aus, aber nicht dessen __main__-Einstieg; dadurch sind dessen Konfigurationsfunktionen wiederverwendbar. |
| 19 | <code>def ping_ok(node, target):</code> | Definiert die strengere Pingprüfung für genau drei erfolgreiche Proben. |
| 20 | <code>    out, err, code = node.pexec([&quot;ping&quot;, &quot;-c&quot;, &quot;3&quot;, &quot;-W&quot;, &quot;2&quot;, target], env={&quot;LC_ALL&quot;: &quot;C&quot;, &quot;PATH&quot;: &quot;/usr/bin:/bin:/usr/sbin:/sbin&quot;})</code> | Startet ping als Argumentliste mit drei Proben und zwei Sekunden Wartezeit; setzt englische Sprache und einen expliziten Werkzeug-PATH. |
| 21 | <code>    counts = re.search(r&quot;(\d+) packets transmitted, (\d+) (?:packets )?received&quot;, out)</code> | Parst gesendete und empfangene Paketanzahl; akzeptiert sowohl received als auch packets received. |
| 22 | <code>    if code != 0 or not counts or counts.groups() != (&quot;3&quot;, &quot;3&quot;):</code> | Verlangt gleichzeitig Exitstatus null, vorhandene Statistik und exakt das Zahlenpaar 3/3; ein 100%-Verlust kann nicht durch einen 0%-Teilstring bestehen. |
| 23 | <code>        raise RuntimeError(out + err)</code> | Bricht bei Abweichung mit beiden erfassten Prozessausgaben ab. |
| 24 | <code>    print(out)</code> | Druckt die tatsächliche Pingausgabe erst nach erfolgreicher Prüfung. |
| 27 | <code>def main():</code> | Definiert den Starter mit erweitertem Netz, Adressierung, strengen Pings und echter Mininet-CLI. |
| 28 | <code>    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True)</code> | Erzeugt Mininet mit der erweiterten Topologie, ohne Controller und mit automatischen MAC-Adressen. |
| 29 | <code>    try:</code> | Beginnt den geschützten Ausführungsbereich; die zugehörige Fehler- oder finally-Behandlung verhindert unkontrolliertes Weiterlaufen beziehungsweise fehlendes Aufräumen. |
| 30 | <code>        net.start()</code> | Startet die Netzinstanz innerhalb des geschützten Aufräumbereichs. |
| 31 | <code>        original.configure_base_network(net)</code> | Wendet die originale explizite Basiskonfiguration auf client, r1, r2 und server an. |
| 32 | <code>        original.set_interface(net[&quot;client2&quot;], &quot;client2-eth0&quot;, &quot;10.0.1.3/24&quot;)</code> | Nutzt den Originalhelfer zum Leeren, Adressieren und Aktivieren von client2-eth0 mit 10.0.1.3/24. |
| 33 | <code>        out, err, code = net[&quot;client2&quot;].pexec([&quot;ip&quot;, &quot;route&quot;, &quot;replace&quot;, &quot;default&quot;, &quot;via&quot;, &quot;10.0.1.1&quot;, &quot;dev&quot;, &quot;client2-eth0&quot;])</code> | Installiert client2s Default Route über das bestehende r1-LAN-Gateway; pexec liefert einen prüfbaren Status. |
| 34 | <code>        if code:</code> | Kontrolliert den Status der zusätzlichen Default Route. |
| 35 | <code>            raise RuntimeError(out + err)</code> | Bricht bei Routingkonfigurationsfehler mit stdout und stderr ab. |
| 36 | <code>        original.show_state(net)</code> | Zeigt den Original-Basiszustand an; dessen Topologieüberschrift beschreibt nur die ursprünglichen vier Knoten. |
| 37 | <code>        print(net[&quot;client2&quot;].cmd(&quot;ip -br addr; ip route&quot;))</code> | Ergänzt ausdrücklich client2s Interface- und Routingausgabe, die der Originalanzeige fehlt. |
| 38 | <code>        for source, target in ((&quot;client&quot;, &quot;10.0.2.2&quot;), (&quot;client2&quot;, &quot;10.0.2.2&quot;), (&quot;server&quot;, &quot;10.0.1.3&quot;)):</code> | Legt drei gerichtete Prüfungen fest: beide Clients zum Server sowie Server zum zweiten Client. |
| 39 | <code>            ping_ok(net[source], target)</code> | Prüft jedes Paar mit der strikten 3/3-Pingfunktion. |
| 40 | <code>        CLI(net)</code> | Öffnet eine tatsächliche Mininet-CLI, anders als der reine ENTER-Wartedialog des Originalstarters. |
| 41 | <code>    finally:</code> | Beginnt den Aufräumpfad, der sowohl nach normalem Ende als auch nach einer Ausnahme ausgeführt wird. |
| 42 | <code>        net.stop()</code> | Stoppt das eigene Netz auch bei Start-, Konfigurations-, Ping- oder CLI-Fehlern. |
| 45 | <code>if __name__ == &quot;__main__&quot;:</code> | Beschränkt den nachfolgenden Programmeinstieg auf direkten Skriptstart; ein Import allein führt ihn nicht aus. |
| 46 | <code>    main()</code> | Ruft den Starter nur bei direkter Ausführung auf; Importieren allein startet kein Netz. |

## [ue6.7/test_topology.py](ue6.7/test_topology.py)

| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.</code> | Kennzeichnet den KI-Anteil mit Kurs, Werkzeug Hermes Agent, exaktem Modell OpenAI gpt-6.1-sol und Erstellungsdatum 2026-10-29. |
| 2 | <code># Tatsächliche Anfrage: Erstelle explizite Mininet-Test-Doubles für Struktur, Schnittstellen,</code> | Dokumentiert die tatsächliche Teilanfrage als Quelltextkommentar; der Text wird nicht als Programm ausgeführt. |
| 3 | <code># OVSBridge, Routerforwarding und Starter mit robusten Ping-Zählern; teste ohne Installation.</code> | Setzt den tatsächlichen Anfragekommentar der vorhergehenden Zeile fort; dies gehört zur KI-Kennzeichnung und ist kein ausführbarer Code. |
| 4 | <code>&quot;&quot;&quot;Nur synthetische API-Test-Doubles: kein Mininet, kein OVS, keine echten Pakete.&quot;&quot;&quot;</code> | Kennzeichnet alle folgenden Netzobjekte ausdrücklich als synthetische API-Doubles; kein Test hier sendet ein echtes Paket. |
| 5 | <code>import contextlib</code> | Lädt das Standardbibliotheksmodul für zeitlich begrenzte Standardausgabeumleitung als Kontextmanager. |
| 6 | <code>import importlib.util</code> | Lädt das Standardbibliotheksmodul für dynamische Modulimporte aus den ausdrücklich angegebenen lokalen Dateien. |
| 7 | <code>import io</code> | Lädt das Standardbibliotheksmodul für Textpuffer im Arbeitsspeicher für aufgefangene Programmausgaben. |
| 8 | <code>from pathlib import Path</code> | Importiert Path für explizite, vom Arbeitsverzeichnis unabhängige Projektpfade und Dateizugriffe. |
| 9 | <code>import sys</code> | Lädt das Standardbibliotheksmodul für aktuellen Interpreter und Modulregister; dies installiert keine Bibliotheken. |
| 10 | <code>import types</code> | Lädt das Standardbibliotheksmodul für explizite Python-Modulobjekte für die gekennzeichneten Import-Doubles. |
| 11 | <code>import unittest</code> | Lädt das Standardbibliotheksmodul für ausführbare Testmethoden, Assertions, Untertests und Ergebnisberichte. |
| 12 | <code>from unittest.mock import Mock, patch</code> | Importiert aufzeichnende Mock-Objekte und zeitlich begrenzte Patches für die ausdrücklich synthetischen Mininet-API-Tests. |
| 14 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert die Testpfade am Verzeichnis ue6.7, unabhängig vom aufrufenden Arbeitsverzeichnis. |
| 17 | <code>def load(name, path):</code> | Definiert das Laden eines Prüfobjekts aus einer lokalen Datei unter eigenem Modulnamen. |
| 18 | <code>    spec = importlib.util.spec_from_file_location(name, path)</code> | Erstellt die Importspezifikation für das angegebene Prüfobjekt. |
| 19 | <code>    module = importlib.util.module_from_spec(spec)</code> | Erzeugt ein Modulobjekt, ohne den direkten Programmeinstieg aufzurufen. |
| 20 | <code>    spec.loader.exec_module(module)</code> | Führt dessen Modulrumpf mit den zuvor installierten Ersatzmodulen aus. |
| 21 | <code>    return module</code> | Gibt das geladene Prüfobjekt mit seinen Klassen und Funktionen zurück. |
| 24 | <code>class NodeDouble:</code> | Definiert einen synthetischen Knotenadapter, der ausschließlich API-Aufrufe protokolliert. |
| 25 | <code>    def __init__(self):</code> | Initialisiert einen neuen unabhängigen Knoten-Datensatz für jeden Testlauf. |
| 26 | <code>        self.calls = []</code> | Startet mit einer leeren chronologischen Aufrufliste. |
| 27 | <code>        self.reply = (&quot;3 packets transmitted, 3 received, 0% packet loss&quot;, &quot;&quot;, 0)</code> | Legt eine ausdrücklich synthetische erfolgreiche Pingrückgabe fest; sie ist keine Messung. |
| 29 | <code>    def config(self, **params):</code> | Stellt die von LinuxRouter per super benutzte Basiskonfigurationsmethode bereit. |
| 30 | <code>        self.calls.append((&quot;config&quot;, params))</code> | Protokolliert den Basiskonfigurationsaufruf und dessen Parameter für den Reihenfolgetest. |
| 32 | <code>    def cmd(self, command):</code> | Stellt Mininets textbasierte cmd-Schnittstelle als reine Aufrufaufzeichnung bereit. |
| 33 | <code>        self.calls.append((&quot;cmd&quot;, command))</code> | Speichert den genauen Shellbefehl, ohne ihn auszuführen. |
| 34 | <code>        return &quot;&quot;</code> | Gibt einen leeren synthetischen Ausgabetext zurück. |
| 36 | <code>    def pexec(self, argv, **kwargs):</code> | Stellt die statusliefernde pexec-Schnittstelle einschließlich Umgebungsoptionen bereit. |
| 37 | <code>        self.calls.append((&quot;pexec&quot;, argv, kwargs))</code> | Speichert Argumentliste und benannte Optionen getrennt, um etwa LC_ALL und PATH prüfen zu können. |
| 38 | <code>        return self.reply if argv[0] == &quot;ping&quot; else (&quot;&quot;, &quot;&quot;, 0)</code> | Gibt bei ping die veränderbare synthetische Antwort zurück und sonst einen erfolgreichen leeren Statusdatensatz. |
| 40 | <code>    def terminate(self):</code> | Stellt die vom Router per super aufgerufene Beendigungsmethode bereit. |
| 41 | <code>        self.calls.append((&quot;terminate&quot;,))</code> | Protokolliert das Beenden für den Forwarding-Lebenszyklustest. |
| 44 | <code>class TopoDouble:</code> | Definiert einen rein strukturellen Ersatz der Mininet-Topo-API. |
| 45 | <code>    def __init__(self):</code> | Initialisiert die Strukturaufzeichnung und ruft danach den Build der konkreten Unterklasse auf. |
| 46 | <code>        self.hosts, self.switches, self.links = {}, {}, []</code> | Erzeugt getrennte Register für Hosts, Switches und geordnete Links. |
| 47 | <code>        self.build()</code> | Führt RoutingTopo.build aus, damit dessen echte Strukturdefinition gegen die Ersatz-API getestet wird. |
| 49 | <code>    def addHost(self, name, **params):</code> | Nimmt einen Hostnamen und dessen Mininet-Parameter entgegen. |
| 50 | <code>        self.hosts[name] = params</code> | Speichert die Hostparameter einschließlich der angeforderten Knotenklasse. |
| 51 | <code>        return name</code> | Gibt den Namen als synthetische Referenz für spätere Links zurück. |
| 53 | <code>    def addSwitch(self, name, **params):</code> | Nimmt einen Switchnamen und dessen Mininet-Parameter entgegen. |
| 54 | <code>        self.switches[name] = params</code> | Speichert die Switchparameter, insbesondere die geforderte OVSBridge-Klasse. |
| 55 | <code>        return name</code> | Gibt den Switchnamen als Linkreferenz zurück. |
| 57 | <code>    def addLink(self, left, right, **params):</code> | Nimmt beide Linkenden sowie Interface-, Klassen- und Verzögerungsparameter entgegen. |
| 58 | <code>        self.links.append((left, right, params))</code> | Speichert den Link in Erzeugungsreihenfolge; kein veth oder OVS-Port wird angelegt. |
| 61 | <code>class TopologyTests(unittest.TestCase):</code> | Bündelt die sieben ohne Mininet ausführbaren API- und Negativtests. |
| 62 | <code>    def setUp(self):</code> | Erzeugt vor jeder Testmethode frische Ersatzmodule und Knoten. |
| 63 | <code>        definitions = {</code> | Beginnt die ausdrückliche Definition sämtlicher ersetzter Mininet-Module. |
| 64 | <code>            &quot;mininet&quot;: {}, &quot;mininet.topo&quot;: {&quot;Topo&quot;: TopoDouble},</code> | Stellt das Mininet-Wurzelmodul und TopoDouble als Topo-Ersatz bereit. |
| 65 | <code>            &quot;mininet.node&quot;: {&quot;Node&quot;: NodeDouble, &quot;Host&quot;: type(&quot;HostDouble&quot;, (), {}), &quot;OVSBridge&quot;: type(&quot;OVSBridgeDouble&quot;, (), {})},</code> | Ersetzt Node durch das protokollierende Double und Host sowie OVSBridge durch unterscheidbare Markerklassen. |
| 66 | <code>            &quot;mininet.link&quot;: {&quot;TCLink&quot;: type(&quot;TCLinkDouble&quot;, (), {})},</code> | Ersetzt TCLink durch eine eigene Markerklasse, deren Identität später geprüft wird. |
| 67 | <code>            &quot;mininet.cli&quot;: {&quot;CLI&quot;: Mock()}, &quot;mininet.net&quot;: {&quot;Mininet&quot;: Mock()},</code> | Ersetzt CLI und Mininet-Konstruktor durch Mock-Objekte mit überprüfbaren Aufruflisten. |
| 68 | <code>            &quot;mininet.log&quot;: {&quot;setLogLevel&quot;: Mock(), &quot;info&quot;: Mock()}, &quot;mininet.term&quot;: {&quot;makeTerm&quot;: Mock()},</code> | Ersetzt auch die nur beim Originalstarterimport benötigten Log- und Terminalfunktionen, ohne ein Terminal zu öffnen. |
| 69 | <code>        }</code> | Schließt die Ersatzmoduldefinition syntaktisch ab. |
| 70 | <code>        modules = {name: types.ModuleType(name) for name in definitions}</code> | Erzeugt für jeden ersetzten Modulnamen ein echtes Python-Modulobjekt als Importattrappe. |
| 71 | <code>        for name, attributes in definitions.items():</code> | Durchläuft die festgelegten Attributbelegungen aller Ersatzmodule. |
| 72 | <code>            modules[name].__dict__.update(attributes)</code> | Installiert die gewünschten Ersatzklassen und Mocks im jeweiligen Modulnamensraum. |
| 73 | <code>        self.addCleanup(patch.stopall)</code> | Registriert das Rückgängigmachen aller gestarteten Patches, auch bei fehlgeschlagenem Test. |
| 74 | <code>        patch.dict(sys.modules, modules).start()</code> | Schaltet die Ersatzmodule nur für die Testdauer in sys.modules ein. |
| 75 | <code>        self.topology = load(&quot;topology_double_subject&quot;, BASE / &quot;topology.py&quot;)</code> | Lädt die echte erweiterte Topologiedatei gegen diese synthetische Importumgebung. |
| 76 | <code>        patch.dict(sys.modules, {&quot;topology&quot;: self.topology}).start()</code> | Legt genau diese geladene Topologie auch unter dem vom Starter erwarteten Namen topology ab. |
| 77 | <code>        self.starter = load(&quot;starter_double_subject&quot;, BASE / &quot;start_erweitert.py&quot;)</code> | Lädt den echten erweiterten Starter; dessen Import des Originalstarters findet ebenfalls nur die Ersatz-API. |
| 78 | <code>        self.nodes = {name: NodeDouble() for name in (&quot;client&quot;, &quot;client2&quot;, &quot;r1&quot;, &quot;r2&quot;, &quot;server&quot;)}</code> | Erzeugt je einen aufzeichnenden Knoten für alle fünf erwarteten Hostnamen. |
| 79 | <code>        self.net = Mock()</code> | Erzeugt die synthetische Netzinstanz mit prüfbaren start- und stop-Aufrufen. |
| 80 | <code>        self.net.__getitem__ = Mock(side_effect=self.nodes.__getitem__)</code> | Leitet den net[name]-Zugriff auf das eindeutige Knotenregister um. |
| 81 | <code>        self.starter.Mininet.return_value = self.net</code> | Lässt den Mininet-Konstruktor genau diese Netzattrappe liefern. |
| 82 | <code>        self.output = contextlib.redirect_stdout(io.StringIO())</code> | Bereitet das Auffangen der vielen Starterausgaben im Arbeitsspeicher vor. |
| 83 | <code>        self.output.__enter__()</code> | Aktiviert die Ausgabeumleitung für die Dauer der Testmethode. |
| 84 | <code>        self.addCleanup(self.output.__exit__, None, None, None)</code> | Registriert das zuverlässige Wiederherstellen von stdout beim Testende. |
| 86 | <code>    def test_structure_interfaces_bridge_and_delay(self):</code> | Prüft vollständige Topologie, Schnittstellenpaare, Bridge-Klasse, Hostrollen und Linkparameter. |
| 87 | <code>        topo = self.topology.RoutingTopo()</code> | Instanziiert das echte RoutingTopo gegen die aufzeichnende TopoDouble-API. |
| 88 | <code>        self.assertEqual(set(topo.hosts), set(self.nodes))</code> | Verlangt genau die fünf erwarteten Hosts, keine fehlenden und keine zusätzlichen. |
| 89 | <code>        self.assertEqual(topo.switches, {&quot;s1&quot;: {&quot;cls&quot;: sys.modules[&quot;mininet.node&quot;].OVSBridge}})</code> | Verlangt genau s1 und die Identität der ausdrücklich gewählten OVSBridge-Ersatzklasse. |
| 90 | <code>        expected = [(&quot;client&quot;, &quot;s1&quot;, &quot;client-eth0&quot;, &quot;s1-eth1&quot;), (&quot;client2&quot;, &quot;s1&quot;, &quot;client2-eth0&quot;, &quot;s1-eth2&quot;), (&quot;s1&quot;, &quot;r1&quot;, &quot;s1-eth3&quot;, &quot;r1-eth0&quot;), (&quot;r1&quot;, &quot;r2&quot;, &quot;r1-eth1&quot;, &quot;r2-eth0&quot;), (&quot;r2&quot;, &quot;server&quot;, &quot;r2-eth1&quot;, &quot;server-eth0&quot;)]</code> | Definiert alle fünf erwarteten gerichteten Linkbeschreibungen mit exakten Schnittstellennamen. |
| 91 | <code>        actual = [(a, b, p[&quot;intfName1&quot;], p[&quot;intfName2&quot;]) for a, b, p in topo.links]</code> | Extrahiert die tatsächlichen Enden und Interfaceparameter der aufgezeichneten Links. |
| 92 | <code>        self.assertEqual(actual, expected)</code> | Vergleicht die gesamte geordnete Linkliste mit der Erwartung. |
| 93 | <code>        for _, _, params in topo.links:</code> | Durchläuft die Parameter jedes aufgezeichneten Links. |
| 94 | <code>            self.assertIs(params[&quot;cls&quot;], sys.modules[&quot;mininet.link&quot;].TCLink)</code> | Prüft per Objektidentität, dass jeder Link tatsächlich als TCLink deklariert wird. |
| 95 | <code>            self.assertEqual(params[&quot;delay&quot;], &quot;10ms&quot;)</code> | Verlangt auf jedem Link den unveränderten nominellen Delay-String 10ms; dies misst keine Kernelverzögerung. |
| 96 | <code>        for name, params in topo.hosts.items():</code> | Durchläuft die angeforderten Klassen aller Hosts. |
| 97 | <code>            self.assertIs(params[&quot;cls&quot;], self.topology.LinuxRouter if name in (&quot;r1&quot;, &quot;r2&quot;) else sys.modules[&quot;mininet.node&quot;].Host)</code> | Verlangt LinuxRouter nur für r1/r2 und die normale Hostklasse für beide Clients sowie server. |
| 98 | <code>        self.assertEqual(self.topology.topos, {&quot;routingtopo&quot;: self.topology.RoutingTopo})</code> | Prüft die vollständige Topologieregistrierung für den Namen routingtopo. |
| 100 | <code>    def test_forwarding_lifecycle(self):</code> | Prüft die Reihenfolge von geerbter Konfiguration, Forwarding ein, Forwarding aus und geerbtem Beenden. |
| 101 | <code>        router = self.topology.LinuxRouter()</code> | Erzeugt einen echten LinuxRouter auf Basis der protokollierenden NodeDouble-Klasse. |
| 102 | <code>        router.config(ip=None)</code> | Ruft dessen echte Konfiguration mit einem kontrollierbaren Parameter auf. |
| 103 | <code>        router.terminate()</code> | Ruft anschließend dessen echte Beendigungslogik auf. |
| 104 | <code>        self.assertEqual(router.calls, [(&quot;config&quot;, {&quot;ip&quot;: None}), (&quot;cmd&quot;, &quot;sysctl -w net.ipv4.ip_forward=1 &gt;/dev/null&quot;), (&quot;cmd&quot;, &quot;sysctl -w net.ipv4.ip_forward=0 &gt;/dev/null&quot;), (&quot;terminate&quot;,)])</code> | Vergleicht alle vier Ereignisse exakt, einschließlich sysctl-Befehlen und Weitergabe von ip=None. |
| 106 | <code>    def test_ping_accepts_both_counter_formats(self):</code> | Prüft beide unterstützten englischen Pingstatistikformate als positive Fälle. |
| 107 | <code>        node = self.nodes[&quot;client2&quot;]</code> | Wählt den unabhängigen client2-Knoten als Ping-Rückgabeträger. |
| 108 | <code>        for received in (&quot;received&quot;, &quot;packets received&quot;):</code> | Durchläuft die Schreibweisen received und packets received. |
| 109 | <code>            node.reply = (f&quot;3 packets transmitted, 3 {received}&quot;, &quot;&quot;, 0)</code> | Setzt jeweils eine synthetische exakte 3/3-Statistik mit Exitstatus null. |
| 110 | <code>            self.starter.ping_ok(node, &quot;10.0.2.2&quot;)</code> | Ruft die echte Pingfunktion des Starters mit dem Serverziel auf. |
| 111 | <code>        self.assertEqual(node.calls[-1], (&quot;pexec&quot;, [&quot;ping&quot;, &quot;-c&quot;, &quot;3&quot;, &quot;-W&quot;, &quot;2&quot;, &quot;10.0.2.2&quot;], {&quot;env&quot;: {&quot;LC_ALL&quot;: &quot;C&quot;, &quot;PATH&quot;: &quot;/usr/bin:/bin:/usr/sbin:/sbin&quot;}}))</code> | Vergleicht den letzten pexec-Aufruf exakt mit drei Proben, Timeout, Ziel und expliziter C-Umgebung. |
| 113 | <code>    def test_ping_rejects_loss_bad_counts_missing_summary_and_status(self):</code> | Definiert Negativtests gegen Paketverlust, falsche Zähler, fehlende Statistik und fehlerhaften Exitstatus. |
| 114 | <code>        for text, code in [(&quot;3 packets transmitted, 0 received, 100% packet loss&quot;, 1), (&quot;3 packets transmitted, 0 received, 100% packet loss&quot;, 0), (&quot;3 packets transmitted, 2 received&quot;, 0), (&quot;2 packets transmitted, 2 received&quot;, 0), (&quot;3 packets transmitted, 3 received&quot;, 1), (&quot;0% packet loss&quot;, 0), (&quot;3 packets transmitted, 30 received&quot;, 0)]:</code> | Durchläuft sieben Fehlerfälle einschließlich irreführendem 100%-Verlust bei Status null und falschem Empfangswert 30. |
| 115 | <code>            with self.subTest(text=text, code=code):</code> | Kennzeichnet jeden Datensatz als Untertest, damit ein Fehler Text und Status nennt. |
| 116 | <code>                self.nodes[&quot;client2&quot;].reply = (text, &quot;TEST-DOUBLE&quot;, code)</code> | Installiert nur für den jeweiligen Fall die synthetische fehlerhafte Prozessrückgabe. |
| 117 | <code>                with self.assertRaises(RuntimeError):</code> | Verlangt, dass die echte Pingfunktion den Datensatz mit RuntimeError verwirft. |
| 118 | <code>                    self.starter.ping_ok(self.nodes[&quot;client2&quot;], &quot;10.0.2.2&quot;)</code> | Ruft genau diese Pingfunktion gegen die programmierte Rückgabe auf. |
| 120 | <code>    def test_starter_configures_original_base_and_extra_client(self):</code> | Prüft den erfolgreichen gesamten Starterablauf einschließlich wiederverwendeter Original-Basiskonfiguration. |
| 121 | <code>        self.starter.main()</code> | Führt die echte main-Funktion ausschließlich gegen die Netz- und Knoten-Doubles aus. |
| 122 | <code>        self.starter.Mininet.assert_called_once_with(topo=unittest.mock.ANY, controller=None, autoSetMacs=True)</code> | Verlangt einen einzelnen Mininet-Konstruktoraufruf ohne Controller und mit automatischen MAC-Adressen; die konkrete Topoinstanz ist hier variabel. |
| 123 | <code>        for name, interface, address in [(&quot;client&quot;, &quot;client-eth0&quot;, &quot;10.0.1.2/24&quot;), (&quot;client2&quot;, &quot;client2-eth0&quot;, &quot;10.0.1.3/24&quot;), (&quot;r1&quot;, &quot;r1-eth0&quot;, &quot;10.0.1.1/24&quot;), (&quot;r1&quot;, &quot;r1-eth1&quot;, &quot;10.0.12.1/30&quot;), (&quot;r2&quot;, &quot;r2-eth0&quot;, &quot;10.0.12.2/30&quot;), (&quot;r2&quot;, &quot;r2-eth1&quot;, &quot;10.0.2.1/24&quot;), (&quot;server&quot;, &quot;server-eth0&quot;, &quot;10.0.2.2/24&quot;)]:</code> | Durchläuft alle sieben erwarteten Dateninterface-Adressen einschließlich client2. |
| 124 | <code>            self.assertIn((&quot;cmd&quot;, f&quot;ip addr add {address} dev {interface}&quot;), self.nodes[name].calls)</code> | Prüft, dass der Original-Konfigurationshelfer den exakten Adressbefehl am richtigen Knoten aufgerufen hat. |
| 125 | <code>        for name, command in [(&quot;r1&quot;, &quot;ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1&quot;), (&quot;r2&quot;, &quot;ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0&quot;), (&quot;client&quot;, &quot;ip route replace default via 10.0.1.1 dev client-eth0&quot;), (&quot;server&quot;, &quot;ip route replace default via 10.0.2.1 dev server-eth0&quot;)]:</code> | Durchläuft die beiden statischen Routerrouten und die beiden Original-Endhost-Default-Routen. |
| 126 | <code>            self.assertIn((&quot;cmd&quot;, command), self.nodes[name].calls)</code> | Verlangt jeden dieser exakten Shellbefehle im Aufrufprotokoll des zugehörigen Knotens. |
| 127 | <code>        self.assertIn((&quot;pexec&quot;, [&quot;ip&quot;, &quot;route&quot;, &quot;replace&quot;, &quot;default&quot;, &quot;via&quot;, &quot;10.0.1.1&quot;, &quot;dev&quot;, &quot;client2-eth0&quot;], {}), self.nodes[&quot;client2&quot;].calls)</code> | Verlangt zusätzlich die statusgeprüfte client2-Default-Route als exakte Argumentliste. |
| 128 | <code>        for name, target in [(&quot;client&quot;, &quot;10.0.2.2&quot;), (&quot;client2&quot;, &quot;10.0.2.2&quot;), (&quot;server&quot;, &quot;10.0.1.3&quot;)]:</code> | Durchläuft die drei vom Starter geforderten gerichteten Pingpaare. |
| 129 | <code>            self.assertEqual([call[1][-1] for call in self.nodes[name].calls if call[0] == &quot;pexec&quot; and call[1][0] == &quot;ping&quot;], [target])</code> | Prüft, dass an jeder Quelle genau das erwartete Pingziel und kein weiteres geprüft wurde. |
| 130 | <code>        self.starter.CLI.assert_called_once_with(self.net)</code> | Verlangt genau einen CLI-Aufruf mit derselben Netzinstanz. |
| 131 | <code>        self.net.start.assert_called_once_with()</code> | Verlangt genau einen Netzstart im Erfolgsfall. |
| 132 | <code>        self.net.stop.assert_called_once_with()</code> | Verlangt genau ein Netzstoppen auch im Erfolgsfall. |
| 134 | <code>    def test_cleanup_after_start_ping_or_cli_failure(self):</code> | Prüft die finally-Aufräumgarantie bei künstlichen Start-, Ping-, CLI- und Routingausnahmen. |
| 135 | <code>        for failure in (&quot;start&quot;, &quot;ping&quot;, &quot;cli&quot;, &quot;route&quot;):</code> | Durchläuft die vier unabhängig eingespritzten Fehlerorte. |
| 136 | <code>            with self.subTest(failure=failure):</code> | Kennzeichnet den jeweiligen Fehlerort als Untertest. |
| 137 | <code>                self.net.reset_mock()</code> | Leert Aufrufzähler der Netzattrappe zwischen den Fehlerfällen. |
| 138 | <code>                self.starter.CLI.reset_mock()</code> | Leert die Aufrufzähler der CLI-Attrappe ebenfalls. |
| 139 | <code>                self.net.start.side_effect = RuntimeError(&quot;TEST-DOUBLE&quot;) if failure == &quot;start&quot; else None</code> | Lässt nur im Startfehlerfall net.start eine RuntimeError-Ausnahme werfen. |
| 140 | <code>                self.starter.CLI.side_effect = RuntimeError(&quot;TEST-DOUBLE&quot;) if failure == &quot;cli&quot; else None</code> | Lässt nur im CLI-Fehlerfall die aufgerufene CLI eine RuntimeError-Ausnahme werfen. |
| 141 | <code>                self.nodes[&quot;client&quot;].reply = (&quot;3 packets transmitted, 0 received&quot;, &quot;&quot;, 1) if failure == &quot;ping&quot; else (&quot;3 packets transmitted, 3 received&quot;, &quot;&quot;, 0)</code> | Programmiert nur für den Pingfehler 3/0 und Status eins; andernfalls 3/3 und Status null. |
| 142 | <code>                with patch.object(self.nodes[&quot;client2&quot;], &quot;pexec&quot;, side_effect=RuntimeError(&quot;TEST-DOUBLE&quot;) if failure == &quot;route&quot; else self.nodes[&quot;client2&quot;].pexec):</code> | Ersetzt client2.pexec zeitlich begrenzt durch eine Routen-Ausnahme oder delegiert auf die normale Double-Methode. |
| 143 | <code>                    with self.assertRaises(RuntimeError):</code> | Verlangt in jedem eingespritzten Fehlerfall eine nach außen sichtbare RuntimeError-Ausnahme. |
| 144 | <code>                        self.starter.main()</code> | Führt den echten Starterablauf bis zum jeweiligen programmierten Fehlerort aus. |
| 145 | <code>                self.net.stop.assert_called_once_with()</code> | Verlangt genau einmal net.stop, unabhängig davon, wie früh der Fehler auftrat. |
| 146 | <code>                if failure != &quot;cli&quot;:</code> | Unterscheidet Fehler vor dem CLI-Aufruf vom Fehler innerhalb der bereits gestarteten CLI. |
| 147 | <code>                    self.starter.CLI.assert_not_called()</code> | Verlangt bei allen frühen Fehlern, dass die CLI gar nicht betreten wurde. |
| 149 | <code>    def test_nonzero_default_route_status_stops_before_cli(self):</code> | Prüft gesondert einen Nichtnull-Exitstatus der client2-Default-Route statt nur einer Python-Ausnahme. |
| 150 | <code>        with patch.object(self.nodes[&quot;client2&quot;], &quot;pexec&quot;, return_value=(&quot;&quot;, &quot;TEST-DOUBLE route failure&quot;, 2)):</code> | Programmiert eine synthetische Routenrückgabe mit Fehlermeldung und Status zwei. |
| 151 | <code>            with self.assertRaisesRegex(RuntimeError, &quot;route failure&quot;):</code> | Verlangt einen RuntimeError, der die tatsächliche Double-Fehlermeldung weitergibt. |
| 152 | <code>                self.starter.main()</code> | Führt den Starter bis zur fehlgeschlagenen Routeninstallation aus. |
| 153 | <code>        self.net.stop.assert_called_once_with()</code> | Verlangt auch in diesem Fehlerpfad genau einmal das Aufräumen des Netzes. |
| 154 | <code>        self.starter.CLI.assert_not_called()</code> | Verhindert, dass trotz fehlerhafter Route eine scheinbar erfolgreiche CLI geöffnet wird. |
| 157 | <code>if __name__ == &quot;__main__&quot;:</code> | Beschränkt den nachfolgenden Programmeinstieg auf direkten Skriptstart; ein Import allein führt ihn nicht aus. |
| 158 | <code>    unittest.main(verbosity=2)</code> | Startet die sieben echten Python-Unittests mit ausführlicher Ergebnisanzeige; die Netzoperationen darin bleiben ausdrücklich synthetisch. |

## [checks.py](checks.py)

| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Datum: 2026-10-29.</code> | Kennzeichnet den KI-Anteil mit Kurs, Werkzeug Hermes Agent, exaktem Modell OpenAI gpt-6.1-sol und Erstellungsdatum 2026-10-29. |
| 2 | <code># Tatsächliche Anfrage: Erstelle Gesamttest für Blatt06, alte Tests, Original-ZIPgleichheit,</code> | Dokumentiert die tatsächliche Teilanfrage als Quelltextkommentar; der Text wird nicht als Programm ausgeführt. |
| 3 | <code># Syntax, KI-Header, Markdownlinks, echte Messwerte, Ping/Echo und vollständige Zeilenerklärung.</code> | Setzt den tatsächlichen Anfragekommentar der vorhergehenden Zeile fort; dies gehört zur KI-Kennzeichnung und ist kein ausführbarer Code. |
| 4 | <code>&quot;&quot;&quot;Read-only Gesamttest; vorhandene Namespace-Messungen, niemals Mininet-Livebehauptung.&quot;&quot;&quot;</code> | Kennzeichnet den Gesamttest als lesende Prüfung vorhandener echter Namespace-Messungen und nicht als Mininet-Liveausführung. |
| 5 | <code>import ast</code> | Lädt das Standardbibliotheksmodul für Syntaxbäume und sichere Literal-Auswertung, ohne ein Programm auszuführen. |
| 6 | <code>import hashlib</code> | Lädt das Standardbibliotheksmodul für SHA-256-Fingerabdrücke zum Vorher-Nachher-Vergleich geschützter Dateien. |
| 7 | <code>import html</code> | Lädt das Standardbibliotheksmodul für HTML-Decodierung der im Markdown enthaltenen Quelltexttabellen. |
| 8 | <code>import json</code> | Lädt das Standardbibliotheksmodul für Lesen und Schreiben maschinenlesbarer echter Adress- und Ergebnisdaten. |
| 9 | <code>import os</code> | Lädt das Standardbibliotheksmodul für Prozessumgebung, Dateisystemcodierung beziehungsweise privilegierte Namespace-Systemaufrufe. |
| 10 | <code>from pathlib import Path</code> | Importiert Path für explizite, vom Arbeitsverzeichnis unabhängige Projektpfade und Dateizugriffe. |
| 11 | <code>import re</code> | Lädt das Standardbibliotheksmodul für reguläre Ausdrücke für exakte Pingzähler, Linkziele oder Erklärungszeilen. |
| 12 | <code>import subprocess</code> | Lädt das Standardbibliotheksmodul für tatsächliche externe Prozessstarts mit Ausgaben und Exitstatus. |
| 13 | <code>import sys</code> | Lädt das Standardbibliotheksmodul für aktuellen Interpreter und Modulregister; dies installiert keine Bibliotheken. |
| 14 | <code>import unittest</code> | Lädt das Standardbibliotheksmodul für ausführbare Testmethoden, Assertions, Untertests und Ergebnisberichte. |
| 15 | <code>from urllib.parse import unquote, urlsplit</code> | Importiert URL-Decodierung und URL-Zerlegung für die Prüfung relativer Markdown-Dateiverweise. |
| 16 | <code>import zipfile</code> | Lädt das Standardbibliotheksmodul für direktes Lesen des gelieferten ZIP-Archivs ohne externes Entpackprogramm. |
| 18 | <code>BASE = Path(__file__).resolve().parent</code> | Bestimmt das Blattverzeichnis aus dem Skriptpfad, damit alle Tests unabhängig vom aktuellen Verzeichnis funktionieren. |
| 19 | <code>EXPLAIN = (&quot;verify_namespaces.py&quot;, &quot;ue6.7/topology.py&quot;, &quot;ue6.7/start_erweitert.py&quot;, &quot;ue6.7/test_topology.py&quot;, &quot;checks.py&quot;)</code> | Legt genau die fünf eigenen Dateien fest, deren nichtleere Zeilen hier vollständig erklärt werden müssen. |
| 20 | <code>PING = re.compile(r&quot;(\d+) packets transmitted, (\d+) (?:packets )?received&quot;)</code> | Erkennt die vollständigen gesendeten und empfangenen Pingzähler mit optionalem Wort packets; Prozent-Teilstrings werden nicht verwendet. |
| 21 | <code>PLAN = {&quot;client&quot;: {&quot;client-eth0&quot;: (&quot;10.0.1.2&quot;, 24)}, &quot;client2&quot;: {&quot;client2-eth0&quot;: (&quot;10.0.1.3&quot;, 24)}, &quot;r1&quot;: {&quot;r1-eth0&quot;: (&quot;10.0.1.1&quot;, 24), &quot;r1-eth1&quot;: (&quot;10.0.12.1&quot;, 30)}, &quot;r2&quot;: {&quot;r2-eth0&quot;: (&quot;10.0.12.2&quot;, 30), &quot;r2-eth1&quot;: (&quot;10.0.2.1&quot;, 24)}, &quot;server&quot;: {&quot;server-eth0&quot;: (&quot;10.0.2.2&quot;, 24)}}</code> | Definiert für jeden erwarteten Knoten alle Dateninterfaces mit exakten IPv4-Adressen und Präfixlängen. |
| 24 | <code>def run(relative, *arguments):</code> | Kapselt den tatsächlichen Start eines vorhandenen Aufgaben- oder Testskripts mit optionalen CLI-Argumenten. |
| 25 | <code>    result = subprocess.run([sys.executable, &quot;-B&quot;, str(BASE / relative), *arguments], cwd=BASE, env={**os.environ, &quot;PYTHONDONTWRITEBYTECODE&quot;: &quot;1&quot;}, capture_output=True, text=True, timeout=90)</code> | Startet mit demselben Interpreter und -B, verhindert Bytecode auch in Kindprozessen, erfasst Ausgaben und begrenzt die Laufzeit auf 90 Sekunden. |
| 26 | <code>    if result.returncode:</code> | Erkennt fehlgeschlagene Aufgabenprozesse an ihrem tatsächlichen Exitstatus. |
| 27 | <code>        raise AssertionError(f&quot;{relative}: Status {result.returncode}\n{result.stdout}\n{result.stderr}&quot;)</code> | Bricht den Test mit Dateiname, Status und vollständigen erfassten Ausgaben ab. |
| 28 | <code>    return result.stdout + result.stderr</code> | Liefert stdout und stderr gemeinsam, damit sowohl generierte Antworten als auch unittest-Berichte prüfbar sind. |
| 31 | <code>def snapshot():</code> | Definiert einen lesenden Fingerabdruck aller besonders zu bewahrenden Original- und Messdateien. |
| 32 | <code>    paths = list((BASE / &quot;Angabe&quot;).rglob(&quot;*&quot;)) + list((BASE / &quot;nachweise&quot;).rglob(&quot;*&quot;))</code> | Sammelt die ursprüngliche Infrastruktur und den gesamten Nachweisbaum rekursiv, ohne dort etwas zu erzeugen. |
| 33 | <code>    paths += [BASE / &quot;erklaerung_routing.md&quot;, BASE / &quot;erklaerung_algorithmen.md&quot;, BASE / &quot;angabe_blatt06.pdf&quot;]</code> | Ergänzt die beiden unveränderlichen älteren Erklärungen sowie die Originalaufgabenstellung. |
| 34 | <code>    return {str(path.relative_to(BASE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.is_file()}</code> | Bildet für jede echte Datei einen SHA-256-Fingerabdruck; auch hinzugefügte oder verschwundene geschützte Dateien ändern das Dictionary. |
| 37 | <code>class SheetChecks(unittest.TestCase):</code> | Bündelt die neun Gesamttestgruppen als unabhängig berichtete unittest-Testmethoden. |
| 38 | <code>    def test_all_exercises_and_old_suites(self):</code> | Prüft alle Aufgabenprogramme und die unveränderten älteren Routing-/Algorithmensuiten tatsächlich durch Prozessstarts. |
| 39 | <code>        for relative in (&quot;ue6.1/adressen.py&quot;, &quot;ue6.2/routing.py&quot;):</code> | Durchläuft die beiden älteren Adress- und Routingmodelle. |
| 40 | <code>            self.assertIn(&quot;Selbsttest&quot;, run(relative, &quot;--test&quot;))</code> | Verlangt ihren erfolgreich ausgeführten Selbsttest und dessen Kennzeichnung. |
| 41 | <code>            self.assertTrue(run(relative).strip())</code> | Startet außerdem den normalen Planmodus und verlangt eine nichtleere Ausgabe. |
| 42 | <code>        for relative, count in ((&quot;ue6.3/test_static_routes.py&quot;, 4), (&quot;ue6.6/test_algorithmen.py&quot;, 6), (&quot;ue6.7/test_topology.py&quot;, 7)):</code> | Legt die drei separat auszuführenden Testsuiten samt exakter erwarteter Testanzahl fest: vier, sechs und sieben. |
| 43 | <code>            output = run(relative)</code> | Führt jede Testsuite tatsächlich aus; ein Nichtnullstatus wird bereits durch run verworfen. |
| 44 | <code>            self.assertRegex(output, rf&quot;Ran {count} tests? in&quot;)</code> | Prüft zusätzlich die gemeldete exakte unittest-Anzahl, sodass ein leer gelaufener Testtreiber nicht genügt. |
| 45 | <code>            self.assertIn(&quot;\nOK\n&quot;, output)</code> | Verlangt den unittest-Abschluss OK als eigene Zeile. |
| 46 | <code>        for relative in (&quot;ue6.4/subnetting.py&quot;, &quot;ue6.5/dijkstra.py&quot;, &quot;ue6.6/distance_vector.py&quot;):</code> | Durchläuft die drei ausführbaren Algorithmen-/Subnettingprogramme. |
| 47 | <code>            self.assertEqual(run(relative), (BASE / relative).with_name(&quot;antwort.md&quot;).read_text())</code> | Vergleicht ihre tatsächlich erzeugte Ausgabe bytezeichengetreu als Text mit der jeweiligen abgelegten antwort.md. |
| 48 | <code>        self.assertTrue(run(&quot;ue6.3/static_routes.py&quot;, &quot;--help&quot;).strip())</code> | Prüft den aufrufbaren Hilfemodus der statischen Routenübung, ohne einen Mininet-Lauf vorzutäuschen. |
| 49 | <code>        for number in range(1, 8):</code> | Durchläuft alle sieben Aufgabennummern des Blatts. |
| 50 | <code>            self.assertTrue((BASE / f&quot;ue6.{number}/antwort.md&quot;).read_text().strip())</code> | Verlangt zu jeder Aufgabe eine vorhandene nichtleere Antwortdatei. |
| 52 | <code>    def test_original_archive_byte_equality(self):</code> | Prüft die unveränderte Infrastruktur direkt gegen jedes Mitglied des gelieferten ZIP-Archivs. |
| 53 | <code>        directory = BASE / &quot;Angabe&quot;</code> | Bestimmt das Originalverzeichnis Angabe. |
| 54 | <code>        with zipfile.ZipFile(directory / &quot;uebb6_template.zip&quot;) as archive:</code> | Öffnet das vorhandene Originalarchiv mit der Python-Standardbibliothek; ein installiertes unzip wird nicht vorausgesetzt. |
| 55 | <code>            members = [item for item in archive.infolist() if not item.is_dir()]</code> | Wählt nur tatsächliche Archivdateien und lässt Verzeichniseinträge aus. |
| 56 | <code>            self.assertEqual(len(members), len({item.filename for item in members}))</code> | Verhindert doppelte Archivnamen, die sonst beim Mengenvergleich unbemerkt überschrieben werden könnten. |
| 57 | <code>            self.assertEqual({item.filename for item in members}, {p.name for p in directory.iterdir() if p.is_file() and p.suffix != &quot;.zip&quot;})</code> | Verlangt die exakte gleiche Dateinamenmenge im Archiv und im extrahierten Verzeichnis, ausgenommen das ZIP selbst. |
| 58 | <code>            for item in members:</code> | Durchläuft jedes Originalarchivmitglied einzeln. |
| 59 | <code>                self.assertEqual(Path(item.filename).name, item.filename)</code> | Verlangt einfache Dateinamen ohne übergeordnete Pfade und verhindert damit unerwartete Archivpfadinterpretation. |
| 60 | <code>                self.assertEqual(archive.read(item), (directory / item.filename).read_bytes(), item.filename)</code> | Vergleicht die vollständigen Originalbytes direkt, nicht nur Größe, Datum oder einen gekürzten Hash. |
| 62 | <code>    def test_syntax_headers_and_shell_syntax(self):</code> | Prüft die Syntax aller Python-Dateien, die KI-Kennzeichnung eigener Programme und die Shellsyntax der Originalhelfer. |
| 63 | <code>        for path in sorted(BASE.rglob(&quot;*.py&quot;)):</code> | Durchläuft jede Pythondatei des gesamten Blatts in stabiler Reihenfolge. |
| 64 | <code>            source = path.read_text()</code> | Liest deren echten Quelltext aus der Datei. |
| 65 | <code>            compile(source, str(path), &quot;exec&quot;)</code> | Kompiliert den Text nur im Speicher; weder wird der Modulrumpf ausgeführt noch ein pyc geschrieben. |
| 66 | <code>            if &quot;Angabe&quot; not in path.relative_to(BASE).parts:</code> | Wendet die Kennzeichnungspflicht nur auf eigene Dateien außerhalb der Originalvorlagen an. |
| 67 | <code>                header = &quot;\n&quot;.join(source.splitlines()[:6])</code> | Begrenzt den zu prüfenden Header auf die ersten sechs physischen Zeilen. |
| 68 | <code>                for required in (&quot;KI-Kennzeichnung RN WS26&quot;, &quot;Hermes Agent&quot;, &quot;OpenAI gpt-6.1-sol&quot;, &quot;2026-10-29&quot;, &quot;Anfrage:&quot;):</code> | Verlangt Kursmarkierung, Werkzeug, Modell, Datum und eine tatsächliche Anfrage am Dateianfang. |
| 69 | <code>                    self.assertIn(required, header, str(path))</code> | Prüft jeden dieser Bestandteile mit Dateipfad im Fehlerbericht. |
| 70 | <code>        for path in (BASE / &quot;Angabe&quot;).glob(&quot;*.sh&quot;):</code> | Durchläuft alle gelieferten Shellskripte, ohne deren Netzwerk- oder Capturebefehle zu starten. |
| 71 | <code>            result = subprocess.run([&quot;bash&quot;, &quot;-n&quot;, str(path)], capture_output=True, text=True, timeout=10)</code> | Lässt bash -n ausschließlich die Syntax prüfen und erfasst Fehler bei begrenzter Laufzeit. |
| 72 | <code>            self.assertEqual(result.returncode, 0, result.stderr)</code> | Verlangt erfolgreichen Syntaxprüfstatus und gibt bei Fehlern die echte bash-Fehlermeldung weiter. |
| 74 | <code>    def test_relative_markdown_links(self):</code> | Prüft relative Markdown-Dateilinks im gesamten Blatt auf einen existierenden lokalen Zielpfad. |
| 75 | <code>        for path in BASE.rglob(&quot;*.md&quot;):</code> | Durchläuft alle Markdown-Dateien rekursiv, einschließlich Antworten und Prüfprotokoll. |
| 76 | <code>            for target in re.findall(r&quot;!?\[[^\]]*\]\(([^\s)]+)(?:\s+\&quot;[^\&quot;]*\&quot;)?\)&quot;, re.sub(r&quot;&lt;code&gt;.*?&lt;/code&gt;&#124;```.*?```&#124;`[^`\n]*`&quot;, &quot;&quot;, path.read_text(), flags=re.DOTALL)):</code> | Entfernt zuerst HTML-Quelltextfelder, Codeblöcke und Inlinecode, damit Quelltextbeispiele keine falschen Links ergeben; extrahiert dann Inline-Link- und Bildziele mit optionalem Titel. Dies ist kein allgemeiner vollständiger Markdownparser. |
| 77 | <code>                parsed = urlsplit(html.unescape(target.strip(&quot;&lt;&gt;&quot;)))</code> | Entfernt optionale Winkelklammern, decodiert HTML-Entities und zerlegt URL-Bestandteile. |
| 78 | <code>                if parsed.scheme or parsed.netloc or not parsed.path:</code> | Erkennt externe URLs sowie reine Fragmentverweise, die keinen relativen Dateipfad verlangen. |
| 79 | <code>                    continue</code> | Überspringt diese nichtlokalen oder dateipfadlosen Verweise; externe Erreichbarkeit wird nicht behauptet. |
| 80 | <code>                resolved = (path.parent / unquote(parsed.path)).resolve()</code> | Decodiert URL-Escapes und löst den relativen Link vom Ort seiner Markdown-Datei aus auf. |
| 81 | <code>                self.assertTrue(resolved.is_relative_to(BASE), f&quot;Link außerhalb Blatt06: {path}: {target}&quot;)</code> | Verlangt, dass der aufgelöste Pfad innerhalb des Blatts bleibt; Symlinks und .. werden vorher normalisiert. |
| 82 | <code>                self.assertTrue(resolved.exists(), f&quot;Fehlender Link: {path}: {target}&quot;)</code> | Verlangt ein tatsächlich vorhandenes Ziel; Überschriftenfragmente werden hier nicht aufgelöst. |
| 84 | <code>    def test_explanation_every_nonempty_line_and_exact_source(self):</code> | Prüft die vollständige Einzelzeilenerklärung gegen die endgültigen echten Quelltexte. |
| 85 | <code>        text = (BASE / &quot;erklaerung_blatt06.md&quot;).read_text()</code> | Liest diese neue Blatt-Erklärung als verbindliche Dokumentationsdatei. |
| 86 | <code>        for relative in EXPLAIN:</code> | Durchläuft genau die fünf in EXPLAIN aufgeführten eigenen Dateien. |
| 87 | <code>            heading = f&quot;## [{relative}]({relative})\n&quot;</code> | Baut die exakte erwartete verlinkte Abschnittsüberschrift für die jeweilige Datei auf. |
| 88 | <code>            self.assertEqual(text.count(heading), 1, relative)</code> | Verlangt genau einen solchen Abschnitt und verhindert doppelte Dateierklärungen. |
| 89 | <code>            section = text.split(heading, 1)[1].split(&quot;\n## &quot;, 1)[0]</code> | Isoliert dessen Inhalt bis zur nächsten Überschrift derselben Ebene. |
| 90 | <code>            rows = re.findall(r&quot;^\&#124; (\d+) \&#124; &lt;code&gt;(.*?)&lt;/code&gt; \&#124; (.+) \&#124;$&quot;, section, re.MULTILINE)</code> | Extrahiert pro Tabellenzeile die physische Zeilennummer, den HTML-codierten Originalquelltext und den Erklärungstext. |
| 91 | <code>            expected = [(number, line) for number, line in enumerate((BASE / relative).read_text().splitlines(), 1) if line.strip()]</code> | Ermittelt direkt aus der echten Datei alle und nur die nichtleeren physischen Zeilen samt unveränderten Einrückungen. |
| 92 | <code>            self.assertEqual([(int(number), html.unescape(code)) for number, code, _ in rows], expected, relative)</code> | Vergleicht vollständige geordnete Nummer-Quelltext-Paare nach HTML-Decodierung; fehlende, zusätzliche, doppelte oder veraltete Zeilen fallen auf. |
| 93 | <code>            self.assertTrue(all(len(description.strip()) &gt;= 20 for _, _, description in rows), relative)</code> | Verlangt je Zeile einen nichttrivial langen Erklärungstext; semantisches Verständnis wird damit nicht automatisch bewiesen. |
| 94 | <code>        routing = (BASE / &quot;erklaerung_routing.md&quot;).read_text()</code> | Liest zusätzlich die bereits vorhandene ältere Routing-Erklärung, ohne sie zu bearbeiten. |
| 95 | <code>        for relative in (&quot;ue6.1/adressen.py&quot;, &quot;ue6.2/routing.py&quot;, &quot;ue6.3/static_routes.py&quot;, &quot;ue6.3/test_static_routes.py&quot;):</code> | Durchläuft deren vier erklärten eigenen Routingdateien. |
| 96 | <code>            section = routing.split(f&quot;## [{relative}]({relative})&quot;, 1)[1].split(&quot;\n## &quot;, 1)[0]</code> | Isoliert jeweils den zur echten Datei gehörenden alten Erklärungsabschnitt. |
| 97 | <code>            numbers = [int(value) for value in re.findall(r&quot;^\&#124; (\d+) \&#124;&quot;, section, re.MULTILINE)]</code> | Liest die dort dokumentierten physischen Zeilennummern aus der Tabelle. |
| 98 | <code>            self.assertEqual(numbers, [i for i, line in enumerate((BASE / relative).read_text().splitlines(), 1) if line.strip()])</code> | Vergleicht deren Reihenfolge vollständig mit allen nichtleeren echten Quellzeilen; die ältere Algorithmenerklärung prüft bereits ihre eigene Testsuite. |
| 99 | <code>        self.assertIn(&quot;erklaerung_routing.md&quot;, text)</code> | Verlangt den Verweis auf die unveränderte Routing-Erklärung auch in dieser neuen Gesamterklärung. |
| 100 | <code>        self.assertIn(&quot;erklaerung_algorithmen.md&quot;, text)</code> | Verlangt ebenso den Verweis auf die unveränderte Algorithmenerklärung. |
| 102 | <code>    def test_namespace_addresses_and_provenance(self):</code> | Prüft die Herkunftskennzeichnung und tatsächlichen IPv4-Interfaceaufnahmen des vorhandenen Namespace-Messlaufs. |
| 103 | <code>        evidence = BASE / &quot;nachweise/run01&quot;</code> | Wählt ausschließlich den bestehenden Lauf nachweise/run01; startet den privilegierten Messrunner nicht erneut. |
| 104 | <code>        results = json.loads((evidence / &quot;results.json&quot;).read_text())</code> | Liest dessen gespeicherte Ergebniszusammenfassung als echtes JSON. |
| 105 | <code>        self.assertEqual([item[&quot;fall&quot;] for item in results], [&quot;basis&quot;, &quot;erweitert&quot;])</code> | Verlangt genau die beiden Fälle basis und erweitert in der vorgesehenen Reihenfolge. |
| 106 | <code>        for item in results:</code> | Bearbeitet beide gemessenen Fälle getrennt. |
| 107 | <code>            self.assertIn(&quot;NICHT Mininet/OVS&quot;, item[&quot;messung&quot;])</code> | Verlangt die ausdrückliche Kennzeichnung, dass die Messung nicht Mininet/OVS stammt. |
| 108 | <code>            self.assertIn(&quot;keine TC-Verzögerung&quot;, item[&quot;messung&quot;])</code> | Verlangt außerdem die Kennzeichnung, dass keine TC-Verzögerung gemessen wurde. |
| 109 | <code>            names = [&quot;client&quot;, &quot;r1&quot;, &quot;r2&quot;, &quot;server&quot;] + ([&quot;client2&quot;] if item[&quot;fall&quot;] == &quot;erweitert&quot; else [])</code> | Bestimmt die vier Basisknoten und ergänzt nur im erweiterten Fall client2. |
| 110 | <code>            self.assertEqual(item[&quot;tcp_clients&quot;], [&quot;client&quot;, &quot;client2&quot;] if item[&quot;fall&quot;] == &quot;erweitert&quot; else [&quot;client&quot;])</code> | Vergleicht die dokumentierten TCP-Clientnamen mit genau den im jeweiligen Fall erwarteten Clients. |
| 111 | <code>            for name in names:</code> | Durchläuft jeden in diesem Fall tatsächlich erwarteten Messknoten. |
| 112 | <code>                data = json.loads((evidence / f&quot;{item[&#x27;fall&#x27;]}-{name}-addr.json&quot;).read_text())</code> | Liest dessen vorhandene ip-JSON-Adressaufnahme. |
| 113 | <code>                addresses = {interface[&quot;ifname&quot;]: (address[&quot;local&quot;], address[&quot;prefixlen&quot;]) for interface in data if interface[&quot;ifname&quot;] != &quot;lo&quot; for address in interface.get(&quot;addr_info&quot;, []) if address[&quot;family&quot;] == &quot;inet&quot;}</code> | Extrahiert IPv4-Dateninterfaces mit Adresse und Präfix; Loopback und IPv6 sind nicht Teil dieses IPv4-Sollvergleichs. |
| 114 | <code>                self.assertEqual(addresses, PLAN[name])</code> | Vergleicht das komplette Dateninterface-Dictionary mit dem vorgegebenen Plan, einschließlich beider Routerinterfaces und aller Präfixe. |
| 115 | <code>                report = (evidence / f&quot;{item[&#x27;fall&#x27;]}-{name}.txt&quot;).read_text()</code> | Liest den zugehörigen menschenlesbaren Zustandsnachweis. |
| 116 | <code>                for command in (&quot;$ ip -br addr&quot;, &quot;$ ip addr&quot;, &quot;$ bash Angabe/inspect_network.sh&quot;, &quot;=== Routing table ===&quot;):</code> | Legt die drei dokumentierten Erhebungsbefehle und die Routingtabellenüberschrift als Pflichtbestandteile fest. |
| 117 | <code>                    self.assertIn(command, report)</code> | Verlangt jeden dieser Bestandteile im tatsächlich gespeicherten Bericht. |
| 118 | <code>                run(&quot;ue6.1/adressen.py&quot;, &quot;--json&quot;, str(evidence / f&quot;{item[&#x27;fall&#x27;]}-{name}-addr.json&quot;), &quot;--host&quot;, &quot;client&quot; if name == &quot;client2&quot; else name)</code> | Startet den alten JSON-Auswertemodus auf jeder echten Aufnahme; für client2 wird nur dessen vom Altprogramm erlaubtes Label client genutzt, die eigene exakte client2-Prüfung erfolgte bereits zuvor. |
| 120 | <code>    def test_exact_ping_counts_statuses_and_route_cycle(self):</code> | Prüft alle gespeicherten Pingzähler, Sequenzen und Routingoperationen ohne erneutes Senden. |
| 121 | <code>        evidence = BASE / &quot;nachweise/run01&quot;</code> | Bestimmt das vorhandene Nachweisverzeichnis run01. |
| 122 | <code>        for tag in (&quot;basis&quot;, &quot;erweitert&quot;):</code> | Durchläuft Basis- und Erweiterungs-Routingdialog separat. |
| 123 | <code>            text = (evidence / f&quot;{tag}-routen-und-ping.txt&quot;).read_text()</code> | Liest den unveränderten tatsächlichen Routing-/Pingdialog des Falls. |
| 124 | <code>            self.assertEqual(PING.findall(text), [(&quot;3&quot;, &quot;3&quot;), (&quot;3&quot;, &quot;0&quot;), (&quot;3&quot;, &quot;3&quot;)])</code> | Verlangt exakt drei Statistiken in der Reihenfolge 3/3, 3/0, 3/3; die absichtliche Nichterreichbarkeit ist Teil des Erfolgsnachweises. |
| 125 | <code>            blocks = re.findall(r&quot;\[client\] \$ .*?ping[^\n]*\n(.*?)\[Exitstatus (\d+)\]&quot;, text, re.DOTALL)</code> | Extrahiert die drei echten Client-Pingblöcke zusammen mit ihrem jeweils dokumentierten Prozessstatus. |
| 126 | <code>            self.assertEqual([status for _, status in blocks], [&quot;0&quot;, &quot;1&quot;, &quot;0&quot;])</code> | Verlangt die Statusfolge null, eins, null passend zu intakter, entfernter und wiederhergestellter Route. |
| 127 | <code>            self.assertEqual([re.findall(r&quot;^64 bytes from .*?icmp_seq=(\d+)&quot;, block, re.MULTILINE) for block, _ in blocks], [[&quot;1&quot;, &quot;2&quot;, &quot;3&quot;], [], [&quot;1&quot;, &quot;2&quot;, &quot;3&quot;]])</code> | Vergleicht die erfolgreichen Reply-Sequenzen exakt mit 1,2,3 und verlangt im negativen Block keine erfolgreichen Echo-Replies. |
| 128 | <code>            for router, network, gateway, interface in ((&quot;r1&quot;, &quot;10.0.2.0/24&quot;, &quot;10.0.12.2&quot;, &quot;r1-eth1&quot;), (&quot;r2&quot;, &quot;10.0.1.0/24&quot;, &quot;10.0.12.1&quot;, &quot;r2-eth0&quot;)):</code> | Legt pro Router die tatsächlich zu entfernende und wiederherzustellende Remote-LAN-Route fest. |
| 129 | <code>                for operation in (&quot;del&quot;, &quot;add&quot;):</code> | Durchläuft die beiden erwarteten Routenoperationen del und add. |
| 130 | <code>                    self.assertIn(f&quot;[{router}] $ ip route {operation} {network} via {gateway} dev {interface}\n[Exitstatus 0]&quot;, text)</code> | Verlangt jeden exakten Befehl einschließlich des direkt folgenden erfolgreichen Exitstatus im gespeicherten Dialog. |
| 131 | <code>                self.assertIn(f&quot;[{router}] $ sysctl -n net.ipv4.ip_forward\n1\n[Exitstatus 0]&quot;, text)</code> | Verlangt außerdem gemessenes IPv4-Forwarding eins auf beiden Routern samt erfolgreichem Abfragestatus. |
| 132 | <code>            self.assertEqual(text.count(&quot;RTNETLINK answers: Network is unreachable\n[Exitstatus 2]&quot;), 2)</code> | Verlangt genau zwei dokumentierte fehlgeschlagene Routenabfragen mit Network is unreachable und Status zwei. |
| 133 | <code>        expected = {&quot;basis-server-ping-10.0.1.2.txt&quot;, &quot;erweitert-server-ping-10.0.1.2.txt&quot;, &quot;erweitert-client2-ping-10.0.1.2.txt&quot;, &quot;erweitert-server-ping-10.0.1.3.txt&quot;}</code> | Definiert die genaue Menge der vier zusätzlichen positiven Pingdateien beider Fälle. |
| 134 | <code>        self.assertEqual({path.name for path in evidence.glob(&quot;*-ping-*.txt&quot;)}, expected)</code> | Vergleicht diese Menge mit allen vorhandenen Einzel-Pingdateien und erkennt fehlende sowie unerwartete Dateien. |
| 135 | <code>        for name in expected:</code> | Durchläuft jeden zusätzlichen positiven Pingnachweis. |
| 136 | <code>            text = (evidence / name).read_text()</code> | Liest seine tatsächlich gespeicherte Ausgabe. |
| 137 | <code>            self.assertEqual(PING.findall(text), [(&quot;3&quot;, &quot;3&quot;)])</code> | Verlangt genau eine Statistik mit exakt drei gesendeten und drei empfangenen Paketen. |
| 138 | <code>            self.assertEqual(re.findall(r&quot;^64 bytes from .*?icmp_seq=(\d+)&quot;, text, re.MULTILINE), [&quot;1&quot;, &quot;2&quot;, &quot;3&quot;])</code> | Verlangt zusätzlich genau drei erfolgreiche Reply-Zeilen mit den Sequenznummern eins bis drei. |
| 140 | <code>    def test_original_tcp_echo_content_and_server_connections(self):</code> | Prüft die Original-Nachrichtenbytes sowie die Client- und Servernachweise aller realen TCP-Verbindungen. |
| 141 | <code>        tree = ast.parse((BASE / &quot;Angabe/tcp_client.py&quot;).read_text())</code> | Parst den Originalclient als Syntaxbaum, ohne beim Import versehentlich eine TCP-Verbindung aufzubauen. |
| 142 | <code>        messages = next(node.iter.elts for node in ast.walk(tree) if isinstance(node, ast.For) and isinstance(node.iter, ast.List))</code> | Findet die im Originalprogramm direkt vorgegebene Nachrichtenliste der for-Schleife. |
| 143 | <code>        payloads = [ast.literal_eval(node) for node in messages]</code> | Wertet ausschließlich die Literale dieser Liste sicher als Daten aus; eval oder Ausführung des Originalcodes findet hier nicht statt. |
| 144 | <code>        self.assertEqual(payloads, [f&quot;Network layer test {i}\n&quot;.encode() for i in (1, 2, 3)])</code> | Verlangt die drei vorgegebenen Bytes-Nachrichten einschließlich genau eines Newlinebytes pro Nachricht. |
| 145 | <code>        for tag, clients in ((&quot;basis&quot;, [&quot;client&quot;]), (&quot;erweitert&quot;, [&quot;client&quot;, &quot;client2&quot;])):</code> | Legt einen Client im Basisfall und zwei Clients im erweiterten Fall als getrennte Prüffälle fest. |
| 146 | <code>            server = (BASE / f&quot;nachweise/run01/{tag}-server-tcp.txt&quot;).read_text().splitlines()</code> | Liest den jeweiligen tatsächlichen Servernachweis als Zeilenliste. |
| 147 | <code>            self.assertEqual(server[0], &quot;Listening on 10.0.2.2:5000&quot;)</code> | Prüft exakt den originalen Listening-Endpunkt 10.0.2.2:5000. |
| 148 | <code>            connections = [ast.literal_eval(line.removeprefix(&quot;Connection from &quot;)) for line in server if line.startswith(&quot;Connection from &quot;)]</code> | Liest die protokollierten Clientadress-Tupel sicher als Literale aus den Verbindungszeilen. |
| 149 | <code>            self.assertEqual([address for address, _ in connections], [&quot;10.0.1.2&quot;, &quot;10.0.1.3&quot;][:len(clients)])</code> | Verlangt die richtigen Client-IP-Adressen und deren Reihenfolge, einschließlich 10.0.1.3 im erweiterten Fall. |
| 150 | <code>            self.assertTrue(all(isinstance(port, int) and 0 &lt; port &lt;= 65535 for _, port in connections))</code> | Prüft die tatsächlich aufgezeichneten dynamischen Quellports nur auf gültige Integer-Portwerte, ohne feste Ports zu erfinden. |
| 151 | <code>            self.assertEqual([line for line in server if line.startswith(&quot;Received &quot;)], [f&quot;Received {len(payload)} bytes&quot; for _ in clients for payload in payloads])</code> | Vergleicht sämtliche protokollierten Empfangslängen in der richtigen Reihenfolge mit den Längen der drei originalen Bytes-Nachrichten je Client. |
| 152 | <code>            self.assertEqual(len(server), 1 + len(clients) * (1 + len(payloads)))</code> | Verlangt die exakte Gesamtzahl der Serverzeilen und schließt dadurch unerwartete zusätzliche Ausgaben aus. |
| 153 | <code>            for client in clients:</code> | Durchläuft die tatsächlich erwarteten Clientnachweise des Falls. |
| 154 | <code>                lines = (BASE / f&quot;nachweise/run01/{tag}-{client}-tcp.txt&quot;).read_text().splitlines()</code> | Liest die gespeicherte Ausgabe des jeweiligen unveränderten Originalclients. |
| 155 | <code>                self.assertEqual(lines[0], &quot;Connected to 10.0.2.2:5000&quot;)</code> | Prüft den exakten gemeldeten Server-Endpunkt der Clientverbindung. |
| 156 | <code>                self.assertEqual([ast.literal_eval(line.removeprefix(&quot;Reply: &quot;)) for line in lines[1:]], payloads)</code> | Decodiert jede komplette Reply-Literalzeile und vergleicht die vollständige geordnete Bytesliste mit dem Original; zusätzliche, verkürzte oder veränderte Echo-Inhalte fallen auf. |
| 157 | <code>        self.assertEqual({p.name for p in (BASE / &quot;nachweise/run01&quot;).glob(&quot;*-tcp.txt&quot;)}, {&quot;basis-client-tcp.txt&quot;, &quot;basis-server-tcp.txt&quot;, &quot;erweitert-client-tcp.txt&quot;, &quot;erweitert-client2-tcp.txt&quot;, &quot;erweitert-server-tcp.txt&quot;})</code> | Verlangt genau die fünf erwarteten TCP-Nachweisdateien und erkennt fehlende oder überzählige Dateien. |
| 159 | <code>    def test_no_helper_files_in_tree_or_staging(self):</code> | Prüft das Arbeitsblattverzeichnis und die aktuelle Git-Stagingliste auf unerwünschte Hilfsartefakte, ohne etwas zu stagen oder zu committen. |
| 160 | <code>        def unwanted(path):</code> | Definiert die lokale Klassifikation unerwünschter Cache-, Sicherungs-, temporärer und Generator-Dateinamen. |
| 161 | <code>            return &quot;__pycache__&quot; in path.parts or path.suffix in {&quot;.pyc&quot;, &quot;.pyo&quot;, &quot;.tmp&quot;, &quot;.log&quot;, &quot;.bak&quot;, &quot;.swp&quot;} or path.name in {&quot;.DS_Store&quot;, &quot;generate_explanation.py&quot;}</code> | Erkennt Bytecodeverzeichnisse und die aufgeführten typischen Hilfsdateiendungen sowie zwei unerwünschte spezielle Dateinamen. |
| 162 | <code>        self.assertEqual([str(path.relative_to(BASE)) for path in BASE.rglob(&quot;*&quot;) if unwanted(path)], [])</code> | Verlangt, dass solche Hilfsartefakte im gesamten Blattbaum überhaupt nicht vorhanden sind. |
| 163 | <code>        result = subprocess.run([&quot;git&quot;, &quot;diff&quot;, &quot;--cached&quot;, &quot;--name-only&quot;, &quot;-z&quot;, &quot;--&quot;, &quot;ueb06&quot;], cwd=BASE.parent, capture_output=True, timeout=10)</code> | Fragt mit git diff --cached ausschließlich die vorgemerkten Blatt06-Dateinamen ab; NUL-Trennung behandelt Leerzeichen robust. |
| 164 | <code>        self.assertEqual(result.returncode, 0)</code> | Verlangt einen erfolgreichen Git-Abfragestatus statt eine fehlgeschlagene Abfrage als leere Liste zu akzeptieren. |
| 165 | <code>        self.assertFalse(any(unwanted(Path(os.fsdecode(name))) for name in result.stdout.split(b&quot;\0&quot;) if name))</code> | Decodiert alle tatsächlich vorgemerkten Dateinamen und verwirft die gleichen unerwünschten Hilfsartefakte auch im Index. |
| 168 | <code>if __name__ == &quot;__main__&quot;:</code> | Beschränkt den nachfolgenden Programmeinstieg auf direkten Skriptstart; ein Import allein führt ihn nicht aus. |
| 169 | <code>    before = snapshot()</code> | Erfasst vor allen Tests die Fingerabdrücke von Originalen, alten Erklärungen und echten Messdateien. |
| 170 | <code>    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SheetChecks)</code> | Lädt die neun Testmethoden automatisch aus SheetChecks. |
| 171 | <code>    result = unittest.TextTestRunner(verbosity=2).run(suite)</code> | Führt die komplette Testsuite mit ausführlichem echten unittest-Bericht aus. |
| 172 | <code>    unchanged = before == snapshot()</code> | Vergleicht nach dem Testlauf erneut den gesamten geschützten Dateisatz mit dem Anfangszustand. |
| 173 | <code>    print(f&quot;Originale, alte Erklärungen und run01 unverändert: {unchanged}&quot;)</code> | Druckt das tatsächliche Ergebnis dieser Unverändertheitsprüfung als True oder False. |
| 174 | <code>    print(&quot;Grenze: API-Test-Doubles + archivierte echte Linux-Namespace-Messungen; Mininet/OVS/xterm NICHT live verifiziert.&quot;)</code> | Druckt die Herkunftsgrenze: synthetische API-Tests und archivierte echte Linux-Namespace-Messungen, keine Mininet/OVS/xterm-Liveverifikation. |
| 175 | <code>    raise SystemExit(0 if result.wasSuccessful() and unchanged else 1)</code> | Beendet nur bei erfolgreicher Suite und unverändertem geschütztem Zustand mit Status null, ansonsten mit Status eins. |

## Unveränderte originale TCP-Dateien knapp erklärt

### [Angabe/tcp_client.py](Angabe/tcp_client.py)

- **Zeilen 1–4:** Shebang, ursprüngliche Modulbeschreibung und Socket-Standardbibliothek. Diese Originaldatei erhält ausdrücklich keinen eigenen KI-Header.
- **Zeilen 6–7:** Festes Serverziel `10.0.2.2`, TCP-Port `5000`. Der Client muss keine eigene Quell-IP hardcodieren; der Kernel wählt sie passend zum lokalen Interface und Routing.
- **Zeilen 9–11:** Öffnet einen IPv4-Stream-Socket als Kontextmanager, verbindet sich zum Server und meldet den Endpunkt. Beim Verlassen wird der Socket geschlossen.
- **Zeilen 13–17:** Enthält genau drei Bytes-Nachrichten `Network layer test 1\n` bis `Network layer test 3\n`. Das abschließende Newline ist Nutzinhalt, kein zu entfernender Darstellungsfehler.
- **Zeilen 18–19:** `sendall` sendet die kompletten jeweiligen Bytes; `recv(4096)` liest bis zu 4096 Antwortbytes und druckt deren Python-Bytesdarstellung. Ein einzelnes `recv` ist allgemein kein Nachrichten-Framing. Für den vorhandenen Lauf prüft der Gesamttest jede komplette Antwortbytefolge, nicht nur drei Reply-Markierungen.

### [Angabe/tcp_server.py](Angabe/tcp_server.py)

- **Zeilen 1–7:** Originalbeschreibung, Socketimport und Bindeadresse `10.0.2.2:5000` bleiben unverändert.
- **Zeilen 9–14:** Öffnet einen IPv4-TCP-Socket, erlaubt Wiederverwendung der lokalen Bindeadresse, bindet und aktiviert eine Warteschlange von fünf Verbindungen. Die Listening-Meldung dient dem Messrunner als tatsächliches Bereitschaftssignal.
- **Zeilen 16–18:** Akzeptiert wiederholt Verbindungen und protokolliert Client-IP und dynamischen Quellport. Daher kann derselbe unveränderte Server beide Clients nacheinander bedienen.
- **Zeilen 20–24:** Schließt jede akzeptierte Verbindung über einen Kontextmanager. Liest bis zu 4096 Bytes pro Schritt; ein leeres Bytesobjekt bedeutet geordnetes Verbindungsende, worauf die innere Schleife endet.
- **Zeilen 26–27:** Protokolliert die Länge der tatsächlich empfangenen Bytes und sendet exakt dieselben Bytes mit `sendall` zurück. Weder Zeichencodierung noch Inhalt werden verändert. Der Server bearbeitet Verbindungen seriell, nicht parallel.

### Weitere Originalinfrastruktur

[Angabe/topology.py](Angabe/topology.py) enthält die vier Basisknoten und drei TCLinks. [Angabe/start_lab.py](Angabe/start_lab.py) setzt explizit /24-LANs und das /30-Transitnetz; der Default-Mininet-/8-Plan ist daher hier nicht maßgeblich. Sein `input()`-Wartedialog ist keine Mininet-CLI. Seine originale `ping_ok`-Teilstringprüfung kann `100% packet loss` fälschlich als `0%` lesen; sie wurde nicht geändert und im Erweiterungsstarter nicht verwendet. Der [eigene Starter](ue6.7/start_erweitert.py) verwendet stattdessen Status und exakte 3/3-Zähler. Die gelieferten Shellskripte werden mit `bash -n` auf Syntax geprüft; Capture- und Traceroute-Läufe werden dadurch nicht als ausgeführt ausgegeben.

Alle gelieferten Dateien unter `Angabe` werden unmittelbar gegen die vollständigen Bytes und Namen des [Originalarchivs](Angabe/uebb6_template.zip) verglichen. Die [Aufgabenstellung](angabe_blatt06.pdf), Originale und archivierten Messungen bleiben erhalten. Es wird weder ein neuer Messlauf noch eine Abgabe-ZIP erzeugt, und kein Git-Commit oder Push ausgeführt.
