# Zeilenerklärung: pcap.py

## Lesemodell und Grenzen

Der Parser benötigt nur die Python-Standardbibliothek und arbeitet offline.
Er versteht klassisches PCAP 2.4 in beiden Byteordnungen und mit Mikro- oder
Nanosekunden-Magic, Linktyp Ethernet, ungetaggtes Ethernet II, Ethernet/IPv4-ARP,
unfragmentiertes IPv4 sowie ICMP und TCP. Zeitstempel werden übersprungen;
Container- und IP-Längen begrenzen jeden Zugriff. Er ist bewusst kein allgemeiner
Wireshark-Ersatz: kein PCAPNG, VLAN-Decoder, IPv6 oder IP-Reassemblierung.
Unbekannte EtherTypes bleiben als Ethernet-Datensatz erhalten. Die kleinen
Belegdateien werden vollständig in den Speicher gelesen.

Die Internet-Checksumme faltet 16-Bit-Überträge und bildet das Einerkomplement.
Über einen gültigen Header **mit** Prüfsummenfeld gerechnet ist ihr Ergebnis null.
TCP umfasst zusätzlich den IPv4-Pseudoheader. Die Messung schaltet Offloads
auf eigenen veth-Enden aus, damit die Capturebytes bereits gültige Checksummen tragen.

Echo-Paare benötigen dieselben IPs und dieselbe ID/Sequenz; eine bloße Anzahlgleichheit
genügt nicht. TCP-Paare nutzen IP-Richtung, IPv4-ID und alle Transportbytes,
sodass Ports, Optionen, Sequenznummern und Payload über den Router unverändert
bleiben müssen. Die TTL-Prüfung berücksichtigt die Rückrichtung. Die Reassemblierung
akzeptiert gleiche überlappende Bytes und falsche Capture-Reihenfolge, aber keine
Lücken oder widersprüchlichen Bytes. Sequenznummern-Wraparound und große/mehrere
Verbindungen sind nicht Teil dieses begrenzten Laborflusses. Ein initiales SYN,
ein SYN/ACK und je ein FIN pro Seite werden für diesen verlustfreien Test erwartet;
allgemeine Retransmissionsszenarien im Handshake sind kein akzeptierter Ersatznachweis.

## Jede nichtleere Originalzeile

| Zeile | Originalquelle | Individuelle Begründung |
|---:|---|---|
| 1 | <code># KI-Kennzeichnung (RN WS26): Hermes Agent; OpenAI gpt-6.1-sol; ChatGPT or Codex Subscription.</code> | Kennzeichnet Urheberwerkzeug, Anbieter, Modell und tatsächlich angegebenen Zugangstyp des Parsercodes. |
| 2 | <code># Datum: 2026-10-29</code> | Dokumentiert das Erstellungsdatum dieser übernommenen Implementierung. |
| 3 | <code># Anfrage: Reale isolierte Blatt08-Messungen, PCAP-Auswertung und negative Tests implementieren.</code> | Hält den tatsächlichen Auftrag zur PCAP-Analyse und Fehlerprüfung fest. |
| 4 | <code>&quot;&quot;&quot;Strikter Standardbibliothek-Parser für die eigenen Ethernet-PCAPs; kein PCAPNG.&quot;&quot;&quot;</code> | Beschränkt den Dateiformatanspruch ausdrücklich auf klassisches Ethernet-PCAP, nicht PCAPNG. |
| 5 | <code>import ipaddress</code> | Formatiert genau vier Netzwerkbytes als validierte IPv4-Adresse. |
| 6 | <code>import struct</code> | Liest Binärfelder mit expliziter Netz- oder PCAP-Byteordnung. |
| 7 | <code>from collections import Counter</code> | Vergleicht Paketidentitäten als Multimengen und erkennt dadurch auch fehlende Duplikate. |
| 8 | <code>from pathlib import Path</code> | Liest gespeicherte PCAP-Dateien ohne externe Python-Pakete ein. |
| 9 | <code>from typing import Any</code> | Erlaubt die bewusst gemischten Feldtypen im Paketdictionary ohne falsche String-Typannahme. |
| 12 | <code>def require(condition, message):</code> | Zentralisiert semantische Prüfungen mit einer konkreten Fehlermeldung. |
| 13 | <code>    if not condition:</code> | Erkennt eine nicht erfüllte Format- oder Nachweisbedingung. |
| 14 | <code>        raise ValueError(message)</code> | Verhindert mit ValueError die Weiterverarbeitung unzureichender Belege. |
| 17 | <code>def checksum(data):</code> | Berechnet die Internet-Prüfsumme für IPv4, ICMP und den TCP-Pseudoheader. |
| 18 | <code>    data += b&quot;\0&quot; * (len(data) % 2)</code> | Ergänzt nur für die Rechnung bei ungerader Länge ein Nullbyte. |
| 19 | <code>    total = sum(struct.unpack(f&quot;!{len(data) // 2}H&quot;, data))</code> | Summiert alle 16-Bit-Wörter in Big-Endian-Netzreihenfolge. |
| 20 | <code>    while total &gt;&gt; 16:</code> | Wiederholt die Übertragsfaltung, solange noch höhere Bits vorhanden sind. |
| 21 | <code>        total = (total &amp; 65535) + (total &gt;&gt; 16)</code> | Addiert den Übertrag zurück zu den niederwertigen 16 Bits. |
| 22 | <code>    return (~total) &amp; 65535</code> | Liefert das 16-Bit-Einerkomplement; bei gültigem vollständigem Header ergibt sich null. |
| 25 | <code>def mac(data):</code> | Definiert die lesbare Darstellung einer Ethernet-Adresse. |
| 26 | <code>    return &quot;:&quot;.join(f&quot;{byte:02x}&quot; for byte in data)</code> | Gibt jedes Byte zweistellig hexadezimal und durch Doppelpunkte getrennt aus. |
| 29 | <code>def ipv4(data):</code> | Definiert die lesbare IPv4-Darstellung aus ihren vier Originalbytes. |
| 30 | <code>    return str(ipaddress.IPv4Address(data))</code> | Überlässt Gültigkeitsprüfung und Dezimalformatierung der Standardbibliothek. |
| 33 | <code>def frame(data, number):</code> | Analysiert einen Ethernet-Frame und erhält seine tatsächliche laufende Capturenummer. |
| 34 | <code>    require(len(data) &gt;= 14, &quot;Ethernet-Header abgeschnitten&quot;)</code> | Verlangt die Mindestlänge des Ethernet-II-Headers vor jedem Feldzugriff. |
| 35 | <code>    packet: dict[str, Any] = dict(frame=number, dst_mac=mac(data[:6]), src_mac=mac(data[6:12]))</code> | Erfasst Ziel-MAC vor Quell-MAC entsprechend der tatsächlichen Ethernet-Byteanordnung. |
| 36 | <code>    packet[&quot;ethertype&quot;] = struct.unpack(&quot;!H&quot;, data[12:14])[0]</code> | Dekodiert das zweibytegroße EtherType-Feld an Offset 12. |
| 37 | <code>    body = data[14:]</code> | Trennt die Ethernet-Nutzlast vom 14-Byte-Linkheader. |
| 38 | <code>    if packet[&quot;ethertype&quot;] == 0x0806:</code> | Wählt anhand von 0x0806 die ARP-Interpretation aus. |
| 39 | <code>        require(len(body) &gt;= 28, &quot;ARP abgeschnitten&quot;)</code> | Verlangt den vollständigen Ethernet/IPv4-ARP-Grundkörper. |
| 40 | <code>        require(body[:6] == b&quot;\x00\x01\x08\x00\x06\x04&quot;, &quot;Nicht Ethernet/IPv4-ARP&quot;)</code> | Prüft Hardwaretyp Ethernet, Protokoll IPv4 sowie MAC- und IP-Adresslängen. |
| 41 | <code>        packet.update(arp_op=struct.unpack(&quot;!H&quot;, body[6:8])[0], arp_sha=mac(body[8:14]))</code> | Liest ARP-Opcode und Sender-Hardwareadresse aus den vorgesehenen Positionen. |
| 42 | <code>        packet.update(arp_spa=ipv4(body[14:18]), arp_tha=mac(body[18:24]), arp_tpa=ipv4(body[24:28]))</code> | Erfasst Sender-IP, Ziel-Hardwareadresse und gesuchte beziehungsweise adressierte Ziel-IP. |
| 43 | <code>    elif packet[&quot;ethertype&quot;] == 0x0800:</code> | Wählt anhand von 0x0800 die IPv4-Interpretation aus. |
| 44 | <code>        require(len(body) &gt;= 20 and body[0] &gt;&gt; 4 == 4, &quot;IPv4-Header fehlt&quot;)</code> | Prüft IPv4-Mindestlänge und Versionsnibble vor der Längenrechnung. |
| 45 | <code>        ihl, length = (body[0] &amp; 15) * 4, struct.unpack(&quot;!H&quot;, body[2:4])[0]</code> | Berechnet IHL in Bytes und liest die gesamte IPv4-Paketlänge. |
| 46 | <code>        require(20 &lt;= ihl &lt;= length &lt;= len(body), &quot;IPv4-Längen inkonsistent&quot;)</code> | Verwirft zu kurze Header, negative Transportbereiche und über den Frame hinausgehende IP-Längen. |
| 47 | <code>        require(struct.unpack(&quot;!H&quot;, body[6:8])[0] &amp; 0x3fff == 0, &quot;Fragmentierung nicht unterstützt&quot;)</code> | Verwirft MF und Fragmentoffset, weil ohne Reassemblierung keine vollständige Transportprüfung möglich wäre. |
| 48 | <code>        header, transport = body[:ihl], body[ihl:length]</code> | Begrenzt die Transportbytes durch IP Total Length, damit Ethernet-Padding keine Nutzdaten vortäuscht. |
| 49 | <code>        packet.update(src_ip=ipv4(body[12:16]), dst_ip=ipv4(body[16:20]), ttl=body[8], proto=body[9])</code> | Liest logische Endpunkte, TTL und das Feld für das nächste Protokoll. |
| 50 | <code>        packet.update(ip_id=struct.unpack(&quot;!H&quot;, body[4:6])[0], ip_length=length, ip_ihl=ihl)</code> | Bewahrt IPv4-ID, Paketlänge und Headerlänge für nachvollziehbare Router-Vergleiche auf. |
| 51 | <code>        packet.update(ip_checksum=struct.unpack(&quot;!H&quot;, body[10:12])[0], ip_checksum_valid=checksum(header) == 0)</code> | Speichert das originale Prüfsummenfeld und berechnet unabhängig dessen tatsächliche Gültigkeit. |
| 52 | <code>        packet[&quot;transport_hex&quot;] = transport.hex()</code> | Bewahrt die unveränderten Transportbytes als JSON-fähigen Hexstring zur Hop-Zuordnung auf. |
| 53 | <code>        if body[9] == 1:</code> | Erkennt IP-Protokollnummer 1 als ICMP. |
| 54 | <code>            require(len(transport) &gt;= 8, &quot;ICMP abgeschnitten&quot;)</code> | Verlangt acht Bytes, bevor Typ, Code und Echo-Kennungen gelesen werden. |
| 55 | <code>            kind, code, _, ident, seq = struct.unpack(&quot;!BBHHH&quot;, transport[:8])</code> | Dekodiert die ersten acht ICMP-Bytes; die gespeicherte Checksumme wird separat rechnerisch überprüft. |
| 56 | <code>            packet.update(icmp_type=kind, icmp_code=code, icmp_id=ident, icmp_seq=seq)</code> | Speichert Echo-Typ, Code, Identifier und Sequenz für die eindeutige Request-Zuordnung. |
| 57 | <code>            packet[&quot;icmp_checksum_valid&quot;] = checksum(transport) == 0</code> | Validiert die Prüfsumme über die gesamte echte ICMP-Nachricht. |
| 58 | <code>        elif body[9] == 6:</code> | Erkennt IP-Protokollnummer 6 als TCP. |
| 59 | <code>            require(len(transport) &gt;= 20, &quot;TCP abgeschnitten&quot;)</code> | Verlangt den vollständigen TCP-Mindestheader. |
| 60 | <code>            sport, dport, seq, ack = struct.unpack(&quot;!HHII&quot;, transport[:12])</code> | Liest beide Ports sowie die absoluten 32-Bit-Sequenz- und Bestätigungsnummern. |
| 61 | <code>            offset = (transport[12] &gt;&gt; 4) * 4</code> | Rechnet TCP Data Offset von 32-Bit-Wörtern in Bytes um. |
| 62 | <code>            require(20 &lt;= offset &lt;= len(transport), &quot;TCP-Headerlänge ungültig&quot;)</code> | Verwirft zu kleine oder über das Segment hinausreichende TCP-Headerlängen. |
| 63 | <code>            pseudo = body[12:20] + struct.pack(&quot;!BBH&quot;, 0, 6, len(transport))</code> | Baut den IPv4-TCP-Pseudoheader aus beiden IPs, Nullbyte, Protokoll und Segmentlänge auf. |
| 64 | <code>            packet.update(src_port=sport, dst_port=dport, tcp_seq=seq, tcp_ack=ack, tcp_flags=transport[13])</code> | Erfasst Port-Endpunkte, Sequenzräume und die TCP-Steuerbits. |
| 65 | <code>            packet.update(tcp_header_length=offset, tcp_window=struct.unpack(&quot;!H&quot;, transport[14:16])[0])</code> | Bewahrt TCP-Headergröße einschließlich Optionen und das rohe Empfangsfenster auf. |
| 66 | <code>            packet.update(tcp_checksum_valid=checksum(pseudo + transport) == 0, payload_hex=transport[offset:].hex())</code> | Prüft TCP einschließlich Pseudoheader und trennt Nutzdaten anhand des Data Offset ab. |
| 67 | <code>    return packet</code> | Liefert den tatsächlich gelesenen Frame auch dann als Linkdatensatz zurück, wenn sein EtherType unbekannt ist. |
| 70 | <code>def read_pcap(path):</code> | Definiert den strikten Leser einer gesicherten klassischen PCAP-Datei. |
| 71 | <code>    raw = Path(path).read_bytes()</code> | Liest die Originalbytes unverändert aus der benannten Belegdatei. |
| 72 | <code>    require(len(raw) &gt;= 24, &quot;PCAP-Dateikopf fehlt&quot;)</code> | Verlangt den vollständigen 24-Byte-PCAP-Dateikopf. |
| 73 | <code>    magics = {b&quot;\xd4\xc3\xb2\xa1&quot;: &quot;&lt;&quot;, b&quot;\xa1\xb2\xc3\xd4&quot;: &quot;&gt;&quot;, b&quot;\x4d\x3c\xb2\xa1&quot;: &quot;&lt;&quot;, b&quot;\xa1\xb2\x3c\x4d&quot;: &quot;&gt;&quot;}</code> | Erkennt Mikro- und Nanosekunden-Magics in beiden Byteordnungen; Zeitstempelwerte werden nicht ausgewertet. |
| 74 | <code>    require(raw[:4] in magics, &quot;Kein klassisches PCAP&quot;)</code> | Lehnt unbekannte Magics und damit insbesondere PCAPNG ab. |
| 75 | <code>    endian = magics[raw[:4]]</code> | Wählt die durch das Magic tatsächlich signalisierte Container-Byteordnung. |
| 76 | <code>    major, minor, _, _, snaplen, linktype = struct.unpack(endian + &quot;HHIIII&quot;, raw[4:24])</code> | Liest Versionsnummer, Snaplen und Linktyp; Zeitzonen- und Genauigkeitsfelder werden nicht benötigt. |
| 77 | <code>    require((major, minor, linktype) == (2, 4, 1) and snaplen &gt; 0, &quot;PCAP-Version oder Linktyp ungültig&quot;)</code> | Beschränkt die Auswertung auf PCAP 2.4, positive Snaplen und Linktyp Ethernet. |
| 78 | <code>    packets, position = [], 24</code> | Initialisiert die Paketliste und den ersten Recordoffset direkt nach dem Dateikopf. |
| 79 | <code>    while position &lt; len(raw):</code> | Bearbeitet Records nur solange tatsächlich weitere Bytes vorhanden sind. |
| 80 | <code>        require(position + 16 &lt;= len(raw), &quot;PCAP-Recordkopf abgeschnitten&quot;)</code> | Verhindert das Lesen eines unvollständigen 16-Byte-Recordheaders. |
| 81 | <code>        _, _, captured, original = struct.unpack(endian + &quot;IIII&quot;, raw[position:position + 16])</code> | Dekodiert Capture- und Originallänge; die beiden Zeitstempelwörter werden bewusst nicht verglichen. |
| 82 | <code>        position += 16</code> | Verschiebt den Cursor vom Recordheader auf die Capturedaten. |
| 83 | <code>        require(captured == original and captured &lt;= snaplen, &quot;Verkürzter PCAP-Record&quot;)</code> | Verlangt ungekürzte Frames und respektiert die im Dateikopf zugesicherte Snaplen. |
| 84 | <code>        require(position + captured &lt;= len(raw), &quot;PCAP-Recorddaten abgeschnitten&quot;)</code> | Verwirft einen Record, dessen behauptete Länge über das reale Dateiende hinausweist. |
| 85 | <code>        packets.append(frame(raw[position:position + captured], len(packets) + 1))</code> | Übergibt exakt diese Recordbytes und eine einsbasierte Frame-ID an den Ethernet-Parser. |
| 86 | <code>        position += captured</code> | Rückt um die wirklich gespeicherte Framegröße zum nächsten Record weiter. |
| 87 | <code>    return packets</code> | Gibt alle erfolgreich gelesenen Ethernet-Datensätze zurück. |
| 90 | <code>def select(packets, field, value):</code> | Definiert einen kleinen, feldbasierten Paketfilter für die nachfolgenden Nachweise. |
| 91 | <code>    return [packet for packet in packets if packet.get(field) == value]</code> | Vergleicht mit get auch Pakete ohne dieses Protokollfeld gefahrlos gegen den Sollwert. |
| 94 | <code>def echo_pairs(before, after):</code> | Ordnet geroutete ICMP-Echo-Requests zweier Capture-Punkte einander zu. |
| 95 | <code>    left, right = select(before, &quot;icmp_type&quot;, 8), select(after, &quot;icmp_type&quot;, 8)</code> | Beschränkt beide Seiten auf Echo Request Typ 8 statt Replies oder ARP mitzuzählen. |
| 96 | <code>    key = lambda p: (p[&quot;src_ip&quot;], p[&quot;dst_ip&quot;], p[&quot;icmp_id&quot;], p[&quot;icmp_seq&quot;])</code> | Verwendet beide IP-Endpunkte, Identifier und Sequenz als Request-Identität. |
| 97 | <code>    require(left and len({key(p) for p in left}) == len(left), &quot;Echo-Requests fehlen oder sind mehrdeutig&quot;)</code> | Verlangt mindestens einen Request und verbietet auf der Eingangsseite mehrdeutige Request-Schlüssel. |
| 98 | <code>    require(Counter(map(key, left)) == Counter(map(key, right)), &quot;Echo-Zuordnung vor/nach Router fehlt&quot;)</code> | Verlangt dieselben Identitäten mit derselben Häufigkeit vor und nach dem Router. |
| 99 | <code>    pairs = [(p, next(q for q in right if key(p) == key(q))) for p in left]</code> | Sucht für jeden Eingangsrequest genau den durch die Multimengenprüfung gesicherten Partner. |
| 100 | <code>    for p, q in pairs:</code> | Kontrolliert alle gefundenen Vorher-Nachher-Paare einzeln. |
| 101 | <code>        require(p[&quot;ttl&quot;] == q[&quot;ttl&quot;] + 1, &quot;Router-TTL nicht um eins vermindert&quot;)</code> | Belegt das Dekrement der TTL um exakt einen Router-Hop. |
| 102 | <code>        require(p[&quot;transport_hex&quot;] == q[&quot;transport_hex&quot;], &quot;ICMP durch Router verändert&quot;)</code> | Verlangt identische ICMP-Header- und Nutzdatenbytes auf beiden Ethernet-LANs. |
| 103 | <code>        require(p[&quot;ip_checksum_valid&quot;] and q[&quot;ip_checksum_valid&quot;], &quot;IPv4-Prüfsumme falsch&quot;)</code> | Prüft beide IPv4-Header unabhängig auf gültige Checksumme. |
| 104 | <code>        require(p[&quot;ip_checksum&quot;] != q[&quot;ip_checksum&quot;], &quot;IPv4-Prüfsumme unverändert&quot;)</code> | Verlangt zusätzlich einen tatsächlichen Wechsel des IPv4-Prüfsummenfeldes. |
| 105 | <code>        require(p[&quot;icmp_checksum_valid&quot;] and q[&quot;icmp_checksum_valid&quot;] and p[&quot;ip_id&quot;] == q[&quot;ip_id&quot;], &quot;ICMP-Prüfsumme oder IP-ID falsch&quot;)</code> | Belegt gültige ICMP-Prüfsummen und die über den Hop erhaltene IPv4-ID. |
| 106 | <code>        require((p[&quot;src_mac&quot;], p[&quot;dst_mac&quot;]) == (&quot;00:00:00:00:00:01&quot;, &quot;02:00:00:00:01:01&quot;), &quot;Echo-MACs in LAN A falsch&quot;)</code> | Verlangt in LAN A das MAC-Paar client1 zu Router-A, nicht bloß beliebig verschiedene Adressen. |
| 107 | <code>        require((q[&quot;src_mac&quot;], q[&quot;dst_mac&quot;]) == (&quot;02:00:00:00:02:01&quot;, &quot;00:00:00:00:00:03&quot;), &quot;Echo-MACs in LAN B falsch&quot;)</code> | Verlangt in LAN B das MAC-Paar Router-B zu server1. |
| 108 | <code>    return [{&quot;before&quot;: p, &quot;after&quot;: q} for p, q in pairs]</code> | Gibt die belegten Originalheader in lesbaren Vorher-Nachher-Gruppen zurück. |
| 111 | <code>def tcp_stream(packets, source):</code> | Rekonstruiert die Nutzdaten einer Senderichtung unabhängig von Segmentreihenfolge. |
| 112 | <code>    segments = [p for p in packets if p.get(&quot;src_ip&quot;) == source and p.get(&quot;payload_hex&quot;)]</code> | Wählt nur Pakete mit der gesuchten Quell-IP und tatsächlichen TCP-Anwendungsbytes aus. |
| 113 | <code>    require(segments, &quot;TCP-Nutzdaten fehlen&quot;)</code> | Verweigert einen angeblichen Datenstrom ohne Nutzdaten. |
| 114 | <code>    start = min(p[&quot;tcp_seq&quot;] for p in segments)</code> | Bestimmt die kleinste beobachtete Nutzdaten-Sequenznummer als lokalen Streamanfang. |
| 115 | <code>    octets = {}</code> | Speichert jedes Datenbyte unter seiner relativen Sequenzposition. |
| 116 | <code>    for p in segments:</code> | Verarbeitet sämtliche beobachteten Nutzdatensegmente dieser Richtung. |
| 117 | <code>        for offset, byte in enumerate(bytes.fromhex(p[&quot;payload_hex&quot;])):</code> | Wandelt den Hexstring zurück in seine tatsächlich aufgenommenen Bytes. |
| 118 | <code>            pos = p[&quot;tcp_seq&quot;] - start + offset</code> | Berechnet für jedes Byte seinen Platz im TCP-Sequenzraum. |
| 119 | <code>            require(pos not in octets or octets[pos] == byte, &quot;Widersprüchliche TCP-Retransmission&quot;)</code> | Akzeptiert gleiche überlappende Retransmissionsbytes, verwirft aber widersprüchliche Überlappungen. |
| 120 | <code>            octets[pos] = byte</code> | Ordnet das Byte seiner eindeutigen relativen Position zu. |
| 121 | <code>    require(set(octets) == set(range(len(octets))), &quot;Lücke im TCP-Datenstrom&quot;)</code> | Verlangt lückenlose Positionen ab null statt fehlende Segmente still zu übergehen. |
| 122 | <code>    return bytes(octets[i] for i in range(len(octets)))</code> | Gibt die Anwendungsbytes nach TCP-Sequenz sortiert zurück. |
| 125 | <code>def tcp_flow(before, after, request, response):</code> | Prüft den kompletten eigenen TCP/HTTP-Fluss und seine Router-Invarianten. |
| 126 | <code>    a, b = select(before, &quot;proto&quot;, 6), select(after, &quot;proto&quot;, 6)</code> | Extrahiert die TCP-Pakete aus beiden Capture-Seiten. |
| 127 | <code>    require(a and b, &quot;TCP-Aufzeichnung fehlt&quot;)</code> | Verlangt TCP-Belege an beiden Messpunkten. |
| 128 | <code>    allowed = {(&quot;10.0.1.2&quot;, &quot;10.0.2.10&quot;, 40080, 8080), (&quot;10.0.2.10&quot;, &quot;10.0.1.2&quot;, 8080, 40080)}</code> | Definiert genau die erlaubte eigene Verbindung und ihre umgekehrte Antwortrichtung. |
| 129 | <code>    require(all((p[&quot;src_ip&quot;], p[&quot;dst_ip&quot;], p[&quot;src_port&quot;], p[&quot;dst_port&quot;]) in allowed for p in a + b), &quot;TCP-Verbindungsendpunkte falsch&quot;)</code> | Verwirft unerwartete IP- oder Port-Endpunkte an einem der beiden Messpunkte. |
| 130 | <code>    key = lambda p: (p[&quot;src_ip&quot;], p[&quot;dst_ip&quot;], p[&quot;ip_id&quot;], p[&quot;transport_hex&quot;])</code> | Identifiziert Pakete über logische Richtung, IPv4-ID und vollständige TCP-Bytes. |
| 131 | <code>    require(Counter(map(key, a)) == Counter(map(key, b)), &quot;TCP-Pakete vor/nach Router verschieden&quot;)</code> | Verlangt dieselbe Paketmultimenge einschließlich aller SYN-, Daten-, ACK- und FIN-Segmente. |
| 132 | <code>    for p in a:</code> | Vergleicht jedes TCP-Paket an beiden Seiten des Routers. |
| 133 | <code>        q = next(q for q in b if key(p) == key(q))</code> | Sucht den Byte-identischen TCP-Partner anhand des hopübergreifenden Schlüssels. |
| 134 | <code>        upstream = p[&quot;src_ip&quot;] == &quot;10.0.1.2&quot;</code> | Unterscheidet Client-zu-Server von Server-zu-Client für die TTL-Orientierung. |
| 135 | <code>        require(p[&quot;ttl&quot;] - q[&quot;ttl&quot;] == (1 if upstream else -1), &quot;TCP-TTL-Änderung falsch&quot;)</code> | Berücksichtigt, dass LAN A in Antwortrichtung hinter und nicht vor dem Router liegt. |
| 136 | <code>        require(p[&quot;ip_checksum_valid&quot;] and q[&quot;ip_checksum_valid&quot;] and p[&quot;tcp_checksum_valid&quot;] and q[&quot;tcp_checksum_valid&quot;], &quot;TCP/IP-Prüfsumme falsch&quot;)</code> | Validiert sowohl IPv4 als auch die inklusive Pseudoheader berechnete TCP-Checksumme an beiden Seiten. |
| 137 | <code>        require(p[&quot;ip_checksum&quot;] != q[&quot;ip_checksum&quot;], &quot;TCP-IPv4-Prüfsumme unverändert&quot;)</code> | Belegt die wegen TTL-Änderung angepasste IPv4-Checksumme auch bei TCP-Paketen. |
| 138 | <code>        expected_a = (&quot;00:00:00:00:00:01&quot;, &quot;02:00:00:00:01:01&quot;)</code> | Definiert die beiden lokalen LAN-A-MACs in Client-Senderichtung. |
| 139 | <code>        expected_b = (&quot;02:00:00:00:02:01&quot;, &quot;00:00:00:00:00:03&quot;)</code> | Definiert die beiden lokalen LAN-B-MACs in derselben logischen Richtung. |
| 140 | <code>        require((p[&quot;src_mac&quot;], p[&quot;dst_mac&quot;]) == expected_a[::1 if upstream else -1], &quot;LAN-A-MACs falsch&quot;)</code> | Kehrt das LAN-A-MAC-Paar bei Serverantworten um und prüft es exakt. |
| 141 | <code>        require((q[&quot;src_mac&quot;], q[&quot;dst_mac&quot;]) == expected_b[::1 if upstream else -1], &quot;LAN-B-MACs falsch&quot;)</code> | Prüft analog das LAN-B-MAC-Paar einschließlich der Server-MAC aus der Vorlage. |
| 142 | <code>    syn = [p for p in a if p[&quot;tcp_flags&quot;] &amp; 0x12 == 0x02]</code> | Isoliert SYN-Segmente ohne ACK anhand der beiden entsprechenden Steuerbits. |
| 143 | <code>    require(len(syn) == 1, &quot;Genau ein initiales SYN erwartet&quot;)</code> | Verlangt genau einen normalen Verbindungsbeginn für diesen kleinen kontrollierten Testfluss. |
| 144 | <code>    opening = syn[0]</code> | Bewahrt das reale eröffnende SYN als erklärbaren Headerbeleg auf. |
| 145 | <code>    synack = [p for p in a if p[&quot;tcp_flags&quot;] &amp; 0x12 == 0x12 and p[&quot;tcp_ack&quot;] == opening[&quot;tcp_seq&quot;] + 1]</code> | Sucht ein SYN/ACK, dessen ACK genau die initiale Client-Sequenz plus eins bestätigt. |
| 146 | <code>    require(len(synack) == 1, &quot;Passendes SYN/ACK fehlt&quot;)</code> | Verlangt die eindeutige passende Serverantwort auf das SYN. |
| 147 | <code>    require(any(p[&quot;src_ip&quot;] == opening[&quot;src_ip&quot;] and p[&quot;tcp_flags&quot;] &amp; 16 and p[&quot;tcp_ack&quot;] == synack[0][&quot;tcp_seq&quot;] + 1 for p in a), &quot;Handshake-ACK fehlt&quot;)</code> | Verlangt clientseitig ein ACK der initialen Server-Sequenz plus eins als dritten Handshake-Schritt. |
| 148 | <code>    require(not any(p[&quot;tcp_flags&quot;] &amp; 4 for p in a), &quot;Unerwartetes TCP-RST&quot;)</code> | Verwirft einen Reset, weil der gewählte vollständige Normalfluss geordnet enden soll. |
| 149 | <code>    fins = [p for p in a if p[&quot;tcp_flags&quot;] &amp; 1]</code> | Isoliert alle tatsächlich beobachteten FIN-Segmente. |
| 150 | <code>    require(len(fins) == 2 and len({p[&quot;src_ip&quot;] for p in fins}) == 2, &quot;Beidseitiger FIN-Abschluss fehlt&quot;)</code> | Verlangt je einen geordneten Sendeschluss von beiden IP-Endpunkten. |
| 151 | <code>    for p in fins:</code> | Prüft jede der beiden FIN-Sequenzpositionen auf Bestätigung. |
| 152 | <code>        end = p[&quot;tcp_seq&quot;] + len(bytes.fromhex(p[&quot;payload_hex&quot;])) + 1</code> | Zählt eventuelle Daten im FIN-Segment und das FIN selbst im Sequenzraum mit. |
| 153 | <code>        require(any(q[&quot;src_ip&quot;] == p[&quot;dst_ip&quot;] and q[&quot;tcp_flags&quot;] &amp; 16 and q[&quot;tcp_ack&quot;] == end for q in a), &quot;FIN nicht bestätigt&quot;)</code> | Verlangt ein Gegenrichtungs-ACK genau bis hinter die jeweilige FIN-Position. |
| 154 | <code>    observed_request, observed_response = tcp_stream(a, &quot;10.0.1.2&quot;), tcp_stream(a, &quot;10.0.2.10&quot;)</code> | Rekonstruiert die echte Anfrage und Antwort unabhängig von ihrer TCP-Segmentierung. |
| 155 | <code>    require(observed_request == request and observed_response == response, &quot;HTTP-Nutzdaten stimmen nicht&quot;)</code> | Vergleicht beide rekonstruierten Bytefolgen vollständig mit den eigenen Anwendungsnachrichten. |
| 156 | <code>    return dict(packets=len(a), syn=opening, synack=synack[0], fins=fins, request=observed_request.decode(&quot;ascii&quot;), response=observed_response.decode(&quot;ascii&quot;), request_bytes=len(request), response_bytes=len(response), all_checksums_valid=True, router_packets_matched=len(a))</code> | Liefert reale Handshake- und FIN-Header, beide HTTP-Texte, Bytezahlen und die bestandenen Hop-Prüfungen. |

KI-Kennzeichnung: Hermes Agent, OpenAI gpt-6.1-sol, ChatGPT or Codex Subscription; 2026-10-29. Auftrag: eigene reale Messimplementierung und exakte Zeilenerklärung für RN Blatt08.
