# Instagram-Auftritt des Mathematischen Instituts — Pflichtdokumente

Dieser Ordner enthält Entwürfe der fünf Dokumente, die die Universität Freiburg
für einen offiziellen Social-Media-Kanal einer Einrichtung verlangt. Sie müssen
**vor dem Start** des Accounts sichtbar im Instagram-Profil verlinkt sein
(in der Praxis: ein Link in der Bio auf eine Sammelseite unter
`uni-freiburg.de/math/`, die auf diese fünf Texte verweist).

| Datei | Zweck |
|---|---|
| [nutzungskonzept.md](nutzungskonzept.md) | Ziele, Zielgruppe, Inhalte, Verantwortlichkeiten, jährliche Evaluation |
| [datenschutzerklaerung.md](datenschutzerklaerung.md) | Welche Daten Meta verarbeitet, welche das Institut verarbeitet, Betroffenenrechte |
| [dsfa.md](dsfa.md) | Datenschutz-Folgenabschätzung nach Art. 35 DSGVO |
| [netiquette.md](netiquette.md) | Verhaltensregeln für Nutzer:innen |
| [disclaimer.md](disclaimer.md) | Bedeutung von Abos/Likes, Verhältnis zu Meta |
| [mail-datenschutzbeauftragter.md](mail-datenschutzbeauftragter.md) | Anfrage nach Art. 35 Abs. 2 DSGVO — abgeschickt 14.07.2026, Antwort dort eintragen |

**Veröffentlicht sind die Dokumente als Webseiten im Repo `mi-hp`**
(`templates/instagram/`, Routen in `app.py`). Live unter
<https://www.math.uni-freiburg.de/nlehre/de/instagram/> — das ist die Adresse für
die Instagram-Bio. Änderungen an den Texten müssen an beiden Orten nachgezogen
werden.

Zusätzlich Pflicht, aber kein eigenes Dokument: ein **Impressum**. Ein Link auf das
Impressum der Institutshomepage genügt — das ist
<https://uni-freiburg.de/math/impressum/>. Dort ist als Verantwortlicher bereits
**Prof. Dr. Thorsten Schmidt** eingetragen, also dieselbe Person, die für den
Instagram-Kanal die inhaltliche Verantwortung trägt. Es muss dafür nichts
geändert werden.

**Domain-Hinweis:** `www.math.uni-freiburg.de` liefert einen 301-Redirect auf
`uni-freiburg.de/math/`. Die Dokumente verwenden deshalb durchgängig die
kanonische Adresse `https://uni-freiburg.de/math/`. (Die *Mail*-Domain
`@math.uni-freiburg.de` ist davon unberührt.)

## Herkunft der Texte

Grundlage sind die veröffentlichten Originaltexte der Universität:

- Zentral: <https://uni-freiburg.de/social-media/> (Stand April 2026) — enthält
  Nutzungskonzept, Datenschutzerklärung, Disclaimer und DSFA für Instagram im Volltext.
- Rechtswissenschaftliche Fakultät: <https://www.jura.uni-freiburg.de/de/social-media/instagram>
  (Stand Juli 2023) — dasselbe Set, aber auf Ebene einer *Einrichtung* statt der
  Gesamtuniversität. Das ist die Vorlage, der wir strukturell folgen.
- Rechtsgrundlage: [Richtlinie des LfDI zur Nutzung von sozialen Netzwerken durch
  öffentliche Stellen](https://uni-freiburg.de/wp-content/uploads/Richtlinie-des-LfDI-zur-Nutzung-von-Sozialen-Netzwerken.pdf)

Gegenüber den Jura-Texten von 2023 wurden drei Dinge **bewusst korrigiert**, weil
sie inzwischen veraltet oder fehlerhaft sind:

1. „Facebook Inc." / „Facebook Ireland Ltd." → **Meta Platforms, Inc.** bzw.
   **Meta Platforms Ireland Limited** (Umbenennung 2022; die zentrale Uni-Fassung
   von April 2026 verwendet ebenfalls schon „Meta Platforms, Inc.").
2. Der Verweis auf das **EU-US Privacy Shield** ist ersatzlos gestrichen — das
   Abkommen wurde 2020 durch den EuGH (Schrems II) für ungültig erklärt. An seine
   Stelle tritt der Verweis auf den **EU-US Data Privacy Framework**
   (Angemessenheitsbeschluss der EU-Kommission vom 10. Juli 2023).
3. Die Jura-Datenschutzerklärung nennt als Kontakt für Betroffenenrechte die
   Social-Media-Mailbox der Fakultät. Zuständig ist aber der/die
   **Datenschutzbeauftragte der Universität**
   (<datenschutzbeauftragter@uni-freiburg.de>); das ist hier so eingetragen.

## Beteiligte

| Rolle | Person | Kontakt |
|---|---|---|
| Redaktionelle Betreuung | **Carolin Mann**, Assistenz Studiendekanat | persönliche Uni-Adresse (fürs Formular) |
| Inhaltliche Verantwortung | **Thorsten Schmidt**, Öffentlichkeitsbeauftragter | persönliche Uni-Adresse (fürs Formular) |
| Account-Login, öffentlicher Kontakt | — (Funktionsadresse) | <socialmedia@math.uni-freiburg.de> ✅ eingerichtet |

Die Funktionsadresse ist zugleich die E-Mail, auf der der Instagram-Account läuft,
und der öffentliche Kontakt in Datenschutzerklärung und Netiquette. Sie sollte ein
**Verteiler mit mindestens zwei Empfänger:innen** sein, damit weder
Account-Wiederherstellung noch Datenschutz-Kontakt an einer einzelnen Person hängen.

Im **Anmeldeformular** der Universität ist diese Adresse dagegen *nicht* das, was
gefragt ist: Dort werden für die betreuende und die verantwortliche Person Name,
Funktion/Abteilung, E-Mail **und Telefon** verlangt, also erreichbare Personen mit
ihren persönlichen Uni-Adressen. Eine eigene Funktionsadresse für die
Verantwortlichkeit wird nicht angelegt.

## Was noch zu tun ist

Die Dokumente sind inhaltlich vollständig — es sind keine Platzhalter mehr offen.
Für das **Anmeldeformular** der Universität werden zusätzlich noch die
Telefonnummern von Carolin Mann und Thorsten Schmidt gebraucht; die gehören aber
nicht in die Dokumente.

**Der Handle ist vorläufig auf `@math_uni_freiburg` gesetzt** — analog zum
Namensschema der Rechtswissenschaftlichen Fakultät (`@jura_uni_freiburg`). Ein
Aufruf von <https://www.instagram.com/math_uni_freiburg/> liefert Instagrams
404-Seite, der Name ist also aller Wahrscheinlichkeit nach frei. Verlässlich ist
das erst bei der Registrierung; weicht ihr auf einen anderen Handle aus, sind die
beiden Fundstellen in `nutzungskonzept.md` und `datenschutzerklaerung.md`
anzupassen.

**Entschieden: keine Kommentarfunktion.** Instagram wird als Einweg-Kanal genutzt;
Nutzungskonzept (Abschnitt 1) und DSFA (Abschnitt 2) sagen das so. Wird das später
geändert, müssen beide Dokumente angepasst werden — die DSFA stützt ihre
Risikobewertung mit auf die deaktivierten Kommentare, und es bräuchte dann eine
feste Zuständigkeit für tägliches Monitoring.

> **Achtung, das ist eine Zusage mit technischer Konsequenz.** Instagram hat
> keinen kontoweiten Schalter für Kommentare — sie lassen sich nur **pro Beitrag**
> abschalten, und per API erst *nach* dem Veröffentlichen
> (`POST /<media-id>?comment_enabled=false`). Wird das bei einem einzigen Beitrag
> vergessen, sind diese Dokumente falsch. Die Anforderungen, die daraus für die
> NEWS-App folgen, stehen in [`insta.md`](../../insta.md) unter „Kommentare müssen
> aus". Wer die Texte hier ändert, muss dort nachsehen — und umgekehrt.

**Vor der Vorlage beim Datenschutzbeauftragten bitte bestätigen:** Die
[Datenschutzerklärung](datenschutzerklaerung.md) enthält in Abschnitt 2 einen
Absatz zur **Rechtsgrundlage** (Art. 6 Abs. 1 lit. e DSGVO i. V. m. § 4 LDSG BW für
die Öffentlichkeitsarbeit, Art. 6 Abs. 1 lit. a für Personenfotos). Dieser Absatz
steht so **nicht** in den Vorlagen der Universität — er ist hier ergänzt worden,
weil Art. 13 Abs. 1 lit. c DSGVO die Angabe der Rechtsgrundlage verlangt. Fachlich
ist das die Verbesserung gegenüber der Vorlage; formal ist es eine Abweichung, die
jemand mit Datenschutz-Zuständigkeit abnicken sollte.

## Ablauf bis zum Livegang

1. Zustimmung der **Geschäftsführenden Direktion** einholen (ohne sie darf kein
   Account im Namen einer Organisationseinheit eingerichtet werden).
2. Diese fünf Dokumente finalisieren, von der Institutsleitung freigeben lassen
   und auf `uni-freiburg.de/math/` veröffentlichen.
3. Rückfrage an <socialmedia@zv.uni-freiburg.de>: Gibt es eine offizielle Vorlage,
   und genügt die Adaption der zentralen DSFA für eine Einrichtung? Ggf. den
   Datenschutzbeauftragten einbinden.
4. Account anlegen — **auf eine Funktions-Mailadresse des Instituts, nicht auf eine
   private Adresse.** Die Accounts gehören der Universität; beim Ausscheiden sind
   die Administrationsrechte an die Vorgesetzten zu übergeben.
5. [Corporate Design](https://cd.uni-freiburg.de/) beachten.
6. Account melden über das
   [Anmeldeformular](https://uni-freiburg.de/formulare/anmeldung-social-media-account/).

## Laufende Pflichten

- Regelmäßiges **Monitoring** des Kanals.
- **Jährliche Evaluation** des Nutzungskonzepts (Nutzungszahlen, Reichweiten,
  Zielgruppenstruktur). Alle fünf Dokumente tragen ein „Stand"-Datum, das dabei
  fortgeschrieben wird.
- Bei eigenen Inhalten **Urheber- und Bildrechte** beachten (Einwilligung der
  abgebildeten Personen).

---

> **Hinweis:** Das sind fachlich sorgfältig adaptierte Entwürfe, aber keine
> Rechtsberatung. Vor dem Livegang gehören sie durch die Institutsleitung und
> idealerweise durch den Datenschutzbeauftragten der Universität.

Stand: Juli 2026
