import streamlit as st
import pymongo
from datetime import datetime, timedelta
from PIL import Image
import io, sys, time
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

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
st.session_state.collection = st.session_state.vortrag

def save(x_updated, text):
    tools.update_confirm(st.session_state.collection, x, x_updated, False, "Gespeichert!")
    st.session_state.expanded = ""

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = st.session_state.vortragsreihe.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(st.session_state.vortragsreihe, x['_id']))
    st.write(f"**Es werden die Vorträge der letzten {st.session_state.tage} angezeigt. Kann links oben geändert werden.**")

    if x['url'] != "":
        st.write(f"Die veröffentlichte Ansicht der Vorträge ist [hier]({x['url']})")
    sprachen = ["en", "de"]
    with st.popover("Neuen Vortrag anlegen"):
        col1, col2 = st.columns([1,1])
        lang = col1.selectbox("Sprache", sprachen, sprachen.index(x["lang_default"]), key = "lang_new")
        _public = col2.toggle("Veröffentlicht", x["_public_default"], key = "public_new")
        if x["_public"]:
            vortragsreihe = [util.leer[st.session_state.vortragsreihe], st.session_state.edit]
        else:
            vortragsreihe = [st.session_state.edit]
        startdatum = st.date_input("Datum", value = x["start"].date() if x["event"] else datetime.now().date(), format = "DD.MM.YYYY", key = "startdatum_new")
        startzeit = st.time_input("Uhrzeit", value = datetime.min.time(), key = "startzeit_new")
        start = datetime.combine(startdatum, startzeit)
        end = start + timedelta(minutes = x["duration_default"])

        col1, col2 = st.columns([1,1])
        sprecher_de = "" if lang == "en" else col1.text_input("Sprecher (de)", "", key = "sprecher_new")
        sprecher_en = "" if lang != "en" else col1.text_input("Sprecher (en)", "", key = "sprecher_new_en")
        sprecher_affiliation_de = "" if lang == "en" else col2.text_input("Sprecher Affiliation (de)", "",  key = "sprecher_affiliation_de_new")
        sprecher_affiliation_en = "" if lang != "en" else col2.text_input("Sprecher Affiliation (en)", "",  key = "sprecher_affiliation_en_new")
        gastgeber = x["gastgeber_default"]
        sekretariat = x["sekretariat_default"]
        ort_de = x["ort_de_default"]
        ort_en = x["ort_en_default"]
        title_de = "" if lang == "en" else st.text_input("Titel (de)", "",  key = "title_de_new")
        title_en = "" if lang != "en" else st.text_input("Titel (en)", "",  key = "title_en_new")
        text_de = ""
        text_en = ""
        url = ""        
        kommentar_de = ""
        kommentar_en = ""
        kommentar_intern = st.text_area("Kommentar (intern)", "",  key = f"kommentar_intern_new")
        x_updated = { 
                        "vortragsreihe" : vortragsreihe,
                        "sprecher_de" : sprecher_de,
                        "sprecher_en" : sprecher_en,
                        "sprecher_affiliation_de" : sprecher_affiliation_de,
                        "sprecher_affiliation_en" : sprecher_affiliation_en,
                        "ort_de" : ort_de,
                        "ort_en" : ort_en,
                        "gastgeber" : gastgeber,
                        "sekretariat" : sekretariat,
                        "title_de" : title_de,
                        "title_en" : title_en,
                        "text_de" : text_de,
                        "text_en" : text_en,
                        "url" : url, 
                        "lang" : lang,
                        "_public" : _public,
                        "start" : start,
                        "end" : end,
                        "bearbeitet": f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}", 
                        "kommentar_de" : kommentar_de,
                        "kommentar_en" : kommentar_en,
                        "kommentar_intern" : kommentar_intern,
                        }
        submit = st.button("Speichern", type="primary", on_click = tools.new, args = (st.session_state.collection, x_updated, False, "🎉 Vortrag erfolgreich angelegt!"), key = f"save_{x['_id']}")
    
    vor = list(st.session_state.collection.find( {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)},  "vortragsreihe" : { "$elemMatch" : { "$eq" : st.session_state.edit}}}, sort = [("start", pymongo.DESCENDING)]))
    vorreihe = list(st.session_state.vortragsreihe.find({}, sort=[("rang", pymongo.ASCENDING)]))
    save_all = False
    for y in vor:
        with st.expander(tools.repr(st.session_state.collection, y['_id'], False, False).replace("\n", "")):
            col1, col2 = st.columns([4,1])
            submit = col1.button("Speichern", type="primary", key = f"save1_{y['_id']}")
            if submit:
                save_all = True
            with col2:
                with st.popover('Vortrag löschen'):
                    st.write("Eintrag wirklich löschen?")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        delete = st.button(label = "Ja", type = 'primary', key = f"delete-{y['_id']}")
                    if delete:
                        tools.delete_item_update_dependent_items(st.session_state.collection, y['_id'], False)
                        st.rerun()
                    with colu3: 
                        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{y['_id']}")

            col1, col2 = st.columns([1,1])
            lang = col1.selectbox("Sprache", sprachen, sprachen.index(y["lang"]), key = f"lang_{y['_id']}")
            col2.write("")
            col2.write(y["bearbeitet"])
            col1, col2 = st.columns([1,1])
            vortragsreihe = col1.multiselect("Vortragsreihen", [y['_id'] for y in st.session_state.vortragsreihe.find(sort = [("kurzname", pymongo.DESCENDING)])], y["vortragsreihe"], format_func = (lambda a: tools.repr(st.session_state.vortragsreihe, a, True, False)), placeholder = "Bitte auswählen", key = f"vortragsreihe_{y['_id']}")
            col2.write("")
            _public =col2.toggle("Veröffentlicht", y["_public"], key = f"public_{y['_id']}")

            col1, col2, col3, col4 = st.columns([1,1,1,1])
            startdatum = col1.date_input("Datum", value = y["start"].date(), format = "DD.MM.YYYY", key = f"startdatum_{y['_id']}")
            startzeit = col2.time_input("Startzeit", value = y["start"].time(), key = f"startzeit_{y['_id']}")
            start = datetime.combine(startdatum, startzeit)
            enddatum = startdatum
            # st.date_input("Enddatum", value = y["end"].date(), format = "DD.MM.YYYY", key = f"enddatum_{y['_id']}")
            endzeit = col3.time_input("Endzeit", value = y["end"].time(), key = f"endzeit_{y['_id']}")
            end = datetime.combine(enddatum, endzeit)

            col1, col2, col3 = st.columns([1,1,1])
            sprecher_de = y["sprecher_de"] if lang == "en" else col1.text_input("Sprecher (de)", y["sprecher_de"], key = f"sprecher_{y['_id']}")
            sprecher_affiliation_de = y["sprecher_affiliation_de"] if lang == "en" else col2.text_input("Sprecher Affiliation (de)", y["sprecher_affiliation_de"],  key = f"sprecher_affiliation_de_{y['_id']}")
            sprecher_en = y["sprecher_en"] if lang != "en" else col1.text_input("Sprecher (en)", y["sprecher_en"],  key = f"sprecher_en_{y['_id']}")
            sprecher_affiliation_en = y["sprecher_affiliation_en"] if lang != "en" else col2.text_input("Sprecher Affiliation (en)", y["sprecher_affiliation_en"],  key = f"sprecher_affiliation_en_{y['_id']}")
            ort_de = y["ort_de"] if lang == "en" else col3.text_input("Raum (de)", y["ort_de"],  key = f"ort_de_{y['_id']}")
            ort_en = y["ort_en"] if lang != "en" else col3.text_input("Raum (en)", y["ort_en"],  key = f"ort_en_{y['_id']}")

            title_de = y["title_de"] if lang == "en" else st.text_input("Titel (de)", y["title_de"],  key = f"title_de_{y['_id']}")
            title_en = y["title_en"] if lang != "en" else st.text_input("Titel (en)", y["title_en"],  key = f"title_en_{y['_id']}")
            text_de = y["text_de"] if lang == "en" else st.text_area("Zusammenfassung (de)", y["text_de"],  key = f"text_de_{y['_id']}")
            text_en = y["text_en"] if lang != "en" else st.text_area("Abstract (en)", y["text_en"],  key = f"text_en_{y['_id']}")
            url = st.text_input("URL", y["url"],  key = f"url_{y['_id']}")

            kommentar_de = y["kommentar_de"] if lang == "en" else st.text_area("Kommentar (de)", y["kommentar_de"],  key = f"kommentar_de_{y['_id']}")
            kommentar_en = y["kommentar_en"] if lang != "en" else st.text_area("Kommentar (en)", y["kommentar_en"],  key = f"kommentar_en_{y['_id']}")
            kommentar_intern = st.text_area("Kommentar (intern)", y["kommentar_intern"],  key = f"kommentar_intern_{y['_id']}")

            submit = st.button("Speichern", type='primary', key = f"speichern_{y['_id']}")
            if submit:
                save_all = True
            if save_all:    
                y_updated = { 
                             "vortragsreihe" : vortragsreihe,
                             "sprecher_de" : sprecher_de,
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
                             "bearbeitet": f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}", 
                             "kommentar_de" : kommentar_de,
                             "kommentar_en" : kommentar_en,
                             "kommentar_intern" : kommentar_intern,
                             }
                tools.update_confirm(st.session_state.collection, y, y_updated, False, "🎉 Daten des Vortrages geändert!")
                time.sleep(1)
                save_all = False
                st.rerun()


else: 
    st.switch_page("NEWS.py")

st.sidebar.button("logout", on_click = tools.logout)




