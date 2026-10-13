# 🌐 Rechnernetze und Netzwerkprogrammierung — WS 2026/27

> AAU Klagenfurt · Teil von [`aau_W26`](https://github.com/Fafoooo/aau_W26)

---

## 🧭 Aufbau

- UE 621.800 bei Kurt Horvath, **prüfungsimmanent → Anwesenheitspflicht**
- **Keine Klausur, keine Kreuzerlliste** — Note aus Abgaben, Präsentation und Abschlussgespräch
- 2 parallele Gruppen (621.801 + 621.802), in Moodle getrennte Abgaben (Gruppe Horvath / Gruppe Alkhateeb)
- Inhalte: ISO/OSI–TCP/IP-Modell top-down (Anwendung → Transport → Netzwerk → Sicherung), Python-Netzwerkprogrammierung (I/O, Threads, Sockets), Mininet
- Tutorium: 621.806 (Raphael Walcher)

---

## 📊 Benotung

| Teil | Info | Gewicht |
|------|------|---------|
| Abgaben | alle Übungsblätter, alle Pflicht | 25 % |
| Präsentation | mind. 1× pro Gruppe/Person, Termine zu Semesterbeginn | 25 % |
| Abschlussgespräch | Einzelgespräch über Abgaben, Code und Übungsthemen | 50 % |

Notenschema (Punkte): 1 = 89–100 · 2 = 76–88 · 3 = 63–75 · 4 = 50–62 · 5 = 0–49

---

## 📝 Abgaben

- Gruppenarbeit, **max. 3 Personen** — Einteilung über die Google-Tabelle aus den Aufnahme-Folien (Moodle)
- Abgabe in Moodle, **2 h vor LV-Beginn** (Blatt 1: Di 20.10. 08:00)
- Format: **eine Datei `uebxx-gruppeyy.zip`** (xx = Blattnummer, yy = Gruppennummer) inkl. Blatt-/Gruppen-Info

---

## 🛠️ Arbeitsumgebung

- Blatt 1–3: **Python**
- Blatt 4–10: **Mininet + Python** (≥ 3.8.5)
- Mininet: VirtualBox-Images (x86 / Apple ARM) aus Moodle, Linux nativ ([mininet.org](https://mininet.org/download/#option-3-installation-from-packages)) oder WSL mit eigenem Kernel ([wsl2-mininet](https://github.com/oscarhua/wsl2-mininet))
- Ablauf im Lab: `topology.py` → `start_lab.py` → Interfaces/Routen/`ping` prüfen → Python UDP/TCP → `tcpdump`/Wireshark
- Wichtige Befehle: `sudo mn`, `nodes`, `net`, `pingall`, `h1 ping -c 1 h2`, `xterm h1 h2`, `sudo mn --link tc,bw=10,delay=10ms`

---

## 🤖 KI-Nutzung

- **Ausdrücklich erlaubt**, aber Eigenverantwortung: Lösung läuft, ist kein Plagiat, funktioniert
- Muss an der Tafel und im Abschlussgespräch **erklärbar** sein
- **Kennzeichnungspflicht**: Tool, Version, Datum — bei direkt übernommenem Code auch die Anfrage, z. B. als Kommentar am Programmanfang

---

## 📚 Literatur

- Kurose, Ross — *Computer Networking: A Top-Down Approach*
- Tanenbaum, Wetherall — *Computer Networks*
- Peterson, Davie — *Computer Networks: A Systems Approach*

---

## 📂 Ordner

- `uebNN/` — pro Übungsblatt: Angabe, `ue<N>.<M>/` pro Teilaufgabe, `erklaerung_blattNN.md`

---

## ✅ To-do

- [ ] Gruppe festlegen und Gruppennummer für die ZIP-Namen notieren
- [ ] Präsentationstermin/Thema eintragen
- [ ] Mininet-Umgebung einrichten (ab Blatt 4)

---

<sub>Quelle: Folien „RN-Aufnahme-KH“ und „RN WS26 Mininet Getting Started“ (Moodle). Verbindlich ist Moodle.</sub>
