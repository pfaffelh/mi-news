import os
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

# --- Zugangsdaten -------------------------------------------------------------
#
# Nichts davon liegt im Repo. Auf www2 wird per `git pull` + rsync deployt --
# alles, was im Baum liegt, wird dabei überschrieben, und die (auskommentierte)
# --delete-Zeile in deploy-mi-news.sh würde es sogar löschen. Die Geheimnisse
# liegen deshalb außerhalb von Checkout UND rsync-Ziel.
#
# Zwei Dateien, weil sich die eine nie und die andere alle 60 Tage ändert:
#
#   .netrc         statisch (App-ID, App-Secret, IG-User-ID). Hausstil, wie in
#                  mi-hp. Nur lesen.
#   ig_token.json  der Long-Lived Token. Rotiert -- den schreibt ausschließlich
#                  der Refresh-Job (bin/refresh_ig_token.py), atomar. Bewusst
#                  NICHT in der .netrc: Ein fehlerhafter Rewrite dort würde
#                  LDAP-, SMTP- und DeepL-Zugänge mitreißen.
#
# Auf www2 läuft die App als www-data (streamlit-mi-news.service); beide Dateien
# müssen www-data gehören, mode 600.

if socket.gethostname() == "www2":
    secrets_dir = "/var/lib/mi-news"
else:
    secrets_dir = os.path.expanduser("~/.mi-news")

# Lokal die übliche ~/.netrc (dort liegen schon LDAP, SMTP, DeepL);
# auf dem Server eine eigene neben der Token-Datei.
if socket.gethostname() == "www2":
    netrc_file = os.path.join(secrets_dir, ".netrc")
else:
    netrc_file = os.path.expanduser("~/.netrc")

ig_token_file = os.path.join(secrets_dir, "ig_token.json")

# Der Eintrag in der .netrc, unter dem App-ID/-Secret und die User-ID stehen.
ig_netrc_machine = "graph.instagram.com"

# Graph-API. Host ist graph.instagram.com (Instagram Login), NICHT
# graph.facebook.com -- der gehört zum alten Facebook-Login-Pfad.
ig_api_host = "https://graph.instagram.com"
ig_api_version = "v25.0"

# Der Token ist 60 Tage gültig und lässt sich nur erneuern, solange er noch
# lebt: "Tokens that have not been refreshed in 60 days will expire and can no
# longer be refreshed." Danach hilft nur noch ein neuer Token von Hand im
# Meta-App-Dashboard. Deshalb wöchentlich refreshen statt das Fenster
# auszureizen -- dann darf der Job siebenmal scheitern, bevor etwas kaputtgeht.
ig_token_warn_days = 14
