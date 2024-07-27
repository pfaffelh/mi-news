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

def remove_from_list(collection, id, field, element):
    collection.update_one({"_id": id}, {"$pull": {field: element}})

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")

def new(collection, ini = {}, switch = True):
    z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
    rang = z[0]["rang"]-1
    util.new[collection]["rang"] = rang    
    for key, value in ini.items():
        util.new[collection][key] = value
    util.new[collection].pop("_id", None)
    x = collection.insert_one(util.new[collection])
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} ein neues Item angelegt.")
    if switch:
        switch_page(f"{util.collection_name[collection].lower()} edit")


# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def references(collection, field, list = False):    
    res = {}
    for x in util.abhaengigkeit[collection]:
        res = res | { collection: references(x["collection"], x["field"], x["list"]) } 
    if list:
        z = list(collection.find({field: {"$elemMatch": {"$eq": id}}}))
    else:
        z = list(collection.find({field: id}))
        res = {collection: [t["_id"] for t in z]}
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_items(collection, id):
    res = []
    for x in util.abhaengigkeit[collection]:
        if x["list"]:
            for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                res.append(repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(repr(x["collection"], y["_id"]))
    return res

def delete_item_update_dependent_items(collection, id, switch = True):
    if collection in util.leer.keys() and id == util.leer[collection]:
            st.toast("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        for x in util.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                st.write(util.collection_name[x["collection"]])
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): util.leer[collection]}})             
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")
        time.sleep(4)
        if switch:
            switch_page(util.collection_name[collection].lower())

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
    u = util.user.find_one({"rz": username})
    id = util.group.find_one({"name": app_name})["_id"]
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
    st.sidebar.page_link("pages/06_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

# short Version ohne abhängige Variablen
def repr(collection, id, show_collection = True):
    x = collection.find_one({"_id": id})
    if collection == util.news:        
        title = x['monitor']['title'] if x['monitor']['title']!="" else x["home"]["title_de"]
        title = f"**{title}**"
        ms = x["monitor"]["start"]
        me = x["monitor"]["end"]
        hs = x["home"]["start"]
        he = x["home"]["end"]
        monitordate = f"monitor: {ms.strftime(util.datetime_format)} bis {me.strftime(util.datetime_format)}" if ms < me else "monitor: -"
        homedate = f"home: {hs.strftime(util.datetime_format)} bis {he.strftime(util.datetime_format)}" if hs < he else "home: -"
        res = f"{title}  _{monitordate}; {homedate}_"
        res = f"{title}"
    elif collection == util.carouselnews:
        res = x['text'][0:30]
    elif collection == util.bild:
        res = x['titel']
    if show_collection:
        res = f"{util.collection_name[collection]}: {res}"
    return res

def hour_of_datetime(dt):
    return "" if dt is None else str(dt.hour)

def delete_temporary(except_field = ""):
    """ Delete temporary data except for the given field."""
    if not except_field == "veranstaltung_tmp":
        st.session_state.veranstaltung_tmp.clear()
        st.session_state.translation_tmp = None

def store_image(filename, titel = "", bildnachweis = "", thumbnail_size = (128,128), rang = 0):
    with Image.open(filename) as img:
        print(filename) 
        if img.mode == 'RGBA':
            print("enter RGBA")
            img = img.convert('RGB')
        encoded_image = io.BytesIO()
        img.save(encoded_image, format='JPEG')
        encoded_image = encoded_image.getvalue()
#        encoded_image = base64.b64encode(encoded_image).decode('utf-8') 
        # Thumbnail erstellen
        img.thumbnail(thumbnail_size)
        encoded_thumbnail = io.BytesIO()
        img.save(encoded_thumbnail, format='JPEG')
        encoded_thumbnail = encoded_thumbnail.getvalue()
#        encoded_thumbnail = base64.b64encode(encoded_thumbnail).decode('utf-8')
        newbild = util.bild.insert_one({"filename": filename, "mime": "JPEG", "data": encoded_image, "thumbnail": encoded_thumbnail, "titel": titel, "bildnachweis": bildnachweis, "rang": rang})
        return newbild.inserted_id

def heutenulluhr():
    return datetime.combine(datetime.today(), datetime.min.time())
