# Instagram-Auftritt des Mathematischen Instituts — Pflichtdokumente

Dieser Ordner enthält Entwürfe der fünf Dokumente, die die Universität Freiburg
für einen offiziellen Social-Media-Kanal einer Einrichtung verlangt. Sie müssen
**vor dem Start** des Accounts sichtbar im Instagram-Profil verlinkt sein
(in der Praxis: ein Link in der Bio auf eine Sammelseite unter
`math.uni-freiburg.de`, die auf diese fünf Texte verweist).

| Datei | Zweck |
|---|---|
| [nutzungskonzept.md](nutzungskonzept.md) | Ziele, Zielgruppe, Inhalte, Verantwortlichkeiten, jährliche Evaluation |
| [datenschutzerklaerung.md](datenschutzerklaerung.md) | Welche Daten Meta verarbeitet, welche das Institut verarbeitet, Betroffenenrechte |
| [dsfa.md](dsfa.md) | Datenschutz-Folgenabschätzung nach Art. 35 DSGVO |
| [netiquette.md](netiquette.md) | Verhaltensregeln für Nutzer:innen |
| [disclaimer.md](disclaimer.md) | Bedeutung von Abos/Likes, Verhältnis zu Meta |

Zusätzlich Pflicht, aber kein eigenes Dokument: ein **Impressum**. Ein Link auf
das Impressum der Institutshomepage genügt.

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

## Was noch zu tun ist

**Platzhalter ausfüllen.** Alle offenen Stellen sind mit `«…»` markiert:

```
grep -rn '«' docs/social-media/
```

Offen sind noch die redaktionell betreuende Person, die verantwortliche Person
und die Postingfrequenz.

Als Funktionsadresse ist **socialmedia@math.uni-freiburg.de** eingetragen — sie
ist zugleich die E-Mail, auf der der Instagram-Account läuft, und der öffentliche
Kontakt in Datenschutzerklärung und Netiquette. Sie sollte ein **Verteiler mit
mindestens zwei Empfänger:innen** sein, damit weder Account-Wiederherstellung noch
Datenschutz-Kontakt an einer einzelnen Person hängen.

Im **Anmeldeformular** der Universität ist diese Adresse dagegen *nicht* das, was
gefragt ist: Dort werden für die betreuende und die verantwortliche Person Name,
Funktion, E-Mail **und Telefon** verlangt, also erreichbare Personen. Betreuende
Person = die Person, die tatsächlich postet, mit ihrer persönlichen Uni-Adresse;
verantwortliche Person = Geschäftsführende Direktion mit der bestehenden
Direktionsadresse. Eine eigene Funktionsadresse für die Verantwortlichkeit wird
nicht angelegt.

**Der Handle ist vorläufig auf `@math_uni_freiburg` gesetzt** — analog zum
Namensschema der Rechtswissenschaftlichen Fakultät (`@jura_uni_freiburg`). Vor
der Anmeldung ist zu prüfen, ob er auf Instagram noch frei ist; andernfalls sind
die beiden Fundstellen in `nutzungskonzept.md` und `datenschutzerklaerung.md`
anzupassen.

**Eine inhaltliche Entscheidung ist noch offen: Kommentarfunktion.**
Die Entwürfe gehen — wie bei der Rechtswissenschaftlichen Fakultät — davon aus,
dass die **Kommentarfunktion deaktiviert** ist und Instagram als Einweg-Kanal
genutzt wird. Das senkt den Monitoring-Aufwand und das Risiko in der DSFA
spürbar. Wollt ihr Kommentare zulassen, müssen Nutzungskonzept und DSFA an den
markierten Stellen angepasst werden; die Netiquette wird dann deutlich wichtiger,
und ihr braucht eine feste Zuständigkeit für tägliches Monitoring (die Uni
verlangt „regelmäßiges Monitoring", um Rechtsverstöße zeitnah zu bemerken).

## Ablauf bis zum Livegang

1. Zustimmung der **Geschäftsführenden Direktion** einholen (ohne sie darf kein
   Account im Namen einer Organisationseinheit eingerichtet werden).
2. Diese fünf Dokumente finalisieren, von der Institutsleitung freigeben lassen
   und auf `math.uni-freiburg.de` veröffentlichen.
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
