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
        st.write("")

    vor = list(collection.find( {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)},  "vortragsreihe" : { "$elemMatch" : { "$eq" : st.session_state.edit}}}, sort = [("start", pymongo.DESCENDING)]))
    vorreihe = list(st.session_state.vortragsreihe.find({}, sort=[("rang", pymongo.ASCENDING)]))

    for x in vor:
        with st.expander(tools.repr(collection, x['_id'], False, False).replace("\n", "")):
            col1, col2, col3, col4 = st.columns([1,1,1,1])
            _public = col1.toggle("Veröffentlicht", x["_public"], key = f"public_{x['_id']}")
            vortragsreihe = st.multiselect("Vortragsreihen", [x['_id'] for x in st.session_state.vortragsreihe.find(sort = [("kurzname", pymongo.DESCENDING)])], x["vortragsreihe"], format_func = (lambda a: tools.repr(st.session_state.vortragsreihe, a, True, False)), placeholder = "Bitte auswählen", key = f"vortragsreihe_{x['_id']}")
            col3.write(x["bearbeitet"])

            col1, col2, col3, col4 = st.columns([1,1,1,1])
            startdatum = st.date_input("Startdatum", value = x["start"].date(), format = "DD.MM.YYYY", key = f"startdatum_{x['_id']}")
            startzeit = st.time_input("Startzeit", value = x["start"].time(), key = f"startzeit_{x['_id']}")
            start = datetime.combine(startdatum, startzeit)
            enddatum = st.date_input("Startdatum", value = x["end"].date(), format = "DD.MM.YYYY", key = f"enddatum_{x['_id']}")
            endzeit = st.time_input("Endzeit", value = x["end"].time(), key = f"endzeit_{x['_id']}")
            end = datetime.combine(enddatum, endzeit)

            col1, col2, col3, col4 = st.columns([1,1,1,1])
            sprecher = col1.text_input("Sprecher", x["sprecher"], key = f"sprecher_{x['_id']}")
            sprecher_affiliation_de = col2.text_input("Sprecher Affiliation (de)", x["sprecher_affiliation_de"],  key = f"sprecher_affiliation_de_{x['_id']}")
            sprecher_en = col3.text_input("Sprecher (en), nur falls abweichend", x["sprecher_en"],  key = f"sprecher_en_{x['_id']}")
            sprecher_affiliation_en = col4.text_input("Sprecher Affiliation (en)", x["sprecher_affiliation_en"],  key = f"sprecher_affiliation_en_{x['_id']}")

            ort_de = st.text_input("Raum (de)", x["ort_de"],  key = f"ort_de_{x['_id']}")
            ort_en = st.text_input("Raum(en)", x["ort_en"],  key = f"ort_en_{x['_id']}")

            title_de = st.text_input("Titel (de)", x["title_de"],  key = f"title_de_{x['_id']}")
            title_en = st.text_input("Titel (en)", x["title_de"],  key = f"title_en_{x['_id']}")
            text_de = st.text_area("Zusammenfassung (de)", x["text_de"],  key = f"text_de_{x['_id']}")
            text_en = st.text_area("Abstract (en)", x["text_en"],  key = f"text_en_{x['_id']}")
            url = st.text_input("URL", x["url"],  key = f"url_{x['_id']}")
            sprachen = ["deutsch", "english", "in deutsch und englisch möglich"]
            lang = st.selectbox("Sprache", sprachen, sprachen.index(x["lang"]), key = f"lang_{x['_id']}")

            kommentar_de = st.text_area("Kommentar (de)", x["kommentar_de"],  key = f"kommentar_de_{x['_id']}")
            kommentar_en = st.text_area("Kommentar (en)", x["kommentar_en"],  key = f"kommentar_en_{x['_id']}")
            kommentar_intern = st.text_area("Kommentar (intern)", x["kommentar_intern"],  key = f"kommentar_intern_{x['_id']}")

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
                tools.update_confirm(collection, x, x_updated, False)
                st.success("Daten des Vortrages geändert!")

    st.write(x["bearbeitet"])

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)




