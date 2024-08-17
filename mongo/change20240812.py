from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

bild = mongo_db["bild"]
news = mongo_db["news"]
carouselnews = mongo_db["carouselnews"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Bilder-Doubletten löschen
dozentenfiles = ["bartels.jpg", "boecherer.jpg", "diehl.jpg", "goette.jpg", "huber.jpg", "kebekus.jpg", "kroener.jpg", "luetkebohmert-holtz.jpg", "pfaffelhuber.jpg", "rohde.jpg", "salimova.jpg", "soergel.jpg", "binder.jpg", "criens.jpg", "dondl.jpg", "grosse.jpg", "junker.jpg", "knies.jpg", "kuwert.jpg", "mildenberger.jpg",  "pizarro.jpg", "ruzicka.jpg", "schmidt.jpg", "wang.jpg"]

# Add fuerhome and fuermonitor
bilder_used = []
ne = list(news.find())
for n in ne:
    if n["image"] != []:
        bilder_used.append(n["image"][0]["_id"])
ne = list(carouselnews.find())
for n in ne:
    bilder_used.append(n["image_id"])
    
ne = list(bild.find())
for n in ne:
    if n not in bilder_used:
        bild.update_one({"_id" : n["_id"]}, { "$set" : {"menu" : False}})
        same_files = list(bild.find({"filename" : n["filename"]}))
        if len(same_files) > 1:
            bild.delete_one({"_id" : n["_id"]})
        else:
            if n["filename"] in dozentenfiles:
                bild.update_one({"_id" : n["_id"]}, { "$set" : {"menu" : True, "bildnachweis" : "Christian Hanner"}})
            
