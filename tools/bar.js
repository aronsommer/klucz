// The bar buttons both pages share: theme, fullscreen and language.

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
