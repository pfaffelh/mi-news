from icalendar import Calendar
from datetime import datetime, timedelta
from pytz import UTC # timezone
import glob, os

import pymongo
from pymongo import MongoClient
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

bild = mongo_db["bild"]
news = mongo_db["news"]
carouselnews = mongo_db["carouselnews"]
vortragsreihe = mongo_db["vortragsreihe"]
vortrag = mongo_db["vortrag"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

vortragsreihe.drop()
vortrag.drop()

def insert_vortragsreihe(ini):
    leer = {
    "kurzname" : "alle",
    "title_de" : "", 
    "title_en" : "", 
    "text_de" : "", 
    "text_en" : "", 
    "url" : "",
    "ort_de_default" : "",
    "duration_default" : 90,
    "ort_en_default" : "",
    "_public" : True, 
    "sichtbar" : True, 
    "_public_default" : False, 
    "sync_with_calendar" : False, 
    "calendar_url" : "", 
    "bearbeitet" : "", 
    "kommentar" : ""
    }
    for key, item in ini.items():
        leer[key] = item
    if list(vortragsreihe.find({})) != []:
        z = list(vortragsreihe.find(sort = [("rang", pymongo.ASCENDING)]))
        leer["rang"] = z[0]["rang"]-1
    else:
        leer["rang"] = 0
    vr = vortragsreihe.insert_one(leer)
    return vr.inserted_id  

def get_sem(start, ende = 2024):
    res = []
    while start <= ende:
        res.append(f"WS{start}-{start+1}")
        res.append(f"SS{start+1}")
        start = start + 1
    return res

data = {
    "Didaktik" : {
        "kurzname" : "Didaktik",
        "title_de" : "Didaktisches Seminar",
        "ort_de_default" : "Hörsaal 2",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
        },
    "Algebra" : {
        "kurzname" : "Algebra",
        "title_de" : "Oberseminar: Algebra, Zahlentheorie und algebraische Geometrie",
        "ort_de_default" : "Seminarraum 404",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
    },
    "Angewandte_Mathematik" : {
        "kurzname" : "AM",
        "title_de" : "Oberseminar: Angewandte Mathematik",
        "ort_de_default" : "Seminarraum 226",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
        },
    "Stochastik" : {
        "kurzname" : "Stochastik",
        "title_de" : "Oberseminar: Stochastik",
        "ort_de_default" : "Seminarraum 232",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
        },
    "Differentialgeometrie" : {
        "kurzname" : "DiffGeo",
        "title_de" : "Oberseminar: Differentialgeometrie",
        "ort_de_default" : "Seminarraum 125",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
        },
    "FDM" : {
        "kurzname" : "FDM",
        "title_de" : "Seminar über Datenanalyse und Modellbildung",
        "ort_de_default" : "Seminarraum 404",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
        },
    "Geometrische_Analysis" : {
        "kurzname" : "GeoAna",
        "title_de" : "Projektseminar Geometrische Analysis",
        "ort_de_default" : "Seminarraum 125",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
    },
    "Mathematische_Logik" : {
        "kurzname" : "Logik",
        "title_de" : "Oberseminar: Mathematische Logik",
        "ort_de_default" : "Seminarraum 404",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
    },
    "Kolloquium" : {
        "kurzname" : "Kolloquium",
        "title_de" : "Mathematisches Kolloquium",
        "ort_de_default" : "Hörsaal 2",
        "sichtbar" : True,
        "_public" : True, 
        "bearbeitet" : "Initialer Eintrag"
    }
}

id = {}
id["leer"] = insert_vortragsreihe({ "kurzname" : "alle"})
for key, item in data.items():
    ini = item
    id[key] = insert_vortragsreihe(item)

ics_files = [f"{sem}.ics" for sem in get_sem(2006)]

for item in ics_files:
    bashCommand = "wget --no-check-certificate -P ics/ " + "http://wochenprogramm.mathematik.uni-freiburg.de/ical/" + item
    print(bashCommand)
    # os.system(bashCommand)

ics_files = glob.glob("ics/*.ics")
for file in ics_files:
    print(file)
    g = open(file,'rb')
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            location = component.get('location')
            description = component.get('description')
            dtstart = component.decoded('dtstart')
            try:
                dtend = component.decoded('dtend')
            except:
                dtend = dtstart + timedelta(hours=1)
            dtstamp = component.decoded('dtstamp')
            sprecher = "" if "Sprecher: " not in description else description.split("Sprecher: ")[-1]
            x = vortrag.insert_one({
                "vortragsreihe" : [id["leer"]], 
                "sprecher" : sprecher,
                "sprecher_en" : "", 
                "sprecher_affiliation_de" : "", 
                "sprecher_affiliation_en" : "", 
                "ort_de" : location, 
                "ort_en" : "", 
                "url" : "", 
                "title_de" : summary, 
                "title_en" : "", 
                "text_de" : description, 
                "text_en" : "", 
                "link" : "", 
                "lang" : "deutsch", 
                "_public" : True, 
                "start" : dtstart,
                "end" : dtend,
                "bearbeitet" : "", 
                "kommentar_de" : "",
                "kommentar_en" : "",
                "kommentar_intern" : ""
            })
            if "Algebra" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Algebra"]}})
            elif "Didakti" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Didaktik"]}})
            elif "Angewand" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Angewandte_Mathematik"]}})
            elif "Kolloquium" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Kolloquium"]}})
            elif "Datenana" in summary or "FDM" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["FDM"]}})
            elif "Logik" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Mathematische_Logik"]}})
            elif "Differentialgeo" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Differentialgeometrie"]}})
            elif "Geometrische" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Geometrische_Analysis"]}})
            elif "Stochastik" in summary:
                vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Stochastik"]}})
            else:
                print(summary)


# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20241113
mongo_db.command('collMod','vortragsreihe', validator=schema20241113.vortragsreihe_validator, validationLevel='moderate')
mongo_db.command('collMod','vortrag', validator=schema20241113.vortrag_validator, validationLevel='moderate')
