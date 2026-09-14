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
import secrets
import time
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageDraw, ImageFont

from misc.config import (
    ig_api_host,
    ig_api_version,
    ig_blatt,
    ig_caption_maxlen,
    ig_einrichtung,
    ig_font_bold,
    ig_font_regular,
    ig_hashtag_max,
    ig_hashtags_default,
    ig_insta_bild_ttl,
    ig_logo,
    ig_min_source_px,
    ig_netrc_machine,
    ig_public_image_base,
    ig_ratio_default,
    ig_ratios,
    ig_siegel,
    ig_token_file,
    mongo_location,
    netrc_file,
    ufr_blau,
    ufr_gelb,
    ufr_sand,
    ufr_weiss,
)

# Die CD-Varianten für Standard-Bilder. Jede legt Hintergrund, Textfarbe, Logo-
# und Blattfarbe fest — die Redaktion wählt nur den Namen.
#
# Das Logo der Universität gibt es in Blau (#344A9A), Weiß und Schwarz. Auf
# hellen Flächen steht das blaue, auf Blau das weiße. Schrift auf hellen Flächen
# ist Nachtblau (#00004A), auf Blau weiß.
# Blatt und Siegel werden NICHT in einer Komplementärfarbe halbtransparent
# gezeichnet — Blau bei 55 % über Gelb ergibt grauen Matsch. Stattdessen ein
# **deckender Ton des Hintergrunds** (Hintergrund Richtung Textfarbe gemischt).
# Das ist zugleich der CD-Ansatz: die Gestaltungselemente sind Tonabstufungen,
# keine Fremdfarben.
VARIANTEN = {
    "gelb": {
        "label": "Gelb",
        "bg": ufr_gelb,
        "fg": ufr_blau,           # gleich wie das blaue Logo — einheitlich
        "logo": ig_logo["blau"],
    },
    "blau": {
        "label": "Blau",
        "bg": ufr_blau,
        "fg": ufr_weiss,
        "logo": ig_logo["weiss"],
    },
    "weiss": {
        "label": "Weiß",
        "bg": ufr_weiss,
        "fg": ufr_blau,
        "logo": ig_logo["blau"],
    },
    "sand": {
        "label": "Sand",
        "bg": ufr_sand,
        "fg": ufr_blau,
        "logo": ig_logo["blau"],
    },
}
VARIANTE_DEFAULT = "gelb"


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mische(a, b, t):
    """Farbe a nach b mischen (t=0 -> a, t=1 -> b)."""
    ra, rb = _hex_rgb(a), _hex_rgb(b)
    return tuple(round(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def _tint(silhouette_pfad, farbe, alpha):
    """Weiße Silhouette (Blatt/Siegel) in `farbe` einfärben, mit `alpha` (0..1).

    Gibt ein RGBA-Bild zurück, dessen Deckung sich nach der Silhouette und dem
    Alpha richtet — so lässt sich dieselbe Datei als kräftiger Akzent oder als
    dezentes Wasserzeichen verwenden.
    """
    sil = Image.open(silhouette_pfad).convert("RGBA")
    r, g, b = _hex_rgb(farbe) if isinstance(farbe, str) else farbe
    farbschicht = Image.new("RGBA", sil.size, (r, g, b, 0))
    a = sil.getchannel("A").point(lambda v: round(v * alpha))
    farbschicht.putalpha(a)
    return farbschicht


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


def _news_titel(news, lang="de"):
    """Titel einer News: Homepage-Titel, sonst Monitor-Titel."""
    home = news.get("home", {})
    return (
        to_plain(home.get(f"title_{lang}", ""))
        or to_plain(news.get("monitor", {}).get("title", ""))
    )


def _news_text(news, lang="de"):
    """Fließtext einer News: Homepage-Text, sonst Monitor-Text."""
    home = news.get("home", {})
    return (
        to_plain(home.get(f"text_{lang}", ""))
        or to_plain(news.get("monitor", {}).get("text", ""))
    )


def caption_from_news(news, lang="de"):
    """Caption-Vorschlag aus einer News — nur als Startpunkt.

    Der Post ist danach eigenständig; die Redaktion schreibt den Text ohnehin
    meist um und länger.
    """
    teile = [t for t in (_news_titel(news, lang), _news_text(news, lang)) if t]

    link = (news.get("link") or "").strip()
    if link:
        # Ausgeschriebene URLs sind im Feed-Post NICHT klickbar (nur @mentions
        # und #hashtags werden verlinkt). Als Klartextzeile, damit niemand einen
        # klickbaren Link erwartet.
        teile.append(f"🔗 {link}")

    if ig_hashtags_default:
        teile.append(" ".join(ig_hashtags_default))

    return "\n\n".join(teile)


def prefill_from_news(news, lang="de"):
    """Felder für einen neuen Instagram-Post, vorbelegt aus einer News.

    Default: Standard-Bild (CD-Hintergrund) mit dem News-Titel als Überschrift
    und einer aus der News gebauten Caption. Der Post ist danach eigenständig —
    Bild und Text lassen sich im Editor frei ändern.
    """
    titel = _news_titel(news, lang)
    return {
        "titel": titel or "Instagram-Post",
        "bildtyp": "standard",
        "variante": VARIANTE_DEFAULT,
        "lang": lang,
        "headline": titel,
        "subline": "",
        "caption": caption_from_news(news, lang),
    }


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


def post_probleme(post, caption):
    """Was das Veröffentlichen verhindern muss — leere Posts abfangen.

    Der erste Live-Testpost (14.09.2026) war ein versehentlich veröffentlichter
    leerer Entwurf: keine Überschrift, keine Caption, also eine nackte gelbe
    Fläche ohne jeden Text. So etwas sieht man erst auf Instagram, und weg
    bekommt man es nur von Hand in der App — die Content-Publishing-API kennt
    keinen Lösch-Endpunkt. Deshalb eine Bremse und nicht bloß eine Warnung.

    Gibt eine Liste von Klartext-Gründen zurück; leer heißt: darf raus.
    """
    probleme = []
    if post.get("bildtyp") == "standard" and not (post.get("headline") or "").strip():
        probleme.append(
            "Das Standardbild trägt keine Überschrift — der Post wäre eine leere "
            "Farbfläche. Bitte eine Überschrift eintragen."
        )
    if not (caption or "").strip():
        probleme.append(
            "Der Post hat keine Bildunterschrift. Auf Instagram stünde er ohne "
            "jeden Text da."
        )
    return probleme


# ------------------------------------------------------------ Standardbild ----


def _font(pfad, groesse):
    """Schrift laden, mit Rückfall auf die PIL-Standardschrift.

    Fehlt Arimo auf dem Server, soll die App nicht abstürzen, sondern hässlich
    aussehen — und das sichtbar melden (siehe `font_verfuegbar`).
    """
    try:
        return ImageFont.truetype(pfad, groesse)
    except OSError:
        # Fehlt die Datei, liefert truetype in aktuellem Pillow schon selbst eine
        # skalierbare Ersatzschrift; dieser Zweig greift nur bei älterem Pillow.
        # Dort MUSS die Größe mitgegeben werden — load_default() ohne Größe wäre
        # eine feste 10-px-Schrift (winziger, unlesbarer Text).
        return ImageFont.load_default(size=groesse)


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
                    ratio=ig_ratio_default, lang="de"):
    """CD-Hintergrund mit Logo, Institutsname, Überschrift und Unterzeile.

    Enthält die CD-Gestaltungselemente: das Siegel als dezentes Wasserzeichen
    unten rechts und die Vierblatt-Form als Akzent oben rechts. Der
    Institutsname ist zweisprachig (`lang` = "de"/"en").

    Gibt (PIL.Image, warnungen) zurück — exakt das Bild, das gepostet würde.
    """
    v = VARIANTEN[variante]
    breite, hoehe = ig_ratios[ratio]
    warnungen = []

    bild = Image.new("RGB", (breite, hoehe), v["bg"])

    rand = round(breite * 0.09)
    inhalt_breite = breite - 2 * rand

    # --- Siegel als Wasserzeichen: unten rechts, über den Rand hinaus, sehr
    # dezent. Deckender Ton, nur leicht vom Hintergrund abgesetzt.
    try:
        siegel_farbe = _mische(v["bg"], v["fg"], 0.10)
        sg = round(breite * 0.85)
        siegel = _tint(ig_siegel, siegel_farbe, 1.0).resize((sg, sg), Image.LANCZOS)
        bild.paste(siegel, (breite - round(sg * 0.72), hoehe - round(sg * 0.72)), siegel)
    except OSError:
        pass  # ohne Siegel ist der Post immer noch gültig

    # --- Vierblatt-Akzent: oben rechts, über den Rand hinaus. Etwas kräftiger
    # als das Siegel, aber ebenfalls ein deckender Ton — nie halbtransparent.
    try:
        blatt_farbe = _mische(v["bg"], v["fg"], 0.20)
        bg = round(breite * 0.42)
        blatt = _tint(ig_blatt, blatt_farbe, 1.0).resize((bg, bg), Image.LANCZOS)
        bild.paste(blatt, (breite - round(bg * 0.55), -round(bg * 0.30)), blatt)
    except OSError:
        pass

    draw = ImageDraw.Draw(bild)

    if not font_verfuegbar():
        warnungen.append(
            "Die Schrift Arimo (Arial-Ersatz) fehlt auf diesem Rechner. Das Bild "
            "wird mit einer Notschrift gerendert und entspricht nicht dem CD."
        )

    # Logo oben links, auf 50 % der Inhaltsbreite.
    y = rand
    try:
        logo = Image.open(v["logo"]).convert("RGBA")
        # Auf den sichtbaren Schriftzug zuschneiden: Die Logodatei hat ~6,5 %
        # transparenten Rand links. Ohne Zuschnitt stünde der Institutsname (der
        # bei x=rand beginnt) weiter links als der sichtbare Schriftzug.
        logo = logo.crop(logo.getbbox())
        logo_breite = round(inhalt_breite * 0.50)
        logo = logo.resize(
            (logo_breite, round(logo.height * logo_breite / logo.width)),
            Image.LANCZOS,
        )
        bild.paste(logo, (rand, y), logo)
        y += logo.height
    except OSError:
        warnungen.append(
            "Das Logo wurde nicht gefunden (static/ufr-logo-*.png). "
            "Das Bild wird ohne Logo gerendert."
        )

    # Einrichtung unter das Logo — sonst sieht der Post aus, als poste die
    # Universität und nicht das Institut. Zweisprachig je nach `lang`.
    name = ig_einrichtung.get(lang) or ig_einrichtung["de"]
    if name:
        font_e = _font(ig_font_bold, round(hoehe * 0.032))
        y += round(hoehe * 0.018)
        draw.text((rand, y), name, font=font_e, fill=v["fg"])
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
        lang=post.get("lang", "de"),
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
    Token. Die öffentliche Bild-Route in mi-hp (/nlehre/insta/<token>.jpg) ist
    inzwischen vorhanden; fehlt nur eines davon, bleibt der Post-Button aus.
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


_mongo_client = None


def _insta_bild_collection():
    """Die Collection insta_bild — mi-hp liest daraus, mi-news schreibt hinein.

    Legt idempotent den TTL-Index an (Absicherung gegen liegengebliebene Bilder,
    falls das Aufräumen nach dem Posten mal ausfällt).
    """
    global _mongo_client
    if _mongo_client is None:
        from pymongo import MongoClient
        _mongo_client = MongoClient(mongo_location)
    coll = _mongo_client["news"]["insta_bild"]
    coll.create_index("created_at", expireAfterSeconds=ig_insta_bild_ttl)
    return coll


def _bild_bereitstellen(coll, image_bytes):
    """Bild unter einem unratbaren Token in insta_bild ablegen; Token zurück.

    Der Token muss zur Validierung in mi-hp passen (alphanumerisch, 16–128
    Zeichen): token_hex(16) liefert 32 Hex-Zeichen — passt. token_urlsafe wäre
    falsch (enthält '-'/'_' und würde dort mit 404 abgelehnt).
    """
    token = secrets.token_hex(16)
    coll.insert_one({
        "token": token,
        "data": image_bytes,
        "created_at": datetime.now(timezone.utc),
    })
    return token


def _graph_fehler(r, kontext=""):
    """Bei HTTP-Fehler eine sprechende Exception werfen (Graph-Fehlertext)."""
    if r.status_code < 400:
        return
    try:
        meldung = r.json().get("error", {}).get("message", r.text)
    except ValueError:
        meldung = r.text
    prefix = f"{kontext}: " if kontext else ""
    raise RuntimeError(f"{prefix}Instagram-API {r.status_code}: {meldung}")


def _warte_auf_fertig(base, container_id, token, versuche=20, pause=3):
    """Auf FINISHED des Media-Containers warten (Meta lädt das Bild von image_url)."""
    import requests

    for _ in range(versuche):
        r = requests.get(
            f"{base}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        _graph_fehler(r)
        status = r.json().get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Media-Container {status} — Bild-URL nicht erreichbar?")
        time.sleep(pause)
    raise RuntimeError("Zeitüberschreitung: Media-Container wurde nicht FINISHED.")


def publish(image_bytes, caption):
    """Post veröffentlichen. Gibt die Instagram-Media-ID zurück oder wirft.

    Der Flow ist dreistufig (siehe `insta.md`, „Kommentare müssen aus"):

    0. Bild unter einem Token in insta_bild ablegen → öffentliche image_url
       (mi-hp liefert sie unter /nlehre/insta/<token>.jpg aus).
    1. POST /media          → Container. Meta lädt das Bild SELBST von image_url.
    2. POST /media_publish  → Beitrag ist live, liefert die Media-ID.
    3. POST /<media-id>?comment_enabled=false
                            → Kommentare aus. **Pflicht**: Nutzungskonzept,
                              Datenschutzerklärung und DSFA sagen zu, dass die
                              Kommentarfunktion deaktiviert ist. Schlägt dieser
                              Schritt fehl, scheitert publish() laut — mit der
                              Media-ID im Fehlertext, damit man von Hand nachfassen
                              kann (der Beitrag ist dann bereits live).
    """
    import requests

    if not is_configured():
        raise NotConfigured(
            "Nicht konfiguriert: Es fehlt ein gültiger Token (ig_token.json) "
            "oder die .netrc-Zugangsdaten. Siehe insta.md / docs/social-media."
        )

    app_id, ig_user_id, app_secret = _netrc_eintrag()
    token = lade_token()["access_token"]
    base = f"{ig_api_host}/{ig_api_version}"

    coll = _insta_bild_collection()
    bild_token = _bild_bereitstellen(coll, image_bytes)
    image_url = f"{ig_public_image_base}/nlehre/insta/{bild_token}.jpg"

    try:
        # 1. Media-Container anlegen (Meta lädt image_url herunter).
        r = requests.post(
            f"{base}/{ig_user_id}/media",
            data={"image_url": image_url, "caption": caption, "access_token": token},
            timeout=60,
        )
        _graph_fehler(r, "Container anlegen")
        container_id = r.json()["id"]

        # 2. Warten, bis Meta das Bild geholt und verarbeitet hat.
        _warte_auf_fertig(base, container_id, token)

        # 3. Veröffentlichen.
        r = requests.post(
            f"{base}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=60,
        )
        _graph_fehler(r, "Veröffentlichen")
        media_id = r.json()["id"]
    finally:
        # Das Bild wird nur bis Schritt 1/2 gebraucht — danach immer aufräumen,
        # egal ob es geklappt hat. Der TTL-Index fängt den Rest ab.
        coll.delete_one({"token": bild_token})

    # 4. Kommentare deaktivieren — Pflicht. Der Beitrag ist ab jetzt live; scheitert
    # dieser Schritt, muss es laut scheitern, aber die Media-ID darf nicht verloren
    # gehen (sonst kommt man an den Beitrag zum Nachbessern nicht mehr heran).
    r = requests.post(
        f"{base}/{media_id}",
        data={"comment_enabled": "false", "access_token": token},
        timeout=60,
    )
    if r.status_code >= 400:
        try:
            meldung = r.json().get("error", {}).get("message", r.text)
        except ValueError:
            meldung = r.text
        raise RuntimeError(
            f"Beitrag {media_id} ist veröffentlicht, aber die Kommentare ließen "
            f"sich NICHT deaktivieren (Instagram-API {r.status_code}: {meldung}). "
            f"Bitte umgehend von Hand am Beitrag {media_id} abschalten."
        )

    return media_id


def permalink(media_id):
    """Die öffentliche URL des Beitrags (https://www.instagram.com/p/<code>/).

    Aus der Media-ID allein kommt man nicht dorthin — der Kurzcode in der URL
    lässt sich nicht aus ihr ableiten. Meta gibt ihn auf Nachfrage heraus,
    deshalb dieser eine zusätzliche Aufruf direkt nach dem Posten.

    Scheitert er, ist nichts kaputt: Der Beitrag ist veröffentlicht, es fehlt
    nur der bequeme Link. Darum "" statt einer Exception — ein Fehler hier darf
    nicht so aussehen, als sei das Posten schiefgegangen.
    """
    import requests

    daten = lade_token()
    if not daten:
        return ""
    try:
        r = requests.get(
            f"{ig_api_host}/{ig_api_version}/{media_id}",
            params={"fields": "permalink", "access_token": daten["access_token"]},
            timeout=30,
        )
        if r.status_code >= 400:
            return ""
        return r.json().get("permalink") or ""
    except Exception:
        return ""
