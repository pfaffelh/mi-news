from pymongo import MongoClient

import schema20260714

# Legt die Collection 'instapost' an und haengt den Validator daran.
#
# Instagram-Posts sind eigenstaendige Objekte, keine Erweiterung der News --
# deshalb eine eigene Collection und kein neues Feld am news-Dokument.
#
# Idempotent: laesst sich gefahrlos mehrfach ausfuehren.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

print("Ab hier wird veraendert")

if "instapost" not in mongo_db.list_collection_names():
    mongo_db.create_collection("instapost")
    print("Collection 'instapost' angelegt.")
else:
    print("Collection 'instapost' existiert bereits.")

mongo_db.command(
    "collMod", "instapost",
    validator=schema20260714.instapost_validator,
    validationLevel="moderate",
)
print("Validator gesetzt.")

print(f"Fertig. {mongo_db['instapost'].count_documents({})} Post(s) in der Collection.")
