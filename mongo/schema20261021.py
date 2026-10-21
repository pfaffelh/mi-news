from pymongo import MongoClient

# Schema der Collection news -- Stand 21.10.2026.
#
# Gegenueber schema20251023.py ist die News deutlich schlanker:
#
# - Ein gemeinsamer Zeitraum (start, end) fuer Monitor und Homepage statt
#   home.start/end und monitor.start/end.
# - Ein gemeinsamer Text: title_de/text_de, dazu title_en/text_en fuer die
#   englische Homepage. title_monitor/text_monitor sind nur gesetzt, wenn der
#   Monitor etwas anderes zeigen soll; leer heisst: der Monitor zeigt
#   title_de/text_de.
# - Entfallen: _public (alles ist sofort veroeffentlicht), archiv (alles kommt
#   ins Archiv), rang (sortiert wird nach start), die vier Popover-Felder und
#   die Bild-Einstellungen stylehome, stylemonitor, widthmonitor (die gab es
#   nur fuer den alten HTML-Monitor).
#
# Die Tags entscheiden weiterhin, wo die News erscheint.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

news_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Nachricht.",
        "required": ["tags", "link", "showlastday", "highlight", "image", "start", "end",
                     "title_de", "title_en", "text_de", "text_en", "title_monitor", "text_monitor",
                     "bearbeitet", "kommentar"],
        "properties": {
            "tags": {
                "bsonType": "array",
                "uniqueItems": True,
                "items": {
                    "enum": ["Monitor", "Lehre", "Institut"]
                },
                "description": "Wo die News erscheint -- required"
            },
            "link": {
                "bsonType": "string",
                "description": "Gibt einen Link für diese News an (oder '') -- required"
            },
            "showlastday": {
                "bsonType": "bool",
                "description": "Gibt an, ob der letzte Tag speziell markiert werden soll. -- required"
            },
            "highlight": {
                "bsonType": "bool",
                "description": "Gibt an, ob die News hervorgehoben werden soll. -- required"
            },
            "image": {
                "bsonType": "array",
                "description": "Das (wenn vorhanden) Bild für die News -- required. Das Array hat Länge 0 oder 1",
                "items": {
                    "bsonType": "object",
                    "description": "Details eines Bildes",
                    "required": ["_id"],
                    "properties": {
                        "_id": {
                            "bsonType": "objectId",
                            "description": "Die id des Bildes -- required"
                        }
                    }
                }
            },
            "start": {
                "bsonType": "date",
                "description": "Ab hier wird die News angezeigt, auf Monitor und Homepage -- required"
            },
            "end": {
                "bsonType": "date",
                "description": "Bis hier wird die News angezeigt, auf Monitor und Homepage -- required"
            },
            "title_de": {
                "bsonType": "string",
                "description": "Titel (de), auch auf dem Monitor, wenn title_monitor leer ist -- required"
            },
            "title_en": {
                "bsonType": "string",
                "description": "Titel (en) für die Homepage; leer heißt: deutscher Titel -- required"
            },
            "text_de": {
                "bsonType": "string",
                "description": "Text (de), auch auf dem Monitor, wenn text_monitor leer ist -- required"
            },
            "text_en": {
                "bsonType": "string",
                "description": "Text (en) für die Homepage; leer heißt: deutscher Text -- required"
            },
            "title_monitor": {
                "bsonType": "string",
                "description": "Abweichender Titel für den Monitor (oder '') -- required"
            },
            "text_monitor": {
                "bsonType": "string",
                "description": "Abweichender Text für den Monitor (oder '') -- required"
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem die News zuletzt bearbeitet wurde -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Ein Kommentar -- required"
            }
        }
    }
}
