---
title: Datenschutz und Sicherheit
description: Überblick über Datenschutz und Sicherheit bei mandari. Verschlüsselung, Mandantentrennung, Berechtigungen, Löschung, öffentliche Schnittstellen und die Dokumente für Datenschutzbeauftragte.
---

# Datenschutz und Sicherheit

mandari verarbeitet in Session und Work personenbezogene Daten von Mandatsträgerinnen, Verwaltungsbeschäftigten und Fraktionsmitgliedern. Diese Seite gibt den Überblick, die Unterseiten liefern die Dokumente, die Datenschutzbeauftragte und Vergabestellen brauchen.

## Dokumente

<div class="mandari-grid" markdown>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-shield-check-24:</span>
**[Technische und organisatorische Maßnahmen](tom.md)**
Vertraulichkeit, Integrität, Verfügbarkeit, Löschung, organisatorische Maßnahmen. Anlage zum AVV nach Art. 32 DSGVO.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-trash-24:</span>
**[Löschkonzept](loeschkonzept.md)**
Datenarten, Aufbewahrungsfristen, auditierter Löschlauf, Betroffenenauskunft, Löschung ganzer Mandanten.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-file-badge-24:</span>
**[Muster-AVV](avv-muster.md)**
Arbeitsgrundlage für den Auftragsverarbeitungsvertrag zwischen Kommune und Betreiber nach Art. 28 DSGVO.
</div>

<div class="mandari-card" markdown>
<span class="mandari-card__icon">:octicons-globe-24:</span>
**[Crawler und Opt-out](crawler.md)**
Wie unser Ingestor mit kommunalen Servern umgeht und wie Kommunen Drosselung oder Entfernung verlangen.
</div>

</div>

## Grundsätze in Kürze

**Verschlüsselung.** Transport ausschließlich über TLS mit HSTS. Sensible Felder wie Kontaktdaten, Bankdaten, nicht-öffentliche Protokollteile und interne Notizen liegen AES-256-GCM-verschlüsselt in der Datenbank, mit einem eigenen Schlüssel je Mandant, der wiederum mit einem Master-Key verschlüsselt ist. Beim Löschen eines Mandanten wird sein Schlüssel vernichtet (Crypto-Shredding).

**Mandantentrennung.** Kommunen und Organisationen sind strikt voneinander isoliert. Jede Datenbankabfrage ist an den Mandanten gebunden, automatische Tests prüfen die Isolation vor jedem Release.

**Berechtigungen.** Feingranulare Rollen und Rechte, Prinzip der geringsten Rechte bei den Standardrollen, Bankdaten zusätzlich auf die Sitzungsgeld-Berechtigung beschränkt. Konten entstehen nur per Einladung, optional mit Zwei-Faktor-Authentifizierung.

**Nachvollziehbarkeit.** Revisionssicheres Audit-Log je Mandant mit Nutzer, Zeitstempel und IP-Adresse. Verschlüsselte Inhalte erscheinen dort nie im Klartext.

**Löschung.** Konfigurierbare Aufbewahrungsfristen je Datenart, ein auditierter Anonymisierungs- und Löschlauf und eine strukturierte Betroffenenauskunft. Details im [Löschkonzept](loeschkonzept.md).

**Öffentliche Schnittstellen.** OParl-APIs, Fraktions-API und Kalender-Feeds liefern ausschließlich als öffentlich gekennzeichnete Inhalte. Zugänge laufen über opake Zufalls-Tokens statt personenbezogener URLs.

**Offener Code.** Der Quellcode ist öffentlich. Sicherheitsmaßnahmen lassen sich prüfen statt glauben.

## Bürgerportal

Das Bürgerportal Insight verarbeitet Daten, die Kommunen selbst veröffentlichen. Personenbezogen sind dabei vor allem Namen und Mandate von Ratsmitgliedern. Wer eine Frage über die Ratsfragen stellt oder einen Beschluss abonniert, gibt eine E-Mail-Adresse an, die nur nach Bestätigung (Double-Opt-in) verwendet wird und jederzeit abgemeldet werden kann. Dokumente werden über den mandari-Proxy ausgeliefert, sodass sich Browser der Besucherinnen nicht mit kommunalen Servern verbinden.

Die Datenschutzerklärung der von uns betriebenen Installation steht unter [mandari.de/datenschutz/](https://mandari.de/datenschutz/).

## Sicherheitslücke melden

Hinweise auf Sicherheitsprobleme bitte vertraulich an <security@mandari.de>, nicht über öffentliche Issues. Wir melden uns zeitnah zurück.
