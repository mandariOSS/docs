---
title: Ratsfragen
description: Öffentliche Fragen an Ratsmitglieder stellen und beantworten. Ablauf, Moderation und Konfiguration für Betreiber.
---

# Ratsfragen

Bürgerinnen und Bürger stellen Mandatsträgerinnen und Mandatsträgern öffentliche Fragen. Fragen und Antworten sind für alle sichtbar, vergleichbar mit bekannten Plattformen für Abgeordnetenfragen, hier auf kommunaler Ebene. Eigener Reiter **Ratsfragen** im Portal unter `/insight/fragen/`.

## Ablauf

1. **Frage stellen**: Unter `/insight/fragen/stellen/` eine Person auswählen und das Formular mit Themenbereich ausfüllen.
2. **E-Mail bestätigen**: Die Frage wird erst nach Klick auf den Bestätigungslink weiterverarbeitet.
3. **Moderation**: Das Moderationsteam prüft die Frage. Es wird bei jeder bestätigten Frage und jeder eingereichten Antwort per E-Mail informiert.
4. **Freischaltung**: Das Ratsmitglied erhält einen persönlichen Antwort-Link (ohne Anmeldung), die Fragestellerin den öffentlichen Link zur Frage.
5. **Antwort**: Die Antwort geht ebenfalls durch die Moderation und wird dann veröffentlicht. Die Fragestellerin wird informiert.

Unbeantwortete Fragen werden nach 14 Tagen und danach alle 14 Tage per E-Mail in Erinnerung gerufen.

## Wer gefragt werden kann

Gefragt werden können Personen mit aktiver Mitgliedschaft in einem Hauptorgan (Rat, Stadtrat, Kreistag, Regionalrat und vergleichbare Gremien) oder in einer Fraktion. Verwaltungs- und Protokollrollen sind ausgenommen. Die Erkennung funktioniert unabhängig von den Rollenbezeichnungen des jeweiligen Ratsinformationssystems.

## Personenfotos

Fotos von Mandatsträgerinnen und Mandatsträgern werden aus dem Ratsinformationssystem geladen und lokal zwischengespeichert (maximal 400 Pixel, JPEG). So gibt es keine kaputten Bilder bei Umzügen oder Bot-Schutz des Quellsystems, und wer kein Foto hat, bekommt einen klaren Initialen-Platzhalter.

## Für Betreiber

| Variable | Bedeutung |
|----------|-----------|
| `INSIGHT_MODERATION_EMAILS` | Kommagetrennte Empfänger der Moderations-Hinweise. Leer: alle aktiven Superuser mit E-Mail-Adresse. |
| `SITE_URL` | Basis-URL für alle Links in E-Mails |

Die Moderation findet im Admin unter *Insight → Öffentliche Fragen* statt.

**Personenfotos je Kommune** konfigurierst du im Admin unter *Kommunen → Personenfotos*: ein URL-Muster mit `{id}` und ein regulärer Ausdruck mit einer Gruppe, der die Kennung aus der OParl-ID der Person extrahiert. Für bekannte Systeme greifen Voreinstellungen automatisch. Manuell hochgeladene Fotos werden nie überschrieben.

Die zugehörigen regelmäßigen Aufgaben (Erinnerungen, Foto-Aktualisierung) stehen unter [Regelmäßige Aufgaben](../betrieb/cron.md).
