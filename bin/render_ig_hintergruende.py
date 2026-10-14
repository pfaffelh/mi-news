#!/usr/bin/env python3
"""Die CD-Hintergruende der Instagram-Posts als PNG herausschreiben.

Gedacht fuer den Fall, dass jemand einen Post von Hand gestaltet -- in GIMP,
Affinity, Canva oder wo auch immer -- statt ihn in der App zu erzeugen. Die
Flaechen kommen aus `misc.instagram`, sind also dieselben, die die App rendert;
diese Datei haelt keine eigenen Masse oder Farben.

PNG und nicht JPEG: verlustfrei, damit mehrfaches Speichern beim Weiterarbeiten
die Flaechen nicht zermatscht.

Zwei Saetze pro Variante und Format:

    *-leer.png      nur Farbflaeche, Siegel-Wasserzeichen und Vierblatt
    *-vorlage.png   zusaetzlich Wortmarke und Institutsname an CD-Position

Aufruf:

    python3 bin/render_ig_hintergruende.py                  # alles nach ./ig-hintergruende
    python3 bin/render_ig_hintergruende.py -o /tmp/ig       # anderes Zielverzeichnis
    python3 bin/render_ig_hintergruende.py --ratio 1:1      # nur ein Format
    python3 bin/render_ig_hintergruende.py --lang en        # englischer Institutsname

Das Skript laeuft lokal und braucht weder Datenbank noch Netz.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from misc import instagram as insta
from misc.config import ig_ratios


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("-o", "--out", default="ig-hintergruende",
                   help="Zielverzeichnis (Vorgabe: ./ig-hintergruende)")
    p.add_argument("--ratio", action="append", choices=sorted(ig_ratios),
                   help="nur dieses Format; mehrfach angebbar (Vorgabe: alle)")
    p.add_argument("--variante", action="append", choices=sorted(insta.VARIANTEN),
                   help="nur diese Farbe; mehrfach angebbar (Vorgabe: alle)")
    p.add_argument("--lang", default="de", choices=["de", "en"],
                   help="Sprache des Institutsnamens in der Vorlage")
    p.add_argument("--nur", choices=["leer", "vorlage"],
                   help="nur einen der beiden Saetze schreiben")
    args = p.parse_args()

    ratios = args.ratio or sorted(ig_ratios)
    varianten = args.variante or sorted(insta.VARIANTEN)
    saetze = [args.nur] if args.nur else ["leer", "vorlage"]

    if "vorlage" in saetze and not insta.font_verfuegbar():
        print("Warnung: Arimo fehlt -- der Institutsname in *-vorlage.png "
              "entspricht nicht dem CD.", file=sys.stderr)

    os.makedirs(args.out, exist_ok=True)

    for variante in varianten:
        for ratio in ratios:
            kurz = ratio.replace(":", "x").replace(".", "_")
            for satz in saetze:
                if satz == "leer":
                    bild = insta.render_hintergrund(variante, ratio)
                else:
                    # Leere Ueberschrift: zeichnet Logo und Institutsname an
                    # CD-Position, aber keinen Text. Die Warnungen betreffen
                    # dann nur fehlende Assets und sind oben schon abgehandelt.
                    bild, _ = insta.render_standard(
                        "", "", variante=variante, ratio=ratio, lang=args.lang)
                pfad = os.path.join(args.out, f"{variante}-{kurz}-{satz}.png")
                bild.save(pfad, "PNG")
                print(pfad)


if __name__ == "__main__":
    main()
