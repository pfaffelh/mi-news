from pymongo import MongoClient

# Write to database:
# Collections are: 
# mensaplan
# bild: File, Titel, Bildnachweis, 
# carouselnews: test, _public, showstart, showend, interval, image, left (in %), right (in %), bottom (in %), text
# news: link, image (object), home (object), monitor (object)


# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

mensaplan_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Mensaessen eines Tages.",
        "required": ["date", "text"],
        "properties": {
            "date": {
                "bsonType": "date",
                "description": "Datum, für das das Essen beschrieben wird. -- required"
            },
            "text": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "description": "eine Textzeile."
                }
            },
        }
    }
}

bild_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Bild.",
        "required": ["filename", "menu", "mime", "data", "thumbnail", "titel", "kommentar", "bildnachweis", "rang"],
        "properties": {
            "filename": {
                "bsonType": "string",
                "description": "Filename of the image -- required"
            },
            "menu": {
                "bsonType": "bool",
                "description": "In Auswahlmenüs sichtbar? -- required"
            },
            "mime": {
                "bsonType": "string",
                "description": "jpg, jpeg, png etc -- required"
            },
            "data": {
                "bsonType": "binData", 
                "description": "Das File, wie es in der Datenbank abgespeichert wird -- required"
            },
            "thumbnail": {
                "bsonType": "binData", 
                "description": "Thumbnail des Bildes -- required"
            },
            "titel": {
                "bsonType": "string",
                "description": "Ein Titel für das Bild -- required"
            },
            "bildnachweis": {
                "bsonType": "string",
                "description": "Der Bildnachweis -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Ein Kommentar -- required"
            },
            "rang": {
                "bsonType": "int",
                "description": "...um alles in eine Reihenfolge zu bringen -- required"
            }
        }
    }
}

carouselnews_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Nachricht für das Carousel.",
        "required": ["_public", "start", "end", "interval", "image_id", "left", "right", "bottom", "text", "rang"],
        "properties": {
            "_public": {
                "bsonType": "bool",
                "description": "Gibt an, ob die News auf monitor erscheint -- required"
            },
            "start": {
                "bsonType": "date",
                "description": "Das Startdatum, zu dem die News angezeigt werden soll -- required"
            },
            "end": {
                "bsonType": "date",
                "description": "Das Enddatum, zu dem die News angezeigt werden soll -- required"
            },
            "interval": {
                "bsonType": "int",
                "description": "Die Dauer wie lange die News angezeigt wird in Milisekunden -- required"
            },
            "image_id": {
                "bsonType": "objectId",
                "description": "Das Hintergrundbild -- required"
            },
            "left": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 100,
                "description": "Entfernung der Box vom linken Rand (in %) -- required"
            },
            "right": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 100,
                "description": "Entfernung der Box vom rechten Rand (in %) -- required"
            },
            "bottom": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 100,
                "description": "Entfernung der Box vom unteren Rand (in %) -- required"
            },
            "text": {
                "bsonType": "string",
                "description": "Text im Bild -- required"
            },
            "rang": {
                "bsonType": "int",
                "description": "...um alles in eine Reihenfolge zu bringen -- required"
            }
        }
    }
}

news_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Nachricht.",
        "required": ["link", "_public", "archiv", "showlastday", "image", "home", "monitor", "rang"],
        "properties": {
            "link": {
                "bsonType": "string",
                "description": "Gibt einen Link für diese News an (oder '') -- required"
            },
            "_public": {
                "bsonType": "bool",
                "description": "Gibt an, ob die News auf home zu sehen ist.  -- required"
            },
            "archiv": {
                "bsonType": "bool",
                "description": "Gibt an, ob die News nach end ins Archiv auf home übernommen wird.  -- required"
            },
            "showlastday": {
                "bsonType": "bool",
                "description": "Gibt an, ob der letzte Tag speziell markiert werden soll. -- required"
            },
            "image": {
                "bsonType": "array",
                "description": "Das (wenn vorhanden) Bild für die News -- required. Das Array hat Länge 0 oder 1",
                "items": {
                    "bsonType": "object",
                    "description": "Details eines Bildes",
                    "required": ["_id", "stylehome", "stylemonitor", "widthmonitor"],
                    "properties": {
                        "_id": {
                            "bsonType": "objectId",
                            "description": "Die id des Bildes -- required"
                        },
                        "stylehome": {
                            "bsonType": "string",
                            "description": "css-Styles für das Bild auf home -- required"
                        },
                        "stylemonitor": {
                            "bsonType": "string",
                            "description": "css-Styles für das Bild auf monitor -- required"
                        },
                        "widthmonitor": {
                            "bsonType": "int",
                            "minimum": 0, 
                            "maximum": 12,
                            "description": "Breite im bootstrap-grid für das Bild auf monitor -- required"
                        },                   
                    },
                },
            },
            "home": {
                "bsonType": "object",
                "description": "Details für home",
                "required": ["fuerhome", "start", "end", "title_de", "title_en", "text_de", "text_en", "popover_title_de", "popover_title_en", "popover_text_de", "popover_text_en"],
                "properties": {
                    "fuerhome": {
                        "bsonType": "bool",
                        "description": "gibt an, ob die News auf home erscheinen soll -- required"
                    },
                    "start": {
                        "bsonType": "date",
                        "description": "Startdatum für die News auf home -- required"
                    },
                    "end": {
                        "bsonType": "date",
                        "description": "Enddatum für die News auf home -- required"
                    },
                    "title_de": {
                        "bsonType": "string",
                        "description": "Titel der News auf home (de) -- required"
                    },                   
                    "title_en": {
                        "bsonType": "string",
                        "description": "Titel der News auf home (en) -- required"
                    },                   
                    "text_de": {
                        "bsonType": "string",
                        "description": "Text der News auf home (de) -- required"
                    },                   
                    "text_en": {
                        "bsonType": "string",
                        "description": "Text der News auf home (en) -- required"
                    },                   
                    "popover_title_de": {
                        "bsonType": "string",
                        "description": "Titel des Popovers der News auf home (de) -- required"
                    },                   
                    "popover_title_en": {
                        "bsonType": "string",
                        "description": "Titel des Popovers der News auf home (en) -- required"
                    },                   
                    "popover_text_de": {
                        "bsonType": "string",
                        "description": "Text des Popovers der News auf home (de) -- required"
                    },                   
                    "popover_text_en": {
                        "bsonType": "string",
                        "description": "Text des Popovers der News auf home (en) -- required"
                    },                   
                },
            },
            "monitor": {
                "bsonType": "object",
                "description": "Details für monitor",
                "required": ["fuermonitor", "start", "end", "title", "text"],
                "properties": {
                    "fuerhome": {
                        "bsonType": "bool",
                        "description": "gibt an, ob die News auf monitor erscheinen soll -- required"
                    },
                    "start": {
                        "bsonType": "date",
                        "description": "Startdatum für die News auf monitor -- required"
                    },
                    "end": {
                        "bsonType": "date",
                        "description": "Enddatum für die News auf monitor -- required"
                    },
                    "title": {
                        "bsonType": "string",
                        "description": "Titel der News auf monitor -- required"
                    },                   
                    "text": {
                        "bsonType": "string",
                        "description": "Text der News auf monitor -- required"
                    },                   
                },
            },
            "rang": {
                "bsonType": "int",
                "description": "...um alles in eine Reihenfolge zu bringen -- required"
            }
        }
    }
}

