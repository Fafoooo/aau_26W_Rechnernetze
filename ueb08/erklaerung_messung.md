# Zeilenerklärung: messen.py

## Zweck und Ausführung

Diese Datei erzeugt **reale** eigene Pakete mit Linux-Netzwerk-Namespaces,
veth-Paaren und **Linux Bridge**. Sie ersetzt keinen Nachweis der originalen
Mininet-/OVS-Umgebung. Vor jeder Netzwerkänderung liegt ein erfolgreiches
`os.unshare(os.CLONE_NEWNET)`; es gibt keine Verbindung zur äußeren Host-NIC.
Auch `ip_forward` und Offload-Einstellungen betreffen ausschließlich eigene Namespaces/Ports.
Python mindestens 3.12 mit `os.unshare` und vorhandene Programme `ip`, `bridge`,
`nsenter`, `sysctl`, `ethtool`, `ping`, `dumpcap` sind nötig. Es wird nichts installiert.

```sh
# Aus ueb08: nur bei noch nicht vorhandenem Zielordner!
sudo -n /usr/bin/python3 -B messen.py
# Späterer, neuer Lauf ohne Überschreiben des dokumentierten run01:
sudo -n /usr/bin/python3 -B messen.py --out nachweise/run02
# Ohne sudo und ohne Netzwerk-/Dateiänderung:
/usr/bin/python3 -B messen.py --analyse
```

`run01` wurde am 2026-10-29 tatsächlich ausgeführt. Elf PCAPs enthalten die in
`nachweise/run01/results.json` aufgeführten Paketbestände. Erster ARP-Ping:
vier Frames; zweiter Ping: zwei Frames ohne ARP. Dynamische FDB: leer, danach
client1/p1 und server1/p3, danach zusätzlich client2/p2. Der stumme server2
lernt keinen Eintrag. Sein eigener Capture enthält beide ARP-Broadcasts,
aber kein ICMP. Die Learning-Captures laufen absichtlich zeitlich überlappend:
`83_ping1.pcap` enthält deshalb fünf Frames, darunter den späteren
ARP-Broadcast von client2. Das ist kein zusätzlicher Ping von client1.

Beim gerouteten Echo Request sind ID 28505 und Sequenz 1 identisch;
TTL 64→63 und IPv4-Checksumme 55588→55844 sind direkt aufgenommen und geprüft.
LAN A: client1-MAC→Router-A-MAC; LAN B: Router-B-MAC→server1-MAC.
Die IPs 10.0.1.2→10.0.2.10 bleiben erhalten. Der lokale Vergleichsping geht
stattdessen direkt an client2s MAC und hat als Request TTL 64.
HTTP läuft ausschließlich zwischen eigenen Sockets: 63 Anfragebytes,
148 Antwortbytes einschließlich Headern, davon 49 Bodybytes; zehn TCP-Pakete
je Messpunkt, vollständiger Handshake und zwei bestätigte FINs, kein RST.

`dumpcap -P` ist in der vorhandenen Version noch funktionsfähig, meldet aber
eine echte Deprecation-Warnung zugunsten `-F pcap`; diese Warnung bleibt im
Originalprotokoll erhalten. Die Reader-Unterstützung ist klassisches PCAP.
Captures enden per Dauerlimit; `communicate` leert stderr, bevor Prozesse
und Dateien eingesammelt werden. Ein erneuter Standardlauf scheitert
absichtlich am vorhandenen exklusiven Ordner, bevor neue Labornetzgeräte entstehen.
Bei Prozessende verschwinden die ausschließlich prozessgebundenen Namespaces;
es werden keine persistenten `ip netns`-Mounts angelegt.

## Jede nichtleere Originalzeile

Die Quellspalte ist wörtlich mit HTML-Escaping wiedergegeben; Einrückungen
gehören zum Vergleich. Leere Zeilen haben keine ausführbare oder dokumentierende Wirkung.

| Zeile | Originalquelle | Individuelle Begründung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.</code> | Kennzeichnet Tool, Modell und Anbieter des übernommenen Messcodes. |
| 2 | <code># Datum: 2026-10-29</code> | Hält das tatsächliche Erstellungsdatum für die KI-Regel fest. |
| 3 | <code># Anfrage: Echte isolierte Linux-Namespace-Messungen für RN Blatt08 mit PCAPs, JSON und Cleanup.</code> | Dokumentiert den Auftrag für diese Mess-Implementierung. |
| 4 | <code>&quot;&quot;&quot;Linux-Bridge-Ersatzmessung, ausdrücklich kein Mininet-/Open-vSwitch-Nachweis.&quot;&quot;&quot;</code> | Grenzt die Linux-Bridge-Messung ausdrücklich von Mininet und OVS ab. |
| 5 | <code>import argparse</code> | Ermöglicht getrennte CLI-Modi für Messung, Offline-Auswertung und eigene Hilfsprozesse. |
| 6 | <code>import json</code> | Serialisiert Messbefunde und FDB-Schnappschüsse ohne Python-spezifische Objekte. |
| 7 | <code>import os</code> | Liefert Namespace-Isolation, effektive Benutzerkennung, Pipe-Lesen und Eigentümerwechsel. |
| 8 | <code>import re</code> | Extrahiert den abschließenden dumpcap-Paketzähler statt Konsolentext nur zu schätzen. |
| 9 | <code>import selectors</code> | Wartet ereignisgesteuert auf Capture- und Server-Bereitschaft. |
| 10 | <code>import signal</code> | Lässt Namespace-Halter ohne aktive CPU-Schleife auf ihre Beendigung warten. |
| 11 | <code>import socket</code> | Erzeugt die eigenen echten TCP-Verbindungen für den HTTP-Nachweis. |
| 12 | <code>import subprocess</code> | Startet ip, bridge, dumpcap und die isolierten Python-Hilfsprozesse. |
| 14 | <code>import time</code> | Stellt monotone Bereitschaftsfristen und das tatsächliche Messdatum bereit. |
| 15 | <code>from pathlib import Path</code> | Behandelt Dateipfade relativ zum Aufgabenordner statt zum Aufrufverzeichnis. |
| 16 | <code>from pcap import echo_pairs, read_pcap, require, select, tcp_flow</code> | Verwendet die unabhängig implementierten PCAP- und Protokollprüfungen. |
| 18 | <code>BASE = Path(__file__).resolve().parent</code> | Verankert Ausgaben und Hilfsprozess-Skript am Ort dieser Datei. |
| 19 | <code>PYTHON = &quot;/usr/bin/python3&quot;</code> | Wählt ausdrücklich den System-Python mit os.unshare-Unterstützung, nicht einen anderen Shell-Python. |
| 20 | <code>REQUEST = b&quot;GET /blatt08 HTTP/1.1\r\nHost: server1.lab\r\nConnection: close\r\n\r\n&quot;</code> | Definiert die exakt erwartete HTTP-Anfrage einschließlich CRLF und leerer Abschlusszeile. |
| 21 | <code>BODY = b&quot;RN Blatt08: echte Pakete, zwei LANs, ein Router.\n&quot;</code> | Legt den ausschließlich eigenen, unkritischen Antwortinhalt fest. |
| 22 | <code>RESPONSE = b&quot;HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: &quot; + str(len(BODY)).encode() + b&quot;\r\nConnection: close\r\n\r\n&quot; + BODY</code> | Berechnet Content-Length aus den tatsächlichen Bodybytes und erstellt eine vollständige HTTP-Antwort. |
| 23 | <code>ADDRESSES = {&quot;client1&quot;: (&quot;10.0.1.2&quot;, &quot;00:00:00:00:00:01&quot;), &quot;client2&quot;: (&quot;10.0.1.3&quot;, &quot;00:00:00:00:00:02&quot;), &quot;server1&quot;: (&quot;10.0.1.10&quot;, &quot;00:00:00:00:00:03&quot;), &quot;server2&quot;: (&quot;10.0.1.11&quot;, &quot;00:00:00:00:00:04&quot;)}</code> | Übernimmt die vier vorgegebenen LAN-A-IP-Adressen und deterministischen Host-MACs. |
| 26 | <code>def worker(mode):</code> | Bündelt die drei kleinen Prozessrollen im eigenen Skript. |
| 27 | <code>    if mode == &quot;holder&quot;:</code> | Wählt die Rolle, die einen Host-Namespace am Leben hält. |
| 28 | <code>        os.unshare(os.CLONE_NEWNET)</code> | Erzeugt für diesen Host einen eigenen Netzwerk-Namespace, bevor seine Bereitschaft gemeldet wird. |
| 29 | <code>        print(&quot;READY&quot;, flush=True)</code> | Meldet erst nach erfolgreichem unshare die nutzbare Namespace-Referenz. |
| 30 | <code>        while True:</code> | Hält den Namespace so lange offen, bis Cleanup den Prozess beendet. |
| 31 | <code>            signal.pause()</code> | Blockiert wartend auf Signale statt künstlichen Netzwerkverkehr zu erzeugen. |
| 32 | <code>    if mode == &quot;http-server&quot;:</code> | Wählt den eigenen HTTP-Dienst im Server-Namespace. |
| 33 | <code>        with socket.socket() as listener:</code> | Öffnet einen IPv4-TCP-Listener mit automatischem Schließen beim Verlassen des Blocks. |
| 34 | <code>            listener.settimeout(8)</code> | Begrenzt insbesondere das Warten auf eine eingehende Verbindung. |
| 35 | <code>            listener.bind((&quot;10.0.2.10&quot;, 8080))</code> | Bindet ausschließlich die isolierte Serveradresse und den dokumentierten Dienstport. |
| 36 | <code>            listener.listen(1)</code> | Aktiviert den Listener mit Platz für die einzige erwartete Verbindung. |
| 37 | <code>            print(&quot;READY&quot;, flush=True)</code> | Gibt Bereitschaft erst nach bind und listen aus, sodass der Client nicht zu früh verbindet. |
| 38 | <code>            connection, _ = listener.accept()</code> | Nimmt genau die selbst gestartete Client-Verbindung entgegen. |
| 39 | <code>            with connection:</code> | Garantiert auch im Fehlerfall das Schließen des angenommenen Sockets. |
| 40 | <code>                connection.settimeout(5)</code> | Begrenzt blockierende Lese- und Schreiboperationen auf der Verbindung. |
| 41 | <code>                incoming = b&quot;&quot;</code> | Beginnt mit einem leeren Bytepuffer, unabhängig von recv-Grenzen. |
| 42 | <code>                while b&quot;\r\n\r\n&quot; not in incoming:</code> | Liest bis zum HTTP-Headerende, nicht nur bis zum ersten TCP-Segment. |
| 43 | <code>                    chunk = connection.recv(1024)</code> | Holt einen weiteren Teil der echten Anfrage aus dem Socket. |
| 44 | <code>                    require(chunk and len(incoming) + len(chunk) &lt;= 4096, &quot;HTTP-Anfrage fehlt/zu lang&quot;)</code> | Verwirft vorzeitiges EOF und einen über das Testlimit hinauswachsenden Header. |
| 45 | <code>                    incoming += chunk</code> | Fügt gelesene Teilstücke in ihrer Socket-Reihenfolge zusammen. |
| 46 | <code>                require(incoming == REQUEST, &quot;Andere HTTP-Anfrage&quot;)</code> | Akzeptiert ausschließlich die eigene, vollständig erwartete HTTP-Anfrage. |
| 47 | <code>                connection.sendall(RESPONSE)</code> | Sendet alle Antwortbytes und lässt sendall partielle Kernel-Schreibvorgänge behandeln. |
| 48 | <code>                connection.shutdown(socket.SHUT_WR)</code> | Schließt die Senderichtung geordnet und erzeugt damit ein TCP-FIN. |
| 49 | <code>                require(connection.recv(1) == b&quot;&quot;, &quot;Client schließt nicht sauber&quot;)</code> | Verlangt das geordnete EOF des Clients statt eines zusätzlichen Anwendungsbytes. |
| 50 | <code>            print(&quot;HTTP-Server: Anfrage korrekt, Antwort gesendet, EOF empfangen.&quot;)</code> | Protokolliert den tatsächlich abgeschlossenen Serveraustausch ohne private Systemdaten. |
| 51 | <code>    if mode == &quot;http-client&quot;:</code> | Wählt den eigenen HTTP-Client im client1-Namespace. |
| 52 | <code>        with socket.socket() as connection:</code> | Erzeugt den Client-TCP-Socket in der bereits betretenen Netzwerkumgebung. |
| 53 | <code>            connection.settimeout(5)</code> | Begrenzt Verbindungsaufbau und blockierende Client-I/O. |
| 54 | <code>            connection.bind((&quot;10.0.1.2&quot;, 40080))</code> | Fixiert die Labor-Quelladresse und den nachvollziehbaren Clientport 40080. |
| 55 | <code>            connection.connect((&quot;10.0.2.10&quot;, 8080))</code> | Verbindet tatsächlich zum Dienst hinter dem Router; keine externe Adresse wird verwendet. |
| 56 | <code>            connection.sendall(REQUEST)</code> | Übergibt die vollständige festgelegte Anfrage an TCP. |
| 57 | <code>            connection.shutdown(socket.SHUT_WR)</code> | Kündigt mit einem Half-Close das Ende der Client-Senderichtung an. |
| 58 | <code>            incoming = b&quot;&quot;</code> | Initialisiert die zu rekonstruierende HTTP-Antwort als Bytefolge. |
| 59 | <code>            while chunk := connection.recv(4096):</code> | Liest beliebig segmentierte Antwortdaten bis zum echten TCP-EOF. |
| 60 | <code>                require(len(incoming) + len(chunk) &lt;= 8192, &quot;HTTP-Antwort zu groß&quot;)</code> | Verhindert unbegrenztes Puffern bei einer unerwarteten Serverantwort. |
| 61 | <code>                incoming += chunk</code> | Hängt jedes gelesene Antwortstück verlustfrei an. |
| 62 | <code>            require(incoming == RESPONSE, &quot;Andere HTTP-Antwort&quot;)</code> | Prüft den vollständigen HTTP-Header und Body gegen die erwarteten Bytes. |
| 63 | <code>            print(f&quot;HTTP-Client: {len(REQUEST)} Anfragebytes, {len(incoming)} Antwortbytes, EOF empfangen.&quot;)</code> | Meldet reale Anwendungsbytezahlen und den beobachteten geordneten Abschluss. |
| 66 | <code>def ready(process, token, timeout=5):</code> | Definiert den Bereitschaftswächter für einen Prozess, ein Token und eine Gesamtfrist. |
| 67 | <code>    deadline, observed = time.monotonic() + timeout, b&quot;&quot;</code> | Fixiert eine einzige monotone Deadline und den bisher gelesenen stderr-Puffer. |
| 68 | <code>    with selectors.DefaultSelector() as selector:</code> | Schließt den Selector nach Erfolg oder Fehler zuverlässig. |
| 69 | <code>        selector.register(process.stderr, selectors.EVENT_READ)</code> | Beobachtet ausschließlich dumpcaps stderr-Pipe auf verfügbare Statusdaten. |
| 70 | <code>        while token not in observed:</code> | Wartet bis zum vollständigen File-Bereitschaftstoken, nicht nur auf den Prozessstart. |
| 71 | <code>            remaining = deadline - time.monotonic()</code> | Berechnet die Restfrist immer gegen dieselbe absolute Deadline. |
| 72 | <code>            require(remaining &gt; 0, &quot;Capture-Bereitschaft: Zeitlimit&quot;)</code> | Bricht bei Fristüberschreitung ab, auch wenn wiederholt keine Daten ankommen. |
| 73 | <code>            if not selector.select(min(0.2, remaining)):</code> | Wartet höchstens ein kurzes Intervall und nie länger als die noch erlaubte Zeit. |
| 74 | <code>                continue</code> | Behandelt ein leeres Selector-Ergebnis als Leerlauf, nicht als fehlgeschlagenen Capture-Start. |
| 75 | <code>            chunk = os.read(process.stderr.fileno(), 4096)</code> | Liest verfügbare Statusbytes direkt vom Pipe-Dateideskriptor. |
| 76 | <code>            require(chunk, &quot;Capture vor Bereitschaft beendet&quot;)</code> | Erkennt EOF vor der Bereitschaftsmeldung als gesonderten Fehler. |
| 77 | <code>            observed += chunk</code> | Bewahrt auch über mehrere Reads verteilte Statusmeldungen auf. |
| 78 | <code>    return observed</code> | Liefert die bereits konsumierten Meldungen für das vollständige Capture-Protokoll zurück. |
| 81 | <code>class Lab:</code> | Kapselt Prozesse, Dateigriffe und Befehlsbelege eines isolierten Messlaufs. |
| 82 | <code>    def __init__(self, out):</code> | Initialisiert die Laborverwaltung für einen exklusiv angelegten Ausgabeordner. |
| 83 | <code>        self.out, self.hosts, self.processes, self.log = out, {}, [], []</code> | Speichert den Ausgabeort und startet leere Host-, Prozess- und Befehlsverzeichnisse. |
| 84 | <code>        self.counts = {}</code> | Sammelt später die unabhängig nachgezählten Paketanzahlen je Capture. |
| 85 | <code>        self.outputs = []</code> | Registriert Capture-Dateigriffe, damit auch abgebrochene Versuche sie schließen. |
| 87 | <code>    def prefix(self, host):</code> | Baut optional das Namespace-Präfix für einen bestimmten Laborhost. |
| 88 | <code>        return [&quot;nsenter&quot;, &quot;-t&quot;, str(self.hosts[host].pid), &quot;-n&quot;, &quot;--&quot;] if host else []</code> | Betritt nur den Netzwerk-Namespace des bekannten Halters; ohne Host bleibt der äußere Labor-Namespace aktiv. |
| 90 | <code>    def run(self, host, *args):</code> | Führt einen begrenzten Laborbefehl aus, ohne eine Shell zur Interpretation zu benötigen. |
| 91 | <code>        result = subprocess.run(self.prefix(host) + list(args), capture_output=True, text=True, timeout=8)</code> | Erfasst stdout, stderr und Exitcode und verhindert unbeschränkt hängende Befehle. |
| 92 | <code>        self.log.append(f&quot;[{host or &#x27;switch&#x27;}] {&#x27; &#x27;.join(args)}\n{result.stdout}{result.stderr}RC={result.returncode}\n&quot;)</code> | Protokolliert den logischen Laborhost, Befehl, Ausgabe und tatsächlichen Exitcode. |
| 93 | <code>        require(result.returncode == 0, f&quot;Laborbefehl fehlgeschlagen: {args[0]}&quot;)</code> | Wertet Erfolg anhand des Exitcodes aus; 100 Prozent Verlust kann nicht als Erfolg durchrutschen. |
| 94 | <code>        return result.stdout.strip()</code> | Gibt die von umgebenden Leerzeichen befreite Befehlsausgabe an den Messablauf zurück. |
| 96 | <code>    def spawn(self, host, mode):</code> | Startet einen langlebigeren eigenen Worker im gewünschten Namespace. |
| 97 | <code>        process = subprocess.Popen(self.prefix(host) + [PYTHON, &quot;-B&quot;, str(BASE / &quot;messen.py&quot;), &quot;--worker&quot;, mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE)</code> | Verwendet das eigene Skript ohne Bytecode-Dateien und mit getrennten Ausgabepipes. |
| 98 | <code>        self.processes.append(process)</code> | Registriert jeden gestarteten Worker sofort für das spätere Cleanup. |
| 99 | <code>        return process</code> | Gibt den Prozessgriff zum Bereitschaftswarten und Einsammeln zurück. |
| 101 | <code>    def holder(self, name):</code> | Erstellt und konfiguriert einen benannten Host-Namespace. |
| 102 | <code>        process = self.spawn(None, &quot;holder&quot;)</code> | Startet den Namespace-Halter aus dem bereits isolierten äußeren Labor heraus. |
| 103 | <code>        self.hosts[name] = process</code> | Macht dessen Prozesskennung für spätere nsenter-Aufrufe auffindbar. |
| 104 | <code>        assert process.stdout is not None</code> | Sichert die vom Popen-Vertrag erwartete stdout-Pipe als interne Invariante ab. |
| 105 | <code>        with selectors.DefaultSelector() as selector:</code> | Verwaltet einen kurzlebigen Selector für die Halter-Bereitschaft. |
| 106 | <code>            selector.register(process.stdout, selectors.EVENT_READ)</code> | Beobachtet die stdout-Pipe des konkreten Halters. |
| 107 | <code>            require(selector.select(5) and process.stdout.readline() == b&quot;READY\n&quot;, &quot;Namespace-Halter nicht bereit&quot;)</code> | Verlangt innerhalb von fünf Sekunden die exakte READY-Zeile nach dessen unshare. |
| 108 | <code>        self.run(name, &quot;sysctl&quot;, &quot;-qw&quot;, &quot;net.ipv6.conf.all.disable_ipv6=1&quot;, &quot;net.ipv6.conf.default.disable_ipv6=1&quot;)</code> | Unterdrückt IPv6-Linklokalverkehr nur innerhalb des neuen Host-Namespace. |
| 109 | <code>        self.run(name, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, &quot;lo&quot;, &quot;up&quot;)</code> | Aktiviert das eigene Loopback-Gerät des isolierten Hosts. |
| 111 | <code>    def bridge(self, name):</code> | Legt eine benannte Linux-Bridge im äußeren Labor-Namespace an. |
| 112 | <code>        self.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;add&quot;, name, &quot;type&quot;, &quot;bridge&quot;, &quot;stp_state&quot;, &quot;0&quot;, &quot;forward_delay&quot;, &quot;0&quot;)</code> | Deaktiviert STP und Forward-Delay für die schleifenfreie eigene Sterntopologie. |
| 113 | <code>        self.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, name, &quot;up&quot;)</code> | Aktiviert die frisch angelegte Bridge für tatsächliche Frame-Weiterleitung. |
| 115 | <code>    def attach(self, host, interface, port, bridge, address, mac):</code> | Verbindet einen Host-Port mit der angegebenen Bridge und adressiert dessen Gegenstelle. |
| 116 | <code>        self.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;add&quot;, port, &quot;type&quot;, &quot;veth&quot;, &quot;peer&quot;, &quot;name&quot;, interface, &quot;netns&quot;, str(self.hosts[host].pid))</code> | Erstellt ein echtes veth-Paar und platziert die Hostseite direkt in dessen Netzwerk-Namespace. |
| 117 | <code>        self.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, port, &quot;master&quot;, bridge)</code> | Ordnet die äußere veth-Seite dem gewünschten LAN-Bridge-Master zu. |
| 118 | <code>        self.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, port, &quot;up&quot;)</code> | Aktiviert die Bridge-seitige Verbindung. |
| 119 | <code>        self.run(host, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, interface, &quot;address&quot;, mac)</code> | Setzt die nachvollziehbare vorgegebene MAC-Adresse der Hostschnittstelle. |
| 120 | <code>        self.run(host, &quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, address + &quot;/24&quot;, &quot;dev&quot;, interface)</code> | Konfiguriert die Host-IP mit dem ausdrücklich vorgegebenen /24-Präfix. |
| 121 | <code>        self.run(host, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, interface, &quot;up&quot;)</code> | Aktiviert die adressierte Hostschnittstelle. |
| 122 | <code>        for node, device in ((None, port), (host, interface)):</code> | Bearbeitet beide Enden des veth-Paares für konsistente Capture-Eigenschaften. |
| 123 | <code>            self.run(node, &quot;ethtool&quot;, &quot;-K&quot;, device, &quot;tx&quot;, &quot;off&quot;, &quot;rx&quot;, &quot;off&quot;, &quot;tso&quot;, &quot;off&quot;, &quot;gso&quot;, &quot;off&quot;, &quot;gro&quot;, &quot;off&quot;)</code> | Deaktiviert Checksum- und Segmentierungs-Offloads nur auf eigenen Ports, damit PCAP-Prüfsummen auswertbar sind. |
| 125 | <code>    def capture(self, host, filename):</code> | Startet eine zeitlich begrenzte Aufzeichnung auf einer eigenen Hostschnittstelle. |
| 126 | <code>        output = (self.out / filename).open(&quot;xb&quot;)</code> | Öffnet die PCAP exklusiv im Binärmodus; existierende Belege werden nicht überschrieben. |
| 127 | <code>        self.outputs.append(output)</code> | Merkt den Dateigriff bereits vor dem Prozessstart für einen möglichen Fehlerpfad. |
| 128 | <code>        command = self.prefix(host) + [&quot;dumpcap&quot;, &quot;-P&quot;, &quot;-i&quot;, host + &quot;-eth0&quot;, &quot;-f&quot;, &quot;arp or icmp or tcp&quot;, &quot;-s&quot;, &quot;65535&quot;, &quot;-a&quot;, &quot;duration:2&quot;, &quot;-w&quot;, &quot;-&quot;]</code> | Beschränkt Protokolle und Snaplen, wählt klassisches PCAP und lässt dumpcap nach zwei Sekunden normal auslaufen. |
| 129 | <code>        process = subprocess.Popen(command, stdout=output, stderr=subprocess.PIPE)</code> | Leitet rohe Capturebytes unmittelbar in die eigene PCAP-Datei und Statusmeldungen separat um. |
| 130 | <code>        self.processes.append(process)</code> | Registriert auch den Capture-Prozess sofort für das Cleanup. |
| 131 | <code>        try:</code> | Beginnt den abgesicherten Bereitschaftsschritt nach dem erfolgreichen Prozessstart. |
| 132 | <code>            startup = ready(process, b&quot;File: -&quot;)</code> | Wartet auf File: -, weil Capturing on allein eine zu frühe Startmeldung sein kann. |
| 133 | <code>        except BaseException:</code> | Fängt auch Unterbrechungen während des Bereitschaftswartens ab. |
| 134 | <code>            output.close()</code> | Schließt bei fehlgeschlagener Bereitschaft den offenen Capture-Dateigriff. |
| 135 | <code>            raise</code> | Reicht den ursprünglichen Startfehler weiter, statt einen scheinbaren Messbefund zu erstellen. |
| 136 | <code>        return process, output, startup, filename</code> | Bündelt Prozess, Datei, bereits gelesene Meldungen und Belegname für finish. |
| 138 | <code>    def finish(self, capture):</code> | Wartet auf das reguläre Ende einer begonnenen Capture-Aufzeichnung. |
| 139 | <code>        process, output, startup, filename = capture</code> | Entpackt die vom Capture-Start gelieferten Verwaltungsdaten. |
| 140 | <code>        try:</code> | Sichert das Schließen der Capture-Datei auch beim Timeout ab. |
| 141 | <code>            _, tail = process.communicate(timeout=6)</code> | Wartet auf dumpcaps eigenes Dauerlimit und leert gleichzeitig die restliche stderr-Pipe. |
| 142 | <code>        finally:</code> | Erzwingt den folgenden Dateischluss unabhängig vom Ausgang von communicate. |
| 143 | <code>            output.close()</code> | Schließt und damit finalisiert die stdout-PCAP-Datei. |
| 144 | <code>        text = (startup + tail).decode(&quot;utf8&quot;, errors=&quot;replace&quot;)</code> | Kombiniert frühe und späte Statusmeldungen ohne den Bereitschaftsteil zu verlieren. |
| 145 | <code>        (self.out / (filename + &quot;.txt&quot;)).write_text(text)</code> | Bewahrt die echte dumpcap-Ausgabe unter einem zum Capture passenden Namen auf. |
| 146 | <code>        require(process.returncode == 0, &quot;dumpcap fehlgeschlagen&quot;)</code> | Verlangt einen erfolgreichen Capture-Exit statt allein auf eine vorhandene Datei zu vertrauen. |
| 147 | <code>        count = re.search(r&quot;Packets captured: (\d+)&quot;, text)</code> | Sucht ausdrücklich den abschließenden Zähler, nicht die Zwischenstände der Fortschrittsanzeige. |
| 148 | <code>        if count is None:</code> | Erkennt fehlende Abschlussstatistik als unzureichenden Capture-Nachweis. |
| 149 | <code>            raise ValueError(&quot;dumpcap-Paketzähler fehlt&quot;)</code> | Meldet das Fehlen des Paketzählers mit einer konkreten Ursache. |
| 150 | <code>        packets = read_pcap(self.out / filename)</code> | Liest die gesicherte Datei unabhängig von dumpcap mit dem eigenen Parser. |
| 151 | <code>        require(len(packets) == int(count.group(1)), &quot;Parser-/Capture-Paketzahl verschieden&quot;)</code> | Vergleicht die vollständige Recordzahl mit dumpcaps realem Endzähler. |
| 152 | <code>        self.counts[filename] = len(packets)</code> | Speichert die verifizierte Anzahl für results.json. |
| 153 | <code>        return packets</code> | Stellt die vollständig geparsten Pakete gegebenenfalls zur weiteren Analyse bereit. |
| 155 | <code>    def ping(self, host, target, count=1):</code> | Führt einen echten Ping im gewählten Namespace mit begrenzter Paketanzahl aus. |
| 156 | <code>        return self.run(host, &quot;ping&quot;, &quot;-n&quot;, &quot;-c&quot;, str(count), &quot;-i&quot;, &quot;0.2&quot;, &quot;-W&quot;, &quot;1&quot;, target)</code> | Verhindert Namensauflösung, setzt ein kurzes Intervall und begrenzt das Warten auf Antworten. |
| 158 | <code>    def fdb(self):</code> | Liest die tatsächlich gelernte Forwarding-Datenbank von LAN A aus. |
| 159 | <code>        entries = json.loads(self.run(None, &quot;bridge&quot;, &quot;-j&quot;, &quot;fdb&quot;, &quot;show&quot;, &quot;br&quot;, &quot;brA&quot;))</code> | Verlangt JSON-Ausgabe der Linux-Bridge statt OVS-Kommandos vorzutäuschen. |
| 160 | <code>        return sorted([e for e in entries if &quot;master&quot; in e and &quot;permanent&quot; not in e.get(&quot;state&quot;, &quot;&quot;)], key=lambda e: e[&quot;mac&quot;])</code> | Entfernt permanente Eigen-/Multicast-Einträge und sortiert dynamisch gelernte MACs reproduzierbar. |
| 162 | <code>    def cleanup(self):</code> | Räumt alle von diesem Lab-Objekt selbst gestarteten Ressourcen auf. |
| 163 | <code>        for process in reversed(self.processes):</code> | Beendet spätere Anwendungen und Captures vor ihren früher gestarteten Namespace-Haltern. |
| 164 | <code>            if process.poll() is None:</code> | Prüft vor dem Signalisieren, ob der konkrete eigene Prozess noch lebt. |
| 165 | <code>                process.terminate()</code> | Fordert lebende eigene Prozesse zunächst mit SIGTERM zum Ende auf. |
| 166 | <code>            try:</code> | Beginnt das begrenzte Warten und Pipe-Leeren nach der Beendigungsanforderung. |
| 167 | <code>                process.communicate(timeout=3)</code> | Sammelt den Prozess und seine Pipes innerhalb von drei Sekunden ein. |
| 168 | <code>            except subprocess.TimeoutExpired:</code> | Erkennt einen Prozess, der die schonende Beendigung nicht rechtzeitig befolgt. |
| 169 | <code>                process.kill()</code> | Eskaliert ausschließlich für diesen registrierten Prozess auf SIGKILL. |
| 170 | <code>                process.communicate()</code> | Sammelt auch nach SIGKILL den Prozess ein und verhindert Zombies. |
| 171 | <code>        for output in self.outputs:</code> | Berücksichtigt alle Capture-Dateien, auch solche ohne erfolgreiches finish. |
| 172 | <code>            output.close()</code> | Schließt verbliebene Dateigriffe; erneutes Schließen bereits geschlossener Dateien ist erlaubt. |
| 173 | <code>        (self.out / &quot;befehle.txt&quot;).write_text(&quot;\n&quot;.join(self.log))</code> | Schreibt die tatsächlich ausgeführten Laborbefehle auch im Fehlerfall nieder. |
| 176 | <code>def analyse(out):</code> | Definiert die rein lesende Auswertung bereits gesicherter PCAP-Dateien. |
| 177 | <code>    load = lambda name: read_pcap(out / name)</code> | Vereinfacht das Laden benannter Belege aus genau dem gewählten Messordner. |
| 178 | <code>    for path in sorted(out.glob(&quot;*.pcap&quot;)):</code> | Prüft alle PCAP-Dateien dieses Ordners in stabiler Namensreihenfolge. |
| 179 | <code>        packets = read_pcap(path)</code> | Parst auch Belege, die später keinen eigenen Ergebnisblock erhalten. |
| 180 | <code>        for packet in packets:</code> | Durchläuft jeden tatsächlich gespeicherten Frame zur Prüfsummenvalidierung. |
| 181 | <code>            require(packet.get(&quot;ip_checksum_valid&quot;, True) and packet.get(&quot;icmp_checksum_valid&quot;, True) and packet.get(&quot;tcp_checksum_valid&quot;, True), &quot;Ungültige Paketprüfsumme&quot;)</code> | Verlangt für vorhandene IPv4-, ICMP- und TCP-Prüfsummen Gültigkeit; ARP hat solche Felder nicht. |
| 182 | <code>    ethernet = load(&quot;81_ethernet.pcap&quot;)</code> | Lädt die Aufzeichnung des vorgegebenen server1-zu-client1-Pings. |
| 183 | <code>    require(len(select(ethernet, &quot;icmp_type&quot;, 8)) == 4 and len(select(ethernet, &quot;icmp_type&quot;, 0)) == 4, &quot;8.1: Vier Echo-Paare fehlen&quot;)</code> | Verlangt vier Echo Requests und vier Echo Replies statt nur einen beispielhaften Frame. |
| 184 | <code>    first, second = load(&quot;82_erster_ping.pcap&quot;), load(&quot;82_zweiter_ping.pcap&quot;)</code> | Lädt den ersten und den getrennt aufgenommenen zweiten ARP-Versuch. |
| 185 | <code>    arp = select(first, &quot;ethertype&quot;, 0x806)</code> | Isoliert Ethernet-Frames mit dem ARP-EtherType 0x0806. |
| 186 | <code>    require(any(p[&quot;arp_op&quot;] == 1 and p[&quot;arp_tpa&quot;] == &quot;10.0.1.3&quot; for p in arp), &quot;8.2: ARP-Request fehlt&quot;)</code> | Prüft, dass der erste Versuch tatsächlich nach der MAC zu 10.0.1.3 fragt. |
| 187 | <code>    require(any(p[&quot;arp_op&quot;] == 2 and p[&quot;arp_sha&quot;] == &quot;00:00:00:00:00:02&quot; for p in arp), &quot;8.2: ARP-Reply fehlt&quot;)</code> | Verlangt eine wirkliche Antwort mit der vorgegebenen MAC von client2. |
| 188 | <code>    require(not select(second, &quot;ethertype&quot;, 0x806), &quot;8.2: Zweiter Ping erzeugte neues ARP&quot;)</code> | Belegt die Cache-Wirkung dadurch, dass im zweiten Capture gar kein ARP vorkommt. |
| 189 | <code>    witness = load(&quot;83_server2_zeuge.pcap&quot;)</code> | Lädt den unbeteiligten server2 als unabhängigen Empfänger von Broadcasts. |
| 190 | <code>    require(len(select(witness, &quot;arp_op&quot;, 1)) == 2 and not select(witness, &quot;proto&quot;, 1), &quot;8.3: Broadcast-/Unicast-Zeuge unerwartet&quot;)</code> | Verlangt zwei ARP-Anfragen, aber keinen ICMP-Unicast am unbeteiligten Bridge-Port. |
| 191 | <code>    pairs = echo_pairs(load(&quot;84_lanA.pcap&quot;), load(&quot;84_lanB.pcap&quot;))</code> | Ordnet den gerouteten Echo Request anhand seiner Identität vor und nach dem Router zu. |
| 192 | <code>    local = select(load(&quot;84_lokal.pcap&quot;), &quot;icmp_type&quot;, 8)</code> | Extrahiert den Echo Request des Vergleichspings innerhalb von LAN A. |
| 193 | <code>    require(len(local) == 1 and local[0][&quot;dst_mac&quot;] == &quot;00:00:00:00:00:02&quot;, &quot;8.4: Lokales MAC-Ziel falsch&quot;)</code> | Verlangt die direkte client2-Ziel-MAC statt der Router-MAC beim lokalen Ping. |
| 194 | <code>    http = tcp_flow(load(&quot;85_lanA.pcap&quot;), load(&quot;85_lanB.pcap&quot;), REQUEST, RESPONSE)</code> | Prüft den vollständigen HTTP/TCP-Fluss und beide Capture-Seiten gegen die tatsächlichen Anwendungsbytes. |
| 195 | <code>    return {&quot;8.1&quot;: {&quot;echo_requests&quot;: 4, &quot;echo_replies&quot;: 4, &quot;request&quot;: select(ethernet, &quot;icmp_type&quot;, 8)[0]}, &quot;8.2&quot;: {&quot;first_arp&quot;: arp, &quot;second_arp_count&quot;: 0}, &quot;8.3&quot;: {&quot;witness_broadcast_requests&quot;: 2, &quot;witness_icmp_count&quot;: 0}, &quot;8.4&quot;: {&quot;routed_echo_pairs&quot;: pairs, &quot;local_request&quot;: local[0]}, &quot;8.5&quot;: http}</code> | Gibt kompakte Aufgabenbefunde einschließlich realer ausgewählter Header und zugeordneter Router-Paare zurück. |
| 198 | <code>def measure(out):</code> | Führt den privilegierten, realen Messablauf in einem neuen äußeren Netzwerk-Namespace aus. |
| 199 | <code>    require(os.geteuid() == 0, &quot;Mit sudo -n /usr/bin/python3 -B messen.py starten&quot;)</code> | Verweigert fehlende Root-Rechte, bevor irgendeine Laborkonfiguration beginnt. |
| 200 | <code>    os.unshare(os.CLONE_NEWNET)</code> | Erzwingt die äußere Netzwerk-Isolation vor allen ip-, bridge- oder sysctl-Änderungen. |
| 201 | <code>    out.mkdir(parents=True, exist_ok=False)</code> | Legt den Belegordner exklusiv neu an; ein früherer Lauf führt zum Abbruch. |
| 202 | <code>    lab, state = Lab(out), {}</code> | Initialisiert Ressourcenverwaltung und die Sammlung tatsächlich gemessener Zustände. |
| 203 | <code>    try:</code> | Umfasst die gesamte eigentliche Laborkonfiguration mit garantiertem Cleanup. |
| 204 | <code>        lab.run(None, &quot;sysctl&quot;, &quot;-qw&quot;, &quot;net.ipv6.conf.all.disable_ipv6=1&quot;, &quot;net.ipv6.conf.default.disable_ipv6=1&quot;)</code> | Deaktiviert IPv6 nur im isolierten äußeren Namespace, auch für künftig erzeugte Ports. |
| 205 | <code>        lab.bridge(&quot;brA&quot;)</code> | Erzeugt das gemeinsame erste Ethernet-LAN als Linux-Bridge. |
| 206 | <code>        for number, (name, (address, mac)) in enumerate(ADDRESSES.items(), 1):</code> | Nummeriert die vier Hosts in Vorlagenreihenfolge für eindeutige Bridge-Portnamen. |
| 207 | <code>            lab.holder(name)</code> | Startet für jeden Host seinen eigenen Namespace-Halter. |
| 208 | <code>            lab.attach(name, name + &quot;-eth0&quot;, &quot;p&quot; + str(number), &quot;brA&quot;, address, mac)</code> | Verbindet und adressiert jeden Host mit seiner vorgegebenen LAN-A-Konfiguration. |
| 209 | <code>        cap = lab.capture(&quot;client1&quot;, &quot;81_ethernet.pcap&quot;)</code> | Startet vor Ü8.1 die Aufzeichnung direkt auf client1-eth0. |
| 210 | <code>        lab.ping(&quot;server1&quot;, &quot;10.0.1.2&quot;, 4)</code> | Sendet die verlangten vier echten Pings von server1 an client1. |
| 211 | <code>        lab.finish(cap)</code> | Lässt die Ethernet-Aufzeichnung regulär auslaufen und validiert ihre Recordzahl. |
| 212 | <code>        lab.run(&quot;client1&quot;, &quot;ip&quot;, &quot;neigh&quot;, &quot;flush&quot;, &quot;all&quot;)</code> | Entfernt client1s bisherige Nachbarzuordnungen für einen kontrollierten ARP-Erstversuch. |
| 213 | <code>        state[&quot;82_neigh_before&quot;] = lab.run(&quot;client1&quot;, &quot;ip&quot;, &quot;neigh&quot;)</code> | Speichert den tatsächlich leeren Cachezustand vor dem ersten Ping. |
| 214 | <code>        cap = lab.capture(&quot;client1&quot;, &quot;82_erster_ping.pcap&quot;)</code> | Startet einen eigenen Beleg für den ersten Ping zu client2. |
| 215 | <code>        lab.ping(&quot;client1&quot;, &quot;10.0.1.3&quot;)</code> | Löst die erste wirkliche ARP-Auflösung und den anschließenden ICMP-Austausch aus. |
| 216 | <code>        state[&quot;82_neigh_after_first&quot;] = lab.run(&quot;client1&quot;, &quot;ip&quot;, &quot;neigh&quot;)</code> | Speichert die vom Kernel danach gelernte client2-MAC und ihren Nachbarstatus. |
| 217 | <code>        lab.finish(cap)</code> | Finalisiert den ersten ARP-Versuch, bevor der separate zweite Versuch beginnt. |
| 218 | <code>        cap = lab.capture(&quot;client1&quot;, &quot;82_zweiter_ping.pcap&quot;)</code> | Erstellt eine getrennte PCAP für den unmittelbaren Cache-Vergleich. |
| 219 | <code>        lab.ping(&quot;client1&quot;, &quot;10.0.1.3&quot;)</code> | Sendet ohne erneutes Cache-Leeren den zweiten Ping zu demselben Nachbarn. |
| 220 | <code>        state[&quot;82_neigh_after_second&quot;] = lab.run(&quot;client1&quot;, &quot;ip&quot;, &quot;neigh&quot;)</code> | Sichert den erneut abgefragten Nachbarzustand nach dem zweiten Versuch. |
| 221 | <code>        lab.finish(cap)</code> | Schließt die zweite Aufzeichnung mitsamt ihrem eigenen dumpcap-Protokoll ab. |
| 222 | <code>        for name in ADDRESSES:</code> | Wählt vor dem Switch-Learning-Versuch alle vier tatsächlichen Hosts aus. |
| 223 | <code>            lab.run(name, &quot;ip&quot;, &quot;neigh&quot;, &quot;flush&quot;, &quot;all&quot;)</code> | Löscht deren Nachbareinträge, damit FDB-Leeren allein keinen unkontrollierten ARP-Zustand hinterlässt. |
| 224 | <code>        for number in range(1, 5):</code> | Durchläuft die vier Host-seitigen Bridge-Ports. |
| 225 | <code>            lab.run(None, &quot;bridge&quot;, &quot;fdb&quot;, &quot;flush&quot;, &quot;dev&quot;, &quot;p&quot; + str(number), &quot;master&quot;, &quot;dynamic&quot;)</code> | Löscht nur deren dynamisch gelernte Master-FDB-Einträge; permanente Bridge-Eigenadressen bleiben erhalten. |
| 226 | <code>        state[&quot;83_fdb_start&quot;] = lab.fdb()</code> | Sichert den gemessenen dynamischen FDB-Startzustand vor neuem Testverkehr. |
| 227 | <code>        witness = lab.capture(&quot;server2&quot;, &quot;83_server2_zeuge.pcap&quot;)</code> | Startet server2 als Broadcast-Zeugen, bevor beide Learning-Pings stattfinden. |
| 228 | <code>        capture1 = lab.capture(&quot;client1&quot;, &quot;83_ping1.pcap&quot;)</code> | Nimmt den ersten Learning-Ping zusätzlich am aktiven client1 auf. |
| 229 | <code>        lab.ping(&quot;client1&quot;, &quot;10.0.1.10&quot;)</code> | Lässt client1 zunächst real mit server1 kommunizieren. |
| 230 | <code>        state[&quot;83_fdb_after_ping1&quot;] = lab.fdb()</code> | Liest die nach diesem ersten Austausch tatsächlich gelernte FDB aus. |
| 231 | <code>        capture2 = lab.capture(&quot;client2&quot;, &quot;83_ping2.pcap&quot;)</code> | Beginnt den zweiten Learning-Beleg direkt am später sendenden client2. |
| 232 | <code>        lab.ping(&quot;client2&quot;, &quot;10.0.1.10&quot;)</code> | Lässt nun client2 real zu demselben server1 pingen. |
| 233 | <code>        state[&quot;83_fdb_after_ping2&quot;] = lab.fdb()</code> | Liest den FDB-Zustand nach dem zusätzlichen Quell-MAC-Lernen aus. |
| 234 | <code>        for cap in (witness, capture1, capture2):</code> | Fasst die überlappenden Learning-Aufzeichnungen für ihren regulären Abschluss zusammen. |
| 235 | <code>            lab.finish(cap)</code> | Wartet jede davon aus und vergleicht ihren Parserzähler mit dumpcap. |
| 236 | <code>        require(not state[&quot;83_fdb_start&quot;], &quot;8.3: FDB am Start nicht leer&quot;)</code> | Verlangt einen wirklich leeren dynamischen Startzustand als Voraussetzung der Interpretation. |
| 237 | <code>        require({e[&quot;mac&quot;] for e in state[&quot;83_fdb_after_ping1&quot;]} == {ADDRESSES[h][1] for h in (&quot;client1&quot;, &quot;server1&quot;)}, &quot;8.3: FDB nach Ping1 falsch&quot;)</code> | Prüft, dass nach Ping1 nur client1 und server1 gelernt wurden. |
| 238 | <code>        require({e[&quot;mac&quot;] for e in state[&quot;83_fdb_after_ping2&quot;]} == {ADDRESSES[h][1] for h in (&quot;client1&quot;, &quot;client2&quot;, &quot;server1&quot;)}, &quot;8.3: FDB nach Ping2 falsch&quot;)</code> | Prüft, dass nach Ping2 zusätzlich client2, aber nicht der stumme server2 gelernt wurde. |
| 239 | <code>        lab.bridge(&quot;brB&quot;)</code> | Fügt die zweite echte Ethernet-Bridge für den Routingversuch hinzu. |
| 240 | <code>        for number, name in ((3, &quot;server1&quot;), (4, &quot;server2&quot;)):</code> | Wählt die beiden Serverports zum Umzug in LAN B aus. |
| 241 | <code>            lab.run(None, &quot;ip&quot;, &quot;link&quot;, &quot;set&quot;, &quot;p&quot; + str(number), &quot;master&quot;, &quot;brB&quot;)</code> | Verschiebt diese Ports in die neue Bridge, statt zwei Subnetze auf dieselbe Broadcastdomäne zu legen. |
| 242 | <code>            lab.run(name, &quot;ip&quot;, &quot;addr&quot;, &quot;flush&quot;, &quot;dev&quot;, name + &quot;-eth0&quot;)</code> | Entfernt die bisherigen LAN-A-Adressen von den Serverinterfaces. |
| 243 | <code>            address = &quot;10.0.2.&quot; + (&quot;10&quot; if number == 3 else &quot;11&quot;)</code> | Bestimmt die vorgesehenen LAN-B-Hostnummern .10 und .11. |
| 244 | <code>            lab.run(name, &quot;ip&quot;, &quot;addr&quot;, &quot;add&quot;, address + &quot;/24&quot;, &quot;dev&quot;, name + &quot;-eth0&quot;)</code> | Adressiert die Server im neuen Subnetz 10.0.2.0/24. |
| 245 | <code>        lab.holder(&quot;router&quot;)</code> | Erstellt einen zusätzlichen isolierten Router-Namespace. |
| 246 | <code>        for side, number in ((&quot;A&quot;, 1), (&quot;B&quot;, 2)):</code> | Verknüpft die Bezeichnungen A/B mit den zugehörigen Subnetznummern. |
| 247 | <code>            lab.attach(&quot;router&quot;, &quot;router-&quot; + side, &quot;pr&quot; + side, &quot;br&quot; + side, f&quot;10.0.{number}.1&quot;, f&quot;02:00:00:00:0{number}:01&quot;)</code> | Verbindet den Router mit beiden LANs und setzt deren getrennte Gateway-IP- und MAC-Adressen. |
| 248 | <code>        lab.run(&quot;router&quot;, &quot;sysctl&quot;, &quot;-qw&quot;, &quot;net.ipv4.ip_forward=1&quot;)</code> | Aktiviert IPv4-Forwarding nur im Router-Namespace. |
| 249 | <code>        for name in ADDRESSES:</code> | Konfiguriert Hin- und Rückwege für alle vier Hosts. |
| 250 | <code>            gateway = &quot;10.0.1.1&quot; if name.startswith(&quot;client&quot;) else &quot;10.0.2.1&quot;</code> | Bestimmt für Clients das LAN-A-Gateway und für Server das LAN-B-Gateway. |
| 251 | <code>            lab.run(name, &quot;ip&quot;, &quot;route&quot;, &quot;add&quot;, &quot;default&quot;, &quot;via&quot;, gateway)</code> | Fügt pro Host die Route über den lokal erreichbaren Router hinzu. |
| 252 | <code>            lab.run(name, &quot;ip&quot;, &quot;neigh&quot;, &quot;flush&quot;, &quot;all&quot;)</code> | Entfernt alte Nachbarzustände vor dem Routingnachweis. |
| 253 | <code>        before, after = lab.capture(&quot;client1&quot;, &quot;84_lanA.pcap&quot;), lab.capture(&quot;server1&quot;, &quot;84_lanB.pcap&quot;)</code> | Startet getrennte Host-Captures auf beiden Seiten desselben Router-Hops. |
| 254 | <code>        lab.ping(&quot;client1&quot;, &quot;10.0.2.10&quot;)</code> | Sendet den echten ICMP-Ping von client1 in das andere Subnetz. |
| 255 | <code>        lab.finish(before)</code> | Finalisiert die Aufzeichnung vor dem Router. |
| 256 | <code>        lab.finish(after)</code> | Finalisiert die zugehörige Aufzeichnung nach dem Router. |
| 257 | <code>        cap = lab.capture(&quot;client1&quot;, &quot;84_lokal.pcap&quot;)</code> | Erstellt einen eigenständigen Beleg für den lokalen Vergleichsping. |
| 258 | <code>        lab.ping(&quot;client1&quot;, &quot;10.0.1.3&quot;)</code> | Ping innerhalb von LAN A liefert den Vergleich ohne Router-Hop. |
| 259 | <code>        lab.finish(cap)</code> | Schließt diesen lokalen Vergleich samt Paketzähler ab. |
| 260 | <code>        before, after = lab.capture(&quot;client1&quot;, &quot;85_lanA.pcap&quot;), lab.capture(&quot;server1&quot;, &quot;85_lanB.pcap&quot;)</code> | Startet beide Capture-Seiten schon vor dem TCP-Verbindungsaufbau des HTTP-Versuchs. |
| 261 | <code>        server = lab.spawn(&quot;server1&quot;, &quot;http-server&quot;)</code> | Startet den eigenen HTTP-Dienst ausschließlich im server1-Namespace. |
| 262 | <code>        assert server.stdout is not None</code> | Sichert die für die Server-Bereitschaft angelegte stdout-Pipe intern ab. |
| 263 | <code>        with selectors.DefaultSelector() as selector:</code> | Begrenzt das ereignisgesteuerte Warten auf den HTTP-Listener. |
| 264 | <code>            selector.register(server.stdout, selectors.EVENT_READ)</code> | Beobachtet die stdout-Bereitschaft dieses konkreten Serverprozesses. |
| 265 | <code>            require(selector.select(5) and server.stdout.readline() == b&quot;READY\n&quot;, &quot;HTTP-Server nicht bereit&quot;)</code> | Verlangt READY nach erfolgreichem listen, bevor der Client gestartet wird. |
| 266 | <code>        client = lab.spawn(&quot;client1&quot;, &quot;http-client&quot;)</code> | Startet den tatsächlichen HTTP-Client in client1s isolierter Netzwerkumgebung. |
| 267 | <code>        for name, process in ((&quot;client&quot;, client), (&quot;server&quot;, server)):</code> | Sammelt beide Anwendungen mit sprechenden Belegnamen ein. |
| 268 | <code>            stdout, stderr = process.communicate(timeout=8)</code> | Wartet begrenzt auf deren Ende und leert gleichzeitig beide Ausgabepipes. |
| 269 | <code>            require(process.returncode == 0, &quot;HTTP-Prozess fehlgeschlagen&quot;)</code> | Verlangt den erfolgreichen Bytevergleich in Client und Server. |
| 270 | <code>            (out / (&quot;85_http_&quot; + name + &quot;.txt&quot;)).write_text((stdout + stderr).decode())</code> | Schreibt die echten Anwendungsausgaben getrennt von den Capture-Protokollen nieder. |
| 271 | <code>        lab.finish(before)</code> | Wartet den LAN-A-Capture regulär aus, einschließlich der letzten TCP-Abschlusssegmente. |
| 272 | <code>        lab.finish(after)</code> | Finalisiert anschließend den zugehörigen LAN-B-Capture. |
| 273 | <code>        results = {&quot;provenance&quot;: &quot;Echte Linux-Netzwerk-Namespaces, veth, Linux Bridge; NICHT Mininet/OVS&quot;, &quot;date&quot;: time.strftime(&quot;%Y-%m-%d&quot;), &quot;state&quot;: state, &quot;capture_packet_counts&quot;: lab.counts, &quot;analysis&quot;: analyse(out)}</code> | Bündelt reale Herkunft, Datum, Zustände, Paketzähler und aus den PCAPs neu berechnete Analyse. |
| 274 | <code>        (out / &quot;results.json&quot;).write_text(json.dumps(results, indent=2, ensure_ascii=False) + &quot;\n&quot;)</code> | Speichert die maschinenlesbare Gesamtauswertung mit lesbaren Unicode-Zeichen. |
| 275 | <code>        (out / &quot;zustand.txt&quot;).write_text(json.dumps(state, indent=2, ensure_ascii=False) + &quot;\n&quot;)</code> | Stellt Nachbartabellen und FDB-Schnappschüsse zusätzlich als eigenen lesbaren Beleg bereit. |
| 276 | <code>    finally:</code> | Erzwingt den Aufräumpfad auch bei einem fehlgeschlagenen Befehl oder Analysefehler. |
| 277 | <code>        lab.cleanup()</code> | Beendet und sammelt alle eigenen Prozesse ein und schließt deren Dateien. |
| 278 | <code>        if &quot;SUDO_UID&quot; in os.environ:</code> | Erkennt einen sudo-Aufruf, dessen Ergebnisse dem aufrufenden Benutzer gehören sollen. |
| 279 | <code>            for item in [out, *out.rglob(&quot;*&quot;)]:</code> | Wählt ausschließlich den eigenen Ergebnisordner und seine Belege für den Eigentümerwechsel aus. |
| 280 | <code>                os.chown(item, int(os.environ[&quot;SUDO_UID&quot;]), int(os.environ[&quot;SUDO_GID&quot;]))</code> | Macht die selbst erzeugten Root-Belege für den sudo-Aufrufer weiterbearbeitbar. |
| 281 | <code>    print(json.dumps({&quot;output&quot;: str(out.relative_to(BASE)), &quot;captures&quot;: lab.counts, &quot;verified&quot;: True}, indent=2))</code> | Gibt erst nach vollständiger Messung und Cleanup den relativen Ergebnisort und verifizierte Zähler aus. |
| 284 | <code>def main():</code> | Definiert den einzigen öffentlichen CLI-Einstiegspunkt. |
| 285 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Verwendet die ehrliche Ersatzmessungsbeschreibung auch in der CLI-Hilfe. |
| 286 | <code>    parser.add_argument(&quot;--worker&quot;, choices=(&quot;holder&quot;, &quot;http-server&quot;, &quot;http-client&quot;), help=argparse.SUPPRESS)</code> | Erlaubt nur die drei bekannten internen Prozessrollen und verbirgt sie aus normaler Hilfsausgabe. |
| 287 | <code>    parser.add_argument(&quot;--out&quot;, default=&quot;nachweise/run01&quot;, help=&quot;Neuer, exklusiver Belegordner relativ zu ueb08&quot;)</code> | Bietet einen dokumentierten neuen Ergebnisordner; der Standard bewahrt den ersten Messlauf. |
| 288 | <code>    parser.add_argument(&quot;--analyse&quot;, action=&quot;store_true&quot;, help=&quot;Nur gesicherte PCAPs auswerten, ohne sudo/Netzänderung&quot;)</code> | Stellt explizit einen rein lesenden Analysemodus ohne Root oder Netzwerkänderungen bereit. |
| 289 | <code>    args = parser.parse_args()</code> | Parst und validiert die vom Benutzer übergebenen CLI-Argumente. |
| 290 | <code>    if args.worker:</code> | Erkennt den internen Prozessaufruf statt einen weiteren Messlauf zu starten. |
| 291 | <code>        worker(args.worker)</code> | Führt nur die gewählte Halter- oder HTTP-Aufgabe aus. |
| 292 | <code>        return</code> | Beendet den internen Aufruf ohne nachfolgende Ordneranlage. |
| 293 | <code>    out = (BASE / args.out).resolve()</code> | Löst den gewählten Ausgabepfad kanonisch relativ zu diesem Aufgabenordner auf. |
| 294 | <code>    require(out.is_relative_to(BASE / &quot;nachweise&quot;) and out != BASE / &quot;nachweise&quot;, &quot;Output muss unter nachweise liegen&quot;)</code> | Verhindert Ausgaben außerhalb des eigenen nachweise-Unterbaums oder direkt in dessen Wurzel. |
| 295 | <code>    if args.analyse:</code> | Unterscheidet ausdrücklich reine Auswertung von privilegierter Paketmessung. |
| 296 | <code>        print(json.dumps(analyse(out), indent=2, ensure_ascii=False))</code> | Gibt die aus vorhandenen PCAPs neu berechneten Ergebnisse ohne Dateischreibzugriff aus. |
| 297 | <code>    else:</code> | Wählt andernfalls den vollständigen realen Messpfad. |
| 298 | <code>        measure(out)</code> | Übergibt den bereits validierten exklusiven Ergebnisort an die Messroutine. |
| 301 | <code>if __name__ == &quot;__main__&quot;:</code> | Verhindert eine versehentliche Messung beim Import durch Tests oder Teilaufgaben-CLIs. |
| 302 | <code>    main()</code> | Startet die Argumentauswertung nur bei direkter Skriptausführung. |

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol, ChatGPT or Codex Subscription; 2026-10-29. Auftrag: eigene reale Messimplementierung und exakte Zeilenerklärung für RN Blatt08.
