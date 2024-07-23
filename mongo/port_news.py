import json
from datetime import datetime
from pymongo import MongoClient
import os
import bson.binary

date_format = '%d.%m.%Y %H:%M'

# The is the file from mi-hp
with open('home.json') as f:
    data = json.load(f)    

carouselnews = data["carouselmonitor"]
data["carouselnews"] = []

for n in carouselnews:
    data["carouselnews"].append(
        {
            "test": True,
            "_public": True, 
            "start": datetime.strptime(n["showstart"], date_format),
            "end": datetime.strptime(n["showend"], date_format),
            "interval": int(n["interval"]),
            "image_id": n["image"],
            "left": int(n["left"].split("%")[0]),
            "right": int(n["right"].split("%")[0]),
            "bottom": int(n["bottom"].split("%")[0]),
            "text": n["text"]
        }
    )


news = data["news"]
data["news"] = []

for n in news:
    # print(n)
    data["news"].append(
        {
        "link": n["link"],
        "_public": True,
        "showlastday": True,
        
        "image": [{
            "_id": n["image"],
            "stylehome": n["style"],
            "stylemonitor": n["style"],
            "widthmonitor": 5
        }] if n["image"] != "" else [],
        "home": {
            "test": True, 
            "_public": True,
            "archiv": True,
            "start": datetime.strptime(n["showhomestart"], date_format),
            "end": datetime.strptime(n["showhomeend"], date_format),
            "title_de": n["title_de"],
            "title_en": n["title_en"],
            "text_de": n["text_de"],
            "text_en": n["text_en"],
            "popover_title_de": n["popover_title_de"],
            "popover_title_en": n["popover_title_en"],
            "popover_text_de": n["popover_text_de"],
            "popover_text_en": n["popover_text_en"],
        },
        "monitor": {
            "test": True, 
            "_public": True,
            "showlastday": True,
            "start": datetime.strptime(n["showmonitorstart"], date_format),
            "end": datetime.strptime(n["showmonitorend"], date_format),
            "title": n["title_de"],
            "text": n["text_de"]
        }
    })

#with open('home2.json', 'w') as f:
#    json.dump(data, f, ensure_ascii=False)    


# Now we write data in the mongodb

os.system("mongo news --eval 'db.dropDatabase()'")

# Write to database:
# Collections are: 
# Mensaplan
# Images: File, Titel, Bildnachweis, 
# Carouselnews: test, _public, showstart, showend, interval, image, left (in %), right (in %), bottom (in %), text
# News: wie oben

try:
    cluster = MongoClient("mongodb://127.0.0.1:27017")
    mongo_db_news = cluster["news"]
    mensaplan = mongo_db_news["mensaplan"]
    bild = mongo_db_news["bild"]
    carouselnews = mongo_db_news["carouselnews"]
    news = mongo_db_news["news"]
    
except:
    pass
    # logger.warning("No connection to Database 1")

for n in data["carouselnews"]:
    im = bild.find_one({"filename" : n["image_id"]})
    if im:
        print(im["_id"])
        n["image_id"] = im["_id"]
    else:
        print(n["image_id"])
        with open(f'../../mi-hp{n["image_id"]}', 'rb') as image_file:
            encoded_image = bson.binary.Binary(image_file.read())
            newbild = bild.insert_one({"filename": n["image_id"], "mime": n["image_id"].split(".")[1].lower(), "data": encoded_image, "titel": "", "bildnachweis": ""})

        n["image_id"] = newbild.inserted_id
        
    carouselnews.insert_one(n)

for n in data["news"]:
    if n["image"] != []:
        im = bild.find_one({"filename" : n["image"][0]["_id"]})
        if im:
            print(im["_id"])
            n["image"][0]["_id"] = im["_id"]
        else:
            print(n["image"][0]["_id"])
            with open(f'../../mi-hp{n["image"][0]["_id"]}', 'rb') as image_file:
                encoded_image = bson.binary.Binary(image_file.read())
                newbild = bild.insert_one({"filename": n["image"][0]["_id"], "mime": n["image"][0]["_id"].split(".")[1].lower(), "data": encoded_image, "titel": "", "bildnachweis": ""})
            n["image"][0]["_id"] = newbild.inserted_id
    news.insert_one(n)


image_list = ['white.jpg']

path = ["../../mi-hp/static/images/", "../../mi-hp/static/images/Dozenten/"]
for p in path:
    for file in os.listdir(p):
        try:
            mime = file.split(".")[1]
            if mime in ["jpg", "jpeg", "png"]:
                image_list.append(p + file)
        except:
            pass

for filename in image_list:
    titel = filename.split(".")[0]
    mime = filename.split(".")[1].lower()
    with open(filename, 'rb') as image_file:
        encoded_image = bson.binary.Binary(image_file.read())
        print(filename)
        bild.insert_one({"filename": filename, "mime": mime, "data": encoded_image, "titel": titel, "bildnachweis": ""})

print("Check schema")
import schema_init

mongo_db_news.command("collMod", "bild", validator = schema_init.bild_validator, validationLevel='moderate')
mongo_db_news.command("collMod", "carouselnews", validator = schema_init.carouselnews_validator, validationLevel='moderate')
mongo_db_news.command("collMod", "news", validator = schema_init.news_validator, validationLevel='moderate')

