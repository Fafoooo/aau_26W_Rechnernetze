# Ü 3.1 – Post Office Protocol 3 (POP3)

> **KI-Kennzeichnung (RN WS26):** erstellt mit Hermes Agent; Modell: OpenAI gpt-6.1-sol (hermes status: ChatGPT or Codex Subscription). **Datum:** 2026-10-19. **Auftrag:** Ü3.1 anhand RFC 1939 erklären: Arbeitsablauf, Sicherheit, Single-/Multi-Line-Antworten und Vergleich mit IMAP; Quellen RFC 2449 und RFC 9051 berücksichtigen.

## 1. Arbeitsablauf

POP3 dient zum **Abrufen** von E-Mails aus einem serverseitigen Postfach (Maildrop), nicht zum Versenden. Der Versand erfolgt über ein anderes Protokoll, typischerweise SMTP. Das Basismodell ist Herunterladen und optionales Löschen; ein Client kann Nachrichten auch auf dem Server belassen. POP3 hat keine IMAP-artige Ordner-/Flag-Synchronisierung.

1. **TCP-Verbindung:** Der Client verbindet sich zum Server, beim unverschlüsselten Standarddienst auf TCP-Port 110. Der Server sendet eine Begrüßung mit `+OK`. Der Übungsserver verwendet den unprivilegierten lokalen Port **11110**.
2. **AUTHORIZATION:** Der Client identifiziert sich mit `USER alice`, danach unmittelbar mit `PASS secret`. Nach erfolgreicher Authentifizierung öffnet und sperrt der Server das Postfach exklusiv. Scheitert Passwortprüfung oder Sperre, erfolgt kein Übergang in die nächste Phase.
3. **TRANSACTION:** `STAT` liefert Anzahl und Gesamtgröße, `LIST` Nummern und Größen, `RETR n` den Inhalt einer Nachricht. `UIDL` bietet dauerhaftere Nachrichtenkennungen, `TOP n k` Kopfzeilen und die ersten `k` Textzeilen. `DELE n` **markiert** nur zur Löschung; `RSET` nimmt alle Löschmarkierungen zurück. `NOOP` verändert nichts. Innerhalb einer Sitzung bleiben Nachrichtennummern unverändert, auch wenn Nachrichten markiert werden.
4. **UPDATE:** Nur `QUIT` aus TRANSACTION löst die tatsächliche Entfernung der markierten Nachrichten aus. Danach werden Ressourcen und Postfachsperre freigegeben und die TCP-Verbindung geschlossen. `QUIT` bereits in AUTHORIZATION beendet nur die Verbindung, ohne UPDATE.
5. **Abbruch statt QUIT:** Bei Verbindungsverlust, Client-Absturz oder Inaktivitäts-Timeout dürfen bloß markierte Nachrichten **nicht** gelöscht werden. Die Sperre muss trotzdem freigegeben werden. Bei einem Fehler während UPDATE kann das Resultat auf realen Servern teilweise unbestimmt sein; das Protokoll ist keine Bestätigung einer beliebigen Datenbanktransaktion.

Zustandsdiagramm:

```text
TCP-Verbindung -> +OK -> AUTHORIZATION
                           | USER / PASS erfolgreich + Maildrop-Lock
                           v
                       TRANSACTION -- QUIT --> UPDATE --> geschlossen
                           |
                           +-- Abbruch/Timeout --> geschlossen, kein UPDATE
AUTHORIZATION -- QUIT/Abbruch --> geschlossen, kein UPDATE
```

Alle Befehle und Protokollzeilen enden mit **CRLF**, also den Bytes `\r\n`. TCP liefert einen Bytestrom: Ein `recv()` kann eine halbe Zeile oder mehrere Zeilen enthalten. Der Empfänger muss deshalb puffern und am Protokollformat, nicht an TCP-Paketen, abgrenzen. Schlüsselwörter sind unabhängig von Groß-/Kleinschreibung; `+OK` und `-ERR` sendet der Server großgeschrieben. RFC 2449 ergänzt mit `CAPA` die Abfrage unterstützter Fähigkeiten in AUTHORIZATION und TRANSACTION.

## 2. Ist POP3 sicher?

**Unverschlüsseltes POP3 mit USER/PASS ist nicht sicher für echte Zugangsdaten.** Das Passwort und die mit RETR/TOP abgerufenen Nachrichten werden im Klartext übertragen. Wer den Verkehr mitlesen oder manipulieren kann, kann diese Informationen auslesen oder Antworten verändern. Eine erfolgreiche Anmeldung allein verschlüsselt die Verbindung nicht.

Für einen realen Dienst ist TLS mit korrekter Zertifikats- und Hostnamenprüfung notwendig: entweder implizites TLS (POP3S, üblicherweise Port 995) oder eine verpflichtende, gegen Downgrade geschützte TLS-Aufrüstung mittels `STLS`. Bloß eine andere Portnummer zu verwenden verschlüsselt nichts. Ein lokaler Tunnel kann den Transport zu einem entfernten TLS-Server übernehmen; dabei muss auch die entfernte Gegenstelle geprüft werden.

Das historische APOP-Verfahren aus RFC 1939 vermeidet die direkte Übertragung des Passworts, verschlüsselt jedoch **nicht** die Nachrichten und verwendet MD5. Es ersetzt daher keine zeitgemäße TLS-Absicherung. POP3 und IMAP sind beide ohne geschützten Transport kein geeigneter Schutz vertraulicher E-Mails.

**Für diese Übung:** ausschließlich künstliche Konten, Serverbindung standardmäßig `127.0.0.1`, kein öffentlicher Listener und keine produktiven Passwörter. Loopback reduziert die Exposition, bietet aber selbst keine Verschlüsselung und schützt nicht vor privilegiertem lokalem Mitschneiden. Unser Server bietet weder STLS noch SASL/APOP an und behauptet diese Fähigkeiten auch nicht in CAPA.

## 3. Single-Line und Multi-Line

### Single-Line

Eine vollständige Antwort besteht aus **einer** CRLF-beendeten Statuszeile:

```text
C: STAT
S: +OK 4 687
C: LIST 2
S: +OK 2 185
C: RETR 99
S: -ERR invalid arguments or no such message
```

Die Größen stammen für das Beispiel aus den bereitgestellten vier Testnachrichten. `USER`, `PASS`, `STAT`, `LIST n`, `UIDL n`, `DELE`, `NOOP`, `RSET` und `QUIT` antworten in einer Zeile. **Eine negative Antwort ist auch bei einem sonst mehrzeiligen Befehl nur einzeilig**: Nach `-ERR` darf der Client nicht noch auf die Punkt-Endmarke warten.

### Multi-Line

Auf eine positive Statuszeile folgen Datenzeilen; eine Zeile mit **nur einem Punkt** beendet die Antwort:

```text
C: LIST
S: +OK listing follows
S: 1 184
S: 2 185
S: 3 154
S: 4 164
S: .
```

`LIST` ohne Nummer, `UIDL` ohne Nummer, `RETR`, `TOP` und `CAPA` liefern bei Erfolg Multi-Line-Antworten. Auch ein leeres Postfach liefert bei `LIST` eine positive Statuszeile und unmittelbar danach die Punkt-Endmarke.

**Dot-Stuffing:** Damit eine echte Datenzeile `.` nicht mit dem Ende verwechselt wird, stellt der Server bei jeder mit Punkt beginnenden Datenzeile einen zusätzlichen Punkt voran:

| Tatsächliche Datenzeile | Übertragene Datenzeile |
|---|---|
| `.erste` | `..erste` |
| `.` | `..` |
| `..dritte` | `...dritte` |

Der Client entfernt genau den zusätzlich eingefügten Punkt. Der Terminator gehört nicht zur Nachricht. LIST/STAT-Größen zählen die Bytes der Nachricht einschließlich ihrer CRLF-Zeilenenden, aber **nicht** Statuszeile, zusätzliche Stuffing-Punkte oder Endmarke. Bei UTF-8 muss man Bytes, nicht Unicode-Zeichen zählen.

## 4. Vergleich mit IMAP

| Aspekt | POP3 (RFC 1939/2449) | IMAP4rev2 (RFC 9051) |
|---|---|---|
| Grundmodell | Einfacher Maildrop, Nachrichten herunterladen und optional löschen | Serverseitige Ordner, Nachrichtenattribute/Flags, Suche, selektiver Abruf und Synchronisierung |
| Befehlszuordnung | Antworten entsprechen der Reihenfolge der Befehle | Befehle tragen Tags wie `A001`; abschließende Antwort enthält dasselbe Tag |
| Status | `+OK` oder `-ERR` | Unter anderem getaggte `OK`, `NO`, `BAD`; ungetaggte Antworten beginnen mit `*`, Fortsetzungsanforderungen mit `+` |
| Mehrzeilige Daten | Nach `+OK` Daten bis zur Punktzeile, Dot-Stuffing | Strukturierte Antworten; Nachrichtendaten können Literale mit expliziter Oktettzahl enthalten, keine POP3-Punkt-Endmarke |
| Serverereignisse | Keine IMAP-artigen spontanen Mailbox-Aktualisierungen | Ungetaggte Daten können auch unabhängig von einem aktuellen Befehl eintreffen |
| Mehrere Geräte | UIDL hilft gegen erneutes Herunterladen, aber keine gemeinsame Ordner-/Gelesen-Flag-Synchronisierung | Für Zugriff und Abgleich des serverseitigen Bestands ausgelegt |

Schematisches IMAP-Beispiel (nicht auf unserem POP3-Server auszuführen):

```text
C: A001 SELECT INBOX
S: * 4 EXISTS
S: A001 OK SELECT completed
```

Die erste Serverzeile ist eine ungetaggte Datenantwort; die letzte schließt **den Befehl A001** ab. Bei FETCH-Literalen bestimmt eine angegebene Bytezahl die Länge des Inhalts. IMAP ist somit nicht einfach „POP3, aber immer mehrzeilig“: Tags, ungetaggte Daten, Fortsetzungen und Literale bilden ein anderes Antwortmodell.

## Quellen

Abgerufen am 2026-10-19:

- [RFC 1939 – POP3](https://www.rfc-editor.org/rfc/rfc1939.html), §§ 1–7: Zweck, Ablauf, Zustände und Befehle; § 3: CRLF, Antwortformen und Stuffing; § 11: Nachrichtengrößen; § 13: Klartext-Risiken.
- [RFC 2449 – POP3 Extension Mechanism](https://www.rfc-editor.org/rfc/rfc2449.txt), §§ 3–5: Grammatik, 255-Oktett-Befehle und CAPA; §§ 6.1, 6.2, 6.7, 6.8: TOP, USER, EXPIRE und UIDL; § 8.1.2: IN-USE.
- [RFC 9051 – IMAP4rev2](https://www.rfc-editor.org/rfc/rfc9051.html), Abstract und §§ 2.2, 2.3, 4.3, 7: Mailbox-Modell, Tags, ungetaggte Antworten, Literale und Serverantworten.
- Ergänzende Transportreferenz: [RFC 8314 § 3.1](https://www.rfc-editor.org/rfc/rfc8314.html#section-3.1) (implizites TLS/POP3S), [RFC 2595](https://www.rfc-editor.org/rfc/rfc2595.html) (STLS; nicht in der eigenen Implementierung enthalten).
