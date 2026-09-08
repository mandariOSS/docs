---
title: Session – Ratsinformationssystem für Verwaltungen
description: Was mandari Session dem kommunalen Sitzungsdienst bietet, wie Mandanten, Rollen und Öffentlichkeit funktionieren und welche Anleitungen es gibt.
---

# Session – Ratsinformationssystem für Verwaltungen

mandari Session ist das Ratsinformationssystem für kommunale Verwaltungen. Der Sitzungsdienst pflegt Gremien, Sitzungen, Vorlagen und Protokolle, kontrolliert Beschlüsse, rechnet Sitzungsgelder ab und veröffentlicht öffentliche Informationen auf Knopfdruck ins Bürgerportal.

Jede Kommune ist ein eigener **Mandant** mit eigenen Nutzerinnen und Nutzern, Rollen, Einstellungen und Verschlüsselungsschlüssel. Der Zugang läuft über `/session/<kommune>/`.

## Funktionen

| Bereich | Was er leistet |
|---------|----------------|
| **Gremien und Personen** | Rat, Ausschüsse, Beiräte, Fraktionen mit Mitgliedschaften, Wahlperioden. Kontaktdaten verschlüsselt gespeichert |
| **Sitzungen** | Sitzungsplanung, Tagesordnung mit öffentlichem und nicht-öffentlichem Teil, Einladungen, Ladungsfristen, Anwesenheit |
| **Vorlagen** | Drucksachen mit Nummernkreis, Anlagen, Beratungsfolge über mehrere Gremien |
| **Anträge** | Eingang von Fraktionsanträgen, auch [digital aus mandari Work](../work/antraege-einreichen.md), Prüfung, Umwandlung in Vorlagen |
| **Abstimmungen** | Ergebnisse je Tagesordnungspunkt: offen, geheim, summiert oder namentlich |
| **Protokolle** | Öffentlicher und nicht-öffentlicher Teil getrennt, Genehmigungsworkflow |
| **Beschlusskontrolle** | Beschlussregister mit Zuständigkeit, Frist und Umsetzungsstand, siehe [Beschlusskontrolle](beschlusskontrolle.md) |
| **Sitzungsgelder** | Abrechnung mit Vier-Augen-Genehmigung, SEPA-Export, Bankdaten zugriffsbeschränkt |
| **Fristen-Erinnerungen** | Automatische E-Mails bei ablaufenden Fristen, siehe [Fristen-Erinnerungen](fristen-erinnerungen.md) |
| **Bürgerportal** | Veröffentlichung öffentlicher Daten ins mandari-Bürgerportal, siehe [Veröffentlichung im Bürgerportal](buergerportal.md) |
| **OParl-Schnittstelle** | Eigene OParl-1.1-API je Kommune für beliebige Konsumenten, siehe [OParl-API je Kommune](oparl-api.md) |
| **Datenschutz** | Aufbewahrungsfristen, auditierter Löschlauf, Betroffenenauskunft, siehe [Löschkonzept](../datenschutz/loeschkonzept.md) |
| **Audit-Log** | Revisionssichere Protokollierung aller relevanten Änderungen je Mandant |

## Öffentlich und nicht-öffentlich

Session trennt konsequent zwischen öffentlichen und nicht-öffentlichen Inhalten. Jede Sitzung, jeder Tagesordnungspunkt, jede Vorlage und jede Anlage hat eine eigene Kennzeichnung. Alles, was das System nach außen gibt, ob über die OParl-Schnittstelle, ins Bürgerportal oder an Fraktionen in Work, filtert serverseitig auf öffentliche Inhalte. Wird ein Objekt nachträglich auf nicht-öffentlich gesetzt, verschwindet es auch aus allen bereits gespiegelten Ansichten (siehe Tombstones in der [OParl-API](oparl-api.md#geloschte-und-entoffentlichte-objekte-tombstones)).

## Rollen und Berechtigungen

Jeder Mandant hat eigene Rollen mit abgestuften Rechten, etwa für Sitzungsverwaltung, Vorlagen, nicht-öffentliche Inhalte, Nutzerverwaltung, Einstellungen und Sitzungsgelder. Bankdaten sind zusätzlich auf die Sitzungsgeld-Berechtigung beschränkt. Konten entstehen ausschließlich per Einladung.

## Anleitungen

- [OParl-API je Kommune](oparl-api.md): Endpunkte, Sichtbarkeitsregeln, Abstimmungsergebnisse, Tombstones
- [Veröffentlichung im Bürgerportal](buergerportal.md): Daten ins mandari-Bürgerportal bringen
- [Beschlusskontrolle](beschlusskontrolle.md): Beschlussregister und Umsetzungsstand
- [Fristen-Erinnerungen](fristen-erinnerungen.md): Typen, Vorlaufzeiten, Betrieb
- [Einreichungs-Zugänge für Fraktionen](einreichungs-zugaenge.md): Tokens für die digitale Antragseinreichung

## Für Datenschutzbeauftragte

Technische und organisatorische Maßnahmen, Löschkonzept und ein Muster für den Auftragsverarbeitungsvertrag stehen unter [Datenschutz](../datenschutz/index.md).

## Einführung und Migration

Beim Umstieg von einem Bestandssystem unterstützen wir bei Migration und Erstimport. Melde dich über [mandari.de/kontakt/](https://mandari.de/kontakt/).
