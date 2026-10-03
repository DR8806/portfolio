"""Regenerate the 2.8 ARG26 Results section of the CG height page from the test data."""
import sys, math, statistics as st

# ---- ARG26 test data ----
d = 51.8                     # width across outside tire edges, d_f = d_r (in)
rh_t, rh_n = 2.7, 1.5        # tested and design ride height (in)
w_car = 440.0                # car without driver (lb)
w_drv = 130.0                # driver weight, both drivers (lb)
w_un_corner = 30.0           # unsprung weight per corner (lb)
cases = [("No driver", 0.0, [69.5, 69.9, 69.7, 69.4]),
         ("Driver 1 (Caroline)", w_drv, [67.8, 68.1, 67.9, 67.7, 68.0, 67.6]),
         ("Driver 2 (Aryaman)", w_drv, [67.0, 67.1, 67.1, 67.5, 67.1])]

half = d / 2
raise_ = rh_t - rh_n
w_un = 4 * w_un_corner
COL = ["#d9481c", "#2b6cb0", "#2f855a"]

calc = []
for name, wd, th in cases:
    W = w_car + wd
    sf = (W - w_un) / W
    corr = sf * raise_
    h = [half / math.tan(math.radians(t)) for t in th]
    hn = [x - corr for x in h]
    calc.append(dict(name=name, W=W, sf=sf, corr=corr, th=th, h=h, hn=hn))
    print(f"{name}: W={W:.0f} sf={sf:.4f} corr={corr:.4f} avg={st.mean(hn):.3f} min={min(hn):.3f} max={max(hn):.3f}", file=sys.stderr)

summary = "".join(
    f'                <tr><td><span class="cg-swatch cg-c{i}" aria-hidden="true"></span>{c["name"]}</td><td>{len(c["th"])}</td><td><strong>{st.mean(c["hn"]):.2f}</strong></td><td>{min(c["hn"]):.2f}</td><td>{max(c["hn"]):.2f}</td></tr>\n'
    for i, c in enumerate(calc))

def case_tbl(i, c):
    rows = "".join(f'                    <tr><td>{k}</td><td>{t:.1f}</td><td>{a:.2f}</td><td>{b:.2f}</td></tr>\n'
                   for k, (t, a, b) in enumerate(zip(c["th"], c["h"], c["hn"]), 1))
    return f'''              <h4 class="cg-case-title"><span class="cg-swatch cg-c{i}" aria-hidden="true"></span>{c["name"]}</h4>
              <p>W = {c["W"]:.0f} lb, W<sub>sprung</sub> / W = ({c["W"]:.0f} &minus; {w_un:.0f}) / {c["W"]:.0f} = {c["sf"]:.3f}, correction = {c["sf"]:.3f} &times; {raise_:.1f} = {c["corr"]:.3f} in</p>
              <div class="a-table-wrap">
                <table class="a-table sheet">
                  <thead><tr><th>Trial</th><th>&theta; (deg)</th><th>h as tested (in)</th><th>h at {rh_n:.1f} in ride height (in)</th></tr></thead>
                  <tbody>
{rows}                    <tr class="a-row-total"><td>Average</td><td>{st.mean(c["th"]):.2f}</td><td>{st.mean(c["h"]):.2f}</td><td>{st.mean(c["hn"]):.2f}</td></tr>
                  </tbody>
                </table>
              </div>
'''

case_tbls = "".join(case_tbl(i, c) for i, c in enumerate(calc))

# static strip plot, same look as the live calculator plot
allv = [v for c in calc for v in c["hn"]]
W_, R_, L_, T_ = 640, 24, 170, 20
H_ = 70 + 3 * 56
lo, hi = min(allv), max(allv)
pad = (hi - lo) * 0.12
lo -= pad; hi += pad
X = lambda v: L_ + (v - lo) / (hi - lo) * (W_ - L_ - R_)
step = next(sv for sv in [0.05, 0.1, 0.25, 0.5, 1, 2] if (hi - lo) / sv <= 8)
axisY = T_ + 3 * 56 + 6
svg = [f'<svg viewBox="0 0 {W_} {H_}" role="img" aria-label="ARG26 CG height at nominal ride height by case">']
t = math.ceil(lo / step) * step
while t <= hi + 1e-9:
    svg.append(f'<line x1="{X(t):.1f}" y1="{T_-6}" x2="{X(t):.1f}" y2="{axisY}" class="cg-grid"/><text x="{X(t):.1f}" y="{axisY+18}" text-anchor="middle" class="cg-tick">{t:.2f}</text>')
    t += step
svg.append(f'<line x1="{L_}" y1="{axisY}" x2="{W_-R_}" y2="{axisY}" class="cg-axis"/><text x="{(L_+W_-R_)/2:.1f}" y="{axisY+40}" text-anchor="middle" class="cg-tick">CG height at {rh_n:.1f} in ride height (in)</text>')
for i, c in enumerate(calc):
    y = T_ + 22 + i * 56
    col = COL[i]
    hn = c["hn"]
    avg = st.mean(hn)
    svg.append(f'<text x="{L_-14}" y="{y+4}" text-anchor="end" class="cg-label" fill="{col}">{c["name"]}</text><line x1="{L_}" y1="{y}" x2="{W_-R_}" y2="{y}" class="cg-row"/>')
    svg.append(f'<line x1="{X(min(hn)):.1f}" y1="{y}" x2="{X(max(hn)):.1f}" y2="{y}" stroke="{col}" stroke-width="2"/>')
    for v in hn:
        cx = X(v)
        if i == 0:
            svg.append(f'<circle cx="{cx:.1f}" cy="{y}" r="5.5" fill="{col}" fill-opacity="0.75"/>')
        elif i == 1:
            svg.append(f'<rect x="{cx-5:.1f}" y="{y-5}" width="10" height="10" fill="{col}" fill-opacity="0.75"/>')
        else:
            svg.append(f'<path d="M {cx:.1f} {y-6.5} L {cx+6:.1f} {y+4.5} L {cx-6:.1f} {y+4.5} Z" fill="{col}" fill-opacity="0.75"/>')
    svg.append(f'<line x1="{X(avg):.1f}" y1="{y-15}" x2="{X(avg):.1f}" y2="{y+15}" stroke="{col}" stroke-width="3"/><text x="{X(avg):.1f}" y="{y-20}" text-anchor="middle" class="cg-avg" fill="{col}">{avg:.2f}</text>')
svg.append('</svg>')
svg = "".join(svg)

section = f'''          <!-- web-only -->
          <h3><span class="a-num">2.8</span>ARG26 Results</h3>
          <p>CG height of ARG26 at its nominal {rh_n:.1f} in ride height. These values already include the ride height correction, so they can be used directly for any vehicle calculations with CG height.</p>
          <div class="a-table-wrap">
            <table class="a-table sheet">
              <thead><tr><th>Case</th><th>Trials</th><th>Average h (in)</th><th>Lowest (in)</th><th>Highest (in)</th></tr></thead>
              <tbody>
{summary}              </tbody>
            </table>
          </div>

          <details class="a-details">
            <summary>Show data and calculations</summary>
            <div class="a-details-body">
              <p class="a-note"><span class="mono">Note</span>Due to the time crunch, we assumed the weight is split evenly (50/50) at all four corners instead of measuring corner weights. We also assumed the CG of the car and the driver both sit at that 50/50 midpoint, so adding the driver does not change the longitudinal position of the CG.</p>
              <p class="a-note"><span class="mono">Note</span>The unsprung weight is {w_un_corner:.0f} lbf at each corner, so {w_un:.0f} lbf total. It is the same with or without a driver, since the driver is part of the sprung mass.</p>

              <h4 class="cg-case-title">Inputs</h4>
              <div class="a-table-wrap">
                <table class="a-table sheet">
                  <thead><tr><th>Symbol</th><th>Measurement</th><th>Value</th></tr></thead>
                  <tbody>
                    <tr><td>W<sub>car</sub></td><td>Car weight without driver (lb)</td><td>{w_car:.0f}</td></tr>
                    <tr><td>W<sub>driver</sub></td><td>Driver weight, driver 1 and driver 2 (lb)</td><td>{w_drv:.0f}</td></tr>
                    <tr><td>W</td><td>Total weight: no driver, with driver (lb)</td><td>{w_car:.0f}, {w_car+w_drv:.0f}</td></tr>
                    <tr><td>W<sub>FL</sub> = W<sub>FR</sub> = W<sub>RL</sub> = W<sub>RR</sub></td><td>Corner weights, assumed even: no driver, with driver (lb)</td><td>{w_car/4:.0f}, {(w_car+w_drv)/4:.1f}</td></tr>
                    <tr><td>W<sub>unsprung</sub></td><td>Unsprung weight, {w_un_corner:.0f} lb per corner (lb)</td><td>{w_un:.0f}</td></tr>
                    <tr><td>L</td><td>Wheelbase (in)</td><td>61</td></tr>
                    <tr><td>d<sub>f</sub> = d<sub>r</sub></td><td>Width across outside tire edges (in)</td><td>{d:.1f}</td></tr>
                    <tr><td>p</td><td>Tire pressure (psi)</td><td>20</td></tr>
                    <tr><td>RH<sub>tested</sub></td><td>Ride height with dummy shocks (in)</td><td>{rh_t:.1f}</td></tr>
                    <tr><td>RH<sub>nominal</sub></td><td>Design ride height (in)</td><td>{rh_n:.1f}</td></tr>
                    <tr><td>&theta;<sub>0</sub></td><td>Level reading, car level (deg)</td><td>0</td></tr>
                  </tbody>
                </table>
              </div>

              <h4 class="cg-case-title">Calculations</h4>
              <p>With d<sub>f</sub> = d<sub>r</sub>, the width at the CG does not depend on the weight split:</p>
              <p class="eq">d = d<sub>f</sub> + (d<sub>r</sub> &minus; d<sub>f</sub>) &times; W<sub>R</sub> / W = {d:.1f} in,&nbsp;&nbsp;d / 2 = {half:.1f} in</p>
              <p class="eq">h = (d / 2) / tan &theta;</p>
              <p>Ride height correction (Section 2.5), from the {rh_t:.1f} in tested ride height down to the {rh_n:.1f} in design ride height. The driver adds sprung mass, so the sprung fraction is worked out for each case:</p>
              <p class="eq">RH<sub>tested</sub> &minus; RH<sub>nominal</sub> = {rh_t:.1f} &minus; {rh_n:.1f} = {raise_:.1f} in</p>
              <p class="eq">W<sub>sprung</sub> / W = (W &minus; W<sub>unsprung</sub>) / W</p>
              <p class="eq">h<sub>nominal</sub> = h &minus; (W<sub>sprung</sub> / W) &times; (RH<sub>tested</sub> &minus; RH<sub>nominal</sub>)</p>

{case_tbls}
              <figure class="a-fig cg-plot">
                <div class="cg-plot-frame">{svg}</div>
                <figcaption><span class="mono">Figure 4</span><span>ARG26 CG height at the {rh_n:.1f} in design ride height for each trial. The bar is the average and the line runs from the lowest to the highest trial.</span></figcaption>
              </figure>
            </div>
          </details>
          <!-- /web-only -->

'''

p = sys.argv[1]
s = open(p).read()
a = s.index('          <!-- web-only -->\n          <h3><span class="a-num">2.8</span>ARG26 Results</h3>')
b = s.index('          <h3><span class="a-num">2.9</span>Downloadable Test Plan</h3>')
open(p, "w").write(s[:a] + section + s[b:])
print("ARG26 section updated", file=sys.stderr)
