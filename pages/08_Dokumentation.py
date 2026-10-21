import streamlit as st
from streamlit_extras.switch_page_button import switch_page 

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("NEWS")

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    with st.expander("# Allgemeines", expanded=True):
        text = """
        Diese App steuert das Wochenprogramm auf dieser [Seite](https://www.math.uni-freiburg.de/wochenprogramm/), sowie die News, die auf
        * dem [Bildschirm im EG](http://mfs1.mathematik.privat:3000/) (nur im Institutsnetz),
        * der [Instituts-Homepage](https://www.math.uni-freiburg.de)
        * der [Lehre-Homepage](https://www.math.uni-freiburg.de/nlehre/de/)
        zu sehen sind.""" 
        st.markdown(text)
    with st.expander("# Wochenprogramm", expanded=False):
        text = """
        Für Einträge in das Wochenprogramm geht man so vor:
        
        - Auswahl der richtigen Vortragsreihe.
        - Unter -> zu den Vorträgen -> Neuer Vortrag lässt sich ein neuer Vortrag anlegen. 
        Ist man fertig und clickt auf -> Veröffentlicht, so ist der Vortrag unter
        [Seite](https://www.math.uni-freiburg.de/wochenprogramm/) sichtbar.
        """
        st.markdown(text)
    with st.expander("# News", expanded=False):
        text = """        
        Hier kann man sowohl Bilder in eine Datenbank laden, als auch News verfassen. Der übliche Workflow einer News sieht wiefolgt aus:  
        
        - Eine News kommt herein, und man loggt sich in die App ein.  
        - Soll ein Bild mit angezeigt werden, braucht man ein entsprechendes jpg, png oder pdf. Das Bild lädt man in die Datenbank ('Bilder' in der Navigation). Dort hat man auch eine beschränkte Möglichkeit, das Bild zu bearbeiten (drehen, zuschneiden, Qualität reduzieren. In der Bildunterschrift sieht man jeweils ein paar Daten des Bildes, insbesondere die Dateigröße).
        - Unter News -> Neue News anlegen gibt man alles in einer Maske ein: Die _Tags_ legen fest, ob die News auf dem Monitor, der Lehre-Homepage und/oder der Instituts-Homepage erscheint. Der Zeitraum gilt für alle diese Stellen. Titel und Text (de) erscheinen auf der Homepage und auf dem Monitor; Titel und Text (en) auf der englischen Homepage. Soll auf dem Monitor etwas anderes stehen, füllt man den abweichenden Titel bzw. Text für den Monitor aus.
        - Mit _Speichern_ ist die News sofort veröffentlicht: sie erscheint, sobald ihr Zeitraum beginnt, und kommt danach ins Archiv. Über die Links oben auf der Seite sieht man Monitor und Homepage zu einem wählbaren Zeitpunkt, auch in der Zukunft.
        - _News kopieren_ öffnet eine neue News mit denselben Inhalten. Angelegt wird sie erst beim Speichern.
        
        Reihenfolge: Die News mit dem spätesten Startdatum steht oben, auf Monitor und Homepages. Wird eine alte News bearbeitet und mit neuem Zeitraum wiederverwendet, rutscht sie also entsprechend ihrem neuen Startdatum nach oben. Die News-Übersicht in dieser App ist genauso sortiert; was gerade online ist, ist dort grün markiert.
        """
        st.markdown(text)
        
        
