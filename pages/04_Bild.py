import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
from PIL import Image
import io, sys

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
collection = bild

bilder = list(bild.find({}, sort=[("rang", pymongo.ASCENDING)]))

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Bilder")
    with st.expander(f'Neues Bild anlegen', expanded = True if st.session_state.uploaded_file is not None else False):
        titel = st.text_input("Titel des Bildes")
        bildnachweis = st.text_input("Bildnachweis")
        menu = st.toggle("In Auswahlmenüs sichtbar", value = True, key = "menu")
        kommentar = st.text_input("Kommentar")
        col1, col2 = st.columns([1,1]) 
        uploaded_file = col1.file_uploader("Bildatei", type = ["jpg", "jpeg", "png"], help = "Erlaubte Formate sind jpg/jpeg/png.")
        st.session_state.uploaded_file = uploaded_file
        filename = ""
        if st.session_state.uploaded_file is not None:
            filename = st.session_state.uploaded_file.name
            filename = filename.replace(".png", ".jpg")
            image_data = st.session_state.uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_data))
            w, h = image.size                   
            col1.write(f"width: {w}, height: {h}, Größe {int(sys.getsizeof(image_data)/1024)} kb")
            col2.image(image_data, caption = filename)


        submit = st.button("Bild anlegen")
        if submit:
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            image.thumbnail((128,128))
            encoded_thumbnail = io.BytesIO()
            image.save(encoded_thumbnail, format='JPEG')
            encoded_thumbnail = encoded_thumbnail.getvalue()

            ini = {
                "menu": menu,
                "filename": filename,
                "mime": "JPEG",
                "data": encoded_image,
                "thumbnail": encoded_thumbnail,
                "titel": titel,
                "bildnachweis": bildnachweis,
                "kommentar": kommentar,
                "bearbeitet": util.bearbeitet,
                "rang" : min([b["rang"] for b in bilder]) - 1 
            }
            tools.new(collection, ini = ini, switch = True)
    
    if bilder is not None:
        for b in bilder:
            col0, col1, col2, col3, col4 = st.columns([1,1,1,4,15]) 
            with col0:
                st.button('↓', key=f'down-{b["_id"]}', on_click = tools.move_down, args = (collection, b,))
            with col1:
                st.button('↓↓', key=f'alldown-{b["_id"]}', on_click = tools.move_alldown, args = (collection, b,))
            with col2:
                st.button('↑', key=f'up-{b["_id"]}', on_click = tools.move_up, args = (collection, b,))
            with col3:
                st.image(b["thumbnail"])
            with col4:
                s = f"{b['titel']} ({b['filename']}))"
                submit = st.button(s, key=f"edit-{b['_id']}")
            if submit:
                st.session_state.edit = b["_id"]
                st.session_state.uploaded_file = None
                switch_page("bild edit")

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
