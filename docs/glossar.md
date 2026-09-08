---
title: Glossar
description: Die wichtigsten Begriffe aus OParl, Kommunalpolitik und mandari kurz erklärt.
---

# Glossar

Begriffe aus dem OParl-Standard, aus der kommunalpolitischen Praxis und aus mandari selbst. OParl-Objekte stehen in ihrer englischen Originalbezeichnung, so wie sie in den Schnittstellen erscheinen.

## OParl-Objekte

| Begriff | Deutsche Bezeichnung | Bedeutung |
|---------|---------------------|-----------|
| `System` | System | Einstiegspunkt einer OParl-Schnittstelle. Von hier aus sind alle weiteren Objekte verlinkt. |
| `Body` | Kommune, Körperschaft | Stadt, Kreis, Gemeinde oder eine andere Körperschaft mit eigenen Gremien. |
| `Organization` | Gremium | Rat, Ausschuss, Beirat, Kommission oder Fraktion. |
| `Person` | Person | Ratsmitglied, sachkundige Bürgerin, Verwaltungsmitarbeiter. |
| `Membership` | Mitgliedschaft | Zugehörigkeit einer Person zu einem Gremium, mit Rolle, Stimmrecht und Zeitraum. |
| `Meeting` | Sitzung | Sitzung eines Gremiums mit Tagesordnung, Ort und Dokumenten. |
| `AgendaItem` | Tagesordnungspunkt (TOP) | Einzelner Punkt einer Sitzung, öffentlich oder nicht-öffentlich, mit Ergebnis. |
| `Paper` | Vorlage, Drucksache | Beschlussvorlage, Antrag, Anfrage, Mitteilung oder Bericht mit Dateien. |
| `Consultation` | Beratung | Verbindet eine Vorlage mit einem Tagesordnungspunkt einer Sitzung. Aus mehreren Beratungen entsteht die Beratungsfolge. |
| `File` | Datei | Dokument zu einer Vorlage oder Sitzung, in der Praxis fast immer PDF. |
| `Location` | Ort | Sitzungsort oder Ortsbezug einer Vorlage, mit Adresse und Koordinaten. |
| `LegislativeTerm` | Wahlperiode | Zeitraum einer Legislatur. |

## Kommunalpolitik

**Beratungsfolge**
:   Der Weg einer Vorlage durch die Gremien, etwa Vorberatung im Fachausschuss und Entscheidung im Rat. In OParl ist jede Station eine `Consultation`; die entscheidende Station trägt `authoritative: true`.

**Beschlusskontrolle**
:   Die Verwaltung dokumentiert nach der Beschlussfassung, wer für die Umsetzung zuständig ist, bis wann sie erfolgen soll und wie weit sie ist. In mandari Session als Beschlussregister umgesetzt, in Insight öffentlich einsehbar, wenn die Kommune das freigibt.

**Ladungsfrist**
:   Frist, mit der die Einladung zu einer Sitzung spätestens verschickt sein muss. Sie ergibt sich aus Gemeindeordnung und Geschäftsordnung. mandari Session erinnert an ablaufende Ladungsfristen.

**Nicht-öffentlicher Teil (NÖ)**
:   Teil einer Sitzung, der aus rechtlichen Gründen nicht öffentlich ist, etwa Personal- oder Grundstücksangelegenheiten. In mandari verlässt nichts aus dem NÖ-Teil den geschützten Bereich.

**Sitzungsgeld**
:   Aufwandsentschädigung für Mandatsträgerinnen und Mandatsträger je besuchter Sitzung. mandari Session rechnet sie ab, Bankdaten sind dabei verschlüsselt und zugriffsbeschränkt.

## mandari-Begriffe

**Ingestor**
:   Der Hintergrunddienst, der Quellen synchronisiert und die Daten in Insight bereitstellt. Er erkennt Änderungen, respektiert robots.txt und drosselt sich bei Störungen selbst.

**Quelle**
:   Eine angebundene Datenquelle, etwa die OParl-Schnittstelle einer Kommune, ein SessionNet-Portal oder die OParl-API eines Session-Mandanten.

**Mandant**
:   Eine Kommune in mandari Session mit eigenen Nutzerinnen, Rollen, Einstellungen und Verschlüsselungsschlüssel.

**Organisation**
:   Eine Fraktion oder politische Gruppe in mandari Work mit eigenen Mitgliedern, Rollen und Berechtigungen.

**Tombstone**
:   Der Platzhalter eines gelöschten oder entöffentlichten Objekts. Er enthält nur noch Kennung, Typ und Zeitstempel, damit inkrementell synchronisierende Clients die Löschung zuverlässig mitbekommen. Vorgesehen im OParl-Standard, konsequent umgesetzt in allen mandari-Schnittstellen.

**Quellen-Schonung**
:   Mechanismus, der eine Quelle nach mehreren Fehlversuchen in Folge in Ruhe lässt: Der Ingestor verlängert die Abstände zwischen seinen Versuchen, Dokument-Cache und Vorschau pausieren für diese Quelle.

**Dokument-Cache**
:   Lokale Kopie aller Dateien angebundener Quellen, damit Vorschau und Download auch dann funktionieren, wenn das kommunale System gerade nicht erreichbar ist.

**Vendor-Attribute**
:   Ergänzende Felder in OParl-Antworten, die nicht Teil des Standards sind. Bei mandari tragen sie das Präfix `mandari:` und können von Standard-Clients ignoriert werden.
