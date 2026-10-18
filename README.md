# Klucz

**Eine Geschichte, die den Grundwortschatz der polnischen Alltagssprache enthält.**

_Klucz_ („Der Schlüssel“) ist das Tagebuch von Jonas, einem Deutschen, der nach Krakau zieht, weil seine polnische Großmutter ihm eine Wohnung, einen alten Schlüssel und einen rätselhaften Satz hinterlassen hat: _„Klucz otwiera to, co zamknęłam.“_ In 30 Kapiteln, von Oktober 2026 bis Oktober 2027, wächst Jonas' Polnisch mit. Die Geschichte beginnt in kurzen Präsenssätzen auf A1-Niveau und endet bei Briefen, Gerichtsverhandlungen und Erinnerungen an 1971.

Die Idee dahinter: **Wer diesen Text versteht, versteht die 3.000 häufigsten Wörter des gesprochenen Polnisch.** Diese Wörter decken gut 90 % dessen ab, was im Alltag gesagt wird. Jedes davon steht mindestens einmal im Text, und zwar nicht als Liste, sondern eingebettet in eine echte Handlung.

- **Lesen:** [index.html](index.html) – Leseseite: Wort antippen für die Übersetzung (🔊 spricht es mit der polnischen Stimme des Geräts aus), alphabetische Wortliste je Kapitel (oben „↓ Wörter“ springt hin), Kopierknöpfe für das ganze Kapitel und seine Teile
- **Buch:** [KLUCZ.md](KLUCZ.md) – das ganze Buch mit einem Glossar nach jedem Kapitel
- **Klartext:** [text/](text/) – jedes Kapitel ohne Formatierung, auch in Teilen für Google Translate
- **Messung:** [REPORT.md](REPORT.md) – Abdeckung, neue Wörter pro Kapitel, grammatische Formen
- **Bauplan:** [PLAN.md](PLAN.md) – die Planung vor dem Schreiben: Figuren, Zeitlinie, Kapitelübersicht

## So funktioniert's im Alltag

Alles, was man liest, wird aus zwei Quellen **erzeugt**. Von Hand bearbeitet werden nur diese Quellen:

| Quelle                     | Inhalt                                                                                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `chapters/01.md` … `30.md` | der Text der Geschichte                                                                                                                      |
| `data/glossary.tsv`        | die Übersetzungen, eine Zeile pro Grundform: `klucz<Tab>Schlüssel`; Eigennamen so geschrieben, wie sie angezeigt werden: `Kraków<Tab>Krakau` |

**Einmalig einrichten** (im Projektordner):

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Nach jeder Änderung** an einem Kapitel oder an einer Übersetzung:

```sh
.venv/bin/python tools/build.py
```

Das baut `index.html`, `KLUCZ.md` und `text/` neu, in wenigen Sekunden, weil nur geänderte Kapitel neu analysiert werden. Kommt ein neues Wort vor, das noch keine Übersetzung hat, meldet das Skript am Ende `… glossary entries missing`. Dann gehört eine Zeile in `data/glossary.tsv`, und man lässt das Skript noch einmal laufen.

**Woher die Grundform kommt:** Das Programm Stanza erkennt in jedem Satz automatisch, zu welcher Grundform ein Wort gehört (_Nazywam_ → _nazywać_, _poszedłem_ → _pójść_). Unter dieser Grundform steht die Übersetzung im Glossar, so wie in einem Wörterbuch.

**Offline:** `index.html` ist eine einzige, in sich geschlossene Datei: Text, Wortlisten, Übersetzungen, Schriften (Literata, Figtree) und Symbole (Material Symbols) stecken alle darin. Sie lässt sich per Doppelklick öffnen, ohne Server und ohne Internet. Die Schriften liegen als Quelle in `fonts/` und werden beim Bauen eingebettet, weil Browser Schriftdateien neben einer direkt geöffneten Datei (`file://`) nicht laden.

---

## Ergebnis

|                              |                                                                             |
| ---------------------------- | --------------------------------------------------------------------------- |
| Länge                        | ~38.500 Wörter, 30 Kapitel (bei ~100 Wörtern/Minute etwa 6–7 Stunden)       |
| Verschiedene Lemmata im Text | 4.587, dazu 172 Eigennamen (Kraków, Wisła, Kasia …)                         |
| Glossar                      | alle 4.759 Wörter übersetzt, Deutsch, mit Genus (m/f/n) und Aspekt (uv./v.) |

| Häufigste Lemmata | im Text vorhanden  | Anteil an gesprochenem Polnisch |
| ----------------- | ------------------ | ------------------------------- |
| 1–500             | 500 (100 %)        | 75,0 %                          |
| 1–1.000           | 1.000 (100 %)      | 81,6 %                          |
| 1–2.000           | 1.999 (99,9 %)     | 87,6 %                          |
| **1–3.000**       | **2.993 (99,8 %)** | **90,5 %**                      |
| 1–5.000           | 3.523 (70,5 %)     | 93,4 %                          |

Die sieben fehlenden Kernwörter sind:

- zwei bewusst ausgelassene Wörter aus dem Bereich sexuelle Gewalt,
- _Chrystus_, das als Eigenname gezählt wird,
- Fälle, die das Analysewerkzeug strukturell nicht erkennt: das Verbalsubstantiv _działanie_, die Partizipien _zabity_ und _przerażający_ sowie _dziewczę_.

Die Ränge 3.001–5.000 sind nicht vollständig enthalten, nur das, was sich natürlich ergab. Das war eine bewusste Entscheidung für einen kürzeren Text.

## Wie man das Buch liest

- **Kapitel für Kapitel, in Reihenfolge.** Die Wörter werden ungefähr nach Häufigkeit eingeführt: Kapitel 1 nutzt fast nur die häufigsten ~300.
- **Das Glossar am Kapitelende** listet alphabetisch jedes Wort, das dort zum ersten Mal vorkommt. Steht die Fundform in Klammern, ist das die Form im Text, etwa _pójść (poszedłem)_.
- **Ab Kapitel 4 schreibt Jonas in der Vergangenheit**, weil seine Lehrerin Kasia es ihm aufgibt, danach folgen Futur, Konditional und Aspekt. Die Grammatik steigt also mit der Geschichte.
- **Für Google Translate** gibt es reinen Text ohne Formatzeichen. Google Translate nimmt höchstens 5.000 Zeichen auf einmal, deshalb liegt jedes Kapitel auch in Teilen unter 4.800 Zeichen vor (`text/parts/07-1.txt` usw.). Auf der Leseseite steht oben unter der Navigation je ein Kopierknopf für „Alles“, „Teil 1“, „Teil 2“ …; ein Klick kopiert das ganze Kapitel bzw. diesen Teil.
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

- [`data/lemma_fixes.tsv`](data/lemma_fixes.tsv) (386 Einträge): Fehllemma → richtiges Lemma. Einträge mit `=` korrigieren eine einzelne, eindeutige Wortform, z. B. `=grzech → grzech`, weil Stanza _grzech_ im Kontext einmal als _gra_ las.
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

Bearbeitet werden nur die **Quellen**: `chapters/` und `data/`. Alles andere wird erzeugt und nie von Hand geändert.

```
klucz/
├── chapters/01.md … 30.md   Quelle: die Kapitel
├── index.html               erzeugt: Leseseite (Startseite für GitHub Pages)
├── .nojekyll                leer: GitHub Pages liefert die Dateien unverändert aus
├── fonts/                   Quelle: Schriften und Symbole, werden in index.html eingebettet
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
│   └── glossary.tsv         Quelle: Polnisch → Deutsch
└── tools/
    ├── build.py             baut index.html, KLUCZ.md und text/ aus den Quellen
    ├── reader.html          Vorlage der Leseseite (Aussehen, Bedienung)
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
