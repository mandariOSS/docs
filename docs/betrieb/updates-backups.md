---
title: Updates und Backups
description: mandari aktualisieren, Datenbank und Dateien sichern und wiederherstellen. Versionierte Images, Migrationen, was in ein Backup gehört.
---

# Updates und Backups

## Versionen

Die Container-Images erscheinen auf der GitHub Container Registry:

| Image | Inhalt |
|-------|--------|
| `ghcr.io/mandarioss/mandari:<tag>` | Anwendung (Insight, Work, Session) |
| `ghcr.io/mandarioss/ingestor:<tag>` | Ingestor und Texterkennung |
| `ghcr.io/mandarioss/website:<tag>` | Öffentliche Website |

Jeder Build trägt ein unveränderliches Tag aus Branch und Commit (`main-<kurzer-hash>`) sowie das bewegliche Tag des Branches. Für den Betrieb empfehlen wir das unveränderliche Tag in `IMAGE_TAG`, damit ein Update eine bewusste Entscheidung ist. Release-Notes erscheinen unter [GitHub Releases](https://github.com/mandariOSS/mandari/releases).

## Update durchführen

1. **Backup** anlegen, siehe unten.
2. Release-Notes lesen. Migrationen sind additiv angelegt, trotzdem können einzelne Releases Hinweise enthalten.
3. Neues Tag in `.env` setzen und den Stack aktualisieren:

    ```bash
    cd /opt/mandari
    sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=main-abc1234/' .env
    docker compose pull
    docker compose up -d
    docker compose exec mandari python manage.py migrate --noinput
    ```

4. Prüfen: `curl -sf https://<domain>/health` antwortet mit `OK`, der [Betriebsmonitor](monitoring.md) zeigt grün, die Sync-Läufe laufen weiter.

!!! tip "Reihenfolge bei Schemaänderungen"
    Anwendung und Ingestor teilen sich die Datenbank. Bei Releases mit Migrationen erst die Anwendung aktualisieren und migrieren, dann den Ingestor neu starten.

## Was in ein Backup gehört

| Bestandteil | Warum |
|-------------|-------|
| **Datenbank** (PostgreSQL) | Alle Inhalte, Nutzer, Einstellungen, Audit-Logs |
| **`.env`** | Schlüssel. Ohne `ENCRYPTION_MASTER_KEY` sind verschlüsselte Felder im Datenbank-Backup wertlos. Getrennt und sicher aufbewahren. |
| **Medien** (`MEDIA_ROOT`) | Hochgeladene Dateien, Logos, Personenfotos, Demo-PDFs |
| **Dokument-Cache** (`OPARL_FILES_ROOT`) | Optional. Lässt sich aus den Quellen wieder aufbauen, ist aber groß und dauert. |

Elasticsearch muss nicht gesichert werden, der Index lässt sich aus der Datenbank neu aufbauen.

## Datenbank sichern

```bash
# Dump erzeugen (komprimiert)
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" > mandari-$(date +%F).dump

# Wiederherstellen in eine leere Datenbank
docker compose exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < mandari-2026-09-08.dump
```

Ein täglicher Cron mit Aufbewahrung von mindestens 14 Tagen und einer Kopie außerhalb des Servers ist das Minimum. Die Wiederherstellung einmal im Quartal testen.

## Wiederherstellung im Überblick

1. Server mit Docker vorbereiten, Compose-Dateien und die gesicherte `.env` einspielen.
2. Stack ohne Anwendung starten: `docker compose up -d postgres redis elasticsearch`.
3. Datenbank-Dump einspielen, Medien und optional den Dokument-Cache zurückkopieren.
4. Anwendung starten, migrieren, Suchindex neu aufbauen: `docker compose exec mandari python manage.py setup_elasticsearch` und Reindex über die Admin-Aktionen oder die Management-Befehle der Suche.
5. DNS auf den neuen Server zeigen lassen. Caddy holt die Zertifikate automatisch.
