---
title: Öffentliche Fraktions-API
description: Referenz der öffentlichen Fraktions-API v1 von mandari Work. Endpunkte, Konfiguration, Beispiele, Sicherheit und Datenschutz.
---

# Öffentliche Fraktions-API v1

Read-only-JSON-API, mit der Fraktionen die **öffentlichen** Termine und Tagesordnungen ihrer Fraktionssitzungen automatisch auf der eigenen Webseite anzeigen. Eine fertige Anleitung zum Einbau steht unter [Termine auf der eigenen Webseite](termine-einbinden.md).

## Grundprinzipien

- **Opt-in je Organisation**: Die API ist standardmäßig deaktiviert und wird bewusst eingeschaltet unter **Work-Portal → Organisation → Reiter „API“**.
- **Opakes Token statt Organisations-Slug**: Der Zugriff läuft über ein zufälliges Token in der URL. Organisationen sind dadurch nicht aufzählbar. Das Token kann jederzeit erneuert werden, bisherige URLs werden dann sofort ungültig.
- **Strikt öffentliche Inhalte**: Ausgeliefert werden ausschließlich öffentliche, angenommene Tagesordnungspunkte (Nummer, Titel) und Sitzungs-Metadaten (Datum, Ort, Status). Niemals enthalten: nicht-öffentliche Punkte (auch nicht als Platzhalter), Protokollinhalte, Beschlüsse, Teilnehmerdaten, Video-Links oder Sitzungsentwürfe.
- **Read-only**: nur `GET`, dazu `OPTIONS` für CORS-Preflight.
- **CORS**: Standardmäßig `Access-Control-Allow-Origin: *`. Optional schränkt die Organisation die erlaubten Origins auf konkrete Webseiten ein, dann wird nur ein gelisteter Origin gespiegelt.
- **Caching**: `Cache-Control: public, max-age=<konfigurierbar>`, Standard 300 Sekunden, Schema 1 Stunde. Bitte clientseitig nicht häufiger als nötig abrufen.
- **Versionierung**: Alle Pfade liegen stabil unter `/api/public/v1/`. Inkompatible Änderungen erscheinen nur unter einer neuen Version.

## Konfiguration im API-Reiter

| Einstellung | Standard | Bedeutung |
|-------------|----------|-----------|
| Zeitfenster vergangene Sitzungen | 90 Tage | Wie weit zurück Sitzungen ausgeliefert werden |
| Zeitfenster kommende Sitzungen | 365 Tage | Wie weit voraus |
| Sitzungsort ausliefern | an | einzeln abschaltbar |
| Tagesordnung ausliefern | an | einzeln abschaltbar |
| Erlaubte Origins | alle | Kommagetrennte Liste von Webseiten-Domains |
| Cache-Dauer | 300 s | Wert des `max-age` |

Der Reiter zeigt außerdem eine Nutzungsstatistik (Abrufe gesamt, letzter Abruf, keine IP-Adressen) und ein fertiges Einbindungs-Snippet zum Kopieren.

## Endpunkte

Basis: `https://mandari.de/api/public/v1`

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/openapi.json` | OpenAPI-3.0-Schema, ohne Token abrufbar |
| GET | `/fraktionen/<token>/` | Zugangs-Info und Endpunkt-Übersicht |
| GET | `/fraktionen/<token>/sitzungen/` | Terminliste: kommende und vergangene Sitzungen im konfigurierten Zeitfenster |
| GET | `/fraktionen/<token>/sitzungen/<id>/` | Sitzungsdetail mit öffentlicher Tagesordnung |

Unbekannte, deaktivierte oder inaktive Zugänge liefern einheitlich **404** mit `{"error": "not_found"}`. Die API verrät nicht, ob ein Token existiert.

## Beispiel

```bash
curl https://mandari.de/api/public/v1/fraktionen/<token>/sitzungen/
```

```json
{
  "api_version": "1.0",
  "organization": {"name": "Fraktion Beispiel"},
  "count": 2,
  "meetings": [
    {
      "id": "6f0c…",
      "title": "Fraktionssitzung März",
      "number": 12,
      "start": "2026-03-02T18:00:00+01:00",
      "end": null,
      "location": "Fraktionsbüro",
      "is_virtual": false,
      "status": "invited",
      "cancelled": false
    }
  ]
}
```

Das Sitzungsdetail (`…/sitzungen/<id>/`) ergänzt das Feld `agenda`:

```json
{
  "agenda": [
    {"number": "1", "title": "Tagesordnung festlegen und letztes Protokoll genehmigen"},
    {"number": "2", "title": "Spielplatz Musterstraße"}
  ]
}
```

## Minimalbeispiel für die Einbindung

```html
<ul id="sitzungen"></ul>
<script>
fetch("https://mandari.de/api/public/v1/fraktionen/<token>/sitzungen/")
  .then((r) => r.json())
  .then((data) => {
    const list = document.getElementById("sitzungen");
    for (const m of data.meetings) {
      const li = document.createElement("li");
      li.textContent = `${new Date(m.start).toLocaleString("de-DE")} – ${m.title}`;
      list.appendChild(li);
    }
  });
</script>
```

## Sicherheit und Datenschutz

- Das Token gewährt ausschließlich Lesezugriff auf ohnehin öffentliche Inhalte. Trotzdem: die URL wie ein Passwort behandeln und bei Bedarf über „API-Token erneuern“ austauschen.
- Aktivierung, Änderungen und Token-Erneuerung werden in der Änderungshistorie der Fraktionssitzungen protokolliert.
- Die Filterung auf öffentliche Inhalte wird serverseitig erzwungen und durch automatische Tests mit Antwort-Scans abgesichert.

## Eigene Installation

Bei einer selbst betriebenen Installation ersetzen Sie `mandari.de` durch Ihre Domain. Die Pfade unterhalb von `/api/public/v1/` bleiben gleich.
