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

  // ---------- CG height calculator (side tilt test) ----------
  // h = (d / 2) / tan(theta); nominal ride height: h - dRH * (W_sprung / W).
  const cgCases = document.querySelectorAll(".cg-case");
  if (cgCases.length) {
    const STORE = "cg-method-a-v1";
    const COLORS = ["#d9481c", "#2b6cb0", "#2f855a"];
    const num = (el) => {
      const v = parseFloat(el && el.value);
      return Number.isFinite(v) ? v : null;
    };
    const fmt = (v, digits = 2) => (v == null ? "" : v.toFixed(digits));
    const inputs = {};
    document.querySelectorAll("[data-cg]").forEach((el) => (inputs[el.dataset.cg] = el));
    const plotEl = document.querySelector("[data-cg-plot]");

    function load() {
      let saved;
      try {
        saved = JSON.parse(localStorage.getItem(STORE) || "null");
      } catch {
        saved = null;
      }
      if (!saved) return;
      Object.entries(saved.inputs || {}).forEach(([k, v]) => {
        if (inputs[k]) inputs[k].value = v;
      });
      cgCases.forEach((c, i) => {
        const rows = (saved.cases || [])[i] || [];
        c.querySelectorAll("tbody tr").forEach((tr, r) => {
          const t = tr.querySelector("[data-theta]");
          const n = tr.querySelector("[data-note]");
          if (!t || !rows[r]) return;
          t.value = rows[r].t || "";
          n.value = rows[r].n || "";
        });
      });
    }

    function save() {
      const data = { inputs: {}, cases: [] };
      Object.entries(inputs).forEach(([k, el]) => (data.inputs[k] = el.value));
      cgCases.forEach((c) => {
        data.cases.push(
          [...c.querySelectorAll("[data-theta]")].map((t) => ({
            t: t.value,
            n: t.closest("tr").querySelector("[data-note]").value,
          }))
        );
      });
      try {
        localStorage.setItem(STORE, JSON.stringify(data));
      } catch {
        /* storage unavailable: calculator still works */
      }
    }

    function stats(values) {
      const n = values.length;
      if (!n) return null;
      const avg = values.reduce((a, b) => a + b, 0) / n;
      const min = Math.min(...values);
      const max = Math.max(...values);
      return { n, avg, min, max };
    }

    function drawPlot(series) {
      if (!plotEl) return;
      const all = series.flatMap((s) => s.values);
      if (!all.length) {
        plotEl.innerHTML = '<p class="cg-plot-empty mono">Enter balance angles to see the plot</p>';
        return;
      }
      const W = 640, H = 70 + series.length * 56, L = 130, R = 24, T = 20;
      let lo = Math.min(...all), hi = Math.max(...all);
      if (hi - lo < 0.5) {
        const mid = (hi + lo) / 2;
        lo = mid - 0.25;
        hi = mid + 0.25;
      }
      const pad = (hi - lo) * 0.12;
      lo -= pad;
      hi += pad;
      const x = (v) => L + ((v - lo) / (hi - lo)) * (W - L - R);
      const step = [0.05, 0.1, 0.25, 0.5, 1, 2].find((s) => (hi - lo) / s <= 8) || 5;
      let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="CG height by case">`;
      const axisY = T + series.length * 56 + 6;
      for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) {
        svg += `<line x1="${x(t)}" y1="${T - 6}" x2="${x(t)}" y2="${axisY}" class="cg-grid"/>`;
        svg += `<text x="${x(t)}" y="${axisY + 18}" text-anchor="middle" class="cg-tick">${t.toFixed(step < 0.1 ? 2 : step < 1 ? 2 : 0)}</text>`;
      }
      svg += `<line x1="${L}" y1="${axisY}" x2="${W - R}" y2="${axisY}" class="cg-axis"/>`;
      svg += `<text x="${(L + W - R) / 2}" y="${axisY + 40}" text-anchor="middle" class="cg-tick">CG height h (in)</text>`;
      series.forEach((s, i) => {
        const y = T + 22 + i * 56;
        const c = COLORS[i];
        svg += `<text x="${L - 14}" y="${y + 4}" text-anchor="end" class="cg-label" fill="${c}">${s.label}</text>`;
        svg += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}" class="cg-row"/>`;
        if (!s.values.length) return;
        const st = stats(s.values);
        svg += `<line x1="${x(st.min)}" y1="${y}" x2="${x(st.max)}" y2="${y}" stroke="${c}" stroke-width="2"/>`;
        s.values.forEach((v) => {
          const cx = x(v);
          if (i === 0) svg += `<circle cx="${cx}" cy="${y}" r="5.5" fill="${c}" fill-opacity="0.75"/>`;
          else if (i === 1) svg += `<rect x="${cx - 5}" y="${y - 5}" width="10" height="10" fill="${c}" fill-opacity="0.75"/>`;
          else svg += `<path d="M ${cx} ${y - 6.5} L ${cx + 6} ${y + 4.5} L ${cx - 6} ${y + 4.5} Z" fill="${c}" fill-opacity="0.75"/>`;
        });
        svg += `<line x1="${x(st.avg)}" y1="${y - 15}" x2="${x(st.avg)}" y2="${y + 15}" stroke="${c}" stroke-width="3"/>`;
        svg += `<text x="${x(st.avg)}" y="${y - 20}" text-anchor="middle" class="cg-avg" fill="${c}">${st.avg.toFixed(2)}</text>`;
      });
      plotEl.innerHTML = svg + "</svg>";
    }

    function update() {
      const d = num(inputs.d);
      const hcad = num(inputs.hcad);
      const drh = num(inputs.drh);
      const sf = num(inputs.sf);
      const exp = document.querySelector('[data-cg-out="theta-exp"]');
      if (exp) exp.textContent = d && hcad ? fmt((Math.atan(d / 2 / hcad) * 180) / Math.PI) : "";

      const series = [];
      cgCases.forEach((c) => {
        const values = [];
        c.querySelectorAll("tbody tr").forEach((tr) => {
          const t = num(tr.querySelector("[data-theta]"));
          const out = tr.querySelector("[data-h]");
          if (!out) return;
          if (d && t && t > 0 && t < 90) {
            const h = d / 2 / Math.tan((t * Math.PI) / 180);
            values.push(h);
            out.textContent = fmt(h);
          } else out.textContent = "";
        });
        const st = stats(values);
        const set = (k, v) => {
          const el = c.querySelector(`[data-r="${k}"]`);
          if (el) el.textContent = v;
        };
        set("n", st ? String(st.n) : "0");
        set("avg", st ? fmt(st.avg) : "");
        set("min", st ? fmt(st.min) : "");
        set("max", st ? fmt(st.max) : "");
        set("nom", st && drh != null && sf != null ? fmt(st.avg - drh * sf) : "");
        series.push({ label: c.dataset.label, values });
      });
      drawPlot(series);
    }

    load();
    update();
    document.querySelectorAll("[data-cg], [data-theta], [data-note]").forEach((el) =>
      el.addEventListener("input", () => {
        update();
        save();
      })
    );
    // Clear needs two clicks; no confirm() pop-up, which some browsers block.
    const clear = document.querySelector("[data-cg-clear]");
    if (clear) {
      const label = clear.textContent;
      let armed = null;
      const disarm = () => {
        clearTimeout(armed);
        armed = null;
        clear.textContent = label;
        clear.classList.remove("is-armed");
      };
      clear.addEventListener("click", () => {
        if (!armed) {
          clear.textContent = "Click again to clear";
          clear.classList.add("is-armed");
          armed = setTimeout(disarm, 4000);
          return;
        }
        disarm();
        document.querySelectorAll("[data-cg], [data-theta], [data-note]").forEach((el) => (el.value = ""));
        try {
          localStorage.removeItem(STORE);
        } catch {
          /* storage unavailable */
        }
        update();
      });
    }
  }

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
