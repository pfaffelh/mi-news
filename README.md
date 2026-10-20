# mi-news — die Redaktionsapp des Mathematischen Instituts

Mit dieser App pflegt die Redaktion alles, was am Institut „Neuigkeit" heißt:
Meldungen für den Monitor im Erdgeschoss und für die beiden Webseiten, das
Wochenprogramm der Vortragsreihen und die Beiträge für den Instagram-Kanal.
Sie ist eine Streamlit-App (Python) und arbeitet auf einer lokalen MongoDB.

Die App **zeigt die Inhalte nicht selbst an**. Sie schreibt sie in die
Datenbank; ausgeliefert werden sie vom Repo `mi-hp` (Flask, über
Apache) und bei Instagram von Meta. Wer etwas an der Darstellung ändern will,
ist hier falsch.

| Was | Wo es erscheint |
|---|---|
| News, Tag „Monitor" | [Bildschirm im EG](https://www.math.uni-freiburg.de/nlehre/monitor/) — zum Ausprobieren der [Testmonitor](https://www.math.uni-freiburg.de/nlehre/monitortest/) |
| News, Tag „Institut" | [Institutshomepage](https://www.math.uni-freiburg.de) |
| News, Tag „Lehre" | [Lehre-Seiten](https://www.math.uni-freiburg.de/nlehre/de/) |
| Vorträge | [Wochenprogramm](https://www.math.uni-freiburg.de/wochenprogramm/) |
| Instagram-Posts | [@math_uni_freiburg](https://www.instagram.com/math_uni_freiburg/) |

Die Tags einer News stehen in `misc/config.py` (`alltags`) und entscheiden
allein darüber, wo sie auftaucht. Sichtbar wird sie erst, wenn zusätzlich
„Veröffentlicht" gesetzt ist und das Anzeigedatum passt — Monitor und Homepage
haben dafür getrennte Zeiträume.

Die Reihenfolge legt mi-hp fest (`utils/util_news.py`). Auf den Homepages
steht die News mit dem spätesten `home.start` oben; `rang` entscheidet nur bei
gleichem Start. Der Monitor sortiert dagegen noch rein nach `rang`. Den
vergibt mi-news beim Anlegen und Kopieren als kleinsten Wert minus 1,
beim Bearbeiten bleibt er unverändert. Die Übersicht in `pages/00_New.py`
sortiert wie die Homepage und färbt die Datumszelle grün, wenn die News gerade
online ist, und orange, wenn sie im Zeitraum liegt, aber nicht veröffentlicht ist.

## Lokal starten

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/streamlit run NEWS.py
```

Vorausgesetzt ist eine **lokale MongoDB** auf `localhost:27017` mit den
Datenbanken `news` (Inhalte) und `user` (Konten und Gruppen). Einen brauchbaren
Datenstand holt man sich am einfachsten aus der Produktion:

```bash
cd mongo && ./pull_mongo.sh     # mongodump auf www2, scp, mongorestore -- lokal mit --drop
```

Zwei Stolpersteine beim Einrichten:

- **`python-ldap`** wird beim Installieren übersetzt und braucht dafür die
  Entwicklungspakete von OpenLDAP und Cyrus-SASL (Debian/Ubuntu:
  `libldap2-dev`, `libsasl2-dev`).
- **Die Anmeldung geht nur im Uni-Netz oder per VPN** — authentifiziert wird
  gegen `ldaps://ldap.uni-freiburg.de`. Ohne Netz sieht es wie ein falsches
  Passwort aus; die Fehlermeldung im Login sagt es dazu.

**Pillow** wird in den Seiten direkt benutzt, steht aber nicht in der
`requirements.txt` — es kommt bisher als Abhängigkeit von Streamlit mit. Wer die
Versionen streng festnageln will, trägt es dort nach.

## Anmeldung und Rechte

Zwei Hürden, beide in `misc/tools.py`:

1. `authenticate()` prüft Kennung und Passwort per LDAP-Bind gegen den
   RZ-Server. Die App speichert kein Passwort.
2. `can_edit()` verlangt, dass die Kennung in der Datenbank `user` Mitglied der
   Gruppe **`news`** ist (der Name steht als `app_name` in `misc/config.py`).

Wer sich anmelden kann, darf alles — feinere Rollen gibt es nicht.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `NEWS.py` | Einstiegsseite, nichts als der Login |
| `pages/` | Die eigentlichen Seiten, von Streamlit nach Dateinamen sortiert |
| `misc/config.py` | Alle Einstellungen: LDAP, MongoDB, CD-Farben, Instagram-Grenzwerte, Pfade der Zugangsdaten |
| `misc/tools.py` | Anmeldung, Navigation, Darstellung einzelner Datensätze |
| `misc/util.py` | Session-State, Datenbankverbindung, Logging |
| `misc/instagram.py` | Bild-Rendering und die Graph-API (Container anlegen, veröffentlichen, Kommentare abschalten) |
| `misc/css_styles.py` | Nachbesserungen am Streamlit-Aussehen |
| `bin/` | Skripte für den Cron und die Einrichtung (siehe unten) |
| `mongo/` | Schemata, Migrationen, Backup-Helfer |
| `static/` | CD-Logos, Siegel, Vierblatt, die Hausschrift Arimo |
| `docs/` | Pflichtdokumente des Instagram-Kanals und die Werbemittel |

Die Seitenleiste wird **von Hand** gebaut (`tools.display_navigation()`); die
eingebaute Navigation von Streamlit ist in `.streamlit/config.toml` abgeschaltet.
Wer eine Seite hinzufügt, muss sie dort selbst eintragen, sonst ist sie nur über
ihre URL erreichbar. So steht es gerade um `pages/02_Carouselnews.py` und
`03_Carouselnews_edit.py`: Der Link ist auskommentiert, der Code lebt noch.

## Die Datenbank

Alles liegt in der Datenbank `news`:

| Collection | Inhalt |
|---|---|
| `news` | Die Meldungen, mit getrennten Feldern und Zeiträumen für Monitor und Homepage |
| `carouselnews` | Lauftexte oben im Monitor |
| `bild` | Die Bilder selbst, als Binärdaten in der Datenbank — nicht im Dateisystem |
| `vortragsreihe`, `vortrag` | Das Wochenprogramm |
| `instapost` | Instagram-Beiträge. Eigenständig, nicht an eine News gehängt: Bild und Text sind meist andere, die Caption ist länger |
| `insta_bild` | Kurzlebige Ablage für das gerenderte Post-Bild, mit TTL-Index (siehe unten) |

Die Kurznamen in `config.kurznamen` sind feste Vortragsreihen und lassen sich in
der App nicht löschen.

**Schema-Änderungen** laufen über zwei Dateien pro Stichtag in `mongo/`:
`schemaYYYYMMDD.py` beschreibt den Validator, `changeYYYYMMDD.py` spielt ihn ein
und migriert vorhandene Daten. Die Änderungsskripte sind idempotent und lassen
sich gefahrlos mehrfach laufen lassen; im Kopf jeder Datei steht, was sich
gegenüber dem Vorgänger ändert und warum. Die jüngsten sind die vom 04.10.2026.

## Instagram

Der Weg eines Posts ist länger als man denkt, weil die Graph-API **keinen
Bild-Upload kennt** — Meta lädt das Bild selbst von einer öffentlichen URL:

1. mi-news rendert das JPEG und legt es unter einem Token in `insta_bild` ab.
2. `mi-hp` liefert es unter `/nlehre/insta/<token>.jpg` öffentlich aus.
3. mi-news legt den Media-Container an, wartet auf `FINISHED`, veröffentlicht
   und **schaltet die Kommentare ab** — das ist keine Kür, sondern in den
   Pflichtdokumenten des Kanals zugesagt.
4. Das Zwischenbild wird gelöscht; der TTL-Index ist nur die Rückfallebene.

Posts lassen sich für einen Zeitpunkt vormerken. Veröffentlicht werden sie
**nicht** von der App — die läuft nur, solange jemand die Seite offen hat —,
sondern von `bin/post_geplante.py` aus dem Cron.

Hintergrund, Entscheidungen und offene Punkte stehen in
[`insta.md`](insta.md); die Einrichtung von Meta-App und Token in
[`docs/social-media/api-einrichtung.md`](docs/social-media/api-einrichtung.md).

## Betrieb auf www2

Deployt wird mit

```bash
./deploy.sh      # ssh flask-reader@www2: git pull, dann sudo deploy-mi-news.sh
```

Das Skript `deploy-mi-news.sh` auf dem Server **gehört den Sysadmins und wird
nicht verändert.** Die App liegt dort in `/usr/local/lib/mi-news` und läuft als
`www-data`.

Zwei Cron-Einträge gehören dazu (`/etc/cron.d/mi-news`):

```cron
17 3 * * 1   www-data …/venv/bin/python …/bin/refresh_ig_token.py --quiet
*/15 * * * * www-data …/venv/bin/python …/bin/post_geplante.py --quiet
```

Der erste hält den Instagram-Token am Leben: Er gilt 60 Tage und lässt sich nur
erneuern, solange er noch lebt — ein abgelaufener Token ist endgültig verloren.
Wöchentlich statt monatlich, damit der Job siebenmal scheitern darf, bevor
etwas kaputtgeht. Der zweite veröffentlicht fällige geplante Posts.

Beide schweigen im Erfolgsfall und melden sich per Mail, wenn etwas zu tun ist —
das setzt ein `MAILTO=` in derselben Datei voraus. Die vollständigen Zeilen mit
Begründung stehen in
[`api-einrichtung.md`](docs/social-media/api-einrichtung.md) (§8).

### Zugangsdaten

**Nichts davon liegt im Repo**, und nichts davon gehört hinein — das
Code-Verzeichnis ist zugleich das rsync-Ziel des Deploys.

| | lokal | auf www2 |
|---|---|---|
| App-ID, App-Secret, IG-User-ID | `~/.netrc` | `/usr/local/lib/mi-news/.netrc` |
| Long-Lived Token | `~/.mi-news/ig_token.json` | `/var/local/lib/mi-news/ig_token.json` |

Der Aufbau der `.netrc` steht in [`netrc.example`](netrc.example). Die beiden
Dateien sind getrennt, weil die eine sich nie ändert und die andere alle 60 Tage
neu geschrieben wird: Ein fehlerhafter Rewrite in der `.netrc` würde die
LDAP-, SMTP- und DeepL-Zugänge mitreißen.

Ohne diese Dateien läuft die App ganz normal, nur der Instagram-Teil ist
abgeschaltet (`instagram.is_configured()` ist dann `False`).

## Skripte in `bin/`

| Skript | Wozu |
|---|---|
| `post_geplante.py` | Fällige geplante Posts veröffentlichen. Gehört in den Cron; `--dry-run` und `--probelauf` posten nichts |
| `refresh_ig_token.py` | Den Token erneuern. Wöchentlich im Cron |
| `set_ig_token.py` | Den ersten Token ablegen. Einmalig, von Hand |
| `render_ig_hintergruende.py` | Die CD-Hintergründe als PNG herausschreiben, etwa für Entwürfe außerhalb der App |

Jedes Skript erklärt im Docstring, was es tut und wie es aufgerufen wird.

## Weiterführendes

- [`insta.md`](insta.md) — Gesamtkonzept des Instagram-Kanals, technisch wie
  organisatorisch. Die längste Datei im Repo und die beste Quelle für das „warum
  eigentlich so".
- [`docs/social-media/`](docs/social-media/) — die Pflichtdokumente des Kanals
  (Nutzungskonzept, Datenschutzerklärung, DSFA, Netiquette, Disclaimer) und die
  API-Einrichtung. Die Texte sind zugleich als Webseiten in `mi-hp` veröffentlicht;
  Änderungen müssen an beiden Stellen nachgezogen werden.
- [`docs/poster/`](docs/poster/) — Aushang und Postkarte für den Kanal (LaTeX).
- In der App selbst: die Seite **Dokumentation** erklärt der Redaktion den
  Arbeitsablauf.
