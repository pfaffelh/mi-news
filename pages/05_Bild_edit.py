import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from PIL import Image
import io, sys
from datetime import datetime

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("NEWS")

from misc.config import *
import misc.util as util
import misc.tools as tools

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = st.session_state.bild
date_format = '%d.%m.%Y um %H:%M:%S.'
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format)}"

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Bild")

    # check if entry can be found in database
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"], show_collection=False))
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("Bild")
    with col2:
        with st.popover('Bild löschen'):
            s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
            if s:
                st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
            else:
                st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
            if submit:
                tools.delete_item_update_dependent_items(collection, x["_id"])
            with colu3: 
                st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")        
        st.download_button("Download Bild", x["data"], file_name = x["filename"])

    col1, col2 = st.columns([1,1])
    with col1:
        with st.form(f'ID-{x["_id"]}'):
            menu = st.toggle("In Auswahlmenüs sichtbar", value = x["menu"])
            titel = st.text_input("Titel des Bildes", value = x["titel"])
            bildnachweis = st.text_input("Bildnachweis", value = x["bildnachweis"])
            kommentar = st.text_input("Kommentar", value = x["kommentar"])
            filename = st.text_input("Dateiname", value = x["filename"])
            btn1 = st.form_submit_button("Grunddaten speichern")        
            if btn1:
                tools.update_confirm(collection, x, {"menu": menu, "titel": titel, "bildnachweis": bildnachweis, "kommentar": kommentar, "bearbeitet": bearbeitet, "filename": filename}, reset = False)            
    with col2:
        image = Image.open(io.BytesIO(x["data"]))
        st.session_state.w, st.session_state.h = image.size                   
        col2.image(x["data"], caption = f"{x['filename']}, width: {st.session_state.w}, height: {st.session_state.h}, Größe {int(sys.getsizeof(x['data'])/1024)} kb")

    key = f"{x['filename']}_austauschen"
    with st.expander("Bild austauschen", expanded = True if st.session_state.expanded == key else False):
        st.session_state.uploaded_file = st.file_uploader("Neue Bildatei", type = ["jpg", "jpeg", "png"], help = "Erlaubte Formate sind jpg/jpeg/png.", key=key)
        if st.session_state.uploaded_file is not None:
            filename = st.session_state.uploaded_file.name
            filename = filename.replace(".png", ".jpg")
            image_data = st.session_state.uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_data))
            st.session_state.w, st.session_state.h = image.size
            #st.write(key)
            #st.write(f"{filename}_austauschen")
            if key != f"{filename}_austauschen":
                st.image(image, caption = f"{filename}, width: {st.session_state.w}, height: {st.session_state.h}, Größe {int(sys.getsizeof(x['data'])/1024)} kb")
            btn2 = st.button("Bild austauschen")
            if btn2:
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                encoded_image = io.BytesIO()
                image.save(encoded_image, format='JPEG')
                encoded_image = encoded_image.getvalue()
                image.thumbnail((128,128))
                encoded_thumbnail = io.BytesIO()
                image.save(encoded_thumbnail, format='JPEG')
                encoded_thumbnail = encoded_thumbnail.getvalue()
                x_updated = {"filename": filename, "bearbeitet": bearbeitet, "data": encoded_image, "thumbnail": encoded_thumbnail}
                tools.update_confirm(collection, x, x_updated, reset = False, text = "🎉 Bild ausgetauscht!")
                st.session_state.uploaded_file = None
                st.session_state.expanded = key
                st.rerun()

    key = f"{x['_id']}_rotieren"
    with st.expander("Bild rotieren", expanded = True if st.session_state.expanded == key else False):
        col1, col2 = st.columns([1, 1])
        btn_left = col1.button("Nach links drehen")
        btn_right = col2.button("Nach rechts drehen")
        image = Image.open(io.BytesIO(x["data"]))
        if btn_left:
            image = image.rotate(90, expand=True)
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            image.thumbnail((128,128))
            encoded_thumbnail = io.BytesIO()
            image.save(encoded_thumbnail, format='JPEG')
            encoded_thumbnail = encoded_thumbnail.getvalue()            
            tools.update_confirm(collection, x, {"data": encoded_image, "thumbnail": encoded_thumbnail, "bearbeitet": bearbeitet}, reset = False, text = "🎉 Bild gedreht!")
            st.session_state.uploaded_file = None
            st.session_state.expanded = key
            st.rerun()
        if btn_right:
            image = image.rotate(270, expand=True)
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            image.thumbnail((128,128))
            encoded_thumbnail = io.BytesIO()
            image.save(encoded_thumbnail, format='JPEG')
            encoded_thumbnail = encoded_thumbnail.getvalue()            
            tools.update_confirm(collection, x, {"data": encoded_image, "thumbnail": encoded_thumbnail, "bearbeitet": bearbeitet}, reset = False, text = "🎉 Bild gedreht!")
            st.session_state.uploaded_file = None
            st.session_state.expanded = key
            st.rerun()

    key = f"{x['_id']}_crop"
    with st.expander("Bild zuschneiden", expanded = True if st.session_state.expanded == key else False):
        st.write("Wieviele Pixel sollen von jeder Seite entfernt werden?")
        col1, col2 = st.columns([2, 1])
        with col1:
            cols1, cols2, cols3 = st.columns([1,1,1])
            st.session_state.crop_left = 0
            st.session_state.crop_right = 0
            st.session_state.crop_top = 0
            st.session_state.crop_bottom = 0
            if st.session_state.wnew == 0:
                st.session_state.wnew = st.session_state.w
            if st.session_state.hnew == 0:        
                st.session_state.hnew = st.session_state.h
            with cols2:
                st.session_state.crop_top = st.number_input("", value=st.session_state.crop_top, min_value=0, max_value=st.session_state.h - st.session_state.crop_bottom, key = "top")
            cols1, cols2, cols3 = st.columns([1,1,1])
            with cols1:
                st.session_state.crop_left = st.number_input("", value=st.session_state.crop_left, min_value=0, max_value=st.session_state.w - st.session_state.crop_right, key="left")
            with cols3:                 
                st.session_state.crop_right = st.number_input("", value=st.session_state.crop_right, min_value=0, max_value=st.session_state.w - st.session_state.crop_left, key="right")
            cols1, cols2, cols3 = st.columns([1,1,1])
            with cols2:
                st.session_state.crop_bottom = st.number_input("", value=st.session_state.crop_bottom, min_value=0, max_value=st.session_state.h - st.session_state.crop_top, key="bottom")
            st.session_state.expanded = key
        with col2:
            image = Image.open(io.BytesIO(x["data"]))
            image = image.crop((st.session_state.crop_left, st.session_state.crop_top, st.session_state.wnew - st.session_state.crop_right, st.session_state.hnew - st.session_state.crop_bottom))
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            a, b = image.size
            st.image(image, caption = f"{x['filename']}, width: {a}, height: {b}, Größe {int(sys.getsizeof(encoded_image)/1024)} kb")
        with col1: 
            btn4 = st.button("Bild übernehmen", key = key)
            if btn4:
                image = Image.open(io.BytesIO(x["data"]))
                image = image.crop((st.session_state.crop_left, st.session_state.crop_top, st.session_state.wnew - st.session_state.crop_right, st.session_state.hnew - st.session_state.crop_bottom))
                encoded_image = io.BytesIO()
                image.save(encoded_image, format='JPEG')
                encoded_image = encoded_image.getvalue()
                image.thumbnail((128,128))
                encoded_thumbnail = io.BytesIO()
                image.save(encoded_thumbnail, format='JPEG')
                encoded_thumbnail = encoded_thumbnail.getvalue()            
                tools.update_confirm(collection, x, {"data": encoded_image, "thumbnail": encoded_thumbnail, "bearbeitet": bearbeitet}, reset = False, text = "🎉 Bild übernommen")
                st.session_state.expanded = ""
                st.rerun()

    key = f"{x['_id']}_resize"
    with st.expander("Bild verkleinern", expanded = True if st.session_state.expanded == key else False):
        col1, col2 = st.columns([2, 1])
        with col1:
            keep = st.checkbox("Verhältnis von Breite und Höhe beibehalten", value = True)
            st.session_state.wnew = st.number_input("Maximale neue Breite", value=st.session_state.w, min_value=0)
            st.session_state.hnew = st.number_input("Maximale neue Höhe", value=st.session_state.h, min_value=0)
        with col2:
            image = Image.open(io.BytesIO(x["data"]))
            if keep == False:
                image = image.resize((st.session_state.wnew, st.session_state.hnew))
            else:
                image.thumbnail((st.session_state.wnew, st.session_state.hnew))
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            a, b = image.size
            st.image(image, caption = f"{x['filename']}, width: {a}, height: {b}, Größe {int(sys.getsizeof(encoded_image)/1024)} kb")
            st.session_state.expanded = key

        btn5 = st.button("Bild übernehmen", key = key)
        if btn5:
            image = Image.open(io.BytesIO(x["data"]))
            if keep == False:
                image = image.resize((st.session_state.wnew, st.session_state.hnew))
            else:
                image.thumbnail((st.session_state.wnew, st.session_state.hnew))
            encoded_image = io.BytesIO()
            image.save(encoded_image, format='JPEG')
            encoded_image = encoded_image.getvalue()
            image.thumbnail((128,128))
            encoded_thumbnail = io.BytesIO()
            image.save(encoded_thumbnail, format='JPEG')
            encoded_thumbnail = encoded_thumbnail.getvalue()            
            tools.update_confirm(collection, x, {"data": encoded_image, "thumbnail": encoded_thumbnail, "bearbeitet": bearbeitet}, reset = False, text = "🎉 Bild übernommen!")
            st.session_state.expanded = key
            st.rerun()

    key = f"{x['_id']}_quality"
    with st.expander("Qualität des Bildes verringern", expanded = True if st.session_state.expanded == key else False):
        col1, col2 = st.columns([2, 1])
        with col1:
            quality = st.slider("Qualität des Bildes", max_value = 100, min_value = 0, value = 100)
        with col2:
            image = Image.open(io.BytesIO(x["data"]))
            encoded_image = io.BytesIO()
            image.save(encoded_image, optimize=True, quality=quality, format='JPEG')
            encoded_image = encoded_image.getvalue()
            a, b = image.size
            st.image(encoded_image, caption = f"{x['filename']}, width: {a}, height: {b}, Größe {int(sys.getsizeof(encoded_image)/1024)} kb")
            st.session_state.expanded = key

        btn6 = st.button("Bild übernehmen", key = key)
        if btn6:
            image = Image.open(io.BytesIO(x["data"]))
            encoded_image = io.BytesIO()
            image.save(encoded_image, optimize=True, quality=quality, format='JPEG')
            encoded_image = encoded_image.getvalue()
            image.thumbnail((128,128))
            encoded_thumbnail = io.BytesIO()
            image.save(encoded_thumbnail, format='JPEG')
            encoded_thumbnail = encoded_thumbnail.getvalue()            
            tools.update_confirm(collection, x, {"data": encoded_image, "thumbnail": encoded_thumbnail, "bearbeitet": bearbeitet}, reset = False, text = "🎉 Bild übernommen!")
            st.session_state.expanded = key
            st.rerun()
            
    st.write(x["bearbeitet"])

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
