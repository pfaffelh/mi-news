import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from streamlit_image_select import image_select
import pymongo
from datetime import datetime, timedelta
from PIL import Image
import io, sys
from datetime import datetime 

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("NEWS")

# load css styles
from misc.css_styles import init_css
init_css()

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.vortrag
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"                    

def save(x_updated, text):
    tools.update_confirm(collection, x, x_updated, False)
    st.success(text)
    st.session_state.expanded = ""

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = st.session_state.vortragsreihe.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(st.session_state.vortragsreihe, x['_id']))
    st.write("Der Zeitraum, in dem Vorträge angezeigt werden, kann links oben eingestellt werden.")

    with st.popover("Neuen Vortrag anlegen"):
        _public = st.toggle("Veröffentlicht", False, key = "public_new")
        vortragsreihe = [util.leer[st.session_state.vortragsreihe], st.session_state.edit]
        startdatum = st.date_input("Startdatum", value = datetime.now().date(), format = "DD.MM.YYYY", key = "startdatum_new")
        startzeit = st.time_input("Startzeit", value = datetime.min.time(), key = "startzeit_new")
        start = datetime.combine(startdatum, startzeit)
        end = start + timedelta(minutes = x["duration_default"])
    
        col1, col2 = st.columns([1,1])
        sprecher = col1.text_input("Sprecher", "", key = "sprecher_new")
        sprecher_affiliation_de = col2.text_input("Sprecher Affiliation (de)", "",  key = "sprecher_affiliation_de_new")
        sprecher_en = ""
        sprecher_affiliation_en = ""
        ort_de = x["ort_de_default"]
        ort_en = x["ort_en_default"]

        title_de = st.text_input("Titel (de)", "",  key = "title_de_new")
        title_en = st.text_input("Titel (en)", "",  key = "title_en_new")
        text_de = ""
        text_en = ""
        url = ""        
        lang = ""
        kommentar_de = ""
        kommentar_en = ""
        kommentar_intern = st.text_area("Kommentar (intern)", "",  key = f"kommentar_intern_new")
        submit = st.button("Speichern", type='primary', key = f"speichern_{x['_id']}")
        if submit:
            x_updated = { 
                            "vortragsreihe" : vortragsreihe,
                            "sprecher" : sprecher,
                            "sprecher_en" : sprecher_en,
                            "sprecher_affiliation_de" : sprecher_affiliation_de,
                            "sprecher_affiliation_en" : sprecher_affiliation_en,
                            "ort_de" : ort_de,
                            "ort_en" : ort_en,
                            "title_de" : title_de,
                            "title_en" : title_en,
                            "text_de" : text_de,
                            "text_en" : text_en,
                            "url" : url, 
                            "lang" : lang,
                            "_public" : _public,
                            "start" : start,
                            "end" : end,
                            "bearbeitet": bearbeitet, 
                            "kommentar_de" : kommentar_de,
                            "kommentar_en" : kommentar_en,
                            "kommentar_intern" : kommentar_intern,
                            }
            tools.new(collection, x_updated, False)
            st.success("Vortrag angelegt!")

    vor = list(collection.find( {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)},  "vortragsreihe" : { "$elemMatch" : { "$eq" : st.session_state.edit}}}, sort = [("start", pymongo.DESCENDING)]))
    vorreihe = list(st.session_state.vortragsreihe.find({}, sort=[("rang", pymongo.ASCENDING)]))

    for y in vor:
        with st.expander(tools.repr(collection, y['_id'], False, False).replace("\n", "")):
            with st.popover('Vortrag löschen'):
                st.write("Eintrag wirklich löschen?")
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    submit = st.button(label = "Ja", type = 'primary', key = f"delete-{y['_id']}")
                if submit:
                    tools.delete_item_update_dependent_items(collection, y['_id'], False)
                    st.rerun()
                with colu3: 
                    st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{y['_id']}")

            _public = st.toggle("Veröffentlicht", y["_public"], key = f"public_{y['_id']}")
            vortragsreihe = st.multiselect("Vortragsreihen", [y['_id'] for y in st.session_state.vortragsreihe.find(sort = [("kurzname", pymongo.DESCENDING)])], y["vortragsreihe"], format_func = (lambda a: tools.repr(st.session_state.vortragsreihe, a, True, False)), placeholder = "Bitte auswählen", key = f"vortragsreihe_{y['_id']}")
            st.write(y["bearbeitet"])

            col1, col2, col3, col4 = st.columns([1,1,1,1])
            startdatum = st.date_input("Startdatum", value = y["start"].date(), format = "DD.MM.YYYY", key = f"startdatum_{y['_id']}")
            startzeit = st.time_input("Startzeit", value = y["start"].time(), key = f"startzeit_{y['_id']}")
            start = datetime.combine(startdatum, startzeit)
            enddatum = st.date_input("Startdatum", value = y["end"].date(), format = "DD.MM.YYYY", key = f"enddatum_{y['_id']}")
            endzeit = st.time_input("Endzeit", value = y["end"].time(), key = f"endzeit_{y['_id']}")
            end = datetime.combine(enddatum, endzeit)

            col1, col2, col3, col4 = st.columns([1,1,1,1])
            sprecher = col1.text_input("Sprecher", y["sprecher"], key = f"sprecher_{y['_id']}")
            sprecher_affiliation_de = col2.text_input("Sprecher Affiliation (de)", y["sprecher_affiliation_de"],  key = f"sprecher_affiliation_de_{y['_id']}")
            sprecher_en = col3.text_input("Sprecher (en), nur falls abweichend", y["sprecher_en"],  key = f"sprecher_en_{y['_id']}")
            sprecher_affiliation_en = col4.text_input("Sprecher Affiliation (en)", y["sprecher_affiliation_en"],  key = f"sprecher_affiliation_en_{y['_id']}")

            ort_de = st.text_input("Raum (de)", y["ort_de"],  key = f"ort_de_{y['_id']}")
            ort_en = st.text_input("Raum(en)", y["ort_en"],  key = f"ort_en_{y['_id']}")

            title_de = st.text_input("Titel (de)", y["title_de"],  key = f"title_de_{y['_id']}")
            title_en = st.text_input("Titel (en)", y["title_de"],  key = f"title_en_{y['_id']}")
            text_de = st.text_area("Zusammenfassung (de)", y["text_de"],  key = f"text_de_{y['_id']}")
            text_en = st.text_area("Abstract (en)", y["text_en"],  key = f"text_en_{y['_id']}")
            url = st.text_input("URL", y["url"],  key = f"url_{y['_id']}")
            sprachen = ["", "deutsch", "english", "in deutsch und englisch möglich"]
            lang = st.selectbox("Sprache", sprachen, sprachen.index(y["lang"]), key = f"lang_{y['_id']}")

            kommentar_de = st.text_area("Kommentar (de)", y["kommentar_de"],  key = f"kommentar_de_{y['_id']}")
            kommentar_en = st.text_area("Kommentar (en)", y["kommentar_en"],  key = f"kommentar_en_{y['_id']}")
            kommentar_intern = st.text_area("Kommentar (intern)", y["kommentar_intern"],  key = f"kommentar_intern_{y['_id']}")

            submit = st.button("Speichern", type='primary', key = f"speichern_{y['_id']}")
            if submit:
                x_updated = { 
                             "vortragsreihe" : vortragsreihe,
                             "sprecher" : sprecher,
                             "sprecher_en" : sprecher_en,
                             "sprecher_affiliation_de" : sprecher_affiliation_de,
                             "sprecher_affiliation_en" : sprecher_affiliation_en,
                             "ort_de" : ort_de,
                             "ort_en" : ort_en,
                             "title_de" : title_de,
                             "title_en" : title_en,
                             "text_de" : text_de,
                             "text_en" : text_en,
                             "url" : url, 
                             "lang" : lang,
                             "_public" : _public,
                             "start" : start,
                             "end" : end,
                             "bearbeitet": bearbeitet, 
                             "kommentar_de" : kommentar_de,
                             "kommentar_en" : kommentar_en,
                             "kommentar_intern" : kommentar_intern,
                             }
                tools.update_confirm(collection, x, x_updated, False)
                st.success("Daten des Vortrages geändert!")
                st.rerun()

    st.write(y["bearbeitet"])

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)




