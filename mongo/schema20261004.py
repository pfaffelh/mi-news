from pymongo import MongoClient

# Schema der Collection instapost -- Stand 14.09.2026.
#
# Gegenueber schema20260714.py neu: das Feld 'permalink'. Aus der Media-ID
# allein kommt man nicht zum Beitrag; den Kurzcode der oeffentlichen URL gibt
# Meta nur auf Nachfrage heraus. Er wird deshalb beim Posten mitgespeichert,
# damit die App direkt auf den Beitrag verlinken kann.
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
        "required": ["titel", "bildtyp", "caption", "status",
                     "bearbeitet", "kommentar"],
        "properties": {
            "titel": {
                "bsonType": "string",
                "description": "Interner Titel fuer die Uebersicht; nicht Teil des Posts -- required"
            },
            "bildtyp": {
                "enum": ["standard", "bild"],
                "description": "Woher das Bild kommt -- required. 'standard': aus Text "
                               "erzeugtes CD-Bild (variante, lang, headline, subline, "
                               "ratio). 'bild': ein Bild aus der bild-Collection "
                               "(image_id, fit, bei fit != 'original' auch ratio)."
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
                "description": "Bild aus der bild-Collection, nur bei bildtyp 'bild'. "
                               "null, solange keines gewaehlt ist."
            },
            "fit": {
                "enum": ["cover", "contain", "auto"],
                "description": "Wie ein eigenes Bild in ein Instagram-Format gebracht "
                               "wird. 'auto': nichts abschneiden -- das Bild behaelt "
                               "seine Groesse und bekommt nur dann Rand, wenn sein "
                               "Seitenverhaeltnis ausserhalb 4:5 .. 1.91:1 liegt. "
                               "'cover': formatfuellend auf 'ratio', schneidet ab. "
                               "'contain': vollstaendig sichtbar in 'ratio', mit Rand."
            },
            "ratio": {
                "enum": ["4:5", "1:1", "1.91:1"],
                "description": "Format, auf das zugeschnitten bzw. aufgefuellt wird. "
                               "Gilt NICHT fuer fit='auto' -- dort behaelt das Bild sein "
                               "eigenes Seitenverhaeltnis, und ein hier gespeicherter "
                               "Wert ist bedeutungslos. Deshalb nicht mehr required."
            },
            "caption": {
                "bsonType": "string",
                "description": "Beschreibung des Posts, Plain Text, max. 2200 Zeichen -- required"
            },
            "status": {
                "enum": ["entwurf", "geplant", "wird_gepostet",
                         "veroeffentlicht", "fehler"],
                "description": "Stand der Veroeffentlichung -- required. 'geplant': "
                               "wartet auf 'geplant_fuer'. 'wird_gepostet': ein Lauf "
                               "von bin/post_geplante.py hat den Post beansprucht und "
                               "ist gerade dabei -- bleibt er so stehen, ist der Lauf "
                               "abgebrochen und ein Mensch muss nachsehen."
            },
            "geplant_fuer": {
                "bsonType": ["date", "null"],
                "description": "Wann der Post rausgehen soll, in UTC. Nur bei "
                               "status 'geplant' bzw. 'wird_gepostet' gesetzt."
            },
            "ig_media_id": {
                "bsonType": "string",
                "description": "Von Instagram zurueckgegebene Media-ID"
            },
            "permalink": {
                "bsonType": "string",
                "description": "Oeffentliche URL des Beitrags (instagram.com/p/<code>/)"
            },
            "published_at": {
                "bsonType": ["date", "null"],
                "description": "Wann veroeffentlicht wurde, in UTC"
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
