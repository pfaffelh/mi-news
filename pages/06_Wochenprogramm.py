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

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Vortragsreihen und Events")
    aktuell = st.toggle("Nur aktuelle Vortragsreihen/Events anzeigen", True)
    with st.expander(f'Neue Vortragsreihe/Event anlegen'):
        col1, col2, col3 = st.columns([1,1,1])
        _public = col1.toggle("Veröffentlicht", value = False)
        event = col2.toggle("Als Event anlegen", value = False)
        _public_default = col3.toggle("Vorträge bereits beim Anlegen veröffentlichen", value = False)
        col1, col2, col3 = st.columns([1,1,1])
        lang_default = col1.selectbox("Typische Sprache", ["en", "de"], index = 0, key ="select_lang_new")
        title_de = "" if lang_default == "en" else col2.text_input("Titel (de)", "")
        title_en = "" if lang_default != "en" else col2.text_input("Titel (en)", "")
        kurzname = col3.text_input("Kurzname", "")
        text_de = "" if lang_default == "en" else st.text_area("Beschreibung (de)", "")
        text_en = "" if lang_default != "en" else st.text_area("Beschreibung (en)", "")
        url = st.text_input("URL für die Vortragsreihe", "")
        if event:
            col1, col2 = st.columns([1,1])        
            startdatum = col1.date_input("Startdatum", datetime.now())
            start = datetime.combine(startdatum, datetime.min.time())
            enddatum = col2.date_input("Enddatum", datetime.now())
            end = datetime.combine(enddatum, datetime.min.time())
            anzeigetage = 30
        else:
            start = datetime.min
            end = datetime.max
            anzeigetage = 7    
        col1, col2 = st.columns([1,1]) 
        gastgeber_default = col1.text_input("Typischer Gastgeber", "")
        sekretariat_default = col2.text_input("Typisches bearbeitendes Sekretariat", "")
        ort_de_default = "" if lang_default == "en" else col1.text_input("Typischer Ort (de), wird automatisch bei Anlegen eines neuen Termins angegeben", "")
        ort_en_default = "" if lang_default != "en" else col1.text_input("Typischer Ort (en), wird automatisch bei Anlegen eines neuen Termins angegeben", "")
        duration_default = col2.number_input("Typische Vortragsdauer in Minuten, wird automatisch bei Anlegen eines neuen Termins angegeben", 90) 
        sync_with_calendar = False # st.toggle("Mit einem Kalender synchronisieren", value = False)
        calendar_url = "" # st.text_area("URL des Kalenders", "")
        kommentar = st.text_input("Kommentar", "")

        btn = st.button("Vortragsreihe anlegen", type="primary")
        if btn:
            new = st.session_state.new[collection]
            new["sichtbar"] = True
            new["event"] = event
            new["lang_default"] = lang_default
            new["_public"] = _public
            new["title_de"] = title_de
            new["title_en"] = title_en
            new["kurzname"] = kurzname
            new["text_de"] = text_de
            new["text_en"] = text_en
            new["url"] = url
            new["ort_de_default"] = ort_de_default
            new["ort_en_default"] = ort_en_default
            new["gastgeber_default"] = gastgeber_default
            new["sekretariat_default"] = sekretariat_default
            new["duration_default"] = duration_default
            new["_public_default"] = _public_default
            new["sync_with_calendar"] = sync_with_calendar
            new["calendar_url"] = calendar_url
            new["kommentar"] = kommentar
            new["start"] = start
            new["end"] = end
            new["anzeigetage"] = anzeigetage            
            new["bearbeitet"] = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"
            new["rang"] = min([x["rang"] for x in list(collection.find())])-1
            tools.new(collection, ini = new, switch = False)

    query = { "sichtbar" : True, "event" : False } if aktuell else {"event" : False}
    vortragsreihen = list(collection.find(query,sort=[("rang", pymongo.ASCENDING)]))

    query = { "sichtbar" : True, "event" : True } if aktuell else {"event" : True}
    events = list(collection.find(query,sort=[("rang", pymongo.ASCENDING)]))

    st.subheader("Vortragsreihen")
    for x in vortragsreihen:
        co1, co2, co3, co4 = st.columns([1,1,15,5]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, { "event" : False }))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, { "event" : False }))
        with co4:
            submit = st.button('Zu den Vorträgen', key=f'talks-{x["_id"]}')
            if submit:
                st.session_state.edit = x["_id"]
                switch_page("Vortrag")
        with co3:
            with st.expander(f"**{tools.repr(collection, x['_id'], False, False)}**"):
                #with st.popover('Veranstaltungsreihe löschen'):
                #    ini = {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}
                #    st.write(collection)
                #    s = ("  \n".join(tools.find_dependent_items(collection, x['_id'], ini)))
                #    if s:
                #        st.write("Eintrag wirklich löschen?  \n" + s + "  \nder letzten " + str(st.session_state.tage) + " Tage werden dadurch geändert.")
                #    else:
                #        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                #    colu1, colu2, colu3 = st.columns([1,1,1])
                #    with colu1:
                #        submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}", disabled = True if x['_id'] == util.leer[collection] else False)
                #    if submit:
                #        tools.delete_item_update_dependent_items(collection, x['_id'], False)
                #        st.rerun()
                #    with colu3: 
                #        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                col1, col2, col3 = st.columns([1,1,1])
                sichtbar = col1.toggle("Aktuell", x["sichtbar"], key = f"sichtbar_{x['_id']}")
                _public = col2.toggle("Veröffentlicht", x["_public"], key = f"public_{x['_id']}")
                _public_default = col3.toggle("Vorträge bereits beim anlegen veröffentlichen", x["_public_default"], key = f"public_default_{x['_id']}")
                col1, col2, col3 = st.columns([1,1,1])
                lang_default = col1.selectbox("Typische Sprache", ["en", "de"], index = 1 if x["lang_default"] == "de" else 0, key = f"lang_default_{x['_id']}")
                title_de = x["title_de"] if lang_default == "en" else col2.text_input("Titel (de)", x["title_de"], key = f"title_de_{x['_id']}")
                title_en = x["title_en"] if lang_default != "en" else col2.text_input("Titel (en)", x["title_en"], key = f"title_en_{x['_id']}")
                kurzname = col3.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}")
                ev = list(collection.find({"kurzname" : kurzname}))
                for e in ev: 
                    if e != x:
                        st.warning(f"Achtung, Kurzname nicht eindeutig, schon bei {e['title_de']} {e['title_en']} verwendet!")
                
                text_de = x["text_de"] if lang_default == "en" else st.text_area("Beschreibung (de)", x["text_de"], key = f"text_de_{x['_id']}")
                text_en = x["text_de"] if lang_default != "en" else st.text_area("Beschreibung (en)", x["text_en"], key = f"text_en_{x['_id']}")
                url = st.text_input("URL für die Vortragsreihe", x["url"], key = f"url_{x['_id']}")
                col1, col2 = st.columns([1,1])        
                gastgeber_default = col1.text_input("Typischer Gastgeber", x["gastgeber_default"], key = f"gastgeber_default_{x['_id']}")
                sekretariat_default = col2.text_input("Typisches bearbeitenden Sekretariat", x["sekretariat_default"], key = f"sekretariat_default_{x['_id']}")
                col1, col2 = st.columns([1,1]) 
                ort_de_default = x["ort_de_default"] if lang_default == "en" else col1.text_input("Typischer Ort (de), wird automatisch bei Anlegen eines neuen Termins angegeben", x["ort_de_default"], key = f"ort_de_default_{x['_id']}")
                ort_en_default = x["ort_en_default"] if lang_default != "en" else col1.text_input("Typischer Ort (en), wird automatisch bei Anlegen eines neuen Termins angegeben", x["ort_en_default"], key = f"ort_en_default_{x['_id']}")
                duration_default = col2.number_input("Typische Vortragsdauer in Minuten, wird automatisch bei Anlegen eines neuen Termins angegeben", x["duration_default"], key = f"duration_default_{x['_id']}") 
                sync_with_calendar = False # st.toggle("Mit einem Kalender synchronisieren", x["sync_with_calendar"], key = f"sync_with_calendar_{x['_id']}")
                calendar_url = "" # st.text_input("URL des Kalenders", x["calendar_url"], key = f"calendar_url_{x['_id']}") if sync_with_calendar else x["calendar_url"]
                kommentar = st.text_input("Kommentar (intern)", x["kommentar"], key = f"kommentar_{x['_id']}")
                x_updated = {
                    "sichtbar" : sichtbar,
                    "_public" : _public,
                    "lang_default": lang_default,
                    "title_de" : title_de,
                    "title_en" : title_en,
                    "kurzname" : kurzname,
                    "text_de" : text_de,
                    "text_en" : text_en,
                    "url" : url,
                    "gastgeber_default" : gastgeber_default,
                    "sekretariat_default" : sekretariat_default,
                    "url" : url,
                    "ort_de_default" : ort_de_default,
                    "ort_en_default" : ort_en_default,
                    "duration_default" : duration_default,
                    "_public_default" : _public_default,
                    "sync_with_calendar" : sync_with_calendar,
                    "calendar_url" : calendar_url,
                    "kommentar" : kommentar
                }
                submit = st.button("Speichern", type="primary", on_click = tools.update_confirm, args = (collection, x, x_updated, ), key = f"save_{x['_id']}")

    st.subheader("Events")
    for x in events:
        co1, co2, co3, co4 = st.columns([1,1,15,5]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, { "event" : True }))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, { "event" : True }))
        with co4:
            submit = st.button('Zu den Vorträgen', key=f'talks-{x["_id"]}')
            if submit:
                st.session_state.edit = x["_id"]
                switch_page("Vortrag")
        with co3:
            with st.expander(f"**{tools.repr(collection, x['_id'], False, False)}**"):
                with st.popover('Event löschen'):
                    ini = {"start" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}
                    s = ("  \n".join(tools.find_dependent_items(collection, x['_id'], ini)))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nder letzten " + str(st.session_state.tage) + " Tage werden dadurch geändert.")
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
                col1, col2, col3 = st.columns([1,1,1])
                sichtbar = col1.toggle("Aktuell", x["sichtbar"], key = f"sichtbar_{x['_id']}")
                _public = col2.toggle("Veröffentlicht", x["_public"], key = f"public_{x['_id']}")
                _public_default = col3.toggle("Vorträge bereits beim anlegen veröffentlichen", x["_public_default"], key = f"public_default_{x['_id']}")
                col1, col2, col3 = st.columns([1,1,1])
                lang_default = col1.selectbox("Typische Sprache", ["en", "deutsch"], index = 1 if x["lang_default"] == "deutsch" else 0, key = f"lang_default_{x['_id']}")
                title_de = x["title_de"] if lang_default == "en" else col2.text_input("Titel (de)", x["title_de"], key = f"title_de_{x['_id']}")
                title_en = x["title_de"] if lang_default != "en" else col2.text_input("Titel (en)", x["title_en"], key = f"title_en_{x['_id']}")
                kurzname = col3.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}")
                
                ev = list(collection.find({"kurzname" : kurzname}))
                for e in ev: 
                    if e != x:
                        st.warning(f"Achtung, Kurzname nicht eindeutig, schon bei {e['title_de']} {e['title_en']} verwendet!")

                col1, col2 = st.columns([1,1])
                startdatum = col1.date_input("Startdatum", value = x["start"].date(), format = "DD.MM.YYYY", key = f"startdatum_{x['_id']}")
                start = datetime.combine(startdatum, datetime.min.time())
                enddatum = col2.date_input("Enddatum", value = x["end"].date(), format = "DD.MM.YYYY", key = f"enddatum_{x['_id']}")
                end = datetime.combine(enddatum, datetime.min.time())
                
                text_de = x["text_de"] if lang_default == "en" else st.text_area("Beschreibung (de)", x["text_de"], key = f"text_de_{x['_id']}")
                text_en = x["text_en"] if lang_default != "en" else st.text_area("Beschreibung (en)", x["text_en"], key = f"text_en_{x['_id']}")
                url = st.text_input("URL für das Event", x["url"], key = f"url_{x['_id']}")
                col1, col2 = st.columns([1,1])
                gastgeber_default = col1.text_input("Gastgeber", x["gastgeber_default"], key = f"gastgeber_default_{x['_id']}")
                sekretariat_default = col2.text_input("Sekretariat", x["sekretariat_default"], key = f"sekretariat_default_{x['_id']}")
                col1, col2 = st.columns([1,1])
                ort_de_default = x["ort_de_default"] if lang_default == "en" else col1.text_input("Ort (de)", x["ort_de_default"], key = f"ort_de_default_{x['_id']}")
                ort_en_default = x["ort_en_default"] if lang_default != "en" else col1.text_input("Ort (en)", x["ort_en_default"], key = f"ort_en_default_{x['_id']}")
                duration_default = col2.number_input("Typische Vortragsdauer in Minuten, wird automatisch bei Anlegen eines neuen Termins angegeben", x["duration_default"], key = f"duration_default_{x['_id']}") 
                sync_with_calendar = False # st.toggle("Mit einem Kalender synchronisieren", x["sync_with_calendar"], key = f"sync_with_calendar_{x['_id']}")
                calendar_url = "" # st.text_input("URL des Kalenders", x["calendar_url"], key = f"calendar_url_{x['_id']}") if sync_with_calendar else x["calendar_url"]
                kommentar = st.text_input("Kommentar (intern)", x["kommentar"], key = f"kommentar_{x['_id']}")
                x_updated = {
                    "sichtbar" : sichtbar,
                    "_public" : _public,
                    "lang_default" : lang_default,
                    "title_de" : title_de,
                    "title_en" : title_en,
                    "kurzname" : kurzname,
                    "start"  : start,
                    "end" : end, 
                    "text_de" : text_de,
                    "text_en" : text_en,
                    "url" : url,
                    "ort_de_default" : ort_de_default,
                    "ort_en_default" : ort_en_default,
                    "duration_default" : duration_default,
                    "_public_default" : _public_default,
                    "sync_with_calendar" : sync_with_calendar,
                    "calendar_url" : calendar_url,
                    "kommentar" : kommentar
                }
                submit = st.button("Speichern", type="primary", on_click = tools.update_confirm, args = (collection, x, x_updated, ), key = f"save_{x['_id']}")                

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
