(function () {
  if (window.self !== window.top) {
    document.documentElement.classList.add("in-preview");
    return;
  }

  // ---------- Resume dropdown ----------
  const toggle = document.querySelector("[data-resume-toggle]");
  const panel = document.getElementById("resume-panel");
  if (toggle && panel) {
    const doc = panel.querySelector(".resume-doc");

    function setOpen(open) {
      // load the PDF only the first time the panel opens
      if (open && doc && !doc.firstElementChild && getComputedStyle(doc).display !== "none") {
        const frame = document.createElement("iframe");
        frame.src = doc.dataset.src;
        frame.title = "Resume preview";
        doc.appendChild(frame);
      }
      panel.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    }

    toggle.addEventListener("click", () => setOpen(!panel.classList.contains("is-open")));
    document.addEventListener("click", (e) => {
      if (!panel.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setOpen(false);
    });
  }

  // ---------- Contact card ----------
  // Opens on hover (CSS); click toggles it for touch screens.
  const contact = document.querySelector(".contact");
  if (contact) {
    const contactToggle = contact.querySelector(".contact-toggle");
    contactToggle.addEventListener("click", () => {
      const open = !contact.classList.contains("is-open");
      contact.classList.toggle("is-open", open);
      contactToggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (e) => {
      if (!contact.contains(e.target)) {
        contact.classList.remove("is-open");
        contactToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.querySelectorAll("[data-copy]").forEach((btn) => {
    const label = btn.querySelector(".copy-label");
    let timer;
    btn.addEventListener("click", async () => {
      const text = btn.dataset.copy;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        // fallback for browsers without the async clipboard API
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      btn.classList.add("is-copied");
      label.textContent = "Copied ✓";
      clearTimeout(timer);
      timer = setTimeout(() => {
        btn.classList.remove("is-copied");
        label.textContent = label.dataset.default;
      }, 1800);
    });
  });

  // ---------- Hover preview ----------
  // Shows a live, scaled-down render of the linked page next to the cursor.
  const links = document.querySelectorAll("[data-preview]");
  if (!links.length || !window.matchMedia("(hover: hover)").matches) return;

  const OFFSET = 24;
  const preview = document.createElement("div");
  preview.className = "preview";
  preview.setAttribute("aria-hidden", "true");
  preview.innerHTML =
    '<div class="preview-bar mono"><span class="preview-label"></span><span>Preview</span></div>' +
    '<div class="preview-viewport"></div>';
  document.body.appendChild(preview);

  const label = preview.querySelector(".preview-label");
  const viewport = preview.querySelector(".preview-viewport");
  const frames = new Map(); // href -> iframe, so each page only loads once

  function frameFor(href) {
    let frame = frames.get(href);
    if (!frame) {
      frame = document.createElement("iframe");
      frame.src = href;
      frame.tabIndex = -1;
      frame.setAttribute("scrolling", "no");
      frames.set(href, frame);
      viewport.appendChild(frame);
    }
    return frame;
  }

  function place(x, y) {
    const w = preview.offsetWidth;
    const h = preview.offsetHeight;
    let left = x + OFFSET;
    let top = y + OFFSET;
    if (left + w > window.innerWidth - 12) left = x - w - OFFSET;
    if (top + h > window.innerHeight - 12) top = y - h - OFFSET;
    preview.style.transform = `translate3d(${Math.max(12, left)}px, ${Math.max(12, top)}px, 0)`;
  }

  links.forEach((link) => {
    link.addEventListener("mouseenter", (e) => {
      const href = link.getAttribute("href");
      const active = frameFor(href);
      frames.forEach((f) => (f.style.visibility = f === active ? "visible" : "hidden"));
      label.textContent = link.dataset.preview;
      place(e.clientX, e.clientY);
      preview.classList.add("is-visible");
    });
    link.addEventListener("mousemove", (e) => place(e.clientX, e.clientY));
    link.addEventListener("mouseleave", () => preview.classList.remove("is-visible"));
  });
})();
