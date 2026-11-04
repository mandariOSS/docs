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
| Backend | Django 6.1, Python 3.12 bis 3.14 |
| Frontend | Django-Templates, HTMX, Alpine.js, Tailwind CSS, Tiptap-Editor; TypeScript, gebaut mit Vite |
| Admin | django-unfold |
| Datenbank | PostgreSQL 16 |
| Suche | Elasticsearch 8 |
| Cache und Echtzeit | Redis 7, Django Channels |
| Ingestor | Python mit httpx und SQLAlchemy, Scraper-Adapter, Prometheus-Metriken |
| Verschlüsselung | AES-256-GCM mit mandantenspezifischen Schlüsseln |
| Proxy | Caddy |

## Lokal entwickeln

Voraussetzungen: Python 3.12 bis 3.14, Node.js 22 oder neuer, Docker (für PostgreSQL, Redis und Elasticsearch) und [uv](https://docs.astral.sh/uv/). Die Python-Abhängigkeiten stehen in `mandari/pyproject.toml`, die gesperrten Versionen in `mandari/uv.lock`. Eine `requirements.txt` liegt nicht im Repository; wer sie für pip braucht, erzeugt sie mit `sh scripts/export_requirements.sh <datei>` aus der Lock-Datei.

```bash
git clone https://github.com/mandariOSS/mandari.git
cd mandari
cp .env.example .env
```

Die `.env` gehört in die **Wurzel** des Repositorys: Docker Compose liest dort die Passwörter für Datenbank und Redis, und die Anwendung lädt dieselbe Datei beim Start. Trag dort `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `SECRET_KEY` und `ENCRYPTION_MASTER_KEY` ein (Passwörter nur aus Buchstaben und Ziffern, den Schlüssel mit `openssl rand -base64 32`) und ergänze die Verbindungen für die Anwendung, die außerhalb von Docker läuft:

```ini
DATABASE_URL=postgresql://mandari:<POSTGRES_PASSWORD>@localhost:5432/mandari
REDIS_URL=redis://:<REDIS_PASSWORD>@localhost:6379/0
```

`docker-compose.yml` veröffentlicht die Ports von Datenbank, Redis und Suche nicht. Für die Entwicklung gibt eine `docker-compose.override.yml` in der Wurzel sie nur auf dem eigenen Rechner frei; das Repository ignoriert diese Datei. Belegt schon ein anderer Dienst einen dieser Ports, wähle links einen freien und pass die Adresse in der `.env` an.

```yaml
services:
  postgres:
    ports: ["127.0.0.1:5432:5432"]
  redis:
    ports: ["127.0.0.1:6379:6379"]
  elasticsearch:
    ports: ["127.0.0.1:9200:9200"]
```

Danach:

```bash
docker compose up -d postgres redis elasticsearch   # Datenbank, Cache und Suche

cd mandari
uv sync --extra dev              # Abhängigkeiten aus uv.lock, mit Test- und Lint-Werkzeugen
npm ci && npm run build          # Frontend bauen

uv run python manage.py migrate
uv run python manage.py setup_roles
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Die Anwendung läuft dann unter <http://localhost:8000>. Für die Frontend-Entwicklung mit Hot Reload laufen `npm run watch` und `DJANGO_VITE_DEV_MODE=1 uv run python manage.py runserver` nebeneinander. Eine neue Abhängigkeit kommt mit `uv lock` in die Lock-Datei; `pyproject.toml` und `uv.lock` gehören in denselben Commit.

Für einen schnellen Überblick über alle drei Portale eignet sich die [Demo-Umgebung](../betrieb/demo-umgebung.md). Die Datei `AGENTS.md` im Repository beschreibt Architektur, Apps, Berechtigungssystem und Konventionen ausführlich, `CONTRIBUTING.md` die Entwicklungsumgebung und die Prüfungen, `docs/ENGINEERING_STANDARDS.md` die Regeln für neuen Code.

## Tests

Die Testsuite läuft mit pytest:

```bash
cd mandari
uv run pytest apps/work/tasks -q                 # einzelne App
uv run --with pytest-xdist pytest -n auto -m "not migrationen"   # parallel wie in der CI, ohne Migrationstests
```

Ohne `DATABASE_URL` in der Umgebung der Shell laufen die Tests auf einer frischen SQLite-Datenbank; der Eintrag in der `.env` zählt dafür nicht. Die CI testet mit PostgreSQL. `pytest-xdist` gehört nicht zu den Entwicklungswerkzeugen in `uv.lock`, deshalb `--with`.

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
