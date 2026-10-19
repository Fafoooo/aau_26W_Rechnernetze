# Erklärung Blatt 03 – Lernpfad

## Was gehört zusammen?

1. Lies die Angabe und [Ü3.1](ue3.1/antwort.md): POP3 ist ein textbasiertes
   Abrufprotokoll, nicht das Protokoll zum Versenden von Mails.
2. Arbeite [POP3: jede Codezeile](erklaerung_pop3.md) durch. Dort sind
   `ue3.2/pop3_client.py`, `ue3.3/pop3_server.py` und beide Testdateien vollständig
   erklärt. Der Client arbeitet mit `socket`, nicht mit einer fertigen POP3-Bibliothek.
   `poplib` ist nur die unabhängige Gegenprobe im Test.
3. Vergleiche [echte Thunderbird-Inbox und geöffnete Mail](ue3.3/gui_testbericht.md).
   [GUI-Test: jede Codezeile](ue3.3/erklaerung_gui.md) erklärt die zusätzliche
   Automatisierung: frisches Profil, synthetisches Konto, Abruf, sichtbare Inhalte,
   Screenshots, kontrolliertes Beenden.
4. Arbeite [HTTP: jede Codezeile](erklaerung_http.md) durch. Dort sind
   `ue3.4/server.py`, `ue3.5/server.py` und beide HTTP-Testdateien erklärt.
5. Lies [Browser-/Referenzintegration](erklaerung_integration.md) und führe die
   [Unittests](README.md#unittests) selbst aus.

## Die grundlegenden Ideen

- **TCP-Stream:** `recv` liefert beliebige Byte-Stücke. Eine Protokollzeile kann
  über mehrere Aufrufe verteilt sein; mehrere Zeilen können gemeinsam eintreffen.
  Der Code puffert bis zur eigenen Protokollgrenze.
- **CRLF:** zwei Bytes, Wagenrücklauf `\r` und Zeilenumbruch `\n`. Nicht mit der
  Plattform-Zeilenende-Konvention oder einer TCP-Paketgrenze verwechseln.
- **Zustandsautomat:** POP3 erlaubt vor der Anmeldung andere Befehle als danach.
  Die Reihenfolge gehört zum Protokoll, nicht nur das richtige Passwort.
- **Framing:** Wo endet eine Antwort? POP3 nutzt bei mehrzeiligen Antworten eine
  alleinstehende Punktzeile und Dot-Stuffing. HTTP/1.0 nutzt hier `Content-Length`.
  Ohne diese Grenzen lassen sich persistente Verbindungen nicht zuverlässig lesen.
- **Thread:** eigener Ausführungsablauf im selben Prozess. Ein blockierender Client
  soll andere Nutzer nicht anhalten. Gemeinsame Daten brauchen Locks oder Queues.
- **Mailbox-Lock:** verschiedene Benutzer dürfen gleichzeitig arbeiten, dieselbe
  Mailbox darf nicht durch zwei konkurrierende POP3-Transaktionen verändert werden.
- **Queue-Logger:** Worker produzieren Einträge, genau ein Logger-Thread gibt sie
  gesammelt alle fünf Sekunden aus. Beim Stoppen werden zuerst alle Produzenten
  beendet, dann wird der Rest ausgegeben.
- **Protokolltreue versus Browser-Kompatibilität:** Ein korrekter HTTP/0.9-Server
  wird nicht automatisch mit modernen Browsern kompatibel. Der Browser sendet
  selbst bereits einen HTTP/1.x-Request. Ü3.5 liefert den passenden Ausbau.

## Was Fabio live ändern und erklären können sollte

1. Client-Port ändern: an beiden Enden denselben Wert verwenden.
2. Eine andere Mail abrufen: `--message 2`, LIST-Nummer nicht mit einer stabilen UID verwechseln.
3. Dot-Stuffing vorführen: eine Testnachricht mit einer Zeile `.` hinzufügen,
   Wire-Daten und zurückgelesenen Text vergleichen.
4. Fehlerpfad vorführen: falsches Passwort, unbekannte Mailnummer, unterbrochene Verbindung.
5. `DELE`, `RSET`, `QUIT` erklären: Markierungen sind erst beim ordentlichen QUIT verbindlich.
6. Zwei unterschiedliche Testnutzer gleichzeitig verbinden; zweiten Login derselben Mailbox ablehnen.
7. HTTP-Port und DocumentRoot ändern; fehlende Datei und `../` anfragen.
8. Den Unterschied zwischen nacktem HTTP/0.9-Dateiinhalt und HTTP/1.0-Headern zeigen.
9. Zwei HTTP/1.0-Requests auf einer Verbindung senden; Länge, Reihenfolge und Close erklären.
10. Im Logger dieselbe Client-Portnummer bei mehreren Requests und unterschiedliche
    Request-Worker zeigen. Eine neue Verbindung hat normalerweise einen neuen Clientport.

Die Testdateien zeigen für jeden dieser Punkte konkrete, ausführbare Beispiele.
Die Originaldatenbank und die Original-Webseite sind Lehrmaterial, keine selbst
implementierten Bestandteile; ihre kleine Datenstruktur wird in den Erklärungen behandelt.
Die PNG-/GIF-Dateien sind Bilder, JSON-Dateien echte Messdaten und keine Programme.

## KI-Kennzeichnung

Hermes Agent; OpenAI gpt-6.1-sol (Status: ChatGPT or Codex Subscription), 2026-10-19.
Anfrage: das Blatt mit allen Teilaufgaben lösen und jede erstellte Code-Datei so erklären,
dass Fabio Abläufe, Gründe, Fehlerfälle und Änderungen selbst nachvollziehen kann.
