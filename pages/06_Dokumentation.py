
import streamlit as st
from streamlit_extras.switch_page_button import switch_page 

# Seiten-Layout
st.set_page_config(page_title="NEWS", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    with st.expander("# Allgemeines"):
        st.markdown("Diese App steuert die News auf der Seite .../lehre, sowie auf dem Bildschirm im EG.\n  Hier können sowohl Bilder in eine Datenbank geladen werden, als auch die News verfasst werden. Es geht dabei sowohl um die News im Carousel (Carouselnews), als auch die dauernd sichtbaren News. Der übliche Workflow einer News sieht wiefolgt aus:\n  * Eine News kommt herein, und man loggt sich in die App ein.\n  * Soll ein Bild mit angezeigt werden, braucht man ei entsprechendes jpg oder png, sowie eine Idee, ob die News auf dem Bildschirm und/oder der Homepage angezeigt werden soll.\n  * Das Bild lädt man in die Datenbank ('Bilder' in der Navigation). Dort hat man auch eine beschränkte Möglichkeit, das Bild zu bearbeiten (Drehen, zuschneiden, Datei verkleinern. In der Bildunterschrift sieht man jeweils ein paar Daten des Bildes, etwa die Dateigröße.).\n  * Unter News -> Neue News anlegen bekommt man ein paar der möglichen Felder angezeigt. Hier ist _Veröffentlicht_ zunächst noch nicht angegeben, weil man ja erstmal die News ansehen will, bevor man sie veröffentlicht. Titel (das ist der Titel auf dem Monitor und der deutsche Titel auf der Homepage), Start/Enddatum der Anzeige lassen sich angeben, sowie das soeben angelegte Bild.\n  * Man schaut etwa [hier](http://www2.mathematik.privat/monitortest/), wie die News angezeigt wird, und kann sie dann den eigenen Wünschen folgend ändern.\n  * Ist man zufrieden, dann clickt man bei der News auf _Veröffentlicht_, und kann das Ergebnis [hier](http://www2.mathematik.privat/monitor/) ansehen.")
        
