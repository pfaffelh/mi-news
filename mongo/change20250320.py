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

import schema20250320
mongo_db.command('collMod','news', validator=schema20250320.news_validator, validationLevel='off')

# Add fuerhome and fuermonitor
ne = list(news.find())
for n in ne:
    mo = n["monitor"]["fuermonitor"]
    ho = n["home"]["fuerhome"]
    tag = ["Institut"]
    if mo:
        tag.append("Monitor")
    if ho:
        tag.append("Lehre")
    news.update_one({"_id" : n["_id"]}, { "$set" : {"tags" : tag}, "$unset" : {"monitor.fuermonitor" : False, "home.fuerhome" : False}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20250320
mongo_db.command('collMod','news', validator=schema20250320.news_validator, validationLevel='moderate')
