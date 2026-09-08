---
title: Löschkonzept
description: Löschkonzept für mandari Session. Datenarten, Speicherorte, Aufbewahrungsfristen, Durchführung und Nachweis des Löschlaufs, Betroffenenauskunft, Löschung ganzer Mandanten.
---

# Löschkonzept

Stand: Juli 2026

Dieses Löschkonzept beschreibt, welche personenbezogenen Daten mandari Session speichert, welche Aufbewahrungsfristen gelten und wie die Löschung bzw. Anonymisierung technisch und nachweisbar erfolgt. Verbindlich sind stets die örtlichen Satzungen und Aufbewahrungsvorschriften der jeweiligen Kommune. Die hier genannten Fristen sind konfigurierbare Voreinstellungen.

## 1. Datenarten und Speicherorte

| Datenart | Schutz |
|----------|--------|
| Stammdaten Mandatsträger (Name, Funktion) | Zugriff nur mit Rollenberechtigung |
| Kontaktdaten (Telefon, Adresse) | AES-256-GCM, Mandantenschlüssel |
| Bankdaten (Kontoinhaber, IBAN, BIC) | AES-256-GCM, Zugriff nur mit Sitzungsgeld-Berechtigung |
| Sitzungsgeld-Positionen | Beträge und Status, keine Bankdaten |
| Nicht-öffentliche Protokollteile | AES-256-GCM |
| Interne Sitzungsnotizen | AES-256-GCM |
| Audit-Log | unveränderbar (revisionssicher), keine Klartextwerte verschlüsselter Felder |

## 2. Aufbewahrungsfristen

Die Fristen werden **je Mandant** unter *Einstellungen → Datenschutz* gepflegt, Angabe in Jahren, `0` deaktiviert die Frist:

| Datenart | Frist ab | Wirkung nach Fristablauf |
|----------|----------|--------------------------|
| Kontakt- und Bankdaten ausgeschiedener Mandatsträger | Mandatsende | E-Mail, Telefon, Adresse und Bankdaten werden entfernt. **Der Name bleibt erhalten**, damit historische Beschlüsse und Protokolle nachvollziehbar bleiben. |
| Nicht-öffentliche Inhalte | Sitzungsdatum | Nicht-öffentlicher Protokollteil und interne Notizen werden geleert. Der öffentliche Protokollteil bleibt unberührt. |
| Audit-Log | Eintragsdatum | Einträge werden gelöscht. |

Empfehlungswerte (unverbindlich): Kontakt- und Bankdaten 2 Jahre nach Mandatsende, Audit-Log 5 bis 10 Jahre, nicht-öffentliche Inhalte gemäß örtlicher Archivsatzung. Häufig gilt dauerhafte Aufbewahrung, dann die Frist deaktiviert lassen und die Inhalte dem Kommunalarchiv anbieten.

## 3. Durchführung des Löschlaufs

Zwei gleichwertige Wege:

1. **Anwendung**: *Einstellungen → Datenschutz → Löschlauf ausführen*, mit Probelauf-Option, Berechtigung zur Verwaltung der Einstellungen.
2. **Kommandozeile**, zum Beispiel monatlich per Cron:

    ```bash
    python manage.py session_privacy_purge              # alle aktiven Mandanten
    python manage.py session_privacy_purge --tenant stadt-musterstadt
    python manage.py session_privacy_purge --dry-run    # nur zählen
    ```

### Nachweisbarkeit

Jeder Lauf schreibt Audit-Einträge:

- je anonymisierter Person ein Eintrag mit den geleerten Datenarten, niemals die Werte selbst
- je bereinigter Sitzung ein Eintrag
- ein Abschlusseintrag mit Zählern und den angewandten Fristen

Damit kann die Verwaltung die Durchführung gegenüber der Aufsichtsbehörde belegen (Rechenschaftspflicht, Art. 5 Abs. 2 DSGVO).

## 4. Betroffenenauskunft (Art. 15 DSGVO)

*Einstellungen → Datenschutz → Betroffenenauskunft* exportiert alle zu einer Person gespeicherten Daten als JSON-Datei: Stammdaten, Gremienmitgliedschaften, Anwesenheiten, Sitzungsgelder, Vorlagen als Verfasserin oder Verfasser. Bankdaten werden nur entschlüsselt, wenn die abrufende Person zusätzlich die Sitzungsgeld-Berechtigung besitzt. Jeder Export wird auditiert.

## 5. Löschung ganzer Mandanten

Beim Löschen eines Mandanten (Vertragsende) werden alle abhängigen Daten kaskadiert gelöscht, einschließlich Audit-Log und mandantenspezifischem Verschlüsselungsschlüssel. Ohne Schlüssel sind etwaige Backups der verschlüsselten Felder nicht mehr lesbar (Crypto-Shredding).

## 6. Zugehörige Dokumente

- [Muster-AVV](avv-muster.md)
- [Technische und organisatorische Maßnahmen](tom.md)
