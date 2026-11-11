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
curl https://oparl.mandari.de/oparl/v1/system
```

Von dort hangelst du dich über die verlinkten Objekte durch alle Daten:

```
System → Bodies (Kommunen) → Organizations, Persons, Meetings, Papers
```

Die Kennungen aller Objekte beginnen mit `https://oparl.mandari.de/oparl/v1/`. Dieselben Pfade unter `https://mandari.de/oparl/` liefern dieselben Objekte mit denselben Kennungen.

## Kommunen finden

Um nicht erst alle Bodies laden zu müssen, gibt es zwei Verzeichnisse mit denselben Kommunen, wie sie im Bürgerportal stehen:

- **Übersicht [`https://oparl.mandari.de/oparl/`](https://oparl.mandari.de/oparl/)**: Das Feld `bodyIndex` nennt je Kommune `name`, `displayName`, `slug`, `ags` (achtstellig, soweit gepflegt), `license` (der Kommune, sonst die der Installation) und die Adressen `body`, `paper`, `meeting`, `organization`, `person` und `web`, alphabetisch nach `displayName`. Ein Abruf genügt.
- **Seite [Offene Daten](https://mandari.de/offene-daten/)**: dieselben Adressen zum Lesen, mit Beispiel und einer eigenen Seite je Kommune, zum Beispiel [mandari.de/offene-daten/muenster/](https://mandari.de/offene-daten/muenster/).

Umgekehrt zeigt `Body.web` auf die Seite der Kommune im Bürgerportal (`https://mandari.de/insight/k/<slug>/`), und jede Seite einer Kommune nennt ihren Body im Kopf als `<link rel="alternate" type="application/json">`. `Body.ags` ist der achtstellige Amtliche Gemeindeschlüssel, wie wir ihn pflegen, sonst die Angabe der Quelle.

## Kurzadressen mit dem Namen der Kommune

Statt der UUID darf in der Adresse der Name der Kommune stehen, wie er im Feld `slug` des Verzeichnisses und in der Adresse des Bürgerportals steht:

```
https://oparl.mandari.de/oparl/v1/body/muenster
https://oparl.mandari.de/oparl/v1/body/muenster/papers
https://oparl.mandari.de/oparl/v1/body/muenster/meetings?modified_since=2026-11-01T00:00:00Z
```

Die Kurzadresse antwortet mit einer Weiterleitung (HTTP 307) auf die Adresse mit der UUID; Parameter bleiben erhalten. Die UUID bleibt die Kennung der Kommune: Sie ändert sich nie, ein Name kann sich ändern. Wer Kennungen speichert oder vergleicht, nimmt sie deshalb aus der Antwort: Die Kennung der Kommune ist das Feld `id` ihres Body-Objekts (`/body/muenster`). Eine Liste wie `/body/muenster/papers` trägt selbst keine Kennung der Kommune; dort ist `data[].id` die Kennung des einzelnen Eintrags, und dessen Feld `body` nennt die Kommune. Ausnahme sind gelöschte Objekte (Tombstones, siehe den Abschnitt „Gelöschte Objekte“ weiter unten): Sie tragen kein Feld `body`. Wer mit `modified_since` abgleicht, merkt sich die Kommune deshalb aus der Abfrage oder aus dem zuvor gespeicherten Objekt. Ein unbekannter Name gibt HTTP 404 mit einem Hinweis auf das Verzeichnis.

## Schnellstart: Anträge einer Kommune abrufen

```bash
# Vorlagen von Münster, die sich seit dem 1. November 2026 geändert haben (Zeitzone angeben; -L folgt der Weiterleitung)
curl -sL "https://oparl.mandari.de/oparl/v1/body/muenster/papers?modified_since=2026-11-01T00:00:00Z"   | jq '.data[] | {name, reference, paperType, date, web}'
```

Ohne Kurzadresse steht die Adresse der Liste im Verzeichnis:

```bash
curl -s https://oparl.mandari.de/oparl/ | jq -r '.bodyIndex[] | select(.slug == "muenster") | .paper'
```

Die Liste der Vorlagen enthält Vorlagen, Anträge und Anfragen. Die Art steht im Feld `paperType` (etwa „Antrag“ oder „Anfrage“), die Dokumente stehen unter `mainFile` und `auxiliaryFile`. Den erkannten Text liefert eine Datei nur unter ihrer eigenen Adresse (`id`) im Feld `text`, nicht in der Liste. Weitere Seiten findest du unter `links.next`.

## Endpunkte

| Endpunkt | Inhalt |
|----------|--------|
| `GET /oparl/v1/` | JSON-Übersicht über die API mit dem Verzeichnis der Kommunen (`bodyIndex`) |
| `GET /oparl/v1/system` | OParl-System-Objekt (Einstiegspunkt) |
| `GET /oparl/v1/bodies` | Liste aller Kommunen (paginiert) |
| `GET /oparl/v1/body/<uuid>` | Einzelne Kommune |
| `GET /oparl/v1/body/<name>[/…]` | Kurzadresse mit dem Namen der Kommune, leitet auf die Adresse mit der UUID weiter |
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
curl "https://oparl.mandari.de/oparl/v1/body/<uuid>/meetings?modified_since=2026-06-01T00%3A00%3A00%2B00%3A00"

# Das Z-Suffix ist ebenfalls gültig
curl "https://oparl.mandari.de/oparl/v1/body/<uuid>/meetings?modified_since=2026-06-01T00:00:00Z"
```

!!! warning "Zeitstempel brauchen eine Zeitzone"
    Zeitstempel **müssen** eine explizite Zeitzone enthalten (`+01:00`, `+00:00` oder `Z`). Zeitstempel ohne Zeitzone sind mehrdeutig und werden mit HTTP 400 und einer klaren Fehlermeldung abgelehnt. Das `+` in URLs als `%2B` kodieren.

Die Filter arbeiten auf denselben Werten, die als `created` und `modified` ausgeliefert werden: den OParl-Zeitstempeln der Quelle, ersatzweise dem Zeitpunkt der Spiegelung in mandari.

## Gelöschte Objekte (Tombstones)

Objekte, die im Quellsystem gelöscht wurden, werden in mandari nicht physisch gelöscht, sondern markiert. Die API verhält sich dabei standardkonform:

- **Objekt-Endpunkte** liefern gelöschte Objekte weiterhin mit HTTP 200 aus, als gekürztes Objekt mit ausschließlich den Pflichtfeldern:

    ```json
    {
      "id": "https://oparl.mandari.de/oparl/v1/paper/<uuid>",
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

Eine physische Löschung erfolgt ausschließlich auf ausdrückliche Aufforderung einer Kommune, siehe [Ingestor und Opt-out](../datenschutz/ingestor.md).

## Zugriff für KI-Assistenten (MCP)

Neben der OParl-Schnittstelle gibt es auf mandari.de einen öffentlichen, nur lesenden MCP-Server ([Model Context Protocol](https://modelcontextprotocol.io)):

```
https://mandari.de/insight/mcp
```

KI-Assistenten und eigene Agenten, die MCP sprechen, können damit Kommunen, Vorlagen, Sitzungen und Beschlüsse abfragen, mit denselben Werkzeugen wie der KI-Assistent im Bürgerportal. Der Server braucht keine Anmeldung und ändert nichts. Transport ist „Streamable HTTP“ (nur `POST` mit JSON-RPC 2.0). Es gelten 30 Anfragen je Minute und 500 Werkzeugaufrufe je Tag und Adresse.

In eigenen Installationen ist der Server ausgeschaltet, bis der Betrieb ihn mit `INSIGHT_MCP_ENABLED=true` einschaltet ([Konfiguration](../betrieb/konfiguration.md)).

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
