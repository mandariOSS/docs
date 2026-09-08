---
title: Termine auf der eigenen Webseite
description: Schritt für Schritt die nächsten öffentlichen Fraktionssitzungen automatisch auf der Fraktions-Webseite anzeigen, ohne Plugin und ohne Backend.
---

# Termine auf der eigenen Webseite

In zehn Minuten zeigt eure Webseite automatisch die nächsten öffentlichen Fraktionssitzungen. Ohne Plugin, ohne Backend, mit einem kleinen JavaScript-Snippet. Grundlage ist die [öffentliche Fraktions-API](fraktions-api.md).

## Schritt 1: API aktivieren

Im Work-Portal unter **Organisation → Reiter „API“** die öffentliche API aktivieren und die **Basis-URL** kopieren. Sie enthält euer Zugangs-Token.

!!! tip "Origins einschränken"
    Beschränkt dort die „Erlaubten Origins“ auf eure Webseiten-Domain. Dann kann niemand sonst die Daten per Browser einbetten.

## Schritt 2: Snippet einbauen

Diesen Block an die gewünschte Stelle eurer Webseite einfügen und `DEINE_BASIS_URL` durch die kopierte URL ersetzen. Der API-Reiter erzeugt das Snippet auch fertig ausgefüllt zum Kopieren.

```html
<div id="fraktions-termine">Termine werden geladen…</div>
<script>
fetch("DEINE_BASIS_URLsitzungen/")
  .then(r => r.json())
  .then(data => {
    const el = document.getElementById("fraktions-termine");
    const kommende = data.meetings.filter(m => new Date(m.start) >= new Date() && !m.cancelled);
    if (!kommende.length) { el.textContent = "Aktuell keine öffentlichen Termine."; return; }
    el.innerHTML = kommende.map(m =>
      "<p><strong>" + new Date(m.start).toLocaleString("de-DE", {dateStyle: "medium", timeStyle: "short"}) +
      "</strong> – " + m.title + (m.location ? " (" + m.location + ")" : "") + "</p>"
    ).join("");
  })
  .catch(() => { document.getElementById("fraktions-termine").textContent = "Termine derzeit nicht verfügbar."; });
</script>
```

## Schritt 3: Prüfen

Seite neu laden, die kommenden Termine erscheinen. Falls nicht:

| Symptom | Ursache und Lösung |
|---------|--------------------|
| „Termine derzeit nicht verfügbar“ | Basis-URL prüfen (endet auf `/`). Ist die API im Work-Portal wirklich aktiviert? |
| Leere Liste | Es gibt aktuell keine geplanten öffentlichen Sitzungen. Entwürfe und nicht-öffentliche Termine erscheinen nie. |
| CORS-Fehler in der Browser-Konsole | Eure Domain unter „Erlaubte Origins“ eintragen, oder das Feld leeren, um alle Origins zuzulassen. |

## WordPress und andere Systeme

Das Snippet funktioniert überall, wo ihr HTML einfügen könnt. Bei WordPress zum Beispiel über einen „Custom HTML“-Block, bei TYPO3 über ein HTML-Inhaltselement. Für Systeme, die kein JavaScript erlauben, könnt ihr die JSON-Daten auch serverseitig abrufen und rendern. Die Details stehen in der [API-Referenz](fraktions-api.md).

## Tagesordnung mit anzeigen

Die Terminliste enthält keine Tagesordnung. Wenn ihr sie anzeigen wollt, ruft je Sitzung den Detail-Endpunkt `…/sitzungen/<id>/` auf. Er liefert das Feld `agenda` mit Nummer und Titel der öffentlichen Punkte. Ob die Tagesordnung überhaupt ausgeliefert wird, entscheidet ihr im API-Reiter.
