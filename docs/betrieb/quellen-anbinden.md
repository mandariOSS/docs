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
3. Der Ingestor synchronisiert im nächsten Zyklus (Standard alle 15 Minuten, Voll-Sync nachts). Alternativ die Admin-Aktion „Vollständiger Sync“ auslösen.
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

Der Ingestor prüft robots.txt automatisch vor jedem Crawl und überspringt die Quelle bei einem Disallow. Der Status wird im Admin angezeigt. Vorab manuell nachsehen schadet nicht: `https://<host>/robots.txt`.

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
| `rate_limit_seconds` | `2.0` | Mindestabstand zwischen Anfragen je Host |
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

## Rücksicht auf die Quellen

Für alle Quellen gelten die gleichen Regeln: begrenzte Anfragerate, Respekt vor robots.txt, ehrlicher User-Agent, keine Umgehung von Logins oder Captchas, automatische Schonung bei Störungen. Wie Kommunen Drosselung oder Entfernung verlangen können, steht unter [Crawler und Opt-out](../datenschutz/crawler.md).
