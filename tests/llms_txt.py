#!/usr/bin/env python3
"""Prüft site/llms.txt nach dem MkDocs-Build (offline).

- Aufbau nach llmstxt.org: Titel als H1, Kurzbeschreibung als Zitat, Abschnitte als H2
- jeder Link ist absolut; Links auf die Dokumentation zeigen auf eine gebaute Seite und
  nicht auf eine Weiterleitungsseite
- jede Seite aus der Sitemap ist verlinkt, damit neue Seiten nicht vergessen werden

Aufruf nach `mkdocs build`:

    python tests/llms_txt.py --site site
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DOCS_URL = "https://docs.mandari.de/"
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def datei_zur_url(site: Path, url: str) -> Path:
    pfad = url[len(DOCS_URL) :]
    if pfad == "" or pfad.endswith("/"):
        pfad += "index.html"
    return site / pfad


def sitemap_urls(site: Path) -> list[str]:
    baum = ET.parse(site / "sitemap.xml")
    return [loc.text.strip() for loc in baum.iter() if loc.tag.endswith("loc") and loc.text]


def pruefe(site: Path) -> list[str]:
    datei = site / "llms.txt"
    if not datei.is_file():
        return [f"{datei} fehlt – liegt docs/llms.txt im Repository?"]
    alle_zeilen = datei.read_text(encoding="utf-8").splitlines()
    zeilen = [zeile for zeile in alle_zeilen if zeile.strip()]
    fehler = []

    if not zeilen or not zeilen[0].startswith("# "):
        fehler.append("Die erste Zeile muss der Titel als H1 sein (# …)")
    if len(zeilen) < 2 or not zeilen[1].startswith("> "):
        fehler.append("Direkt nach dem Titel muss die Kurzbeschreibung als Zitat stehen (> …)")
    if not any(zeile.startswith("## ") for zeile in zeilen):
        fehler.append("Mindestens ein Abschnitt (## …) mit Links fehlt")

    verlinkt: set[str] = set()
    for nummer, zeile in enumerate(alle_zeilen, start=1):
        for titel, url in LINK.findall(zeile):
            if not url.startswith(("https://", "http://")):
                fehler.append(f"Zeile {nummer}: Link „{titel}“ muss absolut sein: {url}")
                continue
            if not url.startswith(DOCS_URL):
                continue
            if url in verlinkt:
                fehler.append(f"Zeile {nummer}: {url} ist doppelt verlinkt")
            verlinkt.add(url)
            ziel = datei_zur_url(site, url)
            if not ziel.is_file():
                fehler.append(f"Zeile {nummer}: „{titel}“ zeigt auf {url}, die Seite gibt es nicht")
            elif 'http-equiv="refresh"' in ziel.read_text(encoding="utf-8"):
                fehler.append(f"Zeile {nummer}: „{titel}“ zeigt auf die Weiterleitungsseite {url}")

    for url in sitemap_urls(site):
        if url not in verlinkt:
            fehler.append(f"{url} fehlt in docs/llms.txt (neue Seite? unter passendem Abschnitt eintragen)")
    return fehler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", type=Path, default=Path("site"), help="Verzeichnis des MkDocs-Builds")
    args = parser.parse_args()

    fehler = pruefe(args.site)
    for meldung in fehler:
        print(f"FEHLER {meldung}")
    print(f"llms.txt geprüft, {len(fehler)} Fehler")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
