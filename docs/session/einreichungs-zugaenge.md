---
title: Einreichungs-Zugänge für Fraktionen
description: Tokens in mandari Session anlegen, mit denen Fraktionen Anträge digital einreichen. Sicherheit, Ablauf, Rückzug und der Weg der Anträge in die Verwaltung.
---

# Einreichungs-Zugänge für Fraktionen

Fraktionen, die mandari Work nutzen, reichen ihre Anträge direkt digital ein. Die Verwaltung erhält sie mit Eingangsnummer im Antragseingang und meldet Status und Beratungstermine automatisch zurück. Dafür legt die Verwaltung je Fraktion einen Zugang an.

## Zugang anlegen

1. *Einstellungen → Einreichungs-Zugänge → Neuer Zugang*
2. Fraktion benennen, optional ein **Ablaufdatum** setzen
3. Speichern. Der Token (64 Zeichen) wird **genau einmal** angezeigt.
4. Token sicher an die Fraktion übergeben, etwa persönlich oder über einen verschlüsselten Kanal. Die Fraktion trägt ihn in Work unter *Organisationseinstellungen → Verwaltung* ein ([Anleitung für Fraktionen](../work/antraege-einreichen.md)).

Gespeichert wird nur ein Hash des Tokens. Geht er verloren, wird ein neuer Zugang angelegt und der alte zurückgezogen.

## Zugang zurückziehen

In der Liste der Zugänge kann jeder Token jederzeit zurückgezogen werden. Ab dann sind keine Einreichungen mehr möglich, bestehende Anträge bleiben unberührt. Abgelaufene Tokens werden automatisch ungültig.

## Was bei einer Einreichung passiert

- Es entsteht ein Antrag mit Eingangsnummer `A/<Jahr>/<Nr>`, Antragsart, Zielgremium, Beschlussvorschlag, Begründung, finanziellen Auswirkungen, Mitunterzeichnenden, Dringlichkeit und Wunschtermin.
- Der Antrag durchläuft den normalen Prüf-Workflow: eingegangen, in Prüfung, angenommen oder abgelehnt, in Vorlage umgewandelt.
- Jeder Statuswechsel und jede angelegte Beratung mit Sitzung meldet sich automatisch an die Fraktion zurück, inklusive Bearbeitungsnotiz.

## Berechtigungen

Zugänge verwalten dürfen Nutzerinnen und Nutzer mit dem Recht zur Verwaltung der Einstellungen. Anlegen und Zurückziehen werden im Audit-Log protokolliert.

## Getrennte Installationen

Betreibt die Fraktion eine eigene mandari-Installation, nutzt sie denselben Token über den HTTP-Endpunkt `/api/v1/session/<kommune>/applications/submit/` der [Session-API v1](api-v1.md) mit Bearer-Authentifizierung. Den Rückmeldestand eines eingereichten Antrags liefert `/api/v1/session/<kommune>/applications/<id>/feedback/`. Der frühere Pfad `/session/<kommune>/api/session/applications/submit/` ist abgekündigt und entfällt am 31. Mai 2027.
