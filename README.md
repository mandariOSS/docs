# mandari Dokumentation

Quelltext der Dokumentation unter **https://docs.mandari.de** – gebaut mit
[MkDocs](https://www.mkdocs.org/) und [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Lokal arbeiten

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve          # http://127.0.0.1:8000 mit Live-Reload
mkdocs build --strict # wie in CI
```

## Struktur

| Pfad | Inhalt |
|------|--------|
| `docs/` | Inhalte als Markdown, gegliedert nach Insight, Work, Session, Betrieb, Datenschutz, Entwicklung |
| `mkdocs.yml` | Navigation, Theme, Plugins |
| `overrides/` | Template-Anpassungen (Meta-Tags, 404-Seite) |
| `Dockerfile`, `nginx.conf` | Produktions-Image: statischer Build hinter unprivilegiertem nginx |
| `.github/workflows/` | CI (strikter Build, Link-Check) und Release (Image nach GHCR) |

## Beitragen

Jede Seite hat oben rechts einen Bearbeiten-Stift, der direkt zur Datei auf GitHub führt.
Tippfehler, Ergänzungen und neue Anleitungen sind als Pull Request willkommen.
Bitte `mkdocs build --strict` vor dem Einreichen laufen lassen – defekte Links lassen den Build fehlschlagen.

## Lizenz

Inhalte: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de). Build-Code: MIT. Details in `LICENSE`.
