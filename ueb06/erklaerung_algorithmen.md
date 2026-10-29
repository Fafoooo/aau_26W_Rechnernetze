# Zeilenweise Erklärung der Algorithmen zu 6.4–6.6

Diese Erklärung bezieht sich auf die drei Lösungsprogramme und den Testtreiber. Jede nichtleere Quellzeile wird einzeln mit ihrer tatsächlichen Zeilennummer erklärt, einschließlich Kommentaren, Ausgabeaufbereitung und Tests. Leerzeilen strukturieren nur den Quelltext. Sämtliche Programme benötigen ausschließlich die Python-Standardbibliothek. Ausführung ohne `-O`, damit die `assert`-Prüfungen aktiv bleiben.

## Ablauf und Reproduktion

Ab der Repository-Wurzel:

```sh
python3 ueb06/ue6.4/subnetting.py --write
python3 ueb06/ue6.5/dijkstra.py --write
python3 ueb06/ue6.6/distance_vector.py --write
```

Jeder Aufruf berechnet das Ergebnis, führt seine eingebauten Tests aus und schreibt erst danach `antwort.md` im jeweiligen Aufgabenordner. Ohne `--write` wird dieselbe Antwort nur auf Standardausgabe ausgegeben. Eine fehlgeschlagene Assertion beendet das Programm, statt eine ungeprüfte Antwort zu erzeugen. Es erfolgt kein Netzzugriff und keine Änderung der Originalangabe.

## 6.4 – `ue6.4/subnetting.py`

### Modell

Ein IPv4-Subnetz mit Präfix p enthält 2^(32−p) Adressen. Unter der hier gewählten klassischen Netz-/Broadcastkonvention sind davon zwei nicht als Hostadressen nutzbar. Die Suche beginnt bei /30 und nimmt den ersten ausreichend großen Block. Das ist die längste zulässige Präfixlänge und damit die kleinste passende Blockgröße. Die /31-Sonderregel für echte P2P-Verbindungen wird bewusst nicht verwendet. Zuerst werden große Blöcke reserviert; der ganzzahlige Cursor wird vor jeder Vergabe auf eine Blockgrenze aufgerundet.

### Jede nichtleere Zeile

- **Z. 1:** Kennzeichnet Hermes Agent und das verwendete Modell als KI-Unterstützung.
- **Z. 2:** Dokumentiert Anbieterbezeichnung und Datum der Bearbeitung.
- **Z. 3:** Beginnt die tatsächliche Nutzeranfrage mit den drei Aufgabennummern.
- **Z. 4:** Vervollständigt die Anfrage mit Python, Tests, deutschen Antworten und Schreibumfang.
- **Z. 5:** Beschreibt im Modul-Docstring Zweck und Ausgabe des Programms.
- **Z. 6:** Importiert `IPv4Network`, das Präfixe, Masken und IPv4-Adressgrenzen berechnet.
- **Z. 7:** Importiert `Path` für den zum Skript relativen Antwortpfad.
- **Z. 8:** Importiert den Parser für den optionalen Kommandozeilenschalter `--write`.
- **Z. 10:** Definiert den frei gewählten privaten Gesamtpool als IPv4-Netzobjekt.
- **Z. 11:** Speichert alle vier Bereiche mit ihren unveränderten Hostanforderungen.
- **Z. 12:** Speichert die KI-Kennzeichnung samt tatsächlicher Anfrage für das Ende jeder erzeugten Antwort.
- **Z. 14:** Definiert die Funktion zur Wahl eines Präfixes aus der geforderten Hostzahl.
- **Z. 15:** Prüft Präfixe ab /30 rückwärts bis /0; kleinere Präfixzahlen bedeuten größere Blöcke.
- **Z. 16:** Berechnet die klassische Hostkapazität und vergleicht sie mit dem Bedarf.
- **Z. 17:** Liefert das erste passende, also platzsparendste Präfix zurück.
- **Z. 18:** Meldet explizit, wenn auch der größte IPv4-Block die Anforderung nicht abdecken kann.
- **Z. 20:** Definiert die Funktion, die den gesamten VLSM-Plan erzeugt.
- **Z. 21:** Wandelt die erste Pooladresse in eine Ganzzahl um, damit Blockgrößen addiert werden können.
- **Z. 22:** Beginnt eine leere Ergebnisliste für die vier zugewiesenen Netze.
- **Z. 23:** Sortiert den Bedarf absteigend; `-item[1]` macht große Anforderungen zuerst sichtbar.
- **Z. 24:** Bestimmt das kleinste ausreichende klassische Subnetz für den aktuellen Bereich.
- **Z. 25:** Berechnet die gesamte Blockgröße einschließlich Netz- und Broadcastadresse.
- **Z. 26:** Rundet den Cursor auf das nächste Vielfache der Blockgröße auf; `//` ist ganzzahlige Division.
- **Z. 27:** Erstellt aus ausgerichteter Startadresse und Präfix das konkrete IPv4-Netzobjekt.
- **Z. 28:** Prüft, ob der reservierte Block vollständig im Gesamtpool liegt.
- **Z. 29:** Bricht bei erschöpftem Pool mit verständlichem Fehler ab, statt externe Adressen zu vergeben.
- **Z. 30:** Speichert Bereichsname, Bedarf und berechnetes Netz gemeinsam.
- **Z. 31:** Verschiebt den Cursor direkt hinter den gerade reservierten Block.
- **Z. 32:** Liefert den vollständigen Plan zurück.
- **Z. 34:** Definiert die eingebauten Tests für den berechneten Plan.
- **Z. 35:** Hält die vier separat festgelegten Sollnetze in der erwarteten Vergabereihenfolge fest.
- **Z. 36:** Vergleicht sämtliche tatsächlich berechneten Netzbezeichnungen exakt mit diesen Sollwerten.
- **Z. 37:** Prüft jeden Planblock einzeln; der Index ermöglicht den paarweisen Überschneidungstest.
- **Z. 38:** Verifiziert erneut die vollständige Zugehörigkeit zum erlaubten Gesamtpool.
- **Z. 39:** Verlangt mindestens so viele nutzbare Hostadressen wie Geräte.
- **Z. 40:** Prüft, dass die halbierte Blockgröße zu klein wäre; damit ist die Präfixwahl minimal.
- **Z. 41:** Zählt die von `ipaddress` tatsächlich aufgezählten Hostadressen als unabhängige Kapazitätsprobe.
- **Z. 42:** Prüft jedes Netz gegen alle späteren Netze; kein Paar darf sich überschneiden.
- **Z. 43:** Testet die /24-Grenze: 254 Hosts passen, 255 benötigen /23.
- **Z. 44:** Testet die /26-Grenze: 62 Hosts passen, 63 benötigen /25.
- **Z. 45:** Testet die /27-Grenze: 30 Hosts passen, 31 benötigen /26.
- **Z. 46:** Testet die /30-Grenze: zwei Hosts passen, drei benötigen /29.
- **Z. 48:** Definiert die deutschsprachige Markdown-Ausgabe aus dem geprüften Plan.
- **Z. 49:** Erstellt Titel, Annahmen, Hostformel und Tabellenkopf; die langen Texte sind Ausgabe, keine verdeckten Berechnungsschritte.
- **Z. 50:** Durchläuft die berechneten Netze in ihrer Vergabereihenfolge.
- **Z. 51:** Schreibt je Bereich Netz, Maske, Netz+1 als ersten Host, Broadcast−1 als letzten Host, Broadcast, Kapazität und Reserve.
- **Z. 52:** Beginnt den Abschnitt zur Begründung der Präfixwahl.
- **Z. 53:** Durchläuft die Bereiche für die jeweilige Kapazitätsbegründung erneut.
- **Z. 54:** Bestimmt die Anzahl der Hostbits durch Abzug der Präfixlänge von 32.
- **Z. 55:** Gibt ausreichende Kapazität und zu kleine halbierte Kapazität als konkrete Rechenprobe aus.
- **Z. 56:** Summiert die reservierten Adressen einschließlich Netz-/Broadcastadressen; `_` ignoriert hier Name und Bedarf.
- **Z. 57:** Ergänzt Restkapazität, Vergleich mit den Lab-/24-LANs, Transit-/30, /31-Abgrenzung und Testaufruf.
- **Z. 58:** Verbindet die Ausgabezeilen mit Zeilenumbrüchen und hängt die KI-Kennzeichnung an.
- **Z. 60:** Führt den folgenden Hauptablauf nur bei direktem Programmstart aus, nicht beim Import.
- **Z. 61:** Berechnet den VLSM-Plan.
- **Z. 62:** Führt alle Tests aus, bevor irgendeine Antwort geschrieben wird.
- **Z. 63:** Erstellt den Kommandozeilenparser mit dem Modul-Docstring als Hilfetext.
- **Z. 64:** Registriert `--write` als booleschen Schalter; ohne ihn bleibt die Dateierzeugung aus.
- **Z. 65:** Liest die Argumente und verzweigt bei ausdrücklich gewünschter Dateierzeugung.
- **Z. 66:** Wählt `antwort.md` direkt neben dem ausgeführten Skript, unabhängig vom aktuellen Arbeitsverzeichnis.
- **Z. 67:** Schreibt die berechnete Markdown-Antwort UTF-8-kodiert mit abschließendem Zeilenumbruch.
- **Z. 68:** Bestätigt bestandene Prüfungen und nennt den tatsächlich beschriebenen Pfad.
- **Z. 69:** Beginnt den Alternativzweig ohne Dateierzeugung.
- **Z. 70:** Gibt die geprüfte Antwort ausschließlich auf Standardausgabe aus.

## 6.5 – `ue6.5/dijkstra.py`

### Modell und unabhängige Probe

Dijkstra verwaltet vorläufige Distanzen und je einen Vorgänger. Der nicht feste Knoten mit kleinster Distanz wird fest; danach werden seine Nachbarn geprüft. Eine strikt kleinere Kandidatendistanz ersetzt den bisherigen Wert. Ein Gleichstand ersetzt den Vorgänger nicht. Damit bleibt für F der Weg über B im Vorgängerbaum, obwohl die vollständige Pfadprüfung zusätzlich den gleich teuren Weg über C,G findet. Jeder Tabellenzustand wird kopiert, damit spätere Änderungen frühere Schritte nicht überschreiben.

Die Kontrollfunktion enumeriert unabhängig alle einfachen Wege rekursiv und vergleicht deren Minimum für jedes Start-Ziel-Paar mit Dijkstra. Sie verwendet weder dessen Distanzwerte noch dessen Vorgänger zur Erzeugung ihrer Kandidaten. Alle Kanten dieses Blatts sind positiv; ein kürzester Weg braucht daher keinen Zyklus. Die vollständige Pfadsuche ist für diesen kleinen Graphen geeignet, aber keine effiziente Alternative für große Netze.

### Jede nichtleere Zeile

- **Z. 1:** Kennzeichnet KI-System und verwendetes Modell.
- **Z. 2:** Nennt die Anbieterbezeichnung und das Bearbeitungsdatum.
- **Z. 3:** Beginnt die tatsächliche Anfrage zur Bearbeitung von 6.4–6.6.
- **Z. 4:** Vervollständigt die Anfrage einschließlich Tests, Antwortsprache und erlaubter Pfade.
- **Z. 5:** Beschreibt Dijkstra, Schrittmitschnitt und unabhängige Pfadenumeration als Modulzweck.
- **Z. 6:** Importiert die Unendlichkeitskonstante für zunächst unerreichbare Ziele.
- **Z. 7:** Importiert die Pfadklasse für die optionale Antwortdatei.
- **Z. 8:** Importiert den Kommandozeilenparser für `--write`.
- **Z. 10:** Übernimmt sämtliche zehn Kanten und Kosten aus Abbildung 1.
- **Z. 11:** Fixiert die alphabetische Reihenfolge aller sieben Knoten für Tabellen und Tests.
- **Z. 12:** Speichert die vollständige KI-Kennzeichnung für den Antwortabschluss.
- **Z. 14:** Definiert die Umwandlung der Kantenliste in eine Nachbarschaftsabbildung.
- **Z. 15:** Legt für jeden Knoten zunächst ein leeres Nachbarwörterbuch an.
- **Z. 16:** Entpackt jede Kante in zwei Endpunkte und deren Kosten.
- **Z. 17:** Erkennt negative Kosten, für die der verwendete Dijkstra-Algorithmus nicht geeignet ist.
- **Z. 18:** Weist negative Kanten ausdrücklich zurück.
- **Z. 19:** Speichert die Kante in Richtung links nach rechts.
- **Z. 20:** Speichert dieselben Kosten in Gegenrichtung und modelliert so einen ungerichteten Graphen.
- **Z. 21:** Liefert die vollständige Adjazenzabbildung zurück.
- **Z. 23:** Definiert Dijkstra mit beliebigem Startknoten innerhalb des übergebenen Graphen.
- **Z. 24:** Initialisiert jede vorläufige Distanz mit Unendlich.
- **Z. 25:** Initialisiert jeden Vorgänger mit `None`, weil noch kein Weg bekannt ist.
- **Z. 26:** Setzt die Distanz des Startknotens zu sich selbst auf null.
- **Z. 27:** Beginnt die Listen für feste Knoten und unveränderliche Schrittabzüge.
- **Z. 28:** Wiederholt die Auswahl, solange noch nicht jeder Knoten fest ist.
- **Z. 29:** Wählt unter nicht festen Knoten das Minimum nach Distanz und danach alphabetischem Knotennamen.
- **Z. 30:** Erkennt, dass selbst der kleinste verbleibende Kandidat unerreichbar ist.
- **Z. 31:** Beendet die Schleife, weil dann auch alle anderen verbleibenden Knoten unerreichbar sind.
- **Z. 32:** Fügt den ausgewählten Knoten der festen Menge in Auswahlreihenfolge hinzu.
- **Z. 33:** Beginnt eine Liste der Begründungen für genau diesen Auswahlschritt.
- **Z. 34:** Durchläuft alle Nachbarn des ausgewählten Knotens in reproduzierbarer alphabetischer Reihenfolge.
- **Z. 35:** Erkennt einen Nachbarn, dessen Distanz bereits endgültig feststeht.
- **Z. 36:** Protokolliert, weshalb dessen Kante nicht mehr relaxiert wird.
- **Z. 37:** Springt zur nächsten Nachbarkante.
- **Z. 38:** Berechnet die Kandidatendistanz als Wegkosten zum aktuellen Knoten plus Linkkosten.
- **Z. 39:** Merkt den bisherigen Nachbarwert für Vergleich und Erläuterung.
- **Z. 40:** Prüft auf echte Verbesserung; gleich teure Wege ändern den Vorgänger nicht.
- **Z. 41:** Übernimmt kleinere Distanz und aktuellen Knoten als neuen Vorgänger gleichzeitig.
- **Z. 42:** Protokolliert Addition, Vergleich und Aktualisierung für die spätere Schrittbegründung.
- **Z. 43:** Beginnt den Zweig ohne Verbesserung.
- **Z. 44:** Protokolliert den nicht besseren Kandidaten, einschließlich möglicher Gleichstände.
- **Z. 45:** Kopiert feste Reihenfolge, Distanzen und Vorgänger in die Spur; spätere Updates verändern diese Zeile nicht.
- **Z. 46:** Gibt Enddistanzen, Vorgängerbaum und vollständige Schrittspur zurück.
- **Z. 48:** Definiert die unabhängige rekursive Suche aller einfachen Wege zum Ziel.
- **Z. 49:** Prüft den Rekursionsbasisfall: aktueller Knoten ist das Ziel.
- **Z. 50:** Liefert den Nullkosten-Restweg, der nur aus diesem Zielknoten besteht.
- **Z. 51:** Beginnt eine Liste aller von hier erreichbaren einfachen Zielpfade.
- **Z. 52:** Betrachtet jede mögliche erste Nachbarkante.
- **Z. 53:** Verhindert Wiederbesuche und unmittelbare Selbstbesuche, damit kein Zyklus entsteht.
- **Z. 54:** Enumeriert alle Restpfade; der aktuelle Knoten wird der besuchten Folge hinzugefügt.
- **Z. 55:** Addiert die erste Kante und stellt den aktuellen Knoten dem Restpfad voran.
- **Z. 56:** Liefert alle gefundenen Kosten-Pfad-Paare zurück, nicht nur das billigste.
- **Z. 58:** Definiert die Rückverfolgung eines einzelnen Pfades im Dijkstra-Vorgängerbaum.
- **Z. 59:** Beginnt die Rückverfolgung beim Zielknoten.
- **Z. 60:** Wiederholt die Rückverfolgung, solange vor dem bisherigen ersten Knoten noch ein Vorgänger existiert.
- **Z. 61:** Fügt diesen Vorgänger vorne ein und nähert sich dadurch dem Startknoten.
- **Z. 62:** Gibt den fertig rekonstruierten Weg als Tupel zurück.
- **Z. 64:** Definiert die Testfunktion für Ergebnisse, Spur und Randfälle.
- **Z. 65:** Prüft den vollständigen erwarteten Distanzvektor in der Reihenfolge A bis G.
- **Z. 66:** Prüft die vollständige Reihenfolge der endgültigen Knotenauswahl.
- **Z. 67:** Prüft, dass bei F der zuerst gefundene Vorgänger B erhalten bleibt.
- **Z. 68:** Prüft unabhängig, dass genau die zwei angegebenen einfachen Wege von A nach F Kosten 6 haben.
- **Z. 69:** Wiederholt die Prüfung für jeden der sieben möglichen Startknoten.
- **Z. 70:** Führt Dijkstra für den jeweiligen Start erneut aus; die dafür nicht benötigte Spur wird ignoriert.
- **Z. 71:** Prüft für diesen Start jeden möglichen Zielknoten.
- **Z. 72:** Enumeriert unabhängig alle einfachen Pfade dieses Start-Ziel-Paares.
- **Z. 73:** Vergleicht Dijkstras Distanz mit dem Minimum der unabhängig berechneten Pfadkosten.
- **Z. 74:** Rekonstruiert den von Dijkstra tatsächlich gewählten Vorgängerpfad.
- **Z. 75:** Kontrolliert beide Endpunkte des rekonstruierten Pfades.
- **Z. 76:** Summiert dessen echte Kantenkosten und vergleicht sie mit der gemeldeten kürzesten Distanz.
- **Z. 77:** Legt einen separaten Graphen mit zwei isolierten Knoten an.
- **Z. 78:** Verifiziert, dass das unerreichbare Ziel bei Unendlich bleibt.
- **Z. 79:** Beginnt den Test auf erwartete Fehlerbehandlung.
- **Z. 80:** Übergibt absichtlich eine negative Kante an den Graphenaufbau.
- **Z. 81:** Fängt ausschließlich den für diesen Fehler vorgesehenen `ValueError` ab.
- **Z. 82:** Akzeptiert diesen erwarteten Fehler als bestandenen Test.
- **Z. 83:** Behandelt den Fall, dass entgegen der Erwartung kein Fehler aufgetreten ist.
- **Z. 84:** Lässt den Test dann mit einer aussagekräftigen Assertion scheitern.
- **Z. 86:** Definiert die einheitliche Textdarstellung einer Distanz.
- **Z. 87:** Formatiert Unendlich als ∞ und endliche Werte als Zeichenketten.
- **Z. 89:** Definiert die vollständige deutsche Markdown-Antwort.
- **Z. 90:** Baut Eingabeauflistung, Dijkstra-Regeln und Tabellenkopf mit allen Distanz-/Vorgängerspalten auf.
- **Z. 91:** Schreibt den Zustand vor der ersten Auswahl: Startdistanz null, übrige Werte unendlich.
- **Z. 92:** Nummeriert die gespeicherten Auswahlzustände beginnend bei eins.
- **Z. 93:** Formatiert pro Zustand feste Knoten, alle Distanzen und alle Vorgänger; `None` erscheint als Gedankenstrich.
- **Z. 94:** Beginnt den Abschnitt zur Begründung sämtlicher Schritte.
- **Z. 95:** Durchläuft die gespeicherten Zustände erneut und entnimmt deren Relaxationsprotokolle.
- **Z. 96:** Schreibt Knotenauswahl und zugehörige Distanz als Schrittüberschrift.
- **Z. 97:** Begründet die erste Auswahl mit dem Startknoten und jede spätere mit dem kleinsten nicht festen Distanzwert.
- **Z. 98:** Übernimmt jede einzelne gespeicherte Kantenbegründung als Aufzählungspunkt.
- **Z. 99:** Trennt aufeinanderfolgende Schritte durch eine Leerzeile in der Ausgabe.
- **Z. 100:** Beginnt die Tabelle aller kürzesten Pfade samt Kosten und Vorgängerbaumpfad.
- **Z. 101:** Erzeugt für jeden Zielknoten eine vollständige Ergebniszeile.
- **Z. 102:** Filtert alle unabhängig enumerierten Wege auf genau die berechnete Minimaldistanz.
- **Z. 103:** Gibt sämtliche Minimalwege sowie den einzelnen im Vorgängerbaum gespeicherten Weg aus.
- **Z. 104:** Erläutert die Gleichstände bei F und E und dokumentiert die tatsächlich ausgeführten Tests.
- **Z. 105:** Verbindet alle Antwortteile und hängt die KI-Kennzeichnung an.
- **Z. 107:** Startet den Hauptablauf ausschließlich bei direktem Programmaufruf.
- **Z. 108:** Erstellt den ungerichteten Graphen aus der überprüften Kantenliste.
- **Z. 109:** Führt die verlangte Dijkstra-Berechnung ab A aus.
- **Z. 110:** Führt alle Ergebnis-, Pfad-, Reihenfolge- und Randfalltests vor der Ausgabe aus.
- **Z. 111:** Erstellt den Kommandozeilenparser mit dem Modulzweck als Beschreibung.
- **Z. 112:** Registriert den optionalen Schalter zur Dateierzeugung.
- **Z. 113:** Verzweigt bei gesetztem `--write` in die Dateiausgabe.
- **Z. 114:** Bestimmt den Antwortpfad direkt neben diesem Skript.
- **Z. 115:** Erzeugt die UTF-8-Antwortdatei aus den getesteten Resultaten.
- **Z. 116:** Meldet bestandene Tests und den beschriebenen Dateipfad.
- **Z. 117:** Beginnt den Zweig ohne Dateierzeugung.
- **Z. 118:** Gibt dieselbe vollständige Antwort auf Standardausgabe aus.

## 6.6 – `ue6.6/distance_vector.py`

### Modell, Nachrichtenreihenfolge und Konvergenz

Jeder Router besitzt einen eigenen Vektor und eine Tabelle der zuletzt empfangenen Kandidaten pro Nachbar. Der erste Tabellenindex ist der Nachbar, der zweite das Ziel. Ein empfangener Nachbarvektor ersetzt genau eine komplette Spalte: Linkkosten plus gemeldete Zielkosten. Erst danach berechnet der Empfänger seine Zielminima neu. Die Eigenkosten bleiben immer null. In der Initialtabelle sind nur die direkten Nachbarziele bekannt; das ist nicht dasselbe wie der bereits verteilte Anfangsvektor eines Nachbarn.

Asynchron werden gerichtete Kanten nach Kosten, Sender und Empfänger sortiert. Damit beginnt die globale Zustellung auf A–E mit Kosten 2; Bs Empfangsfolge ist trotzdem E,C,A mit Kosten 3,7,8. Eine Nachricht verwendet den momentan aktuellen Sendervektor. Weil A→E vor E→B verarbeitet wird, kennt E dann bereits einen Weg nach D mit Kosten 14, den B zunächst als Kandidaten 17 empfängt. Solche Zwischenwerte sind kein Fehler, sondern ein Effekt der gewählten Reihenfolge.

Synchron wird dagegen für eine gesamte Runde ausschließlich die alte Vektormatrix gelesen. Erst nach vollständiger Berechnung der neuen Matrix wird diese übernommen. Der Unterschied steht im Quelltext zwischen dem sofortigen Austausch in Z. 45 und dem späteren Austausch in Z. 63. Beide Verfahren werden bis zu einer netzweit unveränderten vollständigen Runde beziehungsweise einem vollständigen Durchlauf betrieben. Tabellenänderungen ohne Änderung des jeweiligen Minimums werden trotzdem dokumentiert.

Die unabhängige Kontrolle enumeriert alle einfachen Pfade und wird ausschließlich von den Tests aufgerufen. Die eigentliche DV-Berechnung greift nie auf eine globale Kürzeste-Wege-Funktion zu. In beiden simulierten Verfahren braucht ein Router nur seine direkten Linkkosten und empfangene Nachbarvektoren; die gemeinsame Python-Datenstruktur simuliert lediglich das Netz.

### Jede nichtleere Zeile

- **Z. 1:** Kennzeichnet KI-System und verwendetes Modell.
- **Z. 2:** Dokumentiert Anbieterbezeichnung und Bearbeitungsdatum.
- **Z. 3:** Beginnt die tatsächliche Anfrage für die drei Aufgaben.
- **Z. 4:** Ergänzt Implementierungs-, Test-, Sprach- und Umfangsvorgaben.
- **Z. 5:** Beschreibt asynchrone und synchrone DV-Simulation als Modulzweck.
- **Z. 6:** Importiert Unendlich für noch nicht bekannte Ziele.
- **Z. 7:** Importiert die Pfadklasse für die optionale Antwortdatei.
- **Z. 8:** Importiert den Parser für `--write`.
- **Z. 10:** Fixiert A,B,C,D,E als gemeinsame Vektorreihenfolge.
- **Z. 11:** Übernimmt alle sieben ungerichteten Kanten samt Kosten aus Abbildung 2.
- **Z. 12:** Erstellt leere lokale Nachbarschaftsabbildungen für alle Router.
- **Z. 13:** Durchläuft jede eingegebene Kante mit beiden Endpunkten und Kosten.
- **Z. 14:** Speichert ihre erste Richtung.
- **Z. 15:** Speichert die Gegenrichtung mit denselben Kosten.
- **Z. 16:** Sortiert Bs Nachbarn nach direkten Linkkosten; das liefert E,C,A.
- **Z. 17:** Definiert die vier Tabellenziele ohne B, dessen Eigenkosten separat null bleiben.
- **Z. 18:** Erstellt alle gerichteten Zustellungen und sortiert zuerst nach Kosten, dann Sender und Empfänger.
- **Z. 19:** Speichert die KI-Kennzeichnung für das Ende der erzeugten Antwort.
- **Z. 21:** Definiert die Initialisierung aller lokalen Distanzvektoren.
- **Z. 22:** Setzt Eigenkosten null, direkte Nachbarziele auf Linkkosten und alle anderen Ziele auf Unendlich.
- **Z. 24:** Definiert die Initialisierung der gespeicherten Nachbartabellen.
- **Z. 25:** Erzeugt je Router und Nachbar eine Spalte; nur das jeweilige Nachbarziel ist anfangs direkt bekannt.
- **Z. 27:** Definiert die Berechnung eines lokalen Vektors aus seinen gespeicherten Nachbarkandidaten.
- **Z. 28:** Nimmt pro Ziel das kleinste Spaltenelement; für den Router selbst wird unabhängig davon null eingesetzt.
- **Z. 30:** Definiert eine Kopierhilfe für zweistufige Nachbartabellen.
- **Z. 31:** Kopiert jede innere Spalte separat, damit alte Tabellenzustände nicht durch spätere Änderungen mutieren.
- **Z. 33:** Definiert die asynchrone DV-Simulation.
- **Z. 34:** Startet alle lokalen Vektoren und Tabellen ohne vorweggenommene Informationen anderer Router.
- **Z. 35:** Speichert Bs initiale Tabelle und seinen initialen Vektor; `None` bedeutet noch keine empfangene Nachricht.
- **Z. 36:** Beginnt ein vollständiges globales Zustellprotokoll.
- **Z. 37:** Erlaubt höchstens zwanzig Durchläufe als Schutz gegen unerwartete Nichtkonvergenz.
- **Z. 38:** Setzt die netzweite Änderungsmarkierung für den neuen Durchlauf zurück.
- **Z. 39:** Verarbeitet jede gerichtete Nachricht in der festgelegten kostenaufsteigenden Reihenfolge.
- **Z. 40:** Kopiert den zu diesem Zeitpunkt aktuellen Sendervektor als unveränderlichen Nachrichteninhalt.
- **Z. 41:** Ersetzt beim Empfänger genau die Senderspalte durch Linkkosten plus jede gemeldete Zieldistanz.
- **Z. 42:** Berechnet den neuen lokalen Empfängervektor aus seinen aktuellen Spalten.
- **Z. 43:** Prüft, ob dieser neue Vektor vom zuvor gespeicherten Empfängervektor abweicht.
- **Z. 44:** Merkt per booleschem Oder, ob irgendwo im Durchlauf ein Vektor geändert wurde.
- **Z. 45:** Übernimmt das Ergebnis sofort; spätere Nachrichten desselben Durchlaufs dürfen es bereits verwenden.
- **Z. 46:** Vergibt die nächste fortlaufende globale Ereignisnummer.
- **Z. 47:** Speichert Nummer, Durchlauf, Richtung, Kosten und Änderungsstatus dieser Zustellung.
- **Z. 48:** Erkennt die Ereignisse, die Bs lokale Tabelle tatsächlich berühren.
- **Z. 49:** Speichert nach jeder B-Zustellung Tabelle, resultierenden Vektor und empfangenen Vektor als eigenen Schritt.
- **Z. 50:** Prüft erst nach allen Nachrichten, ob im ganzen Netz kein Vektor verändert wurde.
- **Z. 51:** Gibt den dann konvergierten Gesamtzustand und beide Protokolle zurück.
- **Z. 52:** Meldet ein Überschreiten der Schutzgrenze als Fehler statt als angebliche Konvergenz.
- **Z. 54:** Definiert die alternative synchrone DV-Simulation.
- **Z. 55:** Beginnt unabhängig von der asynchronen Simulation mit frischen Anfangszuständen.
- **Z. 56:** Speichert Bs unveränderte Initialtabelle als Runde null.
- **Z. 57:** Erlaubt höchstens zwanzig synchrone Runden.
- **Z. 58:** Berechnet alle neuen Spalten ausschließlich aus der alten Vektormatrix; keine neue Rundendistanz wird vorzeitig gelesen.
- **Z. 59:** Berechnet alle neuen Routervektoren aus diesen vollständig aufgebauten neuen Tabellen.
- **Z. 60:** Speichert Bs Tabelle und Vektor nach Abschluss der Runde.
- **Z. 61:** Vergleicht die gesamte neue Vektormatrix mit der alten, nicht nur Bs Zeile.
- **Z. 62:** Liefert den nach einer netzweit unveränderten Runde bestätigten Fixpunkt zurück.
- **Z. 63:** Übernimmt bei vorhandenen Änderungen die neue Matrix erst jetzt als Grundlage der nächsten Runde.
- **Z. 64:** Meldet eine verletzte Rundengrenze als Fehler.
- **Z. 66:** Definiert die vom DV-Algorithmus unabhängige Brute-force-Kontrolle der kürzesten Kosten.
- **Z. 67:** Prüft, ob der rekursive Restweg sein Ziel erreicht hat.
- **Z. 68:** Liefert dann Restkosten null.
- **Z. 69:** Enumeriert jede zyklusfreie Nachbarfortsetzung, addiert deren Linkkosten und nimmt das Minimum; ohne Fortsetzung gilt Unendlich.
- **Z. 71:** Definiert die gemeinsame Prüfung beider DV-Verfahren.
- **Z. 72:** Entpackt Gesamtvektoren, Tabellen und Protokolle der asynchronen Berechnung.
- **Z. 73:** Entpackt die entsprechenden synchronen Ergebnisse.
- **Z. 74:** Prüft Bs verlangte Nachbarreihenfolge E,C,A.
- **Z. 75:** Prüft, dass global tatsächlich die Minimalkante A→E mit Kosten 2 zuerst bedient wird.
- **Z. 76:** Verknüpft Bs erste drei Tabellenereignisse mit dem globalen Protokoll und prüft deren Senderfolge.
- **Z. 77:** Prüft Bs vollständigen erwarteten Endvektor in der Reihenfolge A,B,C,D,E.
- **Z. 78:** Verlangt identische Endvektoren aller Router in synchroner und asynchroner Simulation.
- **Z. 79:** Durchläuft jeden möglichen Startknoten für die unabhängige Ergebniskontrolle.
- **Z. 80:** Durchläuft jedes Ziel und deckt damit alle 25 Start-Ziel-Paare ab.
- **Z. 81:** Vergleicht die konvergierte Distanz mit der unabhängig rekursiv berechneten minimalen Pfadsumme.
- **Z. 82:** Prüft zusätzlich jede Nachbarspalte jedes Routers.
- **Z. 83:** Durchläuft dafür alle fünf möglichen Zielzeilen einschließlich Eigenziel.
- **Z. 84:** Verifiziert für jede asynchrone Spaltenzelle Linkkosten plus finalen Nachbarvektor; keine veraltete Meldung bleibt verborgen.
- **Z. 85:** Wiederholt dieselbe vollständige Zellprüfung für das synchrone Ergebnis.
- **Z. 86:** Verlangt einen ganzen letzten asynchronen Durchlauf ohne irgendeine Vektoränderung.
- **Z. 87:** Prüft zusätzlich Bs unveränderten Vektor in den letzten zwei synchronen Zuständen.
- **Z. 88:** Prüft Schrittabfolgen beider Interpretationen.
- **Z. 89:** Bildet jeweils Paare aufeinanderfolgender B-Zustände.
- **Z. 90:** Verifiziert, dass keine von Bs Distanzen während dieser statischen Initialkonvergenz steigt.
- **Z. 91:** Berechnet jeden protokollierten B-Vektor aus seiner Tabelle erneut und vergleicht ihn mit dem gespeicherten Vektor.
- **Z. 92:** Prüft sieben eingegebene ungerichtete Kanten und ihre vierzehn gerichteten Nachbarschaftseinträge.
- **Z. 94:** Definiert die Textdarstellung einer Distanz.
- **Z. 95:** Formatiert Unendlich als ∞ und endliche Werte als Zeichenketten.
- **Z. 97:** Definiert die feste geordnete Textdarstellung eines ganzen Vektors.
- **Z. 98:** Formatiert die Werte in Reihenfolge A,B,C,D,E, durch Kommata getrennt und in Klammern.
- **Z. 100:** Definiert die Markdown-Ausgabe eines einzelnen B-Zustands mit optionalem Vorgängerzustand zum Vergleich.
- **Z. 101:** Entpackt Ereignisnummer, Beschriftung, Tabelle, B-Vektor und optionalen Nachrichteninhalt.
- **Z. 102:** Beginnt die Zustandsausgabe mit einer eindeutigen Ereignis- beziehungsweise Rundenüberschrift.
- **Z. 103:** Erkennt, ob dieser Zustand durch eine konkrete asynchrone B-Nachricht entstanden ist.
- **Z. 104:** Gibt deren tatsächlichen empfangenen Nachbarvektor aus.
- **Z. 105:** Schreibt Tabellenkopf und Ausrichtung für die Spalten über E,C,A und das jeweilige Minimum.
- **Z. 106:** Erstellt eine Zielzeile für A,C,D,E; B selbst wird darunter als Eigenkosten null dokumentiert.
- **Z. 107:** Beginnt die Sammlung der drei Kandidatenzellen dieser Zielzeile.
- **Z. 108:** Durchläuft die Nachbarspalten in Kostenreihenfolge E,C,A.
- **Z. 109:** Liest und formatiert die tatsächlichen gespeicherten Kandidatenkosten.
- **Z. 110:** Markiert eine gegenüber der letzten B-Tabelle geänderte Zelle fett; unveränderte Zellen bleiben normal.
- **Z. 111:** Formatiert die minimale Zielkostenzahl aus Bs aktuellem Vektor.
- **Z. 112:** Prüft gesondert, ob sich auch dieses Minimum gegenüber dem vorigen B-Zustand geändert hat.
- **Z. 113:** Markiert das geänderte Minimum fett, unabhängig von anderen Spaltenänderungen.
- **Z. 114:** Verbindet Ziel, drei Kandidaten und Minimum zu einer vollständigen Markdown-Tabellenzeile.
- **Z. 115:** Ergänzt den gesamten B-Vektor und die Erklärung der ausgesparten B-Eigenzeile.
- **Z. 116:** Liefert die erzeugten Textzeilen zurück, ohne selbst Dateien zu schreiben.
- **Z. 118:** Definiert die Gesamtantwort aus beiden simulierten Protokollen.
- **Z. 119:** Entpackt das asynchrone Ergebnis für Ereignisliste und B-Tabellen.
- **Z. 120:** Übernimmt aus dem synchronen Ergebnis die benötigte Zustandsfolge und ignoriert die hier nicht ausgegebenen Matrizen.
- **Z. 121:** Erstellt Eingabekanten, Initialisierungsregel, DV-Formel, genaue Zustellkonvention, D=17-Zwischenwert, Markierungsregel und Ereignistabellenkopf.
- **Z. 122:** Durchläuft alle globalen Zustellungen einschließlich Nachrichten an andere Router.
- **Z. 123:** Schreibt Richtung, Kosten, Änderungsstatus und den Hinweis, ob Bs letzte Tabelle unverändert weitergilt.
- **Z. 124:** Beginnt den Abschnitt sämtlicher asynchroner B-Tabellen.
- **Z. 125:** Durchläuft Bs Initialzustand und jeden gespeicherten Empfangsschritt.
- **Z. 126:** Formatiert jeden Zustand mit dem vorherigen B-Zustand als Grundlage für die Änderungsmarkierung.
- **Z. 127:** Erklärt die synchrone Alternative: alte Vektoren für alle Nachrichten und keine Wiederverwendung neuer Rundenergebnisse.
- **Z. 128:** Durchläuft sämtliche synchronen Rundenzustände einschließlich Initial- und Konvergenzrunde.
- **Z. 129:** Erzeugt deren B-Tabellen und markiert Änderungen gegenüber der jeweils vorigen Runde.
- **Z. 130:** Ergänzt Endpfade, konkrete Kostenproben, dynamisch gezählte Zustellungen/Runden und die Beschreibung der ausgeführten Tests.
- **Z. 131:** Verbindet die Textteile und hängt die vollständige KI-Kennzeichnung an.
- **Z. 133:** Führt den Hauptablauf nur beim direkten Programmstart aus.
- **Z. 134:** Berechnet die vollständige asynchrone Konvergenz.
- **Z. 135:** Berechnet separat die vollständige synchrone Konvergenz.
- **Z. 136:** Führt alle Vergleichs-, Fixpunkt-, Reihenfolge- und Brute-force-Tests vor einer Ausgabe aus.
- **Z. 137:** Erstellt den Kommandozeilenparser mit der Modulbeschreibung als Hilfetext.
- **Z. 138:** Registriert `--write` als optionalen booleschen Schalter.
- **Z. 139:** Verzweigt bei ausdrücklich gewünschter Dateiausgabe.
- **Z. 140:** Bestimmt `antwort.md` relativ zum Skriptpfad.
- **Z. 141:** Schreibt ausschließlich die aus den geprüften Ergebnissen erzeugte UTF-8-Antwortdatei.
- **Z. 142:** Meldet die bestandenen Prüfungen und den erzeugten Antwortpfad.
- **Z. 143:** Beginnt den Zweig ohne Dateierzeugung.
- **Z. 144:** Gibt dann dieselbe vollständige Antwort auf Standardausgabe aus.

## Tests – `ue6.6/test_algorithmen.py`

Aufruf ab Repository-Wurzel: `PYTHONDONTWRITEBYTECODE=1 python3 ueb06/ue6.6/test_algorithmen.py`. Der Treiber verwendet `unittest` aus der Standardbibliothek. Er führt sechs Testmethoden aus und kontrolliert zusätzlich zu den fachlichen Proben die exakte Reproduzierbarkeit aller Antworten und die Vollständigkeit dieser Zeilenerklärung. Keine weitere Datei wird erzeugt.

### Jede nichtleere Zeile

- **Z. 1:** Kennzeichnet KI-System und verwendetes Modell auch für den Testtreiber.
- **Z. 2:** Dokumentiert Anbieterbezeichnung und Bearbeitungsdatum.
- **Z. 3:** Beginnt die tatsächliche Anfrage für 6.4–6.6.
- **Z. 4:** Ergänzt Implementierungs-, Test-, Sprach- und Schreibumfangsvorgaben.
- **Z. 5:** Beschreibt Reproduktions-, Kontroll- und Erklärungstests als Zweck des Moduls.
- **Z. 6:** Importiert `Path` für arbeitsverzeichnisunabhängige Dateipfade.
- **Z. 7:** Importiert reguläre Ausdrücke zur Erfassung der erklärten Zeilennummern.
- **Z. 8:** Importiert `runpy`, um Lösungsfunktionen ohne deren Hauptablauf zu laden.
- **Z. 9:** Importiert die Prozessschnittstelle für echte separate Programmaufrufe.
- **Z. 10:** Importiert `sys`, damit Unterprozesse denselben Python-Interpreter verwenden.
- **Z. 11:** Importiert das Standard-Testframework `unittest`.
- **Z. 13:** Bestimmt den gemeinsamen Ordner `ueb06` aus dem absoluten Testdateipfad.
- **Z. 14:** Listet die drei zu prüfenden Lösungsprogramme als absolute Pfade auf.
- **Z. 15:** Lädt deren Modulvariablen und Funktionen; die jeweiligen `__main__`-Blöcke werden nicht ausgeführt.
- **Z. 17:** Definiert die Sammlung der sechs automatischen Tests als `TestCase`.
- **Z. 18:** Beginnt die Testmethode für alle eingebauten fachlichen Verifikationen.
- **Z. 19:** Berechnet den Subnetzplan und führt seine Kapazitäts-, Minimalitäts- und Überschneidungstests aus.
- **Z. 20:** Baut den Dijkstra-Eingabegraphen auf.
- **Z. 21:** Führt Dijkstra aus und entpackt dessen drei Ergebnisse in die fachliche Testfunktion.
- **Z. 22:** Berechnet beide DV-Varianten und führt deren gesamte unabhängige Verifikation aus.
- **Z. 24:** Beginnt den Test der unveränderten Reproduzierbarkeit aller Antwortdateien.
- **Z. 25:** Durchläuft jedes Lösungsprogramm.
- **Z. 26:** Ordnet mögliche Fehlschläge dem jeweiligen Skriptnamen als Untertest zu.
- **Z. 27:** Startet einen echten Python-Unterprozess, sammelt dessen Ausgabe und verlangt einen erfolgreichen Exitstatus.
- **Z. 28:** Vergleicht die komplette Ausgabe einschließlich Zeilenumbrüchen mit der abgelegten Antwortdatei.
- **Z. 30:** Beginnt die Prüfung von Syntax und KI-Kennzeichnungen.
- **Z. 31:** Prüft die drei Lösungen und zusätzlich den Testtreiber selbst.
- **Z. 32:** Liest den vollständigen UTF-8-Quelltext.
- **Z. 33:** Kompiliert ihn im Speicher zur Syntaxprüfung, ohne Bytecode-Dateien zu schreiben.
- **Z. 34:** Verlangt die vorgeschriebene KI-Kennzeichnung direkt am Anfang jeder Python-Datei.
- **Z. 35:** Prüft das vorgegebene Datum in jedem Python-Quelltext.
- **Z. 36:** Prüft anschließend die drei erzeugten Antwortdateien.
- **Z. 37:** Liest jeweils den abschließenden Kennzeichnungsabschnitt nach dessen letzter Überschrift.
- **Z. 38:** Verlangt dort die Angabe der tatsächlichen Anfrage.
- **Z. 39:** Verlangt dort ebenfalls das vorgegebene Datum.
- **Z. 41:** Beginnt den automatischen Vollständigkeitstest der Zeilenerklärung.
- **Z. 42:** Liest dieses Erklärungsdokument.
- **Z. 43:** Definiert die vier eindeutigen Abschnittsanfänge passend zur Skriptreihenfolge.
- **Z. 44:** Durchläuft alle vier Python-Dateien mit ihrem Abschnittsindex.
- **Z. 45:** Isoliert den zugehörigen Hauptabschnitt bis zur nächsten Überschrift zweiter Ebene.
- **Z. 46:** Extrahiert die einzeln dokumentierten Quellzeilennummern aus den Aufzählungspunkten.
- **Z. 47:** Ermittelt unabhängig aus der echten Datei alle nichtleeren Quellzeilennummern.
- **Z. 48:** Verlangt exakt dieselbe Reihenfolge ohne Lücken, zusätzliche Nummern oder doppelte Erklärungen.
- **Z. 50:** Beginnt eine Negativkontrolle für die Fehlererkennung der Dijkstra-Prüfung.
- **Z. 51:** Baut den originalen Eingabegraphen erneut auf.
- **Z. 52:** Berechnet zunächst ein korrektes Dijkstra-Ergebnis samt Vorgängern und Spur.
- **Z. 53:** Verfälscht absichtlich nur die gemeldete Distanz nach F um eins.
- **Z. 54:** Verlangt, dass die anschließende Verifikation eine Assertion auslöst.
- **Z. 55:** Prüft das absichtlich falsche Ergebnis; unerkannter Fehler würde den Test scheitern lassen.
- **Z. 57:** Beginnt die gesonderte Prüfung charakteristischer DV-Zwischenwerte und Ablaufgrößen.
- **Z. 58:** Berechnet einen frischen asynchronen Ablauf.
- **Z. 59:** Berechnet einen frischen synchronen Ablauf.
- **Z. 60:** Prüft Bs ersten endlichen D-Kandidaten 17 nach der Nachricht von E.
- **Z. 61:** Prüft die Verbesserung auf 11 nach der anschließenden Nachricht von C.
- **Z. 62:** Verlangt insgesamt 42 gerichtete asynchrone Zustellungen.
- **Z. 63:** Verlangt drei synchrone Runden; der zusätzlich gespeicherte Initialzustand wird abgezogen.
- **Z. 65:** Startet die Tests nur beim direkten Aufruf des Testtreibers.
- **Z. 66:** Führt sämtliche Testmethoden mit ausführlicher, einzeln benannter Ergebnisausgabe aus.

## Verifizierte Ergebnisse

- 6.4: Netze 10.10.0.0/24, 10.10.1.0/26, 10.10.1.64/27 und 10.10.1.96/30; alle Kapazitäts-, Ausrichtungs-, Pool- und Überschneidungsprüfungen bestanden.
- 6.5: Distanzen ab A in Reihenfolge A,B,C,D,E,F,G: (0,1,3,8,9,6,4); Auswahl A,B,C,G,F,D,E; zwei gleich kurze Wege nach F und E vollständig aufgeführt; sämtliche 49 Start-Ziel-Paare unabhängig geprüft.
- 6.6: B-Vektor in Reihenfolge A,B,C,D,E: (5,0,7,11,3). Asynchron 42 Zustellungen in drei Durchläufen, synchron drei Runden; beide einschließlich netzweit unveränderter Abschlussphase. Sämtliche 25 Start-Ziel-Paare und alle finalen Spalten geprüft.

## KI-Kennzeichnung

KI-Kennzeichnung RN WS26: Hermes Agent, OpenAI gpt-6.1-sol. Anbieter: ChatGPT or Codex Subscription. Datum: 2026-10-29. Tatsächliche Anfrage: Löse und implementiere Aufgaben 6.4, 6.5 und 6.6 dieses RN-Blatts, mit lauffähigem Python, Tests und deutschen antwort.md; nur vereinbarte Pfade bearbeiten.
