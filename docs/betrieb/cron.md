---
title: Regelmäßige Aufgaben (Cron)
description: Alle wiederkehrenden Aufgaben einer mandari-Installation an einer Stelle. Empfohlene Zeitpläne für Dokument-Cache, Quellenüberwachung, Erinnerungen, Löschlauf und Personenfotos.
---

# Regelmäßige Aufgaben (Cron)

Der Ingestor läuft als Daemon und braucht keinen Cron. Einige Aufgaben der Anwendung werden dagegen bewusst von außen angestoßen, damit ihr Zeitpunkt und Protokoll in eurer Hand liegen. Eine bewährte Crontab für den Host, Container-Name `mandari`, Compose-Verzeichnis `/opt/mandari`:

```cron
# Dokument-Cache: neueste Dokumente nachladen (stündlich)
40 * * * *  docker exec mandari python manage.py cache_files --limit 400 >> /var/log/mandari-file-cache.log 2>&1

# Quellenüberwachung: Alarme und Entwarnungen (stündlich)
15 * * * *  docker exec mandari python manage.py check_source_health >> /var/log/mandari-source-health.log 2>&1

# Session: Fristen-Erinnerungen (täglich 07:00)
0 7 * * *   cd /opt/mandari && docker compose exec -T mandari python manage.py send_session_reminders >> /var/log/mandari-reminders.log 2>&1

# Ratsfragen: Erinnerung an unbeantwortete Fragen (täglich 07:30)
30 7 * * *  docker exec mandari python manage.py send_question_reminders >> /var/log/mandari-question-reminders.log 2>&1

# Session: Anonymisierungs- und Löschlauf nach Aufbewahrungsfristen (monatlich am 1., 03:00)
0 3 1 * *   docker exec mandari python manage.py session_privacy_purge >> /var/log/mandari-privacy-purge.log 2>&1

# Personenfotos aktualisieren (wöchentlich montags 03:00)
0 3 * * 1   docker exec mandari python manage.py fetch_person_photos >> /var/log/mandari-person-photos.log 2>&1
```

## Die Befehle im Detail

| Befehl | Zweck | Nützliche Optionen |
|--------|-------|--------------------|
| `cache_files` | Lädt Dokumente angebundener Quellen in den lokalen Cache, neueste zuerst | `--limit N`, `--body <slug>`, `--stats` |
| `check_source_health` | Bewertet alle Quellen, verschickt Alarme und Entwarnungen | `--report` für einen Bericht ohne Versand |
| `send_session_reminders` | Fristen-Erinnerungen für alle Session-Mandanten | `--tenant <slug>`, `--dry-run` |
| `send_question_reminders` | Erinnert Ratsmitglieder an offene Ratsfragen | |
| `session_privacy_purge` | Anonymisiert und löscht nach den je Mandant konfigurierten Fristen | `--tenant <slug>`, `--dry-run` |
| `fetch_person_photos` | Holt Fotos von Mandatsträgerinnen aus den Quellsystemen | `--body <slug>`, `--force` |
| `purge_deleted` | Löscht als gelöscht markierte Objekte endgültig, nur auf Aufforderung einer Kommune | `--body <slug>`, `--older-than N`, `--ids …`, `--yes` |

Alle Läufe sind idempotent: Mehrfaches Ausführen erzeugt keine doppelten E-Mails und keine doppelten Daten.

## Hinweise

- Die Logdateien unter `/var/log/` sind Beispiele. Wer eine zentrale Protokollierung hat, leitet die Ausgaben dorthin.
- Der Löschlauf ist auch aus der Anwendung heraus möglich (*Einstellungen → Datenschutz*), inklusive Probelauf. Der Cron stellt sicher, dass er nicht vergessen wird. Details im [Löschkonzept](../datenschutz/loeschkonzept.md).
- `cache_files --stats` zeigt Abdeckung, Belegung und freien Speicher. Dieselben Werte sieht der [Betriebsmonitor](monitoring.md).
