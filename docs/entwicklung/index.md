---
title: Entwicklung
description: Quellcode, Technologie-Stack, lokale Entwicklung, Tests und Beitragswege für mandari.
---

# Entwicklung

mandari ist Open Source. Der Code liegt in mehreren Repositories der GitHub-Organisation [mandariOSS](https://github.com/mandariOSS).

| Repository | Inhalt |
|------------|--------|
| [`mandari`](https://github.com/mandariOSS/mandari) | Hauptanwendung mit Insight, Work und Session sowie der Ingestor |
| [`marketing-website`](https://github.com/mandariOSS/marketing-website) | Öffentliche Website mandari.de (Wagtail) |
| [`docs`](https://github.com/mandariOSS/docs) | Diese Dokumentation |

Entwicklung findet im Hauptrepository auf dem Branch `dev` statt, `main` ist der Produktionsstand.

## Technologie-Stack

| Komponente | Technologie |
|------------|-------------|
| Backend | Django 6, Python 3.12 |
| Frontend | Django-Templates, HTMX, Alpine.js, Tailwind CSS, Tiptap-Editor |
| Admin | django-unfold |
| Datenbank | PostgreSQL 16 |
| Suche | Elasticsearch 8 |
| Cache und Echtzeit | Redis 7, Django Channels |
| Ingestor | Python mit httpx und SQLAlchemy, Scraper-Adapter, Prometheus-Metriken |
| Verschlüsselung | AES-256-GCM mit mandantenspezifischen Schlüsseln |
| Proxy | Caddy |

## Lokal entwickeln

```bash
git clone https://github.com/mandariOSS/mandari.git
cd mandari/mandari
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env        # SECRET_KEY, DATABASE_URL, ENCRYPTION_MASTER_KEY setzen
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
python manage.py runserver
```

Für einen schnellen Überblick über alle drei Portale eignet sich die [Demo-Umgebung](../betrieb/demo-umgebung.md). Die Datei `CLAUDE.md` im Repository beschreibt Architektur, Apps, Berechtigungssystem und Konventionen ausführlich.

## Tests

Neben den Unit-Tests gibt es eine Reihe von **Smoke-Tests** unter `scripts/smoke_*.py`. Jeder läuft selbst enthalten auf einer frischen SQLite-Datenbank und prüft ein Feature Ende-zu-Ende, inklusive Berechtigungen, Mandantentrennung und der Garantie, dass nur öffentliche Inhalte nach außen gelangen. Beispiele:

| Skript | Prüft |
|--------|-------|
| `smoke_oparl_api.py` | OParl-Aggregations-API mit synthetischen Daten aller Objekttypen |
| `smoke_tombstones.py` | Tombstone-Verhalten in Sync, Portal und API |
| `smoke_session_oparl.py` | Session-OParl-API inklusive Beweis, dass nichts Nicht-Öffentliches ausgeliefert wird |
| `smoke_insight_durchstich.py` | Weg einer Session-Kommune ins Bürgerportal |
| `smoke_ris_submission.py` | Digitale Antragseinreichung von Work nach Session |
| `smoke_faction_meetings.py` | Fraktionssitzungen und öffentliche Fraktions-API |
| `smoke_demo_environment.py` | Demo-Umgebung anlegen, prüfen, aufräumen |

Die CI führt Linting, Tests, Smoke-Tests und einen Template-Check aus, der mehrzeilige Inline-Kommentare in Django-Templates ablehnt, weil sie sonst als Text auf der Seite landen würden.

## Mitwirken

- **Fehler melden** und **Features vorschlagen** über die [Issues](https://github.com/mandariOSS/mandari/issues). Bitte keine Sicherheitsdetails in öffentlichen Issues, dafür <security@mandari.de>.
- **Pull Requests** gegen `dev`. Die [Contributing Guidelines](https://github.com/mandariOSS/mandari/blob/main/CONTRIBUTING.md) und der [Code of Conduct](https://github.com/mandariOSS/mandari/blob/main/CODE_OF_CONDUCT.md) gelten.
- **Dokumentation verbessern**: siehe [An der Dokumentation mitarbeiten](dokumentation.md).
- **Kommunen anbinden**: Neue Scraper-Adapter oder Bridges für weitere Ratsinformationssysteme sind besonders willkommen, siehe [Quellen anbinden](../betrieb/quellen-anbinden.md).

## Lizenz und Abhängigkeiten

Der Quellcode steht unter einer Open-Source-Lizenz, die in den Repositories angegeben ist. Eine Übersicht der eingesetzten Bibliotheken mit Lizenzen findest du unter [Abhängigkeiten (SBOM)](sbom.md).
