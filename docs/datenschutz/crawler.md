---
title: Crawler und Opt-out
description: Wie mandari Ratsinformationssysteme abruft (Kennung, Takt, robots.txt, Dokumente, Abruf-Adresse) und wie Kommunen den Abruf drosseln, ausschließen oder Inhalte entfernen lassen können.
---

# Crawler und Opt-out

mandari spiegelt öffentliche Ratsinformationen. Dafür rufen zwei Programmteile die OParl-Schnittstellen und, wo es keine gibt, die HTML-Seiten kommunaler Ratsinformationssysteme ab: der Ingestor und die Anwendung selbst (Dokumente, Vorschau, Personenfotos). Kommunale Server sind oft klein, deshalb gelten für alle Abrufe dieselben festen Regeln. Diese Seite fasst sie zusammen und zeigt, wie Sie als Kommune den Abruf [drosseln oder ausschließen](#drosseln-oder-ausschlieen) oder [Inhalte entfernen lassen](#inhalte-entfernen-takedown).

- Kurzfassung für IT-Verantwortliche: [mandari.de/crawler](https://mandari.de/crawler/)
- Technische Referenz mit Fundstellen im Code: [Abrufregeln (ABRUFREGELN.md)](https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md)

!!! info "Stand"
    Diese Seite beschreibt den Code auf dem Entwicklungszweig `dev` nach den Änderungen für [mandari#1027](https://github.com/mandariOSS/mandari/issues/1027). Auf der von uns betriebenen Instanz mandari.de gelten davon heute schon die Kennung `mandari-ingestor` bei Ratsinformationssystemen, höchstens eine Anfrage pro Sekunde je Server und das Änderungsfenster. Eine Gruppe für `mandari-ingestor` in der robots.txt beachten dort Abgleich, Texterkennung, Dokument-Cache, Vorschau und Personenfotos. Für den stündlichen Löschabgleich gilt sie erst mit dem nächsten Update; bis dahin richtet sich der Löschabgleich dort nach einer Gruppe für unsere früheren Kennungen `mandari-file-cache` oder `mandari`, sonst nach `*`. Ebenfalls erst mit dem nächsten Update folgen: die Prüfung jeder Weiterleitung (robots.txt und Takt des Ziels), der Takt je Quelle nach Bedarf, der Vollabgleich in Zeitscheiben, die langsamen Listen sowie Kennung und Takt der [anderen Abrufe](#andere-abrufe).

## Auf einen Blick

| Punkt | Regel |
|---|---|
| User-Agent | `mandari-ingestor/<Version> (+https://mandari.de/crawler/; support@mandari.de)` |
| Token für robots.txt | `mandari-ingestor` |
| Takt | höchstens eine Anfrage pro Sekunde je Server, über alle Abrufe von mandari zusammen; je Quelle nur langsamer |
| Gleichzeitig | höchstens zwei offene Anfragen je Server und Ingestor-Prozess, auch am Ziel einer Weiterleitung |
| robots.txt | nach RFC 9309, für Schnittstelle, Seiten und Dokumente; je Hostname 24 Stunden zwischengespeichert |
| Abgleich | je Quelle nach Bedarf: werktags 7–19 Uhr alle 10 Minuten, sonst stündlich, am Wochenende alle 2 Stunden, an Sitzungstagen und am Vortag (7–22 Uhr) alle 5 Minuten; nach Abgleichen ohne Änderung seltener, an Sitzungstagen bis alle 10 Minuten, sonst bis alle 2 Stunden; gefragt wird nur nach Änderungen (`modified_since`) |
| Vollabgleich | geplant höchstens einmal je Nacht im Zeitfenster der Quelle (bei mandari.de ohne eigenes Fenster: Beginn zwischen 1 und 6 Uhr), je Quelle auch seltener; bei Servern, deren vollständige Listen abbrechen, nur in Zeitscheiben (`modified_since` und `modified_until`); von Hand nur ausnahmsweise, etwa nach der Aufnahme eines neuen Systems; ein eigenes Zeitfenster und der Mindestabstand der Quelle gelten auch dann, ohne eigenes Fenster kann er auch tagsüber laufen (siehe [Vollabgleich](#vollabgleich)) |
| Langsame Listen | eine optionale Liste, die in eine Zeitüberschreitung läuft, ruht 1 Stunde, danach jeweils doppelt so lange, höchstens 24 Stunden |
| Neue Quellen | von unseren Werkzeugen inaktiv angelegt; regelmäßig abgefragt wird eine Quelle erst, wenn sie aktiv ist; neu entdeckte Kommunen bleiben ungelistet (siehe [Neue Quellen und Kommunen](#neue-quellen-und-kommunen)) |
| Dokumente | geladen, wenn sie fehlen oder die Quelle sie geändert hat; dazu Stichproben per `HEAD` |
| Abruf-Adresse | derzeit `144.76.153.200`, nur IPv4; sie kann sich ändern, erkennen Sie uns am User-Agent |
| Andere Dienste | Live-Übertragung und Geodienste mit derselben Kennung und eigenem Takt je Server, ohne robots.txt (siehe [Andere Abrufe](#andere-abrufe)) |
| Kontakt | [support@mandari.de](mailto:support@mandari.de) |

## Drosseln oder ausschließen

Kommunen, die den Abruf drosseln oder ausschließen möchten, haben zwei Wege:

1. **robots.txt:** Eine Gruppe für `mandari-ingestor` wirkt spätestens nach 24 Stunden, ohne dass wir etwas tun müssen, ganz oder nur für Dokumente (siehe [Beispiele](#robotstxt)). Auf mandari.de beachtet der stündliche Löschabgleich eine solche Gruppe erst mit dem nächsten Update (siehe Hinweis „Stand“ oben). Schreiben Sie uns bis dahin bitte zusätzlich; dann schalten wir den Dateiabruf für Ihre Quelle ab.
2. **Kontakt:** Schreiben Sie an [support@mandari.de](mailto:support@mandari.de). Wir können für Ihre Quelle den Abstand je Anfrage erhöhen (bis 30 Sekunden), seltener abgleichen, den Vollabgleich in ein Zeitfenster legen, ihn seltener oder nur in Zeitscheiben ausführen, den Dateiabruf abschalten oder Ihr System gar nicht mehr abrufen. Ein Zeitfenster gilt nur für den Vollabgleich; Änderungsabgleich und Dokumentabrufe laufen weiter im Takt. Liegen mehrere Quellen auf Ihrem Server, stellen wir das bei allen ein.

## Inhalte entfernen (Takedown)

1. **Tombstone**: Betroffene Objekte werden zunächst als gelöscht markiert. Sie verschwinden sofort aus Portal, Suche und Schnittstellen. Die Daten bleiben für Prüfzwecke erhalten.
2. **Physische Löschung** auf ausdrückliche Aufforderung der Kommune, einschließlich Suchindex und lokaler Dateikopien:

    ```bash
    python manage.py purge_deleted --body <slug>            # Vorschau
    python manage.py purge_deleted --body <slug> --yes      # endgültig löschen
    ```

3. **Abwägung**: Opt-out-Wünsche werden geprüft, nicht blind ausgeführt. Amtliche Informationen haben ein Transparenzinteresse. Mindestens einen langsameren Takt und ein Zeitfenster für den Vollabgleich bieten wir immer an. Reaktionszeit: fünf Werktage.

## Kennung

Unsere Abrufe bei Ratsinformationssystemen melden sich mit dem Produkt-Token `mandari-ingestor`, einem Verweis auf unsere Infoseite und unserer Kontaktadresse. Die beiden Ausnahmen stehen unter der Tabelle. Dieselbe Kennung tragen auch unsere Abrufe bei Streaming-Anbietern und Geodiensten (siehe [Andere Abrufe](#andere-abrufe)).

| Abruf | User-Agent |
|---|---|
| Ingestor: Abgleich, Scraper, Texterkennung, Sondierung | `mandari-ingestor/<Version> (+https://mandari.de/crawler/; support@mandari.de)` |
| Anwendung: Dokument-Cache, Vorschau, Löschabgleich, Personenfotos, Texterkennung, Quellenanlage | `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)` |
| Anwendung: Live-Übertragung und Geodienste ([Andere Abrufe](#andere-abrufe)) | `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)` |

- Die Version ist die Paketversion des Ingestors (derzeit `0.1.0`) und kann sich ändern. Prüfen Sie deshalb auf den Anfang `mandari-ingestor`.
- Anfragen an die Schnittstelle senden `Accept: application/json`, Abrufe der robots.txt `Accept: text/plain`.
- **Abweichende Kennung je Quelle:** Für einzelne Quellen können wir eine andere Kennung einstellen, für Schnittstelle und Scraper wie für Dateien. Das ist für Ausnahmen gedacht, etwa wenn ein Server bestimmte Wörter im User-Agent filtert. Die robots.txt wird dann mit dieser Kennung abgerufen und ausgewertet; Regeln für `mandari-ingestor` gelten trotzdem.
- **Vergleichsanfrage nach HTTP 403:** Antwortet ein Server dem Abgleich mit 403, stellen wir je Server und Lauf einer Quelle genau eine Vergleichsanfrage mit der Standardkennung der HTTP-Bibliothek, `python-httpx/<Version>`. Sie geht im Takt und innerhalb der Grenze gleichzeitiger Anfragen an die Adresse, die 403 geliefert hat, und folgt keiner Weiterleitung. Nur eine erfolgreiche Antwort (2xx) werten wir als Sperre unseres User-Agents; eine Weiterleitung oder eine ausbleibende Antwort lässt das offen. Das dient allein der Diagnose: Abgerufen wird weiter nur mit unserer Kennung, und die Quelle wird geschont (siehe [Fehler und Schonung](#fehler-und-schonung)). Dieselbe Vergleichsanfrage stellt die Sondierung nach HTTP 403 auf die Startseite.

## Abruf-Adresse

Die von uns betriebene Instanz (mandari.de) ruft derzeit von der Adresse `144.76.153.200` ab, ausschließlich über IPv4. Erkennen Sie uns bitte vor allem am User-Agent: Die Adresse kann sich ändern, etwa bei einem Serverumzug.

mandari ist Open Source. Wer mandari selbst betreibt, ruft von der Adresse des eigenen Servers ab; für solche Installationen gilt die Adresse oben nicht.

## robots.txt

Ingestor und Anwendung werten die robots.txt nach RFC 9309 mit einem gemeinsamen Parser aus.

- **Gruppen:** Für uns gelten alle Gruppen, deren `User-agent` unserem Token entspricht, ohne Unterschied in der Groß- und Kleinschreibung. Gibt es keine, gelten die Gruppen für `*`; gibt es auch die nicht, ist alles erlaubt. Eine Gruppe für `mandari-ingestor` gilt also anstelle von `*`, nicht zusätzlich.
- **Regeln:** Die längste passende Regel entscheidet, bei gleicher Länge `Allow`. `*` steht für beliebig viele Zeichen, `$` verankert das Ende. Verglichen werden Pfad und Abfrage, Groß- und Kleinschreibung zählt.
- **Token:** Geprüft wird das Token der gesendeten Kennung und immer zusätzlich `mandari-ingestor`; beide müssen den Abruf erlauben. Gruppen für unsere früheren Kennungen `mandari-file-cache` und `mandari` gelten zusätzlich, aber nur, wenn es sie gibt, und sie können nur sperren.
- **Geltung:** für Schnittstelle, HTML-Seiten und Dateien, auch für das Ziel jeder Weiterleitung. `/robots.txt` selbst ist immer erlaubt.
- **Zwischenspeicher:** 24 Stunden je Hostname und Kennung. Schema, Port und Schreibweise ergeben keinen eigenen Eintrag: `https://RIS.example.de:443/`, `http://ris.example.de/` und `https://ris.example.de:8443/` teilen sich eine robots.txt, so wie sie sich den [Takt](#takt) teilen. Geladen wird sie mit Schema und Port der ersten Anfrage, die sie braucht. Änderungen an Ihrer robots.txt wirken spätestens nach 24 Stunden. Ausgewertet werden höchstens 500 KiB.
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
- **Gleichzeitig:** Der Ingestor hält je Server und Prozess höchstens zwei Anfragen gleichzeitig offen, für Abgleich, Scraper, Texterkennung und Vergleichsanfrage zusammen. Folgt ein Abruf einer Weiterleitung auf einen anderen Server, zieht sein Platz vorher dorthin mit; am Ziel gelten Takt und Grenze ebenso.
- **Vorschau:** Öffnet jemand bei uns ein Dokument, das wir noch nicht abgelegt haben, wartet die Anwendung insgesamt höchstens 5 Sekunden auf einen freien Abrufplatz, die robots.txt und einen freien Zeitpunkt, Weiterleitungen eingeschlossen. Sonst bittet sie mit HTTP 503 um einen neuen Versuch, statt den Takt zu überziehen. Zusätzlich gilt: höchstens 4 solche Abrufe gleichzeitig je Prozess und 20 je Besucher-Adresse und Minute.
- **Löschabgleich:** zusätzlich mindestens 2 Sekunden zwischen zwei Prüfungen an demselben Server innerhalb eines Laufs; die Nachprüfung per `GET` nach einer `HEAD`-Stichprobe ohne klare Antwort läuft nur im gemeinsamen Takt.
- **Ohne Redis:** Ist der gemeinsame Speicher nicht erreichbar, drosselt jeder Prozess für sich und versucht es nach 60 Sekunden wieder mit Redis. In dieser Zeit können mehrere Prozesse zusammen schneller abrufen als eine Anfrage pro Sekunde.

## Weiterleitungen

Weiterleitungen folgen wir höchstens fünfmal je Abruf. Vor jeder Weiterleitung prüfen wir:

1. in der Anwendung, ob das Ziel eine öffentliche Adresse ist (außer beim Anlegen einer Quelle),
2. die robots.txt des Ziel-Servers, mit derselben Kennung wie die erste Anfrage,
3. einen eigenen Zeitpunkt im Takt des Ziel-Servers.

Sperrt die robots.txt das Ziel, folgen wir nicht. Ist sie nicht erreichbar, stellen wir den Abruf zurück. Mehr als fünf Weiterleitungen beenden den Abruf mit einem Fehler.

## Wann wir abrufen

### Abgleich

Einen gemeinsamen Durchlauf über alle Quellen gibt es nicht mehr. Jede Quelle hat ihren eigenen Takt nach Bedarf, in Ortszeit (`Europe/Berlin`):

| Wann | Abstand zwischen zwei Abgleichen einer Quelle |
|---|---|
| Tag einer Sitzung und Tag davor, 7–22 Uhr | 5 Minuten, ohne Änderung höchstens 10 |
| werktags 7–19 Uhr | 10 Minuten |
| werktags außerhalb dieser Zeit | 60 Minuten |
| Samstag und Sonntag | 120 Minuten |

- **Sitzungstage:** Als Sitzungstag zählt ein Tag, an dem laut unserem Bestand eine Sitzung einer Kommune der Quelle beginnt; abgesagte und von der Quelle gelöschte Sitzungen zählen nicht. Diese Regel gilt auch am Wochenende. Feiertage behandelt der Takt wie Werktage.
- **Ruhe:** Nach je drei Abgleichen in Folge ohne Änderung verdoppelt sich der Abstand, höchstens bis 2 Stunden, an Sitzungstagen und am Vortag bis 10 Minuten. Werktags tagsüber sind es also 10, nach drei ruhigen Abgleichen 20, dann 40, 80 und höchstens 120 Minuten. Ein Abgleich mit Änderung setzt den Abstand auf den Takt der Tageszeit zurück, ebenso der Wechsel in einen anderen Takt, etwa um 7 Uhr.
- **Nächster Abgleich:** Der Abstand zählt ab dem Ende des vorigen Abgleichs. Beginnt vorher ein kürzerer Takt, ist der Abgleich zu dessen Beginn fällig, etwa um 7 Uhr statt um 7:30 Uhr. Je Quelle läuft höchstens ein Abgleich zugleich; der Ingestor gleicht standardmäßig höchstens vier Quellen gleichzeitig ab. Der Takt je Server gilt unabhängig davon.
- **Wenig Last ohne Änderungen:** Ändert sich nichts und steht keine Sitzung an, sind das je Quelle am Wochenende 12 Abgleiche am Tag, werktags von 19 bis 7 Uhr 7 und von 7 bis 19 Uhr 14, in einer Woche 131 statt 1008 im früheren Takt von 10 Minuten.
- **Schonung geht vor:** Eine Quelle in Schonung (siehe [Fehler und Schonung](#fehler-und-schonung)) gleicht der Ingestor nicht ab, auch nicht, wenn wir einen Abgleich im Admin anfordern. Nur ohne laufenden Ingestor, bei einer abgeschalteten Quelle oder wenn die Anforderung den Ingestor nicht erreicht, läuft ein angeforderter Abgleich in der Anwendung; er hält robots.txt, Takt je Server sowie Zeitfenster und Mindestabstand des Vollabgleichs ein, aber nicht die Schonung. Scraper-Quellen gleicht nur der Ingestor ab.
- **Je Quelle:** Für einzelne Quellen stellen wir den Takt auf Wunsch langsamer ein, für jede Tageszeit getrennt. In einer eigenen Installation setzt `INGESTOR_INTERVAL` den Takt werktags 7–19 Uhr (siehe [Konfiguration](../betrieb/konfiguration.md#ingestor)).
- Gefragt wird jede Liste nur nach Änderungen (OParl-Filter `modified_since`). Ohne Änderungen kostet das bei einer Quelle, die den Filter auswertet, eine Seite je Liste. Die Kommunenliste lesen wir über alle Seiten (`links.next`), höchstens 20.
- **Änderungsfenster:** Gefragt wird nach Änderungen seit dem Beginn des letzten vollständigen Abgleichs der Kommune, mit zwei Stunden Sicherheitsabstand, höchstens aber der letzten sieben Tage. Dieses kurze Fenster bekommen nur Listen, deren Änderungsdatum nachweislich eine Uhrzeit trägt; die übrigen, auch neue Listen und Listen ohne bisher gesehene Änderung, fragen wir ab Tagesbeginn an.
- **Ohne Filter:** Lehnt ein System den Filter ab oder ignoriert ihn, lesen wir die Liste von vorn, vergleichen selbst und hören nach fünf Seiten ohne Änderung auf. Nach jedem Vollabgleich prüfen wir mit einer Anfrage, ob Ihr System nach Änderungsdatum filtert; bringt sie keine Aussage, wiederholen wir sie einmal nach 60 Sekunden.
- **Fehlende Listen:** Optionale Listen (Mitgliedschaften, Tagesordnungspunkte, Beratungen, Dateien, Orte), die Ihr System nicht anbietet, vermerken wir. Der Abgleich fragt sie dann höchstens einmal am Tag wieder an, der Vollabgleich jedes Mal, der Vollabgleich in Zeitscheiben nicht. Meldet ein SD.NET-System auf diese Prüfung nur „keine Treffer“, bleibt der Vermerk, und die nächste Prüfung folgt nach einem Tag.
- **Langsame Listen:** Bricht eine optionale Liste ab, weil die letzte Anfrage nach 60 Sekunden ohne Antwort blieb oder mit HTTP 504 endete, fragen wir diese Liste zunächst 1 Stunde nicht an, nach jeder weiteren Zeitüberschreitung in Folge doppelt so lange: 1, 2, 4, 8, 16, höchstens 24 Stunden. Auch der Vollabgleich lässt sie so lange aus; er zählt dann nicht als vollständig. Andere Fehler setzen keine Liste aus. Die übrigen Listen gleichen wir weiter ab. Danach holen wir die Änderungen der Liste nach, bei Systemen, die nach Änderungsdatum filtern, in Abschnitten zu einem Tag (`modified_since` und `modified_until`), sonst ohne Abschnitte wie jede andere Liste. Pflichtlisten (Gremien, Personen, Sitzungen, Vorlagen) setzen wir nie aus.

Wertet Ihre Schnittstelle `modified_since` aus, bleibt unsere Last am kleinsten.

### Vollabgleich

- **Wann:** Höchstens einmal je Zeitfenster liest der Ingestor alle Listen einer Quelle vollständig, als Sicherheitsnetz für Änderungen, die ein Filter nicht meldet. Ohne eigenes Zeitfenster der Quelle beginnt er im Standardfenster: ab der Stunde `INGESTOR_FULL_SYNC_HOUR` (Standard 03:00 Uhr Ortszeit) für 5 Stunden; die von uns betriebene Instanz beginnt um 01:00 Uhr, ihr Standardfenster reicht also bis 06:00 Uhr. Läuft zu Beginn noch ein Änderungsabgleich der Quelle, folgt der Vollabgleich direkt danach. Während er läuft, ruhen nur die Änderungsabgleiche derselben Quelle; die anderen Quellen gleichen weiter in ihrem Takt ab.
- **Einmal je Nacht:** Bricht ein Vollabgleich ab oder bleibt er unvollständig, wiederholen wir ihn erst im nächsten Fenster, auch nach einem Neustart nicht in derselben Nacht. Vollabgleiche belegen höchstens alle Plätze des Ingestors bis auf einen, standardmäßig also drei; ist keiner frei, wartet der Vollabgleich, solange das Fenster offen ist, und die Quelle wird derweil in ihrem Takt abgeglichen. Unter den geplanten Vollabgleichen bekommt einen frei werdenden Platz zuerst die Quelle, deren letzter Vollabgleich am längsten zurückliegt.
- **Je Quelle:** Er lässt sich seltener ausführen (Mindestabstand in Tagen) und in ein eigenes Zeitfenster legen, auch über Mitternacht. Der Vollabgleich beginnt dann in diesem Fenster, unabhängig von der Stunde des Standardfensters; außerhalb läuft nur der Änderungsabgleich. Nach dem Ende eines eigenen Fensters holt der Ingestor keine weitere Seite; offene Listen kommen beim nächsten Vollabgleich wieder dran. Das Standardfenster begrenzt dagegen nur den Beginn: Ein begonnener Vollabgleich läuft zu Ende.
- **In Zeitscheiben:** Liefert ein Server seine vollständigen Listen nicht aus (etwa weil sie nach 60 Sekunden mit HTTP 504 abbrechen), fragt der Vollabgleich jede Liste nur in Zeitscheiben an, von alt nach neu, mit `modified_since` und `modified_until` (OParl 1.1) auf jeder Seite. Ohne Filter fragt er nie an: Lehnt der Server den Filter ab, bleibt die Liste offen, statt dass wir die vollständige Liste anfordern. Jede Scheibe kostet mindestens eine Anfrage, auch wenn sie leer ist; Scheiben zu 30 Tagen ab 2010 sind am 16.10.2026 je Liste 206 Scheiben.
- **Zeitscheiben nur im Fenster:** Ein Vollabgleich in Zeitscheiben läuft nur im Zeitfenster der Quelle (eigenes oder Standardfenster) und endet immer mit ihm. Außerhalb des Fensters läuft stattdessen ein Änderungsabgleich, ebenso bei einem Aufruf ohne Zeitfenster, etwa über die Kommandozeile. Ein Durchgang kann so mehrere Nächte brauchen: Der nächste Vollabgleich setzt an der letzten vollständigen Scheibe fort.
- **Filter nicht beachtet:** Liefert eine Scheibe Objekte, die mehr als einen Tag vor oder nach ihrem Zeitraum geändert wurden, beachtet der Server den Filter nicht. Dann übernehmen wir nichts aus dieser Seite und brechen den Vollabgleich ab, statt in jeder Scheibe dieselbe vollständige Liste zu holen. 30 Tage lang läuft der Vollabgleich der Quelle danach nur als Änderungsabgleich.
- **Von Hand:** Einen Vollabgleich fordern wir im Admin nur ausnahmsweise an, etwa nach der Aufnahme eines neuen Systems. Auch dann gelten das eigene Zeitfenster und der Mindestabstand der Quelle: Liegt der letzte vollständige Vollabgleich weniger lange zurück als dieser Abstand oder ist das eigene Fenster gerade geschlossen, läuft nur ein Änderungsabgleich. Sonst beginnt er ohne eigenes Fenster sofort, auch tagsüber, und läuft zu Ende; ein Vollabgleich in Zeitscheiben nur im Standardfenster. Bei Systemen ohne OParl-Schnittstelle (Scraper) gelten Zeitfenster und Mindestabstand derzeit nur für den geplanten Vollabgleich.

### Vor der Aufnahme eines Systems

- **Sondierung:** Ob ein System für uns infrage kommt, prüfen wir mit höchstens fünf Anfragen je Kommune: robots.txt, Startseite und die üblichen Adressen einer OParl-Schnittstelle. Weiterleitungen und die robots.txt eines weiteren Servers zählen mit. Gesperrte Pfade fragen wir nicht an; ist die robots.txt nicht erreichbar, endet die Prüfung nach dieser einen Anfrage. Zwischen zwei Kommunen liegen zusätzlich 2 Sekunden Pause.
- **Quellenanlage:** Beim Anlegen einer Quelle rufen wir nach Prüfung der robots.txt System und Kommunenliste ab (höchstens 20 Seiten), im selben Takt.

### Neue Quellen und Kommunen

- **Neue Quellen** sind inaktiv, wenn unsere Werkzeuge sie anlegen: das Werkzeug zum Anlegen einer Quelle (`manage.py add_oparl_source`) und der Ingestor (`add-source`, `init-sources`, ein Abgleich von Hand mit einer noch unbekannten Adresse). Regelmäßig abgefragt wird eine Quelle erst, wenn sie aktiv ist. Vorhandene Quellen behalten ihren Status.
- **Ausnahmen:** Aktiv legen eine Quelle das Formular „Quelle hinzufügen“ im Admin an (das Feld „Aktiv“ ist vorbelegt), `manage.py import_oparl_sources --activate` und die Veröffentlichung eines Session-Mandanten im Bürgerportal; diese schaltet eine abgeschaltete Quelle des Mandanten auch wieder ein.
- **Neue Kommunen** bleiben ungelistet, bis wir sie im Admin listen, außer bei der eigenen Schnittstelle eines Session-Mandanten. Bis dahin erscheinen sie nicht in Kommunenauswahl, Übersichten, Sitemaps und öffentlichen Listen. Abgerufen werden ihre Daten und Dateien trotzdem, solange die Quelle aktiv ist; nur abgelegt werden ihre Dokumente beim Abgleich nicht.

## Dokumente

Dateien (Vorlagen, Anlagen, Niederschriften, fast immer PDF) laden wir unter den Regeln oben: robots.txt, Takt je Server, Weiterleitungen. Für einzelne Quellen schalten wir den Dateiabruf ganz ab, etwa wenn Sie das wünschen; die Vorschau verweist dann auf das Original.

- **Texterkennung:** Jede neu erfasste Datei, deren Text fehlt, lädt der Ingestor einmal, je Kommune und Lauf höchstens 500 Dateien, bis 50 MB je Datei.
- **Dokument-Cache:** stündlich höchstens 400 Dateien, je Quelle höchstens 200, bis 80 MB je Datei. Nach Zeitüberschreitung, Verbindungsfehler, leerer Antwort, 429, 5xx oder nicht erreichbarer robots.txt versuchen wir es nach 15 Minuten, 1, 6, 24 und 72 Stunden erneut. Danach und bei anderen Fehlern, auch HTTP 403, versuchen wir es alle sieben Tage wieder, ohne Obergrenze. Die Versuche enden, wenn die robots.txt die Datei sperrt oder die Quelle statt der Datei eine HTML-Seite liefert (siehe unten), wenn die Datei größer als 80 MB ist, wenn sie mit HTTP 404 oder 410 nicht mehr vorhanden ist (dann übernimmt der Löschabgleich) oder wenn wir Ihre Quelle oder den Dateiabruf dafür abschalten. HTTP 404 oder 410 gilt in den ersten sieben Tagen nach unserer Erfassung als vorläufig, weil Quellen das Objekt oft vor der Datei veröffentlichen.
- **Vorschau:** Öffnet jemand bei uns ein Dokument, das wir nicht abgelegt haben, laden wir es bei der Quelle, mit den Grenzen unter [Takt](#takt). Bei Kommunen, deren Dokumente wir ablegen, legen wir es dabei ab; bei den übrigen fragt jedes Öffnen bei der Quelle an.
- **Löschabgleich:** stündlich. Dokumente, die die Quelle geändert hat, laden wir neu (höchstens 200 je Lauf). Dazu kommen Stichproben per `HEAD`, nur bei öffentlich gelisteten Kommunen und höchstens 30 je Kommune und Lauf. Dokumente, die mit 404 oder 410 verschwunden sind, prüfen wir bei öffentlich gelisteten Kommunen nach 1, 7 und 25 Tagen erneut; nach 30 Tagen fragen wir sie vor dem Löschen noch einmal per `GET` an. Fehlen sie weiter, löschen wir Kopie und Text, sonst heben wir die Sperre auf. Nach HTTP 429 oder 503 oder nach fünf Fehlern in Folge fragt der Lauf diesen Server nicht weiter an. Melden in einem Lauf mehr als 10 Dokumente einer Quelle neu 404 oder 410, lässt er die Quelle für diesen Lauf ruhen. Was Sie löschen, verschwindet so auch bei uns.
- **Abgeschaltete Quelle:** Vorschau und Löschabgleich richten sich nicht danach, ob die Quelle aktiv ist, sondern nur nach dem Dateiabruf und der Schonung. Sollen bei Ihrem Ratsinformationssystem gar keine Abrufe mehr stattfinden, schalten wir deshalb zusätzlich den Dateiabruf ab. Eine Sperre per robots.txt wirkt ohnehin bei allen Abrufen bei Ratsinformationssystemen. Den Abruf Ihres Geoportals und eine Live-Übertragung schalten wir auf Wunsch getrennt ab (siehe [Andere Abrufe](#andere-abrufe)).
- **Gesperrt per robots.txt oder Bot-Schutz** (eine HTML-Seite statt der Datei): Diese Datei laden wir erst nach einer Freigabe wieder. Zugangsprüfungen umgehen wir nicht.

## Personenfotos

- Montags um 03:00 Uhr, nur für Kommunen, bei denen wir ein Muster für Fotoadressen hinterlegt haben.
- Höchstens 500 Personen je Kommune und Lauf. Geladen werden Fotos, die noch nie geprüft wurden oder deren letzte Prüfung mehr als 30 Tage zurückliegt. Zwischen zwei Fotos liegen 0,1 Sekunden Pause, dazu gilt der Takt je Server.
- Ein fehlendes Foto oder ein Fehler wird vermerkt und frühestens nach 30 Tagen wieder angefragt. Ist die robots.txt nicht erreichbar, wird nichts vermerkt; der nächste Lauf versucht es erneut.
- Ist die Quelle abgeschaltet, der Dateiabruf aus oder wird die Quelle gerade geschont, laden wir keine Fotos und vermerken nichts.

## Fehler und Schonung

- **Wiederholungen im Abgleich:** Nach Netzfehler, Zeitüberschreitung oder 5xx höchstens 3 Versuche, mit Pausen von 1 und 2 Sekunden, jeder Versuch im Takt. HTTP 403, 404, 429 und andere 4xx wiederholen wir in diesem Lauf nicht. Für Dateien gilt der Plan unter [Dokumente](#dokumente).
- **Schutzschalter:** Nach 5 Fehlversuchen an einen Server im Lauf einer Quelle stellen wir 60 Sekunden lang keine Anfragen an diesen Server. HTTP 404 zählt dabei nicht.
- **Gestörte Quelle:** 5 Serverfehler in Folge an einen Server gelten als Störung (5xx-Serie).
- **Pausen:** Ab dem dritten fehlgeschlagenen Lauf einer Quelle in Folge pausiert der Abgleich 10 Minuten, danach je weiterem Fehlversuch doppelt so lang, höchstens 6 Stunden (10, 20, 40 … 360 Minuten). Bei drei Arten von Befunden pausiert er schon beim ersten Mal: mindestens 60 Minuten, wenn ein Server unseren User-Agent sperrt, 30 Minuten bei einer 5xx-Serie oder nicht erreichbarer robots.txt und 24 Stunden, wenn die robots.txt keine Anfrage zulässt. Ist die Pause aus der Reihe länger, gilt sie.
- **Anwendung:** Dokument-Cache, Vorschau, Löschabgleich und Personenfotos ruhen für eine Quelle ab drei fehlgeschlagenen Läufen des Abgleichs in Folge, bis ein Lauf sie wieder erreicht. Eine Sperre per robots.txt beachten sie unabhängig davon bei jedem Abruf. Ein getrennt betriebener Worker für die Texterkennung richtet sich nur nach dem Dateiabruf der Quelle und der robots.txt, nicht nach der Schonung und nicht danach, ob die Quelle abgeschaltet ist.
- Einen `Retry-After`-Header werten wir nicht aus. Eine Sperre unseres User-Agents umgehen wir nicht; wir versuchen es nur in den genannten Abständen wieder.

## Andere Abrufe

Diese Abrufe gehen nicht an Ratsinformationssysteme, sondern an Streaming-Anbieter und Geodienste. Sie melden sich mit derselben Kennung, `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)`, und halten einen eigenen Takt je Server ein, vor jeder Anfrage und vor jeder Weiterleitung. Der Takt nutzt denselben gemeinsamen Speicher wie die Abrufe bei Ratsinformationssystemen: Liegt ein Dienst auf dem Server eines Ratsinformationssystems, etwa das Geoportal einer Kommune, teilen sich beide den Takt. Haben wir für eine Quelle auf demselben Hostnamen einen größeren Abstand eingestellt, halten Live-Übertragung und Geoportale ihn ebenfalls ein, auch wenn die Quelle abgeschaltet ist; ein geänderter Abstand wirkt dort spätestens nach fünf Minuten.

Die robots.txt werten diese Abrufe nicht aus, auch nicht bei Geoportalen von Kommunen: Sie durchsuchen keine Seiten, sondern fragen Schnittstellen ab, und es gelten die Nutzungsregeln des jeweiligen Dienstes. Eine Gruppe für `mandari-ingestor` in der robots.txt Ihres Geoportals stoppt den täglichen Abruf der Umringe von Bebauungsplänen also nicht. Möchten Sie ihn nicht, schreiben Sie an [support@mandari.de](mailto:support@mandari.de); wir schalten ihn dann ab.

| Abruf | Ziel | Abstand je Server | Wann |
|---|---|---|---|
| Live-Übertragung | Streaming-Anbieter (3Q, HLS-Server) | 1 Sekunde; ein größerer Abstand einer Quelle auf dem Server gilt | nur bei eingeschalteter Live-Übertragung: Status einmal je Minute rund um Sitzungen, ab 45 Minuten vor bis längstens 10 Stunden nach ihrem Beginn; während einer Übertragung ein Einzelbild alle 10 Sekunden (je Quelle 5 bis 60), je Einzelbild 2 bis 4 Anfragen |
| Umringe von Bebauungsplänen | Geoportale von Kommunen und Land (WFS, OGC API – Features) | 1 Sekunde; ein größerer Abstand einer Quelle auf dem Server gilt; dazu 1 Sekunde Pause zwischen zwei Seiten | täglich um 04:50 Uhr |
| Nominatim (OpenStreetMap) | `nominatim.openstreetmap.org` | 1 Sekunde, wie es die Nutzungsregeln verlangen | Geodaten einer Kommune, von Hand beim Einrichten; Ersatz bei der Verortung von Vorgängen, wenn Photon nichts findet |
| Overpass (OpenStreetMap) | `overpass-api.de`, Ersatz `overpass.kumi.systems` | 1 Sekunde | Straßen, Adressen und Grenzen, von Hand beim Einrichten einer Kommune |
| Photon | `photon.komoot.io` | 1 Sekunde; in der Adresssuche höchstens 2 Sekunden Wartezeit, sonst keine Vorschläge | Verortung von Vorgängen an Orten, die das eigene Straßenverzeichnis nicht kennt; Adresssuche nur ohne eigenes Straßenverzeichnis |
| Kartenkacheln | `tile.openstreetmap.org` | 0,05 Sekunden (bis zu 20 Kacheln je Sekunde); höchstens 5 Sekunden Wartezeit, sonst HTTP 503 | nur Kacheln, die nicht im eigenen Zwischenspeicher liegen; insgesamt höchstens 1200 Abrufe je Minute, 300 je Besucher-Adresse |
| Kacheln vorab laden | `tile.openstreetmap.org` | 0,5 Sekunden | nur von Hand |

## Für Betreiber eigener Installationen

Wer mandari selbst betreibt, ruft von der Adresse des eigenen Servers ab und übernimmt die Verantwortung gegenüber den Betreibern der eigenen Quellen.

- Setzen Sie `INGESTOR_USER_AGENT` (älterer Name: `SCRAPER_USER_AGENT`) auf eine Kennung mit Ihrer Kontaktadresse, etwa `mandari-ingestor/0.1.0 (+https://ris.example.de/abruf/; it@example.de)`. Die Variable gehört in die Umgebung des Ingestors und auch in die Umgebung der Anwendung: Die Sync-Aktionen an einer Quelle im Admin gehen an den Ingestor, solange er läuft; ohne ihn, für abgeschaltete Quellen und wenn die Anforderung ihn nicht erreicht, laufen sie im Worker der Anwendung. Ein Eintrag nur in der `.env` wirkt unter Docker Compose nicht. Regeln der robots.txt für `mandari-ingestor` gelten weiter, weil mandari dieses Token immer zusätzlich prüft.
- Die Abrufe der Anwendung (Dokument-Cache, Vorschau, Löschabgleich, Personenfotos, Quellenanlage, Live-Übertragung und Geodienste) melden sich mit der festen Kennung `mandari-ingestor (+https://mandari.de/crawler/; support@mandari.de)`. Abweichend lässt sie sich nur je Quelle über `sync_config["download_headers"]` setzen (nicht für Quellenanlage, Live-Übertragung und Geodienste).
- Den gemeinsamen Takt über alle Prozesse gibt es nur mit Redis, das Ingestor und Anwendung beide erreichen. `INGESTOR_REQUEST_INTERVAL` und `RIS_REQUEST_INTERVAL` (Standard je `1.0`) legen den Abstand je Server fest; `0` schaltet die Drossel ab und ist nur für Tests und Notfälle gedacht. Den Takt der [anderen Abrufe](#andere-abrufe) legt der Code je Dienst fest; eine Umgebungsvariable dafür gibt es nicht.
- Eine Quelle abzuschalten (`is_active = false`) stoppt nicht alle Abrufe: Vorschau, Löschabgleich und ein getrennt betriebener Worker für die Texterkennung richten sich nicht danach, ob die Quelle aktiv ist. Sollen nach einem Opt-out gar keine Abrufe beim Ratsinformationssystem mehr stattfinden, schalten Sie zusätzlich den Dateiabruf ab (`sync_config["file_downloads"] = false`). Den Abruf der Umringe vom Geoportal (`PlanBoundarySource.is_active`) und eine Live-Übertragung (`BroadcastSource.active`) schalten Sie getrennt ab.

Alle Einstellungen je Quelle und per Umgebungsvariable stehen in den [Abrufregeln](https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md). Wie Sie Quellen anbinden und Takt und Vollabgleich je Quelle einstellen, steht unter [Quellen anbinden](../betrieb/quellen-anbinden.md#takt-und-vollabgleich-je-quelle), weitere Variablen in der [Konfigurationsreferenz](../betrieb/konfiguration.md#ingestor).
