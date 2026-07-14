import streamlit as st
import pymongo
from datetime import datetime

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

st.subheader(x.get("titel") or x.get("headline") or "Instagram-Post")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Zurück (ohne Speichern)"):
        st.switch_page("pages/09_Instagram.py")
with col3:
    with st.popover("Post löschen"):
        st.write("Eintrag wirklich löschen?")
        if st.button("Ja", type="primary", key=f"delete-{x['_id']}"):
            tools.delete_item_update_dependent_items(collection, x["_id"])
        st.button("Nein", on_click=st.success, args=("Nicht gelöscht!",),
                  key=f"not-deleted-{x['_id']}")

if veroeffentlicht:
    pa = x.get("published_at")
    st.success(
        f"Dieser Post wurde am {pa.strftime(util.date_format) if pa else '—'} "
        f"veröffentlicht (Media-ID {x.get('ig_media_id') or '—'}). "
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

    bildtyp = st.radio(
        "Bildquelle", ["standard", "bild"],
        index=0 if x.get("bildtyp", "standard") == "standard" else 1,
        format_func=lambda t: {
            "standard": "Standard-Bild (Uni-Hintergrund mit Text)",
            "bild": "Eigenes Bild aus der Bild-Sammlung",
        }[t],
    )

    variante = x.get("variante", insta.VARIANTE_DEFAULT)
    headline = x.get("headline", "")
    subline = x.get("subline", "")
    image_id = x.get("image_id")
    fit = x.get("fit", "cover")

    if bildtyp == "standard":
        varianten = list(insta.VARIANTEN.keys())
        variante = st.radio(
            "Farbe", varianten,
            index=varianten.index(variante) if variante in varianten else 0,
            format_func=lambda v: insta.VARIANTEN[v]["label"],
            horizontal=True,
        )
        headline = st.text_area("Überschrift", headline, height=80)
        subline = st.text_area("Unterzeile", subline, height=80)
        st.caption(
            "Die Schriftgröße passt sich automatisch an die Textlänge an. "
            "Die Wortmarke und „Mathematisches Institut“ stehen immer oben."
        )
    else:
        bilder = list(st.session_state.bild.find({"menu": True},
                                                 sort=[("rang", pymongo.ASCENDING)]))
        if bilder:
            ids = [b["_id"] for b in bilder]
            idx = ids.index(image_id) if image_id in ids else 0
            gewaehlt = st.selectbox(
                "Bild", bilder, index=idx,
                format_func=lambda b: b["titel"] or b["filename"],
            )
            image_id = gewaehlt["_id"]
        else:
            st.warning("Es sind keine Bilder in der Bild-Sammlung vorhanden.")
            image_id = None
        fit = st.radio(
            "Zuschnitt", ["cover", "contain"],
            index=0 if fit == "cover" else 1,
            format_func=lambda f: {
                "cover": "Formatfüllend (schneidet Ränder ab)",
                "contain": "Vollständig sichtbar (mit Rand)",
            }[f],
        )

    st.markdown("### Beschreibung")

    caption = st.text_area(
        "Caption", x.get("caption", ""), height=260,
        help="Reiner Text. Instagram kennt kein Fett/Kursiv, und ausgeschriebene "
             "Links sind im Post NICHT anklickbar — nur @Erwähnungen und #Hashtags.",
    )

    n_zeichen, n_hashtags, probleme = insta.caption_stats(caption)
    st.caption(f"{n_zeichen} / {ig_caption_maxlen} Zeichen · "
               f"{n_hashtags} / {ig_hashtag_max} Hashtags")
    for p in probleme:
        st.error(p)

    kommentar = st.text_input("Interner Kommentar", x.get("kommentar", ""))

# --- Vorschau -----------------------------------------------------------------

post = {
    "bildtyp": bildtyp, "variante": variante, "headline": headline,
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

with c1:
    if st.button("Entwurf speichern", type="primary"):
        tools.update_confirm(
            collection, x,
            {
                "titel": titel, "bildtyp": bildtyp, "variante": variante,
                "headline": headline, "subline": subline, "image_id": image_id,
                "fit": fit, "ratio": ratio, "caption": caption,
                "kommentar": kommentar, "bearbeitet": bearbeitet,
            },
            False, "🎉 Entwurf gespeichert!",
        )

with c2:
    kann_posten = insta.is_configured() and vorschau is not None and not probleme
    if veroeffentlicht:
        st.button("Bereits veröffentlicht", disabled=True,
                  help="Doppeltes Posten wird verhindert.")
    elif not insta.is_configured():
        st.button("Auf Instagram veröffentlichen", disabled=True,
                  help="Account, Token und öffentliche Bild-Route fehlen noch. "
                       "Siehe insta.md.")
    else:
        if st.button("Auf Instagram veröffentlichen", disabled=not kann_posten):
            try:
                media_id = insta.publish(insta.to_jpeg(vorschau), caption)
                tools.update_confirm(
                    collection, x,
                    {"status": "veroeffentlicht", "ig_media_id": media_id,
                     "published_at": datetime.now(), "last_error": ""},
                    False, "🎉 Auf Instagram veröffentlicht!",
                )
                st.rerun()
            except Exception as e:
                util.logger.error(f"Instagram-Post fehlgeschlagen: {e}")
                collection.update_one(
                    {"_id": x["_id"]},
                    {"$set": {"status": "fehler", "last_error": str(e)}},
                )
                st.error(f"Veröffentlichen fehlgeschlagen: {e}")

st.write(x.get("bearbeitet", ""))
st.sidebar.button("logout", on_click=tools.logout)
