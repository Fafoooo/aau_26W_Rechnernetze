# Zeilenweise Erklärung – Routingaufgaben 6.1 bis 6.3
Erstellt mit Hermes Agent, OpenAI gpt-6.1-sol; Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29. Anfrage: Erkläre jede nichtleere Zeile des eigenen Routingcodes einzeln und nummeriert.
Jede Tabellenzeile bezieht sich auf genau die angegebene physische Zeilennummer der verlinkten Quelldatei. Leerzeilen werden ausgelassen; Shebangs, Kommentare, fortgesetzte Datenzeilen und schließende Klammern werden mit erklärt. Die Originaldateien unter Angabe werden hier weder verändert noch als eigener Code ausgegeben.
**Messgrenze:** 6.1/6.2 verwenden standardmäßig den Sollplan. 6.1 kann übergebene echte ip-JSON-Aufnahmen auswerten. Die NodeDouble-Tests von 6.3 erzeugen ausdrücklich synthetische Rückgaben; nur ein tatsächlicher Labaufruf kann echte Pakete nachweisen. Ohne installiertes Mininet ist dessen Ausführung nicht verifiziert.

## [ue6.1/adressen.py](ue6.1/adressen.py)
| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code>#!/usr/bin/env python3</code> | Shebang: Beim direkten Start wird python3 über PATH gesucht; mit python3 datei.py ist dieselbe Datei nutzbar. |
| 2 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.</code> | Kennzeichnet den KI-Anteil und nennt Tool sowie exaktes Modell; kein ausführbarer Programmcode. |
| 3 | <code># Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | Dokumentiert den vorgegebenen Anbieter und das Erstellungsdatum; kein Laufzeitdatum wird behauptet. |
| 4 | <code># Anfrage: Implementiere 6.1: Adresstabelle, Plan oder ip -j addr, mit Tests.</code> | Hält die tatsächliche Teilanfrage als Kommentar fest und erfüllt damit die Kennzeichnung direkt übernommenen Codes. |
| 5 | <code>&quot;&quot;&quot;Adressplan oder explizit übergebene IPv4-Interface-Messdaten auswerten.&quot;&quot;&quot;</code> | Modul-Docstring: beschreibt Plan- und JSON-Auswertung; wird außerdem als Kommandozeilenbeschreibung benutzt. |
| 6 | <code>import argparse</code> | Lädt argparse für --json, --host, --test und automatisch erzeugte Hilfe. |
| 7 | <code>import ipaddress</code> | Lädt die Standardbibliothek für korrekte IPv4-Adressen, Präfixe und Netzberechnung. |
| 8 | <code>import json</code> | Lädt den Parser für die JSON-Ausgabe von ip -j addr. |
| 9 | <code>import sys</code> | Stellt sys.stdin bereit, damit --json - eine Pipeline lesen kann. |
| 10 | <code>from pathlib import Path</code> | Importiert Path für das Lesen einer ausdrücklich genannten JSON-Datei. |
| 12 | <code>PLAN = {</code> | Beginnt das Dictionary des unveränderlichen fachlichen Sollplans; dies liest keine Netzwerkkonfiguration aus. |
| 13 | <code>    &quot;client&quot;: [(&quot;client-eth0&quot;, &quot;10.0.1.2/24&quot;)],</code> | Ordnet dem Client sein einziges Dateninterface und dessen Adresse mit /24 zu. |
| 14 | <code>    &quot;r1&quot;: [(&quot;r1-eth0&quot;, &quot;10.0.1.1/24&quot;), (&quot;r1-eth1&quot;, &quot;10.0.12.1/30&quot;)],</code> | Ordnet r1 die Client-LAN-Adresse und die erste Adresse des /30-Transitnetzes zu. |
| 15 | <code>    &quot;r2&quot;: [(&quot;r2-eth0&quot;, &quot;10.0.12.2/30&quot;), (&quot;r2-eth1&quot;, &quot;10.0.2.1/24&quot;)],</code> | Ordnet r2 die zweite Transitadresse und die Server-LAN-Adresse zu. |
| 16 | <code>    &quot;server&quot;: [(&quot;server-eth0&quot;, &quot;10.0.2.2/24&quot;)],</code> | Ordnet dem Server sein Dateninterface mit der vorgegebenen /24-Adresse zu. |
| 17 | <code>}</code> | Schließt das Plan-Dictionary syntaktisch ab. |
| 20 | <code>def rows(host, interfaces):</code> | Definiert einen Generator, der aus Knotenlabel und Interfacepaaren Tabellenzeilen berechnet. |
| 21 | <code>    for name, address in interfaces:</code> | Zerlegt jedes Paar in Interfacename und Adresse einschließlich Präfix. |
| 22 | <code>        interface = ipaddress.IPv4Interface(address)</code> | Validiert Adresse/Präfix als IPv4Interface; dessen network berücksichtigt die tatsächliche Netzmaske. |
| 23 | <code>        yield host, name, str(interface.ip), f&quot;/{interface.network.prefixlen}&quot;, str(interface.network)</code> | Liefert genau fünf Spalten: Label, Interface, reine IP, Präfix und normalisierte Netzadresse. |
| 26 | <code>def measured(host, data):</code> | Definiert den Adapter für bereits aufgenommene ip-JSON-Daten; er führt selbst keinen ip-Befehl aus. |
| 27 | <code>    for interface in data:</code> | Durchläuft alle in der JSON-Liste enthaltenen Interfaces, einschließlich eines eventuell vorhandenen lo. |
| 28 | <code>        for address in interface.get(&quot;addr_info&quot;, []):</code> | Durchläuft jede Adresse eines Interfaces; fehlendes addr_info wird wie eine leere Liste behandelt. |
| 29 | <code>            if address.get(&quot;family&quot;) == &quot;inet&quot;:</code> | Wählt nur IPv4-Einträge mit family inet; IPv6 wird bewusst übersprungen. |
| 30 | <code>                yield from rows(host, [(interface[&quot;ifname&quot;], f&quot;{address[&#x27;local&#x27;]}/{address[&#x27;prefixlen&#x27;]}&quot;)])</code> | Baut local/prefixlen zusammen und reicht das Interface an die gemeinsame Berechnung weiter; yield from delegiert deren Ausgabe. |
| 33 | <code>def self_test():</code> | Beginnt die ohne Netzwerkrechte ausführbaren Selbsttests. |
| 34 | <code>    result = [row for host, interfaces in PLAN.items() for row in rows(host, interfaces)]</code> | Berechnet alle Sollplanzeilen mit verschachtelter List Comprehension. |
| 35 | <code>    assert len(result) == 6</code> | Prüft, dass alle sechs vorgegebenen Dateninterfaces vorkommen. |
| 36 | <code>    assert {row[4] for row in result} == {&quot;10.0.1.0/24&quot;, &quot;10.0.12.0/30&quot;, &quot;10.0.2.0/24&quot;}</code> | Vergleicht die berechneten Netzadressen exakt mit den drei erwarteten Netzen. |
| 37 | <code>    fixture = [{&quot;ifname&quot;: &quot;probe&quot;, &quot;addr_info&quot;: [</code> | Beginnt eine ausdrücklich synthetische ip-JSON-Teststruktur mit Interface probe. |
| 38 | <code>        {&quot;family&quot;: &quot;inet&quot;, &quot;local&quot;: &quot;10.0.12.2&quot;, &quot;prefixlen&quot;: 30}, {&quot;family&quot;: &quot;inet6&quot;}]}]</code> | Ergänzt eine IPv4-/30-Adresse und einen IPv6-Eintrag; Letzterer muss ignoriert werden. |
| 39 | <code>    assert list(measured(&quot;r2&quot;, fixture)) == [(&quot;r2&quot;, &quot;probe&quot;, &quot;10.0.12.2&quot;, &quot;/30&quot;, &quot;10.0.12.0/30&quot;)]</code> | Prüft alle fünf Ausgabefelder und dass nur die IPv4-Adresse aus dem Testdatensatz übrig bleibt. |
| 40 | <code>    assert list(measured(&quot;r1&quot;, [{&quot;ifname&quot;: &quot;leer&quot;}])) == []</code> | Prüft ein Interface ohne addr_info; es darf keine Adresszeile erzeugen. |
| 41 | <code>    assert list(rows(&quot;x&quot;, [(&quot;lo&quot;, &quot;127.0.0.1/8&quot;)]))[0][4] == &quot;127.0.0.0/8&quot;</code> | Prüft anhand eines synthetischen Loopback-Beispiels die Berechnung von 127.0.0.0/8. |
| 42 | <code>    print(&quot;Selbsttest: Plan, Präfix, IPv4-Filter, leeres Interface und Loopback OK.&quot;)</code> | Gibt die Erfolgsmeldung erst nach sämtlichen Assertions aus; ohne -O starten, damit Assertions aktiv bleiben. |
| 45 | <code>def main():</code> | Definiert den Einstieg für die Kommandozeilenbedienung. |
| 46 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erzeugt den Argumentparser und übernimmt den Docstring als Erklärung. |
| 47 | <code>    parser.add_argument(&quot;--json&quot;, metavar=&quot;DATEI&quot;, help=&quot;ip -j addr; - liest stdin&quot;)</code> | Registriert den JSON-Dateiparameter; der besondere Name - bedeutet stdin. |
| 48 | <code>    parser.add_argument(&quot;--host&quot;, choices=tuple(PLAN), help=&quot;Knotenlabel der JSON-Aufnahme&quot;)</code> | Verlangt bei einem angegebenen Label einen der vier bekannten Knotennamen; JSON selbst garantiert dieses Label nicht. |
| 49 | <code>    parser.add_argument(&quot;--test&quot;, action=&quot;store_true&quot;)</code> | Registriert den booleschen Selbsttestschalter, der ohne zusätzlichen Wert angegeben wird. |
| 50 | <code>    args = parser.parse_args()</code> | Liest und validiert die Argumente des tatsächlichen Aufrufs. |
| 51 | <code>    if args.test:</code> | Wählt den Selbsttestpfad, wenn --test gesetzt ist. |
| 52 | <code>        self_test()</code> | Führt die tatsächlichen Python-Selbsttests aus. |
| 53 | <code>        return</code> | Beendet main danach, sodass kein Plan mit Testausgaben vermischt wird. |
| 54 | <code>    if args.json:</code> | Unterscheidet den expliziten JSON-Modus vom standardmäßigen Sollplan. |
| 55 | <code>        if not args.host:</code> | Prüft, ob zur Aufnahme auch ein Knotenlabel angegeben wurde. |
| 56 | <code>            parser.error(&quot;--json verlangt --host; der JSON-Inhalt nennt den Mininet-Knoten nicht&quot;)</code> | Bricht bei fehlendem Label mit argparse-Fehlerstatus 2 ab statt eine Herkunft zu erfinden. |
| 57 | <code>        data = json.load(sys.stdin) if args.json == &quot;-&quot; else json.loads(Path(args.json).read_text())</code> | Liest JSON direkt aus stdin oder liest den Dateitext mit Path und parst ihn anschließend. |
| 58 | <code>        result = list(measured(args.host, data))</code> | Materialisiert alle aus den aufgenommenen IPv4-Adressen berechneten Zeilen. |
| 59 | <code>        print(f&quot;Quelle: übergebenes ip-JSON für {args.host}; Herkunft vom Aufnehmenden zu prüfen.&quot;)</code> | Kennzeichnet die Datenquelle und macht deutlich, dass das Label vom Benutzer geprüft werden muss. |
| 60 | <code>    else:</code> | Beginnt den Alternativzweig ohne JSON-Aufnahme. |
| 61 | <code>        if args.host:</code> | Erkennt ein allein angegebenes --host als missverständlichen Aufruf. |
| 62 | <code>            parser.error(&quot;--host ist nur zusammen mit --json sinnvoll&quot;)</code> | Meldet dafür einen Argumentfehler, statt heimlich nur einen Teil des Plans auszugeben. |
| 63 | <code>        result = [row for host, interfaces in PLAN.items() for row in rows(host, interfaces)]</code> | Berechnet für den Planmodus alle Tabellenzeilen aus PLAN. |
| 64 | <code>        print(&quot;Quelle: deterministischer Sollplan aus Angabe/start_lab.py; KEINE Messung.&quot;)</code> | Kennzeichnet die Ausgabe ausdrücklich als Sollplan und nicht als Messung. |
| 65 | <code>    print(&quot;&#124; Hostname/Knoten &#124; Interface &#124; IPv4-Adresse &#124; Präfix &#124; Netzwerk &#124;&quot;)</code> | Druckt die fünf verlangten Markdown-Spaltenüberschriften. |
| 66 | <code>    print(&quot;&#124;---&#124;---&#124;---&#124;---&#124;---&#124;&quot;)</code> | Druckt die zu Markdown gehörende Trennzeile mit genau fünf Spalten. |
| 67 | <code>    for row in result:</code> | Durchläuft die tatsächlich vorbereiteten Ergebniszeilen. |
| 68 | <code>        print(&quot;&#124; &quot; + &quot; &#124; &quot;.join(row) + &quot; &#124;&quot;)</code> | Verbindet deren fünf Strings mit Tabellentrennern und gibt genau eine Markdown-Zeile aus. |
| 71 | <code>if __name__ == &quot;__main__&quot;:</code> | Führt main nur beim direkten Skriptstart aus; Importieren stellt lediglich Funktionen bereit. |
| 72 | <code>    main()</code> | Ruft die Kommandozeilenlogik auf. |

## [ue6.2/routing.py](ue6.2/routing.py)
| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code>#!/usr/bin/env python3</code> | Shebang: Beim direkten Start wird python3 über PATH gesucht; mit python3 datei.py ist dieselbe Datei nutzbar. |
| 2 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.</code> | Kennzeichnet den KI-Anteil und nennt Tool sowie exaktes Modell; kein ausführbarer Programmcode. |
| 3 | <code># Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | Dokumentiert den vorgegebenen Anbieter und das Erstellungsdatum; kein Laufzeitdatum wird behauptet. |
| 4 | <code># Anfrage: Implementiere 6.2: Forwardingtabellen, beide Paketwege, LPM und Tests.</code> | Hält die tatsächliche Teilanfrage als Kommentar fest und erfüllt damit die Kennzeichnung direkt übernommenen Codes. |
| 5 | <code>&quot;&quot;&quot;Deterministisches IPv4-Routingmodell; keine ausgelesenen Kernelrouten.&quot;&quot;&quot;</code> | Kennzeichnet das ganze Modul als deterministisches Routingmodell, nicht als Kernelmessung. |
| 6 | <code>import argparse</code> | Lädt argparse für --test und --help. |
| 7 | <code>from ipaddress import IPv4Address, IPv4Network</code> | Importiert IPv4Address für das Ziel und IPv4Network für Präfixvergleich und LPM. |
| 9 | <code>TABLES = {</code> | Beginnt die Modell-Haupttabellen aller vier Knoten; jeder Eintrag besteht aus Netz, Gateway oder None und Interface. |
| 10 | <code>    &quot;client&quot;: [(&quot;10.0.1.0/24&quot;, None, &quot;client-eth0&quot;), (&quot;0.0.0.0/0&quot;, &quot;10.0.1.1&quot;, &quot;client-eth0&quot;)],</code> | Definiert Client-LAN direkt und Default Route über r1; None bezeichnet einen direkt angeschlossenen Nachbarn. |
| 11 | <code>    &quot;r1&quot;: [(&quot;10.0.1.0/24&quot;, None, &quot;r1-eth0&quot;), (&quot;10.0.12.0/30&quot;, None, &quot;r1-eth1&quot;),</code> | Beginnt r1 mit seinen beiden angeschlossenen Netzen und ihren unterschiedlichen Interfaces. |
| 12 | <code>           (&quot;10.0.2.0/24&quot;, &quot;10.0.12.2&quot;, &quot;r1-eth1&quot;)],</code> | Ergänzt r1s einzige explizite Route zum Server-LAN über r2 im Transitnetz. |
| 13 | <code>    &quot;r2&quot;: [(&quot;10.0.12.0/30&quot;, None, &quot;r2-eth0&quot;), (&quot;10.0.2.0/24&quot;, None, &quot;r2-eth1&quot;),</code> | Beginnt r2 mit Transitnetz und direkt angeschlossenem Server-LAN. |
| 14 | <code>           (&quot;10.0.1.0/24&quot;, &quot;10.0.12.1&quot;, &quot;r2-eth0&quot;)],</code> | Ergänzt r2s explizite Rückroute zum Client-LAN über r1. |
| 15 | <code>    &quot;server&quot;: [(&quot;10.0.2.0/24&quot;, None, &quot;server-eth0&quot;), (&quot;0.0.0.0/0&quot;, &quot;10.0.2.1&quot;, &quot;server-eth0&quot;)],</code> | Definiert Server-LAN direkt und Server-Default Route über die lokale r2-Adresse. |
| 16 | <code>}</code> | Schließt das Tabellendictionary; auf r1/r2 wurde absichtlich keine Default Route hinzugefügt. |
| 17 | <code>OWNERS = {&quot;10.0.1.2&quot;: &quot;client&quot;, &quot;10.0.1.1&quot;: &quot;r1&quot;, &quot;10.0.12.1&quot;: &quot;r1&quot;,</code> | Beginnt die Zuordnung bekannter Interface-IP-Adressen zu Modellknoten mit Client und beiden r1-Adressen. |
| 18 | <code>          &quot;10.0.12.2&quot;: &quot;r2&quot;, &quot;10.0.2.1&quot;: &quot;r2&quot;, &quot;10.0.2.2&quot;: &quot;server&quot;}</code> | Vervollständigt die Besitzerzuordnung mit beiden r2-Adressen und der Serveradresse. |
| 21 | <code>def lookup(routes, destination):</code> | Definiert die Forwarding-Entscheidung für eine Routentabelle und eine Zieladresse. |
| 22 | <code>    address = IPv4Address(destination)</code> | Validiert den Zielstring als IPv4-Adresse und macht ihn für Netzmitgliedschaftsprüfungen verwendbar. |
| 23 | <code>    matches = [route for route in routes if address in IPv4Network(route[0])]</code> | Filtert alle Routen heraus, deren Präfix die Zieladresse enthält. |
| 24 | <code>    if not matches:</code> | Erkennt, dass weder eine Netzroute noch eine Default Route passt. |
| 25 | <code>        raise LookupError(f&quot;Keine Route nach {destination}&quot;)</code> | Meldet ausdrücklich das fehlende Ziel; es wird kein Next Hop erfunden. |
| 26 | <code>    return max(matches, key=lambda route: IPv4Network(route[0]).prefixlen)</code> | Wählt aus allen Treffern die Route mit der größten Präfixlänge, also Longest Prefix Match, unabhängig von der Reihenfolge. |
| 29 | <code>def path(source, destination, tables=TABLES, forwarding=True):</code> | Definiert die Wegsimulation; eigene Tabellen erlauben Negativtests und forwarding modelliert den Router-Schalter. |
| 30 | <code>    node, target = OWNERS[source], OWNERS[destination]</code> | Bestimmt den Startknoten und den lokalen Besitzer der Zieladresse aus der bekannten Topologie. |
| 31 | <code>    steps, visited = [], set()</code> | Initialisiert Wegliste und Menge der bereits besuchten Knoten. |
| 32 | <code>    while node != target:</code> | Wiederholt die Weiterleitung nur bis zum Zielknoten; dort wäre die Zustellung lokal. |
| 33 | <code>        if node in visited:</code> | Erkennt den erneuten Besuch eines bereits durchlaufenen Knotens. |
| 34 | <code>            raise RuntimeError(&quot;Routing-Schleife&quot;)</code> | Bricht eine Routingschleife ab, statt endlos zu simulieren. |
| 35 | <code>        visited.add(node)</code> | Merkt den aktuellen Knoten zur Schleifenerkennung vor. |
| 36 | <code>        if node in (&quot;r1&quot;, &quot;r2&quot;) and not forwarding:</code> | Prüft bei einem transitierenden Router das modellierte IPv4-Forwarding. |
| 37 | <code>            raise RuntimeError(f&quot;IPv4-Forwarding auf {node} deaktiviert&quot;)</code> | Verweigert Weiterleitung bei abgeschaltetem Forwarding trotz vorhandener Route. |
| 38 | <code>        network, gateway, interface = lookup(tables[node], destination)</code> | Ermittelt die längste passende Route des aktuellen Knotens und zerlegt ihre drei Bestandteile. |
| 39 | <code>        neighbor = gateway or destination</code> | Für Gatewayrouten ist der ARP-Nachbar das Gateway; bei direkt angeschlossener Route ist es das IP-Ziel selbst. |
| 40 | <code>        steps.append((node, network, interface, neighbor))</code> | Speichert Knoten, gewähltes Präfix, Ausgangsinterface und aufzulösende Nachbar-IP für diesen Hop. |
| 41 | <code>        node = OWNERS[neighbor]</code> | Springt im Modell zum Besitzer des Next Hops; es wird weder ARP noch ein echtes Paket gesendet. |
| 42 | <code>    return steps</code> | Gibt die vollständige Liste der Weiterleitungsentscheidungen zurück. |
| 45 | <code>def self_test():</code> | Beginnt die deterministischen Routing-Selbsttests. |
| 46 | <code>    forward = path(&quot;10.0.1.2&quot;, &quot;10.0.2.2&quot;)</code> | Berechnet den Hinweg des Clients zum Server. |
| 47 | <code>    backward = path(&quot;10.0.2.2&quot;, &quot;10.0.1.2&quot;)</code> | Berechnet unabhängig den Rückweg des Servers zum Client. |
| 48 | <code>    assert [step[0] for step in forward] == [&quot;client&quot;, &quot;r1&quot;, &quot;r2&quot;]</code> | Prüft die exakte Knotenfolge vor der lokalen Serverzustellung. |
| 49 | <code>    assert [step[3] for step in forward] == [&quot;10.0.1.1&quot;, &quot;10.0.12.2&quot;, &quot;10.0.2.2&quot;]</code> | Prüft alle drei aufzulösenden Nachbaradressen des Hinwegs. |
| 50 | <code>    assert [step[0] for step in backward] == [&quot;server&quot;, &quot;r2&quot;, &quot;r1&quot;]</code> | Prüft die exakte Knotenfolge vor der lokalen Clientzustellung. |
| 51 | <code>    assert [step[3] for step in backward] == [&quot;10.0.2.1&quot;, &quot;10.0.12.1&quot;, &quot;10.0.1.2&quot;]</code> | Prüft die drei Nachbaradressen des Rückwegs, nicht nur die Existenz irgendeines Wegs. |
| 52 | <code>    extra = TABLES[&quot;client&quot;] + [(&quot;10.0.2.0/24&quot;, &quot;10.0.1.8&quot;, &quot;client-eth0&quot;),</code> | Erweitert eine Kopie der Clienttabelle für einen künstlichen LPM-Test um eine passende /24-Route. |
| 53 | <code>                                (&quot;10.0.2.2/32&quot;, &quot;10.0.1.9&quot;, &quot;client-eth0&quot;)]</code> | Fügt außerdem eine konkurrierende /32-Hostroute hinzu; beide Gateways sind nur Testwerte. |
| 54 | <code>    assert lookup(extra, &quot;10.0.2.2&quot;)[0] == &quot;10.0.2.2/32&quot;</code> | Prüft, dass für das eine Ziel die spezifische /32 gegenüber /24 und /0 gewinnt. |
| 55 | <code>    assert lookup(extra, &quot;10.0.2.3&quot;)[0] == &quot;10.0.2.0/24&quot;</code> | Prüft für eine andere Adresse im Servernetz, dass /24 vor /0 gewinnt. |
| 56 | <code>    assert lookup(extra, &quot;192.0.2.1&quot;)[0] == &quot;0.0.0.0/0&quot;</code> | Prüft für eine Adresse außerhalb der spezifischen Netze den Rückfall auf die /0-Default Route. |
| 57 | <code>    assert lookup(TABLES[&quot;client&quot;], &quot;10.0.1.1&quot;)[0] == &quot;10.0.1.0/24&quot;</code> | Prüft zusätzlich die reale Modellentscheidung zur angeschlossenen Client-/24-Route statt Default. |
| 58 | <code>    missing = {name: list(routes) for name, routes in TABLES.items()}</code> | Kopiert die Listen aller Tabellen, um das globale Sollmodell bei Negativtests nicht zu verändern. |
| 59 | <code>    missing[&quot;r1&quot;] = [route for route in missing[&quot;r1&quot;] if route[1] is None]</code> | Entfernt nur r1s Gatewayroute; direkt angeschlossene Routen bleiben in der Testkopie erhalten. |
| 60 | <code>    for operation, error in [(lambda: path(&quot;10.0.1.2&quot;, &quot;10.0.2.2&quot;, missing), LookupError),</code> | Beginnt die Liste zweier verzögert ausgeführter Negativoperationen und nennt für die fehlende Route den erwarteten Fehlertyp. |
| 61 | <code>                             (lambda: path(&quot;10.0.1.2&quot;, &quot;10.0.2.2&quot;, forwarding=False), RuntimeError)]:</code> | Ergänzt als zweite Operation den Weg mit abgeschaltetem Forwarding und erwartet RuntimeError. |
| 62 | <code>        try:</code> | Beginnt den kontrollierten Aufruf einer Negativoperation. |
| 63 | <code>            operation()</code> | Ruft die aktuelle Lambda-Funktion tatsächlich auf; bloßes Erzeugen der Lambda würde nichts testen. |
| 64 | <code>        except error:</code> | Fängt genau den für diese Operation erwarteten Fehlertyp. |
| 65 | <code>            continue</code> | Springt bei korrekt aufgetretenem Fehler zur nächsten Operation. |
| 66 | <code>        raise AssertionError(&quot;Negativtest hätte fehlschlagen müssen&quot;)</code> | Lässt den Test scheitern, falls eine erwartete Ausnahme nicht aufgetreten ist. |
| 67 | <code>    print(&quot;Selbsttest: Hin-/Rückweg, /32 vor /24 vor /0, fehlende Route, Forwarding OK.&quot;)</code> | Meldet Erfolg erst nach allen Weg-, Präfix- und Fehlerprüfungen; Assertions bleiben ohne -O aktiv. |
| 70 | <code>def main():</code> | Definiert die Kommandozeilenfunktion. |
| 71 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erstellt Parser und Hilfetext aus dem Modul-Docstring. |
| 72 | <code>    parser.add_argument(&quot;--test&quot;, action=&quot;store_true&quot;)</code> | Registriert den booleschen Testschalter. |
| 73 | <code>    if parser.parse_args().test:</code> | Liest die Argumente und entscheidet, ob nur getestet werden soll. |
| 74 | <code>        self_test()</code> | Führt die Selbsttests wirklich aus. |
| 75 | <code>        return</code> | Beendet den Testmodus vor der normalen Modellanzeige. |
| 76 | <code>    print(&quot;SOLLPLAN, kein Livebefund. Haupttabelle, keine Policy-Regeln/ECMP/NAT.&quot;)</code> | Kennzeichnet die Ausgabe und ihre Modellgrenzen ausdrücklich: keine Policy-Regeln, kein ECMP, kein NAT. |
| 77 | <code>    for node in (&quot;r1&quot;, &quot;r2&quot;):</code> | Durchläuft die beiden geforderten Router für die kleinen Forwardingtabellen. |
| 78 | <code>        print(f&quot;\n{node}: Zielpräfix &#124; Next Hop &#124; Interface&quot;)</code> | Gibt Knoten und Spaltenüberschriften aus. |
| 79 | <code>        for network, gateway, interface in TABLES[node]:</code> | Zerlegt jede Modellroute in Zielnetz, Gateway und Ausgangsinterface. |
| 80 | <code>            print(f&quot;{network} &#124; {gateway or &#x27;direkt: Ziel-IP&#x27;} &#124; {interface}&quot;)</code> | Druckt einen konkreten Next Hop oder den Hinweis auf direkte Zustellung an die Ziel-IP. |
| 81 | <code>    for source, destination in [(&quot;10.0.1.2&quot;, &quot;10.0.2.2&quot;), (&quot;10.0.2.2&quot;, &quot;10.0.1.2&quot;)]:</code> | Durchläuft Hin- und Rückrichtung als zwei getrennte Quell-/Zielpaare. |
| 82 | <code>        print(f&quot;\n{source} -&gt; {destination}:&quot;)</code> | Kennzeichnet die gerade ausgegebene Richtung. |
| 83 | <code>        for node, network, interface, neighbor in path(source, destination):</code> | Berechnet den Weg und zerlegt jede gespeicherte Weiterleitungsentscheidung. |
| 84 | <code>            print(f&quot;{node}: {network}, {interface}, ARP-Nachbar {neighbor}&quot;)</code> | Druckt das gewählte Präfix, Ausgangsinterface und den tatsächlichen ARP-Zielnachbarn je Hop im Modell. |
| 85 | <code>        print(f&quot;{OWNERS[destination]}: lokale Zustellung an {destination}&quot;)</code> | Kennzeichnet am Ende die lokale Zustellung statt noch einen erfundenen Gateway-Hop anzuhängen. |
| 88 | <code>if __name__ == &quot;__main__&quot;:</code> | Verhindert beim Import die automatische Ausgabe und Testausführung. |
| 89 | <code>    main()</code> | Startet main nur für den direkten Programmaufruf. |

## [ue6.3/static_routes.py](ue6.3/static_routes.py)
| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code>#!/usr/bin/env python3</code> | Shebang: Beim direkten Start wird python3 über PATH gesucht; mit python3 datei.py ist dieselbe Datei nutzbar. |
| 2 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.</code> | Kennzeichnet den KI-Anteil und nennt Tool sowie exaktes Modell; kein ausführbarer Programmcode. |
| 3 | <code># Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | Dokumentiert den vorgegebenen Anbieter und das Erstellungsdatum; kein Laufzeitdatum wird behauptet. |
| 4 | <code># Anfrage: Implementiere 6.3: apply(node), Routen löschen/ergänzen, Ping3 prüfen.</code> | Hält die tatsächliche Teilanfrage als Kommentar fest und erfüllt damit die Kennzeichnung direkt übernommenen Codes. |
| 5 | <code>&quot;&quot;&quot;Statische Routen im Lab; ohne --mininet keine Netzwerkänderungen.&quot;&quot;&quot;</code> | Beschreibt die Funktion und die Sicherheitsgrenze: ohne ausdrückliches --mininet keine Netzänderung beim Skriptstart. |
| 6 | <code>import argparse</code> | Lädt argparse für den expliziten Mininet-Startschalter. |
| 7 | <code>import re</code> | Lädt reguläre Ausdrücke zur Auswertung der tatsächlichen Pingstatistik. |
| 8 | <code>import shlex</code> | Lädt shlex, um vorgegebene Befehle als Argumentliste statt als frei interpretierte Shellzeichenfolge aufzurufen. |
| 9 | <code>import sys</code> | Lädt sys für die temporäre Erweiterung des Importpfades im expliziten VM-Modus. |
| 10 | <code>from pathlib import Path</code> | Lädt Path, damit Angabe relativ zum Skript und unabhängig vom aktuellen Verzeichnis gefunden wird. |
| 12 | <code>ROUTES = {</code> | Beginnt die erlaubten expliziten statischen Routen; keine beliebigen Routenziele werden vom Benutzer interpoliert. |
| 13 | <code>    &quot;r1&quot;: (&quot;10.0.2.0/24&quot;, &quot;10.0.12.2&quot;, &quot;r1-eth1&quot;, &quot;10.0.2.2&quot;),</code> | Speichert für r1 Servernetz, r2-Gateway, Transitinterface und Prüfzieldresse im entfernten Netz. |
| 14 | <code>    &quot;r2&quot;: (&quot;10.0.1.0/24&quot;, &quot;10.0.12.1&quot;, &quot;r2-eth0&quot;, &quot;10.0.1.2&quot;),</code> | Speichert für r2 Clientnetz, r1-Gateway, Transitinterface und die Gegenrichtungs-Prüfadresse. |
| 15 | <code>}</code> | Schließt die fest vorgegebene Routenkonfiguration. |
| 18 | <code>def run(node, command, check=True):</code> | Definiert den gemeinsamen Befehlsadapter mit optionaler automatischer Statusprüfung. |
| 19 | <code>    stdout, stderr, status = node.pexec(shlex.split(command))</code> | Ruft pexec des ausdrücklich übergebenen Knotens auf; stdout, stderr und Exitstatus werden getrennt übernommen. |
| 20 | <code>    print(f&quot;[{node.name}] $ {command}\n{stdout}{stderr}[Exitstatus {status}]&quot;)</code> | Dokumentiert Knoten, exakten Befehl, beide Ausgabeströme und Status, statt Erfolg bloß zu behaupten. |
| 21 | <code>    if check and status != 0:</code> | Prüft für normalerweise erfolgreiche Kommandos den Prozessstatus. |
| 22 | <code>        raise RuntimeError(f&quot;{node.name}: Befehl fehlgeschlagen: {command}&quot;)</code> | Meldet einen fehlgeschlagenen Befehl als Ausnahme mit Knoten und vollständigem Kommando. |
| 23 | <code>    return stdout, stderr, status</code> | Gibt alle drei tatsächlichen Rückgabewerte für zusätzliche Prüfungen zurück. |
| 26 | <code>def apply(node, phase=&quot;cycle&quot;):</code> | Definiert die wiederverwendbare apply-Funktion; standardmäßig wird ein einzelner Router gelöscht und wiederhergestellt. |
| 27 | <code>    if node.name not in ROUTES or phase not in (&quot;cycle&quot;, &quot;remove&quot;, &quot;restore&quot;):</code> | Beschränkt die Funktion auf r1/r2 und die drei dokumentierten Phasen. |
| 28 | <code>        raise ValueError(&quot;Nur r1/r2 und cycle/remove/restore sind erlaubt&quot;)</code> | Lehnt falsche Knoten oder Phasen ab, bevor irgendein Netzwerkbefehl ausgeführt wird. |
| 29 | <code>    network, gateway, interface, target = ROUTES[node.name]</code> | Entpackt genau die für diesen Router definierte Route und ihre Prüfzieldresse. |
| 30 | <code>    route = f&quot;{network} via {gateway} dev {interface}&quot;</code> | Baut den expliziten Routenparameter aus Zielpräfix, Next Hop und Interface zusammen. |
| 31 | <code>    if phase == &quot;cycle&quot;:</code> | Erkennt den vollständigen Einzelknotenzyklus. |
| 32 | <code>        apply(node, &quot;remove&quot;)</code> | Führt dafür dieselbe dokumentierte Löschphase aus, die auch exercise benutzt. |
| 33 | <code>        apply(node, &quot;restore&quot;)</code> | Führt unmittelbar danach die Wiederanlagephase aus. |
| 34 | <code>        return</code> | Verhindert, dass nach dem Zyklus versehentlich noch eine zusätzliche Phase folgt. |
| 35 | <code>    run(node, &quot;ip route&quot;)</code> | Zeigt vor jeder eigentlichen Phasenänderung die gegenwärtige Routingtabelle des Knotens an. |
| 36 | <code>    if phase == &quot;remove&quot;:</code> | Wählt den Löschpfad. |
| 37 | <code>        run(node, f&quot;ip route del {route}&quot;)</code> | Entfernt nur die exakte explizite LAN-Route; keine Flush-Operation und keine angeschlossenen Routen. |
| 38 | <code>        try:</code> | Beginnt den Schutzbereich nach einer tatsächlich erfolgreichen Löschung. |
| 39 | <code>            run(node, &quot;ip route&quot;)</code> | Zeigt die Tabelle nach dem Entfernen, damit der Zwischenschritt nachvollziehbar ist. |
| 40 | <code>            _, _, status = run(node, f&quot;ip route get {target}&quot;, check=False)</code> | Fragt den Weg zur entfernten Zieladresse ab und erlaubt zunächst einen Fehlerstatus, weil dieser hier erwartet wird. |
| 41 | <code>            if status == 0:</code> | Erkennt einen unerwartet weiterhin erreichbaren Zielweg, etwa durch eine zusätzliche Default Route. |
| 42 | <code>                raise RuntimeError(&quot;Trotz Löschung existiert ein Weg; Basis-Lab erwartet keine Defaultroute&quot;)</code> | Lehnt diese vom Basis-Lab abweichende Situation ab, statt einen nicht vorhandenen Routenverlust zu behaupten. |
| 43 | <code>        except BaseException:</code> | Fängt in diesem engen Reparaturbereich auch Abbruchausnahmen, um nach erfolgreichem Delete möglichst nicht ohne Route abzubrechen. |
| 44 | <code>            run(node, f&quot;ip route add {route}&quot;)</code> | Stellt vor dem Weiterreichen eines solchen Fehlers genau die zuvor entfernte Route wieder her. |
| 45 | <code>            raise</code> | Reicht den ursprünglichen Fehler weiter; die Prüfung wird nicht stillschweigend als Erfolg gewertet. |
| 46 | <code>    else:</code> | Wählt nach ausgeschlossenen anderen Fällen die restore-Phase. |
| 47 | <code>        run(node, f&quot;ip route add {route}&quot;)</code> | Legt die exakte Route mit add erneut an; ein bereits existierender Eintrag ist bewusst ein Fehler. |
| 48 | <code>        run(node, &quot;ip route&quot;)</code> | Liest unmittelbar danach die Routingtabelle desselben Knotens zurück. |
| 49 | <code>        run(node, f&quot;ip route get {target}&quot;)</code> | Prüft zusätzlich mit route get, dass ein Weg zur entfernten Prüfzieldresse wieder erfolgreich auflösbar ist. |
| 52 | <code>def ping3(node, expect_success=True):</code> | Definiert den Dreier-Ping; standardmäßig werden drei echte Antworten verlangt, im Negativtest explizit keine. |
| 53 | <code>    output, _, status = run(node, &quot;env LC_ALL=C ping -n -c 3 -W 1 10.0.2.2&quot;, check=False)</code> | Führt Ping auf dem übergebenen Client aus; C-Locale, numerische Anzeige, genau drei Probes und begrenzte Wartezeit. |
| 54 | <code>    match = re.search(r&quot;(\d+) packets transmitted, (\d+) (?:packets )?received&quot;, output)</code> | Sucht die gesendeten und empfangenen Zähler; akzeptiert die üblichen Formen received und packets received, nicht bloß einen Prozentstring. |
| 55 | <code>    counts = tuple(map(int, match.groups())) if match else None</code> | Wandelt beide gefundenen Zähler in Integer um; fehlende Statistik bleibt None und kann nicht versehentlich Erfolg bedeuten. |
| 56 | <code>    expected = (3, 3) if expect_success else (3, 0)</code> | Setzt das geforderte exakte Zählerpaar auf 3/3 oder für den Löschtest auf 3/0. |
| 57 | <code>    if counts is None or counts != expected or status != (0 if expect_success else 1):</code> | Verlangt vorhandene Statistik, genau passende Zähler und Pingstatus 0 bei Erfolg beziehungsweise 1 beim erwarteten Paketverlust. |
| 58 | <code>        raise RuntimeError(f&quot;Pingnachweis ungültig: Status={status}, gesendet/empfangen={counts}&quot;)</code> | Bricht bei jeder Abweichung mit den tatsächlich gefundenen Diagnosewerten ab. |
| 59 | <code>    print(f&quot;Ping geprüft: gesendet={counts[0]}, empfangen={counts[1]}, Status={status}.&quot;)</code> | Gibt erst nach erfolgreicher Prüfung die belegten Zähler und den Status aus; bei Test-Doubles sind dies ausdrücklich nur synthetische Werte. |
| 60 | <code>    return counts</code> | Gibt das geprüfte Zählerpaar für weitere Tests zurück. |
| 63 | <code>def exercise(net):</code> | Definiert die ganze Übung auf einem Mininet-ähnlichen Netzobjekt; dies erlaubt getrennte reale und synthetische Adapter. |
| 64 | <code>    routers = [net[&quot;r1&quot;], net[&quot;r2&quot;]]</code> | Holt ausschließlich die beiden Router aus dem übergebenen Netz. |
| 65 | <code>    for node in routers:</code> | Durchläuft beide Router, bevor statische Routen geändert werden. |
| 66 | <code>        output, _, _ = run(node, &quot;sysctl -n net.ipv4.ip_forward&quot;)</code> | Liest jeweils den vorhandenen IPv4-Forwardingwert aus, ohne ihn zu verändern. |
| 67 | <code>        if output.strip() != &quot;1&quot;:</code> | Verlangt den Wert 1 nach Entfernen von Zeilenumbrüchen. |
| 68 | <code>            raise RuntimeError(f&quot;IPv4-Forwarding auf {node.name} muss bereits 1 sein&quot;)</code> | Bricht bei abgeschaltetem Forwarding mit einer klaren Vorbedingungsdiagnose ab. |
| 69 | <code>    removed = []</code> | Beginnt die Liste der erfolgreich entfernten Routen für gezielte spätere Wiederherstellung. |
| 70 | <code>    try:</code> | Beginnt den durch finally abgesicherten Abschnitt mit verändertem Routingzustand. |
| 71 | <code>        for node in routers:</code> | Durchläuft r1 und r2 für die Löschphase, bevor eine Wiederanlage beginnt. |
| 72 | <code>            apply(node, &quot;remove&quot;)</code> | Löscht und prüft jeweils die explizite Route mit apply. |
| 73 | <code>            removed.append(node)</code> | Merkt nur einen erfolgreich abgeschlossenen Löschvorgang als wiederherzustellenden Router. |
| 74 | <code>        ping3(net[&quot;client&quot;], expect_success=False)</code> | Prüft am Client den erwarteten Verlust aller drei Echo-Antworten, während beide LAN-Routen fehlen. |
| 75 | <code>    finally:</code> | Erzwingt den Wiederherstellungsversuch auch dann, wenn eine Löschung oder der Negativ-Ping eine Ausnahme auslöst. |
| 76 | <code>        failures = []</code> | Beginnt eine Sammlung möglicher Wiederherstellungsfehler, damit nicht der erste Fehler den zweiten Router überspringt. |
| 77 | <code>        for node in removed:</code> | Durchläuft genau die in diesem Ablauf erfolgreich entfernten Routen. |
| 78 | <code>            try:</code> | Schützt jeden einzelnen Wiederanlageversuch separat. |
| 79 | <code>                apply(node, &quot;restore&quot;)</code> | Fügt die Route wieder hinzu und liest Tabelle sowie Zielweg zurück. |
| 80 | <code>            except RuntimeError as error:</code> | Fängt einen über run bzw. apply gemeldeten Wiederherstellungsfehler. |
| 81 | <code>                failures.append(str(error))</code> | Merkt den Fehlertext und fährt trotzdem mit dem nächsten betroffenen Router fort. |
| 82 | <code>        if failures:</code> | Prüft, ob mindestens eine Wiederherstellung fehlgeschlagen ist. |
| 83 | <code>            raise RuntimeError(&quot;Wiederherstellung prüfen: &quot; + &quot;; &quot;.join(failures))</code> | Meldet alle gesammelten Wiederherstellungsprobleme deutlich; es wird kein erfolgreicher Endzustand behauptet. |
| 84 | <code>    ping3(net[&quot;client&quot;])</code> | Führt erst nach erfolgreicher Wiederanlage den abschließenden strengen Dreier-Ping aus. |
| 87 | <code>def main():</code> | Definiert den eigenständigen, standardmäßig rein informativen Programmeinstieg. |
| 88 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Erstellt den Argumentparser mit der beschriebenen Sicherheitsgrenze. |
| 89 | <code>    parser.add_argument(&quot;--mininet&quot;, action=&quot;store_true&quot;, help=&quot;eigenes Basis-Lab starten; braucht Mininet/root&quot;)</code> | Registriert den ausdrücklich anzufordernden Lab-Start; benötigt vorhandenes Mininet und passende Rechte, installiert aber nichts. |
| 90 | <code>    if not parser.parse_args().mininet:</code> | Prüft, ob der Benutzer auf den optionalen Mininet-Modus verzichtet hat. |
| 91 | <code>        print(&quot;Kein Hosteingriff. Import: exercise(net) oder apply(net[&#x27;r1&#x27;]).&quot;)</code> | Zeigt dann nur die Import-Schnittstelle und führt keine Netzoperation aus. |
| 92 | <code>        print(&quot;Test-Doubles: python3 -m unittest discover -s ueb06/ue6.3 -p &#x27;test_*.py&#x27; -v&quot;)</code> | Nennt den ausführbaren unittest-Aufruf für die klar getrennten Test-Doubles. |
| 93 | <code>        return</code> | Beendet den Standardmodus vor jeglichem Mininet-Import oder Lab-Start. |
| 94 | <code>    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / &quot;Angabe&quot;))</code> | Ergänzt ausschließlich im aktivierten VM-Modus den Pfad zum unveränderten Originalordner Angabe. |
| 95 | <code>    try:</code> | Beginnt den Importversuch für die optionalen VM-Abhängigkeiten. |
| 96 | <code>        from mininet.net import Mininet</code> | Importiert die echte Mininet-Netzklasse; hier fehlt das Paket, was getrennt als Blocker protokolliert wird. |
| 97 | <code>        from start_lab import RoutingTopo, configure_base_network</code> | Importiert Originaltopologie und Original-Basiskonfiguration, ohne start_lab.main oder dessen input-Prompt zu starten. |
| 98 | <code>    except ImportError as error:</code> | Fängt fehlende Mininet- oder Original-Importabhängigkeiten als Startblocker ab. |
| 99 | <code>        parser.exit(2, f&quot;Mininet-Start nicht verfügbar: {error}\n&quot;)</code> | Beendet in diesem Fall mit verständlichem Hinweis und Status 2, noch bevor ein Netz erzeugt wird. |
| 100 | <code>    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True)</code> | Erzeugt im verfügbaren VM-Modus ein eigenes Basis-Lab ohne Controller und mit automatisch vergebenen MAC-Adressen. |
| 101 | <code>    try:</code> | Beginnt den Schutzbereich für den Lebenszyklus des eigenen Labs. |
| 102 | <code>        net.start()</code> | Startet dessen echte Mininet-Knoten und Links. |
| 103 | <code>        configure_base_network(net)</code> | Verwendet die unveränderte vorgegebene Funktion, um Adressen, Default-/LAN-Routen und Forwarding einzurichten. |
| 104 | <code>        exercise(net)</code> | Führt die vollständige Routenübung auf dem so erzeugten Lab aus. |
| 105 | <code>    finally:</code> | Erzwingt nach normalem Ende oder behandelbarem Fehler den Abbau des eigenen Labs. |
| 106 | <code>        net.stop()</code> | Stoppt ausschließlich das hier erzeugte Mininet-Netz und seine Komponenten. |
| 109 | <code>if __name__ == &quot;__main__&quot;:</code> | Verhindert, dass Importieren des Moduls automatisch ein Lab startet oder Bedienhinweise ausgibt. |
| 110 | <code>    main()</code> | Ruft beim direkten Start die Argumentauswertung auf. |

## [ue6.3/test_static_routes.py](ue6.3/test_static_routes.py)
| Zeile | Eigener Quellcode | Einzelne Erklärung |
|---:|---|---|
| 1 | <code>#!/usr/bin/env python3</code> | Shebang: Beim direkten Start wird python3 über PATH gesucht; mit python3 datei.py ist dieselbe Datei nutzbar. |
| 2 | <code># KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol.</code> | Kennzeichnet den KI-Anteil und nennt Tool sowie exaktes Modell; kein ausführbarer Programmcode. |
| 3 | <code># Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.</code> | Dokumentiert den vorgegebenen Anbieter und das Erstellungsdatum; kein Laufzeitdatum wird behauptet. |
| 4 | <code># Anfrage: Teste 6.3 mit klar benannten Test-Doubles, auch Fehler und Ping-Zähler.</code> | Hält die tatsächliche Teilanfrage als Kommentar fest und erfüllt damit die Kennzeichnung direkt übernommenen Codes. |
| 5 | <code>&quot;&quot;&quot;Synthetische Test-Doubles: KEIN Mininet, KEINE echten Pakete oder Routen.&quot;&quot;&quot;</code> | Kennzeichnet alle folgenden Antworten ausdrücklich als synthetisch; diese Datei misst weder Mininet noch echte Netzwerkpakete. |
| 6 | <code>import unittest</code> | Lädt das Standardbibliotheks-Testframework unittest. |
| 7 | <code>from static_routes import ROUTES, apply, exercise, ping3</code> | Importiert genau die zu prüfenden Funktionen und die festgelegten Routen aus dem Lösungsmodul. |
| 10 | <code>class NodeDouble:</code> | Definiert einen klar benannten Ersatz für einen Mininet-Knoten, nicht einen echten Namespace. |
| 11 | <code>    def __init__(self, name, world):</code> | Beginnt den Konstruktor mit Knotenname und Referenz auf die gesamte synthetische Testwelt. |
| 12 | <code>        self.name, self.world = name, world</code> | Speichert Name und gemeinsame Welt; Letztere ermöglicht die beidseitige Erreichbarkeitsbedingung des Ping-Doubles. |
| 13 | <code>        self.static, self.forward, self.reply = True, &quot;1\n&quot;, None</code> | Setzt im Modell Route vorhanden, Forwarding an und keine erzwungene Pingantwort; all dies sind Testwerte. |
| 14 | <code>        self.commands = []</code> | Beginnt das Befehlsprotokoll dieses Testknotens. |
| 16 | <code>    def pexec(self, argv):</code> | Implementiert die für das Lösungsmodul benötigte pexec-Schnittstelle rein im Python-Testprozess. |
| 17 | <code>        command = &quot; &quot;.join(argv)</code> | Verbindet die übergebene Argumentliste für exakten Vergleich mit den modellierten Kommandos. |
| 18 | <code>        self.commands.append(command)</code> | Speichert jeden tatsächlich vom Lösungscode angeforderten Befehl. |
| 19 | <code>        if command == &quot;sysctl -n net.ipv4.ip_forward&quot;:</code> | Erkennt die Forwardingabfrage des Übungsablaufs. |
| 20 | <code>            return self.forward, &quot;&quot;, 0</code> | Gibt den veränderbaren synthetischen Forwardingwert samt erfolgreichem Status zurück. |
| 21 | <code>        if command == &quot;ip route&quot;:</code> | Erkennt die Tabellenabfrage. |
| 22 | <code>            return f&quot;TEST-DOUBLE: connected bleibt; explizite Route vorhanden={self.static}\n&quot;, &quot;&quot;, 0</code> | Gibt einen ausdrücklich TEST-DOUBLE-markierten Zustandsbericht zurück, keine vorgetäuschte Linux-Routingtabelle. |
| 23 | <code>        if command.startswith(&quot;ip route del &quot;) or command.startswith(&quot;ip route add &quot;):</code> | Behandelt ausschließlich die beiden für die Übung vorgesehenen Typen von Routenänderungen. |
| 24 | <code>            network, gateway, interface, _ = ROUTES[self.name]</code> | Liest die exakten erwarteten Routenbestandteile für diesen Router. |
| 25 | <code>            operation = &quot;del&quot; if command.startswith(&quot;ip route del &quot;) else &quot;add&quot;</code> | Bestimmt, ob ein Delete oder ein Add modelliert werden soll. |
| 26 | <code>            assert command == f&quot;ip route {operation} {network} via {gateway} dev {interface}&quot;</code> | Prüft mit assert den vollständigen vom Lösungscode erzeugten Befehl inklusive Netz, Gateway und Interface. |
| 27 | <code>            if self.static == (operation == &quot;add&quot;):</code> | Erkennt inkonsistente Operationen: Löschen einer fehlenden oder Hinzufügen einer vorhandenen Route. |
| 28 | <code>                return &quot;&quot;, &quot;TEST-DOUBLE: Route fehlt oder existiert bereits\n&quot;, 2</code> | Gibt dafür einen synthetischen Fehler mit Status 2 aus, statt doppelte Änderungen still zu akzeptieren. |
| 29 | <code>            self.static = operation == &quot;add&quot;</code> | Ändert nur den booleschen Modellzustand, nicht die Kernelroutingtabelle. |
| 30 | <code>            return &quot;&quot;, &quot;&quot;, 0</code> | Gibt bei erlaubter Änderung leere Ausgaben und Status 0 zurück. |
| 31 | <code>        if command == f&quot;ip route get {ROUTES.get(self.name, (&#x27;&#x27;, &#x27;&#x27;, &#x27;&#x27;, &#x27;&#x27;))[3]}&quot;:</code> | Erkennt ausschließlich die zum jeweiligen Router gehörende Prüfzieldresse; beim Client ergibt der Default keinen echten Zielweg. |
| 32 | <code>            return (&quot;TEST-DOUBLE: Weg vorhanden\n&quot;, &quot;&quot;, 0) if self.static else (&quot;&quot;, &quot;TEST-DOUBLE: unreachable\n&quot;, 2)</code> | Modelliert route get abhängig vom Routenflag mit markierter Antwort und Status 0 oder 2. |
| 33 | <code>        if command == &quot;env LC_ALL=C ping -n -c 3 -W 1 10.0.2.2&quot;:</code> | Erkennt den exakten verwendeten Dreier-Pingbefehl. |
| 34 | <code>            count = 3 if all(self.world[name].static for name in ROUTES) else 0</code> | Erzeugt drei Modellantworten nur wenn beide Routerrouten vorhanden sind, sonst null; dabei werden keine Pakete gesendet. |
| 35 | <code>            return self.reply or (f&quot;3 packets transmitted, {count} received\n&quot;, &quot;&quot;, 0 if count == 3 else 1)</code> | Gibt eine explizit erzwungene Fehlerfixture oder die synthetische Statistik mit dazugehörigem Status zurück. |
| 36 | <code>        raise AssertionError(f&quot;Nicht modellierter Befehl: {command}&quot;)</code> | Lässt jeden nicht modellierten Befehl sofort scheitern; das Double kann also keine unerwarteten Hostbefehle verschlucken. |
| 39 | <code>class RouteTests(unittest.TestCase):</code> | Beginnt die eigentlichen unittest-Testfälle. |
| 40 | <code>    def setUp(self):</code> | Definiert die Einrichtung, die vor jeder Testmethode neu ausgeführt wird. |
| 41 | <code>        self.net = {}</code> | Erstellt eine frische leere synthetische Welt, damit kein Test Zustand eines anderen erbt. |
| 42 | <code>        for name in (&quot;r1&quot;, &quot;r2&quot;, &quot;client&quot;):</code> | Durchläuft die zwei Router und den Client; ein Serverobjekt wird für die hier simulierten Kommandos nicht benötigt. |
| 43 | <code>            self.net[name] = NodeDouble(name, self.net)</code> | Legt die drei benannten NodeDouble-Instanzen mit gemeinsamer Weltreferenz an. |
| 45 | <code>    def test_complete_exercise(self):</code> | Beginnt den Test des gesamten Übungsablaufs. |
| 46 | <code>        exercise(self.net)</code> | Ruft die echte exercise-Funktion auf den Doubles auf; nur die Betriebssystem-Schnittstelle ist ersetzt. |
| 47 | <code>        self.assertTrue(all(self.net[name].static for name in ROUTES))</code> | Prüft, dass nach Abschluss beide entfernten Routen im Modell wieder vorhanden sind. |
| 48 | <code>        self.assertEqual(len(self.net[&quot;client&quot;].commands), 2)</code> | Prüft, dass der Client genau den negativen und den abschließenden Ping angefordert hat. |
| 50 | <code>    def test_apply_and_duplicate_delete(self):</code> | Beginnt die Prüfung der Einzelfunktion und eines echten Fehlerzweigs ihrer Schnittstelle. |
| 51 | <code>        for name in ROUTES:</code> | Durchläuft beide erlaubten Router. |
| 52 | <code>            apply(self.net[name])</code> | Führt apply(node) mit Standardphase cycle tatsächlich aus. |
| 53 | <code>        apply(self.net[&quot;r1&quot;], &quot;remove&quot;)</code> | Entfernt anschließend r1s explizite Route einmal erfolgreich. |
| 54 | <code>        with self.assertRaises(RuntimeError):</code> | Verlangt beim folgenden Befehl eine RuntimeError-Ausnahme. |
| 55 | <code>            apply(self.net[&quot;r1&quot;], &quot;remove&quot;)</code> | Löscht absichtlich dieselbe fehlende Route erneut und prüft damit die Exitstatusbehandlung. |
| 56 | <code>        apply(self.net[&quot;r1&quot;], &quot;restore&quot;)</code> | Stellt den vorübergehenden Testzustand wieder her. |
| 58 | <code>    def test_ping_requires_status_and_exact_counts(self):</code> | Beginnt die strenge Prüfung der Ping-Erfolgserkennung gegen irreführende Ausgaben. |
| 59 | <code>        for text, status in [(&quot;3 packets transmitted, 0 received, 100% packet loss&quot;, 1),</code> | Erster Negativfall: drei gesendet, null empfangen und 100 Prozent Verlust; der alte Teilstringtest wäre hier falsch. |
| 60 | <code>                             (&quot;3 packets transmitted, 2 received&quot;, 0),</code> | Zweiter Negativfall: ein erfolgreicher Status genügt bei nur zwei statt drei Antworten nicht. |
| 61 | <code>                             (&quot;3 packets transmitted, 3 received&quot;, 1), (&quot;0% packet loss&quot;, 0)]:</code> | Ergänzt Fehlerstatus trotz drei Antworten und Prozenttext ohne Zähler; beides muss zurückgewiesen werden. |
| 62 | <code>            self.net[&quot;client&quot;].reply = (text, &quot;&quot;, status)</code> | Setzt die jeweils ausdrücklich synthetische Pingausgabe für diesen Untertest. |
| 63 | <code>            with self.subTest(text=text, status=status), self.assertRaises(RuntimeError):</code> | Markiert den Untertest für genaue Diagnose und erwartet die notwendige Ausnahme. |
| 64 | <code>                ping3(self.net[&quot;client&quot;])</code> | Ruft den tatsächlichen Parser samt Status-/Zählerprüfung auf dieser Fixture auf. |
| 65 | <code>        self.net[&quot;client&quot;].reply = (&quot;3 packets transmitted, 3 packets received&quot;, &quot;&quot;, 0)</code> | Setzt einen gültigen Positivfall mit der alternativen üblichen Statistikform packets received. |
| 66 | <code>        self.assertEqual(ping3(self.net[&quot;client&quot;]), (3, 3))</code> | Prüft, dass der Parser dabei genau das Integerpaar 3/3 zurückliefert. |
| 68 | <code>    def test_cleanup_and_forwarding_guard(self):</code> | Beginnt die Tests für Wiederherstellung, Forwardingvorbedingung und Knotenschutz. |
| 69 | <code>        self.net[&quot;client&quot;].reply = (&quot;defekter Testoutput&quot;, &quot;&quot;, 2)</code> | Erzwingt defekte Pingstatistik und Status 2 als künstlichen Fehler im Zwischenzustand. |
| 70 | <code>        with self.assertRaises(RuntimeError):</code> | Erwartet den Fehler dieses vollständigen Übungsversuchs. |
| 71 | <code>            exercise(self.net)</code> | Führt exercise aus, sodass der finally-Pfad wirklich erreicht wird. |
| 72 | <code>        self.assertTrue(all(self.net[name].static for name in ROUTES))</code> | Prüft, dass trotz Fehler beide entfernten Routen wiederhergestellt wurden. |
| 73 | <code>        self.net[&quot;r1&quot;].forward = &quot;0\n&quot;</code> | Simuliert anschließend abgeschaltetes Forwarding auf r1. |
| 74 | <code>        with self.assertRaises(RuntimeError):</code> | Verlangt beim erneuten Übungsstart eine Vorbedingungsausnahme. |
| 75 | <code>            exercise(self.net)</code> | Führt den echten Forwarding-Schutzpfad aus; er darf die Übung nicht still starten. |
| 76 | <code>        with self.assertRaises(ValueError):</code> | Erwartet für einen unzulässigen Routerknoten einen ValueError. |
| 77 | <code>            apply(self.net[&quot;client&quot;])</code> | Übergibt absichtlich den Client an apply, um Änderungen am falschen Knoten abzuweisen. |
| 80 | <code>if __name__ == &quot;__main__&quot;:</code> | Beschränkt den eigenständigen Teststart auf den direkten Skriptaufruf. |
| 81 | <code>    unittest.main(verbosity=2)</code> | Startet unittest mit ausführlicher Ausgabe; bei unittest discover erfolgt die Ausführung durch dessen Runner. |

## Vollständigkeitsprüfung

Die Zuordnung wurde maschinell gegen alle **306 nichtleeren Zeilen** der vier angegebenen Pythondateien geprüft: genau ein Eintrag pro Quellzeile, keine fehlenden oder zusätzlichen Nummern. Änderungen am Code erfordern eine Aktualisierung dieser Erklärung.

## Tests und fachliche Antworten

- [6.1: Antwort](ue6.1/antwort.md), [wirkliches Python-Testprotokoll](ue6.1/testprotokoll.txt).
- [6.2: Antwort](ue6.2/antwort.md), [wirkliches Python-Testprotokoll](ue6.2/testprotokoll.txt).
- [6.3: Antwort](ue6.3/antwort.md), [wirkliches Python-/Double-Testprotokoll](ue6.3/testprotokoll.txt).
