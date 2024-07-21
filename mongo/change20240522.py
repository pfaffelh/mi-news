from pymongo import MongoClient
import pymongo
import os
import datetime

# Create mongodump 
os.system(f"mongodump --db vvz --archive=vvz_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}")

# Delete complete database
os.system("mongo vvz --eval 'db.dropDatabase()'")

# Restore complete database
# Should be executed from mi-vvz/mongo/
os.system(f"mongorestore --archive='vvz_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}'")  

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
gebaeude = mongo_db["gebaeude"]
raum = mongo_db["raum"]
cod = mongo_db["code"]
rub = mongo_db["rubrik"]
mod = mongo_db["modul"]
per = mongo_db["person"]
stu = mongo_db["studiengang"]
anf = mongo_db["anforderung"]
anfkat = mongo_db["anforderungkategorie"]
ver = mongo_db["veranstaltung"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240522
mongo_db.command('collMod','veranstaltung', validator=schema20240522.veranstaltung_validator, validationLevel='off')
mongo_db.command('collMod','semester', validator=schema20240522.semester_validator, validationLevel='off')
mongo_db.command('collMod','code', validator=schema20240522.code_validator, validationLevel='off')
#mongo_db.command('collMod','terminart', validator=schema20240522.terminart_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This gives a rang to 1. Vorlesung etc
allrubs = list(rub.find({}).sort({"titel_de": 1}))
i = 0
for r in allrubs:
    i = i+1
    rub.update_one({"_id": r["_id"]}, { "$set": {"rang": i}, "$unset": {"category_id" : ""}})

# Neue Collection terminart
ter = mongo_db["terminart"]
i = 0
for v in list(ver.find()):
    for t in v["woechentlicher_termin"]:        
            x = ter.find_one({'name_de': t["key"]})
            if x:
                ver.update_one({"_id": v["_id"]}, {"$set": {"woechentlicher_termin."+str(v["woechentlicher_termin"].index(t))+".key" : x["_id"]}})
#                logging.debug("Already available: " + x['name_de'])
            else:
                newter =   { "name_de": t["key"],
                             "rang": i,
                             "name_en": "",
                             "hp_sichtbar": True,
                             "komm_sichtbar": True
                }
                i = i+1
                z = ter.insert_one(newter)
                ver.update_one({"_id": v["_id"]}, {"$set": {"woechentlicher_termin."+ str(v["woechentlicher_termin"].index(t))+ ".key" : z.inserted_id}})
    for t in v["einmaliger_termin"]:        
            x = ter.find_one({'name_de': t["key"]})
            if x:
                ver.update_one({"_id": v["_id"]}, {"$set": {"einmaliger_termin."+ str(v["einmaliger_termin"].index(t)) + ".key" : x["_id"]}})
#                logging.debug("Already available: " + x['name_de'])
            else:
                newter =   { "name_de": t["key"],
                             "rang": i,
                             "name_en": "",
                             "hp_sichtbar": True,
                             "komm_sichtbar": True
                }
                i = i+1
                z = ter.insert_one(newter)
                ver.update_one({"_id": v["_id"]}, {"$set": {"einmaliger_termin."+ str(v["einmaliger_termin"].index(t)) + ".key" : z.inserted_id}})

newter =   { "name_de": "-",
                "rang": i,
                "name_en": "-",
                "hp_sichtbar": True,
                "komm_sichtbar": True
}
i = i+1
ter.insert_one(newter)

# Delete hp_sichtbar from code (goes to codekategorie)
cod.update_many({}, {"$unset": {"hp_sichtbar":""}})
codkat = mongo_db["codekategorie"]
for s in sem.find():
    a = codkat.insert_one({"name_de": "Allgemein", "name_en" : "general", "hp_sichtbar" : True, "beschreibung_de": "", "beschreibung_en": "", "rang": 1, "code": [], "kommentar": "", "semester": s["_id"]})
    cod.update_many({"semester": s["_id"]}, {"$set": {"codekategorie": a.inserted_id}})
for c in list(cod.find()):
    codkat.update_one({"semester": c["semester"]}, { "$push": { "code" : c["_id"]}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240522
mongo_db.command("collMod", "anforderung", validator = schema20240522.anforderung_validator, validationLevel='moderate')
mongo_db.command("collMod", "anforderungkategorie", validator = schema20240522.anforderungkategorie_validator, validationLevel='moderate')
mongo_db.command("collMod", "code", validator = schema20240522.code_validator, validationLevel='moderate')
mongo_db.command("collMod", "codekategorie", validator = schema20240522.codekategorie_validator, validationLevel='moderate')
mongo_db.command("collMod", "gebaeude", validator = schema20240522.gebaeude_validator, validationLevel='moderate')
mongo_db.command("collMod", "modul", validator = schema20240522.modul_validator, validationLevel='moderate')
mongo_db.command("collMod", "person", validator = schema20240522.person_validator, validationLevel='moderate')
mongo_db.command("collMod", "raum", validator = schema20240522.raum_validator, validationLevel='moderate')
mongo_db.command("collMod", "rubrik", validator = schema20240522.rubrik_validator, validationLevel='moderate')
mongo_db.command("collMod", "semester", validator = schema20240522.semester_validator, validationLevel='moderate')
mongo_db.command("collMod", "studiengang", validator = schema20240522.studiengang_validator, validationLevel='moderate')
mongo_db.command("collMod", "terminart", validator = schema20240522.terminart_validator, validationLevel='moderate')
mongo_db.command("collMod", "veranstaltung", validator = schema20240522.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
