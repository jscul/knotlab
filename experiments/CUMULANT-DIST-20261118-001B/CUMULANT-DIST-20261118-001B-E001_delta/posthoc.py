"""Post hoc readings of CUMULANT-DIST-20261118-001B-E001, after the frozen read-out (labelled as such in the note).
1. P4 as the advisor stated it: with a separating distinction, kappa_4 = -E[xy]E[uv] - E[xv]E[uy] = -2 (-1/3)^(d(x,y) + d(u,v)),
   the exponent over the cross pairs (the frozen code used the pairs on each side).
2. The rings: delta, steps apart and tau for every pair.
3. The weave patch: delta, tau and steps apart; where delta < tau.
4. The split line of eight: the delta table and the four-sets at the largest value.
5. The split grids: the triangle signs of C (the two-graph) at the corner, its neighbour and the far corner."""
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta"
sys.path.insert(0, str(HERE))
import cumlib as L  # noqa: E402

part = lambda n: json.load(open(ART / "parts" / f"{n}.json"))["result"]
out = {}

# 1
rows = []
for k in range(3, 6):
    knots, n = [], 1
    for i in range(k):
        knots.append(("N", (n - 1, n, n + 1)))
        n += 2
    B = L.Base(L.states_from_knots(n, knots), n)
    sp = L.steps_apart([kk for _, kk in knots], n)
    tested = bad_formula = bad_identity = 0
    for S in itertools.combinations(range(n), 4):
        for (x, u), (y, v) in (((S[0], S[1]), (S[2], S[3])), ((S[0], S[2]), (S[1], S[3])), ((S[0], S[3]), (S[1], S[2]))):
            seps = [w for w in range(0, n, 2) if all(sp[a][w] + sp[w][b] == sp[a][b] for a in (x, u) for b in (y, v))
                    and w not in (x, u, y, v) or (w in (x, u, y, v) and all(sp[a][w] + sp[w][b] == sp[a][b] for a in (x, u) for b in (y, v)))]
            if not seps:
                continue
            tested += 1
            kap = B.cumulant(S)
            ident = -B.moment((x, y)) * B.moment((u, v)) - B.moment((x, v)) * B.moment((u, y))
            formula = -2 * (-1 / 3) ** (sp[x][y] + sp[u][v])
            bad_identity += abs(kap - ident) > 1e-12
            bad_formula += abs(kap - formula) > 1e-12
            break
    rows.append({"k": k, "tested": tested, "identity_mismatch": bad_identity, "formula_mismatch": bad_formula})
out["P4_as_stated"] = rows

# 2
rg = part("rings")
out["rings"] = []
for r in rg:
    t = r["table"]
    out["rings"].append({"m": r["m"], "law": r["law"],
                         "delta_below_steps": sum(v["delta"] < v["steps"] - 1e-9 for v in t.values()),
                         "delta_above_steps": sum(v["delta"] > v["steps"] + 1e-9 for v in t.values()),
                         "pairs": len(t),
                         "values": sorted({(v["steps"], round(v["delta"], 4)) for v in t.values()})})

# 3
wp = part("weave_patch")
from collections import defaultdict
by = defaultdict(list)
for r in wp["rows"]:
    by[r["steps"]].append((round(r["tau"], 3), round(r["delta"], 3)))
out["weave_patch"] = {"by_steps": {s: {"tau_range": [min(a for a, _ in v), max(a for a, _ in v)],
                                       "delta_range": [min(b for _, b in v), max(b for _, b in v)], "pairs": len(v)}
                                   for s, v in sorted(by.items())},
                      "shortcuts": [r for r in wp["rows"] if r["delta"] < r["tau"] - 1e-9]}

# 4
m = 8
full = (1 << m) - 1
st = {0, full}
for c in range(m - 1):
    cut = (1 << (c + 1)) - 1
    st |= {cut, full ^ cut}
B = L.Base(sorted(st), m)
tab = {}
for x, y in itertools.combinations(range(m), 2):
    v, S, kap = B.delta(x, y, smax=6)
    tab[f"{x}-{y}"] = {"L1": y - x, "C": B.correlation(x, y), "delta": v, "argmin": S, "kappa": kap}
out["split_line"] = tab

# 5
res = []
for W, H in ((3, 3), (3, 4), (4, 4)):
    cells = [(i, j) for i in range(W) for j in range(H)]
    n = len(cells)
    fl = (1 << n) - 1
    st = {0, fl}
    for ax, size in ((0, W), (1, H)):
        for c in range(size - 1):
            mm = sum(1 << k for k, p in enumerate(cells) if p[ax] <= c)
            st |= {mm, fl ^ mm}
    B = L.Base(sorted(st), n)
    o, nb, far = cells.index((0, 0)), cells.index((0, 1)), cells.index((W - 1, H - 1))
    def tri(a, b):
        return sorted(round(B.correlation(a, b) * B.correlation(b, z) * B.correlation(a, z), 6) for z in range(n) if z not in (a, b))
    res.append({"W": W, "H": H, "absC_neighbour": abs(B.correlation(o, nb)), "absC_far": abs(B.correlation(o, far)),
                "triangles_neighbour": tri(o, nb), "triangles_far": tri(o, far)})
out["split_grid_two_graph"] = res

json.dump(out, open(ART / "posthoc.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "split_line"}, default=str)[:4000])
print({k: (round(v["delta"], 4), v["argmin"], round(v["kappa"], 4)) for k, v in tab.items() if k.startswith("0-") or k.startswith("3-")})
