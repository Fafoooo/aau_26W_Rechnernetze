# 6.2 – Routingtabellen und beidseitiger Paketweg

## 1. Tabellen erheben und richtig einordnen

In den vier Knotenterminals jeweils `ip route` ausführen. Zusätzlich sind `ip route get 10.0.2.2` auf client/r1 und `ip route get 10.0.1.2` auf server/r2 hilfreich. `ip route` zeigt üblicherweise die IPv4-Haupttabelle; lokale Eigenadressen liegen zusätzlich in der Tabelle `local` (`ip route show table local`). Zieladressen eigener Interfaces werden lokal zugestellt statt weitergeleitet.

Die folgenden Tabellen sind aus `Angabe/start_lab.py` abgeleitete **Solltabellen**, keine hier erhobenen Mininet-Ausgaben. Durch das Setzen einer Interfaceadresse legt Linux die direkt angeschlossenen Netzrouten an. Die beiden zusätzlichen Netzrouten werden ausdrücklich gesetzt. `src`-Hinweise, `proto kernel` und die Reihenfolge können in einer echten Ausgabe zusätzlich vorkommen.

## 2. Kleine Forwardingtabellen

| Router | Zielpräfix | Next Hop | Ausgangsinterface | Herkunft |
|---|---|---|---|---|
| r1 | 10.0.1.0/24 | direkt: jeweilige Ziel-IP | r1-eth0 | angeschlossen |
| r1 | 10.0.12.0/30 | direkt: jeweilige Ziel-IP | r1-eth1 | angeschlossen |
| r1 | 10.0.2.0/24 | 10.0.12.2 | r1-eth1 | explizite statische Route |
| r2 | 10.0.12.0/30 | direkt: jeweilige Ziel-IP | r2-eth0 | angeschlossen |
| r2 | 10.0.2.0/24 | direkt: jeweilige Ziel-IP | r2-eth1 | angeschlossen |
| r2 | 10.0.1.0/24 | 10.0.12.1 | r2-eth0 | explizite statische Route |

**Direkt** bedeutet: kein zwischengeschaltetes IP-Gateway; die MAC-Adresse der tatsächlichen Ziel-IP wird auf diesem Link benötigt. Die Router haben im Basisskript **keine Defaultroute**. Es gibt deshalb nach Entfernen der betreffenden statischen Route keinen Ersatzweg zum entfernten LAN.

Die Endgeräte haben zusätzlich zu ihrer angeschlossenen Netzroute:

| Knoten | Zielpräfix | Gateway | Interface |
|---|---|---|---|
| client | 0.0.0.0/0 | 10.0.1.1 | client-eth0 |
| server | 0.0.0.0/0 | 10.0.2.1 | server-eth0 |

## 3. Entscheidung nach längstem passenden Präfix

Die Ziel-IP wird mit allen relevanten Präfixen verglichen. Unter den passenden Routen gewinnt das **längste Präfix**: beispielsweise `/32` vor `/24` vor `/0`. Die Reihenfolge der gedruckten Zeilen ist dafür nicht entscheidend. Ein Clientziel `10.0.1.1` trifft seine direkte `/24`-Route und auch die `/0`-Route; die `/24` gewinnt. Für `10.0.2.2` passt am Client im Basisplan dagegen nur die Default Route. Metriken entscheiden gegebenenfalls zwischen vergleichbaren Routen; Policy Routing und ECMP sind in diesem Lab nicht eingerichtet und werden im kleinen Python-Modell nicht nachgebildet.

**Next-Hop-Erreichbarkeit:** r1 erreicht Gateway `10.0.12.2` über seine angeschlossene `/30`-Route, r2 entsprechend `10.0.12.1`. Ein Gateway muss über einen passenden lokalen Link erreichbar sein; es genügt nicht, irgendeine fremde IP hinter `via` zu schreiben.

## 4. Hinweg: 10.0.1.2 → 10.0.2.2

1. **Client:** Das Ziel liegt nicht im eigenen `10.0.1.0/24`. Die Default Route wählt `10.0.1.1` auf `client-eth0`. Falls der Nachbarcache keinen gültigen Eintrag enthält, fragt der Client per **ARP nach 10.0.1.1**, nicht nach dem entfernten Server.
2. **r1:** Das empfangene Paket ist nicht an eine eigene IP adressiert. Bei aktiviertem `net.ipv4.ip_forward=1` wird die Route `10.0.2.0/24 via 10.0.12.2 dev r1-eth1` gewählt. ARP gilt hier dem direkt angeschlossenen Gateway **10.0.12.2**.
3. **r2:** Das Ziel passt zur angeschlossenen Route `10.0.2.0/24 dev r2-eth1`. r2 fragt gegebenenfalls per ARP nach **10.0.2.2** und sendet direkt an die Server-MAC.
4. **Server:** Die Ziel-IP ist eine eigene Adresse, also lokale Zustellung an ICMP bzw. den passenden Transportprotokoll-Handler.

## 5. Rückweg: 10.0.2.2 → 10.0.1.2

1. **Server:** Außerhalb des eigenen `/24`, deshalb Default Gateway **10.0.2.1** über `server-eth0`; ARP nach diesem Gateway.
2. **r2:** Statische Route `10.0.1.0/24 via 10.0.12.1 dev r2-eth0`; ARP nach **10.0.12.1**.
3. **r1:** Angeschlossenes Zielnetz `10.0.1.0/24 dev r1-eth0`; ARP nach **10.0.1.2**, danach direkte Zustellung an den Client.
4. Ohne r2-Rückroute kann selbst ein beim Server angekommenes Echo Request nicht erfolgreich beantwortet werden. Ein vollständiger Ping prüft daher Hin- **und** Rückweg, nicht nur die Auslieferung des Requests.

## 6. Was sich je Hop ändert

Ohne NAT bleiben IPv4-Quell- und Zieladresse im Hinpaket `10.0.1.2` und `10.0.2.2`. Im Antwortpaket sind sie vertauscht. Die Ethernet-Quell-/Ziel-MAC-Adressen gelten dagegen jeweils nur auf einem Link und werden bei der Weiterleitung neu gesetzt. Jeder weiterleitende Router verringert die TTL und aktualisiert die IPv4-Header-Prüfsumme. Bei abgelaufener TTL wird nicht normal weitergeleitet; ICMP Time Exceeded kann zurückgesendet werden. ARP-Broadcasts werden nicht durch die Router bis zum Server transportiert; Cachetreffer vermeiden eine erneute ARP-Abfrage.

`ip_forward=1` ist auf **beiden** Routern nötig. Korrekte Routen allein reichen nicht: Linkstatus, Nachbarauflösung und etwaige Firewallregeln müssen die Weiterleitung ebenfalls zulassen. Das Original setzt Forwarding sowohl in `LinuxRouter.config()` als auch in `configure_base_network()`; es enthält für dieses Lab keine eigenen NAT- oder Firewallregeln.

## 7. Code und ausgeführte Prüfungen

```sh
python3 ueb06/ue6.2/routing.py
python3 ueb06/ue6.2/routing.py --test
```

Der normale Aufruf druckt beide Routertabellen und beide Paketwege einschließlich der aufzulösenden Nachbar-IP. Das ist ein ausdrücklich gekennzeichnetes Modell der bekannten Topologie, kein universeller Linux-Router. Tests prüfen beide Wege und Next Hops, eine konkurrierende `/32`-/`/24`-/`/0`-Auswahl, fehlende Route und deaktiviertes Forwarding. Siehe [testprotokoll.txt](testprotokoll.txt) und [zeilenweise Erklärung](../erklaerung_routing.md). Mininet/OVS/xterm selbst wurden hier mangels Installation nicht ausgeführt.

## Ergänzender realer Namespace-Nachweis

Im anschließend ausgeführten isolierten Linux-Namespace-Lauf wurden die Kernel-Routingtabellen tatsächlich ausgelesen: [r1](../nachweise/run01/basis-r1.txt), [r2](../nachweise/run01/basis-r2.txt), [Client](../nachweise/run01/basis-client.txt), [Server](../nachweise/run01/basis-server.txt). Die Hin-/Rückverbindung und die fehlende Erreichbarkeit nach Routenlöschung sind gemessen. Der [Gesamttest](../checks.py) prüft diese Nachweise. Es handelt sich **nicht um Mininet/OVS**; die vorbereitete VM ist weiterhin separat zu prüfen.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Implementiere ausschließlich ueb06/ue6.1, ue6.2, ue6.3 sowie ueb06/erklaerung_routing.md; je Aufgabe ausführbares Python, schrittweise Antworten und echte Tests.
