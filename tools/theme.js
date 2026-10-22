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
