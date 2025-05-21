import streamlit as st
from streamlit_image_select import image_select
import pymongo
from datetime import datetime, timedelta
from PIL import Image
import io

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

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.carouselnews
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"                    


# dictionary saving keys from all expanders
ver_updated_all = dict()
save_all = False
addimage = False

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"]))

    st.write("Unter folgenden Links erreicht man die Ansichten auf Monitor und Homepage an folgendem Datum:")
    col1, col2 = st.columns([1, 1])
    col1, col2 = st.columns([1, 1])
    with col1: 
        ansicht_datum = st.date_input("Datum", value = datetime.now().date(), format = "DD.MM.YYYY", key = "ansicht_datum")
    with col2: 
        ansicht_zeit = st.time_input("Zeit", value = datetime.now().time(), key = "ansicht_zeit")
    with col1: 
        t = datetime.combine(ansicht_datum, ansicht_zeit).strftime(util.date_format_no_space)        
        st.write(f"[Testansicht des Monitors](https://www.math.uni-freiburg.de/nlehre/monitortest/{t})")
        st.write(f"[Veröffentlichte Ansicht des Monitors](https://www.math.uni-freiburg.de/nlehre/monitor/{t})")
    with col2: 
        st.write(f"[Testansicht der Homepage (de)](https://www.math.uni-freiburg.de/nlehre/test/de/{t})")
        st.write(f"[Testansicht der Homepage (en)](https://www.math.uni-freiburg.de/nlehre/test/en/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (de)](https://www.math.uni-freiburg.de/nlehre/de/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (en)](https://www.math.uni-freiburg.de/nlehre/en/{t})")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Zurück (ohne Speichern)"):
            st.switch_page("pages/02_Carouselnews.py")
    with col2:
        if st.button("Alles Speichern (außer Änderungen am Bild)", type = 'primary'):
            save_all = True # the actual saving needs to be done after the expanders

    with col3:
        with st.popover('Carouselnews kopieren'):
            st.write("Kopiere " + tools.repr(collection, x["_id"]))
            daten_anpassen = st.checkbox("Startdatum der kopierten News heute, Enddatum in 7 Tagen", value = True, key = f"kopiere_veranstaltung_{x['_id']}_daten")
            colu1, colu2 = st.columns([1,1])
            with colu1:
                submit = st.button(label = "Carouselnews kopieren", type = 'primary', key = f"copy-{x['_id']}")
                if submit:
                    new = { key: value for key, value in x.items()}
                    del new["_id"]
                    if daten_anpassen:
                        new["start"] = tools.heutenulluhr()
                        new["end"] = tools.heutenulluhr() + timedelta(days=7)
                    new["bearbeitet"] = bearbeitet
                    new["rang"] = min([x["rang"] for x in list(collection.find())])-1
                    st.session_state.expanded = "grunddaten"            
                    tools.new(collection, ini = new, text = "🎉 Carouselnews kopiert!")

            with colu2: 
                st.button(label="Abbrechen", on_click = st.success, args=("Nicht kopiert!",), key = f"not-copied-{x['_id']}")

    with col4:
        with st.popover('Carouselnews löschen'):
            st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
            if submit:
                tools.delete_item_update_dependent_items(collection, x["_id"])
            with colu3: 
                st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    with st.expander("Grunddaten", expanded = True if st.session_state.expanded == "grunddaten" else False):
        _public = st.toggle("Veröffentlicht", value = x['_public'], help = "Falls nicht veröffentlicht, ist die News unter ...test zu sehen.")
        text = st.text_area("Text", x["text"])
        left = st.number_input("Linker Rand (in Prozent der ganzen Breite)", value = x["left"], min_value = 0, max_value = 100)
        right = st.number_input("Rechter Rand (in Prozent der ganzen Breite)", value = x["right"], min_value = 0, max_value = 100)
        bottom = st.number_input("Unterer Rand (in Prozent der ganzen Höhe)", value = x["bottom"], min_value = 0, max_value = 100)
        interval = st.number_input("Intervall bis zum nächsten Bild in Milisekunden", value = x["interval"], min_value = 0)
        kommentar = st.text_input("Kommentar", x["kommentar"])
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum = st.date_input("Startdatum", value = x["start"].date(), format = "DD.MM.YYYY", key = f"startdatum")
        with col2:
            startzeit = st.time_input("Startzeit", value = x["start"].time(), key = f"startzeit")
        with col1:
            enddatum = st.date_input("Enddatum", value = x["end"].date(), format = "DD.MM.YYYY", key = f"enddatum")
        with col2:
            endzeit = st.time_input("Endzeit", value = x["end"].time(), key = f"endzeit")
        changegrunddaten = st.button("Grunddaten ändern")
        if changegrunddaten:
            x_updated = {"_public" : _public, "text" : text, "left" : left, "right" : right, "bottom" : bottom, "interval" : interval, "bearbeitet": bearbeitet, "kommentar": kommentar, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit), "rang" : min([x["rang"] for x in list(collection.find())])-1}
            tools.update_confirm(collection, x, x_updated, False, "🎉 Grunddaten geändert!")

    with st.expander("Bild", expanded = True if st.session_state.expanded == "bild" else False): 
        st.write("\n  ")
        co1, co2, co3, co4 = st.columns([5,1, 5,5])
        with co1:
            b = st.session_state.bild.find_one({"_id": x["image_id"] })
            st.image(b["data"])
        with co3: 
            changeimage = st.session_state.changeimage
            changeimage = st.toggle("Bild ändern", value = False, key = "changeimage")
        if st.session_state.changeimage:
            st.session_state.expanded = "bild"
            bilderliste = list(st.session_state.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
            images = [Image.open(io.BytesIO(b["thumbnail"])) for b in bilderliste]
            img = image_select("Bild auswählen", images, return_value = "index")
            img = bilderliste[img]["_id"]
            btn2 = st.button("Bild übernehmen", on_click = tools.changeimagefun, args = (collection, x, {"image_id" : img, "bearbeitet": bearbeitet}, ))

    if save_all:
        x_updated = {"_public" : _public, "text" : text, "left" : left, "right" : right, "bottom" : bottom, "interval" : interval, "bearbeitet": bearbeitet, "kommentar" : kommentar, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit), "rang" : min([x["rang"] for x in list(collection.find())])-1}
        tools.update_confirm(collection, x, x_updated, False, "🎉 Alles gespeichert!")
        st.switch_page("pages/02_Carouselnews.py")
    st.write(x["bearbeitet"])

else: 
    st.switch_page("NEWS.py")

st.sidebar.button("logout", on_click = tools.logout)
