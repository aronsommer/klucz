"""Build every output from chapters/*.md, data/glossary.tsv and the dictionary excerpts (tools/lexicon.py).

KLUCZ.md               the book with a glossary after each chapter
text/NN.txt, klucz.txt plain text without markup, for copying or text-to-speech
text/parts/NN-K.txt    the same, split into parts that fit Google Translate's 5,000 characters
index.html             reading page (also the GitHub Pages start page) in German and English: tap a word, word
                       lists, copy, and the translation from chapters/<lang>/NN.md where one exists
grammar.html           every grammar sheet from grammar/NN.html (German) and grammar/en/NN.html (English) in the
                       reading page's look

Run with --accept-de or --accept-en to confirm that every paragraph of that translation still fits its Polish one.
"""

import base64
import hashlib
import json
import re
import sys
from collections import Counter
from urllib.parse import quote

from analyze import EXCLUDED, GLOSSARY, ROOT, chapters, is_word, read_tsv, tokens, tsv
from lexicon import LABELS, Dictionary, describe, load

LANGS = ("de", "en")  # the languages of the pages; the first is the one KLUCZ.md and the grammar sheets start from
NAMES = {"de": "German", "en": "English"}
TEXT = ROOT / "text"
SYNC = ROOT / "data" / "translation_sync.tsv"
TEMPLATE = ROOT / "tools" / "reader.html"
GRAMMAR_TEMPLATE = ROOT / "tools" / "grammar.html"
BASE = ROOT / "tools" / "base.css"
BAR = ROOT / "tools" / "bar.js"
LANG_JS = ROOT / "tools" / "lang.js"
FOCUS = ROOT / "tools" / "focus.js"
UI = ROOT / "tools" / "ui.tsv"
GRAMMAR = ROOT / "grammar"
FONTS = ROOT / "fonts"
ICON = FONTS / "key.svg"  # the tab icon of both pages
PRINT_COLORS = {"#000": "var(--text)", "#8c8c8c": "var(--text-2)", "#bbb": "var(--line)"}
PART_LIMIT = 4800
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


def entries(marked, dictionary, glossary):
    """Word list entries, and what each marked word in the text is.

    marked holds each chapter's segments from segments(). Returns (words, lists, found):
    words    {headword: [display, {lang: [part of speech, grammar, meaning]}]}, headwords lowercase
    lists    chapter index -> [(headword, form in the text, its description)] of the words new in it,
             alphabetically; form is empty and description None when the form is the lemma
    found    {id(segment): (headword, description or None)} for every marked word
    A description is {lang: what form the word is}.
    """
    first, kinds, forms, found = {}, {}, {}, {}
    for i, chapter in enumerate(marked):
        for _, segs in chapter:
            for seg in segs:
                if isinstance(seg, str):
                    continue
                surface, parts = seg
                form, lemma, upos, f, się = parts[0]
                lemma = dictionary.lemma(form, lemma, upos, f)
                headword = dictionary.headword(lemma, się and upos == "VERB")
                kinds.setdefault(headword, Counter())[dictionary.pos((form, lemma, upos, f, się))] += 1
                forms.setdefault(headword, set()).add(form)
                text = (surface if upos == "PROPN" else surface.lower()) if surface.lower() != lemma else ""
                description = {lang: describe(parts, lang) for lang in LANGS} if text else None
                found[id(seg)] = (headword, description)
                first.setdefault(headword, (i, text, description, (form, lemma, upos, f, się)))
    words, lists = {}, {}
    for headword, (i, text, description, token) in first.items():
        pos = kinds[headword].most_common(1)[0][0]
        display, meanings = glossary.get(headword, (headword, {}))
        words[headword] = [display, {lang: [LABELS[lang]["pos"].get(pos, ""),
                                            dictionary.entry(headword, pos, token, forms[headword], lang),
                                            meanings.get(lang, "")] for lang in LANGS}]
        lists.setdefault(i, []).append((headword, text, description))
    for i in lists:
        lists[i].sort(key=lambda w: polish_order(w[0]))
    return words, lists, found


def find(text, form, pos, glued):
    """Index of form at or after pos that does not start inside another word (unless glued at pos)."""
    j = text.find(form, pos)
    while j >= 0:
        if (glued and j == pos) or j == 0 or not LETTER.match(text[j - 1]) or not LETTER.match(form[0]):
            return j
        j = text.find(form, j + 1)
    return -1


def segments(chapter_blocks, chapter_tokens, excluded):
    """Mark each word of the display text with its tokens: [[kind, [text | [form, tokens], ...]], ...].

    Stanza splits forms such as "poszedłem" into "poszedł" + "em"; glued parts join the word before.
    A token that cannot be found in this or the next two blocks is skipped.
    """
    out, ti = [], 0
    for bi, (kind, text) in enumerate(chapter_blocks):
        segs, pos = [], 0
        while ti < len(chapter_tokens):
            form = chapter_tokens[ti][0]
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
                segs[-1][1].append(chapter_tokens[ti])
            elif is_word(chapter_tokens[ti], excluded, names=True):
                segs.append([form, [chapter_tokens[ti]]])
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


def book(story, words, lists):
    out = ["# Klucz", ""]
    for i, (_, text, _) in enumerate(story):
        out += [text.strip().replace("# ", "## ", 1), "", "### Neue Wörter", ""]
        for headword, form, description in lists.get(i, []):
            display, meanings = words[headword]
            pos, grammar, de = meanings["de"]
            label = " · ".join(p for p in (pos, grammar) if p)
            seen = f" · im Text: {form}" + (f" ({description['de']})" if description["de"] else "") if form else ""
            out.append(f"- **{display}**{f' _{label}_' if label else ''} — {de or '?'}{seen}")
        out.append("")
    (ROOT / "KLUCZ.md").write_text("\n".join(out), encoding="utf-8")


def translation(story, lang):
    """Map chapter index -> (Polish blocks, blocks of chapters/<lang>), checked before anything is written.

    Paragraphs must match one to one in number, order and kind (title, date, para, quote, break).
    """
    folder = ROOT / "chapters" / lang
    numbers = {f"{i + 1:02d}" for i in range(len(story))}
    strays = sorted(p.name for p in folder.glob("*.md") if p.stem not in numbers)
    if strays:
        raise SystemExit(f"chapters/{lang}: no Polish chapter for {', '.join(strays)}")
    result = {}
    for i, (_, markdown, _) in enumerate(story):
        path = folder / f"{i + 1:02d}.md"
        if not path.exists():
            continue
        pl, tr = blocks(markdown), blocks(path.read_text(encoding="utf-8"))
        kinds_pl, kinds_tr = [k for k, _ in pl], [k for k, _ in tr]
        if kinds_pl != kinds_tr:
            j = next((j for j, (a, b) in enumerate(zip(kinds_pl, kinds_tr)) if a != b), min(len(pl), len(tr)))
            show = lambda bl: f"{bl[j][0]}: {bl[j][1][:80]}".replace("\n", " / ") if j < len(bl) else "(none, the file ends)"
            raise SystemExit(
                f"{path.relative_to(ROOT)} does not match chapters/{path.name} paragraph by paragraph "
                f"({len(pl)} Polish, {len(tr)} {NAMES[lang]}); nothing was built.\n"
                f"paragraph {j + 1} is the first that differs in kind; an extra or missing one can be earlier:\n"
                f"  pl  {show(pl)}\n  {lang}  {show(tr)}"
            )
        result[i] = (pl, tr)
    return result


def outdated(translations, accepted):
    """Translated paragraphs whose Polish changed since they were last in sync: [(lang, chapter, paragraph, Polish)].

    translations maps lang -> translation(story, lang). data/translation_sync.tsv keeps (lang, chapter,
    Polish hash, translation hash) for every paragraph in sync. A pair is new when either side changed: a new
    translation is taken as updated, but an unchanged one next to a changed Polish text is reported and keeps
    its old pair until it is updated or --accept-<lang> (a lang in accepted) confirms it.
    """
    digest = lambda text: hashlib.sha1(text.encode()).hexdigest()[:12]
    known = set()
    if SYNC.exists():
        known = {tuple(line.split("\t")) for line in SYNC.read_text(encoding="utf-8").splitlines()[1:]}
    known_tr = {(lang, c, t) for lang, c, _, t in known}
    keep, report = set(), []
    for lang, chapters_tr in translations.items():
        for i, (pl, tr) in sorted(chapters_tr.items()):
            number = f"{i + 1:02d}"
            for j, ((_, a), (_, b)) in enumerate(zip(pl, tr)):
                pair = (lang, number, digest(a), digest(b))
                if lang in accepted or pair in known or (lang, number, pair[3]) not in known_tr:
                    keep.add(pair)
                else:
                    report.append((lang, i + 1, j + 1, a))
                    keep |= {k for k in known if (k[0], k[1], k[3]) == (lang, number, pair[3])}
    rows = ["lang\tchapter\tpl\ttranslation"] + ["\t".join(k) for k in sorted(keep)]
    SYNC.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return report


def fonts_css():
    """fonts/fonts.css with every font file embedded: browsers refuse font files next to a page opened as file://."""
    def embed(match):
        data = base64.b64encode((FONTS / match.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"

    return re.sub(r"url\(([\w.-]+\.woff2)\)", embed, (FONTS / "fonts.css").read_text(encoding="utf-8"))


def sheet(path):
    """(title, body, own css) of a grammar sheet, its print colors in the css turned into the page's."""
    html = path.read_text(encoding="utf-8")
    page = re.search(r'<div class="page">(.*)</div>\s*</body>', html, re.S)
    title = re.search(r"<h1>(.*?)</h1>", html, re.S)
    if not page or not title:
        raise SystemExit(f'{path.relative_to(ROOT)}: no <div class="page"> or <h1>')
    style = re.search(r"<style>(.*?)</style>", html, re.S)
    css = re.sub(r"#(?:000|8c8c8c|bbb)\b", lambda m: PRINT_COLORS[m[0]], style[1]) if style else ""
    return title[1], page[1], css


def skeleton(body):
    """A sheet's tags with only their classes, and its bold texts: what a sheet and its translation share.

    A <b lang="…"> is a bold word of the explanation, not Polish; it is translated, so its text is not compared.
    """
    tags = [re.sub(r'\s(?!class=)[\w-]+="[^"]*"', "", t) for t in re.findall(r"<[^>]+>", body)]
    return tags, re.findall(r"<b>(.*?)</b>", body, re.S)


def sheets():
    """The grammar page's sheets, checked before anything is written: (their html, numbers without English).

    An English sheet grammar/en/NN.html must have the tags, classes and bold texts of grammar/NN.html. Without one,
    the German sheet stands in for it. The page script shows one sheet at a time, in the chosen language.
    """
    german = sorted(GRAMMAR.glob("[0-9][0-9].html"))
    strays = sorted(p.name for p in (GRAMMAR / "en").glob("*.html") if not (GRAMMAR / p.name).exists())
    if strays:
        raise SystemExit(f"grammar/en: no German sheet for {', '.join(strays)}")
    out, missing = [], []
    for path in german:
        number, versions = int(path.stem), {"de": sheet(path)}
        english = GRAMMAR / "en" / path.name
        if english.exists():
            versions["en"] = sheet(english)
            for what, a, b in zip(("tags and classes", "bold texts"), skeleton(versions["de"][1]),
                                  skeleton(versions["en"][1])):
                if a != b:
                    j = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                    show = lambda items: items[j] if j < len(items) else "(none, the sheet ends)"
                    raise SystemExit(f"grammar/en/{path.name} does not match grammar/{path.name} in its {what}; "
                                     f"nothing was built.\nthe first difference:\n  de  {show(a)}\n  en  {show(b)}")
        else:
            missing.append(path.stem)
        for lang, (title, body, css) in versions.items():
            langs = lang if len(versions) > 1 else " ".join(LANGS)
            where = f'[data-sheet="{number}"][data-lang="{langs}"]'
            scoped = f"<style>@scope ({where}) {{{css}}}</style>" if css else ""
            body = body.replace("<h1>", "<h1><small></small>", 1)  # the page script writes "Thema N" into it
            out.append(f'{scoped}<div class="page" data-sheet="{number}" data-lang="{langs}" hidden>{body}</div>')
    return "\n".join(out), missing


def fill(template, **values):
    """A template with each __KEY__ replaced by values[key]."""
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(f"__{key.upper()}__", value)
    return text


def ui():
    """tools/ui.tsv as {lang: {key: text}}; every key needs a text in every language."""
    rows = tsv(UI)
    empty = [r["key"] for r in rows if not all(r.get(lang) for lang in LANGS)]
    if empty:
        raise SystemExit(f"tools/ui.tsv: no text in every language for {', '.join(empty)}")
    return {lang: {r["key"]: r[lang] for r in rows} for lang in LANGS}


def main():
    story = chapters(names=True)
    translations = {lang: translation(story, lang) for lang in LANGS}
    grammar_sheets, untranslated = sheets()
    texts = ui()
    glossary = {r["lemma"].lower(): (r["lemma"], {lang: r.get(lang) or "" for lang in LANGS}) for r in tsv(GLOSSARY)}
    dictionary = Dictionary(*load([w for _, _, words in story for w in words]))
    excluded = read_tsv(EXCLUDED)
    marked = [segments(blocks(markdown), tokens(markdown), excluded) for _, markdown, _ in story]
    words, lists, found = entries(marked, dictionary, glossary)
    book(story, words, lists)
    order = [w for i in sorted(lists) for w, _, _ in lists[i]]
    ids = {w: n for n, w in enumerate(order)}
    descriptions = {}  # (description in each language) -> its index in the page data
    index = lambda d: descriptions.setdefault(tuple(d[lang] for lang in LANGS), len(descriptions))
    for chapter in marked:  # [form, tokens] -> [form, id] or [form, id, description]
        for _, segs in chapter:
            for seg in segs:
                if not isinstance(seg, str):
                    headword, description = found[id(seg)]
                    seg[1:] = [ids[headword]] + ([] if description is None else [index(description)])

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
            "blocks": marked[i],
            "parts": chapter_parts,
            "words": [[ids[w]] + ([form, index(d)] if form else []) for w, form, d in lists.get(i, [])],
            "tr": {lang: [t for _, t in translations[lang][i][1]] for lang in LANGS if i in translations[lang]},
        })
    (TEXT / "klucz.txt").write_text("\n\n\n".join(whole) + "\n", encoding="utf-8")

    data = {"chapters": chapters_data, "words": [words[w] for w in order],
            "forms": {lang: [d[k] for d in descriptions] for k, lang in enumerate(LANGS)}}
    json_script = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    shared = {
        "base": fonts_css() + BASE.read_text(encoding="utf-8"),
        "icon": "data:image/svg+xml," + quote(ICON.read_text(encoding="utf-8").strip()),
        "ui": json_script(texts),
        "shared": "".join(p.read_text(encoding="utf-8") for p in (LANG_JS, BAR, FOCUS)),
    }
    page = fill(TEMPLATE, data=json_script(data), **shared)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    (ROOT / "grammar.html").write_text(fill(GRAMMAR_TEMPLATE, print=(GRAMMAR / "style.css").read_text(encoding="utf-8"),
                                            sheets=grammar_sheets, **shared), encoding="utf-8")

    missing = {lang: [words[w][0] for w in order if not words[w][1][lang][2]] for lang in LANGS}
    print(f"KLUCZ.md, text/ ({len(story)} chapters, "
          f"{sum(len(c['parts']) for c in chapters_data)} parts), "
          f"index.html ({len(page) // 1024} KB), grammar.html ({len(list(GRAMMAR.glob('[0-9][0-9].html')))} sheets); "
          f"glossary entries missing: " + ", ".join(f"{len(m)} {lang}" for lang, m in missing.items()))
    for lang, m in missing.items():
        if 0 < len(m) < len(order):  # a language whose glossary column is not started yet is not listed
            print(f"missing in data/glossary.tsv ({lang}):", ", ".join(m))
    unused = [display for lemma, (display, _) in glossary.items() if lemma not in words]
    if unused:
        print("in data/glossary.tsv but not in the story:", ", ".join(unused))
    for lang in LANGS:
        if len(translations[lang]) < len(story):
            absent = [f"{i + 1:02d}" for i in range(len(story)) if i not in translations[lang]]
            print(f"no {NAMES[lang]} translation (chapters/{lang}):", ", ".join(absent))
    if untranslated:
        print("no English grammar sheet (grammar/en):", ", ".join(untranslated))
    report = outdated(translations, {lang for lang in LANGS if f"--accept-{lang}" in sys.argv})
    if report:
        print(f"{len(report)} translated paragraphs may be outdated, their Polish changed. Update them in "
              "chapters/<lang>, or run again with --accept-<lang> if they still fit:")
        for lang, c, j, text in report:
            print(f"  {lang}, chapter {c}, paragraph {j}: {text[:80]}")


if __name__ == "__main__":
    main()
