---
title: Fehlertypen der Schnittstellen
description: Fehlerantworten der mandari-Schnittstellen nach RFC 9457 (Problem Details). Aufbau, Felder und alle Fehlertypen der Session-API v1, des Änderungsfeeds, des Datenkatalogs und der Befehle der Datendrehscheibe.
---

# Fehlertypen der Schnittstellen

Mehrere Schnittstellen von mandari melden Fehler im Format **Problem Details** nach [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) als `application/problem+json`. Das Feld `type` nennt eine Adresse unter `https://docs.mandari.de/api/probleme/`. Jeder Typ hat auf dieser Seite einen eigenen Abschnitt; die Adresse eines Typs führt direkt dorthin.

## Aufbau einer Fehlerantwort

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

| Feld | Bedeutung |
|------|-----------|
| `type` | Fehlertyp als Adresse auf dieser Seite. Ohne eigenen Typ steht dort `about:blank`; dann gilt nur der HTTP-Status. |
| `title` | Kurzbezeichnung zum HTTP-Status, zum Beispiel „Keine Berechtigung“ |
| `status` | HTTP-Status, derselbe wie in der Antwort |
| `detail` | Erläuterung für Menschen. Programme werten `type` und `status` aus, nicht diesen Text. |
| `instance` | Pfad der Anfrage |
| `request_id` | Kennung der Anfrage, dieselbe wie im Header `X-Request-ID`. Nennen Sie sie bei Rückfragen; der Betrieb findet damit die Anfrage im Protokoll. |
| `errors` | Nur bei Validierungsfehlern: die beanstandeten Stellen, siehe [validierung](#validierung) |

Manche Typen tragen weitere Felder, etwa `snapshot` bei [cursor-abgelaufen](#cursor-abgelaufen). Unbekannte Felder können Sie ignorieren.

## Wo das Format gilt

| Schnittstelle | Fehler nach RFC 9457 |
|---------------|----------------------|
| [Session-API v1](../session/api-v1.md) (`/api/v1/session/<mandant>/…`) | alle Fehler |
| Änderungsfeed und Snapshot je Kommune ([OParl-Aggregations-API](../insight/oparl-api.md), [OParl-API je Kommune](../session/oparl-api.md)) | nur [cursor-abgelaufen](#cursor-abgelaufen) und [kommune-zurueckgenommen](#kommune-zurueckgenommen); die übrigen Fehler der OParl-Schnittstellen sind einfaches JSON mit `error` und `status` |
| Datenkatalog nach DCAT-AP.de (`/data/dcat/…` und `/session/<mandant>/api/dcat/catalog`, nur wenn die Installation ihn eingeschaltet hat) | [keine-lizenz](#keine-lizenz) und [kommune-zurueckgenommen](#kommune-zurueckgenommen) |
| Befehle der Datendrehscheibe | alle Fehler, siehe [Befehle der Datendrehscheibe](#befehle-der-datendrehscheibe) |

## Session-API v1, Änderungsfeed und Datenkatalog

### nicht-authentifiziert { #nicht-authentifiziert }

**Status 401.** Die Anfrage braucht eine gültige Anmeldung. Bei der Session-API fehlt das API-Token, es hat ein ungültiges Format, ist unbekannt, gehört zu einem anderen Mandanten oder ist deaktiviert bzw. abgelaufen. Die Antwort trägt den Header `WWW-Authenticate: Bearer realm="mandari Session-API"`.

Abhilfe: Ein gültiges Token des Mandanten im Header `Authorization: Bearer <token>` mitsenden. Wer Anträge einreicht oder den Rückmeldestand abfragt, braucht immer ein Token. Den Rückmeldestand eines Antrags liefert nur das Token, mit dem der Antrag eingereicht wurde.

### keine-berechtigung { #keine-berechtigung }

**Status 403.** Die Anmeldung ist gültig, reicht für diese Anfrage aber nicht. Beispiele: Das Token darf keine Anträge einreichen, für den Bereich fehlt das Leserecht, das Token darf von dieser IP-Adresse nicht verwendet werden, oder die einreichende Organisation passt nicht zum Token.

Abhilfe: Rechte des Tokens bzw. der Person beim Mandanten prüfen lassen. Die Rechte der Token beschreibt die [Session-API v1](../session/api-v1.md).

### nicht-gefunden { #nicht-gefunden }

**Status 404.** Den Mandanten oder den Antrag gibt es nicht, zum Beispiel ein falscher Mandanten-Kurzname im Pfad.

### ratenlimit { #ratenlimit }

**Status 429.** Das Token hat sein Ratenlimit je Minute erreicht. Das Limit gilt je Token für alle Wege der Session-API. Die Antwort trägt `Retry-After: 60`.

Abhilfe: Nach der genannten Wartezeit erneut senden und Anfragen gleichmäßiger verteilen.

### validierung { #validierung }

**Status 422.** Die Anfrage enthält ungültige oder fehlende Felder. Das Feld `errors` nennt die Stellen:

- **Session-API:** je Fehler `loc` (Stelle), `msg` (Meldung) und `type` (Art der Prüfung).
- **Befehle der Datendrehscheibe:** je Fehler `pointer` (Stelle als JSON-Pointer nach RFC 6901, etwa `/antrag/titel`) und `detail` (verletzte Regel). Werte aus der Anfrage stehen nie in der Antwort.

Abhilfe: Die genannten Felder nach der OpenAPI-Beschreibung bzw. dem Vertrag des Befehls korrigieren.

### cursor-abgelaufen { #cursor-abgelaufen }

**Status 410.** Der Cursor des Änderungsfeeds gilt nicht mehr. Er ist älter als die Aufbewahrung des Feeds, stammt nicht aus diesem Feed oder ist älter als eine Rücknahme der Kommune. Das Zusatzfeld `snapshot` nennt die Adresse des Snapshots:

```json
{
  "type": "https://docs.mandari.de/api/probleme/cursor-abgelaufen",
  "title": "Nicht mehr verfügbar",
  "status": 410,
  "detail": "Der Cursor ist nicht mehr gültig: …",
  "instance": "/oparl/v1/body/<uuid>/changes",
  "snapshot": "https://mandari.de/oparl/v1/body/<uuid>/snapshot"
}
```

Abhilfe: Den Snapshot abrufen und mit dessen Cursor im Feed fortsetzen.

### kommune-zurueckgenommen { #kommune-zurueckgenommen }

**Status 410.** Die Kommune hat die Veröffentlichung dauerhaft zurückgenommen. Ihre Einträge gelten als gelöscht, ein vorhandener Cursor gilt nicht mehr. Feed, Snapshot und Datenkatalog der Kommune antworten so. Veröffentlicht die Kommune wieder, beginnt der Abgleich erneut mit dem Snapshot.

Abhilfe: Die Einträge der Kommune wie gelöscht behandeln, also auch aus eigenen Kopien entfernen.

### keine-lizenz { #keine-lizenz }

**Status 404.** Für die Kommune bzw. den Mandanten ist keine offene Lizenz bekannt; ohne Lizenz gibt es keinen Datenkatalog. Im Bürgerportal nennt die Kommune die Lizenz in ihrer OParl-Schnittstelle (`Body.license`). Ein Session-Mandant wählt sie in den Einstellungen (Karte „OParl-Schnittstelle“).

## Befehle der Datendrehscheibe

Wer Daten eines anderen Moduls ändern will, schickt dessen Eigentümer einen **Befehl** und erhält sofort eine Quittung oder ein Problem mit den Typen dieses Abschnitts. Noch nutzt kein Einreichungsweg die Befehle, und die Standardinstallation bindet ihren HTTP-Weg nicht unter einer öffentlichen Adresse ein. Die Typen stehen trotzdem schon fest; Grundlage ist die Architekturentscheidung [Befehle synchron](https://github.com/mandariOSS/mandari/blob/dev/docs/adr/20260929-befehle-synchron.md).

Eine Anfrage, die mit 409, 429, 502, 503 oder 504 scheitert, darf mit **demselben** Idempotenzschlüssel wiederholt werden.

### idempotenzschluessel-fehlt { #idempotenzschluessel-fehlt }

**Status 400.** Der Idempotenzschlüssel fehlt oder ist ungültig. Erlaubt sind 1 bis 255 sichtbare ASCII-Zeichen ohne Anführungszeichen.

### ungueltiges-json { #ungueltiges-json }

**Status 400.** Der Inhalt ist kein gültiges JSON, kein JSON-Objekt oder zu tief verschachtelt.

### methode-nicht-erlaubt { #methode-nicht-erlaubt }

**Status 405.** Befehle werden per `POST` gesendet; die Antwort trägt `Allow: POST`.

### anfrage-zu-gross { #anfrage-zu-gross }

**Status 413.** Der Inhalt ist zu groß.

### format-nicht-unterstuetzt { #format-nicht-unterstuetzt }

**Status 415.** Der Inhalt muss `application/json` sein.

### befehl-unbekannt { #befehl-unbekannt }

**Status 404.** Diesen Befehl gibt es in dieser Version nicht.

### idempotenzschluessel-wiederverwendet { #idempotenzschluessel-wiederverwendet }

**Status 422.** Der Idempotenzschlüssel wurde schon für einen anderen Befehl oder einen anderen Inhalt verwendet. Für einen neuen Befehl einen neuen Schlüssel erzeugen.

### interner-fehler { #interner-fehler }

**Status 500.** Der Befehl konnte nicht ausgeführt werden. Später mit demselben Idempotenzschlüssel wiederholen; die Meldung nennt bewusst keine Einzelheiten.

### befehl-nicht-verfuegbar { #befehl-nicht-verfuegbar }

**Status 501.** Den Befehl gibt es, diese Installation führt ihn aber nicht aus.

### unerwartete-antwort { #unerwartete-antwort }

**Status 502.** Der Eigentümer hat unerwartet geantwortet, wenn Sender und Eigentümer getrennt laufen. Später mit demselben Idempotenzschlüssel wiederholen.

### eigentuemer-nicht-erreichbar { #eigentuemer-nicht-erreichbar }

**Status 503.** Der Eigentümer ist nicht erreichbar, wenn Sender und Eigentümer getrennt laufen. Später mit demselben Idempotenzschlüssel wiederholen.

Über den HTTP-Weg kommen [nicht-authentifiziert](#nicht-authentifiziert) (401) und [keine-berechtigung](#keine-berechtigung) (403) hinzu, für Inhalte, die nicht zum Vertrag passen, [validierung](#validierung) (422). Fachliche Ablehnungen meldet der Eigentümer mit einem eigenen Typ, etwa mit Status 409.
