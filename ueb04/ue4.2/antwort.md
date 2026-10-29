# Ü4.2 – Separate Konsolen für virtuelle Hosts

## Ausgangspunkt und Belegstatus

Quelle: `../angabe_blatt04.pdf`, Ü4.2, sowie die vollständig gelesenen sechs Original-Python-Dateien in `../Angabe/`. `standard_mininet.py` setzt h1/h2 explizit auf `/24` (Z.12–13), öffnet aber **keine Mininet-CLI**: Z.30 wartet nur auf Enter. `xterm h1 h2` kann daher nicht an dessen `input()`-Prompt als Mininetbefehl ausgeführt werden.

Hier fehlen Mininet, xterm und OVS. Es wurde nichts installiert und keine Netzkonfiguration des aufrufenden Hosts verändert. Die zwei xterm-Fenster wurden **nicht geöffnet**; es werden keine GUI-Beobachtungen behauptet. Die Gegenüberstellung beschreibt erwartete Laborwerte. `../nachweise/run01/h1-network.txt`, `h2-network.txt` und `results.json` belegen zusätzlich zwei echte Linux-Netzwerk-Namespaces mit Linux-Bridge und `/24`, aber weder Mininet/OVS noch xterm. Private Hostdiagnosen werden nicht veröffentlicht.

Das geprüfte Original-ZIP enthält sechs Python-Dateien, aber entgegen dem Anhang **keine README.md**. Für die Lösung wurde keine Anleitung als Originaldatei ausgegeben.

## Durchführung in der vorbereiteten Labor-VM

Zunächst entsprechend der Angabe `sudo mn` verwenden. Falls der Referenzcontroller fehlt, kann für die gleiche Zwei-Host-/Ein-Switch-Struktur ohne Controller gearbeitet werden:

```console
sudo mn --topo single,2 --mac --switch ovsbr --controller none
```

Dann in der **Mininet-CLI**, nicht in einer gewöhnlichen Linux-Shell und nicht am `input()`-Prompt des Python-Skripts:

```console
mininet> xterm h1 h2
```

Voraussetzung ist eine funktionierende grafische Sitzung bzw. X11-Anzeige mit gesetztem `DISPLAY` und bereits installiertem xterm. `echo "$DISPLAY"` und `command -v xterm` sind lesende Prüfungen. Bei fehlender GUI keine Installation ändern; die bereitgestellte VM verwenden bzw. Übungsleitung kontaktieren. Als rein textbasierte Alternative lassen sich dieselben Netzwerkbefehle mit Präfixen `h1` und `h2` in der Mininet-CLI ausführen, dies ist aber **kein Nachweis zweier geöffneter xterm-Fenster**.

In **jedem** der beiden neu geöffneten Terminals ohne Hostpräfix ausführen:

```console
ip addr
ip route
hostname
readlink /proc/self/ns/net
readlink /proc/self/ns/uts
readlink /proc/self/ns/pid
readlink /proc/self/ns/mnt
```

## Ausgaben erklären und Unterschiede bestimmen

| Wert | Erwartet im h1-Terminal | Erwartet im h2-Terminal | Erklärung |
|---|---|---|---|
| Netzwerkinterface | `lo`, `h1-eth0` | `lo`, `h2-eth0` | Eigene virtuelle Ethernetinterfaces in verschiedenen Netzwerk-Namespaces; jedes hat sein eigenes Loopback. |
| IPv4 bei `sudo mn` bzw. obigem CLI-Start | `10.0.0.1/8` | `10.0.0.2/8` | Mininets CLI-Standard-IP-Basis ist `10.0.0.0/8`; die Hostadressen unterscheiden sich. |
| IPv4 beim unveränderten `standard_mininet.py` | `10.0.0.1/24` | `10.0.0.2/24` | Explizite Python-Konfiguration, nicht mit dem `/8`-CLI-Standard vermischen. Das Skript hat selbst keine CLI zum xterm-Aufruf. |
| Loopback-IPv4 | gewöhnlich `127.0.0.1/8` | gewöhnlich `127.0.0.1/8` | Gleiche Adresse, aber je Namespace ein anderer lokaler Endpunkt. |
| Route beim CLI-Standard | `10.0.0.0/8 dev h1-eth0 scope link src 10.0.0.1` | `10.0.0.0/8 dev h2-eth0 scope link src 10.0.0.2` | Gleiches Zielnetz, anderes Ausgangsinterface und andere bevorzugte Quelladresse. Zusätzliche Felder wie `proto kernel` sind möglich. |
| Route bei explizitem `/24` | `10.0.0.0/24 dev h1-eth0 scope link src 10.0.0.1` | `10.0.0.0/24 dev h2-eth0 scope link src 10.0.0.2` | Route passt zum gesetzten Präfix. |
| Default Route | im unveränderten Zwei-Host-Fall normalerweise keine | entsprechend keine | Kommunikation im direkt angeschlossenen Netz braucht keinen Router/Defaultweg. |
| MAC-Adresse | bei Start oben `00:00:00:00:00:01` | bei Start oben `00:00:00:00:00:02` | `--mac` fordert deterministische Host-MACs; bei anderem Start konkrete Ausgabe prüfen, nicht übernehmen. |
| `hostname` | VM-/UTS-Hostname | üblicherweise derselbe VM-/UTS-Hostname | Netzwerk-Namespace und UTS-Namespace sind verschiedene Mechanismen. Mininet erzeugt standardmäßig keine individuellen UTS-Hostnamen. |
| Netzwerk-Namespace-ID | eigene `net:[…]`-ID | andere `net:[…]`-ID | Unterschiedliche Netzwerkgeräte und Netzwerkstackzustände. Die konkreten Nummern sind Laufzeitdaten. |
| UTS-/PID-/Mount-Namespace-ID | bei normalem Mininet geteilt | jeweils dieselbe ID wie h1 | Ein Netzwerk-Namespace isoliert nicht automatisch Hostnamen, PID-Sicht oder Dateisystem. |

`ip addr` enthält außerdem Linkstatus, MTU und gegebenenfalls IPv6-Adressen. Interfaceindizes, Peerindizes und MACs können je nach Startoptionen/Lauf variieren. Darum gehören genaue Ausgaben in einen echten Laufbericht und nicht in eine aus Quellen abgeleitete Sollwerttabelle.

**Warum gehören die Fenster zu unterschiedlichen Hosts?** Die von Mininet gestartete Shell läuft im Netzwerk-Namespace des jeweiligen Knotens. Ihre Kindprozesse erben diesen Netzwerk-Kontext. Deshalb bearbeitet `ip addr` im h1-Terminal h1s Netzsicht und im h2-Terminal h2s Netzsicht. Der Fenstertitel und das Ergebnis von `hostname` sind dagegen keine zuverlässigen Namespace-Nachweise.

**Was ist nicht getrennt?** Beide Prozesse laufen auf demselben Kernel. Normales Mininet trennt nicht automatisch UTS-, PID- und Mount-Namespace. Netzwerk-Namespaces ordnen Prozesse einer Netzsicht zu, verstecken aber nicht allgemein alle anderen Prozesse. Die Einführung ist in dieser Hinsicht verkürzt. Programme und Dateien sind gewöhnlich gemeinsam sichtbar. `pwd` ist pro Prozess/Shell veränderlich und muss nicht identisch sein, belegt jedoch auch bei Gleichheit kein getrenntes Dateisystem.

Nach der Arbeit beide Zusatzterminals schließen und in der Mininet-CLI `exit` ausführen. Keine zurückbleibenden eigenen Terminals/Prozesse als bereits bereinigt behaupten, ohne es zu prüfen.

## Ausführbare Diagnose und Tests

```console
./diagnose.py --self-test
./diagnose.py --output weiterer-hostlauf.json
```

Die lokale Diagnose führt `ip addr`, `ip route`, `hostname`, die Version des verwendeten Python-Interpreters, `pwd`, `printenv PATH` und `ip -details link show` aus. Sie dokumentiert zusätzlich die eigenen net-/uts-/pid-/mnt-Namespace-IDs, UTC-Zeit und Verfügbarkeit der Labortools. Es gibt keine Shell-Interpolation, keine Privilegienerhöhung und keine aktiven Netzproben.

In den echten xterm-Fenstern kann das Skript über seinen absoluten Pfad im **jeweiligen bereits bestehenden** Namespace gestartet werden:

```console
# Im h1-Terminal:
python3 /pfad/zum/repo/ueb04/ue4.2/diagnose.py --context h1 --output h1-diagnose.json
# Im h2-Terminal:
python3 /pfad/zum/repo/ueb04/ue4.2/diagnose.py --context h2 --output h2-diagnose.json
```

Bei anderer VM-Ablage Pfade anpassen. Das Label `--context h1` allein wechselt keinen Namespace und beweist keine Mininetherkunft! Unterschiedliche Ausgabedateien sind nötig, weil das Dateisystem gemeinsam ist. `--output` akzeptiert nur einen neuen einfachen Dateinamen direkt im Aufgabenordner und überschreibt nichts. Ohne Option erfolgt nur JSON-Ausgabe auf stdout. Exitcode 1 dokumentiert mindestens einen fehlgeschlagenen Befehl; Fehlerausgaben bleiben erhalten; Exitcode 2 bezeichnet Argument-/Speicherfehler.

**Tatsächlich ausgeführt:** Acht unittest-Testmethoden pro Skript bestehen, siehe `self-test.txt`. Test-Mocks sind keine Mininetdaten. Echte Linux-Namespace-Netzwerte und die Prüfung verschiedener net-Namespaces bei gleichem UTS-Namespace stehen in den oben genannten Nachweisen. Die Erklärung aller eigenen Codezeilen steht in `erklaerung.md`. Echte Mininet-/xterm-Belege sind weiterhin ausständig. Diagnoseausgaben enthalten lokale Systeminformationen; vor einer Veröffentlichung prüfen.

## KI-Kennzeichnung

Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-29**. Tatsächliche Anfrage sinngemäß: vollständige, sachlich korrekte Lösungen für Ü4.1, Ü4.2 und Ü4.5 mit read-only Python-Hostdiagnosen, echten Selbsttests und zeilenweisen Erklärungen erstellen; Originalquellen und KI-Policy beachten, nichts installieren und keine Hostdiagnose als Mininetdaten darstellen.
