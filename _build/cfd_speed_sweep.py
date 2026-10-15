import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# plots for the CFD speed sweep (yaw 0, roll 0, pitch 0) on the Miscellaneous page
ROOT = "/Users/davisrattanavijai/Desktop/portfolio"
DATA = os.path.join(ROOT, "assets/docs/cfd-speed-sweep-yaw0-roll0-pitch0.csv")
OUT = os.path.join(ROOT, "assets/img/cfd")

rows = list(csv.DictReader(open(DATA)))
col = lambda k: [float(r[k]) for r in rows]
v = col("speed_m_s")

plt.rcParams.update({
    "font.family": "Helvetica", "font.size": 13, "axes.linewidth": 1.0,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.8,
    "legend.fancybox": False, "legend.edgecolor": "black", "legend.framealpha": 1,
})
BLUE, RED = "#0072bd", "#d95319"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=150)
    plt.close(fig)


# forces vs speed
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(v, col("downforce_N"), "-o", color="black", lw=2, ms=4, label="Total downforce")
ax.plot(v, col("front_downforce_N"), "-o", color=BLUE, lw=2, ms=4, label="Front downforce")
ax.plot(v, col("rear_downforce_N"), "-o", color=RED, lw=2, ms=4, label="Rear downforce")
ax.plot(v, col("drag_N"), "--s", color="#555555", lw=2, ms=4, label="Drag")
ax.set(xlim=(10, 20), ylim=(0, 1000), xlabel="Speed [m/s]", ylabel="Force [N]",
       title="Downforce and Drag vs Speed")
ax.legend(loc="upper left")
save(fig, "01-forces-vs-speed.png")

# coefficients vs speed
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(v, col("ClA"), "-o", color=BLUE, lw=2, ms=4, label="C$\\mathregular{_L}$A (downforce)")
ax.plot(v, col("CdA"), "-s", color=RED, lw=2, ms=4, label="C$\\mathregular{_D}$A (drag)")
ax.set(xlim=(10, 20), ylim=(0, 4.5), xlabel="Speed [m/s]", ylabel="Coefficient × area [m$\\mathregular{^2}$]",
       title="C$\\mathregular{_L}$A and C$\\mathregular{_D}$A vs Speed")
ax.legend(loc="center right")
save(fig, "02-cla-cda-vs-speed.png")
