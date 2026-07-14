# Plan: News als Instagram-Post veröffentlichen

Ziel: In der bestehenden Streamlit-News-App soll man bei jeder News optional
einen Instagram-Post erzeugen können. Bild in korrekter Größe, editierbarer
Text mit Live-Vorschau, Veröffentlichung über die Instagram-API.

Branch: `instagram`

---

## 1. Welcher Instagram-Account? Wer beantragt was?

Instagram lässt **kein automatisches Posten von privaten Accounts** zu. Die
offizielle „Content Publishing API" ist Teil der **Meta / Instagram Graph API**
und funktioniert nur mit einem ganzen Stapel verknüpfter Konten.

### Benötigte Konten (Kette)

| # | Was | Zweck | Wer / Hinweis |
|---|-----|-------|---------------|
| 1 | **Instagram Professional Account** (Typ *Business*, nicht *Creator*) | Das eigentliche Konto `@...` des Mathematischen Instituts | Falls schon ein Insta-Account existiert: in den Einstellungen zu „Professional / Business" umstellen (kostenlos, reversibel). |
| 2 | **Facebook-Seite** des Instituts | Instagram-Business-Accounts müssen zwingend mit einer FB-Seite verknüpft sein — auch wenn die Seite selbst nicht bespielt wird | Muss existieren und mit (1) verknüpft werden. |
| 3 | **Meta Business Portfolio** (früher „Business Manager") | Klammer um Seite, Insta-Konto und App; hier hängt die Verifizierung | Auf `business.facebook.com` anlegen. |
| 4 | **Meta Developer App** (Typ *Business*) | Die technische App, die die API-Calls macht und den Access-Token trägt | Auf `developers.facebook.com` anlegen. |
| 5 | **Long-Lived Access Token** mit den passenden Permissions | Token, den unsere App zum Posten benutzt | Wird über die App/Graph-API-Explorer erzeugt, siehe unten. |

### Benötigte Permissions (App Review)
- `instagram_basic`
- `instagram_content_publish`  ← Kernberechtigung fürs Posten
- `pages_read_engagement` / `business_management` (für die Verknüpfung)

> **App Review nötig:** Solange die App im *Development*-Modus ist, kann sie nur
> auf Konten posten, deren Nutzer als **Tester/Admin** in der App eingetragen
> sind. Für unseren Fall (wir posten nur auf **unser eigenes** Institutskonto)
> reicht das — **eine öffentliche App-Review durch Meta ist NICHT zwingend**,
> solange nur das eigene, in der App als Rolle hinterlegte Konto bespielt wird.
> Das spart die 2–4 Wochen Review-Zeit. (App-Review wird erst nötig, wenn man
> auf *fremde* Konten posten will.)

### Wer sollte das beantragen? — Empfehlung
Das ist **keine rein technische, sondern eine institutionelle/Marken-Frage**.
Die Konten repräsentieren offiziell das Mathematische Institut.

1. **Kontoinhaber = Institut, nicht Privatperson.** Instagram-, FB-Seiten- und
   Business-Portfolio-Konten sollten auf einer **institutionellen Funktions-Mail**
   laufen (z. B. `oeffentlichkeitsarbeit@math.uni-freiburg.de` oder ein eigens
   dafür angelegtes Postfach), damit die Konten beim Personalwechsel nicht
   verloren gehen. **Kein privater Google/Facebook-Account.**
2. **Antragsteller / Verantwortliche:** Geschäftsführung des Instituts bzw. die
   Person, die für Öffentlichkeitsarbeit / Web zuständig ist. Ggf. Abstimmung
   mit der **zentralen Presse-/Öffentlichkeitsarbeit der Uni Freiburg** — die Uni
   hat Social-Media-Guidelines und ggf. schon ein Meta-Business-Portfolio, unter
   dem das Institut als Asset laufen kann.
3. **Datenschutz (wichtig an einer Uni):** Vor dem Livegang die
   **Datenschutzbeauftragte / Stabsstelle Datenschutz** einbinden. Meta verarbeitet
   Daten in den USA; es braucht ggf. eine Datenschutzerklärung / Impressum für den
   Insta-Auftritt. Das ist ein Freigabe-Schritt, kein Code-Schritt, aber er gehört
   in die Planung.
4. **Technischer Admin (Rolle in der Meta-App):** Der/die App-Betreiber (du) wird
   als Admin/Developer in der Meta Developer App eingetragen, um Token zu erzeugen
   und zu erneuern.

**Konkrete Reihenfolge zum Beantragen:**
1. Geschäftsführung/ÖA-Verantwortliche klärt: Gibt es schon einen Insta-Auftritt
   des Instituts? Gibt es ein Uni-weites Meta-Business-Portfolio?
2. Institutionelle Funktions-Mail bereitstellen (Rechenzentrum / RZ-Ticket).
3. Auf dieser Mail: FB-Seite + Instagram-Business-Account + Business-Portfolio anlegen/verknüpfen.
4. Datenschutz-Freigabe einholen.
5. Meta Developer App anlegen, technische Admins eintragen, Token erzeugen.

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
