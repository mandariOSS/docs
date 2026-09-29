---
title: Session-API v1
description: Authentifizierte Schnittstelle des Verwaltungs-RIS je Kommune – Sitzungen, Vorlagen, Anträge, Antrag einreichen; OpenAPI, Token, Fehlerformat.
---

# Session-API v1

Die Session-API ist die erweiterte, authentifizierte Schnittstelle des Verwaltungs-RIS. Sie ergänzt die
[OParl-API je Kommune](oparl-api.md), die ausschließlich öffentliche Daten anonym liefert, um
nicht-öffentliche Daten für berechtigte Nutzer und um das Einreichen von Anträgen durch Fraktionen.

Basis-URL: `https://<host>/api/v1/session/<kommune>/` – `<kommune>` ist der Kurzname (Slug) des Mandanten.

| Methode | Pfad | Zugriff |
|---------|------|---------|
| GET | `/api/v1/session/<kommune>/` | Einstiegspunkt mit allen Links |
| GET | `/api/v1/session/<kommune>/meetings/` | Sitzungen – öffentliche für alle; nicht-öffentliche nur für angemeldete Nutzer mit Recht *Nicht-öffentliche Sitzungen anzeigen* |
| GET | `/api/v1/session/<kommune>/papers/` | Vorlagen – veröffentlichte für alle; nicht-öffentliche, Entwürfe und Vorlagen in Prüfung nur für angemeldete Nutzer mit Recht *Nicht-öffentliche Vorlagen anzeigen* |
| GET | `/api/v1/session/<kommune>/applications/` | Eingereichte Anträge – nur angemeldete Nutzer mit Recht *Anträge anzeigen* |
| POST | `/api/v1/session/<kommune>/applications/submit/` | Antrag einreichen – API-Token mit *Anträge einreichen* |
| GET | `/api/v1/session/<kommune>/applications/<id>/feedback/` | Rückmeldestand eines eingereichten Antrags – nur für das einreichende Token bzw. ein Token derselben Fraktion |
| GET | `/api/v1/session/openapi.json` | OpenAPI-3-Dokument |
| GET | `/api/v1/session/docs` | Interaktive Dokumentation (Swagger UI, ohne externe Dienste) |

Listen liefern `data` und `meta` (`total`, `limit`, `offset`, `authenticated`). `limit` ist 1 bis 200,
Standard 100.

## Authentifizierung

**API-Token** werden in Session unter *Einstellungen → API-Tokens* angelegt (siehe
[Einreichungs-Zugänge für Fraktionen](einreichungs-zugaenge.md)) und im Header mitgeschickt:

```http
Authorization: Bearer <token>
```

Ein Token gehört zu genau einer Kommune. Seine Flags heißen *Öffentliche Sitzungen lesen*, *Öffentliche
Vorlagen lesen* und *Anträge einreichen*. Ein Token liest **nur öffentliche Daten** – nicht-öffentliche
Sitzungen, Vorlagen, Texte und interne Notizen liefert die API nie an ein Token, unabhängig von den
Flags: Ein Token gehört zu keiner Person, deren Berechtigung für Nicht-Öffentliches geprüft wäre.
Optional lässt sich das Token auf IP-Adressen beschränken und mit einem Ratenlimit je Minute versehen;
bei Überschreitung antwortet die API mit `429` und `Retry-After`.

**Angemeldete Nutzer** des Session-RIS nutzen die API mit ihrer Browser-Sitzung und ihren Rollenrechten
(nur lesend); nur so sind nicht-öffentliche Daten erreichbar. Ohne Token und ohne Sitzung sind nur
öffentliche Daten sichtbar.

## Antrag einreichen

```http
POST /api/v1/session/musterstadt/applications/submit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Spielplatz Musterstraße",
  "application_type": "motion",
  "justification": "…",
  "resolution_proposal": "…",
  "submitter_name": "Fraktion Beispiel",
  "submitter_email": "fraktion@example.org",
  "target_organization_id": "…",
  "is_urgent": false
}
```

Antwort `201` mit `id`, `reference` (Aktenzeichen) und `status`. Zulässige `application_type`-Werte:
`motion`, `inquiry`, `resolution`, `urgent`, `amendment`, `other`. Das Work-Portal nutzt genau diesen
Weg, siehe [Anträge digital einreichen](../work/antraege-einreichen.md).

## Fehlerformat

Fehler kommen als `application/problem+json` nach [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457):

```json
{
  "type": "https://docs.mandari.de/api/probleme/keine-berechtigung",
  "title": "Keine Berechtigung",
  "status": 403,
  "detail": "Dieses Token darf keine Anträge einreichen.",
  "instance": "/api/v1/session/musterstadt/applications/submit/",
  "request_id": "3f2b…"
}
```

Validierungsfehler (`422`) tragen zusätzlich `errors` mit Feld, Meldung und Typ. Die `request_id`
entspricht dem Antwort-Header `X-Request-ID`; Betreiber finden sie in den Server-Logs wieder
(siehe [Logging und Tracing](../betrieb/logging-tracing.md)).

## Ablösung der alten Pfade

!!! warning "Abgekündigt: alte Session-API, Wegfall am 31. Mai 2027"
    Die früheren Endpunkte unter `/session/<kommune>/api/session/…` (`meetings/`, `papers/`,
    `applications/`, `applications/submit/`) sind abgekündigt und entfallen am **31. Mai 2027**.
    Bis dahin bleiben sie erreichbar und antworten mit den Headern `Deprecation: true`,
    `Sunset: Mon, 31 May 2027 00:00:00 GMT` und `Link: <neuer Pfad>; rel="successor-version"`.
    Bis Version 0.11 nannte der Header den 31. März 2027; der Termin wurde zugunsten der Nutzer
    verlängert. Ersatz ist die hier beschriebene Session-API v1.

Der Einstiegspunkt `/session/<kommune>/api/` und die [OParl-API je Kommune](oparl-api.md) bleiben.
Unterschiede beim Umstieg:

| Alt | Neu |
|-----|-----|
| Fehler als `{"error": "…"}` | `application/problem+json`, fehlende oder ungültige Felder als `422` mit `errors` |
| feste 100 Einträge | `limit`/`offset`, `meta.total` |
| Token nur zum Einreichen | Token reicht ein und fragt den Rückmeldestand eigener Anträge ab (`…/feedback/`); lesend nur öffentliche Daten wie anonyme Aufrufer – nicht-öffentliche Daten nie, unabhängig von den Flags |
| `application_type`-Aliase `proposal`, `urgent_motion` | weiterhin akzeptiert |
