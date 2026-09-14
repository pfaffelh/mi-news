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

# Farben aus dem Corporate Design der Universität (offizielle Farbvorgaben,
# cd.uni-freiburg.de). HEX-Werte 1:1 aus dem CD-Dokument "Corporate Design
# Farbvorgaben".
ufr_blau = "#344A9A"          # Hauptfarbe Blau 100 %
ufr_dunkelblau = "#00004A"    # Nachtblau — Schrift auf hellen Flächen
ufr_gelb = "#FFE863"          # Zusatzfarbe Schwefelgelb
ufr_gruen = "#00A082"         # Zusatzfarbe Türkisgrün
ufr_sand = "#F6F1E3"          # Hintergrundfarbe Sand (wärmer als Weiß)
ufr_schwarz = "#000000"       # offiziell reines Schwarz (war fälschlich #2A2A2A)
ufr_weiss = "#FFFFFF"

# Die Hausschrift der CD-Vorlagen ist Arial (LaTeX-Vorlage: \usepackage{helvet}).
# Arimo ist metrisch identisch und frei lizenziert (SIL Open Font License).
#
# Die Schrift liegt IM Repo (static/fonts/), nicht als System-Paket: Auf www2
# ist fonts-croscore nicht installiert, und Pillows eingebaute Ersatzschrift hat
# keine deutschen Umlaute — ä/ö/ü/ß erschienen dort als leere Kästchen. Gebündelt
# wird die Schrift per rsync mitdeployt und ist überall verfügbar. Relativer
# Pfad wie bei den Logos (App läuft aus dem Repo-Wurzelverzeichnis).
ig_font_regular = "static/fonts/Arimo-Regular.ttf"
ig_font_bold = "static/fonts/Arimo-Bold.ttf"

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
ig_hashtags_default = ["#mathematik", "#unifreiburg"]

# Steht unter der Wortmarke. Die Wortmarke allein sagt nur "Albert-Ludwigs-
# Universität Freiburg" — im CD wird die Einrichtung darunter genannt, sonst
# sieht der Post aus, als poste die Universität. Zweisprachig, passend zum
# zweisprachigen Kanal (deutscher BSc, englischer MSc).
ig_einrichtung = {
    "de": "Mathematisches Institut",
    "en": "Mathematical Institute",
}

# CD-Assets (aus dem offiziellen Vorlagen-Kit, cd.uni-freiburg.de):
#   Logo (Wortmarke "universität freiburg") in drei Farben, transparent
#   Siegel als dezentes Wasserzeichen
#   Blatt = Vierblatt-Gestaltungselement, weiße Silhouette zum Einfärben
ig_logo = {
    "blau": "static/ufr-logo-blau.png",
    "weiss": "static/ufr-logo-weiss.png",
    "schwarz": "static/ufr-logo-schwarz.png",
}
# Siegel-Linien als transparente Silhouette (aus dem deckenden Original
# extrahiert), damit es sich auf jedem Hintergrund tonal einfärben lässt.
ig_siegel = "static/ufr-siegel-linien.png"
ig_blatt = "static/ufr-blatt.png"

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
    secrets_dir = "/var/local/lib/mi-news"
else:
    secrets_dir = os.path.expanduser("~/.mi-news")

# Lokal die übliche ~/.netrc (dort liegen schon LDAP, SMTP, DeepL).
#
# Auf www2 liegt sie neben dem Code, in /usr/local/lib/mi-news/.netrc. Das ist
# die Hauskonvention der Sysadmins -- mi-hp hält es seit jeher genauso
# (/usr/local/lib/mi-hp/.netrc), und dort wurde sie am 14.09.2026 auch für
# mi-news abgelegt. Wir folgen dem, statt eine zweite Datei daneben zu
# verlangen; secrets_dir bleibt als Fallback stehen, falls sie später doch
# dorthin wandert.
#
# Ein Vorbehalt, damit er nicht verlorengeht: Das Code-Verzeichnis ist zugleich
# das rsync-Ziel von deploy-mi-news.sh. Solange --delete dort auskommentiert
# ist, lässt rsync eine Datei, die im Checkout nicht vorkommt, in Ruhe -- wird
# die Zeile jemals scharf geschaltet, ist die .netrc beim nächsten Deploy weg.
# Die Token-Datei bleibt deshalb ausserhalb: die wird laufend neu geschrieben,
# und ihr Verlust wäre endgültig (kein Refresh mehr möglich).

app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if socket.gethostname() == "www2":
    _netrc_kandidaten = [
        os.path.join(app_dir, ".netrc"),       # Hauskonvention, wie mi-hp
        os.path.join(secrets_dir, ".netrc"),   # Fallback
    ]
    netrc_file = next((f for f in _netrc_kandidaten if os.path.exists(f)),
                      _netrc_kandidaten[0])
else:
    # Bewusst NICHT app_dir: eine .netrc im Checkout wäre einen Fehlgriff vom
    # Commit entfernt. (Sicherheitshalber steht sie auch in .gitignore.)
    netrc_file = os.path.expanduser("~/.netrc")

ig_token_file = os.path.join(secrets_dir, "ig_token.json")

# Der Eintrag in der .netrc, unter dem App-ID/-Secret und die User-ID stehen.
ig_netrc_machine = "graph.instagram.com"

# Graph-API. Host ist graph.instagram.com (Instagram Login), NICHT
# graph.facebook.com -- der gehört zum alten Facebook-Login-Pfad.
ig_api_host = "https://graph.instagram.com"
ig_api_version = "v25.0"

# Öffentliche Basis-URL, unter der mi-hp das gerenderte Bild ausliefert
# (Route /nlehre/insta/<token>.jpg). Meta lädt das Bild SELBST von dieser URL
# herunter (die Graph-API kennt keinen Upload) -- sie muss also von außen
# erreichbar sein: die kanonische Domain, nicht die VPN-interne Editor-App.
ig_public_image_base = "https://www.math.uni-freiburg.de"

# TTL für die Bilder in der Collection insta_bild (Sekunden). Das Bild wird nur
# während der Container-Erstellung gebraucht; mi-news löscht es danach selbst.
# Der TTL-Index ist die Absicherung, falls das Aufräumen mal ausfällt.
ig_insta_bild_ttl = 3600

# Der Token ist 60 Tage gültig und lässt sich nur erneuern, solange er noch
# lebt: "Tokens that have not been refreshed in 60 days will expire and can no
# longer be refreshed." Danach hilft nur noch ein neuer Token von Hand im
# Meta-App-Dashboard. Deshalb wöchentlich refreshen statt das Fenster
# auszureizen -- dann darf der Job siebenmal scheitern, bevor etwas kaputtgeht.
ig_token_warn_days = 14
