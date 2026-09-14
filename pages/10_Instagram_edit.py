import streamlit as st
import pymongo
from datetime import datetime, timezone

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("NEWS.py")

from misc.css_styles import init_css
init_css()

from misc.config import *
import misc.util as util
import misc.tools as tools
import misc.instagram as insta

# Navigation in Sidebar anzeigen
tools.display_navigation()

collection = st.session_state.instapost
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"

if not st.session_state.logged_in:
    st.switch_page("NEWS.py")

x = collection.find_one({"_id": st.session_state.edit})
if x is None:
    st.switch_page("pages/09_Instagram.py")

veroeffentlicht = x.get("status") == "veroeffentlicht"

# Gelöscht werden dürfen nur Entwürfe. Bei allem anderen kann ein Beitrag auf
# Instagram stehen, den dieser Eintrag als einziger nachweist: Media-ID und
# Permalink stehen nur hier. Löschen liesse den Beitrag draussen stehen und
# nähme uns den Weg dorthin -- und über die API bekommen wir ihn nicht zurück,
# der DELETE-Endpunkt gilt nur für die Facebook-Login-Variante.
#
# "fehler" zählt ausdrücklich nicht als Entwurf: Scheitert das Abschalten der
# Kommentare (Schritt 4 in publish()), ist der Beitrag bereits veröffentlicht,
# der Status hier aber "fehler".
loeschbar = x.get("status", "entwurf") == "entwurf"

st.subheader(x.get("titel") or x.get("headline") or "Instagram-Post")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Zurück (ohne Speichern)"):
        st.switch_page("pages/09_Instagram.py")
with col3:
    if not loeschbar:
        st.button(
            "Post löschen", disabled=True,
            help=("Veröffentlichte Posts lassen sich hier nicht löschen. Dieser "
                  "Eintrag ist der einzige Nachweis des Beitrags (Media-ID und "
                  "Link). Den Beitrag selbst löscht man in der Instagram-App — "
                  "über die API geht es bei unserem Zugang nicht."
                  if veroeffentlicht else
                  "Der letzte Veröffentlichungsversuch ist fehlgeschlagen. "
                  "Möglicherweise steht der Beitrag trotzdem auf Instagram — "
                  "bitte erst dort nachsehen. Gelöscht werden können nur "
                  "Entwürfe."),
        )
    else:
        with st.popover("Post löschen"):
            st.write("Eintrag wirklich löschen?")
            if st.button("Ja", type="primary", key=f"delete-{x['_id']}"):
                # switch=False, damit nicht die generische Weiterleitung auf die
                # News-Seite (reset_vars -> 00_New.py) greift. Stattdessen zurück
                # zur Instagram-Übersicht.
                tools.delete_item_update_dependent_items(
                    collection, x["_id"], switch=False)
                st.session_state.edit = ""
                st.switch_page("pages/09_Instagram.py")
            st.button("Nein", on_click=st.success, args=("Nicht gelöscht!",),
                      key=f"not-deleted-{x['_id']}")

st.info(
    "**„Link in Bio“:** Links im Post-Text sind auf Instagram **nicht "
    "anklickbar** — nur @Erwähnungen und #Hashtags werden verlinkt. Der einzige "
    "klickbare Link im ganzen Account steht in der **Profil-Bio** von "
    "[@math_uni_freiburg](https://www.instagram.com/math_uni_freiburg/) und gilt "
    "für alle Posts gleich. Schreibe im Text also „Mehr Infos: Link in Bio“ statt "
    "einer URL. Die Bio wird direkt in der Instagram-App gepflegt (Profil "
    "bearbeiten), nicht hier."
)

if veroeffentlicht:
    pa = util.lokal(x.get("published_at"))
    pl = x.get("permalink")
    # Der Link ist der kürzeste Weg zur Kontrolle, ob der Beitrag so aussieht
    # wie gedacht. Fehlt er (ältere Posts, oder der Abruf ging daneben), führt
    # wenigstens das Profil hin.
    ziel = (f"[Beitrag auf Instagram ansehen]({pl})" if pl else
            "[Zum Profil](https://www.instagram.com/math_uni_freiburg/) — der "
            "direkte Link zu diesem Beitrag wurde nicht gespeichert.")
    st.success(
        f"Dieser Post wurde am {pa.strftime(util.date_format) if pa else '—'} "
        f"veröffentlicht (Media-ID {x.get('ig_media_id') or '—'}). {ziel}  \n"
        "Eine veröffentlichte Caption lässt sich über die API nicht mehr ändern; "
        "Änderungen hier wirken nur auf den gespeicherten Entwurf."
    )

# Die Seite ist zweispaltig: links wird eingegeben, rechts steht durchgehend die
# Vorschau. Streamlit rendert bei jeder Eingabe neu, die Vorschau ist also live.
links, rechts = st.columns([1, 1])

with links:
    st.markdown("### Bild")

    titel = st.text_input(
        "Interner Titel", x.get("titel", ""),
        help="Nur für die Übersicht in der App. Erscheint nicht im Post.",
    )

    ratio = st.radio(
        "Format", list(ig_ratios.keys()),
        index=list(ig_ratios.keys()).index(x.get("ratio", ig_ratio_default)),
        horizontal=True,
        help="4:5 nutzt im Feed die größte Fläche und ist die übliche Wahl.",
    )

    # Zurzeit nur Standard-Bilder (CD-Hintergrund mit Text). Die Auswahl der
    # Bildquelle ist bewusst ausgeblendet; die Code-Pfade für eigene Bilder
    # (render_bild, image_id, fit) bleiben im Modul erhalten für später.
    bildtyp = "standard"
    variante = x.get("variante", insta.VARIANTE_DEFAULT)
    lang = x.get("lang", "de")
    headline = x.get("headline", "")
    subline = x.get("subline", "")
    image_id = x.get("image_id")
    fit = x.get("fit", "cover")

    c_farbe, c_lang = st.columns([2, 1])
    with c_farbe:
        varianten = list(insta.VARIANTEN.keys())
        variante = st.radio(
            "Farbe", varianten,
            index=varianten.index(variante) if variante in varianten else 0,
            format_func=lambda v: insta.VARIANTEN[v]["label"],
            horizontal=True,
        )
    with c_lang:
        lang = st.radio(
            "Sprache (Institutsname)", ["de", "en"],
            index=0 if lang == "de" else 1,
            format_func=lambda l: {"de": "Deutsch", "en": "English"}[l],
            horizontal=True,
            help="Bestimmt, ob „Mathematisches Institut“ oder „Mathematical "
                 "Institute“ auf dem Bild steht.",
        )
    headline = st.text_area("Überschrift", headline, height=80)
    subline = st.text_area("Unterzeile", subline, height=80)
    st.caption(
        "Die Schriftgröße passt sich automatisch an die Textlänge an. Logo, "
        "Institutsname und die CD-Gestaltungselemente (Siegel, Vierblatt) "
        "werden automatisch gesetzt."
    )

    st.markdown("### Beschreibung")

    caption = st.text_area(
        "Caption", x.get("caption", ""), height=260,
        help="Reiner Text. Instagram kennt kein Fett/Kursiv, und ausgeschriebene "
             "Links sind im Post NICHT anklickbar — nur @Erwähnungen und #Hashtags.",
    )

    # Zwei Sorten von Problemen, bewusst getrennt: Was die Caption betrifft,
    # steht hier am Feld. Was den Post als Ganzes betrifft (leere Überschrift,
    # fehlende Caption), steht unten am Knopf, den es sperrt -- doppelt anzeigen
    # wäre nur Rauschen.
    n_zeichen, n_hashtags, caption_probleme = insta.caption_stats(caption)
    st.caption(f"{n_zeichen} / {ig_caption_maxlen} Zeichen · "
               f"{n_hashtags} / {ig_hashtag_max} Hashtags")
    for p in caption_probleme:
        st.error(p)

    st.caption(
        "**Sinnvolle Erwähnungen:** @unifreiburg (zentrale Uni) und "
        "@fsmathefreiburg (Fachschaft) — Institutionen erwähnen ist unkritisch "
        "und gut für die Reichweite. **Personen** (z. B. „@… wir gratulieren“) "
        "nur mit deren Einwilligung markieren — eine @Erwähnung ist eine "
        "Datenverarbeitung im Sinne der DSFA."
    )

    kommentar = st.text_input("Interner Kommentar", x.get("kommentar", ""))

# --- Vorschau -----------------------------------------------------------------

post = {
    "bildtyp": bildtyp, "variante": variante, "lang": lang, "headline": headline,
    "subline": subline, "image_id": image_id, "fit": fit, "ratio": ratio,
}

bild_data = None
if bildtyp == "bild" and image_id:
    b = st.session_state.bild.find_one({"_id": image_id})
    if b is None:
        st.warning("Das verknüpfte Bild existiert nicht mehr.")
    else:
        bild_data = b["data"]

vorschau, warnungen = insta.render(post, bild_data)

# Leere Posts lassen sich auf Instagram nicht mehr rückgängig machen -- sie
# blockieren das Veröffentlichen, statt nur zu warnen. Siehe post_probleme().
leer_probleme = insta.post_probleme(post, caption)

with rechts:
    st.markdown("### Vorschau")
    if vorschau is None:
        st.warning("Kein Bild — bitte eine Bildquelle wählen.")
    else:
        # Genau das Bild, das gepostet würde: richtige Größe, sRGB, JPEG.
        st.image(vorschau, use_container_width=True)
        st.caption(f"{vorschau.width} × {vorschau.height} px — so wird der Post aussehen.")

    for w in warnungen:
        st.warning(w)

    if caption.strip():
        # Captions sind Plain Text, die Vorschau ist damit echtes WYSIWYG.
        st.markdown("**@math_uni_freiburg**")
        st.text(caption)

    if vorschau is not None:
        st.download_button(
            "Bild herunterladen (JPEG)",
            data=insta.to_jpeg(vorschau),
            file_name=f"instagram-{ratio.replace(':', 'x')}.jpg",
            mime="image/jpeg",
            help="Nützlich, solange der Account noch nicht steht: Bild "
                 "herunterladen und von Hand posten.",
        )

# --- Speichern und Veröffentlichen --------------------------------------------

st.divider()
c1, c2 = st.columns([1, 1])

# Der Stand, den der Editor gerade anzeigt. BEIDE Knöpfe schreiben ihn.
#
# Vorher hat "Veröffentlichen" nur die Status-Felder gespeichert: Gepostet wurde
# das, was im Formular stand, abgelegt blieb der alte Entwurf. Beim ersten
# Testpost am 14.09.2026 ist genau das passiert -- auf Instagram ein blauer Post
# mit Überschrift, in der Datenbank ein leerer gelber Entwurf. Der Eintrag ist
# aber der einzige Nachweis dessen, was veröffentlicht wurde.
inhalt = {
    "titel": titel, "bildtyp": bildtyp, "variante": variante,
    "lang": lang, "headline": headline, "subline": subline,
    "image_id": image_id, "fit": fit, "ratio": ratio,
    "caption": caption, "kommentar": kommentar,
    "bearbeitet": bearbeitet,
}

with c1:
    if st.button("Entwurf speichern", type="primary"):
        tools.update_confirm(collection, x, inhalt, False,
                             "🎉 Entwurf gespeichert!")

with c2:
    kann_posten = (insta.is_configured() and vorschau is not None
                   and not caption_probleme and not leer_probleme)
    if veroeffentlicht:
        st.button("Bereits veröffentlicht", disabled=True,
                  help="Doppeltes Posten wird verhindert.")
    elif not insta.is_configured():
        st.button("Auf Instagram veröffentlichen", disabled=True,
                  help="Account und Token fehlen noch (ig_token.json / .netrc). "
                       "Siehe insta.md / docs/social-media.")
    else:
        # Ein grauer Knopf ohne Begründung ist eine Sackgasse: hier steht,
        # was noch fehlt. (Caption-Probleme stehen schon am Feld selbst.)
        for p in leer_probleme:
            st.warning(p)
        if vorschau is None:
            st.warning("Es gibt kein Bild — bitte eine Bildquelle wählen.")
        elif caption_probleme:
            st.warning("Die Caption ist noch zu lang bzw. hat zu viele Hashtags "
                       "— siehe die Meldung am Textfeld.")
        if st.button("Auf Instagram veröffentlichen", disabled=not kann_posten):
            try:
                media_id = insta.publish(insta.to_jpeg(vorschau), caption)
                tools.update_confirm(
                    collection, x,
                    {**inhalt,
                     "status": "veroeffentlicht", "ig_media_id": media_id,
                     "permalink": insta.permalink(media_id),
                     # Bewusst UTC: dieser Zeitstempel wird mit dem von Meta
                     # verglichen, und MongoDB legt Datumswerte ohnehin als UTC
                     # ab. Zur Anzeige rechnet util.lokal() zurueck.
                     "published_at": datetime.now(timezone.utc),
                     "last_error": ""},
                    False, "🎉 Auf Instagram veröffentlicht!",
                )
                st.rerun()
            except Exception as e:
                util.logger.error(f"Instagram-Post fehlgeschlagen: {e}")
                collection.update_one(
                    {"_id": x["_id"]},
                    {"$set": {**inhalt, "status": "fehler",
                              "last_error": str(e)}},
                )
                st.error(f"Veröffentlichen fehlgeschlagen: {e}")

st.write(x.get("bearbeitet", ""))
st.sidebar.button("logout", on_click=tools.logout)
