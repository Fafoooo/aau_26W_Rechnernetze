# Ü 2.8 – Streaming gespeicherter Videos

**Aufgabe:** Streaming gespeicherter Videos erklären, heute bekannte Angebote nennen und deren Funktionsweise recherchieren.

## 1. Was bedeutet Streaming gespeicherter Videos?

Bei **Video-on-Demand (VoD)** ist der Film bereits produziert und als Mediendatei beziehungsweise in mehreren Mediensegmenten gespeichert. Der Nutzer bestimmt den Startzeitpunkt und kann üblicherweise pausieren und springen. Beim **Streaming** beginnt die Wiedergabe, sobald genügend Daten gepuffert sind, während weitere Daten noch übertragen werden. Man muss nicht zuerst den vollständigen Film herunterladen. [Apple: HTTP Live Streaming für Live- und On-Demand-Inhalte](https://developer.apple.com/streaming/), [RFC 8216, §§ 2 und 6.2.1](https://www.rfc-editor.org/rfc/rfc8216#section-2)

Der Begriff bedeutet **nicht**, dass keine Daten heruntergeladen oder zwischengespeichert werden: Der Player lädt Daten in einen Puffer beziehungsweise Cache. Der Unterschied zum vollständigen Download liegt im Beginn der Wiedergabe und der laufenden Beschaffung weiterer Abschnitte. Ein Offline-Download wird dagegen vorab für eine spätere Wiedergabe ohne Netzverbindung gespeichert. **Live-Streaming** unterscheidet sich dadurch, dass neue Inhalte während des Ereignisses entstehen; Pausieren oder Zurückspulen ist dort nur im angebotenen Zeitfenster möglich. [RFC 8216, §§ 2 und 6](https://www.rfc-editor.org/rfc/rfc8216#section-2), [Netflix: Streaming und Offline-Download](https://www.netflix.com/at/)

## 2. Beispiele tatsächlich angebotener Dienste

Bekannte Beispiele, **ohne Rangliste oder Behauptung gemessener Marktanteile**:

- **YouTube** (`youtube.com`): gespeicherte Nutzervideos und weitere Videoangebote. Die offizielle Hilfe beschreibt die automatische Anpassung der Wiedergabequalität an Verbindung, Bildschirm, Originalvideo und Browser. [YouTube-Hilfe](https://support.google.com/youtube/answer/91449?hl=de)
- **Netflix** (`netflix.com`): Filme und Serien auf Abruf; Wiedergabe in Browsern und Apps. Die offizielle Anbieterseite beschreibt auch optionale Offline-Downloads. [Netflix-Angebotsbeschreibung](https://www.netflix.com/at/)
- **Disney+** (`disneyplus.com`): Filme und Serien verschiedener Programmmarken auf Abruf. [Offizielle Angebotsseite](https://www.disneyplus.com/de-at)
- **ORF ON** (`on.orf.at`): unter anderem gespeicherte Sendungen, Filme, Serien und ein Archiv, neben gesonderten Livestreams. [ORF ON](https://on.orf.at/)

**Recherchegrenze:** Anbieter-Webseiten können auf den Standort des abrufenden Systems reagieren; Netflix und Disney+ lieferten beim Rechercheabruf teilweise US-Inhalte trotz österreichischem URL-Pfad. Deshalb werden daraus **keine österreichischen Abopreise oder spezifischen österreichischen Katalogzusagen** abgeleitet. Die Beispiele belegen das jeweilige Streamingangebot, nicht eine identische regionale Verfügbarkeit aller Titel. Abruf: **19.10.2026**.

## 3. Typischer technischer Ablauf eines adaptiven VoD-Streams

### Schritt 1 – Aufbereitung vor der Wiedergabe

Der Anbieter komprimiert Bild und Ton und stellt mehrere geeignete **Repräsentationen** bereit, etwa unterschiedliche Auflösungen, Bitraten und Codecs. Der Inhalt wird in zeitlich zusammenpassende Segmente aufgeteilt beziehungsweise über adressierbare Bytebereiche zugänglich gemacht. **Codec**, **Container** und **Streamingprotokoll** haben unterschiedliche Aufgaben: Der Codec komprimiert, der Container ordnet Bild/Ton/Metadaten, das Streamingprotokoll beschreibt die Beschaffung und Auswahl der Daten. [RFC 8216, §§ 2–4](https://www.rfc-editor.org/rfc/rfc8216#section-2), [DASH Industry Forum: Interoperabilität](https://dashif.org/guidelines/iop-v5/)

### Schritt 2 – Auswahl, Berechtigung und Wiedergabebeschreibung

Nach der Titelauswahl erhält der Player eine **Wiedergabebeschreibung**, häufig ein Manifest beziehungsweise eine Playlist. Sie enthält zum Beispiel verfügbare Varianten, Segmentadressen, Codecangaben, Sprachen und Zeitinformationen. Falls das Angebot Zugriffsschutz verlangt, muss die Anwendung den Nutzer beziehungsweise die Wiedergabeberechtigung prüfen. Bei verschlüsselten kommerziellen Inhalten kann zusätzlich eine DRM-Lizenz benötigt werden; das ist nicht bei jedem Videoangebot vorgeschrieben. [RFC 8216, §§ 4.3.4 und 5](https://www.rfc-editor.org/rfc/rfc8216#section-4.3.4), [Apple: FairPlay Streaming](https://developer.apple.com/streaming/fps/)

### Schritt 3 – Medienabruf über HTTP(S)

Der Player fordert die benötigten Segmente oder Bytebereiche von einem HTTP-Server an. Dabei kann normales HTTPS eingesetzt werden: HTTP/1.1 oder HTTP/2 über TCP/TLS, bei Unterstützung auch HTTP/3 über QUIC/UDP. **Streaming gespeicherter Videos ist daher nicht automatisch UDP-/RTP-Streaming.** Auch ein zuverlässiger Transport kann für VoD gut geeignet sein, weil ein Puffer kurze Übertragungsverzögerungen überbrückt. [RFC 8216, § 6.3.3](https://www.rfc-editor.org/rfc/rfc8216#section-6.3.3), [RFC 9113, § 2](https://www.rfc-editor.org/rfc/rfc9113#section-2), [RFC 9114, §§ 1–2](https://www.rfc-editor.org/rfc/rfc9114#section-1)

### Schritt 4 – Puffern und Decodieren

Der Player sammelt zunächst einen gewissen Vorrat an abspielbaren Medien und beginnt dann mit der Decodierung. Während er einen Abschnitt zeigt, lädt er weitere. Ein größerer Puffer toleriert kurzfristige Netzschwankungen, erhöht aber Anlaufzeit und gegebenenfalls unnötig geladene Daten. Sinkt der Puffer auf null, entsteht eine sichtbare Nachladepause (**Rebuffering**). [RFC 8216, §§ 6.3.3 und 6.3.4](https://www.rfc-editor.org/rfc/rfc8216#section-6.3.3)

### Schritt 5 – Adaptive Bitrate (ABR)

Der Player wählt laufend eine passende angebotene Qualitätsstufe. Dazu sind unter anderem der beobachtete Durchsatz, der Pufferstand, verfügbare Codecs und die Anzeigeeigenschaften nützlich. Sinkt die verfügbare Leistung, kann er die nächsten Abschnitte mit geringerer Bitrate laden; bei besseren Bedingungen kann er wieder eine höhere Stufe wählen. Das verändert nicht nachträglich schon gezeigte Bilder. Der genaue Auswahlalgorithmus ist **nicht für alle Anbieter gleich**. YouTube dokumentiert die situationsabhängige Qualitätsanpassung, Apple die Anpassung von HLS an die Netzbedingungen. [YouTube-Hilfe](https://support.google.com/youtube/answer/91449?hl=de), [Apple HLS](https://developer.apple.com/streaming/)

### Schritt 6 – Springen und Beenden

Beim Springen im Film ermittelt der Player die Segmente für die neue Zeitposition und füllt den Puffer dafür neu. Für VoD kann eine vollständige Liste der Segmente beziehungsweise ein zugänglicher Zeitindex vorliegen. Beim Beenden werden nicht mehr benötigte Abrufe gestoppt; es muss nicht der Rest des Films geladen werden. [RFC 8216, §§ 4.3.3.5, 6.2.1 und 6.3.3](https://www.rfc-editor.org/rfc/rfc8216#section-6.2.1)

## 4. HLS und MPEG-DASH

- **HTTP Live Streaming (HLS)** verwendet M3U8-Playlists. Eine Master-Playlist kann mehrere Varianten beschreiben; Media-Playlists verweisen auf die Mediensegmente. Trotz des Namens unterstützt HLS **auch gespeicherte Videos**. [RFC 8216, §§ 2 und 4](https://www.rfc-editor.org/rfc/rfc8216#section-2), [Apple HLS](https://developer.apple.com/streaming/)
- **MPEG-DASH** verwendet eine Media Presentation Description (**MPD**) und beschreibt ebenfalls Repräsentationen und deren Mediensegmente für adaptives Streaming über HTTP. Die DASH-IF-Dokumente enthalten Implementierungs- und Interoperabilitätsrichtlinien. [DASH-IF IOP](https://dashif.org/guidelines/iop-v5/)

Das sind zwei wichtige **Technikfamilien**, aber kein Beleg dafür, dass jeder genannte Anbieter auf jedem Endgerät immer exakt dasselbe Verfahren verwendet. Eine solche Aussage würde eine Untersuchung des konkreten Players beziehungsweise zusätzliche aktuelle Herstellerangaben erfordern.

## 5. Tatsächlich recherchiertes Anbieterbeispiel: Netflix Open Connect

Netflix betreibt mit **Open Connect** ein eigenes Content Delivery Network. Netflix arbeitet mit Providern zusammen und bietet qualifizierten Partnern **Open Connect Appliances (OCA)** zur Einbettung in deren Netze an. Zusätzlich bestehen Peering-Verbindungen. Dadurch können große Teile des Videoverkehrs aus einem näheren Cache statt über entfernte Transitverbindungen geliefert werden. Das entlastet überregionale Verbindungen und kann Verzögerungen sowie Kosten reduzieren. [Offizielle technische Beschreibung von Open Connect](https://openconnect.netflix.com/en/)

Wichtig ist die Trennung: Das CDN bestimmt, **woher** Daten effizient kommen. Adaptive Wiedergabe bestimmt, **welche angebotene Qualitätsstufe** der Player abruft. Verschlüsselung/DRM bestimmen, **wer die geschützten Inhalte nutzen darf**. Das sind zusammenarbeitende, aber unterschiedliche Mechanismen.

## 6. Leistungsanforderungen richtig interpretieren

Für dauerhaft störungsarme Wiedergabe muss der langfristig nutzbare Durchsatz zur ausgewählten Medienbitrate passen; kurzfristige Einbrüche können durch den Puffer aufgefangen werden. Eine beliebig große beworbene Anschlussrate garantiert dagegen weder gutes WLAN noch geringe Verluste oder geeignete Geräte. YouTube nennt als **ungefähre Empfehlungen**, nicht als eigene Messung, beispielsweise **5 Mbit/s für HD 1080p** und **20 Mbit/s für 4K UHD**. Diese Werte dürfen nicht pauschal auf alle Anbieter, Codecs und Filme übertragen werden. [YouTube: Systemanforderungen](https://support.google.com/youtube/answer/78358?hl=en)

**Fazit:** Modernes VoD kombiniert vorbereitete Medien, Manifest/Playlists, laufenden Segmentabruf, Pufferung, adaptive Qualitätswahl und häufig ein CDN. Die vollständige Datei muss vor Wiedergabebeginn nicht am Endgerät vorliegen.

**Quellenstand:** Abruf am 19.10.2026. Die allgemeine Funktionsbeschreibung ist von ausdrücklich belegten Anbieterinformationen getrennt. Keine eigenen Streamingmessungen oder erfundenen Paketaufzeichnungen.

**KI-Kennzeichnung:** Erstellt mit **Hermes Agent**, Modell **OpenAI gpt-6.1-sol**, am **2026-10-19**. Tatsächlicher Auftrag, sinngemäß: „Erkläre Ü 2.8 auf Deutsch: Streaming gespeicherter Videos, bekannte heutige Angebote und recherchierte Funktionsweise mit Quellen; unterscheide allgemeine Technik von belegten Anbieterangaben.“
