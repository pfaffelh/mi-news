"""Instagram-Posts erzeugen.

Ein Instagram-Post ist ein **eigenständiges Objekt**, keine Erweiterung einer
News: Bild und Text sind in aller Regel andere als auf der Homepage, und die
Beschreibung darf deutlich länger sein.

Zwei Bildquellen:

* **Standard-Bild** — ein CD-Hintergrund der Universität (Gelb/Blau/Weiß) mit
  Wortmarke, auf den in der App eine Überschrift und eine Unterzeile
  geschrieben werden. Kein Bildmaterial nötig.
* **Eigenes Bild** — ein Bild aus der bild-Collection, zugeschnitten auf ein
  von Instagram akzeptiertes Format.

Alles hier ist **rein lokal** und ohne Account, Token oder Netz testbar. Der
einzige Teil, der eine Verbindung braucht, ist `publish()` — und der ist noch
nicht angebunden.

Warum die Caption Plain Text ist: Instagram-Captions kennen kein Fett/Kursiv/
Markdown und keine klickbaren Links. Gliederung geht nur über Zeilenumbrüche und
Emojis. Der Unicode-Pseudo-Fett-Trick (𝐁𝐨𝐥𝐝) wird bewusst nicht verwendet —
Screenreader lesen die Zeichen als Kauderwelsch, was an einer Uni ein
Barrierefreiheitsproblem ist (BITV).
"""

import io
import json
import netrc
import os
import re
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageDraw, ImageFont

from misc.config import (
    ig_api_host,
    ig_caption_maxlen,
    ig_einrichtung,
    ig_font_bold,
    ig_font_regular,
    ig_hashtag_max,
    ig_hashtags_default,
    ig_min_source_px,
    ig_netrc_machine,
    ig_ratio_default,
    ig_ratios,
    ig_token_file,
    netrc_file,
    ufr_blau,
    ufr_gelb,
    ufr_schwarz,
    ufr_weiss,
)

# Die drei CD-Varianten für Standard-Bilder. Jede legt Hintergrund, Textfarbe
# und die passende Wortmarke fest — die Redaktion wählt nur den Namen.
#
# Die Wortmarke der Universität ist blau (#344A9A), nicht schwarz; es gibt sie
# nur in Blau und in Weiß. Auf Gelb und Weiß steht die blaue, auf Blau die weiße.
VARIANTEN = {
    "gelb": {
        "label": "Gelb",
        "bg": ufr_gelb,
        "fg": ufr_schwarz,
        "logo": "static/ufr-wortmarke-blau.png",
    },
    "blau": {
        "label": "Blau",
        "bg": ufr_blau,
        "fg": ufr_weiss,
        "logo": "static/ufr-wortmarke-weiss.png",
    },
    "weiss": {
        "label": "Weiß",
        "bg": ufr_weiss,
        "fg": ufr_blau,
        "logo": "static/ufr-wortmarke-blau.png",
    },
}
VARIANTE_DEFAULT = "gelb"


# ---------------------------------------------------------------- Caption ----

_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")   # [Text](url) -> Text
_MD_EMPH = re.compile(r"(\*\*|__|\*|_)")
_HTML_TAG = re.compile(r"<[^>]+>")
_BLANK_RUN = re.compile(r"\n{3,}")


def to_plain(text):
    """Markdown/HTML entfernen — in einer Caption käme es als Zeichensalat an."""
    if not text:
        return ""
    text = _MD_LINK.sub(r"\1", text)
    text = _HTML_TAG.sub("", text)
    text = _MD_EMPH.sub("", text)
    return _BLANK_RUN.sub("\n\n", text).strip()


def caption_from_news(news, lang="de"):
    """Caption-Vorschlag aus einer News — nur als Startpunkt.

    Der Post ist danach eigenständig; die Redaktion schreibt den Text ohnehin
    meist um und länger.
    """
    home = news.get("home", {})
    teile = [
        t
        for t in (
            to_plain(home.get(f"title_{lang}", "")),
            to_plain(home.get(f"text_{lang}", "")),
        )
        if t
    ]

    link = (news.get("link") or "").strip()
    if link:
        # Ausgeschriebene URLs sind im Feed-Post NICHT klickbar (nur @mentions
        # und #hashtags werden verlinkt). Als Klartextzeile, damit niemand einen
        # klickbaren Link erwartet.
        teile.append(f"🔗 {link}")

    if ig_hashtags_default:
        teile.append(" ".join(ig_hashtags_default))

    return "\n\n".join(teile)


def caption_stats(caption):
    """(Zeichen, Hashtags, Probleme) für die Anzeige im Editor."""
    caption = caption or ""
    hashtags = re.findall(r"#\w+", caption)
    probleme = []
    if len(caption) > ig_caption_maxlen:
        probleme.append(
            f"Caption ist {len(caption)} Zeichen lang, erlaubt sind {ig_caption_maxlen}."
        )
    if len(hashtags) > ig_hashtag_max:
        probleme.append(f"{len(hashtags)} Hashtags, erlaubt sind {ig_hashtag_max}.")
    return len(caption), len(hashtags), probleme


# ------------------------------------------------------------ Standardbild ----


def _font(pfad, groesse):
    """Schrift laden, mit Rückfall auf die PIL-Standardschrift.

    Fehlt Arimo auf dem Server, soll die App nicht abstürzen, sondern hässlich
    aussehen — und das sichtbar melden (siehe `font_verfuegbar`).
    """
    try:
        return ImageFont.truetype(pfad, groesse)
    except OSError:
        return ImageFont.load_default()


def font_verfuegbar():
    """Ist die CD-Schrift da? Wenn nicht, warnt der Editor."""
    return os.path.exists(ig_font_regular) and os.path.exists(ig_font_bold)


def _umbrechen(draw, text, font, max_breite):
    """Text auf `max_breite` umbrechen. Eigene Zeilenumbrüche bleiben erhalten."""
    zeilen = []
    for absatz in (text or "").split("\n"):
        if not absatz.strip():
            zeilen.append("")
            continue
        zeile = ""
        for wort in absatz.split():
            probe = f"{zeile} {wort}".strip()
            if draw.textlength(probe, font=font) <= max_breite or not zeile:
                zeile = probe
            else:
                zeilen.append(zeile)
                zeile = wort
        zeilen.append(zeile)
    return zeilen


def _passende_groesse(draw, text, pfad, max_breite, max_hoehe, start, minimum=28):
    """Größte Schriftgröße, bei der der Text noch in den Kasten passt.

    Damit muss die Redaktion nicht an Schriftgrößen schrauben — sie tippt, und
    der Text passt sich an.
    """
    groesse = start
    while groesse > minimum:
        font = _font(pfad, groesse)
        zeilen = _umbrechen(draw, text, font, max_breite)
        hoehe = len(zeilen) * round(groesse * 1.25)
        if hoehe <= max_hoehe:
            return font, zeilen
        groesse -= 2
    font = _font(pfad, minimum)
    return font, _umbrechen(draw, text, font, max_breite)


def render_standard(headline, subline="", variante=VARIANTE_DEFAULT,
                    ratio=ig_ratio_default):
    """CD-Hintergrund mit Wortmarke, Überschrift und Unterzeile rendern.

    Gibt (PIL.Image, warnungen) zurück — exakt das Bild, das gepostet würde.
    """
    v = VARIANTEN[variante]
    breite, hoehe = ig_ratios[ratio]
    warnungen = []

    bild = Image.new("RGB", (breite, hoehe), v["bg"])
    draw = ImageDraw.Draw(bild)

    rand = round(breite * 0.09)
    inhalt_breite = breite - 2 * rand

    if not font_verfuegbar():
        warnungen.append(
            "Die Schrift Arimo (Arial-Ersatz) fehlt auf diesem Rechner. Das Bild "
            "wird mit einer Notschrift gerendert und entspricht nicht dem CD."
        )

    # Wortmarke oben links, auf 55 % der Inhaltsbreite.
    y = rand
    try:
        logo = Image.open(v["logo"]).convert("RGBA")
        logo_breite = round(inhalt_breite * 0.55)
        logo = logo.resize(
            (logo_breite, round(logo.height * logo_breite / logo.width)),
            Image.LANCZOS,
        )
        bild.paste(logo, (rand, y), logo)
        y += logo.height
    except OSError:
        warnungen.append(
            "Die Wortmarke wurde nicht gefunden (static/ufr-wortmarke-*.png). "
            "Das Bild wird ohne Logo gerendert."
        )

    # Einrichtung unter die Wortmarke — sonst sieht der Post aus, als poste die
    # Universität und nicht das Institut.
    if ig_einrichtung:
        font_e = _font(ig_font_bold, round(hoehe * 0.032))
        y += round(hoehe * 0.018)
        draw.text((rand, y), ig_einrichtung, font=font_e, fill=v["fg"])
        y += round(font_e.size * 1.25)

    kopf_unterkante = y + round(hoehe * 0.05)

    # Überschrift und Unterzeile werden **unten verankert**, nicht direkt unter
    # das Logo geklebt: Sonst bleibt bei kurzem Text (und besonders bei 1:1) die
    # untere Bildhälfte leer und der Post wirkt unfertig.
    platz = hoehe - rand - kopf_unterkante
    subline = (subline or "").strip()
    kopf_max = round(platz * (0.55 if subline else 0.9))

    font_h, zeilen_h = _passende_groesse(
        draw, headline, ig_font_bold, inhalt_breite, kopf_max,
        start=round(hoehe * 0.10),
    )
    hoehe_h = len(zeilen_h) * round(font_h.size * 1.25)

    zeilen_s, font_s, hoehe_s, abstand = [], None, 0, 0
    if subline:
        abstand = round(hoehe * 0.03)
        font_s, zeilen_s = _passende_groesse(
            draw, subline, ig_font_regular, inhalt_breite,
            platz - hoehe_h - abstand, start=round(hoehe * 0.055),
        )
        hoehe_s = len(zeilen_s) * round(font_s.size * 1.3)

    block = hoehe_h + abstand + hoehe_s
    y = max(kopf_unterkante, hoehe - rand - block)
    if block > platz:
        warnungen.append(
            "Der Text ist zu lang für das Bild und wird beschnitten. Bitte kürzen."
        )

    for zeile in zeilen_h:
        draw.text((rand, y), zeile, font=font_h, fill=v["fg"])
        y += round(font_h.size * 1.25)

    if zeilen_s:
        y += abstand
        for zeile in zeilen_s:
            draw.text((rand, y), zeile, font=font_s, fill=v["fg"])
            y += round(font_s.size * 1.3)

    return bild, warnungen


# ------------------------------------------------------------- Eigenes Bild --


def render_bild(data, ratio=ig_ratio_default, fit="cover", bg=ufr_weiss):
    """Ein Bild aus der bild-Collection auf ein Instagram-Format bringen.

    `fit` — "cover" (formatfüllend, schneidet ab) oder
            "contain" (vollständig sichtbar, füllt mit `bg` auf)
    """
    ziel_w, ziel_h = ig_ratios[ratio]
    warnungen = []

    src = Image.open(io.BytesIO(data))
    if src.width < ig_min_source_px or src.height < ig_min_source_px:
        warnungen.append(
            f"Quellbild ist nur {src.width}×{src.height} px. Instagram verlangt "
            f"mindestens {ig_min_source_px} px; der Post wird unscharf."
        )

    # Instagram erwartet sRGB. Transparenz muss auf `bg` — sonst wird sie schwarz.
    if src.mode in ("RGBA", "LA", "P"):
        src = src.convert("RGBA")
        flach = Image.new("RGB", src.size, bg)
        flach.paste(src, mask=src.split()[-1])
        src = flach
    else:
        src = src.convert("RGB")

    if fit == "cover":
        skala = max(ziel_w / src.width, ziel_h / src.height)
        src = src.resize(
            (max(1, round(src.width * skala)), max(1, round(src.height * skala))),
            Image.LANCZOS,
        )
        links = (src.width - ziel_w) // 2
        oben = (src.height - ziel_h) // 2
        out = src.crop((links, oben, links + ziel_w, oben + ziel_h))
    else:
        skala = min(ziel_w / src.width, ziel_h / src.height)
        src = src.resize(
            (max(1, round(src.width * skala)), max(1, round(src.height * skala))),
            Image.LANCZOS,
        )
        out = Image.new("RGB", (ziel_w, ziel_h), bg)
        out.paste(src, ((ziel_w - src.width) // 2, (ziel_h - src.height) // 2))

    return out, warnungen


def render(post, bild_data=None):
    """Das Bild eines Posts rendern — egal welcher Bildtyp."""
    if post.get("bildtyp") == "bild":
        if not bild_data:
            return None, ["Es ist kein Bild ausgewählt."]
        return render_bild(
            bild_data,
            ratio=post.get("ratio", ig_ratio_default),
            fit=post.get("fit", "cover"),
        )
    return render_standard(
        post.get("headline", ""),
        post.get("subline", ""),
        variante=post.get("variante", VARIANTE_DEFAULT),
        ratio=post.get("ratio", ig_ratio_default),
    )


def to_jpeg(image, quality=90):
    """PIL-Bild als JPEG-Bytes — das Format, das Instagram bekommt."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


# -------------------------------------------------------------------- API ----


class NotConfigured(Exception):
    """Zugangsdaten oder Bild-Route fehlen — es kann nicht gepostet werden."""


def _netrc_eintrag():
    """(app_id, ig_user_id, app_secret) aus der .netrc — oder None.

    Hausstil, wie in mi-hp: statische Zugangsdaten stehen in der .netrc. Der
    rotierende Token gehört ausdrücklich NICHT hierher (siehe misc/config.py).

    Belegung des Eintrags:
        machine graph.instagram.com
          login    <IG_APP_ID>
          account  <IG_USER_ID>
          password <IG_APP_SECRET>
    """
    if not os.path.exists(netrc_file):
        return None
    try:
        return netrc.netrc(netrc_file).authenticators(ig_netrc_machine)
    except (netrc.NetrcParseError, OSError):
        return None


def lade_token():
    """Den aktuellen Long-Lived Token laden — oder None.

    Rückgabe: dict mit 'access_token' und 'expires_at' (ISO-8601).
    """
    if not os.path.exists(ig_token_file):
        return None
    try:
        with open(ig_token_file, encoding="utf-8") as f:
            daten = json.load(f)
    except (OSError, ValueError):
        return None
    return daten if daten.get("access_token") else None


def speichere_token(access_token, expires_in):
    """Token atomar schreiben.

    Erst in eine Nachbardatei, dann umbenennen: Ein Absturz mitten im Schreiben
    darf keinen halben Token hinterlassen — der wäre nicht mehr refreshbar, und
    dann hilft nur noch das Meta-Dashboard.
    """
    os.makedirs(os.path.dirname(ig_token_file), exist_ok=True)
    daten = {
        "access_token": access_token,
        "expires_at": (
            datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        ).isoformat(),
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp = f"{ig_token_file}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, ig_token_file)          # atomar
    return daten


def token_restlaufzeit():
    """Tage bis der Token abläuft — oder None, wenn es keinen gibt.

    Kann negativ sein. Dann ist er tot und lässt sich auch nicht mehr erneuern.
    """
    daten = lade_token()
    if not daten or not daten.get("expires_at"):
        return None
    try:
        ende = datetime.fromisoformat(daten["expires_at"])
    except ValueError:
        return None
    return (ende - datetime.now(timezone.utc)).days


def is_configured():
    """Kann überhaupt gepostet werden?

    Braucht beides: die statischen Daten aus der .netrc und einen lebenden
    Token. Die öffentliche Bild-Route in mi-hp fehlt weiterhin — deshalb wirft
    `publish()` noch.
    """
    daten = lade_token()
    if not daten:
        return False
    rest = token_restlaufzeit()
    if rest is not None and rest < 0:
        return False
    return _netrc_eintrag() is not None


def refresh_token():
    """Den Long-Lived Token gegen einen frischen tauschen (60 Tage ab jetzt).

    Bedingungen von Meta: Der Token muss mindestens 24 Stunden alt und darf
    nicht abgelaufen sein. Ein abgelaufener Token ist endgültig verloren —
    dann muss im Meta-App-Dashboard von Hand ein neuer erzeugt werden.

    Wird vom Cron-Job bin/refresh_ig_token.py aufgerufen (wöchentlich).
    """
    import requests

    daten = lade_token()
    if not daten:
        raise NotConfigured(
            f"Kein Token in {ig_token_file}. Einmalig im Meta-App-Dashboard "
            f"erzeugen und dort ablegen."
        )

    rest = token_restlaufzeit()
    if rest is not None and rest < 0:
        raise NotConfigured(
            f"Der Token ist seit {-rest} Tagen abgelaufen und kann nicht mehr "
            f"erneuert werden. Im Meta-App-Dashboard einen neuen erzeugen."
        )

    r = requests.get(
        f"{ig_api_host}/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": daten["access_token"],
        },
        timeout=30,
    )
    r.raise_for_status()
    antwort = r.json()
    return speichere_token(antwort["access_token"], antwort["expires_in"])


def publish(image_bytes, caption):
    """Post veröffentlichen — noch nicht angebunden.

    Der Flow ist dreistufig (siehe `insta.md`, „Kommentare müssen aus"):

    1. POST /media          → Container. Braucht eine **öffentliche** image_url;
                              die Route dafür (`/nlehre/insta/<token>.jpg` in
                              mi-hp) gibt es noch nicht. Das ist der Blocker.
    2. POST /media_publish  → Beitrag ist live, liefert die Media-ID.
    3. POST /<media-id>?comment_enabled=false
                            → Kommentare aus. **Pflicht**: Nutzungskonzept,
                              Datenschutzerklärung und DSFA sagen zu, dass die
                              Kommentarfunktion deaktiviert ist, und die DSFA
                              stützt ihre Risikobewertung darauf. Schlägt dieser
                              Schritt fehl, muss das laut scheitern.
    """
    raise NotConfigured(
        "Veröffentlichen ist noch nicht angebunden: Es fehlt die öffentliche "
        "Bild-Route in mi-hp (Meta lädt das Bild selbst von einer URL herunter, "
        "einen Upload gibt es nicht). Siehe insta.md."
    )
