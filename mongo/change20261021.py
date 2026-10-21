from pymongo import MongoClient

import schema20261021

# Stellt die Collection 'news' auf das schlanke Format aus schema20261021.py um
# und loescht die Collection 'carouselnews' (die enthielt fast nur noch den
# Mensaplan, den die News-App selbst bei swfr holt).
#
# Pro News:
# - start/end: Hat die News den Tag 'Monitor' und einen Homepage-Tag, wird der
#   Zeitraum vereinigt (frueherer Start, spaeteres Ende). Sonst gilt der
#   Zeitraum der Stelle, an der sie erscheint.
# - title_de/text_de kommen von der Homepage. Sind sie dort leer oder erscheint
#   die News nur auf dem Monitor, kommen sie vom Monitor.
# - title_monitor/text_monitor werden nur gesetzt, wenn die News auf dem
#   Monitor erscheint und dort etwas anderes steht als in title_de/text_de.
# - image behaelt nur noch die _id.
# - Weg: home, monitor, _public, archiv, rang.
#
# Vorher ein Backup machen (mongodump --db news).
#
# Idempotent: bereits umgestellte News (ohne 'home') werden uebersprungen.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]
news = mongo_db["news"]

print("Ab hier wird veraendert")
mongo_db.command("collMod", "news", validator={}, validationLevel="off")

umgestellt = 0
for n in news.find({"home": {"$exists": True}}):
    home, monitor = n["home"], n["monitor"]
    auf_monitor = "Monitor" in n["tags"]
    auf_home = [t for t in n["tags"] if t != "Monitor"] != []

    if auf_monitor and auf_home:
        start = min(home["start"], monitor["start"])
        end = max(home["end"], monitor["end"])
    elif auf_monitor:
        start, end = monitor["start"], monitor["end"]
    else:
        start, end = home["start"], home["end"]

    def gemeinsam(feld):
        if auf_home and home[f"{feld}_de"].strip() != "":
            return home[f"{feld}_de"]
        return monitor[feld]

    title_de = gemeinsam("title")
    text_de = gemeinsam("text")
    title_monitor = monitor["title"] if auf_monitor and monitor["title"].strip() != title_de.strip() else ""
    text_monitor = monitor["text"] if auf_monitor and monitor["text"].strip() != text_de.strip() else ""

    news.update_one({"_id": n["_id"]}, {
        "$set": {
            "start": start,
            "end": end,
            "title_de": title_de,
            "title_en": home["title_en"],
            "text_de": text_de,
            "text_en": home["text_en"],
            "title_monitor": title_monitor,
            "text_monitor": text_monitor,
            "image": [{"_id": i["_id"]} for i in n["image"]],
        },
        "$unset": {"home": "", "monitor": "", "_public": "", "archiv": "", "rang": ""},
    })
    umgestellt += 1
print(f"{umgestellt} News umgestellt.")

if "carouselnews" in mongo_db.list_collection_names():
    mongo_db.drop_collection("carouselnews")
    print("Collection carouselnews geloescht.")

print("Check schema")
mongo_db.command("collMod", "news", validator=schema20261021.news_validator, validationLevel="moderate")
ungueltig = news.count_documents({"$nor": [schema20261021.news_validator]})
print(f"Fertig. {news.count_documents({})} News, davon {ungueltig} nicht schemakonform.")
