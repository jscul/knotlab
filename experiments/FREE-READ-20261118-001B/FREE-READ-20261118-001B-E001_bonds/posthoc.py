"""Post hoc (after the frozen read-out; no prediction): the freedom-gated cumulant distance

    delta_F(x, y) = min over S holding x and y, kappa_S != 0 and every proper subset of S free, of (|S| - 2) + tau(kappa_S),

and delta_KB = min(delta_K, the least (|S| - 2) + tau(kappa_S) over bonds S holding x and y), against bond distance, delta,
delta_K and tau on the frozen run's cycles and rings, on every knot tree to five knots under every
law assignment, on the split line and split grids (where bond distance is two for every pair), and on a weave patch.

    .venv/bin/python -B posthoc.py      writes artifacts/.../posthoc.json
"""
import itertools
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import freelib as F  # noqa: E402

L, T = F.L, F.T
ART = Path(__file__).resolve().parents[3] / "artifacts/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds"


def delta_F(B, sup, x, y, smax):
    others = [z for z in range(B.n) if z not in (x, y)]
    best = math.inf
    for m in range(2, smax + 1):
        if m - 2 >= best:
            break
        for extra in itertools.combinations(others, m - 2):
            S = tuple(sorted((x, y) + extra))
            k = B.cumulant(S)
            if k == 0.0:
                continue
            if m > 2 and not all(sup.full(U) for U in itertools.combinations(S, m - 1)):
                continue
            best = min(best, (m - 2) + max(0.0, -math.log(abs(k), 3)))
    return best


def delta_bond(B, sup, x, y, smax):
    """min over bonds S holding x and y with kappa_S != 0 of (|S| - 2) + tau(kappa_S)."""
    others = [z for z in range(B.n) if z not in (x, y)]
    best = math.inf
    for m in range(3, smax + 1):
        if m - 2 >= best:
            break
        for extra in itertools.combinations(others, m - 2):
            S = tuple(sorted((x, y) + extra))
            if not sup.is_bond(S):
                continue
            k = B.cumulant(S)
            if k != 0.0:
                best = min(best, (m - 2) + max(0.0, -math.log(abs(k), 3)))
    return best


def fin(v):
    return None if v == math.inf else round(v, 4)


def read(name, knots_or_states, n, smax, steps=None, states=False, cap=None):
    st = knots_or_states if states else L.states_from_knots(n, knots_or_states)
    B, sup = L.Base(st, n), F.Supports(st, n)
    rows = []
    pairs = list(itertools.combinations(range(n), 2))
    for x, y in pairs[:cap] if cap else pairs:
        b = sup.bond_distance(x, y, smax)
        d, dK = T.both(B, x, y, smax)
        rows.append({"x": x, "y": y, "steps": None if steps is None else steps[x][y], "bond_minus_1": None if b is None else b - 1,
                     "tau": fin(L.tau(B.correlation(x, y))), "delta": fin(d), "delta_K": fin(dK), "delta_F": fin(delta_F(B, sup, x, y, smax)),
                     "delta_KB": fin(min(dK, delta_bond(B, sup, x, y, smax)))})
    return {"name": name, "n": n, "N": len(st), "rows": rows}


def main():
    out = {"note": "post hoc, after the frozen read-out; no prediction was registered for delta_F", "bases": []}
    # cycles and rings of the frozen run
    for m in range(3, 7):
        for name, laws in (("P", "P" * m), ("N", "N" * m), ("alt", ("PN" * m)[:m])):
            knots = [(laws[i], (2 * i, 2 * i + 1, (2 * i + 2) % (2 * m))) for i in range(m)]
            sp = L.steps_apart([k for _, k in knots], 2 * m)
            out["bases"].append(read(f"ring{m}-{name}", knots, 2 * m, min(2 * m, 8), sp))
    for k in range(2, 6):
        knots = [("N", (2 * j, 2 * j + 1, 2 * j + 2)) for j in range(k)] + [("P", (0, 2 * k, 2 * k + 1))]
        n = 2 * k + 2
        sp = L.steps_apart([kk for _, kk in knots], n)
        out["bases"].append(read(f"closed{k}", knots, n, 5, sp))
    # every knot tree to five knots, every law assignment: does delta_F equal steps apart?
    tree_off, tree_pairs = [], 0
    for kk in range(1, 6):
        for knots, n in L.tree_shapes(kk):
            sp = L.steps_apart(knots, n)
            for laws in itertools.product("PN", repeat=kk):
                st = L.states_from_knots(n, list(zip(laws, knots)))
                B, sup = L.Base(st, n), F.Supports(st, n)
                for x, y in itertools.combinations(range(n), 2):
                    tree_pairs += 1
                    v = delta_F(B, sup, x, y, sp[x][y] + 2)
                    if abs(v - sp[x][y]) > 1e-9:
                        tree_off.append(["".join(laws), knots, x, y, sp[x][y], fin(v)])
    out["trees_to_five"] = {"pairs": tree_pairs, "off": len(tree_off), "examples": tree_off[:10]}
    # split line and split grids: cuts and their complements plus the two all-equal states
    def split_states(cells, axes):
        n = len(cells)
        full = (1 << n) - 1
        st = {0, full}
        for ax, size in axes:
            for c in range(size - 1):
                msk = sum(1 << q for q, p in enumerate(cells) if p[ax] <= c)
                st |= {msk, full ^ msk}
        return sorted(st)
    line = [(i, 0) for i in range(8)]
    out["bases"].append(read("split-line8", split_states(line, [(0, 8)]), 8, 6, states=True))
    for W, H in ((3, 3), (4, 4)):
        cells = [(i, j) for i in range(W) for j in range(H)]
        out["bases"].append(read(f"split-grid{W}x{H}", split_states(cells, [(0, W), (1, H)]), len(cells), 5, states=True))
    # weave patch of radius 2 (NAE on every knot inside), pairs from the centre
    R = 2
    sites = [(i, j) for i in range(-R, R + 1) for j in range(-R, R + 1) if max(abs(i), abs(j), abs(i + j)) <= R]
    ix = {p: q for q, p in enumerate(sites)}
    knots = []
    for (i, j) in sites:
        for tri in (((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i, j + 1), (i + 1, j + 1))):
            if all(p in ix for p in tri):
                knots.append(("N", tuple(ix[p] for p in tri)))
    n = len(sites)
    st = L.states_from_knots(n, knots)
    B, sup = L.Base(st, n), F.Supports(st, n)
    c = ix[(0, 0)]
    rows = []
    for y in range(n):
        if y == c:
            continue
        a, b = sites[c], sites[y]
        s = max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[0] - b[0] + a[1] - b[1]))
        bd = sup.bond_distance(c, y, 5)
        d, dK = T.both(B, c, y, 5)
        rows.append({"y": b, "steps": s, "bond_minus_1": None if bd is None else bd - 1, "tau": fin(L.tau(B.correlation(c, y))),
                     "delta": fin(d), "delta_K": fin(dK), "delta_F": fin(delta_F(B, sup, c, y, 5)),
                     "delta_KB": fin(min(dK, delta_bond(B, sup, c, y, 5)))})
    out["bases"].append({"name": "weave-patch-R2-from-centre", "n": n, "N": len(st), "rows": rows})
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "posthoc.json", "w"), indent=1)
    print(json.dumps(out["trees_to_five"]))
    for base in out["bases"]:
        agree = lambda a, b: sum(r[a] is not None and r[b] is not None and abs(r[a] - r[b]) < 1e-9 for r in base["rows"])
        print(base["name"], "pairs", len(base["rows"]), "| delta_F = tau", agree("delta_F", "tau"), "= bond-1", agree("delta_F", "bond_minus_1"),
              "= delta", agree("delta_F", "delta"), "= delta_K", agree("delta_F", "delta_K"),
              "| delta_KB = tau", agree("delta_KB", "tau"), "= delta", agree("delta_KB", "delta"), "= delta_K", agree("delta_KB", "delta_K"))


if __name__ == "__main__":
    main()
