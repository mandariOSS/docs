---
title: OParl-Aggregations-API
description: Die OParl-1.1-Schnittstelle von mandari Insight liefert die Ratsinformationen aller angebundenen Kommunen über einen Endpunkt. Endpunkte, Pagination, Zeitfilter, Tombstones, Vendor-Attribute.
---

# OParl-Aggregations-API

mandari stellt die gespiegelten Ratsinformationen aller angebundenen Kommunen als **eigene, OParl-1.1-konforme Datenquelle** bereit. Statt viele kommunale OParl-Endpunkte einzeln abzufragen, genügt ein einziger Endpunkt. Dazu kommen mandari-Anreicherungen wie Volltexte, Zusammenfassungen und stabile Datei-Adressen.

- **Lesend, anonym, JSON**: keine Authentifizierung nötig
- **CORS offen**: `Access-Control-Allow-Origin: *`
- **Rate-Limit**: 120 Anfragen pro Minute je IP-Adresse, darüber HTTP 429
- **Spezifikation**: [oparl.org/spezifikation](https://oparl.org/spezifikation/)

## Einstiegspunkt

```bash
curl https://mandari.de/oparl/v1/system
```

Von dort hangelst du dich über die verlinkten Objekte durch alle Daten:

```
System → Bodies (Kommunen) → Organizations, Persons, Meetings, Papers
```

## Endpunkte

| Endpunkt | Inhalt |
|----------|--------|
| `GET /oparl/v1/` | JSON-Übersicht über die API |
| `GET /oparl/v1/system` | OParl-System-Objekt (Einstiegspunkt) |
| `GET /oparl/v1/bodies` | Liste aller Kommunen (paginiert) |
| `GET /oparl/v1/body/<uuid>` | Einzelne Kommune |
| `GET /oparl/v1/body/<uuid>/organizations` | Gremien der Kommune (paginiert, filterbar) |
| `GET /oparl/v1/body/<uuid>/people` | Personen der Kommune (paginiert, filterbar) |
| `GET /oparl/v1/body/<uuid>/meetings` | Sitzungen der Kommune (paginiert, filterbar) |
| `GET /oparl/v1/body/<uuid>/papers` | Vorlagen und Drucksachen der Kommune (paginiert, filterbar) |
| `GET /oparl/v1/body/<uuid>/locations` | Orte der Kommune (Vendor-Erweiterung, paginiert) |
| `GET /oparl/v1/<typ>/<uuid>` | Objekt-Endpunkte aller Typen |

Objekttypen für `<typ>`: `body`, `organization`, `person`, `membership`, `meeting`, `agendaitem`, `paper`, `consultation`, `file`, `location`, `legislativeterm`.

Einbettungen gemäß OParl 1.1: `Body.legislativeTerm`, `Person.membership`, `Meeting.agendaItem`, `Meeting.location`, `Meeting.invitation` und `auxiliaryFile`, `Paper.consultation`, `Paper.mainFile` und `auxiliaryFile` werden als vollständige Objekte eingebettet. Alle übrigen Referenzen sind URLs auf diese API.

## Pagination

Listen liefern 100 Objekte pro Seite (`?page=N`), sortiert nach `modified` aufsteigend. Diese Sortierung ist stabil und damit ideal für inkrementelle Clients. Die Antwort folgt dem OParl-Listen-Envelope:

```json
{
  "data": ["..."],
  "pagination": {
    "totalElements": 150,
    "elementsPerPage": 100,
    "currentPage": 1,
    "totalPages": 2
  },
  "links": {
    "first": ".../meetings",
    "self": ".../meetings",
    "next": ".../meetings?page=2",
    "last": ".../meetings?page=2"
  }
}
```

Zusätzlich werden die Links als HTTP-`Link`-Header mit `rel="first|prev|next|last"` ausgeliefert.

## Zeitfilter

Alle Listen unterstützen `created_since`, `created_until`, `modified_since` und `modified_until`. Die Filter sind inklusiv und kombinierbar.

```bash
# Alle Sitzungen, die seit dem 1. Juni 2026 (UTC) geändert wurden
curl "https://mandari.de/oparl/v1/body/<uuid>/meetings?modified_since=2026-06-01T00%3A00%3A00%2B00%3A00"

# Das Z-Suffix ist ebenfalls gültig
curl "https://mandari.de/oparl/v1/body/<uuid>/meetings?modified_since=2026-06-01T00:00:00Z"
```

!!! warning "Zeitstempel brauchen eine Zeitzone"
    Zeitstempel **müssen** eine explizite Zeitzone enthalten (`+01:00`, `+00:00` oder `Z`). Zeitstempel ohne Zeitzone sind mehrdeutig und werden mit HTTP 400 und einer klaren Fehlermeldung abgelehnt. Das `+` in URLs als `%2B` kodieren.

Die Filter arbeiten auf denselben Werten, die als `created` und `modified` ausgeliefert werden: den OParl-Zeitstempeln der Quelle, ersatzweise dem Zeitpunkt der Spiegelung in mandari.

## Gelöschte Objekte (Tombstones)

Objekte, die im Quellsystem gelöscht wurden, werden in mandari nicht physisch gelöscht, sondern markiert. Die API verhält sich dabei standardkonform:

- **Objekt-Endpunkte** liefern gelöschte Objekte weiterhin mit HTTP 200 aus, als gekürztes Objekt mit ausschließlich den Pflichtfeldern:

    ```json
    {
      "id": "https://mandari.de/oparl/v1/paper/<uuid>",
      "type": "https://schema.oparl.org/1.1/Paper",
      "created": "2024-01-01T00:00:00+00:00",
      "modified": "2026-07-01T12:00:00+00:00",
      "deleted": true
    }
    ```

    `modified` entspricht dem Löschzeitpunkt, alle weiteren Attribute entfallen.

- **Listen ohne Filter** (und mit reinen `created_*`- oder `modified_until`-Filtern) enthalten gelöschte Objekte nicht.
- **Listen mit `modified_since`** enthalten die passenden gelöschten Objekte als Tombstones. Inkrementelle Clients bekommen Löschungen so zuverlässig mit, ohne Voll-Sync.
- **Eingebettete Referenzen** wie `Meeting.agendaItem` oder `Paper.consultation` lassen gelöschte Objekte aus. Tombstones erscheinen nur als Top-Level-Objekte.

Eine physische Löschung erfolgt ausschließlich auf ausdrückliche Aufforderung einer Kommune, siehe [Crawler und Opt-out](../datenschutz/crawler.md).

## Dateien

`accessUrl` und `downloadUrl` zeigen auf den mandari-Dokumentproxy (`/insight/dokumente/<uuid>/preview/` bzw. mit `?download=1`). Das hat zwei Vorteile:

- stabil erreichbar, auch wenn der kommunale Quellserver gerade offline ist
- datenschutzfreundlich, weil sich der Client nicht mit dem Server der Kommune verbindet

Die Original-URL bleibt als `mandari:originalAccessUrl` erhalten. Der extrahierte Volltext (`text`) wird nur am Objekt-Endpunkt `/oparl/v1/file/<uuid>` ausgeliefert, nicht in eingebetteten Datei-Objekten.

## Vendor-Attribute

Ergänzende Felder tragen das Präfix `mandari:` und können von Standard-Clients ignoriert werden.

| Attribut | Objekt | Inhalt |
|----------|--------|--------|
| `mandari:originalId` | alle | Original-URL des Objekts im kommunalen Quellsystem |
| `mandari:slug`, `mandari:displayName` | Body | URL-Slug und Anzeigename der Kommune |
| `mandari:locationList` | Body | URL der Orte-Liste |
| `mandari:summary` | Paper | Automatisch erstellte Zusammenfassung, falls vorhanden |
| `mandari:originalAccessUrl` | File | Original-Datei-URL beim Quellserver |
| `mandari:sha256`, `mandari:pageCount` | File | SHA-256-Hash und Seitenzahl |
| `mandari:locationName`, `mandari:locationAddress` | Meeting | Ortsangabe als Text, falls kein Location-Objekt auflösbar |
| `mandari:vote` | AgendaItem | Abstimmungsergebnis in Summen (`method`, `result`, `yes`, `no`, `abstain`), wenn die Quelle es liefert |
| `mandari:rollCall` | AgendaItem | Einzelstimmen bei namentlicher Abstimmung, wenn die Quelle es liefert |

Die beiden Abstimmungsfelder stammen aus Kommunen, die mandari Session nutzen. Details unter [OParl-API je Kommune](../session/oparl-api.md).

## Einschränkungen

- **Nicht abgebildete Referenzen**: Felder ohne Gegenstück im Datenmodell (`Meeting.participant`, `Paper.originatorPerson`, `originatorOrganization`, `underDirectionOf`, `relatedPaper`, `Organization.subOrganizationOf`, `AgendaItem.resolutionFile`) werden ausgelassen, statt Original-URLs durchzureichen.
- **Lizenz**: Die Lizenz der Quelldaten wird, soweit die Kommune sie angibt, am Body-Objekt (`license`) durchgereicht. Eine übergreifende Lizenzangabe am System-Objekt ist noch offen.
- Protokolle (`invitation`, `resultsProtocol`, `verbatimProtocol`) und `Paper.mainFile` werden über die Original-Rohdaten zugeordnet. Fehlt diese Zuordnung, erscheinen die Dateien unter `auxiliaryFile`.

## Fair Use

- Bitte inkrementell synchronisieren (`modified_since`) statt Vollabzüge zu wiederholen.
- Setze einen aussagekräftigen `User-Agent` mit Kontaktmöglichkeit.
- Fragen zur Anbindung beantworten wir über [mandari.de/kontakt/](https://mandari.de/kontakt/).

Betreibst du mandari selbst? Die Betriebsparameter der API stehen in der [Konfigurationsreferenz](../betrieb/konfiguration.md#oparl-aggregations-api).
