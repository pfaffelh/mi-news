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
i = 1
date_format = '%d.%m.%Y um %H:%M:%S.'

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

vortragsreihe.drop()
vortrag.drop()

def insert_vortragsreihe(ini):
    leer = {
    "kurzname" : "alle",
    "event" : False, 
    "anzeigetage" : 7, 
    "title_de" : "", 
    "title_en" : "", 
    "text_de" : "", 
    "text_en" : "", 
    "url" : "",
    "ort_de_default" : "",
    "duration_default" : 90,
    "gastgeber_default" : "",
    "sekretariat_default" : "", 
    "ort_en_default" : "",
    "start" : datetime.min,
    "end" : datetime.max,
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
    "   " : {
        "event" : True,
        "kurzname" : "geomod",
        "title_de" : "Geomod Conference in Model Theory",
        "ort_de_default" : "Seminarraum 404",
        "start" : datetime(2023, 11, 14),
        "end" : datetime(2023, 11, 17), 
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

import re
import json

def replace_word_in_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # Ersetzung durchführen
    updated_content = content.replace('Geheim', '"Geheim";')
        
    # Datei überschreiben
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)


def convert_to_json(input_file, output_file):
    # Datei einlesen
    with open(input_file, 'r', encoding='utf-8') as file:
        raw_data = file.read()
    # Regex, um Blöcke von Daten zu parsen
    block_pattern = r'{\s*((?:[\w_]+=".*?";\s*)+)}'
    blocks = re.findall(block_pattern, raw_data)

    # Liste für die extrahierten Datensätze
    data = []

    for block in blocks:
        # Regex, um Schlüssel-Wert-Paare innerhalb eines Blocks zu finden
        key_value_pattern = r'([\w_]+)="(.*?)"'
        key_value_matches = re.findall(key_value_pattern, block)

        # Umwandlung in ein Dictionary
        item = {}
        for key, value in key_value_matches:
            # Escaping von `\q` zu Anführungszeichen
            value = value.replace("\\q", "\"")
            item[key] = value

        data.append(item)

    # JSON-Daten speichern
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Daten erfolgreich in {output_file} gespeichert.")

files = [f"data/{sem}.dat" for sem in get_sem(2006)]
files2 = [f"data/{sem}.dat2" for sem in get_sem(2006)]
json_files = [f"data/{sem}.json" for sem in get_sem(2006)]

for i, file in enumerate(files2):
    replace_word_in_file(files[i], files2[i])
    convert_to_json(files2[i], json_files[i])
    with open(json_files[i], 'r', encoding='utf-8') as file:
        data = json.load(file)
        for d in data:
            if "Zusammenf" in d.keys():
                description = d["Zusammenf"]
                location = d["Ort"]
                summary = d["Titel"]
                sprecher = d["Sprecher"]
                dtstart = datetime.strptime(d["Zeit"] , "%Y-%m-%d %H:%M:%S")
                dtend = dtstart + timedelta(hours=1)
                gastgeber = d.get("Einladender", "")
                sekretariat = "",
                x = vortrag.insert_one({
                    "vortragsreihe" : [id["leer"]], 
                    "gastgeber" : gastgeber,
                    "sekretariat" : "",
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
                    "bearbeitet" : f"Übernommen aus altem Wochenprogramm, {datetime.now().strftime(date_format)}", 
                    "kommentar_de" : "",
                    "kommentar_en" : "",
                    "kommentar_intern" : ""
                })

                if "Geomod" in d.get("Veranst", ""):
                    print("Geomod")
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Geomod"]}})
                elif "Algebra" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Algebra"]}})
                elif "Didakti" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Didaktik"]}})
                elif "Angewand" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Angewandte_Mathematik"]}})
                elif "Datenana" in d.get("Veranst", "") or "FDM" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["FDM"]}})
                elif "Logik" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Mathematische_Logik"]}})
                elif "Differentialgeo" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Differentialgeometrie"]}})
                elif "Geometrische" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Geometrische_Analysis"]}})
                elif "Stochastik" in d.get("Veranst", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Stochastik"]}})
                elif "Kolloquium" in d.get("Type", ""):
                    vortrag.update_one({"_id" : x.inserted_id}, { "$push" : { "vortragsreihe" : id["Kolloquium"]}})
                else:
#                    print(d)
                    print(i)
                    i = i+1

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20241113
mongo_db.command('collMod','vortragsreihe', validator=schema20241113.vortragsreihe_validator, validationLevel='moderate')
mongo_db.command('collMod','vortrag', validator=schema20241113.vortrag_validator, validationLevel='moderate')
