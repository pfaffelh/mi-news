from pymongo import MongoClient

import schema20261021b

# Raum, Sprecher und Affiliation gibt es nur noch einmal statt je Sprache
# (siehe schema20261021b.py).
#
# Uebernommen wird der Wert in der Sprache des Vortrags (bzw. der
# Standardsprache der Reihe), denn nur der war im Editor sichtbar. Ist er leer,
# der Wert der anderen Sprache.
#
# Vorher ein Backup machen (mongodump --db news).
#
# Idempotent: bereits umgestellte Dokumente (ohne ort_de bzw. ort_de_default)
# werden uebersprungen.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]
vortrag = mongo_db["vortrag"]
vortragsreihe = mongo_db["vortragsreihe"]


def wert(x, feld, lang, suffix=""):
    andere = "en" if lang == "de" else "de"
    eigen = (x.get(f"{feld}_{lang}{suffix}") or "").strip()
    return eigen if eigen else (x.get(f"{feld}_{andere}{suffix}") or "").strip()


print("Ab hier wird veraendert")
mongo_db.command("collMod", "vortrag", validator={}, validationLevel="off")
mongo_db.command("collMod", "vortragsreihe", validator={}, validationLevel="off")

geaendert = 0
for v in vortrag.find({"ort_de": {"$exists": True}}):
    vortrag.update_one({"_id": v["_id"]}, {
        "$set": {
            "sprecher": wert(v, "sprecher", v["lang"]),
            "sprecher_affiliation": wert(v, "sprecher_affiliation", v["lang"]),
            "ort": wert(v, "ort", v["lang"]),
        },
        "$unset": {k: "" for k in ["sprecher_de", "sprecher_en", "sprecher_affiliation_de",
                                   "sprecher_affiliation_en", "ort_de", "ort_en"]},
    })
    geaendert += 1
print(f"{geaendert} Vortraege umgestellt.")

geaendert = 0
for r in vortragsreihe.find({"ort_de_default": {"$exists": True}}):
    vortragsreihe.update_one({"_id": r["_id"]}, {
        "$set": {"ort_default": wert(r, "ort", r["lang_default"], "_default")},
        "$unset": {"ort_de_default": "", "ort_en_default": ""},
    })
    geaendert += 1
print(f"{geaendert} Vortragsreihen umgestellt.")

print("Check schema")
for name, validator in [("vortrag", schema20261021b.vortrag_validator),
                        ("vortragsreihe", schema20261021b.vortragsreihe_validator)]:
    mongo_db.command("collMod", name, validator=validator, validationLevel="moderate")
    ungueltig = mongo_db[name].count_documents({"$nor": [validator]})
    print(f"{name}: {mongo_db[name].count_documents({})} Dokumente, davon {ungueltig} nicht schemakonform.")
