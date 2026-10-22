# Vorlage für die Grammatikblätter

Jedes Blatt ist eine HTML-Datei, die als **genau eine A4-Seite** gedruckt wird, mit etwas Luft
unten: Ein Blatt, das nur knapp passt, kann auf einem anderen Rechner auf zwei Seiten rutschen. Alle
Blätter teilen sich `style.css` und sehen deshalb gleich aus.

Dieselben Blätter erscheinen auch auf der Leseseite: `tools/build.py` setzt sie in
`grammar.html` zusammen, im Aussehen der Leseseite statt mit `style.css`.

## Inhalt

- **Alles muss stimmen.** Nur Formen und Regeln, die sicher sind. Im Zweifel weglassen.
- Hat eine Regel Ausnahmen, steht das dabei: „meist“, „fast immer“, „oft“.
- Zielgruppe: Deutschsprachige Lernende (A1–A2). Erklärungen auf Deutsch, kurz und einfach
  („Mitlaut“ statt „Konsonant“, „Grundform“ statt „Infinitiv“).
- Alltägliche Beispielwörter mit deutscher Übersetzung. Namen: Robert, Kasia, Anna.
- Jedes Blatt funktioniert **für sich allein**: keine Verweise auf andere Blätter.

## Englische Blätter

`grammar/en/NN.html` ist dasselbe Blatt für Englischsprachige: gleicher Inhalt, nur die Erklärungen
auf Englisch, übersetzt aus dem Polnischen, nicht aus dem Deutschen.

- Einfaches britisches Englisch für A1–A2. Grammatikwörter sind im Englischen üblich und bleiben
  („ending“, „consonant“, „infinitive“, „genitive“).
- Gleiche Tags, Klassen und fett gedruckte polnische Wörter wie das deutsche Blatt: `tools/build.py`
  prüft das und bricht sonst ab. Fett gedruckte Wörter der Erklärung (kein Polnisch) bekommen
  `lang`: `<b lang="de">Endung</b>` bzw. `<b lang="en">ending</b>`; sie werden nicht verglichen.
- Nicht länger als das deutsche Blatt, damit es auf eine A4-Seite passt.
- `<html lang="en">` und `<link rel="stylesheet" href="../style.css" />`.

## Aufbau

1. `h1`: **Polnisch – Deutsch**, z. B. „Biernik – Akkusativ“. Keine Nummer im Titel.
2. `.sub`: ein Satz mit der Kernidee. Trennt das Blatt Stamm und Endung, steht hier auch die
   Legende `<span class="stem">Stamm</span> + <b lang="de">Endung</b>`.
3. Nummerierte Abschnitte: `<h2>1. Deutsch <span>· Hinweis</span></h2>`, darunter optional
   `<p class="rule">` mit der Regel in einem Satz.
4. Tabellen oder Spalten (`.cols` / `.col`).
5. Am Ende ein Kasten `.box` mit Beispielen („Beispiele“, „Merke“ …). Eine Beispieltabelle mit
   Polnisch | Deutsch bekommt `class="ex"`, dann ist das Deutsche kursiv.

## Aussehen

- Nur Schwarz und Grau, druckfreundlich.
- In Tabellen ist der Text grau. **Fett schwarz** ist das, was man lernen muss (meist die Endung):
  `czyta<b>m</b>`.
- Die erste Tabellenspalte ist die Beschriftung: kursiv, schwarz.
- Farben nur `#000`, `#8c8c8c` und `#bbb`: `tools/build.py` ersetzt sie in `grammar.html` durch
  die Farben der Leseseite (hell und dunkel).
- Alle Größen in px. Eigene Anpassungen (nur Spaltenbreiten) in einem `<style>` im Kopf des
  Blatts, nach `style.css`.

## Dateinamen und Reihenfolge

`NN.html`: die Nummer ist die Lernreihenfolge, wie bei den Kapiteln. Auf der Grammatikseite ist sie
auch die Adresse (`grammar.html#8`); wird ein Blatt eingeschoben, rücken die folgenden eine Nummer
weiter. Das PDF heißt nach Nummer und Titel, klein geschrieben, ohne Sonderzeichen (ą → a,
ł → l, ä → ae, ß → ss …), Leerzeichen und Striche als `-`: `08.html` mit „Biernik – Akkusativ“
→ `08-biernik-akkusativ.pdf`.

| Nr. | Blatt                                        | Englisch                   |
| --- | -------------------------------------------- | -------------------------- |
| 01  | Alfabet i wymowa – Alphabet und Aussprache   | Alphabet and Pronunciation |
| 02  | Rzeczowniki – Nomen                          | Nouns                      |
| 03  | Czasowniki – Verben                          | Verbs                      |
| 04  | Ważne czasowniki – Wichtige Verben           | Important Verbs            |
| 05  | Pytania i przeczenie – Fragen und Verneinung | Questions and Negation     |
| 06  | Liczebniki – Zahlen                          | Numbers                    |
| 07  | Przypadki – Fälle                            | Cases                      |
| 08  | Biernik – Akkusativ                          | Accusative                 |
| 09  | Narzędnik – Instrumental                     | Instrumental               |
| 10  | Miejscownik – Lokativ                        | Locative                   |
| 11  | Dopełniacz – Genitiv                         | Genitive                   |
| 12  | Przymiotniki – Adjektive                     | Adjectives                 |
| 13  | Zaimki osobowe – Personalpronomen            | Personal Pronouns          |
| 14  | Mój, twój, ten – mein, dein, dieser          | my, your, this             |
| 15  | Iść i jechać – gehen und fahren              | On Foot or by Vehicle      |
| 16  | Czas – Uhrzeit, Tage, Monate                 | Time, Days, Months         |
| 17  | Aspekt i przyszłość – Aspekt und Zukunft     | Aspect and Future          |
| 18  | Tryb rozkazujący – Imperativ                 | Imperative                 |
| 19  | Stopniowanie – Steigerung                    | Comparison                 |
| 20  | Tryb przypuszczający – Konditional           | Conditional                |

## PDFs erzeugen

```sh
grammar/pdf.sh de ../polski/gramatyka/de
grammar/pdf.sh en ../polski/gramatyka/en
```

Löscht zuerst die nummerierten PDFs (`NN-….pdf`) im angegebenen Ordner, damit nach einer Änderung
von Nummer oder Titel kein altes Blatt liegen bleibt. Erzeugt dann aus jeder nummerierten HTML-Datei
ein PDF dort, prüft, dass jedes genau eine Seite hat, und fügt alle in Reihenfolge zu
`gramatyka-grammatik.pdf` (Deutsch, aus `grammar/`) bzw. `gramatyka-grammar.pdf` (Englisch, aus
`grammar/en/`, dort mit `../style.css`) zusammen. Ist ein Blatt länger als eine Seite, bricht das Skript ab und
nennt es. Braucht Google Chrome und macOS.

## Gerüst für ein neues Blatt

```html
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <title>Polnisch – Deutsch</title>
    <link rel="stylesheet" href="style.css" />
  </head>
  <body>
    <div class="page">
      <h1>Polnisch – Deutsch</h1>
      <p class="sub">
        Kernidee in einem Satz · <span class="stem">Stamm</span> + <b lang="de">Endung</b>
      </p>

      <h2>1. Abschnitt <span>· Hinweis</span></h2>
      <p class="rule">Die Regel in einem Satz.</p>
      <table>
        <tr>
          <th>Person</th>
          <th>Spalte<small>Untertitel</small></th>
        </tr>
        <tr>
          <td>ja</td>
          <td>czyta<b>m</b></td>
        </tr>
      </table>

      <div class="box">
        <h3>Beispiele</h3>
        <table class="ex">
          <tr>
            <td>Czytam książkę.</td>
            <td>Ich lese ein Buch.</td>
          </tr>
        </table>
      </div>
    </div>
  </body>
</html>
```
