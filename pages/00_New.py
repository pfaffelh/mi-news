import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
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
bild = st.session_state.bild
news = st.session_state.news
carouselnews = st.session_state.carouselnews
collection = news

# Ab hier wird die Seite angezeigt
st.write(st.session_state.logged_in)
if st.session_state.logged_in:
    st.header("News")
    with st.expander(f'Neue News anlegen'):
        _public = st.toggle("Veröffentlicht", value = False, help = "Falls nicht veröffentlicht, ist die News unter ...test zu sehen.")
        showlastday = st.toggle("Letzten Tag anzeigen", value = False, help = "News erscheint gelb am letzten Tag.")
        archiv = st.toggle("Archivieren", value = False, help = "News erscheint im Archiv nach dem Ablauf.")
        titel = st.text_input("Titel", "")
        images = [Image.open(io.BytesIO(b["data"])) for b in list(bild.find({"mime": "jpeg"}))]
        img = image_select("Bild auswählen", images)

        

        name_de=st.text_input('Name (de)', "")
        name_en=st.text_input('Name (en)', "")
        kurzname=st.text_input('Kurzname', "", help = "Wird im Raumplan verwendet.")
        pe = list(util.person.find({"semester": { "$elemMatch": { "$eq": st.session_state.semester_id}}}, sort = [("name", pymongo.ASCENDING)]))
        per_dict = {p["_id"]: tools.repr(util.person, p["_id"], False, True) for p in pe }
        doz_list = st.multiselect("Dozent*innen", per_dict.keys(), [], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
        doz = list(util.person.find({"_id": {"$in": doz_list}}, sort=[("name", pymongo.ASCENDING)]))
        doz_list = [d["_id"] for d in doz]
        kat = [g["_id"] for g in list(util.rubrik.find({"semester": st.session_state.semester_id}))]
        kat = st.selectbox("Rubrik", [x for x in kat], index = 0, format_func = (lambda a: tools.repr(util.rubrik, a)))
        v = {
            "name_de": name_de,
            "name_en": name_en,
            "kurzname": kurzname,
            "dozent": doz_list,
            "rubrik": kat,
        }
        submit = st.button("Veranstaltung anlegen", on_click=tools.veranstaltung_anlegen, args = (st.session_state.semester_id, kat, v), type="primary")
        if submit:
            switch_page("veranstaltungen edit")

    if st.session_state.semester_id is not None:
        kat = list(util.rubrik.find({"semester": st.session_state.semester_id}, sort=[("rang", pymongo.ASCENDING)]))
        for k in kat:
            st.write(k["titel_de"])
            ver = list(util.veranstaltung.find({"rubrik": k["_id"]},sort=[("rang", pymongo.ASCENDING)]))
            for v in ver:
                col1, col2, col3 = st.columns([1,1,23]) 
                with col1:
                    st.button('↓', key=f'down-{v["_id"]}', on_click = tools.move_down, args = (collection, v,{"rubrik": v["rubrik"]}, ))
                with col2:
                    st.button('↑', key=f'up-{v["_id"]}', on_click = tools.move_up, args = (collection, v, {"rubrik": v["rubrik"]},))
                with col3:
                    d = [(util.person.find_one({"_id": x}))["name"] for x in v["dozent"]]
                    s = f"{v['name_de']} ({', '.join(d) if d else ''})"
                    submit = st.button(s, key=f"edit-{v['_id']}")
                if submit:
                    st.session_state.edit = v["_id"]
                    st.session_state.expanded = "termine"
                    switch_page("veranstaltungen edit")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
