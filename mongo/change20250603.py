from datetime import datetime, timedelta
# from pytz import UTC # timezone
# import glob, os

import pymongo
from pymongo import MongoClient
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

reihe = mongo_db["vortragsreihe"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

import schema20250603
mongo_db.command('collMod','vortragsreihe', validator=schema20250603.vortragsreihe_validator, validationLevel='off')

# Add fuerhome and fuermonitor
reihe.update_many({}, {"$set" : { "nurintern" : False}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20250603
mongo_db.command('collMod','vortragsreihe', validator=schema20250603.vortragsreihe_validator, validationLevel='moderate')
