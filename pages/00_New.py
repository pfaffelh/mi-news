import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta 

import pymongo
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
collection = util.news

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("News")
    col1, col2 = st.columns([1, 1])
    with col1: 
        st.write("[http://gateway.mathematik.uni-freiburg.de/monitortest](Testansicht des Monitors)")
        st.write("[http://gateway.mathematik.uni-freiburg.de/monitor](Veröffentlichte Ansicht des Monitors)")
    with col2: 
        st.write("[http://gateway.mathematik.uni-freiburg.de/de/test](Testansicht der Homepage (de))")
        st.write("[http://gateway.mathematik.uni-freiburg.de/en/test](Testansicht der Homepage (en))")
        st.write("[http://gateway.mathematik.uni-freiburg.de/de/](Veröffentlichte Ansicht der Homepage (de))")
        st.write("[http://gateway.mathematik.uni-freiburg.de/en/](Veröffentlichte Ansicht der Homepage (en))")

    key = "news_anlegen"
    with st.expander(f'Neue News anlegen', expanded = True if st.session_state.expanded == key else False):
        _public = st.toggle("Veröffentlicht", value = False, help = "Falls nicht veröffentlicht, ist die News unter ...test zu sehen.")
        showlastday = st.toggle("Letzten Tag anzeigen", value = False, help = "News erscheint gelb am letzten Tag.")
        fuermonitor = st.toggle("Für den Monitor", value = True, help = "News erscheint auf dem Monitor.")
        fuerhome = st.toggle("Für Lehre-Homepage", value = True, help = "News erscheint auf der Lehre-Homepage.")
        title = st.text_input("Titel", "")
        text = st.text_area("Text", "")
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum = st.date_input("Startdatum", value = datetime.today(), format = "DD.MM.YYYY", key = f"startdatum")
        with col2:
            startzeit = st.time_input("Startzeit", value = datetime.min.time(), key = f"startzeit")
        with col1:
            enddatum = st.date_input("Enddatum", value = datetime.today() + timedelta(days=7), format = "DD.MM.YYYY", key = f"enddatum")
        with col2:
            endzeit = st.time_input("Endzeit", value = datetime.min.time(), key = f"endzeit")
        mitbild = st.toggle("...mit Bild", value = False, key=None, help="Gibt an, ob es kein oder ein Bild für die News gibt.")
        if mitbild:
            bilderliste = list(util.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
            images = [Image.open(io.BytesIO(b["thumbnail"])) for b in bilderliste]
            img = image_select("Bild auswählen", images, return_value = "index")
            img = bilderliste[img]["_id"]
            img = [{"_id": img, "stylehome": "", "stylemonitor": "", "widthmonitor": 5}]
        else:
            img = []
        btn = st.button("News anlegen")
        if btn:
            new = st.session_state.new[collection]
            new["_public"] = _public
            new["showlastday"] = showlastday
            new["home"]["fuerhome"] = fuerhome
            new["monitor"]["fuermonitor"] = fuermonitor
            new["home"]["title_de"] = title
            new["monitor"]["title"] = title
            new["home"]["text_de"] = text
            new["monitor"]["text"] = text
            new["home"]["start"] = datetime.combine(startdatum, startzeit)
            new["monitor"]["start"] = datetime.combine(startdatum, startzeit)
            new["home"]["end"] = datetime.combine(enddatum, endzeit)
            new["monitor"]["end"] = datetime.combine(enddatum, endzeit)
            new["image"] = img
            new["rang"] = min([x["rang"] for x in list(collection.find())])-1
            st.session_state.expanded = "grunddaten"
            tools.new(collection, ini = new, switch = True)

    def compute_end(n):
        return max(n["home"]["end"], n["monitor"]["end"])   

    news_display = list(collection.find({ "$or" : [{"home.end" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}, {"monitor.end" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}]},sort=[("rang", pymongo.ASCENDING)]))

    co1, co2, co3, co4, co5, co6 = st.columns([1,1,3,10,5,5]) 
    co4.markdown("**Titel**")
    co5.markdown("Monitor")
    co6.markdown("Home")
    for x in news_display:
        st.divider()
        co1, co2, co3, co4, co5, co6 = st.columns([1,1,3,10,5,5]) 
        ms = x["monitor"]["start"]
        me = x["monitor"]["end"]
        hs = x["home"]["start"]
        he = x["home"]["end"]
        monitordate = f"{ms.strftime(util.datetime_format)} bis {me.strftime(util.datetime_format)}" if x["monitor"]["fuermonitor"] else " -- "
        homedate = f"{hs.strftime(util.datetime_format)} bis {he.strftime(util.datetime_format)}" if x["home"]["fuerhome"] else " -- "
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            if x["image"] != []:
#                st.write(x)
                b = util.bild.find_one({"_id": x["image"][0]["_id"]})
#                st.write(x["image"][0])
                st.image(b["thumbnail"])
        with co4:
            abk = f"{x['monitor']['title'].strip()}"
            submit = st.button(tools.repr(collection, x["_id"], False), key=f"edit-{x['_id']}")
        with co5: 
            st.write(monitordate)
        with co6: 
            st.write(homedate)
        if submit:
            st.session_state.edit = x["_id"]
            st.session_state.expanded = ""
            switch_page("news edit")


else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
