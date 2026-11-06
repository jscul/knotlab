#!/usr/bin/env python3
"""Independent check of the shape-and-mechanism test; imports no producer code.

Parses the raw rows, recomputes every estimate, slope, difference, coupling statistic and decision from the raw counts,
and compares them with result.json. It then replays two tori (the 9 x 18 axis torus and the (12,5) rotated square) with
its own lattice construction, its own sampler and its own satisfiability test (forced-value propagation with
exhaustive branching, checked against brute force on a 3 x 3 torus first), and requires each replayed consistent
fraction to lie within five standard errors of the recorded one. A deliberately altered threshold must change the
verdict.
"""

from __future__ import annotations

import json
import math
import random
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts/BASE-CRITICALITY-20261022-001B/BASE-CRITICALITY-20261022-001B-E001_shape_and_mechanism"


def wls_slope(points):
    xs = [math.log2(s) for s, _, _ in points]
    ys = [e for _, e, _ in points]
    ws = [1 / se ** 2 for _, _, se in points]
    W = sum(ws)
    xm = sum(w * x for w, x in zip(ws, xs)) / W
    ym = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - xm) ** 2 for w, x in zip(ws, xs))
    return sum(w * (x - xm) * (y - ym) for w, x, y in zip(ws, xs, ys)) / sxx, math.sqrt(1 / sxx)


def torus_points(v1, v2):
    """Vertices of Z^2 / <v1, v2> by breadth-first exploration with a membership test (independent of any normal form)."""
    (a, b), (c, d) = v1, v2
    det = a * d - b * c

    def in_lattice(x, y):
        # solve (x, y) = s v1 + t v2 over the rationals; integral solutions mean membership
        s_num = x * d - y * c
        t_num = a * y - b * x
        return s_num % det == 0 and t_num % det == 0

    reps, index = [], {}

    def find(x, y):
        for k, (px, py) in enumerate(reps):
            if in_lattice(x - px, y - py):
                return k
        return None

    frontier = [(0, 0)]
    reps.append((0, 0))
    while frontier:
        nxt = []
        for (x, y) in frontier:
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                p = (x + dx, y + dy)
                if find(*p) is None:
                    reps.append(p)
                    nxt.append(p)
        frontier = nxt
    assert len(reps) == abs(det)
    edges = []
    for k, (x, y) in enumerate(reps):
        edges.append((k, find(x + 1, y)))
        edges.append((k, find(x, y + 1)))
    return len(reps), edges


def extends(nv, edges, x):
    """Is there h with not (h_u = h_v = x_e) on every edge? Forced-value propagation with branching per component."""
    adj = [[] for _ in range(nv)]
    for (u, v), xe in zip(edges, x):
        adj[u].append((v, xe))
        adj[v].append((u, xe))
    val = {}
    for s in range(nv):
        if s in val:
            continue
        for start in (0, 1):
            trial = {s: start}
            stack = [s]
            ok = True
            while stack and ok:
                u = stack.pop()
                for w, xe in adj[u]:
                    if trial[u] == xe:
                        need = 1 - xe
                        have = trial.get(w, val.get(w))
                        if have is None:
                            trial[w] = need
                            stack.append(w)
                        elif have != need:
                            ok = False
                            break
            if ok:
                val.update(trial)
                break
        else:
            return False
    return all(not (val[u] == val[v] == xe) for (u, v), xe in zip(edges, x))


def brute(nv, edges, x):
    return any(all(not (h[u] == h[v] == xe) for (u, v), xe in zip(edges, x)) for h in product((0, 1), repeat=nv))


def decide(rows, shape_threshold=0.05):
    fam = {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r)
    slopes, means = {}, []
    for ratio in ("2/3", "4/3", "2", "4"):
        pts = [(r["size"], r["E"], r["se_E"]) for r in fam[f"F1_{ratio}"]]
        slopes[ratio] = wls_slope(pts)
        means.append(sum(p[1] for p in pts) / len(pts))
    H_shape = all(abs(b) <= shape_threshold for b, _ in slopes.values()) and all(x < y for x, y in zip(means, means[1:]))

    def mean_se(rs):
        return sum(r["E"] for r in rs) / len(rs), math.sqrt(sum(r["se_E"] ** 2 for r in rs)) / len(rs)
    a1, sa1 = mean_se(fam["F2_square_axis"])
    r1, sr1 = mean_se(fam["F2_square_rotated"])
    a2, sa2 = mean_se(fam["F2_long_axis"])
    r2, sr2 = mean_se(fam["F2_long_rotated"])
    d1, s1, d2, s2 = r1 - a1, math.hypot(sa1, sr1), r2 - a2, math.hypot(sa2, sr2)
    H_rotation = abs(d1) <= 0.06 and abs(d1) <= 3 * s1 and abs(d2) <= 0.06 and abs(d2) <= 3 * s2
    return {"slopes": {k: v[0] for k, v in slopes.items()}, "H_shape": H_shape, "H_rotation": H_rotation,
            "square_difference": d1, "long_difference": d2}


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    assert len(rows) == result["rows"], len(rows)
    assert result["controls_ok"] is True and result["control_failures"] == []
    for r in rows:
        if r["family"] == "control_parity":
            assert r["agree"] == r["samples"] == 500
            continue
        p = r["consistent"] / r["samples"]
        assert abs(p - r["P"]) < 1e-12
        if r["consistent"] == 0:
            assert r["E"] is None and abs(r["E_lower_bound"] - math.log2(r["samples"])) < 1e-12
        else:
            assert abs(-math.log2(p) - r["E"]) < 1e-12
            assert abs(math.sqrt(p * (1 - p) / r["samples"]) / (p * math.log(2)) - r["se_E"]) < 1e-12
        if r["family"] == "control_bipartite":
            assert r["consistent"] == r["samples"]
        if r.get("solvers_agree") is not None:
            assert r["solvers_agree"] == r["samples"], r["label"]
        if "both" in r:
            assert r["consistent_and_both"] <= r["both"] <= min(r["up"], r["down"])
            assert r["samples"] - r["consistent"] <= r["both"]          # inconsistency needs two-way crossings
    d = decide(rows)
    for ratio in ("2/3", "4/3", "2", "4"):
        assert abs(d["slopes"][ratio] - result["F1_shape"][ratio]["slope"]) < 1e-12
    assert d["H_shape"] == result["primary"]["H_shape"] and d["H_rotation"] == result["primary"]["H_rotation"]
    assert abs(d["square_difference"] - result["F2_rotation"]["square_difference"]) < 1e-12
    for c in result["F4_coupling"]:
        r = next(x for x in rows if x["family"] == "F1_4/3" and x["size"] == c["size"])
        p1 = 1 - r["up"] / r["samples"]
        p2 = 1 - r["percolation_up"] / r["percolation_samples"]
        se = math.sqrt(p1 * (1 - p1) / r["samples"] + p2 * (1 - p2) / r["percolation_samples"])
        assert abs(round((p1 - p2) / se, 3) - c["z"]) < 1e-9

    # replay with an independent construction, sampler and solver
    nv, edges = torus_points((3, 0), (0, 3))
    rng = random.Random("check-brute")
    for _ in range(300):
        x = [rng.randrange(2) for _ in edges]
        assert extends(nv, edges, x) == brute(nv, edges, x)
    replay = {}
    for family, label, v1, v2 in (("F1_2", "9x18", (18, 0), (0, 9)), ("F2_square_rotated", "(12,5)", (12, 5), (-5, 12))):
        rec = next(r for r in rows if r["family"] == family and r["label"] == label)
        nv, edges = torus_points(v1, v2)
        rng = random.Random(f"check-replay-{label}")
        n = 2500
        good = sum(extends(nv, edges, [rng.randrange(2) for _ in edges]) for _ in range(n))
        p = good / n
        se = math.sqrt(rec["P"] * (1 - rec["P"]) * (1 / n + 1 / rec["samples"]))
        replay[label] = (round(p, 4), round(rec["P"], 4))
        assert abs(p - rec["P"]) <= 5 * se, (label, p, rec["P"])

    altered = decide(rows, shape_threshold=0.0)
    assert altered["H_shape"] is False
    print(f"checked: {len(rows)} rows, verdict {result['verdict']}, primary {result['primary']}, replay {replay}; "
          "altered threshold rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
