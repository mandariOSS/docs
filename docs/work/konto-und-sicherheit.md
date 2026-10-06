---
title: Konto und Sicherheit
description: Passwort, Zwei-Faktor-Anmeldung mit Authenticator-App und Backup-Codes, Sicherheitsschlüssel und Passkeys, aktive Sitzungen, Datenexport und das Beenden der Mitgliedschaft in mandari Work.
---

# Konto und Sicherheit

In Work arbeiten Sie mit vertraulichen Inhalten: Positionen, Antragsentwürfe, interne Protokolle. Diese Seite zeigt, wie Sie Ihr Konto schützen. Alle Einstellungen finden Sie unter *Profil → Sicherheit*.

## Passwort { #passwort }

Ein neues Passwort muss

- mindestens 12 Zeichen lang sein,
- Groß- und Kleinbuchstaben sowie mindestens eine Ziffer enthalten,
- sich deutlich von Ihrem Namen und Ihrer E-Mail-Adresse unterscheiden und
- darf kein verbreitetes oder rein aus Ziffern bestehendes Passwort sein.

**Ändern**: Unter *Profil → Sicherheit* geben Sie Ihr aktuelles Passwort und zweimal das neue ein. Sie bleiben danach angemeldet.

**Vergessen**: Auf der Anmeldeseite führt „Passwort vergessen“ zu einem Formular. Sie bekommen einen Link per E-Mail, über den Sie ein neues Passwort festlegen. Der Link ist nur begrenzt gültig und nur einmal verwendbar.

!!! tip
    Ein Passwort-Manager erzeugt und merkt sich lange, zufällige Passwörter. Verwenden Sie Ihr mandari-Passwort nirgendwo sonst.

## Zwei-Faktor-Anmeldung { #zwei-faktor }

Mit der Zwei-Faktor-Anmeldung brauchen Sie beim Anmelden neben dem Passwort einen zweiten Nachweis: einen sechsstelligen Code aus einer Authenticator-App auf Ihrem Smartphone oder einen Sicherheitsschlüssel. Wer nur Ihr Passwort kennt, kommt so nicht in Ihr Konto.

### Einrichten { #zwei-faktor-einrichten }

1. Installieren Sie eine Authenticator-App, zum Beispiel die App Ihres Passwort-Managers oder eine der verbreiteten Authenticator-Apps für iOS und Android.
2. Öffnen Sie *Profil → Sicherheit* und wählen Sie **2FA einrichten**.
3. Scannen Sie den QR-Code mit der App. Alternativ geben Sie den angezeigten Schlüssel von Hand ein.
4. Geben Sie den sechsstelligen Code aus der App ein, um die Einrichtung zu bestätigen.
5. Speichern Sie die **Backup-Codes** sicher, etwa im Passwort-Manager oder ausgedruckt.

### Backup-Codes { #backup-codes }

Bei der Einrichtung bekommen Sie zehn Backup-Codes. Jeder funktioniert genau einmal anstelle des Codes aus der App, zum Beispiel wenn Sie Ihr Smartphone verloren haben. Unter *Profil → Sicherheit → Backup-Codes* erzeugen Sie mit Ihrem Passwort neue Codes, die alten werden dabei ungültig.

### Wann ist sie Pflicht? { #zwei-faktor-pflicht }

Die Zwei-Faktor-Anmeldung ist vorgeschrieben

- für Mitglieder mit der Administrator-Rolle,
- für Rollen, bei denen Ihre Organisation „2FA erforderlich“ eingestellt hat, und
- für alle Mitglieder, wenn Ihre Organisation sie für alle verlangt.

Fehlt der zweite Faktor, führt Sie die Anmeldung direkt zur Einrichtung. Ist er für Sie vorgeschrieben, können Sie ihn nicht abschalten. Sonst lässt er sich unter *Profil → Sicherheit* mit Ihrem Passwort deaktivieren, wir raten aber davon ab.

### Kein Zugriff mehr auf die App? { #zwei-faktor-verloren }

Melden Sie sich mit einem Backup-Code an und richten Sie die App auf dem neuen Gerät neu ein. Haben Sie keine Backup-Codes mehr, schreiben Sie unserem Support an <support@mandari.de>. Nachdem wir geprüft haben, dass die Anfrage wirklich von Ihnen kommt, setzen wir den zweiten Faktor zurück. Sie bekommen darüber eine E-Mail.

## Sicherheitsschlüssel und Passkeys { #sicherheitsschluessel }

Zusätzlich zur Authenticator-App können Sie Sicherheitsschlüssel registrieren: einen Hardware-Schlüssel wie einen YubiKey, einen Passkey oder die Entsperrung Ihres Geräts per Fingerabdruck oder Gesichtserkennung.

- Voraussetzung ist eine eingerichtete Authenticator-App. Sie bleibt zusammen mit den Backup-Codes Ihr Rückfall, falls ein Schlüssel verloren geht.
- Sie finden die Verwaltung unter *Profil → Sicherheit → Sicherheitsschlüssel*.
- Registrieren Sie am besten zwei Schlüssel, einen davon als Reserve.
- Beim Anmelden wählen Sie dann **Mit Sicherheitsschlüssel anmelden** oder geben wie gewohnt einen Code ein.

Sicherheitsschlüssel funktionieren nur auf der echten mandari-Adresse. Eine gefälschte Anmeldeseite kann sie deshalb nicht abgreifen.

## Aktive Sitzungen { #sitzungen }

Unter *Profil → Sicherheit* sehen Sie, auf welchen Geräten und Browsern Sie angemeldet sind. Einzelne Sitzungen beenden Sie dort, oder alle außer der aktuellen, etwa nach der Anmeldung an einem fremden Rechner. Ohne Abmeldung bleibt eine Sitzung bis zu 30 Tage bestehen.

## Sicherheitshinweise { #hinweise }

Wichtige Änderungen an Ihrem Konto melden wir Ihnen per E-Mail und auf der Sicherheitsseite: ein geändertes oder zurückgesetztes Passwort, ein ein- oder abgeschalteter zweiter Faktor und hinzugefügte oder entfernte Sicherheitsschlüssel. Haben Sie eine solche Änderung nicht selbst vorgenommen, ändern Sie sofort Ihr Passwort und wenden Sie sich an den Support.

## Ihre Daten { #daten }

Unter *Profil → Daten* gibt es zwei Aktionen:

- **Datenexport**: Sie lassen sich die Daten zusammenstellen, die in dieser Organisation zu Ihnen gespeichert sind, als JSON- oder PDF-Datei. Der Export läuft im Hintergrund, die Datei laden Sie anschließend auf derselben Seite herunter.
- **Mitgliedschaft beenden**: Nach Eingabe Ihres Passworts wird Ihre Mitgliedschaft in dieser Organisation deaktiviert. Sind Sie Eigentümerin oder Eigentümer der Organisation, übertragen Sie die Eigentümerschaft vorher an ein anderes Mitglied. Für die vollständige Löschung Ihres Kontos wenden Sie sich an den Support.

Was beim Löschen mit welchen Daten geschieht, beschreibt das [Löschkonzept](../datenschutz/loeschkonzept.md).
