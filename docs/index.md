---
title: Start
description: Einstieg in die Dokumentation der mandari-Plattform für Bürgerinnen und Bürger, Fraktionen, Verwaltungen, Entwicklerinnen und Betreiber.
hide:
  - toc
---

# mandari Dokumentation

Willkommen! Hier findest du alles, um mandari zu nutzen, Daten einzubinden und die Plattform selbst zu betreiben: vom Bürgerportal über die offenen Schnittstellen bis zu Self-Hosting und Datenschutz.

## Wo möchtest du hin?

<div class="mandari-grid" markdown>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-eye-24:</span>
**[Insight – Bürgerportal](insight/index.md)**
Ratsinformationen durchsuchen, Beschlüsse verfolgen, Fragen an Ratsmitglieder stellen. Plus die OParl-Aggregations-API für Entwicklerinnen und Entwickler.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-briefcase-24:</span>
**[Work – Fraktionen](work/index.md)**
Sitzungsvorbereitung, Anträge, digitale Einreichung bei der Verwaltung und die öffentliche Fraktions-API für eure Webseite.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-law-24:</span>
**[Session – Verwaltung](session/index.md)**
Das Ratsinformationssystem für Kommunen: Sitzungsdienst, Beschlusskontrolle, Fristen, OParl-Schnittstelle je Kommune.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-server-24:</span>
**[Betrieb und Self-Hosting](betrieb/index.md)**
mandari mit Docker selbst betreiben, konfigurieren, Quellen anbinden, überwachen und aktualisieren.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-shield-lock-24:</span>
**[Datenschutz](datenschutz/index.md)**
Technische und organisatorische Maßnahmen, Löschkonzept, Muster-AVV und der Umgang unseres Crawlers mit kommunalen Servern.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-code-24:</span>
**[Entwicklung](entwicklung/index.md)**
Quellcode, Technologie-Stack, Tests und wie du an mandari oder an dieser Dokumentation mitarbeitest.
</div>

</div>

## Schnellzugriff

| Du bist … | Starte hier |
|-----------|-------------|
| **Fraktion** und willst Termine auf eurer Webseite zeigen | [Termine auf der eigenen Webseite](work/termine-einbinden.md) |
| **Entwickler:in** und willst Ratsinformationen maschinell nutzen | [OParl-Aggregations-API](insight/oparl-api.md) |
| **Verwaltung** und willst eure Daten ins Bürgerportal bringen | [Veröffentlichung im Bürgerportal](session/buergerportal.md) |
| **Admin** und willst mandari selbst hosten | [Self-Hosting mit Docker](betrieb/index.md) |
| **Datenschutzbeauftragte:r** und brauchst TOM und AVV | [Datenschutz](datenschutz/index.md) |

## Über mandari

mandari ist eine Open-Source-Plattform für kommunalpolitische Transparenz in Deutschland. Sie baut auf dem [OParl-Standard](https://oparl.org) für offene Ratsinformationssysteme auf und besteht aus drei Bausteinen, die auf denselben offenen Daten aufsetzen. Mehr dazu unter [Die Plattform im Überblick](plattform.md).

Der Quellcode liegt auf [GitHub](https://github.com/mandariOSS/mandari), der aktuelle Betriebsstatus aller Dienste unter [status.mandari.de](https://status.mandari.de). Auch diese Dokumentation ist [quelloffen](https://github.com/mandariOSS/docs): Jede Seite hat oben rechts einen Bearbeiten-Stift.
