#!/usr/bin/env python3
"""Prüft die Antworten des laufenden Docs-Containers gegen tests/nginx_pfade.txt.

Zusätzlich muss jede gebaute HTML-Seite unter site/ mit 200 ausgeliefert werden, damit
keine Weiterleitungsregel eine echte Doku-Seite trifft.

Aufruf (Container läuft auf Port 8080, site/ stammt aus `mkdocs build`):

    python tests/nginx_pfade.py --basis http://127.0.0.1:8080 --site site
"""

from __future__ import annotations

import argparse
import http.client
import sys
import time
import urllib.parse
from pathlib import Path

ZIEL = "https://mandari.de"
FAELLE = Path(__file__).with_name("nginx_pfade.txt")


def lade_faelle(datei: Path) -> list[tuple[int, str, str | None]]:
    faelle = []
    for nummer, zeile in enumerate(datei.read_text(encoding="utf-8").splitlines(), start=1):
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#"):
            continue
        teile = zeile.split(maxsplit=2)
        if len(teile) < 2 or not teile[0].isdigit() or not teile[1].startswith("/"):
            raise SystemExit(f"{datei}:{nummer}: Zeile nicht lesbar: {zeile!r}")
        faelle.append((int(teile[0]), teile[1], teile[2] if len(teile) == 3 else None))
    return faelle


def seiten_aus_site(site: Path) -> list[str]:
    pfade = []
    for datei in sorted(site.rglob("*.html")):
        relativ = datei.relative_to(site).as_posix()
        if relativ == "index.html" or relativ.endswith("/index.html"):
            relativ = relativ[: -len("index.html")]
        pfade.append("/" + relativ)
    return pfade


def abfrage(basis: urllib.parse.SplitResult, pfad: str) -> tuple[int, str | None, str | None]:
    verbindung = http.client.HTTPConnection(basis.hostname, basis.port or 80, timeout=10)
    try:
        verbindung.request("GET", pfad, headers={"Host": "docs.mandari.de"})
        antwort = verbindung.getresponse()
        antwort.read()
        return antwort.status, antwort.getheader("Location"), antwort.getheader("Content-Type")
    finally:
        verbindung.close()


def warte_auf_container(basis: urllib.parse.SplitResult, sekunden: int) -> None:
    ende = time.monotonic() + sekunden
    while True:
        try:
            if abfrage(basis, "/health")[0] == 200:
                return
        except OSError:
            pass
        if time.monotonic() > ende:
            raise SystemExit(f"Container antwortet nach {sekunden} s nicht auf /health")
        time.sleep(1)


def pruefe(basis: urllib.parse.SplitResult, status: int, pfad: str, erwartung: str | None) -> str | None:
    ist_status, location, content_type = abfrage(basis, pfad)
    if ist_status != status:
        zusatz = f" → {location}" if location else ""
        return f"{pfad}: erwartet {status}, erhalten {ist_status}{zusatz}"
    if status in (301, 302, 307, 308):
        ziel = erwartung or ZIEL + pfad
        if location != ziel:
            return f"{pfad}: Ziel {location!r}, erwartet {ziel!r}"
    elif status == 200 and erwartung and (content_type or "").lower() != erwartung.lower():
        return f"{pfad}: Content-Type {content_type!r}, erwartet {erwartung!r}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--basis", default="http://127.0.0.1:8080", help="Adresse des Containers")
    parser.add_argument("--site", type=Path, default=Path("site"), help="Verzeichnis des MkDocs-Builds")
    parser.add_argument("--warten", type=int, default=30, help="Sekunden, die auf den Container gewartet wird")
    args = parser.parse_args()

    basis = urllib.parse.urlsplit(args.basis)
    warte_auf_container(basis, args.warten)

    faelle = lade_faelle(FAELLE)
    seiten = seiten_aus_site(args.site)
    if not seiten:
        raise SystemExit(f"Keine HTML-Seiten unter {args.site} gefunden – erst `mkdocs build` ausführen")
    faelle += [(200, pfad, None) for pfad in seiten]

    fehler = [meldung for fall in faelle if (meldung := pruefe(basis, *fall))]
    for meldung in fehler:
        print(f"FEHLER {meldung}")
    weiterleitungen = sum(1 for status, _, _ in faelle if status == 301)
    print(
        f"{len(faelle)} Pfade geprüft ({len(seiten)} gebaute Seiten, {weiterleitungen} Weiterleitungen),"
        f" {len(fehler)} Fehler"
    )
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
