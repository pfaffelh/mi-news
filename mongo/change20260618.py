from datetime import datetime, timedelta
# from pytz import UTC # timezone
# import glob, os

import pymongo
from pymongo import MongoClient
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

news = mongo_db["news"]
bild = mongo_db["bild"]

# Entfernt verwaiste Bild-Referenzen aus news.image.
# Hintergrund: news.image ist eine Liste von Dicts ({"_id": ObjectId, ...}).
# Beim Loeschen eines Bildes wurden diese Eintraege bisher nicht aufgeraeumt,
# sodass News auf nicht mehr existierende Bilder zeigten -> die App crashte
# beim Rendern (None["thumbnail"]).

# Ab hier wird die Datenbank veraendert
print("Ab hier wird veraendert")

# Menge aller tatsaechlich existierenden Bild-IDs.
existing = set(b["_id"] for b in bild.find({}, {"_id": 1}))
print(f"{len(existing)} Bilder in der Datenbank.")

geaendert = 0
for n in news.find({"image": {"$ne": []}}):
    dangling = [img for img in n.get("image", [])
                if isinstance(img, dict) and img.get("_id") not in existing]
    for img in dangling:
        title = n.get("monitor", {}).get("title") or n.get("home", {}).get("title_de")
        print(f"Entferne verwaiste Referenz {img['_id']} aus News {n['_id']} ({title!r}).")
        # Genau dieses Dict aus dem Array ziehen.
        news.update_one({"_id": n["_id"]}, {"$pull": {"image": {"_id": img["_id"]}}})
        geaendert += 1

print(f"Fertig. {geaendert} verwaiste Referenz(en) entfernt.")
