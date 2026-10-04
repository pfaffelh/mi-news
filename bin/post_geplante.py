#!/usr/bin/env python3
"""Faellige Instagram-Posts veroeffentlichen. Gehoert in einen Cron-Job.

Die Editor-App ist Streamlit und laeuft nur, solange jemand die Seite offen
hat -- um 9 Uhr morgens fuehrt sie nichts aus. Ein geplanter Post braucht
deshalb einen eigenen Prozess. Gerendert wird hier neu aus den Feldern des
Posts (bildtyp, image_id, fit, ratio, caption); ein vorgerendertes Bild muss
also nicht gespeichert werden, und eine spaete Korrektur wirkt noch.

Einrichtung auf www2 -- zweite Zeile in der schon vorhandenen Datei:

    # /etc/cron.d/mi-news
    */15 * * * * www-data /usr/local/lib/mi-news/venv/bin/python \\
        /usr/local/lib/mi-news/bin/post_geplante.py --quiet

Als www-data, nicht als flask-reader: ig_token.json in /var/local/lib/mi-news
hat Modus 600 und gehoert www-data.

Warum ein Post vor dem Posten atomar beansprucht wird: publish() ist nicht
idempotent, und loeschen koennen wir einen Beitrag nicht -- der
DELETE-Endpunkt der Graph-API steht nur der Facebook-Login-Variante offen.
Ein Lauf dauert bis zu gut einer Minute (Meta holt das Bild selbst ab,
_warte_auf_fertig pollt bis zu 60 s). Bei 15-Minuten-Takt ueberlappen sich
zwei Laeufe praktisch nie -- aber "praktisch nie" ist bei einer Aktion, die
sich nicht zuruecknehmen laesst, zu wenig. find_one_and_update setzt den
Status in derselben Operation, in der es den Post findet; ein zweiter Lauf
findet ihn dann nicht mehr.

Aus demselben Grund gibt es keinen automatischen Neuversuch. Scheitert der
letzte Schritt von publish() (Kommentare abschalten), ist der Beitrag bereits
live; ein Retry wuerde ihn ein zweites Mal posten. Solche Posts bleiben auf
"fehler" stehen, bis ein Mensch nachsieht -- ebenso Posts, die in
"wird_gepostet" haengen, weil der Prozess abgebrochen ist.

Exit-Codes: 0 = nichts zu tun oder alles veroeffentlicht,
            1 = mindestens ein Post ist gescheitert (Cron schickt eine Mail).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone

import pymongo

from misc import instagram as ig
from misc.config import mongo_location

# Laenger als das her, wird nicht mehr gepostet. Ein Reminder fuer eine
# Veranstaltung von gestern hilft niemandem mehr, und stillschweigend etwas
# Veraltetes zu posten ist schlimmer, als es liegen zu lassen.
MAX_VERSPAETUNG = timedelta(hours=24)


def hole_faelligen(instapost, jetzt):
    """Einen faelligen Post beanspruchen -- atomar. None, wenn keiner da ist."""
    return instapost.find_one_and_update(
        {"status": "geplant",
         "geplant_fuer": {"$lte": jetzt, "$gte": jetzt - MAX_VERSPAETUNG}},
        {"$set": {"status": "wird_gepostet"}},
        sort=[("geplant_fuer", pymongo.ASCENDING)],
        return_document=pymongo.ReturnDocument.AFTER,
    )


def verfallene_melden(instapost, jetzt, sag):
    """Posts, deren Zeitpunkt zu lange her ist, auf 'fehler' setzen.

    Sonst blieben sie unbemerkt auf "geplant" stehen und sagten niemandem,
    dass sie nie rausgegangen sind.
    """
    anzahl = 0
    while True:
        p = instapost.find_one_and_update(
            {"status": "geplant",
             "geplant_fuer": {"$lt": jetzt - MAX_VERSPAETUNG}},
            {"$set": {"status": "fehler",
                      "last_error": "Der geplante Zeitpunkt liegt mehr als "
                                    f"{MAX_VERSPAETUNG // timedelta(hours=1)} "
                                    "Stunden zurueck -- nicht mehr automatisch "
                                    "gepostet. Bitte pruefen und von Hand "
                                    "veroeffentlichen oder neu planen."}},
        )
        if p is None:
            return anzahl
        anzahl += 1
        sag(f"VERFALLEN: {p.get('titel') or '(ohne Titel)'} "
            f"(geplant fuer {p['geplant_fuer']:%Y-%m-%d %H:%M} UTC)",
            fehler=True)


def posten(instapost, bild, post, sag):
    """Einen beanspruchten Post rendern und veroeffentlichen."""
    titel = post.get("titel") or post.get("headline") or "(ohne Titel)"

    bild_data = None
    if post.get("bildtyp") == "bild" and post.get("image_id"):
        b = bild.find_one({"_id": post["image_id"]})
        bild_data = b["data"] if b else None

    vorschau, _ = ig.render(post, bild_data)
    if vorschau is None:
        raise RuntimeError("Es liess sich kein Bild erzeugen "
                           "(fehlende oder geloeschte Bildquelle).")

    probleme = ig.post_probleme(post, post.get("caption", ""))
    if probleme:
        raise RuntimeError("; ".join(probleme))

    media_id = ig.publish(ig.to_jpeg(vorschau), post.get("caption", ""))
    instapost.update_one(
        {"_id": post["_id"]},
        {"$set": {"status": "veroeffentlicht",
                  "ig_media_id": media_id,
                  "permalink": ig.permalink(media_id),
                  "published_at": datetime.now(timezone.utc),
                  "geplant_fuer": None,
                  "last_error": ""}},
    )
    sag(f"veroeffentlicht: {titel} (Media-ID {media_id})")


def main():
    parser = argparse.ArgumentParser(
        description="Veroeffentlicht faellige, geplante Instagram-Posts.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Im Erfolgsfall nichts ausgeben. Fehler gehen "
                             "weiterhin nach stderr.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Jeden geplanten Post durchrechnen: Bild erzeugen, "
                             "pruefen, Lage melden. Nichts posten, nichts in der "
                             "Datenbank aendern, kein Zugriff auf die "
                             "Instagram-API -- laeuft daher auch lokal ohne Token.")
    parser.add_argument("--probelauf", action="store_true",
                        help="Die ganze Kette gegen Instagram durchspielen, aber "
                             "NICHT veroeffentlichen: Bild bereitstellen, "
                             "Media-Container anlegen, auf FINISHED warten. "
                             "Prueft Token und ob Meta unsere Bild-URL erreicht. "
                             "Aendert nichts in der Datenbank.")
    args = parser.parse_args()

    def sag(text, fehler=False):
        if fehler:
            print(text, file=sys.stderr)
        elif not args.quiet:
            jetzt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            print(f"{jetzt}  {text}")

    db = pymongo.MongoClient(mongo_location)["news"]
    instapost, bild = db["instapost"], db["bild"]
    jetzt = datetime.now(timezone.utc)

    if args.dry_run or args.probelauf:
        geplante = list(instapost.find({"status": "geplant"},
                                       sort=[("geplant_fuer", pymongo.ASCENDING)]))
        if not geplante:
            print("Kein geplanter Post.")
            return 0
        schlecht = 0
        for p in geplante:
            wann = p.get("geplant_fuer")
            if wann is None:
                lage = "ohne Zeit"
            elif wann.replace(tzinfo=timezone.utc) < jetzt - MAX_VERSPAETUNG:
                lage = "verfallen"
            elif wann.replace(tzinfo=timezone.utc) <= jetzt:
                lage = "FAELLIG"
            else:
                lage = "wartet"
            titel = p.get("titel") or p.get("headline") or "(ohne Titel)"
            zeit = f"{wann:%Y-%m-%d %H:%M}" if wann else "        —       "
            print(f"  {lage:10} {zeit} UTC  {titel}")

            # Dasselbe Rendern und Pruefen wie beim echten Lauf -- nur ohne zu
            # posten. Damit faellt hier auf, was sonst erst zur Postzeit auffiele:
            # geloeschtes Bild, leere Caption, zu lange Caption.
            try:
                bild_data = None
                if p.get("bildtyp") == "bild" and p.get("image_id"):
                    b = bild.find_one({"_id": p["image_id"]})
                    bild_data = b["data"] if b else None
                vorschau, warnungen = ig.render(p, bild_data)
                if vorschau is None:
                    raise RuntimeError("kein Bild (Bildquelle fehlt oder geloescht)")
                jpg = ig.to_jpeg(vorschau)
                print(f"             Bild {vorschau.width}x{vorschau.height} px, "
                      f"{len(jpg) // 1024} KB")
                for w in warnungen:
                    print(f"             Hinweis: {w}")
                for pr in ig.post_probleme(p, p.get("caption", "")):
                    schlecht += 1
                    sys.stdout.flush()
                    print(f"             WUERDE SCHEITERN: {pr}", file=sys.stderr)
                if args.probelauf and lage in ("FAELLIG", "wartet"):
                    cid = ig.probelauf(jpg, p.get("caption", ""))
                    print(f"             Probelauf ok — Container {cid} angelegt "
                          "und von Instagram akzeptiert, nicht veroeffentlicht.")
            except Exception as e:
                schlecht += 1
                sys.stdout.flush()
                print(f"             FEHLER: {e}", file=sys.stderr)
        return 1 if schlecht else 0

    if not ig.is_configured():
        # Kein Grund zur Aufregung, solange nichts ansteht -- aber wenn etwas
        # faellig ist und der Token fehlt, muss es auffallen.
        if instapost.count_documents({"status": "geplant",
                                      "geplant_fuer": {"$lte": jetzt}}):
            print("FEHLER: Es sind Posts faellig, aber der Instagram-Zugang "
                  "ist nicht konfiguriert (ig_token.json / .netrc).",
                  file=sys.stderr)
            return 1
        return 0

    fehler = verfallene_melden(instapost, jetzt, sag)

    while True:
        post = hole_faelligen(instapost, jetzt)
        if post is None:
            break
        try:
            posten(instapost, bild, post, sag)
        except Exception as e:
            fehler += 1
            instapost.update_one(
                {"_id": post["_id"]},
                {"$set": {"status": "fehler", "last_error": str(e)}},
            )
            sag(f"FEHLER bei '{post.get('titel') or '(ohne Titel)'}': {e}",
                fehler=True)

    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
