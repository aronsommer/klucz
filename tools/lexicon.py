"""Dictionary excerpts limited to the story's word forms and lemmas, and the word list entries made from them.

data/sgjp.tsv        SGJP, the Grammatical Dictionary of Polish: every analysis of each text form, and for each
                     lemma the forms a word list entry shows (Gen. Sg., Nom. Pl., 1st and 2nd person Sg.,
                     the cases after a preposition). Rows are copied unchanged: form, lemma, tag, kind, labels.
data/wiktionary.tsv  per verb: whether the Polish Wiktionary has it with się, without, or both, and its aspect
                     partners from the English Wiktionary (both via kaikki.org).

Both are made again from the full dictionaries (downloaded once into .cache/) whenever the story's forms or
lemmas change, so the build stays offline otherwise.
"""

import gzip
import hashlib
import json
import re
import urllib.request
from collections import Counter

from analyze import CACHE, ROOT, feats
from build_frequency import RAW

SGJP_URL = "https://download.sgjp.pl/morfeusz/20261018/sgjp-20261018.tab.gz"
WIKT_URL = "https://kaikki.org/dictionary/Polish/kaikki.org-dictionary-Polish.jsonl.gz"
WIKT_INFO = "https://kaikki.org/dictionary/Polish/index.html"
PLWIKT_URL = "https://kaikki.org/plwiktionary/raw-wiktextract-data.jsonl.gz"
PLWIKT_INFO = "https://kaikki.org/plwiktionary/index.html"
SGJP = ROOT / "data" / "sgjp.tsv"
WIKT = ROOT / "data" / "wiktionary.tsv"
SHOWN = re.compile(r"^(subst:sg(\.pl)?:([a-z.]*\.)?gen[:.]|subst:(sg\.)?pl:([a-z.]*\.)?nom[:.]|fin:sg:(pri|sec):|prep:)")
OLD = {"obsolete", "archaic", "dated", "dialectal", "rare"}  # senses that do not count for się
OLD_GLOSS = ("gw.", "daw.", "przest.", "reg.")  # the same, marked in the Polish Wiktionary's gloss


def base(lemma):
    """SGJP lemma without its homonym mark: "rok:Sm3~lata" -> "rok"."""
    return lemma.split(":", 1)[0]


def download(url):
    path = CACHE / url.rsplit("/", 1)[1]
    if not path.exists():
        print(f"downloading {url} …")
        CACHE.mkdir(exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def make_sgjp(forms, lemmas):
    """Copy the SGJP rows for the text forms and the shown forms of their lemmas; returns the source note."""
    hits, shown, source = [], {}, ""
    with gzip.open(download(SGJP_URL), "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#!DICT-ID"):
                source = line.split()[1]
            row = line.rstrip("\n").split("\t")
            if len(row) < 3:
                continue
            if row[0] in forms:
                hits.append(row)
            if SHOWN.match(row[2]):
                shown.setdefault(base(row[1]).lower(), []).append(row)
    needed = lemmas | {base(r[1]).lower() for r in hits}
    seen = {tuple(r) for r in hits}
    rows = hits + [r for l in sorted(needed) for r in shown.get(l, []) if tuple(r) not in seen]
    return source, rows


def verb_entries(url, verbs):
    """(verb, entry) for the Polish verb entries of a kaikki.org export whose word, without "się", is in verbs."""
    with gzip.open(download(url), "rt", encoding="utf-8") as f:
        for line in f:
            if '"pos": "verb"' not in line:
                continue
            entry = json.loads(line)
            verb = entry["word"].removesuffix(" się")
            if verb in verbs and entry.get("pos") == "verb" and entry.get("lang_code") == "pl" \
                    and "form-of" not in entry.get("tags", []):
                yield verb, entry


def current(sense):
    """A sense that is not dialectal, dated or rare."""
    glosses = sense.get("glosses") or [""]
    return glosses[0] and not OLD & set(sense.get("tags", [])) and not glosses[0].startswith(OLD_GLOSS)


def export_date(url):
    page = urllib.request.urlopen(url).read().decode()
    found = re.search(r"extracted on (\S+) from the (\w+) dump dated (\S+)", page)
    return f"{found[2]} of {found[3]}, extracted {found[1]}" if found else url


def make_wiktionary(verbs):
    """Rows [verb, się, perfective partners, imperfective partners].

    The aspect partners come from the English Wiktionary, which lists them for each verb: for each aspect, those of
    the first entry that has any (the second entry of wysłać, "to line", has other partners than "to send").
    się is "+", "-" or "+-": the Polish Wiktionary has the verb (in a current sense) with się, without, or both.
    The partners get a row too, for verbs the Polish Wiktionary lacks (it has zastanawiać się, not zastanowić się).
    """
    kinds, partners = {}, {}
    for verb, entry in verb_entries(WIKT_URL, verbs):
        found = partners.setdefault(verb, {"perfective": [], "imperfective": []})
        for aspect in found:
            if not found[aspect]:
                found[aspect] = unique(form["form"] for form in entry.get("forms", [])
                                       if aspect in form.get("tags", []) and form["form"] != verb)
    others = {p for found in partners.values() for forms in found.values() for p in forms}
    for verb, entry in verb_entries(PLWIKT_URL, verbs | others):
        if any(current(s) for s in entry.get("senses", [])):
            reflexive = entry["word"].endswith(" się") or "reflexive" in entry.get("tags", [])
            kinds.setdefault(verb, set()).add("+" if reflexive else "-")
    rows = []
    for verb in sorted(set(kinds) | set(partners)):
        found = partners.get(verb, {"perfective": [], "imperfective": []})
        rows.append([verb, "".join(sorted(kinds.get(verb, ()))), ", ".join(found["perfective"]),
                     ", ".join(found["imperfective"])])
    sources = [f"{export_date(PLWIKT_INFO)} via kaikki.org, {PLWIKT_URL}",
               f"{export_date(WIKT_INFO)} via kaikki.org, {WIKT_URL}"]
    return sources, rows


def write(path, header, rows):
    lines = [f"# {h}" for h in header] + ["\t".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read(path):
    """Header lines (without "# ") and rows of an excerpt."""
    header, rows = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            header.append(line[2:])
        else:
            rows.append(line.split("\t"))
    return header, rows


def load(words):
    """Return (sgjp rows, wiktionary rows) for the story's [(form, lemma, upos, feats, się)].

    The excerpts are made again when the forms and lemmas they were made for changed.
    """
    forms = {w[0] for w in words} | {w[0].lower() for w in words}
    lemmas = {w[1] for w in words}
    digest = hashlib.sha1("\n".join(sorted(forms) + ["", *sorted(lemmas)]).encode()).hexdigest()
    stamp = f"made for {digest}"
    if not (SGJP.exists() and WIKT.exists() and stamp in read(SGJP)[0]):
        source, rows = make_sgjp(forms, lemmas)
        write(SGJP, [f"SGJP {source}, {SGJP_URL}",
                     "Copyright © 2007–2026 Marcin Woliński, Zbigniew Bronk, Włodzimierz Gruszczyński, "
                     "Witold Kieraś, Zygmunt Saloni, Danuta Skowrońska, Robert Wołosz; "
                     "BSD license (see the downloaded file)",
                     "form, lemma, tag, kind, labels; written by tools/lexicon.py, never by hand", stamp], rows)
        verbs = {base(r[1]) for r in rows if r[2].split(":")[0] in {"fin", "inf", "praet", "impt"}}
        verbs |= {w[1] for w in words if w[2] in {"VERB", "AUX"}}
        sources, rows = make_wiktionary(verbs)
        write(WIKT, sources + ["Wiktionary, CC BY-SA 4.0",
                               "verb, się (+ with, - without, as the Polish Wiktionary has it), "
                               "perfective partners, imperfective partners (English Wiktionary); "
                               "written by tools/lexicon.py, never by hand"],
              rows)
    return read(SGJP)[1], read(WIKT)[1]


GENDERS = {"m1": "m", "m2": "m", "m3": "m", "f": "f", "n": "n"}
ASPECTS = ("imperf", "perf")
CASES = ("nom", "gen", "dat", "acc", "inst", "loc", "voc")
UNUSUAL = {  # SGJP labels of dated, rare, regional, pejorative, bookish and similar forms
    "daw.", "przest.", "rzad.", "gwar.", "reg.", "hom.", "niepopr.", "niezal.", "indyw.", "arch.", "pogard.",
    "książk.", "środ.", "slang", "żart.", "podniosłe", "przest._dziś_książk.", "daw._dziś_gwar.", "daw._dziś_fraz.",
}
CLASSES = {  # SGJP classes as Stanza's parts of speech
    "subst": "NOUN", "depr": "NOUN", "adj": "ADJ", "adja": "ADJ", "adjp": "ADJ", "adjc": "ADJ", "adv": "ADV",
    "interj": "INTJ", "part": "PART", "conj": "CCONJ", "comp": "SCONJ", "prep": "ADP", "num": "NUM", "numcomp": "NUM",
    "ppron12": "PRON", "ppron3": "PRON", "pred": "PRED",
    **dict.fromkeys(["fin", "bedzie", "praet", "impt", "imps", "inf", "pcon", "pant", "ger", "pact", "ppas", "winien"],
                    "VERB"),
}
LABELS = {  # the words of word list entries and form descriptions, per language of the page
    "de": {
        "pos": {"NOUN": "Substantiv", "PROPN": "Eigenname", "VERB": "Verb", "ADJ": "Adjektiv", "ADV": "Adverb",
                "PRON": "Pronomen", "DET": "Pronomen", "NUM": "Zahlwort", "ADP": "Präposition",
                "CCONJ": "Konjunktion", "SCONJ": "Konjunktion", "PART": "Partikel", "INTJ": "Interjektion",
                "PRED": "Prädikativ"},
        "aspect": {"imperf": "uv.", "perf": "v."},
        "case": {"nom": "Nom.", "gen": "Gen.", "dat": "Dat.", "acc": "Akk.", "inst": "Instr.", "loc": "Lok.",
                 "voc": "Vok."},
        "gen": "Gen.", "pl": "Pl.", "plural only": "nur Pl.", "indeclinable": "undeklinierbar",
        "case name": {"Nom": "Nominativ", "Gen": "Genitiv", "Dat": "Dativ", "Acc": "Akkusativ",
                      "Ins": "Instrumental", "Loc": "Lokativ", "Voc": "Vokativ"},
        "number": {"Sing": "Sg.", "Plur": "Pl.", "Ptan": "Pl."},
        "person": {"1": "1.", "2": "2.", "3": "3."},
        "tense": {"Pres": "Präsens", "Fut": "Futur", "Past": "Vergangenheit"},
        "infinitive": "Infinitiv", "converb": "Adverbialpartizip", "impersonal": "unpersönliche Form, Vergangenheit",
        "imperative": "Imperativ", "conditional": "Konditional",
        "participle": {"Act": "Partizip Aktiv", "Pass": "Partizip Passiv"}, "verbal noun": "Verbalsubstantiv",
        "degree": {"Cmp": "Komparativ", "Sup": "Superlativ"},
    },
    "en": {
        "pos": {"NOUN": "noun", "PROPN": "proper noun", "VERB": "verb", "ADJ": "adjective", "ADV": "adverb",
                "PRON": "pronoun", "DET": "pronoun", "NUM": "numeral", "ADP": "preposition",
                "CCONJ": "conjunction", "SCONJ": "conjunction", "PART": "particle", "INTJ": "interjection",
                "PRED": "predicative"},
        "aspect": {"imperf": "impf.", "perf": "pf."},
        "case": {"nom": "Nom.", "gen": "Gen.", "dat": "Dat.", "acc": "Acc.", "inst": "Inst.", "loc": "Loc.",
                 "voc": "Voc."},
        "gen": "Gen.", "pl": "Pl.", "plural only": "pl. only", "indeclinable": "indeclinable",
        "case name": {"Nom": "nominative", "Gen": "genitive", "Dat": "dative", "Acc": "accusative",
                      "Ins": "instrumental", "Loc": "locative", "Voc": "vocative"},
        "number": {"Sing": "sg.", "Plur": "pl.", "Ptan": "pl."},
        "person": {"1": "1st", "2": "2nd", "3": "3rd"},
        "tense": {"Pres": "present", "Fut": "future", "Past": "past"},
        "infinitive": "infinitive", "converb": "adverbial participle", "impersonal": "impersonal form, past",
        "imperative": "imperative", "conditional": "conditional",
        "participle": {"Act": "active participle", "Pass": "passive participle"}, "verbal noun": "verbal noun",
        "degree": {"Cmp": "comparative", "Sup": "superlative"},
    },
}
OPEN = {  # SGJP classes for Stanza's open parts of speech, best fitting first
    "NOUN": [{"subst", "depr"}, {"ger"}],
    "VERB": [{"fin", "bedzie", "praet", "impt", "imps", "inf", "pcon", "pant", "winien"}],
    "ADJ": [{"adj", "adja", "adjp", "adjc"}, {"pact", "ppas"}],
    "ADV": [{"adv"}, {"pcon", "pant"}],
}
AGREEMENT = {  # Stanza features as SGJP tag values
    "Number": {"Sing": {"sg"}, "Plur": {"pl"}, "Ptan": {"pl"}},
    "Case": {"Nom": {"nom"}, "Gen": {"gen"}, "Dat": {"dat"}, "Acc": {"acc"}, "Ins": {"inst"}, "Loc": {"loc"},
             "Voc": {"voc"}},
    "Gender": {"Masc": {"m1", "m2", "m3"}, "Fem": {"f"}, "Neut": {"n"}},
    "Aspect": {"Imp": {"imperf"}, "Perf": {"perf"}},
}


def agrees(tag, feature):
    """An SGJP tag that has every value Stanza found for the token (where the tag has that category at all)."""
    found = values(tag)
    for name, mapping in AGREEMENT.items():
        wanted = mapping.get(feature.get(name))
        if wanted and found & set().union(*mapping.values()) and not wanted & found:
            return False
    return True


def unique(items):
    return list(dict.fromkeys(items))


def values(tag):
    """All values of an SGJP tag: "subst:sg:gen.loc:f" -> {"subst", "sg", "gen", "loc", "f"}."""
    return set(tag.replace(":", ".").split("."))


def usual(row):
    """An SGJP row that is not marked dated, rare, regional or the like (subject labels such as zool. are fine)."""
    return not UNUSUAL & set(re.split(r"[,|]", row[3]))


class Dictionary:
    """Lemmas, headwords and word list entries from the SGJP and Wiktionary excerpts."""

    def __init__(self, sgjp, wiktionary):
        self.forms, self.lemmas = {}, {}  # rows (form, lemma, tag, labels) by form and by lowercase lemma
        for r in sgjp:
            row = (r[0], r[1], r[2], r[4] if len(r) > 4 else "")
            self.forms.setdefault(r[0], []).append(row)
            self.lemmas.setdefault(base(r[1]).lower(), []).append(row)
        self.wiktionary = {r[0]: r[1:] for r in wiktionary}  # verb -> (się, perfective, imperfective)
        self.counts = Counter()  # how often each word form occurs in the subtitle corpus
        with gzip.open(RAW, "rt", encoding="utf-8") as f:
            for line in f:
                _, _, form, count = line.rstrip("\n").split("\t")
                self.counts[form.lower()] += int(count)

    def common(self, rows):
        """The forms of rows for one slot (say Gen. Sg.) to show: the usual ones (or all, when every one is marked),
        and of those the ones that occur at least a tenth as often in the corpus as the most frequent one."""
        forms = unique(r[0] for r in [r for r in rows if usual(r)] or rows)
        top = max((self.counts[f.lower()] for f in forms), default=0)
        return [f for f in forms if self.counts[f.lower()] * 10 >= top]

    def analyses(self, form, proper=False):
        """SGJP rows of a text form: as written for proper nouns, lowercase for other words."""
        first, second = (form, form.lower()) if proper else (form.lower(), form)
        return self.forms.get(first) or self.forms.get(second, [])

    def lemma(self, form, lemma, upos, features):
        """Stanza's lemma, unless SGJP does not know the form under it but under exactly one other lemma.

        Only nouns, verbs, adjectives and adverbs: SGJP lacks some pronouns (sobie), and names are often foreign.
        Among SGJP's analyses, those of Stanza's part of speech count first (for nouns: real nouns before verbal
        nouns), and of those, the ones that agree with the token's case, number, gender and aspect.
        """
        if upos not in OPEN:
            return lemma
        rows = self.analyses(form)
        if lemma in {base(r[1]).lower() for r in rows}:
            return lemma
        rows = [r for r in rows if r[2] != "frag"]  # parts of fixed phrases (z dala) are no lemma to switch to
        classes = lambda tier: [r for r in rows if r[2].split(":")[0] in tier]
        fitting = next((t for t in map(classes, OPEN[upos]) if t), rows)
        agreeing = [r for r in fitting if agrees(r[2], feats(features))] or fitting
        lemmas = {base(r[1]).lower() for r in agreeing}
        return lemmas.pop() if len(lemmas) == 1 else lemma

    def rows(self, lemma, proper=False):
        """SGJP rows of a lemma: as a name (capitalized) or as a common word."""
        return [r for r in self.lemmas.get(lemma, ())
                if (base(r[1])[:1].isupper() if proper else base(r[1]) == lemma)]

    def is_verb(self, lemma):
        return any(r[2].startswith("fin:") for r in self.rows(lemma))

    def headword(self, lemma, się):
        """The lemma, with "się" when the Polish Wiktionary has the verb only with się, or both with and without
        it and the parser attached a się to it in the text.

        The verb's aspect partners count as well, as the Polish Wiktionary often has only one of a pair with
        się (zastanawiać się, not zastanowić się). For a verb it lacks entirely, the parser alone decides.
        """
        row = self.wiktionary.get(lemma, ("", "", ""))
        kinds = {k for v in [lemma, *", ".join(row[1:]).split(", ")] if v for k in self.wiktionary.get(v, ("",))[0]}
        if not kinds:
            return f"{lemma} się" if się else lemma
        return f"{lemma} się" if "+" in kinds and (się or "-" not in kinds) else lemma

    def pos(self, token):
        """Part of speech of a token, for its headword.

        Every form of a verb counts as verb (participles, verbal nouns), unless SGJP also has the lemma as a
        noun. Where Stanza guesses worst, SGJP decides: words it takes for verbs that SGJP has as no verb
        (trzeba: predicative, oto: particle), and capitalized words that are no names (Aha).
        """
        form, lemma, upos, _, _ = token
        noun = upos in {"NOUN", "PROPN"} and any(r[2].startswith("subst:") for r in self.rows(lemma))
        if self.is_verb(lemma) and not noun:
            return "VERB"
        kinds = {CLASSES.get(r[2].split(":")[0]) for r in self.analyses(form) if base(r[1]).lower() == lemma} - {None}
        if upos in {"VERB", "AUX"}:  # no verb in SGJP: wolno (man darf), to, oto
            return "PRED" if upos == "VERB" and "PRED" in kinds else kinds.pop() if len(kinds) == 1 else "PART"
        if upos == "PROPN" and len(kinds) == 1 and not any(base(r[1])[:1].isupper() for r in self.forms.get(form, ())):
            return kinds.pop()
        return upos

    def entry(self, headword, pos, token, forms, lang):
        """The grammar of a word list entry in lang's words, e.g. "f · Gen. kieszeni · Pl. kieszenie".

        token is the headword's first one in the text, forms all its forms there.
        """
        labels = LABELS[lang]
        _, lemma, upos, f, _ = token
        rows = self.rows(lemma, proper=pos == "PROPN")
        group = "NOUN" if pos == "PROPN" else pos
        # among homonyms, those of the entry's part of speech (bez: ohne, not Flieder),
        known = {r[1] for r in rows if CLASSES.get(r[2].split(":")[0]) == group} or {r[1] for r in rows}
        # of those the ones with the most of the text's forms (boleć: boli, not boleje),
        cover = Counter(i for form in forms
                        for i in {r[1] for r in self.analyses(form, upos == "PROPN") if r[1] in known})
        ids = {i for i, n in cover.items() if n == max(cover.values())} if cover else known
        # then for verbs those of the first token's aspect (stać: stoi / stanie się),
        # for nouns those of its gender and animacy (Jonas m / f)
        feature = feats(f)
        animacy = {"Hum": {"m1"}, "Nhum": {"m2"}, "Anim": {"m2"}, "Inan": {"m3"}}.get(feature.get("Animacy"),
                                                                                        {"m1", "m2", "m3"})
        wanted = {"VERB": {"Imp": {"imperf"}, "Perf": {"perf"}}.get(feature.get("Aspect")),
                  "NOUN": {"Masc": animacy, "Fem": {"f"}, "Neut": {"n"}}.get(feature.get("Gender"))}.get(group)
        if wanted:
            ids = {r[1] for r in rows if r[1] in ids and CLASSES.get(r[2].split(":")[0]) == group
                   and wanted & values(r[2])} or ids
        tagged = [(r, r[2].split(":")) for r in rows if r[1] in ids]
        if pos in {"NOUN", "PROPN"}:
            nouns = [(r, t) for r, t in tagged if t[0] == "subst"]
            if any("pt" in t[4:] for _, t in nouns):
                return labels["plural only"]
            fixed = lambda t: t[1] == "sg.pl" and len(t[2].split(".")) == len(CASES)  # one form for every case
            if nouns and all(fixed(t) for _, t in nouns):
                genders = unique(GENDERS[g] for _, t in nouns for g in t[3].split("."))
                return " · ".join(p for p in ("/".join(genders), labels["indeclinable"]) if p)
            nouns = [(r, t) for r, t in nouns if not fixed(t)]  # molo: the declined variant only
            genders = unique(GENDERS[g] for _, t in nouns for g in t[3].split("."))
            gen = self.common([r for r, t in nouns if "sg" in t[1].split(".") and "gen" in t[2].split(".")])
            plural = self.common([r for r, t in nouns if "pl" in t[1].split(".") and "nom" in t[2].split(".")])
            shown = ((labels["gen"], gen),) if pos == "PROPN" else ((labels["gen"], gen), (labels["pl"], plural))
            parts = ["/".join(genders)] + [f"{label} {' / '.join(forms)}" for label, forms in shown if forms]
            return " · ".join(p for p in parts if p)
        if pos == "VERB":
            aspects = [a for a in ASPECTS if any(CLASSES.get(t[0]) == "VERB" and a in values(r[2]) for r, t in tagged)]
            if not aspects:
                return ""
            się = " się" if headword.endswith(" się") else ""
            _, perfective, imperfective = self.wiktionary.get(lemma, ("", "", ""))
            partners = perfective if aspects == ["imperf"] else imperfective if aspects == ["perf"] else ""
            aspect = "/".join(labels["aspect"][a] for a in aspects)
            if partners:
                other = labels["aspect"]["perf" if aspects == ["imperf"] else "imperf"]
                aspect += f" ({other} {', '.join(p + się for p in partners.split(', '))})"
            persons = [self.common([r for r, t in tagged if t[:3] == ["fin", "sg", person]])
                       for person in ("pri", "sec")]
            persons = ", ".join(" / ".join(f + się for f in fs) for fs in persons if fs)
            return " · ".join(p for p in (aspect, persons) if p)
        if pos == "ADP":
            cases = {c for _, t in tagged if t[0] == "prep" for c in t[1].split(".")}
            return "+ " + ", ".join(labels["case"][c] for c in CASES if c in cases) if cases else ""
        return ""


def describe(parts, lang):
    """What form a word in the text is, in lang's words, e.g. "Genitiv Pl." or "Vergangenheit, 1. Sg. m".

    parts are its tokens: the word, then any glued on (poszedł + em, zrobił + by + m).
    """
    _, _, upos, f, _ = parts[0]
    f = feats(f)
    glued = [feats(t[3]) for t in parts[1:]]
    labels = LABELS[lang]
    number = labels["number"].get(f.get("Number"), "")
    gender = {"Masc": "m", "Fem": "f", "Neut": "n"}.get(f.get("Gender")) if f.get("Number") == "Sing" else None
    verb_form = f.get("VerbForm")
    if verb_form == "Inf":
        return labels["infinitive"]
    if verb_form == "Conv":
        return labels["converb"]
    if verb_form == "Fin":
        person = next((g["Person"] for g in glued if "Person" in g), f.get("Person"))
        if person == "0":
            return labels["impersonal"]
        if f.get("Mood") == "Imp":
            return f"{labels['imperative']}, {labels['person'][person or '2']} {number}"
        conditional = any(t[1] == "by" for t in parts[1:])
        past = conditional or f.get("Tense") == "Past"
        tense = labels["conditional"] if conditional else labels["tense"].get(f.get("Tense"), "")
        who = f"{labels['person'][person or '3']} {number}" + (f" {gender}" if past and gender else "") if number else ""
        return ", ".join(p for p in (tense, who) if p)
    out = [
        {"Part": labels["participle"]["Pass" if f.get("Voice") == "Pass" else "Act"],
         "Vnoun": labels["verbal noun"]}.get(verb_form),
        labels["degree"].get(f.get("Degree")),
    ]
    if f.get("Case"):
        shown_gender = gender if upos in {"ADJ", "DET", "NUM", "PRON"} or verb_form == "Part" else None
        out.append(f"{labels['case name'][f['Case']]} {number}".strip() + (f" {shown_gender}" if shown_gender else ""))
    return ", ".join(p for p in out if p)
