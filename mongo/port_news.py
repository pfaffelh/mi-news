import json
from datetime import datetime
from pymongo import MongoClient
import os, io
from PIL import Image
import base64   

bild_no = 1
news_no = 1
carouselnews_no = 1
date_format = '%d.%m.%Y %H:%M'
    
# The is the file from mi-hp
with open('home.json') as f:
    data = json.load(f)    

carouselnews = data["carouselmonitor"]
data["carouselnews"] = []

def store_image(filename, titel = "", bildnachweis = "", thumbnail_size = (128,128), rang = 0, menu = True, kommentar = ""):
    with Image.open(filename) as img:
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
        newbild = bild.insert_one({"filename": filename, "mime": "JPEG", "data": encoded_image, "thumbnail": encoded_thumbnail, "titel": titel, "bildnachweis": bildnachweis, "rang": rang, "menu": menu, "kommentar": kommentar})
        return newbild.inserted_id

for n in carouselnews:
    data["carouselnews"].append(
        {
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
        "archiv": True,      
        "image": [{
            "_id": n["image"],
            "stylehome": n["style"],
            "stylemonitor": n["style"],
            "widthmonitor": 5
        }] if n["image"] != "" else [],
        "home": {
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
        newbild = store_image(f'../../mi-hp{n["image_id"]}', titel = "", bildnachweis = "", rang = bild_no)
        bild_no = bild_no + 1
        n["image_id"] = newbild
    n["rang"] = carouselnews_no
    carouselnews.insert_one(n)
    carouselnews_no = carouselnews_no +1 

for n in data["news"]:
    if n["image"] != []:
        im = bild.find_one({"filename" : n["image"][0]["_id"]})
        if im:
            print(im["_id"])
            n["image"][0]["_id"] = im["_id"]
        else:
            print(n["image"][0]["_id"])
            newbild = store_image(f'../../mi-hp{n["image"][0]["_id"]}', titel = "", bildnachweis = "", rang = bild_no)
            bild_no = bild_no + 1
            n["image"][0]["_id"] = newbild
    n["rang"] = news_no
    news.insert_one(n)
    news_no = news_no +1 

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
    try:
        store_image(filename, rang = bild_no)
        bild_no = bild_no + 1
    except:        
        print("Error with "+ filename)
        pass

print("Check schema")
import schema_init

mongo_db_news.command("collMod", "bild", validator = schema_init.bild_validator, validationLevel='moderate')
mongo_db_news.command("collMod", "carouselnews", validator = schema_init.carouselnews_validator, validationLevel='moderate')
mongo_db_news.command("collMod", "news", validator = schema_init.news_validator, validationLevel='moderate')

