from pymongo import MongoClient

# Write to database:
# Collections are: 
# mensaplan
# bild: File, Titel, Bildnachweis, 
# carouselnews: test, _public, showstart, showend, interval, image, left (in %), right (in %), bottom (in %), text
# news: link, image (object), home (object), monitor (object)
# vortragsreihe
# vortrag

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
        "required": ["filename", "menu", "mime", "data", "thumbnail", "titel", "kommentar", "bearbeitet", "bildnachweis", "rang"],
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
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem das Bild zuletzt bearbeitet wurde -- required"
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
        "required": ["_public", "start", "end", "interval", "image_id", "left", "right", "bottom", "text", "rang", "bearbeitet", "kommentar"],
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
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem das Bild zuletzt bearbeitet wurde -- required"
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

news_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Nachricht.",
        "required": ["link", "_public", "archiv", "showlastday", "highlight", "image", "home", "monitor", "rang", "bearbeitet", "kommentar", "tags"],
        "properties": {
            "tags": {
            "bsonType": "array",
            "uniqueItems": True,
            "items": {
                "enum": ["Monitor", "Lehre", "Institut"]
                }
            },
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
                "required": ["start", "end", "title_de", "title_en", "text_de", "text_en", "popover_title_de", "popover_title_en", "popover_text_de", "popover_text_en"],
                "properties": {
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
                "required": ["start", "end", "title", "text"],
                "properties": {
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
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem das Bild zuletzt bearbeitet wurde -- required"
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

vortragsreihe_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Vortragsreihe.",
        "required": ["sichtbar", "event", "lang_default", "anzeigetage", "kurzname", "title_de", "title_en", "text_de", "text_en", "url", "ort_de_default", "start", "end", "duration_default", "ort_en_default", "gastgeber_default", "sekretariat_default", "_public", "_public_default", "sync_with_calendar", "calendar_url", "rang", "bearbeitet", "kommentar"],
        "properties": {
            "sichtbar": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Vortragsreihe per Default sichbar ist. -- required"
            },
            "event": {
                "bsonType": "bool",
                "description": "Gibt an, ob es ein Event ist. -- required"
            },
            "lang_default": {
                "enum": ["de", "en"],
                "description": "Sprache der Reihe",
            },
            "anzeigetage": {
                "bsonType": "int",
                "description": "Anzahl der Tage vor dem Termine, die auf der hp angezeigt werden. -- required"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "Kurzname der Vortragsreihe (de) -- required"
            },
            "title_de": {
                "bsonType": "string",
                "description": "Titel der Vortragsreihe (de) -- required"
            },
            "title_en": {
                "bsonType": "string",
                "description": "Titel der Vortragsreihe (en) -- required"
            },
            "text_de": {
                "bsonType": "string",
                "description": "Beschreibung der Vortragsreihe (de) -- required"
            },
            "text_en": {
                "bsonType": "string",
                "description": "Beschreibung der Vortragsreihe (en) -- required"
            },
            "url": {
                "bsonType": "string",
                "description": "Gibt einen url für diese Vortragsreihe an -- required"
            },
            "ort_de_default": {
                "bsonType": "string",
                "description": "Ort, wo der Vortrag normalerweise stattfindet -- required"
            },                   
            "ort_en_default": {
                "bsonType": "string",
                "description": "Ort, wo der Vortrag normalerweise stattfindet -- required"
            },                   
            "duration_default": {
                "bsonType": "int",
                "description": "Default duration in minutes -- required"
            },                   
            "gastgeber_default": {
                "bsonType": "string",
                "description": "Üblicher Gastgeber -- required"
            },                   
            "sekretariat_default": {
                "bsonType": "string",
                "description": "Übliches Sekretariat -- required"
            },                   
            "start": {
                "bsonType": "date",
                "description": "Startdatum für die News auf home -- required"
            },
            "end": {
                "bsonType": "date",
                "description": "Enddatum für die News auf home -- required"
            },
            "_public": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Vortragsreihe veröffentlicht (dh auf home zu sehen) werden soll.  -- required"
            },
            "_public_default": {
                "bsonType": "bool",
                "description": "Gibt an, ob Vorträge generell sofort veröffentlicht werden soll.  -- required"
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem die Vortragsreihe zuletzt bearbeitet wurde -- required"
            },
            "sync_with_calendar": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Vortragsreihe mit einem Kalender synchronisiert werden soll. -- required"
            },
            "calendar_url": {
                "bsonType": "string",
                "description": "url zum caldav-Server oder '' -- required"
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

vortrag_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Vortrag.",
        "required": ["vortragsreihe", "lang", "sprecher_de", "sprecher_en", "sprecher_affiliation_de", "sprecher_affiliation_en", "ort_de", "ort_en", "title_de", "title_en", "text_de", "text_en", "gastgeber", "sekretariat", "url", "_public", "start", "end", "bearbeitet", "kommentar_de", "kommentar_en", "kommentar_intern"],
        "properties": {
            "vortragsreihe": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "eine Vortragsreihe, in der der Termin erscheinen soll."
                }
            },
            "lang": {
                "enum" : ["de", "en"],
                "description": "Sprache des Vortrages"
            },
            "sprecher_de": {
                "bsonType": "string",
                "description": "Sprecher des Vortrages -- required"
            },                   
            "sprecher_en": {
                "bsonType": "string",
                "description": "Sprecher des Vortrages auf englisch, falls abweichend-- required"
            },
            "sprecher_affiliation_de": {
                "bsonType": "string",
                "description": "Sprecher des Vortrages -- required"
            },                   
            "sprecher_affiliation_en": {
                "bsonType": "string",
                "description": "Sprecher des Vortrages auf englisch, falls abweichend-- required"
            },
            "gastgeber": {
                "bsonType": "string",
                "description": "Wer hat den Sprecher eingeladen?"
            },
            "sekretariat": {
                "bsonType": "string",
                "description": "Welches Sekretariat bearbeitet den Vortrag?"
            },
            "ort_de": {
                "bsonType": "string",
                "description": "Ort, wo der Vortrag stattfindet -- required"
            },                   
            "ort_en": {
                "bsonType": "string",
                "description": "Ort, wo der Vortrag stattfindet -- required"
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
            "url": {
                "bsonType": "string",
                "description": "Gibt einen url für diesen Vortrag an (oder '') -- required"
            },
            "_public": {
                "bsonType": "bool",
                "description": "Gibt an, ob der Vortrag bereits auf home zu sehen ist.  -- required"
            },
            "start": {
                "bsonType": "date",
                "description": "Startdatum und Zeit des Vortrages -- required"
            },
            "end": {
                "bsonType": "date",
                "description": "Enddatum und Zeit des Vortrages -- required"
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Gibt an wann und von wem der Vortrag zuletzt bearbeitet wurde -- required"
            },
            "kommentar_de": {
                "bsonType": "string",
                "description": "Ein Kommentar -- required"
            },
            "kommentar_en": {
                "bsonType": "string",
                "description": "Ein Kommentar -- required"
            },
            "kommentar_intern": {
                "bsonType": "string",
                "description": "Ein Kommentar -- required"
            }
        }
    }
}

