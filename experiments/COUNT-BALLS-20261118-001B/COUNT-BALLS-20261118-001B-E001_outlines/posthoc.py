"""Post hoc readings of COUNT-BALLS-20261118-001B-E001, after the frozen read-out (labelled as such in the note).
1. chain_scan stored the correlation at t = +1/3; the chain grid's own correlation carries the gauge sign (-1)^(l |x|_1)
   (proved; checked literally by the gate C-two-classes-open-l1).  Recompute C4c with it.
2. The weave's tau-balls (all classes): growth in tau.
3. A wider chain-grid scan (l = 1, every grid distinction within 40, where the two formulas agree): local exponents of the
   tau-ball against tau, and the outline against the ball.
4. The l = 2 axis estimates k by k, against the exact axis rate 2(K* - K) (Onsager), which the closed form equals."""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines"
sys.path.insert(0, str(HERE))
import chain as C  # noqa: E402
import outline as O  # noqa: E402

part = lambda n: json.load(open(ART / "parts" / f"{n}.json"))["result"]
out = {}

# 1
cs = part("chain_scan")
signs = []
for s in cs["sites"]:
    a, b = s["site"]
    c = s["C"] * (-1) ** (a + b)
    signs.append((c > 0) == ((a + b) % 2 == 0))
out["C4c_with_gauge_sign"] = all(signs)

# 2
ws = part("weave_scan")
tau = [-math.log(abs(s["C"])) / math.log(3) for s in ws["sites"]]
levels = [0.8, 1.0, 1.2, 1.4, 1.6]
sizes = [1 + sum(t <= x for t in tau) for x in levels]
rmax = [max([s["r"] for s, t in zip(ws["sites"], tau) if t <= x] or [0]) for x in levels]
out["weave_tau_balls"] = {"tau": levels, "size": sizes, "farthest": rmax,
                          "slope_ln_size_per_tau": float(np.polyfit(levels, np.log(sizes), 1)[0]),
                          "predicted_slope": 4 * math.log(3)}

# 3
t = 1 / 3
Rt = C.Resolvent(t)
Rd = C.Resolvent((1 - t) / (1 + t))
cm = {}
for a in range(0, 41):
    for b in range(0, a + 1):
        if (a, b) != (0, 0) and math.hypot(a, b) <= 40:
            p = C.path([(1, 0)] * a + [(0, 1)] * b)
            x, y = C.corr_reweight(Rt, t, p), C.corr_dual(Rd, p)
            if abs(x - y) / abs(y) > 1e-8:
                continue
            for u, v in {(a, b), (b, a)}:
                for sx in (1, -1):
                    for sy in (1, -1):
                        cm[(sx * u, sy * v)] = y
cm[(0, 0)] = 1.0
ta = {k: -math.log(abs(v)) / math.log(3) for k, v in cm.items()}
nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
rows = []
for t0 in range(2, 15):
    inside = {k for k, v in ta.items() if v <= t0}
    edge = [k for k in inside if any((k[0] + d[0], k[1] + d[1]) not in inside for d in nb)]
    rows.append({"tau": t0, "ball": len(inside), "outline": len(edge), "farthest": max(math.hypot(*k) for k in inside)})
loc = [math.log(rows[i + 1]["ball"] / rows[i]["ball"]) / math.log(rows[i + 1]["tau"] / rows[i]["tau"]) for i in range(len(rows) - 1)]
out["chain_wide"] = {"sites": len(cm), "rows": rows, "local_ball_exponents": loc,
                     "slope_ball_tau_6_to_14": float(np.polyfit(np.log([r["tau"] for r in rows[4:]]), np.log([r["ball"] for r in rows[4:]]), 1)[0]),
                     "slope_outline_ball": float(np.polyfit(np.log([r["ball"] for r in rows]), np.log([r["outline"] for r in rows]), 1)[0])}

# 4
cr = part("chain_rays")["l=2"]["(1,0)"]
K = math.atanh(1 / 9)
Ks = -0.5 * math.log(math.tanh(K))
exact = 2 * (Ks - K)
pts = [p for p in cr["points"] if p["rel_agree"] < 1e-8]
est = []
for p, q in zip(pts, pts[1:]):
    k = p["k"]
    plain = math.log(abs(p["C_dual"])) - math.log(abs(q["C_dual"]))
    est.append({"k": k, "plain": plain, "with_OZ": plain - 0.5 * math.log((k + 1) / k)})
out["l2_axis"] = {"onsager_exact": exact, "closed_form": cr["rate_closed_form"], "estimates": est}

json.dump(out, open(ART / "posthoc.json", "w"), indent=1)
print(json.dumps(out, indent=1))
