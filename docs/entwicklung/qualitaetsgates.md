---
title: Qualitätsgates und Tests
description: Welche Prüfungen in der CI laufen, wie man sie lokal ausführt und welche Regeln für Templates, Komponenten und Tests gelten.
---

# Qualitätsgates und Tests

Jeder Pull Request gegen `dev` oder `main` und jeder Stand in der Merge-Queue durchläuft die Prüfungen der CI (`.github/workflows/pr-check.yml`), die auch lokal laufen. Im Pull Request starten nur die Jobs, deren Bereich die Änderung berührt; in der Merge-Queue, bei jedem Push auf `main` und im nächtlichen Volllauf auf `dev` laufen alle. Maßgeblich ist der Job „CI-Ergebnis“. Die Prüfungen sind blockierend; Kennzahlen, die nicht sofort auf null gebracht werden können, werden mit einer Baseline geführt, die nur sinken darf („Ratchet“). Die Regeln stehen im Repository unter `docs/ENGINEERING_STANDARDS.md`, Entscheidungen unter `docs/adr/`, die Einzelheiten in `CONTRIBUTING.md`.

## Prüfungen in der CI

| Job | Prüft | Lokal |
|-----|-------|-------|
| Qualität (Lint, Typprüfung, Frontend-Gates) | ruff (Regeln E, F, I, N, W, UP, B, SIM, C4, RET) und ruff-Format, mehrzeilige Template-Kommentare, Schichtregeln (import-linter), Ratchets für Frontend, Datenbankzugriffe in Views und Zugriffe auf den RIS-Bestand, djlint, mypy (strict) mit django-stubs und einer Allowlist, die nur schrumpfen darf, Schema-Contract zwischen Django-Modellen und Ingestor-Tabellen, Ereignisverträge, TypeScript (`tsc --noEmit`), Biome, Frontend-Unit-Tests, Vite-Build | in `mandari/`: `uv run ruff check . && uv run ruff format --check .`, `uv run djlint templates --lint`, `uv run lint-imports`, `npm run typecheck`, `npm run lint`; in der Wurzel: `python scripts/mypy_allowlist.py`, `python scripts/check_frontend_ratchet.py`, `python scripts/check_view_orm_ratio.py`, `python scripts/check_schema_contract.py` |
| Test, Test-Ergebnis | pytest mit PostgreSQL in drei parallelen Teilen, Coverage-Gate (mindestens 38 %), jeder Test genau einmal | `uv run pytest` (lokal SQLite) |
| Migrationstests | Tests, die Migrationen zurück- und wieder vorspielen (Kennzeichen `migrationen`) | `uv run pytest -m migrationen` |
| Smoke-Tests | `scripts/smoke_*.py` auf eigenen SQLite-Datenbanken, Leistungsbudgets | `python scripts/run_smokes.py scripts/smoke_<name>.py` |
| OParl-Validator | Aggregator und Session-Schnittstelle gegen den OParl-Validator | – |
| Ereignistechnik hinter PgBouncer | Ereignistechnik und Anwendung hinter einem echten PgBouncer im Transaktionsmodus | – |
| E2E (Playwright, axe-core, Screenshots) | Playwright (Chromium) auf Kernpfaden mit aktivem JavaScript, axe-core (WCAG 2.2 AA), Screenshots hell/dunkel als Artefakt | `MANDARI_E2E=1 uv run pytest tests_e2e` |
| Ingestor Tests | pytest des Ingestors | `cd ingestor && uv sync --extra dev && uv run pytest` |
| Abhängigkeiten prüfen (pip-audit, npm audit) | `uv lock --check`, pip-audit gegen die gesperrten Abhängigkeiten von Anwendung und Ingestor mit befristeten Ausnahmen, npm audit ab „high“ | `sh scripts/export_requirements.sh /tmp/mandari.txt && pip-audit -r /tmp/mandari.txt` |
| Verweise (Link-Prüfung) | lychee: interne Verweise und Anker aller Markdown-Dateien, im Pull Request auch externe Verweise der öffentlichen Dateien | `lychee --offline …`, Einstellungen in `lychee.toml` |
| Docker Build | Images der Anwendung und des Ingestors | `docker build -f mandari/Dockerfile .` |
| Kubernetes-Chart | `helm lint`, `helm template`, `kubeconform`, Gleichstand der Roh-Manifeste | – |
| CodeQL-Analyse | statische Sicherheitsanalyse | – |

Ein eigener Workflow prüft mit `reuse lint`, dass jede Datei eine maschinenlesbare Lizenzangabe trägt.

Bei jedem Release entsteht zusätzlich eine [CycloneDX-SBOM](sbom.md).

## Regeln für Templates und Frontend

- Templates sind Struktur, nicht Programm: kein `<script>` oder `<style>` in Seiten-Templates,
  höchstens 300 Zeilen je Datei. JavaScript liegt als TypeScript unter `frontend/`, wird mit Vite
  gebaut und über das Manifest geladen.
- Wiederkehrendes Markup kommt aus der Komponentenbibliothek (`templates/cotton/`): Buttons, Karten,
  Badges, Hinweise, Modals, Reiter, Formularfelder. Die Vorschau aller Komponenten liegt in der
  Entwicklung unter `/dev/ui/`.
- Alpine-Komponenten werden in TypeScript registriert und im Template nur referenziert; Server-Daten
  gehen als JSON an den Client.
- Barrierefreiheit ist Teil jeder Komponente (Tastatur, Fokus, ARIA, Zielgrößen); die E2E-Tests
  prüfen das mit axe-core.

## Tests schreiben

- Unit- und Integrationstests liegen je App unter `apps/<app>/tests/` und laufen mit pytest-django
  (lokal SQLite, in der CI Postgres). Testdaten kommen aus den Factories in
  `apps/common/tests/factories.py` und den Fixtures in `conftest.py`.
- Neue Module müssen typisiert sein; das mypy-Gate meldet Fehler außerhalb der Allowlist.
- Für jede neue Seite gehört ein Rendering-Test dazu, für Kernpfade zusätzlich ein E2E-Test.
- Die Sicherheitsmatrizen (Tenant-Isolation, Öffentlich/Nicht-öffentlich, Gastzugänge) sind als
  parametrisierte pytest-Module abgelegt und laufen mit der Testsuite.

## Lokal einrichten

```bash
cd mandari
uv sync --extra dev               # Abhängigkeiten aus uv.lock, mit Test- und Lint-Werkzeugen
npm ci && npm run build
uv run pytest
```

Die Prüfungen vor jedem Commit übernimmt pre-commit (`pip install pre-commit && pre-commit install`). Für die E2E-Tests zusätzlich `uv run playwright install chromium`. Wie Datenbank, Redis und Suche für den Entwicklungsserver laufen, steht unter [Entwicklung](index.md#lokal-entwickeln), weitere Kommandos in der `CONTRIBUTING.md` des Repositorys.
