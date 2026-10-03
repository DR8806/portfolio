"""Build the downloadable Method A test plan PDF from the CG height page content."""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
SRC = os.path.join(HERE, "content", "cg-height-test.html")
OUT_HTML = os.path.join(HERE, "print.html")
OUT_PDF = os.path.join(ROOT, "assets", "docs", "ARG27_CG_Height_Test_Method_A.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

s = open(SRC).read()

purpose = re.search(r'<section class="a-section" id="purpose">.*?<p>(.*?)</p>', s, re.S).group(1)
method_a = re.search(r'(<section class="a-section" id="method-a">.*?</section>)', s, re.S).group(1)
refs = re.search(r'(<ol class="a-refs">.*?</ol>)', s, re.S).group(1)

# the PDF doesn't need web-only bits
method_a = re.sub(r'\s*<p class="a-top">.*?</p>', "", method_a)
method_a = re.sub(r'\s*<h3><span class="a-num">[\d.]+</span>Downloadable Test Plan</h3>\s*<div class="a-download">.*?</div>\s*</div>', "", method_a, flags=re.S)
method_a = re.sub(r'\s*<!-- web-only -->.*?<!-- /web-only -->', "", method_a, flags=re.S)
method_a = re.sub(r'<input[^>]*>', "", method_a)
method_a = re.sub(r'<details class="a-details">\s*<summary>[^<]*</summary>', '<div class="a-derivation"><p class="mono deriv-label">Derivation</p>', method_a)
method_a = method_a.replace("</details>", "</div>")  # interactive cells become blank write-in cells
method_a = re.sub(r'\s*<!--.*?-->', "", method_a)

css = os.path.join(ROOT, "assets", "css", "style.css")
logo = os.path.join(ROOT, "assets", "img", "cornell-racing-logo.png")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>ARG26 CG Height Test Plan: Method A</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="file://{css}" />
<style>
  @page {{ size: Letter; margin: 0.6in 0.65in 0.7in; }}
  body {{ background: #fff; font-size: 11pt; }}
  .article {{ border: 0; }}
  .article .wrap {{ max-width: none; padding: 0; }}
  .doc-title {{ border-bottom: 1px solid #141414; padding-bottom: 14px; margin-bottom: 4px; }}
  .doc-title {{ position: relative; }}
  .doc-logo {{ position: absolute; top: 0; right: 0; height: 0.42in; width: auto; }}
  .doc-title .byline {{ margin-top: 10px; }}
  .a-derivation {{ margin: 6px 0 10px; padding: 4px 14px 2px; border-left: 2px solid #d9d8d3; }}
  .a-derivation .a-details-body {{ padding: 0; border: 0; }}
  .article .deriv-label {{ margin: 6px 0 2px; font-size: 9pt; }}
  .doc-title h1 {{  font-weight: 400; font-size: 26pt; line-height: 1.1; margin: 6px 0 4px; }}
  .doc-title .sub {{ font-size: 14pt; color: #6c6b66; }}
  .article h2 {{ font-size: 17pt; margin-bottom: 10px; }}
  .article h3 {{ font-size: 13pt; margin: 20px 0 8px; break-after: avoid; }}
  .article p, .article li, .article dd {{ font-size: 11pt; line-height: 1.5; }}
  .article .eq {{ font-size: 13pt; margin: 4px 0 12px; }}
  .a-section {{ padding-top: 14px; }}
  .a-section + .a-section {{ margin-top: 14px; }}
  .a-fig {{ margin: 14px 0 16px; }}
  .a-diagram svg {{ max-width: 4.6in; }}
  .a-fig figcaption {{ font-size: 9.5pt; max-width: 4.6in; }}
  .a-table.sheet {{ font-size: 10pt; }}
  .a-table.sheet td {{ height: 26px; }}
  .a-table.sheet td:empty {{ min-width: 80px; }}
  .a-refs li {{ font-size: 10pt; }}
  /* tables: centered, never split across pages */
  .a-table-wrap {{ overflow: visible; display: flex; justify-content: center; break-inside: avoid; margin: 12px 0; }}
  .a-table.sheet {{ margin: 0 auto; }}
  .a-derivation, .eq {{ break-inside: avoid; }}
  h3, h4 {{ break-after: avoid; }}
  p:has(+ .a-table-wrap), p:has(+ .eq) {{ break-after: avoid; }}  /* keep a lead-in line with what it introduces */
  /* the three data cases share one page */
  .cg-case[data-case="0"] {{ break-before: page; }}
  .cg-case {{ break-inside: avoid; margin-top: 0; }}
  .cg-case + .cg-case {{ margin-top: 10px; }}
  .cg-case-grid {{ justify-content: center; gap: 0 22px; }}
  .cg-case-grid .a-table-wrap {{ margin: 6px 0; }}
  .cg-case .a-table.sheet td {{ height: 21px; padding: 2px 10px; }}
  .cg-case .a-table.sheet th {{ padding: 4px 10px; }}
  .cg-case h4.cg-case-title {{ justify-content: center; margin: 4px 0 0; }}
  /* references alone on the last page */
  .refs-page {{ break-before: page; border-top: 0 !important; margin-top: 0 !important; }}
  .a-table tr {{ break-inside: avoid; }}
  .a-table thead {{ display: table-header-group; }}
  .a-fig {{ break-inside: avoid; }}
  h2, h3 {{ break-after: avoid; }}
  h4.cg-case-title {{ font-size: 12pt; margin: 14px 0 0; }}
  .cg-case {{ break-inside: avoid; margin-top: 8px; }}
  .cg-case-grid {{ gap: 0 18px; }}
  .a-table.sheet td.cg-in {{ min-width: 90px; }}
  .a-table.sheet td.cg-in:last-child {{ min-width: 150px; }}
</style>
</head>
<body>
<article class="article">
  <div class="wrap">
    <header class="doc-title">
      <img class="doc-logo" src="file://{logo}" alt="Cornell Racing Project Team" />
      <h1>CG Height Test Plan</h1>
      <div class="sub">Method A: Side Tilt (Balance) Test</div>
      <div class="byline mono">Davis Rattanavijai &middot; Last edited October 2, 2026</div>
    </header>
    <section class="a-section">
      <h2><span class="a-num">1</span>Purpose</h2>
      <p>{purpose}</p>
    </section>
    {method_a}
    <section class="a-section refs-page">
      <h2><span class="a-num">3</span>References</h2>
      {refs}
    </section>
  </div>
</article>
</body>
</html>
"""
open(OUT_HTML, "w").write(html)

subprocess.run([
    CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    "--allow-file-access-from-files", "--virtual-time-budget=8000",
    f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML,
], check=True, capture_output=True)
print("wrote", OUT_PDF, os.path.getsize(OUT_PDF), "bytes")
