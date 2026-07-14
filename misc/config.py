import socket

# Das ist der LDAP-Server der Universität, der für die Authentifizierung verwendet wird.
server="ldaps://ldap.uni-freiburg.de"
base_dn = "ou=people,dc=uni-freiburg,dc=de"

# Hier ist die MongoDBsocket.gethostname()
if socket.gethostname() == "www2":
    mongo_location = "mongodb://localhost:27017"
else:
    mongo_location = "mongodb://localhost:27017"

# Name der Berechtigung für diese App in der Datenbank
app_name = "news"

# Die log-Datei
log_file = 'mi.log'

# Feste Vortragsreihen, deren Kurzname nicht gelöscht werden soll:
kurznamen = ["Logik", "Kolloquium", "GeoAna", "FDMAI", "DiffGeo", "Stochastik", "AM", "Algebra", "Didaktik", "alle"]

# Falls alltags geändert wird, muss das Datenbank-Schema angepasst werden.
alltags = ["Monitor", "Lehre", "Institut"]

# ----------------------------------------------------------------- Instagram --

# Farben aus dem Corporate Design der Universität (Slide-Master von
# poster-A3.potx, cd.uni-freiburg.de). Achtung: Das Theme in mi-hp verwendet
# #34499a; verbindlich ist der Wert hier aus der offiziellen Vorlage.
ufr_blau = "#344A9A"
ufr_gelb = "#FFE863"
ufr_schwarz = "#2A2A2A"
ufr_weiss = "#FFFFFF"

# Die Hausschrift der CD-Vorlagen ist Arial (LaTeX-Vorlage: \usepackage{helvet}).
# Arimo ist metrisch identisch und frei lizenziert — deshalb kein Lizenzproblem.
ig_font_regular = "/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"
ig_font_bold = "/usr/share/fonts/truetype/croscore/Arimo-Bold.ttf"

# Zulässige Instagram-Formate für Feed-Posts (Breite × Höhe in px).
# Erlaubt ist alles zwischen 4:5 (hoch) und 1.91:1 (quer).
ig_ratios = {
    "4:5": (1080, 1350),
    "1:1": (1080, 1080),
    "1.91:1": (1080, 566),
}
ig_ratio_default = "4:5"

# Instagram skaliert unter 320 px hoch — das sieht man.
ig_min_source_px = 320

# Harte Grenzen der Caption.
ig_caption_maxlen = 2200
ig_hashtag_max = 30

# Vorschlag, den die Redaktion im Editor überschreiben kann.
ig_hashtags_default = ["#unifreiburg", "#mathematik"]

# Steht unter der Wortmarke. Die Wortmarke allein sagt nur "Albert-Ludwigs-
# Universität Freiburg" — im CD wird die Einrichtung darunter genannt, sonst
# sieht der Post aus, als poste die Universität.
ig_einrichtung = "Mathematisches Institut"
