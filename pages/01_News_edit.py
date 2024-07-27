import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from streamlit_image_select import image_select
import pymongo
import time
import pandas as pd
import translators as ts
from itertools import chain
from bson import ObjectId
from datetime import datetime, timedelta
from PIL import Image
import io

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
collection = util.news

# dictionary saving keys from all expanders
ver_updated_all = dict()
save_all = False
changeimage = False
addimage = False


# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = util.news.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"]))
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Zurück (ohne Speichern)"):
            switch_page("News")
    with col2:
        if st.button("Alles Speichern (außer Änderungen am Bild)", type = 'primary'):
            save_all = True # the actual saving needs to be done after the expanders

    with col3:
        with st.popover('News kopieren'):
            st.write("Kopiere " + tools.repr(collection, x["_id"]))
            st.write("Was soll mitkopiert werden?")
            kopiere_grunddaten = st.checkbox("Grunddaten inkl Bild", value = True, key = f"kopiere_news_{x['_id']}_grunddaten")
            kopiere_monitor = st.checkbox("Daten für Monitor", value = False, key = f"kopiere_veranstaltung_{x['_id']}_monitor")
            kopiere_home = st.checkbox("Daten für Homepage", value = True, key = f"kopiere_veranstaltung_{x['_id']}_komm")
            daten_anpassen = st.checkbox("Startdatum heute, Enddatum in 7 Tagen", value = True, key = f"kopiere_veranstaltung_{x['_id']}_daten")
            colu1, colu2 = st.columns([1,1])
            with colu1:
                submit = st.button(label = "News kopieren", type = 'primary', key = f"copy-{x['_id']}")
                if submit:
                    new = st.session_state.new[util.news]
                    if kopiere_grunddaten:
                        new["image"] = x["image"]
                        new["_public"] = x["_public"]
                        new["showlastday"] = x["showlastday"]
                        new["archiv"] = x["archiv"]
                        new["link"] = x["link"]
                    if kopiere_monitor:
                        new["monitor"] = x["monitor"]
                    if kopiere_home:
                        new["home"] = x["home"]
                    if daten_anpassen:
                        new["monitor"]["start"] = tools.heutenulluhr()
                        new["monitor"]["end"] = tools.heutenulluhr() + timedelta(days=7)
                        new["home"]["start"] = tools.heutenulluhr()
                        new["home"]["end"] = tools.heutenulluhr() + timedelta(days=7)
                    if "_id" in new:
                        del new["_id"]
                    n = util.news.insert_one(new)
                    st.session_state.edit = n.inserted_id            
                    st.session_state.expanded = ""
                    switch_page("News_edit")
                    st.rerun()
            with colu2: 
                st.button(label="Abbrechen", on_click = st.success, args=("Nicht kopiert!",), key = f"not-copied-{x['_id']}")

    with col4:
        with st.popover('News löschen'):
            st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
            if submit:
                tools.delete_item_update_dependent_items(collection, x["_id"])
            with colu3: 
                st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    with st.expander("Grunddaten", expanded = True if st.session_state.expanded == "grunddaten" else False):
        _public = st.toggle("Veröffentlicht", value = x["_public"], help = "Falls nicht veröffentlicht, ist die News unter ...test zu sehen.")
        showlastday = st.toggle("Letzten Tag anzeigen", value = x["showlastday"], help = "News erscheint gelb am letzten Tag.")
        archiv = st.toggle("Ins Archiv aufnehmen", value = x["archiv"], help = "Erscheint nach Ablauf im Archiv auf der Homepage.")        
        link = st.text_input('Link', x["link"])
        changegrunddaten = st.button("Grunddaten ändern")
        if changegrunddaten:
            util.news.update_one({"_id": x["_id"]}, { "$set" : { "_public" : _public, "showlastaday": showlastday, "archiv" : archiv, "link" : link}})
            st.success("Grunddaten geändert!")
    with st.expander("Daten für Monitor ändern", expanded = True if st.session_state.expanded == "monitordaten" else False):
        title = st.text_input("Titel", x["monitor"]["title"])
        text = st.text_area("Text", x["monitor"]["text"])
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum = st.date_input("Startdatum", value = x["monitor"]["start"].date(), format = "DD.MM.YYYY", key = "startdatum_monitor")
        with col2:
            startzeit = st.time_input("Startzeit", value = x["monitor"]["start"].time(), key = "startzeit_monitor")
        with col1:
            enddatum = st.date_input("Enddatum", value = x["monitor"]["end"].date(), format = "DD.MM.YYYY", key = "enddatum_monitor")
        with col2:
            endzeit = st.time_input("Endzeit", value = x["monitor"]["end"].time(), key = "endzeit_monitor")
        btnmonitor = st.button("Monitordaten ändern")
        if btnmonitor:
            util.news.update_one({"_id": x["_id"]}, { "$set" : { "monitor" : {"title" : title, "text" : text, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit)} }})
            st.success("Monitordaten erfolgreich geändert!")
            st.session_state.expanded = ""
            switch_page("News_edit")

    with st.expander("Daten für Homepage ändern", expanded = True if st.session_state.expanded == "homepagedaten" else False):
        title_de = st.text_input("Titel (de)", x["home"]["title_de"])
        title_en = st.text_input("Titel (en)", x["home"]["title_en"])
        text_de = st.text_area("Text (de)", x["home"]["text_de"])
        text_en = st.text_area("Text (en)", x["home"]["text_en"])
        popover_title_de = st.text_input("Popover Titel (de)", x["home"]["popover_title_de"])
        popover_title_en = st.text_input("Popover Titel (en)", x["home"]["popover_title_en"])
        popover_text_de = st.text_area("Popover Text (de)", x["home"]["popover_text_de"])
        popover_text_en = st.text_area("Popover Text (en)", x["home"]["popover_text_en"])        
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum = st.date_input("Startdatum", value = x["monitor"]["start"].date(), format = "DD.MM.YYYY", key = "startdatum_home")
        with col2:
            startzeit = st.time_input("Startzeit", value = x["monitor"]["start"].time(), key = "startzeit_home")
        with col1:
            enddatum = st.date_input("Enddatum", value = x["monitor"]["end"].date(), format = "DD.MM.YYYY", key = "enddatum_home")
        with col2:
            endzeit = st.time_input("Endzeit", value = x["monitor"]["end"].time(), key = "endzeit_home")
        btnhome = st.button("Homepage, Daten ändern")
        if btnhome:
            util.news.update_one({"_id": x["_id"]}, { "$set" : { "home" : {"title_de" : title_de, "title_en" : title_en,  "text_de" : text_de, "text_en" : text_en, "popover_title_de" : popover_title_de, "popover_title_en" : popover_title_en,  "popover_text_de" : popover_text_de, "popover_text_en" : popover_text_en, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit)} }})
            st.success("Homepage, Daten erfolgreich geändert!")
            st.session_state.expanded = ""
            switch_page("News_edit")

    if save_all:
        util.news.update_one({"_id": x["_id"]}, { "$set" : { "_public" : _public, "showlastaday": showlastday, "archiv" : archiv, "link" : link, "monitor" : {"title" : title, "text" : text, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit)}, "home" : {"title_de" : title_de, "title_en" : title_en,  "text_de" : text_de, "text_en" : text_en, "popover_title_de" : popover_title_de, "popover_title_en" : popover_title_en,  "popover_text_de" : popover_text_de, "popover_text_en" : popover_text_en, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit)} }})
        st.success("News geändert!")
        time.sleep(2)
#        switch_page("NEWS")

    with st.expander("Bild", expanded = True if st.session_state.expanded == "bild" else False): 
        co1, co2, co3 = st.columns([2,2,2])
        if x["image"] != []:
            stylehome = x["image"][0]["stylehome"]
            stylemonitor = x["image"][0]["stylemonitor"]
            widthmonitor = x["image"][0]["widthmonitor"]
            with co1:
                b = util.bild.find_one({"_id": x["image"][0]["_id"] })
                st.image(b["data"])
            with co2: 
                changeimage = st.button("Bild ändern", key = "changeimage")
            with co3: 
                deleteimage = st.button("Bild löschen", key = "delete_image")   
                if deleteimage:
                    util.news.update_one({"_id": x["_id"]}, { "$set": { "image" : [] }})
                    st.success("Bild erfolgreich gelöscht!")
                    st.rerun()
        else:
            stylehome = ""
            stylemonitor = ""
            widthmonitor = 5
            addimage = st.button("Bild hinzufügen", key = "addimage")
        if changeimage or addimage:
            bilderliste = list(util.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
            images = [Image.open(io.BytesIO(b["thumbnail"])) for b in bilderliste]
            img = image_select("Bild auswählen", images, return_value = "index")
            img = bilderliste[img]["_id"]
            img = [{"_id": img, "stylehome": stylehome, "stylemonitor": stylemonitor, "widthmonitor": widthmonitor}]
            n = util.news.update_one({"_id": x["_id"]}, { "$set" : { "image" : img } })
            st.success("Bild erfolgreich geändert!")
            st.session_state.edit = n.upserted_id            
            st.session_state.expanded = ""
            switch_page("News_edit")

    if x["image"] != []:
       with st.expander("Einstellung für das Bild", expanded = True if st.session_state.expanded == "cssimage" else False):
            stylehome = st.text_input("css-Style für die Homepage", value = x["image"][0]["stylehome"])
            stylemonitor = st.text_input("css-Style für den Monitor", value = x["image"][0]["stylemonitor"])
            widthmonitor = st.text_input("css-Style für die Homepage", value = x["image"][0]["widthmonitor"])
            takecss = st.button("Daten übernehmen", key = "takecss")
            if takecss:
                img = [{"_id": x["image"][0]["_id"], "stylehome": stylehome, "stylemonitor": stylemonitor, "widthmonitor": widthmonitor}]
                n = util.news.update_one({"_id": x["_id"]}, { "$set" : { "image" : img } })
                st.success("Einstellungen des Bildes erfolgreich geändert!")
                st.session_state.edit = n.inserted_id
                st.session_state.expanded = ""
                switch_page("News_edit")



else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
