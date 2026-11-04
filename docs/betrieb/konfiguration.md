---
title: Konfiguration
description: Referenz der Umgebungsvariablen einer mandari-Installation. Pflichtwerte, Anmeldung, E-Mail, Datenbank, Suche, Worker und Ereignisse, Texterkennung, KI, OParl-API, offene Daten, Dokument-Cache und Ablage, Betriebsprüfungen, Bürgerportal, Session, Live-Übertragungen, Ingestor.
---

# Konfiguration

mandari wird über Umgebungsvariablen konfiguriert, in der Docker-Installation über die Datei `.env`. Diese Seite ist die Referenz. Werte in der Spalte Standard gelten, wenn die Variable nicht gesetzt ist.

Die Seite nennt jede Umgebungsvariable, die die Anwendung (`mandari/mandari/settings.py` und übriger Code) und `docker-compose.yml` lesen, dazu die wichtigen des Ingestors. Ob das noch stimmt, prüft das Skript `tests/umgebungsvariablen.py` im [Repository der Dokumentation](https://github.com/mandariOSS/docs) gegen einen Checkout der Anwendung; mit `--liste` gibt es alle Variablen mit dem Standardwert im Code und der Fundstelle aus.

!!! note "Nicht jede Variable erreicht die Dienste"
    Unter Docker Compose erreicht einen Dienst nur, was `docker-compose.yml` in seinem Abschnitt `environment` nennt. Die Anwendung und ihre Worker erhalten die Variablen aus `x-app-environment`, der Ingestor die aus seinem eigenen Abschnitt. Fehlt eine Variable dort, wirkt ein Eintrag nur in der `.env` nicht: Tragen Sie sie in einer `docker-compose.override.yml` beim Dienst ein (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)). Im Helm-Chart gehören solche Variablen in `app.extraEnv` (Anwendung und Worker) bzw. `ingestor.extraEnv`.

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

## Eigene Variablen unter Docker Compose { #eigene-variablen }

Unter Docker Compose erhält ein Dienst nur die Variablen, die `docker-compose.yml` ihm nennt; die `.env` dient dort nur zum Einsetzen von Werten in die Compose-Datei. Viele Variablen dieser Seite reicht `docker-compose.yml` nicht durch, das steht bei jeder Gruppe.

Ändern Sie dafür nicht die versionierte `docker-compose.yml`. `update.sh` holt bei jedem Update den neuen Stand aus Git; mit einer geänderten Datei kann das scheitern, und die Installation läuft dann mit der alten Compose-Datei weiter. Legen Sie stattdessen eine `docker-compose.override.yml` daneben; das Repository ignoriert sie, und Docker Compose liest sie ohne weitere Angabe mit. Anwendung und Worker teilen sich in `docker-compose.yml` einen gemeinsamen Block (`x-app-environment`), auf den der Dienst `mandari` und die Worker nur verweisen. In der Override-Datei steht eine Variable deshalb bei jedem Dienst, der sie braucht, also für Anwendung und Worker bei `mandari`, `worker`, `worker-heavy` und `worker-live`:

```yaml
# docker-compose.override.yml
x-eigene-umgebung: &eigene-umgebung
  EMAIL_HOST: smtp.example.org
  EMAIL_HOST_USER: mandari@example.org
  EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD}   # Wert aus der .env

services:
  mandari:
    environment: *eigene-umgebung
  worker:
    environment: *eigene-umgebung
  worker-heavy:
    environment: *eigene-umgebung
  worker-live:
    environment: *eigene-umgebung
```

Compose ergänzt die Umgebung dieser Dienste um die Einträge; danach `docker compose up -d`. Ist `COMPOSE_FILE` gesetzt (Betrieb auf mehreren Servern), liest Compose die Override-Datei nicht von selbst; dann gehört sie mit in diese Liste. Im Helm-Chart gehören solche Variablen in `app.extraEnv` (Anwendung und Worker) bzw. `ingestor.extraEnv`.

## Allgemein

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `DEBUG` | `True` (`docker-compose.yml`: `false`) | Nur für die lokale Entwicklung einschalten; ohne Compose in Produktion ausdrücklich `false` setzen |
| `TZ` | `Europe/Berlin` | Zeitzone der Container |
| `IMAGE_TAG` | `latest` | Version der Container-Images, siehe [Updates](updates-backups.md) |
| `PROVISIONING_API_KEY` | leer | Aktiviert die Provisioning-API unter `/api/provisioning/`. Leer bedeutet abgeschaltet. |
| `PROVISIONING_V2_API_KEY` | leer | Eigener Schlüssel (Bearer) für die Provisioning-API v2 unter `/api/provisioning/v2/`. Leer bedeutet abgeschaltet; alle Adressen antworten dann mit 404. |
| `PROVISIONING_V2_ALLOWED_NETWORKS` | leer | Provisioning-API v2 nur aus diesen Netzen (CIDR, kommagetrennt), leer = keine Beschränkung; andere Absender erhalten 404. Voraussetzung wie bei `ADMIN_ALLOWED_NETWORKS`. |
| `SEITENHINWEIS` | leer | Kurzer Betriebshinweis oben in Insight und Work, etwa bei einer Störung außerhalb von mandari. Leer = kein Hinweis. Wirkt nach dem Neuerstellen der Container, ohne Update. |
| `SEITENHINWEIS_LINK` | `https://status.mandari.de/` | Ziel des Links im Betriebshinweis; für eine eigene Installation auf die eigene Statusseite setzen |
| `COMPOSE_PROJECT_NAME` | `mandari` | Projektname für Container und Volumes; eine zweite Installation auf demselben Server braucht einen anderen |
| `ENCRYPTION_MASTER_KEY_PREVIOUS` | leer | Nur während eines Schlüsselwechsels: der bisherige Hauptschlüssel, mehrere durch Komma getrennt. Wird nur zum Lesen verwendet und danach wieder geleert; Ablauf in `docs/KRYPTOKONZEPT.md` im Repository. |
| `CSRF_TRUSTED_ORIGINS` | `SITE_URL` | Weitere vertrauenswürdige Ursprünge für Formulare und WebSockets, kommagetrennt mit Schema. Nur nötig, wenn ein anderer Host Formulare an diese Installation sendet. |
| `MAIN_DOMAIN` | Host aus `SITE_URL` ohne `www.` | Hauptdomain, etwa für Subdomains von Organisationen und als Standard von `WEBAUTHN_RP_ID` |
| `SUBDOMAIN_REDIRECT_ENABLED` | `true` | Subdomain einer Organisation leitet in ihren Arbeitsbereich weiter (`fraktion.example.org` nach `/work/fraktion/`) |
| `PORTAL_HOSTS` | leer | Bürgerportal einer Körperschaft unter eigenem Host: `host=slug`, kommagetrennt. Jeder Host muss zusätzlich in `ALLOWED_HOSTS` stehen; DNS, Zertifikat und Proxy richtet der Betrieb ein. |
| `MARKETING_URL` | leer (mit `DEBUG`: `http://localhost:8001`) | Adresse der Website, wenn sie nicht unter derselben Domain läuft |
| `DEMO_INSTANCE` | `false` | Macht die Installation zur öffentlichen Demo: kein Mailversand, keine KI, Passwort, zweiter Faktor und Konto nicht änderbar. Nie in einer Installation mit echten Daten setzen, siehe [Demo-Umgebung](demo-umgebung.md). |
| `DEMO_PASSWORD` | leer | Nur mit `DEMO_INSTANCE`: festes Passwort aller Demo-Konten |
| `OLD_MASTER_KEY` | leer | Nur für `manage.py rotate_encryption`: ein zusätzlicher alter Hauptschlüssel, etwa nach einem Datenbankumzug. Im laufenden Betrieb gilt `ENCRYPTION_MASTER_KEY_PREVIOUS`. |
| `DJANGO_VITE_DEV_MODE` | leer | Nur in der Entwicklung: Skripte und Styles kommen vom Vite-Dev-Server mit Hot Reload statt aus dem gebauten Manifest, siehe [Entwicklung](../entwicklung/index.md#lokal-entwickeln) |

Unter Docker Compose wirken aus dieser Tabelle `TZ` und `ENCRYPTION_MASTER_KEY_PREVIOUS`, die `docker-compose.yml` an die Dienste weiterreicht, sowie `IMAGE_TAG` und `COMPOSE_PROJECT_NAME`, die die Compose-Datei selbst liest; `DEBUG` steht dort fest auf `false`. `OLD_MASTER_KEY` gehört nicht in die `.env`, sondern nur in den einzelnen Aufruf, etwa `docker compose exec -e OLD_MASTER_KEY mandari python manage.py rotate_encryption` mit dem Wert in der Umgebung der aufrufenden Shell. Die übrigen tragen Sie unter Docker Compose in einer `docker-compose.override.yml` (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)) ein, im Helm-Chart in `app.extraEnv`; ein Eintrag nur in der `.env` wirkt nicht.

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

Keine dieser Variablen reicht `docker-compose.yml` durch. Im Standard gilt also die Pflicht zum zweiten Faktor; abweichende Werte gehören unter Docker Compose in einer `docker-compose.override.yml` (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)), im Helm-Chart in `app.extraEnv`. Für die Bedienung siehe [Konto und Sicherheit](../work/konto-und-sicherheit.md).

## E-Mail

Den SMTP-Zugang pflegen Sie am einfachsten im Admin in den Systemeinstellungen; die Variablen `EMAIL_*` gelten nur, wenn dort nichts hinterlegt ist. Organisationen in Work können zusätzlich einen eigenen SMTP-Zugang hinterlegen.

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `EMAIL_HOST`, `EMAIL_PORT` | leer, `587` | SMTP-Server und Port |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | leer | Zugangsdaten |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | `true`, `false` | STARTTLS bzw. TLS von Anfang an |
| `EMAIL_TIMEOUT` | `30` | Zeitgrenze der SMTP-Verbindung in Sekunden |
| `EMAIL_BACKEND` | Systemeinstellungen (mit `DEBUG`: Ausgabe auf der Konsole) | Versandweg der Plattform als Python-Pfad. Der Standard liest den SMTP-Zugang aus den Systemeinstellungen und fällt auf die `EMAIL_*`-Werte zurück; nur für Tests oder Sonderfälle ändern. |
| `DEFAULT_FROM_EMAIL` | `noreply@mandari.de` | Absender, wenn die Systemeinstellungen keinen nennen |
| `SERVER_EMAIL` | `DEFAULT_FROM_EMAIL` | Absender der Fehlermails, die Django selbst verschickt |
| `EMAIL_MESSAGE_ID_DOMAIN` | Domain von `DEFAULT_FROM_EMAIL`, sonst Host aus `SITE_URL` | Domain hinter dem `@` der Message-ID und Name im EHLO. Setzen, wenn der Absender in den Systemeinstellungen eine andere Domain hat. |
| `MAIL_QUEUE` | leer | Mailarten, die nicht in der Anfrage, sondern als Auftrag im Worker (Warteschlange `mail`, mit Wiederholung) hinausgehen: kommagetrennte Muster wie `work.*,konto.*` oder `*`. Braucht `TASKS_BACKEND=journal`; leer = sofort. |
| `MAIL_QUEUE_MAX_BYTES` | `20971520` | Größere Mails (Text und Anhänge in Bytes) gehen sofort hinaus |
| `INSIGHT_DIGEST_FROM_EMAIL` | `DEFAULT_FROM_EMAIL` | Absender für Bürgerportal-Mails (Beschluss-Abos, Digest) |
| `INSIGHT_ALERT_EMAILS` | leer | Kommagetrennte Empfänger für Betriebsalarme. Ersatzweise `INSIGHT_MODERATION_EMAILS`, sonst alle Superuser. |
| `INSIGHT_MODERATION_EMAILS` | leer | Kommagetrennte Empfänger für Moderationshinweise der Ratsfragen |

`docker-compose.yml` reicht von diesen nur `DEFAULT_FROM_EMAIL`, `EMAIL_MESSAGE_ID_DOMAIN`, `MAIL_QUEUE`, `MAIL_QUEUE_MAX_BYTES` und `INSIGHT_ALERT_EMAILS` durch. Für den SMTP-Zugang unter Docker Compose deshalb die Systemeinstellungen nutzen oder die `EMAIL_*`-Variablen in einer `docker-compose.override.yml` (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)) eintragen.

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
| `DB_PGBOUNCER` | `false` | `DATABASE_URL` zeigt auf PgBouncer im Transaktionsmodus: keine serverseitigen Cursor, keine vorbereiteten Anweisungen. Nur zusammen mit einem Pooler setzen. |
| `DB_DIRECT_URL` | leer | Direktverbindung zu PostgreSQL für `migrate`, `safemigrate` und `events_after_restore`, wenn `DB_PGBOUNCER` gesetzt ist; ohne sie laufen auch diese über den Pooler |
| `APP_PROCESSES` | `1` | Zahl der Anwendungsprozesse an Port 8000 (1 bis 64). Jeder Prozess hat einen eigenen Pool mit `DB_POOL_MAX` Verbindungen und braucht rund 1 GB Arbeitsspeicher. Im Helm-Chart nicht setzen, dort skaliert `app.replicas`. |

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

**Anwendung im Compose-Stack.** Auch diese Werte liest `docker-compose.yml` selbst aus der `.env` und setzt daraus die Variablen nur des Dienstes `mandari`; Worker, Ingestor, Protokoll-Orchestrator und Website verbinden sich immer direkt mit PostgreSQL. Danach `docker compose up -d mandari`:

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `APP_PROCESSES` | `1` | Anwendungsprozesse, siehe oben |
| `MANDARI_MEM_LIMIT` | `1g` | Speichergrenze des Dienstes `mandari` für alle Prozesse zusammen; mit `APP_PROCESSES` mitziehen, rund 1 GB je Prozess |
| `MANDARI_DB_POOL_MAX` | `10` | wird zu `DB_POOL_MAX` der Anwendung |
| `MANDARI_DB_HOST` | `postgres` | Host in `DATABASE_URL` der Anwendung; `pgbouncer` für den Weg über PgBouncer |
| `MANDARI_DB_PGBOUNCER` | `false` | wird zu `DB_PGBOUNCER`; `DB_DIRECT_URL` setzt `docker-compose.yml` selbst auf `postgres` |
| `COMPOSE_PROFILES` | leer | `pgbouncer` startet den optionalen Dienst `pgbouncer` |
| `PGBOUNCER_MAX_CLIENT_CONN` | `200` | Verbindungen der Anwendung zu PgBouncer, höchstens: `MANDARI_DB_POOL_MAX` × Prozesse mit Reserve |
| `PGBOUNCER_DEFAULT_POOL_SIZE` | `20` | Verbindungen von PgBouncer zu PostgreSQL; zählen gegen `POSTGRES_MAX_CONNECTIONS` |

PgBouncer schalten Sie mit drei Zeilen gemeinsam ein: `COMPOSE_PROFILES=pgbouncer`, `MANDARI_DB_HOST=pgbouncer` und `MANDARI_DB_PGBOUNCER=true`, dazu meist ein größerer `MANDARI_DB_POOL_MAX`. Zeigt die Anwendung ohne den Schalter auf PgBouncer, scheitern Seiten mit großen Ergebnissen unter Last. Lohnend ist PgBouncer ab zwei Anwendungsprozessen; ohne ihn erhöhen Sie `POSTGRES_MAX_CONNECTIONS` je zusätzlichem Prozess um `DB_POOL_MAX`. Verbindungsrechnung, Prüfung und Rückweg beschreibt `DEPLOYMENT.md` im Repository („PgBouncer für die Webanwendung“, „Mehrere Anwendungsprozesse“).

`DB_POOL`, `DB_POOL_MIN`, `DB_POOL_MAX_WAITING`, `DB_POOL_TIMEOUT`, `DB_POOL_MAX_LIFETIME`, `DB_CONN_MAX_AGE` und `ELASTICSEARCH_AUTO_INDEX` reicht `docker-compose.yml` nicht an die Anwendung weiter; abweichende Werte gehören unter Docker Compose in einer `docker-compose.override.yml` (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)), im Helm-Chart in `app.extraEnv`.

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
| `EVENTS_VALIDATE_CONTRACTS` | wie `DEBUG` | Jedes veröffentlichte Ereignis zusätzlich gegen seinen Vertrag prüfen. Im Betrieb aus; dort gelten nur die Formatprüfungen, die Verträge sichern die Tests. |
| `EVENTS_IDEMPOTENCY_RETENTION_DAYS` | `30` | Aufbewahrung der Idempotenzschlüssel der Befehle in Tagen |
| `EVENTS_JOURNAL_PURGE_ENABLED` | `false` | Journal täglich nach Frist aufräumen; vorher `manage.py events_purge --dry-run` prüfen |
| `EVENTS_JOURNAL_RETENTION_DAYS` | `90` | Aufbewahrung des Journals in Tagen; mindestens 90 und nie kürzer als `OPARL_CHANGES_RETENTION_DAYS` |
| `EVENTS_TASKS_DONE_RETENTION_DAYS`, `EVENTS_TASKS_DEAD_RETENTION_DAYS` | `14`, `90` | Aufbewahrung erledigter bzw. toter und fehlgeschlagener Aufträge in Tagen |
| `WORKER_PUSH_URL`, `WORKER_PUSH_TOKEN` | leer | „Worker lebt“ an einen externen Endpunkt der Statusseite melden |
| `WORKER_PUSH_INTERVAL` | `60` | Abstand dieser Meldungen in Sekunden |
| `WORKER_HEAVY_MEM_LIMIT` | `3g` | Speichergrenze des Dienstes `worker-heavy` (nur Docker Compose) |
| `WORKER_HEAVY_OCR_MEMORY_LIMIT_MB` | `2048` | Adressraum je Tesseract-Prozess in `worker-heavy`, höchstens Speichergrenze minus 1 GB (nur Docker Compose) |
| `WORKER_SERVICES` | `ingestor minutes-orchestrator worker worker-heavy worker-live` | Dienste, die `update.sh` während der Migrationen anhält |

`docker-compose.yml` reicht alle durch außer `EVENTS_VALIDATE_CONTRACTS`, `EVENTS_IDEMPOTENCY_RETENTION_DAYS` und `WORKER_PUSH_INTERVAL`; `WORKER_HEAVY_*` liest die Compose-Datei selbst, `WORKER_SERVICES` das Skript `update.sh`. Im Helm-Chart heißen die wichtigsten `events.producers`, `events.changesFeed`, `events.journalPurge` und `worker.*`, siehe [Betrieb in Kubernetes](kubernetes.md).

## Datendrehscheibe: schrittweise Umstellungen

Diese Schalter stellen einzelne Aufgaben schrittweise auf Ereignisse und Abonnements um. Standard ist überall `aus`, außer bei `URHEBER_SUBSCRIPTION`; `schatten` bzw. `probe` arbeitet neben dem bisherigen Weg und vergleicht nur. Alle brauchen den Worker; Voraussetzungen und Reihenfolge beim Umschalten beschreibt `DEPLOYMENT.md` im Repository.

| Variable | Werte | Bedeutung |
|----------|-------|-----------|
| `SEARCH_INDEX_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | Suchindex aus den Ereignissen; `schatten` pflegt einen Schattenindex neben dem Live-Index |
| `SEARCH_INDEX_SHADOW_BODIES` | Kennungen, kommagetrennt | Schattenbetrieb nur für diese Kommunen; leer = alle |
| `SEARCH_INDEX_SHADOW_MAX_DOCS` | Zahl, Standard `100000` | ungefähre Obergrenze der Dokumente in allen Schattenindizes; `0` = keine |
| `WORK_NOTIFICATION_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | Benachrichtigungen in Work über Ereignisse; `schatten` und `aktiv` brauchen `TASKS_BACKEND=journal` |
| `GEOREF_SUBSCRIPTION`, `SUMMARY_SUBSCRIPTION` | `aus`, `schatten`, `aktiv` | neuer Text eines Dokuments stößt die Verortung seines Vorgangs an bzw. verwirft dessen KI-Zusammenfassung |
| `URHEBER_SUBSCRIPTION` | `aus`, `schatten`, `aktiv`; Standard `aktiv` | neue oder geänderte Vorlagen und neuer Text ihrer Anlagen stoßen die Ermittlung der antragstellenden Fraktionen an (Bürgerportal und OParl `originatorOrganization`); schreibt nur eigene, abgeleitete Tabellen |
| `RIS_SESSION_PROJECTOR` | `aus`, `schatten` | RIS-Bestand der Session-Mandanten aus deren Ereignissen, vorerst als unsichtbare Schatten-Quelle |
| `RIS_SESSION_PROJECTOR_TENANTS` | Kennungen, kommagetrennt | nur diese Session-Mandanten; leer = alle |
| `WORK_RIS_RELINK` | `aus`, `probe`, `aktiv` | Notizen, Positionen und Kommentare in Work folgen ihrem Tagesordnungspunkt bzw. ihrer Vorlage, wenn ein RIS seinen Stand neu veröffentlicht; `probe` meldet nur im Protokoll |
| `WORK_RIS_RELINK_INTERVAL_MINUTES` | Zahl, Standard `15` | Abstand des Abgleichs in Minuten |

`docker-compose.yml` reicht alle durch außer `URHEBER_SUBSCRIPTION`.

## Texterkennung

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `TEXT_EXTRACTION_RUNNER` | `ingestor` | Wer den Text der RIS-Dateien erkennt: `ingestor` (der Ingestor lädt und erkennt selbst) oder `worker` (Aufträge der Anwendung, die nur aus Ablage und Objektspeicher lesen, in zwei Stufen: die Textebene in der Warteschlange `text` im Dienst `worker`, die Erkennung aus dem Bild nur für Dateien ohne ausreichende Textebene in `ocr` im Dienst `worker-heavy`). `worker` braucht `TASKS_BACKEND=journal`, sonst startet die Anwendung nicht. In Anwendung und Ingestor gleich setzen. |
| `TEXT_EXTRACTION_ENABLED` | `True` | Nur im Ingestor: Volltext aus Dokumenten extrahieren |
| `TEXT_EXTRACTION_MAX_SIZE_MB` | `50` | Größere Dateien werden nicht verarbeitet |
| `TEXT_EXTRACTION_QUEUE_DEPTH` | `20` | Nur mit `worker`: höchstens so viele Aufträge der Erkennung aus dem Bild (`ocr`) warten oder laufen zugleich |
| `TEXT_LAYER_QUEUE_DEPTH` | `300` | Nur mit `worker`: höchstens so viele Aufträge der ersten Stufe (`text`) warten oder laufen zugleich. Die Tiefe bestimmt den Durchsatz, denn der Zeitplan füllt nur alle zwei Minuten nach. |
| `TEXT_LAYER_MEMORY_LIMIT_MB` | `512` | Adressraum je Prozess, der die Textebene liest, in MB, `0` = ohne Grenze; darüber geht die Datei an die Erkennung aus dem Bild. Im Ingestor gilt ein eigener Wert, siehe [Ingestor](#ingestor). |
| `TEXT_EXTRACTION_OCR_MIXED_PAGES` | `true` | Eingescannte Seiten eines sonst getippten PDFs erkennen (Seite mit Bild und kaum Text); `false` = jeder Text in der Textebene reicht |
| `TEXT_EXTRACTION_STALE_MINUTES`, `TEXT_EXTRACTION_MAX_ATTEMPTS` | `60`, `3` | Eine Datei, die länger in Bearbeitung ist, gilt als abgebrochen; nach so vielen Abbrüchen als gescheitert |
| `TEXT_EXTRACTION_GIVE_UP_ALERT` | `5` | Die Prüfung „texterkennung“ wird erst ab so vielen aufgegebenen Dateien in 24 Stunden rot |
| `TEXT_EXTRACTION_BACKLOG_ALERT_HOURS` | `24` | Nur mit `worker`: Die Prüfung „dokumenttext“ wird rot, wenn ein abgelegtes Dokument länger auf seinen Text wartet |
| `OCR_DPI`, `OCR_MAX_MEGAPIXELS` | `200`, `8` | Auflösung der Texterkennung, je Seite gedeckelt |
| `OCR_MEMORY_LIMIT_MB` | `1024` | Adressraum je Tesseract-Prozess. `docker-compose.yml` setzt `512` für Anwendung und Worker und `384` für den Ingestor, `worker-heavy` hat `WORKER_HEAVY_OCR_MEMORY_LIMIT_MB`. |
| `OCR_PAGE_TIMEOUT`, `OCR_FILE_BUDGET_SECONDS`, `OCR_MAX_PAGES` | `120`, `1200`, `100` | Zeitgrenze je Seite, Zeitbudget und Seitenzahl je Datei; danach gilt der bis dahin erkannte Text |
| `MISTRAL_API_KEY`, `MISTRAL_BASE_URL` | leer | Optionale externe Texterkennung für öffentliche RIS-Dateien. Wirkt nur mit Schlüssel **und** einer Basis-URL, deren Host in `KI_ERLAUBTE_HOSTS` steht. |
| `MISTRAL_OCR_MODEL` | `pixtral-12b-2409` | Modell des externen Dienstes |
| `MISTRAL_OCR_RATE_LIMIT` | `60` | Anfragen pro Minute an den externen Dienst |

Die Erkennung liest zuerst die Textebene des PDFs, dann, falls eingerichtet, den externen Dienst, sonst und als Rückfall die lokale Texterkennung mit Tesseract. `docker-compose.yml` reicht `TEXT_EXTRACTION_RUNNER`, `TEXT_EXTRACTION_QUEUE_DEPTH`, `TEXT_LAYER_QUEUE_DEPTH`, `TEXT_LAYER_MEMORY_LIMIT_MB`, `TEXT_EXTRACTION_OCR_MIXED_PAGES`, `OCR_MEMORY_LIMIT_MB`, `MISTRAL_API_KEY` und `MISTRAL_BASE_URL` an Anwendung und Worker durch, die übrigen nicht. Umstellen auf `worker`: Ablauf „Dokumentkette einschalten“ in `DEPLOYMENT.md` im Repository.

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
| `RIS_REQUEST_INTERVAL` | `1.0` | Abstand je Server in Sekunden für alle Abrufe der Anwendung (gemeinsamer Takt über Redis); `0` schaltet die Drossel ab, nur für Tests und Notfälle |
| `INSIGHT_SOURCE_BACKOFF_FAILURES` | `3` | Ab so vielen fehlgeschlagenen Läufen des Abgleichs in Folge ruhen Dokument-Cache, Vorschau, Löschabgleich und Personenfotos für die Quelle |

`OPARL_FILES_ROOT` setzt `docker-compose.yml` fest auf `/app/files`, `FILE_CACHE_MIN_FREE_GB` reicht es durch. `FILE_CACHE_MAX_MB`, `FILE_PROXY_TIMEOUT_SECONDS`, `RIS_REQUEST_INTERVAL` und `INSIGHT_SOURCE_BACKOFF_FAILURES` reicht es nicht durch; tragen Sie sie unter Docker Compose in einer `docker-compose.override.yml` ein (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)), im Helm-Chart in `app.extraEnv`. Ein Eintrag nur in der `.env` wirkt nicht.

Details unter [Dokument-Cache](dokument-cache.md).

## Dokumentablage und Objektspeicher

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `FILE_STORE_LAYOUT` | `sha256` | Ablage nach SHA-256 mit Referenzzählung; `kommune` behält das ältere Verzeichnis je Kommune, ohne Deduplizierung und ohne Objektspeicher |
| `FILE_STORE_SHARED` | `true` | Sieht dieser Dienst die gemeinsame Ablage? `false` nur auf einem eigenen Server für die Texterkennung, der die Inhalte allein über den Objektspeicher sieht: Was weder in der lokalen Ablage noch im Objektspeicher liegt, gilt dann als gestört statt als fehlend und löst keinen Abruf bei der Quelle aus. |
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
| `OBJ_EVICT_MAX_MISSING` | `20` | Bremse: Verdrängen und Zurückholen brechen ab, wenn so viele Inhalte in Folge im Objektspeicher fehlen (etwa ein falscher Bucket); `0` = ohne Grenze |
| `OBJ_CHECKSUMS` | `when_required` | Prüfsummen beim Hochladen: `when_required` (verträglich mit S3-kompatiblen Anbietern) oder `when_supported` |
| `OBJ_ADDRESSING_STYLE`, `OBJ_TIMEOUT_SECONDS`, `OBJ_FETCH_TOTAL_SECONDS` | `auto`, `30`, `60` | Adressierung, Zeitgrenze je Anfrage und Gesamtdauer eines Abrufs aus dem Objektspeicher |

`docker-compose.yml` reicht `FILE_STORE_LAYOUT`, `FILE_STORE_SHARED`, `INGESTOR_STORES_FILES`, `FILE_CACHE_MAX_TOTAL_GB`, `FILE_CACHE_EVICT_TARGET_PERCENT`, `FILE_ACCEL_REDIRECT`, `INSIGHT_FETCH_ALLOW_PRIVATE_NETWORKS` sowie `OBJ_ENABLED`, `OBJ_ENDPOINT`, `OBJ_BUCKET`, `OBJ_KEY`, `OBJ_SECRET`, `OBJ_REGION`, `OBJ_CACHE_MAX_GB`, `OBJ_EVICT_MAX_MISSING` und `OBJ_CHECKSUMS` durch, die übrigen nicht. Die Zugangsdaten des Objektspeichers können auch in einer eigenen Umgebungsdatei liegen: `docker compose --env-file .env --env-file <datei> up -d`.

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
| `DJANGO_LOG_LEVEL` | `INFO` | Protokollstufe der Meldungen von Django selbst; `LOG_LEVEL` gilt für die Anwendung |

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
| `SECURITY_AUDIT_ARCHIVE_RETENTION_DAYS` | `0` | Aufbewahrung der Archivpakete des Sicherheitsprotokolls in Tagen ab Ablage; `0` = keine Löschung |
| `LOGIN_ATTEMPT_RETENTION_DAYS` | `30` | Aufbewahrung der Anmeldeversuche, mit denen die Anmeldung gedrosselt wird, in Tagen; `0` = keine Löschung. Es löscht der tägliche Zeitplan `befehl:purge_login_attempts`. |
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
| `INGESTOR_INTERVAL` | `10` (`.env.example`, `install.sh` und Helm: `15`) | Grundtakt je Quelle werktags 7–19 Uhr in Minuten; sonst stündlich, am Wochenende alle 2 Stunden, an Sitzungstagen und am Vortag (7–22 Uhr) alle 5 Minuten, nach Abgleichen ohne Änderung seltener; je Quelle einstellbar (siehe [Takt und Vollabgleich je Quelle](quellen-anbinden.md#takt-und-vollabgleich-je-quelle)) |
| `INGESTOR_FULL_SYNC_HOUR` | `3` | Beginn des nächtlichen Standardfensters für Vollabgleiche (5 Stunden, Ortszeit) für Quellen ohne eigenes Zeitfenster; Werte außerhalb von 0 bis 23 schalten geplante Vollabgleiche ab, auch in eigenen Zeitfenstern der Quellen; im Admin angeforderte bleiben möglich |
| `INGESTOR_CONCURRENT` | `10` | Abrufplätze je Quelle; je Server gilt trotzdem `INGESTOR_HOST_MAX_CONCURRENT` |
| `INGESTOR_SYNC_POOL_SIZE` | `4` | Quellen, die der Ingestor gleichzeitig abgleicht, je Quelle höchstens ein Lauf; Vollabgleiche belegen höchstens alle Plätze bis auf einen |
| `INGESTOR_MEM_LIMIT` | `512m` | Speichergrenze des Ingestor-Containers (nur Docker Compose) |
| `INGESTOR_REQUEST_INTERVAL` | `1.0` | Abstand je Server in Sekunden (gemeinsamer Takt über Redis); `0` schaltet die Drossel ab, nur für Tests und Notfälle |
| `INGESTOR_HOST_MAX_CONCURRENT` | `2` | Offene Anfragen je Server und Prozess; `0` = ohne Grenze |
| `INGESTOR_USER_AGENT` (älter: `SCRAPER_USER_AGENT`) | `mandari-ingestor/<Version> (+https://mandari.de/ingestor/; support@mandari.de)` | User-Agent des Ingestors (Abgleich, Scraper, Texterkennung, Sondierung) |
| `SCRAPER_TOMBSTONE_FULL_CRAWLS` | `3` | Nach so vielen Voll-Crawls ohne Sichtung gilt ein Objekt als gelöscht |
| `SCRAPER_PARSE_QUOTA_WARN` | `0.8` | Warnung, wenn weniger als dieser Anteil der Seiten geparst werden konnte |
| `INGESTOR_MODIFIED_SINCE_MARGIN_MINUTES` | `120` | Sicherheitsabstand des Änderungsfensters in Minuten: Ein Änderungsabgleich fragt ab dem Beginn des letzten vollständig erfolgreichen Abgleichs abzüglich dieses Abstands; je Quelle abweichend über `sync_config` |
| `OPARL_REQUEST_TIMEOUT`, `OPARL_MAX_RETRIES` | `60`, `3` | Zeitgrenze einer Anfrage in Sekunden und Wiederholungen bei Fehlern. Die gleichnamigen Einstellungen der Anwendung (Standard `300` und `5`) werden dort derzeit nicht verwendet. |
| `INGESTOR_TEXT_LAYER_MEMORY_LIMIT_MB`, `INGESTOR_TEXT_LAYER_TIMEOUT`, `INGESTOR_TEXT_LAYER_CONCURRENCY` | `384`, `120`, `2` | Nur Docker Compose, im Ingestor `TEXT_LAYER_MEMORY_LIMIT_MB`, `TEXT_LAYER_TIMEOUT` und `TEXT_LAYER_CONCURRENCY`: Die Textebene eines PDFs liest ein eigener Prozess mit Grenze des Adressraums in MB (`0` = ohne) und Zeitgrenze in Sekunden, höchstens so viele zugleich. Anzahl mal Grenze plus rund 200 MB unter `INGESTOR_MEM_LIMIT` halten. |

`INGESTOR_INTERVAL`, `INGESTOR_FULL_SYNC_HOUR`, `INGESTOR_CONCURRENT`, `INGESTOR_SYNC_POOL_SIZE`, `INGESTOR_MEM_LIMIT` und `INGESTOR_TEXT_LAYER_*` liest `docker-compose.yml` aus der `.env`; im Helm-Chart heißen die ersten drei `ingestor.syncInterval`, `ingestor.fullSyncHour` und `ingestor.concurrent`, `INGESTOR_SYNC_POOL_SIZE` gehört dort in `ingestor.extraEnv`. Die übrigen Variablen der Tabelle reicht es nicht durch: Tragen Sie sie unter Docker Compose in einer `docker-compose.override.yml` beim Dienst `ingestor` ein (siehe [Eigene Variablen unter Docker Compose](#eigene-variablen)), im Helm-Chart in `ingestor.extraEnv`; ein Eintrag nur in der `.env` wirkt nicht. Abgeglichen wird nur im Ingestor: Die Sync-Aktionen im Admin gehen an den laufenden Ingestor, ohne ihn meldet der Admin einen Fehler. `INGESTOR_USER_AGENT`, `INGESTOR_REQUEST_INTERVAL` und `INGESTOR_HOST_MAX_CONCURRENT` gehören deshalb nur in die Umgebung des Ingestors. Die Abrufe der Anwendung selbst (Dokument-Cache, Vorschau, Löschabgleich, Personenfotos) melden sich mit der festen Kennung `mandari-ingestor (+https://mandari.de/ingestor/; support@mandari.de)`; ihren Abstand je Server stellt `RIS_REQUEST_INTERVAL` ein.

Weitere Feineinstellungen des Ingestors, etwa Parallelität, Wiederholungen und Schutzschalter, stehen mit ihren Standardwerten in `ingestor/src/config.py` im Repository. Ihre Namen sind die Feldnamen in Großbuchstaben.

Details unter [Quellen anbinden](quellen-anbinden.md), Regeln für den Abruf unter [Ingestor und Opt-out](../datenschutz/ingestor.md).
