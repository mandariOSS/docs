---
title: Quellen anbinden
description: Kommunen an mandari anbinden. Echte OParl-Schnittstellen, SessionNet-Portale über den Scraper-Adapter und ALLRIS über die externe oparl-bridge, Schritt für Schritt.
---

# Quellen anbinden

mandari liest kommunale Ratsinformationen aus drei Arten von Quellen. Alle landen in derselben Pipeline: Verarbeitung, Speicherung, Texterkennung, Suche, Tombstones.

| Art | `source_type` | Beschreibung |
|-----|---------------|--------------|
| **OParl-Schnittstelle** | `oparl` (Standard) | Das Ratsinformationssystem der Kommune bietet selbst OParl an. Der einfachste Fall. |
| **Scraper-Adapter** | `scraper:sessionnet` | Für Systeme ohne OParl, aktuell **SessionNet**. Der Adapter im Ingestor erzeugt aus den HTML-Seiten OParl-1.1-JSON. |
| **Externe Bridge** | `bridge:allris` | Für **ALLRIS**: Ein eigener Container übersetzt in OParl, mandari konsumiert dessen Ausgabe als normale Quelle. |

Die Art steht in der Sync-Konfiguration der Quelle (`sync_config["source_type"]`). Im Admin unter *OParl-Quellen* sind Art, Parse-Quote und robots.txt-Status je Quelle sichtbar, der Filter „Quellen-Art“ trennt die drei.

## OParl-Schnittstelle anbinden

1. System-Endpunkt der Kommune ermitteln, zum Beispiel `https://ratsinfo.example.org/oparl/v1/system`. Ein Blick in die JSON-Antwort zeigt Name und Body-Liste.
2. Admin → *Insight → OParl-Quellen → Hinzufügen*: Name und URL des System-Endpunkts eintragen, aktiv setzen.
3. Eine aktive Quelle ohne bisherigen Abgleich ist sofort fällig; der Ingestor beginnt, sobald ein Platz frei ist. Danach gleicht er sie in ihrem Takt ab (werktags tagsüber alle 10 Minuten, sonst seltener) und vollständig nachts im Zeitfenster, siehe [Crawler und Opt-out](../datenschutz/crawler.md#abgleich). Alternativ die Admin-Aktion „Vollständiger Sync“ auslösen; ohne eigenes Zeitfenster der Quelle beginnt der Vollabgleich dann sofort, auch tagsüber, in Zeitscheiben nur im Standardfenster (siehe [Takt und Vollabgleich je Quelle](#takt-und-vollabgleich-je-quelle)). Das Werkzeug `manage.py add_oparl_source` legt eine Quelle dagegen inaktiv an; sie wird erst nach dem Aktivieren im Admin abgeglichen.
4. Fortschritt im [Betriebsmonitor](monitoring.md) verfolgen. Beim Onboarding wächst die OCR-Warteschlange sprunghaft, daher Kommunen einzeln aufschalten.

## SessionNet-Kommune anbinden

SessionNet-Bürgerinfo-Portale sind Standard-Templates. Der Adapter unterstützt die klassische `.asp`-Variante und die neuere `.php`-Variante mit identischem Markup.

### Schritt 1: Basis-URL ermitteln

Die Basis-URL ist das Verzeichnis, in dem die SessionNet-Seiten liegen, erkennbar an Seiten wie `si0040.asp` (Sitzungskalender), `vo0050.asp` (Vorlage) und `gr0040.asp` (Gremien). Typische Formen:

- `https://buergerinfo.example.org/` (direkt im Root, `.asp`)
- `https://rat.example.org/bi/` (Unterverzeichnis, `.php`)
- `https://sessionnet.hoster.example/kommune/bi/` (Hoster mit Mandantenpfad)

Kurz prüfen: `<basis-url>si0040.asp` (oder `.php`) muss den Sitzungskalender liefern und der Seitentitel mit „SessionNet“ beginnen.

### Schritt 2: robots.txt prüfen

Der Ingestor prüft die robots.txt vor jeder Anfrage, auch vor jeder Weiterleitung. Sperrt sie die Basis-URL, wird die Quelle nicht gecrawlt; sperrt sie eine Seite unterwegs, bricht der Crawl ab. In beiden Fällen ruht die Quelle mindestens 24 Stunden, bei einer nicht erreichbaren robots.txt mindestens 30 Minuten. Der Status wird im Admin angezeigt. Die Regeln im Einzelnen stehen unter [Crawler und Opt-out](../datenschutz/crawler.md#robotstxt). Vorab manuell nachsehen schadet nicht: `https://<host>/robots.txt`.

### Schritt 3: Quelle anlegen

Admin → *Insight → OParl-Quellen → Hinzufügen*:

- **Name**: zum Beispiel „Stadt Musterstadt (SessionNet)“
- **URL**: die Basis-URL, sie dient als eindeutiger Schlüssel
- **Sync config**:

```json
{
  "source_type": "scraper:sessionnet",
  "scraper": {
    "base_url": "https://rat.example.org/bi/",
    "body_name": "Stadt Musterstadt",
    "variant": "php",
    "rate_limit_seconds": 2.0,
    "calendar_window_days": [-60, 210],
    "full_window_days": [-365, 210]
  }
}
```

Alle Schlüssel unter `scraper` außer `base_url` sind optional:

| Schlüssel | Standard | Bedeutung |
|-----------|----------|-----------|
| `body_name` | „Unbekannte Kommune“ | Anzeigename der Kommune |
| `variant` | automatisch | `"asp"` oder `"php"` |
| `rate_limit_seconds` | `2.0` | Mindestabstand zwischen Anfragen je Host in Sekunden; kleinere Werte als `1.0` gelten als `1.0` |
| `max_concurrent` | `1` | immer 1, Anfragen laufen nacheinander |
| `calendar_window_days` | `[-60, 210]` | Kalenderfenster inkrementeller Läufe |
| `full_window_days` | `[-365, 210]` | Fenster des Voll-Crawls (Historie) |
| `max_detail_pages` | unbegrenzt | Obergrenze Detailseiten je Lauf, für Probe-Crawls |
| `members_on_full_only` | `true` | Gremienmitglieder nur im Voll-Crawl laden |

### Schritt 4: Probe-Crawl mit Limit

Beim Onboarding zunächst mit strengem Limit fahren (`"max_detail_pages": 20`), das Ergebnis im Admin prüfen (Parse-Quote, gespeicherte Objekte) und Stichproben gegen die Live-Seiten vergleichen. Danach das Limit entfernen und einen Voll-Sync auslösen.

### Was der Adapter extrahiert

| SessionNet-Seite | OParl-Objekt |
|------------------|--------------|
| Basis-URL | Body |
| Sitzungsdetail (`si0057`) | Meeting mit Tagesordnungspunkten, öffentlich und nicht-öffentlich gekennzeichnet, mit Beschlüssen |
| Sitzungsdokumente (`si0050`) | Einladung, Niederschrift als File |
| Vorlage (`vo0050`) | Paper mit Betreff, Nummer, Art und Anlagen |
| Gremienliste (`gr0040`) | Organizations |
| Gremiendetail (`kp0040`) | Persons und Memberships inklusive Stimmrecht |
| Punkt ↔ Vorlage | Consultation |

Anlagen laufen automatisch durch die Texterkennung und werden in der Suche indexiert.

### Änderungserkennung und Löschungen

- **Listen-Diffing**: Je Kalendermonat wird ein Hash der Sitzungsliste gehalten, unveränderte Monate überspringt der inkrementelle Lauf.
- **Inhalts-Hash je Objekt**: Aktualisiert wird nur bei tatsächlicher Änderung. `modified` ist die Crawl-Zeit des letzten echten Updates, damit bleibt die eigene OParl-Ausgabe inkrementell konsumierbar.
- **Verschwinden ist nicht Löschen**: Objekte, die in drei aufeinanderfolgenden Voll-Crawls nicht mehr gesehen wurden (`SCRAPER_TOMBSTONE_FULL_CRAWLS`), werden als gelöscht markiert, nie physisch gelöscht. Taucht ein Objekt wieder auf, wird die Markierung automatisch aufgehoben.

### Überwachung

Fällt die Parse-Quote eines Laufs unter 80 Prozent (`SCRAPER_PARSE_QUOTA_WARN`), wird gewarnt und der Lauf als fehlerhaft protokolliert. Das ist das typische Symptom eines Frontend-Redesigns der Instanz. Für Prometheus stehen Zähler für geladene Seiten, Parse-Fehler je Seitentyp und die Parse-Quote je Quelle bereit.

## ALLRIS über oparl-bridge anbinden

ALLRIS rendert sein Frontend per Ajax, klassisches HTML-Scraping reicht dort nicht. Das externe Open-Source-Projekt [oparl-bridge](https://github.com/Aeroid/oparl-bridge) (MIT-Lizenz) liest eine ALLRIS-Instanz aus und publiziert die Daten als OParl-1.1-API. mandari konsumiert diese API als normale OParl-Quelle.

Empfohlen ist eine gepinnte Version der Bridge. Kein offizielles Docker-Image, daher ein eigenes Dockerfile. Beispieldateien:

- [`oparl-bridge.Dockerfile`](oparl-bridge.Dockerfile)
- [`docker-compose.oparl-bridge.yml`](docker-compose.oparl-bridge.yml)

```bash
# Image einmalig aus der gepinnten Upstream-Version bauen
docker build -f oparl-bridge.Dockerfile \
  -t mandari/oparl-bridge:v0.2.0 \
  https://github.com/Aeroid/oparl-bridge.git#v0.2.0
```

```yaml
# Auszug: ein Bridge-Container je ALLRIS-Kommune
services:
  oparl-bridge-musterstadt:
    image: mandari/oparl-bridge:v0.2.0
    environment:
      OPARL_ALLRIS_BASE_URL: "https://ratsinfo.musterstadt.example/allris"
      OPARL_API_BASE_URL: "https://oparl-musterstadt.intern.example"
      OPARL_BODY_NAME: "Stadt Musterstadt"
      OPARL_SCRAPER_DELAY_MS: "2000"
    volumes:
      - oparl_bridge_musterstadt:/data
    restart: unless-stopped
```

### Anbindung in mandari

1. Bridge-Container starten, den initialen Sync abwarten (je nach Kommune 10 bis 40 Minuten) und die OParl-Ausgabe prüfen: `curl https://<bridge-host>/` liefert das System-Objekt.
2. Quelle im Admin anlegen mit der URL des Bridge-System-Endpunkts und der Sync-Konfiguration `{"source_type": "bridge:allris"}`.
3. Sync auslösen. Die Bridge liefert Listen ohne Pagination und ohne `modified_since`-Filter. Das ist unkritisch, der Ingestor vergleicht Objekte clientseitig.

Ein Bridge-Container bedient genau eine ALLRIS-Instanz. PDFs werden von der Bridge bei Bedarf durchgereicht, nicht gespeichert.

## Takt und Vollabgleich je Quelle

Der Ingestor gleicht jede Quelle in ihrem eigenen Takt ab: werktags 7–19 Uhr im Grundtakt (`INGESTOR_INTERVAL`), sonst stündlich, am Wochenende alle 2 Stunden, an Sitzungstagen und am Vortag (7–22 Uhr) alle 5 Minuten, nach Abgleichen ohne Änderung seltener. Den Vollabgleich startet er höchstens einmal je Nacht im Zeitfenster der Quelle. Die Regeln im Einzelnen stehen unter [Crawler und Opt-out](../datenschutz/crawler.md#wann-wir-abrufen).

Abweichungen für eine Quelle stehen in ihrer Sync-Konfiguration. Ungültige Werte gelten als nicht gesetzt.

| Schlüssel | Wirkung | Beispiel |
|-----------|---------|----------|
| `request_interval` | Abstand der Abrufe dieser Quelle in Sekunden, 1 bis 30; nur langsamer als der Standard, kleinere Werte gelten als 1 | `2.0` |
| `sync_schedule` | Takt der Quelle: `workday_minutes`, `off_hours_minutes`, `weekend_minutes`, `meeting_minutes`, `idle_max_minutes`, `meeting_idle_max_minutes` (ganze Minuten von 5 bis 1440), `workday_hours`, `meeting_hours` (etwa `{"start": "07:00", "end": "19:00"}`, Beginn vor Ende am selben Tag), `meeting_days_before` (0 bis 7), `idle_runs` (0 bis 100, 0 = nie verlängern), `tz` | `{"weekend_minutes": 240}` |
| `full_sync_window` | eigenes Zeitfenster des Vollabgleichs in Ortszeit (`Europe/Berlin`, abweichend mit `tz`), auch über Mitternacht; außerhalb läuft nur der Änderungsabgleich | `{"start": "00:00", "end": "06:00"}` |
| `full_sync_every_days` | Mindestabstand zwischen vollständigen Vollabgleichen in Tagen, 1 bis 365 | `7` |
| `full_sync_slices` | Vollabgleich nur in Zeitscheiben mit `modified_since` und `modified_until`, für Server, deren vollständige Listen abbrechen: `since` (Pflicht), `days` (1 bis 366, Standard 30), optional `lists` | `{"days": 30, "since": "2010-01-01"}` |

- **Zeitscheiben** gibt es nur für OParl-Schnittstellen, die nach Änderungsdatum filtern (`modified_since` und `modified_until`). Ein Vollabgleich in Zeitscheiben endet immer mit dem Zeitfenster und setzt im nächsten an der letzten vollständigen Scheibe fort; außerhalb des Fensters und ohne bekanntes Fenster (Kommandozeile, Worker ohne eigenes `full_sync_window`) läuft ein Änderungsabgleich. Geben Sie solchen Quellen deshalb ein eigenes `full_sync_window`.
- **Langsame Listen** setzt der Ingestor selbst aus: Läuft eine optionale Liste in eine Zeitüberschreitung oder HTTP 504, ruht sie 1 Stunde, danach jeweils doppelt so lange, höchstens 24 Stunden (`sync_config["slow_lists"]`).
- **Geplante Vollabgleiche abschalten:** `INGESTOR_FULL_SYNC_HOUR` außerhalb von 0 bis 23 schaltet sie für alle Quellen ab, auch in eigenen Zeitfenstern; im Admin angeforderte bleiben möglich.

Alle Schlüssel samt der Werte, die der Ingestor selbst pflegt (`sync_state`, `full_sync_progress`, `slow_lists` und weitere), stehen in den [Abrufregeln](https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md#einstellungen-je-quelle).

### Abgleich anstoßen und prüfen

- **Aktionen im Admin:** „Inkrementeller Sync“ und „Vollständiger Sync“ an einer Quelle gehen an den Ingestor, solange er läuft. Der Abgleich beginnt, sobald ein Platz frei ist; eine Quelle in Schonung bleibt in Ruhe. Ohne laufenden Ingestor, für abgeschaltete Quellen und wenn die Nachricht keinen Empfänger findet, laufen die Aktionen im Worker der Anwendung, mit robots.txt, Takt je Server und eigenem Zeitfenster der Quelle, aber ohne Schonung.
- **Jetzt synchronisieren** auf der Startseite des Admins stößt alle aktiven Quellen an. Ohne laufenden Ingestor meldet der Admin einen Fehler.
- **Läuft der Ingestor?** Er schreibt bei jeder Prüfung, mindestens alle 30 Sekunden, ein Lebenszeichen in Redis (`mandari:ingestor:heartbeat`, 180 Sekunden gültig). Fehlt es, etwa weil Redis nicht erreichbar ist, gilt er als laufend, wenn in den letzten 30 Minuten ein Sync-Protokoll begonnen hat.
- **Kommandozeile** (im Container `ingestor`): `python -m src.main sync --all` gleicht alle aktiven Quellen einmal ab, höchstens zwei zugleich, mit Schonung, aber ohne den Takt je Quelle; der Takt je Server gilt. `sync --source` und `sync --body` gleichen eine Quelle ab, auch eine abgeschaltete, ohne Schonung.
- **Sync-Protokoll:** Jeder Lauf des Ingestor-Daemons schreibt eines für seine Quelle, mit den Zählern, höchstens 20 Fehlern, der Zahl der Abrufe (`details.requests`) und dem Takt (`details.takt`: Art, Abstand, Läufe ohne Änderung, nächster Lauf), dazu gegebenenfalls ausgesetzte Listen (`details.suspended_lists`) und den Stand der Zeitscheiben (`details.full_sync_slices`).
- **Älterer Sync-Daemon:** `manage.py sync_daemon` der Anwendung gleicht alle aktiven Quellen gemeinsam in festem Abstand ab, ohne Takt je Quelle. Docker Compose und das Helm-Chart starten ihn nicht; verwenden Sie den Daemon des Ingestors.

## Rücksicht auf die Quellen

Für alle Quellen gelten die gleichen Regeln: begrenzte Anfragerate, Respekt vor robots.txt, ehrlicher User-Agent, keine Umgehung von Logins oder Captchas, automatische Schonung bei Störungen. Wie Kommunen Drosselung oder Entfernung verlangen können, steht unter [Crawler und Opt-out](../datenschutz/crawler.md).
