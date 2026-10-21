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
    st.header("Dokumentation")

    with st.expander("Allgemeines", expanded=True):
        st.markdown("""
Mit dieser App pflegt man alles, was am Institut als Neuigkeit erscheint. Die App zeigt nichts selbst an, sie schreibt in die Datenbank. Angezeigt wird es hier:

| Was | Wo es erscheint |
|---|---|
| News mit Tag „Monitor“ | [Bildschirm im EG](http://mfs1.mathematik.privat:3000/) (nur im Institutsnetz) |
| News mit Tag „Institut“ | [Instituts-Homepage](https://www.math.uni-freiburg.de) |
| News mit Tag „Lehre“ | [Lehre-Homepage](https://www.math.uni-freiburg.de/nlehre/de/) |
| Vorträge und Events | [Wochenprogramm](https://www.math.uni-freiburg.de/wochenprogramm/), Monitor, wöchentliche Mail |
| Instagram-Posts | [@math_uni_freiburg](https://www.instagram.com/math_uni_freiburg/) |

Die Anmeldung geht mit der Uni-Kennung, nur im Uni-Netz oder per VPN, und nur für Mitglieder der Gruppe „news“.

Links in der Seitenleiste stellt man ein, wie weit die Listen zurückreichen („Welche News sollen angezeigt werden?“). Das gilt für News, Vorträge und die Bildauswahl bei Instagram.

Gespeichert wird nur mit dem jeweiligen Knopf. Wer eine Seite über die Seitenleiste verlässt, verliert nicht gespeicherte Eingaben.
""")

    with st.expander("News"):
        st.markdown("""
**Anlegen.** Unter *News → Neue News anlegen* gibt man alles in einer Maske ein:

- **Tags** legen fest, wo die News erscheint: Monitor, Lehre-Homepage, Instituts-Homepage, auch mehreres zugleich.
- **Zeitraum** (Start und Ende) gilt für alle diese Stellen.
- **Titel und Text (de)** erscheinen auf der Homepage und auf dem Monitor. **Titel und Text (en)** sind optional und erscheinen auf der englischen Homepage; bleiben sie leer, steht dort der deutsche Text.
- **Titel und Text für den Monitor** sind ebenfalls optional. Man füllt sie nur aus, wenn dort etwas anderes stehen soll als der deutsche Text, etwa eine kürzere Fassung. Die Felder sind nur mit dem Tag „Monitor“ bearbeitbar.
- **Highlight** färbt die News dauerhaft gelb, **Letzten Tag gelb** nur an ihrem letzten Tag.
- **Link** wird auf der Homepage als „Mehr erfahren“ und auf dem Monitor als QR-Code gezeigt.
- **Kommentar** ist nur intern.
- **Bild**: Unter der Maske wählt man ein Bild aus der Bilddatenbank (siehe *Bilder*).

Ohne Titel (de) oder mit einem Ende vor dem Start wird nicht gespeichert.

**Veröffentlichen.** Mit *Speichern* ist die News veröffentlicht: Sie erscheint, sobald ihr Zeitraum beginnt, und kommt danach ins News-Archiv. Eine neue News entsteht erst beim Speichern; *Zurück (ohne Speichern)* lässt nichts zurück.

**Ansehen.** Über die Links oben auf der Seite sieht man Monitor und Homepage zu einem wählbaren Zeitpunkt, auch in der Zukunft.

**Kopieren.** *News kopieren* öffnet eine neue News mit denselben Inhalten und dem Zeitraum heute bis in 7 Tagen. Angelegt wird sie erst beim Speichern.

**Instagram.** *Insta Post (deutsch/englisch)* legt aus der News einen Instagram-Entwurf an (siehe *Instagram*).

**Reihenfolge.** Die News mit dem spätesten Start steht oben, auf Monitor und Homepages. Wird eine alte News mit neuem Zeitraum wiederverwendet, rutscht sie also nach oben. Die Übersicht in dieser App ist genauso sortiert; was gerade online ist, hat einen grünen Knopf.
""")

    with st.expander("Bilder"):
        st.markdown("""
Bilder liegen in einer eigenen Datenbank und werden von News und Instagram-Posts nur verknüpft. Dasselbe Bild kann also mehrfach verwendet werden.

**Hochladen.** Unter *Bilder → Neues Bild anlegen*: jpg, png oder pdf. Von einer PDF wird die erste Seite verwendet. Gespeichert wird immer als JPEG.

- **Titel** dient nur zum Wiederfinden.
- **Bildnachweis** erscheint auf der Seite [Bildnachweis](https://www.math.uni-freiburg.de/nlehre/de/bildnachweis/), solange eine News mit diesem Bild läuft.
- **In Auswahlmenüs sichtbar**: Ist das aus, wird das Bild bei News und Instagram nicht mehr zur Auswahl angeboten. Bereits verknüpfte Bilder bleiben.

**Reihenfolge.** Mit ↑, ↓ und ↓↓ (ans Ende) ordnet man die Liste. In dieser Reihenfolge erscheinen die Bilder auch in den Auswahlmenüs.

**Bearbeiten.** Ein Klick auf das Bild öffnet es. Dort kann man es austauschen, drehen, zuschneiden, verkleinern, die Qualität verringern (kleinere Datei), herunterladen oder löschen. Die Bildunterschrift zeigt Breite, Höhe und Dateigröße. Wird ein Bild gelöscht, verlieren News, die es benutzen, ihr Bild; Instagram-Posts bekommen ein leeres weißes Bild.
""")

    with st.expander("Wochenprogramm: Vortragsreihen und Events"):
        st.markdown("""
Unter *Wochenprogramm* gibt es zwei Arten von Einträgen:

- **Vortragsreihen** wie Kolloquium oder Oberseminare. Sie laufen unbefristet.
- **Events** wie Workshops oder Tagungen, mit Start- und Enddatum. Ein Event steht im Menü des Wochenprogramms, bis es vorbei ist, und auf dem Monitor in den 30 Tagen davor. Es kann ein eigenes Programm aus Vorträgen haben.

Die Reihe **„alle“** ist das Gesamtprogramm. Vorträge einer im Wochenprogramm sichtbaren Reihe kommen beim Anlegen automatisch auch dorthin.

**Felder einer Reihe:**

- **Kurzname**: Aus ihm entsteht die Seite im Wochenprogramm, zum Beispiel `…/wochenprogramm/de/vortragsreihe/Kolloquium/`, bei Events `…/event/<kurzname>/`. Er muss eindeutig sein und sollte nur Buchstaben, Ziffern, - und _ enthalten. Ändert man ihn, ändert sich auch die Adresse. Die Kurznamen der festen Reihen (etwa Kolloquium, Algebra, Stochastik und „alle“) sind gesperrt.
- **Externe Homepage** (optional): eine eigene Seite außerhalb des Wochenprogramms. Bei Events verlinkt das Wochenprogramm darauf.
- **Typische Sprache** bestimmt die Reihenfolge der Felder und die Vorbelegung neuer Vorträge.
- **Titel und Beschreibung** gibt es in beiden Sprachen. Fehlt eine, wird die andere angezeigt.
- **Typischer Raum, Vortragsdauer, Gastgeber, Sekretariat** werden in neue Vorträge übernommen.
- **Aktuell** steuert nur, ob die Reihe in dieser App bei „Nur aktuelle anzeigen“ erscheint.
- **Im Wochenprogramm sichtbar** schaltet die Reihe auf der Homepage ein oder aus.
- **Vorträge bereits beim Anlegen veröffentlichen** setzt bei neuen Vorträgen das Häkchen *Veröffentlicht* vor.

Oben in jeder Reihe stehen die Links auf ihre Seite im Wochenprogramm (deutsch und englisch) und, falls vorhanden, auf die externe Homepage.
""")

    with st.expander("Wochenprogramm: Vorträge"):
        st.markdown("""
Mit *Zu den Vorträgen* öffnet man die Vorträge einer Reihe. Oben stehen wieder die Links auf die Seite im Wochenprogramm.

**Anlegen.** *Neuen Vortrag anlegen* fragt nur das Nötigste ab: Sprache, Datum, Uhrzeit, Sprecher, Affiliation, Raum (vorbelegt mit dem typischen Raum der Reihe) und Titel. Das Ende ergibt sich aus der typischen Vortragsdauer. Alles Weitere trägt man danach im Vortrag nach.

**Bearbeiten.** Ein Klick auf den Vortrag öffnet ihn:

- **Sprecher, Affiliation und Raum** gibt es nur einmal; sie gelten für die deutsche und die englische Seite.
- **Titel, Abstract und Kommentar** gibt es je Sprache. Die Sprache des Vortrags steht zuerst. Die andere ist optional; bleibt sie leer, zeigt die Seite der anderen Sprache den vorhandenen Text. Im Abstract wird einfache LaTeX-Formatierung umgesetzt.
- **Vortragsreihen**: Ein Vortrag kann in mehreren Reihen stehen, etwa in einem Oberseminar und im Kolloquium. Für das Gesamtprogramm muss „alle“ dabei sein.
- **URL**: ein Link zum Vortrag, etwa zu Folien oder einer Ankündigung.
- **Veröffentlicht**: Nur veröffentlichte Vorträge erscheinen irgendwo.

**Wo Vorträge erscheinen:**

- auf den Seiten des Wochenprogramms (deutsch und englisch) und in deren Kalenderdateien (ICS),
- auf dem Monitor als eine Meldung „Vorträge der nächsten sieben Tage“; Events der nächsten 30 Tage bekommen je eine eigene Meldung,
- in der Mail mit dem Wochenprogramm der folgenden Woche, die jeden Sonntag um 12:30 an mathkoll@math.uni-freiburg.de geht.
""")

    with st.expander("Instagram"):
        st.markdown("""
Instagram-Posts sind eigenständig und nicht an eine News gebunden: Bild und Text sind meist andere, die Beschreibung darf länger sein. Es gibt zwei Arten:

- **Post aus Text**: ein Bild im Uni-Design (Hintergrund gelb, blau, weiß oder sand), auf das Überschrift und Unterzeile geschrieben werden. Die Sprache bestimmt, ob „Mathematisches Institut“ oder „Mathematical Institute“ darauf steht.
- **Post aus Bild**: ein Bild aus der Bilddatenbank, im Format 4:5 (hoch, empfohlen), 1:1 oder 1.91:1. Beim Zuschnitt wählt man, ob nichts abgeschnitten, formatfüllend abgeschnitten oder das Bild mit Rand vollständig gezeigt wird.

Einen Post aus Text kann man auch direkt aus einer News anlegen (*Insta Post* im News-Editor). Überschrift und Beschreibung sind dann vorbelegt.

**Beschreibung (Caption).** Höchstens 2200 Zeichen und 30 Hashtags. Instagram kennt kein Fett oder Kursiv, und ausgeschriebene Links sind im Post nicht klickbar.

**Speichern und Verwerfen.** *Entwurf speichern* speichert, ohne zu posten. *Zurück (ohne Speichern)* verwirft einen nie gespeicherten Entwurf wieder. Die Vorschau lässt sich als JPEG herunterladen.

**Veröffentlichen.** *Auf Instagram veröffentlichen* postet sofort; die Kommentare werden dabei abgeschaltet. Unter *Später posten* legt man einen Zeitpunkt fest; gepostet wird dann automatisch, auch wenn niemand die App offen hat (Prüfung alle 15 Minuten). Ein Post wird nie doppelt veröffentlicht. Veröffentlichte Posts lassen sich in der App nicht löschen; das geht nur in der Instagram-App.

**Zugang.** Der Zugang zu Instagram (Token) erneuert sich jeden Montag automatisch. Läuft er trotzdem bald ab, erscheint auf der Seite *Instagram* eine Warnung.
""")
