"""Compile every Suspension Lead page on the site into one PDF (cover + contents + pages).

Needs pymupdf:  python3 -m pip install pymupdf
"""
import os, re, subprocess, tempfile
from datetime import date
import pymupdf as fitz

ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
PROJECTS = os.path.join(ROOT, "projects")
OUT_PDF = os.path.join(ROOT, "assets", "docs", "ARG27_Suspension_Lead_Compilation.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# same order as the Suspension Lead list on the home page
PAGES = [
    "kinematics", "rates-and-parameters", "physical-tests", "race-data-analysis",
    "load-cases", "tire-analysis", "aero-analysis", "miscellaneous",
]

PRINT_CSS = """
<style>
  @page { size: Letter; margin: 0.6in 0.65in 0.75in; }
  body { background: #fff; }
  .site-notice, .topbar, .toc, .p-nav, .footer, .preview, .crumbs,
  .a-top, .cg-tools, summary { display: none !important; }
  .p-hero { border-bottom: 1px solid #141414; }
  .p-hero .wrap { padding: 0 0 16px; max-width: none; }
  .p-title { font-size: 34px; margin-top: 0; }
  .p-desc { font-size: 19px; margin-top: 12px; max-width: none; }
  .article { border: 0; }
  .article .wrap, .article .wrap.a-doc { display: block; max-width: none; padding: 0; }
  .a-section:first-child { padding-top: 20px; }
  .a-details { border: 0; }
  .a-details-body { padding-left: 0; padding-right: 0; }
  .a-table-wrap { overflow: visible; }
  pre { white-space: pre-wrap; word-break: break-word; }
  h2, h3, h4 { break-after: avoid; }
  .a-fig, .a-table-wrap, .eq, pre { break-inside: avoid; }
</style>
"""


def print_html(name):
    s = open(os.path.join(PROJECTS, name + ".html")).read()
    s = s.replace("<head>", f'<head>\n<base href="file://{PROJECTS}/">', 1)
    s = s.replace("</head>", PRINT_CSS + "</head>", 1)
    s = re.sub(r'<script[^>]*>.*?</script>', "", s, flags=re.S)
    s = s.replace("<details", "<details open")
    # interactive bits of the CG height page: typing prompt, live plot, embedded test plan
    s = re.sub(r'<!-- web-only -->(?:(?!<!-- /web-only -->).)*?(?:Type the balance|data-cg-plot).*?<!-- /web-only -->',
               "", s, flags=re.S)
    s = re.sub(r'<h3[^>]*><span class="a-num">[\d.]+</span>Downloadable Test Plan</h3>\s*<div class="a-download">.*?<div class="doc-actions">.*?</div>\s*</div>',
               "", s, flags=re.S)
    title = re.search(r'<h1 class="display p-title">(.*?)</h1>', s, re.S).group(1)
    return s, re.sub(r"<[^>]+>", "", title).replace("&amp;", "&").strip()


def render(html, path, tmp):
    src = os.path.join(tmp, os.path.basename(path) + ".html")
    open(src, "w").write(html)
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--allow-file-access-from-files", "--virtual-time-budget=10000",
        f"--print-to-pdf={path}", "file://" + src,
    ], check=True, capture_output=True)


def cover_html(rows):
    css = os.path.join(ROOT, "assets", "css", "style.css")
    logo = os.path.join(ROOT, "assets", "img", "cornell-racing-logo.png")
    items = "\n".join(
        f'<li><span class="n mono">{i}</span><span class="t">{t}</span><span class="p mono">{p}</span></li>'
        for i, (t, p) in enumerate(rows, 1))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" />
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="file://{css}" />
<style>
  @page {{ size: Letter; margin: 0.9in 0.85in; }}
  body {{ background: #fff; }}
  .head {{ position: relative; border-bottom: 1px solid #141414; padding-bottom: 18px; }}
  .head img {{ position: absolute; top: 0; right: 0; height: 0.5in; }}
  h1 {{ font-weight: 400; font-size: 34pt; line-height: 1.1; margin: 0 0 8px; }}
  .sub {{ font-size: 15pt; color: #6c6b66; }}
  .by {{ margin-top: 14px; font-size: 9pt; }}
  h2 {{ font-weight: 400; font-size: 17pt; margin: 36px 0 10px; }}
  ol {{ list-style: none; margin: 0; padding: 0; }}
  li {{ display: flex; align-items: baseline; gap: 14px; padding: 9px 0; border-bottom: 1px solid #d9d8d3; font-size: 13pt; }}
  li .n {{ width: 22px; font-size: 9pt; color: #6c6b66; }}
  li .t {{ flex: 1; }}
  li .p {{ font-size: 10pt; }}
</style></head><body>
<div class="head">
  <img src="file://{logo}" alt="Cornell Racing" />
  <h1>Suspension Lead Work</h1>
  <div class="sub">Cornell Racing, ARG27</div>
  <div class="by mono">Davis Rattanavijai &middot; Compiled {date.today():%B} {date.today().day}, {date.today().year}</div>
</div>
<h2>Contents</h2>
<ol>{items}</ol>
</body></html>"""


with tempfile.TemporaryDirectory() as tmp:
    parts = []
    for name in PAGES:
        html, title = print_html(name)
        pdf = os.path.join(tmp, name + ".pdf")
        render(html, pdf, tmp)
        parts.append((title, pdf))

    # cover is one page, so section k starts after the cover and the sections before it
    counts = [fitz.open(p).page_count for _, p in parts]
    starts = [2 + sum(counts[:i]) for i in range(len(parts))]
    cover = os.path.join(tmp, "cover.pdf")
    render(cover_html([(t, s) for (t, _), s in zip(parts, starts)]), cover, tmp)

    out = fitz.open(cover)
    toc = [[1, "Contents", 1]]
    for (title, pdf), start in zip(parts, starts):
        out.insert_pdf(fitz.open(pdf))
        toc.append([1, title, start])
    out.set_toc(toc)

    for i, page in enumerate(out):
        if i == 0:
            continue
        r = page.rect
        label = f"{i + 1}"
        w = fitz.get_text_length(label, fontname="tiro", fontsize=9)
        page.insert_text(((r.width - w) / 2, r.height - 0.4 * 72), label,
                         fontname="tiro", fontsize=9, color=(0.42, 0.42, 0.4))

    # screenshots are embedded at full resolution; 200 dpi keeps them sharp at a fraction of the size
    out.rewrite_images(dpi_threshold=220, dpi_target=200, quality=85)
    out.set_metadata({"title": "Suspension Lead Work", "author": "Davis Rattanavijai"})
    out.save(OUT_PDF, garbage=3, deflate=True)
    print("wrote", OUT_PDF, out.page_count, "pages,", os.path.getsize(OUT_PDF) // 1024, "KB")
