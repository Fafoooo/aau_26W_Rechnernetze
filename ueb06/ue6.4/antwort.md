# 6.4 – IPv4-Subnetting und Adressplanung

## Annahmen und Verfahren

Frei gewählter privater RFC-1918-Pool: **10.10.0.0/23**. Je ein getrenntes Subnetz für 200 Endgeräte, 50 Server, 20 Management-Geräte und zwei Routerinterfaces einer Punkt-zu-Punkt-Verbindung. Gatewayinterfaces benötigen ebenfalls Adressen; selbst bei einem zusätzlichen Gateway pro LAN reichen die gewählten Netze aus. Die Management-Anforderung wird unabhängig davon vollständig reserviert.

VLSM bedeutet unterschiedliche Präfixlängen im selben Adresspool. Absteigend nach Bedarf werden ausgerichtete, nicht überlappende Blöcke vergeben. Für klassische IPv4-Subnetze gilt: nutzbare Hosts = 2^(32 − Präfix) − 2 (Netz- und Broadcastadresse ausgeschlossen).

| Bereich | Bedarf | Netz/Präfix | Maske | Erster Host | Letzter Host | Broadcast | Nutzbare Hosts | Reserve |
|---|---:|---|---|---|---|---|---:|---:|
| Endgeräte | 200 | 10.10.0.0/24 | 255.255.255.0 | 10.10.0.1 | 10.10.0.254 | 10.10.0.255 | 254 | 54 |
| Server | 50 | 10.10.1.0/26 | 255.255.255.192 | 10.10.1.1 | 10.10.1.62 | 10.10.1.63 | 62 | 12 |
| Management | 20 | 10.10.1.64/27 | 255.255.255.224 | 10.10.1.65 | 10.10.1.94 | 10.10.1.95 | 30 | 10 |
| Router-P2P | 2 | 10.10.1.96/30 | 255.255.255.252 | 10.10.1.97 | 10.10.1.98 | 10.10.1.99 | 2 | 0 |

## Präfixwahl, jeweils auch Prüfung des nächstkleineren Blocks

- **Endgeräte:** 2^8 − 2 = 254 ≥ 200; 2^7 − 2 = 126 < 200. Daher /24 unter der klassischen Netz/Broadcast-Konvention minimal.
- **Server:** 2^6 − 2 = 62 ≥ 50; 2^5 − 2 = 30 < 50. Daher /26 unter der klassischen Netz/Broadcast-Konvention minimal.
- **Management:** 2^5 − 2 = 30 ≥ 20; 2^4 − 2 = 14 < 20. Daher /27 unter der klassischen Netz/Broadcast-Konvention minimal.
- **Router-P2P:** 2^2 − 2 = 2 ≥ 2; 2^1 − 2 = 0 < 2. Daher /30 unter der klassischen Netz/Broadcast-Konvention minimal.

Die Blöcke belegen 356 von 512 Adressen. Frei bleiben 156 Adressen: 10.10.1.100–10.10.1.255 (kein einzelner CIDR-Block).

## Vergleich mit der RN-Lab-Topologie

Das Lab verwendet 10.0.1.0/24 zwischen Client und r1 sowie 10.0.2.0/24 zwischen r2 und Server: jeweils 254 nutzbare Adressen, obwohl im abgebildeten Lab nur zwei Interfaces je LAN vorkommen. Unser Endgeräte-/24 passt auch für 200 Geräte; /26 und /27 vermeiden im Server- und Management-LAN unnötige /24-Reservierungen. Ein /24 pro Bereich wäre für diese kleinen Segmente möglich, aber weniger sparsam. Alle vorgeschlagenen Netze und Lab-Netze gehören zum privaten Bereich 10.0.0.0/8.

Der Transit des Labs ist 10.0.12.0/30, mit r1=10.0.12.1 und r2=10.0.12.2; Netzadresse .0 und Broadcast .3. Unser Transit 10.10.1.96/30 folgt derselben Konvention: r1=10.10.1.97, r2=10.10.1.98. /31 wäre auf einer RFC-3021-fähigen echten P2P-Verbindung möglich, verwendet aber keine klassische Netz-/Broadcastaufteilung. Hier wird /30 gewählt, damit alle geforderten Tabellenattribute und der Vergleich zum Lab einheitlich bleiben.

## Reproduktion und echte Prüfungen

`python3 ueb06/ue6.4/subnetting.py` (ab Repository-Wurzel). Das Programm prüft vor jeder Ausgabe exakte Netze, Poolzugehörigkeit, ausreichende/minimale Kapazität, Hostzählung, Überschneidungsfreiheit und acht Präfix-Grenzfälle per `assert`. Erfolgreiche Ausgabe bedeutet: alle Prüfungen bestanden.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.

