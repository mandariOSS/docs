---
title: Demo-Umgebung
description: Mit einem Befehl eine vollständige, klar als Demo erkennbare Musterumgebung über Insight, Work und Session anlegen und wieder entfernen.
---

# Demo-Umgebung

Der Befehl `setup_demo_environment` erstellt eine vollständige, klar als Demo erkennbare Musterumgebung über alle drei Portale hinweg. Alle Daten sind synthetisch und frei erfunden. Ideal, um mandari nach der Installation kennenzulernen oder vorzuführen.

```bash
python manage.py setup_demo_environment          # anlegen oder aktualisieren
python manage.py setup_demo_environment --reset  # restlos entfernen
```

## Was angelegt wird

### Insight

Fiktive Kommune **„Musterstadt (Demo)“**:

- 3 Gremien (Rat, Hauptausschuss, Ausschuss für Bauen und Verkehr) und 2 Fraktionen
- 8 fiktive Personen mit Mitgliedschaften
- 6 Sitzungen, vergangene und kommende, mit Tagesordnungspunkten
- 12 Vorlagen verschiedener Typen (Beschlussvorlage, Antrag, Anfrage, Mitteilungsvorlage) mit Beratungen
- 2 kleine, selbst erzeugte PDF-Dateien mit bereits gesetztem Volltext

Die Kommune erscheint bewusst im öffentlichen Portal. Sie ist überall mit „(Demo)“ gekennzeichnet.

### Work

Organisation **„Musterfraktion (Demo)“**, verknüpft mit der Musterstadt und der Parteigruppe „Musterpartei (Demo)“:

- Standardrollen
- 3 Demo-Nutzer: Fraktionsvorsitz, Fraktionsmitglied und ein Gast mit lesender Ordnerfreigabe
- 2 Anträge (Entwurf und eingereicht), 1 Sitzungsvorbereitung mit Positionen und Notizen, 3 Aufgaben, 1 Fraktionssitzung

### Session

Mandant **„Stadtverwaltung Musterstadt (Demo)“**:

- Standardrollen, 1 Demo-Verwaltungsnutzer mit Administratorrechten
- 3 Gremien und 8 Personen passend zur Kommune, Kontaktdaten verschlüsselt gespeichert
- 3 Sitzungen mit Tagesordnung, 4 Vorlagen, 2 Anträge der Musterfraktion

## Zugangsdaten

Die Passwörter der Demo-Nutzer werden bei **jedem Lauf neu erzeugt** und ausschließlich auf der Konsole ausgegeben. Sie werden nirgendwo gespeichert. Ein erneuter Lauf rotiert die Passwörter, praktisch, wenn sie verloren gegangen sind.

## Wiederholbarkeit und Aufräumen

- Alle Objekte hängen an festen Demo-Kennungen (Slugs mit Endung `-demo`, OParl-IDs unter einer nicht auflösbaren Demo-Domain). Wiederholte Läufe aktualisieren statt zu duplizieren.
- Die Demo-Quelle ist **inaktiv**, damit der Ingestor sie nie abruft.
- `--reset` löscht ausschließlich die über diese Kennungen identifizierten Objekte: Session-Mandant, Work-Organisation, Parteigruppe, Demo-Nutzer, Quelle inklusive Kommune und erzeugte PDF-Dateien.

## Verifikation

Ein selbst enthaltener Test auf einer frischen SQLite-Instanz prüft doppelten Lauf ohne Duplikate, Demo-Logins, Darstellung der Insight-Seiten, Work-Dashboard inklusive Gastzugriff, Session-Dashboard und vollständiges Aufräumen:

```bash
python scripts/smoke_demo_environment.py
```
