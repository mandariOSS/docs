---
title: Dokumente und Datenstand
description: Wie das Bürgerportal Dokumente bereitstellt, warum Vorschau und Download auch bei Ausfall des kommunalen Systems funktionieren und was der Hinweis zum Datenstand bedeutet.
---

# Dokumente und Datenstand

## Dokumente aus dem Portal

Vorlagen, Anlagen und Niederschriften öffnest du direkt im Portal. Die Dateien werden von mandari ausgeliefert, nicht vom Server der Kommune. Das hat drei Effekte:

- **Verfügbarkeit**: Vorschau und Download funktionieren auch dann, wenn das Ratsinformationssystem der Kommune gerade nicht erreichbar ist. Dafür hält mandari eine lokale Kopie aller Dokumente vor (siehe [Dokument-Cache](../betrieb/dokument-cache.md)).
- **Datenschutz**: Dein Browser verbindet sich nicht mit dem kommunalen Server. Deine IP-Adresse landet also nicht in dessen Protokollen.
- **Volltext**: Aus jedem Dokument wird der Text extrahiert, bei gescannten Dokumenten per Texterkennung. Darauf arbeitet die Suche.

Dokumente, die noch nicht lokal vorliegen, werden beim ersten Aufruf direkt von der Quelle geholt und dabei abgelegt. Ist die Quelle gerade nicht erreichbar, erhältst du eine Meldung mit der Bitte, es später erneut zu versuchen. Die Original-Adresse beim kommunalen System ist in der [OParl-API](oparl-api.md#dateien) als `mandari:originalAccessUrl` hinterlegt.

## Hinweis zum Datenstand

Die Daten der Kommunen werden fortlaufend synchronisiert. Klappt das über längere Zeit nicht, etwa weil das kommunale System eine Störung hat oder Anfragen blockiert, zeigt das Portal bei dieser Kommune einen Hinweis **„Datenstand: TT.MM.JJJJ“**. Alles Angezeigte ist dann korrekt, nur eben nicht neuer als dieses Datum.

Sobald die Quelle wieder erreichbar ist, holt mandari die Änderungen automatisch nach und der Hinweis verschwindet.

## Rücksicht auf die Quellen

Kommunale Server sind oft klein. mandari hält sich deshalb an einige Regeln: begrenzte Anfragerate, Respekt vor robots.txt, ein ehrlicher `User-Agent` mit Kontaktadresse und eine automatische Schonung, wenn eine Quelle wiederholt nicht antwortet. Details unter [Crawler und Opt-out](../datenschutz/crawler.md).

## Für Betreiber

Der Betriebsmonitor im Admin zeigt den Zustand jeder Quelle und des Dokument-Caches. Wie die Bewertung funktioniert und wann Alarme verschickt werden, steht unter [Betriebsmonitor](../betrieb/monitoring.md).
