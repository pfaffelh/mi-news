from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

bild = mongo_db["bild"]
news = mongo_db["news"]
carouselnews = mongo_db["carouselnews"]

import schema20240805
mongo_db.command('collMod','bild', validator=schema20240805.bild_validator, validationLevel='off')
mongo_db.command('collMod','news', validator=schema20240805.news_validator, validationLevel='off')
mongo_db.command('collMod','carouselnews', validator=schema20240805.carouselnews_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Add fuerhome and fuermonitor
ne = list(news.find())
for n in ne:
    news.update_one({"_id" : n["_id"]}, { "$set" : {"monitor.fuermonitor" : True, "home.fuerhome" : True} })

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240805
mongo_db.command('collMod','bild', validator=schema20240805.bild_validator, validationLevel='moderate')
mongo_db.command('collMod','news', validator=schema20240805.news_validator, validationLevel='moderate')
mongo_db.command('collMod','carouselnews', validator=schema20240805.carouselnews_validator, validationLevel='moderate')


