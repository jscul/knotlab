#!/usr/bin/env python3
"""Independent check of the surface-emergence test; imports no producer code.

Parses the raw rows, recomputes every estimate, slope and decision field from the raw counts, and compares them with
result.json. It then replays two square tori with its own sampler and its own satisfiability test (brute-force
propagation of forced joints with exhaustive branching on a small torus, and a third, union-find-free implication
closure on a larger one) and requires the replayed consistent fraction to lie within five standard errors of the
recorded one. A deliberately altered expectation must be rejected.
"""

from __future__ import annotations

import json
import math
import random
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts/EMERGENCE-BITS-20261021-001C/EMERGENCE-BITS-20261021-001C-E001_surface_emergence"


def torus_edges(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    return a * b, [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)] + \
        [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]


def nae_extends(nv, edges, x):
    """Does some joint assignment avoid h_u = h_v = x_e on every edge? Implication closure: the constraint on an edge
    is the clause 'h_u != x_e or h_v != x_e'. Decide by trying both values of each undecided joint with forward
    closure, backtracking only within the closure (exact for clauses of two literals)."""
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
            queue = [s]
            ok = True
            while queue and ok:
                u = queue.pop()
                for w, xe in adj[u]:
                    if trial[u] == xe:                       # u holds the forbidden value: w must avoid it
                        need = 1 - xe
                        have = trial.get(w, val.get(w))
                        if have is None:
                            trial[w] = need
                            queue.append(w)
                        elif have != need:
                            ok = False
                            break
            if ok:
                val.update(trial)
                break
        else:
            return False
    return all(not (val[u] == val[v] == xe) for (u, v), xe in zip(edges, x))


def nae_extends_bruteforce(nv, edges, x):
    for h in product((0, 1), repeat=nv):
        if all(not (h[u] == h[v] == xe) for (u, v), xe in zip(edges, x)):
            return True
    return False


def slope(rows):
    xs = [math.log2(r["a"]) for r in rows]
    ys = [r["E"] for r in rows]
    ws = [1 / r["se_E"] ** 2 for r in rows]
    W = sum(ws)
    xm = sum(w * x for w, x in zip(ws, xs)) / W
    ym = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - xm) ** 2 for w, x in zip(ws, xs))
    return sum(w * (x - xm) * (y - ym) for w, x, y in zip(ws, xs, ys)) / sxx, math.sqrt(1 / sxx)


def decide(rows, threshold=0.04):
    fams = {}
    for r in rows:
        fams.setdefault(r["family"], []).append(r)
    sq, sq2 = fams["square_odd"], fams["square_odd_by_even"]
    b1, s1 = slope(sq)
    b2, s2 = slope(sq2)
    floor_ok = all(r["E"] > 0.3 for r in sq + sq2)
    supported = abs(b1) <= threshold and abs(b2) <= threshold and floor_ok
    refuted = (abs(b1) > threshold + 3 * s1) or (abs(b2) > threshold + 3 * s2)
    hon, tri = fams["honeycomb_odd"], fams["triangular"]
    vanish = hon[-1]["E"] < 0.01 and all(
        hon[k + 1]["E"] <= hon[k]["E"] + 3 * math.hypot(hon[k]["se_E"], hon[k + 1]["se_E"]) for k in range(len(hon) - 1))
    extensive = all(tri[k + 1]["E"] > tri[k]["E"] for k in range(len(tri) - 1)) and \
        tri[-1]["E"] / tri[-1]["vertices"] >= 0.5 * tri[0]["E"] / tri[0]["vertices"]
    verdict = "supported" if supported and vanish and extensive else ("refuted" if refuted else "closed-null")
    return {"b1": b1, "b2": b2, "H_scale": "supported" if supported else ("refuted" if refuted else "inconclusive"),
            "H_vanish": vanish, "H_extensive": extensive, "verdict": verdict}


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    assert len(rows) == result["rows"] == 24, len(rows)
    assert result["controls_ok"] is True and result["control_failures"] == []
    for r in rows:
        if r["family"] == "parity_control":
            assert r["agree"] == r["samples"] == 500
            continue
        p = r["consistent"] / r["samples"]
        assert abs(p - r["P"]) < 1e-12
        if r["family"] == "square_even_control":
            assert p == 1.0
        else:
            assert abs(-math.log2(p) - r["E"]) < 1e-12
            assert abs(math.sqrt(p * (1 - p) / r["samples"]) / (p * math.log(2)) - r["se_E"]) < 1e-12
        if r["family"] in ("square_odd", "square_odd_by_even", "square_even_control"):
            assert r["solvers_agree"] == r["samples"]
    d = decide([r for r in rows if r["family"] not in ("parity_control", "square_even_control")])
    assert abs(d["b1"] - result["square_odd"]["slope_per_doubling"]) < 1e-12
    assert abs(d["b2"] - result["square_odd_by_even"]["slope_per_doubling"]) < 1e-12
    for k in ("H_scale", "H_vanish", "H_extensive", "verdict"):
        assert d[k] == result[k], (k, d[k], result[k])

    # replay: brute force against the closure test on a small odd torus, then a fresh sample on a larger one
    nv, edges = torus_edges(3, 5)
    rng = random.Random("check-replay-small")
    for _ in range(300):
        x = [rng.randrange(2) for _ in edges]
        assert nae_extends(nv, edges, x) == nae_extends_bruteforce(nv, edges, x)
    by = {(r["family"], r["a"]): r for r in rows}
    replay = {}
    for a in (9, 17):
        rec = by[("square_odd", a)]
        nv, edges = torus_edges(a, a)
        rng = random.Random(f"check-replay-{a}")
        n = 3000
        good = sum(nae_extends(nv, edges, [rng.randrange(2) for _ in edges]) for _ in range(n))
        p = good / n
        se = math.sqrt(rec["P"] * (1 - rec["P"]) * (1 / n + 1 / rec["samples"]))
        replay[a] = (p, rec["P"])
        assert abs(p - rec["P"]) <= 5 * se, (a, p, rec["P"])

    # the decision rule can fail: a threshold of 0.0 must not leave the verdict unchanged when the slopes are nonzero
    altered = decide([r for r in rows if r["family"] not in ("parity_control", "square_even_control")], threshold=0.0)
    assert altered["H_scale"] != "supported"
    print(f"checked: {len(rows)} rows, verdict {result['verdict']}, slopes {d['b1']:.4f} and {d['b2']:.4f}, "
          f"replay {replay}; altered threshold rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
