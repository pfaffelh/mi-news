from pymongo import MongoClient

# Neue Collection: instapost
#
# Ein Instagram-Post ist ein eigenstaendiges Objekt und keine Erweiterung einer
# News: Bild und Text sind in der Regel andere als auf der Homepage, und die
# Beschreibung (caption) darf deutlich laenger sein.
#
# Zwei Bildquellen:
#   bildtyp "standard" -> CD-Hintergrund der Uni (gelb/blau/weiss) mit Wortmarke,
#                         headline und subline werden in der App daraufgeschrieben.
#   bildtyp "bild"     -> ein Bild aus der bild-Collection, per fit zugeschnitten.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

instapost_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Instagram-Post.",
        "required": ["titel", "bildtyp", "ratio", "caption", "status",
                     "bearbeitet", "kommentar"],
        "properties": {
            "titel": {
                "bsonType": "string",
                "description": "Interner Titel fuer die Uebersicht; nicht Teil des Posts -- required"
            },
            "bildtyp": {
                "enum": ["standard", "bild"],
                "description": "Woher das Bild kommt -- required"
            },
            "variante": {
                "enum": ["gelb", "blau", "weiss", "sand"],
                "description": "CD-Farbvariante, nur bei bildtyp 'standard'"
            },
            "lang": {
                "enum": ["de", "en"],
                "description": "Sprache des Institutsnamens auf dem Standard-Bild"
            },
            "headline": {
                "bsonType": "string",
                "description": "Ueberschrift auf dem Standard-Bild"
            },
            "subline": {
                "bsonType": "string",
                "description": "Unterzeile auf dem Standard-Bild"
            },
            "image_id": {
                "bsonType": ["objectId", "null"],
                "description": "Bild aus der bild-Collection, nur bei bildtyp 'bild'"
            },
            "fit": {
                "enum": ["cover", "contain"],
                "description": "Zuschnitt eines eigenen Bildes"
            },
            "ratio": {
                "enum": ["4:5", "1:1", "1.91:1"],
                "description": "Seitenverhaeltnis des Posts -- required"
            },
            "caption": {
                "bsonType": "string",
                "description": "Beschreibung des Posts, Plain Text, max. 2200 Zeichen -- required"
            },
            "status": {
                "enum": ["entwurf", "veroeffentlicht", "fehler"],
                "description": "Stand der Veroeffentlichung -- required"
            },
            "ig_media_id": {
                "bsonType": "string",
                "description": "Von Instagram zurueckgegebene Media-ID"
            },
            "published_at": {
                "bsonType": ["date", "null"],
                "description": "Wann veroeffentlicht wurde"
            },
            "last_error": {
                "bsonType": "string",
                "description": "Fehlermeldung des letzten Veroeffentlichungsversuchs"
            },
            "rang": {
                "bsonType": "int",
                "description": "Reihenfolge in der Uebersicht"
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Wann und von wem zuletzt bearbeitet -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Interner Kommentar -- required"
            }
        }
    }
}
