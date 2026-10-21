#!/bin/sh
# Deletes the numbered PDFs in the given folder, renders every numbered sheet to a PDF there, named
# after its number and <h1> (08.html, "Biernik – Akkusativ" -> 08-biernik-akkusativ.pdf), checks that
# each is exactly one page and merges them in order into gramatyka-grammatik.pdf there. Exits non-zero
# on failure.
[ -d "$1" ] || { echo "usage: grammar/pdf.sh <output folder>" >&2; exit 1; }
out="$(cd "$1" && pwd)"
rm -f "$out"/[0-9][0-9]-*.pdf
cd "$(dirname "$0")" || exit 1
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in [0-9][0-9].html; do
  name=$(perl -CSD -Mutf8 -ne 'if (/<h1>(.*?)<\/h1>/) { $_ = lc $1; tr/ąćęłńóśźż/acelnoszz/;
    s/ä/ae/g; s/ö/oe/g; s/ü/ue/g; s/ß/ss/g; s/[^a-z0-9]+/-/g; s/^-|-$//g; print; exit }' "$f")
  [ -n "$name" ] || { echo "$f: no <h1>" >&2; exit 1; }
  "$chrome" --headless --no-pdf-header-footer --print-to-pdf="$out/${f%.html}-$name.pdf" "file://$PWD/$f" 2>/dev/null
done
cd "$out" || exit 1
osascript -l JavaScript - gramatyka-grammatik.pdf [0-9][0-9]-*.pdf <<'EOF'
ObjC.import("PDFKit");
function run([out, ...files]) {
  const all = $.PDFDocument.alloc.init;
  const bad = [];
  for (const f of files) {
    const doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(f));
    const pages = Number(doc.pageCount);
    if (pages !== 1) bad.push(`${f}: ${pages} pages`);
    for (let i = 0; i < pages; i++) all.insertPageAtIndex(doc.pageAtIndex(i), all.pageCount);
  }
  if (bad.length) throw new Error(`Not one page:\n${bad.join("\n")}`);
  all.writeToFile(out);
  return `OK: ${files.length} sheets, ${Number(all.pageCount)} pages -> ${out}`;
}
EOF
