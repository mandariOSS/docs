#!/usr/bin/env python3
"""Gleicht die Konfigurationsreferenz (docs/betrieb/konfiguration.md) mit dem Code von mandari ab.

Die Seite ist von Hand gegliedert und erklärt jede Variable. Dieses Skript hält sie vollständig und
findet Veraltetes. Es braucht einen Checkout des Anwendungs-Repositorys mandariOSS/mandari:

    git clone --depth 1 https://github.com/mandariOSS/mandari.git ../mandari
    python tests/umgebungsvariablen.py --mandari ../mandari          # prüfen, Exit-Code 1 bei Lücken
    python tests/umgebungsvariablen.py --mandari ../mandari --liste  # alle Variablen mit Standard und Fundstelle

Erfasst werden

- die Django-Settings (``mandari/mandari/settings.py``): jeder Aufruf ``os.environ.get`` bzw. ``os.getenv``
  mit festem Namen, der Standard als Ausdruck aus dem Quelltext;
- der übrige Code der Anwendung und ``shared/``, ohne Tests und Migrationen;
- ``docker-compose.yml``: jede Variable ``${NAME…}``, die Compose aus der ``.env`` einsetzt;
- der Ingestor (``ingestor/src/config.py``): die Felder der Klasse ``Settings``, Name in Großbuchstaben,
  dazu ihre Aliase.

Geprüft wird:

1. Jede Variable aus Settings, Anwendung und ``docker-compose.yml`` steht auf der Seite (in Backticks).
2. Jede Variable, die die Seite nennt, kommt im Repository noch vor.

Variablen des Ingestors, die die Seite nicht nennt, meldet das Skript nur; ``--ingestor-pflicht`` macht
auch sie zur Pflicht.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SEITE = Path(__file__).resolve().parent.parent / "docs" / "betrieb" / "konfiguration.md"

#: Code der Anwendung (relativ zum Checkout), ohne Tests, Migrationen und Testeinstellungen
ANWENDUNG = ("mandari", "shared")
AUSGESCHLOSSEN = re.compile(r"(^|/)(tests?|tests_e2e|migrations|node_modules|\.venv|static)(/|$)|(^|/)(test_[^/]*|conftest|settings_test)\.py$")

#: Variablen, die nur die Anwendung selbst setzt oder liest; sie gehören nicht in die Referenz
INTERN = {
    "PROMETHEUS_MULTIPROC_DIR": "setzt mandari.app_processes für mehrere Anwendungsprozesse selbst",
    "MANDARI_AUS_ZEITPLAN": "setzt der Worker für Verwaltungsbefehle aus einem Zeitplan",
}

#: Namen in Backticks auf der Seite, die keine Umgebungsvariablen des Codes sind
KEINE_VARIABLE = {
    "STORAGES",  # Django-Einstellung, auf die AUDIT_ARCHIVE_STORAGE verweist
}

NAME = re.compile(r"`([A-Z][A-Z0-9_]{1,})`")
COMPOSE_VARIABLE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)")


@dataclass(frozen=True)
class Fund:
    name: str
    herkunft: str  # settings, anwendung, compose, ingestor
    standard: str
    stelle: str


def _umgebungsaufrufe(datei: Path, wurzel: Path, herkunft: str) -> list[Fund]:
    """``os.environ.get("X", …)``, ``os.getenv("X", …)`` und ``os.environ["X"]`` mit festem Namen."""
    try:
        baum = ast.parse(datei.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    stelle = datei.relative_to(wurzel).as_posix()
    funde = []
    for knoten in ast.walk(baum):
        name = standard = None
        if isinstance(knoten, ast.Call) and ast.unparse(knoten.func) in ("os.environ.get", "os.getenv"):
            if knoten.args and isinstance(knoten.args[0], ast.Constant) and isinstance(knoten.args[0].value, str):
                name = knoten.args[0].value
                standard = ast.unparse(knoten.args[1]) if len(knoten.args) > 1 else "None"
        elif isinstance(knoten, ast.Subscript) and ast.unparse(knoten.value) == "os.environ":
            if isinstance(knoten.slice, ast.Constant) and isinstance(knoten.slice.value, str):
                name, standard = knoten.slice.value, "(Pflicht)"
        if name:
            funde.append(Fund(name, herkunft, standard or "", f"{stelle}:{knoten.lineno}"))
    return funde


def settings(wurzel: Path) -> list[Fund]:
    return _umgebungsaufrufe(wurzel / "mandari" / "mandari" / "settings.py", wurzel, "settings")


def anwendung(wurzel: Path) -> list[Fund]:
    funde: list[Fund] = []
    for teil in ANWENDUNG:
        for datei in sorted((wurzel / teil).rglob("*.py")):
            relativ = datei.relative_to(wurzel).as_posix()
            if AUSGESCHLOSSEN.search(relativ) or relativ == "mandari/mandari/settings.py":
                continue
            funde += _umgebungsaufrufe(datei, wurzel, "anwendung")
    return funde


def compose(wurzel: Path) -> list[Fund]:
    datei = wurzel / "docker-compose.yml"
    funde = []
    for nummer, zeile in enumerate(datei.read_text(encoding="utf-8").splitlines(), start=1):
        if zeile.lstrip().startswith("#"):
            continue
        for treffer in COMPOSE_VARIABLE.finditer(zeile):
            rest = zeile[treffer.end() :]
            standard = rest[2 : rest.find("}")] if rest[:2] in (":-", ":?") else ""
            funde.append(Fund(treffer.group(1), "compose", standard, f"docker-compose.yml:{nummer}"))
    return funde


def ingestor(wurzel: Path) -> list[Fund]:
    """Felder von ``Settings`` in ``ingestor/src/config.py`` (pydantic-settings, Namen ohne Groß-/Kleinschreibung)."""
    datei = wurzel / "ingestor" / "src" / "config.py"
    baum = ast.parse(datei.read_text(encoding="utf-8"))
    funde = []
    for klasse in (k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == "Settings"):
        for feld in klasse.body:
            if not (isinstance(feld, ast.AnnAssign) and isinstance(feld.target, ast.Name)):
                continue
            namen = [feld.target.id.upper()]
            standard = ast.unparse(feld.value) if feld.value is not None else ""
            if isinstance(feld.value, ast.Call) and ast.unparse(feld.value.func) == "Field":
                for wort in feld.value.keywords:
                    if wort.arg == "default":
                        standard = ast.unparse(wort.value)
                    if wort.arg == "validation_alias" and isinstance(wort.value, ast.Call):
                        namen = [a.value.upper() for a in wort.value.args if isinstance(a, ast.Constant)]
            for name in dict.fromkeys(namen):
                funde.append(Fund(name, "ingestor", standard, f"ingestor/src/config.py:{feld.lineno}"))
    return funde


def namen_der_seite(seite: Path) -> set[str]:
    return set(NAME.findall(seite.read_text(encoding="utf-8")))


def kommt_vor(wurzel: Path, namen: set[str]) -> set[str]:
    """Welche der Namen stehen irgendwo im Repository (außer .git und node_modules)?"""
    offen = set(namen)
    gefunden: set[str] = set()
    for datei in wurzel.rglob("*"):
        if not offen:
            break
        if not datei.is_file() or {".git", "node_modules", ".venv"} & set(datei.parts):
            continue
        try:
            text = datei.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        treffer = {name for name in offen if name in text or name.lower() in text}
        gefunden |= treffer
        offen -= treffer
    return gefunden


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--mandari", type=Path, required=True, help="Checkout von mandariOSS/mandari")
    parser.add_argument("--seite", type=Path, default=SEITE, help="geprüfte Seite (Vorgabe: betrieb/konfiguration.md)")
    parser.add_argument("--liste", action="store_true", help="alle Variablen als Markdown-Tabelle ausgeben")
    parser.add_argument("--ingestor-pflicht", action="store_true", help="auch Variablen des Ingestors verlangen")
    args = parser.parse_args()

    wurzel = args.mandari.resolve()
    if not (wurzel / "mandari" / "mandari" / "settings.py").is_file():
        print(f"{wurzel} ist kein Checkout von mandariOSS/mandari", file=sys.stderr)
        return 2

    funde = settings(wurzel) + anwendung(wurzel) + compose(wurzel) + ingestor(wurzel)

    if args.liste:
        print("| Variable | Herkunft | Standard im Code | Fundstelle |")
        print("|----------|----------|------------------|------------|")
        gesehen: set[tuple[str, str]] = set()
        for fund in sorted(funde, key=lambda f: (f.name, f.herkunft)):
            if (fund.name, fund.herkunft) in gesehen:
                continue
            gesehen.add((fund.name, fund.herkunft))
            standard = fund.standard.replace("|", "\\|")
            print(f"| `{fund.name}` | {fund.herkunft} | `{standard}` | {fund.stelle} |")
        return 0

    auf_der_seite = namen_der_seite(args.seite)
    pflicht = {f.name for f in funde if f.herkunft != "ingestor" or args.ingestor_pflicht} - set(INTERN)
    fehlen = sorted(pflicht - auf_der_seite)
    nur_ingestor = sorted({f.name for f in funde if f.herkunft == "ingestor"} - auf_der_seite - set(fehlen))
    veraltet = sorted(auf_der_seite - KEINE_VARIABLE - kommt_vor(wurzel, auf_der_seite - KEINE_VARIABLE))

    for name in fehlen:
        stellen = sorted({f.stelle for f in funde if f.name == name})
        print(f"FEHLT auf der Seite: {name} ({', '.join(stellen[:3])})")
    for name in veraltet:
        print(f"VERALTET: {name} steht auf der Seite, kommt im Code nicht mehr vor")
    if nur_ingestor:
        print(f"Hinweis: {len(nur_ingestor)} Einstellungen des Ingestors nennt die Seite nicht: {', '.join(nur_ingestor)}")

    print(
        f"{len(pflicht)} Variablen aus Settings, Anwendung und docker-compose.yml, "
        f"{len(auf_der_seite)} Namen auf der Seite, {len(fehlen)} fehlen, {len(veraltet)} veraltet"
    )
    return 1 if fehlen or veraltet else 0


if __name__ == "__main__":
    sys.exit(main())
