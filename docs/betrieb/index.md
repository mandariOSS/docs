---
title: Self-Hosting mit Docker
description: mandari auf eigener Infrastruktur betreiben. Voraussetzungen, Dienste der Installation, Installer mit seinen Optionen, Installation mit Docker Compose, erste Schritte nach dem Start.
---

# Self-Hosting mit Docker

!!! tip "Kubernetes"
    Diese Seite beschreibt den Betrieb auf einem einzelnen Server mit Docker Compose.
    Für einen Cluster gibt es ein Helm-Chart und einen eigenen Installer:
    [Betrieb in Kubernetes](kubernetes.md).

mandari ist Open Source und vollständig selbst betreibbar: volle Datenhoheit auf Ihrer eigenen Infrastruktur. Diese Seite führt durch die Installation, die weiteren Seiten dieses Bereichs durch Konfiguration, regelmäßige Aufgaben, Quellen, Überwachung und Updates.

## Voraussetzungen

- Linux-Server, zum Beispiel Ubuntu 22.04 oder neuer, Debian 12 oder Rocky 9, mit mindestens 4 GB Arbeitsspeicher. Den meisten Speicher brauchen die Suche und die Texterkennung. Auf einem Server mit 4 GB senken Sie die Grenzen des Dienstes `worker-heavy`, zum Beispiel `WORKER_HEAVY_MEM_LIMIT=2g` und `WORKER_HEAVY_OCR_MEMORY_LIMIT_MB=1024` (siehe [Konfiguration](konfiguration.md#worker-auftraege-und-ereignisse)).
- Docker mit Docker Compose. Fehlt Docker, installiert der Installer es mit.
- Eine Domain mit DNS-Eintrag auf den Server. TLS-Zertifikate holt der mitgelieferte Caddy automatisch; dafür müssen die Ports 80 und 443 aus dem Internet erreichbar sein.
- Ausreichend Plattenplatz für den [Dokument-Cache](dokument-cache.md), abhängig von den angebundenen Kommunen.

## Dienste der Installation

`docker-compose.yml` startet diese Dienste. Container und Volumes tragen den Projektnamen `mandari` (änderbar mit `COMPOSE_PROJECT_NAME`, etwa für eine zweite Installation auf demselben Server).

| Dienst | Aufgabe |
|--------|---------|
| `caddy` | Reverse Proxy, TLS-Zertifikate, Verteilung der Pfade auf Anwendung und Website |
| `mandari` | Django-Anwendung mit Insight, Work und Session |
| `worker` | Ereignisse, Aufträge und alle [Zeitpläne](cron.md) (`manage.py events_worker`, Warteschlangen `default`, `mail`, `index`, `adapter`). Ohne ihn laufen keine Erinnerungen, kein Nachladen von Dokumenten und keine Sitzungsmappen. |
| `worker-heavy` | Aufträge der Texterkennung und der KI (Warteschlangen `ocr` und `ai`) mit eigener Speichergrenze, Standard 3 GB. Er arbeitet erst, wenn die Texterkennung auf den Worker umgestellt ist (`TASKS_BACKEND=journal` und `TEXT_EXTRACTION_RUNNER=worker`); bis dahin wartet er. |
| `worker-live` | Live-Übertragungen von Gremiensitzungen (Warteschlange `live`). Solange `LIVE_UEBERTRAGUNG_AKTIV` aus ist, wartet er nur. |
| `minutes-orchestrator` | Protokollierung: legt GPU-Rechenknoten für die Transkription nach Bedarf an und löscht sie wieder. Tut nichts, solange im Admin unter *System → GPU-Rechenknoten* „Rechenknoten aktiv“ ausgeschaltet ist. |
| `website` | Website mit Wagtail aus dem Repository [mandariOSS/marketing-website](https://github.com/mandariOSS/marketing-website), dieselbe wie auf mandari.de, mit eigener Datenbank `mandari_website`. Caddy gibt ihr alle Pfade, die nicht zur Anwendung gehören, auch die Startseite `/`. Das Image hat dieselben Versions-Tags wie die Anwendung. |
| `ingestor` | Abgleich der OParl- und Scraper-Quellen; erkennt im Standard auch den Text der Dokumente (`TEXT_EXTRACTION_RUNNER=ingestor`) |
| `postgres` | Datenbank (PostgreSQL 16) |
| `elasticsearch` | Volltextsuche (Elasticsearch 8) |
| `redis` | Cache, Sitzungen, Sperren und Echtzeitfunktionen (Redis 7) |

Alle Dienste laufen auf **einer Domain** hinter Caddy. Zur Anwendung gehen `/insight/`, `/work/`, `/session/`, `/accounts/`, `/admin/`, `/api/`, `/public/`, `/ws/`, `/oparl/`, `/nachweis/`, `/kalender/`, `/feedback/`, `/csp-report/`, `/ladung/`, `/data/dcat/`, `/static/`, `/media/`, die Sitemaps des Bürgerportals und die Dateien der App (`/manifest.webmanifest`, `/sw.js`, `/offline/`). Alles andere geht an die Website.

## Installation

=== "Interaktiver Installer"

    ```bash
    git clone https://github.com/mandariOSS/mandari.git
    cd mandari
    ./install.sh
    ```

    Der Installer fragt Domain, E-Mail-Adresse für die Zertifikate, Zeitzone, Administrationskonto und den Release-Kanal (`latest` oder `dev`) ab. Danach erzeugt er alle Schlüssel und die `.env`, startet die Dienste in der richtigen Reihenfolge, führt die Migrationen aus, legt Rollen, Suchindex und das Administrationskonto an und übernimmt die mitgelieferte Liste der OParl-Quellen. Welche davon aktiv sein sollen, fragt er nach; ohne Rückfragen bleiben alle inaktiv. Zum Schluss trägt er eine tägliche Sicherung um 02:00 in die Crontab ein.

=== "Ohne Rückfragen"

    ```bash
    DOMAIN=ris.meine-kommune.de ACME_EMAIL=it@meine-kommune.de \
    ADMIN_EMAIL=admin@meine-kommune.de ADMIN_PASSWORD='EinLangesPasswort' \
    ./install.sh --unattended
    ```

    Die Werte kommen aus Umgebungsvariablen: `DOMAIN` (Vorgabe `localhost`), `ACME_EMAIL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `TZ` (Vorgabe `Europe/Berlin`), dazu optional `POSTGRES_USER`, `POSTGRES_DB`, `REDIS_MAXMEMORY` und `INGESTOR_INTERVAL`. Ohne `--tag` gilt `latest`.

=== "Docker Compose von Hand"

    Aus dem geklonten Repository, in derselben Reihenfolge wie der Installer:

    ```bash
    git clone https://github.com/mandariOSS/mandari.git && cd mandari
    cp .env.example .env
    nano .env            # Domain, Zugangsdaten und Schlüssel setzen, siehe Konfiguration

    docker compose up -d postgres redis elasticsearch
    docker compose up -d mandari
    docker compose exec mandari python manage.py migrate
    docker compose exec mandari python manage.py setup_roles
    docker compose exec mandari python manage.py setup_elasticsearch
    docker compose exec mandari python manage.py createsuperuser
    docker compose up -d worker worker-heavy worker-live
    docker compose up -d website
    docker compose exec website python manage.py migrate
    docker compose up -d
    ```

    Wichtig ist die Reihenfolge: Ingestor und Worker starten erst nach den Migrationen der Anwendung. Startet der Ingestor vorher, legt er eigene Tabellen an, und die Migrationen scheitern.

### Optionen des Installers

| Option | Wirkung |
|--------|---------|
| `--tag <tag>` | Version der Images `mandari`, `ingestor` und `website`: `latest` (Vorgabe), `dev` (Entwicklungsstand, instabil) oder eine veröffentlichte Version wie `v0.11.0` ([Releases](https://github.com/mandariOSS/mandari/releases)). Gibt es das Tag nicht für alle drei Images, bricht der Installer ab, bevor er etwas verändert. |
| `--unattended` | Ohne Rückfragen, Werte aus Umgebungsvariablen (siehe oben). Liegt im Verzeichnis schon eine Installation (eine `.env`), bricht er mit Exit-Code 1 ab, ohne etwas anzufassen. Eine bestehende Installation aktualisiert `./update.sh`. |
| `--reinstall-destroy-data` | Nur zusammen mit `--unattended`: eine bestehende Installation verwerfen und neu aufsetzen. **Löscht alle Daten** (Datenbank, Uploads, Dokument-Cache, Suchindex, Zertifikate) und erzeugt neue Schlüssel. Die bisherige `.env` bleibt als `.env.vor-neuinstallation-<Zeitstempel>` liegen; sie enthält den alten `ENCRYPTION_MASTER_KEY`, ohne den ältere Sicherungen nicht lesbar sind. Vorher `./backup.sh` ausführen. Interaktiv fragt der Installer stattdessen nach. |
| `-h`, `--help` | Hilfe anzeigen |

Mehrere Installationen auf einem Server brauchen unterschiedliche Projektnamen, zum Beispiel `COMPOSE_PROJECT_NAME=mandari-test ./install.sh`.

!!! danger "Schlüssel sichern"
    Die Datei `.env` enthält den Django-`SECRET_KEY` und den `ENCRYPTION_MASTER_KEY`. Ohne den Master-Key sind verschlüsselte Felder in Sicherungen nicht mehr lesbar. Sichern Sie die Datei getrennt vom Server und tauschen Sie den Master-Key nie einfach aus; für einen Wechsel gibt es einen eigenen Ablauf mit `ENCRYPTION_MASTER_KEY_PREVIOUS` (siehe [Konfiguration](konfiguration.md#pflichtwerte)).

## Erste Schritte nach dem Start

1. **Prüfen:** `https://<domain>/health/ready/` meldet `"status": "ok"`, `docker compose ps` zeigt `worker` und `worker-heavy` als `healthy`.
2. **Anmelden** unter `https://<domain>/admin/` mit dem Administrationskonto. Beim Installer ist es schon angelegt, sonst mit `createsuperuser` (siehe oben).
3. **E-Mail einrichten** in den Systemeinstellungen im Admin und eine Testmail senden. Die Variablen `EMAIL_*` reicht `docker-compose.yml` nicht an die Dienste weiter (siehe [Konfiguration](konfiguration.md#e-mail)).
4. **Quellen anbinden:** Im Admin unter *OParl-Quellen* die gewünschten Kommunen aktivieren oder neu eintragen, siehe [Quellen anbinden](quellen-anbinden.md).
5. **Sicherung einrichten:** Passphrase für die Konfiguration in der Sicherung anlegen und `./backup.sh --verify` ausführen, siehe [Updates und Backups](updates-backups.md#sicherung-mit-backupsh).
6. **Betriebsmonitor** unter `/admin/monitoring/` prüfen, siehe [Betriebsmonitor](monitoring.md). Die [regelmäßigen Aufgaben](cron.md) laufen von selbst im Worker.
7. Optional eine **Demo-Umgebung** anlegen, um alle drei Portale mit Beispieldaten zu sehen, siehe [Demo-Umgebung](demo-umgebung.md).

## Provisioning-API

Für den Betrieb als Dienst kann ein externes System Organisationen über `/api/provisioning/` anlegen und verwalten. Die API wird ausschließlich über die Variable `PROVISIONING_API_KEY` aktiviert. Ohne gesetzten Schlüssel antworten alle Anfragen mit 404, sodass Community-Installationen keine offene Angriffsfläche haben. `docker-compose.yml` reicht die Variable nicht durch; wer die API braucht, trägt sie im Abschnitt `environment` des Dienstes `mandari` ein.

## Support

Community-Support läuft über [GitHub-Issues](https://github.com/mandariOSS/mandari/issues). Für Kommunen bieten wir betreutes Hosting und Support-Verträge an, siehe [mandari.de/kommunen/](https://mandari.de/kommunen/).
