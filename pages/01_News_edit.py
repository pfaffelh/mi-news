import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import time
import pandas as pd
import translators as ts
from itertools import chain
from bson import ObjectId

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

tools.delete_temporary("veranstaltung_tmp")

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.news

# dictionary saving keys from all expanders
ver_updated_all = dict()
save_all = False

news = list(util.news.find(sort=[("kurzname", pymongo.DESCENDING)]))

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    x = util.veranstaltung.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"]))
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Zurück (ohne Speichern)"):
            switch_page("Veranstaltungen")
    with col2:
        if st.button("Alles Speichern", type = 'primary'):
            save_all = True # the actual saving needs to be done after the expanders

    with col3:
        with st.popover('Veranstaltung kopieren'):
            st.write("Kopiere " + tools.repr(collection, x["_id"]))
            st.write("In welches Semester soll kopiert werden?")
            sem_ids = [x["_id"] for x in semesters]
            kop_sem_id = st.selectbox(label="In welches Semester kopieren?", options = sem_ids, index = sem_ids.index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = f"kopiere_veranstaltung_{x['_id']}_sem")
            if kop_sem_id != st.session_state.semester_id:
                st.write("Rubrik und Code können nicht kopiert werden, da sie semesterabhängig sind. URL wird nicht kopiert.")
            st.write("Was soll mitkopiert werden?")
            kopiere_personen = st.checkbox("Personen", value = True, key = f"kopiere_veranstaltung_{x['_id']}_per")
            kopiere_termine = st.checkbox("Termine/Räume", value = False, key = f"kopiere_veranstaltung_{x['_id']}_ter")
            kopiere_kommVVZ = st.checkbox("Kommentiertes VVZ", value = True, key = f"kopiere_veranstaltung_{x['_id']}_komm")
            kopiere_verwendbarkeit = st.checkbox("Verwendbarkeit", value = True, key = f"kopiere_veranstaltung_{x['_id']}_ver")
            colu1, colu2 = st.columns([1,1])
            with colu1:
                submit = st.button(label = "Kopieren", type = 'primary', key = f"copy-{x['_id']}")
                if submit:
                    w_id = tools.kopiere_veranstaltung(x["_id"], kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit)
                    st.success("Erfolgreich kopiert!")
                    time.sleep(2)
                    st.session_state.semester_id = kop_sem_id
                    st.session_state.edit = w_id
                    st.rerun()
            with colu2: 
                st.button(label="Abbrechen", on_click = st.success, args=("Nicht kopiert!",), key = f"not-copied-{x['_id']}")

    with col4:
        with st.popover('Veranstaltung löschen'):
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

    with st.expander("Grunddaten", expanded = True if st.session_state.expanded == "grunddaten" else False):
        #with st.form(f'Grunddaten-{x["_id"]}'):
        hp_sichtbar = st.checkbox("Auf Homepages sichtbar", x["hp_sichtbar"])
        name_de=st.text_input('Name (de)', x["name_de"])
        name_en=st.text_input('Name (en)', x["name_en"])
        midname_de=st.text_input('Mittelkurzer Name (de)', x["midname_de"])
        midname_en=st.text_input('Mittelkurzer Name (en)', x["midname_en"])
        kurzname=st.text_input('Kurzname', x["kurzname"], help = "Wird im Raumplan verwendet.")
        ects=st.text_input('ECTS', x["ects"], help = "Bitte eine typische Anzahl angeben, die genaue Zahl kann vom verwendeten Modul abhängen.")
        kat = [g["_id"] for g in list(util.rubrik.find({"semester": x["semester"]}))]
        index = [g for g in kat].index(x["rubrik"])
        kat = st.selectbox("Rubrik", [x for x in kat], index = index, format_func = (lambda a: tools.repr(util.rubrik, a)))
        code_list = st.multiselect("Codes", [x["_id"] for x in util.code.find({"$or": [{"semester": st.session_state.semester_id}, {"_id": {"$in": x["code"]}}]}, sort = [("rang", pymongo.ASCENDING)])], x["code"], format_func = (lambda a: tools.repr(util.code, a, show_collection=False)), placeholder = "Bitte auswählen", help = "Es können nur Codes aus dem ausgewählten Semester verwendet werden.")
        # Sortiere codes nach ihrem Rang 
        co = list(util.code.find({"_id": {"$in": code_list}}, sort=[("rang", pymongo.ASCENDING)]))
        code_list = [c["_id"] for c in co]
        kommentar_html_de = st.text_area('Kommentar (HTML, de)', x["kommentar_html_de"], help = "Dieser Kommentar erscheint auf www.math...")
        kommentar_html_en = st.text_area('Kommentar (HTML, en)', x["kommentar_html_en"], help = "Dieser Kommentar erscheint auf www.math...")
        url=st.text_input('URL', x["url"], help = "Gemeint ist die URL, auf der Inhalte zur Veranstaltung hinterlegt sind, etwa Skript, Übungsblätter etc.")
        ver_updated = {
            "hp_sichtbar": hp_sichtbar,
            "name_de": name_de,
            "name_en": name_en,
            "midname_de": midname_de,
            "midname_en": midname_en,
            "kurzname": kurzname,
            "ects": ects,
            "rubrik": kat,
            "code": code_list,
            "url": url,
            "kommentar_html_de": kommentar_html_de,
            "kommentar_html_en": kommentar_html_en
        }
        ver_updated_all.update(ver_updated)

        #submit = st.form_submit_button('Speichern (Grunddaten)', type = 'primary')
        submit = st.button('Speichern (Grunddaten)', type = 'primary')
        if submit:
            st.session_state.expanded = "grunddaten"
            tools.update_confirm(collection, x, ver_updated, reset = False)

    with st.expander("Personen, Termine etc", expanded = True if st.session_state.expanded == "termine" else False):
        ## Personen, dh Dozent*innen, Assistent*innen und weitere Organisation
        st.subheader("Personen")
        pe = list(util.person.find({"$or": [{"semester": { "$elemMatch": { "$eq": x["semester"]}}}, {"veranstaltung": { "$elemMatch": { "$eq": x["_id"]}}}]}, sort = [("name", pymongo.ASCENDING)]))
        per_dict = {p["_id"]: tools.repr(util.person, p["_id"], False, True) for p in pe }
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            doz_list = st.multiselect("Dozent*innen", per_dict.keys(), x["dozent"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
            doz = list(util.person.find({"_id": {"$in": doz_list}}, sort=[("name", pymongo.ASCENDING)]))
            doz_list = [d["_id"] for d in doz]
        with col2: 
            ass_list = st.multiselect("Assistent*innen", per_dict.keys(), x["assistent"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
            ass = list(util.person.find({"_id": {"$in": ass_list}}, sort=[("name", pymongo.ASCENDING)]))
            ass_list = [d["_id"] for d in ass]
        with col3: 
            org_list = st.multiselect("Organisation", per_dict.keys(), x["organisation"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
            org = list(util.person.find({"_id": {"$in": org_list}}, sort=[("name", pymongo.ASCENDING)]))
            org_list = [d["_id"] for d in org]

        st.subheader("Wöchentliche Termine")
        wt = x["woechentlicher_termin"]

        # check for new termine in session state
        tmp_id_start = len(wt)
        if "woechentlicher_termin" in st.session_state.veranstaltung_tmp:
            for termin in st.session_state.veranstaltung_tmp["woechentlicher_termin"]:
                wt.append(termin)
        termin_remove_id = -1 # id which was removed -1 => no entry removed

        woechentlicher_termin = []
        for i, w in enumerate(wt):
            # skip temporary removed temine
            if i in st.session_state.veranstaltung_tmp["woechentlicher_termin_removed"]:
                continue

            cols = st.columns([1,1,10,5,5,5,1])
            disable_move = ((len(st.session_state.veranstaltung_tmp["woechentlicher_termin_removed"])) > 0)  or i >= tmp_id_start
            with cols[0]:
                st.write("")
                st.write("")
                st.button('↓', key=f'down-w-{i}', on_click = tools.move_down_list, args = (collection, x["_id"], "woechentlicher_termin", w,), disabled=disable_move)
            with cols[1]:
                st.write("")
                st.write("")
                disable = False if tmp_id_start > i else True 
                st.button('↑', key=f'up-w-{i}', on_click = tools.move_up_list, args = (collection, x["_id"], "woechentlicher_termin", w,), disabled=disable_move)
            with cols[2]:
                terminart_list = list(util.terminart.find({}, sort = [("rang", pymongo.ASCENDING)]))
                terminart_dict = {r["_id"]: tools.repr(util.terminart, r["_id"], show_collection = False) for r in terminart_list}
                index = [g["_id"] for g in terminart_list].index(w["key"])
                w_key = st.selectbox("Art des Termins", terminart_dict.keys(), index, format_func = (lambda a: terminart_dict[a]), key = f"wt_{i}")
            with cols[3]:
                wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
                try:
                    wochentag_index = wochentage.index(w["wochentag"])
                except:
                    wochentag_index = None
                w_wochentag = st.selectbox("Tag", wochentage, wochentag_index, key = f"termin_{i}_wochentag", placeholder = "Bitte auswählen")
            with cols[4]:
                start_display = w["start"] if w["start"] else None # datetime.time(9, 00)
                w_start = st.time_input("Start", start_display, key =f"termin_{i}_start", step=3600)
            with cols[5]:
                ende_display = w["ende"] if w["ende"] else None # datetime.time(9, 00)
                w_ende = st.time_input("Ende", ende_display, key =f"termin_{i}_ende", step=3600)
            with cols[6]:
                st.write("")
                st.write("")
                if st.button('✕', key=f'close-w-{i}'):
                    termin_remove_id = i

            cols = st.columns([1,1,5,5,15,1])
            with cols[2]:
                termin_raum = list(util.raum.find({"$or": [{"sichtbar": True}, {"_id": w["raum"]}]}, sort = [("rang", pymongo.ASCENDING)]))
                termin_raum_dict = {r["_id"]: tools.repr(util.raum, r["_id"], show_collection = False) for r in    termin_raum }
                index = [g["_id"] for g in termin_raum].index(w["raum"])
                w_raum = st.selectbox("Raum", termin_raum_dict.keys(), index, format_func = (lambda a: termin_raum_dict[a]), key = f"termin_{i}_raum")
            with cols[3]:
                w_person = st.multiselect("Personen", per_dict.keys(), w["person"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen", key =f"termin_{i}_person")
            with cols[4]:
                w_kommentar = st.text_input("Kommentar", w["kommentar"], key =f"termin_{i}_kommentar")
            #st.divider()
            woechentlicher_termin.append({
                "key": w_key,
                "raum": w_raum,
                "person": [],
                # wochentag muss so gespeichert werden, um das schema nicht zu verletzen.
                "wochentag": w_wochentag if w_wochentag is not None else "", 
                "start": None if w_start == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_start),
                "ende": None if w_ende == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_ende),
                "person": w_person,
                "kommentar": w_kommentar
            })
        ver_updated = {
            "dozent": doz_list,
            "assistent": ass_list,
            "organisation": org_list,
            "woechentlicher_termin": woechentlicher_termin
        }
        ver_updated_all.update(ver_updated)

        write_tmp(tmp_id_start, "woechentlicher_termin", woechentlicher_termin)

        if termin_remove_id >= 0:
            remove_termin(tmp_id_start, termin_remove_id, "woechentlicher_termin")


        neuer_termin = st.button('Neuer Termin', key = "neuer_wöchentlicher_termin")
        if neuer_termin:
            st.session_state.expanded = "termine"
            leerer_termin = {
                "key": util.terminart.find_one({"name_de": "-"})["_id"],
                "kommentar": "",
                "wochentag": "",
                "raum": util.raum.find_one({"name_de": "-"})["_id"],
                "person": [],
                "start": None,
                "ende": None
            }
            st.session_state.veranstaltung_tmp["woechentlicher_termin"].append(leerer_termin)
            st.rerun()

        st.subheader("Einmalige Termine")
        wt = x["einmaliger_termin"]

        # check for new termine in session state
        tmp_id_start = len(wt)
        if "einmaliger_termin" in st.session_state.veranstaltung_tmp:
            for termin in st.session_state.veranstaltung_tmp["einmaliger_termin"]:
                wt.append(termin)
        termin_remove_id = -1 # id which was removed -1 => no entry removed

        einmaliger_termin = []
        for i, w in enumerate(wt):
            # skip temporary removed temine
            if i in st.session_state.veranstaltung_tmp["einmaliger_termin_removed"]:
                continue

            cols = st.columns([1,1,10,5,5,5,1])
            disable_move = ((len(st.session_state.veranstaltung_tmp["einmaliger_termin_removed"])) > 0)  or i >= tmp_id_start
            with cols[0]:
                st.write("")
                st.write("")
                st.button('↓', key=f'down-e-{i}', on_click = tools.move_down_list, args = (collection, x["_id"], "einmaliger_termin", w,), disabled=disable_move)
            with cols[1]:
                st.write("")
                st.write("")
                st.button('↑', key=f'up-e-{i}', on_click = tools.move_up_list, args = (collection, x["_id"], "einmaliger_termin", w,), disabled=disable_move)
            with cols[2]:
                ta = [g["_id"] for g in list(st.session_state.terminart.find(sort=[("rang", pymongo.ASCENDING)]))]
                index = ta.index(w["key"])
                w_key = st.selectbox("", ta, index = index, format_func = (lambda a: tools.repr(st.session_state.terminart, a)), key = f"et_{i}")
            with cols[3]:
                w_startdatum = st.date_input("Start", value = None if w["startdatum"] == None else w["startdatum"], format = "DD.MM.YYYY", key = f"einmaliger_termin_{i}_startdatum")
                #st.write(type(w_startdatum))
                w_startdatum = None if w_startdatum == None else datetime.datetime.combine(w_startdatum, datetime.time(hour = 0, minute = 0))
            with cols[4]:
                w_enddatum = st.date_input("Ende", value = w["enddatum"], format = "DD.MM.YYYY", key = f"einmaliger_termin_{i}_enddatum")
                w_enddatum = None if w_enddatum == None else datetime.datetime.combine(w_enddatum, datetime.time(hour = 0, minute = 0))                                           
            with cols[5]:
                w_kommentar = st.text_input("Kommentar", w["kommentar"], key =f"einmaliger_termin_{i}_kommentar")
            with cols[6]:
                st.write("")
                st.write("")
                if st.button('✕', key=f'close-e-{i}'):
                    termin_remove_id = i

            cols = st.columns([1,1,5,5,5,5,5,1])
            with cols[2]:
                termin_raum = list(util.raum.find({"$or": [{"sichtbar": True}, {"_id": {"$in": w["raum"]}}]}, sort = [("rang", pymongo.ASCENDING)]))
                termin_raum_dict = {r["_id"]: tools.repr(util.raum, r["_id"], show_collection = False) for r in termin_raum }
                w_raum = st.multiselect("Raum", termin_raum_dict.keys(), w["raum"], format_func = (lambda a: termin_raum_dict[a]), placeholder = "Bitte auswählen", key = f"einmaliger_termin_{i}_raum")
            with cols[3]:
                w_person = st.multiselect("Personen", per_dict.keys(), w["person"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen", key =f"etermin_{i}_person")
            with cols[4]:
                w_startzeit = st.time_input("", value = w["startzeit"], key = f"einmaliger_termin_{i}_startzeit")
                w_startzeit = None if w_startzeit == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_startzeit)
            with cols[5]:
                w_endzeit = st.time_input("", value = w["endzeit"], key = f"einmaliger_termin_{i}_endzeit")
                w_endzeit = None if w_endzeit == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_endzeit)
            einmaliger_termin.append({
                "key": w_key,
                "raum": w_raum,
                "person": [],
                # wochentag muss so gespeichert werden, um das schema nicht zu verletzen.
                "startdatum": w_startdatum,
                "startzeit": w_startzeit,
                "enddatum": w_enddatum,
                "endzeit": w_endzeit,
                "kommentar": w_kommentar
            })
        ver_updated = {
            "dozent": doz_list,
            "assistent": ass_list,
            "organisation": org_list,
            "woechentlicher_termin": woechentlicher_termin,
            "einmaliger_termin": einmaliger_termin
        }
        ver_updated_all.update(ver_updated)

        write_tmp(tmp_id_start, "einmaliger_termin", einmaliger_termin)

        if termin_remove_id >= 0:
            remove_termin(tmp_id_start, termin_remove_id, "einmaliger_termin")


        neuer_termin = st.button('Neuer Termin', key = "neuer_einmaliger_termin")
        submit = st.button('Speichern (Personen, Termine) ', type = 'primary', key = "speichern_einmaliger_termin")

        if neuer_termin:
            leerer_termin = {
                "key": util.terminart.find_one({"name_de": "-"})["_id"],
                "kommentar": "",
                "raum": [],
                "person": [],
                "startdatum": None,
                "startzeit": None,
                "enddatum": None,
                "endzeit": None
            }
            st.session_state.veranstaltung_tmp["einmaliger_termin"].append(leerer_termin)
            st.rerun()

        if submit:
            st.session_state.expanded = "termine"
            sync_termine()
            tools.update_confirm(collection, x, ver_updated, reset = False)
            time.sleep(0.1) ## to show toast
            st.rerun()

    with st.expander("Kommentiertes Vorlesungsverzeichnis", expanded = True if st.session_state.expanded == "kommentiertes_VVZ" else False):
        if st.session_state.translation_tmp is not None:
            x.update(st.session_state.translation_tmp[0])
        inhalt_de = st.text_area('Inhalt (de)', x["inhalt_de"])
        inhalt_en = st.text_area('Inhalt (en)', x["inhalt_en"])
        literatur_de = st.text_area('Literatur (de)', x["literatur_de"])
        literatur_en = st.text_area('Literatur (en)', x["literatur_en"])
        vorkenntnisse_de = st.text_area('Vorkenntnisse (de)', x["vorkenntnisse_de"])
        vorkenntnisse_en = st.text_area('Vorkenntnisse (en)', x["vorkenntnisse_en"])
        kommentar_latex_de = st.text_area('Kommentar (Latex, de)', x["kommentar_latex_de"])
        kommentar_latex_en = st.text_area('Kommentar (Latex, en)', x["kommentar_latex_en"])
        ver_updated = {
            "inhalt_de": inhalt_de,
            "inhalt_en": inhalt_en,
            "literatur_de": literatur_de,
            "literatur_en": literatur_en,
            "vorkenntnisse_de": vorkenntnisse_de,
            "vorkenntnisse_en": vorkenntnisse_en,
            "kommentar_latex_de": kommentar_latex_de,
            "kommentar_latex_en": kommentar_latex_en
        }
        ver_updated_all.update(ver_updated)

        col1_button, col2_button = st. columns([2,5])
        with col1_button:
            submit = st.button('Speichern (Kommentiertes Vorlesungsverzeichnis)', type = 'primary')
        if submit:  # TODO: Update Save all for translation
            st.session_state.expanded = "kommentiertes_VVZ"
            if st.session_state.translation_tmp is not None:
                print(x["kommentar_latex_de"], x["kommentar_latex_en"])
                x.update(st.session_state.translation_tmp[1])
                print(x["kommentar_latex_de"], x["kommentar_latex_en"])
                print(ver_updated["kommentar_latex_de"], ver_updated["kommentar_latex_en"])
                st.session_state.translation_tmp = None
            tools.update_confirm(collection, x, ver_updated, reset = False)
        with col2_button:
            translate = st.button("Übersetzungsvorschlag")
        if translate:
            ver_updated_old = ver_updated.copy()
            for key in ver_updated.keys():
                if "_en" in key and ver_updated[key] == "":
                    ver_updated[key] = ts.translate_text(x[key.replace("_en", "_de")], translator="google", from_language="de", to_language="en")
            st.session_state.expanded = "kommentiertes_VVZ"
            st.session_state.translation_tmp = (ver_updated.copy(), ver_updated_old)
            st.rerun()

    ## Verwendbarkeiten
    with st.expander("Verwendbarkeit", expanded = True if st.session_state.expanded == "verwendbarkeit" else False):
        st.subheader("Verwendbarkeit")
        with st.popover("Aus anderer Veranstaltung importieren", help = "Es wird eine Auswahlliste angezeigt, bestehend aus Veranstaltungen der selben Rubrik, und Veranstaltungen derselben Dozent*innen."):
            ver_auswahl = list(util.veranstaltung.find({"$or": [{"rubrik": x["rubrik"]}, {"dozent": {"$in": x["dozent"]}}]}))
            verwendbarkeit_import = st.selectbox("Veranstaltung", [v["_id"] for v in ver_auswahl], format_func = (lambda a: tools.repr(util.veranstaltung, a, show_collection=False)))
            v = util.veranstaltung.find_one({"_id": verwendbarkeit_import})
            x_updated = {"verwendbarkeit_modul": v["verwendbarkeit_modul"],
                            "verwendbarkeit_anforderung": v["verwendbarkeit_anforderung"],
                            "verwendbarkeit": v["verwendbarkeit"]}
            ver_updated_all.update(ver_updated)

            colu1, colu2 = st.columns([1,1])
            with colu1:
                st.button(label = "Importieren", type = 'primary', on_click = tools.update_confirm, args = (util.veranstaltung, x, x_updated, False), key = f"import-verwendbarkeit-{x['_id']}")
            with colu2: 
                st.button(label="Abbrechen", on_click = st.rerun, args=(), key = f"not-imported-{x['_id']}")

        mo = list(util.modul.find({"$or": [{"sichtbar": True}, {"_id": { "$elemMatch": { "$eq": x["verwendbarkeit_modul"]}}}]}, sort = [("rang", pymongo.ASCENDING)]))

        for m in x["verwendbarkeit_modul"]:
            m1 = util.modul.find_one({"_id" : m})
            l = list(util.studiengang.find({"_id" : { "$in" : m1["studiengang"]}, "semester" : { "$elemMatch" : { "$eq" : st.session_state.semester_id}}}))
            if l == []:
                x["verwendbarkeit_modul"].remove(m)
            
        mo_dict = {m["_id"]: tools.repr(util.modul, m["_id"], show_collection = False) for m in mo }
        mod_list = st.multiselect("Module", mo_dict.keys(), x["verwendbarkeit_modul"], format_func = (lambda a: mo_dict[a]), placeholder = "Bitte auswählen")

        ver_an = list(util.anforderung.find({"$or": [{"sichtbar": True}, {"_id": { "$in": x["verwendbarkeit_anforderung"]}}]}, sort = [("rang", pymongo.ASCENDING)]))
        an_dict = {a["_id"]: tools.repr(util.anforderung, a["_id"], show_collection = False) for a in ver_an }
        an_list = st.multiselect("Anforderung", an_dict.keys(), x["verwendbarkeit_anforderung"], format_func = (lambda a: an_dict[a]), placeholder = "Bitte auswählen")
        cols = st.columns([15] + [15/len(mod_list) for x in mod_list])
        for i, m in enumerate(mod_list):
            with cols[i+1]:
                co1, co2 = st.columns([1,1])
                with co1:
                    st.button('←', key=f'left-m-{m}', on_click = tools.move_up_list, args = (collection, x["_id"], "verwendbarkeit_modul", m,))
                with co2:
                    st.button('→', key=f'right-m-{m}', on_click = tools.move_down_list, args = (collection, x["_id"], "verwendbarkeit_modul", m,))
                st.write(mo_dict[m])
        data = {str(m) : [] for m in mod_list}
        g = pd.DataFrame(data)
        for a in an_list:
            cols = st.columns([1,1,13] + [15/len(mod_list) for x in mod_list])
            with cols[0]:
                st.button('↓', key=f'down-a-{a}', on_click = tools.move_down_list, args = (collection, x["_id"], "verwendbarkeit_anforderung", a,))
            with cols[1]:
                st.button('↑', key=f'up-a-{a}', on_click = tools.move_up_list, args = (collection, x["_id"], "verwendbarkeit_anforderung", a,))
            with cols[2]:
                st.write(an_dict[a])
            for i, m in enumerate(mod_list):
                with cols[i+3]:
                    g.loc[str(a),str(m)] = float(st.checkbox(f"{m}_{a}", True if { "modul": m, "anforderung": a } in x["verwendbarkeit"] else False, key = f"anforderung_{a}_modul_{m}", label_visibility="collapsed"))
        verwendbarkeit = [{"modul": m, "anforderung": a} for m in mod_list for a in an_list if g.loc[str(a),str(m)] == True]
        x_updated = { "verwendbarkeit_modul": mod_list, "verwendbarkeit_anforderung": an_list, "verwendbarkeit": verwendbarkeit }
        ver_updated_all.update(x_updated)

        submit = st.button('Speichern (Verwendbarkeit)', type = 'primary', key = f"verwendbarkeit_{x['_id']}")
        if submit:
            st.session_state.expanded = "verwendbarkeit"
            tools.update_confirm(util.veranstaltung, x, x_updated, False,)

    if save_all:
        sync_termine()
        tools.update_confirm(collection, x, ver_updated_all, reset = False)
        ver_updated_all = dict()
        time.sleep(2)
        switch_page("Veranstaltungen")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
