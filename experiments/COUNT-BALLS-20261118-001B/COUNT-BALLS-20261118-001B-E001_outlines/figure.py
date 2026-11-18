"""Figure for the decision note: count balls and their outlines (from the frozen run's parts; drawing coordinates are the
literature's, used only to show the result)."""
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines"
sys.path.insert(0, str(HERE))
import outline as O  # noqa: E402

BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#2b2b29", "#8a8984"
part = lambda n: json.load(open(ART / "parts" / f"{n}.json"))["result"]
res = json.load(open(ART / "results.json"))
fig, ax = plt.subplots(1, 3, figsize=(15, 5.2), gridspec_kw={"width_ratios": [1, 1, 0.9]})

# weave, own class, raw count u = 0.15
ws = part("weave_scan")
a = res["weave"]["a_row_fit"]
u = 0.15
cm = {tuple(s["site"]): s["C"] for s in ws["sites"]}
cm[(0, 0)] = 1.0
nb = [tuple(x) for x in res["weave"]["six_nearest"]]
inside = {k for k, v in cm.items() if v >= u}
edge = {k for k in inside if any((k[0] + d[0], k[1] + d[1]) not in inside for d in nb)}
pos = lambda k: (k[0] + k[1] / 2, k[1] * math.sqrt(3) / 2)
others = [pos(k) for k in cm if (k[0] + 2 * k[1]) % 3 == 0 and k not in inside]
P = np.array([pos(k) for k in inside - edge]); E = np.array([pos(k) for k in edge]); Q = np.array(others)
ax[0].scatter(Q[:, 0], Q[:, 1], s=4, color="#d9d8d3", label="own class, outside")
ax[0].scatter(P[:, 0], P[:, 1], s=10, color=BLUE, label="ball (count below the level)")
ax[0].scatter(E[:, 0], E[:, 1], s=16, color=ORANGE, label="outline")
R = (a / u) ** 2
th = np.linspace(0, 2 * np.pi, 400)
ax[0].plot(R * np.cos(th), R * np.sin(th), color=INK, lw=1.4, label=f"predicted round outline, reach (a/u)² = {R:.1f}")
hx = [R * math.cos(k * math.pi / 3) for k in range(7)]; hy = [R * math.sin(k * math.pi / 3) for k in range(7)]
ax[0].plot(hx, hy, color=MUTED, lw=1.2, ls="--", label="bond distance's outline (steps apart), same reach")
ax[0].set_title("Six-regular weave, not-all-equal: the start's class,\n1 − 2d/N ≥ 0.15 (379 distinctions)", fontsize=11)
ax[0].set_aspect("equal"); ax[0].set_xlim(-23, 23); ax[0].set_ylim(-23, 23); ax[0].axis("off")
ax[0].legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), fontsize=8, frameon=False)

# chain grid l = 1, tau <= 7
cs = part("chain_scan")
cmap = {}
for s in cs["sites"]:
    x0, y0 = s["site"]
    for x, y in {(x0, y0), (y0, x0)}:
        for sx in (1, -1):
            for sy in (1, -1):
                cmap[(sx * x, sy * y)] = s["C"]
cmap[(0, 0)] = 1.0
tau = {k: -math.log(abs(v)) / math.log(3) for k, v in cmap.items()}
t0 = 7.0
ins = {k for k, v in tau.items() if v <= t0}
nb4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
ed = {k for k in ins if any((k[0] + d[0], k[1] + d[1]) not in ins for d in nb4)}
outk = [k for k in cmap if k not in ins]
P = np.array(sorted(ins - ed)); E = np.array(sorted(ed)); Q = np.array(outk)
ax[1].scatter(Q[:, 0], Q[:, 1], s=4, color="#d9d8d3", label="grid distinction, outside")
ax[1].scatter(P[:, 0], P[:, 1], s=10, color=BLUE, label="ball (τ ≤ 7)")
ax[1].scatter(E[:, 0], E[:, 1], s=16, color=ORANGE, label="outline")
A = O.A_of(1 / 3)
Rax = max(abs(k[0]) for k in ins if k[1] == 0) + 0.5
h0 = O.rate(0.0, A)
r = np.array([Rax * h0 / O.rate(x, A) for x in th])
ax[1].plot(r * np.cos(th), r * np.sin(th), color=INK, lw=1.4, label="closed-form outline (1.0034 from round)")
ax[1].plot([Rax, 0, -Rax, 0, Rax], [0, Rax, 0, -Rax, 0], color=MUTED, lw=1.2, ls="--", label="taxicab diamond, same reach")
ax[1].set_title("Chain grid, one not-all-equal knot per pair:\ngrid distinctions with τ ≤ 7 (681)", fontsize=11)
ax[1].set_aspect("equal"); ax[1].set_xlim(-23, 23); ax[1].set_ylim(-23, 23); ax[1].axis("off")
ax[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), fontsize=8, frameon=False)

# Golab pi against chain length
ls = list(range(1, 13))
pis = [O.golab_pi(lambda x, A=O.A_of(3.0 ** -l): O.rate(x, A), 4000) for l in ls]
ax[2].axhline(math.pi, color=MUTED, lw=1, ls=":")
ax[2].axhline(4, color=MUTED, lw=1, ls=":")
ax[2].text(12.3, math.pi, "π: round\n(the weave's own class)", va="center", fontsize=8, color=INK)
ax[2].text(12.3, 4, "4: taxicab diamond\n(grown split grids,\nl → ∞)", va="center", fontsize=8, color=INK)
ax[2].plot(ls, pis, color=BLUE, lw=2, marker="o", ms=5)
ax[2].set_xlabel("knots per chain, l", fontsize=10)
ax[2].set_ylabel("Gołąb's π of the count's outline", fontsize=10)
ax[2].set_title("Chain grids: π from 3.1417 (l = 1) toward 4", fontsize=11)
ax[2].set_xlim(0.5, 12.5); ax[2].set_ylim(3.05, 4.08)
for s in ("top", "right"):
    ax[2].spines[s].set_visible(False)
ax[2].grid(axis="y", color="#ecebe7", lw=0.8)
fig.tight_layout()
fig.savefig(ART / "outlines.png", dpi=170, bbox_inches="tight", facecolor="white")
print(ART / "outlines.png")
