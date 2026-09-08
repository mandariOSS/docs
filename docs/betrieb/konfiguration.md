---
title: Konfiguration
description: Referenz aller Umgebungsvariablen einer mandari-Installation. Pflichtwerte, E-Mail, Suche, Texterkennung, OParl-API, Dokument-Cache, Quellenüberwachung, Ingestor.
---

# Konfiguration

mandari wird über Umgebungsvariablen konfiguriert, in der Docker-Installation über die Datei `.env`. Diese Seite ist die Referenz. Werte in der Spalte Standard gelten, wenn die Variable nicht gesetzt ist.

## Pflichtwerte

| Variable | Bedeutung |
|----------|-----------|
| `DOMAIN` | Domain der Installation, zum Beispiel `mandari.example.org`. Bei `localhost` bleibt HTTPS aus. |
| `ACME_EMAIL` | E-Mail-Adresse für Zertifikatshinweise von Let's Encrypt |
| `SECRET_KEY` | Django-Geheimschlüssel, lang und zufällig |
| `ENCRYPTION_MASTER_KEY` | Base64-kodierter 256-Bit-Schlüssel. Verschlüsselt die mandantenspezifischen Schlüssel. Nach der Installation nie ändern. |
| `DATABASE_URL` | Verbindung zur Datenbank, zum Beispiel `postgresql://user:pass@postgres:5432/mandari`. Im Compose-Stack aus `POSTGRES_USER`, `POSTGRES_PASSWORD` und `POSTGRES_DB` zusammengesetzt. |
| `ALLOWED_HOSTS` | Kommagetrennte Hostnamen, unter denen die Anwendung erreichbar ist |
| `SITE_URL` | Öffentliche Basis-URL, zum Beispiel `https://mandari.example.org`. Basis für Links in E-Mails und OParl-IDs. |

## Allgemein

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `DEBUG` | `False` | Nur für die lokale Entwicklung einschalten |
| `TZ` | `Europe/Berlin` | Zeitzone der Container |
| `IMAGE_TAG` | `latest` | Version der Container-Images, siehe [Updates](updates-backups.md) |
| `PROVISIONING_API_KEY` | leer | Aktiviert die Provisioning-API. Leer bedeutet abgeschaltet. |

## E-Mail

E-Mail kann alternativ im Admin unter *Site-Einstellungen* gepflegt werden. Organisationen in Work können zusätzlich einen eigenen SMTP-Zugang hinterlegen.

| Variable | Bedeutung |
|----------|-----------|
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP-Server und Port |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Zugangsdaten |
| `EMAIL_USE_TLS` | `True` für STARTTLS |
| `DEFAULT_FROM_EMAIL` | Absenderadresse |
| `INSIGHT_DIGEST_FROM_EMAIL` | Absender für Bürgerportal-Mails (Beschluss-Abos, Digest). Ersatzweise `DEFAULT_FROM_EMAIL`. |
| `INSIGHT_ALERT_EMAILS` | Kommagetrennte Empfänger für Betriebsalarme. Ersatzweise `INSIGHT_MODERATION_EMAILS`, sonst alle Superuser. |
| `INSIGHT_MODERATION_EMAILS` | Kommagetrennte Empfänger für Moderationshinweise der Ratsfragen |

## Datenbank, Cache, Suche

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | | Zugangsdaten des Datenbank-Containers |
| `REDIS_PASSWORD` | | Passwort des Redis-Containers |
| `REDIS_MAXMEMORY` | `256mb` | Speicherobergrenze von Redis |
| `ELASTICSEARCH_URL` | `http://elasticsearch:9200` | Adresse der Suche |
| `ELASTICSEARCH_AUTO_INDEX` | `True` | Änderungen sofort indexieren |

## Texterkennung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `TEXT_EXTRACTION_ENABLED` | `True` | Volltext aus Dokumenten extrahieren |
| `TEXT_EXTRACTION_ASYNC` | `True` | Extraktion im Hintergrund statt beim Abruf |
| `TEXT_EXTRACTION_MAX_SIZE_MB` | `50` | Größere Dateien werden nicht verarbeitet |
| `MISTRAL_API_KEY` | leer | Optionaler externer OCR-Dienst für gescannte Dokumente. Ohne Schlüssel läuft die lokale Texterkennung. |
| `MISTRAL_OCR_RATE_LIMIT` | `60` | Anfragen pro Minute an den externen Dienst |

Die Extraktion versucht zuerst die Textebene des PDFs, dann die lokale Texterkennung, optional den externen Dienst.

## OParl-Aggregations-API

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `OPARL_BASE_URL` | `SITE_URL` + `/oparl` | Basis aller Objekt-IDs. Erlaubt die Auslieferung unter einer eigenen Subdomain. |
| `OPARL_API_PAGE_SIZE` | `100` | Objekte pro Listenseite, gilt auch für die Session-OParl-API |
| `OPARL_API_RATE_LIMIT` | `120` | Anfragen pro Minute je IP-Adresse, `0` deaktiviert das Limit |
| `OPARL_API_CACHE_SECONDS` | `60` | Cache-Dauer ungefilterter Listenseiten |

## Dokument-Cache und Quellen-Schonung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `OPARL_FILES_ROOT` | `<MEDIA_ROOT>/oparl_files` | Wurzelverzeichnis des Caches, im Container `/app/files` |
| `FILE_CACHE_MAX_MB` | `80` | Größere Dateien werden nicht gecacht, aber durchgereicht |
| `FILE_CACHE_MIN_FREE_GB` | `15` | Unter dieser Grenze freien Speichers wird nichts mehr geschrieben |
| `FILE_PROXY_TIMEOUT_SECONDS` | `15` | Lese-Timeout für Live-Abrufe bei der Quelle |
| `INSIGHT_SOURCE_BACKOFF_FAILURES` | `3` | Ab so vielen Fehlversuchen in Folge pausieren Cache und Proxy für die Quelle |

Details unter [Dokument-Cache](dokument-cache.md).

## Quellenüberwachung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `INSIGHT_SOURCE_STALE_WARNING_HOURS` | `48` | Ab diesem Alter des letzten Syncs: Warnung |
| `INSIGHT_SOURCE_STALE_CRITICAL_DAYS` | `7` | Ab diesem Alter: kritisch, Alarm-E-Mail |

Details unter [Betriebsmonitor](monitoring.md).

## Ingestor

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `INGESTOR_INTERVAL` | `15` | Minuten zwischen inkrementellen Läufen |
| `INGESTOR_FULL_SYNC_HOUR` | `3` | Stunde des täglichen Voll-Syncs |
| `INGESTOR_CONCURRENT` | `10` | Parallel verarbeitete Quellen |
| `SCRAPER_USER_AGENT` | `mandari-ingestor (+https://mandari.de/crawler)` | User-Agent der Scraper-Quellen |
| `SCRAPER_TOMBSTONE_FULL_CRAWLS` | `3` | Nach so vielen Voll-Crawls ohne Sichtung gilt ein Objekt als gelöscht |
| `SCRAPER_PARSE_QUOTA_WARN` | `0.8` | Warnung, wenn weniger als dieser Anteil der Seiten geparst werden konnte |

Details unter [Quellen anbinden](quellen-anbinden.md).
