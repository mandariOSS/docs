---
title: Insight – das Bürgerportal
description: Was das kostenlose Bürgerportal mandari Insight bietet und wie du Ratsinformationen findest, verfolgst und weiterverwendest.
---

# Insight – das Bürgerportal

mandari Insight ist das kostenlose, anmeldefreie Bürgerportal unter [mandari.de/insight/](https://mandari.de/insight/). Es zeigt die öffentlichen Ratsinformationen aller angebundenen Kommunen an einem Ort: Vorlagen, Sitzungen, Tagesordnungen, Beschlüsse, Gremien und Personen.

## Was du im Portal findest

| Bereich | Adresse | Inhalt |
|---------|---------|--------|
| Volltextsuche | `/insight/suche/` | Suche über Vorlagen, Sitzungen, Beschlüsse und Dokumenttexte aller Kommunen. Tippfehlertolerant, mit über hundert kommunalpolitischen Synonymen (etwa Radweg und Fahrradweg). |
| Vorgänge | `/insight/vorgaenge/` | Vorlagen und Drucksachen mit Beratungsfolge, Dateien, Volltext und, wo vorhanden, einer automatisch erstellten Zusammenfassung. |
| Termine | `/insight/termine/` | Sitzungskalender mit Tagesordnungen, Monatsansicht und Jahresplan. Termine lassen sich als Kalender abonnieren. |
| Gremien und Personen | `/insight/gremien/`, `/insight/personen/` | Rat, Ausschüsse und Fraktionen mit Mitgliedern, Personen mit ihren Mandaten. |
| Beschlüsse | `/insight/beschluesse/` | Was aus einem Beschluss geworden ist, inklusive Abonnement. Siehe [Beschlüsse verfolgen](beschluesse.md). |
| Ratsfragen | `/insight/fragen/` | Öffentliche Fragen an Mandatsträgerinnen und Mandatsträger. Siehe [Ratsfragen](ratsfragen.md). |

## Woher die Daten kommen

Insight spiegelt die öffentlichen Daten der angebundenen Kommunen. Quellen sind die OParl-Schnittstellen der Ratsinformationssysteme, Adapter für Systeme ohne OParl sowie Kommunen, die mandari Session als Ratsinformationssystem nutzen und ihre Daten freigegeben haben.

Die Daten werden fortlaufend aktualisiert. Ist eine Quelle länger nicht erreichbar, zeigt das Portal einen Hinweis mit dem Datenstand an. Mehr dazu unter [Dokumente und Datenstand](dokumente.md).

!!! info "Nur öffentliche Inhalte"
    Insight zeigt ausschließlich Informationen, die die Kommunen selbst öffentlich bereitstellen. Nicht-öffentliche Sitzungsteile, Personalangelegenheiten oder interne Vermerke gelangen nie ins Portal.

## Daten weiterverwenden

Alles, was im Portal steht, ist auch maschinenlesbar verfügbar: Die [OParl-Aggregations-API](oparl-api.md) liefert die Daten aller Kommunen über einen einzigen, standardkonformen Endpunkt. Anonym, lesend, kostenlos.

## Informiert bleiben

- **Beschlüsse abonnieren**: Bei jedem freigegebenen Beschluss kannst du dich per E-Mail über Fortschritte bei der Umsetzung informieren lassen ([Beschlüsse verfolgen](beschluesse.md)).
- **Kalender abonnieren**: Sitzungstermine gibt es als iCal-Feed für deinen Kalender.
- **Fragen stellen**: Über die Ratsfragen erreichst du Mandatsträgerinnen und Mandatsträger öffentlich und nachvollziehbar ([Ratsfragen](ratsfragen.md)).

## Eure Kommune fehlt?

Kommunen mit OParl-Schnittstelle können wir in der Regel schnell anbinden, für andere Systeme gibt es Adapter. Wie das technisch funktioniert, steht unter [Quellen anbinden](../betrieb/quellen-anbinden.md). Melde dich über [mandari.de/kontakt/](https://mandari.de/kontakt/).
