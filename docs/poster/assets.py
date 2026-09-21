#!/usr/bin/env python3
"""Erzeugt die abgeleiteten Bilddateien fuer das Poster.

Aus dem Repo-Wurzelverzeichnis aufrufen:

    venv/bin/python docs/poster/assets.py

Die drei Dateien liegen im Repo, damit sich das Poster ohne Python uebersetzen
laesst. Neu erzeugen muss man sie nur, wenn die Quellen unter static/ sich
aendern.

Warum ueberhaupt abgeleitet:

  Vierblatt und Siegel sind weisse Silhouetten mit Alphakanal, die erst
  eingefaerbt werden. Das erledigt _tint() -- dieselbe Funktion, die auch die
  Instagram-Bilder einfaerbt, im selben Mischungsverhaeltnis. So trifft das
  Poster den Farbton der Posts exakt, statt ihn nachzuempfinden.

  Die Wortmarke hat rundum einen transparenten Rand (links 6,5 % der
  Dateibreite). Ohne Zuschnitt saesse der sichtbare Schriftzug bei 80 mm
  Bildbreite 5,2 mm weiter rechts als der Institutsname darunter -- die
  Blockkante waere sichtbar verrutscht. render_standard() schneidet aus genau
  diesem Grund auf die Bounding-Box zu; hier passiert dasselbe.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PIL import Image

from misc.config import ufr_blau, ufr_gelb
from misc.instagram import _mische, _tint

ZIEL = os.path.dirname(os.path.abspath(__file__))


def main():
    # Anteil Blau im Gelb -- exakt die Werte aus render_standard().
    for quelle, anteil, name in [
        ("static/ufr-siegel-linien.png", 0.10, "ufr-siegel-gelb.png"),
        ("static/ufr-blatt.png", 0.20, "ufr-blatt-gelb.png"),
    ]:
        farbe = _mische(ufr_gelb, ufr_blau, anteil)
        bild = _tint(quelle, farbe, 1.0)
        bild.save(os.path.join(ZIEL, name))
        print(f"{name:26s} {bild.size}  Ton {farbe}")

    logo = Image.open("static/ufr-logo-blau.png").convert("RGBA")
    vorher = logo.size
    logo = logo.crop(logo.getbbox())
    name = "ufr-logo-blau-beschnitten.png"
    logo.save(os.path.join(ZIEL, name))
    print(f"{name:26s} {logo.size}  (vorher {vorher}, transparenter Rand entfernt)")


if __name__ == "__main__":
    main()
