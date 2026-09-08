---
title: An der Dokumentation mitarbeiten
description: Wie diese Dokumentation gebaut wird, wie du Seiten korrigierst oder ergänzt und welche Konventionen gelten.
---

# An der Dokumentation mitarbeiten

Diese Dokumentation ist selbst Open Source und lebt im Repository [mandariOSS/docs](https://github.com/mandariOSS/docs). Sie wird mit [MkDocs](https://www.mkdocs.org/) und dem Theme [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) gebaut und als statische Seite ausgeliefert.

## Kleine Korrektur

Jede Seite hat oben rechts einen Stift. Er öffnet die Markdown-Datei direkt auf GitHub, wo du sie im Browser ändern und als Pull Request einreichen kannst. Ein GitHub-Konto genügt.

## Größere Änderung

```bash
git clone https://github.com/mandariOSS/docs.git
cd docs
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve                                        # http://127.0.0.1:8000 mit Live-Reload
```

Vor dem Einreichen:

```bash
mkdocs build --strict
```

Der strikte Build schlägt bei defekten internen Links, fehlenden Seiten in der Navigation oder unbekannten Ankern fehl. Dieselbe Prüfung läuft in der CI, dazu ein Offline-Link-Check über das gebaute HTML.

## Struktur

```
docs/
├── index.md              Startseite
├── plattform.md, glossar.md, aenderungen.md
├── insight/              Bürgerportal
├── work/                 Fraktionen
├── session/              Verwaltung
├── betrieb/              Self-Hosting, Konfiguration, Cron, Quellen, Monitoring
├── datenschutz/          TOM, Löschkonzept, AVV, Crawler
└── entwicklung/          Code, Mitarbeit, SBOM
mkdocs.yml                Navigation, Theme, Plugins
overrides/                Template-Anpassungen
```

Neue Seiten müssen in der Navigation in `mkdocs.yml` eingetragen werden. Jede Seite beginnt mit einem Frontmatter aus `title` und `description`, die Beschreibung erscheint in Suchmaschinen und Vorschauen.

## Konventionen

- **Sprache**: Deutsch. Leserinnen und Leser werden mit „du“ bzw. „ihr“ angesprochen, mandari spricht von sich als „wir“.
- **Zielgruppe zuerst**: Jeder Bereich beginnt mit einer Übersichtsseite, die erklärt, für wen die Inhalte sind.
- **Nichts Internes**: Keine Zugangsdaten, keine internen Hostnamen, keine Produktnamen von Hosting-Anbietern, keine Preisdetails. Preise stehen ausschließlich auf [mandari.de/preise/](https://mandari.de/preise/).
- **Konkrete Befehle in Codeblöcken**, Platzhalter in spitzen Klammern wie `<kommune>`.
- **Hinweiskästen** sparsam: `!!! info`, `!!! tip`, `!!! warning`, `!!! danger` für wirklich Wichtiges.
- **Relative Links** zwischen Seiten (`../betrieb/cron.md`), damit der strikte Build sie prüfen kann.

## Was wo hingehört

Erklärungen für Nutzerinnen, Betreiber und Integratoren gehören hierher. Implementierungsnotizen, Dateipfade und Entwicklerdetails bleiben im Quellcode-Repository, dort im Verzeichnis `docs/` und in `CLAUDE.md`. Wenn ein Feature im Hauptrepository dokumentiert wird, gehört eine für Außenstehende verständliche Fassung in diese Dokumentation.

## Technische Details der Plattform

- **Suche**: clientseitig, deutsch, ohne externen Dienst
- **Keine externen Ressourcen**: Systemschriften, keine Web-Fonts, kein Tracking
- **Auslieferung**: Docker-Image mit statischem Build hinter einem unprivilegierten nginx, gebaut und veröffentlicht durch GitHub Actions bei jedem Push auf `main`
- **Lizenz**: Inhalte CC BY 4.0, Build-Code MIT
