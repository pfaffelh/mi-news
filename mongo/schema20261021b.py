from pymongo import MongoClient

# Schema der Collections vortrag und vortragsreihe -- Stand 21.10.2026.
#
# Gegenueber schema20251023.py gibt es Raum, Sprecher und Affiliation nur noch
# einmal statt je Sprache:
#
#   vortrag:       ort_de/ort_en                         -> ort
#                  sprecher_de/sprecher_en               -> sprecher
#                  sprecher_affiliation_de/_en           -> sprecher_affiliation
#   vortragsreihe: ort_de_default/ort_en_default         -> ort_default
#
# Der Editor zeigte je nach Sprache nur eine der beiden Fassungen. Die andere
# behielt ihren alten Wert, und die deutsche Seite zeigte dann einen
# veralteten Raum. Titel, Abstract und Kommentare bleiben zweisprachig.

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

vortragsreihe_validator = {'$jsonSchema': {'bsonType': 'object',
                 'title': 'Eine Vortragsreihe.',
                 'required': ['sichtbar',
                              'event',
                              'lang_default',
                              'anzeigetage',
                              'kurzname',
                              'title_de',
                              'title_en',
                              'text_de',
                              'text_en',
                              'url',
                              'ort_default',
                              'start',
                              'end',
                              'duration_default',
                              'gastgeber_default',
                              'sekretariat_default',
                              '_public',
                              '_public_default',
                              'sync_with_calendar',
                              'calendar_url',
                              'rang',
                              'bearbeitet',
                              'kommentar'],
                 'properties': {'sichtbar': {'bsonType': 'bool',
                                             'description': 'Gibt an, ob die Vortragsreihe per Default '
                                                            'sichbar ist. -- required'},
                                'event': {'bsonType': 'bool',
                                          'description': 'Gibt an, ob es ein Event ist. -- required'},
                                'lang_default': {'enum': ['de', 'en'], 'description': 'Sprache der Reihe'},
                                'anzeigetage': {'bsonType': 'int',
                                                'description': 'Anzahl der Tage vor dem Termine, die auf der '
                                                               'hp angezeigt werden. -- required'},
                                'kurzname': {'bsonType': 'string',
                                             'description': 'Kurzname der Vortragsreihe (de) -- required'},
                                'title_de': {'bsonType': 'string',
                                             'description': 'Titel der Vortragsreihe (de) -- required'},
                                'title_en': {'bsonType': 'string',
                                             'description': 'Titel der Vortragsreihe (en) -- required'},
                                'text_de': {'bsonType': 'string',
                                            'description': 'Beschreibung der Vortragsreihe (de) -- required'},
                                'text_en': {'bsonType': 'string',
                                            'description': 'Beschreibung der Vortragsreihe (en) -- required'},
                                'url': {'bsonType': 'string',
                                        'description': "Externe Homepage der Reihe oder des Events (oder ''). Die Seite im "
                                                       'Wochenprogramm entsteht aus dem kurznamen. -- required'},
                                'ort_default': {'bsonType': 'string',
                                                'description': 'Ort, wo der Vortrag normalerweise '
                                                               'stattfindet, in allen Sprachen gleich -- '
                                                               'required'},
                                'duration_default': {'bsonType': 'int',
                                                     'description': 'Default duration in minutes -- '
                                                                    'required'},
                                'gastgeber_default': {'bsonType': 'string',
                                                      'description': 'Üblicher Gastgeber -- required'},
                                'sekretariat_default': {'bsonType': 'string',
                                                        'description': 'Übliches Sekretariat -- required'},
                                'start': {'bsonType': 'date',
                                          'description': 'Startdatum für die News auf home -- required'},
                                'end': {'bsonType': 'date',
                                        'description': 'Enddatum für die News auf home -- required'},
                                '_public': {'bsonType': 'bool',
                                            'description': 'Gibt an, ob die Vortragsreihe veröffentlicht (dh '
                                                           'auf home zu sehen) werden soll.  -- required'},
                                '_public_default': {'bsonType': 'bool',
                                                    'description': 'Gibt an, ob Vorträge generell sofort '
                                                                   'veröffentlicht werden soll.  -- '
                                                                   'required'},
                                'bearbeitet': {'bsonType': 'string',
                                               'description': 'Gibt an wann und von wem die Vortragsreihe '
                                                              'zuletzt bearbeitet wurde -- required'},
                                'sync_with_calendar': {'bsonType': 'bool',
                                                       'description': 'Gibt an, ob die Vortragsreihe mit '
                                                                      'einem Kalender synchronisiert werden '
                                                                      'soll. -- required'},
                                'calendar_url': {'bsonType': 'string',
                                                 'description': "url zum caldav-Server oder '' -- required"},
                                'kommentar': {'bsonType': 'string',
                                              'description': 'Ein Kommentar -- required'},
                                'rang': {'bsonType': 'int',
                                         'description': '...um alles in eine Reihenfolge zu bringen -- '
                                                        'required'}}}}

vortrag_validator = {'$jsonSchema': {'bsonType': 'object',
                 'title': 'Ein Vortrag.',
                 'required': ['vortragsreihe',
                              'lang',
                              'sprecher',
                              'sprecher_affiliation',
                              'ort',
                              'title_de',
                              'title_en',
                              'text_de',
                              'text_en',
                              'gastgeber',
                              'sekretariat',
                              'url',
                              '_public',
                              'start',
                              'end',
                              'bearbeitet',
                              'kommentar_de',
                              'kommentar_en',
                              'kommentar_intern'],
                 'properties': {'vortragsreihe': {'bsonType': 'array',
                                                  'items': {'bsonType': 'objectId',
                                                            'description': 'eine Vortragsreihe, in der der '
                                                                           'Termin erscheinen soll.'}},
                                'lang': {'enum': ['de', 'en'], 'description': 'Sprache des Vortrages'},
                                'sprecher': {'bsonType': 'string',
                                             'description': 'Sprecher des Vortrages, in allen Sprachen '
                                                            'gleich -- required'},
                                'sprecher_affiliation': {'bsonType': 'string',
                                                         'description': 'Affiliation des Sprechers, in allen '
                                                                        'Sprachen gleich -- required'},
                                'ort': {'bsonType': 'string',
                                        'description': 'Ort, wo der Vortrag stattfindet, in allen Sprachen '
                                                       'gleich -- required'},
                                'gastgeber': {'bsonType': 'string',
                                              'description': 'Wer hat den Sprecher eingeladen?'},
                                'sekretariat': {'bsonType': 'string',
                                                'description': 'Welches Sekretariat bearbeitet den Vortrag?'},
                                'title_de': {'bsonType': 'string',
                                             'description': 'Titel der News auf home (de) -- required'},
                                'title_en': {'bsonType': 'string',
                                             'description': 'Titel der News auf home (en) -- required'},
                                'text_de': {'bsonType': 'string',
                                            'description': 'Text der News auf home (de) -- required'},
                                'text_en': {'bsonType': 'string',
                                            'description': 'Text der News auf home (en) -- required'},
                                'url': {'bsonType': 'string',
                                        'description': "Gibt einen url für diesen Vortrag an (oder '') -- "
                                                       'required'},
                                '_public': {'bsonType': 'bool',
                                            'description': 'Gibt an, ob der Vortrag bereits auf home zu '
                                                           'sehen ist.  -- required'},
                                'start': {'bsonType': 'date',
                                          'description': 'Startdatum und Zeit des Vortrages -- required'},
                                'end': {'bsonType': 'date',
                                        'description': 'Enddatum und Zeit des Vortrages -- required'},
                                'bearbeitet': {'bsonType': 'string',
                                               'description': 'Gibt an wann und von wem der Vortrag zuletzt '
                                                              'bearbeitet wurde -- required'},
                                'kommentar_de': {'bsonType': 'string',
                                                 'description': 'Ein Kommentar -- required'},
                                'kommentar_en': {'bsonType': 'string',
                                                 'description': 'Ein Kommentar -- required'},
                                'kommentar_intern': {'bsonType': 'string',
                                                     'description': 'Ein Kommentar -- required'}}}}
