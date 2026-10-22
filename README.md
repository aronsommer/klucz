# Klucz

**Eine Geschichte, die den Grundwortschatz der polnischen Alltagssprache enthält.**

_Klucz_ („Der Schlüssel“) ist das Tagebuch von Jonas, einem Deutschen, der nach Krakau zieht, weil seine polnische Großmutter ihm eine Wohnung, einen alten Schlüssel und einen rätselhaften Satz hinterlassen hat: _„Klucz otwiera to, co zamknęłam.“_ In 30 Kapiteln, von Oktober 2026 bis Oktober 2027, wächst Jonas' Polnisch mit. Die Geschichte beginnt in kurzen Präsenssätzen auf A1-Niveau und endet bei Briefen, Gerichtsverhandlungen und Erinnerungen an 1971.

Die Idee dahinter: **Wer diesen Text versteht, versteht die 3.000 häufigsten Wörter des gesprochenen Polnisch.** Diese Wörter decken gut 90 % dessen ab, was im Alltag gesagt wird. Jedes davon steht mindestens einmal im Text, und zwar nicht als Liste, sondern eingebettet in eine echte Handlung.

- **Lesen:** [index.html](index.html) – Leseseite: Wort antippen für die Übersetzung (🔊 spricht es mit der polnischen Stimme des Geräts aus), „DE“/„PL“ oben rechts zeigt das ganze Kapitel auf Deutsch oder wieder auf Polnisch, ohne dass der Text springt, „Vorlesen“ liest das Kapitel ab dem Absatz oben auf dem Bildschirm vor und hebt den gelesenen Absatz hervor, alphabetische Wortliste je Kapitel (oben „↓ Wörter“ springt hin), Kopiermenü für das ganze Kapitel und seine Teile, Druckknopf für das ganze Buch (im Druckdialog auch als PDF speicherbar), Vollbild (nicht auf dem iPhone) und Hell/Dunkel-Umschalter (die Wahl bleibt gespeichert)
- **Grammatik:** [grammar.html](grammar.html) – die Grammatikblätter im Aussehen der Leseseite, eines nach dem anderen zum Durchblättern wie die Kapitel; erreichbar über den Knopf 🎓 oben auf der Leseseite, zurück geht es mit 📖; 🖨 druckt das offene Thema als A4-Seite wie in den PDFs. Die Quelle sind die Blätter in [grammar/](grammar/), Regeln dafür in [grammar/README.md](grammar/README.md). `grammar/pdf.sh <Ordner>` macht aus denselben Blättern A4-PDFs in diesem Ordner (im Repository liegen keine PDFs)
- **Buch:** [KLUCZ.md](KLUCZ.md) – das ganze Buch mit einem Glossar nach jedem Kapitel
- **Klartext:** [text/](text/) – jedes Kapitel ohne Formatierung, auch in Teilen für Google Translate
- **Messung:** [REPORT.md](REPORT.md) – Abdeckung, neue Wörter pro Kapitel, grammatische Formen
- **Bauplan:** [PLAN.md](PLAN.md) – die Planung vor dem Schreiben: Figuren, Zeitlinie, Kapitelübersicht

## So funktioniert's im Alltag

Alles, was man liest, wird aus drei Quellen **erzeugt**. Von Hand bearbeitet werden nur diese Quellen:

| Quelle                        | Inhalt                                                                                                                                                                                                                                                   |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `chapters/01.md` … `30.md`    | der Text der Geschichte                                                                                                                                                                                                                                  |
| `chapters/de/01.md` … `30.md` | die deutsche Übersetzung, Absatz für Absatz wie das Original; `tools/build.py` bricht ab, wenn die Absätze nicht eins zu eins übereinstimmen                                                                                                             |
| `data/glossary.tsv`           | die deutschen Bedeutungen, eine Zeile pro Eintrag der Wortliste: `klucz<Tab>Schlüssel`, `bać się<Tab>Angst haben`; nur Bedeutungen und Wendungen aus dem Text, keine Grammatik; Eigennamen so geschrieben, wie sie angezeigt werden: `Kraków<Tab>Krakau` |

**Einmalig einrichten** (im Projektordner):

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Nach jeder Änderung** an einem Kapitel, einer Übersetzung oder einem Grammatikblatt:

```sh
.venv/bin/python tools/build.py
```

Das baut `index.html`, `grammar.html`, `KLUCZ.md` und `text/` neu, in wenigen Sekunden, weil nur geänderte Kapitel neu analysiert werden. Kommt ein neues Wort vor, das noch keine Übersetzung hat, meldet das Skript am Ende `… glossary entries missing`. Dann gehört eine Zeile in `data/glossary.tsv`, und man lässt das Skript noch einmal laufen. Ebenso meldet es Zeilen im Glossar, deren Wort im Buch nicht mehr vorkommt.

Ändern sich die Wortformen im Text, schreibt das Skript die Wörterbuchauszüge `data/sgjp.tsv` und `data/wiktionary.tsv` neu (rund eine Minute). Die vollständigen Wörterbücher lädt es dafür beim ersten Mal nach `.cache/` herunter (rund 270 MB). SGJP ist auf eine feste Fassung festgelegt; die Wiktionary-Exporte von kaikki.org gibt es nur in der jeweils neuesten Fassung, deshalb können sich beim Neuschreiben einzelne _się_- oder Partnerangaben ändern. Die verwendete Fassung steht im Kopf beider Auszüge.

**Nach dem Umschreiben eines Kapitels** genügt der Build. Danach bleibt Handarbeit nur an drei Stellen: fehlende Zeilen in `data/glossary.tsv` ergänzen und nicht mehr benutzte löschen (beides meldet das Skript), und eine falsche Grundform, die keine Regel erkennt, als Formkorrektur `=form<Tab>grundform` in `data/lemma_fixes.tsv` eintragen (siehe [die Regeln](#wortliste-und-pop-up-die-regeln), Punkt 2).

**Deutsche Übersetzung:** Zu jedem Kapitel `chapters/NN.md` gehört `chapters/de/NN.md`, Absatz für Absatz. Auf der Leseseite liegen beide Fassungen eines Absatzes übereinander in derselben Fläche, deshalb springt beim Umschalten nichts. Polnisch und Deutsch lassen sich unabhängig voneinander bearbeiten; drei Sicherungen im Build sorgen dafür, dass sie zusammenpassen:

1. **Gleiche Absätze, sonst kein Build.** Beide Dateien müssen dieselben Absätze in derselben Reihenfolge und derselben Art haben (Überschrift, Datum `_…_`, Absatz, Zitat `>`, Trennstrich `---`). Absätze trennt eine Leerzeile; eine zusätzliche Leerzeile teilt also einen Absatz. Passt etwas nicht, bricht das Skript ab, bevor es irgendetwas schreibt, und zeigt die Stelle:

   ```
   chapters/de/05.md does not match chapters/05.md paragraph by paragraph (75 Polish, 76 German); nothing was built.
   paragraph 12 is the first that differs in kind; an extra or missing one can be earlier:
     pl  quote: Zupy: żurek z jajkiem, …
     de  para: Die Bar hieß „Pod Aniołem“, …
   ```

   Ein eingeschobener oder fehlender Absatz kann vor der genannten Stelle liegen, denn erst dort weicht die Art ab. Die beiden gezeigten Texte verraten meist, wie weit die Fassungen gegeneinander verrutscht sind. Ebenso bricht das Skript ab, wenn in `chapters/de/` eine Datei ohne polnisches Kapitel liegt.

2. **Veraltete Übersetzungen werden gemeldet.** `data/translation_sync.tsv` merkt sich für jeden Absatz, welche polnische und welche deutsche Fassung zuletzt zusammengehörten (als Prüfsumme). Ändert sich ein polnischer Absatz, der deutsche aber nicht, meldet das Skript ihn bei jedem Lauf, bis er erledigt ist:

   ```
   1 German paragraphs may be outdated, their Polish changed. Update them in chapters/de, or run again with --accept-german if they still fit:
     chapter 5, paragraph 6: Umówiliśmy się na drugą. Tak.
   ```

   Erledigt ist die Meldung, sobald der deutsche Absatz angepasst ist. Passt er trotz der Änderung noch (etwa nach einem korrigierten Komma im Polnischen), bestätigt `.venv/bin/python tools/build.py --accept-german` alle Absätze so, wie sie jetzt sind. Eine Änderung nur am Deutschen gilt als gewollt und wird nicht gemeldet (außer der neue Text gleicht wörtlich einem anderen deutschen Absatz desselben Kapitels, etwa „— Ja.“; dann genügt einmal `--accept-german`). `data/translation_sync.tsv` wird vom Skript geschrieben, nie von Hand, und gehört ins Repository, damit die Meldungen auch auf einem anderen Rechner stimmen.

3. **Fehlende Übersetzungen werden gemeldet.** Fehlt zu einem Kapitel die deutsche Datei, baut das Skript trotzdem, nennt das Kapitel aber am Ende; auf der Leseseite fehlt dort der Knopf „DE“.

Nicht prüfen kann das Skript, ob ein deutscher Absatz inhaltlich richtig übersetzt ist; das bleibt Sache des Lesens.

**Wortliste und Pop-up** entstehen automatisch nach festen Regeln, beschrieben im Abschnitt [Wortliste und Pop-up: die Regeln](#wortliste-und-pop-up-die-regeln).

**Offline:** `index.html` ist eine einzige, in sich geschlossene Datei: Text, Wortlisten, Übersetzungen, Schriften (Literata, Figtree) und Symbole (Material Symbols) stecken alle darin. Sie lässt sich per Doppelklick öffnen, ohne Server und ohne Internet. Die Schriften liegen als Quelle in `fonts/` und werden beim Bauen eingebettet, weil Browser Schriftdateien neben einer direkt geöffneten Datei (`file://`) nicht laden.

---

## Ergebnis

|                              |                                                                       |
| ---------------------------- | --------------------------------------------------------------------- |
| Länge                        | ~38.500 Wörter, 30 Kapitel (bei ~100 Wörtern/Minute etwa 6–7 Stunden) |
| Verschiedene Lemmata im Text | 4.585, dazu rund 170 Eigennamen (Kraków, Wisła, Kasia …)              |
| Wortliste                    | 4.788 Einträge, alle übersetzt, mit Wortart, Formen, Genus und Aspekt |

| Häufigste Lemmata | im Text vorhanden  | Anteil an gesprochenem Polnisch |
| ----------------- | ------------------ | ------------------------------- |
| 1–500             | 500 (100 %)        | 75,0 %                          |
| 1–1.000           | 999 (99,9 %)       | 81,6 %                          |
| 1–2.000           | 1.997 (99,9 %)     | 87,6 %                          |
| **1–3.000**       | **2.991 (99,7 %)** | **90,5 %**                      |
| 1–5.000           | 3.520 (70,4 %)     | 93,4 %                          |

Die neun fehlenden Kernwörter sind:

- zwei bewusst ausgelassene Wörter aus dem Bereich sexuelle Gewalt,
- _Chrystus_, das als Eigenname gezählt wird,
- Fälle, die das Analysewerkzeug strukturell nicht erkennt: das Verbalsubstantiv _działanie_, die Partizipien _zabity_ und _przerażający_ sowie _dziewczę_,
- _rola_ und _zemrzeć_, die früher nur durch Analysefehler mitgezählt wurden: _Lali wosk_ heißt „sie gossen Wachs“ (_lać_), und _zmarli_ heißt im Text „die Verstorbenen“ (_zmarły_).

Die Ränge 3.001–5.000 sind nicht vollständig enthalten, nur das, was sich natürlich ergab. Das war eine bewusste Entscheidung für einen kürzeren Text.

## Wie man das Buch liest

- **Kapitel für Kapitel, in Reihenfolge.** Die Wörter werden ungefähr nach Häufigkeit eingeführt: Kapitel 1 nutzt fast nur die häufigsten ~300.
- **Die Wortliste am Kapitelende** listet alphabetisch jedes Wort, das dort zum ersten Mal vorkommt, wie im Wörterbuch. Weicht die Form im Text ab, steht sie mit ihrer Bestimmung dabei, etwa _pójść_ · im Text: _poszedłem_ (Vergangenheit, 1. Sg. m).
- **Ab Kapitel 4 schreibt Jonas in der Vergangenheit**, weil seine Lehrerin Kasia es ihm aufgibt, danach folgen Futur, Konditional und Aspekt. Die Grammatik steigt also mit der Geschichte.
- **Für Google Translate** gibt es reinen Text ohne Formatzeichen. Google Translate nimmt höchstens 5.000 Zeichen auf einmal, deshalb liegt jedes Kapitel auch in Teilen unter 4.800 Zeichen vor (`text/parts/07-1.txt` usw.). Auf der Leseseite steht oben unter der Kapitelauswahl ein Kopierknopf; er öffnet ein Menü mit „Ganzes Kapitel“, „Teil 1“, „Teil 2“ … (bei einem Kapitel ohne Teile kopiert er es direkt).
- **Zweimal lesen lohnt sich.** Rund 1.350 Kernwörter kommen nur ein einziges Mal vor. Beim zweiten Durchgang kennt man die Handlung und achtet auf die Wörter.

---

## Die Methode

### 1. Korpus: gesprochene Sprache statt Bücher

Frequenzlisten aus Untertiteln sagen nachweislich besser voraus, welche Wörter Menschen kennen, als Listen aus Zeitungen oder Büchern (Brysbaert & New 2009, „SUBTLEX“). Als Quelle dient das polnische **OpenSubtitles-2018-Korpus** von OPUS (rund 237 Mio. Untertitelzeilen).

- Das Korpus wird gestreamt, jede 10. Zeile bleibt erhalten (23,7 Mio. Zeilen).
- Daraus werden **1,2 Mio. Zeilen zufällig** gezogen (Seed 1), damit nicht wenige Filme dominieren.
- Ergebnis: **7,36 Mio. Tokens**, davon **5,24 Mio. lexikalische** (ohne Satzzeichen und Eigennamen).

### 2. Lemmatisierung mit Stanza

Polnisch hat bis zu 14 Formen pro Substantiv und Dutzende pro Verb. Gezählt werden deshalb **Lemmata** (Wörterbuchformen), nicht Wortformen. Getestet wurden spaCy und Stanza. spaCy machte aus _poszedłem_ „poszedć być“, Stanza erkennt richtig _pójść + być_. Deshalb lemmatisiert **Stanza** sowohl das Korpus als auch die Geschichte, mit derselben Pipeline, damit beide Seiten vergleichbar sind.

### 3. Bereinigung

Automatische Lemmatisierung macht Fehler, vor allem bei Superlativen (_najmocniejszy → „macny“_), Imperativen (_wróć, złap_) und Untertiteln ohne polnische Sonderzeichen (_moze, troche_). Zwei Tabellen korrigieren das, und beide gelten **gleichermaßen für Korpus und Geschichte**:

- [`data/lemma_fixes.tsv`](data/lemma_fixes.tsv) (392 Einträge): Fehllemma → richtiges Lemma. Einträge mit `=` korrigieren eine einzelne, eindeutige Wortform, z. B. `=grzech → grzech`, weil Stanza _grzech_ im Kontext einmal als _gra_ las.
- [`data/excluded.tsv`](data/excluded.tsv) (51 Einträge): ausgeschlossen mit Begründung. Das sind englische Wörter aus Übersetzungen (_sir, lady_), Untertitel-Artefakte sowie starke Vulgärwörter und Beleidigungen (siehe unten).

Die Liste ist bewusst **nicht** von Film-Genre-Wörtern bereinigt (_kapitan, agent, planeta, wampir_). Das sind echte polnische Wörter, die man im Fernsehen ständig hört. In der Geschichte schaut der kranke Jonas Filme mit polnischen Untertiteln und schreibt sich genau diese Wörter auf.

### 4. Schreiben, messen, nachschärfen

1. **Bauplan:** Tagebuchform, Figuren, ein Familiengeheimnis aus dem Jahr 1971, eine Zeitlinie über alle Jahreszeiten und Feste. Auf diese Weise kommen viele Lebensbereiche ganz natürlich vor: Behörden, Arzt, Polizei, Gericht, Berge, Meer, Wigilia, Ostern.
2. **Natürlich geschrieben** deckten die ersten 25.000 Wörter nur **53 %** der Top 3.000 ab. Freies Erzählen wiederholt immer wieder dieselben Wörter.
3. **Gezielte Runden:** `analyze.py missing` listet die fehlenden Lemmata. Daraus entstehen Passagen, die thematisch in Szenen passen, etwa Radionachrichten, die Korrektur von Jonas' Tagebuch durch Kasia, eine Lektion über Präfixverben oder die Urteilsbegründung im Gericht. Nach jeder Runde wird neu gemessen. Am effizientesten waren Dialoge, die 3–6 fehlende Wörter pro Satz tragen.
4. **Prüfung:** Unabhängige Korrekturdurchgänge (Grammatik, Idiomatik, Fakten, Kontinuität) haben rund 180 Stellen korrigiert. Darunter sind Fakten wie die Zeugenformel nach Art. 266 k.p.c., die Zuständigkeit des _Sąd Rejonowy_ in Erbsachen, die Altstadtverteidigung 1944 oder die Messe von Johannes Paul II. in Nowy Targ 1979.

### 5. Grenzen

- **Text und Glossar wurden von einer KI geschrieben und von KI geprüft.** Sie sind sorgfältig korrigiert, aber nicht von Muttersprachlern lektoriert. Ein Lektorat durch eine polnische Muttersprachlerin wäre der nächste sinnvolle Schritt.
- **Aspektpaare zählen als zwei Wörter** (_robić/zrobić_). Das entspricht der Lemmatisierung, und man muss ohnehin beide kennen.
- **Verbalsubstantive auf _-nie_ und Partizipien** ordnet Stanza teils dem Verb zu. Einzelne Wörter fallen dadurch durchs Raster, in beide Richtungen.
- **Untertitel-Bias:** Untertitel sind oft aus dem Englischen übersetzt, daher gibt es mehr _agent_ und _szeryf_ als im echten Krakauer Alltag.
- **Die Adresse ul. Lipowa 7 auf dem Kazimierz ist fiktiv.** Die reale ul. Lipowa liegt in Zabłocie, dort steht Schindlers Fabrik.

## Wortliste und Pop-up: die Regeln

Jeder Eintrag entsteht beim Bauen automatisch, nach denselben Regeln für alle Wörter. Die Quellen:

| Angabe                                                           | Quelle                                                                                                                                 |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Grundform (Vorschlag), Wortart, Bestimmung der Form im Satz      | Stanza, die Satzanalyse                                                                                                                |
| Prüfung der Grundform; Genus, Formen, Aspekt, Kasus nach Präpos. | [SGJP](https://sgjp.pl), _Słownik gramatyczny języka polskiego_, das grammatische Wörterbuch des Polnischen; Auszug in `data/sgjp.tsv` |
| ob ein Verb mit _się_ steht                                      | das polnische [Wiktionary](https://pl.wiktionary.org); Auszug in `data/wiktionary.tsv`                                                 |
| Aspektpartner                                                    | das englische [Wiktionary](https://en.wiktionary.org), das sie für jedes polnische Verb nennt; Auszug in `data/wiktionary.tsv`         |
| welche von zwei Formen üblich ist                                | die Untertitel-Zählung, `data/raw_counts.tsv.gz`                                                                                       |
| deutsche Bedeutung                                               | `data/glossary.tsv`                                                                                                                    |

1. **Ein Eintrag pro Wort**, in dem Kapitel, in dem es zum ersten Mal vorkommt, alphabetisch.
2. **Grundform.** Stanza schlägt sie vor. Kennt SGJP die Form im Text nicht unter dieser Grundform, aber unter genau einer anderen, gilt diese (_lotnisk_ → _lotnisko_). Passen mehrere, entscheiden Wortart, Kasus, Zahl, Genus und Aspekt aus dem Satz (_sera_ → _ser_, nicht _serum_). Das gilt für Substantive, Verben, Adjektive und Adverbien, nie für Eigennamen. Was keine Regel lösen kann, steht als Formkorrektur in `data/lemma_fixes.tsv`.
3. **_się_.** Kennt das polnische Wiktionary ein Verb (oder seinen Aspektpartner) nur mit _się_, steht es immer mit _się_ (_uśmiechać się_). Kennt es beides (_uczyć_ / _uczyć się_), steht _się_ dort, wo die Satzanalyse ein _się_ zu diesem Verb stellt. Das ergibt dann zwei Einträge mit eigener Bedeutung. Fehlen Verb und Partner im Wiktionary, entscheidet die Satzanalyse allein.
4. **Wortart:** die häufigste im Buch. Alle Formen eines Verbs zählen zum Verb, auch Partizipien und Verbalsubstantive, außer SGJP führt das Wort als eigenes Substantiv. Hält Stanza ein Wort für ein Verb, das SGJP nicht als Verb kennt, entscheidet SGJP (_trzeba_: Prädikativ, _oto_: Partikel), ebenso bei großgeschriebenen Wörtern, die kein Name sind (_Aha_: Interjektion).
5. **Angaben je Wortart**, aus SGJP:
   - Substantiv: Genus (m/f/n) · Gen. Sg. · Nom. Pl.; „nur Pl.“ bei Wörtern ohne Singular, „undeklinierbar“ bei Wörtern ohne Endungen
   - Eigenname: Genus · Gen. Sg.
   - Verb: Aspekt (uv. unvollendet, v. vollendet), in Klammern der Aspektpartner · 1. und 2. Person Sg. (bei vollendeten Verben sind das Futurformen)
   - Präposition: der Kasus danach (_z_ + Gen., Instr.)
   - alle anderen Wortarten: nur die Wortart

   Hat SGJP mehrere gleich geschriebene Wörter, gilt das der passenden Wortart (_bez_ „ohne“, nicht „Flieder“), dann das mit den meisten Formen aus dem Text (_boleć_: _boli_, nicht _boleje_), dann das mit dem Aspekt bzw. Genus aus dem Satz. Kennt SGJP ein Wort nicht, bleibt die Angabe leer. Hat eine Angabe mehrere Formen, fallen die von SGJP als veraltet, selten, regional, abwertend oder gehoben markierten weg, sofern es eine unmarkierte gibt. Von den übrigen erscheint jede, die in den Untertiteln mindestens ein Zehntel so oft vorkommt wie die häufigste (_dyrektorzy / dyrektorowie_).

6. **Form im Text.** Weicht die Form an der ersten Fundstelle von der Grundform ab, steht sie in der Wortliste darunter, kleingeschrieben außer bei Eigennamen, mit ihrer Bestimmung aus der Satzanalyse, falls es eine gibt: _im Text: lat (Genitiv Pl.)_.
7. **Pop-up:** derselbe Eintrag, darüber die angetippte Form mit ihrer Bestimmung, wenn sie nicht die Grundform ist. 🔊 spricht die angetippte Form.
8. **Bedeutung:** aus `data/glossary.tsv`, nur deutsche Bedeutungen und Wendungen aus dem Text (_w domu – zu Hause_).

**Überprüfbar:** Jede grammatische Angabe steht wörtlich in den Auszügen in `data/` (mit Version und Quelle im Dateikopf) und lässt sich auf [sgjp.pl](https://sgjp.pl) oder im Wiktionary nachschlagen.

**Grenzen:**

- Unpersönliches _się_ (_gotuje się jajka_ – „man kocht die Eier“) unterscheidet die Satzanalyse nicht vom _się_ eines Verbs. Gibt es das Verb auch mit _się_, landet die Stelle dort (_gotować się_). Das Glossar nennt dann die Wendung aus dem Text.
- Fehler der Satzanalyse bei Wortart oder Bestimmung bleiben bestehen, wenn kein Wörterbuch sie aufdeckt (_zmarli_ „die Verstorbenen“ als Verbform bestimmt).
- Gleich geschriebene Wörter verschiedener Wortart teilen sich einen Eintrag (_piec_ – Ofen; backen).

## Bewusst ausgelassen: starke Vulgärwörter

Sie gehören zur gesprochenen Sprache, _kurwa_ stünde in der Liste etwa auf Rang 234. In einem Lesebuch haben sie aber nichts verloren. Damit man sie trotzdem versteht:

| Wort                            | Bedeutung                                                                   |
| ------------------------------- | --------------------------------------------------------------------------- |
| _kurwa_ (_kurwa mać_)           | wörtlich „Hure“; das universelle Fluchwort, etwa wie „Scheiße!“, „verdammt“ |
| _pierdolić, pierdolony_         | ficken; verdammt, scheiß-                                                   |
| _jebać, jebany_                 | ficken; verfickt                                                            |
| _chuj, kutas, fiut_             | Schwanz; als Schimpfwort „Arschloch“                                        |
| _skurwiel, skurwysyn, sukinsyn_ | Hurensohn, Mistkerl                                                         |
| _dziwka, suka_                  | Hure; Schlampe (_suka_ auch: Hündin)                                        |
| _cipa, cipka, cycek_            | vulgär für weibliche Geschlechtsteile bzw. Brust                            |
| _spierdalać, wypierdalać_       | verpiss dich                                                                |
| _zajebisty, zajebiście_         | (vulgär) geil, verdammt gut                                                 |
| _kurewsko_                      | verdammt (sehr)                                                             |
| _srać, zasrać_                  | scheißen, vollscheißen                                                      |
| _bzykać_                        | bumsen                                                                      |

Ebenfalls ausgeschlossen sind zwei herabwürdigende Bezeichnungen (_czarnuch, ciota_). Milde Flüche wie _cholera, kurczę, do diabła, dupa, tyłek, gówno_ sind dagegen im Text enthalten.

---

## Dateien

Bearbeitet werden nur die **Quellen**: `chapters/`, `data/` und `grammar/`. Alles andere wird erzeugt und nie von Hand geändert.

```
klucz/
├── chapters/01.md … 30.md   Quelle: die Kapitel
├── chapters/de/01.md … 30.md Quelle: die deutsche Übersetzung, Absatz für Absatz
├── index.html               erzeugt: Leseseite (Startseite für GitHub Pages)
├── grammar.html             erzeugt: Grammatikseite
├── grammar/                 Quelle: Grammatikblätter (je eine A4-Seite), style.css fürs Drucken, pdf.sh, README.md
├── .nojekyll                leer: GitHub Pages liefert die Dateien unverändert aus
├── fonts/                   Quelle: Schriften und Symbole, werden in index.html und grammar.html eingebettet
├── KLUCZ.md                 erzeugt: Gesamtbuch mit Glossaren
├── text/01.txt … 30.txt     erzeugt: Klartext je Kapitel, klucz.txt: das ganze Buch
├── text/parts/07-1.txt …    erzeugt: Klartext in Teilen bis 4.800 Zeichen
├── REPORT.md                erzeugt: Abdeckungsbericht
├── PLAN.md                  Bauplan
├── data/
│   ├── frequency.tsv        Top-10.000-Lemmata: Rang, Wortart, Anzahl, pro Million, kumulierte Abdeckung, häufigste Formen
│   ├── raw_counts.tsv.gz    Rohzählung (Lemma, Wortart, Form, Anzahl) aus dem Korpus
│   ├── lemma_fixes.tsv      Korrekturen der Lemmatisierung
│   ├── excluded.tsv         Ausschlüsse mit Begründung
│   ├── glossary.tsv         Quelle: Polnisch → Deutsch
│   ├── sgjp.tsv             erzeugt: Auszug aus SGJP (Formen, Genus, Aspekt) für die Wörter im Text
│   ├── wiktionary.tsv       erzeugt: Auszug aus Wiktionary (się, Aspektpartner) für die Verben im Text
│   └── translation_sync.tsv erzeugt: welche polnischen und deutschen Absätze zuletzt zusammenpassten
└── tools/
    ├── build.py             baut index.html, grammar.html, KLUCZ.md und text/ aus den Quellen
    ├── base.css             Farben, Schriften und Leiste beider Seiten
    ├── reader.html          Vorlage der Leseseite (Aussehen, Bedienung)
    ├── grammar.html         Vorlage der Grammatikseite
    ├── lexicon.py           Wörterbuchauszüge und daraus die Einträge der Wortliste
    ├── analyze.py           misst die Geschichte: report, missing
    └── build_frequency.py   Korpus → Frequenzliste
```

## PDF und GitHub Pages

**PDF:** `index.html` im Browser öffnen, das gewünschte Kapitel wählen, Strg/⌘ + P drücken und „Als PDF sichern“ wählen. Gedruckt werden Kapiteltext und Wortliste, ohne Bedienelemente.

**GitHub Pages:** In den Repository-Einstellungen unter _Pages_ als Quelle den Branch `main` und den Ordner `/ (root)` wählen. Die Leseseite liegt dann unter `https://<benutzername>.github.io/klucz/`.

## Reproduzieren

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Korpus streamen (1,9 GB gzip), jede 10. Zeile behalten
curl -s https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/pl.txt.gz \
  | gunzip -c | awk 'NR%10==0' > subs_sample.txt

# Zufallsstichprobe lemmatisieren (gut eine Stunde auf 8 Kernen) und Liste bauen
.venv/bin/python tools/build_frequency.py count subs_sample.txt --lines 1200000
.venv/bin/python tools/build_frequency.py list

# Geschichte messen und alles bauen
.venv/bin/python tools/analyze.py missing --upto 3000
.venv/bin/python tools/analyze.py report
.venv/bin/python tools/build.py
```

`list`, `report`, `missing` und `build.py` laufen auch ohne Korpus, weil `raw_counts.tsv.gz` mitgeliefert wird. Stanza lädt sein polnisches Modell beim ersten Aufruf selbst herunter. Die Analyse der Kapitel wird in `.cache/` zwischengespeichert, sodass nur geänderte Kapitel neu lemmatisiert werden.

## Quellen

- P. Lison, J. Tiedemann, M. Kouylekov (2018): _OpenSubtitles2018: Statistical Rescoring of Sentence Alignments in Large, Noisy Parallel Corpora._ LREC 2018. Daten über [OPUS](https://opus.nlpl.eu/).
- P. Qi, Y. Zhang, Y. Zhang, J. Bolton, C. D. Manning (2020): _Stanza: A Python Natural Language Processing Toolkit for Many Human Languages._ ACL 2020 (System Demonstrations).
- M. Brysbaert, B. New (2009): _Moving beyond Kučera and Francis._ Behavior Research Methods 41(4). (SUBTLEX: Untertitel-Frequenzen)
- I. S. P. Nation (2006): _How large a vocabulary is needed for reading and listening?_ Canadian Modern Language Review 63(1).
- Schriften: [Literata](https://fonts.google.com/specimen/Literata) und [Figtree](https://fonts.google.com/specimen/Figtree) (SIL Open Font License), [Material Symbols](https://fonts.google.com/icons) (Apache 2.0), lokal in `fonts/`.
