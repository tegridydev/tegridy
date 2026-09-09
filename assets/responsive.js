(() => {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector("#mobile-nav-panel");
  const themeToggle = document.querySelector(".theme-toggle");

  if (!header || !toggle || !panel) return;

  const setOpen = (open, restoreFocus = false) => {
    header.classList.toggle("nav-expanded", open);
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");

    if (restoreFocus) {
      toggle.focus({ preventScroll: true });
    }
  };

  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";

    if (open && themeToggle?.getAttribute("aria-expanded") === "true") {
      themeToggle.click();
    }

    setOpen(open);
  });

  panel.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  themeToggle?.addEventListener("click", () => {
    if (toggle.getAttribute("aria-expanded") === "true") {
      setOpen(false);
    }
  });

  document.addEventListener("pointerdown", (event) => {
    if (
      toggle.getAttribute("aria-expanded") === "true" &&
      !header.contains(event.target)
    ) {
      setOpen(false);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      toggle.getAttribute("aria-expanded") === "true"
    ) {
      setOpen(false, true);
    }
  });

  window.addEventListener("resize", () => {
    if (
      window.innerWidth > 900 &&
      toggle.getAttribute("aria-expanded") === "true"
    ) {
      setOpen(false);
    }
  });
})();
