# Übungsblatt06 – IP, Subnetting und Routing

[Originalangabe](angabe_blatt06.pdf) · [Schritt-für-Schritt-Erklärung](erklaerung_blatt06.md) · [Prüfbericht](pruefung.md) · [Unabhängige Prüfung](review.md)

**⚠️ Mininet-/OVS-Abnahme in der vorbereiteten VM steht noch aus.** Hier wurden keine Pakete installiert. Vorhandene echte Linux-Namespace-Messungen und synthetische Mininet-API-Tests sind getrennt gekennzeichnet. Lösungen nicht als vollständig in Mininet geprüft ausgeben.

## Aufgaben

- [6.1 Interfaces und IP-Adressen](ue6.1/antwort.md): Originalkonfiguration und JSON-Auswertung.
- [6.2 Routingtabellen](ue6.2/antwort.md): Forwardingtabellen, Next Hops, Hin-/Rückweg.
- [6.3 Statische Routen](ue6.3/antwort.md): löschen, fehlende Verbindung zeigen, manuell wiederherstellen, Ping streng prüfen.
- [6.4 Subnetting](ue6.4/antwort.md): vollständiger VLSM-Adressplan und Kapazitätsproben.
- [6.5 Dijkstra](ue6.5/antwort.md): komplette Schritttabelle, kürzeste Pfade einschließlich Gleichständen.
- [6.6 Distance Vector](ue6.6/antwort.md): Initialisierung, alle B-Tabellen, markierte Änderungen und erklärte synchrone/asynchrone Interpretation.
- [6.7 Zusätzlicher Client](ue6.7/antwort.md): gemeinsame LAN-Bridge, erweiterte Topologie und separater Mininet-Starter; Original-TCP-Code unverändert.

## Reproduzierbare Tests

Vom Repository-Stamm:

```sh
python3 -B ueb06/checks.py
```

Der Gesamttest lief erfolgreich: **9 Testgruppen**, darin **4 Routing-, 6 Algorithmen- und 7 Topologie-API-Tests**. Python 3.12 oder neuer wird für den optionalen Namespace-Runner benötigt; der reine Gesamttest erzeugt keine Netzwerke und braucht kein root.

Der bereits erfolgte echte Namespace-Lauf liegt unter [nachweise/run01](nachweise/run01). Er belegt Adressierung, Routenlöschung samt Wiederanlage, Ping und die unveränderten TCP-Echos des alten sowie neuen Clients. Kein Mininet, kein OVS, keine TC-Verzögerungen. Die Run-Dateien werden nicht automatisch überschrieben.

**Noch manuell:** Erweiterungsstarter in der vorbereiteten Mininet-/OVS-VM ausführen, [Anleitung 6.7](ue6.7/antwort.md) befolgen und die dortigen Messungen ergänzen. Gruppennummer unbekannt, daher kein Abgabe-ZIP erstellt. Nichts in Moodle abgegeben.

## Quellen und Kennzeichnung

`Angabe/` enthält das echte Moodle-Vorlagenarchiv und seine elf bytegenau unveränderten Dateien. Eine eigene Arbeitskopie von `topology.py` liegt ausschließlich in `ue6.7/`; der pauschale Änderungsverbots-/6.8-Kommentar widerspricht dem expliziten Arbeitsauftrag6.7 und wird dort erläutert.

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol; Anbieter laut `hermes status`: ChatGPT or Codex Subscription; Datum2026-10-29. Auftrag: Übungsblatt06 vollständig lösen, Originalvorlagen und KI-Regel beachten, ausführbaren Code, Antworten, zeilenweise Erklärung und echte Prüfungen erstellen. Menschliche Eigenleistung wird nicht behauptet.
