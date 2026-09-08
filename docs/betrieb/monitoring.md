---
title: Betriebsmonitor
description: Der Betriebsmonitor im mandari-Admin. Bewertung der Quellen, Systemchecks, Handlungsbedarf, Alarmierung per E-Mail und Datenstand-Hinweis im Bürgerportal.
---

# Betriebsmonitor

Der Betriebsmonitor macht Ausfälle sichtbar, die sonst still bleiben, etwa eine Quelle, die über Wochen nur noch HTTP 403 liefert, ohne dass es jemand bemerkt.

## Wo

- **Admin-Dashboard** (`/admin/`): Panel „Betriebsstatus“ ganz oben mit Gesamtstatus, kritischen Quellen und Handlungsbedarf.
- **Betriebsmonitor** (`/admin/monitoring/`, Sidebar „Sync & Quellen“): alle aktiven Quellen mit Bewertung, Systemchecks (Datenbank, Cache, Elasticsearch, Ingestor-Daemon, Sync-Läufe der letzten 24 Stunden, Dokument-Cache), Handlungsbedarf, letzte Sync-Läufe.
- **OParl-Quellen-Liste**: Spalte „Gesundheit“, Filter nach Status, Felder *Letzter Fehler*, *Fehlversuche in Folge*, *Alarm gesendet am*.
- **Bürgerportal**: Ist die Quelle einer Kommune länger als die kritische Schwelle nicht synchronisiert, sehen Besucherinnen einen Hinweis „Datenstand: TT.MM.JJJJ“.

## Bewertung einer Quelle

| Status | Bedingung |
|--------|-----------|
| OK | letzter erfolgreicher Sync jünger als `INSIGHT_SOURCE_STALE_WARNING_HOURS` (Standard 48 Stunden) |
| Warnung | älter als die Warnschwelle **oder** letzter Versuch fehlgeschlagen |
| Kritisch | älter als `INSIGHT_SOURCE_STALE_CRITICAL_DAYS` (Standard 7 Tage) **oder** mindestens 3 Fehlversuche in Folge **oder** seit mehr als 7 Tagen angelegt und nie synchronisiert |
| Inaktiv | deaktivierte Quelle, erscheint nur im Admin-Filter der Quellenliste, nicht im Betriebsmonitor |

Der Ingestor schreibt bei jedem fehlgeschlagenen Versuch den letzten Fehler mit Zeitstempel und zählt die Fehlversuche in Folge hoch. Ein erfolgreicher Sync setzt die Werte zurück. So ist der konkrete Grund, zum Beispiel `HTTP 403`, direkt im Admin sichtbar.

Ab `INSIGHT_SOURCE_BACKOFF_FAILURES` (Standard 3) Fehlversuchen greift die **Quellen-Schonung**: Dokument-Cache und Datei-Proxy pausieren für diese Quelle, der Ingestor verdoppelt den Abstand zwischen den Versuchen bis auf 6 Stunden. Details unter [Dokument-Cache](dokument-cache.md#quellen-schonung).

## Alarmierung

```cron
15 * * * * docker exec mandari python manage.py check_source_health >> /var/log/mandari-source-health.log 2>&1
```

- Kritische Quelle: E-Mail-Alarm, Wiederholung frühestens nach 7 Tagen
- Quelle wieder OK: Entwarnung, der Alarm-Zeitstempel wird gelöscht
- Ingestor-Daemon mehr als 6 Stunden ohne Lauf: Alarm, höchstens einmal je 24 Stunden
- Empfänger: `INSIGHT_ALERT_EMAILS` (kommagetrennt), sonst `INSIGHT_MODERATION_EMAILS`, sonst alle Superuser

Bericht ohne Versand: `python manage.py check_source_health --report`

## Öffentliche Statusseite

Für die von uns betriebene Installation ist der Betriebsstatus aller Dienste öffentlich unter [status.mandari.de](https://status.mandari.de) einsehbar, inklusive angekündigter Wartungsfenster. Für eine eigene Installation empfiehlt sich ein externer Verfügbarkeitsmonitor auf `https://<domain>/health`, der Endpunkt antwortet mit `OK`.
