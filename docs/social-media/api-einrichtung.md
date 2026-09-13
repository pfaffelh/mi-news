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

Warum außerhalb des Git-Checkouts und des rsync-Ziels: siehe `netrc.example` und
`misc/config.py`. Beim Deploy wird der Baum überschrieben; die Geheimnisse dürfen
das nicht mitbekommen.

**`.netrc`** (nur die statischen Werte; Vorlage: `netrc.example`)
- lokal: `~/.netrc` · auf www2: `/var/lib/mi-news/.netrc` (owner `www-data`, mode 600)

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

- **Hostname** ist exakt `www2` → in `misc/config.py` greift der `== "www2"`-Zweig,
  die App sucht die Secrets in **`/var/lib/mi-news/`** (absolut, **kein** Home).
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

**1. Verzeichnis anlegen**
```bash
install -d -o www-data -g www-data -m 700 /var/lib/mi-news
```

**2. `.netrc` ablegen** — Inhalt (App-ID + User-ID nicht geheim, Geheimcode geheim):
```
machine graph.instagram.com
  login 1365354842045499
  account 17841414345604875
  password <INSTAGRAM_APP_GEHEIMCODE>
```
z. B. aus einer vorbereiteten Datei:
```bash
install -o www-data -g www-data -m 600 /pfad/zur/.netrc /var/lib/mi-news/.netrc
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

Beides schreibt `/var/lib/mi-news/ig_token.json` (mode 600, owner www-data). Ein
bereits vorhandener, **noch gültiger** Token wird ohne `--force` **nicht**
überschrieben (schützt den vom Cron rotierten Token).

**4. Log-Datei anlegen** (www-data muss hineinschreiben können):
```bash
install -o www-data -g www-data -m 640 /dev/null /var/log/mi-news-token.log
```

**5. Cron-Eintrag** — die Zeile für die Crontab:

Variante A — Datei `/etc/cron.d/mi-news-token` (**mit** User-Feld, empfohlen):
```
17 3 * * 1 www-data /usr/local/lib/mi-news/venv/bin/python /usr/local/lib/mi-news/bin/refresh_ig_token.py >> /var/log/mi-news-token.log 2>&1
```

Variante B — User-Crontab via `crontab -u www-data -e` (**ohne** User-Feld):
```
17 3 * * 1 /usr/local/lib/mi-news/venv/bin/python /usr/local/lib/mi-news/bin/refresh_ig_token.py >> /var/log/mi-news-token.log 2>&1
```

Bedeutung der Felder: **jeden Montag um 03:17 Uhr** (`Min Std * * Wochentag`).
Für E-Mail-Alarm bei Fehlern das abschließende `2>&1` weglassen (dann geht stderr
an Cron → Mail, sofern ein MTA/`MAILTO` eingerichtet ist).

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
- [ ] mi-news (`main`) auf www2 deployt (`sudo deploy-mi-news.sh`)
- [ ] **Sysadmins:** `/var/lib/mi-news/.netrc` angelegt (owner www-data, 600)
- [ ] **Sysadmins:** initiales `ig_token.json` abgelegt (`bin/set_ig_token.py`)
- [ ] **Sysadmins:** Cron-Eintrag angelegt (§8, Schritt 5)
- [ ] mi-hp (`master`) auf www2 deployt (öffentliche Bild-Route erreichbar)
- [ ] Datenschutz-Freigabe liegt vor
- [ ] End-to-End-Testpost aufs eigene Konto gemacht

Stand: 13. September 2026
