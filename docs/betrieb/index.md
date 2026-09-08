---
title: Self-Hosting mit Docker
description: mandari auf eigener Infrastruktur betreiben. Voraussetzungen, Komponenten, Installation mit Docker Compose, erste Schritte nach dem Start.
---

# Self-Hosting mit Docker

mandari ist Open Source und vollständig selbst betreibbar: volle Datenhoheit auf eurer eigenen Infrastruktur. Diese Seite führt durch die Installation, die weiteren Seiten dieses Bereichs durch Konfiguration, regelmäßige Aufgaben, Quellen, Überwachung und Updates.

## Voraussetzungen

- Linux-Server, Ubuntu 22.04 oder neuer empfohlen, mindestens 2 CPU-Kerne und 8 GB RAM. Elasticsearch und Texterkennung sind die Speicherfresser.
- Docker und Docker Compose
- Eine Domain mit DNS-Eintrag auf den Server. TLS-Zertifikate holt der mitgelieferte Caddy automatisch.
- Ausreichend Plattenplatz für den [Dokument-Cache](dokument-cache.md), abhängig von den angebundenen Kommunen

## Komponenten

| Container | Aufgabe |
|-----------|---------|
| `caddy` | Reverse Proxy, TLS-Zertifikate, Routing zwischen Anwendung und Website |
| `mandari` | Django-Anwendung mit Insight, Work und Session |
| `website` | Öffentliche Website (Wagtail), optional |
| `ingestor` | Synchronisation der OParl- und Scraper-Quellen, Texterkennung |
| `postgres` | Datenbank (PostgreSQL 16) |
| `elasticsearch` | Volltextsuche (Elasticsearch 8) |
| `redis` | Cache und Echtzeitfunktionen |

Alle Dienste laufen auf **einer Domain** hinter Caddy. Die Pfade `/insight/`, `/work/`, `/session/`, `/accounts/`, `/admin/`, `/api/` und `/oparl/` gehen an die Anwendung, alles andere an die Website.

## Installation

=== "Interaktiver Installer"

    ```bash
    git clone https://github.com/mandariOSS/mandari.git
    cd mandari
    ./install.sh
    ```

    Der Installer fragt Domain, E-Mail-Adresse für Zertifikate und Datenbankzugang ab, erzeugt Schlüssel und startet den Stack.

=== "Nur Docker Compose"

    ```bash
    mkdir mandari && cd mandari
    curl -LO https://raw.githubusercontent.com/mandariOSS/mandari/main/docker-compose.yml
    curl -LO https://raw.githubusercontent.com/mandariOSS/mandari/main/Caddyfile
    curl -Lo .env https://raw.githubusercontent.com/mandariOSS/mandari/main/.env.example
    nano .env            # Domain, Zugangsdaten und Schlüssel setzen, siehe Konfiguration
    docker compose up -d
    docker compose exec mandari python manage.py migrate
    docker compose exec mandari python manage.py createsuperuser
    ```

!!! danger "Schlüssel sichern"
    Die Datei `.env` enthält den Django-`SECRET_KEY` und den `ENCRYPTION_MASTER_KEY`. Ohne den Master-Key sind verschlüsselte Felder in Backups nicht mehr lesbar. Sichert die Datei getrennt vom Server und ändert die Schlüssel nach der Installation nie.

## Erste Schritte nach dem Start

1. **Anmelden** unter `https://<domain>/admin/` mit dem eben angelegten Superuser.
2. **Rollen anlegen**: `docker compose exec mandari python manage.py setup_roles` erzeugt die Standardrollen für Work und Session.
3. **Suche einrichten**: `docker compose exec mandari python manage.py setup_elasticsearch` konfiguriert Synonyme und Tippfehlertoleranz.
4. **Quellen anbinden**: Im Admin unter *OParl-Quellen* die erste Kommune eintragen, siehe [Quellen anbinden](quellen-anbinden.md). Der Ingestor synchronisiert im eingestellten Intervall.
5. **Regelmäßige Aufgaben** einrichten, siehe [Cron](cron.md).
6. **Betriebsmonitor** unter `/admin/monitoring/` prüfen, siehe [Betriebsmonitor](monitoring.md).
7. Optional eine **Demo-Umgebung** anlegen, um alle drei Portale mit Beispieldaten zu sehen, siehe [Demo-Umgebung](demo-umgebung.md).

## Provisioning-API

Für den Betrieb als Dienst kann ein externes System Organisationen über `/api/provisioning/` anlegen und verwalten. Die API wird ausschließlich über die Variable `PROVISIONING_API_KEY` aktiviert. Ohne gesetzten Schlüssel antworten alle Anfragen mit 404, sodass Community-Installationen keine offene Angriffsfläche haben.

## Support

Community-Support läuft über [GitHub-Issues](https://github.com/mandariOSS/mandari/issues). Für Kommunen bieten wir betreutes Hosting und Support-Verträge an, siehe [mandari.de/kommunen/](https://mandari.de/kommunen/).
