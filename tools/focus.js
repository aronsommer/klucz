// Chrome keeps the focus ring on a select picked with the mouse, even when the same option is picked
// (no "change", so no blur); the ring is meant for the keyboard, so a select used with the pointer hides it.
addEventListener("pointerdown", (e) => e.target.closest("select")?.classList.add("by-pointer"));
addEventListener("keydown", (e) => e.target.classList.remove("by-pointer"));
addEventListener("focusout", (e) => e.target.classList.remove("by-pointer"));
