---
title: Release- und Support-Politik
description: Wie mandari versioniert wird, wie oft Releases erscheinen, wie lange eine Version unterstützt wird, in welcher Frist Sicherheitslücken geschlossen werden, wie lange Schnittstellen stabil bleiben und wie Sie Sicherheitsmeldungen abonnieren.
---

# Release- und Support-Politik

Kommunen planen Fachverfahren über Jahre. Diese Seite legt fest, wie mandari versioniert wird, wie oft Releases erscheinen, wie lange eine Version unterstützt wird, in welcher Frist Sicherheitslücken geschlossen werden und wie lange Schnittstellen stabil bleiben. Sie ist die verbindliche Grundlage für Betreiber, Selbstbetreiber und Vergabestellen.

!!! info "Stand"
    Beschlossen am 17.09.2026, gültig ab Version 0.10.0. Das erste Release nach diesen Regeln ist [0.11.0 vom 27.09.2026](https://github.com/mandariOSS/mandari/releases/tag/v0.11.0). Änderungen vermerken wir hier mit Datum. Die Fassung im Repository steht in `docs/RELEASE_POLITIK.md`.

## Versionierung

mandari folgt [Semantic Versioning 2.0](https://semver.org/lang/de/) (`MAJOR.MINOR.PATCH`):

| Teil | Wann | Beispiel |
|------|------|----------|
| **MAJOR** | Änderungen, die eine Migration mit Handarbeit, den Bruch einer veröffentlichten Schnittstelle oder den Wegfall einer Funktion bedeuten | 0.x → 1.0 |
| **MINOR** | neue Funktionen, neue Einstellungen, neue Schnittstellenversionen; Aktualisierung ohne Handarbeit | 0.10 → 0.11 |
| **PATCH** | Fehlerbehebungen und Sicherheitskorrekturen ohne Funktionsänderung | 0.10.0 → 0.10.1 |

**Vor 1.0** halten wir uns bereits an diese Regeln. MINOR-Versionen können bis 1.0 in Ausnahmefällen brechende Änderungen enthalten; sie stehen dann im Changelog unter „Brechend“ und bekommen eine Migrationsanleitung.

Die Container-Images tragen die Version als Tag, zum Beispiel `v0.11.0`. Dazu gibt es bewegliche und Entwicklungs-Tags, siehe [Updates und Backups](../betrieb/updates-backups.md#versionen). Entwicklungsstände (`dev`, `dev-<commit>`) sind keine Releases und tragen keine Zusage. Zu jedem Release gehört eine Stückliste der Abhängigkeiten als Anhang (siehe [Abhängigkeiten (SBOM)](sbom.md)).

## Release-Rhythmus

| Art | Rhythmus | Inhalt |
|-----|----------|--------|
| **MINOR** | alle **zwei Monate**, jeweils in der ersten Woche | Funktionen, die auf `dev` fertig und in Produktion erprobt sind |
| **PATCH** | bei Bedarf, für Sicherheitskorrekturen innerhalb der Fristen unten | nur Korrekturen, keine neuen Funktionen |
| **MAJOR** | angekündigt mindestens **sechs Monate** vorher | mit Migrationsleitfaden |

Zwei Monate sind kurz genug, damit Korrekturen nicht liegen bleiben, und lang genug, damit Kommunen mit Test- und Freigabeprozessen nachziehen können. Das von uns betriebene Hosting läuft zwischen den Releases auf erprobten Entwicklungsständen, die vor jedem Release in Produktion waren; ein Release ist damit nie der erste Kontakt mit echtem Betrieb.

## Supportzeitraum je Version

| Version | Erhält | Dauer |
|---------|--------|-------|
| **Jüngste MINOR** | Funktionen, Fehlerbehebungen, Sicherheitskorrekturen | bis zur nächsten MINOR |
| **Vorherige MINOR** | Sicherheitskorrekturen | **sechs Monate** ab Erscheinen der Nachfolgerin |
| **LTS** | Sicherheitskorrekturen und kritische Fehlerbehebungen | **24 Monate**; die erste LTS-Linie kommt mit **1.0** |

Eine LTS-Linie gibt es ab 1.0 jeweils alle zwölf Monate. Bis dahin gilt: Wer selbst betreibt, bleibt auf einem unterstützten Stand, solange er die jüngste oder die vorherige MINOR-Version einsetzt und innerhalb von sechs Monaten nach einem MINOR-Release aktualisiert.

**Betreutes Hosting:** Wir aktualisieren alle gehosteten Instanzen spätestens **14 Tage** nach einem Release, Sicherheitskorrekturen innerhalb der Fristen unten, ohne gesonderte Zustimmung. Angekündigt wird über die Statusseite [status.mandari.de](https://status.mandari.de) und, wenn sich die Bedienung ändert, per Mail an die hinterlegte Kontaktadresse.

## Fristen für Sicherheitskorrekturen

Schweregrad nach CVSS 3.1:

| Schweregrad | CVSS | Korrektur in Produktion und als PATCH | Veröffentlichung des Advisories |
|-------------|------|---------------------------------------|---------------------------------|
| **Kritisch** | ab 9,0 | **72 Stunden** | mit der Korrektur, CVE wird beantragt |
| **Hoch** | 7,0 bis 8,9 | **7 Tage** | mit der Korrektur, CVE wird beantragt |
| **Mittel** | 4,0 bis 6,9 | **30 Tage** | mit der Korrektur |
| **Niedrig** | unter 4,0 | nächstes reguläres Release | im Changelog |

Die Frist beginnt mit der Bestätigung der Meldung; den Eingang bestätigen wir innerhalb von drei Werktagen. Abhängigkeiten überwacht Dependabot, und die Prüfungen mit `pip-audit` und `npm audit` blockieren Änderungen mit bekannten Lücken ab „hoch“. Ist eine Korrektur in der Frist nicht möglich, veröffentlichen wir eine Übergangsmaßnahme (Konfiguration, Abschaltung einer Funktion) und einen Termin.

Sicherheitslücken melden Sie bitte nicht öffentlich, sondern an <security@mandari.de>; den Ablauf beschreibt [SECURITY.md](https://github.com/mandariOSS/mandari/blob/main/SECURITY.md).

## Schnittstellen und Abkündigung

| Schnittstelle | Versionierung | Ankündigungsfrist für brechende Änderungen |
|---------------|---------------|--------------------------------------------|
| [OParl-API](../insight/oparl-api.md) (`/oparl/v1/`) | folgt dem OParl-Standard (1.0, 1.1); Erweiterungen mit dem Präfix `mandari:` | **12 Monate**, die alte Version bleibt parallel erreichbar |
| [Session-API](../session/api-v1.md) (`/api/v1/session/`) | Version im Pfad (`v1`, `v2`) | **6 Monate**, die alte Version parallel |
| [Fraktions-API](../work/fraktions-api.md) (`/api/public/v1/`) | Version im Pfad | **6 Monate**, die alte Version parallel |
| Provisioning-API | intern, nur für den Betreiber | keine Zusage |

Abkündigungen stehen im Changelog unter „Abgekündigt“ mit dem Datum des Wegfalls, in der Antwort der Schnittstelle als Header `Deprecation` ([RFC 9745](https://www.rfc-editor.org/rfc/rfc9745), Zeitpunkt der Abkündigung) und `Sunset` ([RFC 8594](https://www.rfc-editor.org/rfc/rfc8594), Zeitpunkt des Wegfalls) und in dieser Dokumentation. Ein Beispiel sind die alten Pfade der Session-API, die am 31.05.2027 entfallen (siehe [Session-API v1](../session/api-v1.md)). Felder werden nie umgedeutet; sie werden ergänzt oder nach Frist entfernt.

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
| Rhythmus MINOR | alle zwei Monate |
| Support der vorherigen MINOR | sechs Monate |
| LTS | ab 1.0, 24 Monate, jährlich |
| Aktualisierung im betreuten Hosting | binnen 14 Tagen, Sicherheit nach Fristen |
| Sicherheitsfristen | 72 Stunden, 7 Tage, 30 Tage, nächstes Release |
| Abkündigung von Schnittstellen | OParl 12 Monate, übrige 6 Monate |
| Verteiler | security-announce@mandari.de |
