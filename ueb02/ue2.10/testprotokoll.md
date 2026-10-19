# Ü2.10 – tatsächliches Prüfprotokoll

Prüfung: 2026-10-19T13:41:21+02:00

## Ergebnis

- Python-Syntax beider abgegebenen Dateien geprüft.
- Jede Zeilennummer beider Python-Dateien hat genau einen Eintrag in `../erklaerung_capture.md`.
- Alle lokalen Markdown-Nachweislinks in antwort.md und gui_kontrolle.md existieren.
- Originalaufnahme: 7/7 Offline-Tests bestanden.
- Zweiter tatsächlicher Live-Lauf: 7/7 Offline-Tests bestanden.
- Vier echte GUI-CSV-Exporte gelesen; TCP-Richtungssummen und Gesamtzahlen geprüft.
- Sieben PNG-Screenshots vorhanden und als PNG validiert; die wesentlichen GUI-Ansichten wurden zusätzlich visuell gelesen.

## Tatsächliche Aufnahmen

### .

```json
{
  "directory": ".",
  "packets": 10,
  "frame_bytes": 855,
  "client_bytes": 61,
  "server_bytes": 118,
  "pcap_file_bytes": 1039,
  "sha256": "10fa639adfee0f7d6c44ce0db0f4e5909690c30d530b08cc505f8b8d9f2024c4",
  "client_port": 52599,
  "server_port": 44625,
  "flags": [
    "0x2",
    "0x12",
    "0x10",
    "0x18",
    "0x10",
    "0x18",
    "0x10",
    "0x11",
    "0x11",
    "0x10"
  ]
}
```

### wiederholung

```json
{
  "directory": "wiederholung",
  "packets": 10,
  "frame_bytes": 855,
  "client_bytes": 61,
  "server_bytes": 118,
  "pcap_file_bytes": 1039,
  "sha256": "44b0506c51864985df4a714a4dc5f6b345ae5fe95526695325bc6ceb75111935",
  "client_port": 34503,
  "server_port": 46071,
  "flags": [
    "0x2",
    "0x12",
    "0x10",
    "0x18",
    "0x10",
    "0x18",
    "0x10",
    "0x11",
    "0x11",
    "0x10"
  ]
}
```

## Hinweise zur Durchführung

- Ein erster Versuch, dumpcap den Home-Ausgabepfad selbst öffnen zu lassen, scheiterte mit Permission denied.
- Die endgültige Lösung verwendet dumpcaps reguläre stdout-Ausgabe und einen bereits von unprivilegiertem Python geöffneten Dateideskriptor. Kein AppArmor-Profil geändert, kein tshark zur Umgehung von Dateiregeln benutzt.
- Die Ausgabe im Format pcap besitzt hier Nanosekunden-Zeitstempel. Der Offline-Parser unterstützt deshalb beide klassischen PCAP-Zeitskalen.
- XWD vom X11-Rootfenster zeigte Popup-Dialoge schwarz; die endgültigen Statistik-Screenshots wurden mit ffmpeg x11grab direkt vom sichtbaren X11-Bildschirm aufgenommen.
- Die GUI wurde unter Xvfb tatsächlich bedient; der eigene Live-Verkehr wurde mit dumpcap, nicht mit einem zusätzlichen GUI-Capture, aufgezeichnet.

## KI-Kennzeichnung

Hermes Agent, OpenAI gpt-6.1-sol, 19.10.2026. Anfrage: Ü2.10 praktisch durchführen, ausschließlich eigene harmlose Loopback-HTTP-Kommunikation aufzeichnen, Tests und Nachweise liefern und alle abgegebenen Python-Zeilen erklären.
