import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta 

import pymongo
import pandas as pd
from itertools import chain
from bson import ObjectId
from streamlit_image_select import image_select
from PIL import Image
import io

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
collection = st.session_state.carouselnews
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"                    

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Carouselnews")
    st.write("Unter folgenden Links erreicht man die Ansichten auf Monitor und Homepage an folgendem Datum:")
    col1, col2 = st.columns([1, 1])
    with col1: 
        ansicht_datum = st.date_input("Datum", value = datetime.now().date(), format = "DD.MM.YYYY", key = "ansicht_datum")
    with col2: 
        ansicht_zeit = st.time_input("Zeit", value = datetime.now().time(), key = "ansicht_zeit")
    with col1: 
        t = datetime.combine(ansicht_datum, ansicht_zeit).strftime(util.date_format_no_space)        
        st.write(f"[Testansicht des Monitors](http://gateway.mathematik.uni-freiburg.de/monitortest/{t})")
        st.write(f"[Veröffentlichte Ansicht des Monitors](http://gateway.mathematik.uni-freiburg.de/monitor/{t})")
    with col2: 
        st.write(f"[Testansicht der Homepage (de)](http://gateway.mathematik.uni-freiburg.de/test/de/{t})")
        st.write(f"[Testansicht der Homepage (en)](http://gateway.mathematik.uni-freiburg.de/test/en/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (de)](http://gateway.mathematik.uni-freiburg.de/de/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (en)](http://gateway.mathematik.uni-freiburg.de/en/{t})")
    with st.expander(f'Neue News anlegen', expanded = True if st.session_state.expanded == "news_anlegen" else False):
        st.write("\n  ")
        _public = st.toggle("Veröffentlicht", value = False, help = "Falls nicht veröffentlicht, ist die News unter ...test zu sehen.")
        text = st.text_area("Text", "")
        left = st.number_input("Linker Rand (in Prozent der ganzen Breite)", value = 30, min_value = 0, max_value = 100)
        right = st.number_input("Rechter Rand (in Prozent der ganzen Breite)", value = 70, min_value = 0, max_value = 100)
        bottom = st.number_input("Unterer Rand (in Prozent der ganzen Höhe)", value = 30, min_value = 0, max_value = 100)
        interval = st.number_input("Intervall bis zum nächsten Bild in Milisekunden", value = 5000, min_value = 0)
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum = st.date_input("Startdatum", value = datetime.today(), format = "DD.MM.YYYY", key = f"startdatum")
        with col2:
            startzeit = st.time_input("Startzeit", value = datetime.min.time(), key = f"startzeit")
        with col1:
            enddatum = st.date_input("Enddatum", value = datetime.today() + timedelta(days=7), format = "DD.MM.YYYY", key = f"enddatum")
        with col2:
            endzeit = st.time_input("Endzeit", value = datetime.min.time(), key = f"endzeit")
        mitbild = st.toggle("...mit Bild", value = False, key=None, help="Falls nicht, ist der Hintergrund weiß.")
        if mitbild:
            bilderliste = list(st.session_state.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
            images = [Image.open(io.BytesIO(b["thumbnail"])) for b in bilderliste]
            img = image_select("Bild auswählen", images, return_value = "index")
            img = bilderliste[img]["_id"]
        else:
            img = st.session_state.leer[st.session_state.bild]
        btn = st.button("News anlegen")
        if btn:
            ini = {"_public" : _public, "text" : text, "left" : left, "right" : right, "bottom" : bottom, "interval" : interval, "start" : datetime.combine(startdatum, startzeit), "end" : datetime.combine(enddatum, endzeit), "bearbeitet": bearbeitet, "image_id" : img, "rang" : min([x["rang"] for x in list(collection.find())])-1}
            st.session_state.expanded = "grunddaten"
            tools.new(collection, ini = ini, switch = True)

    carouselnews_display = list(collection.find({"end" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}},sort=[("rang", pymongo.ASCENDING)]))

    co1, co2, co3, co4, co5 = st.columns([1,1,3,10,5]) 
    for x in carouselnews_display:
        st.divider()
        co1, co2, co3, co4, co5 = st.columns([1,1,3,10,5]) 
        ms = x["start"]
        me = x["end"]
        monitordate = f"{ms.strftime(util.datetime_format)} bis {me.strftime(util.datetime_format)}" if ms < me else " -- "
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            b = st.session_state.bild.find_one({"_id": x["image_id"]})
            st.image(b["thumbnail"])
        with co4:
            submit = st.button(tools.repr(collection, x["_id"], False), key=f"edit-{x['_id']}")
        with co5: 
            st.write(monitordate)
        if submit:
            st.session_state.edit = x["_id"]
            st.session_state.expanded = ""
            switch_page("carouselnews edit")


else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
