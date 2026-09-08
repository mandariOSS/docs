---
title: Abhängigkeiten (SBOM)
description: Software Bill of Materials der mandari-Plattform. Wo die Liste der Abhängigkeiten mit Lizenzen liegt und welche externen Dienste optional eingebunden sind.
---

# Abhängigkeiten (SBOM)

Die Software Bill of Materials der mandari-Plattform wird im Hauptrepository gepflegt, damit sie mit dem Code versioniert bleibt:

**[docs/SBOM.md im Repository mandariOSS/mandari](https://github.com/mandariOSS/mandari/blob/main/docs/SBOM.md)**

Sie listet die direkten Abhängigkeiten der Django-Anwendung, des Ingestors und des gemeinsamen OParl-Pakets mit Version, Lizenz und Zweck. Transitive Abhängigkeiten sind nicht vollständig aufgeführt. Eine maschinenlesbare CycloneDX-Erzeugung in der CI ist geplant.

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
