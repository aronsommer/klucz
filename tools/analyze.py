"""Measure the story against the frequency list.

report:  write REPORT.md (coverage, per-chapter new words, grammar forms)
missing: print target lemmas not yet in the story, up to a rank
"""

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_frequency import EXCLUDED, FIXES, LEMMA, fix, read_tsv

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "chapters"
CACHE = ROOT / ".cache"
FREQUENCY = ROOT / "data" / "frequency.tsv"
GLOSSARY = ROOT / "data" / "glossary.tsv"
LEXICAL_POS = {"NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "NUM", "ADP", "AUX",
               "CCONJ", "SCONJ", "PART", "INTJ"}
BANDS = [500, 1000, 2000, 3000, 4000, 5000]
MARKUP = re.compile(r"[_*#>]|^-{3,}$", re.M)
PIPELINE = "tokenize,mwt,pos,lemma,depparse"

nlp = None


def tsv(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))


def ranks():
    return {row["lemma"]: int(row["rank"]) for row in tsv(FREQUENCY)}


def tokens(text):
    """Return [(form, lemma, upos, feats, się)] of all of a chapter's tokens, lemmas fixed.

    się is true when the parser attaches a "się" to this word.
    Stanza output is cached by content, so only changed chapters are parsed again.
    """
    global nlp
    text = MARKUP.sub(" ", text)
    cached = CACHE / f"{hashlib.sha1((PIPELINE + text).encode()).hexdigest()}.json"
    if cached.exists():
        words = json.loads(cached.read_text())
    else:
        if nlp is None:
            import stanza

            nlp = stanza.Pipeline("pl", processors=PIPELINE, verbose=False)
        words = []
        for s in nlp(text).sentences:
            heads = {w.head for w in s.words if w.lemma == "się"}
            words += [(w.text, (w.lemma or "").lower(), w.upos, w.feats or "", w.id in heads) for w in s.words]
        CACHE.mkdir(exist_ok=True)
        cached.write_text(json.dumps(words, ensure_ascii=False))
    fixes = read_tsv(FIXES)
    return [(form, fix(fixes, lemma, form), pos, f, się) for form, lemma, pos, f, się in words]


def is_word(token, excluded, names=False):
    """A lexical word; with names, proper nouns too (but not one-letter initials)."""
    _, lemma, pos, *_ = token
    kind = pos in LEXICAL_POS or (names and pos == "PROPN" and len(lemma) > 1)
    return kind and LEMMA.match(lemma) and lemma not in excluded


def parse(text, names=False):
    """Return [(form, lemma, upos, feats, się)] of a chapter's words, optionally with proper nouns."""
    excluded = read_tsv(EXCLUDED)
    return [t for t in tokens(text) if is_word(t, excluded, names)]


def chapters(names=False):
    """Return [(title, text, words)] in file order; the title is the first line."""
    result = []
    for path in sorted(CHAPTERS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        result.append((title, text, parse(text, names)))
    return result


def first_occurrences(story):
    """Map chapter index -> [(form, lemma, upos, feats, się)] of lemmas new in that chapter."""
    seen, new = set(), defaultdict(list)
    for i, (_, _, words) in enumerate(story):
        for word in words:
            if word[1] not in seen:
                seen.add(word[1])
                new[i].append(word)
    return new


def feats(f):
    return dict(p.split("=", 1) for p in f.split("|") if "=" in p)


def report(args):
    rank = ranks()
    story = chapters()
    new = first_occurrences(story)
    counts = Counter(w[1] for _, _, words in story for w in words)
    tokens = sum(counts.values())
    out = ["# Abdeckungsbericht", ""]
    out += [f"Wörter im Text: **{tokens}** · verschiedene Lemmata: **{len(counts)}**", ""]
    out += ["## Abdeckung der Frequenzliste", "",
            "| Rang | vorhanden | fehlt | nur 1× |", "|---|---|---|---|"]
    for band in BANDS:
        target = [l for l, r in rank.items() if r <= band]
        present = [l for l in target if counts[l]]
        once = [l for l in present if counts[l] == 1]
        out.append(f"| 1–{band} | {len(present)} ({len(present) / len(target):.1%})"
                   f" | {len(target) - len(present)} | {len(once)} |")
    out += ["", "## Kapitel", "",
            "| Kapitel | Wörter | neue Lemmata | nicht in Liste | höchster Rang |",
            "|---|---|---|---|---|"]
    for i, (title, _, words) in enumerate(story):
        lemmas = [w[1] for w in new[i]]
        outside = [l for l in lemmas if l not in rank]
        top = max((rank[l] for l in lemmas if l in rank), default=0)
        out.append(f"| {title} | {len(words)} | {len(lemmas)} | {len(outside)} | {top} |")
    out += ["", "## Wörter außerhalb der Liste (Top 10.000)", ""]
    for i, (title, _, _) in enumerate(story):
        outside = [f"{l} ({f})" for f, l, *_ in new[i] if l not in rank]
        if outside:
            out.append(f"- **{title}:** {', '.join(outside)}")
    out += ["", "## Grammatische Formen", ""]
    grammar = Counter()
    for _, _, words in story:
        for _, _, pos, f, _ in words:
            f = feats(f)
            if pos in {"NOUN", "ADJ", "PRON", "DET", "NUM"} and "Case" in f:
                grammar[f"{pos} {f['Case']} {f.get('Number', '-')}"] += 1
            if pos == "VERB":
                form = f.get("VerbForm", "-")
                detail = f.get("Mood") if form == "Fin" else f.get("Tense", "")
                grammar[f"VERB {form} {detail or ''} {f.get('Aspect', '')}".strip()] += 1
            if f.get("Degree") in {"Cmp", "Sup"}:
                grammar[f"{pos} Degree={f['Degree']}"] += 1
    out += ["| Form | Anzahl |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in sorted(grammar.items())]
    (ROOT / "REPORT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:14]))


def missing(args):
    rows = tsv(FREQUENCY)
    present = {w[1] for _, _, words in chapters() for w in words}
    gaps = [r for r in rows if int(r["rank"]) <= args.upto and r["lemma"] not in present]
    for r in gaps:
        print(f"{r['rank']}\t{r['lemma']}\t{r['pos']}\t{r['forms']}")
    print(f"# {len(gaps)} missing up to rank {args.upto}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report")
    m = sub.add_parser("missing")
    m.add_argument("--upto", type=int, default=3000)
    args = parser.parse_args()
    {"report": report, "missing": missing}[args.cmd](args)
