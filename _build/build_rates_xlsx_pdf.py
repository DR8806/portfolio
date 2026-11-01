"""Render every sheet of the ARG27 Rates workbook to one Letter page each, straight from the .xlsx.

Reads cached values, cell styles, merged cells and conditional formatting with openpyxl, lays each
sheet out as an HTML table, scales it to fit one page and prints it with headless Chrome.
Needs: python3 -m pip install openpyxl pymupdf matplotlib

usage: python3 build_rates_xlsx_pdf.py [workbook.xlsx] [out.pdf]
"""
import colorsys, html, io, os, re, subprocess, sys, tempfile, zipfile
from datetime import date, datetime
import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string, range_boundaries
import pymupdf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
SRC = sys.argv[1] if len(sys.argv) > 1 else "/Users/davisrattanavijai/Desktop/ARG27 Rates (davis live edit).xlsx"
OUT_PDF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "assets", "docs", "ARG27_Rates_Spreadsheet.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = "/Applications/Microsoft Excel.app/Contents/Resources/DFonts"
MARGIN_IN = 0.45
for f in ("Calibri.ttf", "Calibrib.ttf"):
    if os.path.exists(os.path.join(FONTS, f)):
        font_manager.fontManager.addfont(os.path.join(FONTS, f))

wb = openpyxl.load_workbook(SRC)
vals = openpyxl.load_workbook(SRC, data_only=True)

# ---------- colors ----------

theme_xml = zipfile.ZipFile(SRC).read("xl/theme/theme1.xml").decode()
scheme = {}
for tag in ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"]:
    m = re.search(rf"<a:{tag}>.*?(?:srgbClr val|lastClr)=\"([0-9A-Fa-f]{{6}})\"", theme_xml, re.S)
    scheme[tag] = m.group(1)
THEME = [scheme[k] for k in ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"]]


def tinted(hex6, tint):
    r, g, b = (int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l * (1 + tint) if tint < 0 else l + (1 - l) * tint
    return "".join(f"{round(c * 255):02X}" for c in colorsys.hls_to_rgb(h, l, s))


def color(c, default=None):
    if c is None:
        return default
    try:
        if c.type == "rgb" and isinstance(c.rgb, str):
            return "#" + c.rgb[-6:]
        if c.type == "theme" and c.theme is not None and c.theme < len(THEME):
            return "#" + tinted(THEME[c.theme], c.tint or 0)
        if c.type == "indexed" and c.indexed not in (64, None):
            from openpyxl.styles.colors import COLOR_INDEX
            return "#" + COLOR_INDEX[c.indexed][-6:]
    except Exception:
        pass
    return default


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


# ---------- number formats ----------

def general(v, chars):
    if v == 0:
        return "0"
    if abs(v) >= 1e11 or abs(v) < 1e-9:
        return f"{v:.5E}".replace("E+0", "E+").replace("E-0", "E-")
    v = float(f"{v:.10g}")
    for d in range(9, -1, -1):
        s = f"{v:.{d}f}".rstrip("0").rstrip(".") if d else f"{v:.0f}"
        if len(s) <= max(chars, 1):
            return s
    return s


def fmt(v, nf, chars):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (datetime, date)):
        return v.strftime("%m-%d-%y") if "yy" in nf else v.strftime("%Y-%m-%d")
    if isinstance(v, str):
        return v
    sec = re.sub(r'\[[^\]]*\]|"[^"]*"|\\.|_.', "", nf.split(";")[1 if v < 0 and ";" in nf else 0])
    if nf in ("General", "@") or not re.search(r"[0#]", sec):
        return general(v, chars)
    pct = "%" in sec
    x = abs(v) * 100 if pct else abs(v)
    dec = len(re.search(r"\.([0#]*)", sec).group(1)) if "." in sec else 0
    s = f"{x:,.{dec}f}" if "," in sec else f"{x:.{dec}f}"
    if v < 0 and ";" not in nf and float(s.replace(",", "")) != 0:
        s = "-" + s
    return s + ("%" if pct else "")


# ---------- conditional formatting ----------

REF = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\w(])")


class XlErr:
    pass


def SEARCH(needle, hay, start=1):
    i = str(hay).lower().find(str(needle).lower(), start - 1)
    return XlErr() if i < 0 else i + 1


FUNCS = {
    "IF": lambda c, a, b=False: a if c else b, "ABS": abs, "NOT": lambda x: not x,
    "AND": lambda *a: all(a), "OR": lambda *a: any(a), "ISERROR": lambda x: isinstance(x, XlErr),
    "SEARCH": SEARCH, "ISBLANK": lambda x: x in (None, ""), "TRUE": True, "FALSE": False,
}


def evaluate(formula, grid, dr, dc):
    """Evaluate a conditional format formula for the cell offset (dr, dc) from the range's anchor."""
    parts = formula.split('"')
    for i in range(0, len(parts), 2):  # outside string literals
        p = parts[i]
        p = REF.sub(lambda m: f"_v({int(m.group(4)) + (0 if m.group(3) else dr)},"
                              f"{column_index_from_string(m.group(2)) + (0 if m.group(1) else dc)})", p)
        p = p.replace("<>", "!=")
        p = re.sub(r"(?<![<>!=])=(?!=)", "==", p)
        parts[i] = p
    expr = '"'.join(parts)
    env = dict(FUNCS, _v=lambda r, c: grid.get((r, c)) if grid.get((r, c)) is not None else 0)
    try:
        return eval(expr, {"__builtins__": {}}, env)
    except Exception:
        return False


def cf_styles(ws, grid):
    out = {}  # (r, c) -> {"bg":..., "fg":..., "b":...}
    rules = []
    for rng in ws.conditional_formatting:
        for rule in rng.rules:
            rules.append((rule.priority or 0, str(rng.sqref), rule))
    for _, sqref, rule in sorted(rules, key=lambda t: -t[0]):  # lowest priority number applied last, so it wins
        boxes = [range_boundaries(b) for b in sqref.split()]
        cells = [(r, c) for (c1, r1, c2, r2) in boxes for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        ar, ac = boxes[0][1], boxes[0][0]
        if rule.type == "colorScale":
            cs = rule.colorScale
            nums = [grid[k] for k in cells if isinstance(grid.get(k), (int, float)) and not isinstance(grid.get(k), bool)]
            if not nums:
                continue
            lo, hi = min(nums), max(nums)

            def point(cfvo):
                if cfvo.type == "min": return lo
                if cfvo.type == "max": return hi
                if cfvo.type == "num": return float(cfvo.val)
                if cfvo.type == "percent": return lo + (hi - lo) * float(cfvo.val) / 100
                if cfvo.type == "percentile":
                    s = sorted(nums); k = (len(s) - 1) * float(cfvo.val) / 100
                    f = int(k); return s[f] + (s[min(f + 1, len(s) - 1)] - s[f]) * (k - f)
                return lo
            stops = [(point(v), color(c)) for v, c in zip(cs.cfvo, cs.color)]
            for k in cells:
                v = grid.get(k)
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    continue
                if v <= stops[0][0]:
                    col = stops[0][1]
                elif v >= stops[-1][0]:
                    col = stops[-1][1]
                else:
                    for (a, ca), (b, cb) in zip(stops, stops[1:]):
                        if a <= v <= b:
                            col = mix(ca, cb, 0 if b == a else (v - a) / (b - a)); break
                out.setdefault(k, {})["bg"] = col
            continue
        d = rule.dxf
        if d is None:
            continue
        style = {}
        if d.fill is not None:
            bg = color(d.fill.bgColor) or color(d.fill.fgColor)
            if bg: style["bg"] = bg
        if d.font is not None:
            if d.font.color is not None and color(d.font.color): style["fg"] = color(d.font.color)
            if d.font.b: style["b"] = True
        for (r, c) in cells:
            v = grid.get((r, c))
            if rule.type == "containsText":
                hit = rule.text is not None and v is not None and str(rule.text).lower() in str(v).lower()
            elif rule.type == "cellIs":
                f = [evaluate(x, grid, r - ar, c - ac) for x in rule.formula]
                n = v if v is not None else 0
                try:
                    hit = {"lessThan": lambda: n < f[0], "greaterThan": lambda: n > f[0],
                           "lessThanOrEqual": lambda: n <= f[0], "greaterThanOrEqual": lambda: n >= f[0],
                           "equal": lambda: n == f[0], "notEqual": lambda: n != f[0],
                           "between": lambda: min(f) <= n <= max(f),
                           "notBetween": lambda: not (min(f) <= n <= max(f))}[rule.operator]()
                except Exception:
                    hit = False
            elif rule.type == "expression":
                hit = bool(evaluate(rule.formula[0], grid, r - ar, c - ac))
            else:
                hit = False
            if hit:
                out.setdefault((r, c), {}).update(style)
    return out


# ---------- layout ----------

def col_px(ws, c):
    dim = ws.column_dimensions.get(get_column_letter(c))
    if dim is not None and dim.hidden:
        return 0
    w = dim.width if dim is not None and dim.customWidth and dim.width else None
    if w is None:
        w = ws.sheet_format.defaultColWidth or (ws.sheet_format.baseColWidth or 8) + 0.71
    return int(w * 7 + 5)


def row_px(ws, r):
    dim = ws.row_dimensions.get(r)
    if dim is not None and dim.hidden:
        return 0
    h = dim.height if dim is not None and dim.height else (ws.sheet_format.defaultRowHeight or 15)
    return round(h * 4 / 3)


BORDER = {"thin": "1px solid", "medium": "2px solid", "thick": "3px solid", "double": "3px double",
          "hair": "1px solid", "dotted": "1px dotted", "dashed": "1px dashed", "mediumDashed": "2px dashed",
          "dashDot": "1px dashed", "mediumDashDot": "2px dashed", "dashDotDot": "1px dotted",
          "mediumDashDotDot": "2px dotted", "slantDashDot": "2px dashed"}


def side(s):
    if s is None or not s.style:
        return None
    return f"{BORDER.get(s.style, '1px solid')} {color(s.color, '#000000')}"


def chart_svg(ws, anchor_px):
    """Re-draw the workbook's bar charts from their cached data."""
    out = []
    for ch in ws._charts:
        try:
            ser = ch.series[0]
            cats = [p.v for p in ser.cat.strRef.strCache.pt] if ser.cat.strRef else [p.v for p in ser.cat.numRef.numCache.pt]
            ys = [float(p.v) for p in ser.val.numRef.numCache.pt]
        except Exception:
            continue

        def rich(t):
            try:
                return "".join(r.t for p in t.tx.rich.p for r in (p.r or []))
            except Exception:
                return ""
        a = ch.anchor
        x0, y0 = anchor_px(a._from.col, a._from.colOff, a._from.row, a._from.rowOff)
        x1, y1 = anchor_px(a.to.col, a.to.colOff, a.to.row, a.to.rowOff)
        w, h = x1 - x0, y1 - y0
        plt.rcParams["font.family"] = ["Calibri", "Arial", "sans-serif"]
        fig, ax = plt.subplots(figsize=(w / 96, h / 96), dpi=96)
        bars = ax.bar(cats, ys, color="#" + THEME[4], width=0.6)
        ax.bar_label(bars, labels=[f"{y:.1f}" for y in ys], fontsize=8, padding=2)
        ax.axhline(0, color="#bfbfbf", lw=0.8)
        ax.set_title(rich(ch.title) if ch.title else "", fontsize=12)
        if ch.x_axis.title: ax.set_xlabel(rich(ch.x_axis.title), fontsize=9)
        if ch.y_axis.title: ax.set_ylabel(rich(ch.y_axis.title), fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", color="#d9d9d9", lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        buf = io.StringIO()
        fig.savefig(buf, format="svg")
        plt.close(fig)
        svg = re.sub(r"^.*?(<svg)", r"\1", buf.getvalue(), flags=re.S)
        out.append(f'<div class="chart" style="left:{x0}px;top:{y0}px;width:{w}px;height:{h}px;border:1px solid #d9d9d9">{svg}</div>')
    return "".join(out)


def sheet_html(ws, wv):
    grid = {(c.row, c.column): wv.cell(c.row, c.column).value for row in ws.iter_rows() for c in row}
    cf = cf_styles(ws, grid)

    # print range: used cells plus anything a chart covers
    used = [(r, c) for (r, c) in grid if grid[(r, c)] is not None or ws.cell(r, c).fill.fill_type
            or any(getattr(ws.cell(r, c).border, s).style for s in ("left", "right", "top", "bottom"))]
    used += [k for k in cf]
    chart_ends = [(ch.anchor.to.col + 1, ch.anchor.to.row + 1) for ch in ws._charts]
    r1 = min(r for r, _ in used); c1 = min(c for _, c in used)
    r2 = max([r for r, _ in used] + [r for _, r in chart_ends])
    c2 = max([c for _, c in used] + [c for c, _ in chart_ends])

    widths = {c: col_px(ws, c) for c in range(c1, c2 + 1)}
    heights = {r: row_px(ws, r) for r in range(r1, r2 + 1)}

    merged = {}
    skip = set()
    for m in ws.merged_cells.ranges:
        merged[(m.min_row, m.min_col)] = m
        for r in range(m.min_row, m.max_row + 1):
            for c in range(m.min_col, m.max_col + 1):
                if (r, c) != (m.min_row, m.min_col):
                    skip.add((r, c))

    rows = []
    for r in range(r1, r2 + 1):
        if heights[r] == 0:
            continue
        tds = []
        for c in range(c1, c2 + 1):
            if widths[c] == 0 or (r, c) in skip:
                continue
            cell = ws.cell(r, c)
            v = grid.get((r, c))
            css = []
            attrs = ""
            m = merged.get((r, c))
            span_w = widths[c]
            if m:
                attrs = f' colspan="{m.max_col - m.min_col + 1}" rowspan="{m.max_row - m.min_row + 1}"'
                span_w = sum(widths.get(k, 0) for k in range(m.min_col, m.max_col + 1))
            f = cell.font
            if f is not None:
                if f.b: css.append("font-weight:700")
                if f.sz and f.sz != 11: css.append(f"font-size:{f.sz}pt")
                if f.u: css.append("text-decoration:underline")
                if f.strike: css.append("text-decoration:line-through")
                fg = color(f.color)
                if fg and fg.upper() != "#000000": css.append(f"color:{fg}")
            if cell.fill is not None and cell.fill.fill_type == "solid":
                bg = color(cell.fill.fgColor)
                if bg: css.append(f"background:{bg}")
            b = cell.border
            edges = {"left": b.left, "top": b.top, "right": b.right, "bottom": b.bottom}
            if m:
                edges["right"] = ws.cell(m.min_row, m.max_col).border.right
                edges["bottom"] = ws.cell(m.max_row, m.min_col).border.bottom
            for k, s in edges.items():
                s = side(s)
                if s: css.append(f"border-{k}:{s}")
            al = cell.alignment
            h = al.horizontal or "general"
            if h == "general":
                h = "right" if isinstance(v, (int, float)) and not isinstance(v, bool) else ("center" if isinstance(v, bool) else "left")
            h = {"centerContinuous": "center", "fill": "left", "distributed": "center"}.get(h, h)
            if h != "left": css.append(f"text-align:{h}")
            va = {"center": "middle", "top": "top", "distributed": "middle", "justify": "middle"}.get(al.vertical, "bottom")
            if va != "bottom": css.append(f"vertical-align:{va}")
            if al.indent: css.append(f"padding-left:{2 + 9 * al.indent}px")
            if al.wrap_text:
                css.append("white-space:normal")
            elif isinstance(v, str) and h == "left" and not m:
                # text spills into empty cells to its right, like Excel
                if grid.get((r, c + 1)) is not None:
                    css.append("overflow:hidden")
            else:
                css.append("overflow:hidden")
            extra = cf.get((r, c), {})
            if "bg" in extra: css.append(f"background:{extra['bg']}")
            if "fg" in extra: css.append(f"color:{extra['fg']}")
            if extra.get("b"): css.append("font-weight:700")
            text = html.escape(fmt(v, cell.number_format, max(1, (span_w - 5) // 7)))
            st = f' style="{";".join(css)}"' if css else ""
            tds.append(f"<td{attrs}{st}>{text}</td>")
        rows.append(f'<tr style="height:{heights[r]}px">{"".join(tds)}</tr>')

    xs, acc = {}, 0
    for c in range(c1, c2 + 2):
        xs[c] = acc; acc += widths.get(c, 0)
    ys, acc = {}, 0
    for r in range(r1, r2 + 2):
        ys[r] = acc; acc += heights.get(r, 0)

    def anchor_px(col0, coff, row0, roff):
        c, r = col0 + 1, row0 + 1
        return (xs.get(c, xs[max(xs)]) + coff / 9525, ys.get(r, ys[max(ys)]) + roff / 9525)

    charts = chart_svg(ws, anchor_px)
    cols = "".join(f'<col style="width:{widths[c]}px">' for c in range(c1, c2 + 1) if widths[c])
    total_w = sum(widths.values())
    total_h = sum(heights.values())
    table = f'<table style="width:{total_w}px"><colgroup>{cols}</colgroup>{"".join(rows)}</table>'
    return table, charts, total_w, total_h


def page_html(table, charts, w, h):
    # one tall page at full size; it is scaled onto Letter afterwards, so the vectors stay sharp
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
  @font-face {{ font-family: Calibri; src: url("file://{FONTS}/Calibri.ttf"); }}
  @font-face {{ font-family: Calibri; font-weight: 700; src: url("file://{FONTS}/Calibrib.ttf"); }}
  @page {{ size: {w + 40}px {int(h * 1.5) + 200}px; margin: 0; }}
  html, body {{ margin: 0; }}
  .sheet {{ position: relative; width: max-content; }}
  table {{ border-collapse: collapse; table-layout: fixed; font: 11pt Calibri, Arial, sans-serif; color: #000; }}
  td {{ padding: 0 2px; white-space: nowrap; vertical-align: bottom; line-height: 1.15; }}
  .chart {{ position: absolute; background: #fff; }}
  .chart svg {{ width: 100%; height: 100%; display: block; }}
</style></head><body><div class="sheet">{table}{charts}</div></body></html>"""


def content_box(page):
    boxes = [pymupdf.Rect(r) for _, r in page.get_bboxlog()]
    boxes = [b for b in boxes if not b.is_empty and b.width < page.rect.width * 0.999]
    box = pymupdf.Rect(boxes[0])
    for b in boxes[1:]:
        box |= b
    return box & page.rect


with tempfile.TemporaryDirectory() as tmp:
    out = pymupdf.open()
    toc = []
    font = os.path.join(FONTS, "Calibri.ttf")
    bold = os.path.join(FONTS, "Calibrib.ttf")
    for i, ws in enumerate(wb.worksheets):
        if ws.sheet_state != "visible":
            continue
        table, charts, w, h = sheet_html(ws, vals[ws.title])
        src = os.path.join(tmp, f"s{i}.html")
        pdf = os.path.join(tmp, f"s{i}.pdf")
        open(src, "w").write(page_html(table, charts, w, h))
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", "--virtual-time-budget=5000",
                        f"--print-to-pdf={pdf}", "file://" + src], check=True, capture_output=True)
        full = pymupdf.open(pdf)
        if full.page_count != 1:
            print(f"warning: {ws.title} ran past one tall page")
        clip = content_box(full[0])
        clip = pymupdf.Rect(0, 0, clip.x1, clip.y1)  # keep the sheet's own top-left origin

        # whichever orientation lets the sheet print larger
        m = MARGIN_IN * 72
        label_h = 24
        def fit(pw, ph):
            return min(1, (pw - 2 * m) / clip.width, (ph - 2 * m - label_h) / clip.height)
        landscape = fit(792, 612) > fit(612, 792)
        pw, ph = (792, 612) if landscape else (612, 792)
        k = fit(pw, ph)
        page = out.new_page(width=pw, height=ph)
        page.insert_font(fontname="cal", fontfile=font)
        page.insert_font(fontname="calb", fontfile=bold)
        page.insert_text((m, m + 11), ws.title, fontname="calb", fontsize=12)
        tw = pymupdf.Font(fontfile=font).text_length("ARG27 Rates", fontsize=10)
        page.insert_text((pw - m - tw, m + 11), "ARG27 Rates", fontname="cal", fontsize=10, color=(0.35, 0.35, 0.35))
        page.draw_line((m, m + 17), (pw - m, m + 17), color=(0.75, 0.75, 0.75), width=0.6)
        target = pymupdf.Rect(m, m + label_h, m + clip.width * k, m + label_h + clip.height * k)
        page.show_pdf_page(target, full, 0, clip=clip)
        toc.append([1, ws.title, out.page_count])
        print(f"{ws.title:30s} {'landscape' if landscape else 'portrait '} scale {k:.2f}")
    out.set_toc(toc)
    out.set_metadata({"title": "ARG27 Rates", "author": "Davis Rattanavijai"})
    out.save(OUT_PDF, garbage=3, deflate=True)
    print("wrote", OUT_PDF, out.page_count, "pages,", os.path.getsize(OUT_PDF) // 1024, "KB")
