---
title: Konfiguration
description: Referenz der Umgebungsvariablen einer mandari-Installation. Pflichtwerte, Anmeldung, E-Mail, Datenbank, Suche, Worker und Ereignisse, Texterkennung, KI, OParl-API, offene Daten, Dokument-Cache und Ablage, Betriebsprüfungen, Bürgerportal, Session, Live-Übertragungen, Ingestor.
---

# Konfiguration

mandari wird über Umgebungsvariablen konfiguriert, in der Docker-Installation über die Datei `.env`. Diese Seite ist die Referenz. Werte in der Spalte Standard gelten, wenn die Variable nicht gesetzt ist.

## Pflichtwerte

| Variable | Bedeutung |
|----------|-----------|
| `DOMAIN` | Domain der Installation, zum Beispiel `mandari.example.org`. Bei `localhost` bleibt HTTPS aus. |
| `ACME_EMAIL` | E-Mail-Adresse für Zertifikatshinweise von Let's Encrypt |
| `SECRET_KEY` | Django-Geheimschlüssel, lang und zufällig |
| `ENCRYPTION_MASTER_KEY` | Base64-kodierter 256-Bit-Schlüssel (`openssl rand -base64 32`). Verschlüsselt die mandantenspezifischen Schlüssel. Nie einfach austauschen, sonst sind verschlüsselte Daten unlesbar; für einen Wechsel siehe `ENCRYPTION_MASTER_KEY_PREVIOUS`. |
| `DATABASE_URL` | Verbindung zur Datenbank, zum Beispiel `postgresql://user:pass@postgres:5432/mandari`. Im Compose-Stack aus `POSTGRES_USER`, `POSTGRES_PASSWORD` und `POSTGRES_DB` zusammengesetzt. |
| `ALLOWED_HOSTS` | Kommagetrennte Hostnamen, unter denen die Anwendung erreichbar ist |
| `SITE_URL` | Öffentliche Basis-URL, zum Beispiel `https://mandari.example.org`. Basis für Links in E-Mails und OParl-IDs. |
| `POSTGRES_PASSWORD`, `REDIS_PASSWORD` | Passwörter für Datenbank und Redis; ohne sie startet `docker-compose.yml` nicht |

Unter Docker Compose setzt `docker-compose.yml` `ALLOWED_HOSTS`, `SITE_URL` und `CSRF_TRUSTED_ORIGINS` selbst aus `DOMAIN` und `DATABASE_URL` aus den `POSTGRES_*`-Werten, außerdem `DEBUG=false`. Eigene Werte dieser Variablen in der `.env` wirken dort nicht.

## Allgemein

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `DEBUG` | `True` (`docker-compose.yml`: `false`) | Nur für die lokale Entwicklung einschalten; ohne Compose in Produktion ausdrücklich `false` setzen |
| `TZ` | `Europe/Berlin` | Zeitzone der Container |
| `IMAGE_TAG` | `latest` | Version der Container-Images, siehe [Updates](updates-backups.md) |
| `PROVISIONING_API_KEY` | leer | Aktiviert die Provisioning-API. Leer bedeutet abgeschaltet. |
| `COMPOSE_PROJECT_NAME` | `mandari` | Projektname für Container und Volumes; eine zweite Installation auf demselben Server braucht einen anderen |
| `ENCRYPTION_MASTER_KEY_PREVIOUS` | leer | Nur während eines Schlüsselwechsels: der bisherige Hauptschlüssel, mehrere durch Komma getrennt. Wird nur zum Lesen verwendet und danach wieder geleert; Ablauf in `docs/KRYPTOKONZEPT.md` im Repository. |
| `CSRF_TRUSTED_ORIGINS` | `SITE_URL` | Weitere vertrauenswürdige Ursprünge für Formulare und WebSockets, kommagetrennt mit Schema. Nur nötig, wenn ein anderer Host Formulare an diese Installation sendet. |
| `MAIN_DOMAIN` | Host aus `SITE_URL` ohne `www.` | Hauptdomain, etwa für Subdomains von Organisationen und als Standard von `WEBAUTHN_RP_ID` |
| `SUBDOMAIN_REDIRECT_ENABLED` | `true` | Subdomain einer Organisation leitet in ihren Arbeitsbereich weiter (`fraktion.example.org` nach `/work/fraktion/`) |
| `PORTAL_HOSTS` | leer | Bürgerportal einer Körperschaft unter eigenem Host: `host=slug`, kommagetrennt. Jeder Host muss zusätzlich in `ALLOWED_HOSTS` stehen; DNS, Zertifikat und Proxy richtet der Betrieb ein. |
| `MARKETING_URL` | leer (mit `DEBUG`: `http://localhost:8001`) | Adresse der Website, wenn sie nicht unter derselben Domain läuft |
| `DEMO_INSTANCE` | `false` | Macht die Installation zur öffentlichen Demo: kein Mailversand, keine KI, Passwort, zweiter Faktor und Konto nicht änderbar. Nie in einer Installation mit echten Daten setzen, siehe [Demo-Umgebung](demo-umgebung.md). |
| `DEMO_PASSWORD` | leer | Nur mit `DEMO_INSTANCE`: festes Passwort aller Demo-Konten |

Unter Docker Compose wirken aus dieser Tabelle `TZ` und `ENCRYPTION_MASTER_KEY_PREVIOUS`, die `docker-compose.yml` an die Dienste weiterreicht, sowie `IMAGE_TAG` und `COMPOSE_PROJECT_NAME`, die die Compose-Datei selbst liest; `DEBUG` steht dort fest auf `false`. Die übrigen tragen Sie unter Docker Compose im Abschnitt `x-app-environment` ein, im Helm-Chart in `app.extraEnv`; ein Eintrag nur in der `.env` wirkt nicht.

## Anmeldung und Zugriffsschutz

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `TWO_FACTOR_ENFORCEMENT` | `true` (mit `DEBUG`: `false`) | Pflicht zum zweiten Faktor für Administratoren und, je nach Einstellung, je Organisation bzw. Mandant |
| `TWO_FACTOR_EXEMPT_EMAIL_DOMAINS` | `demo.mandari.de` | E-Mail-Domains ohne diese Pflicht, nur für gemeinsam genutzte Demo-Zugänge ohne echte Daten |
| `TWO_FACTOR_REQUIRE_SECURITY_KEY_FOR_SUPERUSERS` | `false` | Plattform-Administration nur mit Sicherheitsschlüssel; erst einschalten, wenn die Schlüssel ausgegeben sind |
| `WEBAUTHN_RP_ID` | `MAIN_DOMAIN` | Relying-Party-ID für Sicherheitsschlüssel und Passkeys, gilt auch für Subdomains |
| `WEBAUTHN_RP_NAME` | `mandari` | Name, den Browser und Schlüssel anzeigen |
| `ADMIN_ALLOWED_NETWORKS` | leer | Django-Admin nur aus diesen Netzen (CIDR, kommagetrennt), leer = keine Beschränkung. Voraussetzung: Der vorgelagerte Proxy ersetzt `X-Forwarded-For` durch die echte Adresse. |
| `SECURE_HSTS_SECONDS` | `31536000` | Dauer des HSTS-Headers in Sekunden (nur ohne `DEBUG`) |
| `SECURE_SSL_REDIRECT` | `false` | Umleitung auf HTTPS durch Django; im Standard übernimmt das der Proxy |

Keine dieser Variablen reicht `docker-compose.yml` durch. Im Standard gilt also die Pflicht zum zweiten Faktor; abweichende Werte gehören in `x-app-environment` bzw. `app.extraEnv`. Für die Bedienung siehe [Konto und Sicherheit](../work/konto-und-sicherheit.md).

## E-Mail

Den SMTP-Zugang pflegen Sie am einfachsten im Admin in den Systemeinstellungen; die Variablen `EMAIL_*` gelten nur, wenn dort nichts hinterlegt ist. Organisationen in Work können zusätzlich einen eigenen SMTP-Zugang hinterlegen.

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `EMAIL_HOST`, `EMAIL_PORT` | leer, `587` | SMTP-Server und Port |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | leer | Zugangsdaten |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | `true`, `false` | STARTTLS bzw. TLS von Anfang an |
| `EMAIL_TIMEOUT` | `30` | Zeitgrenze der SMTP-Verbindung in Sekunden |
| `DEFAULT_FROM_EMAIL` | `noreply@mandari.de` | Absender, wenn die Systemeinstellungen keinen nennen |
| `EMAIL_MESSAGE_ID_DOMAIN` | Domain von `DEFAULT_FROM_EMAIL`, sonst Host aus `SITE_URL` | Domain hinter dem `@` der Message-ID und Name im EHLO. Setzen, wenn der Absender in den Systemeinstellungen eine andere Domain hat. |
| `MAIL_QUEUE` | leer | Mailarten, die nicht in der Anfrage, sondern als Auftrag im Worker (Warteschlange `mail`, mit Wiederholung) hinausgehen: kommagetrennte Muster wie `work.*,konto.*` oder `*`. Braucht `TASKS_BACKEND=journal`; leer = sofort. |
| `MAIL_QUEUE_MAX_BYTES` | `20971520` | Größere Mails (Text und Anhänge in Bytes) gehen sofort hinaus |
| `INSIGHT_DIGEST_FROM_EMAIL` | `DEFAULT_FROM_EMAIL` | Absender für Bürgerportal-Mails (Beschluss-Abos, Digest) |
| `INSIGHT_ALERT_EMAILS` | leer | Kommagetrennte Empfänger für Betriebsalarme. Ersatzweise `INSIGHT_MODERATION_EMAILS`, sonst alle Superuser. |
| `INSIGHT_MODERATION_EMAILS` | leer | Kommagetrennte Empfänger für Moderationshinweise der Ratsfragen |

`docker-compose.yml` reicht von diesen nur `DEFAULT_FROM_EMAIL`, `EMAIL_MESSAGE_ID_DOMAIN`, `MAIL_QUEUE`, `MAIL_QUEUE_MAX_BYTES` und `INSIGHT_ALERT_EMAILS` durch. Für den SMTP-Zugang unter Docker Compose deshalb die Systemeinstellungen nutzen oder die `EMAIL_*`-Variablen in `x-app-environment` eintragen.

## Datenbank, Cache, Suche

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | | Zugangsdaten des Datenbank-Containers |
| `REDIS_PASSWORD` | | Passwort des Redis-Containers |
| `REDIS_MAXMEMORY` | `256mb` | Speicherobergrenze von Redis |
| `REDIS_URL` | `redis://localhost:6379/0` | Adresse von Redis; `docker-compose.yml` setzt sie selbst mit `REDIS_PASSWORD` |
| `ELASTICSEARCH_URL` | `http://localhost:9200` (`docker-compose.yml`: `http://elasticsearch:9200`) | Adresse der Suche |
| `ELASTICSEARCH_AUTO_INDEX` | `True` | Änderungen sofort indexieren |
| `DB_POOL` | `true` | Verbindungspool der Anwendung an PostgreSQL |
| `DB_POOL_MIN`, `DB_POOL_MAX` | `2`, `10` | vorgehaltene bzw. höchstens gleichzeitig genutzte Verbindungen je Prozess |
| `DB_POOL_MAX_WAITING` | `20` | So viele Anfragen dürfen auf eine Verbindung warten; jede weitere bekommt sofort 503. `0` = unbegrenzt. |
| `DB_POOL_TIMEOUT` | `5` | Sekunden Wartezeit bei erschöpftem Pool, danach 503 |
| `DB_POOL_MAX_LIFETIME` | `1800` | Verbindungen nach so vielen Sekunden erneuern |
| `DB_CONN_MAX_AGE` | `60` | Lebensdauer einer Verbindung ohne Pool; mit Pool setzt die Anwendung `0` |

**PostgreSQL im Compose-Stack.** Diese Werte liest `docker-compose.yml` selbst aus der `.env`. Die Einstellungen von PostgreSQL wirken erst, wenn der Datenbankdienst neu startet (`docker compose up -d postgres`):

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `POSTGRES_MEM_LIMIT` | `1g` | Speichergrenze des Containers; `shared_buffers` ist auf ein Viertel davon ausgelegt |
| `POSTGRES_SHARED_BUFFERS`, `POSTGRES_EFFECTIVE_CACHE_SIZE` | `256MB`, `768MB` | Puffer und angenommener Cache des Betriebssystems |
| `POSTGRES_WORK_MEM`, `POSTGRES_MAINTENANCE_WORK_MEM` | `8MB`, `128MB` | Speicher je Sortierung bzw. für Wartung |
| `POSTGRES_RANDOM_PAGE_COST`, `POSTGRES_EFFECTIVE_IO_CONCURRENCY` | `1.1`, `200` | Annahmen für SSD-Speicher |
| `POSTGRES_MAX_CONNECTIONS` | `100` | Höchstzahl der Verbindungen aller Dienste zusammen |
| `POSTGRES_MAX_WAL_SIZE` | `2GB` | Größe des Write-Ahead-Logs bis zum Checkpoint |
| `POSTGRES_TEMP_FILE_LIMIT` | `5GB` | Obergrenze für temporäre Dateien je Sitzung |
| `POSTGRES_SHARED_PRELOAD_LIBRARIES` | `pg_stat_statements` | vorab geladene Erweiterungen; leer setzen schaltet die Abfragestatistik ab |
| `WEBSITE_DB`, `WEBSITE_SECRET_KEY` | `mandari_website`, `SECRET_KEY` | Datenbank und Schlüssel der Website |

Die `DB_POOL*`- und `DB_CONN_MAX_AGE`-Werte und `ELASTICSEARCH_AUTO_INDEX` reicht `docker-compose.yml` nicht an die Anwendung weiter; abweichende Werte gehören in `x-app-environment` bzw. `app.extraEnv`.

## Volltextsuche

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `SEARCH_RANKING` | `v2` | `v2`: alle Wörter müssen vorkommen, Unschärfe nur, wenn fast nichts gefunden wird, begrenzter Aktualitätsbonus. `v1`: bisherige Abfrage als Rückfall ohne Update (Neustart genügt). |
| `SEARCH_RECENCY_WEIGHT` | `1.0` | Aktualitätsbonus: Neue Treffer zählen höchstens (1 + Wert)-fach; `0` schaltet ihn ab |
| `SEARCH_MIN_RELEVANCE` | `0.05` | Treffer unter diesem Anteil des besten Werts ihres Index entfallen; `0` = alle behalten |
| `SEARCH_NAME_PART_MAX_DOCS` | `400` | Der Namensteil eines Straßennamens (etwa „witzleben“ aus „Witzlebenstraße“) zählt als eigene Lesart nur, wenn höchstens so viele Vorgänge und Dateien der Kommune ihn enthalten |
| `INSIGHT_SEARCH_PLACES` | `true` | Ortsband im Bürgerportal: erkannte Straße mit den neuesten Vorgängen im Umkreis und Karte, nur aus dem eigenen Straßenverzeichnis |
| `INSIGHT_SEARCH_PLACES_MIN_SHARE` | `0.5` | nur für Kommunen mit mindestens diesem Anteil verorteter Vorgänge |
| `INSIGHT_SEARCH_PLACES_RADIUS` | `500` | Umkreis in Metern |

`docker-compose.yml` reicht alle außer `SEARCH_NAME_PART_MAX_DOCS` durch.

## Worker, Aufträge und Ereignisse { #worker-auftraege-und-ereignisse }

Die Dienste `worker`, `worker-heavy` und `worker-live` führen Aufträge, die Ereignistechnik der Datendrehscheibe und die [Zeitpläne](cron.md) aus.

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `TASKS_BACKEND` | `immediate` | `immediate`: Aufträge laufen sofort in der Anfrage. `journal`: Aufträge gehen in die Datenbank und laufen im Worker. Erst umschalten, wenn die Worker laufen. Zeitpläne und die Aufträge aus dem Admin laufen in jedem Fall im Worker. |
| `TASKS_MAX_TASKS_PER_PROCESS` | `1000` | Nach so vielen Aufträgen startet der Runner neu |
| `TASKS_MAX_MEMORY_MB` | `400` | Oberhalb dieses Speichers startet der Runner neu; unter der Speichergrenze des Containers halten |
| `EVENTS_WORKER_REQUIRED` | leer | Braucht die Installation einen Worker? Leer: ja, für Zeitpläne und Aufträge, mit Ereignissen der Erzeuger auch für den Sequenzierer. `true`: alle Rollen. `false`: keine Meldung; ohne Worker laufen trotzdem keine Zeitpläne. Ohne nötigen Worker melden `/health/` und `/health/ready/` „degraded“. |
| `EVENTS_SCHEDULES_DISABLED` | leer | einzelne Zeitpläne abschalten, Namen kommagetrennt (siehe [Regelmäßige Aufgaben](cron.md#einzelne-zeitplaene-abschalten)) |
| `EVENTS_DB_DIRECT_URL` | leer | Direktverbindung zu PostgreSQL für den Weckruf der Ereignistechnik, nötig hinter PgBouncer im Transaktionsmodus |
| `INGESTOR_EVENTS_ENABLED` | `false` | Ingestor und Anwendung melden Änderungen am RIS-Bestand als Ereignisse ins Journal. Erst einschalten, wenn der Worker läuft. |
| `SESSION_EVENTS` | `aus` | Ereignisse aus mandari Session an die Datendrehscheibe: `aus`, `schatten` (Ereignisse werden geschrieben; scheitert das, bleibt die Änderung trotzdem bestehen) oder `aktiv` (Änderung und Ereignis atomar); je Mandant im Admin überschreibbar |
| `EVENTS_REDACT_NEUTRALIZE` | `false` | Nach einem Ereignis mit `operation=redact` personenbezogene Nutzlasten im Journal leeren (DSGVO) |
| `EVENTS_IDEMPOTENCY_RETENTION_DAYS` | `30` | Aufbewahrung der Idempotenzschlüssel der Befehle in Tagen |
| `EVENTS_JOURNAL_PURGE_ENABLED` | `false` | Journal täglich nach Frist aufräumen; vorher `manage.py events_purge --dry-run` prüfen |
| `EVENTS_JOURNAL_RETENTION_DAYS` | `90` | Aufbewahrung des Journals in Tagen; mindestens 90 und nie kürzer als `OPARL_CHANGES_RETENTION_DAYS` |
| `EVENTS_TASKS_DONE_RETENTION_DAYS`, `EVENTS_TASKS_DEAD_RETENTION_DAYS` | `14`, `90` | Aufbewahrung erledigter bzw. toter und fehlgeschlagener Aufträge in Tagen |
| `WORKER_PUSH_URL`, `WORKER_PUSH_TOKEN` | leer | „Worker lebt“ an einen externen Endpunkt der Statusseite melden |
| `WORKER_PUSH_INTERVAL` | `60` | Abstand dieser Meldungen in Sekunden |
| `WORKER_HEAVY_MEM_LIMIT` | `3g` | Speichergrenze des Dienstes `worker-heavy` (nur Docker Compose) |
| `WORKER_HEAVY_OCR_MEMORY_LIMIT_MB` | `2048` | Adressraum je Tesseract-Prozess in `worker-heavy`, höchstens Speichergrenze minus 1 GB (nur Docker Compose) |
| `WORKER_SERVICES` | `ingestor minutes-orchestrator worker worker-heavy worker-live` | Dienste, die `update.sh` während der Migrationen anhält |

`docker-compose.yml` reicht alle durch außer `EVENTS_IDEMPOTENCY_RETENTION_DAYS` und `WORKER_PUSH_INTERVAL`; `WORKER_HEAVY_*` liest die Compose-Datei selbst, `WORKER_SERVICES` das Skript `update.sh`. Im Helm-Chart heißen die wichtigsten `events.producers`, `events.changesFeed`, `events.journalPurge` und `worker.*`, siehe [Betrieb in Kubernetes](kubernetes.md).

## Datendrehscheibe: schrittweise Umstellungen

Diese Schalter stellen einzelne Aufgaben schrittweise auf Ereignisse und Abonnements um. Standard ist überall `aus`; `schatten` bzw. `probe` arbeitet neben dem bisherigen Weg und vergleicht nur. Alle brauchen den Worker; Voraussetzungen und Reihenfolge beim Umschalten beschreibt `DEPLOYMENT.md` im Repository.

| Variable | Werte | Bedeutung |
|----------|-------|-----------|
| `SEARCH_INDEX_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | Suchindex aus den Ereignissen; `schatten` pflegt einen Schattenindex neben dem Live-Index |
| `SEARCH_INDEX_SHADOW_BODIES` | Kennungen, kommagetrennt | Schattenbetrieb nur für diese Kommunen; leer = alle |
| `SEARCH_INDEX_SHADOW_MAX_DOCS` | Zahl, Standard `100000` | ungefähre Obergrenze der Dokumente in allen Schattenindizes; `0` = keine |
| `WORK_NOTIFICATION_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | Benachrichtigungen in Work über Ereignisse; `schatten` und `aktiv` brauchen `TASKS_BACKEND=journal` |
| `GEOREF_SUBSCRIPTION`, `SUMMARY_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | neuer Text eines Dokuments stößt die Verortung seines Vorgangs an bzw. verwirft dessen KI-Zusammenfassung |
| `RIS_SESSION_PROJECTOR` | `aus`, `schatten` | RIS-Bestand der Session-Mandanten aus deren Ereignissen, vorerst als unsichtbare Schatten-Quelle |
| `RIS_SESSION_PROJECTOR_TENANTS` | Kennungen, kommagetrennt | nur diese Session-Mandanten; leer = alle |
| `WORK_RIS_RELINK` | `aus`, `probe`, `aktiv` | Notizen, Positionen und Kommentare in Work folgen ihrem Tagesordnungspunkt bzw. ihrer Vorlage, wenn ein RIS seinen Stand neu veröffentlicht; `probe` meldet nur im Protokoll |
| `WORK_RIS_RELINK_INTERVAL_MINUTES` | Zahl, Standard `15` | Abstand des Abgleichs in Minuten |

`docker-compose.yml` reicht alle durch.

## Texterkennung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `TEXT_EXTRACTION_RUNNER` | `ingestor` | Wer den Text der RIS-Dateien erkennt: `ingestor` (der Ingestor lädt und erkennt selbst) oder `worker` (Aufträge im Dienst `worker-heavy`, die nur aus Ablage und Objektspeicher lesen). `worker` braucht `TASKS_BACKEND=journal`, sonst startet die Anwendung nicht. In Anwendung und Ingestor gleich setzen. |
| `TEXT_EXTRACTION_ENABLED` | `True` | Nur im Ingestor: Volltext aus Dokumenten extrahieren |
| `TEXT_EXTRACTION_MAX_SIZE_MB` | `50` | Größere Dateien werden nicht verarbeitet |
| `TEXT_EXTRACTION_QUEUE_DEPTH` | `20` | Nur mit `worker`: höchstens so viele Aufträge der Texterkennung warten oder laufen zugleich |
| `TEXT_EXTRACTION_STALE_MINUTES`, `TEXT_EXTRACTION_MAX_ATTEMPTS` | `60`, `3` | Eine Datei, die länger in Bearbeitung ist, gilt als abgebrochen; nach so vielen Abbrüchen als gescheitert |
| `TEXT_EXTRACTION_GIVE_UP_ALERT` | `5` | Die Prüfung „texterkennung“ wird erst ab so vielen aufgegebenen Dateien in 24 Stunden rot |
| `TEXT_EXTRACTION_BACKLOG_ALERT_HOURS` | `24` | Nur mit `worker`: Die Prüfung „dokumenttext“ wird rot, wenn ein abgelegtes Dokument länger auf seinen Text wartet |
| `OCR_DPI`, `OCR_MAX_MEGAPIXELS` | `200`, `8` | Auflösung der Texterkennung, je Seite gedeckelt |
| `OCR_MEMORY_LIMIT_MB` | `1024` | Adressraum je Tesseract-Prozess. `docker-compose.yml` setzt `512` für Anwendung und Worker und `384` für den Ingestor, `worker-heavy` hat `WORKER_HEAVY_OCR_MEMORY_LIMIT_MB`. |
| `OCR_PAGE_TIMEOUT`, `OCR_FILE_BUDGET_SECONDS`, `OCR_MAX_PAGES` | `120`, `1200`, `100` | Zeitgrenze je Seite, Zeitbudget und Seitenzahl je Datei; danach gilt der bis dahin erkannte Text |
| `MISTRAL_API_KEY`, `MISTRAL_BASE_URL` | leer | Optionale externe Texterkennung für öffentliche RIS-Dateien. Wirkt nur mit Schlüssel **und** einer Basis-URL, deren Host in `KI_ERLAUBTE_HOSTS` steht. |
| `MISTRAL_OCR_MODEL` | `pixtral-12b-2409` | Modell des externen Dienstes |
| `MISTRAL_OCR_RATE_LIMIT` | `60` | Anfragen pro Minute an den externen Dienst |

Die Erkennung liest zuerst die Textebene des PDFs, dann, falls eingerichtet, den externen Dienst, sonst und als Rückfall die lokale Texterkennung mit Tesseract. `docker-compose.yml` reicht `TEXT_EXTRACTION_RUNNER`, `TEXT_EXTRACTION_QUEUE_DEPTH`, `OCR_MEMORY_LIMIT_MB`, `MISTRAL_API_KEY` und `MISTRAL_BASE_URL` durch, die übrigen nicht. Umstellen auf `worker`: Ablauf „Dokumentkette einschalten“ in `DEPLOYMENT.md` im Repository.

## KI

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `KI_ERLAUBTE_HOSTS` | leer | Positivliste der Hosts, an die KI-Aufrufe gehen dürfen (kommagetrennt, genauer Vergleich, nur HTTPS). Leer = nichts erlaubt, die KI bleibt überall aus. Anbieter, Modell und Schlüssel stehen im Admin unter „KI-Einstellungen“. Gilt auch für den Ingestor. |
| `INSIGHT_CHAT_MAX_TOOL_ROUNDS`, `INSIGHT_CHAT_TIME_LIMIT_SECONDS` | `4`, `90` | KI-Assistent im Bürgerportal: Runden mit Werkzeugen und Zeitlimit je Antwort |
| `INSIGHT_CHAT_DAILY_MAX_CALLS`, `INSIGHT_CHAT_DAILY_MAX_TOKENS` | `500`, `1000000` | Kostenbremse: Tagesobergrenze aller Antworten zusammen; danach bis zum nächsten Tag keine Anfrage |
| `INSIGHT_MCP_ENABLED` | `false` | öffentlicher, nur lesender MCP-Server unter `/insight/mcp` |
| `INSIGHT_MCP_PER_IP_MINUTE`, `INSIGHT_MCP_PER_IP_DAY`, `INSIGHT_MCP_PER_MINUTE` | `30`, `500`, `300` | Grenzen je Adresse und Minute, je Adresse und Tag (Werkzeugaufrufe) und insgesamt je Minute; `0` schaltet eine Grenze ab |
| `INSIGHT_MCP_ALLOWED_ORIGINS` | leer | weitere Hosts, deren Browser-Clients zugreifen dürfen |

`docker-compose.yml` reicht alle durch.

## OParl-Aggregations-API

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `OPARL_BASE_URL` | `SITE_URL` + `/oparl` | Basis aller Objekt-IDs. Erlaubt die Auslieferung unter einer eigenen Subdomain. |
| `OPARL_API_PAGE_SIZE` | `100` | Objekte pro Listenseite, gilt auch für die Session-OParl-API |
| `OPARL_API_RATE_LIMIT` | `120` | Anfragen pro Minute je IP-Adresse, `0` deaktiviert das Limit |
| `OPARL_API_CACHE_SECONDS` | `60` | Cache-Dauer ungefilterter Listenseiten |
| `OPARL_LICENSE_URL` | leer | Lizenz am System-Objekt des Aggregators; leer = es gilt die Lizenz der Kommune |
| `OPARL_CHANGES_ENABLED` | `false` | Änderungsfeed und Snapshot je Kommune. Erst einschalten, wenn die Erzeuger laufen (`INGESTOR_EVENTS_ENABLED=true`, Worker), sonst täuschte ein leerer Feed vor, es habe sich nichts geändert. |
| `OPARL_CHANGES_RETENTION_DAYS` | `90` | Gültigkeit eines Cursors in Tagen, mindestens 30 |
| `OPARL_SNAPSHOT_PARALLEL` | `2` | gleichzeitig entstehende Snapshots; weitere Anfragen erhalten 503 mit `Retry-After` |

`docker-compose.yml` reicht nur `OPARL_CHANGES_ENABLED`, `OPARL_CHANGES_RETENTION_DAYS` und `OPARL_SNAPSHOT_PARALLEL` durch. Fehler des Änderungsfeeds beschreibt [Fehlertypen der Schnittstellen](../api/probleme.md).

## Offene Daten und Suchmaschinen

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `DCAT_ENABLED` | `false` | Katalog der offenen Ratsinformationen nach DCAT-AP.de unter `/data/dcat/` und je Session-Mandant. Erst einschalten, wenn Herausgeber und Kontakt stimmen. |
| `DCAT_PUBLISHER_NAME`, `DCAT_PUBLISHER_URL` | `mandari`, `SITE_URL` | Herausgeber der Datensätze des Aggregators (der Betreiber, keine Person) und seine Webseite |
| `DCAT_CONTACT_EMAIL` | leer | Funktionspostfach als Kontakt im Katalog |
| `DCAT_CONTRIBUTOR_ID` | leer | Kennung des Betreibers bei GovData |
| `DCAT_CACHE_SECONDS` | `300` | fertige Kataloge im Cache; `0` = aus |
| `INDEXNOW_KEY` | leer | Meldet neue, geänderte und entfernte Seiten des Bürgerportals über IndexNow an Suchmaschinen (nur öffentliche Adressen). 8 bis 128 Zeichen aus Buchstaben, Ziffern und `-`. Braucht den Worker und `INGESTOR_EVENTS_ENABLED=true`. |
| `INDEXNOW_ENDPOINT` | `https://api.indexnow.org/indexnow` | Adresse der Meldungen |

`docker-compose.yml` reicht nur `INDEXNOW_KEY` durch, an Anwendung, Worker und Website.

## Dokument-Cache und Quellen-Schonung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `OPARL_FILES_ROOT` | `<MEDIA_ROOT>/oparl_files` | Wurzelverzeichnis des Caches, im Container `/app/files` |
| `FILE_CACHE_MAX_MB` | `80` | Größere Dateien werden nicht gecacht, aber durchgereicht |
| `FILE_CACHE_MIN_FREE_GB` | `15` | Unter dieser Grenze freien Speichers wird nichts mehr geschrieben |
| `FILE_PROXY_TIMEOUT_SECONDS` | `15` | Lese-Timeout für Live-Abrufe bei der Quelle |
| `INSIGHT_SOURCE_BACKOFF_FAILURES` | `3` | Ab so vielen Fehlversuchen in Folge pausieren Cache und Proxy für die Quelle |

Details unter [Dokument-Cache](dokument-cache.md).

## Dokumentablage und Objektspeicher

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `FILE_STORE_LAYOUT` | `sha256` | Ablage nach SHA-256 mit Referenzzählung; `kommune` behält das ältere Verzeichnis je Kommune, ohne Deduplizierung und ohne Objektspeicher |
| `INGESTOR_STORES_FILES` | `false` (`docker-compose.yml`: `true`) | Der Ingestor legt Dateien, die er für den Text lädt, selbst in der Ablage ab; der Dokument-Cache holt sie dann nicht noch einmal |
| `FILE_CACHE_MAX_TOTAL_GB` | `0` | Obergrenze der Gesamtgröße in GB, `0` = unbegrenzt. Darüber verdrängt das stündliche Aufräumen die am wenigsten gebrauchten Dokumente. |
| `FILE_CACHE_EVICT_TARGET_PERCENT` | `90` | so weit unter die Obergrenze räumt das Aufräumen |
| `FILE_ACCEL_REDIRECT` | `false` | Dokumente liefert Caddy aus statt Django (Range, ETag). Voraussetzung: Caddyfile und Volume aus `docker-compose.yml`, sonst kommen leere Antworten an. |
| `FILE_PROXY_PACE_MAX_WAIT_SECONDS` | `5` | So lange wartet die Vorschau höchstens auf einen Abrufplatz bei der Quelle, sonst bittet sie um einen neuen Versuch |
| `FILE_PURGE_AFTER_DAYS` | `30` | Löschabgleich: Kopie und Text eines gesperrten Dokuments nach so vielen Tagen löschen |
| `FILE_PURGE_CONFIRM_GRACE_DAYS` | `7` | so viele Tage zusätzlich, wenn sich die Quelle vor dem Löschen nicht befragen lässt |
| `FILE_RECONCILE_MAX_MISSING` | `10` | Bremse: Melden in einem Lauf mehr Dokumente einer Quelle neu 404 oder 410, wird keines gesperrt |
| `DOCUMENT_FETCH_STALE_MINUTES`, `DOCUMENT_FETCH_MAX_QUEUED` | `30`, `200` | Ein Abruf beansprucht seine Datei höchstens so lange; je Quelle und Lauf höchstens so viele Abrufe |
| `DOCUMENT_FETCH_RETRY_ALERT_HOURS` | `6` | Die Prüfung „dokumentabruf“ wird rot, wenn fällige Wiederholungen länger liegen |
| `INSIGHT_FETCH_ALLOW_PRIVATE_NETWORKS` | `false` | Dokumente auch von Adressen im internen Netz abrufen; nur für ein Ratsinformationssystem im Intranet |
| `OBJ_ENABLED` | `false` | S3-kompatibler Objektspeicher für die Ablage; die lokale Ablage wird dann zum Zwischenspeicher. Erst einschalten, wenn `dokumentablage --umstellen` durchgelaufen ist. |
| `OBJ_ENDPOINT`, `OBJ_BUCKET`, `OBJ_REGION` | leer | Adresse, Bucket und Region |
| `OBJ_KEY`, `OBJ_SECRET` | leer | Zugangsdaten, nie im Repository |
| `OBJ_CACHE_MAX_GB` | `60` | Größe des lokalen Zwischenspeichers |
| `OBJ_CHECKSUMS` | `when_required` | Prüfsummen beim Hochladen: `when_required` (verträglich mit S3-kompatiblen Anbietern) oder `when_supported` |
| `OBJ_ADDRESSING_STYLE`, `OBJ_TIMEOUT_SECONDS`, `OBJ_FETCH_TOTAL_SECONDS` | `auto`, `30`, `60` | Adressierung, Zeitgrenze je Anfrage und Gesamtdauer eines Abrufs aus dem Objektspeicher |

`docker-compose.yml` reicht `FILE_STORE_LAYOUT`, `INGESTOR_STORES_FILES`, `FILE_CACHE_MAX_TOTAL_GB`, `FILE_CACHE_EVICT_TARGET_PERCENT`, `FILE_ACCEL_REDIRECT`, `INSIGHT_FETCH_ALLOW_PRIVATE_NETWORKS` sowie `OBJ_ENABLED`, `OBJ_ENDPOINT`, `OBJ_BUCKET`, `OBJ_KEY`, `OBJ_SECRET`, `OBJ_REGION`, `OBJ_CACHE_MAX_GB` und `OBJ_CHECKSUMS` durch, die übrigen nicht. Die Zugangsdaten des Objektspeichers können auch in einer eigenen Umgebungsdatei liegen: `docker compose --env-file .env --env-file <datei> up -d`.

## Quellenüberwachung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `INSIGHT_SOURCE_STALE_WARNING_HOURS` | `48` | Ab diesem Alter des letzten Syncs: Warnung |
| `INSIGHT_SOURCE_STALE_CRITICAL_DAYS` | `7` | Ab diesem Alter: kritisch, Alarm-E-Mail |

Details unter [Betriebsmonitor](monitoring.md).

## Betriebsprüfungen und Metriken

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `METRICS_ALLOWED_NETWORKS` | Loopback und private Netze | Der Endpunkt `/metrics/` antwortet nur diesen Netzen (CIDR, kommagetrennt) oder mit Token, sonst 404 |
| `METRICS_TOKEN` | leer | Bearer-Token für `/metrics/` von außerhalb dieser Netze |
| `METRICS_URL` | `http://127.0.0.1:8000/metrics/` (`docker-compose.yml`: `http://mandari:8000/metrics/`) | Woher die Prüfung der Service-Level im Worker die Metriken der Anwendung holt; leer = Fehlerquote nicht prüfen |
| `GATUS_URL` | leer | Statusseite (Gatus) für den monatlichen Verfügbarkeitsbericht; ohne sie gibt es den Zeitplan nicht |
| `SERVICE_LEVEL_DISK_MIN_FREE_PERCENT`, `SERVICE_LEVEL_DISK_MIN_FREE_GB` | `10`, `2` | Alarm bei weniger freiem Plattenplatz |
| `SERVICE_LEVEL_TLS_MIN_DAYS` | `14` | Alarm, wenn ein Zertifikat früher abläuft |
| `SERVICE_LEVEL_ERROR_RATE_MAX_PERCENT`, `SERVICE_LEVEL_ERROR_RATE_MIN_REQUESTS` | `1`, `100` | Alarm bei höherer Fehlerquote, gerechnet ab so vielen Anfragen |
| `SERVICE_LEVEL_QUEUE_MAX_AGE_MINUTES` | `120` | Alarm, wenn ein Auftrag länger wartet |
| `MONITOR_TLS_HOSTS` | leer | weitere Hosts, deren Zertifikat geprüft wird; `SITE_URL` immer |
| `HEALTH_READY_OPTIONAL` | leer | Prüfungen, die `/health/ready/` meldet, ohne deshalb 503 zu antworten, zum Beispiel `elasticsearch` |
| `REPORTS_ROOT` | `<MEDIA_ROOT>/berichte` | Ablage der Berichte, etwa des Verfügbarkeitsberichts; nie über `/media/` abrufbar |
| `LOG_FORMAT`, `LOG_LEVEL`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME` | | siehe [Logging und Tracing](logging-tracing.md) |

Die Alarme gehen an `INSIGHT_ALERT_EMAILS`. `docker-compose.yml` reicht nur `METRICS_URL` und `GATUS_URL` durch.

## Bürgerportal

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `INSIGHT_SUBSCRIPTIONS_ENABLED` | `false` | Abos zu Themen und Orten (`/insight/benachrichtigungen/`); eingeschaltet laufen die Zeitpläne `generate_alerts` und `send_digest`. Beschluss-Abos sind davon unabhängig. |
| `INSIGHT_QUESTIONS_ENABLED` | `false` | Ratsfragen (`/insight/fragen/`); aus heißt pausiert: Bisherige Fragen bleiben lesbar, neue sind nicht möglich, es gehen keine Mails hinaus |
| `INSIGHT_DIGEST_ENABLED` | `true` | Versand der Wochenmail durch `send_digest` |
| `INSIGHT_DIGEST_MAX_ALERTS_PER_MAIL` | `20` | Höchstzahl der Meldungen je Wochenmail |
| `GEOREF_ENABLED` | `true` | Verortung von Vorlagen insgesamt |
| `GEOREF_AUTO_ENABLED`, `GEOREF_AUTO_LIMIT`, `GEOREF_AUTO_INTERVAL_MINUTES` | `true`, `50`, `15` | automatischer Verortungslauf als Zeitplan: an oder aus, Vorlagen je Lauf, Abstand in Minuten |
| `GEOREF_TEXT_MAX_CHARS` | `8000` | Kürzung des Textes für die Verortung über KI und Photon |
| `PHOTON_API_URL`, `GEOCODING_RATE_LIMIT` | `https://photon.komoot.io/api/`, `5` | Geocoding-Dienst und Anfragen je Sekunde, etwa für die Nachbarschaftssuche |
| `MAP_MARKERS_CACHE_SECONDS` | `600` | Cache der Kartenmarker |

`docker-compose.yml` reicht nur `INSIGHT_SUBSCRIPTIONS_ENABLED` und `INSIGHT_QUESTIONS_ENABLED` durch.

## Session, Work und Protokollierung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `SESSION_PACKAGE_MAX_EMBED_MB`, `SESSION_PACKAGE_MAX_PAGES` | `200`, `3000` | Obergrenzen der PDF-Anlagen im Gesamt-PDF einer Sitzungsmappe; weitere erscheinen als Verweisseite, im ZIP-Paket bleiben alle |
| `AUDIT_ARCHIVE_ROOT` | `<MEDIA_ROOT>/audit_archive` | Archivpakete vor der fristgerechten Löschung; nie über `/media/` abrufbar |
| `AUDIT_ARCHIVE_STORAGE` | leer | statt des Verzeichnisses ein Speicher aus `STORAGES`, etwa ein S3-Speicher |
| `AUDIT_EXPORT_MAX_ROWS` | `100000` | Obergrenze eines Exports des Prüfprotokolls aus der Oberfläche; größere Zeiträume mit `manage.py export_audit_log` |
| `SECURITY_AUDIT_RETENTION_DAYS` | `365` | Aufbewahrung des Sicherheitsprotokolls in Tagen |
| `FACTION_SCHEDULE_INTERVAL_MINUTES`, `FACTION_SCHEDULE_HORIZON_DAYS` | `60`, `90` | Work: Fraktionssitzungen aus Sitzungsreihen; Abstand des Laufs in Minuten und Zeitraum in Tagen, für den Sitzungen im Voraus entstehen |

`docker-compose.yml` reicht keine davon durch.

## Live-Übertragungen

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `LIVE_UEBERTRAGUNG_AKTIV` | `false` | Status der Streaming-Anbieter rund um die Sitzungen abfragen und während der Übertragung Tagesordnungspunkt und Namen aus Einzelbildern lesen (nur im Speicher). Aus: keine Anfragen nach außen, kein Zeitplan. An: Dienst `worker-live` muss laufen. |
| `LIVE_PROTOKOLL_TAGE` | `90` | Aufbewahrung des Protokolls in Tagen |
| `LIVE_TESSERACT_CMD`, `LIVE_TESSDATA_DIR` | `tesseract`, leer | Programm und Sprachdaten der Texterkennung |
| `LIVE_OCR_MEMORY_LIMIT_MB`, `LIVE_OCR_TIMEOUT_SECONDS` | `256`, `20` | Speicher- und Zeitgrenze je Erkennung |

`docker-compose.yml` reicht `LIVE_UEBERTRAGUNG_AKTIV` und `LIVE_PROTOKOLL_TAGE` durch, im Helm-Chart heißt der Schalter `liveStreams.enabled`.

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
