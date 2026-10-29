# Ü 7.5 – CSMA: theoretische Fragen

## 1. Was ist CSMA?

**CSMA (Carrier Sense Multiple Access)** ist ein Verfahren für den verteilten Zugriff mehrerer Stationen auf ein gemeinsames Übertragungsmedium:

- **Carrier Sense:** Eine sendewillige Station prüft zunächst, ob das Medium belegt ist – sie „hört“ den Kanal ab.
- **Multiple Access:** Mehrere Stationen teilen sich dasselbe Medium; es gibt nicht für jede Station einen dauerhaft exklusiven Übertragungskanal.
- **Kanal frei:** Die Station darf abhängig von der CSMA-Variante senden. Bei **1-persistentem CSMA** sendet sie, sobald sie den Kanal als frei erkennt.
- **Kanal belegt:** Sie stellt ihre Übertragung zurück. Bei 1-persistentem CSMA hört sie weiter und startet, sobald der Kanal frei wird. Bei **nichtpersistentem CSMA** wartet sie zunächst eine zufällige Zeit und prüft erneut. Bei **p-persistentem CSMA** auf einem zeitgeschlitzten Kanal sendet sie bei freiem Kanal nur mit Wahrscheinlichkeit p und verschiebt sonst auf einen späteren Slot.

CSMA ist somit das Grundprinzip „erst hören, dann senden“; die genaue Warte- und Zugriffsregel hängt von der Variante ab.

### Warum kann es trotzdem Kollisionen geben?

Die Ausbreitung eines Signals benötigt Zeit. Station A kann bereits senden, während Station B das Signal aufgrund der **Signallaufzeit** noch nicht empfangen hat. B hält den Kanal ebenfalls für frei und beginnt zu senden. Die Signale überlagern sich; der Empfänger kann die betroffenen Frames nicht korrekt empfangen. Auch mehrere Stationen, die auf das Ende derselben Übertragung warten, können nahezu gleichzeitig starten.

Carrier Sense ist also eine **lokale Beobachtung**, keine atomare Reservierung des gesamten Mediums. Bei Funk kommt zusätzlich das **Hidden-Station-Problem** hinzu: Zwei Sender können einander nicht hören, obwohl ihre Signale beim gemeinsamen Empfänger kollidieren.

## 2. Unterschied zwischen CSMA und CSMA/CD

**CSMA allein** legt fest, dass vor dem Zugriff die Kanalbelegung geprüft wird. Eine Erkennung von Kollisionen während der eigenen Übertragung und deren konkrete Behandlung sind damit noch nicht festgelegt.

**CSMA/CD (Carrier Sense Multiple Access with Collision Detection)** ergänzt dies um die Erkennung von Kollisionen **während des Sendens**. Im klassischen Halbduplex-Ethernet läuft die Reaktion so ab:

1. Die Station prüft den Kanal und beginnt bei freiem Medium mit der Übertragung, unter Beachtung der vorgeschriebenen Rahmenabstände.
2. Während des Sendens überwacht sie das Medium auf eine Kollision.
3. Bei erkannter Kollision beendet sie die normale Frameübertragung und sendet noch ein **Jam-Signal**, damit die Kollision zuverlässig bemerkbar wird. Der betroffene Frame ist ungültig.
4. Sie wartet eine zufällig gewählte Zeit nach dem **trunkierten binären exponentiellen Backoff**. Bei wiederholten Kollisionen wächst das Auswahlfenster zunächst an. Die unabhängige Zufallswahl soll verhindern, dass dieselben Stationen immer wieder gleichzeitig starten.
5. Danach versucht sie unter erneuter Beachtung des Kanalzustands erneut zu senden. Nach Erreichen der begrenzten Zahl erfolgloser Versuche wird der Frame verworfen und ein Sendefehler gemeldet; Wiederholungen höherer Schichten sind davon getrennt.

**CD vermeidet Kollisionen nicht vollständig**, sondern erkennt sie und regelt die Wiederholung. Im klassischen Ethernet hängt die vorgeschriebene Mindestframelänge mit der Notwendigkeit zusammen, dass eine mögliche Kollision noch während des Sendens erkannt werden kann.

## 3. Wo werden CSMA/CD und CSMA/CA eingesetzt?

| Verfahren | Typischer Einsatz | Prinzip |
|---|---|---|
| **CSMA/CD** | Klassisches **Halbduplex-Ethernet**, etwa gemeinsames Koaxialkabel oder Ethernet-Hub; auch ein tatsächlich im Halbduplexmodus betriebener Ethernet-Link | Medium vorab prüfen, Kollision während des Sendens erkennen, Jam und zufälliger Backoff, erneut senden |
| **CSMA/CA** | **IEEE-802.11-WLAN** beim konkurrenzbasierten Kanalzugriff, etwa DCF beziehungsweise EDCA | Kollisionswahrscheinlichkeit vor dem Senden durch Kanalprüfung, Warteintervalle und zufälligen Backoff verringern |
| **Keines der beiden erforderlich** | Heutige korrekt konfigurierte **Vollduplex-Ethernet-Punkt-zu-Punkt-Verbindungen** zwischen Host und Switch bzw. zwei Switches | Gleichzeitiges Senden und Empfangen ohne geteilte Halbduplex-Kollisionsdomäne; CSMA/CD ist deaktiviert |

Ein Switch allein ist nicht die Definition von Vollduplex: Entscheidend ist der tatsächlich konfigurierte beziehungsweise ausgehandelte Betriebsmodus des jeweiligen Links. Überlastung kann auch bei Vollduplex zu Warteschlangen und Paketverlust führen; das sind **keine Ethernet-Kollisionen**.

### Wie funktioniert CSMA/CA im WLAN?

**CA bedeutet Collision Avoidance**, also Verringerung des Kollisionsrisikos, nicht Kollisionsfreiheit. Eine Funkstation kann eine Kollision während ihrer eigenen Übertragung nicht zuverlässig wie bei klassischem Ethernet erkennen: Ihr eigenes Sendesignal ist am eigenen Empfänger sehr stark, und andere Sender sind möglicherweise verborgen.

Beim grundlegenden konkurrenzbasierten Zugriff prüft die Station das Medium, wartet den vorgeschriebenen freien Zwischenraum ab und verwendet die Backoff-Regeln mit einem zufälligen Slotzähler. Der Zähler läuft nur bei freiem Kanal weiter; wird das Medium belegt, wird er angehalten und nach dem erforderlichen freien Intervall fortgesetzt. Eine erfolgreich empfangene individuelle Datenübertragung wird typischerweise durch ein **MAC-ACK** bestätigt. Bleibt die Bestätigung aus, kann eine Kollision, aber auch eine Funkstörung oder ein anderer Verlust vorliegen; die Station wiederholt nach den Wiederholungs- und Backoff-Regeln. Das ist keine sichere unmittelbare Kollisionserkennung.

Optional kann **RTS/CTS** den Kanal vor einer Datenübertragung zeitlich reservieren und insbesondere Hidden-Station-Konflikte verringern. Andere Stationen berücksichtigen die angekündigte Dauer als virtuelle Kanalbelegung (NAV). Auch RTS/CTS beseitigt nicht jede Kollision und verursacht zusätzlichen Overhead. Neuere WLAN-Verfahren können zusätzlich koordinierte Übertragungen nutzen; nicht jeder einzelne Funkzugriff ist deshalb ein unabhängiger CSMA-Wettbewerb.

**Merksatz:** CSMA hört vor dem Senden zu; CSMA/CD erkennt und behandelt Kollisionen während des Sendens; CSMA/CA senkt vorab deren Wahrscheinlichkeit und nutzt im WLAN unter anderem Bestätigungen zur Erfolgskontrolle.

## Quellen

- Cisco: [Troubleshooting Ethernet](https://cisco.com/en/US/docs/internetworking/troubleshooting/guide/tr1904.html), Abschnitte zu Halb-/Vollduplex und Backoff.
- Cisco: [WLAN DSSS and CSMA/CA](https://www.cisco.com/E-Learning/bulk/guest/celc/fwl/ch3/3_6_2/content.html), physische/virtuelle Kanalprüfung und RTS/CTS.

## KI-Kennzeichnung

Tool: Hermes Agent; Modell: OpenAI `gpt-6.1-sol`; Provider/Zugang laut Auftragskontext: `ChatGPT or Codex Subscription`; Datum: 2026-10-29. Anfrage: „Erstelle deutsche fachlich vollständige Antworten für RN Blatt07 Aufgaben 7.1 und 7.5 in den jeweiligen antwort.md sowie konzeptionelle Antworten zu 7.3 und 7.4 mit Platz für tatsächliche Messwerte; keine Messungen erfinden, keine Commits/Pushes.“
