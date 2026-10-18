"""Build every output from chapters/*.md and data/glossary.tsv.

KLUCZ.md               the book with a glossary after each chapter
text/NN.txt, klucz.txt plain text without markup, for copying or text-to-speech
text/parts/NN-K.txt    the same, split into parts that fit Google Translate's 5,000 characters
index.html             reading page (also the GitHub Pages start page): tap a word, word lists, copy
"""

import base64
import json
import re

from analyze import EXCLUDED, GLOSSARY, ROOT, chapters, feats, first_occurrences, is_word, read_tsv, tokens, tsv

TEXT = ROOT / "text"
TEMPLATE = ROOT / "tools" / "reader.html"
FONTS = ROOT / "fonts"
PART_LIMIT = 4800
TAGS = {"Masc": "m", "Fem": "f", "Neut": "n", "Imp": "uv.", "Perf": "v."}
LETTER = re.compile(r"[^\W\d_]")
ALPHABET = "aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż"


def blocks(markdown):
    """Split a chapter into [(kind, text)]; kind is title, date, para, quote or break."""
    result = []
    for chunk in markdown.strip().split("\n\n"):
        lines = chunk.split("\n")
        if chunk.startswith("# "):
            result.append(("title", chunk[2:].strip()))
        elif chunk.strip() == "---":
            result.append(("break", ""))
        elif all(l.startswith(">") for l in lines):
            quote = "\n".join(l[1:].strip() for l in lines)  # a bare ">" line separates paragraphs
            result += [("quote", inline(q)) for q in quote.split("\n\n") if q.strip()]
        elif chunk.startswith("_") and chunk.endswith("_") and "\n" not in chunk:
            result.append(("date", inline(chunk)))
        else:
            result.append(("para", inline(chunk)))
    return result


def inline(text):
    """Drop Markdown emphasis markers."""
    return text.replace("**", "").replace("_", "").strip()


def plain(chapter_blocks):
    return "\n\n".join(t for k, t in chapter_blocks if k != "break")


def parts(chapter_blocks):
    """Group paragraphs into parts of at most PART_LIMIT characters."""
    result, current = [], ""
    for kind, text in chapter_blocks:
        if kind == "break":
            continue
        if current and len(current) + len(text) + 2 > PART_LIMIT:
            result.append(current)
            current = ""
        current = f"{current}\n\n{text}" if current else text
    return result + [current] if current else result


def polish_order(word):
    return [ALPHABET.find(c) if c in ALPHABET else len(ALPHABET) for c in word]


def word_lists(new, glossary):
    """Map chapter index -> [[lemma, display, first form, tag, German]] of the words new in it, alphabetically.

    Lemmas are lowercase; the glossary spells the word as it is displayed (Kraków, PESEL).
    """
    lists = {}
    for i, words in new.items():
        lists[i] = []
        for form, lemma, pos, f in words:
            tag = TAGS.get(feats(f).get("Gender" if pos == "NOUN" else "Aspect")) if pos in {"NOUN", "VERB"} else None
            display, de = glossary.get(lemma, (lemma, ""))
            shown = "" if form.lower() == lemma else form
            lists[i].append([lemma, display, shown, tag or "", de])
        lists[i].sort(key=lambda w: polish_order(w[0]))
    return lists


def find(text, form, pos, glued):
    """Index of form at or after pos that does not start inside another word (unless glued at pos)."""
    j = text.find(form, pos)
    while j >= 0:
        if (glued and j == pos) or j == 0 or not LETTER.match(text[j - 1]) or not LETTER.match(form[0]):
            return j
        j = text.find(form, j + 1)
    return -1


def segments(chapter_blocks, chapter_tokens, ids, excluded):
    """Mark each word of the display text with its lemma: [[kind, [text | [form, id], ...]], ...].

    Stanza splits forms such as "poszedłem" into "poszedł" + "em"; glued parts join the word before.
    A token that cannot be found in this or the next two blocks is skipped.
    """
    out, ti = [], 0
    for bi, (kind, text) in enumerate(chapter_blocks):
        segs, pos = [], 0
        while ti < len(chapter_tokens):
            form, lemma, _, _ = chapter_tokens[ti]
            glued = bool(segs) and isinstance(segs[-1], list) and bool(LETTER.match(form[:1]))
            j = find(text, form, pos, glued)
            if j < 0:
                if any(find(t, form, 0, False) >= 0 for _, t in chapter_blocks[bi + 1 : bi + 3]):
                    break
                ti += 1
                continue
            if j > pos:
                segs.append(text[pos:j])
            if glued and j == pos:
                segs[-1][0] += form
            elif is_word(chapter_tokens[ti], excluded, names=True) and lemma in ids:
                segs.append([form, ids[lemma]])
            else:
                segs.append(form)
            pos, ti = j + len(form), ti + 1
        segs.append(text[pos:])
        merged = []
        for s in segs:
            if isinstance(s, str) and merged and isinstance(merged[-1], str):
                merged[-1] += s
            elif s:
                merged.append(s)
        out.append([kind, merged])
    return out


def book(story, lists):
    out = ["# Klucz", ""]
    for i, (_, text, _) in enumerate(story):
        out += [text.strip().replace("# ", "## ", 1), "", "### Nowe słowa", ""]
        for _, display, form, tag, de in lists[i]:
            shown = f"{display} ({form})" if form else display
            out.append(f"- **{shown}**{f' _{tag}_' if tag else ''} — {de or '?'}")
        out.append("")
    (ROOT / "KLUCZ.md").write_text("\n".join(out), encoding="utf-8")


def fonts_css():
    """fonts/fonts.css with every font file embedded: browsers refuse font files next to a page opened as file://."""
    def embed(match):
        data = base64.b64encode((FONTS / match.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"

    return re.sub(r"url\(([\w.-]+\.woff2)\)", embed, (FONTS / "fonts.css").read_text(encoding="utf-8"))


def main():
    story = chapters(names=True)
    glossary = {r["lemma"].lower(): (r["lemma"], r["de"]) for r in tsv(GLOSSARY)}
    lists = word_lists(first_occurrences(story), glossary)
    book(story, lists)
    words = [w for i in sorted(lists) for w in lists[i]]
    ids = {w[0]: n for n, w in enumerate(words)}
    excluded = read_tsv(EXCLUDED)

    (TEXT / "parts").mkdir(parents=True, exist_ok=True)
    for stale in (TEXT / "parts").glob("*.txt"):  # a shortened chapter needs fewer parts
        stale.unlink()
    chapters_data, whole = [], []
    for i, (title, markdown, _) in enumerate(story):
        chapter_blocks = blocks(markdown)
        number = f"{i + 1:02d}"
        text = plain(chapter_blocks)
        whole.append(text)
        (TEXT / f"{number}.txt").write_text(text + "\n", encoding="utf-8")
        chapter_parts = parts(chapter_blocks)
        for k, part in enumerate(chapter_parts, 1):
            (TEXT / "parts" / f"{number}-{k}.txt").write_text(part + "\n", encoding="utf-8")
        chapters_data.append({
            "title": title,
            "blocks": segments(chapter_blocks, tokens(markdown), ids, excluded),
            "parts": chapter_parts,
            "words": [[ids[lemma], form] for lemma, _, form, _, _ in lists[i]],
        })
    (TEXT / "klucz.txt").write_text("\n\n\n".join(whole) + "\n", encoding="utf-8")

    data = {"chapters": chapters_data, "words": [[display, tag, de] for _, display, _, tag, de in words]}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__FONTS__", fonts_css()).replace("__DATA__", payload)
    (ROOT / "index.html").write_text(page, encoding="utf-8")

    missing = [w[1] for words in lists.values() for w in words if not w[4]]
    print(f"KLUCZ.md, text/ ({len(story)} chapters, "
          f"{sum(len(c['parts']) for c in chapters_data)} parts), "
          f"index.html ({len(page) // 1024} KB); {len(missing)} glossary entries missing")
    if missing:
        print("missing in data/glossary.tsv:", ", ".join(missing))


if __name__ == "__main__":
    main()
