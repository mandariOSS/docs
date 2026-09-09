---
title: Qualitätsgates und Tests
description: Welche Prüfungen in der CI laufen, wie man sie lokal ausführt und welche Regeln für Templates, Komponenten und Tests gelten.
---

# Qualitätsgates und Tests

Jeder Push auf `dev` durchläuft dieselben Prüfungen, die auch lokal laufen. Sie sind blockierend;
Kennzahlen, die nicht sofort auf null gebracht werden können, werden mit einer Baseline geführt, die
nur sinken darf („Ratchet“). Die Regeln stehen im Repository unter `docs/ENGINEERING_STANDARDS.md`,
Entscheidungen unter `docs/adr/`.

## Prüfungen in der CI

| Job | Prüft | Lokal |
|-----|-------|-------|
| Lint | ruff (Regeln E, F, I, N, W, UP, B, SIM, C4, RET) und ruff-Format | `ruff check . && ruff format --check .` |
| Typprüfung | mypy (strict) mit django-stubs; Bestandsmodule stehen auf einer Allowlist, die nur schrumpfen darf | `python scripts/mypy_allowlist.py` |
| Test | pytest mit Postgres, Coverage-Gate (mindestens 38 %), Django `check --deploy`, Schema-Contract zwischen Django-Modellen und Ingestor-Tabellen | `pytest`, `python scripts/check_schema_contract.py` |
| Frontend-Qualitätsgates | djlint für Templates, Ratchet (Inline-Skripte, Inline-Styles, Templates über 300 Zeilen, Event-Handler-Attribute, style-Attribute, Duplikat-Ketten), TypeScript (`tsc --noEmit`), Biome, Vite-Build | `djlint templates --lint`, `python scripts/check_frontend_ratchet.py`, `npm run typecheck`, `npm run lint` |
| E2E | Playwright (Chromium) auf Kernpfaden mit aktivem JavaScript, axe-core (WCAG 2.2 AA), Screenshots hell/dunkel als Artefakt | `MANDARI_E2E=1 pytest tests_e2e` |
| Ingestor Tests | pytest des Ingestors | `cd ingestor && uv run pytest` |
| Abhängigkeiten prüfen | pip-audit gegen das Lockfile, REUSE-Lizenzprüfung | `pip-audit -r mandari/requirements.lock`, `reuse lint` |
| Docker Build | Image-Build inklusive Frontend-Assets | `docker build .` |

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
  parametrisierte pytest-Module abgelegt und laufen bei jedem Push.

## Lokal einrichten

```bash
cd mandari
pip install -r requirements.lock -e ".[dev]"
npm ci && npm run build
pre-commit install
pytest
```

Für die E2E-Tests zusätzlich `pip install pytest-playwright && python -m playwright install chromium`.
Details und weitere Kommandos stehen in der `CONTRIBUTING.md` des Repositories.
