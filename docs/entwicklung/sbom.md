---
title: Abhängigkeiten (SBOM)
description: Software Bill of Materials der mandari-Plattform. Wo die Liste der Abhängigkeiten mit Lizenzen liegt und welche externen Dienste optional eingebunden sind.
---

# Abhängigkeiten (SBOM)

Jedes Release bringt eine maschinenlesbare Stückliste im Format CycloneDX mit, versionsgenau und mit allen transitiven Paketen. Sie hängt als drei Dateien an jedem [GitHub-Release](https://github.com/mandariOSS/mandari/releases): `sbom-mandari-python.cdx.json` (Django-Anwendung), `sbom-ingestor-python.cdx.json` (Ingestor) und `sbom-mandari-npm.cdx.json` (Frontend).

Wie die Stückliste entsteht und welche Lizenzen gelten, steht in der Datei `DEPENDENCIES.md` im Hauptrepository:

**[Stückliste (SBOM) je Release in DEPENDENCIES.md](https://github.com/mandariOSS/mandari/blob/main/DEPENDENCIES.md#stückliste-sbom-je-release)**

## Die wichtigsten Bausteine

| Bereich | Komponenten |
|---------|-------------|
| Framework und Server | Django, django-htmx, django-unfold, whitenoise, gunicorn, daphne, channels, channels-redis, django-safemigrate |
| Datenbank und Cache | PostgreSQL 16, psycopg, Redis 7 |
| Suche | Elasticsearch 8 mit Python-Client |
| Dokumente | pypdf, Tesseract-OCR, optional ein externer OCR-Dienst |
| Frontend | HTMX, Alpine.js, Tailwind CSS, Tiptap, Lucide Icons |
| Ingestor | httpx, SQLAlchemy, APScheduler, Prometheus-Client |

## Externe Dienste

mandari läuft ohne externe Dienste. Optional einbindbar sind:

- **Externer OCR-Dienst** für gescannte Dokumente, nur wenn ein API-Schlüssel konfiguriert ist. Ohne Schlüssel arbeitet die lokale Texterkennung.
- **Externe Bridges** für Ratsinformationssysteme ohne OParl, als eigene Container, siehe [Quellen anbinden](../betrieb/quellen-anbinden.md).

Kartenkacheln für Ortsbezüge werden lokal zwischengespeichert, damit Besucherinnen des Bürgerportals keine Anfragen an Dritte auslösen.

## Diese Dokumentation

Die Dokumentationsseite selbst basiert auf MkDocs und Material for MkDocs (beide MIT-Lizenz) mit den Plugins für Suche, Weiterleitungen, Bildergalerie, Minifizierung und Datum der letzten Änderung. Die genauen Versionen stehen in der [requirements.txt](https://github.com/mandariOSS/docs/blob/main/requirements.txt) des Dokumentations-Repositories.
