import os, html, hashlib

ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
EMAIL = "dr653@cornell.edu"
RESUME = "DavisRattanavijai_Resume.pdf"


def asset_version():
    # changes whenever the CSS or JS changes, so browsers fetch the new files
    h = hashlib.sha1()
    for f in ("assets/css/style.css", "assets/js/main.js"):
        h.update(open(os.path.join(ROOT, f), "rb").read())
    return h.hexdigest()[:8]


VER = asset_version()

def doc(file, pages):
    return dict(pdf="assets/docs/" + file, pages=pages)


def article(name):
    # page body written as HTML in content/<name>.html
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", name + ".html")
    return dict(article=open(path).read())


# status: "complete", "live" (live updating) or "todo" (to be filled out)
SECTIONS = [
    ("Cornell Racing", "cornell-racing", "Formula SAE · Electric", [
        ("Suspension Lead", [
            ("Suspension Kinematics Design", "kinematics", "Suspension kinematics design for the ARG26 car, done in OptimumK.", article("kinematics"), "live"),
            ("Suspension Rates and Parameters Selection", "rates-and-parameters", "To be filled out.", None, "todo"),
            ("Physical CG Height Test", "cg-height-test", "Test procedure for measuring the CG height of ARG26 with two methods: a side tilt test and a front lift test.", article("cg-height-test"), "complete"),
            ("Longitudinal CG Shift Calculation", "cg-shift", "A preliminary calculation of how far the longitudinal CG moves on ARG27 as the accumulator and inverter change, and what that means for a 50/50 weight distribution.", article("cg-shift"), "complete"),
            ("Tire Analysis", "tire-analysis", "To be filled out.", None, "todo"),
            ("Ackermann Selection Methodology", "ackermann-selection-methodology", "The methodology used on ARG27 to determine what Ackermann geometry to design the car to.", article("ackermann-selection-methodology"), "live"),
            ("Manufacturing Compilation", "manufacturing-compilation", "To be filled out.", None, "todo"),
        ]),
        ("Suspension Part Designer", [
            ("Jig Plate", "jig-plate", "My spring 2026 technical report on the jig plate, the fixture that holds each suspension link in position while it is welded.", doc("ARG26_Jig_Plate_Technical_Report.pdf", 23), "complete"),
        ]),
        ("Purchasing Coordinator", [
            ("Managing Purchasing", "managing-purchasing", "To be filled out.", None, "todo"),
            ("RFQ Business Case Submission", "rfq-business-case", "The request for quote I wrote for our Formula SAE Business Case, asking a supplier to manufacture and assemble the ARG26 suspension system.", doc("ARG26_Suspension_RFQ.pdf", 214), "complete"),
        ]),
    ]),
    ("Entrepreneurship", "entrepreneurship", "Product Development", [
        (None, [
            ("KIX Shoe Rack", "kix-shoe-rack", "A shoe rack that takes your shoes off and stores them in one step.", article("kix-shoe-rack"), "live"),
            ("Door-Mounted Cable Machine Prototype", "cable-machine-prototype", "To be filled out.", None, "todo"),
        ]),
    ]),
    ("Machine Shop", "machine-shop", "Manufacturing Learning Studio · Staff", [
        ("Training Manuals", [
            ("HAAS CNC Overview Manual", "haas-cnc-manual", "I wrote this manual for the Cornell Engineering machine shop so students can learn how to set up and run the HAAS CNC mills.", doc("HAAS_CNC_Overview_Manual.pdf", 10), "complete"),
            ("C-Block CAM Manual", "c-block-cam-manual", "I wrote this manual for the Cornell Engineering machine shop so students can learn how to program a part in Fusion 360 and machine it on the HAAS.", doc("C-Block_CAM_Manual.pdf", 27), "complete"),
        ]),
    ]),
    ("Math Modeling Papers", "math-modeling", "Team Lead · Newton North HS", [
        (None, [
            ("Household Readiness of Pet Ownership Model (Paper)", "pets-paper", "Our team's paper for the 2024 International Mathematical Modeling Challenge (IMMC). We built a model to measure whether a household is ready to own a pet.", doc("IMMC2024_Pets_Paper.pdf", 31), "complete"),
            ("Forecasting Hydroelectric Power Decline at Hoover Dam (Paper)", "lake-mead-paper", "Our team's paper for the 2023–24 Modeling the Future Challenge (MTFC), on Lake Mead and the Colorado River water supply.", doc("MTFC2023_Colorado_River_Paper.pdf", 31), "complete"),
            ("Model of the Electrification of Buses in Metropolitan Cities (Paper)", "e-bus-paper", "Our team's paper for the 2023 High School Mathematical Contest in Modeling (HiMCM). We modeled the cost of switching a bus fleet to electric buses.", doc("HiMCM2023_E_Bus_Paper.pdf", 24), "complete"),
            ("Statistical Analysis of Melanoma Cancer in America (Paper)", "melanoma-paper", "Our team's paper for the 2022–23 Modeling the Future Challenge (MTFC). We looked at how demographic and geographic factors relate to melanoma rates.", doc("MTFC2022_Melanoma_Paper.pdf", 31), "complete"),
            ("Modeling the Optimal Plane Boarding Method (Paper)", "plane-boarding-paper", "Our team's paper for the 2022 International Mathematical Modeling Challenge (IMMC). We modeled plane boarding and exiting methods to find the fastest one.", doc("IMMC2022_Plane_Boarding_Paper.pdf", 45), "complete"),
        ]),
    ]),
]

STATUS = {"complete": "Complete", "live": "Live updating", "todo": "To be filled out"}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{base}assets/css/style.css?v={ver}" />
</head>
<body{body_class}>
  <!-- EDIT: site notice banner; delete this div to remove it -->
  <div class="site-notice"><div class="wrap"><span class="mono">Notice</span>This site is continually being updated throughout the year, but check out what I&rsquo;ve written about so far!</div></div>
  <header class="topbar">
    <div class="wrap">
      <a class="brand" href="{base}index.html">Davis Rattanavijai</a>
      <nav class="nav">
        <a href="{base}index.html#work">Work</a>
        <div class="nav-item contact">
          <button type="button" class="contact-toggle" aria-expanded="false" aria-controls="contact-panel">Contact</button>
          <div class="contact-panel" id="contact-panel">
            <div class="contact-card">
              <span class="mono">Email</span>
              <button type="button" class="copy-email" data-copy="{email}">
                <span class="email">{email}</span>
                <span class="copy-label mono" data-default="Click to copy">Click to copy</span>
              </button>
            </div>
          </div>
        </div>
        <button type="button" data-resume-toggle aria-expanded="false" aria-controls="resume-panel">Resume<span class="caret" aria-hidden="true">&#9662;</span></button>
      </nav>
      <div class="resume-panel" id="resume-panel">
        <div class="resume-head mono"><span>Resume</span><span>Sep 2026</span></div>
        <div class="resume-doc" data-src="{base}{resume}#toolbar=0&amp;navpanes=0&amp;view=FitH"></div>
        <div class="resume-actions">
          <a class="primary" href="{base}{resume}" download>Download PDF</a>
          <a href="{base}resume.html">Open &rarr;</a>
        </div>
      </div>
    </div>
  </header>
"""

FOOT = """
  <footer class="footer">
    <div class="wrap mono">
      <span>&copy; 2026 Davis Rattanavijai</span>
      <a href="mailto:{email}">{email}</a>
    </div>
  </footer>
  <script src="{base}assets/js/main.js?v={ver}"></script>
</body>
</html>
"""

e = html.escape


def head(title, desc, base, body_class=""):
    return HEAD.format(title=title, desc=desc, base=base, email=EMAIL, resume=RESUME, ver=VER,
                       body_class=f' class="{body_class}"' if body_class else "")


def foot(base):
    return FOOT.format(base=base, email=EMAIL, ver=VER)


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(text)


# ---------- flatten for numbering + prev/next ----------
pages = []
for si, (sec, sec_slug, sec_tag, groups) in enumerate(SECTIONS, 1):
    n = 0
    for role, items in groups:
        for title, slug, blurb, doc, status in items:
            n += 1
            pages.append(dict(sec=sec, role=role, title=title, slug=slug, blurb=blurb, doc=doc,
                              idx=f"{si:02d}.{n:02d}"))
by_slug = {p["slug"]: p for p in pages}

# ---------- index ----------
out = [head("Davis Rattanavijai — Portfolio",
            "Engineering portfolio of Davis Rattanavijai, Mechanical Engineering, Cornell University Class of 2028.", "")]
out.append("""
  <main>
    <section class="hero">
      <div class="wrap">
        <div>
          <h1 class="display hero-name"><span>Davis</span><span>Rattanavijai</span></h1>
          <div class="hero-meta">
            <span>Mechanical Engineering</span>
            <span>Cornell University</span>
            <span>Class of 2028</span>
          </div>
        </div>
        <figure class="headshot">
          <div class="shot"><img src="davisheadshot.jpeg" alt="Portrait of Davis Rattanavijai" width="400" height="400" /></div>
        </figure>
      </div>
    </section>

    <section class="section" id="about">
      <div class="wrap">
        <div class="section-label">
          <span class="num">00</span>
          <h2 class="caps">About Me</h2>
        </div>
        <div>
          <p class="about-text">
            Hi, I&rsquo;m Davis! I&rsquo;m a mechanical engineering student at Cornell interested in supply chain
            and operations, and I consider myself a business-oriented engineer. My experience spans technical
            work in design, manufacturing, and testing, as well as customer-facing roles that have strengthened
            my communication and problem-solving skills.
          </p>
        </div>
      </div>
    </section>
""")

for si, (sec, sec_slug, sec_tag, groups) in enumerate(SECTIONS, 1):
    sid = ' id="work"' if si == 1 else f' id="{sec_slug}"'
    out.append(f"""
    <section class="section"{sid}>
      <div class="wrap">
        <div class="section-label">
          <span class="num">{si:02d}</span>
          <h2 class="caps">{e(sec)}</h2>
          <span class="mono">{e(sec_tag)}</span>
        </div>
        <div>""")
    for role, items in groups:
        out.append('\n          <div class="dir-group">')
        if role:
            out.append(f"""
            <div class="dir-role"><h3 class="caps">{e(role)}</h3><span class="mono">{len(items):02d} {'item' if len(items) == 1 else 'items'}</span></div>""")
        out.append('\n            <ul class="dir-list">')
        for title, slug, blurb, doc, status in items:
            p = by_slug[slug]
            flag = f'<span class="status status--{status} mono">{STATUS[status]}</span>'
            out.append(f"""
              <li><a class="dir-link" href="projects/{slug}.html" data-preview="{p['idx']} / {e(title)}"><span class="idx">{p['idx']}</span><span class="title">{e(title)}</span>{flag}<span class="arrow">&rarr;</span></a></li>""")
        out.append("\n            </ul>\n          </div>")
    out.append("""
        </div>
      </div>
    </section>
""")
out.append("  </main>\n")
out.append(foot(""))
write("index.html", "".join(out))

# ---------- resume page ----------
write("resume.html", head("Resume — Davis Rattanavijai", "Resume of Davis Rattanavijai.", "", "viewer-page") + f"""
  <main class="viewer">
    <div class="viewer-bar">
      <div class="wrap">
        <div class="crumbs mono"><a href="index.html">Index</a><span class="sep">/</span><span>Resume</span></div>
        <a class="btn primary" href="{RESUME}" download>Download PDF</a>
      </div>
    </div>
    <iframe class="viewer-frame" src="{RESUME}#view=FitH&amp;navpanes=0" title="Davis Rattanavijai resume"></iframe>
    <p class="viewer-fallback mono">Can't see the resume? <a href="{RESUME}">Open the PDF directly</a>.</p>
  </main>
  <script src="assets/js/main.js?v={VER}"></script>
</body>
</html>
""")


# ---------- project pages ----------
def doc_block(p):
    d = p["doc"]
    pdf = "../" + d["pdf"]
    return f"""
    <section class="p-content">
      <div class="wrap">
        <div class="doc-embed">
          <div class="doc-head mono"><span>{e(p["title"])}</span><span>{d["pages"]} pages &middot; PDF</span></div>
          <iframe src="{pdf}#view=FitH&amp;navpanes=0" title="{e(p["title"])}" loading="lazy"></iframe>
        </div>
        <div class="doc-actions">
          <a class="btn primary" href="{pdf}" download>Download PDF</a>
          <a class="btn" href="{pdf}" target="_blank" rel="noopener">Open full screen &#8599;</a>
        </div>
      </div>
    </section>
"""


for p in pages:
    sec_pages = [q for q in pages if q["sec"] == p["sec"]]
    j = sec_pages.index(p)
    prev = sec_pages[j - 1] if j > 0 else None
    nxt = sec_pages[j + 1] if j < len(sec_pages) - 1 else None
    d = p["doc"]

    crumbs = f'<a href="../index.html#work">Index</a><span class="sep">/</span><span>{e(p["sec"])}</span>'
    if p["role"]:
        crumbs += f'<span class="sep">/</span><span>{e(p["role"])}</span>'

    body = d["article"] if d and "article" in d else doc_block(p) if d else ""
    hero = f"""
  <main>
    <section class="p-hero">
      <div class="wrap">
        <div class="crumbs mono">{crumbs}</div>
        <h1 class="display p-title">{e(p["title"])}</h1>
        <!-- EDIT: description -->
        <p class="p-desc">{e(p["blurb"])}</p>
      </div>
    </section>
"""
    nav = '\n    <nav class="p-nav">\n      <div class="wrap">\n'
    if prev:
        nav += f'        <a class="prev" href="{prev["slug"]}.html"><span class="mono">&larr; Previous</span><span class="display">{e(prev["title"])}</span></a>\n'
    else:
        nav += '        <a class="prev" href="../index.html#work"><span class="mono">&larr; Back</span><span class="display">Index</span></a>\n'
    if nxt:
        nav += f'        <a class="next" href="{nxt["slug"]}.html"><span class="mono">Next &rarr;</span><span class="display">{e(nxt["title"])}</span></a>\n'
    else:
        nav += '        <a class="next" href="../index.html#work"><span class="mono">Back &rarr;</span><span class="display">Index</span></a>\n'
    nav += "      </div>\n    </nav>\n  </main>\n"

    write(f"projects/{p['slug']}.html",
          head(f"{p['title']} — Davis Rattanavijai", e(p["blurb"]), "../") + hero + body + nav + foot("../"))

print(len(pages), "pages")
