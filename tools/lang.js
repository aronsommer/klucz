// The language of the page's own texts, kept for both pages; without a stored one, the browser's (German, else English).
// t(key, ...values) is a text of tools/ui.tsv with {0}, {1} … filled in. data-t sets an element's content,
// data-tip its title and aria-label.
const UI = JSON.parse(document.getElementById("ui").textContent);
let lang;
try {
  lang = localStorage.getItem("klucz-lang");
} catch {}
if (!(lang in UI)) lang = navigator.language.startsWith("de") ? "de" : "en";
const t = (key, ...values) => UI[lang][key].replace(/\{(\d)\}/g, (_, i) => values[i]);
function applyLang() {
  for (const e of document.querySelectorAll("[data-t]")) e.innerHTML = t(e.dataset.t);
  for (const e of document.querySelectorAll("[data-tip]")) e.title = e.ariaLabel = t(e.dataset.tip);
}
// a new language, stored; fires "langchange" for the texts the page scripts write
function setLang(next) {
  lang = next;
  try {
    localStorage.setItem("klucz-lang", lang);
  } catch {}
  applyLang();
  dispatchEvent(new Event("langchange"));
}
applyLang();
