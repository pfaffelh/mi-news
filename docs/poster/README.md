# Poster für den Instagram-Kanal

Aushang fürs Institut: gelbe CD-Fläche, Wortmarke, Überschrift, QR-Code zum
Profil. Die Gestaltung ist dieselbe wie bei den Instagram-Posts selbst
(`misc/instagram.py`, Variante „gelb") — wer das Poster im Flur sieht und später
einen Beitrag im Feed, soll beides zusammenbringen.

| Datei | Zweck |
|---|---|
| [instagram-poster.tex](instagram-poster.tex) | Das Poster, A4 hoch |
| [assets.py](assets.py) | Erzeugt die drei abgeleiteten Bilddateien aus `static/` |
| `ufr-blatt-gelb.png`, `ufr-siegel-gelb.png` | Vierblatt und Siegel, im Gelbton eingefärbt |
| `ufr-logo-blau-beschnitten.png` | Wortmarke ohne ihren transparenten Rand |

## Übersetzen

```bash
lualatex instagram-poster.tex
```

**LuaLaTeX, nicht pdflatex** — `fontspec` braucht Lua- oder XeTeX. Zweimal
laufen lassen: Der QR-Code wird beim ersten Lauf berechnet und in der `.aux`
abgelegt, erst der zweite setzt ihn. Zu installieren ist nichts: Die Schrift
(Arimo, metrisch identisch zu Arial) liegt im Repo unter `static/fonts/`, die
Pakete `qrcode`, `fontawesome5` und `tikz` sind in jeder TeX-Live-Vollinstallation
enthalten.

## Sprache

Der Kanal ist deutsch, das Poster deshalb auch — **Deutsch ist der Standard.**
Für eine englische Fassung (etwa für die Master-Studiengänge) genügt Zeile 33:

```latex
\sprachedetrue      % deutsch:  "Folgt dem Mathematischen Institut auf Instagram"
\sprachedefalse     % englisch: "Follow the Mathematical Institute on Instagram"
```

Beide Fassungen sind gesetzt und geprüft.

## Wenn der Text geändert wird

Die Überschrift steht in einem TikZ-Knoten **ohne** `text width`, und ihre
Zeilenumbrüche stehen von Hand — auf einem Poster ist der Umbruch Gestaltung,
nicht Zufall. Beides hat eine Konsequenz: **Zu lange Zeilen laufen stillschweigend
über den Rand, ohne Overfull-Warnung.** Ins Satzfeld passen 170 mm (A4 minus
2 × 20 mm Rand); bis etwa 163 mm bleibt Reserve. Nachmessen statt schätzen:

```latex
\newlength{\laenge}
\settowidth{\laenge}{Die längste Zeile}\typeout{BREITE = \the\laenge}
```

Deshalb sind die Schriftgrößen sprachabhängig: Bei einheitlichen 46 pt wäre
„Mathematischen Institut" 185 mm breit geworden und 15 mm über den Rand gelaufen.
Jetzt sind es 40 pt (deutsch, 161 mm) und 44 pt (englisch, 162 mm).

## Der QR-Code

Ziel ist `https://www.instagram.com/math_uni_freiburg/`. Die URL steht **wörtlich**
im `\qrcode`-Argument, mit blankem Unterstrich: Das Paket liest das Argument mit
umgestellten Catcodes, ein escapetes `\_` wäre dort ein Risiko. Der Handle im
Fließtext braucht das Escape dagegen sehr wohl — beide müssen bei einer Änderung
angefasst werden.

Geprüft ist beides: Die kodierte Zeichenkette steht in der `.aux`, und der
gesetzte Code wurde aus dem 300-dpi-Ausdruck maschinell zurückgelesen (OpenCV) —
er ergibt exakt die obige URL.

**Lesbar aus etwa 2 bis 3 m.** Ermittelt, indem der Ausdruck stufenweise
verkleinert und wieder dekodiert wurde; ab etwa 90 px Kantenlänge im Kamerabild
bricht es ab. Die verbreitete Faustregel „lesbar aus dem Zehnfachen der
Kantenlänge" (hier also 6,6 m) ist deutlich zu optimistisch. Für einen Aushang
reicht es: Wer scannt, tritt ohnehin heran.

**Ein QR-Code kann nicht abonnieren.** Er führt aufs Profil; das Folgen ist dann
ein Tipp auf „Folgen". Das ist der beste erreichbare Weg — eine URL, die das Abo
direkt auslöst, gibt es bei Instagram nicht. Wer die App nicht hat, landet im
Browser auf derselben Profilseite.

## Drucken

Das PDF ist randlos angelegt: Die gelbe Fläche und die beiden
Gestaltungselemente laufen über den Blattrand hinaus. Ein normaler Bürodrucker
lässt ringsum einen weißen Rand stehen — das sieht ordentlich aus, ist aber nicht
die gedachte Wirkung. Für den randlosen Druck braucht die Druckerei eine Fassung
mit Beschnittzugabe; das sind drei Zeilen in der Präambel, sagt Bescheid.

Beim Vergrößern auf A3 bleibt alles proportional, der QR-Code wird dann 93 mm
groß und entsprechend weiter lesbar.

## Herkunft der Elemente

Wortmarke, Siegel und Vierblatt stammen aus dem offiziellen Vorlagen-Kit
(<https://cd.uni-freiburg.de/>) und liegen im Repo unter `static/`. Die drei
Bilddateien hier sind daraus abgeleitet und liegen mit im Repo, damit sich das
Poster ohne Python übersetzen lässt. Neu erzeugen muss man sie nur, wenn die
Quellen sich ändern — aus dem Repo-Wurzelverzeichnis:

```bash
venv/bin/python docs/poster/assets.py
```

**Siegel und Vierblatt** sind weiße Silhouetten mit Alphakanal und werden erst
eingefärbt. Das erledigt `_tint()` — dieselbe Funktion, die auch die
Instagram-Bilder einfärbt, im selben Mischungsverhältnis (Siegel 10 %, Vierblatt
20 % Blau im Gelb). So trifft das Poster den Farbton der Posts exakt, statt ihn
nachzuempfinden.

**Die Wortmarke wird zugeschnitten.** Die Datei hat rundum einen transparenten
Rand, links 6,5 % ihrer Breite. Ungeschnitten säße der sichtbare Schriftzug bei
80 mm Bildbreite 5,2 mm weiter rechts als der Institutsname darunter — die linke
Blockkante wäre sichtbar verrutscht. `render_standard()` schneidet aus genau
diesem Grund auf die Bounding-Box zu; `assets.py` tut dasselbe. Nachgemessen am
300-dpi-Ausdruck stehen Wortmarke, Institutsname und Überschrift jetzt innerhalb
eines halben Millimeters auf derselben Kante; was bleibt, ist die natürliche
Seitenlage der Buchstaben.

Das Instagram-Zeichen auf der Karte ist das Markenglyph aus `fontawesome5`, nicht
das farbige Logo von Meta. Das ist Absicht: einfarbig, im CD-Blau, und ohne eine
Markendatei ins Repo zu legen. Metas Brand-Richtlinien erlauben die Verwendung
des Glyphs zum Verweis auf den eigenen Kanal; verändert werden darf es nicht.
