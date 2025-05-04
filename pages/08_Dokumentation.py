
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
        * dem [Bildschirm im EG](https://www.math.uni-freiburg.de/nlehre/monitor/),
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
        Hier kann man sowohl Bilder in eine Datenbank laden, als auch News (sowohl als Carouselnews oben im Monitor, als auch Einzelmeldungen) verfassen. Der übliche Workflow einer News sieht wiefolgt aus:  
        
        - Eine News kommt herein, und man loggt sich in die App ein.  
        - Soll ein Bild mit angezeigt werden, braucht man ei entsprechendes jpg oder png, sowie eine Idee, ob die News auf dem Bildschirm und/oder der Homepage angezeigt werden soll.  
        - Das Bild lädt man in die Datenbank ('Bilder' in der Navigation). Dort hat man auch eine beschränkte Möglichkeit, das Bild zu bearbeiten (Drehen, zuschneiden, Datei verkleinern. In der Bildunterschrift sieht man jeweils ein paar Daten des Bildes, etwa die Dateigröße.).
        - Unter News -> Neue News anlegen bekommt man ein paar der möglichen Felder angezeigt. Hier ist _Veröffentlicht_ zunächst noch nicht angegeben, weil man ja erstmal die News ansehen will, bevor man sie veröffentlicht. Titel (das ist der Titel auf dem Monitor und der deutsche Titel auf der Homepage), Start/Enddatum der Anzeige lassen sich angeben, sowie das soeben angelegte Bild.  
        - Man schaut etwa [hier](https://www.math.uni-freiburg.de/nlehre/monitortest/), wie die News angezeigt wird, und kann sie dann den eigenen Wünschen folgend ändern.  
        - Ist man zufrieden, dann clickt man bei der News auf _Veröffentlicht_, und kann das Ergebnis [hier](https://www.math.uni-freiburg.de/nlehre/monitor/) ansehen.
        """
        st.markdown(text)
        
        
