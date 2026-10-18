"""Build a Polish lemma frequency list from a subtitle corpus.

count: lemmatize a random sample of corpus lines with Stanza -> raw counts
list:  filter raw counts into the ranked lemma list used by analyze.py
"""

import argparse
import csv
import gzip
import random
import re
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "raw_counts.tsv.gz"
LIST = DATA / "frequency.tsv"
EXCLUDED = DATA / "excluded.tsv"
FIXES = DATA / "lemma_fixes.tsv"

TAG = re.compile(r"<[^>]*>|\{[^}]*\}|\[[^\]]*\]")
LEMMA = re.compile(r"^[a-ząćęłńóśźż]+$")
SKIP_POS = {"PUNCT", "SYM", "X", "PROPN"}

nlp = None


def read_tsv(path):
    """Return {first column: second column} of a TSV file, skipping # comments."""
    if not path.exists():
        return {}
    rows = csv.reader(open(path, encoding="utf-8"), delimiter="\t")
    return {r[0]: r[1] if len(r) > 1 else "" for r in rows if r and not r[0].startswith("#")}


def fix(fixes, lemma, form):
    """Correct a Stanza lemma: by exact form ("=form" keys) first, then by lemma."""
    return fixes.get("=" + form.lower(), fixes.get(lemma, lemma))


def clean(line):
    line = TAG.sub(" ", line).replace("/", " ").strip(" -–—\t")
    return " ".join(line.split())


def init_worker(threads):
    global nlp
    import stanza
    import torch

    torch.set_num_threads(threads)
    nlp = stanza.Pipeline(
        "pl",
        processors="tokenize,mwt,pos,lemma",
        tokenize_no_ssplit=True,
        verbose=False,
    )


def count_chunk(lines):
    counts = Counter()
    doc = nlp("\n\n".join(lines))
    for sentence in doc.sentences:
        for word in sentence.words:
            counts[(word.lemma or "").lower(), word.upos, word.text.lower()] += 1
    return counts


def count(args):
    lines = [clean(l) for l in open(args.corpus, encoding="utf-8")]
    lines = [l for l in lines if l and re.search(r"[a-ząćęłńóśźż]", l, re.I)]
    random.Random(args.seed).shuffle(lines)
    lines = lines[: args.lines]
    chunks = [lines[i : i + 500] for i in range(0, len(lines), 500)]
    total = Counter()
    with Pool(args.workers, init_worker, (args.threads,)) as pool:
        for i, counts in enumerate(pool.imap_unordered(count_chunk, chunks), 1):
            total.update(counts)
            if i % 50 == 0:
                print(f"{i}/{len(chunks)} chunks", flush=True)
    DATA.mkdir(exist_ok=True)
    with gzip.open(RAW, "wt", encoding="utf-8") as f:
        for (lemma, pos, form), n in total.most_common():
            f.write(f"{lemma}\t{pos}\t{form}\t{n}\n")
    print(f"{len(lines)} lines, {sum(total.values())} tokens -> {RAW}")


def build_list(args):
    excluded, fixes = read_tsv(EXCLUDED), read_tsv(FIXES)
    lemmas = Counter()
    pos_by_lemma = defaultdict(Counter)
    forms = defaultdict(Counter)
    lexical = 0
    for line in gzip.open(RAW, "rt", encoding="utf-8"):
        lemma, pos, form, n = line.rstrip("\n").split("\t")
        n, lemma = int(n), fix(fixes, lemma, form)
        if pos in SKIP_POS or (pos == "NUM" and not LEMMA.match(lemma)):
            continue
        lexical += n
        if not LEMMA.match(lemma) or lemma in excluded:
            continue
        lemmas[lemma] += n
        pos_by_lemma[lemma][pos] += n
        forms[lemma][form] += n
    cumulative = 0
    with open(LIST, "w", encoding="utf-8") as f:
        f.write("rank\tlemma\tpos\tcount\tper_million\tcoverage\tforms\n")
        for rank, (lemma, n) in enumerate(lemmas.most_common(args.top), 1):
            cumulative += n
            top_forms = ",".join(w for w, _ in forms[lemma].most_common(5))
            f.write(
                f"{rank}\t{lemma}\t{pos_by_lemma[lemma].most_common(1)[0][0]}\t{n}"
                f"\t{n / lexical * 1e6:.1f}\t{cumulative / lexical * 100:.2f}\t{top_forms}\n"
            )
    print(f"{lexical} lexical tokens, top {args.top} -> {LIST}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count")
    c.add_argument("corpus")
    c.add_argument("--lines", type=int, default=1_000_000)
    c.add_argument("--seed", type=int, default=1)
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--threads", type=int, default=2)
    l = sub.add_parser("list")
    l.add_argument("--top", type=int, default=10_000)
    args = parser.parse_args()
    count(args) if args.cmd == "count" else build_list(args)
