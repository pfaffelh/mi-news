import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from streamlit_image_select import image_select
import pymongo
from datetime import datetime, timedelta
from PIL import Image
import io, sys
from datetime import datetime 

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
collection = st.session_state.news
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(util.date_format)}"                    

def save(x_updated, text):
    tools.update_confirm(collection, x, x_updated, False)
    st.success(text)
    st.session_state.expanded = ""

# dictionary saving keys from all expanders
ver_updated_all = dict()
save_all = False
addimage = False

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"]))

    st.write("Unter folgenden Links erreicht man die Ansichten auf Monitor und Homepage an folgendem Datum:")
    col1, col2 = st.columns([1, 1])
    with col1: 
        ansicht_datum = st.date_input("Datum", value = datetime.now().date(), format = "DD.MM.YYYY", key = "ansicht_datum")
    with col2: 
        ansicht_zeit = st.time_input("Zeit", value = datetime.now().time(), key = "ansicht_zeit")
    with col1: 
        t = datetime.combine(ansicht_datum, ansicht_zeit).strftime(util.date_format_no_space)        
        st.write(f"[Testansicht des Monitors](https://www.math.uni-freiburg.de/nlehre/monitortest/{t})")
        st.write(f"[Veröffentlichte Ansicht des Monitors](https://www.math.uni-freiburg.de/nlehre/monitor/{t})")
    with col2: 
        st.write(f"[Testansicht der Homepage (de)](https://www.math.uni-freiburg.de/nlehre/test/de/{t})")
        st.write(f"[Testansicht der Homepage (en)](https://www.math.uni-freiburg.de/nlehre/test/en/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (de)](https://www.math.uni-freiburg.de/nlehre/de/{t})")
        st.write(f"[Veröffentlichte Ansicht der Homepage (en)](https://www.math.uni-freiburg.de/nlehre/en/{t})")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Zurück (ohne Speichern)"):
            switch_page("new")
    with col2:
        if st.button("Alles Speichern (außer Änderungen am Bild)", type = 'primary'):
            save_all = True # the actual saving needs to be done after the expanders

    with col3:
        with st.popover('News kopieren'):
            st.write("Kopiere " + tools.repr(collection, x["_id"]))
            st.write("Was soll mitkopiert werden?")
            kopiere_grunddaten = st.checkbox("Grunddaten inkl Bild", value = True, key = f"kopiere_news_{x['_id']}_grunddaten")
            kopiere_monitor = st.checkbox("Daten für Monitor", value = True, key = f"kopiere_veranstaltung_{x['_id']}_monitor")
            kopiere_home = st.checkbox("Daten für Homepage", value = True, key = f"kopiere_news_{x['_id']}_home")
            daten_anpassen = st.checkbox("Startdatum der kopierten News heute, Enddatum in 7 Tagen", value = True, key = f"kopiere_news_{x['_id']}_datena")
            colu1, colu2 = st.columns([1,1])
            with colu1:
                submit = st.button(label = "News kopieren", type = 'primary', key = f"copy-{x['_id']}")
                if submit:
                    new = st.session_state.new[collection]
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
                    new["rang"] = min([x["rang"] for x in list(collection.find())])-1
                    st.session_state.expanded = "grunddaten"            
                    tools.new(collection, new)

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
        kommentar = st.text_input('Kommentar', x["kommentar"])
        changegrunddaten = st.button("Grunddaten ändern")
        if changegrunddaten:
            x_updated = { "_public" : _public, "showlastday": showlastday, "archiv" : archiv, "link" : link, "bearbeitet": bearbeitet, "kommentar" : kommentar}
            tools.update_confirm(collection, x, x_updated, False)
            st.success("Grunddaten geändert!")
    with st.expander("Daten für Monitor ändern", expanded = True if st.session_state.expanded == "monitordaten" else False):
        fuermonitor = st.toggle("Für den Monitor", value = x["monitor"]["fuermonitor"], help = "News erscheint auf dem Monitor.")
        title = st.text_input("Titel", x["monitor"]["title"], disabled = not fuermonitor)
        text = st.text_area("Text", x["monitor"]["text"], disabled = not fuermonitor)
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum_monitor = st.date_input("Startdatum", value = x["monitor"]["start"].date(), format = "DD.MM.YYYY", key = "startdatum_monitor", disabled = not fuermonitor)
        with col2:
            startzeit_monitor = st.time_input("Startzeit", value = x["monitor"]["start"].time(), key = "startzeit_monitor", disabled = not fuermonitor)
        with col1:
            enddatum_monitor = st.date_input("Enddatum", value = x["monitor"]["end"].date(), format = "DD.MM.YYYY", key = "enddatum_monitor", disabled = not fuermonitor)
        with col2:
            endzeit_monitor = st.time_input("Endzeit", value = x["monitor"]["end"].time(), key = "endzeit_monitor", disabled = not fuermonitor)
        btnmonitor = st.button("Monitordaten ändern", on_click=save, args = ({ "monitor" : {"fuermonitor": fuermonitor, "title" : title, "text" : text, "start" : datetime.combine(startdatum_monitor, startzeit_monitor), "end" : datetime.combine(enddatum_monitor, endzeit_monitor)} },"Monitordaten erfolgreich geändert!",))
    with st.expander("Daten für Lehre-Homepage ändern", expanded = True if st.session_state.expanded == "homepagedaten" else False):
        fuerhome = st.toggle("Für Lehre-Homepage", value =  x["home"]["fuerhome"], disabled = True if x["image"] == [] else False, help = "Kann hier nur mit Bild veröffentlicht werden!")
        fuerhome = fuerhome and x["image"] != []
        title_de = st.text_input("Titel (de)", x["home"]["title_de"], disabled = not fuerhome)
        title_en = st.text_input("Titel (en)", x["home"]["title_en"], disabled = not fuerhome)
        text_de = st.text_area("Text (de)", x["home"]["text_de"], disabled = not fuerhome)
        text_en = st.text_area("Text (en)", x["home"]["text_en"], disabled = not fuerhome)
        popover_title_de = st.text_input("Popover Titel (de)", x["home"]["popover_title_de"], disabled = not fuerhome)
        popover_title_en = st.text_input("Popover Titel (en)", x["home"]["popover_title_en"], disabled = not fuerhome)
        popover_text_de = st.text_area("Popover Text (de)", x["home"]["popover_text_de"], disabled = not fuerhome)
        popover_text_en = st.text_area("Popover Text (en)", x["home"]["popover_text_en"], disabled = not fuerhome)        
        col1, col2 = st.columns([1,1])
        with col1:
            startdatum_home = st.date_input("Startdatum", value = x["home"]["start"].date(), format = "DD.MM.YYYY", key = "startdatum_home", disabled = not fuerhome)
        with col2:
            startzeit_home = st.time_input("Startzeit", value = x["home"]["start"].time(), key = "startzeit_home", disabled = not fuerhome)
        with col1:
            enddatum_home = st.date_input("Enddatum", value = x["home"]["end"].date(), format = "DD.MM.YYYY", key = "enddatum_home", disabled = not fuerhome)
        with col2:
            endzeit_home = st.time_input("Endzeit", value = x["home"]["end"].time(), key = "endzeit_home", disabled = not fuerhome)
        btnhome = st.button("Homepage, Daten ändern", on_click=save, args = ({ "home" : {"fuerhome": fuerhome, "title_de" : title_de, "title_en" : title_en,  "text_de" : text_de, "text_en" : text_en, "popover_title_de" : popover_title_de, "popover_title_en" : popover_title_en,  "popover_text_de" : popover_text_de, "popover_text_en" : popover_text_en, "start" : datetime.combine(startdatum_home, startzeit_home), "end" : datetime.combine(enddatum_home, endzeit_home)} }, "Homepage, Daten erfolgreich geändert!",))

    if save_all:
        x_updated = { "_public" : _public, "showlastday": showlastday, "archiv" : archiv, "link" : link, "bearbeitet": bearbeitet, "kommentar" : kommentar, "monitor" : {"fuermonitor": fuermonitor, "title" : title, "text" : text, "start" : datetime.combine(startdatum_monitor, startzeit_monitor), "end" : datetime.combine(enddatum_monitor, endzeit_monitor)}, "home" : {"fuerhome": fuerhome, "title_de" : title_de, "title_en" : title_en,  "text_de" : text_de, "text_en" : text_en, "popover_title_de" : popover_title_de, "popover_title_en" : popover_title_en,  "popover_text_de" : popover_text_de, "popover_text_en" : popover_text_en, "start" : datetime.combine(startdatum_home, startzeit_home), "end" : datetime.combine(enddatum_home, endzeit_home)} }
        tools.update_confirm(collection, x, x_updated, False)
        switch_page("new")

    with st.expander("Bild", expanded = True if st.session_state.expanded == "bild" else False): 
        st.write("\n  ")
        co1, co2, co3, co4 = st.columns([5,1, 5,5])
        if x["image"] != []:
            stylehome = x["image"][0]["stylehome"]
            stylemonitor = x["image"][0]["stylemonitor"]
            widthmonitor = x["image"][0]["widthmonitor"]
            with co1:
                b = st.session_state.bild.find_one({"_id": x["image"][0]["_id"] })
                image = Image.open(io.BytesIO(b["data"]))
                wi, he = image.size            
                st.image(b["data"], caption = f"{b['filename']}, width: wi, height: he, Größe {int(sys.getsizeof(b['data'])/1024)} kb")                
            with co3: 
                changeimage = st.session_state.changeimage
                changeimage = st.toggle("Bild ändern", value = False, key = "changeimage")
            with co4: 
                deleteimage = st.button("Bild löschen", key = "delete_image")   
                if deleteimage:                    
                    collection.update_one({"_id": x["_id"]}, { "$set": { "image" : [] }})
                    st.success("Bild erfolgreich gelöscht!")
                    st.rerun()
        else:
            stylehome = ""
            stylemonitor = ""
            widthmonitor = 5
            addimage = st.toggle("Bild hinzufügen", value = addimage, key = "addimage")

        if st.session_state.changeimage or addimage:
            st.session_state.expanded = "bild"
            bilderliste = list(st.session_state.bild.find({"menu": True}, sort=[("rang", pymongo.ASCENDING)]))
            images = [tools.get_thumbnail(b["_id"]) for b in bilderliste]
            img = image_select("Bild auswählen", images, return_value = "index")
            img = bilderliste[img]["_id"]
            img = [{"_id": img, "stylehome": stylehome, "stylemonitor": stylemonitor, "widthmonitor": widthmonitor}]
            btn2 = st.button("Bild übernehmen", on_click = tools.changeimagefun, args = (collection, x, { "image" : img, "bearbeitet": bearbeitet }))
    if x["image"] != []:
       with st.expander("Einstellung für das Bild", expanded = True if st.session_state.expanded == "cssimage" else False):
            st.write("\n  ")
            st.markdown("Styles müssen mit ; getrennt werden. Mögliche Styles sind:\n  * height: 18vw; Dies begrenzt die Höhe des Bildes\n  * width: 10vw; Dies begrenzt die Breite des Bildes.\n  * object-fit: cover; Hier wird das Bild vergrößert, so dass die maximale Fläche ausgenutzt wird.\n  * object-fit: contain; hier werden Ränder gelassen, das Bild ist aber vollständig sichtbar.")
            
            stylehome = st.text_input("css-Style für die Homepage", value = x["image"][0]["stylehome"])
            stylemonitor = st.text_input("css-Style für den Monitor", value = x["image"][0]["stylemonitor"])
            
            st.divider()
            st.markdown("Der Monitor ist in ein Raster mit 12 Spalten eingeteilt. Hier gibt man an, wie viele Spalten das Bild breit sein soll.")
            widthmonitor = st.number_input("Breite für die Homepage", value = x["image"][0]["widthmonitor"], min_value = 0, max_value = 12)
            st.divider()
            takecss = st.button("Daten übernehmen", key = "takecss")
            if takecss:
                img = [{"_id": x["image"][0]["_id"], "stylehome": stylehome, "stylemonitor": stylemonitor, "widthmonitor": widthmonitor}]
                st.session_state.expanded = ""
                tools.update_confirm(collection, x, { "image" : img, "bearbeitet": bearbeitet }, False)
                switch_page("News_edit")
    st.write(x["bearbeitet"])

else: 
    switch_page("NEWS")

st.sidebar.button("logout", on_click = tools.logout)
