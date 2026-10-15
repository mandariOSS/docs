---
title: Crawler und Opt-out
description: Wie mandari Ratsinformationssysteme abruft (Kennung, Takt, robots.txt, Dokumente, Abruf-Adresse) und wie Kommunen den Abruf drosseln, ausschließen oder Inhalte entfernen lassen können.
---

# Crawler und Opt-out

mandari spiegelt öffentliche Ratsinformationen. Dafür rufen zwei Programmteile die OParl-Schnittstellen und, wo es keine gibt, die HTML-Seiten kommunaler Ratsinformationssysteme ab: der Ingestor und die Anwendung selbst (Dokumente, Vorschau, Personenfotos). Kommunale Server sind oft klein, deshalb gelten für alle Abrufe dieselben festen Regeln. Diese Seite fasst sie zusammen und zeigt, wie Sie als Kommune den Abruf drosseln, ausschließen oder Inhalte entfernen lassen.

- Kurzfassung für IT-Verantwortliche: [mandari.de/crawler](https://mandari.de/crawler/)
- Technische Referenz mit Fundstellen im Code: [Abrufregeln (ABRUFREGELN.md)](https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md)

!!! info "Stand"
    Diese Seite beschreibt den Code auf dem Entwicklungszweig `dev` mit den Änderungen aus [mandari#1025](https://github.com/mandariOSS/mandari/issues/1025) und [mandari#1031](https://github.com/mandariOSS/mandari/pull/1031). Die von uns betriebene Instanz mandari.de folgt diesen Regeln ab dem ersten Update, das #1031 enthält; bis dahin läuft dort noch ein älterer Stand.

## Auf einen Blick

| Punkt | Regel |
|---|---|
| User-Agent | `mandari-ingestor/<Version> (+https://mandari.de/crawler/; support@mandari.de)` |
| Token für robots.txt | `mandari-ingestor` |
| Takt | höchstens eine Anfrage pro Sekunde je Server, über alle Abrufe von mandari zusammen; je Quelle nur langsamer |
| Gleichzeitig | höchstens zwei offene Anfragen je Server und Ingestor-Prozess |
| robots.txt | nach RFC 9309, für Schnittstelle, Seiten und Dokumente; 24 Stunden zwischengespeichert |
| Abgleich | alle 10 Minuten, gefragt wird nur nach Änderungen (`modified_since`) |
| Vollabgleich | einmal täglich nachts, je Quelle auch seltener oder nur in einem Zeitfenster |
| Dokumente | geladen, wenn sie fehlen oder die Quelle sie geändert hat; dazu Stichproben per `HEAD` |
| Abruf-Adresse | derzeit `144.76.153.200`, nur IPv4; sie kann sich ändern, erkennen Sie uns am User-Agent |
| Kontakt | [support@mandari.de](mailto:support@mandari.de) |

## Kennung

Unsere Abrufe bei Ratsinformationssystemen melden sich mit dem Produkt-Token `mandari-ingestor`, einem Verweis auf unsere Infoseite und unserer Kontaktadresse. Die beiden Ausnahmen stehen unter der Tabelle.

| Abruf | User-Agent |
|---|---|
| Ingestor: Abgleich, Scraper, Texterkennung, Sondierung | `mandari-ingestor/<Version> (+https://mandari.de/crawler/; support@mandari.de)` |
| Anwendung: Dokument-Cache, Vorschau, Löschabgleich, Personenfotos, Texterkennung, Quellenanlage | `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)` |

- Die Version ist die Paketversion des Ingestors (derzeit `0.1.0`) und wechselt mit jeder Ausgabe. Prüfen Sie deshalb auf den Anfang `mandari-ingestor`.
- Anfragen an die Schnittstelle senden `Accept: application/json`, Abrufe der robots.txt `Accept: text/plain`.
- **Abweichende Kennung je Quelle:** Für einzelne Quellen können wir eine andere Kennung einstellen, für Schnittstelle und Scraper wie für Dateien. Das ist für Ausnahmen gedacht, etwa wenn ein Server bestimmte Wörter im User-Agent filtert. Die robots.txt wird dann mit dieser Kennung abgerufen und ausgewertet; Regeln für `mandari-ingestor` gelten trotzdem.
- **Vergleichsanfrage nach HTTP 403:** Antwortet ein Server dem Abgleich mit 403, stellen wir je Server und Lauf einer Quelle genau eine Vergleichsanfrage mit der Standardkennung der HTTP-Bibliothek, `python-httpx/<Version>`. Sie geht im Takt an die Adresse, die 403 geliefert hat, und folgt keiner Weiterleitung. Nur eine erfolgreiche Antwort (2xx) werten wir als Sperre unseres User-Agents. Das dient allein der Diagnose: Abgerufen wird weiter nur mit unserer Kennung, und die Quelle wird geschont (siehe [Fehler und Schonung](#fehler-und-schonung)). Dieselbe Vergleichsanfrage stellt die Sondierung nach HTTP 403 auf die Startseite.

## Abruf-Adresse

Die von uns betriebene Instanz (mandari.de) ruft derzeit von der Adresse `144.76.153.200` ab, ausschließlich über IPv4. Erkennen Sie uns bitte vor allem am User-Agent: Die Adresse kann sich ändern, etwa bei einem Serverumzug.

mandari ist Open Source. Wer mandari selbst betreibt, ruft von der Adresse des eigenen Servers ab; für solche Installationen gilt die Adresse oben nicht.

## robots.txt

Ingestor und Anwendung werten die robots.txt nach RFC 9309 mit einem gemeinsamen Parser aus.

- **Gruppen:** Für uns gelten alle Gruppen, deren `User-agent` unserem Token entspricht, ohne Unterschied in der Groß- und Kleinschreibung. Gibt es keine, gelten die Gruppen für `*`; gibt es auch die nicht, ist alles erlaubt. Eine Gruppe für `mandari-ingestor` gilt also anstelle von `*`, nicht zusätzlich.
- **Regeln:** Die längste passende Regel entscheidet, bei gleicher Länge `Allow`. `*` steht für beliebig viele Zeichen, `$` verankert das Ende. Verglichen werden Pfad und Abfrage, Groß- und Kleinschreibung zählt.
- **Token:** Geprüft wird das Token der gesendeten Kennung und immer zusätzlich `mandari-ingestor`; beide müssen den Abruf erlauben. Gruppen für unsere früheren Kennungen `mandari-file-cache` und `mandari` gelten zusätzlich, aber nur, wenn es sie gibt, und sie können nur sperren.
- **Geltung:** für Schnittstelle, HTML-Seiten und Dateien, auch für das Ziel jeder Weiterleitung. `/robots.txt` selbst ist immer erlaubt.
- **Zwischenspeicher:** 24 Stunden je Server und Kennung. Änderungen an Ihrer robots.txt wirken also spätestens nach 24 Stunden. Ausgewertet werden höchstens 500 KiB.
- **Nicht vorhanden:** Ein 4xx-Status (auch 401, 403, 406) gilt als „keine robots.txt“, also ist alles erlaubt.
- **Nicht erreichbar:** 5xx, 408, 429, ein Netzfehler oder mehr als fünf Weiterleitungen. Gab es vorher eine gültige Fassung, gilt sie weiter, bis ein Abruf wieder gelingt. Gab es keine, fragen wir nichts an, sondern stellen den Abruf zurück und rufen die robots.txt frühestens nach 15 Minuten erneut ab. Eine nicht erreichbare robots.txt gilt also nie als Erlaubnis.
- **Gesperrt:** Wir stellen die Anfrage nicht. Lässt die robots.txt an einem Server keine einzige Anfrage einer Quelle zu, versucht der Abgleich es frühestens nach 24 Stunden wieder.
- **Nicht ausgewertet:** `Crawl-delay` und `Sitemap`. Für einen langsameren Takt schreiben Sie uns; wir stellen ihn dann für Ihre Quellen ein.
- **Ausnahmen** gibt es nur mit Freigabe der zuständigen Stelle und einem Vermerk in der Konfiguration der Quelle, für die Schnittstelle, für Dateien oder für beides. Ohne gültigen Vermerk gilt die robots.txt.

Beispiele:

```text
# mandari ganz ausschließen
User-agent: mandari-ingestor
Disallow: /

# Schnittstelle erlauben, Dokumente sperren
User-agent: mandari-ingestor
Disallow: /*.pdf$
```

Gibt es eine Gruppe für `mandari-ingestor`, gelten die Regeln unter `User-agent: *` für uns nicht mehr. Wiederholen Sie in unserer Gruppe, was auch für uns gelten soll.

## Takt

- **Eine Anfrage pro Sekunde je Server:** Vor jeder Anfrage reserviert ein Abruf einen Zeitpunkt für den Server, auch vor jeder Weiterleitung und vor dem Abruf einer robots.txt. Der Zeitstempel liegt in einem gemeinsamen Speicher (Redis) und gilt für Ingestor, Anwendung und Werkzeuge zusammen. Liegen mehrere Kommunen auf demselben Server, teilen sie sich diesen Takt.
- **Server** heißt hier: der Hostname, ohne Port und ohne Unterschied in der Schreibweise. `https://RIS.example.de:443/` und `http://ris.example.de/` teilen sich einen Takt; verschiedene Hostnamen zählen getrennt, auch wenn sie auf demselben Rechner liegen.
- **Je Quelle nur langsamer:** Für eine Quelle lässt sich ein größerer Abstand von bis zu 30 Sekunden einstellen. Kleinere Werte als eine Sekunde gelten als eine Sekunde. Scraper-Quellen (Systeme ohne OParl-Schnittstelle) fragen standardmäßig alle 2 Sekunden an, nie schneller als einmal je Sekunde, und streng nacheinander.
- **Gleichzeitig:** Der Ingestor hält je Server und Prozess höchstens zwei Anfragen gleichzeitig offen, im Abgleich wie in der Texterkennung.
- **Vorschau:** Öffnet jemand bei uns ein Dokument, das wir noch nicht abgelegt haben, wartet die Anwendung höchstens 5 Sekunden auf robots.txt und einen freien Zeitpunkt, Weiterleitungen eingeschlossen. Sonst bittet sie mit HTTP 503 um einen neuen Versuch, statt den Takt zu überziehen. Zusätzlich gilt: höchstens 4 solche Abrufe gleichzeitig je Prozess und 20 je Besucher-Adresse und Minute.
- **Löschabgleich:** zusätzlich mindestens 2 Sekunden zwischen zwei Prüfungen an demselben Server innerhalb eines Laufs.
- **Ohne Redis:** Ist der gemeinsame Speicher nicht erreichbar, drosselt jeder Prozess für sich und versucht es nach 60 Sekunden wieder mit Redis. In dieser Zeit können mehrere Prozesse zusammen schneller abrufen als eine Anfrage pro Sekunde.

## Weiterleitungen

Weiterleitungen folgen wir höchstens fünfmal je Abruf. Vor jeder Weiterleitung prüfen wir:

1. in der Anwendung, ob das Ziel eine öffentliche Adresse ist (außer beim Anlegen einer Quelle),
2. die robots.txt des Ziel-Servers, mit derselben Kennung wie die erste Anfrage,
3. einen eigenen Zeitpunkt im Takt des Ziel-Servers.

Sperrt die robots.txt das Ziel, folgen wir nicht. Ist sie nicht erreichbar, stellen wir den Abruf zurück. Mehr als fünf Weiterleitungen beenden den Abruf mit einem Fehler.

## Wann wir abrufen

### Abgleich

- Der Ingestor gleicht alle 10 Minuten ab und fragt jede Liste nur nach Änderungen (OParl-Filter `modified_since`). Ohne Änderungen kostet das bei einer Quelle, die den Filter auswertet, eine Seite je Liste.
- **Änderungsfenster:** Gefragt wird nach Änderungen seit dem Beginn des letzten vollständigen Abgleichs der Kommune, mit zwei Stunden Sicherheitsabstand, höchstens aber der letzten sieben Tage. Listen, deren Änderungsdatum keine Uhrzeit trägt, fragen wir ab Tagesbeginn an.
- **Ohne Filter:** Lehnt ein System den Filter ab oder ignoriert ihn, lesen wir die Liste von vorn, vergleichen selbst und hören nach fünf Seiten ohne Änderung auf. Nach jedem Vollabgleich prüfen wir mit einer Anfrage, ob Ihr System nach Änderungsdatum filtert; bringt sie keine Aussage, wiederholen wir sie einmal nach 60 Sekunden.
- **Fehlende Listen:** Optionale Listen (Mitgliedschaften, Tagesordnungspunkte, Beratungen, Dateien, Orte), die Ihr System nicht anbietet, vermerken wir. Der Abgleich fragt sie dann höchstens einmal am Tag wieder an, der Vollabgleich jedes Mal.

Wertet Ihre Schnittstelle `modified_since` aus, bleibt unsere Last am kleinsten.

### Vollabgleich

- Einmal täglich zu einer festen Stunde liest der Ingestor alle Listen vollständig, als Sicherheitsnetz für Änderungen, die ein Filter nicht meldet. Standard ist 03:00 Uhr Ortszeit; die von uns betriebene Instanz startet ihn um 01:00 Uhr. Läuft zu dieser Stunde noch ein Abgleich, folgt der Vollabgleich direkt danach.
- Je Quelle lässt er sich seltener ausführen (Mindestabstand in Tagen) oder auf ein Zeitfenster begrenzen, auch über Mitternacht. Außerhalb des Fensters läuft nur der Änderungsabgleich. Das Fenster muss die Startstunde enthalten und für einen ganzen Vollabgleich reichen: Nach dem Ende des Fensters holt der Ingestor keine weitere Seite, und offene Listen kommen beim nächsten Vollabgleich wieder dran.

### Vor der Aufnahme eines Systems

- **Sondierung:** Ob ein System für uns infrage kommt, prüfen wir mit höchstens fünf Anfragen je Kommune: robots.txt, Startseite und die üblichen Adressen einer OParl-Schnittstelle. Weiterleitungen und die robots.txt eines weiteren Servers zählen mit. Gesperrte Pfade fragen wir nicht an; ist die robots.txt nicht erreichbar, endet die Prüfung nach dieser einen Anfrage. Zwischen zwei Kommunen liegen zusätzlich 2 Sekunden Pause.
- **Quellenanlage:** Beim Anlegen einer Quelle rufen wir nach Prüfung der robots.txt System und Kommunenliste ab, im selben Takt.

## Dokumente

Dateien (Vorlagen, Anlagen, Niederschriften, fast immer PDF) laden wir unter den Regeln oben: robots.txt, Takt je Server, Weiterleitungen. Für einzelne Quellen schalten wir den Dateiabruf ganz ab, etwa wenn Sie das wünschen; die Vorschau verweist dann auf das Original.

- **Texterkennung:** Jede neu erfasste Datei, deren Text fehlt, lädt der Ingestor einmal, je Kommune und Lauf höchstens 500 Dateien, bis 50 MB je Datei.
- **Dokument-Cache:** stündlich höchstens 400 Dateien, je Quelle höchstens 200, bis 80 MB je Datei. Nach Zeitüberschreitung, Verbindungsfehler, 429, 5xx oder nicht erreichbarer robots.txt versuchen wir es nach 15 Minuten, 1, 6, 24 und 72 Stunden erneut; danach gilt die Datei als Fehler und wird nach sieben Tagen noch einmal versucht. HTTP 404 oder 410 gilt in den ersten sieben Tagen nach unserer Erfassung als vorläufig, weil Quellen das Objekt oft vor der Datei veröffentlichen.
- **Vorschau:** Öffnet jemand bei uns ein Dokument, das wir nicht abgelegt haben, laden wir es bei der Quelle, mit den Grenzen unter [Takt](#takt). Bei Kommunen, deren Dokumente wir ablegen, legen wir es dabei ab; bei den übrigen fragt jedes Öffnen bei der Quelle an.
- **Löschabgleich:** stündlich. Dokumente, die die Quelle geändert hat, laden wir neu (höchstens 200 je Lauf). Dazu kommen Stichproben per `HEAD`, nur bei öffentlich gelisteten Kommunen und höchstens 30 je Kommune und Lauf. Dokumente, die mit 404 oder 410 verschwunden sind, prüfen wir bei öffentlich gelisteten Kommunen nach 1, 7 und 25 Tagen erneut; nach 30 Tagen fragen wir ein letztes Mal per `GET` an und löschen dann Kopie und Text. Nach HTTP 429 oder 503 oder nach fünf Fehlern in Folge fragt der Lauf diesen Server nicht weiter an. Melden in einem Lauf mehr als 10 Dokumente einer Quelle neu 404 oder 410, lässt er die Quelle für diesen Lauf ruhen. Was Sie löschen, verschwindet so auch bei uns.
- **Gesperrt per robots.txt oder Bot-Schutz** (eine HTML-Seite statt der Datei): Diese Datei laden wir erst nach einer Freigabe wieder. Zugangsprüfungen umgehen wir nicht.

## Personenfotos

- Montags um 03:00 Uhr, nur für Kommunen, bei denen wir ein Muster für Fotoadressen hinterlegt haben.
- Höchstens 500 Personen je Kommune und Lauf. Geladen werden Fotos, die noch nie geprüft wurden oder deren letzte Prüfung mehr als 30 Tage zurückliegt. Zwischen zwei Fotos liegen 0,1 Sekunden Pause, dazu gilt der Takt je Server.
- Ein fehlendes Foto oder ein Fehler wird vermerkt und frühestens nach 30 Tagen wieder angefragt. Ist die robots.txt nicht erreichbar, wird nichts vermerkt; der nächste Lauf versucht es erneut.
- Ist die Quelle abgeschaltet, der Dateiabruf aus oder wird die Quelle gerade geschont, laden wir keine Fotos und vermerken nichts.

## Fehler und Schonung

- **Wiederholungen:** Nach Netzfehler, Zeitüberschreitung oder 5xx höchstens 3 Versuche, mit Pausen von 1 und 2 Sekunden, jeder Versuch im Takt. HTTP 403, 404, 429 und andere 4xx wiederholen wir nicht.
- **Schutzschalter:** Nach 5 Fehlversuchen an einen Server im Lauf einer Quelle stellen wir 60 Sekunden lang keine Anfragen an diesen Server. HTTP 404 zählt dabei nicht.
- **Gestörte Quelle:** 5 Serverfehler in Folge an einen Server gelten als Störung (5xx-Serie).
- **Pausen:** Ab dem dritten fehlgeschlagenen Lauf einer Quelle in Folge pausiert der Abgleich 10 Minuten, danach je weiterem Fehlversuch doppelt so lang, höchstens 6 Stunden (10, 20, 40 … 360 Minuten). Bei drei Befunden pausiert er schon beim ersten Mal, und zwar mindestens 60 Minuten, wenn ein Server unseren User-Agent sperrt, 30 Minuten bei einer 5xx-Serie oder nicht erreichbarer robots.txt und 24 Stunden, wenn die robots.txt keine Anfrage zulässt. Ist die Pause aus der Reihe länger, gilt sie.
- **Anwendung:** Dokument-Cache, Vorschau, Löschabgleich und Personenfotos ruhen für eine Quelle ab drei fehlgeschlagenen Läufen des Abgleichs in Folge, bis ein Lauf sie wieder erreicht. Eine Sperre per robots.txt beachten sie unabhängig davon bei jedem Abruf. Ein getrennt betriebener Worker für die Texterkennung richtet sich nur nach dem Dateiabruf der Quelle und der robots.txt, nicht nach der Schonung.
- Einen `Retry-After`-Header werten wir nicht aus. Eine Sperre unseres User-Agents umgehen wir nicht; wir versuchen es nur in den genannten Abständen wieder.

## Drosseln oder ausschließen

Kommunen, die den Abruf drosseln oder ausschließen möchten, haben zwei Wege:

1. **robots.txt:** Eine Gruppe für `mandari-ingestor` wirkt spätestens nach 24 Stunden, ohne dass wir etwas tun müssen, ganz oder nur für Dokumente (siehe [Beispiele](#robotstxt)).
2. **Kontakt:** Schreiben Sie an [support@mandari.de](mailto:support@mandari.de). Wir können für Ihre Quelle den Abstand je Anfrage erhöhen (bis 30 Sekunden), den Vollabgleich in ein Zeitfenster legen, ihn seltener ausführen oder den Dateiabruf abschalten. Liegen mehrere Quellen auf Ihrem Server, stellen wir das bei allen ein.

## Inhalte entfernen (Takedown)

1. **Tombstone**: Betroffene Objekte werden zunächst als gelöscht markiert. Sie verschwinden sofort aus Portal, Suche und Schnittstellen. Die Daten bleiben für Prüfzwecke erhalten.
2. **Physische Löschung** auf ausdrückliche Aufforderung der Kommune, einschließlich Suchindex und lokaler Dateikopien:

    ```bash
    python manage.py purge_deleted --body <slug>            # Vorschau
    python manage.py purge_deleted --body <slug> --yes      # endgültig löschen
    ```

3. **Abwägung**: Opt-out-Wünsche werden geprüft, nicht blind ausgeführt. Amtliche Informationen haben ein Transparenzinteresse. Mindestens Drosselung oder Nachtfenster bieten wir immer an. Reaktionszeit: fünf Werktage.

## Andere Abrufe

Diese Abrufe gehen nicht an Ratsinformationssysteme und folgen nicht den Regeln dieser Seite:

- Live-Übertragung von Sitzungen bei Streaming-Anbietern, mit der Kennung `mandari (+https://mandari.de)`.
- Geodienste für die Umringe von Bebauungsplänen, mit der Kennung `Mandari/1.0 (https://mandari.de; support@mandari.de)` und einer Sekunde Pause zwischen zwei Seiten.
- OpenStreetMap, Overpass und Photon für Karten, Orte und Adresssuche.

## Für Betreiber eigener Installationen

Wer mandari selbst betreibt, ruft von der Adresse des eigenen Servers ab und übernimmt die Verantwortung gegenüber den Betreibern der eigenen Quellen.

- Setzen Sie `INGESTOR_USER_AGENT` (älterer Name: `SCRAPER_USER_AGENT`) auf eine Kennung mit Ihrer Kontaktadresse, etwa `mandari-ingestor/0.1.0 (+https://ris.example.de/abruf/; it@example.de)`. Die Variable gehört in die Umgebung des Ingestors und, weil die Sync-Aktionen im Admin im Worker der Anwendung laufen, auch in die Umgebung der Anwendung; ein Eintrag nur in der `.env` wirkt unter Docker Compose nicht. Regeln der robots.txt für `mandari-ingestor` gelten weiter, weil mandari dieses Token immer zusätzlich prüft.
- Die Abrufe der Anwendung (Dokument-Cache, Vorschau, Löschabgleich, Personenfotos, Quellenanlage) melden sich mit der festen Kennung `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)`. Abweichend lässt sie sich nur je Quelle über `sync_config["download_headers"]` setzen (nicht für die Quellenanlage).
- Den gemeinsamen Takt über alle Prozesse gibt es nur mit Redis, das Ingestor und Anwendung beide erreichen. `INGESTOR_REQUEST_INTERVAL` und `RIS_REQUEST_INTERVAL` (Standard je `1.0`) legen den Abstand je Server fest; `0` schaltet die Drossel ab und ist nur für Tests und Notfälle gedacht.

Alle Einstellungen je Quelle und per Umgebungsvariable stehen in den [Abrufregeln](https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md). Wie Sie Quellen anbinden, steht unter [Quellen anbinden](../betrieb/quellen-anbinden.md), weitere Variablen in der [Konfigurationsreferenz](../betrieb/konfiguration.md#ingestor).
