# Ü 2.7 – Entwurf eines IEEE-802.11-Heimnetzes

**Aufgabe:** Ein WLAN-Heimnetz entwerfen und konkrete Produktmodelle mit ihren Kosten angeben.

## 1. Abgrenzung: ausdrücklich hypothetisches Referenzhaus

Grundriss, Baustoffe, Anschluss und vorhandene Geräte des tatsächlichen Hauses sind **nicht bekannt**. Deshalb ist das Folgende **keine Behauptung über mein Haus oder das Haus meiner Eltern**, sondern ein nachvollziehbarer Plan für dieses Referenzszenario:

- Einfamilienhaus mit Erdgeschoss und Obergeschoss, angenommen jeweils etwa 80 m².
- Ein zentraler Technikplatz im Erdgeschoss, ein zentraler Deckenmontageplatz je Geschoss.
- Ein bereits bezahlter Glasfaseranschluss mit vom Provider gestelltem, Ethernet bereitstellendem ONT.
- **Alle benötigten Cat-6-Leitungen und Patchkabel sind im Referenzszenario bereits vorhanden:** ONT–Gateway, Gateway–Switch sowie Switch–AP je Geschoss. Diese Annahme umfasst ausdrücklich auch Stecker und Anschlussdosen.
- Vorhandene WLAN-Endgeräte und einige vorhandene Ethernet-Endgeräte; keine Neuanschaffung von Computern, Smartphones oder Fernsehern.
- Typische Nutzung: Lernen/Homeoffice, Videokonferenzen, gespeicherte Videos und getrenntes Gäste-/IoT-Netz.

Diese Angaben sind **Planungsannahmen**, keine erhobenen Nutzerdaten. Bei einem realen Haus müssten sie zuerst überprüft und insbesondere Verkabelung, Montage und Internetvertrag gegebenenfalls zusätzlich angeboten werden.

## 2. Topologie und Rollen

```text
Internet / Provider
       │
vorhandenes ONT mit Ethernet
       │ WAN
Ubiquiti Cloud Gateway Ultra (UCG-Ultra)
       │ LAN / VLAN-Verbindung
Ubiquiti UniFi Switch Lite 8 PoE (USW-Lite-8-PoE)
       ├── Ethernet + PoE ── U6+ im Erdgeschoss ── WLAN-Geräte
       ├── Ethernet + PoE ── U6+ im Obergeschoss ── WLAN-Geräte
       └── Ethernet ──────── vorhandene stationäre Geräte
```

- Das **Gateway** übernimmt Routing, Firewall, DHCP und bei IPv4 gegebenenfalls NAT sowie die UniFi-Netzverwaltung. Das UCG-Ultra enthält **keinen WLAN-Access-Point** und ersetzt kein DSL-/Kabelmodem oder optisches ONT. Es hat einen 2,5-GbE-WAN-Port und vier 1-GbE-Ports; die Herstellerangabe für IDS/IPS-Routing liegt bei 1 Gbit/s. [Herstellerdaten UCG-Ultra](https://techspecs.ui.com/unifi/cloud-gateways/ucg-ultra)
- Der **Switch** verbindet die kabelgebundenen Geräte. Er besitzt acht Gigabit-Ports, davon vier PoE+-Ports, und ein gesamtes PoE-Budget von 52 W. Das Netzteil ist laut Hersteller enthalten. [Herstellerdaten USW-Lite-8-PoE](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe)
- Die **beiden U6+** stellen WLAN nach IEEE 802.11ax (**Wi-Fi 6**) in 2,4 und 5 GHz bereit, jeweils mit 2×2 MIMO pro Band, einem Gigabit-Ethernet-Uplink und PoE-Versorgung. Sie verwenden **kein 6-GHz-Band**. Montagehalterungen sind enthalten. [Herstellerdaten U6+](https://techspecs.ui.com/unifi/wifi/u6-plus)

Ich verwende **kabelgebundenen Backhaul** statt WLAN-Repeating: Die Verbindung zwischen den Geschossen beansprucht dann keine zusätzliche Funk-Airtime für das Weiterreichen der Nutzdaten. Mehrere Access Points mit Ethernet-Anbindung benötigen dafür keinen drahtlosen Mesh-Backhaul. [Ubiquiti: Optimierung und Meshing](https://help.ui.com/hc/en-us/articles/221029967-Optimizing-WiFi-Connectivity-and-Reducing-Latency)

## 3. Funkplanung

Die zwei APs werden im Plan frei und zentral an der Decke ihres jeweiligen Geschosses montiert, nicht im Technikschrank. Die endgültigen Positionen hängen von den Wänden und den Messungen vor Ort ab. Die Hersteller-Flächenangabe eines APs ist **keine garantierte Ausleuchtung dieses Hauses**. [Herstellerdaten und Montageoptionen U6+](https://techspecs.ui.com/unifi/wifi/u6-plus)

Vorgesehene Startkonfiguration, noch ohne Funkmessung:

- **2,4 GHz:** 20 MHz Kanalbreite; AP Erdgeschoss auf Kanal 1, AP Obergeschoss auf Kanal 6. Das Band bleibt für größere Reichweite und ältere IoT-Geräte verfügbar.
- **5 GHz:** zunächst 40 MHz Kanalbreite; beispielsweise Kanalgruppe 36/40 im Erdgeschoss und 44/48 im Obergeschoss. Diese Gruppen überlappen sich nicht. Ein späterer Wechsel auf 80 MHz wäre nur nach Prüfung der Nachbarnetze sinnvoll; beide APs dürfen dann nicht irrtümlich als unabhängig betrachtet werden, wenn sie denselben 80-MHz-Block nutzen.
- Länderprofil **Österreich** setzen und nur erlaubte Kanäle/Sendeleistungen verwenden. Gegebenenfalls vorgeschriebene DFS-Prüfungen müssen aktiv bleiben.
- Auf beiden APs dieselben SSIDs, Sicherheitseinstellungen und VLAN-Zuordnungen. Roaming entscheidet grundsätzlich das Endgerät; 802.11k/v und optional 802.11r können helfen, garantieren aber nicht bei jedem Client einen unterbrechungsfreien Wechsel.

Das sind **begründete Planungsentscheidungen**, keine Behauptung, diese Kanäle seien am unbekannten Standort frei. Ubiquiti empfiehlt 20 MHz bei 2,4 GHz und abhängig von Funkdichte 40 beziehungsweise 80 MHz bei 5 GHz; das U6+ unterstützt 802.11k/v/r. [Ubiquiti: Funkoptimierung](https://help.ui.com/hc/en-us/articles/221029967-Optimizing-WiFi-Connectivity-and-Reducing-Latency), [U6+-Funktionen](https://techspecs.ui.com/unifi/wifi/u6-plus)

## 4. Sicherheit und logische Netze

Vorgesehene, **frei gewählte Beispielkonfiguration**:

- `Haus` → VLAN 10, IPv4-Netz `192.168.10.0/24`: persönliche Geräte; bevorzugt WPA3-Personal, soweit alle vorgesehenen Clients damit kompatibel sind.
- `Gast` → VLAN 20, `192.168.20.0/24`: Internetzugang, kein Zugriff auf Haus-, IoT- oder Verwaltungsgeräte; zusätzlich Client-Isolation.
- `IoT` → VLAN 30, `192.168.30.0/24`: getrennte Smart-Home-Geräte, bei Bedarf eigenes 2,4-GHz-WLAN mit WPA2-AES für ältere Clients. Nicht WEP oder TKIP verwenden.

Switch- und AP-Uplinks müssen die benötigten VLANs transportieren; die SSID muss dem passenden VLAN zugeordnet sein. Am Gateway werden DHCP-Bereiche, DNS-Vorgaben und Firewallregeln je Netz eingerichtet. **Eine zweite SSID oder ein VLAN allein ist noch keine vollständige Zugriffssperre:** Die Firewall muss unerwünschten Verkehr zwischen den Netzen tatsächlich unterbinden; benötigte IoT-Freigaben werden einzeln erlaubt. Dasselbe Sicherheitsziel muss auch für gegebenenfalls aktiviertes IPv6 gelten. [Ubiquiti: VLANs und SSID-Zuweisung](https://help.ui.com/hc/en-us/articles/9761080275607), [Gateway-Segmentierung und Firewall](https://techspecs.ui.com/unifi/cloud-gateways/ucg-ultra)

Weiter vorgesehen: lange unterschiedliche WLAN-/Administrationskennwörter, zeitnahe Firmwareupdates, geschützte Verwaltung nur aus dem vertrauenswürdigen Netz, keine unnötige Fernadministration und keine unkontrollierten Portfreigaben. Die unterstützten aktuellen Sicherheitsmodi werden vor Inbetriebnahme in der tatsächlich installierten Firmware geprüft. [U6+-Produktangaben zu WPA2/WPA3](https://geizhals.at/ubiquiti-unifi-6-u6-a2849254.html)

## 5. Konkrete Modelle und belegte Anschaffungskosten

**Rechercheabruf: 19.10.2026.** Verwendet werden ausdrücklich die folgenden **über Geizhals Österreich ausgelesenen Händlerangebote**, nicht die teilweise netto dargestellten Basispreise im Hersteller-Shop. Die Preise sind nach dem Geizhals-Preishinweis inklusive Mehrwertsteuer; beim Kauf gilt der dann angezeigte Händlerpreis. Es wurde nichts bestellt.

1. **1 × Ubiquiti Cloud Gateway Ultra, UCG-Ultra:** **114,00 €**, im gelesenen Angebot von **electronic4you**, mit ausgewiesenem Gratisversand innerhalb Österreichs. [Preisquelle mit Händlerangebot](https://geizhals.at/ubiquiti-cloud-gateway-ultra-ucg-ultra-a3145685.html)
2. **1 × Ubiquiti UniFi Switch Lite 8 PoE, USW-Lite-8-PoE:** **124,00 €**, im gelesenen Angebot von **electronic4you**, ebenfalls mit ausgewiesenem Gratisversand. Das günstigere Vorbestellangebot wurde bewusst nicht als Grundlage gewählt. [Preisquelle mit Händlerangebot](https://geizhals.at/ubiquiti-unifiswitch-lite-8-desktop-gigabit-managed-switch-usw-lite-8-poe-a2378317.html)
3. **2 × Ubiquiti UniFi 6+, U6+:** **je 111,90 €**, im gelesenen Angebot von **1ashop.at**, mit ausgewiesenem Gratisversand innerhalb Österreichs. Die APs werden über den Switch gespeist; separate PoE-Injektoren werden daher nicht benötigt. [Preisquelle mit Händlerangebot](https://geizhals.at/ubiquiti-unifi-6-u6-a2849254.html)

**Im Referenzszenario keine zusätzliche Anschaffung:** Provider-ONT, alle genannten Kabel/Anschlussdosen und die Endgeräte sind bereits vorhanden. Für diese Dinge werden **keine fiktiven Neupreise** angegeben. Gateway- und Switch-Netzteile sowie AP-Halterungen sind laut Hersteller enthalten. [UCG-Ultra-Lieferumfang/Stromversorgung](https://techspecs.ui.com/unifi/cloud-gateways/ucg-ultra), [Switch-Netzteil](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe), [U6+-Halterungen](https://techspecs.ui.com/unifi/wifi/u6-plus)

### Nachgerechnete Summe

Die Rechnung wurde mit [`kosten.py`](kosten.py) und `decimal.Decimal` tatsächlich ausgeführt:

```text
1 × 114,00 € = 114,00 €
1 × 124,00 € = 124,00 €
2 × 111,90 € = 223,80 €
Warenwert inklusive MwSt. = 461,80 €
Versand gemäß ausgewählten Angeboten = 0,00 €
Geplante Anschaffung insgesamt = 461,80 €
```

**461,80 € sind die bedingte Hardware-Anschaffungssumme dieses Referenzplans**, keine Zusage eines unveränderlichen Komplettpreises für ein reales Haus. Sie gilt, wenn Preise, Mengenverfügbarkeit und Versandbedingungen der ausgewählten Angebote beim Kauf unverändert sind. Nicht enthalten sind Internet-Grundgebühr, Strom, externe Installationsarbeit oder erst nach einer Standortprüfung erforderliche weitere Geräte/Leitungen. Dafür ist kein belastbares Angebot vorhanden. Preisbelege sind zusätzlich in [`preisnachweise.md`](preisnachweise.md) zusammengefasst.

### PoE-Kompatibilität und Leistungsbudget

Ein U6+ benötigt laut Hersteller maximal **9 W**. Zwei APs benötigen damit rechnerisch höchstens **18 W**; gegenüber dem Switch-PoE-Budget von **52 W** verbleiben rechnerisch **34 W** vor einer detaillierten Berücksichtigung der Leitungsverluste. Es stehen vier PoE+-Ports zur Verfügung, benötigt werden zwei. Das ist eine **Datenblatt-/Planungsrechnung, keine gemessene Leistungsaufnahme**; das Budget wird bei der Installation nochmals geprüft. [U6+-Leistungsbedarf](https://techspecs.ui.com/unifi/wifi/u6-plus), [Switch-PoE-Budget](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe)

## 6. Überprüfung nach einem tatsächlichen Aufbau

Geplant wären ein Rundgang mit Signal-/Kanalprüfung in allen genutzten Räumen, ein lokaler Durchsatztest gegen einen verkabelten Rechner, ein gesonderter Internettest, ein Roamingtest und negative Zugriffstests aus Gast- und IoT-Netz. Erst diese Tests zeigen, ob Positionen und Kanalwahl passen und die Isolation tatsächlich wirkt. **Diese Messungen wurden nicht durchgeführt; es werden keine RSSI-, Durchsatz- oder Latenzwerte erfunden.** [Ubiquiti: Site Survey und Fehlerbehebung](https://help.ui.com/hc/en-us/articles/221029967-Optimizing-WiFi-Connectivity-and-Reducing-Latency)

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Entwirf für Ü 2.7 ein ausdrücklich hypothetisches WLAN-Referenzhaus, recherchiere konkrete Produktmodelle und belegte Preise, berechne die Kosten mit Python und erfinde weder private Hausdetails noch Messdaten.“
