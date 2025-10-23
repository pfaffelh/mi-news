from datetime import datetime, timedelta
# from pytz import UTC # timezone
# import glob, os

import pymongo
from pymongo import MongoClient
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

news = mongo_db["news"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

import schema20251023
mongo_db.command('collMod','news', validator=schema20251023.news_validator, validationLevel='off')

# Add fuerhome and fuermonitor


# Add fuerhome and fuermonitor
ne = list(news.find())
for n in ne:
    news.update_one({"_id" : n["_id"]}, { "$set" : {"highlight" : False}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20251023
mongo_db.command('collMod','news', validator=schema20251023.news_validator, validationLevel='moderate')
