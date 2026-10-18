---
title: Regelmäßige Aufgaben
description: Wiederkehrende Aufgaben einer mandari-Installation laufen als Zeitpläne im Worker, nicht per Host-Cron. Alle Zeitpläne mit Terminen, Abschalten einzelner Zeitpläne, Umstellung von einer bestehenden Crontab.
---

# Regelmäßige Aufgaben

Wiederkehrende Aufgaben laufen als **Zeitpläne im Worker** (Dienst `worker`), nicht mehr per Crontab auf dem Host. Die Zeitpläne stehen im Code und sind damit in jeder Installationsart gleich: ein Server mit Docker Compose, mehrere Server oder Kubernetes. Läuft kein Worker, laufen auch keine Zeitpläne; die Anwendung meldet das (siehe [Überwachung](#ueberwachung)).

So arbeiten die Zeitpläne:

- Der Worker legt je Termin genau einen Auftrag an, auch wenn mehrere Worker laufen.
- Zeiten gelten in der Zeitzone der Anwendung (Europe/Berlin).
- Ein verpasster Termin, etwa während eines Updates, wird in der Regel einmal nachgeholt. Ein neuer Zeitplan beginnt mit seinem nächsten Termin.
- Verwaltungsbefehle laufen wie früher der Cron-Eintrag als eigener Prozess im Worker-Container, mit Sperre gegen parallele Läufe und fester Zeitgrenze. Ein gescheiterter Lauf wird nicht wiederholt; der nächste Termin ist die Wiederholung. Er erscheint im Admin unter „Aufträge“ und in der Metrik `mandari_tasks_dead`.
- Die Ausgabe steht im Protokoll des Workers: `docker compose logs worker`.

## Zeitpläne mit Verwaltungsbefehlen

| Zeitplan | Wann | Aufgabe |
|----------|------|---------|
| `befehl:send_session_reminders` | täglich 07:00 | [Fristen-Erinnerungen](../session/fristen-erinnerungen.md) des Sitzungsdienstes |
| `befehl:send_task_due_reminders` | täglich 07:15 | Erinnerungen an fällige Aufgaben |
| `befehl:send_question_reminders` | täglich 07:30 | Erinnerungen zu Ratsfragen; ohne Wirkung, solange die Ratsfragen pausiert sind |
| `befehl:fetch_person_photos` | montags 03:00 | Personenfotos aus den Quellsystemen |
| `befehl:sync_plan_boundaries` | täglich 04:50 | Umringe von Bebauungsplänen aus den Geodiensten |
| `befehl:cleanup_orphaned_accounts` | täglich 03:45 | verwaiste Konten nach Frist löschen |
| `befehl:cache_files` | stündlich :40 | [Dokument-Cache](dokument-cache.md): fehlende Dateien nachladen, neueste zuerst (`--limit 400`) |
| `befehl:loeschabgleich` | stündlich :15 | Löschabgleich der Dokumente mit den Quellen |
| `befehl:dokumentablage` | stündlich :50 | Dokumentablage aufräumen, mit Objektspeicher vorher hochladen; hält die Obergrenze `FILE_CACHE_MAX_TOTAL_GB` ein |
| `befehl:generate_alerts` | täglich 07:45 | Benachrichtigungen der Abos zu Themen und Orten; nur mit `INSIGHT_SUBSCRIPTIONS_ENABLED=true` |
| `befehl:send_digest` | montags 08:00 | Wochenmail dieser Abos; nur mit `INSIGHT_SUBSCRIPTIONS_ENABLED=true` |
| `befehl:check_source_health` | stündlich :15 | Zustand der Quellen, Alarme und Entwarnungen ([Betriebsmonitor](monitoring.md)) |
| `befehl:check_service_levels` | täglich 06:30 | Service-Level: Plattenplatz, Zertifikate, Fehlerquote, Warteschlangen |
| `befehl:availability_report` | am 1. um 00:15 | Verfügbarkeitsbericht des Vormonats; nur mit `GATUS_URL` |
| `befehl:verify_audit_chain` | täglich 04:20 | Hash-Ketten der Protokollierung prüfen; ein Befund lässt den Lauf scheitern |
| `befehl:purge_security_audit_log` | täglich 04:40 | Sicherheitsprotokoll nach Frist löschen |
| `befehl:session_privacy_purge` | am 1. um 05:00 | Anonymisierungs- und Löschlauf nach den Fristen je Mandant ([Löschkonzept](../datenschutz/loeschkonzept.md)) |
| `befehl:build_meeting_packages` | jede Minute | Sitzungsmappen erzeugen, die die Oberfläche angefordert hat |
| `befehl:events_purge` | täglich 04:10 | Journal der Ereignistechnik nach Frist aufräumen; nur mit `EVENTS_JOURNAL_PURGE_ENABLED=true` |

## Weitere Zeitpläne

| Zeitplan | Wann | Aufgabe |
|----------|------|---------|
| `insight_sync.schedules.haengende_syncs_bereinigen` | alle 5 Minuten | Sync-Protokolle, die länger als 15 Minuten laufen, als fehlgeschlagen markieren |
| `insight_core.schedules.verortung_automatisch` | alle 15 Minuten (`GEOREF_AUTO_INTERVAL_MINUTES`) | begrenzter Verortungslauf für Vorlagen, abschaltbar mit `GEOREF_AUTO_ENABLED=false` |
| `insight_core.schedules.kommunenverzeichnis_abgleichen` | stündlich | gelistete Kommunen ins Kommunenverzeichnis übernehmen |
| `insight_core.schedules.rueckmeldungen_aufraeumen` | täglich 03:50 | Rückmeldungen zu Seiten nach Frist löschen |
| `insight_core.schedules.texterkennung_einplanen` | alle 2 Minuten | Aufträge für die Texterkennung einreihen; nur mit `TEXT_EXTRACTION_RUNNER=worker` |
| `apps.work.schedules.fraktionserinnerungen_senden` | alle 15 Minuten | Erinnerungen an Fraktionssitzungen |
| `apps.work.schedules.fraktionseinladungen_senden` | alle 15 Minuten | automatische Einladungen, Freigabe-Hinweise, Erinnerungen zum Eintragen von TOPs |
| `apps.work.schedules.fraktionssitzungen_erzeugen` | alle 60 Minuten (`FACTION_SCHEDULE_INTERVAL_MINUTES`) | Fraktionssitzungen aus Sitzungsreihen anlegen |
| `apps.work.schedules.ris_verknuepfungen_abgleichen` | alle 15 Minuten (`WORK_RIS_RELINK_INTERVAL_MINUTES`) | Work-Daten nach einer Neuveröffentlichung im RIS umhängen; tut nichts, solange `WORK_RIS_RELINK=aus` |
| `apps.work.schedules.fraktionsprotokolle_versenden` | alle 15 Minuten | automatischer Protokollversand, wenn die Organisation ihn eingeschaltet hat |
| `apps.events.schedules.idempotenzschluessel_aufraeumen` | täglich 03:40 | Idempotenzschlüssel nach `EVENTS_IDEMPOTENCY_RETENTION_DAYS` löschen |
| `apps.events.schedules.auftraege_aufraeumen` | täglich 03:50 | beendete Aufträge löschen: erledigte nach `EVENTS_TASKS_DONE_RETENTION_DAYS`, tote und fehlgeschlagene nach `EVENTS_TASKS_DEAD_RETENTION_DAYS` Tagen |
| `apps.common.schedules.postausgang_aufraeumen` | täglich 03:55 | Postausgang des Mail-Dienstes nach Frist leeren |
| `hub.live.schedules.live_status_abfragen` | jede Minute | Status der Live-Übertragungen abfragen; nur mit `LIVE_UEBERTRAGUNG_AKTIV=true` |
| `hub.live.schedules.live_protokoll_aufraeumen` | täglich 04:20 | Protokoll der Live-Übertragungen nach `LIVE_PROTOKOLL_TAGE` löschen |

Die aktuelle Liste mit dem zuletzt geplanten Termin zeigt:

```bash
docker compose exec worker python manage.py events_scheduler --list
```

## Von Hand ausführen

Ein Verwaltungsbefehl, den ein Zeitplan bedient, endet beim Aufruf von Hand mit dem Hinweis „läuft als Zeitplan im Worker – Aufruf übersprungen“ (Exit-Code 0). So entstehen keine Doppelläufe. Einen echten Lauf erzwingt `--trotz-zeitplan`:

```bash
docker compose exec worker python manage.py cache_files --trotz-zeitplan
```

Aufrufe, die nur lesen oder berichten, laufen immer: `--dry-run`, `check_source_health --report`, `check_service_levels --report`, `cache_files --stats`, `loeschabgleich --robots`, `dokumentablage` ohne Schritt und `availability_report` ohne `--out`.

| Befehl | Nützliche Optionen |
|--------|--------------------|
| `cache_files` | `--limit N`, `--body <slug>`, `--stats` |
| `check_source_health` | `--report` für einen Bericht ohne Versand |
| `send_session_reminders` | `--tenant <slug>`, `--dry-run` |
| `session_privacy_purge` | `--tenant <slug>`, `--dry-run` |
| `fetch_person_photos` | `--body <slug>`, `--force` |
| `purge_deleted` | Löscht als gelöscht markierte Objekte endgültig, nur auf Aufforderung einer Kommune: `--body <slug>`, `--older-than N`, `--ids …`, `--yes`. Kein Zeitplan. |

## Einzelne Zeitpläne abschalten { #einzelne-zeitplaene-abschalten }

`EVENTS_SCHEDULES_DISABLED` nimmt die Namen kommagetrennt auf, zum Beispiel `EVENTS_SCHEDULES_DISABLED=befehl:build_meeting_packages`. Danach Worker und Anwendung neu starten (`docker compose up -d worker mandari`). Die Termine verstreichen dann ohne Auftrag; wird der Zeitplan wieder eingeschaltet, geht es mit dem nächsten Termin weiter, nichts wird nachgeholt.

## Was auf dem Host bleibt

In der Crontab des Hosts stehen nur noch Aufgaben des Betriebssystems:

- die Datensicherung mit `./backup.sh`, die der Installer täglich um 02:00 einträgt (siehe [Updates und Backups](updates-backups.md)),
- bei einer Sicherung mit restic deren Überwachung (`backup-watchdog.sh`),
- auf Wunsch der Neustart ungesunder Container (`deploy/scripts/restart-unhealthy.sh`) und der Alarm aus dem Systemjournal (`deploy/logging/journal-alert.sh`).

Steht danach noch ein `manage.py`-Aufruf in der Crontab, gehört er als Zeitplan in den Code.

## Umstellung von einer bestehenden Crontab

Ältere Installationen hatten die Verwaltungsbefehle in der Crontab des Hosts. Die Umstellung läuft ohne Doppelläufe und ohne Lücke:

1. **Worker prüfen:** `docker compose ps worker` zeigt `healthy`, `/health/` meldet `"worker": "ok"`.
2. **Update einspielen.** Ab jetzt planen die Zeitpläne. Ein noch vorhandener Cron-Eintrag erkennt den Worker und endet mit „Aufruf übersprungen“; läuft kein Worker, arbeitet er wie bisher. Kontrolle nach einem Tag:

    ```bash
    grep -h "Aufruf übersprungen" /var/log/mandari-*.log | tail
    docker compose logs --since 24h worker | grep "Zeitplan befehl:"
    ```

3. **Crontab bereinigen:** erst sichern (`crontab -l > ~/crontab-vorher.txt`), dann die Zeilen der Verwaltungsbefehle entfernen.
4. **Rückweg:** einzelne Zeitpläne mit `EVENTS_SCHEDULES_DISABLED` abschalten und den gesicherten Cron-Eintrag wieder eintragen.

## Überwachung { #ueberwachung }

Braucht die Installation einen Worker (Standard, wegen der Zeitpläne) und läuft keiner, melden `/health/` und `/health/ready/` „degraded“, und Admin-Startseite und Betriebsmonitor zeigen den Hinweis „Worker“. Die Anwendung bleibt dabei in Betrieb. Wer den Worker an eine Statusseite melden will, setzt `WORKER_PUSH_URL` (siehe [Konfiguration](konfiguration.md#worker-auftraege-und-ereignisse)).
