---
title: Fristen-Erinnerungen
description: Automatische E-Mail-Erinnerungen in mandari Session an Ladungsfristen, Vorlagenfristen, fehlende Rückmeldungen und Wiedervorlagen der Beschlusskontrolle.
---

# Fristen-Erinnerungen

Der Sitzungsdienst wird per E-Mail an ablaufende Fristen erinnert. Der Lauf ist idempotent: Jede Erinnerung wird pro Objekt und Frist genau einmal versendet. Mehrfaches Ausführen am selben Tag erzeugt keine doppelten E-Mails.

## Erinnerungstypen

| Typ | Empfänger | Standard-Vorlauf |
|-----|-----------|------------------|
| Ladungsfrist läuft ab | Nutzerinnen mit Sitzungs-Bearbeitungsrecht | 3 Tage |
| Ladungsfrist verstrichen | Nutzerinnen mit Sitzungs-Bearbeitungsrecht | sofort |
| Vorlagenfrist läuft ab (Status Entwurf oder In Prüfung) | Nutzerinnen mit Vorlagen-Bearbeitungsrecht | 3 Tage |
| Fehlende Rückmeldung zur Sitzung (nach Ladungsversand) | eingeladene Person | 5 Tage |
| Wiedervorlage Beschlusskontrolle (Frist naht oder überfällig) | Nutzerinnen mit Sitzungs-Bearbeitungsrecht | 7 Tage |

Vorlaufzeiten und An/Aus je Typ konfiguriert jede Kommune unter **Einstellungen → Fristen-Erinnerungen**. Wird eine Erledigungsfrist in der Beschlusskontrolle verschoben, wird für die neue Frist erneut erinnert.

## Betrieb

Die Erinnerungen verschickt ein Zeitplan im Worker, täglich um 07:00 für alle aktiven Mandanten. Ein Cron-Eintrag auf dem Host ist dafür nicht mehr nötig. Von Hand:

```bash
# Testlauf ohne Versand (läuft immer)
docker compose exec -T worker python manage.py send_session_reminders --dry-run

# echter Lauf für einen Mandanten, obwohl der Zeitplan ihn bedient
docker compose exec -T worker python manage.py send_session_reminders --tenant stadt-musterstadt --trotz-zeitplan
```

Alle regelmäßigen Aufgaben einer Installation sind unter [Regelmäßige Aufgaben](../betrieb/cron.md) zusammengefasst.
