---
title: Logging und Tracing
description: Strukturierte Logs mit Request-Kennung, Log-Level in Produktion, OpenTelemetry-Export für Anwendung und Ingestor.
---

# Logging und Tracing

mandari schreibt Logs auf die Standardausgabe der Container. In Produktion sind das JSON-Zeilen, die sich
direkt in Loki, Elastic, OpenSearch oder CloudWatch einlesen lassen; in der Entwicklung ein lesbares
Textformat. Jede Zeile trägt eine Request-Kennung, mit der sich alle Einträge einer Anfrage über
Anwendung und Ingestor hinweg zusammensuchen lassen.

## Umgebungsvariablen

| Variable | Anwendung (`mandari`) | Ingestor | Bedeutung |
|----------|------------------------|----------|-----------|
| `LOG_FORMAT` | `json` (Standard ohne DEBUG) / `text` | `text` (Standard) / `json` | Ausgabeformat |
| `LOG_LEVEL` | `INFO` (Standard) | `INFO` (Standard) | Mindest-Level der eigenen Module; `DEBUG` wird in Produktion auf `INFO` gekappt |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | z. B. `http://otel-collector:4318` | ebenso | Aktiviert das Tracing; leer = aus |
| `OTEL_SERVICE_NAME` | `mandari-web` | `mandari-ingestor` | Dienstname in Traces und Logs |

## Aufbau einer Log-Zeile

```json
{"ts": "2026-09-09T09:12:44.120+00:00", "level": "INFO", "logger": "apps.work.motions",
 "msg": "Antrag gespeichert", "service": "mandari-web",
 "request_id": "243f21aac997439db2e38434bf1a2762",
 "user_id": "879538a4-e32d-4a14-b07d-f519a8f02cae", "trace_id": "-", "span_id": "-"}
```

- `request_id` kommt aus dem Header `X-Request-ID`, wenn der Reverse Proxy einen setzt (empfohlen,
  z. B. mit Caddy `header X-Request-ID {http.request.uuid}`), sonst erzeugt die Anwendung eine. Der
  Wert steht auch in der Antwort, sodass Nutzer ihn bei Fehlermeldungen mitgeben können; die
  [Session-API](../session/api-v1.md) liefert ihn in jedem Fehlerobjekt.
- `user_id` ist ausschließlich die interne UUID des angemeldeten Nutzers. Namen, E-Mail-Adressen oder
  Inhalte gehören nicht in Log-Zeilen.
- `trace_id`/`span_id` sind gesetzt, sobald Tracing aktiv ist.

## Tracing mit OpenTelemetry

Mit gesetztem `OTEL_EXPORTER_OTLP_ENDPOINT` instrumentieren sich beide Dienste selbst (OTLP über HTTP):

- **Anwendung:** Django-Requests, Datenbank (psycopg), Redis, ausgehende HTTP-Aufrufe (requests, httpx).
- **Ingestor:** ausgehende HTTP-Aufrufe (httpx), Datenbank (asyncpg, SQLAlchemy).

Löst ein Admin im Betriebsmonitor einen Sync aus, übergibt die Anwendung `trace_id` und `span_id` mit
dem Trigger an den Ingestor. Der Ingestor hängt seinen Sync-Span darunter – im Trace-Backend erscheint
der gesamte Vorgang von der Anfrage bis zum Sync als ein Baum.

Als Empfänger eignet sich ein OpenTelemetry Collector, der an Grafana Tempo, Jaeger oder einen
kommerziellen Dienst weiterleitet. Ohne Collector bleibt alles aus; es entstehen keine Verbindungen
nach außen.

## Empfehlungen für den Betrieb

- Logs über den Container-Treiber einsammeln (`docker logs`, Promtail, Fluent Bit); keine Log-Dateien
  im Container.
- `LOG_LEVEL=DEBUG` nur kurzzeitig in der Entwicklung; in Produktion wird der Wert ohnehin auf `INFO`
  begrenzt.
- Aufbewahrungsfristen der Logs im [Löschkonzept](../datenschutz/loeschkonzept.md) berücksichtigen:
  Request-Kennungen und Nutzer-UUIDs sind pseudonym, aber personenbezogen.
