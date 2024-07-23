import streamlit as st
from misc.config import *
import pymongo
import base64
from datetime import datetime, timedelta

# Initialize logging
import logging
from misc.config import log_file

@st.cache_resource
def configure_logging(file_path, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - MI-VVZ - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging(log_file)

def setup_session_state():
    # Das ist die mongodb; 
    # news enthält alle News. 
    # user ist aus dem Cluster user und wird nur bei der Authentifizierung benötigt
    try:
        cluster = pymongo.MongoClient(mongo_location)
        mongo_db_users = cluster["user"]
        st.session_state.user = mongo_db_users["user"]
        st.session_state.group = mongo_db_users["group"]

        mongo_db = cluster["news"]
        logger.debug("Connected to MongoDB")
        st.session_state.bild = mongo_db["bild"]
        st.session_state.carouselnews = mongo_db["carouselnews"]
        st.session_state.news = mongo_db["news"]

    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    user = st.session_state.user
    group = st.session_state.group
    bild = st.session_state.bild
    news = st.session_state.news
    carouselnews = st.session_state.carouselnews

    # sem ist ein gewähltes Semester
    if "days_back" not in st.session_state:
        st.session_state.daysback = 180
    # expanded zeigt an, welches Element ausgeklappt sein soll
    if "expanded" not in st.session_state:
        st.session_state.expanded = ""
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True # change later back to False
    # Element to edit
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    # Determines which page we are on
    if "page" not in st.session_state:
        st.session_state.page = ""

    ### temporary data ###
    ### should be also cleared on every page with tools.
    # data for new termine
    if "veranstaltung_tmp" not in st.session_state:
        st.session_state.veranstaltung_tmp = dict()
    # data for translations
    if "translation_tmp" not in st.session_state:
        st.session_state.translation_tmp = None  # Could be specified

    st.session_state.collection_name = {
        bild: "Bilder",
        news: "News",
        carouselnews: "News im Carousel"
    }


    st.session_state.leer = {
                bild: bild.find_one({"titel": "white"})["_id"]
                }
    leer = st.session_state.leer

    st.session_state.new = {
        bild: {"data": base64.b64encode(b""),
                "mime": "", 
                "filename": "", 
                "titel": "", 
                "bildnachweis": ""},
        carouselnews: {
                "test": True, 
                "_public": True, 
                "start": datetime.now(),
                "end": datetime.now() + timedelta(days=7),
                "interval": 5000, 
                "image_id": leer[bild],
                "left": 30,
                "right": 70, 
                "bottom": 30,
                "text": ""
        },
        news: {
            "link": "",
            "image": [],
            "home": {
                "test": True, 
                "_public": True,
                "archiv": True,
                "showlastday": True,
                "start": datetime.now(),
                "end": datetime.now() + timedelta(days=7),
                "title_de": "",
                "title_en": "",
                "text_de": "",
                "text_en": "",
                "popover_title_de": "",
                "popover_title_en": "",
                "popover_text_de": "",
                "popover_text_en": "",
            },
            "monitor": {
                "test": True, 
                "_public": True,
                "showlastday": True,
                "start": datetime.now(),
                "end": datetime.now() + timedelta(days=7),
                "title": "",
                "text": ""
            }
        }
    }

    st.session_state.abhaengigkeit = {
        bild: [{"collection": carouselnews, "field": "image_id", "list": False},
               {"collection": news, "field": "image", "list": True}]    }

setup_session_state()
collection_name = st.session_state.collection_name
leer = st.session_state.leer
new = st.session_state.new
abhaengigkeit = st.session_state.abhaengigkeit

