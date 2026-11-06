#!/usr/bin/env python3
"""Producer for CONTACT-CENSUS-20261022-001B-E001: the contact census measured, and the conformal test.

Confirmatory Monte Carlo over the roster frozen in contract.json. One placed three-variable contact sits on every edge
of a square-lattice torus (oriented east and north) with hidden joints and fair visible spokes. The producer counts
consistent samples and reports E = -log2 of the consistent fraction. The contact 'x or (h != h')' is judged by two
independent tests (limited backtracking on the transfer tables; union-find bipartiteness of its disequality edges).
Self-contained: it enumerates the knots and placements itself and never reads the predicted values.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import math
import random
import resource
import time
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "CONTACT-CENSUS-20261022-001B" / HERE.name

I = ((1, 0), (0, 1))
S = ((0, 1), (1, 0))
J = ((1, 1), (1, 1))
U = ((1, 1), (0, 1))
L = ((1, 0), (1, 1))
A1 = ((0, 1), (1, 1))
A2 = ((1, 1), (1, 0))
NAMES = {I: "I", S: "S", J: "J", U: "U", L: "L", A1: "A1", A2: "A2"}


# ------------------------------------------------------------------ placements

def placements():
    cube = list(product((0, 1), repeat=3))
    out = []
    for mask in range(1, 256):
        R = frozenset(cube[k] for k in range(8) if mask >> k & 1)
        if len(R) == 8 or not all(len({t[:d] + t[d + 1:] for t in R}) == 4 for d in range(3)):
            continue
        for a, b in ((0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (2, 1)):
            sp = [k for k in range(3) if k not in (a, b)][0]
            pair = []
            for x in (0, 1):
                M = [[0, 0], [0, 0]]
                for t in R:
                    if t[sp] == x:
                        M[t[a]][t[b]] = 1
                pair.append(tuple(map(tuple, M)))
            out.append(tuple(pair))
    return out


def class_name(pair):
    def swap(M):
        return ((M[1][1], M[1][0]), (M[0][1], M[0][0]))

    def tr(M):
        return ((M[0][0], M[1][0]), (M[0][1], M[1][1]))

    variants = []
    for f in (lambda M: M, swap):
        for g in (lambda M: M, tr):
            variants.append("+".join(sorted(NAMES[g(f(M))] for M in pair)))
    return min(variants)


# ------------------------------------------------------------------ tori

def torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    edges = [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)]
    edges += [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]
    return a * b, edges


def hnf(v1, v2):
    (a, b), (c, d) = v1, v2

    def egcd(x, y):
        if y == 0:
            return x, 1, 0
        g, s, t = egcd(y, x % y)
        return g, t, s - (x // y) * t

    g, s, t = egcd(b, d)
    if g < 0:
        g, s, t = -g, -s, -t
    p = abs((d // g) * a - (b // g) * c)
    return p, (s * a + t * c) % p, g


def rotated_torus(v1, v2):
    p, q, r = hnf(v1, v2)

    def canon(x, y):
        beta = y // r
        return (x - beta * q) % p, y - beta * r

    coords = [(x, y) for y in range(r) for x in range(p)]
    index = {c: k for k, c in enumerate(coords)}
    edges = []
    for (x, y) in coords:
        u = index[(x, y)]
        edges.append((u, index[canon(x, y + 1)]))      # north
        edges.append((u, index[canon(x + 1, y)]))      # east
    return len(coords), edges


# ------------------------------------------------------------------ tests

def consistent_tables(nv, edges, mats):
    adj = [[] for _ in range(nv)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k, 0))
        adj[v].append((u, k, 1))
    val = [None] * nv

    def propagate(start, a, changed):
        val[start] = a
        changed.append(start)
        stack = [start]
        while stack:
            u = stack.pop()
            for w, k, side in adj[u]:
                M = mats[k]
                if side == 0:
                    allowed = [c for c in (0, 1) if M[val[u]][c]]
                else:
                    allowed = [c for c in (0, 1) if M[c][val[u]]]
                if val[w] is None:
                    if not allowed:
                        return False
                    if len(allowed) == 1:
                        val[w] = allowed[0]
                        changed.append(w)
                        stack.append(w)
                elif val[w] not in allowed:
                    return False
        return True

    for v in range(nv):
        if val[v] is not None:
            continue
        ok = False
        for a in (0, 1):
            changed = []
            if propagate(v, a, changed):
                ok = True
                break
            for w in changed:
                val[w] = None
        if not ok:
            return False
    return True


def bipartite_open(nv, edges, open_mask):
    parent = list(range(nv))
    par = [0] * nv

    def find(x):
        p = 0
        while parent[x] != x:
            p ^= par[x]
            x = parent[x]
        return x, p

    for (u, v), op in zip(edges, open_mask):
        if not op:
            continue
        ru, pu = find(u)
        rv, pv = find(v)
        if ru == rv:
            if pu == pv:
                return False
        else:
            parent[ru] = rv
            par[ru] = pu ^ pv ^ 1
    return True


# ------------------------------------------------------------------ measuring

def estimate(good, n):
    p = good / n
    if good == 0:
        return p, None, None
    return p, -math.log2(p), math.sqrt(p * (1 - p) / n) / (p * math.log(2))


def measure(family, label, nv, edges, pair, samples, size, or_neq=False, double_check=None):
    t0 = time.time()
    rng = random.Random(f"{family}-{label}")
    good = agree = checked = 0
    disequality_spoke = 0 if pair[0] == S else 1
    for k in range(samples):
        x = [rng.randrange(2) for _ in edges]
        if or_neq:
            ok = bipartite_open(nv, edges, [xe == disequality_spoke for xe in x])
            if double_check is None or k < double_check:
                checked += 1
                agree += ok == consistent_tables(nv, edges, [pair[xe] for xe in x])
        else:
            ok = consistent_tables(nv, edges, [pair[xe] for xe in x])
        good += ok
    p, E, se = estimate(good, samples)
    row = {"family": family, "label": label, "vertices": nv, "edges": len(edges), "samples": samples, "consistent": good,
           "P": p, "E": E, "se_E": se, "E_lower_bound": math.log2(samples) if good == 0 else None, "size": size,
           "tests_agree": agree if or_neq else None, "doubly_judged": checked if or_neq else None,
           "seconds": round(time.time() - t0, 1)}
    print(json.dumps({k: row[k] for k in ("family", "label", "E", "se_E", "seconds")}), flush=True)
    return row


def wls(points):
    xs = [math.log2(s) for s, _, _ in points]
    ys = [e for _, e, _ in points]
    ws = [1 / se ** 2 for _, _, se in points]
    W = sum(ws)
    xm = sum(w * x for w, x in zip(ws, xs)) / W
    ym = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - xm) ** 2 for w, x in zip(ws, xs))
    return sum(w * (x - xm) * (y - ym) for w, x, y in zip(ws, xs, ys)) / sxx, math.sqrt(1 / sxx)


def wmean(rows):
    ws = [1 / r["se_E"] ** 2 for r in rows]
    m = sum(w * r["E"] for w, r in zip(ws, rows)) / sum(ws)
    return m, math.sqrt(1 / sum(ws))


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows, failures = [], []
    NAE, ORNEQ = (A1, A2), (S, J)

    # controls: bipartite tori
    for a in (16, 32):
        nv, edges = torus(a, a)
        for name, pair, flag in (("not-all-equal", NAE, False), ("x or (h != h')", ORNEQ, True)):
            r = measure("control_bipartite", f"{name} {a}x{a}", nv, edges, pair, 2000, a, or_neq=flag)
            rows.append(r)
            if r["consistent"] != r["samples"] or (flag and r["tests_agree"] != r["doubly_judged"]):
                failures.append(f"bipartite control {name} {a}")
    if failures:
        return finish(rows, failures, started, contract)

    # C1 census
    vacuum = {"I+J": (I, J), "L+U": (U, L), "A1+I": (A1, I), "A1+J": (A1, J), "J+L": (J, L), "A1+L": (A1, L)}
    for name, pair in vacuum.items():
        for a, b in ((9, 9), (17, 17), (9, 18)):
            nv, edges = torus(a, b)
            rows.append(measure(f"C1_vacuum_{name}", f"{a}x{b}", nv, edges, pair, 2000, a))
    for a, b, n in ((3, 3, 200000), (3, 5, 1000000)):
        nv, edges = torus(a, b)
        rows.append(measure("C1_parity", f"{a}x{b}", nv, edges, (I, S), n, a))
    for a, n in ((3, 200000), (5, 200000)):
        nv, edges = torus(a, a)
        rows.append(measure("C1_swap_or_order", f"{a}x{a}", nv, edges, (S, L), n, a))
    for a in (9, 17, 33, 65):
        nv, edges = torus(a, a)
        rows.append(measure("C1_not_all_equal", f"{a}x{a}", nv, edges, NAE, 8000, a))
        rows.append(measure("C1_or_neq", f"{a}x{a}", nv, edges, ORNEQ, 8000, a, or_neq=True,
                            double_check=None if a <= 33 else 1000))

    # C2 conformal test for x or (h != h')
    shapes = {"square_both_odd": [(a, a) for a in (9, 17, 33, 65)],
              "rows_odd_columns_double": [(a, 2 * a) for a in (9, 17, 33, 65)],
              "columns_odd_rows_double": [(2 * a, a) for a in (9, 17, 33)],
              "rows_3k_columns_2k": [(3 * k, 2 * k) for k in (3, 5, 11, 21)],
              "both_odd_3_by_5": [(3 * m, 5 * m) for m in (3, 5, 9, 13)]}
    for shape, sizes in shapes.items():
        for a, b in sizes:
            nv, edges = torus(a, b)
            rows.append(measure(f"C2_{shape}", f"{a}x{b}", nv, edges, ORNEQ, 10000, min(a, b), or_neq=True,
                                double_check=None if max(a, b) <= 33 else 1000))
    for c, d in ((12, 5), (24, 7), (20, 13), (35, 12)):
        nv, edges = rotated_torus((c, d), (-d, c))
        rows.append(measure("C2_rotated_square", f"({c},{d})", nv, edges, ORNEQ, 10000, round(math.hypot(c, d), 2),
                            or_neq=True, double_check=None if nv <= 1100 else 1000))

    # C3 contrast
    for a in (17, 33):
        nv, edges = torus(a, 2 * a)
        rows.append(measure("C3_not_all_equal_1to2", f"{a}x{2 * a}", nv, edges, NAE, 8000, a))

    # C4 all placements of the critical classes on 17 x 17
    nv, edges = torus(17, 17)
    seen = {}
    for pair in placements():
        name = class_name(pair)
        if name in ("A1+A2", "J+S"):
            seen.setdefault(name, []).append(pair)
    for name, pairs in seen.items():
        for k, pair in enumerate(pairs):
            label = f"{name} #{k} " + "/".join(NAMES[M] for M in pair)
            rows.append(measure(f"C4_{name}", label, nv, edges, pair, 4000, 17, or_neq=(name == "J+S"), double_check=500))

    for r in rows:
        if r.get("tests_agree") is not None and r["tests_agree"] != r["doubly_judged"]:
            failures.append(f"test disagreement {r['family']} {r['label']}")
    return finish(rows, failures, started, contract)


def finish(rows, failures, started, contract):
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not failures, "control_failures": failures,
              "rows": len(rows)}
    if not failures:
        fam = {}
        for r in rows:
            fam.setdefault(r["family"], []).append(r)
        pred = contract["predictions"]["pinson_limits_bits"]
        conformal = {}
        ok_conf, refuted = True, False
        for shape, limit in pred.items():
            rs = fam[f"C2_{shape}"]
            m, se = wmean(rs[-2:])
            dev = m - limit
            conformal[shape] = {"E": [round(r["E"], 4) for r in rs], "se": [round(r["se_E"], 4) for r in rs],
                                "two_largest_mean": m, "se_mean": se, "limit": limit, "deviation": dev}
            ok_conf &= abs(dev) <= 3 * se + 0.01
            refuted |= abs(dev) > 5 * se + 0.02
        rm, rse = wmean(fam["C2_rotated_square"])
        conformal["rotated_square"] = {"E": [round(r["E"], 4) for r in fam["C2_rotated_square"]], "mean": rm, "se_mean": rse,
                                       "limit": pred["square_both_odd"], "deviation": rm - pred["square_both_odd"]}
        ok_conf &= abs(rm - pred["square_both_odd"]) <= 3 * rse + 0.01

        vac_ok = all(r["consistent"] == r["samples"] for k, v in fam.items() if k.startswith("C1_vacuum") for r in v)
        par = fam["C1_parity"]
        par_ok = abs(par[0]["E"] - 10) <= 3 * par[0]["se_E"] and par[1]["E"] is not None and abs(par[1]["E"] - 16) <= 3 * par[1]["se_E"]
        so = fam["C1_swap_or_order"]
        so_ok = so[1]["E"] is not None and so[1]["E"] > so[0]["E"] + 3
        crit = {}
        for name in ("C1_not_all_equal", "C1_or_neq"):
            pts = [(r["size"], r["E"], r["se_E"]) for r in fam[name]]
            b, s = wls(pts)
            crit[name] = {"E": [round(p[1], 4) for p in pts], "slope": b, "slope_se": s, "mean": sum(p[1] for p in pts) / len(pts)}
        crit_ok = all(abs(v["slope"]) <= 0.05 for v in crit.values()) and \
            abs(crit["C1_not_all_equal"]["mean"] - crit["C1_or_neq"]["mean"]) > 0.5
        H_census = vac_ok and par_ok and so_ok and crit_ok

        plc = {}
        H_placements = True
        for name in ("C4_A1+A2", "C4_J+S"):
            rs = fam[name]
            m, _ = wmean(rs)
            zs = [(r["E"] - m) / r["se_E"] for r in rs]
            plc[name] = {"E": [round(r["E"], 4) for r in rs], "mean": m, "max_abs_z": max(abs(z) for z in zs), "count": len(rs)}
            H_placements &= max(abs(z) for z in zs) <= 3.5 and len(rs) == 12
        verdict = "supported" if ok_conf and H_census and H_placements else ("refuted" if refuted else "closed-null")
        result.update({
            "C2_conformal": conformal, "C1_critical": crit,
            "C1_parity": [{"label": r["label"], "E": r["E"], "se_E": r["se_E"]} for r in par],
            "C1_swap_or_order": [{"label": r["label"], "E": r["E"], "se_E": r["se_E"]} for r in so],
            "C1_vacuum_all_consistent": vac_ok,
            "C3_not_all_equal_1to2": [round(r["E"], 4) for r in fam["C3_not_all_equal_1to2"]],
            "C4_placements": plc,
            "primary": {"H_conformal": ok_conf, "H_census": H_census, "H_placements": H_placements},
            "verdict": verdict,
        })
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    (OUT / "raw_rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in result if k in ("controls_ok", "primary", "verdict", "wall_seconds")}, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
