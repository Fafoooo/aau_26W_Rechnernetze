# Prüfbericht – Blatt 09

Datum: 2026-10-29. KI-Kennzeichnung: Hermes Agent; OpenAI `gpt-6.1-sol`; Provider laut `hermes status`: ChatGPT or Codex Subscription.

## Ergebnis und offene Grenze

Die Gateway-Diagnose und Ein-Zeilen-Reparatur wurden in einem **echten isolierten Linux-Bridge-/veth-/Namespace-Nachbau** mit den unveränderten Original-TCP-Anwendungen getestet. Beide Clients scheitern vorher und funktionieren nachher. Der Nachbau ist **kein Mininet-/OVS-/xterm-Nachweis**, und er bildet die TCLink-Verzögerungen nicht nach. Die erfolgreiche Wiederholung in der vorgesehenen Kurs-VM bleibt offen.

Die Originaldatei `start_lab.py` wurde hier tatsächlich mit `/usr/bin/python3 -B start_lab.py` gestartet. Sie endet vor dem Aufbau bei `ModuleNotFoundError: No module named 'mininet'`; `mn` und `ovs-vsctl` stehen nicht zur Verfügung. Es wurde nichts installiert und keine VM-Ausführung erfunden.

## Tatsächlich ausgeführt

1. Original-PDF mit `pdftotext -layout` gelesen und alle drei Seiten bei 150 dpi gerendert und angesehen. Erfasst wurden Ü9.1, Ü9.3, Ü9.4, Ü9.5, Ü9.6; keine Ü9.2 in der Angabe.
2. Original-ZIP aus Moodle geladen; alle sieben Vorlagendateien gelesen und im späteren Test bytegenau mit dem Archiv verglichen.
3. `sudo -n /usr/bin/python3 -B messen.py`: **Exit 0**. Ein frischer äußerer Netzwerk-Namespace wurde vor jeder Netzänderung erzeugt. Vier Host-Namespaces, zwei Linux-Bridges und fünf veth-Links bilden das Lab ab. TCP-Server und Clients sind die unveränderten Originale. Diagnose und Vorher-PCAP-Prüfung erfolgen vor der einzigen serverseitigen `ip route replace default via 10.10.2.1 dev server-eth0`-Reparatur.
4. `python3 -B auswertung.py`: **Exit 0**. Zehn echte PCAPs mit dumpcap-Zählern geprüft. Vorher zwölf erfolglose ARP-Anfragen nach `.254`, SYNs beider Clients am Server, keine serverseitigen TCP-Rückpakete. Je Client vorher 0/3, nachher 3/3 Echo-Antworten. Nachher neun TCP-Pakete pro Verbindung, vollständiger Handshake, 28 Bytes Originalbegrüßung, bestätigte FINs und kein RST. Vergleich beider Routerinterfaces bestätigt MAC-/TTL-Änderung und gleiche IP-Endpunkte/Transportbytes.
5. `tcpdump -nn -e -vv -r ...`: beide Server-PCAPs unabhängig dekodiert, Ausgaben unter `nachweise/run01/` gesichert. Die Tests dekodieren zusätzlich alle zehn PCAPs mit tcpdump und vergleichen die Framezahlen.
6. `python3 -B -m unittest -v test_nachweise`: **11 Tests bestanden**, Python 3.14.7. Originaltreue, alle fünf CLIs, positive Belege, vier PCAP-Magic-Varianten, defekte Dateien, fünf TCP-Mutationen, Isolation-vor-Änderungen, Überschreibschutz, Bereitschaft nach leerem Poll und alle wörtlichen Zeilenerklärungen geprüft.
7. `/usr/bin/python3 -B -m unittest -v test_nachweise`: **dieselben 11 Tests bestanden**, Python 3.13.3. Gesicherte echte Testausgaben: `nachweise/run01/tests-python314.txt` und `tests-python313.txt`.
8. Unabhängige Instanz hat Angabe, Vorlagen, Programme, Antworten und PCAPs geprüft: [review.md](review.md). Kernlösung bestanden. Drei redaktionelle Befunde wurden danach behoben: ungenaue SYN/ACK-Erklärung korrigiert, Testdokumentation aktualisiert, dieser Prüfbericht angelegt. Die zum Reviewzeitpunkt noch unfertige Zeilenerklärung wurde vollständig ergänzt; beide finalen Testsuiten sind grün. Der historische Review wird nicht nachträglich als fehlerfreier Lauf umgeschrieben.

9. Abschließende Artefaktprüfung: sämtliche lokalen Markdown-Links und Python-Syntax gültig; Schutz-Hashes von Quellen, Originalen und Belegen unverändert. Fehlende, doppelte und veraltete Quelltextzeilen in der Zeilendokumentation wurden als getrennte Negativkontrollen jeweils korrekt erkannt. Ausgabe unter `nachweise/run01/artefakt-pruefung.txt`. Nach Ende des Laufs wurden keine zugehörigen Namespace-Halter, TCP-Server oder Capture-Prozesse mehr gefunden.

Die Originalvorlagen behalten ihre CRLF-Zeilenenden, und das echte Befehlsprotokoll behält die von `ip` ausgegebenen Leerzeichen. Die daraus entstehenden `git diff --check`-Hinweise werden nicht durch Verändern der Originale oder Rohbelege „bereinigt“; eigene Programme und Dokumentation werden getrennt geprüft.

## Was die Tests nicht behaupten

- Die Schutztests mit `Mock` führen keine neue Netzkonfiguration aus. Sie ergänzen die reale Messung; sie ersetzen sie nicht.
- Die ICMP-Prüfung zählt die passenden Echo-Replies pro Client; sie implementiert keine allgemeine Zuordnung sämtlicher ICMP-Fehlerquotes.
- Der Parser ist gezielt auf klassisches Ethernet-PCAP, unfragmentiertes IPv4, ARP, ICMP und TCP begrenzt, kein universeller Wireshark-Ersatz.
- Die Originalanwendung sendet nur die Begrüßung vom Server zum Client, keine Client-Nutzdaten. Eine erfolgreiche Client-Payload-Übertragung wird nicht erfunden.
- Kein Wireshark-GUI-Nachweis; tcpdump ist laut Angabe ausdrücklich zulässig.
- Keine Abgabe in Moodle, kein Abgabe-ZIP ohne bekannte Gruppennummer, keine Behauptung eigener studentischer Durchführung.

Alle Zahlen und Framebezüge gehören zu `nachweise/run01`. Neue Messungen müssen einen neuen Ordner erhalten und dürfen nicht mit diesen Belegen vermischt werden.
