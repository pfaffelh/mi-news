import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta 
import pandas as pd
import pymongo
from PIL import Image
import io
import tarfile


def create_tgz_in_memory(files):
    tgz_buffer = io.BytesIO()
    with tarfile.open(fileobj=tgz_buffer, mode="w:gz") as tar:
        for filename, file_content in files.items():
            file_obj = io.BytesIO(file_content)
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(file_content)
            tar.addfile(tarinfo, fileobj=file_obj)
    tgz_buffer.seek(0)  # Setze den Zeiger auf den Anfang des Streams
    return tgz_buffer

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("NEWS.py")

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.news
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"


if 'initial_zeit' not in st.session_state:
    st.session_state.initial_zeit = datetime.now().time()

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("News")
    tools.ansicht_links()

    if st.button("Neue News anlegen", type = "primary"):
        tools.news_vorlage_bearbeiten()

    st.write(f"**Es werden die News der letzten {st.session_state.tage} Tage angezeigt. Kann links oben geändert werden.**")
    st.write("Sortiert wie auf der Homepage: neueste (nach Startdatum) zuerst. :green-background[Grün] = gerade online.")

    news_display = list(collection.find({"end" : {"$gte" : datetime.now() + timedelta(days = - st.session_state.tage)}}, sort=[("start", pymongo.DESCENDING)]))

    jetzt = datetime.now()
    co1, co2, co3, co4 = st.columns([3,10,5,5]) 
    co2.markdown("**Titel**")
    co3.markdown("Zeitraum")
    co4.markdown("Wo")
    for x in news_display:
        st.divider()
        co1, co2, co3, co4 = st.columns([3,10,5,5]) 
        zeitraum = f"{x['start'].strftime(util.datetime_format)} bis {x['end'].strftime(util.datetime_format)}"
        label = tools.repr(collection, x["_id"], False)
        if x["start"] <= jetzt <= x["end"]:
            label = f":green-background[{label}]"
        with co1:
            if x["image"] != []:
                b = st.session_state.bild.find_one({"_id": x["image"][0]["_id"]})
                if b is not None:
                    st.image(b["thumbnail"])
        with co2:
            submit = st.button(label, key=f"edit-{x['_id']}")
        with co3: 
            st.write(zeitraum)
        with co4: 
            st.write(", ".join(x["tags"]))
        if submit:
            st.session_state.edit = x["_id"]
            st.switch_page("pages/01_News_edit.py")

    st.divider()        
    with st.expander("Download data"):
        bilder = {}
        data = []
        for x in news_display:
            item = {}
            item["titel"] = x["title_de"]
            item["text"] = x["text_de"]
            item["link"] = x["link"]
            item["filename"] = ""
            if x["image"] != []:
                b = st.session_state.bild.find_one({"_id" : x["image"][0]["_id"]})
                bilder[b["filename"]] = b["data"]
                item["filename"] = b["filename"]
            data.append(item)
        df = pd.DataFrame.from_records(data)
        st.write(df)
        tgz_buffer = create_tgz_in_memory(bilder)
        st.download_button(
            label="Download .tgz",
            data=tgz_buffer,
            file_name="bilder.tgz",
            mime="application/x-tgz"
        )

else: 
    st.switch_page("NEWS.py")

st.sidebar.button("logout", on_click = tools.logout)
