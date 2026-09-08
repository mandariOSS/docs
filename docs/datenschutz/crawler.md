---
title: Crawler und Opt-out
description: Wie der mandari-Ingestor kommunale Ratsinformationssysteme abruft, welche Rücksicht er nimmt und wie Kommunen Drosselung, Pausierung oder Entfernung von Inhalten verlangen können.
---

# Crawler und Opt-out

mandari spiegelt öffentliche Ratsinformationen. Dafür ruft unser Ingestor die OParl-Schnittstellen und, wo es keine gibt, die Bürgerinfo-Seiten kommunaler Ratsinformationssysteme ab. Kommunale Server sind oft klein, deshalb gelten feste Regeln.

## So verhält sich der Ingestor

**Ehrlicher Absender.** Alle Anfragen tragen einen `User-Agent` mit Kontaktmöglichkeit, für Scraper-Quellen `mandari-ingestor (+https://mandari.de/crawler)`, für Dokumentabrufe `mandari-file-cache/1.0 (+https://mandari.de; support@mandari.de)`. Die Seite [mandari.de/crawler](https://mandari.de/crawler) erklärt, wer wir sind und wie man uns erreicht.

**Begrenzte Rate.** Scraper-Quellen stellen höchstens eine Anfrage je zwei Sekunden pro Host, immer nacheinander, nie parallel. Die Rate ist je Quelle konfigurierbar. OParl-Quellen werden inkrementell abgefragt (`modified_since`), Voll-Syncs laufen selten und nachts.

**robots.txt.** Wird vor jedem Crawl geprüft und mit 24 Stunden Cache respektiert. Ein Disallow für unseren User-Agent stoppt die Quelle, im Admin wird das markiert. Eine nicht abrufbare oder ungültige robots.txt gilt als erlaubt (RFC 9309).

**Keine Umgehung.** Keine Logins, keine Captchas, keine Session-Schranken. Nur öffentliche Bürgerinfo-Bereiche.

**Automatische Schonung.** Antwortet eine Quelle dreimal in Folge nicht, verdoppelt der Ingestor den Abstand zwischen den Versuchen (10, 20, 40 Minuten, höchstens 6 Stunden). Dokument-Cache und Vorschau-Proxy pausieren für diese Quelle ebenfalls. Nach dem ersten erfolgreichen Sync normalisiert sich alles wieder.

**Dokumente einmal.** Jede Datei wird einmal geladen und lokal gespeichert. Besucherinnen des Bürgerportals erzeugen keine Anfragen an den kommunalen Server.

## Drosseln oder pausieren

Kommunen, die den Abruf drosseln oder pausieren möchten, haben zwei Wege:

1. **robots.txt**: Ein Disallow für `mandari-ingestor` wirkt ab dem nächsten Zyklus, ohne dass wir etwas tun müssen.
2. **Kontakt**: Über die auf [mandari.de/crawler](https://mandari.de/crawler) genannten Adressen. Wir erhöhen den Anfrageabstand, verlegen Abrufe in ein Nachtfenster oder deaktivieren die Quelle.

## Inhalte entfernen (Takedown)

1. **Tombstone**: Betroffene Objekte werden zunächst als gelöscht markiert. Sie verschwinden sofort aus Portal, Suche und Schnittstellen. Die Daten bleiben für Prüfzwecke erhalten.
2. **Physische Löschung** auf ausdrückliche Aufforderung der Kommune, einschließlich Suchindex und lokaler Dateikopien:

    ```bash
    python manage.py purge_deleted --body <slug>            # Vorschau
    python manage.py purge_deleted --body <slug> --yes      # endgültig löschen
    ```

3. **Abwägung**: Opt-out-Wünsche werden geprüft, nicht blind ausgeführt. Amtliche Informationen haben ein Transparenzinteresse. Mindestens Drosselung oder Nachtfenster bieten wir immer an. Reaktionszeit: fünf Werktage.

## Für Betreiber eigener Installationen

Wer mandari selbst betreibt, übernimmt diese Verantwortung für die eigenen Quellen. Die Konfiguration der Politeness-Parameter steht unter [Quellen anbinden](../betrieb/quellen-anbinden.md) und in der [Konfigurationsreferenz](../betrieb/konfiguration.md#ingestor). Bitte passt den `SCRAPER_USER_AGENT` so an, dass er auf eure Kontaktmöglichkeit zeigt.
