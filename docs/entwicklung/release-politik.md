---
title: Release- und Support-Politik
description: Wie mandari versioniert wird, wie oft Releases erscheinen, welche Versionen wie lange Korrekturen erhalten, in welcher Frist Sicherheitslücken geschlossen werden, wie lange Schnittstellen stabil bleiben und wie Sie Sicherheitsmeldungen abonnieren.
---

# Release- und Support-Politik

Kommunen planen Fachverfahren über Jahre. Diese Seite legt fest, wie mandari versioniert wird, wie oft Releases erscheinen, welche Versionen wie lange Korrekturen erhalten, in welcher Frist Sicherheitslücken geschlossen werden und wie lange Schnittstellen stabil bleiben. Sie ist die verbindliche Grundlage für Betreiber, Selbstbetreiber und Vergabestellen.

!!! info "Stand"
    Fassung vom 26.11.2026: keine Pflegeversionen und kein LTS, unterstützt wird nur die jüngste MINOR; eine MAJOR-Version kündigen wir mindestens drei Monate vorher an. Die vorige Fassung vom 11.11.2026 galt ab Version 0.13.0 (Release alle zwei Wochen). Die erste Fassung wurde am 17.09.2026 beschlossen und galt ab 0.10.0. Änderungen vermerken wir unten mit Datum. Die Fassung im Repository steht in `docs/RELEASE_POLITIK.md`.

## Versionierung

mandari folgt [Semantic Versioning 2.0](https://semver.org/lang/de/) (`MAJOR.MINOR.PATCH`):

| Teil | Bedeutung | Für Sie heißt das | Beispiel |
|------|-----------|-------------------|----------|
| **PATCH** | nur Fehlerbehebungen und Sicherheitskorrekturen, keine neuen Funktionen | ohne Prüfung einspielen | 0.16.0 → 0.16.1 |
| **MINOR** | neue Funktionen, Einstellungen, Schnittstellenversionen; alles Bisherige läuft weiter | einspielen ohne Handarbeit | 0.16 → 0.17 |
| **MAJOR** | eine Migration mit Handarbeit, der Bruch einer veröffentlichten Schnittstelle oder der Wegfall einer Funktion | Umstellung planen; wir kündigen sie mindestens drei Monate vorher an | 1.x → 2.0 |

**Vor 1.0** halten wir uns bereits an diese Regeln. Brechende Änderungen sind bis 1.0 in einer MINOR-Version nur ausnahmsweise erlaubt: Sie stehen mindestens vier Wochen vorher im Changelog unter „Abgekündigt“, bekommen eine Migrationsanleitung und kommen nie in eine PATCH-Version.

Die Container-Images tragen die Version als Tag, zum Beispiel `v0.16.0`. Dazu gibt es bewegliche Tags (`v0.16` für die jüngste Patch-Version einer Linie, `latest`) und Entwicklungs-Tags, siehe [Updates und Backups](../betrieb/updates-backups.md#versionen). Entwicklungsstände (`dev`, `dev-<commit>`) sind keine Releases und tragen keine Zusage. Zu jedem Release gehört eine Stückliste der Abhängigkeiten als Anhang (siehe [Abhängigkeiten (SBOM)](sbom.md)).

## Release-Rhythmus

| Art | Rhythmus | Inhalt |
|-----|----------|--------|
| **MINOR** | alle **zwei Wochen**, dienstags | was am Donnerstag davor fertig war und seitdem in unserem Betrieb läuft |
| **PATCH** | bei Bedarf, innerhalb der Fristen unten | nur Korrekturen, keine neuen Funktionen |
| **MAJOR** | angekündigt mindestens **drei Monate** vorher | mit Migrationsleitfaden |

Jedes Release läuft vorher in dem von uns betriebenen Hosting; ein Release ist damit nie der erste Kontakt mit echtem Betrieb. Muss nach dem Donnerstag ein Fehler behoben werden, der das Release verhindert, erscheint der korrigierte Stand, wenn er bis Dienstag mindestens einen Werktag bei uns läuft; er enthält dann auch, was seitdem fertig wurde. Sonst entfällt das Release, und das nächste erscheint planmäßig. Fällt ein Termin zwischen den 24.12. und den 01.01. oder auf einen bundesweiten Feiertag, entfällt das Release. Die Termine stehen an den [Meilensteinen auf GitHub](https://github.com/mandariOSS/mandari/milestones).

Zwei Wochen bringen Korrekturen und neue Funktionen schnell zu allen Installationen, und jedes Release bleibt klein. Jede MINOR lässt sich ohne Handarbeit einspielen, außer bei einer vor 1.0 angekündigten brechenden Änderung (mit Migrationsanleitung) und bei einer MAJOR-Version (mit Migrationsleitfaden). Deshalb pflegen wir nur die jüngste.

## Supportzeitraum

Wir unterstützen nur die **jüngste MINOR**. Pflegeversionen gibt es nicht, und es gibt **kein LTS**, auch nicht ab 1.0. Dafür entwickeln wir zu schnell.

| Version | Erhält | Dauer |
|---------|--------|-------|
| **Jüngste MINOR** | Sicherheitskorrekturen und Korrekturen kritischer Fehler als PATCH oder mit der nächsten MINOR, wenn diese innerhalb der Frist erscheint | bis zur nächsten MINOR |
| **ältere MINOR** | keine Korrekturen mehr nach Erscheinen der Nachfolgerin; die Aktualisierung auf die jüngste Version geht ohne Handarbeit, außer bei angekündigten brechenden Änderungen und MAJOR-Versionen | – |
| **0.11 und 0.12** (Übergang) | Sicherheitskorrekturen ab „mittel“ und Korrekturen kritischer Fehler als PATCH | bis **31.01.2027** |

Kritische Fehler sind Datenverlust oder die Verfälschung gespeicherter Daten, Nichtöffentliches oder Personenbezogenes, das Unbefugten sichtbar wird, der Ausfall einer Kernfunktion ohne Umgehung und Fehler mit Rechtswirkung, etwa falsch berechnete Fristen. Zurückportierte Korrekturen enthalten keine Datenbankmigrationen. Die jeweils gültige Liste steht in [SECURITY.md](https://github.com/mandariOSS/mandari/blob/main/SECURITY.md#unterstützte-versionen).

!!! warning "Änderung vom 26.11.2026"
    Bisher war die erste MINOR jedes Quartals eine Pflegeversion mit sechs Monaten Pflege, ab 1.0 war LTS mit 24 Monaten angekündigt. Beides entfällt. Zugesagt waren Korrekturen für 0.11 bis 03.05.2027 und für 0.12 bis 17.05.2027. Beide erhalten Sicherheitskorrekturen ab „mittel“ und Korrekturen kritischer Fehler nur noch bis **31.01.2027**; danach endet ihre Pflege. Wenn Sie 0.11 oder 0.12 betreiben, aktualisieren Sie bis dahin auf die jüngste Version. 0.16 und spätere Versionen werden keine Pflegeversionen.

**Betreutes Hosting:** Unsere Cloud läuft auf dem jüngsten Stand. Weitere gehostete Instanzen aktualisieren wir spätestens **14 Tage** nach einem Release, Sicherheitskorrekturen innerhalb der Fristen unten, ohne gesonderte Zustimmung. Angekündigt wird über die Statusseite [status.mandari.de](https://status.mandari.de) und, wenn sich die Bedienung ändert, per Mail an die hinterlegte Kontaktadresse.

## Fristen für Sicherheitskorrekturen

Schweregrad nach CVSS 3.1:

| Schweregrad | CVSS | Korrektur in Produktion und als Release | 0.11 und 0.12 (bis 31.01.2027) | Veröffentlichung des Advisories |
|-------------|------|------------------------------------------|--------------------------------|---------------------------------|
| **Kritisch** | ab 9,0 | **72 Stunden** | PATCH in derselben Frist | mit der Korrektur, CVE wird beantragt |
| **Hoch** | 7,0 bis 8,9 | **7 Tage** | PATCH in derselben Frist | mit der Korrektur, CVE wird beantragt |
| **Mittel** | 4,0 bis 6,9 | **30 Tage** | PATCH in derselben Frist | mit der Korrektur |
| **Niedrig** | unter 4,0 | spätestens mit der nächsten MINOR | – | im Changelog |

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
| Unterstützt | nur die jüngste MINOR: Sicherheitskorrekturen und kritische Fehler als PATCH oder mit der nächsten MINOR |
| ältere MINOR | keine Korrekturen mehr; Aktualisierung ohne Handarbeit (Ausnahmen: angekündigte brechende Änderungen, MAJOR) |
| Pflegeversionen, LTS | keine, auch nicht ab 1.0 |
| Übergang | 0.11 und 0.12 bis 31.01.2027, Sicherheitskorrekturen ab „mittel“ und kritische Fehler |
| Aktualisierung im betreuten Hosting | binnen 14 Tagen, Sicherheit nach Fristen |
| Sicherheitsfristen | 72 Stunden, 7 Tage, 30 Tage, nächste MINOR |
| Brechende Änderungen vor 1.0 | mindestens vier Wochen angekündigt, nie in einer PATCH-Version |
| MAJOR | mindestens drei Monate angekündigt, mit Migrationsleitfaden |
| Abkündigung von Schnittstellen | OParl 12 Monate, übrige 6 Monate |
| Verteiler | security-announce@mandari.de |

## Änderungen

| Datum | Änderung |
|-------|----------|
| 26.11.2026 | keine Pflegeversionen und kein LTS mehr, unterstützt wird nur die jüngste MINOR; 0.11 und 0.12 erhalten Korrekturen nur noch bis 31.01.2027 statt bis 03.05.2027 bzw. 17.05.2027; niedrige Sicherheitsbefunde mit der nächsten MINOR; MAJOR mindestens drei statt sechs Monate vorher angekündigt |
| 11.11.2026 | Release alle zwei Wochen statt alle zwei Monate; Pflegeversionen je Quartal statt Pflege jeder vorherigen MINOR; Frist für niedrige Befunde an die Pflegeversion gebunden; Übergang für 0.11 und 0.12 |
| 17.09.2026 | erste Fassung, gültig ab 0.10.0 |
