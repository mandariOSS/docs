---
title: Release- und Support-Politik
description: Wie mandari versioniert wird, wie oft Releases erscheinen, welche Versionen wie lange Korrekturen erhalten, in welcher Frist Sicherheitslücken geschlossen werden, wie lange Schnittstellen stabil bleiben und wie Sie Sicherheitsmeldungen abonnieren.
---

# Release- und Support-Politik

Kommunen planen Fachverfahren über Jahre. Diese Seite legt fest, wie mandari versioniert wird, wie oft Releases erscheinen, welche Versionen wie lange Korrekturen erhalten, in welcher Frist Sicherheitslücken geschlossen werden und wie lange Schnittstellen stabil bleiben. Sie ist die verbindliche Grundlage für Betreiber, Selbstbetreiber und Vergabestellen.

!!! info "Stand"
    Fassung vom 11.11.2026, gültig ab Version 0.13.0: Release alle zwei Wochen, Pflegeversionen je Quartal. Die erste Fassung wurde am 17.09.2026 beschlossen und galt ab 0.10.0. Änderungen vermerken wir unten mit Datum. Die Fassung im Repository steht in `docs/RELEASE_POLITIK.md`.

## Versionierung

mandari folgt [Semantic Versioning 2.0](https://semver.org/lang/de/) (`MAJOR.MINOR.PATCH`):

| Teil | Bedeutung | Für Sie heißt das | Beispiel |
|------|-----------|-------------------|----------|
| **PATCH** | nur Fehlerbehebungen und Sicherheitskorrekturen, keine neuen Funktionen | ohne Prüfung einspielen | 0.16.0 → 0.16.1 |
| **MINOR** | neue Funktionen, Einstellungen, Schnittstellenversionen; alles Bisherige läuft weiter | einspielen ohne Handarbeit | 0.16 → 0.17 |
| **MAJOR** | eine Migration mit Handarbeit, der Bruch einer veröffentlichten Schnittstelle oder der Wegfall einer Funktion | Umstellung planen; wir kündigen sie lange vorher an | 1.x → 2.0 |

**Vor 1.0** halten wir uns bereits an diese Regeln. Brechende Änderungen sind bis 1.0 in einer MINOR-Version nur ausnahmsweise erlaubt: Sie stehen mindestens vier Wochen vorher im Changelog unter „Abgekündigt“, bekommen eine Migrationsanleitung und kommen nie in eine Patch-Version einer Pflegeversion.

Die Container-Images tragen die Version als Tag, zum Beispiel `v0.16.0`. Dazu gibt es bewegliche Tags (`v0.16` für die jüngste Patch-Version einer Linie, `latest`) und Entwicklungs-Tags, siehe [Updates und Backups](../betrieb/updates-backups.md#versionen). Entwicklungsstände (`dev`, `dev-<commit>`) sind keine Releases und tragen keine Zusage. Zu jedem Release gehört eine Stückliste der Abhängigkeiten als Anhang (siehe [Abhängigkeiten (SBOM)](sbom.md)).

## Release-Rhythmus

| Art | Rhythmus | Inhalt |
|-----|----------|--------|
| **MINOR** | alle **zwei Wochen**, dienstags | was am Donnerstag davor fertig war und seitdem in unserem Betrieb läuft |
| **PATCH** | bei Bedarf, innerhalb der Fristen unten | nur Korrekturen, keine neuen Funktionen |
| **MAJOR** | angekündigt mindestens **sechs Monate** vorher | mit Migrationsleitfaden |

Jedes Release läuft vorher mehrere Tage in dem von uns betriebenen Hosting; ein Release ist damit nie der erste Kontakt mit echtem Betrieb. Fällt ein Termin zwischen den 24.12. und den 01.01. oder auf einen bundesweiten Feiertag, entfällt das Release. Die Termine stehen an den [Meilensteinen auf GitHub](https://github.com/mandariOSS/mandari/milestones).

Zwei Wochen bringen Korrekturen und neue Funktionen schnell zu allen Installationen, und jedes Release bleibt klein. Wer seltener aktualisieren möchte, bleibt auf einer Pflegeversion.

## Pflegeversionen und Supportzeitraum

Sie können zwischen zwei Wegen wählen: mit dem Takt gehen oder auf einer Pflegeversion bleiben.

| Version | Erhält | Dauer |
|---------|--------|-------|
| **Jüngste MINOR** | Funktionen, Fehlerbehebungen, Sicherheitskorrekturen | bis zur nächsten MINOR |
| **Pflegeversion** | Sicherheitskorrekturen ab „mittel“ und Korrekturen kritischer Fehler als PATCH | **sechs Monate** ab Erscheinen |
| **übrige MINOR** | keine Korrekturen mehr nach Erscheinen der Nachfolgerin; die Aktualisierung auf die jüngste Version geht ohne Handarbeit | – |
| **LTS** (ab 1.0) | Sicherheitskorrekturen und kritische Fehlerbehebungen | **24 Monate**, eine Linie je Jahr |

**Pflegeversion** ist die erste MINOR-Version eines Kalenderquartals. Alle drei Monate kommt also eine neue hinzu, meist werden zwei gleichzeitig gepflegt. Kritische Fehler sind Datenverlust oder die Verfälschung gespeicherter Daten, Nichtöffentliches oder Personenbezogenes, das Unbefugten sichtbar wird, der Ausfall einer Kernfunktion ohne Umgehung und Fehler mit Rechtswirkung, etwa falsch berechnete Fristen. Patch-Versionen einer Pflegeversion enthalten keine Datenbankmigrationen.

| Unterstützte Pflegeversion | Sicherheitskorrekturen bis |
|----------------------------|----------------------------|
| 0.11 (Übergang, bisher zugesagt) | 03.05.2027 |
| 0.12 (4. Quartal 2026) | 17.05.2027 |
| 0.16 (1. Quartal 2027, erscheint am 12.01.2027) | 12.07.2027 |

Die jeweils gültige Liste steht in [SECURITY.md](https://github.com/mandariOSS/mandari/blob/main/SECURITY.md#unterstützte-versionen). Wie Pflegeversionen und LTS-Linien ab 1.0 zusammenspielen, legen wir spätestens mit der Ankündigung von 1.0 fest.

**Betreutes Hosting:** Unsere Cloud läuft auf dem jüngsten Stand. Weitere gehostete Instanzen aktualisieren wir spätestens **14 Tage** nach einem Release, Sicherheitskorrekturen innerhalb der Fristen unten, ohne gesonderte Zustimmung. Angekündigt wird über die Statusseite [status.mandari.de](https://status.mandari.de) und, wenn sich die Bedienung ändert, per Mail an die hinterlegte Kontaktadresse.

## Fristen für Sicherheitskorrekturen

Schweregrad nach CVSS 3.1:

| Schweregrad | CVSS | Korrektur in Produktion und als Release | Pflegeversionen | Veröffentlichung des Advisories |
|-------------|------|------------------------------------------|-----------------|---------------------------------|
| **Kritisch** | ab 9,0 | **72 Stunden** | PATCH in derselben Frist | mit der Korrektur, CVE wird beantragt |
| **Hoch** | 7,0 bis 8,9 | **7 Tage** | PATCH in derselben Frist | mit der Korrektur, CVE wird beantragt |
| **Mittel** | 4,0 bis 6,9 | **30 Tage** | PATCH in derselben Frist | mit der Korrektur |
| **Niedrig** | unter 4,0 | spätestens mit der nächsten Pflegeversion | – | im Changelog |

Für die jüngste Version erscheint die Korrektur als PATCH oder mit der nächsten MINOR, wenn diese innerhalb der Frist erscheint. Die Frist beginnt mit der Bestätigung der Meldung; den Eingang bestätigen wir innerhalb von drei Werktagen. Abhängigkeiten überwacht Dependabot, und die Prüfungen mit `pip-audit` und `npm audit` blockieren Änderungen mit bekannten Lücken ab „hoch“. Ist eine Korrektur in der Frist nicht möglich, veröffentlichen wir eine Übergangsmaßnahme (Konfiguration, Abschaltung einer Funktion) und einen Termin.

Sicherheitslücken melden Sie bitte nicht öffentlich, sondern an <security@mandari.de>; den Ablauf beschreibt [SECURITY.md](https://github.com/mandariOSS/mandari/blob/main/SECURITY.md).

## Schnittstellen und Abkündigung

| Schnittstelle | Versionierung | Ankündigungsfrist für brechende Änderungen |
|---------------|---------------|--------------------------------------------|
| [OParl-API](../insight/oparl-api.md) (`/oparl/v1/`) | folgt dem OParl-Standard (1.0, 1.1); Erweiterungen mit dem Präfix `mandari:` | **12 Monate**, die alte Version bleibt parallel erreichbar |
| [Session-API](../session/api-v1.md) (`/api/v1/session/`) | Version im Pfad (`v1`, `v2`) | **6 Monate**, die alte Version parallel |
| [Fraktions-API](../work/fraktions-api.md) (`/api/public/v1/`) | Version im Pfad | **6 Monate**, die alte Version parallel |
| Provisioning-API | intern, nur für den Betreiber | keine Zusage |

Diese Fristen hängen am Kalender, nicht am Release-Rhythmus: Wer auf mandari aufbaut, braucht die Zeit unabhängig davon, wie oft wir veröffentlichen. Abkündigungen stehen im Changelog unter „Abgekündigt“ mit dem Datum des Wegfalls, in der Antwort der Schnittstelle als Header `Deprecation` ([RFC 9745](https://www.rfc-editor.org/rfc/rfc9745), Zeitpunkt der Abkündigung) und `Sunset` ([RFC 8594](https://www.rfc-editor.org/rfc/rfc8594), Zeitpunkt des Wegfalls) und in dieser Dokumentation. Ein Beispiel sind die alten Pfade der Session-API, die am 31.05.2027 entfallen (siehe [Session-API v1](../session/api-v1.md)). Felder werden nie umgedeutet; sie werden ergänzt oder nach Frist entfernt.

## Changelog

Der [Changelog](https://github.com/mandariOSS/mandari/blob/main/CHANGELOG.md) folgt [Keep a Changelog 1.1](https://keepachangelog.com/de/1.1.0/): je Release die Abschnitte *Hinzugefügt*, *Geändert*, *Abgekündigt*, *Entfernt*, *Behoben* und *Sicherheit* (mit GHSA- bzw. CVE-Kennung). Jedes Release ab 0.10.0 enthält einen Eintrag; ohne Eintrag wird kein Release gesetzt. Beim Veröffentlichen prüft die Release-Pipeline, dass das Tag zu den Versionsangaben im Code passt.

## Sicherheitsmeldungen und Releases abonnieren

| Weg | So geht es |
|-----|------------|
| **Benachrichtigung bei GitHub** | Im Repository [mandariOSS/mandari](https://github.com/mandariOSS/mandari) unter „Watch → Custom“ die Punkte „Security alerts“ und „Releases“ wählen. Die veröffentlichten Advisories stehen unter [Security Advisories](https://github.com/mandariOSS/mandari/security/advisories). |
| **Atom-Feed der Releases** | <https://github.com/mandariOSS/mandari/releases.atom> in einem Feedreader abonnieren. Sicherheitskorrekturen erscheinen in einem Release und dort im Abschnitt „Sicherheit“ des Changelogs. |
| **E-Mail-Verteiler** | `security-announce@mandari.de`, nur Ankündigungen. Die Anmeldung über das Trust Center auf mandari.de folgt. |

## Auf einen Blick

| Punkt | Regel |
|-------|-------|
| Rhythmus MINOR | alle zwei Wochen, dienstags |
| Pflegeversion | erste MINOR jedes Quartals, sechs Monate Sicherheitskorrekturen ab „mittel“ und kritische Fehler |
| übrige MINOR | Korrekturen bis zur nächsten MINOR |
| Übergang | 0.11 bis 03.05.2027, 0.12 bis 17.05.2027 |
| LTS | ab 1.0, 24 Monate, jährlich |
| Aktualisierung im betreuten Hosting | binnen 14 Tagen, Sicherheit nach Fristen |
| Sicherheitsfristen | 72 Stunden, 7 Tage, 30 Tage, nächste Pflegeversion |
| MAJOR | mindestens sechs Monate angekündigt |
| Abkündigung von Schnittstellen | OParl 12 Monate, übrige 6 Monate |
| Verteiler | security-announce@mandari.de |

## Änderungen

| Datum | Änderung |
|-------|----------|
| 11.11.2026 | Release alle zwei Wochen statt alle zwei Monate; Pflegeversionen je Quartal statt Pflege jeder vorherigen MINOR; Frist für niedrige Befunde an die Pflegeversion gebunden; Übergang für 0.11 und 0.12 |
| 17.09.2026 | erste Fassung, gültig ab 0.10.0 |
