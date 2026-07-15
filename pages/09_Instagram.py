import streamlit as st
import pymongo
from datetime import datetime

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("NEWS.py")

from misc.config import *
import misc.util as util
import misc.tools as tools
import misc.instagram as insta

# Navigation in Sidebar anzeigen
tools.display_navigation()

collection = st.session_state.instapost
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"

STATUS_TEXT = {
    "entwurf": "Entwurf",
    "veroeffentlicht": "Veröffentlicht",
    "fehler": "Fehlgeschlagen",
}

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Instagram")
    st.write(
        "Instagram-Posts sind eigenständig — Bild und Text sind meist andere als "
        "in einer News, und die Beschreibung darf länger sein. "
        f"Kanal: [@math_uni_freiburg](https://www.instagram.com/math_uni_freiburg/)"
    )

    if not insta.is_configured():
        st.info(
            "**Veröffentlichen ist noch nicht möglich.** Es fehlen der "
            "Instagram-Account, der API-Token und die öffentliche Bild-Route. "
            "Entwürfe lassen sich trotzdem anlegen, gestalten und als Bild "
            "herunterladen."
        )
    else:
        # Ein Token, der klaglos abläuft, ist die wahrscheinlichste Ursache
        # dafür, dass das Posten irgendwann nicht mehr funktioniert. Deshalb
        # sichtbar machen, bevor es passiert: Ist er einmal abgelaufen, lässt
        # er sich nicht mehr erneuern.
        rest = insta.token_restlaufzeit()
        if rest is not None and rest < ig_token_warn_days:
            st.warning(
                f"**Der Instagram-Token läuft in {rest} Tagen ab.** Er lässt "
                "sich nur erneuern, solange er lebt — danach muss im "
                "Meta-App-Dashboard von Hand ein neuer erzeugt werden. Bitte "
                "prüfen, ob der wöchentliche Refresh-Job (`bin/refresh_ig_token.py`) "
                "noch läuft."
            )

    if st.button("Neuen Post anlegen", type="primary"):
        # switch=True springt via switch_page("instagram edit") direkt in den
        # Editor und setzt st.session_state.edit.
        tools.new(collection, ini={"bearbeitet": bearbeitet},
                  text="🎉 Post angelegt!")

    st.divider()

    posts = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
    if not posts:
        st.write("Noch keine Posts angelegt.")

    for p in posts:
        col1, col2, col3 = st.columns([2, 8, 3])
        with col1:
            # Miniatur der Vorschau — man erkennt den Post, ohne ihn zu öffnen.
            try:
                bild_data = None
                if p.get("bildtyp") == "bild" and p.get("image_id"):
                    b = st.session_state.bild.find_one({"_id": p["image_id"]})
                    bild_data = b["data"] if b else None
                vorschau, _ = insta.render(p, bild_data)
                if vorschau is not None:
                    st.image(vorschau, width=110)
            except Exception:
                # Eine kaputte Vorschau darf die Liste nicht unbrauchbar machen.
                st.write("—")
        with col2:
            titel = p.get("titel") or p.get("headline") or "(ohne Titel)"
            if st.button(titel, key=f"edit-{p['_id']}"):
                st.session_state.edit = p["_id"]
                st.switch_page("pages/10_Instagram_edit.py")
            st.caption(f"{p.get('ratio', '4:5')} · {(p.get('caption') or '')[:80]}")
        with col3:
            status = p.get("status", "entwurf")
            if status == "veroeffentlicht":
                pa = p.get("published_at")
                wann = pa.strftime(util.datetime_format) if pa else ""
                st.success(f"Veröffentlicht {wann}")
            elif status == "fehler":
                st.error("Fehlgeschlagen")
                if p.get("last_error"):
                    st.caption(p["last_error"][:120])
            else:
                st.info("Entwurf")

else:
    st.switch_page("NEWS.py")

st.sidebar.button("logout", on_click=tools.logout)
