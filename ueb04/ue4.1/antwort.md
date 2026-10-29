# Ü4.1 – Mininet-Hosts untersuchen (einschließlich Einführung)

## Quellen und Belegstatus

Grundlage: `../angabe_blatt04.pdf`, Einführung und Ü4.1; sämtliche sechs Python-Dateien in `../Angabe/`; insbesondere `standard_mininet.py`, Zeilen 10–19. Die Aussagen zur RN-Lab-Infrastruktur werden in Ü4.5 getrennt behandelt. Die Kursregel zur KI-Kennzeichnung wurde gelesen.

**Konfiguration ist nicht Messung:** Hier ist Mininet nicht installiert. Der bereitgestellte Umgebungstest bestätigt fehlende Labortools. Es wurden keine Pakete installiert und keine Netzwerkeinstellungen des aufrufenden Hosts verändert. Erwartete Mininet-Werte unten sind Sollwerte. Zusätzlich liegen unter `../nachweise/run01/` echte Messwerte einer isolierten Linux-Namespace-Topologie mit Linux-Bridge und `/24` vor: **kein Mininet-/OVS-Nachweis**. Sie bestätigen getrennte Netzsicht bei gemeinsamem UTS-Namespace. Private Hostdiagnosen werden nicht veröffentlicht.

Das Original-ZIP `../Angabe/uebb4_template.zip` wurde mit `python3 -m zipfile -l` geprüft: Es enthält die sechs Python-Dateien, aber **keine `README.md`**, obwohl der Anhang eine solche nennt. Es wurde keine vermeintliche Original-README erfunden.

## Start und Einführung

Nur in der bereitgestellten Labor-VM zunächst `sudo mn --version` und `python3 --version` prüfen. Bei Problemen keine Systeminstallation ändern, sondern Übungsleitung kontaktieren. Die Angabe verlangt zunächst `sudo mn`. Bei fehlendem Referenzcontroller kann dieselbe Zwei-Host-/Ein-Switch-Struktur ohne Controller-Abhängigkeit so interaktiv untersucht werden:

```console
sudo mn --topo single,2 --mac --switch ovsbr --controller none
```

`ovsbr` verwendet einen OVS-Switch im Standalone-/Bridge-Modus. OVS und Mininet müssen in der VM bereits funktionieren. Auf diesem Host wurde dieser Start **nicht** ausgeführt. `standard_mininet.py` ist kein gleichwertiger interaktiver Start: Es öffnet **keine Mininet-CLI**, sondern wartet in Zeile 30 nur mit `input()` auf Enter. Die dort gedruckten `h1 ...`-Zeilen lassen sich daher nicht an diesem Eingabeprompt als Mininetbefehle ausführen. Das Originalskript wird nicht verändert.

| CLI-Befehl | Bedeutung |
|---|---|
| `nodes` | Namen der Mininet-Knoten, also Hosts, Switches und gegebenenfalls Controller. Beim Start oben: h1, h2, s1; bei einem Controllerstart zusätzlich etwa c0. Keine Liste aller Linux-Prozesse. |
| `net` | Verbindungen pro Knoten mit lokalen Interfaces und Gegeninterfaces; zeigt die Verkabelung h1–s1–h2. Kein IP-Routingplan. |
| `links` | Einzelne Links mit den beiden Interface-Endpunkten und Linkstatus, etwa h1-eth0↔s1-eth1 und h2-eth0↔s1-eth2. Die konkrete Portnummerierung ist zu prüfen. |
| `dump` | Detaillierte Repräsentation der Knoten, typischerweise Klasse, Name, Interfaces/IPs und PID. Feldumfang hängt vom Knotentyp und der Mininet-Version ab. Eine PID bedeutet keinen eigenen PID-Namespace. |
| `exit` | Beendet die CLI; Mininet stoppt die Topologie und räumt die zugehörigen Interfaces/Prozesse auf. Nach Beendigung kontrollieren, nicht pauschal vollständiges Cleanup behaupten. |

## IP-Präfix: zwei verschiedene Ausgangskonfigurationen

| Startquelle | h1 | h2 | Erwartete direkt verbundene Route auf h1 |
|---|---|---|---|
| `sudo mn` bzw. obiger CLI-Start **ohne `--ipbase`** | `10.0.0.1/8` | `10.0.0.2/8` | `10.0.0.0/8 dev h1-eth0 scope link src 10.0.0.1` |
| Original `standard_mininet.py`, Z.12–13 | explizit `10.0.0.1/24` | explizit `10.0.0.2/24` | `10.0.0.0/24 dev h1-eth0 scope link src 10.0.0.1` |

Die CLI-Standard-IP-Basis ist `10.0.0.0/8`; `/24` darf nicht stillschweigend vom Python-Beispiel übernommen werden. Mit explizitem `--ipbase 10.0.0.0/24` ließe sich ein interaktiver `/24`-Fall starten; dieser Zusatz gehört jedoch **nicht** zum unveränderten `sudo mn`. `proto kernel` und andere Anzeigefelder können zusätzlich erscheinen. Üblicherweise ist hier keine Default Route nötig oder vorkonfiguriert: beide Hosts liegen im selben direkt angeschlossenen Netz.

## Antworten auf alle Fragen

1. **Interfaces von h1:** Normalerweise `lo` und das virtuelle Ethernetinterface `h1-eth0`. `lo` ist die eigene Loopback-Schnittstelle des Netzwerk-Namespace, gewöhnlich mit `127.0.0.1/8`; `h1-eth0` führt über einen virtuellen Link zu s1. Es können IPv6- bzw. zusätzliche versionsabhängige Anzeigen auftreten; maßgeblich wäre `h1 ip addr`.
2. **IPv4 von h1:** Für die ungeänderte Standardtopologie `10.0.0.1/8`, beim gelieferten Python-Skript `10.0.0.1/24`; jeweils zusätzlich die Loopback-Adresse.
3. **IPv4 von h2:** Entsprechend `10.0.0.2/8` bzw. explizit `10.0.0.2/24`, zusätzlich Loopback im eigenen Netzwerk-Namespace.
4. **„Welche path ist auf h1 eingetragen?“** Die Formulierung ist mehrdeutig. Wegen der unmittelbar vorausgehenden `ip route`-Befehle ist vermutlich die **Route** gemeint: die direkt verbundene Netzroute aus obiger Tabelle. Falls stattdessen die Umgebungsvariable **`$PATH`** gemeint ist, enthält diese die Suchverzeichnisse für ausführbare Programme; ihr konkreter Wert muss gemessen werden und folgt nicht aus einer IP-Konfiguration. Beide Lesarten werden so überprüft:

   ```console
   mininet> h1 ip route
   mininet> h1 printenv PATH
   ```

5. **Virtuelles gegenüber normalem Rechnerinterface:** `h1-eth0` ist in dieser Mininet-Konfiguration ein Ende eines Linux-veth-Paars; das andere Ende ist am virtuellen Switch angeschlossen. Es hat keine eigene physische Netzkarte/Kabelbuchse. Eine physische Ethernet-/WLAN-Schnittstelle bindet dagegen Hardware an; auch auf einem normalen Rechner gibt es allerdings virtuelle Interfaces. Beide Interfacearten werden vom echten Linux-Netzwerkstack verarbeitet. Mininet emuliert kein eigenes Python-TCP/IP-Protokoll.

## Prozesse, Hostname und Isolation

In der Mininet-CLI ausführen:

```console
mininet> h1 ip addr
mininet> h2 ip addr
mininet> h1 ip route
mininet> h2 ip route
mininet> h1 hostname
mininet> h1 python3 --version
mininet> h1 pwd
mininet> h1 readlink /proc/self/ns/net
mininet> h2 readlink /proc/self/ns/net
mininet> h1 readlink /proc/self/ns/uts
mininet> h2 readlink /proc/self/ns/uts
mininet> h1 readlink /proc/self/ns/pid
mininet> h2 readlink /proc/self/ns/pid
mininet> h1 readlink /proc/self/ns/mnt
mininet> h2 readlink /proc/self/ns/mnt
```

- `hostname` liest den **UTS-Hostnamen**, nicht den Mininet-Knotennamen. Normales Mininet legt keine getrennten UTS-Namespaces an. Darum ist üblicherweise der VM-/Systemhostname in h1 und h2 gleich. **`h1 hostname` muss nicht `h1` ergeben.** Die Präfixe h1/h2 sind Befehlszuordnungen der Mininet-CLI.
- `python3 --version` zeigt den tatsächlich im jeweiligen Prozess gefundenen Interpreter. Bei gemeinsamem Dateisystem und gleichem PATH ist gewöhnlich dieselbe Python-Version verfügbar; ein venv oder geänderter PATH könnte dies ändern.
- `pwd` zeigt das Arbeitsverzeichnis des Prozesses. Ein Netzwerk-Namespace erzeugt weder ein eigenes Dateisystem noch ein eigenes Home-Verzeichnis. Beide Prozesse starten häufig mit demselben Arbeitsverzeichnis; `cd` kann es anschließend pro Shell ändern. Auch Mount- und PID-Namespaces sind bei normalem Mininet nicht automatisch pro Host getrennt.
- Ein in h1 gestartetes Programm erbt den **Netzwerk-Namespace von h1**. Geräte, Routen, Nachbartabellen, Loopback und Netzwerkstackzustand gehören zu diesem Namespace. Ein gewöhnlicher `ip addr`-Aufruf in h1 sieht deshalb nicht h2-eth0. Berechtigte Prozesse könnten einen Namespace gezielt wechseln; dies widerlegt die normale Trennung nicht.
- Die Einführung formuliert eine Trennung von „Prozessen“ durch Netzwerk-Namespaces zu weitgehend: Ein Prozess wird einem Netzwerk-Namespace zugeordnet, aber dessen Netzwerkisolation ist **keine allgemeine Prozess-/PID-Isolation**. h1/h2 teilen normalerweise den Kernel sowie den PID-Namespace. Gleiche UTS/PID/Mount-IDs, aber unterschiedliche net-IDs wären passende Belege; solche Ergebnisse werden hier nicht erfunden.

## Diagnoseprogramm, echte Tests und Grenzen

`diagnose.py` ist ausführbar und benötigt nur die Python-Standardbibliothek. Es führt ausschließlich lokale lesende Befehle aus, kein `sudo`, `ping`, Paketmitschnitt oder Konfigurationskommando. Es dokumentiert Argumentlisten, stdout, stderr, Exitcodes, UTC-Zeit, Namespace-IDs und Toolverfügbarkeit als JSON.

```console
./diagnose.py --self-test
./diagnose.py --output weiterer-hostlauf.json
```

Der zweite Aufruf schreibt eine **neue** Datei direkt in diesen Aufgabenordner, überschreibt nichts und bleibt ohne expliziten Namespacewechsel eine Hostdiagnose. Das Kontextlabel `--context` ist nur Text und kein Herkunftsbeweis. Exitcode 0: alle Diagnosebefehle erfolgreich; 1: mindestens ein Befehl gescheitert; 2: Argument-/Speicherfehler. Fehler bleiben im Bericht erhalten.

Im echten Mininet kann der passende absolute Pfad nach Hostpräfix ausgeführt werden, z.B. `h1 python3 /pfad/zum/repo/ueb04/ue4.1/diagnose.py --context h1 --output h1-diagnose.json`. Die Diagnose enthält lokale Systeminformationen und ist vor einer Weitergabe zu prüfen. Die gemessenen Namespace-IDs und Interfaces müssen zur gestarteten Topologie passen. Gemeinsames Dateisystem bedeutet: für h1 und h2 unterschiedliche Dateinamen verwenden.

**Tatsächlich geprüft:** Alle acht unittest-Testmethoden bestanden; `self-test.txt` protokolliert den Lauf. Geprüft sind Subprocess-Argumentlisten und Sicherheitsoptionen, Fehlerfälle, JSON, Ausgabepfadschutz und Herkunftshinweis. Mocks sind ausschließlich Testdaten. Echte isolierte Netzwerte: `../nachweise/run01/h1-network.txt` und `h2-network.txt`; Namespace-Vergleich: `results.json`. Die Zeilenerklärung steht in `erklaerung.md`. Der tatsächliche Mininetlauf bleibt in der VM zu prüfen.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-29**. Tatsächliche Anfrage sinngemäß: vollständige, sachlich korrekte Lösungen für Ü4.1, Ü4.2 und Ü4.5 mit read-only Python-Hostdiagnosen, echten Selbsttests und zeilenweisen Erklärungen erstellen; Originalangabe und KI-Policy beachten, nichts installieren, keine Hostdaten als Mininetdaten ausgeben. Der Text und Code wurden mit KI-Unterstützung erstellt, nicht als unbelegte Eigenleistung bezeichnet.
