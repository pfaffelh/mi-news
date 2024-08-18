from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["news"]

bild = mongo_db["bild"]
news = mongo_db["news"]
carouselnews = mongo_db["carouselnews"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

keepcarouselnews = ["Wenn Sie neue Nachrichten haben, schicken Sie diese bitte an <br> news@math.uni-freiburg.de"]

ne = list(carouselnews.find())
for n in ne:
    if n["text"] not in keepcarouselnews:
        carouselnews.delete_one({"_id": n["_id"]})

keepnews = ["Bewerbung für die Master-Studiengänge", 
"Neue Homepage für Lehre", 
"Neuer Studiengang MSc Mathematics in Data and Technology", 
"Lehrzertifikat für Postdocs"]

ne = list(news.find())
for n in ne:
    if n["home"]["title_de"] not in keepnews:
        news.delete_one({"_id": n["_id"]})

# Bilder-Doubletten löschen und nur einige behalten
dozentenfiles = ["bartels.jpg", "boecherer.jpg", "diehl.jpg", "goette.jpg", "huber.jpg", "kebekus.jpg", "kroener.jpg", "luetkebohmert-holtz.jpg", "pfaffelhuber.jpg", "rohde.jpg", "salimova.jpg", "soergel.jpg", "binder.jpg", "criens.jpg", "dondl.jpg", "grosse.jpg", "junker.jpg", "knies.jpg", "kuwert.jpg", "mildenberger.jpg",  "pizarro.jpg", "ruzicka.jpg", "schmidt.jpg", "wang.jpg"]
# images to keep
filenames = dozentenfiles + ["Uni Freiburg_Okt_2021_4.jpg", 
"slider_Dies_Universitaet_Freiburg_final-1024x717.jpg", 
"HN17065984.jpg", 
"Uni Freiburg_Okt 2021 1.jpg", 
"Universitätsbibliothek_Sommer_2023 2.jpg", 
"ALU_Botanische_Garten_228.jpg", 
"ALU_Botanische_Garten_322.jpg", 
"_MG_7561_2.jpg", 
"MScData_Postkarte_E_00001.jpg",
"Uni Rostock-UnterrichtsfreieZeit_23-02-19_0034a-small-30254@528f6ee5-d1ae-49fd-a381-88c12a465571.jpg", 
"Uni Rostock-Bewerbung_19-04-11_0009 px-preview-14850@528f6ee5-d1ae-49fd-a381-88c12a465571.jpg", 
"Bildschirmfoto von 2024-08-06 22-04-14.jpg", 
"circle_cropped.jpg", 
"modulhandbuch.jpg", 
"zulassungsordnung.jpg", 
"institut_resize.jpg", 
"startseite_dozenten_2023_klein.jpg", 
"ordnung.jpg", 
"yt_stuber.jpg", 
"yt_dondl.jpg", 
"sciencedays.jpeg", 
"yt_mathe1_resize.jpg", 
"yt_mathe2.jpg", 
"yt_mathe2_resize.jpg", 
"slider_Dies_Universitaet_Freiburg_final-1024x717.png", 
"Logo_Freiburg_Seminar.png", 
"yt_grosse.jpg", 
"40min_header-1-1024x533.jpg", 
"startseite_dozenten_2023_resize.jpg", 
"startseite_dozenten_2023.jpg", 
"yt_mathe_channel.jpg", 
"yt_schmidt.jpg", 
"yt_pfaffelhuber.jpg", 
"MEdDual.png", 
"gasthoerer.jpeg", 
"kosmicxn.png", 
"sommerfest.png", 
"pngout.png", 
"Webseite-oben-schmal-alte_Buecher.jpg", 
"startseite_tafel.jpg", 
"MAT_kachel_OSA-Stempel_364.jpg", 
"studint-schild_rundbau-junker.jpg", 
"Logo_Freiburg_Seminar.png", 
"gasthoerer.jpeg", 
"Barbara-Hanser.jpg", 
"studint-max2-ghasemi_weismann.jpg", 
"logo_didaktik.png", 
"20150928-2690.jpg", 
"20150928-2712.jpg", 
"20150928-2702.jpg", 
"Peter-Pfaffelhuber.jpg", 
"Markus-Junker.jpg", 
"studint-marius.jpg", 
"studint-song.jpg", 
"studint-rundbau-kramer.jpg", 
"studint-oben.jpg", 
"studint-song.jpg", 
"ALU_MG_8797.jpg"]




ne = list(bild.find())
for n in ne:
    if n["filename"] not in filenames:
        bild.delete_one({"_id": n["_id"]})
    
