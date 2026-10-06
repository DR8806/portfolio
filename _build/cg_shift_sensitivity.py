"""Write the error sensitivity section of the CG shift page.

Recomputes the longitudinal CG shift while one ARG27 input is varied and the rest
stay at their nominal values, then writes four line charts (inline SVG) and a
summary table between the sensitivity markers in content/cg-shift.html.
Run it after changing any input, then run gen.py.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "content", "cg-shift.html")

# ---------- model (same inputs as the page) ----------
M26, X26 = 470.0, -20.289 - 61 * 0.5
M_ACC26, X_ACC26 = 102.0, -64.0
M_INV26, X_INV26 = 34.17, -78.2
M_OTHER = M26 - M_ACC26 - M_INV26
X_OTHER = (M26 * X26 - M_ACC26 * X_ACC26 - M_INV26 * X_INV26) / M_OTHER

REAR_FACE = -81.676      # monocoque rear inner face
INV_LEN = 13.5           # ARG27 inverter enclosure length along x
NOM = dict(
    m_acc=95.0,
    x_acc=X_ACC26 - (7.25 - 50 / 25.4) / 2,      # grows rearward to 50 mm from the rear face
    m_inv=15.0,
    x_inv=REAR_FACE + INV_LEN * (1 - 0.60),      # 60% rearward weight bias
)


def shift(**kw):
    v = {**NOM, **kw}
    m27 = M_OTHER + v["m_acc"] + v["m_inv"]
    x27 = (M_OTHER * X_OTHER + v["m_acc"] * v["x_acc"] + v["m_inv"] * v["x_inv"]) / m27
    return x27 - X26


BASE = shift()
M27 = M_OTHER + NOM["m_acc"] + NOM["m_inv"]
X27 = X26 + BASE

# ---------- chart drawing ----------
W, H = 380, 236
L, R, T, B = 46, 48, 18, 44
WHEELBASE = 61.0
FRONT_TICKS = [1.0, 1.5, 2.0]   # right axis: change in front weight %, as in section 3.4
Y_MIN, Y_MAX = 0.4, 1.4            # shared vertical scale so the four charts compare directly
Y_TICKS = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4]


def num(v, d=2, sign=False):
    s = f"{abs(v):.{d}f}"
    if v < 0 and float(s) != 0:
        return "&#8722;" + s
    return ("+" if sign and float(s) != 0 else "") + s


def chart(key, err, unit, x_title, aria, marks=()):
    lo, hi = err
    px = lambda e: L + (e - lo) / (hi - lo) * (W - L - R)
    py = lambda y: T + (Y_MAX - y) / (Y_MAX - Y_MIN) * (H - T - B)
    out = [f'<svg class="sv-chart" viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">']
    for y in Y_TICKS:
        out.append(f'<line class="sv-grid" x1="{L}" x2="{W - R}" y1="{py(y):.1f}" y2="{py(y):.1f}" />')
        out.append(f'<text class="sv-tick" x="{L - 6}" y="{py(y) + 3.5:.1f}" text-anchor="end">{num(y)}</text>')
    out.append(f'<line class="sv-axis" x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}" />')
    steps = 4
    for i in range(steps + 1):
        e = lo + (hi - lo) * i / steps
        out.append(f'<line class="sv-axis" x1="{px(e):.1f}" x2="{px(e):.1f}" y1="{H - B}" y2="{H - B + 4}" />')
        out.append(f'<text class="sv-tick" x="{px(e):.1f}" y="{H - B + 16}" text-anchor="middle">{num(e, 0 if e == int(e) else 1, sign=True)}</text>')
    out.append(f'<text class="sv-title" x="{(L + W - R) / 2:.1f}" y="{H - 6}" text-anchor="middle">{x_title}</text>')
    out.append(f'<text class="sv-title" x="12" y="{(T + H - B) / 2:.1f}" text-anchor="middle" transform="rotate(-90 12 {(T + H - B) / 2:.1f})">CG shift (in)</text>')
    # right axis: the same CG shift read as change in front weight %, 100 * shift / L
    out.append(f'<line class="sv-axis" x1="{W - R}" x2="{W - R}" y1="{T}" y2="{H - B}" />')
    for f in FRONT_TICKS:
        y = py(f / 100 * WHEELBASE)
        out.append(f'<line class="sv-axis" x1="{W - R}" x2="{W - R + 4}" y1="{y:.1f}" y2="{y:.1f}" />')
        out.append(f'<text class="sv-tick" x="{W - R + 7}" y="{y + 3.5:.1f}">+{f:.1f}</text>')
    xr = W - 8
    out.append(f'<text class="sv-title" x="{xr}" y="{(T + H - B) / 2:.1f}" text-anchor="middle" transform="rotate(90 {xr} {(T + H - B) / 2:.1f})">Change in front weight (%)</text>')

    n = 40
    pts = [(lo + (hi - lo) * i / n) for i in range(n + 1)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{px(e):.1f},{py(shift(**{key: NOM[key] + e})):.1f}" for i, e in enumerate(pts))
    out.append(f'<path class="sv-line" d="{path}" />')

    # hover: one hit column per sample, native tooltip with the value
    colw = (W - L - R) / n
    for e in pts:
        y = shift(**{key: NOM[key] + e})
        out.append(f'<rect class="sv-hit" x="{px(e) - colw / 2:.1f}" y="{T}" width="{colw:.1f}" height="{H - T - B}">'
                   f'<title>Error {num(e, 2, True)} {unit}: CG shift {num(y, 2, True)} in, front weight {num(100 * y / WHEELBASE, 1, True)}%</title></rect>')

    rising = shift(**{key: NOM[key] + hi}) > shift(**{key: NOM[key] + lo})
    for e, label in marks:
        y = shift(**{key: NOM[key] + e})
        cls = "sv-dot" if e == 0 else "sv-dot sv-dot-alt"
        out.append(f'<circle class="{cls}" cx="{px(e):.1f}" cy="{py(y):.1f}" r="4.5"><title>{label}: CG shift {num(y, 2, True)} in, front weight {num(100 * y / WHEELBASE, 1, True)}%</title></circle>')
        if len(marks) == 1:  # lone label goes on the side of the dot the line leaves open
            dx, anchor = (-9, "end") if rising else (9, "start")
            out.append(f'<text class="sv-label" x="{px(e) + dx:.1f}" y="{py(y) - 8:.1f}" text-anchor="{anchor}">{label}</text>')
        else:
            out.append(f'<text class="sv-label" x="{px(e):.1f}" y="{py(y) - 11:.1f}" text-anchor="middle">{label}</text>')
    out.append("</svg>")
    return "\n".join(out)


def per_unit(key):
    return (shift(**{key: NOM[key] + 1}) - shift(**{key: NOM[key] - 1})) / 2


bias_marks = []
for b in (70, 65, 60, 55, 50):
    e = INV_LEN * (1 - b / 100) + REAR_FACE - NOM["x_inv"]
    bias_marks.append((round(e, 6), f"{b}%"))

CHARTS = [
    ("m_acc", (-10, 10), "lb", "Error in ACC27 mass (lb)",
     "CG shift versus error in ACC27 mass from minus 10 to plus 10 lb", [(0, "nominal")],
     "ACC27 mass, nominal 95 lb."),
    ("x_acc", (-2, 2), "in", "Error in ACC27 CG x (in), + is forward",
     "CG shift versus error in ACC27 CG position from minus 2 to plus 2 in", [(0, "nominal")],
     f"ACC27 CG x, nominal {num(NOM['x_acc'])} in."),
    ("m_inv", (-5, 5), "lb", "Error in INV27 mass (lb)",
     "CG shift versus error in INV27 mass from minus 5 to plus 5 lb", [(0, "nominal")],
     f"INV27 mass, nominal {NOM['m_inv']:.0f} lb."),
    ("x_inv", (-2, 2), "in", "Error in INV27 CG x (in), + is forward",
     "CG shift versus error in INV27 CG position from minus 2 to plus 2 in, with rearward weight biases from 50 to 70 percent marked",
     bias_marks,
     f"INV27 CG x, nominal {num(NOM['x_inv'])} in. Labels mark the CG for rearward weight biases of 70% to 50%; 60% is nominal."),
]

NAMES = {"m_acc": ("ACC27 mass", "lb"), "x_acc": ("ACC27 CG, x", "in"),
         "m_inv": ("INV27 mass", "lb"), "x_inv": ("INV27 CG, x", "in")}

rows = []
for key, (lo, hi), unit, *_ in CHARTS:
    name, u = NAMES[key]
    a, b = shift(**{key: NOM[key] + lo}), shift(**{key: NOM[key] + hi})
    rows.append(f'<tr><td>{name}</td><td>{num(lo, 0, True)} to {num(hi, 0, True)}&nbsp;{u}</td>'
                f'<td>{num(min(a, b), 2, True)} to {num(max(a, b), 2, True)}&nbsp;in</td>'
                f'<td>{num(per_unit(key), 3, True)}&nbsp;in per {u}</td></tr>')

figs = []
for i, (key, err, unit, x_title, aria, marks, cap) in enumerate(CHARTS, 1):
    figs.append(f'''            <figure class="a-fig sv-fig" id="sens-{i}">
{chart(key, err, unit, x_title, aria, marks)}
              <figcaption><span class="mono">Chart {i}</span> {cap}</figcaption>
            </figure>''')

inv_lo = min(shift(x_inv=NOM["x_inv"] + e) for e, _ in bias_marks)
inv_hi = max(shift(x_inv=NOM["x_inv"] + e) for e, _ in bias_marks)

section = f'''        <!-- sensitivity:start -->
        <!-- generated by _build/cg_shift_sensitivity.py; edit that script, not this block -->
        <section class="a-section" id="sensitivity">
          <h2><span class="a-num">4</span>Error Sensitivity</h2>
          <p>The ARG27 masses and positions are estimates, so this section shows how much the CG shift changes if one of them is off. Each chart varies one input and keeps the others at their nominal values. All four charts use the same vertical scale, so a steeper line means the result depends more on that input. The nominal CG shift is {num(BASE, 2, True)} in. The right axis reads the same CG shift as the change in front weight percentage from section 3.4: &Delta;(front %) = 100 &times; &Delta;x<sub>CG</sub> / 61.</p>
          <div class="a-table-wrap">
            <table class="a-table sheet">
              <thead><tr><th>Input</th><th>Error range</th><th>CG shift range</th><th>Change in CG shift</th></tr></thead>
              <tbody>
{chr(10).join("                " + r for r in rows)}
              </tbody>
            </table>
          </div>
          <p>The slopes in the last column come from differentiating the ARG27 CG equation. For a part i, the accumulator or the inverter, moving its CG by 1 in moves the car's CG by its share of the total mass, and adding 1 lb pulls the car's CG toward that part by its distance from the CG divided by the total mass:</p>
          <p class="eq">&part;&Delta;x<sub>CG</sub> / &part;x<sub>i</sub> = m<sub>i</sub> / m<sub>27</sub></p>
          <p class="eq">&part;&Delta;x<sub>CG</sub> / &part;m<sub>i</sub> = (x<sub>i</sub> &#8722; x<sub>27</sub>) / m<sub>27</sub></p>
          <p>With m<sub>27</sub> = {M27:.2f} lb and x<sub>27</sub> = {num(X27, 3)} in:</p>
          <ul>
            <li>ACC27 CG, x: {NOM["m_acc"]:.0f} / {M27:.2f} = {num(NOM["m_acc"] / M27, 3, True)} in per in</li>
            <li>ACC27 mass: ({num(NOM["x_acc"])} &#8722; ({num(X27, 3)})) / {M27:.2f} = {num((NOM["x_acc"] - X27) / M27, 3, True)} in per lb</li>
            <li>INV27 CG, x: {NOM["m_inv"]:.2f} / {M27:.2f} = {num(NOM["m_inv"] / M27, 3, True)} in per in</li>
            <li>INV27 mass: ({num(NOM["x_inv"])} &#8722; ({num(X27, 3)})) / {M27:.2f} = {num((NOM["x_inv"] - X27) / M27, 3, True)} in per lb</li>
          </ul>
          <p>The position lines are straight. The mass lines curve slightly because the mass also appears in m<sub>27</sub>, so their slope is given at the nominal mass.</p>
          <p>The accumulator CG position matters most: every inch it is off changes the CG shift by about {num(per_unit("x_acc"), 2)} in. The inverter CG position matters least. Going from a 50% to a 70% rearward weight bias only moves the CG shift between {num(inv_lo, 2, True)} and {num(inv_hi, 2, True)} in.</p>
          <div class="sv-grid-wrap">
{chr(10).join(figs)}
          </div>
        </section>
        <!-- sensitivity:end -->'''

page = open(PAGE).read()
page, n = re.subn(r"        <!-- sensitivity:start -->.*?<!-- sensitivity:end -->", lambda m: section, page, flags=re.S)
assert n == 1, "sensitivity markers not found"
open(PAGE, "w").write(page)
print(f"nominal shift {BASE:+.4f} in; x_acc {NOM['x_acc']:.3f}; x_inv {NOM['x_inv']:.3f}")
for key, *_ in CHARTS:
    print(key, f"{per_unit(key):+.4f} in per unit")
