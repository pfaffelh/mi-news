from pymongo import MongoClient

import schema20260914

# Haengt den erweiterten Validator an die Collection 'instapost': neu ist das
# Feld 'permalink' (oeffentliche URL des Beitrags).
#
# Warum ueberhaupt noetig: Der Validator listet die erlaubten Felder samt Typ.
# Ohne diesen Lauf wuerde 'permalink' zwar durchgehen (JSON-Schema erlaubt
# zusaetzliche Felder, solange additionalProperties nicht verboten ist), aber
# ungeprueft -- und die Schema-Datei waere nicht mehr die Wahrheit ueber die
# Collection.
#
# Idempotent: laesst sich gefahrlos mehrfach ausfuehren.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

print("Ab hier wird veraendert")

mongo_db.command(
    "collMod", "instapost",
    validator=schema20260914.instapost_validator,
    validationLevel="moderate",
)
print("Validator gesetzt (mit 'permalink').")

n = mongo_db["instapost"].count_documents({})
ohne = mongo_db["instapost"].count_documents({"permalink": {"$exists": False}})
print(f"Fertig. {n} Post(s), davon {ohne} ohne permalink-Feld.")
print("Das ist in Ordnung: Das Feld wird beim naechsten Veroeffentlichen gesetzt;")
print("die App faellt ohne es auf den Profil-Link zurueck.")
