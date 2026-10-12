from pymongo import MongoClient

import schema20261004

# Passt den Validator der Collection 'instapost' an die zweite Art von Posts an
# -- ein Bild aus der bild-Collection, unveraendert gepostet:
#
# 1. 'fit' kennt zusaetzlich den Wert 'auto' (nichts abschneiden).
# 2. 'ratio' ist NICHT mehr required. Bei fit='auto' wird nichts
#    zugeschnitten; das Bild behaelt sein eigenes Seitenverhaeltnis -- ein
#    Format waere dort bedeutungslos. Als Pflichtfeld haette das Schema etwas
#    behauptet, was fuer diese Posts nicht mehr stimmt.
# 3. Schaerfere Beschreibungen: welche Felder zu welchem 'bildtyp' gehoeren.
# 4. Neues Feld 'geplant_fuer' (UTC) und zwei neue 'status'-Werte: 'geplant'
#    (wartet auf seinen Zeitpunkt) und 'wird_gepostet' (ein Lauf von
#    bin/post_geplante.py hat ihn beansprucht). Beide optional -- bestehende
#    Posts bleiben gueltig.
#
# Keine Datenmigration noetig: bestehende Posts haben 'ratio' und ein gueltiges
# 'fit'; weniger required macht sie nicht ungueltig.
#
# Idempotent: laesst sich gefahrlos mehrfach ausfuehren.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

print("Ab hier wird veraendert")

mongo_db.command(
    "collMod", "instapost",
    validator=schema20261004.instapost_validator,
    validationLevel="moderate",
)
print("Validator gesetzt (fit kennt 'auto', ratio nicht mehr required).")

n = mongo_db["instapost"].count_documents({})
print(f"Fertig. {n} Post(s) in der Collection.")
