# Plan: News als Instagram-Post veröffentlichen

Ziel: In der bestehenden Streamlit-News-App soll man bei jeder News optional
einen Instagram-Post erzeugen können. Bild in korrekter Größe, editierbarer
Text mit Live-Vorschau, Veröffentlichung über die Instagram-API.

Branch: `instagram`

---

## 1. Welcher Instagram-Account? Wer beantragt was?

Instagram lässt **kein automatisches Posten von privaten Accounts** zu; nötig ist
ein **Instagram Professional Account**. Die Kontenkette ist aber deutlich kürzer
als früher — siehe den Kasten unten.

> **Korrigiert (verifiziert gegen die Meta-Doku, Juli 2026).** Dieser Abschnitt
> hat ursprünglich behauptet, ein Instagram-Business-Account müsse zwingend mit
> einer **Facebook-Seite** verknüpft sein. Das galt für die klassische
> Instagram-Graph-API („Instagram API with Facebook Login"). Seit Juli 2024 gibt
> es daneben die **„Instagram API with Instagram Login"**, und dort steht
> ausdrücklich: *„This API setup does not require a Facebook Page to be linked to
> the Instagram professional account."* Sie unterstützt Content Publishing und ist
> für uns der richtige Weg. Damit entfallen Facebook-Seite und Business Portfolio
> als technische Voraussetzung.
>
> Quellen: [Instagram Platform –
> Overview](https://developers.facebook.com/docs/instagram-platform/overview/),
> [Instagram API with Instagram
> Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/),
> [Content
> Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)

### Benötigte Konten (Kette)

| # | Was | Zweck | Wer / Hinweis |
|---|-----|-------|---------------|
| 1 | **Instagram Professional Account** (Typ *Business*, nicht *Creator*) | Das eigentliche Konto `@math_uni_freiburg` des Instituts | Anlegen auf die **institutionelle Funktions-Mail**; in den Einstellungen auf „Professional / Business" umstellen (kostenlos, reversibel). |
| 2 | **Meta Developer App** (Typ *Business*) | Die technische App, die die API-Calls macht und den Access-Token trägt | Auf `developers.facebook.com` anlegen, Produkt „Instagram" → *Instagram API with Instagram Login* hinzufügen. |
| 3 | **Long-Lived Access Token** | Token, den die NEWS-App zum Posten benutzt | Direkt im **App-Dashboard** erzeugbar (kein Login-Flow nötig). Gültig **60 Tage**, muss erneuert werden — siehe unten. |

**Nicht (mehr) nötig:** Facebook-Seite, Meta Business Portfolio, Business
Verification, App Review.

Ein **Business Portfolio** (`business.facebook.com`) bleibt trotzdem sinnvoll —
nicht für die API, sondern für die **Rollenverwaltung**: Instagram selbst kennt
nur einen einzigen Login, und Passwörter im Institut herumzureichen ist genau die
Übergabefalle, die die Uni-Guidelines mit „Accounts gehören der Universität"
adressieren. Über das Portfolio bekommen Personen Zugriff über ihre *eigenen*
Logins und lassen sich sauber wieder entfernen.

### Benötigte Permissions

- `instagram_business_basic`
- `instagram_business_content_publish` ← Kernberechtigung fürs Posten
- `instagram_business_manage_comments` ← **zwingend nötig**, um Kommentare
  abzuschalten (siehe „Kommentare müssen aus" weiter unten). Leicht zu übersehen,
  weil es nach einer Funktion klingt, die wir gar nicht wollen.

> **Achtung, alte Scopes sind tot:** `instagram_basic`, `instagram_content_publish`
> und `pages_read_engagement` gehören zum Facebook-Login-Pfad; die alten
> Scope-Werte wurden am **27.01.2025 abgeschaltet**. Nicht mehr verwenden.

### App Review: nicht nötig — aber aus einem anderen Grund als gedacht

Die ursprüngliche Einschätzung („keine App Review nötig") **stimmt**, die
Begründung war aber falsch. Es liegt nicht am *Development-Modus mit
Tester-Rollen*, sondern an der Zugriffsstufe:

- **Standard Access** genügt, wenn die App *„only serves your Instagram
  professional account or an account you manage"* — also genau unser Fall.
- **Advanced Access** (mit App Review **und** Business Verification, 2–4 Wochen)
  braucht man erst, wenn die App auf **fremde** Konten postet.

Da wir ausschließlich auf unser eigenes Institutskonto posten, reicht Standard
Access. Wir brauchen deshalb auch **keinen OAuth-Login-Flow** in der NEWS-App:
Der Token wird einmal im App-Dashboard erzeugt und als Secret hinterlegt.

### Betriebsrisiko: der Token läuft nach 60 Tagen ab

Der wichtigste operative Punkt, der bisher fehlte. Tokens aus dem App-Dashboard
sind **long-lived und 60 Tage gültig** (die aus dem Business-Login-Flow sogar nur
1 Stunde). Ohne Erneuerung hört das Posten nach zwei Monaten **stillschweigend**
auf.

Zu planen ist daher ein **Token-Refresh** (`GET /refresh_access_token` mit
`grant_type=ig_refresh_token` gegen `graph.instagram.com`), der den Token
rechtzeitig vor Ablauf verlängert — als Cronjob auf `www2` oder beim App-Start,
plus eine sichtbare Warnung im Editor, wenn der Token in weniger als *n* Tagen
abläuft. Ein Token, der klaglos abläuft, ist die wahrscheinlichste Ursache dafür,
dass diese Integration in einem Jahr nicht mehr funktioniert.

### Kommentare müssen aus — und das kostet einen dritten API-Call

**Das betrifft das Interface direkt.** Unsere veröffentlichten Pflichtdokumente
([Nutzungskonzept](docs/social-media/nutzungskonzept.md),
[Datenschutzerklärung](docs/social-media/datenschutzerklaerung.md),
[DSFA](docs/social-media/dsfa.md)) sagen an drei Stellen zu, dass die
**Kommentarfunktion deaktiviert** ist — und die DSFA stützt ihre Risikobewertung
ausdrücklich mit darauf. Diese Zusage muss die App technisch einlösen; sie darf
nicht an der Disziplin der postenden Person hängen.

**Verifiziert gegen die Meta-Doku (Juli 2026):**

- Es gibt **keinen** Kommentar-Parameter beim Erstellen des Containers
  (`POST /media`). Die dort erlaubten Felder sind `image_url`, `media_type`,
  `caption`, `alt_text`, `is_carousel_item`, `user_tags`, `is_ai_generated`,
  `is_paid_partnership`, `branded_content_sponsor_ids` — kein
  `comment_enabled`.
- Es gibt auch keinen Parameter bei `POST /media_publish`.
- Kommentare lassen sich **nur nachträglich am fertigen Beitrag** abschalten:

  ```
  POST https://graph.instagram.com/v25.0/<IG_MEDIA_ID>
       ?comment_enabled=false
       &access_token=<TOKEN>
  → {"success": true}
  ```

- Dafür braucht die App die Permission **`instagram_business_manage_comments`**.
- Kontrollierbar ist das Ergebnis über das GET-Feld **`is_comment_enabled`** am
  Media-Objekt. (`comment_enabled` gibt es nur als POST-Parameter, nicht als
  lesbares Feld — beim Nachprüfen leicht zu verwechseln.)
- Es gibt **keinen kontoweiten Schalter**, weder in der App noch in der API. Auch
  manuell muss man Kommentare bei jedem einzelnen Beitrag abschalten.

**Der Posting-Flow ist damit dreistufig, nicht zweistufig:**

1. `POST /media` → Container-ID
2. `POST /media_publish` → **Media-ID**, Beitrag ist live
3. `POST /<media-id>?comment_enabled=false` → Kommentare aus

**Bekannte Lücke:** Zwischen Schritt 2 und 3 ist der Beitrag für einige Sekunden
mit *offenen* Kommentaren live. Das lässt sich mit der API nicht vermeiden — es
gibt keinen Weg, den Beitrag von vornherein ohne Kommentare zu veröffentlichen.
Praktisch ist das Fenster winzig, aber es ist nicht null; wer das für relevant
hält, muss den Kanal manuell bespielen (dort ist es allerdings genauso).

**Anforderungen ans Interface, die daraus folgen:**

- Schritt 3 gehört **fest in die Publish-Funktion**, nicht in einen optionalen
  Haken. Es darf keinen Pfad geben, auf dem ein Beitrag mit offenen Kommentaren
  stehen bleibt.
- Schlägt Schritt 3 fehl (Netzwerk, Token, Rate Limit), muss das **laut** scheitern:
  Fehlermeldung im Editor, Retry, und der Beitrag ist als „Kommentare offen"
  markiert, bis es geklappt hat. Ein stiller Fehlschlag macht unsere DSFA falsch.
- Sinnvoll wäre ein **Nachlauf-Check**, der per `GET ?fields=is_comment_enabled`
  über die letzten Beiträge geht und meldet, wenn bei einem die Kommentare offen
  sind — als Cronjob oder als Anzeige im Editor. Das fängt auch Beiträge ab, die
  jemand von Hand über die Instagram-App gepostet hat.

### Weitere harte Grenzen

- **Host ist `graph.instagram.com`**, nicht `graph.facebook.com` (der gehört zum
  Facebook-Login-Pfad).
- **Rate Limit: max. 100 per API veröffentlichte Posts pro 24 Stunden.** Für uns
  völlig unkritisch (ein Karussell zählt als ein Post).

### Wer sollte das beantragen? — Empfehlung
Das ist **keine rein technische, sondern eine institutionelle/Marken-Frage**.
Die Konten repräsentieren offiziell das Mathematische Institut.

1. **Kontoinhaber = Institut, nicht Privatperson.** Der Instagram-Account (und ein
   etwaiges Business-Portfolio) muss auf einer **institutionellen Funktions-Mail**
   laufen (z. B. `oeffentlichkeitsarbeit@math.uni-freiburg.de` oder ein eigens
   dafür angelegtes Postfach), damit die Konten beim Personalwechsel nicht
   verloren gehen. **Kein privater Google/Facebook-Account.** Das ist der eine
   Schritt, der sich später nicht mehr sauber reparieren lässt.
2. **Antragsteller / Verantwortliche:** Geschäftsführung des Instituts bzw. die
   Person, die für Öffentlichkeitsarbeit / Web zuständig ist. Ggf. Abstimmung
   mit der **zentralen Presse-/Öffentlichkeitsarbeit der Uni Freiburg** — die Uni
   hat Social-Media-Guidelines und ggf. schon ein Meta-Business-Portfolio, unter
   dem das Institut als Asset laufen kann.
3. **Datenschutz (wichtig an einer Uni):** Vor dem Livegang sind fünf Dokumente
   Pflicht — Nutzungskonzept, Datenschutzerklärung, DSFA, Netiquette, Disclaimer —
   und müssen sichtbar im Profil verlinkt sein. Entwürfe liegen in
   [`docs/social-media/`](docs/social-media/README.md). Das ist ein
   Freigabe-Schritt, kein Code-Schritt, aber er gehört in die Planung.
4. **Technischer Admin (Rolle in der Meta-App):** Der/die App-Betreiber (du) wird
   als Admin/Developer in der Meta Developer App eingetragen, um Token zu erzeugen
   und zu erneuern.

**Konkrete Reihenfolge zum Beantragen:**
1. Zustimmung der Geschäftsführenden Direktion einholen; klären, ob es schon einen
   Insta-Auftritt des Instituts gibt und ob die Uni ein Meta-Business-Portfolio hat,
   unter dem wir als Asset laufen können.
2. Institutionelle Funktions-Mail bereitstellen (Rechenzentrum / RZ-Ticket).
3. Auf dieser Mail: Instagram-Account `@math_uni_freiburg` anlegen, auf
   *Professional / Business* umstellen, 2FA aktivieren.
4. Die fünf Pflichtdokumente freigeben lassen, auf `math.uni-freiburg.de`
   veröffentlichen und im Profil verlinken; Account über das
   [Uni-Formular](https://uni-freiburg.de/formulare/anmeldung-social-media-account/)
   melden.
5. Meta Developer App (Typ *Business*) anlegen, Produkt *Instagram API with
   Instagram Login* hinzufügen, technische Admins eintragen, Long-Lived Token
   erzeugen — und **den Token-Refresh gleich mitbauen**.

---

## 2. Technische Rahmenbedingungen der Instagram-API (Stand 2026)

Die zentrale Hürde für **unsere** App:

### 2a. Bild muss über eine öffentliche URL erreichbar sein
Der Publishing-Flow ist zweistufig:
1. `POST /{ig-user-id}/media`  → erzeugt einen *Media-Container*; man übergibt
   **`image_url` = eine öffentlich per HTTPS erreichbare Bilddatei** und die
   `caption` (den Text). Meta lädt das Bild **selbst von dieser URL herunter** —
   es gibt **keinen direkten Datei-Upload**.
2. `POST /{ig-user-id}/media_publish` mit der Container-ID → Post geht live.

**Ausgangslage / Topologie** (aus `deploy.sh`, `mongo/pull_mongo.sh`, `config.py`):
- Die produktive MongoDB mit den Bild-Blobs (`bild.data`) liegt auf dem Host
  **`www2` = `www.math.uni-freiburg.de`**, also dem **öffentlichen** Webserver.
- Auf `www2` läuft bereits eine **Flask-App** (User `flask-reader`, separates Repo
  **`mi-hp`**), die die öffentliche Homepage `…/nlehre/…` rendert — **inklusive der
  News-Bilder** aus derselben DB.
- Diese Streamlit-Editor-App läuft ebenfalls auf `www2` gegen `localhost:27017`,
  ist aber **nur per Uni-VPN** erreichbar.

**Kernpunkt:** *Wer den Meta-API-Call macht* und *wer das Bild an Meta ausliefert*
sind zwei verschiedene Dinge.
- **Ausgehende Calls sind unkritisch:** Das VPN blockt nur eingehenden Verkehr.
  Die Editor-App kann Metas Graph-API von hinter dem VPN aus aufrufen.
- **Öffentlich erreichbar muss nur die `image_url` sein** — und dafür gibt es mit
  `www2` bereits einen öffentlichen Server, der ohnehin schon Bild-Blobs aus
  derselben DB ausliefert. Meta erreicht `www2`, nur die Editor-App selbst nicht.

### Gewählte Lösung — Option A: öffentliche Bild-Route in `mi-hp` (auf www2)
1. **Editor (hinter VPN):** schneidet das Bild auf ein zulässiges Insta-Format
   (Default 1080×1350) zu und legt das gerenderte JPEG in Mongo ab — Feld
   `news.instagram.rendered` (binData) oder Mini-Collection `insta_bild` — mit
   einem **unratbaren Zufalls-Token**.
2. **`mi-hp` (öffentlich, separates Repo):** neue Route
   `GET /nlehre/insta/<token>.jpg` → liest den Blob aus Mongo → streamt ihn
   (Content-Type `image/jpeg`). ~15 Zeilen Flask.
3. **Editor:** ruft Metas API auf und übergibt
   `image_url = https://www.math.uni-freiburg.de/nlehre/insta/<token>.jpg`.
4. Meta lädt das Bild in Sekunden; danach kann Blob/Token wieder gelöscht werden.

> **Achtung — betrifft zwei Repos:** Diese Änderung erfordert einen kleinen Eingriff
> im **separaten `mi-hp`-Repo** (die neue Flask-Route), zusätzlich zu den Änderungen
> hier. Beim Umsetzen mit einplanen.

**Datenschutz:** Das Bild wird durchs Posten ohnehin öffentlich auf Instagram. Die
kurzzeitige, Token-geschützte Auslieferung über `www2` ist daher kein zusätzliches
Leck; mit unratbarem Token ist der Endpoint nicht enumerierbar.

**Variante A′ (evtl. ohne mi-hp-Zuschnitt-Route):** Die Homepage zeigt das
News-Bild bereits öffentlich → es existiert schon eine öffentliche URL fürs
Originalbild. Instagram akzeptiert 4:5 … 1.91:1; fällt das Original in diesen
Bereich, ist **kein Zuschnitt** nötig und die bestehende URL kann direkt verwendet
werden. Nur wenn zugeschnitten werden muss, braucht es die Route aus Option A.

**Fallback B (nur falls mi-hp-Eingriff unerwünscht):** Bild temporär in einen
öffentlichen Bucket (bwCloud / S3-kompatibel / Uni-Nextcloud Public Link) laden,
URL an Meta geben, nach dem Post löschen. Neue Zugangsdaten/Abhängigkeit.

**Verworfen:** Bild aus der Streamlit-Editor-App selbst ausliefern — scheitert
genau am VPN (Meta kommt nicht rein).

### 2b. Bild-Anforderungen (Feed-Post)
- **Seitenverhältnis:** zwischen **4:5** (hoch) und **1.91:1** (quer). Quadrat 1:1 erlaubt.
- **Empfohlene Auflösung:** **1080 × 1350** (4:5, maximale Bildschirmfläche) oder
  **1080 × 1080** (1:1). Breite max. 1440 px (wird sonst herunterskaliert), min. 320 px.
- **Farbraum:** sRGB. **Format:** JPEG. **Dateigröße:** ≤ 8 MB.
- Unsere Bilder sind bereits JPEG/RGB (siehe `05_Bild_edit.py`) — gut. Aber die
  Seitenverhältnisse passen i. d. R. **nicht** → wir müssen **zuschneiden/padden**.

### 2c. Caption / Text
- Max. **2 200 Zeichen**, bis zu **30 Hashtags**, Emojis erlaubt.
- **Keine Rich-Text-Formatierung:** Captions sind **reiner Text** — es gibt **kein
  echtes Fett/Kursiv**, kein Markdown, kein HTML. Nutzbar zur Gliederung sind nur
  **Zeilenumbrüche** und **Emojis**. Auch **Formeln/LaTeX gibt es nicht** (relevant
  fürs Math. Institut) — mathematische Notation ginge nur über Unicode (`ℝ`, `∫`, `α`).
  - Den verbreiteten **Unicode-Pseudo-Fett/-Kursiv-Trick** (𝐁𝐨𝐥𝐝, 𝘐𝘵𝘢𝘭𝘪𝘤) bewusst
    **nicht** einbauen: Screenreader lesen diese Zeichen nicht/als Kauderwelsch
    (**Barrierefreiheit / BITV** — an einer Uni rechtlich relevant), Hashtags/@Mentions
    funktionieren damit nicht, und die Darstellung ist unzuverlässig.
- **Links im Caption-Text sind NICHT anklickbar.** Nur `@Erwähnungen` und `#Hashtags`
  werden automatisch verlinkt; eine ausgeschriebene URL erscheint als reiner Text.
  Klickbare Links gibt es nur in der **Bio** (Profil) und in **Stories** (Link-Sticker),
  nicht im Feed-Post. Daher die Konvention **„Link in Bio"**.
  - **Bio nicht per API änderbar:** Die Graph API kann keine Profilfelder (Bio-Text,
    Bio-Link, Profilbild) bearbeiten. Der Bio-Link wird **manuell** gepflegt und ist
    **nicht Teil der Automatisierung**. Pragmatisch: **ein dauerhafter Bio-Link** auf
    eine feste Übersichtsseite (z. B. die News-/Homepage), der nicht pro Post wechselt.
  - Konsequenz für den News-`link`: als **Klartextzeile** in die Caption übernehmen
    (z. B. „🔗 math.uni-freiburg.de/…" oder „Mehr Infos: Link in Bio"), nicht als
    vermeintlich klickbaren Link.

---

## 3. Was ist an der App zu ändern?

Grundprinzip: **additiv, nichts Bestehendes umbauen.** Der Instagram-Teil ist pro
News optional und liegt in einem eigenen Expander + eigenem Helfer-Modul.

### 3a. Datenmodell (`mongo/schema*.py` + `misc/util.py`)
Neues optionales Feld am `news`-Dokument, z. B. `instagram` (Objekt) — Länge 0/1
analog zu `image`, oder direkt ein eingebettetes Objekt:

```
"instagram": {
    "enabled":      bool,          # soll aus dieser News ein Post werden?
    "caption":      str,           # editierter Post-Text (Plain Text, inkl. Hashtags)
    "ratio":        str,           # gewähltes Seitenverhältnis "4:5" | "1:1" | "1.91:1"
    "crop":         { ... },       # optionale Zuschnitt-Parameter aufs Quell-Bild (x,y,w,h)
    "source_image_id": ObjectId,   # welches bild-Doc als Quelle dient
    "status":       str,           # "draft" | "published" | "failed"
    "ig_media_id":  str,           # von Instagram zurückgegebene Post-ID
    "published_at": datetime,
    "last_error":   str
}
```
- **`caption` bekommt bewusst ein DB-Feld** und **bleibt auch nach dem Posten
  erhalten:** Man will einen Post entwerfen und ggf. **erst später** veröffentlichen —
  der Entwurf muss also über Sitzungen/Reloads hinweg überleben (nicht nur im
  Streamlit-`session_state`). Der Text ist winzig; Speicherplatz ist kein Argument.
  (Instagram bleibt nach dem Posten die Quelle der Wahrheit — die API kann eine
  veröffentlichte Caption ohnehin nicht mehr ändern —, aber der gespeicherte Text
  dient als Entwurf und als Archiv „was haben wir gepostet".)
- **`caption` ist Plain Text** (kein Fett/Kursiv/Markdown, siehe §2c) → im Editor
  genügt ein einfaches `st.text_area`.
- Schema-Validator in `mongo/schemaYYYYMMDD.py` erweitern (neues Datum, wie bei
  bisherigen Migrationen). Feld **optional** halten, damit Altbestand valide bleibt.
- Default-Template in `misc/util.py` (`st.session_state.new[...]`) um `instagram` ergänzen.
- Das gerenderte Insta-Bild + Auslieferungs-Token (§2a, Option A) liegen **nicht**
  dauerhaft hier, sondern kurzlebig (Feld `rendered`/`token` oder Mini-Collection
  `insta_bild`), und werden nach dem Posten aufgeräumt.

### 3b. Neues Helfer-Modul `misc/instagram.py`
Analog zu `authenticate()`/`update_confirm()` in `misc/tools.py`, aber gekapselt:
- `build_caption(news_doc) -> str` — Default-Caption aus News generieren, als
  **Plain Text** (Titel + Text + Standard-Hashtags). Der News-`link` wird als
  **Klartextzeile** eingebaut („🔗 …" bzw. „Mehr Infos: Link in Bio"), nicht als
  klickbarer Link (§2c). Gliederung nur über Zeilenumbrüche/Emojis.
- `render_preview_image(bild_bytes, crop, ratio) -> PIL.Image` — schneidet/padded
  das Quellbild auf ein zulässiges Insta-Format (Default 1080×1350), sRGB, JPEG.
- `upload_and_publish(image_bytes, caption) -> ig_media_id` — kümmert sich um
  (i) Bild öffentlich bereitstellen via Option A (Blob + Token in Mongo, Auslieferung
  durch die `mi-hp`-Route), (ii) `POST …/media` mit der `www2`-`image_url`,
  (iii) Status-Poll, (iv) `POST …/media_publish`, (v) Token/Blob aufräumen,
  (vi) Fehlerbehandlung. Der Call läuft von hinter dem VPN — nur ausgehend, daher ok.
- `refresh_token()` / Token-Handling (Long-Lived-Token, 60 Tage gültig, erneuerbar).

Neue Dependency in `requirements.txt`: **`requests`** (erste ausgehende HTTP-Integration
der App). Pillow ist bereits vorhanden.

### 3c. Konfiguration / Secrets
Bisher gibt es **kein** Secrets-Handling. Neu einführen:
- `.streamlit/secrets.toml` (via `st.secrets[...]`), **in `.gitignore` aufnehmen**.
- Inhalt: `IG_USER_ID`, `IG_ACCESS_TOKEN`, `IG_APP_ID`, `IG_APP_SECRET`,
  ggf. Bucket-/Upload-Zugangsdaten für §2a-Option-B.
- Nicht-geheime Endpunkte/Defaults (Graph-API-Version, Standard-Hashtags,
  Standard-Seitenverhältnis) nach `misc/config.py`.

### 3d. UI in `pages/01_News_edit.py` — neuer Expander „Instagram-Post"
Eingefügt nach dem Bild-Expander (~Zeile 229). Aufbau:

1. **Aktivieren:** `st.toggle("Instagram-Post erstellen")` (schreibt `instagram.enabled`).
2. **Bild-Vorschau + Zuschnitt:**
   - Quelle = das bereits verknüpfte News-Bild (`x["image"][0]._id`), falls vorhanden.
   - Auswahl Seitenverhältnis (`st.radio`: 4:5 / 1:1 / 1.91:1), Default 4:5.
   - Zuschnitt-Controls (einfachste Variante: Format wählen + Objekt-Fit
     cover/contain; ausbaubar zu echtem Crop mit Slidern für x/y).
   - `st.image(render_preview_image(...))` zeigt das **exakte** Bild, das gepostet
     wird (1080×1350 etc.). Warnung, falls Quellbild zu klein (< 320 px) oder fehlt.
3. **Text-Vorschau (editierbar):**
   - `caption = st.text_area("Caption", value = saved_caption_or_default)` —
     **Plain Text**, keine Rich-Text-/Markdown-Toolbar (§2c). Vorbelegung: gespeicherter
     Entwurf, sonst `build_caption(...)`.
   - Live-Zeichenzähler (`len(caption)/2200`) + Hashtag-Zähler (Warnung > 30).
   - Optional: eine **„so sieht der Post aus"-Kachel** — Bild oben, darunter der
     Caption-Text 1:1 (Zeilenumbrüche erhalten) in Insta-ähnlichem Styling (kleiner
     HTML/CSS-Block, analog zu `misc/css_styles.py`). Da Captions ohnehin Plain Text
     sind, ist die Vorschau echtes WYSIWYG. Hinweis, dass ausgeschriebene URLs im Post
     **nicht klickbar** sind.
4. **Buttons:**
   - `Entwurf speichern` → schreibt `instagram.{enabled,caption,crop,...}` per
     `tools.update_confirm(...)` (bestehender Speicher-Mechanismus, kein Sonderweg).
   - `Jetzt auf Instagram veröffentlichen` → ruft
     `instagram.upload_and_publish(...)`; bei Erfolg `status="published"`,
     `ig_media_id`, `published_at` speichern und `st.success`/`tools.flash`;
     bei Fehler `status="failed"`, `last_error` + `st.error`.
   - Nach dem Posten: Button ausgrauen / Hinweis „bereits veröffentlicht am …"
     inkl. `ig_media_id`, damit man nicht versehentlich doppelt postet.

Kein neuer Sidebar-Eintrag nötig (Aktion ist pro News). Optional später eine
Übersichtsseite `pages/09_Instagram.py`, die alle Entwürfe/veröffentlichten Posts listet.

### 3e. Speichern
Kein neuer Save-Weg: `instagram`-Teil geht über das bestehende
`tools.update_confirm(collection, x, x_updated, ...)`. Der veröffentlichende Call
ist der einzige neue Seiteneffekt (externer API-Call) — sauber im Helfer gekapselt,
mit try/except und Logging über das vorhandene `mi.log`.

---

## 4. Ablauf für die/den Redakteur:in (fertiger Zustand)

1. News wie gewohnt anlegen, Bild zuweisen.
2. Expander „Instagram-Post" öffnen → Toggle an.
3. Seitenverhältnis wählen, Vorschau des zugeschnittenen Bildes prüfen.
4. Vorgeschlagenen Text anpassen (Zeichen-/Hashtag-Zähler im Blick), Post-Vorschau ansehen.
5. „Entwurf speichern" (jederzeit) und/oder „Jetzt veröffentlichen".
6. Bestätigung + Insta-Post-ID; erneutes Posten wird verhindert.

---

## 5. Umsetzungs-Schritte (Reihenfolge)

1. **Konten & Freigaben** (kein Code): §1 abarbeiten — Institut/ÖA + Datenschutz +
   Meta-Konten + Token. **Blocker für den Livegang, nicht für die Entwicklung.**
2. **Öffentliche Bild-Route in `mi-hp` bauen** (§2a, Option A) — `GET /nlehre/insta/<token>.jpg`
   im separaten `mi-hp`-Repo, plus Ablage des gerenderten Blobs + Token in Mongo.
   Vorab mit einem Test-Bild + Test-Token die Graph-API-Zwei-Schritt-Kette manuell
   durchspielen (curl), um sie zu verstehen. **Betrifft zwei Repos.**
3. **Datenmodell** erweitern (Schema + `util.py`-Default).
4. **`misc/instagram.py`** mit `build_caption` + `render_preview_image` (rein lokal,
   ohne API testbar) — inkl. sRGB/JPEG/Ratio-Logik.
5. **UI-Expander** in `01_News_edit.py`: Toggle, Ratio-Auswahl, Bild-Vorschau,
   Caption-Editor mit Zählern, Post-Vorschau-Kachel, „Entwurf speichern".
6. **Secrets** (`secrets.toml` + `.gitignore`), `requests` in `requirements.txt`.
7. **`upload_and_publish`** anbinden, mit dem in Schritt 2 gewählten Bild-Weg.
8. **„Jetzt veröffentlichen"** verdrahten, Fehler-/Doppelpost-Handling, Logging.
9. **End-to-End-Test** auf dem echten (eigenen) Institutskonto.
10. Optional: Übersichtsseite, geplantes Posten (Scheduling) später.

---

## 6. Offene Fragen / Entscheidungen (vor Umsetzung zu klären)

1. ~~**Bild-Bereitstellung (§2a):**~~ **Entschieden: Option A** — öffentliche
   Route `GET /nlehre/insta/<token>.jpg` in `mi-hp` auf www2; `mi-hp` wird
   angepasst. (A′ als Optimierung, B nur als Fallback.)
2. **Existiert schon** ein Instagram-Auftritt / ein Meta-Business-Portfolio des
   Instituts oder der Uni, unter dem wir andocken?
3. **Datenschutz-Freigabe:** wer, bis wann? (Uni-Guidelines beachten.)
4. **Zuschnitt-Tiefe:** reicht „Format wählen + cover/contain", oder echter
   interaktiver Crop (aufwändiger)? Vorschlag: mit einfacher Variante starten.
5. **Caption-Sprache:** deutsch (`home.title_de`/`text_de`) als Default? Oder wählbar de/en?
6. **Nur Einzelbild** (Feed-Post) zum Start? Carousel/Reels/Stories bewusst später.
7. **Token-Erneuerung:** manueller Prozess (alle 60 Tage) oder automatischer Refresh-Job?

---

## Quellen (Instagram-API, Stand 2026)
- [Publish Content using the Instagram Platform — Meta Developer Docs](https://developers.facebook.com/docs/instagram-platform/content-publishing/)
- [Media reference — IG User /media — Meta Developer Docs](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/)
- [Post to Instagram via API: Guide (2026) — Postproxy](https://postproxy.dev/blog/post-to-instagram-via-api/)
- [Instagram Graph API: Complete Developer Guide for 2026 — Elfsight](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2026/)
- [Instagram API Integration Guide 2026 — Phyllo](https://www.getphyllo.com/post/instagram-api-integration-101-for-developers-of-the-creator-economy)
- [Updated Instagram aspect ratio and image size for 2026 — SocialBee](https://socialbee.com/blog/instagram-aspect-ratio-and-image-size/)
- [Instagram Image Size Guide 2026 — Buffer](https://buffer.com/resources/instagram-image-size/)
