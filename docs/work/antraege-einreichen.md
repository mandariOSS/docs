---
title: Anträge digital einreichen
description: Anträge aus mandari Work direkt beim Ratsinformationssystem der Verwaltung einreichen, mit Eingangsnummer, Statusverfolgung und Beratungsterminen.
---

# Anträge digital einreichen

Fraktionen im Work-Portal reichen Anträge direkt beim mandari Session der eigenen Verwaltung ein und sehen ohne Rückfrage Eingangsnummer, Bearbeitungsstatus und Beratungstermine. Voraussetzung ist, dass die Verwaltung mandari Session als Ratsinformationssystem nutzt.

## Einmalig: Verbindung einrichten

1. **Verwaltung**: Legt unter *Session → Einstellungen → Einreichungs-Zugänge* einen Zugang für die Fraktion an. Der Token wird genau einmal angezeigt und muss sicher übergeben werden. Details für die Verwaltung unter [Einreichungs-Zugänge](../session/einreichungs-zugaenge.md).
2. **Fraktion**: Fügt den Token unter *Organisationseinstellungen → Verwaltung* ein. Er wird sofort geprüft. Dafür ist die Berechtigung zur Verwaltung der Organisation nötig.

Die Verbindung bleibt bestehen, bis die Verwaltung den Zugang zurückzieht oder ein Ablaufdatum erreicht ist.

## Antrag einreichen

Im Dokument-Editor erscheint für Mitglieder mit der Berechtigung „Bei Verwaltung einreichen“ die gleichnamige Aktion, sowohl in der Kopfzeile als auch in der Sidebar „Verwaltung“.

Die Einreichungsseite zeigt die Dokumentvorschau und ein vorbelegtes Formular:

| Feld | Vorbelegung |
|------|-------------|
| Titel | Titel des Dokuments |
| Antragsart | aus Dokumenttyp und Titel geraten |
| Beschlussvorschlag, Begründung, finanzielle Auswirkungen | aus den gleichnamigen Überschriften des Dokuments herausgelöst |
| Zielgremium | Auswahl aus den Gremien der Verwaltung |
| Mitunterzeichnende, Dringlichkeit, Wunschtermin | frei |

Nach der Bestätigung entsteht bei der Verwaltung ein Antrag mit Eingangsnummer im Format `A/<Jahr>/<Nr>`. Das Dokument wechselt in Work auf den Status „Eingereicht“ und ist dauerhaft mit dem Antrag verknüpft.

### Voraussetzungen

- Verbindung vorhanden, Token gültig und nicht zurückgezogen, Verwaltung aktiv
- Der Dokumenttyp ist als einreichbar konfiguriert
- Das Dokument ist im Status „Freigegeben“, oder die einreichende Person besitzt die Freigabe-Berechtigung
- Für dieses Dokument gibt es noch keine Einreichung

## Rückmeldung der Verwaltung

Statuswechsel bei der Verwaltung laufen automatisch ins Work-Dokument. Autorin und Federführung werden benachrichtigt, in der Anwendung und je nach Einstellung per E-Mail.

| Status bei der Verwaltung | Status in Work | Benachrichtigung |
|---------------------------|----------------|------------------|
| eingegangen, in Prüfung, angenommen, in Vorlage umgewandelt | Bei Verwaltung | ja, inklusive Bearbeitungsnotiz |
| Beratung mit Sitzung angelegt | Auf Tagesordnung | ja, mit Gremium und Termin |
| abgelehnt | Abgelehnt | ja |
| zurückgezogen | Freigegeben | ja |

Die Statusseite in Work zeigt zusätzlich die Beratungsfolge der Vorlagen, die aus dem Antrag entstanden sind.

## Getrennte Installationen

Betreiben Fraktion und Verwaltung getrennte mandari-Installationen, steht der HTTP-Endpunkt `/api/v1/session/<kommune>/applications/submit/` der [Session-API v1](../session/api-v1.md) mit Bearer-Token zur Verfügung (der frühere Pfad `/session/<kommune>/api/session/applications/submit/` entfällt am 31. Mai 2027). Der Token ist derselbe wie oben. Innerhalb einer Installation läuft die Einreichung direkt, ohne HTTP-Umweg.
