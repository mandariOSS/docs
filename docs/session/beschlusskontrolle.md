---
title: Beschlusskontrolle
description: Beschlussregister in mandari Session. Zuständigkeit, Fristen und Umsetzungsstand je Beschluss dokumentieren, Wiedervorlagen erhalten und den Stand für Fraktionen und Öffentlichkeit freigeben.
---

# Beschlusskontrolle

Nach der Beschlussfassung dokumentiert die Verwaltung je Beschluss den Umsetzungsstand: zuständige Stelle, Erledigungsfrist, Status und Erledigungsvermerk. So bleibt nachvollziehbar, was aus den Beschlüssen des Rates und seiner Ausschüsse geworden ist.

## Beschlussregister

Unter `<kommune>/resolutions/` listet das Register alle Tagesordnungspunkte mit Abstimmungsergebnis:

- **Ampel**: offen, in Umsetzung, überfällig, erledigt
- **Filter** nach Gremium, Jahr, Ergebnis und Umsetzungsstand
- **CSV-Export** für Berichte an Rat und Ausschüsse

## Umsetzungsstand pflegen

Je Beschluss öffnet *Tracking* am Tagesordnungspunkt (`<kommune>/agenda/<top>/tracking/`) das Formular mit:

| Feld | Bedeutung |
|------|-----------|
| Zuständige Stelle | Amt oder Fachbereich, das die Umsetzung verantwortet |
| Erledigungsfrist | Geplantes Datum der Umsetzung |
| Umsetzungsstand | offen, in Umsetzung, erledigt, zurückgestellt |
| Erledigungsvermerk | Interner Vermerk, wird nie veröffentlicht |
| Öffentliche Statusmeldung | Freitext ohne Interna für das Bürgerportal (nur bei aktivierter Veröffentlichung) |
| Öffentlich zeigen | Einzelnen Beschluss vom Portal ausnehmen (Standard: an) |

Nötig ist die Berechtigung zur Bearbeitung von Sitzungen. Jede Änderung erzeugt einen Audit-Eintrag.

## Wiedervorlage

Naht eine Erledigungsfrist oder ist sie überschritten, erinnert Session die zuständigen Nutzerinnen und Nutzer per E-Mail. Wird die Frist verschoben, wird für die neue Frist erneut erinnert. Vorlaufzeit und An/Aus konfiguriert die Kommune unter [Fristen-Erinnerungen](fristen-erinnerungen.md).

## Sichtbarkeit nach außen

Die Beschlusskontrolle hat zwei Adressaten außerhalb der Verwaltung, beide sehen ausschließlich öffentliche Beschlüsse:

- **Fraktionen in mandari Work** sehen unter *Ratsinformation → Beschlüsse* den Umsetzungsstand inklusive Erledigungsvermerk, sobald Tagesordnungspunkt und Sitzung öffentlich sind ([Beschlüsse der Kommune](../work/beschluesse.md)).
- **Bürgerinnen und Bürger** sehen im Portal Status-Zeitleiste und öffentliche Statusmeldung, wenn die Kommune „Umsetzungsstand veröffentlichen“ aktiviert hat ([Beschlüsse verfolgen](../insight/beschluesse.md)). Der interne Erledigungsvermerk bleibt immer intern.
