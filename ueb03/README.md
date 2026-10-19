# Übungsblatt 03 – POP3 und HTTP mit Python Sockets

Alle Aufgaben Ü3.1–Ü3.5 sind bearbeitet. Der Originalauftrag steht in
[angabe_blatt03.pdf](angabe_blatt03.pdf).

## Einstieg

- [Erklärung Blatt 03](erklaerung_blatt03.md): Lernpfad, Grundlagen, zeilenweise Codeerklärungen.
- [Testprotokoll](testprotokoll_blatt03.md): echte Tests, Referenzimplementierungen und Browserbefunde.
- [Ü3.1 POP3-Theorie](ue3.1/antwort.md)
- [Ü3.2 Socket-Client](ue3.2/antwort.md)
- [Ü3.3 Thread-Server](ue3.3/antwort.md) und [Thunderbird-Nachweis](ue3.3/gui_testbericht.md)
- [Ü3.4 HTTP/0.9](ue3.4/antwort.md)
- [Ü3.5 HTTP/1.0](ue3.5/antwort.md)

## Voraussetzungen und Start

Python 3.10 oder neuer unter Linux/POSIX; getestet mit Python 3.14.7.
Die vier eigentlichen Programme und ihre Unittests verwenden nur die Standardbibliothek.
Browser-/Mail-GUI-Integrationstests benötigen zusätzliche, in ihren Berichten dokumentierte Programme.

Befehle aus dem Repository-Hauptverzeichnis, für POP3 in zwei Terminals:

```sh
python3 ueb03/ue3.3/pop3_server.py --port 11110
python3 ueb03/ue3.2/pop3_client.py --port 11110 --user alice --message 1
```

Passwort beim Client verdeckt eingeben: `secret`. Dies ist ausschließlich das öffentliche
synthetische Laborkonto der bereitgestellten Datenbank, kein echtes Mailkonto.

Der DocumentRoot ist bereits aus der Original-ZIP entpackt:

```sh
python3 ueb03/ue3.4/server.py ueb03/Angabe/document_root --port 8089
python3 ueb03/ue3.5/server.py ueb03/Angabe/document_root --port 8080
```

HTTP/0.9 lässt sich beispielsweise mit `curl --http0.9 http://127.0.0.1:8089/`
**nicht** korrekt anfordern: Diese Option erlaubt nur die alte Antwort, sendet aber
weiterhin einen modernen Request. Verwende die dokumentierten Sockettests mit
`GET /\r\n`. Moderne Browser erhalten hier erwartungsgemäß einen Verbindungsfehler.
Die HTTP/1.0-Erweiterung ist dagegen unter `http://127.0.0.1:8080/` sichtbar.

Alle Bind-Adressen sind standardmäßig Loopback. Die unverschlüsselten POP3-Lernprogramme
nicht mit echten Passwörtern oder als Internetdienst verwenden. Port 80 ist einstellbarer
Standard, die Beispiele benutzen unprivilegierte Ports.

## Unittests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.2 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.3 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.4 -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ueb03/ue3.5 -v
```

## Originaldateien und Abgabe

`Angabe/SampleDataBase.py`, `Angabe/README.md` und `Angabe/document_root.zip` sind
unverändert aus Moodle übernommen. Die README-Beispiele nennen teils `alice123`,
aber der ausführbare Originalcode und die Parameterbeschreibung definieren `secret`.
Diese Abweichung ist in den POP3-Antworten erklärt.

Es wurde nichts bei Moodle abgegeben. Da die Gruppennummer unbekannt ist, wurde
kein `ueb03-gruppeyy.zip` erzeugt. Vor einer eigenen Abgabe die tatsächliche Gruppe
prüfen, die Erklärung durcharbeiten und die Programme selbst ausführen.

## KI-Kennzeichnung

Erstellt mit Hermes Agent, Modell OpenAI gpt-6.1-sol; `hermes status` meldete
„ChatGPT or Codex Subscription“. Datum: 2026-10-19. Auftrag: Übungsblatt 03
vollständig lösen, Originalmaterial verwenden, Programme implementieren, echte Tests
und unabhängige Prüfung durchführen, Erklärung und Nachweise erstellen.
Die Code-Dateien enthalten die jeweiligen Teilaufträge. Keine studentische Eigenleistung
wird behauptet; Verantwortung und eigene Vorbereitung verbleiben beim Abgebenden.
