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

def store_image(filename, titel = "", bildnachweis = "", thumbnail_size = (128,128), quality = 100, rang = 0, menu = True, kommentar = ""):
    with Image.open(filename) as img:
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        encoded_image = io.BytesIO()
        img.save(encoded_image, optimize=True, quality=quality, format='JPEG')
#        img.save(encoded_image, format='JPEG')
        encoded_image = encoded_image.getvalue()
    #        encoded_image = base64.b64encode(encoded_image).decode('utf-8') 
        # Thumbnail erstellen
        img.thumbnail(thumbnail_size)
        encoded_thumbnail = io.BytesIO()
        img.save(encoded_thumbnail, format='JPEG')
        encoded_thumbnail = encoded_thumbnail.getvalue()
    #        encoded_thumbnail = base64.b64encode(encoded_thumbnail).decode('utf-8')
        filename_store = filename.split("/")[-1]
        newbild = bild.insert_one({"filename": filename_store, "mime": "JPEG", "data": encoded_image, "thumbnail": encoded_thumbnail, "titel": titel, "bildnachweis": bildnachweis, "rang": rang, "menu": menu, "kommentar": kommentar, "bearbeitet": "Zuletzt bearbeitet von Markus Junker"})
    return newbild.inserted_id

# os.system("mongo news --eval 'db.dropDatabase()'")

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

path = ["/home/pfaffelh/Downloads/intern/bilder/junker/"]
image_list = []
for p in path:
    for file in os.listdir(p):
        try:
            mime = file.split(".")[1].lower()
            if mime in ["jpg", "jpeg", "png"]:
                image_list.append(p + file)
        except:
            pass
print("Image List")
print(image_list)

bild_no = 300
for filename in image_list:
    titel = filename.split(".")[0]
    mime = filename.split(".")[1].lower()
    try:
        store_image(filename, titel = "", bildnachweis = "Markus Junker", quality = 5, rang = bild_no)
        bild_no = bild_no + 1
        print("Stored file " + filename)
    except:
        print("Error with "+ filename)
        pass

bild.create_index("rang")

