import streamlit as st
from streamlit_image_select import image_select
import pymongo
from datetime import datetime
from PIL import Image
import io, sys
from datetime import datetime 

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("NEWS.py")

# load css styles
from misc.css_styles import init_css
init_css()

from misc.config import *
import misc.util as util
import misc.tools as tools
import misc.instagram as insta

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.news
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"                    

# Ein Bild setzen oder entfernen. Bei einer gespeicherten News sofort in der
# Datenbank, bei einer neuen erst in der Vorlage (angelegt wird beim Speichern).
def bild_setzen(img, text, neu, x, xid):
    if neu:
        st.session_state.news_vorlage["image"] = img
    else:
        tools.update_confirm(collection, x, {"image" : img, "bearbeitet" : bearbeitet}, False, text)
    st.session_state[f"bildwahl_{xid}"] = False

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    neu = st.session_state.edit is None
    if neu:
        x = st.session_state.news_vorlage
        xid = f"neu{st.session_state.neu_nr}"
        st.subheader("Neue News")
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        xid = str(x["_id"])
        st.subheader(tools.repr(collection, x["_id"]))

    tools.ansicht_links()

    save = False
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        if st.button("Zurück (ohne Speichern)"):
            st.switch_page("pages/00_New.py")
    with col2:
        if st.button("Speichern", type = 'primary'):
            save = True # gespeichert wird erst unten, wenn alle Eingaben gelesen sind
    if not neu:
        with col3:
            if st.button("News kopieren", help = "Öffnet eine neue News mit diesen Inhalten und dem Zeitraum heute bis in 7 Tagen. Angelegt wird sie erst beim Speichern."):
                tools.news_vorlage_bearbeiten(x)

        with col4:
            # Zwei gestapelte Buttons: erzeugen je einen neuen, eigenständigen
            # Instagram-Post aus dieser News, vorbelegt in der gewählten Sprache
            # (Überschrift und Caption aus title_{lang}/text_{lang}, Institutsname
            # de/en), und springen in den Instagram-Editor. Bild und Text sind
            # danach frei änderbar.
            def _insta_aus_news(lang):
                st.session_state.expanded = ""
                st.session_state.edit = tools.new(
                    st.session_state.instapost,
                    ini={**insta.prefill_from_news(x, lang), "bearbeitet": bearbeitet},
                    switch=False, text="🎉 Instagram-Post aus News erzeugt!",
                )
                tools.insta_als_ungespeichert_merken(st.session_state.edit)
                st.switch_page("pages/10_Instagram_edit.py")

            if st.button('Insta Post (deutsch)', key=f"insta-de-{x['_id']}",
                         help="Neuer Instagram-Post, deutsch vorbelegt."):
                _insta_aus_news("de")
            if st.button('Insta Post (englisch)', key=f"insta-en-{x['_id']}",
                         help="Neuer Instagram-Post, englisch vorbelegt."):
                _insta_aus_news("en")

        with col5:
            with st.popover('News löschen'):
                st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                if submit:
                    tools.delete_item_update_dependent_items(collection, x["_id"])
                with colu3: 
                    st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    st.divider()
    tags = st.multiselect("Tags", alltags, x["tags"], help = "Die Tags steuern, wo die News zu sehen sein wird.", key = f"tags_{xid}")
    col1, col2 = st.columns([1,1])
    with col1:
        highlight = st.toggle("Highlight", value = x["highlight"], help = "News erscheint dauerhaft gelb.", key = f"highlight_{xid}")
    with col2:
        showlastday = st.toggle("Letzten Tag gelb", value = x["showlastday"], help = "News erscheint am letzten Tag gelb.", key = f"showlastday_{xid}")
    with col1:
        startdatum = st.date_input("Startdatum", value = x["start"].date(), format = "DD.MM.YYYY", key = f"startdatum_{xid}")
    with col2:
        startzeit = st.time_input("Startzeit", value = x["start"].time(), key = f"startzeit_{xid}")
    with col1:
        enddatum = st.date_input("Enddatum", value = x["end"].date(), format = "DD.MM.YYYY", key = f"enddatum_{xid}")
    with col2:
        endzeit = st.time_input("Endzeit", value = x["end"].time(), key = f"endzeit_{xid}")
    title_de = st.text_input("Titel (de)", x["title_de"], help = "Erscheint auf der Homepage und auf dem Monitor.", key = f"title_de_{xid}")
    text_de = st.text_area("Text (de)", x["text_de"], help = "Erscheint auf der Homepage und auf dem Monitor.", key = f"text_de_{xid}")
    title_en = st.text_input("Titel (en)", x["title_en"], help = "Für die englische Homepage. Leer: der deutsche Titel wird angezeigt.", key = f"title_en_{xid}")
    text_en = st.text_area("Text (en)", x["text_en"], help = "Für die englische Homepage. Leer: der deutsche Text wird angezeigt.", key = f"text_en_{xid}")
    fuermonitor = "Monitor" in tags
    title_monitor = st.text_input("Abweichender Titel für den Monitor", x["title_monitor"], help = "Nur ausfüllen, wenn auf dem Monitor etwas anderes stehen soll als der deutsche Titel.", disabled = not fuermonitor, key = f"title_monitor_{xid}")
    text_monitor = st.text_area("Abweichender Text für den Monitor", x["text_monitor"], help = "Nur ausfüllen, wenn auf dem Monitor etwas anderes stehen soll als der deutsche Text.", disabled = not fuermonitor, key = f"text_monitor_{xid}")
    link = st.text_input('Link', x["link"], key = f"link_{xid}")
    kommentar = st.text_input('Kommentar', x["kommentar"], help = "Nur intern, erscheint nirgends.", key = f"kommentar_{xid}")

    if save:
        start = datetime.combine(startdatum, startzeit)
        end = datetime.combine(enddatum, endzeit)
        if title_de.strip() == "":
            st.error("Bitte einen Titel (de) eingeben.")
        elif end <= start:
            st.error("Das Ende muss nach dem Start liegen.")
        else:
            x_updated = {"tags" : tags, "showlastday": showlastday, "highlight" : highlight, "link" : link, "bearbeitet": bearbeitet, "kommentar" : kommentar, "start" : start, "end" : end, "title_de" : title_de, "title_en" : title_en, "text_de" : text_de, "text_en" : text_en, "title_monitor" : title_monitor, "text_monitor" : text_monitor}
            if neu:
                collection.insert_one({**x_updated, "image" : x["image"]})
                util.logger.info(f"User {st.session_state.user} hat in News ein neues Item angelegt.")
                tools.flash("🎉 News angelegt!")
            else:
                tools.update_confirm(collection, x, x_updated, False, "🎉 Alles gespeichert!")
            st.switch_page("pages/00_New.py")

    st.divider()
    st.markdown("**Bild**")
    co1, co2 = st.columns([1,1])
    if x["image"] != []:
        with co1:
            b = st.session_state.bild.find_one({"_id": x["image"][0]["_id"] })
            if b is not None:
                image = Image.open(io.BytesIO(b["data"]))
                wi, he = image.size
                st.image(b["data"], caption = f"{b['filename']}, width: {wi}, height: {he}, Größe {int(sys.getsizeof(b['data'])/1024)} kb")
            else:
                st.warning("Das verknüpfte Bild existiert nicht mehr. Bitte ein neues Bild auswählen oder die Verknüpfung entfernen.")
        with co2:
            bildwahl = st.toggle("Bild ändern", value = False, key = f"bildwahl_{xid}")
            st.button("Bild entfernen", on_click = bild_setzen, args = ([], "Bild entfernt!", neu, x, xid), key = f"bild_entfernen_{xid}")
    else:
        bildwahl = st.toggle("Bild hinzufügen", value = False, key = f"bildwahl_{xid}")

    if bildwahl:
        bilderliste = list(st.session_state.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
        images = [tools.get_thumbnail(b["_id"]) for b in bilderliste]
        img = image_select("Bild auswählen", images, return_value = "index")
        img = [{"_id": bilderliste[img]["_id"]}]
        st.button("Bild übernehmen", on_click = bild_setzen, args = (img, "🎉 Bild übernommen!", neu, x, xid), key = f"bild_uebernehmen_{xid}")
    if not neu:
        st.write(x["bearbeitet"])

else: 
    st.switch_page("NEWS.py")

st.sidebar.button("logout", on_click = tools.logout)
