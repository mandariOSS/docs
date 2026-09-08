---
title: Technische und organisatorische Maßnahmen
description: Technische und organisatorische Maßnahmen (TOM) der mandari-Plattform nach Art. 32 DSGVO. Anlage zum Auftragsverarbeitungsvertrag.
---

# Technische und organisatorische Maßnahmen (TOM)

Stand: Juli 2026 · Bezug: Art. 32 DSGVO

Dieses Dokument beschreibt die technischen und organisatorischen Maßnahmen der Plattform mandari (Session, Work, Insight). Es dient als Anlage zum Auftragsverarbeitungsvertrag ([Muster-AVV](avv-muster.md)).

## 1. Vertraulichkeit

### Zutritts- und Zugangskontrolle

- Hosting in einem europäischen Rechenzentrum. Zugriff auf Server nur per SSH mit Schlüssel-Authentifizierung.
- Anmeldung an der Anwendung mit E-Mail-Adresse und Passwort, optional TOTP-basierte Zwei-Faktor-Authentifizierung. Rate-Limiting gegen Brute-Force (5 Versuche je 15 Minuten), Sitzungs- und Geräteverwaltung je Konto.

### Zugriffskontrolle (Berechtigungskonzept)

- Mandantenfähigkeit mit strikter Datenisolation je Kommune und Organisation. Alle Abfragen sind mandantengebunden.
- Feingranulares Rollen- und Rechtesystem. Session: unter anderem Nutzerverwaltung, Einstellungen, Sitzungsgelder, nicht-öffentliche Sitzungen. Work: über fünfzig Berechtigungen.
- Bankdaten sind zusätzlich auf die Sitzungsgeld-Berechtigung beschränkt, nicht-öffentliche Inhalte auf eigens berechtigte Rollen.

### Verschlüsselung

- Transport: ausschließlich TLS (HTTPS, HSTS).
- Speicherung sensibler Felder: AES-256-GCM mit **mandantenspezifischen Schlüsseln**, die ihrerseits mit einem Master-Key verschlüsselt sind (Schlüsselhierarchie, Crypto-Shredding beim Löschen eines Mandanten).
- Verschlüsselt gespeichert werden unter anderem Kontaktdaten, Bankdaten, nicht-öffentliche Protokollteile und interne Notizen.

## 2. Integrität

- Revisionssicheres Audit-Log je Mandant: alle relevanten Änderungen (Erstellen, Ändern, Löschen, Freigaben, Exporte, Einladungsversand) mit Nutzer, Zeitstempel und IP-Adresse. Einträge sind unveränderbar und nicht einzeln löschbar.
- Verschlüsselte Feldinhalte erscheinen im Audit-Log niemals im Klartext.
- Vier-Augen-Prinzip bei der Genehmigung von Sitzungsgeldern.

## 3. Verfügbarkeit und Belastbarkeit

- Tägliche automatisierte Datenbank-Backups mit definierter Aufbewahrung.
- Infrastruktur als Container (reproduzierbare Deployments), getrennte Staging- und Produktionsumgebung.
- Monitoring der Sync- und Hintergrunddienste (Watchdog), öffentliche Statusseite.

## 4. Löschung und Datenminimierung

- Konfigurierbare Aufbewahrungsfristen je Datenart und Mandant. Nachweisbar auditierter Anonymisierungs- und Löschlauf über die Anwendung oder die Kommandozeile. Details im [Löschkonzept](loeschkonzept.md).
- Betroffenenauskunft als strukturierter Export (Art. 15 DSGVO).
- Öffentliche Schnittstellen (OParl-API, öffentliche Fraktions-API, Kalender-Feeds) liefern ausschließlich als öffentlich gekennzeichnete Inhalte. Opake Zufalls-Tokens statt personenbezogener URLs.

## 5. Organisatorische Maßnahmen

- Prinzip der geringsten Rechte bei der Rollenzuweisung (Standardrollen mit abgestuften Rechten).
- Einladungsbasierte Konten, keine Selbstregistrierung in Mandanten.
- Quelloffener Code, überprüfbare Sicherheitsmaßnahmen.
- Regelmäßige automatisierte Testläufe inklusive Berechtigungs- und Mandanten-Isolationstests vor jedem Release.

## 6. Weisungs- und Kontrollrechte des Auftraggebers

- Der Auftraggeber (Kommune) steuert Rollen, Fristen und Veröffentlichungen selbst in der Anwendung.
- Export aller Daten über dokumentierte Schnittstellen (OParl, CSV, JSON). Keine Anbieterbindung.
