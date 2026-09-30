---
title: Konto und Sicherheit
description: Passwort, Zwei-Faktor-Anmeldung mit Authenticator-App und Backup-Codes, Sicherheitsschlüssel und Passkeys, aktive Sitzungen, Datenexport und das Beenden der Mitgliedschaft in mandari Work.
---

# Konto und Sicherheit

In Work arbeitet ihr mit vertraulichen Inhalten: Positionen, Antragsentwürfe, interne Protokolle. Diese Seite zeigt, wie du dein Konto schützt. Alle Einstellungen findest du unter *Profil → Sicherheit*.

## Passwort { #passwort }

Ein neues Passwort muss

- mindestens 12 Zeichen lang sein,
- Groß- und Kleinbuchstaben sowie mindestens eine Ziffer enthalten,
- sich deutlich von deinem Namen und deiner E-Mail-Adresse unterscheiden und
- darf kein verbreitetes oder rein aus Ziffern bestehendes Passwort sein.

**Ändern**: Unter *Profil → Sicherheit* gibst du dein aktuelles Passwort und zweimal das neue ein. Du bleibst danach angemeldet.

**Vergessen**: Auf der Anmeldeseite führt „Passwort vergessen“ zu einem Formular. Du bekommst einen Link per E-Mail, über den du ein neues Passwort festlegst. Der Link ist nur begrenzt gültig und nur einmal verwendbar.

!!! tip
    Ein Passwort-Manager erzeugt und merkt sich lange, zufällige Passwörter. Verwende dein mandari-Passwort nirgendwo sonst.

## Zwei-Faktor-Anmeldung { #zwei-faktor }

Mit der Zwei-Faktor-Anmeldung brauchst du beim Anmelden neben dem Passwort einen zweiten Nachweis: einen sechsstelligen Code aus einer Authenticator-App auf deinem Smartphone oder einen Sicherheitsschlüssel. Wer nur dein Passwort kennt, kommt so nicht in dein Konto.

### Einrichten { #zwei-faktor-einrichten }

1. Installiere eine Authenticator-App, zum Beispiel die App deines Passwort-Managers oder eine der verbreiteten Authenticator-Apps für iOS und Android.
2. Öffne *Profil → Sicherheit* und wähle **2FA einrichten**.
3. Scanne den QR-Code mit der App. Alternativ gibst du den angezeigten Schlüssel von Hand ein.
4. Gib den sechsstelligen Code aus der App ein, um die Einrichtung zu bestätigen.
5. Speichere die **Backup-Codes** sicher, etwa im Passwort-Manager oder ausgedruckt.

### Backup-Codes { #backup-codes }

Bei der Einrichtung bekommst du zehn Backup-Codes. Jeder funktioniert genau einmal anstelle des Codes aus der App, zum Beispiel wenn du dein Smartphone verloren hast. Unter *Profil → Sicherheit → Backup-Codes* erzeugst du mit deinem Passwort neue Codes, die alten werden dabei ungültig.

### Wann ist sie Pflicht? { #zwei-faktor-pflicht }

Die Zwei-Faktor-Anmeldung ist vorgeschrieben

- für Mitglieder mit der Administrator-Rolle,
- für Rollen, bei denen eure Organisation „2FA erforderlich“ eingestellt hat, und
- für alle Mitglieder, wenn eure Organisation sie für alle verlangt.

Fehlt der zweite Faktor, führt dich die Anmeldung direkt zur Einrichtung. Ist er für dich vorgeschrieben, kannst du ihn nicht abschalten. Sonst lässt er sich unter *Profil → Sicherheit* mit deinem Passwort deaktivieren, wir raten aber davon ab.

### Kein Zugriff mehr auf die App? { #zwei-faktor-verloren }

Melde dich mit einem Backup-Code an und richte die App auf dem neuen Gerät neu ein. Hast du keine Backup-Codes mehr, schreib unserem Support an <support@mandari.de>. Nachdem wir geprüft haben, dass die Anfrage wirklich von dir kommt, setzen wir den zweiten Faktor zurück. Du bekommst darüber eine E-Mail.

## Sicherheitsschlüssel und Passkeys { #sicherheitsschluessel }

Zusätzlich zur Authenticator-App kannst du Sicherheitsschlüssel registrieren: einen Hardware-Schlüssel wie einen YubiKey, einen Passkey oder die Entsperrung deines Geräts per Fingerabdruck oder Gesichtserkennung.

- Voraussetzung ist eine eingerichtete Authenticator-App. Sie bleibt zusammen mit den Backup-Codes dein Rückfall, falls ein Schlüssel verloren geht.
- Du findest die Verwaltung unter *Profil → Sicherheit → Sicherheitsschlüssel*.
- Registriere am besten zwei Schlüssel, einen davon als Reserve.
- Beim Anmelden wählst du dann **Mit Sicherheitsschlüssel anmelden** oder gibst wie gewohnt einen Code ein.

Sicherheitsschlüssel funktionieren nur auf der echten mandari-Adresse. Eine gefälschte Anmeldeseite kann sie deshalb nicht abgreifen.

## Aktive Sitzungen { #sitzungen }

Unter *Profil → Sicherheit* siehst du, auf welchen Geräten und Browsern du angemeldet bist. Einzelne Sitzungen beendest du dort, oder alle außer der aktuellen, etwa nach der Anmeldung an einem fremden Rechner. Ohne Abmeldung bleibt eine Sitzung bis zu 30 Tage bestehen.

## Sicherheitshinweise { #hinweise }

Wichtige Änderungen an deinem Konto melden wir dir per E-Mail und auf der Sicherheitsseite: ein geändertes oder zurückgesetztes Passwort, ein ein- oder abgeschalteter zweiter Faktor und hinzugefügte oder entfernte Sicherheitsschlüssel. Hast du eine solche Änderung nicht selbst vorgenommen, ändere sofort dein Passwort und wende dich an den Support.

## Deine Daten { #daten }

Unter *Profil → Daten* gibt es zwei Aktionen:

- **Datenexport**: Du lässt dir die Daten zusammenstellen, die in dieser Organisation zu dir gespeichert sind, als JSON- oder PDF-Datei. Der Export läuft im Hintergrund, die Datei lädst du anschließend auf derselben Seite herunter.
- **Mitgliedschaft beenden**: Nach Eingabe deines Passworts wird deine Mitgliedschaft in dieser Organisation deaktiviert. Bist du Eigentümerin oder Eigentümer der Organisation, überträgst du die Eigentümerschaft vorher an ein anderes Mitglied. Für die vollständige Löschung deines Kontos wende dich an den Support.

Was beim Löschen mit welchen Daten geschieht, beschreibt das [Löschkonzept](../datenschutz/loeschkonzept.md).
