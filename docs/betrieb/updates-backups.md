---
title: Updates und Backups
description: mandari aktualisieren und sichern. Versions-Tags der Images, Update mit update.sh samt Rückfall, Sicherung mit backup.sh, verschlüsselte Sicherung an zwei Standorten mit restic, Wiederherstellung.
---

# Updates und Backups

## Versionen

Die Container-Images liegen in der GitHub Container Registry. Ein einziges `IMAGE_TAG` in der `.env` gilt für alle drei:

| Image | Inhalt |
|-------|--------|
| `ghcr.io/mandarioss/mandari:<tag>` | Anwendung (Insight, Work, Session) und die Worker |
| `ghcr.io/mandarioss/ingestor:<tag>` | Ingestor und Texterkennung |
| `ghcr.io/mandarioss/website:<tag>` | Öffentliche Website |

| Tag | Bedeutung |
|-----|-----------|
| `v0.11.0` usw. | eine veröffentlichte Version (Release) mit Changelog, siehe [GitHub Releases](https://github.com/mandariOSS/mandari/releases) |
| `latest` | beweglich: der jüngste Stand des Zweigs `main`; auch ein Release setzt `latest` |
| `main-<commit>` | unveränderlicher Stand eines Commits auf `main` |
| `dev`, `dev-<commit>` | Entwicklungsstand, instabil und nicht für den Produktivbetrieb |

Für den Betrieb empfehlen wir eine Release-Version, damit jedes Update eine bewusste Entscheidung ist. Versionierung, Release-Rhythmus und Supportzeiträume regelt die [Release- und Support-Politik](../entwicklung/release-politik.md).

## Aktualisieren mit update.sh

```bash
./update.sh                  # auf latest
./update.sh --tag v0.11.0    # auf eine bestimmte Version
./update.sh --tag dev        # Entwicklungsstand (instabil)
./update.sh --dry-run        # nur prüfen, nichts ändern
./update.sh --rollback       # zurück auf die Version vor dem letzten Update
```

| Option | Wirkung |
|--------|---------|
| `--tag <tag>` | Zielversion, Vorgabe `latest` |
| `--dry-run` | nur prüfen, nichts ändern |
| `--rollback` | zurück auf die Version aus `.env.pre-update` |
| `--no-backup` | die Rückfrage nach einer Sicherung überspringen |
| `--no-cleanup` | alte Images nicht aufräumen |

So läuft ein Update:

1. Das Skript prüft, ob es das Ziel-Tag für alle drei Images gibt, und bricht sonst ab, bevor es etwas ändert.
2. Es bietet eine Sicherung mit `./backup.sh` an und merkt sich die bisherige `.env` als `.env.pre-update`.
3. Liegt die Installation in einem Git-Repository, holt es den neuesten Stand des aktuellen Zweigs.
4. Es zieht die neuen Images; die laufenden Dienste arbeiten weiter.
5. Ingestor, Protokoll-Orchestrator und Worker halten während der Migrationen an. Die verträglichen Migrationen laufen vor dem Umschalten in einem eigenen Container (`safemigrate`), ebenso die der Website.
6. Die Worker starten mit dem neuen Image vor der Anwendung (Migration, dann Worker, dann Web). Danach tauscht das Skript die Container der Anwendung und der Website; Caddy hält Anfragen währenddessen kurz an.
7. Eine Anwendungsprüfung im Container ruft unter anderem Bereitschaft, Anmeldeseite, Bürgerportal und OParl-System ab. Scheitert sie, schaltet das Skript selbst auf das vorherige Image zurück.
8. Zum Schluss spielt es die übrigen Migrationen ein und startet Ingestor und Protokoll-Orchestrator mit dem neuen Image.

Welche Dienste während der Migrationen stehen, legt `WORKER_SERVICES` fest (Vorgabe: `ingestor minutes-orchestrator worker worker-heavy worker-live`). Wer einen weiteren Dienst in einer eigenen Compose-Datei betreibt, ergänzt ihn dort, zum Beispiel `WORKER_SERVICES="ingestor minutes-orchestrator worker worker-heavy ocr-worker"` in der `.env`.

!!! note "Migrationen und Rückfall"
    Migrationen sind abwärtsverträglich angelegt. Der Rückfall rollt deshalb nur das Image zurück, keine Migrationen. Lesen Sie vor einem Update trotzdem die Release-Notes; einzelne Releases nennen dort Schritte nach dem Update.

Für nicht interaktive Updates (Betrieb, Automatisierung) gibt es `deploy/scripts/deploy.sh` mit derselben Prüfung und demselben Rückfall, Beschreibung in `DEPLOYMENT.md` im Repository.

## Sicherung mit backup.sh { #sicherung-mit-backupsh }

`./backup.sh` schreibt ein Archiv nach `./backups/`; die letzten sieben bleiben liegen. Der Installer richtet dafür einen täglichen Lauf um 02:00 per Crontab ein (`./backup.sh --quiet`).

| Inhalt | Im Archiv | Abschalten |
|--------|-----------|------------|
| Datenbanken der Anwendung und der Website | `postgres.sql`, `postgres_website.sql` (`pg_dump`) | – |
| Uploads (`/app/media`, Volume `mandari_media`) | `media.tar` | `--no-media` bzw. `BACKUP_NO_MEDIA=true` |
| Dokument-Cache (`/app/files`, Volume `mandari_files`) | `files.tar` | `--no-files` bzw. `BACKUP_NO_FILES=true` |
| Konfiguration (`.env`) | `config.env.enc`, nur verschlüsselt | ohne Passphrase ausgelassen |
| Suchindex, Redis, TLS-Zertifikate | nicht enthalten | Der Suchindex wird bei der Wiederherstellung neu aufgebaut, Caddy holt neue Zertifikate. |

| Option | Wirkung |
|--------|---------|
| `VERZEICHNIS` | anderes Zielverzeichnis statt `./backups/` |
| `--no-media`, `--no-files` | Uploads bzw. Dokument-Cache auslassen. Der Dokument-Cache lässt sich aus den Ratsinformationssystemen neu laden. |
| `--verify` | Archiv nach dem Erstellen prüfen |
| `--quiet` | nur Warnungen und Fehler ausgeben (für Cron) |
| `--restore <datei>` | aus einem Archiv wiederherstellen |
| `S3_BACKUP_BUCKET` | Archiv zusätzlich nach `s3://<bucket>/mandari/` hochladen |

Ein unvollständiger Lauf (Uploads nicht lesbar, Passphrase-Datei fehlt) schreibt das Archiv trotzdem, endet aber mit Exit-Code 1 und räumt dann keine alten Archive auf.

### Konfiguration nur verschlüsselt

Die `.env` enthält alle Schlüssel, darunter den `ENCRYPTION_MASTER_KEY`. `backup.sh` legt sie deshalb nur verschlüsselt ins Archiv (`openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -md sha256`). Die Passphrase kommt aus `BACKUP_PASSPHRASE` (nur Umgebung) oder aus der ersten Zeile der Datei `BACKUP_PASSPHRASE_FILE` (Vorgabe `./.backup-passphrase`). Ohne Passphrase fehlt die Konfiguration im Archiv, und jeder Lauf warnt.

```bash
(umask 077; openssl rand -base64 32 > .backup-passphrase)
./backup.sh --verify
```

Verwahren Sie die Passphrase **zusätzlich außerhalb des Servers**, etwa in einem Passwort-Manager. Für eine Wiederherstellung auf einem neuen Server wird sie gebraucht.

### Wiederherstellen

```bash
./backup.sh --restore backups/mandari_backup_<zeit>.tar.gz
```

Das Skript liest zuerst das ganze Archiv und entschlüsselt die Konfiguration; scheitert eins davon, bricht es ab, ohne etwas zu verändern. Nach einer Rückfrage stoppt es die Dienste, setzt die Konfiguration ein, spielt jede Datenbank zuerst in eine Zwischen-Datenbank ein und tauscht sie erst danach aus. Vor dem Start des Workers hebt es die Folgenummer der Ereignistechnik an (`events_after_restore --apply`), spielt Uploads und Dokument-Cache zurück, startet alle Dienste, führt `migrate` aus und baut den Suchindex neu auf.

Auf einem **neuen Server** genügt: Docker installieren, Repository klonen, Archiv und Passphrase bereitstellen und direkt `./backup.sh --restore …` aufrufen, ohne vorher `install.sh` auszuführen. Danach die tägliche Sicherung wieder eintragen:

```cron
0 2 * * * cd /opt/mandari && ./backup.sh --quiet >> /opt/mandari/logs/backup.log 2>&1
```

Spielen Sie eine Wiederherstellung regelmäßig in einer Testumgebung durch; erst sie zeigt, dass die Sicherung taugt.

## Verschlüsselte Sicherung an zwei Standorten (restic)

Für den Produktivbetrieb liegt im Repository unter `deploy/backup/` ein eigener Sicherungsdienst mit [restic](https://restic.net/). Er läuft als Container neben der Installation und sichert täglich verschlüsselt in zwei Repositorys an getrennten Standorten, per SFTP (ein reiner SFTP-Speicher genügt).

| Was | Wann (Standard) |
|-----|-----------------|
| Sicherung: alle PostgreSQL-Datenbanken einzeln (`pg_dump`) samt Rollen, Dokument-Cache, Uploads, Installationsverzeichnis mit `.env`, TLS-Daten von Caddy und Protokolle | täglich 02:30 |
| Aufbewahrung: je Tag der letzte Stand, höchstens 30 Tage | nach jeder Sicherung |
| Integritätsprüfung (`restic check`, liest rotierend ein Viertel der Daten zurück) | sonntags 06:30 |
| Wiederherstellungstest in eine Wegwerf-Datenbank | am 3. jedes Monats, 04:30 |
| Überwachung auf dem Host (`backup-watchdog.sh`): Mail bei Fehler, veralteter Sicherung oder fehlgeschlagener Prüfung | stündlich |

restic verschlüsselt vor der Übertragung; das Zielsystem sieht nur verschlüsselte Blöcke. **Das restic-Passwort ist der Schlüssel zu allen Sicherungen** und gehört zusätzlich außerhalb des Servers verwahrt. Einrichtung, Bedienung und Wiederherstellung beschreibt `docs/BACKUP.md` im Repository.

## Was in jede Sicherung gehört

| Bestandteil | Warum |
|-------------|-------|
| **Datenbank** (PostgreSQL) | Alle Inhalte, Nutzer, Einstellungen, Audit-Logs, dazu das Journal der Ereignistechnik und die Aufträge |
| **`.env`** | Schlüssel. Ohne `ENCRYPTION_MASTER_KEY` sind verschlüsselte Felder im Datenbank-Backup wertlos. |
| **Uploads** (`/app/media`) | Hochgeladene Dateien, Logos, Personenfotos, Sitzungsmappen, Archivpakete und Berichte der Zeitpläne |
| **Dokument-Cache** (`/app/files`) | Optional. Lässt sich aus den Quellen wieder aufbauen, ist aber groß und dauert. |

Elasticsearch muss nicht gesichert werden, der Index lässt sich aus der Datenbank neu aufbauen.
