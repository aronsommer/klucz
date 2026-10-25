// The bar buttons both pages share: share, theme, fullscreen and language; and the toast under the bar.

// a short message under the bar
let toastTimer;
function toast(msg) {
  const box = document.getElementById("toast");
  box.textContent = msg;
  box.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    box.hidden = true;
  }, 3500);
}

// The share button: a menu of the page's items(), each {label, detail, link | copy | run}, null a line.
// A link goes to the device's share menu on a touch screen, else to the clipboard like a copy.
// Returns a function that closes the menu.
function shareButton(items) {
  const button = document.getElementById("share"),
    menu = document.getElementById("share-menu");
  let timer;
  const open = (on) => {
    menu.hidden = !on;
    button.ariaExpanded = on;
  };
  // the check on the button after a copy, for 2 seconds or until the next tap on it
  const mark = (on) => {
    clearTimeout(timer);
    button.classList.toggle("done", on);
    button.firstElementChild.textContent = on ? "check" : "ios_share";
    if (on) timer = setTimeout(() => mark(false), 2000);
  };
  // success shows on the button only; a failure needs the message
  const done = (ok) => {
    mark(ok);
    if (!ok) toast(t("copy_blocked"));
  };
  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      return done(true);
    } catch {}
    // without the clipboard API: a hidden textarea and the old copy command
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.readOnly = true;
    ta.style.cssText = "position: fixed; left: 0; top: 0; opacity: 0; pointer-events: none";
    document.body.append(ta);
    ta.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch {}
    ta.remove();
    done(ok);
  }
  async function send(url) {
    if (navigator.share && matchMedia("(pointer: coarse)").matches) {
      try {
        return await navigator.share({ title: document.title, url });
      } catch (e) {
        if (e.name === "AbortError") return; // closed by the reader
      }
    }
    copy(url);
  }
  button.onclick = () => {
    mark(false);
    if (!menu.hidden) return open(false);
    menu.replaceChildren(
      ...items().map((item) => {
        if (!item) return document.createElement("hr");
        const b = document.createElement("button");
        b.textContent = item.label;
        if (item.detail) {
          const small = document.createElement("small");
          small.textContent = item.detail;
          b.append(small);
        }
        b.onclick = () => {
          open(false);
          if (item.link) send(item.link);
          else if (item.copy) copy(item.copy);
          else item.run();
        };
        return b;
      }),
    );
    open(true);
  };
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".share")) open(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") open(false);
  });
  addEventListener("langchange", () => open(false));
  // its reading position would be outdated
  addEventListener("scroll", () => open(false), { passive: true });
  return () => open(false);
}

// The theme button. A stored theme (set in the head) wins over the system's; the button shows the theme it switches to.
{
  const button = document.getElementById("theme");
  const systemDark = matchMedia("(prefers-color-scheme: dark)");
  const isDark = () => {
    const s = document.documentElement.style.colorScheme;
    return s ? s === "dark" : systemDark.matches;
  };
  const update = () => {
    button.firstElementChild.textContent = isDark() ? "light_mode" : "dark_mode";
    button.title = button.ariaLabel = t(isDark() ? "theme_light" : "theme_dark");
  };
  button.onclick = () => {
    const next = isDark() ? "light" : "dark";
    document.documentElement.style.colorScheme = next;
    try {
      localStorage.setItem("klucz-theme", next);
    } catch {}
    update();
  };
  systemDark.addEventListener("change", update);
  addEventListener("langchange", update);
  update();
}

// The fullscreen button, hidden where a page cannot go fullscreen (iPhone).
{
  const button = document.getElementById("fullscreen");
  button.hidden = !document.fullscreenEnabled;
  button.onclick = () =>
    document.fullscreenElement
      ? document.exitFullscreen()
      : document.documentElement.requestFullscreen();
  const update = () => {
    const on = !!document.fullscreenElement;
    button.firstElementChild.textContent = on ? "fullscreen_exit" : "fullscreen";
    button.title = button.ariaLabel = t(on ? "fullscreen_exit" : "fullscreen");
  };
  document.addEventListener("fullscreenchange", update);
  addEventListener("langchange", update);
  update();
}

// The language button.
{
  const select = document.getElementById("lang");
  select.value = lang;
  select.onchange = () => {
    select.blur();
    setLang(select.value);
  };
}
