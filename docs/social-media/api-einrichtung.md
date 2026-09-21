# Instagram-API einrichten: App anlegen und Token erzeugen

Diese Anleitung beschreibt die **einmalige** Einrichtung, damit die NEWS-App auf
Instagram posten darf: Meta Developer App anlegen, den Long-Lived Token erzeugen
und die Zugangsdaten dort ablegen, wo der Code sie sucht.

Verwandt: [`zugadangsdaten.md`](zugangsdaten.md) (Verwaltung von Passwort/2FA/Token
in KeePass) und [`insta.md`](../../insta.md) (Gesamtkonzept). Diese Datei enthält
**keine** echten Werte — die kommen nie ins Repo.

Der Flow ist heute schlank: Der **„Generate Token"-Button im Meta-Dashboard**
erledigt die ganze OAuth-Strecke. Ein selbstgebauter Login-Flow ist nicht nötig,
und es braucht **keine Facebook-Seite** (wir nutzen „Instagram API with Instagram
Login", nicht den alten Facebook-Login-Pfad).

## Vor dem Start

- Das Konto `@math_uni_freiburg` muss ein **Professional Account (Business)** sein:
  Instagram → Einstellungen → *Konto* → *Als Professional-Konto wechseln* →
  **Business**. Kostenlos und reversibel.
- Zugangsdaten und 2FA aus der KeePass-Datei bereithalten — im Token-Schritt meldest
  du dich am Instagram-Konto an (Login + 6-stelliger TOTP-Code).

## 1. Meta Developer App anlegen

Auf `developers.facebook.com`:

1. Oben rechts *My Apps* → **Create App**
2. **App name** (z. B. „mi-news-instagram") + Kontakt-E-Mail
   (`socialmedia@math.uni-freiburg.de`)
3. Use case: **„Manage messaging & content on Instagram"** (Kategorie
   *Content management*) → *Next* → App erstellen

## 2. Instagram-Produkt hinzufügen

1. Im App-Dashboard beim Produkt **Instagram** auf **Set up**
2. Linke Seitenleiste: **Instagram → API setup with Instagram Login**

## 3. Token generieren (das eigentliche „Durchklicken")

1. Im Panel *API setup with Instagram Login* erscheint dein Instagram-Benutzername
   → **Generate Token**
2. Es öffnet sich ein Instagram-Fenster → **Login + 2FA-Code** (aus KeePass) →
   im Zustimmungs-Dialog **alle Berechtigungen an lassen** (insb. „Auf Content
   zugreifen und diesen veröffentlichen" = `instagram_business_content_publish`) →
   **Zulassen**
3. Zurück im Dashboard steht der **Access Token** direkt unter dem Kontonamen →
   **kopieren** (in KeePass).

Das ist ein **Long-Lived Token, 60 Tage gültig** — danach hält ihn der wöchentliche
Refresh-Cron am Leben (§7).

## 4. Die drei statischen Werte holen

- **Instagram-App-ID** und **Instagram-App-Geheimcode**: im Panel *API setup with
  Instagram Login* (der Geheimcode erst nach Klick auf *Anzeigen*).
  *Achtung:* das ist **nicht** die Meta-App-ID aus der URL — es ist die eigene
  Instagram-App-ID.
- **Instagram User ID**: im Abschnitt *Zugriffstokens generieren* neben dem
  Kontonamen — oder per Terminal:

  ```
  curl -s "https://graph.instagram.com/me?fields=user_id,username&access_token=DEIN_TOKEN"
  ```

## 5. Eintragen — dort, wo der Code sie sucht

Nie im Git-Checkout: von dort wird deployt, ein Fehlgriff wäre einen Commit
entfernt. Warum die Token-Datei zusätzlich außerhalb des rsync-Ziels liegt:
siehe `netrc.example` und `misc/config.py`.

**`.netrc`** (nur die statischen Werte; Vorlage: `netrc.example`)
- lokal: `~/.netrc` · auf www2: `/usr/local/lib/mi-news/.netrc` (owner `www-data`, mode 600)

```
machine graph.instagram.com
  login <INSTAGRAM_APP_ID>
  account <INSTAGRAM_USER_ID>
  password <INSTAGRAM_APP_SECRET>
```

**`ig_token.json`** — **einmalig** anlegen (der Refresh-Job erneuert nur, er
bootstrappt nicht). Am einfachsten mit der vorhandenen Helferfunktion; sie schreibt
das korrekte Format (`expires_at`) atomar und mit mode 600:

```
venv/bin/python -c "from misc import instagram as ig; ig.speichere_token('DEIN_TOKEN', 60*24*3600)"
```

(`60*24*3600` = 60 Tage in Sekunden, die Gültigkeit eines frisch erzeugten Tokens.)

## 6. Prüfen (lokal)

```
venv/bin/python -c "from misc import instagram as ig; print('konfiguriert:', ig.is_configured(), '| Resttage:', ig.token_restlaufzeit())"
```

`konfiguriert: True` bedeutet: `.netrc` und ein lebender Token sind da — der
Button **„Auf Instagram veröffentlichen"** im Editor wird aktiv.

## 7. Token am Leben halten

Ein **wöchentlicher Cron-Job** ruft `bin/refresh_ig_token.py` auf. Auf www2 richten
das die **Sysadmins** ein (siehe §8).

**Das Skript existiert bereits:** `bin/refresh_ig_token.py` (ausführbar, im Repo).
Es prüft die Restlaufzeit, ruft `refresh_token()` und schreibt den neuen Token
atomar. Exit 0 = erneuert, Exit 1 = Fehler (kein/abgelaufener Token). Erfolg geht
nach **stdout**, Fehler nach **stderr** (relevant für E-Mail-Alarme, siehe unten).
Kein eigener Code nötig — nur die Cron-Zeile (§8) verweist darauf.

### Was passiert nach 59 Tagen?

**Im Normalbetrieb läuft der Token nie ab.** Jeder erfolgreiche Refresh verlängert
ihn um **weitere 60 Tage ab dem Refresh-Zeitpunkt**. Der Cron läuft **wöchentlich**,
setzt die Restlaufzeit also jeden Montag wieder auf ~60 Tage. Die „59 Tage" beim
Prüfen sind nur der *aktuelle* Momentwert. Der Token erneuert sich damit **unbegrenzt
selbst**.

**Der Failure-Fall:** Nur wenn der Refresh **60 Tage am Stück** nicht durchläuft
(≈ 8 verpasste Montage), läuft der Token ab und ist **endgültig verloren** (Metas
Regel: nach 60 Tagen ohne Refresh nicht mehr erneuerbar). Dann: im Dashboard einen
**neuen** Token erzeugen (§3) und mit `set_ig_token.py` neu ablegen (§8, Schritt 3).
Ein **abgelaufener** Token (Restlaufzeit < 0) wird dabei automatisch überschrieben —
`--force` ist nur bei einem noch gültigen Token nötig.

**Warum wöchentlich statt „kurz vor Ablauf":** Das gibt **~7–8 Rettungsversuche**,
bevor überhaupt etwas kaputtgeht. Bei monatlichem Lauf blieben nur zwei.

### Überwachung

- `refresh_ig_token.py` schreibt nach `/var/log/mi-news-token.log`
  (`sudo tail -n50 /var/log/mi-news-token.log`).
- `misc/config.py` kennt `ig_token_warn_days = 14` — Schwelle, ab der die App im
  Editor warnen soll.
- E-Mail-Alarm bei Fehlern: im Cron-Eintrag `2>&1` weglassen (dann geht stderr an
  Cron → Mail, sofern MTA/`MAILTO` eingerichtet).

## 8. Deployment auf www2 (Produktivbetrieb)

Die Abschnitte 5–6 beschreiben die Ablage **lokal** (zum Verifizieren). Auf **www2**
gelten Besonderheiten.

### Die Randbedingungen auf www2 (ermittelt Sept. 2026)

- **Hostname** ist exakt `www2` → in `misc/config.py` greift der `== "www2"`-Zweig.
  Die beiden Dateien liegen dort **nicht** am selben Ort:
  - **`.netrc`** neben dem Code, in **`/usr/local/lib/mi-news/.netrc`** — die
    Hauskonvention der Sysadmins, `mi-hp` hält es mit `/usr/local/lib/mi-hp/.netrc`
    genauso. (`misc/config.py` prüft zuerst diesen Pfad und fällt auf
    `/var/local/lib/mi-news/.netrc` zurück, falls die Datei später doch dorthin
    wandert.)
  - **`ig_token.json`** in **`/var/local/lib/mi-news/`**, also außerhalb des
    rsync-Ziels. Diese Datei wird laufend neu geschrieben, und ihr Verlust wäre
    endgültig — ein abgelaufener Token lässt sich nicht mehr erneuern.
    `/var/local`, nicht `/var/lib`: die App liegt unter `/usr/local/lib`, und die
    FHS trennt lokal installierte Software samt ihrer veränderlichen Daten von dem,
    was aus Distributionspaketen kommt.
- Alle Apps laufen als **`www-data`**; mi-news liegt in **`/usr/local/lib/mi-news`**
  (venv daneben, Start via `run.sh`). **mi-hp** wird über **Apache** ausgeliefert,
  Deploy via `deploy-hp.sh`.
- `flask-reader` (SSH-/Deploy-User) hat **kein sudo-Passwort** und darf per
  `NOPASSWD` **nur** die `deploy-*.sh`-Skripte, `tail` auf Apache-Logs und
  `systemctl start/status mongod`.

### Aufgabenteilung

Das **Deploy-Skript `deploy-mi-news.sh` gehört den Sysadmins und wird NICHT
verändert.** Daher:

- **flask-reader** deployt nur den **Code** wie gewohnt (`git pull` +
  `sudo deploy-mi-news.sh`) — damit landet der aktuelle `main` (inkl. `publish()`
  und `bin/refresh_ig_token.py`) in `/usr/local/lib/mi-news`.
- **Die Sysadmins** erledigen einmalig als root das Privilegierte: `.netrc` ablegen,
  initialen Token bootstrappen, Cron eintragen.

### Auftrag an die Sysadmins (einmalig, als root)

Die geheimen Werte (App-Geheimcode, Token) kommen sicher (KeePass), **nicht** per
Repo/Mail.

**1. Verzeichnis anlegen** — ✅ am 14.09.2026 angelegt.
```bash
install -d -o www-data -g www-data -m 700 /var/local/lib/mi-news
```
Es existiert derzeit als `drwxr-sr-x` (2755) statt 700. Die Geheimnisse selbst sind
dadurch nicht lesbar (die Dateien darin sind 600), aber jeder Account auf www2 kann
das Verzeichnis auflisten. Beim nächsten Handgriff mit root-Rechten bitte
`chmod 700` nachziehen.

**2. `.netrc` ablegen** — Inhalt (App-ID + User-ID nicht geheim, Geheimcode geheim):
```
machine graph.instagram.com
  login 1365354842045499
  account 17841414345604875
  password <INSTAGRAM_APP_GEHEIMCODE>
```
z. B. aus einer vorbereiteten Datei:
```bash
install -o www-data -g www-data -m 600 /pfad/zur/.netrc /usr/local/lib/mi-news/.netrc
```

**3. Initialen Token einmalig ablegen** mit `bin/set_ig_token.py` (der Cron erneuert
nur, er legt nicht an). Immer als **`www-data`** ausführen. Zwei Wege:

*Variante A* — die lokal erzeugte `ig_token.json` nach www2 kopieren und einspielen
(das Skript zieht `access_token` selbst heraus):
```bash
# lokal -> www2 kopieren (z. B. nach ~flask-reader/ig_token.json), dann:
sudo -u www-data /usr/local/lib/mi-news/venv/bin/python \
    /usr/local/lib/mi-news/bin/set_ig_token.py /pfad/zur/kopierten/ig_token.json
```

*Variante B* — Token via stdin (nicht als Argument, damit er nicht in `ps` auftaucht):
```bash
printf '%s' '<LONG_LIVED_TOKEN>' | sudo -u www-data \
    /usr/local/lib/mi-news/venv/bin/python \
    /usr/local/lib/mi-news/bin/set_ig_token.py
```

Beides schreibt `/var/local/lib/mi-news/ig_token.json` (mode 600, owner www-data). Ein
bereits vorhandener, **noch gültiger** Token wird ohne `--force` **nicht**
überschrieben (schützt den vom Cron rotierten Token).

**4. Cron-Eintrag** — die Zeile für die Crontab:

Variante A — Datei `/etc/cron.d/mi-news-token` (**mit** User-Feld, empfohlen):
```
17 3 * * 1 www-data /usr/local/lib/mi-news/venv/bin/python /usr/local/lib/mi-news/bin/refresh_ig_token.py --quiet
```

Variante B — User-Crontab via `crontab -u www-data -e` (**ohne** User-Feld):
```
17 3 * * 1 /usr/local/lib/mi-news/venv/bin/python /usr/local/lib/mi-news/bin/refresh_ig_token.py --quiet
```

Bedeutung der Felder: **jeden Montag um 03:17 Uhr** (`Min Std * * Wochentag`).

`--quiet` unterdrückt die Erfolgsmeldung; Fehler gehen unverändert nach stderr.
Damit gilt die übliche Cron-Arbeitsteilung: **keine Ausgabe = keine Mail**, und
eine Mail bedeutet immer, dass jemand etwas tun muss. Voraussetzung ist ein
MTA bzw. ein `MAILTO=` in der Crontab — ohne das verfällt die Meldung stumm, und
dann ist die Log-Variante die bessere Wahl.

Log-Variante (statt `--quiet`, wenn ihr den Nachweis wollt, dass der Job
überhaupt gelaufen ist — jeder Lauf schreibt dann eine Zeile):
```bash
install -o www-data -g www-data -m 640 /dev/null /var/log/mi-news-token.log
```
```
17 3 * * 1 www-data /usr/local/lib/mi-news/venv/bin/python /usr/local/lib/mi-news/bin/refresh_ig_token.py >> /var/log/mi-news-token.log 2>&1
```

### Verifikation (nach dem Provisionieren)

`sudo -u www-data …` ad-hoc ist für flask-reader **nicht** erlaubt. Prüfung daher
entweder durch einen Sysadmin:
```bash
sudo -u www-data /usr/local/lib/mi-news/venv/bin/python -c \
  "import sys; sys.path.insert(0,'/usr/local/lib/mi-news'); from misc import instagram as ig; print(ig.is_configured(), ig.token_restlaufzeit())"
```
→ erwartet `True 59`. **Oder** direkt im Editor: der Button „Auf Instagram
veröffentlichen" wird aktiv, sobald `is_configured()` True ist.

### mi-hp (öffentliche Bild-Route)

flask-reader deployt wie gewohnt:
```bash
cd ~/mi-hp && git checkout master && git pull
sudo /media/data/home/flask-reader/deploy-hp.sh
```
Danach prüfen, dass die Route öffentlich antwortet (404 bei unbekanntem Token ist
korrekt — die Route lebt, nur der Token existiert nicht):
```bash
curl -sI https://www.math.uni-freiburg.de/nlehre/insta/0000000000000000.jpg
sudo tail -n50 /var/log/apache2/error-flask.log     # bei Problemen
```

## Umsetzungsstand (Stand: 13. September 2026)

Erledigt und **live verifiziert**:
- Konto `@math_uni_freiburg` ist Business-Account.
- Meta Developer App „Mathematik, Uni Freiburg" (Meta-App-ID `2037884977613511`),
  Produkt „Instagram API with Instagram Login".
- Instagram-App-ID `1365354842045499`, Instagram-User-ID `17841414345604875`.
- Berechtigungen inkl. `instagram_business_content_publish` erteilt.
- Long-Lived Token erzeugt; **lokal** geprüft: `is_configured() = True`,
  Live-`/me` → HTTP 200, `math_uni_freiburg`.

## Checkliste zum Live-Gang

- [x] Konto ist Professional/Business
- [x] Meta Developer App angelegt, Instagram-Produkt + „API setup with Instagram Login"
- [x] Token generiert (60 Tage)
- [x] `.netrc`-Werte bekannt (App ID, IG User ID, App Secret)
- [x] `ig_token.json` lokal geschrieben, `is_configured()` → `True` (lokal)
- [x] mi-news (`main`) auf www2 deployt — 14.09.2026, Stand `86ad6a7`, Dienst neu gestartet
- [x] **Sysadmins:** `.netrc` abgelegt — 14.09.2026 unter
      `/usr/local/lib/mi-news/.netrc`; `misc/config.py` folgt diesem Pfad
- [x] **Sysadmins:** initiales `ig_token.json` abgelegt — 14.09.2026
- [x] **Sysadmins:** Cron-Eintrag angelegt (`/etc/cron.d/mi-news`) — siehe Nachträge unten
- [x] mi-hp (`master`) auf www2 deployt — Bild-Route live (404 auf unbekannten
      Token), Rechtsseiten unter `/nlehre/de/instagram/` liefern 200
- [x] Rat des/der Datenschutzbeauftragten eingeholt (Art. 35 Abs. 2 DSGVO) —
      Mail vom 14.07.2026, 15:02 Uhr; Original im Wortlaut in
      `mail-datenschutzbeauftragter.md` archiviert. Eine „Freigabe“ gibt es
      nicht: nachzuweisen ist, dass gefragt wurde, nicht, dass zugestimmt wurde.
- [ ] Antwort (oder ein Vermerk über die verstrichene Frist) in
      `mail-datenschutzbeauftragter.md` unter „Antwort“ nachgetragen
- [x] End-to-End-Testpost gemacht — 14.09.2026, 12:36 Uhr:
      <https://www.instagram.com/p/DdQ76Y3CIHK/>. Er bleibt stehen und ist
      damit der Auftaktbeitrag des Kanals. Kommentare nachweislich aus
      (`is_comment_enabled: false` über die API geprüft).
- [x] Link in der Instagram-Bio gesetzt (Sammelseite mit den Pflichtdokumenten)

### Offene Nachträge an die Sysadmins (Stand 14.09.2026)

Die `.netrc` ist **erledigt**: Sie liegt unter `/usr/local/lib/mi-news/.netrc`,
und `misc/config.py` sucht seit dem 14.09.2026 genau dort — die Hauskonvention
der Sysadmins (wie `mi-hp`) hat Vorrang vor dem ursprünglich geplanten Pfad.
Zwei Dinge bleiben dazu anzumerken:

- Das Code-Verzeichnis ist das rsync-Ziel von `deploy-mi-news.sh`. Solange die
  `--delete`-Zeile darin auskommentiert bleibt, überlebt die Datei jeden Deploy
  (verifiziert am 14.09.2026). Wird sie je scharf geschaltet, ist die `.netrc`
  weg und muss neu abgelegt werden — die Token-Datei liegt deshalb weiterhin
  außerhalb.
- Die Datei ist 601 Byte groß, also offenbar die vereinigte
  `~flask-reader/netrc` mit allen sechs Maschinen (LDAP, DAViCal, SWFR, DeepL,
  SMTP, Instagram). Nötig ist für mi-news nur der Block `graph.instagram.com`.
  Kein Fehler, aber mehr Zugangsdaten als die App braucht.

Offen sind noch:

1. **`--quiet` an die Cron-Zeile** anhängen (am 14.09.2026 an die Sysadmins
   gemeldet). Ohne das meldet sich der Job jeden Montag auch im Erfolgsfall
   per Mail.
2. **`MAILTO=` setzen** in `/etc/cron.d/mi-news`. Ein MTA ist vorhanden, aber
   ohne `MAILTO` adressiert Cron an `www-data`, und `/etc/aliases` existiert auf
   www2 nicht — die Fehlermeldung landet dann in einer Mailbox, in die niemand
   sieht. Das ist genau der Fall, für den sie gedacht ist.
3. **`chmod 700 /var/local/lib/mi-news`** — derzeit 2755. Betrifft nur noch
   die Token-Datei; die `.netrc` liegt inzwischen woanders.

## Was der erste Testpost ergeben hat (14.09.2026)

Die API-Kette lief auf Anhieb durch: Meta hat das Bild selbst von der
öffentlichen Route geholt, der Beitrag wurde veröffentlicht, die Kommentare
wurden abgeschaltet, und das Zwischenbild in `insta_bild` war danach wieder weg.
Zwei Fehler in der App sind dabei aufgefallen und behoben:

1. **Der Inhalt wurde beim Veröffentlichen nicht gespeichert.** Gepostet wurde
   der Formularstand, zurückgeschrieben nur `status`, `ig_media_id` und
   `published_at` — in der Datenbank blieb der alte Entwurf stehen. Der Eintrag
   ist aber der einzige Nachweis dessen, was veröffentlicht wurde. Jetzt
   schreiben beide Knöpfe denselben Stand.
2. **Ein Post ohne Inhalt ließ sich veröffentlichen**, und ein veröffentlichter
   Eintrag ließ sich löschen — beides Einbahnstraßen, weil der DELETE-Endpunkt
   der API unserem Zugang nicht offensteht. Jetzt sperrt ein fehlender
   Überschrift- oder Caption-Text den Post-Knopf, und gelöscht werden dürfen
   nur Entwürfe.

Der Datensatz des Testposts wurde nachträglich aus dem Beitrag rekonstruiert;
sein `kommentar`-Feld hält fest, welche Angabe woher stammt.

Stand: 14. September 2026
