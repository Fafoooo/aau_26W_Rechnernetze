# KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol
# Anbieter: ChatGPT or Codex Subscription; Datum: 2026-10-29.
# Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts,
# mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
"""VLSM-Adressplan; Ausführung erzeugt die geprüfte Markdown-Antwort."""
from ipaddress import IPv4Network
from pathlib import Path
from argparse import ArgumentParser

BASE = IPv4Network("10.10.0.0/23")
REQUIREMENTS = (("Endgeräte", 200), ("Server", 50), ("Management", 20), ("Router-P2P", 2))
NOTICE = "\n## KI-Kennzeichnung\n\nKI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.\n"

def prefix_for(hosts):
    for prefix in range(30, -1, -1):
        if 2 ** (32 - prefix) - 2 >= hosts:
            return prefix
    raise ValueError("Hostanforderung ist zu groß")

def allocate():
    cursor = int(BASE.network_address)
    result = []
    for name, demand in sorted(REQUIREMENTS, key=lambda item: -item[1]):
        prefix = prefix_for(demand)
        size = 2 ** (32 - prefix)
        cursor = ((cursor + size - 1) // size) * size
        network = IPv4Network((cursor, prefix))
        if not network.subnet_of(BASE):
            raise ValueError("Adresspool zu klein")
        result.append((name, demand, network))
        cursor += size
    return result

def verify(plan):
    expected = ("10.10.0.0/24", "10.10.1.0/26", "10.10.1.64/27", "10.10.1.96/30")
    assert tuple(str(row[2]) for row in plan) == expected
    for index, (_, demand, network) in enumerate(plan):
        assert network.subnet_of(BASE)
        assert network.num_addresses - 2 >= demand
        assert network.num_addresses // 2 - 2 < demand
        assert len(list(network.hosts())) == network.num_addresses - 2
        assert all(not network.overlaps(other[2]) for other in plan[index + 1:])
    assert prefix_for(254) == 24 and prefix_for(255) == 23
    assert prefix_for(62) == 26 and prefix_for(63) == 25
    assert prefix_for(30) == 27 and prefix_for(31) == 26
    assert prefix_for(2) == 30 and prefix_for(3) == 29

def render(plan):
    lines = ["# 6.4 – IPv4-Subnetting und Adressplanung", "", "## Annahmen und Verfahren", "", "Frei gewählter privater RFC-1918-Pool: **10.10.0.0/23**. Je ein getrenntes Subnetz für 200 Endgeräte, 50 Server, 20 Management-Geräte und zwei Routerinterfaces einer Punkt-zu-Punkt-Verbindung. Gatewayinterfaces benötigen ebenfalls Adressen; selbst bei einem zusätzlichen Gateway pro LAN reichen die gewählten Netze aus. Die Management-Anforderung wird unabhängig davon vollständig reserviert.", "", "VLSM bedeutet unterschiedliche Präfixlängen im selben Adresspool. Absteigend nach Bedarf werden ausgerichtete, nicht überlappende Blöcke vergeben. Für klassische IPv4-Subnetze gilt: nutzbare Hosts = 2^(32 − Präfix) − 2 (Netz- und Broadcastadresse ausgeschlossen).", "", "| Bereich | Bedarf | Netz/Präfix | Maske | Erster Host | Letzter Host | Broadcast | Nutzbare Hosts | Reserve |", "|---|---:|---|---|---|---|---|---:|---:|"]
    for name, demand, network in plan:
        lines.append(f"| {name} | {demand} | {network} | {network.netmask} | {network.network_address + 1} | {network.broadcast_address - 1} | {network.broadcast_address} | {network.num_addresses - 2} | {network.num_addresses - 2 - demand} |")
    lines += ["", "## Präfixwahl, jeweils auch Prüfung des nächstkleineren Blocks", ""]
    for name, demand, network in plan:
        bits = 32 - network.prefixlen
        lines.append(f"- **{name}:** 2^{bits} − 2 = {network.num_addresses - 2} ≥ {demand}; 2^{bits - 1} − 2 = {network.num_addresses // 2 - 2} < {demand}. Daher /{network.prefixlen} unter der klassischen Netz/Broadcast-Konvention minimal.")
    used = sum(network.num_addresses for _, _, network in plan)
    lines += ["", f"Die Blöcke belegen {used} von {BASE.num_addresses} Adressen. Frei bleiben {BASE.num_addresses - used} Adressen: 10.10.1.100–10.10.1.255 (kein einzelner CIDR-Block).", "", "## Vergleich mit der RN-Lab-Topologie", "", "Das Lab verwendet 10.0.1.0/24 zwischen Client und r1 sowie 10.0.2.0/24 zwischen r2 und Server: jeweils 254 nutzbare Adressen, obwohl im abgebildeten Lab nur zwei Interfaces je LAN vorkommen. Unser Endgeräte-/24 passt auch für 200 Geräte; /26 und /27 vermeiden im Server- und Management-LAN unnötige /24-Reservierungen. Ein /24 pro Bereich wäre für diese kleinen Segmente möglich, aber weniger sparsam. Alle vorgeschlagenen Netze und Lab-Netze gehören zum privaten Bereich 10.0.0.0/8.", "", "Der Transit des Labs ist 10.0.12.0/30, mit r1=10.0.12.1 und r2=10.0.12.2; Netzadresse .0 und Broadcast .3. Unser Transit 10.10.1.96/30 folgt derselben Konvention: r1=10.10.1.97, r2=10.10.1.98. /31 wäre auf einer RFC-3021-fähigen echten P2P-Verbindung möglich, verwendet aber keine klassische Netz-/Broadcastaufteilung. Hier wird /30 gewählt, damit alle geforderten Tabellenattribute und der Vergleich zum Lab einheitlich bleiben.", "", "## Reproduktion und echte Prüfungen", "", "`python3 ueb06/ue6.4/subnetting.py` (ab Repository-Wurzel). Das Programm prüft vor jeder Ausgabe exakte Netze, Poolzugehörigkeit, ausreichende/minimale Kapazität, Hostzählung, Überschneidungsfreiheit und acht Präfix-Grenzfälle per `assert`. Erfolgreiche Ausgabe bedeutet: alle Prüfungen bestanden."]
    return "\n".join(lines) + "\n" + NOTICE

if __name__ == "__main__":
    plan = allocate()
    verify(plan)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Geprüfte antwort.md neben diesem Skript erzeugen")
    if parser.parse_args().write:
        destination = Path(__file__).with_name("antwort.md")
        destination.write_text(render(plan) + "\n", encoding="utf-8")
        print(f"Alle Prüfungen bestanden; erzeugt: {destination}")
    else:
        print(render(plan))
