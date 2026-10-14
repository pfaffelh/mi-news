# Werbemittel für den Instagram-Kanal

Aushang fürs Institut und Postkarte zum Mitnehmen: gelbe CD-Fläche, Wortmarke,
Überschrift, QR-Code zum Profil. Die Gestaltung ist dieselbe wie bei den
Instagram-Posts selbst (`misc/instagram.py`, Variante „gelb") — wer das Poster
im Flur sieht und später einen Beitrag im Feed, soll beides zusammenbringen.

| Datei | Zweck |
|---|---|
| [instagram-poster.tex](instagram-poster.tex) | Das Poster, A4 hoch |
| [instagram-poster-a3.tex](instagram-poster-a3.tex) | Dasselbe Poster auf A3, als Wrapper um das A4-PDF |
| [postkarte-a6.tex](postkarte-a6.tex) | Die Postkarte, A6 hoch, mit Anschnitt |
| [assets.py](assets.py) | Erzeugt die drei abgeleiteten Bilddateien aus `static/` |
| `ufr-blatt-gelb.png`, `ufr-siegel-gelb.png` | Vierblatt und Siegel, im Gelbton eingefärbt |
| `ufr-logo-blau-beschnitten.png` | Wortmarke ohne ihren transparenten Rand |

Poster und Postkarte sind eigenständig und teilen sich nur die Bilddateien.
**Der Handle steht in beiden** — wird er geändert, muss er an beiden Stellen
geändert werden, und in jeder Datei zweimal (Fließtext und QR-Ziel). Die
A3-Fassung ist davon ausgenommen: Sie bindet nur das fertige Poster-PDF ein und
enthält selbst keinen Text.

## Poster (A4)

### Übersetzen

```bash
lualatex instagram-poster.tex
```

**LuaLaTeX, nicht pdflatex** — `fontspec` braucht Lua- oder XeTeX. Zweimal
laufen lassen: Der QR-Code wird beim ersten Lauf berechnet und in der `.aux`
abgelegt, erst der zweite setzt ihn. Zu installieren ist nichts: Die Schrift
(Arimo, metrisch identisch zu Arial) liegt im Repo unter `static/fonts/`, die
Pakete `qrcode`, `fontawesome5` und `tikz` sind in jeder TeX-Live-Vollinstallation
enthalten.

### Sprache

Der Kanal ist deutsch, das Poster deshalb auch — **Deutsch ist der Standard.**
Für eine englische Fassung (etwa für die Master-Studiengänge) genügt Zeile 33:

```latex
\sprachedetrue      % deutsch:  "Folgt dem Mathematischen Institut auf Instagram"
\sprachedefalse     % englisch: "Follow the Mathematical Institute on Instagram"
```

Beide Fassungen sind gesetzt und geprüft.

### Wenn der Text geändert wird

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

### Der QR-Code

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

### Drucken

Das PDF ist randlos angelegt: Die gelbe Fläche und die beiden
Gestaltungselemente laufen über den Blattrand hinaus. Ein normaler Bürodrucker
lässt ringsum einen weißen Rand stehen — das sieht ordentlich aus, ist aber nicht
die gedachte Wirkung. **Beschnittzugabe hat das Poster nicht** (die Postkarte
dagegen schon, siehe unten); für den Druckereiauftrag müsste sie nachgerüstet
werden — es sind dieselben paar Zeilen wie in `postkarte-a6.tex`.

### A3

Auf A3 bleibt alles proportional, der QR-Code wird dann 93 mm groß (nachgemessen
am Ausdruck: 93,3 mm) und entsprechend weiter lesbar. A4 und A3 haben dasselbe
Seitenverhältnis; was an Verzerrung bleibt, ist die Rundung der ISO-Maße und
liegt bei 0,01 %.

**Im Druckdialog** reicht Papierformat A3 und eine Skalierung von Hand auf
**141 %** (√2, das exakte A4→A3-Verhältnis). Das ist zuverlässiger als „an Seite
anpassen": Viele Treiber rechnen dabei auf den *bedruckbaren* Bereich statt aufs
Blatt und lassen deshalb Rand stehen. Steht die Skalierung auf „tatsächliche
Größe", sitzt das Poster in A4-Größe mitten auf dem A3-Bogen — das ist kein
Fehler im Satz, sondern die Voreinstellung des Dialogs.

**Als echtes A3-PDF** gibt es [instagram-poster-a3.tex](instagram-poster-a3.tex).
Das Poster muss dafür schon gesetzt sein; der Wrapper liest nur dessen PDF ein:

```bash
lualatex instagram-poster.tex        # zweimal, wegen des QR-Codes
pdflatex instagram-poster-a3.tex
```

Ein direktes `\documentclass[a3paper]` im Poster selbst hilft **nicht**: Alle
Elemente sind absolut positioniert, in Millimetern ab den Seitenecken. Auf dem
größeren Blatt bliebe die Schrift 40 pt groß und das Layout klebte in der linken
oberen Ecke — vergrößert würde das Papier, nicht das Poster. Der Wrapper skaliert
deshalb die fertige Seite als Ganzes.

`pdfjam --paper a3paper` wäre der naheliegende Einzeiler, scheitert hier aber:
pdfjam übergibt `geometry` eine leere Papierbreite und bricht mit
`\paperwidth (0.0pt) too short` ab.

## Postkarte (A6)

```bash
lualatex postkarte-a6.tex
lualatex postkarte-a6.tex
```

Einseitig (4/0), **die Rückseite bleibt leer.** Sprache umschalten wie beim
Poster, mit `\sprachedetrue` / `\sprachedefalse`.

### Warum keine verkleinerte Fassung des Posters

A6 ist geometrisch exakt ein Viertel von A4, das Poster ließe sich also mit
Faktor 0,5 skalieren (`pdfjam --paper a6paper --scale 1.0`). Das Ergebnis wäre
sauber, aber an beiden Enden falsch gerechnet: Die Schriftgrößen des Posters
folgen der Leseentfernung im Flur (2 bis 3 m), eine Postkarte hält man in der
Hand (30 cm). Beim reinen Skalieren wäre die Überschrift unnötig groß und die
Hinweiszeile mit 7,5 pt unnötig klein.

| Element | Poster A4 | skaliert (verworfen) | Postkarte A6 |
|---|---|---|---|
| Überschrift | 40 pt, 3 Zeilen | 20 pt | **28 pt, 4 Zeilen** |
| Institutsname, Handle | 19 pt | 9,5 pt | 9,5 / 11 pt |
| Hinweiszeile | 15 pt | 7,5 pt | **9 pt** |
| Instagram-Zeichen | 34 pt | 17 pt | 20 pt |
| QR-Code | 66 mm | 33 mm | 28 mm |
| Rand | 20 mm | 10 mm | 10 mm |

Die größere Überschrift wird durch den vierzeiligen Umbruch möglich: Die längste
Zeile ist dann „Mathematischen" (77 mm bei 28 pt) statt „Mathematischen Institut"
(das wäre bei 28 pt 112 mm und liefe weit über das 85 mm breite Satzfeld).
Getrennt wird nur innerhalb von „Mathematischen Institut"; „auf Instagram"
bleibt zusammen. Nach oben begrenzt nicht die Breite, sondern die Höhe: Vier
Zeilen passen zwischen Institutsnamen und Karte bis etwa 29 pt.

Beide Sprachen stehen deshalb in 28 pt, obwohl die englische Fassung breiter
werden könnte („Mathematical" misst nur 62 mm) — sie hat rechts eben mehr Luft.
Die Zeile „Mathematisches Institut" bleibt auch in der englischen Fassung
deutsch; das ist aus dem Poster übernommen.

### Anschnitt und Endformat

Die Seite ist **111 × 154 mm**, nicht 105 × 148: Das Endformat plus 3 mm
Beschnittzugabe ringsum. Ohne sie blitzt bei der Schnitttoleranz der Druckerei
das weiße Papier am Rand durch, weil das Gelb bis an die Kante läuft. Die
`/TrimBox` ist im PDF eingetragen, die Preflight-Prüfung der Druckerei findet
das Endformat also von selbst:

```
MediaBox:   0.00   0.00  314.65  436.53     (111 × 154 mm)
TrimBox:    8.50   8.50  306.14  428.03     (105 × 148 mm)
```

Alles Inhaltliche hält 10 mm Abstand zur Endformatkante, liegt also auch bei
ungünstigem Schnitt sicher.

Für den eigenen Ausdruck zum Selberschneiden gibt es `\markentrue` in der
Präambel: Dann wird die Seite 123 × 166 mm und bekommt Schnittmarken, die 1 mm
hinter dem Anschnitt beginnen. Druckereien wollen das meist *nicht* — dort gilt
der Standard `\markenfalse`.

Eine Fußangel beim Setzen der TrimBox: `\pdfvariable pageattr` schreibt seinen
Inhalt wörtlich ins PDF, ohne Makros zu expandieren. Die Werte müssen vorher
per `\edef` ausgerechnet werden, sonst stehen die Makronamen samt geschweiften
Klammern im PDF und die Datei ist defekt.

### Der QR-Code auf der Karte

Dieselbe URL, derselbe Level Q, also derselbe Code wie auf dem Poster — nur
kleiner gesetzt. Nachgeprüft: Die 33 × 33 Module des gerasterten Ausdrucks
stimmen Modul für Modul mit denen des Posters überein, inklusive der drei
Suchmuster an den Ecken.

Bei 28 mm Kantenlänge ist ein Modul **0,85 mm** breit; als Untergrenze für
sicheres Scannen gelten 0,4 mm. Die 66 mm des Posters braucht die Karte nicht —
die hält man in der Hand, nicht im Flur. Die gewonnene Breite geht an den
Textblock links, der sonst zu eng für eine einzeilige Hinweiszeile wäre.

Der Code sitzt 3 mm von der Kartenkante entfernt, links stehen 6,5 mm. Das ist
Absicht und keine Schlamperei: Die Option `padding` gibt dem Code seine Quiet
Zone von 4 Modulen (gut 3 mm) im eigenen Kasten mit. Mit gleichen Zahlen auf
beiden Seiten sähe die Karte rechts sichtbar zu luftig aus.

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
