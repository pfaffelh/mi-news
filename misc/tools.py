import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *
from datetime import datetime, timedelta 
from PIL import Image
import io

def get_thumbnail(_id):
    b = st.session_state.bild.find_one({"_id": _id})
    try:
        res = Image.open(io.BytesIO(b["thumbnail"]))
    except:
        res = Image.open(io.BytesIO(b["data"]))
    return res

def move_up(collection, x, query = {}):
    query["rang"] = {"$lt": x["rang"]}
    target = collection.find_one(query, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_down(collection, x, query = {}):
    query["rang"] = {"$gt": x["rang"]}
    target = collection.find_one(query, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_alldown(collection, x, query = {}):
    highestrank = max([x["rang"] for x in collection.find()])    
    if highestrank:
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": highestrank+1}})    

def remove_from_list(collection, id, field, element):
    collection.update_one({"_id": id}, {"$pull": {field: element}})

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")

def new(collection, ini = {}, switch = True):
    z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
    rang = z[0]["rang"]-1
    st.session_state.new[collection]["rang"] = rang    
    for key, value in ini.items():
        st.session_state.new[collection][key] = value
    st.session_state.new[collection].pop("_id", None)
    x = collection.insert_one(st.session_state.new[collection])
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} ein neues Item angelegt.")
    if switch:
        switch_page(f"{st.session_state.collection_name[collection].lower()} edit")


# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def references(collection, field, list = False):    
    res = {}
    for x in st.session_state.abhaengigkeit[collection]:
        res = res | { collection: references(x["collection"], x["field"], x["list"]) } 
    if list:
        z = list(collection.find({field: {"$elemMatch": {"$eq": id}}}))
    else:
        z = list(collection.find({field: id}))
        res = {collection: [t["_id"] for t in z]}
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_items(collection, id, ini = {}):
    res = []
    for x in st.session_state.abhaengigkeit[collection]:
        if x["list"]:
            ini[x["field"]] = { "$elemMatch": { "$eq": id }}
            for y in list(x["collection"].find(ini)):
                res.append(repr(x["collection"], y["_id"]))
        else:
            ini[x["field"]] = id
            for y in list(x["collection"].find(ini)):
                res.append(repr(x["collection"], y["_id"]))
    return res

def delete_item_update_dependent_items(collection, id, switch = True):
    if collection in st.session_state.leer.keys() and id == st.session_state.leer[collection]:
            st.toast("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        for x in st.session_state.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                st.write(st.session_state.collection_name[x["collection"]])
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): st.session_state.leer[collection]}})             
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")
        time.sleep(4)
        if switch:
            switch_page(st.session_state.collection_name[collection].lower())

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2.0)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        util.logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = st.session_state.users.find_one({"rz": username})
    id = st.session_state.group.find_one({"name": app_name})["_id"]
    return (True if id in u["groups"] else False)

def logout():
    st.session_state.logged_in = False
    util.logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

def reset_vars(text=""):
    st.session_state.edit = ""
    if text != "":
        st.success(text)

def display_navigation():
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    st.sidebar.image("static/ufr.png", use_column_width=True)
    st.session_state.tage = st.sidebar.slider("Welche News sollen angezeigt werden?", 0, 500, 25)
    st.sidebar.write("Nur News der letzten ", st.session_state.tage, "Tage werden angezeigt.")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/00_New.py", label="News")
    st.sidebar.page_link("pages/02_Carouselnews.py", label="Carouselnews")
    st.sidebar.page_link("pages/04_Bild.py", label="Bilder")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/06_Wochenprogramm.py", label="Wochenprogramm")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/08_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

# short Version ohne abhängige Variablen
def repr(collection, id, short = False, show_collection = True):
    x = collection.find_one({"_id": id})
    if collection == st.session_state.news:        
        title = x['monitor']['title'] if x['monitor']['title']!="" else x["home"]["title_de"]
        title = f"**{title.strip()}**"
        ms = x["monitor"]["start"]
        me = x["monitor"]["end"]
        hs = x["home"]["start"]
        he = x["home"]["end"]
        monitordate = f"monitor: {ms.strftime(util.datetime_format)} bis {me.strftime(util.datetime_format)}" if ms < me else "monitor: -"
        homedate = f"home: {hs.strftime(util.datetime_format)} bis {he.strftime(util.datetime_format)}" if hs < he else "home: -"
        res = f"{title}  _{monitordate}; {homedate}_"
        res = f"{title}"
    elif collection == st.session_state.carouselnews:
        res = x['text'][0:50]
    elif collection == st.session_state.bild:
        res = x['titel']
    elif collection == st.session_state.vortragsreihe:
        res = x['kurzname'] if short else x['title_de'] 
    elif collection == st.session_state.vortrag:
        res = f"{x['start'].strftime('%d.%m.%Y')}: "
        res = res + f"{x['sprecher']}, {x['title_de']}"
        vre = ", ".join([repr(st.session_state.vortragsreihe, y, True, False) for y in x['vortragsreihe']])
        res = (res + f" ({vre})").replace("\n", "")
    if show_collection:
        res = f"{st.session_state.collection_name[collection]}: {res}"
    return res

def hour_of_datetime(dt):
    return "" if dt is None else str(dt.hour)

def delete_temporary(except_field = ""):
    """ Delete temporary data except for the given field."""
    if not except_field == "veranstaltung_tmp":
        st.session_state.veranstaltung_tmp.clear()

def heutenulluhr():
    return datetime.combine(datetime.today(), datetime.min.time())

def changeimagefun(collection, x, x_updated):
    st.session_state.changeimage = False
    st.session_state.expanded = "bild"
    update_confirm(collection, x, x_updated, False)
