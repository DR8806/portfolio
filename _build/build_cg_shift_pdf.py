"""Build the downloadable CG shift calculation PDF from the CG shift page content."""
import os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
SRC = os.path.join(HERE, "content", "cg-shift.html")
OUT_HTML = os.path.join(HERE, "print-cg-shift.html")
OUT_PDF = os.path.join(ROOT, "assets", "docs", "ARG27_CG_Shift_Calculation.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

s = open(SRC).read()

byline = re.search(r'<p class="a-byline mono">(.*?)</p>', s).group(1)
body = re.search(r'(<section class="a-section" id="context">.*</section>)', s, re.S).group(1)
# shrink images to print size so the PDF stays small enough to email
tmp = tempfile.mkdtemp()
def small(m):
    src = os.path.join(ROOT, m.group(1))
    out = os.path.join(tmp, os.path.splitext(os.path.basename(src))[0] + ".jpg")
    subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", "-s", "formatOptions", "82", src, "--out", out],
                   check=True, capture_output=True)
    return f'src="file://{out}"'
body = re.sub(r'src="\.\./(assets/[^"]+)"', small, body)
body = re.sub(r'<a href="\.\./assets/[^"]*"[^>]*>(<img[^>]*>)</a>', r"\1", body)  # no click-to-enlarge in print
body = body.replace(' loading="lazy"', "")

css = os.path.join(ROOT, "assets", "css", "style.css")
logo = os.path.join(ROOT, "assets", "img", "cornell-racing-logo.png")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>ARG27 CG Shift Calculation</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="file://{css}" />
<style>
  @page {{ size: Letter; margin: 0.6in 0.65in 0.7in; }}
  body {{ background: #fff; font-size: 11pt; }}
  .article {{ border: 0; }}
  .article .wrap {{ max-width: none; padding: 0; }}
  .doc-title {{ position: relative; border-bottom: 1px solid #141414; padding-bottom: 14px; margin-bottom: 4px; }}
  .doc-logo {{ position: absolute; top: 0; right: 0; height: 0.42in; width: auto; }}
  .doc-title h1 {{ font-weight: 400; font-size: 26pt; line-height: 1.1; margin: 6px 0 4px; }}
  .doc-title .sub {{ font-size: 14pt; color: #6c6b66; }}
  .doc-title .byline {{ margin-top: 10px; }}
  .article h2 {{ font-size: 17pt; margin-bottom: 10px; }}
  .article h3 {{ font-size: 13pt; margin: 20px 0 8px; }}
  .article p, .article li {{ font-size: 11pt; line-height: 1.5; }}
  .article .eq {{ font-size: 13pt; margin: 4px 0 12px; }}
  .article a {{ color: inherit; text-decoration: none; }}
  .article .a-note {{ font-size: 10.5pt; line-height: 1.45; margin: 14px 0 14px !important; }}
  .a-section {{ padding-top: 14px; }}
  .a-section + .a-section {{ margin-top: 14px; }}
  .a-fig {{ margin: 14px 0 16px; break-inside: avoid; }}
  .a-fig img {{ max-width: 5.2in; max-height: 6.4in; width: auto; }}
  .a-fig--chart img {{ max-width: 3.6in; max-height: 4.05in; }}
  .a-fig--wide img {{ max-width: 100%; }}
  .a-fig figcaption {{ font-size: 9.5pt; max-width: 5.2in; }}
  .a-fig--wide figcaption {{ max-width: none; }}
  .a-table.sheet {{ font-size: 10pt; margin: 0 auto; }}
  .a-table.sheet td {{ height: 24px; }}
  .a-table-wrap {{ overflow: visible; display: flex; justify-content: center; break-inside: avoid; margin: 12px 0; }}
  .a-table.sheet.a-sources {{ width: 100%; }}
  .a-table.sheet.a-sources td:last-child {{ min-width: 0; }}
  .a-table tr {{ break-inside: avoid; }}
  .a-table thead {{ display: table-header-group; }}
  .eq {{ break-inside: avoid; }}
  h2, h3 {{ break-after: avoid; }}
  p:has(+ .a-table-wrap), p:has(+ .eq) {{ break-after: avoid; }}  /* keep a lead-in line with what it introduces */
  #appendix {{ break-before: page; }}
</style>
</head>
<body>
<article class="article">
  <div class="wrap">
    <header class="doc-title">
      <img class="doc-logo" src="file://{logo}" alt="Cornell Racing Project Team" />
      <h1>CG Shift Calculation</h1>
      <div class="sub">Preliminary ARG27 longitudinal CG shift from the accumulator and inverter changes</div>
      <div class="byline mono">{byline}</div>
    </header>
    {body}
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
