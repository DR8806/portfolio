import os, re, html, hashlib

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
CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")

def doc(file, pages):
    return dict(pdf="assets/docs/" + file, pages=pages)


def article(name, pdf=None):
    # page body written as HTML in content/<name>.html; pdf: original document attached at the end
    return dict(parts=[dict(content=name)], attach=pdf)


def parts(*items):
    # page made of several write-ups, each with its own heading in the page and in the contents
    # items: (heading, content name, short description)
    return dict(parts=[dict(title=t, content=c, blurb=d) for t, c, d in items])


# status: "complete" or "live" (continually updated); year: shown on the home page list
def item(title, slug, blurb, body, status, year):
    return dict(title=title, slug=slug, blurb=blurb, doc=body, status=status, year=year)


# old page -> where its write-up lives now, so old links still work
MOVED = {
    "ackermann-selection-methodology": "kinematics",
    "cg-height-test": "physical-tests",
    "cg-shift": "miscellaneous",
}


def link_out(text, url):
    return f'<a class="a-link" href="{url}" target="_blank" rel="noopener">{text}</a>'


HIMCM = link_out("High School Mathematical Contest in Modeling (HiMCM)", "https://www.comap.com/contests/himcm-midmcm")
IMMC = link_out("International Mathematical Modeling Challenge (IMMC)", "https://www.immchallenge.org/")
MTFC = link_out("Modeling the Future Challenge (MTFC)", "https://www.mtfchallenge.org/")
COMAP_RESULTS = "https://www.contest.comap.com/highschool/contests/himcm/"
IMMC24_RESULTS = COMAP_RESULTS + "2024_IMMC_USA_Regional_Results.pdf"
HIMCM23_RESULTS = COMAP_RESULTS + "2023_HiMCM_Results.pdf"
HIMCM22_RESULTS = COMAP_RESULTS + "2022_HiMCM_Results.pdf"
HIMCM21_RESULTS = COMAP_RESULTS + "2021_HiMCM_Results.pdf"
TEAM = "Davis Rattanavijai, Yuhan Wu, Youcef Chahboun, Tsubasa Tamura"
COACH = "Mrs. Michele MacDonald"
COACH_THEN = "Mrs. Michele MacDonald (then Ms. Michele Widener)"
MENTOR = "; MTFC mentor Mrs. Susan Witcraft"


def paper(title, slug, file, pages, year, summary, comp, dates, result, team, coach, results=None):
    # math modeling paper: details at the top, the PDF, then our row of the official results if there is one
    facts = [("Competition", comp), ("Written", dates), ("Result", result), ("Team", team), ("Coach", coach)]
    body = dict(doc(file, pages), facts=facts, results=results)
    return item(title, slug, summary, body, "complete", year)


SECTIONS = [
    ("Cornell Racing", "cornell-racing", [
        ("Suspension Lead", [
            item("Suspension Kinematics Design", "kinematics", "Suspension kinematics design done in OptimumK, along with the Ackermann selection that goes into it.", parts(
                ("Kinematics", "kinematics", "Suspension kinematics design for the ARG26 car, done in OptimumK."),
                ("Ackermann", "ackermann-selection-methodology", "The methodology used on ARG27 to determine what Ackermann geometry to design the car to."),
                ("Steering Torque", "steering-torque", "The torque at the steering wheel and the force on the rack for ARG27's NARRco rack."),
            ), "live", "2026"),
            item("Suspension Rates", "rates-and-parameters", "Selection of the suspension rates and parameters for ARG27. More will be added here as the work continues.", article("rates-and-parameters"), "live", "2026"),
            item("Physical Tests", "physical-tests", "Tests run on the car to measure its real properties.", parts(
                ("CG Height Test", "cg-height-test", "Test procedure for measuring the CG height of ARG26 with two methods: a side tilt test and a front lift test."),
            ), "complete", "2026"),
            item("Race Data Analysis", "race-data-analysis", "Lateral acceleration, speed and corner radius from ARG26's autocross and endurance runs at competition.", article("race-data-analysis"), "complete", "2026"),
            item("Load Cases", "load-cases", "ARG26 and ARG27 load cases from IMU data, with a year over year comparison.", article("load-cases"), "live", "2026"),
            item("Tire Analysis", "tire-analysis", "Lateral force plots from TTC tire data, comparing Hoosier tire candidates.", article("tire-analysis"), "live", "2026"),
            item("Aero Analysis", "aero-analysis", "Downforce and drag from a CFD speed sweep at 0° yaw, roll and pitch, and the aero values used in the suspension work.", article("aero-analysis"), "live", "2026"),
            item("Miscellaneous", "miscellaneous", "Other calculations done for the suspension.", parts(
                ("Longitudinal CG Shift Calculation", "cg-shift", "A preliminary calculation of how far the longitudinal CG moves on ARG27 as the accumulator and inverter change, and what that means for a 50/50 weight distribution."),
            ), "complete", "2026"),
        ]),
        ("Suspension Engineer", [
            item("Suspension Jig Plate Project", "jig-plate", "My spring 2026 technical report on the jig plate, the fixture that holds each suspension link in position while it is welded.", doc("ARG26_Jig_Plate_Technical_Report.pdf", 23), "complete", "2026"),
        ]),
        ("Procurement Lead", [
            item("RFQ Business Case Submission", "rfq-business-case", "The request for quote I wrote for our Formula SAE Business Case, asking a supplier to manufacture and assemble the ARG26 suspension system.", doc("ARG26_Suspension_RFQ.pdf", 214), "complete", "2026"),
        ]),
    ]),
    ("Entrepreneurship", "entrepreneurship", [
        (None, [
            item("KIX Shoe Rack", "kix-shoe-rack", "A shoe rack that takes your shoes off and stores them in one step.", article("kix-shoe-rack"), "live", "2026"),
        ]),
    ]),
    ("Machine Shop", "machine-shop", [
        (None, [
            item("HAAS CNC Overview Manual", "haas-cnc-manual", "I wrote this manual for the Cornell Engineering machine shop so students can learn how to set up and run the HAAS CNC mills.", doc("HAAS_CNC_Overview_Manual.pdf", 10), "complete", "2026"),
            item("C-Block CAM Manual", "c-block-cam-manual", "I wrote this manual for the Cornell Engineering machine shop so students can learn how to program a part in Fusion 360 and machine it on the HAAS.", doc("C-Block_CAM_Manual.pdf", 27), "complete", "2026"),
        ]),
    ]),
    ("Math Modeling Papers", "math-modeling", [
        (None, [
            paper("Household Readiness of Pet Ownership Model (Paper)", "pets-paper", "IMMC2024_Pets_Paper.pdf", 31, "2024",
                  "Written in April 2024 over five days for the International Mathematical Modeling Challenge (IMMC), which our team qualified for through HiMCM. "
                  "We built a model that scores whether a household is ready to own a cat by balancing the well-being of the people and the pet. "
                  "It compares household answers to breed data using modified cosine similarity and vector projection, then extends to dogs, birds, guinea pigs and fish.",
                  IMMC, "April 12 &ndash; 16, 2024",
                  "USA Regional Finalist, top 5 of 13 qualified teams. " + link_out("Results (PDF)", IMMC24_RESULTS),
                  TEAM, COACH, results=("immc2024-results.png", IMMC24_RESULTS)),
            paper("Forecasting Hydroelectric Power Decline at Hoover Dam (Paper)", "lake-mead-paper", "MTFC2023_Colorado_River_Paper.pdf", 31, "2023&ndash;24",
                  "Written between December 2023 and March 2024 for the Modeling the Future Challenge (MTFC), a three-month competition with semifinal and final rounds. "
                  "We forecast how far Lake Mead will fall through 2030 and what that means for hydroelectric power at Hoover Dam, using symbolic regression and Facebook Prophet. "
                  "The model estimated a 29.2% drop in volume and $440M in replacement energy costs, and we proposed ways to reduce the impact.",
                  MTFC, "December 2023 &ndash; March 3, 2024",
                  "3rd place ($10,000 award), top 3 of 268 teams. " + link_out("Awards", "https://www.mtfchallenge.org/awards/") + " &middot; "
                  + link_out("Finalists", "https://www.mtfchallenge.org/unveiling-the-2023-2024-modeling-the-future-challenge-finalists/"),
                  "Davis Rattanavijai, Tsubasa Tamura, Karina Chung, Avnish Kumar, Maya Figelman", COACH + MENTOR),
            paper("Model of the Electrification of Buses in Metropolitan Cities (Paper)", "e-bus-paper", "HiMCM2023_E_Bus_Paper.pdf", 24, "2023",
                  "Written in November 2023 over two weeks for the High School Mathematical Contest in Modeling (HiMCM). "
                  "We built an optimization model using Lagrange multipliers to find how many electric buses and chargers a city like Boston, Philadelphia or Detroit should buy. "
                  "The model used real route data, energy prices and ecological benefits, with the algorithms written in code.",
                  HIMCM, "November 1 &ndash; 14, 2023",
                  "Finalist, top 6% of 967 submissions. " + link_out("Results (PDF)", HIMCM23_RESULTS),
                  TEAM, COACH, results=("himcm2023-results.png", HIMCM23_RESULTS)),
            paper("Statistical Analysis of Melanoma Cancer in America (Paper)", "melanoma-paper", "MTFC2022_Melanoma_Paper.pdf", 31, "2022&ndash;23",
                  "Written between December 2022 and March 2023 for the Modeling the Future Challenge (MTFC). "
                  "We built a geospatial model linking melanoma rates across the U.S. to UV exposure, elevation and demographics, using ArcGIS, regression and image analysis in MATLAB. "
                  "The results pointed to high-risk regions where public health efforts could be targeted.",
                  MTFC, "December 2022 &ndash; March 3, 2023",
                  "Finalist, top 13 of 227 teams. " + link_out("Finalists", "https://actuarialfoundation.org/2023-modeling-the-future-challenge-finalists/"),
                  "Davis Rattanavijai, Tsubasa Tamura, Youcef Chahboun, Michael Dai, Jennifer Li", COACH + MENTOR),
            paper("Modeling the Optimal Plane Boarding Method (Paper)", "plane-boarding-paper", "IMMC2022_Plane_Boarding_Paper.pdf", 45, "2022",
                  "Written in April 2022 over five days for the International Mathematical Modeling Challenge (IMMC). "
                  "We built a simulation in Python and R to test airline boarding methods, with random variation between passengers. "
                  "The model found methods that beat the standard boarding strategies.",
                  IMMC, "April 8 &ndash; 12, 2022", "USA Regional Meritorious.", TEAM, COACH),
            paper("Honey Bee Population and Orchard Pollination Model (Paper)", "honey-bees-paper", "HiMCM2022_Honey_Bees_Paper.pdf", 25, "2022",
                  "Written in November 2022 over two weeks for the High School Mathematical Contest in Modeling (HiMCM). "
                  "We simulated a honey bee hive's population in R under reproduction, starvation, mites, predators and hurricanes. "
                  "We then used the model to find how many hives it takes to pollinate a 20-acre apple orchard.",
                  HIMCM, "November 2 &ndash; 15, 2022",
                  "Honorable Mention. " + link_out("Results (PDF)", HIMCM22_RESULTS),
                  TEAM, COACH_THEN, results=("himcm2022-results.png", HIMCM22_RESULTS)),
            paper("Off-Grid Battery Model and Evaluation (Paper)", "batteries-paper", "HiMCM2021_Electric_Batteries_Paper.pdf", 22, "2021",
                  "Written in November 2021, my sophomore year of high school, as our team's first paper, for the High School Mathematical Contest in Modeling (HiMCM). "
                  "We modeled the daily power demand of an off-grid 1,600 sq ft home from its appliances and compared home battery systems against it. "
                  "The model picked the Tesla Powerwall 2 as the best option and looked at whether newer batteries could do better.",
                  HIMCM, "November 3 &ndash; 16, 2021",
                  "Meritorious. " + link_out("Results (PDF)", HIMCM21_RESULTS),
                  TEAM, COACH_THEN, results=("himcm2021-results.png", HIMCM21_RESULTS)),
        ]),
    ]),
]


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
      <a class="brand" href="{base}index.html">Davis Rattanavijai <span>Portfolio</span></a>
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
        <div class="resume-head mono"><span>Resume</span><span>Oct 2026</span></div>
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


# ---------- flatten for prev/next ----------
pages = []
for sec, sec_slug, groups in SECTIONS:
    for role, items in groups:
        for it in items:
            pages.append(dict(it, sec=sec, role=role))

out = [head("Davis Rattanavijai — Portfolio",
            "Engineering portfolio of Davis Rattanavijai, Mechanical Engineering, Cornell University Class of 2028.", "")]
out.append("""
  <main>
    <section class="hero">
      <div class="wrap">
        <div>
          <h1 class="display hero-name">Davis Rattanavijai</h1>
          <ul class="hero-meta">
            <li>Mechanical Engineering</li>
            <li>Cornell University</li>
            <li>Class of 2028</li>
          </ul>
        </div>
        <figure class="headshot">
          <div class="shot"><img src="davisheadshot.jpeg" alt="Portrait of Davis Rattanavijai" width="400" height="400" /></div>
        </figure>
      </div>
    </section>

    <section class="section" id="about">
      <div class="wrap">
        <div class="section-label">
          <h2 class="caps">About Me</h2>
        </div>
        <div>
          <p class="about-text">
            Hi, I&rsquo;m Davis! I&rsquo;m a third-year mechanical engineering student at Cornell interested in
            supply chain, operations, and mechanical engineering. I bring technical experience through Formula SAE
            and manufacturing, complemented by experience in customer service and entrepreneurship.
          </p>
        </div>
      </div>
    </section>
""")

def link(it):
    note = '<span class="status status--live mono">Continually updated</span>' if it["status"] == "live" else '<span class="status"></span>'
    return (f'\n              <li><a class="dir-link" href="projects/{it["slug"]}.html" data-preview="{e(it["title"])}">'
            f'<span class="title">{e(it["title"])}</span>{note}<span class="year mono">{it["year"]}</span></a></li>')


for si, (sec, sec_slug, groups) in enumerate(SECTIONS):
    sid = ' id="work"' if si == 0 else f' id="{sec_slug}"'
    out.append(f"""
    <section class="section"{sid}>
      <div class="wrap">
        <div class="section-label">
          <h2 class="caps">{e(sec)}</h2>
        </div>
        <div>""")
    for role, items in groups:
        out.append('\n          <div class="dir-group">')
        if role:
            out.append(f'\n            <div class="dir-role"><h3 class="caps">{e(role)}</h3></div>')
        out.append('\n            <ul class="dir-list">')
        out.extend(link(it) for it in items)
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
def pdf_embed(title, d):
    pdf = "../" + d["pdf"]
    return f"""<div class="doc-embed">
          <div class="doc-head mono"><span>{e(title)}</span><span>{d["pages"]} pages &middot; PDF</span></div>
          <iframe src="{pdf}#view=FitH&amp;navpanes=0" title="{e(title)}" loading="lazy"></iframe>
        </div>
        <div class="doc-actions">
          <a class="btn primary" href="{pdf}" download>Download PDF</a>
          <a class="btn" href="{pdf}" target="_blank" rel="noopener">Open full screen &#8599;</a>
        </div>"""


def results_block(d):
    if not d.get("results"):
        return ""
    img, url = d["results"]
    return f"""
        <figure class="p-results">
          <figcaption class="mono">Official results</figcaption>
          <img src="../assets/img/math-modeling/{img}" alt="Our team's row in the official results" loading="lazy" />
          <p>{link_out("Full results (PDF)", url)}</p>
        </figure>"""


def doc_block(p):
    return f"""
    <section class="p-content">
      <div class="wrap">
        {pdf_embed(p["title"], p["doc"])}{results_block(p["doc"])}
      </div>
    </section>
"""


def facts_block(d):
    if not d or not d.get("facts"):
        return ""
    rows = "".join(f'\n          <div><dt class="mono">{k}</dt><dd>{v}</dd></div>' for k, v in d["facts"])
    return f'\n        <dl class="p-facts">{rows}\n        </dl>'



def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def outline(body, prefix, taken):
    # give every h2/h3 an id (reusing the id of the section it opens) and return (body, [(level, id, num, text)])
    heads, out, last = [], [], 0
    for m in re.finditer(r'<h([23])([^>]*)>(.*?)</h\1>', body, re.S):
        level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
        num = re.search(r'<span class="a-num">(.*?)</span>', inner)
        text = re.sub(r"<[^>]+>", "", re.sub(r'<span class="a-num">.*?</span>', "", inner)).strip()
        own = re.search(r'\bid="([^"]+)"', attrs)
        sec = re.search(r'<section\b[^>]*\bid="([^"]+)"[^>]*>\s*(?:<!--.*?-->\s*)?$', body[last:m.start()], re.S)
        if own:
            hid = own.group(1)
        elif sec:
            hid = sec.group(1)
        else:
            hid = base = f"{prefix}-{slugify(text)}" if prefix else slugify(text)
            n = 2
            while hid in taken:
                hid, n = f"{base}-{n}", n + 1
            attrs += f' id="{hid}"'
        taken.add(hid)
        out.append(body[last:m.start()] + f"<h{level}{attrs}>{inner}</h{level}>")
        last = m.end()
        heads.append((level, hid, num.group(1) if num else "", text))
    out.append(body[last:])
    return "".join(out), heads


def toc_list(heads, indent):
    # nested list of h2 entries, each with its h3 entries
    pad = " " * indent
    html_, i = [], 0
    while i < len(heads):
        level, hid, num, text = heads[i]
        subs = []
        i += 1
        while i < len(heads) and heads[i][0] == 3:
            subs.append(heads[i])
            i += 1
        num_html = f'<span class="toc-num mono">{num}</span>' if num else ""
        row = f'{pad}<li><a href="#{hid}">{num_html}<span>{text}</span></a>'
        if subs:
            row += f'\n{pad}  <ol class="toc-sub">\n' + "\n".join(
                f'{pad}    <li><a href="#{h}">' + (f'<span class="toc-num mono">{n}</span>' if n else "") + f"<span>{t}</span></a></li>"
                for _, h, n, t in subs) + f"\n{pad}  </ol>\n{pad}"
        html_.append(row + "</li>")
    return "\n".join(html_)


def article_block(p):
    # write-up pages: contents column on the left that stays in view, write-up on the right
    taken = set()
    for part in p["doc"]["parts"]:
        raw = open(os.path.join(CONTENT, part["content"] + ".html")).read()
        taken |= set(re.findall(r'\bid="([^"]+)"', raw))
    body_html, toc_html = [], []
    for part in p["doc"]["parts"]:
        raw = open(os.path.join(CONTENT, part["content"] + ".html")).read()
        inner = re.search(r'<article class="article">\s*<div class="wrap">(.*)</div>\s*</article>', raw, re.S).group(1)
        if "title" in part:
            pid = part["content"]
            inner, heads = outline(inner, slugify(part["title"]), taken)
            body_html.append(f"""
        <section class="a-part" id="{pid}">
          <header class="a-part-head">
            <h2 class="display a-part-title">{e(part["title"])}</h2>
            <p class="a-part-desc">{e(part["blurb"])}</p>
          </header>
{inner.rstrip()}
        </section>""")
            toc_html.append(f'          <li class="toc-part"><a href="#{pid}">{e(part["title"])}</a>\n            <ol>\n'
                            + toc_list(heads, 14) + "\n            </ol>\n          </li>")
        else:
            inner, heads = outline(inner, "", taken)
            body_html.append(inner.rstrip())
            toc_html.append(toc_list(heads, 10))
    if p["doc"].get("attach"):
        body_html.append(f"""
        <section class="a-section" id="original-pdf">
          <h2>Original PDF</h2>
          {pdf_embed(p["title"], p["doc"]["attach"])}
        </section>""")
        toc_html.append('<li><a href="#original-pdf"><span>Original PDF</span></a></li>')
    return f"""
    <article class="article">
      <div class="wrap a-doc">
        <nav class="toc" aria-label="Contents">
          <button type="button" class="toc-toggle mono" aria-expanded="false">Contents<span class="caret" aria-hidden="true">&#9662;</span></button>
          <p class="toc-head mono">Contents</p>
          <ol class="toc-list">
{chr(10).join(toc_html)}
          </ol>
        </nav>
        <div class="a-doc-body">
{"".join(body_html)}
        </div>
      </div>
    </article>
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

    body = article_block(p) if d and "parts" in d else doc_block(p) if d else ""
    hero = f"""
  <main>
    <section class="p-hero">
      <div class="wrap">
        <div class="crumbs mono">{crumbs}</div>
        <h1 class="display p-title">{e(p["title"])}</h1>
        <!-- EDIT: description -->
        <p class="p-desc">{e(p["blurb"])}</p>{facts_block(d)}
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

# ---------- old links ----------
for old, new in MOVED.items():
    write(f"projects/{old}.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Moved</title>
  <link rel="canonical" href="{new}.html#{old}" />
  <meta http-equiv="refresh" content="0; url={new}.html#{old}" />
</head>
<body>
  <p>This page moved to <a href="{new}.html#{old}">{new}.html</a>.</p>
</body>
</html>
""")

# the old Useful Data page was split into one page per write-up; send its section links to the new pages
USEFUL_DATA = {"race-data-analysis": "race-data-analysis", "load-cases": "load-cases", "tire-analysis": "tire-analysis", "cfd-data": "aero-analysis"}
write("projects/useful-data.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Moved</title>
  <script>
    var to = {{{", ".join(f'"{k}": "{v}"' for k, v in USEFUL_DATA.items())}}};
    location.replace((to[location.hash.slice(1)] || "race-data-analysis") + ".html");
  </script>
</head>
<body>
  <p>This page was split up. Start at <a href="race-data-analysis.html">Race Data Analysis</a>.</p>
</body>
</html>
""")

print(len(pages), "pages")
