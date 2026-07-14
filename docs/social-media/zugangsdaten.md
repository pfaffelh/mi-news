# Zugangsdaten und 2FA für den Instagram-Account

Diese Notiz beschreibt, **wie** die Geheimnisse des Instagram-Accounts verwaltet
werden — nicht, **was** sie sind. In diesem Repository stehen keine Passwörter,
keine TOTP-Seeds und keine Tokens. Wer diese Datei liest und Zugriff braucht,
wendet sich an die unten genannten Personen.

## Warum das nicht trivial ist

Zwei-Faktor-Authentifizierung ist dafür gebaut, ein Konto an *eine Person* zu
binden. Wir brauchen das Gegenteil: Der Account gehört der Universität und muss
Personalwechsel überstehen. Die Social-Media-Guidelines sagen das ausdrücklich —
„Accounts, die im Namen der Universität oder einer Organisationseinheit
eingerichtet werden, gehören der Universität", und beim Ausscheiden sind die
Administrationsrechte zu übergeben.

Deshalb darf der Zweitfaktor **nicht** auf dem Handy einer einzelnen Person liegen.

## Wo die Geheimnisse liegen

Das Institut hat keinen zentralen Passwortmanager. Wir verwenden daher eine
**KeePass-Datei** (`.kdbx`, KeePassXC — frei, kein Server, kein Dienst, keine
Datenschutzprüfung nötig).

- **Datei:** `mi-social-media.kdbx`
- **Ablageort:** «Institutslaufwerk/Nextcloud-Pfad eintragen»
- **Zugriff haben:** Carolin Mann, Thorsten Schmidt, Peter Pfaffelhuber
- **Master-Passwort:** lange Passphrase, **nicht per E-Mail verteilt** (mündlich
  oder auf Papier weitergegeben)
- **Backup der Datei:** «Ort eintragen» — die Datei *ist* das Geheimnis; geht sie
  verloren, ist der Account verloren

Inhalt der Datei:

| Eintrag | Zweck |
|---|---|
| Instagram-Passwort | Login `@math_uni_freiburg` |
| **TOTP-Seed** | KeePassXC erzeugt daraus die 6-stelligen 2FA-Codes |
| Backup-Codes (5 Stück) | Wiederherstellung, wenn TOTP nicht verfügbar |
| Meta-API-Token *(später)* | Long-Lived Token der NEWS-App, siehe [`insta.md`](../../insta.md) |

Zusätzlich liegen die **fünf Backup-Codes ausgedruckt** «Ort eintragen, z. B.
Sekretariat / Geschäftsführung» — Redundanz für den Fall, dass die Datei einmal
nicht erreichbar ist.

## Einrichtung der 2FA (einmalig)

In den Instagram-Einstellungen **„Authentifizierungs-App"** wählen, **nicht SMS**.
Instagram zeigt einen QR-Code und darunter einen **Text-Seed**. Dieser Seed — nicht
die App auf irgendeinem Handy — ist das eigentliche Geheimnis und gehört in die
KeePass-Datei. Danach die fünf Backup-Codes sichern.

## Die bewusste Abschwächung

Liegen Passwort und TOTP-Seed in derselben Datei, ist die Zwei-Faktor-Authentifizierung
effektiv wieder **ein** Faktor: Wer die Datei und ihr Master-Passwort hat, hat alles.

Das ist eine bewusste Entscheidung. Die Alternative — Zweitfaktor auf einem
persönlichen Handy — macht diese Person zum Single Point of Failure und
widerspricht der Vorgabe, dass der Account der Institution gehört. Der Preis ist,
dass die KeePass-Datei und ihr Ablageort ordentlich abgesichert sein müssen.

## Account-Recovery

Der eigentliche Wiederherstellungsweg von Instagram läuft über die hinterlegte
E-Mail-Adresse **socialmedia@math.uni-freiburg.de**. Deshalb muss diese Adresse ein
**Verteiler mit mindestens zwei Empfänger:innen** sein und nicht ein Alias auf ein
einzelnes Postfach — sonst hängt die Wiederherstellung doch wieder an einer Person.
Das steht so auch im [Nutzungskonzept](nutzungskonzept.md).

## Beim Ausscheiden einer beteiligten Person

**Beides ändern, nicht nur eins:**

1. Master-Passwort der KeePass-Datei
2. Instagram-Passwort (und damit auch neue Backup-Codes erzeugen)

Zusätzlich prüfen, ob die Person noch im Verteiler `socialmedia@` steht, und — sobald
es sie gibt — ob sie noch eine Admin-Rolle in der Meta Developer App hat.

## Offen

- **Rechenzentrum fragen**, ob die Universität einen Passwortmanager anbietet oder
  empfiehlt. Falls ja, ist das der bessere Weg als die Eigenbastelei, und die
  KeePass-Datei kann dorthin migriert werden.
- Die «…»-Platzhalter oben ausfüllen, sobald Ablageort und Backup feststehen.

Stand: Juli 2026
