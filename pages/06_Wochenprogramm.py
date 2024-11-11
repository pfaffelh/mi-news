import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta 
import pandas as pd
import pymongo
import io
import tarfile

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("NEWS")

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.vortragsreihe
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Vortragsreihen")
    key = "vortragsreihe_anlegen"
    with st.expander(f'Neue Vortragsreihe anlegen', expanded = True if st.session_state.expanded == key else False):
        _public = st.toggle("Veröffentlicht", value = False)
        title_de = st.text_input("Titel (de)", "")
        title_en = st.text_input("Titel (en)", "")
        text_de = st.text_area("Beschreibung (de)", "")
        text_en = st.text_area("Beschreibung (en)", "")
        link = st.text_input("URL für die Vortragsreihe", "")
        ort_de_default = st.text_input("Üblicher Ort (de), wird automatisch bei Anlegen eines neuen Termins angegeben", "")
        ort_en_default = st.text_input("Üblicher Ort (en), wird automatisch bei Anlegen eines neuen Termins angegeben", "")
        duration_default = st.number_input("Übliche Vortragsdauer in Minuten, wird automatisch bei Anlegen eines neuen Termins angegeben", 90) 
        _public_default = st.toggle("Vorträge bereits beim anlegen veröffentlichen", value = False)
        sync_with_calendar = st.toggle("Mit einem Kalender synchronisieren", value = False)
        calendar_link = st.text_area("URL des Kalenders", "")
        kommentar = st.text_input("Kommentar", "")

        btn = st.button("Vortragsreihe anlegen")
        if btn:
            new = st.session_state.new[collection]
            new["sichtbar"] = True
            new["_public"] = _public
            new["title_de"] = title_de
            new["title_en"] = title_en
            new["text_de"] = text_de
            new["text_en"] = text_en
            new["link"] = link
            new["ort_de_default"] = ort_de_default
            new["ort_en_default"] = ort_en_default
            new["duration_default"] = duration_default
            new["_public_default"] = _public_default
            new["sync_with_calendar"] = sync_with_calendar
            new["calendar_link"] = calendar_link
            new["kommentar"] = kommentar
            new["bearbeitet"] = bearbeitet
            new["rang"] = min([x["rang"] for x in list(collection.find())])-1
            tools.new(collection, ini = new, switch = False)


    aktuell = st.toggle("Nur aktuelle Vortragsreihen anzeigen", True)
    query = { "sichtbar" : True} if aktuell else {}
    vortragsreihen = list(collection.find(query,sort=[("rang", pymongo.ASCENDING)]))

    for x in vortragsreihen:
        co1, co2, co3, co4 = st.columns([1,1,15,5]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co4:
            submit = st.button('Zu den Vorträgen', key=f'talks-{x["_id"]}')
            if submit:
                st.session_state.edit = x["_id"]
                switch_page("Vortrag")

        with co3:
            with st.expander(f"**{tools.repr(collection, x['_id'], False, False)}**"):
                with st.popover('Veranstaltungsreihe löschen'):
                    ini = {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}
                    s = ("  \n".join(tools.find_dependent_items(collection, x['_id'], ini)))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}", disabled = True if x['_id'] == util.leer[collection] else False)
                    if submit:
                        tools.delete_item_update_dependent_items(collection, x['_id'], False)
                        st.rerun()
                    with colu3: 
                        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                sichtbar = st.toggle("Aktuell", x["sichtbar"], key = f"sichtbar_{x['_id']}")
                _public = st.toggle("Veröffentlicht", x["_public"], key = f"public_{x['_id']}")
                title_de = st.text_input("Titel (de)", x["title_de"], key = f"title_de_{x['_id']}")
                title_en = st.text_input("Titel (en)", x["title_en"], key = f"title_en_{x['_id']}")
                text_de = st.text_area("Beschreibung (de)", x["text_de"], key = f"text_de_{x['_id']}")
                text_en = st.text_area("Beschreibung (en)", x["text_en"], key = f"text_en_{x['_id']}")
                url = st.text_input("URL für die Vortragsreihe", x["url"], key = f"url_{x['_id']}")
                ort_de_default = st.text_input("Üblicher Ort (de), wird automatisch bei Anlegen eines neuen Termins angegeben", x["ort_de_default"], key = f"ort_de_default_{x['_id']}")
                ort_en_default = st.text_input("Üblicher Ort (en), wird automatisch bei Anlegen eines neuen Termins angegeben", x["ort_en_default"], key = f"ort_en_default_{x['_id']}")
                duration_default = st.number_input("Übliche Vortragsdauer in Minuten, wird automatisch bei Anlegen eines neuen Termins angegeben", x["duration_default"], key = f"duration_default_{x['_id']}") 
                _public_default = st.toggle("Vorträge bereits beim anlegen veröffentlichen", x["_public_default"], key = f"public_default_{x['_id']}")
                sync_with_calendar = st.toggle("Mit einem Kalender synchronisieren", x["sync_with_calendar"], key = f"sync_with_calendar_{x['_id']}")
                calendar_url = st.text_area("URL des Kalenders", x["calendar_url"]) if sync_with_calendar else x["calendar_url"]
                kommentar = st.text_input("Kommentar (intern)", x["kommentar"], key = f"kommentar_{x['_id']}")
                x_updated = {
                    "sichtbar" : sichtbar,
                    "_public" : _public,
                    "title_de" : title_de,
                    "title_en" : title_en,
                    "text_de" : text_de,
                    "text_en" : text_en,
                    "url" : url,
                    "ort_de_default" : ort_de_default,
                    "duration_default" : duration_default,
                    "_public_default" : _public_default,
                    "sync_with_calendar" : sync_with_calendar,
                    "calendar_url" : calendar_url,
                    "kommentar" : kommentar
                }
                submit = st.button("Speichern", on_click = tools.update_confirm, args = (collection, x, x_updated, ), key = f"save_{x['_id']}")
                

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
