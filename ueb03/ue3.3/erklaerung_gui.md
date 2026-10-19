<!-- KI-Kennzeichnung: Hermes Agent / OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). Datum: 2026-10-19. Auftrag: Zusatzcode des tatsächlich ausgeführten Thunderbird-GUI-Tests zeilenweise erklären; POP3-Server unverändert lassen. -->

# Zeilenweise Erklärung von `gui_test.py`

Die Nummern beziehen sich auf die abgegebene Datei [gui_test.py](gui_test.py). Jede nichtleere Zeile hat einen eigenen Eintrag. Leerzeilen strukturieren nur den Text; auch ihre Nummern werden unten genannt. Eingebettetes JavaScript wird **im echten Thunderbird** ausgeführt. Es erzeugt keine simulierte Oberfläche und setzt keine vorbereiteten Nachrichten in eine Mailbox ein.

## Idee und Grenzen

`Python → Original-POP3-Server → echter TCP-Abruf durch Thunderbird → echte Inbox/Lesebereich → X11-Screenshot`.

`RecordingHandler` ergänzt ausschließlich im Test eine Beobachtungsschicht um den bestehenden Handler. Die eigentliche Protokollverarbeitung bleibt in dessen `super().dispatch`. Der Test verwendet ein neues temporäres Profil, Originaldaten für `alice/secret`, `leave_on_server` und ausschließlich Loopback als POP3-Ziel. `marionette_driver` ist nur beim Start des optionalen Tests erforderlich; der Server bleibt unabhängig davon ausführbar.

## Kopf und Imports

| Zeile | Erklärung |
|---:|---|
| 1 | Kennzeichnet die KI-Unterstützung mit Werkzeug, Modell und angegebenem Providerhinweis. |
| 2 | Nennt das Erstellungsdatum. |
| 3 | Dokumentiert den tatsächlichen Zusatzauftrag und den Schutz des bestehenden Servers. |
| 4 | Beginnt den Modul-Docstring und nennt die isolierte Testausführung. |
| 6 | Nennt externe Programme und das optionale Python-Paket. |
| 7 | Zeigt einen portablen Aufruf mit explizitem Thunderbird-Pfad. |
| 8 | Empfiehlt eine getrennte Python-Umgebung statt Eingriffen in die Serverabhängigkeiten. |
| 9 | Beendet den Docstring; `argparse` nutzt ihn später als Hilfetext. |
| 10 | Importiert den Parser für Kommandozeilenargumente. |
| 11 | Importiert den Stapel für garantierte Prozess-Cleanup-Callbacks. |
| 12 | Importiert UTC-Zeitstempel für den Prüfbericht. |
| 13 | Importiert die aktuelle E-Mail-Parsing-Policy für dekodierte Inhalte. |
| 14 | Importiert den Parser für originale Nachrichtendaten als Bytes. |
| 15 | Importiert SHA-256 zur Kontrolle von Quellen und Screenshots. |
| 16 | Importiert JSON für Präferenzwerte und Prüfbericht. |
| 17 | Erlaubt das Kopieren und Ergänzen der Prozessumgebung. |
| 18 | Importiert plattformgerechte Dateipfade. |
| 19 | Wird zur Suche nach installierten Programmen verwendet. |
| 20 | Importiert lokale TCP-Sockets für Portwahl und Bereitschaftsprüfung. |
| 21 | Ermöglicht Start, Kontrolle und Ende externer Programme. |
| 22 | Ermöglicht ein temporäres, automatisch gelöschtes Profil; berücksichtigt die konfigurierte temporäre Umgebung. |
| 23 | Stellt den Hintergrundthread für den POP3-Server bereit. |
| 24 | Liefert monotone Wartefristen und kurze Pollingpausen. |
| 26 | Importiert ausschließlich vorhandene Server-Schnittstellen aus der unveränderten Nachbardatei. |

## Beobachtung und Wartefunktionen

| Zeile | Erklärung |
|---:|---|
| 29 | Leitet eine reine Test-Beobachtungsklasse vom echten POP3-Handler ab. |
| 30 | Beschreibt Quellschutz und Passwortredaktion. |
| 32 | Überschreibt den zentralen Befehlseinstieg für die Beobachtung. |
| 33 | Baut den Protokolleintrag; bei `PASS` ersetzt ein Platzhalter das Argument. |
| 34 | Führt den echten ursprünglichen Befehl aus und bewahrt dessen Rückgabewert. |
| 35 | Protokolliert den Befehl erst nach seiner Verarbeitung; dies sind Befehlsereignisse, keine vollständigen Serverantworten. |
| 36 | Gibt das ursprüngliche Sitzungsende-Signal unverändert zurück. |
| 39 | Definiert eine allgemeine Wartefunktion mit standardmäßig 40 Sekunden Zeitlimit. |
| 40 | Erklärt, dass eine konkrete Bedingung geprüft wird. |
| 41 | Berechnet eine monotone Endfrist, unabhängig von Änderungen der Systemuhr. |
| 42 | Initialisiert den zuletzt beobachteten Wert beziehungsweise Fehler. |
| 43 | Wiederholt die Prüfung nur bis zur Frist. |
| 44 | Beginnt den Schutz gegen vorübergehende Fehler beim Start der GUI. |
| 45 | Ruft die übergebene Prüffunktion auf. |
| 46 | Erkennt einen erfolgreichen, wahrheitswertigen Prüfwert. |
| 47 | Gibt diesen Wert zurück, beispielsweise die tatsächlich empfangenen Betreffe. |
| 48 | Fängt gewöhnliche Prüf-Ausnahmen ab, damit noch nicht fertige Oberflächen erneut geprüft werden können. |
| 49 | Bewahrt den letzten Fehler für die spätere Timeout-Diagnose auf. |
| 50 | Wartet 0,2 Sekunden zwischen Prüfversuchen; dies ersetzt nicht die Erfolgsbedingung. |
| 51 | Meldet bei Fristablauf die Bedingung und letzte Beobachtung. |
| 54 | Definiert die lokale TCP-Bereitschaftsprüfung für Marionette. |
| 55 | Beginnt die Behandlung noch nicht erreichbarer Ports. |
| 56 | Versucht eine kurz begrenzte Verbindung zu Loopback; `with` schließt die Probeverbindung. |
| 57 | Meldet bei erfolgreicher Verbindung Bereitschaft. |
| 58 | Erkennt verweigerte oder anderweitig fehlgeschlagene Verbindungen. |
| 59 | Veranlasst in diesem Fall einen weiteren Warteversuch. |
| 62 | Definiert das idempotente Aufräumen eines gestarteten Unterprozesses. |
| 63 | Erkennt fehlende oder bereits beendete Prozesse. |
| 64 | Tut in diesen Fällen nichts; doppelte Cleanup-Aufrufe sind damit erlaubt. |
| 65 | Fordert sonst zunächst ein Ende mit `terminate` an. |
| 66 | Beginnt das begrenzte Warten auf das Ende. |
| 67 | Wartet maximal 15 Sekunden. |
| 68 | Erkennt einen Prozess, der trotz Aufforderung weiterläuft. |
| 69 | Erzwingt dann als Notfallmaßnahme sein Ende. |
| 70 | Wartet auch nach dem Erzwingen, um den eigenen Kindprozess einzusammeln. |

## Argumente, Schutzprüfungen und Serverstart

| Zeile | Erklärung |
|---:|---|
| 73 | Definiert den ausführbaren Testablauf. |
| 74 | Erzeugt den Kommandozeilenparser mit Modulbeschreibung. |
| 75 | Akzeptiert den Thunderbird-Pfad; ohne Angabe wird im `PATH` gesucht. |
| 76 | Wählt standardmäßig das dedizierte lokale Display `:183`. |
| 77 | Legt den Belegordner standardmäßig relativ zum Skript fest. |
| 78 | Verarbeitet die tatsächlichen Kommandozeilenargumente. |
| 79 | Beginnt den erst jetzt nötigen optionalen Import. |
| 80 | Lädt den echten Marionette-Treiber; `--help` funktioniert bereits vor dieser Zeile. |
| 81 | Erkennt ein fehlendes optionales Paket. |
| 82 | Beendet den Test mit verständlicher Abhängigkeitsmeldung und Parser-Fehlercode. |
| 83 | Prüft, dass ein Thunderbird-Pfad vorhanden ist und auf eine Datei zeigt. |
| 84 | Meldet einen fehlenden Thunderbird-Pfad vor dem Start eigener Dienste. |
| 85 | Prüft beide zusätzlich erforderlichen externen Programme. |
| 86 | Sucht das jeweilige Programm im `PATH`. |
| 87 | Beendet den Test bei fehlendem Programm. |
| 88 | Erlaubt nur lokale Displaynummern wie `:183`, keine entfernten X-Server. |
| 89 | Meldet eine ungültige Displayangabe. |
| 90 | Entfernt den Doppelpunkt für die X11-Socket- und Locknamen. |
| 91 | Prüft vorhandenen X11-Socket beziehungsweise X-Server-Lock; `/tmp` ist hier nur der systemweite X11-Namensraum, kein Ablageort für Testdateien. |
| 92 | Verweigert die Benutzung eines bereits belegten Displays. |
| 93 | Erstellt den gewünschten Belegordner bei Bedarf. |
| 94 | Bestimmt die beiden geschützten Originaldateien über relative Repository-Pfade. |
| 95 | Berechnet ihre tatsächlichen SHA-256-Werte vor dem Test. |
| 96 | Initialisiert den Bericht mit UTC-Startzeit, laufendem Status und Quellhashes. |
| 97 | Erzeugt den echten Server auf Loopback; Port 0 lässt das Betriebssystem einen freien Port wählen. |
| 98 | Legt die Ereignisliste ausschließlich auf der Test-Serverinstanz an. |
| 99 | Setzt deren Handlerklasse auf den beobachtenden Untertyp, ohne die Serverdatei zu bearbeiten. |
| 100 | Bereitet den nicht als Daemon gestarteten Serverthread mit kurzem Shutdown-Pollintervall vor. |
| 101 | Startet die echte TCP-Bedienung. |
| 102 | Initialisiert Prozess- und Sitzungsvariablen für sicheren späteren Cleanup. |
| 103 | Beginnt den Testteil, dessen Ressourcen im äußeren `finally` wieder geschlossen werden. |
| 104 | Liest die originalen Datenbanknachrichten und parst Header und Text; diese Daten dienen nur als Erwartungswerte. |
| 105 | Leitet die erwarteten Betreffe aus diesen Originalen ab. |
| 106 | Bereitet den erwarteten Text der ersten Mail vor; normalisiert nur Rand-Whitespace und CRLF. |
| 107 | Protokolliert Soll-Betreffe und die tatsächlich gebundene Serveradresse. |
| 108 | Führt das Thunderbird-Binary mit `--version` aus und speichert dessen reale Ausgabe. |

## Isoliertes Profil und Kontoeinstellungen

| Zeile | Erklärung |
|---:|---|
| 109 | Öffnet erst den temporären Ordner, dann den Cleanup-Stapel; beim Verlassen werden dadurch Prozesse vor dem Löschen des Profils beendet. |
| 110 | Bestimmt den neuen Profil-Unterordner innerhalb des temporären Verzeichnisses. |
| 111 | Erstellt das leere Profil, statt ein vorhandenes persönliches zu verwenden. |
| 112 | Öffnet einen temporären Socket zur Auswahl eines Marionette-Ports. |
| 113 | Bindet ihn an Loopback mit Betriebssystem-Portwahl. |
| 114 | Liest den Port aus; am Ende des Blocks wird die Reservierung freigegeben. Bis zum Thunderbird-Start bleibt ein kleines übliches Portwahl-Rennen möglich. |
| 115 | Beginnt das Präferenzwörterbuch für dieses Testprofil. |
| 116 | Setzt den gerade ausgewählten Marionette-Port. |
| 117 | Registriert Testkonto und lokale Ordner. |
| 118 | Wählt das synthetische POP3-Konto als Standardkonto. |
| 119 | Ordnet den Server für lokale Ordner zu. |
| 120 | Verknüpft Konto 1 mit dem POP3-Testserver. |
| 121 | Verknüpft Konto 1 mit einer synthetischen Identität. |
| 122 | Verknüpft Konto 2 mit lokalen Ordnern. |
| 123 | Setzt einen ausdrücklich als Laboridentität erkennbaren Anzeigenamen. |
| 124 | Verwendet eine Beispieldomain-Adresse; es wird kein SMTP-Zugang eingerichtet. |
| 125 | Wählt tatsächlich POP3 als Kontotyp. |
| 126 | Gibt dem Konto einen erkennbaren lokalen Labornamen. |
| 127 | Beschränkt das POP3-Ziel auf die lokale IPv4-Loopbackadresse. |
| 128 | Stellt den Original-Testbenutzer `alice` ein. |
| 129 | Nutzt den tatsächlich dynamisch zugewiesenen Serverport. |
| 130 | Wählt unverschlüsseltes POP3, passend zum lokalen Lernserver; nicht für echte Zugangsdaten geeignet. |
| 131 | Wählt Passwortauthentifizierung im Klartextkanal, passend zu `USER`/`PASS`. |
| 132 | Lässt abgerufene Nachrichten auf dem Server. |
| 133 | Deaktiviert periodische automatische Prüfungen. |
| 134 | Verhindert einen verfrühten Login beim Programmstart. |
| 135 | Sorgt dafür, dass die später explizit ausgelöste Biff-Prüfung Nachrichten wirklich herunterlädt. |
| 136 | Kennzeichnet den zweiten Server als lokale Ordner statt Netzwerkdienst. |
| 137 | Setzt dessen lokalen Hostnamen. |
| 138 | Setzt den üblichen Platzhalterbenutzer für lokale Ordner. |
| 139 | Setzt deren lesbaren Anzeigenamen. |
| 140 | Unterdrückt Benachrichtigungspopups, die eine Aufnahme verdecken könnten. |
| 141 | Unterdrückt den Benachrichtigungston. |
| 142 | Unterdrückt den Dialog zur Standard-Mailprogrammwahl. |
| 143 | Deaktiviert die Mail-Startseite. |
| 144 | Verhindert das automatische Laden entfernter Nachrichtenbilder. |
| 145 | Deaktiviert den für diesen Test unnötigen globalen Nachrichtenindex. |
| 146 | Fordert eine ungruppierte Standardansicht ohne gesetzte View-Flags an. |
| 147 | Vermeidet eine versionsabhängige Startseiten-Umleitung. |
| 148 | Deaktiviert den eingebauten Kontoanbieter-Assistenten per Präferenz. |
| 149 | Fordert keine automatischen Anwendungsupdates an. |
| 150 | Setzt zusätzlich die historische Update-Aktivierungspräferenz; einzelne Präferenzen ersetzen keine Netzwerksandbox. |
| 151 | Deaktiviert die Datenübermittlungsrichtlinie im Testprofil. |
| 152 | Unterdrückt den Telemetrie-Erststartzustand per Präferenz. |
| 153 | Deaktiviert Telemetrie per Präferenz. |
| 154 | Deaktiviert die Captive-Portal-Erkennung per Präferenz. |
| 155 | Deaktiviert die Netzverbindungserkennung per Präferenz. |
| 156 | Deaktiviert eine neue-Tab-Startseite per Präferenz. |
| 157 | Beendet das Wörterbuch; nicht jede Präferenz ist in jeder Thunderbird-Version wirksam. |
| 158 | Schreibt `user.js` nur in das neue Profil; JSON-Escaping erzeugt gültige JavaScript-Strings, Zahlen und boolesche Werte. |

## Echte Anwendung und Automatisierungszugang

| Zeile | Erklärung |
|---:|---|
| 159 | Kopiert die Umgebung und ergänzt nur für Kindprozesse das Testdisplay und die Trennung von bestehenden Instanzen. |
| 160 | Öffnet die unbearbeitete Anwendungsausgabe als Textlog im Belegordner. |
| 161 | Startet den echten virtuellen X-Server mit 1440 × 1000 Pixeln, Farbtiefe 24 und ohne TCP-X11-Listener. |
| 162 | Registriert sofort dessen Stopfunktion auf dem Cleanup-Stapel. |
| 163 | Speichert seine tatsächliche Prozess-ID. |
| 164 | Wartet auf X11-Socket und lebenden Xvfb-Prozess. |
| 165 | Startet das echte Thunderbird mit frischem Profil und Marionette; `--remote-allow-system-access` erlaubt die benötigten internen UI-APIs. |
| 166 | Registriert sofort auch Thunderbirds Stopfunktion; der zuletzt registrierte Prozess wird zuerst beendet. |
| 167 | Speichert die tatsächliche Thunderbird-Prozess-ID. |
| 168 | Wartet bis zu 60 Sekunden auf den lokalen Marionette-Zugang. |
| 169 | Verbindet den optionalen Python-Treiber mit genau dieser gestarteten Instanz. |
| 170 | Eröffnet die echte Automatisierungssitzung. |
| 171 | Wählt den privilegierten Anwendungs- statt Webseitenkontext; `chrome` meint hier Mozilla-Anwendungsoberfläche, nicht Google Chrome. |
| 173 | Definiert einen Helfer für JavaScript und dessen explizite Argumente. |
| 174 | Sucht das echte Hauptfenster, dessen Tabverwaltung und die aktuelle Drei-Fenster-Ansicht; optionale Zugriffe erlauben Bereitschaftsprüfungen. |
| 175 | Führt das Präfix und den jeweiligen Befehl über Marionette aus; übergibt Werte getrennt statt sie in JavaScript einzusetzen. |
| 177 | Wartet auf die tatsächliche Ordner- und Nachrichtenliste. |
| 178 | Positioniert und vergrößert das echte Fenster für lesbare, einheitliche Aufnahmen. |

## Passwort, echter Abruf und Inbox-Verifikation

| Zeile | Erklärung |
|---:|---|
| 179 | Beginnt den JavaScript-Block zum Hinterlegen des synthetischen Passworts. |
| 180 | Importiert Thunderbirds echte Mail-Dienste. |
| 181 | Erstellt einen Login-Datensatz über die Mozilla-Komponentenschnittstelle. |
| 182 | Initialisiert dessen Mailbox-Herkunft, Realm und Laborkennung; `secret` gehört nur zum synthetischen Originalkonto. |
| 183 | Markiert den noch nicht abgeschlossenen Speichervorgang im echten Fenster. |
| 184 | Speichert den Login asynchron; erst bei erfülltem Promise wird die Bereitschaft markiert. |
| 185 | Liefert zur Kontrolle die URI des konfigurierten echten POP3-Kontos zurück. |
| 186 | Beendet diesen JavaScript-Aufruf. |
| 187 | Wartet auf den wirklich abgeschlossenen Passwortspeichervorgang, bevor ein Abruf starten kann. |
| 188 | Beginnt den JavaScript-Aufruf für den tatsächlichen Nachrichtenabruf. |
| 189 | Importiert erneut Mail-Dienste, da jeder Aufruf einen neuen Ausführungskontext erhalten kann. |
| 190 | Holt das echte konfigurierte POP3-Eingangskonto. |
| 191 | Löst mit `performBiff` Thunderbirds eigenen POP3-Client aus; die Testfunktion implementiert keinen Ersatzclient. |
| 192 | Beendet den Abruf-Auslöseblock. |
| 193 | Beginnt ein wiederverwendbares JavaScript-Präfix für den echten Posteingang. |
| 194 | Importiert die Mail-Dienste für nachfolgende unabhängige Aufrufe. |
| 195 | Sucht den tatsächlichen Inbox-Ordner anhand des Thunderbird-Ordnerflags statt eines sprachabhängigen Namens. |
| 196 | Beendet den gespeicherten JavaScript-Text. |
| 197 | Wartet auf genau vier tatsächlich empfangene Nachrichten und liest ihre dekodierten Betreffe aus Thunderbirds Maildatenbank. |
| 198 | Vergleicht die Betreffmengen unabhängig von der Sortierreihenfolge. |
| 199 | Bricht mit konkreter Diagnose ab, falls die empfangenen Daten nicht den Originalen entsprechen. |
| 200 | Hält die beobachteten Betreffe im Verifikationslog fest. |
| 201 | Wählt über die echte UI-Ansicht die Inbox und blendet Ordner- sowie Lesebereich ein. |
| 202 | Wartet zusätzlich auf vier Zeilen im tatsächlichen Nachrichtenansichtsmodell. |
| 203 | Liest die Betreffe in der aktuellen Anzeigereihenfolge aus genau diesem Ansichtsmodell. |
| 204 | Vergleicht auch die sichtbare Ansicht mit den Originaldaten. |
| 205 | Verhindert einen Erfolg bei falscher oder unvollständiger Nachrichtenansicht. |

## Bildschirmaufnahmen, geöffnete Mail und reguläres Ende

| Zeile | Erklärung |
|---:|---|
| 207 | Definiert die Funktion für echte Bildschirmaufnahmen. |
| 208 | Bestimmt die PNG-Zieldatei im Belegordner. |
| 209 | Nimmt mit `ffmpeg`/`x11grab` genau ein Bild des echten X-Displays auf; Fehlercode und 20-Sekunden-Limit werden geprüft. `-y` erlaubt den dokumentierten Ersatz alter Belege. |
| 210 | Berechnet den SHA-256 der tatsächlich geschriebenen PNG-Datei und protokolliert ihn. |
| 212 | Wartet darauf, dass Thunderbird die POP3-Sitzung tatsächlich mit `QUIT` beendet hat. |
| 213 | Erstellt den echten Inbox-Screenshot vor der Mailauswahl. |
| 214 | Wählt die erste Originalmail nach ihrem Betreff über die echte Thunderbird-Ansicht; die Auswahl löst deren normalen Lesebereich aus. |
| 215 | Wartet auf den tatsächlich geladenen und gerenderten Nachrichtentext im verschachtelten Nachrichtenbrowser, nicht nur auf einen Datenbankeintrag. |
| 216 | Normalisiert Zeilenenden und Rand-Whitespace des gelesenen sichtbaren Textes. |
| 217 | Vergleicht den gesamten so normalisierten Mailtext mit dem Original. |
| 218 | Bricht bei Textabweichung ab und nennt den tatsächlich beobachteten Inhalt. |
| 219 | Speichert Betreff, tatsächlichen Text und erfolgreichen Originalvergleich. |
| 220 | Fotografiert die echte Oberfläche erneut, jetzt mit geöffneter Nachricht. |
| 221 | Plant Thunderbirds regulären Anwendungs-Shutdown nach 500 Millisekunden, damit vorher die Automatisierungssitzung geordnet getrennt werden kann. |
| 222 | Schließt die Marionette-Sitzung; `Marionette.quit()` wird bewusst nicht benutzt, weil Python und nicht Marionette die Anwendung gestartet hat. |
| 223 | Markiert die Sitzung als geschlossen, um unnötigen zweiten Zugriff zu vermeiden. |
| 224 | Wartet auf das tatsächliche Prozessende und protokolliert den Exitcode. |
| 225 | Prüft ausdrücklich, ob die Anwendung erfolgreich mit Code 0 endete. |
| 226 | Verhindert einen Erfolgsbericht bei fehlerhaftem Prozessende. |
| 227 | Nach Verlassen von Cleanup-Stapel und temporärem Ordner wird die tatsächliche Entfernung des Profils protokolliert. |
| 228 | Extrahiert die von Thunderbird wirklich ausgeführten `RETR`-Nachrichtennummern. |
| 229 | Prüft, dass genau die vier erwarteten Abrufe stattfanden; auch zusätzliche doppelte Abrufe würden auffallen. |
| 230 | Bricht bei falscher Abrufmenge ab. |
| 231 | Prüft, dass die vier Originalnachrichten noch in der Serverdatenbank vorhanden sind. |
| 232 | Meldet eine entgegen der Testkonfiguration erfolgte Löschung. |
| 233 | Markiert erst nach diesen Prüfungen den fachlichen Erfolg; Cleanup kann den Status noch auf Fehler setzen. |

## Fehlerpfad, abschließender Cleanup und Bericht

| Zeile | Erklärung |
|---:|---|
| 234 | Erfasst auch Abbruchsignale wie `KeyboardInterrupt`, damit ein Fehlerbericht entsteht. |
| 235 | Speichert den Fehlertyp und die konkrete Fehlermeldung. |
| 236 | Wirft den ursprünglichen Fehler weiter; ein gescheiterter Lauf bekommt keinen Erfolgsexitcode. |
| 237 | Beginnt den unabhängig vom Ergebnis auszuführenden Schlussblock. |
| 238 | Erkennt eine möglicherweise noch offene Marionette-Sitzung. |
| 239 | Versucht deren getrennten Cleanup ohne Maskierung durch gewöhnliche Sitzungsfehler. |
| 240 | Schließt die Sitzung, sofern Thunderbird noch erreichbar ist. |
| 241 | Fängt Fehler ab, wenn die Anwendung im Fehlerpfad bereits beendet wurde. |
| 242 | Ignoriert nur diesen sekundären Sitzungs-Cleanup-Fehler. |
| 243 | Beendet einen eventuell verbliebenen Thunderbird-Prozess; bei regulärem Ende ist dies wirkungslos. |
| 244 | Beendet einen eventuell verbliebenen Xvfb-Prozess; fremde X-Server werden nie ausgewählt. |
| 245 | Stoppt die `serve_forever`-Schleife über die vorgesehene Server-API. |
| 246 | Schließt Serversocket und aktive Verbindungen über die vorhandene Server-Implementierung. |
| 247 | Wartet begrenzt auf das Ende des Serverthreads. |
| 248 | Übernimmt die tatsächlich beobachtete POP3-Befehlsfolge in den Bericht. |
| 249 | Berechnet die Quellhashes nach dem Test neu aus den echten Dateien. |
| 250 | Vergleicht Vorher und Nachher, um unbeabsichtigte Quelländerungen aufzudecken. |
| 251 | Prüft die tatsächlichen Prozess-Endzustände, das Ende des Serverthreads und den geschlossenen Server-Dateideskriptor. |
| 252 | Verlangt unveränderte geschützte Dateien und vollständig erfolgreichen Ressourcen-Cleanup. |
| 253 | Überschreibt einen fachlichen Erfolg andernfalls mit `FAIL`. |
| 254 | Protokolliert die tatsächliche UTC-Endzeit. |
| 255 | Schreibt den echten vollständigen Bericht als lesbares UTF-8-JSON; keine erfundenen Ersatzdaten bei Fehlern. |
| 256 | Gibt dieselben Prüfdaten zur unmittelbaren Ausführungskontrolle aus. |
| 257 | Liefert bei normalem Kontrollfluss nur für `PASS` Exitcode 0, sonst 1. |
| 260 | Unterscheidet direkten Skriptstart vom Import als Modul. |
| 261 | Startet `main` und macht dessen Rückgabewert zum Prozess-Exitcode. |

### Leerzeilen

Die Zeilen **5, 25, 27, 28, 31, 37, 38, 52, 53, 60, 61, 71, 72, 172, 176, 206, 211, 258 und 259** sind Leerzeilen. Sie trennen Dokumentation, Imports, Klassen, Funktionen und Ablaufabschnitte und verändern die Ausführung nicht.

## Warum die Nachweise belastbar sind

- Die Erwartungswerte stammen aus der Originaldatenbank; Thunderbird muss sie selbst über den echten Server empfangen. Der Test schreibt keine Maildateien oder angeblichen Abrufantworten als Ersatz.
- Beobachtete `RETR`-Befehle, Thunderbirds Posteingangsdatenbank, dessen Ansichtsmodell und der tatsächlich gerenderte Mailtext werden getrennt kontrolliert.
- Die beiden Bildschirmaufnahmen stammen aus dem realen X11-Framebuffer. Die abschließende visuelle Prüfung ist im [Testbericht](gui_testbericht.md) beschrieben; sie wird nicht als automatisch durchgeführte Bildanalyse im Python-Skript ausgegeben.
- Das finale [Verifikationslog](screenshots/verifikation.json) enthält `PASS`, die echten Werte, identische Quellhashes, Thunderbird-Exitcode 0 und vier positive Cleanup-Prüfungen.
- Die eingebauten Wartefristen schützen vor endlosem Warten, garantieren aber keine Unterstützung beliebiger Thunderbird-Versionen. Reale Ausführung ist für Version 158.0 belegt.
