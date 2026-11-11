---
title: Demo-Umgebung
description: Mit einem Befehl eine vollständige, klar als Demo erkennbare Musterumgebung über Insight, Work und Session anlegen und wieder entfernen. Öffentliche Demo-Instanz mit DEMO_INSTANCE, Präsentationsumgebung für Vorführungen.
---

# Demo-Umgebung

Der Befehl `setup_demo_environment` erstellt eine vollständige, klar als Demo erkennbare Musterumgebung über alle drei Portale hinweg. Alle Daten sind synthetisch und frei erfunden. Ideal, um mandari nach der Installation kennenzulernen oder vorzuführen.

```bash
python manage.py setup_demo_environment          # anlegen oder aktualisieren
python manage.py setup_demo_environment --reset  # restlos entfernen
```

Sitzungstermine liegen relativ zum Tag des Aufbaus, immer an einem Werktag um 17 Uhr Ortszeit (die Fraktionssitzung um 19 Uhr). Die kommende Ratssitzung liegt in Insight und Session am selben Tag.

## Was angelegt wird

### Insight

Fiktive Kommune **„Musterstadt (Demo)“**:

- 3 Gremien (Rat, Hauptausschuss, Ausschuss für Bauen und Verkehr) und 2 Fraktionen
- 8 fiktive Personen mit Mitgliedschaften
- 1 Wahlperiode, 6 Sitzungen, vergangene und kommende, mit Tagesordnungspunkten
- 12 Vorlagen verschiedener Typen (Beschlussvorlage, Antrag, Anfrage, Mitteilungsvorlage) mit Beratungen; 8 davon sind mit zusammen 12 erfundenen Orten verortet, sodass die Karten in Insight und Work Punkte zeigen
- 5 kleine, selbst erzeugte PDF-Dateien mit bereits gesetztem Volltext, darunter die Unterlagen aller Vorlagen der kommenden Ratssitzung

Die Kommune ist **nicht gelistet**: Sie erscheint weder in der Kommunenauswahl noch in Übersichten, Sitemaps oder der OParl-Aggregations-API. Erreichbar ist sie nur über ihre direkte Adresse (`/insight/kommune/<uuid>/`). Überall steht „(Demo)“ im Namen.

### Work

Organisation **„Musterfraktion (Demo)“**, verknüpft mit der Musterstadt und der Parteigruppe „Musterpartei (Demo)“:

- Standardrollen
- 5 Demo-Nutzer: Fraktionsvorsitz, Fraktionsmitglied, sachkundige Bürgerin, ein noch nicht vereidigtes Fraktionsmitglied und ein Gast mit lesender Ordnerfreigabe
- 2 Anträge (Entwurf und eingereicht), 1 Sitzungsvorbereitung mit Positionen und Notizen zur kommenden Ratssitzung, 3 Aufgaben
- das neue Design von Work, nur für die Demo-Organisation eingeschaltet
- Fraktionssitzungen mit Standard-Tagesordnung, einer vergangenen und einer kommenden Sitzung (öffentliche und nichtöffentliche TOPs, ein TOP-Vorschlag), eine Sitzungsreihe mit Ferienpause, Positionen mit Beratungsverlauf über zwei Gremien, Kommentare und Änderungsanträge
- eine Ankündigung „Was ist neu in Work“ für alle Mitglieder außer dem Gast

### Session

Mandant **„Stadtverwaltung Musterstadt (Demo)“**:

- Standardrollen und 4 Verwaltungsnutzer, je einer für Administration, Sachbearbeitung, Protokollführung und Lesezugriff
- 3 Gremien und 8 Personen passend zur Kommune, Kontaktdaten verschlüsselt gespeichert; dazu das Amt „Kämmerei (Demo)“ mit einer Mitzeichnungsregel
- 3 Sitzungen mit Tagesordnung, 4 Vorlagen (eine mit vertraulichem Inhalt) und 2 Anträge der Musterfraktion; einer ist eingegangen, der andere schon in eine Vorlage für die kommende Ratssitzung umgewandelt
- Anwesenheit und genehmigtes Protokoll der vergangenen Sitzung des Hauptausschusses

Der Mandant veröffentlicht **nicht** im Bürgerportal. Die Musterstadt in Insight stammt aus der eigenen Demo-Quelle, nicht aus dem Session-Mandanten.

### Bestand der Musterstadt

Die Abläufe oben sind von Hand geschrieben. Damit Rat, Ausschüsse, Fraktionen und Verwaltung so voll aussehen wie in einer echten Stadt, legt `setup_demo_environment` danach einen **Bestand** an. Jedes Portal legt seinen Teil selbst an, aus einem gemeinsamen Katalog:

| Befehl | Portal | Inhalt |
|---|---|---|
| `setup_demo_insight` | Insight | 6 Fraktionen und Gruppen, gut 50 Personen mit Rat-, Fraktions- und Ausschussmitgliedschaften, 11 Gremien, ein Jahr Sitzungen (rund 115) mit Tagesordnungen samt nichtöffentlichen Teilen, rund 185 Vorgänge mit Beratungsfolgen, Beschlussnummern, Abstimmungen (auch namentlich), Umsetzungsstand, PDF-Drucksachen, Einladungen, Niederschriften und Orten für die Karte |
| `setup_demo_work_bestand` | Work | weitere Mitglieder der Musterfraktion (ohne Anmeldung), ihre Anträge und Anfragen passend zum Ratsinformationssystem, Entwürfe, Ordner, Aufgaben, Sitzungsvorbereitungen mit Positionen |
| `setup_demo_session` | Session | dieselben Gremien, Personen, Ämter, Vorlagen, Sitzungen, Anträge, Anwesenheiten und Niederschriften im Sitzungsdienst |

Termine liegen relativ zum Tag des Aufbaus: Ratssitzung alle sechs Wochen, die Ausschüsse davor; Ausschüsse sind nach d'Hondt besetzt. `DEMO_UMFANG=voll` ist der Standard; `klein` legt dieselben Wege mit einem Bruchteil der Daten an (für Tests).

## Zugangsdaten

Die Passwörter der Demo-Nutzer werden bei **jedem Lauf neu erzeugt** und ausschließlich auf der Konsole ausgegeben. Sie werden nirgendwo gespeichert. Ein erneuter Lauf rotiert die Passwörter, praktisch, wenn sie verloren gegangen sind.

Die Konten haben Adressen unter `demo.mandari.de`. Diese Domain ist über `TWO_FACTOR_EXEMPT_EMAIL_DOMAINS` (Standardwert) von der Pflicht zum zweiten Faktor ausgenommen, weil die Zugänge gemeinsam genutzt werden und keine echten Daten enthalten.

## Öffentliche Demo-Instanz

Für einen öffentlichen Testzugang läuft die Demo als **eigene Installation mit eigener Datenbank**, in der nur die synthetischen Daten liegen. Der Schalter `DEMO_INSTANCE=true` macht aus einer normalen Installation diese Demo:

| Was | Verhalten in der Demo-Instanz |
|-----|-------------------------------|
| E-Mail | Es wird nichts versendet, auch nicht über SMTP-Zugänge aus den Systemeinstellungen oder einer Organisation. |
| KI-Funktionen | abgeschaltet |
| Passwort, zweiter Faktor, Sicherheitsschlüssel | nicht änderbar; alle Besucher teilen sich die Konten |
| Registrierung, „Passwort vergessen“, Kontolöschung | gesperrt |
| Hinweis | auf jeder Seite: Demo-Umgebung, alle Daten sind erfunden und werden zurückgesetzt, mit den Uhrzeiten aus `DEMO_NEUAUFBAU_UTC` |
| Anmeldeseite | Liste aller Demo-Zugänge mit dem Passwort; je Rolle meldet ein Klick an und führt in Work oder Session. Dazu ein Link ins Bürgerportal der Musterstadt. |

Ist zusätzlich `DEMO_PASSWORD` gesetzt, bekommen alle Demo-Konten dieses feste Passwort, damit es öffentlich genannt werden kann. Das gilt **nur** mit `DEMO_INSTANCE`; sonst ignoriert der Befehl die Variable. Setzen Sie `DEMO_INSTANCE` nie in einer Installation mit echten Daten.

Wer die Demo regelmäßig zurücksetzen will, verwirft die Demo-Datenbank, migriert neu und ruft `setup_demo_environment` (und gegebenenfalls `setup_demo_praesentation`) erneut auf. Den Zeitplan richtet der Betreiber selbst ein, etwa per Cron. Damit der Hinweis ihn nennen kann, steht er zusätzlich in `DEMO_NEUAUFBAU_UTC`: Uhrzeiten in UTC, kommagetrennt, etwa `03:30,15:30`; angezeigt werden sie in Ortszeit. Beide Angaben müssen zusammenpassen. Ohne die Variable sagt der Hinweis nur „regelmäßig“.

## Präsentationsumgebung

Auf der Demo-Umgebung setzt `setup_demo_praesentation` eine Vorführung auf, in der eine Drucksache ihren Weg von der Fraktion (Work) über den Sitzungsdienst (Session) ins Bürgerportal und die OParl-Schnittstelle nimmt. Dazu kommen ein zweiter Mandant, eine Leitstelle mit Zugang zu beiden und ein Einreichungs-Token für die Musterfraktion. Dafür veröffentlicht der Demo-Mandant im Bürgerportal; die Kommune bleibt ungelistet. Ein erneuter Lauf setzt die live gespielten Schritte zurück, sodass sich die Vorführung proben lässt.

```bash
python manage.py setup_demo_praesentation                      # Profil nrw: Nummern wie 0001/2026
python manage.py setup_demo_praesentation --profil stadtstaat   # Drucksachen wie 22-0001, beide Mandanten als Mandantengruppe
python manage.py setup_demo_praesentation --reset              # nur die Präsentation entfernen, die Basisdemo bleibt
```

Das Passwort der Leitstelle entsteht beim Anlegen und erscheint nur dann auf der Konsole.

## Wiederholbarkeit und Aufräumen

- Alle Objekte hängen an festen Demo-Kennungen (Slugs mit Endung `-demo`, OParl-IDs unter einer nicht auflösbaren Demo-Domain). Wiederholte Läufe aktualisieren statt zu duplizieren.
- Kennungen des Bestands beginnen mit `b-`. Ein wiederholter Lauf entfernt den Bestand und legt ihn neu an; die von Hand geschriebenen Abläufe bleiben unberührt.
- Die Demo-Quelle ist **inaktiv**, damit der Ingestor sie nie abruft.
- `--reset` löscht ausschließlich die über diese Kennungen identifizierten Objekte: Session-Mandant, Work-Organisation, Parteigruppe, Demo-Nutzer, Quelle samt Kommune und die erzeugten PDF-Dateien, dazu eine darauf aufgesetzte Präsentationsumgebung (siehe unten).

## Verifikation

Ein selbst enthaltener Test auf einer frischen SQLite-Instanz prüft doppelten Lauf ohne Duplikate, Demo-Logins, Darstellung der Insight-Seiten, Work-Dashboard inklusive Gastzugriff, Session-Dashboard und vollständiges Aufräumen:

```bash
python scripts/smoke_demo_environment.py
```
