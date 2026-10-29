# Ü4.3 – UDP-Anwendung

## Ausführen in der Labor-VM

Die Programme entsprechen dem **einseitigen UDP-Beispiel der PDF**: kein Echo, keine Antwort erforderlich. Die Original-ZIP-Beispiele ergänzen dagegen `ACK: `-Antworten und haben RN-Lab-IPs als Default. Diese beiden Varianten nicht vermischen. Unsere Dateien sind eigenständige Lösungen; `../Angabe/` bleibt unverändert.

Interaktive Zwei-Host-Topologie entsprechend Ü4.1 starten. `standard_mininet.py` öffnet keine CLI; für `/24` und einen controllerlosen OVS-Bridge-Switch kann in der vorbereiteten VM gestartet werden:

```sh
sudo mn --topo single,2 --ipbase 10.0.0.0/24 --mac --switch ovsbr --controller none
```

Dann `xterm h1 h2`. In beiden Fenstern ins gemeinsame Verzeichnis `ueb04/ue4.3` wechseln. Auf **h2**:

```sh
python3 -B server.py --count 3
```

Nach `READY 10.0.0.2:5000` auf **h1**:

```sh
python3 -B client.py
python3 -B client.py --message 'Geänderte Nachricht'
python3 -B client.py --message 'Grüße 🌍'
```

Jeder Clientlauf verwendet einen neuen Socket. Der Kernel vergibt den Quellport automatisch; ein anderer Port ist möglich, aber kein garantierter Unterschied. Der Server zeigt Quell-IP, tatsächlichen Quellport und die empfangenen Bytes. Nach drei Datagrammen endet er. Ohne `--count` wartet er bis Abbruch oder dem konfigurierbaren Inaktivitätstimeout (Default 300 Sekunden). `Ctrl+C` beendet ihn ebenfalls und schließt den Socket.

`client.connect()` auf einem UDP-Socket stellt **keine TCP-artige Verbindung und keinen Handshake** her: Es legt nur den Standardpeer fest. `send()` verschickt ein Datagramm. Dies ist für unseren einzelnen festen Empfänger gleichwertig zum `sendto()`-Muster der PDF. Die Nutzlast ist auf 4096 Bytes begrenzt, passend zum `recvfrom(4096)` im Blatt. Größere fremde Datagramme könnte dieser kleine Server abschneiden; er ist kein allgemeiner UDP-Dateidienst.

## Fragen

- **Server-IP:** Hier `10.0.0.2`, das Interface von h2; Port `5000`. Im späteren RN-Lab wäre explizit `--host 10.0.2.2` zu verwenden.
- **Nicht localhost:** `127.0.0.1` führt zum Loopback im **eigenen** Netzwerk-Namespace. Auf h1 erreicht man damit nicht h2. Dieselbe Loopback-IP kann in beiden Namespaces existieren und verschiedene Endpunkte bezeichnen.
- **Port 5000:** Identifiziert den UDP-Empfangsendpunkt innerhalb der Ziel-IP; `bind()` ordnet diesen Socket dem lokalen IP-/Port-Paar zu. Er ist frei für diese Anwendung gewählt, keine besondere UDP-Pflichtnummer. UDP- und TCP-Port 5000 sind verschiedene Transportendpunkte.
- **Warum `b"..."`:** Sockets übertragen Bytes, keine Python-Unicode-Objekte. Das `b`-Präfix erzeugt direkt Bytes. Für veränderlichen Text verwenden wir `message.encode("utf-8")`. `str` ohne Kodierung lässt sich nicht direkt an `sendto()` übergeben. UTF-8-Zeichen können mehrere Bytes benötigen.

## Reale Prüfung und Grenzen

```sh
python3 -B -W error::ResourceWarning -m unittest -v test_udp
```

`test_udp.py` prüft auf eigenen echten Loopback-Sockets die Originalnachricht, UTF-8, leere Datagramme, die 4096-Byte-Grenze, Überlänge, CLI-Fehler, Server-Timeout und drei echte CLI-Clientläufe. Ergebnisse stehen in `test_udp.txt`.

Zusätzlich wurden drei Datagramme zwischen **echten Linux-Netzwerk-Namespaces** mit `/24` und Linux-Bridge übertragen: `../nachweise/run01/udp-server.txt`, `udp-clients.txt`, `udp.pcap`, `udp-analyse.json`. Die Paketbytes sind unabhängig geprüft und in der echten Wireshark-GUI geöffnet. Das ist **kein behaupteter Mininet-/OVS-/xterm-Lauf**. Die VM-Schritte bleiben dort zu wiederholen; fehlende Labortools wurden entsprechend der Angabe nicht installiert.

## KI-Kennzeichnung

Hermes Agent, OpenAI **gpt-6.1-sol** (Hermes-Status: ChatGPT or Codex Subscription), **2026-10-29**. Anfrage sinngemäß: UDP-Beispiel aus Ü4.3 umsetzen, Nachricht verändern, alle Fragen beantworten, echte Socket-/CLI-Tests und isolierte Namespace-Tests durchführen; Herkunft der Messungen offenlegen. Keine Eigenleistung des Studierenden behauptet.
