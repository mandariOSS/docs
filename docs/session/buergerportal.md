---
title: Veröffentlichung im Bürgerportal
description: Wie eine Kommune mit mandari Session ihre öffentlichen Daten ins mandari-Bürgerportal bringt, was dabei passiert und wie Betreiber den Sync steuern.
---

# Veröffentlichung im Bürgerportal

Eine Kommune, die mandari Session nutzt, erscheint auf Wunsch **automatisch** im offenen, kommunenübergreifenden Bürgerportal. Technisch konsumiert der Ingestor die [OParl-API der Kommune](oparl-api.md) als ganz normale OParl-Quelle. Es gibt keinen zweiten Datenweg und damit keine Möglichkeit, dass nicht-öffentliche Inhalte ins Portal gelangen.

## Der Veröffentlichungs-Schalter

Die Kommune entscheidet, ab wann ihre öffentlichen Daten ins Portal fließen: **Session → Einstellungen → Bürgerportal → „Im Bürgerportal veröffentlichen“**. Nötig ist die Berechtigung zur Verwaltung der Einstellungen. Jedes Umschalten wird im Audit-Log protokolliert.

Beim Aktivieren wird die OParl-API der Kommune automatisch als Quelle registriert. Beim Deaktivieren wird die Quelle inaktiv gesetzt, es findet kein weiterer Sync statt. Bereits gespiegelte Daten bleiben erhalten, bis die Kommune eine Löschung beauftragt.

## Umsetzungsstand veröffentlichen

Ein zweiter Schalter auf derselben Karte, **„Umsetzungsstand veröffentlichen“**, gibt zusätzlich die Beschlusskontrolle für das Portal frei. Er setzt die Veröffentlichung im Bürgerportal voraus. Sichtbar wird nur die eigens dafür formulierte öffentliche Statusmeldung je Beschluss, nie der interne Erledigungsvermerk. Details unter [Beschlusskontrolle](beschlusskontrolle.md) und [Beschlüsse verfolgen](../insight/beschluesse.md).

## Was im Portal erscheint

Die öffentlichen Gremien, Personen, Sitzungen (nur öffentliche Teile), Vorlagen, Anlagen und Beratungsfolgen der Kommune erscheinen unter `/insight/`. Änderungen kommen mit dem nächsten Sync-Zyklus an. Wechsel von öffentlich auf nicht-öffentlich und Löschungen werden über Tombstones nachgezogen und im Portal ausgeblendet.

## Für Betreiber

### Quelle per Kommandozeile registrieren

```bash
# Registrieren (setzt den Schalter und legt die Quelle an)
python manage.py session_insight_source --tenant musterstadt

# Alle veröffentlichten Mandanten nachregistrieren, z. B. nach einem Umzug
python manage.py session_insight_source --all

# Deaktivieren
python manage.py session_insight_source --tenant musterstadt --deactivate

# Abweichende Basis-URL, z. B. lokale Instanz
python manage.py session_insight_source --tenant musterstadt --base-url http://localhost:8000
```

### Sync-Wege

1. **Produktion: Ingestor-Daemon.** Die registrierte Quelle ist eine normale OParl-Quelle und wird vom Daemon im regulären Zyklus mitsynchronisiert, inklusive `modified_since` und Tombstones. Keine weitere Konfiguration nötig.
2. **Lokal oder Einzel-Sync.** Ein leichtgewichtiger, synchroner Spiegel ohne Daemon-Abhängigkeiten, der auch mit SQLite funktioniert:

    ```bash
    # inkrementell (modified_since = letzter Sync, inkl. Tombstones)
    python manage.py sync_session_insight --tenant musterstadt

    # Voll-Sync bzw. gezielt nach Quell-URL
    python manage.py sync_session_insight --source-url http://localhost:8000/session/musterstadt/api/oparl/ --full

    # alle registrierten Session-Quellen
    python manage.py sync_session_insight --all
    ```

### Schritt für Schritt: Kommune anbinden

1. In Session als Administratorin der Kommune anmelden: *Einstellungen → Karte „Bürgerportal“ → „Im Bürgerportal veröffentlichen“*.
2. Prüfen: Im Admin unter *OParl-Quellen* existiert jetzt eine aktive Quelle mit der URL `<SITE_URL>/session/<kommune>/api/oparl/`.
3. Optional den Sync sofort anstoßen: `python manage.py sync_session_insight --tenant <kommune> --full`.
4. Ergebnis: Die öffentlichen Daten der Kommune erscheinen im Bürgerportal.
