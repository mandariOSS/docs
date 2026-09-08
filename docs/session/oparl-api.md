---
title: OParl-API je Kommune
description: Die OParl-1.1-Schnittstelle jedes mandari-Session-Mandanten. Sichtbarkeitsregeln, Endpunkte, Abstimmungsergebnisse, Beratungsfolge, Tombstones.
---

# OParl-API je Kommune

Jede aktive Kommune in mandari Session stellt unter

```
https://<host>/session/<kommune>/api/oparl/
```

einen eigenen, **OParl-1.1-konformen System-Endpunkt** bereit. Die API folgt dem Muster der [OParl-Aggregations-API](../insight/oparl-api.md): rein lesend, anonym, JSON, CORS offen, Rate-Limit von 120 Anfragen pro Minute je IP-Adresse.

Spezifikation: [oparl.org/spezifikation](https://oparl.org/spezifikation/)

## Sicherheitsgarantie: nur öffentliche Daten

Die API liefert ausschließlich Daten, die im Ratsinformationssystem als öffentlich markiert sind:

| Objekttyp | Sichtbarkeitsregel |
|-----------|--------------------|
| Meeting | Sitzung öffentlich |
| AgendaItem | Punkt öffentlich **und** Sitzung öffentlich. Der nicht-öffentliche Teil erscheint nie, `resolutionText` enthält nur den öffentlichen Beschlusstext |
| Paper | Vorlage öffentlich |
| File | Datei öffentlich **und** übergeordnetes Objekt (Vorlage, Sitzung, Punkt) öffentlich |
| Consultation | Vorlage öffentlich. Referenzen auf nicht-öffentliche Sitzungen oder Punkte werden ausgelassen |
| Person | ohne geschützte Daten. Verschlüsselte Felder wie Telefon, Adresse und Bankdaten werden nie gelesen |
| Organization, Membership, LegislativeTerm | vollständig, hier gibt es keine Unterteilung |

Nicht-öffentliche Objekte existieren nach außen nicht: Ihre Objekt-Endpunkte liefern 404, sofern sie nie veröffentlicht waren. Diese Garantie wird durch automatische Tests über die gesamte API-Oberfläche abgesichert.

## Endpunkte

| Endpunkt | Inhalt |
|----------|--------|
| `GET …/api/oparl/` | System-Objekt (Einstiegspunkt) |
| `GET …/api/oparl/bodies/` | Liste mit der einen Kommune |
| `GET …/api/oparl/body/` | Body-Objekt inklusive eingebetteter `legislativeTerm` |
| `GET …/api/oparl/organizations/` | Gremien (paginiert, filterbar) |
| `GET …/api/oparl/people/` | Personen (paginiert, Mitgliedschaften eingebettet) |
| `GET …/api/oparl/meetings/` | Sitzungen, nur öffentlich, Punkte des öffentlichen Teils eingebettet |
| `GET …/api/oparl/papers/` | Vorlagen, nur öffentlich, `mainFile`, `auxiliaryFile` und `consultation` eingebettet |
| `GET …/api/oparl/memberships/`, `…/agendaitems/`, `…/consultations/`, `…/files/`, `…/legislativeterms/` | weitere Listen gemäß OParl 1.1 |
| `GET …/api/oparl/<typ>/<uuid>/` | Objekt-Endpunkte aller Typen |
| `GET …/api/oparl/file/<uuid>/download/` | Anonymer Datei-Abruf öffentlicher Anlagen, `?download=1` für Attachment |

Objekttypen für `<typ>`: `organization`, `person`, `membership`, `meeting`, `agendaitem`, `paper`, `consultation`, `file`, `legislativeterm`.

`Paper.mainFile` ist die älteste öffentliche Anlage der Vorlage, alle weiteren erscheinen unter `auxiliaryFile`.

## Abstimmungsergebnisse

Öffentliche Tagesordnungspunkte mit Ergebnis tragen zusätzlich zu `result` und `resolutionText` zwei Vendor-Felder:

- `mandari:vote`: Summen mit `method`, `methodLabel`, `result`, `resultLabel`, `yes`, `no`, `abstain`
- `mandari:rollCall`: **nur bei namentlicher Abstimmung** eine Liste aus `name`, `vote`, `voteLabel`, inklusive Befangenheit als `excluded`

Offen erfasste, geheime oder nur summierte Abstimmungen liefern nie Einzelstimmen. Die Aggregations-API des Bürgerportals reicht beide Felder durch, die Sitzungsseite im Portal zeigt Summen und aufklappbar die namentlichen Stimmen.

## Beratungsfolge

Die Beratungsfolge wird standardkonform als `Consultation` ausgeliefert: `paper`, `organization`, `meeting` und `agendaItem` (sobald terminiert und öffentlich), `role` (Vorberatung, Anhörung, Entscheidung, Kenntnisnahme) und `authoritative` für die entscheidende Station.

## Pagination und Zeitfilter

Wie beim Aggregator: OParl-Listen-Envelope mit `data`, `pagination` und `links`, echte `links.next`-URLs, HTTP-`Link`-Header, 100 Objekte pro Seite, Sortierung nach `modified` aufsteigend.

Alle Listen unterstützen `created_since`, `created_until`, `modified_since` und `modified_until`. Zeitstempel **müssen** eine explizite Zeitzone enthalten, sonst antwortet die API mit HTTP 400. Das `+` in URLs als `%2B` kodieren.

## Gelöschte und entöffentlichte Objekte (Tombstones)

Objekte, die einmal öffentlich ausgeliefert wurden und danach **gelöscht** oder auf **nicht-öffentlich** gestellt werden, hinterlassen einen Tombstone:

- Objekt-Endpunkte liefern weiterhin HTTP 200 mit dem gekürzten Objekt (`id`, `type`, `created`, `modified`, `deleted: true`). `modified` ist der Löschzeitpunkt, Inhalte entfallen vollständig.
- Listen ohne Filter enthalten keine Tombstones.
- Listen mit `modified_since` enthalten passende Tombstones, damit inkrementelle Clients Löschungen zuverlässig mitbekommen.
- Wird ein Objekt wieder veröffentlicht, verschwindet der Tombstone und das Vollobjekt ist wieder abrufbar.
- Der Wechsel von öffentlich auf nicht-öffentlich kaskadiert: Eine entöffentlichte Sitzung hinterlässt auch Tombstones für ihre öffentlichen Punkte und Anlagen, eine entöffentlichte Vorlage für ihre Anlagen und Beratungsstationen.

## Konsumenten

Ein generischer OParl-Client kann eine Kommune vollständig und inkrementell spiegeln. Der wichtigste Konsument ist das mandari-Bürgerportal selbst, siehe [Veröffentlichung im Bürgerportal](buergerportal.md).

## Betrieb

Die IDs der API werden aus dem Host der Anfrage gebaut. Die API funktioniert damit unter jedem konfigurierten Host ohne weitere Einstellung. Seitengröße und Rate-Limit teilen sich die Variablen `OPARL_API_PAGE_SIZE` und `OPARL_API_RATE_LIMIT` mit der Aggregations-API, siehe [Konfiguration](../betrieb/konfiguration.md#oparl-aggregations-api).
