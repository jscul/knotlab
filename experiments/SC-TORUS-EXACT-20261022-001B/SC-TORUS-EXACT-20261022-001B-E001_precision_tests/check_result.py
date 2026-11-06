#!/usr/bin/env python3
"""Independent check of the precision tests; imports no producer code.

Parses raw_rows.jsonl and the frozen contract, checks that the rows are the frozen roster and satisfy the exact count
identities, recomputes every estimate, fit and decision with its own code (estimators from outcome distributions, least
squares by elimination), re-evaluates every declared control, and compares with result.json. The rectangle identity of
the cone theorem is evaluated directly from the wrapping counts, and the duality control is also applied to the twisted
sectors of the common-random-number rows. Three small tori are replayed in pure Python by different methods: consistency
of the x-twisted 16 x 16 torus by propagation on its two-literal clauses; untwisted 16 x 16 wrapping by Kosaraju
components and lifted potentials; directed winding on 16 x 16 by textbook Bellman-Ford with V rounds. Shifted target
values must be decisively rejected (power).

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/SC-TORUS-EXACT-20261022-001B" / HERE.name

# the frozen roster, copied from contract.json public_inputs: (family, Lh, Lv, s, px, py) -> samples
ROSTER = {("F_small", 16, 16, 0, 1, 0): 20000, ("F_small", 16, 16, 0, 0, 0): 20000,
          ("F_half", 64, 64, 0, 1, 0): 7000000, ("F_half", 128, 128, 0, 1, 0): 7000000,
          ("F_half", 256, 256, 0, 1, 0): 3200000, ("F_half", 512, 512, 0, 1, 0): 1100000,
          ("F_34", 64, 64, 0, 0, 0): 6000000, ("F_34", 128, 128, 0, 0, 0): 6000000,
          ("F_34", 256, 256, 0, 0, 0): 3300000, ("F_34", 512, 512, 0, 0, 0): 1400000,
          ("F_long", 128, 64, 0, 1, 0): 1000000, ("F_long", 192, 64, 0, 1, 0): 1500000, ("F_long", 256, 64, 0, 1, 0): 3000000,
          ("F_short", 64, 128, 0, 1, 0): 400000, ("F_short", 64, 192, 0, 1, 0): 400000, ("F_short", 64, 256, 0, 1, 0): 400000,
          ("F_scan", 256, 256, 0, 1, 1): 400000, ("F_scan", 128, 128, 64, 1, 0): 400000, ("F_scan", 128, 128, 64, 0, 1): 400000,
          ("F_scan", 128, 128, 64, 1, 1): 400000, ("F_scan", 256, 128, 0, 1, 0): 400000, ("F_scan", 128, 256, 0, 1, 0): 400000,
          ("F_scan", 256, 128, 0, 1, 1): 400000}
CRN_ROSTER = {(64, 64, 0): 2200000, (128, 128, 0): 2200000, (256, 256, 0): 800000, (128, 64, 0): 1000000}
DIR_ROSTER = {16: 20000, 64: 400000, 128: 200000}
BETA_NU = 0.19635


def same(a, b, tol=1e-9):
    assert abs(a - b) <= tol * max(1.0, abs(a), abs(b)), (a, b)


def moments(outcomes, n):
    """Mean and standard error of a per-sample variable given (count, value) pairs over n samples."""
    mean = sum(c * v for c, v in outcomes) / n
    var = sum(c * (v - mean) ** 2 for c, v in outcomes) / n
    return mean, math.sqrt(var / n)


def consistent(r):
    """P(consistent) = P(contractible) + P(even winding) with P(contractible) replaced by (contractible + cross)/2."""
    return moments([(r["contr"], 0.5), (r["cross"], 0.5), (r["wind_even"], 1.0), (r["wind_odd"], 0.0)], r["samples"])


def one_direction(r):
    """Untwisted square: (1[H] + 1[V])/2 per sample."""
    n, both = r["samples"], r["hvwrap"]
    return moments([(both, 1.0), (r["hwrap"] - both, 0.5), (r["vwrap"] - both, 0.5),
                    (n - r["hwrap"] - r["vwrap"] + both, 0.0)], n)


def invert(M):
    k = len(M)
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(M)]
    for c in range(k):
        p = max(range(c, k), key=lambda i: abs(a[i][c]))
        a[c], a[p] = a[p], a[c]
        piv = a[c][c]
        a[c] = [v / piv for v in a[c]]
        for i in range(k):
            if i != c:
                f = a[i][c]
                a[i] = [v - f * u for v, u in zip(a[i], a[c])]
    return [row[k:] for row in a]


def lsq(xs, ys, ses, degree):
    """Weighted polynomial least squares; returns coefficients, their standard errors and chi-square."""
    k = degree + 1
    A = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    for x, y, s in zip(xs, ys, ses):
        w = 1 / (s * s)
        for i in range(k):
            b[i] += w * x ** i * y
            for j in range(k):
                A[i][j] += w * x ** (i + j)
    inv = invert(A)
    coef = [sum(inv[i][j] * b[j] for j in range(k)) for i in range(k)]
    chi2 = sum((y - sum(c * x ** i for i, c in enumerate(coef))) ** 2 / s ** 2 for x, y, s in zip(xs, ys, ses))
    return coef, [math.sqrt(inv[i][i]) for i in range(k)], chi2


# ------------------------------------------------------------------ independent replays

class Lattice:
    def __init__(self, Lh, Lv, s):
        self.Lh, self.Lv, self.s, self.V = Lh, Lv, s, Lh * Lv
        self.edges = []      # (u, w, period offset (a, b)): w + a*(Lh, 0) + b*(s, Lv) is the lattice neighbour of u
        for u in range(self.V):
            x, y = u % Lh, u // Lh
            self.edges.append((u, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
            if y + 1 < Lv:
                self.edges.append((u, u + Lh, (0, 0)))
            else:
                X = x - s
                a = X // Lh
                self.edges.append((u, X - a * Lh, (a, 1)))


def satisfiable(n, clauses):
    """Two-literal satisfiability by trial assignment and propagation (literal 2v + 1 is the negation of x_v)."""
    imp = [[] for _ in range(2 * n)]
    for a, b in clauses:
        imp[a ^ 1].append(b)
        imp[b ^ 1].append(a)
    val = [-1] * n
    for v in range(n):
        if val[v] >= 0:
            continue
        for first in (2 * v, 2 * v + 1):
            trail, stack, ok = [], [first], True
            while stack:
                lit = stack.pop()
                x, want = lit >> 1, 1 - (lit & 1)
                if val[x] >= 0:
                    if val[x] != want:
                        ok = False
                        break
                    continue
                val[x] = want
                trail.append(x)
                stack.extend(imp[lit])
            if ok:
                break
            for x in trail:
                val[x] = -1
        else:
            return False
    return True


def replay_consistency(Lh, Lv, px, py, m, seed):
    """Each edge gives one clause: orientation u -> w is x_u => (x_w, negated when the twist is odd on the edge)."""
    lat, rng, good = Lattice(Lh, Lv, 0), random.Random(seed), 0
    for _ in range(m):
        clauses = []
        for u, w, (a, b) in lat.edges:
            lw = 2 * w + ((a * px + b * py) & 1)
            clauses.append((2 * u + 1, lw) if rng.getrandbits(1) else (lw ^ 1, 2 * u))
        good += satisfiable(lat.V, clauses)
    return good / m


def kosaraju(n, adj):
    radj = [[] for _ in range(n)]
    for v in range(n):
        for w in adj[v]:
            radj[w].append(v)
    seen, order = [False] * n, []
    for r in range(n):
        if seen[r]:
            continue
        seen[r] = True
        stack = [(r, iter(adj[r]))]
        while stack:
            v, it = stack[-1]
            for w in it:
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, iter(adj[w])))
                    break
            else:
                stack.pop()
                order.append(v)
    comp, c = [-1] * n, 0
    for r in reversed(order):
        if comp[r] >= 0:
            continue
        comp[r], stack = c, [r]
        while stack:
            v = stack.pop()
            for w in radj[v]:
                if comp[w] < 0:
                    comp[w] = c
                    stack.append(w)
        c += 1
    return comp


def wrapping(lat, comp):
    """Lift each strong component by breadth-first potentials; a mismatch on a closing edge is a cycle class."""
    nb = [[] for _ in range(lat.V)]
    for u, w, (a, b) in lat.edges:
        if comp[u] == comp[w]:
            nb[u].append((w, a, b))
            nb[w].append((u, -a, -b))
    pos, h, v = [None] * lat.V, False, False
    for root in range(lat.V):
        if pos[root] is not None:
            continue
        pos[root], queue = (0, 0), [root]
        for u in queue:
            pu = pos[u]
            for w, a, b in nb[u]:
                t = (pu[0] + a, pu[1] + b)
                if pos[w] is None:
                    pos[w] = t
                    queue.append(w)
                elif pos[w] != t:
                    h |= t[0] != pos[w][0]
                    v |= t[1] != pos[w][1]
    return h, v


def replay_untwisted(L, m, seed):
    lat, rng = Lattice(L, L, 0), random.Random(seed)
    noh = contr = 0
    for _ in range(m):
        adj = [[] for _ in range(lat.V)]
        for u, w, _o in lat.edges:
            (adj[u].append(w) if rng.getrandbits(1) else adj[w].append(u))
        h, v = wrapping(lat, kosaraju(lat.V, adj))
        noh += not h
        contr += not (h or v)
    return noh / m, contr / m


def positive_closed_walk(V, arcs):
    """Textbook Bellman-Ford for the longest walk from a virtual source: a change in round V means a positive cycle."""
    dist = [0] * V
    for _ in range(V):
        changed = False
        for u, w, c in arcs:
            if dist[u] + c > dist[w]:
                dist[w] = dist[u] + c
                changed = True
        if not changed:
            return False
    return True


def replay_directed(L, m, seed):
    """Directed winding by sign; per sample it must agree with undirected wrapping of the strong components."""
    lat, rng = Lattice(L, L, 0), random.Random(seed)
    counts, disagree = [0] * 16, 0
    for _ in range(m):
        arcs = []
        for u, w, (a, b) in lat.edges:
            arcs.append((u, w, a, b) if rng.getrandbits(1) else (w, u, -a, -b))
        bits = 0
        for i, (key, sign) in enumerate(((2, 1), (2, -1), (3, 1), (3, -1))):
            if positive_closed_walk(lat.V, [(t[0], t[1], sign * t[key]) for t in arcs]):
                bits |= 1 << i
        counts[bits] += 1
        adj = [[] for _ in range(lat.V)]
        for t in arcs:
            adj[t[0]].append(t[1])
        h, v = wrapping(lat, kosaraju(lat.V, adj))
        disagree += (bits & 3 != 0) != h or (bits & 12 != 0) != v
    return counts, disagree


# ------------------------------------------------------------------ checks

def directed_summary(states, n):
    P = lambda f: sum(states[i] for i in range(16) if f(i & 1, (i >> 1) & 1, (i >> 2) & 1, (i >> 3) & 1)) / n
    return {"H+ only": P(lambda a, b, c, d: a and not b), "H- only": P(lambda a, b, c, d: b and not a),
            "both": P(lambda a, b, c, d: a and b), "neither": P(lambda a, b, c, d: not a and not b),
            "no winding at all": P(lambda a, b, c, d: not (a or b or c or d)), "all four": P(lambda a, b, c, d: a and b and c and d)}


def main(art=ART, frozen=True) -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((art / "result.json").read_text())
    rows = [json.loads(line) for line in (art / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    assert result["experiment_id"] == contract["experiment_id"] and len(rows) == result["rows"]
    pred = contract["predictions"]
    for key in ("candidate_half_bit", "candidate_three_quarters"):
        assert "<= 3 sigma" in pred[key] and "> 5 sigma" in pred[key]
    assert "<= 3 sigma" in pred["candidate_additivity"] and "3 sigma + 0.005" in pred["candidate_beta_nu"]
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)

    # roster
    if frozen:
        got = {(r["family"], r["Lh"], r["Lv"], r["s"], r["px"], r["py"]): r["samples"] for r in rows if r["mode"] == "sector"}
        assert got == ROSTER, set(got.items()) ^ set(ROSTER.items())
        assert {(r["Lh"], r["Lv"], r["s"]): r["samples"] for r in by["F_add"]} == CRN_ROSTER
        assert {r["L"]: r["samples"] for r in by["F_dir"]} == DIR_ROSTER
        assert len(rows) == len(ROSTER) + len(CRN_ROSTER) + len(DIR_ROSTER)

    # exact count identities, row by row
    fails = []
    for r in rows:
        if r["mode"] == "sector":
            n, tw = r["samples"], r["px"] or r["py"]
            wind = r["wind_odd"] + r["wind_even"]
            assert r["contr"] + r["cross"] + wind == n
            assert r["hwrap"] + r["vwrap"] - r["hvwrap"] == n - r["contr"]          # every winding class is nonzero
            assert r["cross"] <= r["hvwrap"] <= min(r["hwrap"], r["vwrap"])
            cl = {tuple(map(int, k.split(","))): v for k, v in r["classes"].items()}
            assert all(a >= 0 and math.gcd(a, b) == 1 and (a, b) != (0, -1) for a, b in cl)
            odd = sum(v for (a, b), v in cl.items() if (a * r["px"] + b * r["py"]) & 1)
            assert sum(cl.values()) <= wind and odd <= r["wind_odd"] and sum(cl.values()) - odd <= r["wind_even"]
            if sum(cl.values()) == wind:
                assert odd == r["wind_odd"]
            assert sum(v for (a, b), v in cl.items() if a) <= r["hwrap"] - r["cross"]
            assert sum(v for (a, b), v in cl.items() if a and b) <= r["hvwrap"] - r["cross"]
            if tw:
                assert r["cons"] == r["contr"] + r["wind_even"] and r["invariant"] == n - r["cons"]
                if r["mismatch"]:
                    fails.append(f"test disagreement {r['label']}")
                if abs(r["contr"] - r["cross"]) > 4 * math.sqrt(r["contr"] + r["cross"]):
                    fails.append(f"duality {r['family']} {r['label']}")
            else:
                assert r["cons"] == n and r["wind_odd"] == 0 and r["invariant"] == 0 and r["mismatch"] == 0
        elif r["mode"] == "crn":
            n = r["samples"]
            assert r["dsum"] == r["c00"] - r["c10"] - r["c01"] + r["c11"]
            assert r["ssum"] == r["c00"] - (r["c10"] + r["x10"]) / 2 - (r["c01"] + r["x01"]) / 2 + (r["c11"] + r["x11"]) / 2
            assert r["ssq"] >= r["ssum"] ** 2 / n - 1e-6 and r["dsq"] >= r["dsum"] ** 2 / n - 1e-6
        else:
            assert sum(r["states"]) == r["samples"]

    # controls: the rectangle identity of the cone theorem, P(no H) + P(no V) = 1 - P(lines in classes with both
    # coordinates nonzero); per sample it is 1[contractible] - 1[cross], so its error comes from those two counts
    extra = []
    for r in rows:
        if r["mode"] == "sector" and (r["px"] or r["py"]):
            n = r["samples"]
            z = ((n - r["hwrap"]) + (n - r["vwrap"]) - (n - (r["hvwrap"] - r["cross"]))) / n
            _m, se = moments([(r["contr"], 1.0), (r["cross"], -1.0), (n - r["contr"] - r["cross"], 0.0)], n)
            if abs(z) > 4 * se:
                fails.append(f"rectangle identity {r['family']} {r['label']}")
            extra.append(z / se if se else 0.0)
        if r["mode"] == "crn":
            for q in ("10", "01", "11"):
                c, x = r["c" + q], r["x" + q]
                if abs(c - x) > 4 * math.sqrt(c + x):
                    fails.append(f"duality F_add {r['label']} sector {q}")
    und = {r["Lh"]: r for r in by["F_34"]}
    for r in by["F_dir"]:
        if r["L"] in und:
            n, u = r["samples"], und[r["L"]]
            neither = directed_summary(r["states"], n)["neither"]
            notH = 1 - u["hwrap"] / u["samples"]
            if abs(neither - notH) > 4 * math.sqrt(neither * (1 - neither) / n + notH * (1 - notH) / u["samples"]):
                fails.append(f"directed vs undirected at L={r['L']}")
    producer_fails = [f for f in fails if not f.startswith(("rectangle identity", "duality F_add"))]
    assert producer_fails == result["control_failures"] and result["controls_ok"] == (not producer_fails)
    assert not fails, fails
    if result["verdict"] == "invalid":
        print("run invalid; controls failed:", fails)
        return 0

    # half bit
    half = sorted(by["F_half"], key=lambda r: r["Lh"])
    pts = []
    for r, rec in zip(half, result["half_bit"]["points"]):
        p, sp = consistent(r)
        E, sE = -math.log2(p), sp / (p * math.log(2))
        assert rec["L"] == r["Lh"]
        same(p, rec["P"]); same(sp, rec["sigma_P"], 1e-7); same(E, rec["E"]); same(sE, rec["sigma_E"], 1e-7)
        same((r["contr"] + r["wind_even"]) / r["samples"], rec["P_raw"])
        pts.append((1 / r["Lh"], E, sE))
    (E_inf, slope), (sig, _), chi2 = lsq(*zip(*pts), 1)
    (E2, _b, _c), (sig2, _sb, _sc), _ = lsq(*zip(*pts), 2)
    hb = result["half_bit"]
    same(E_inf, hb["E_inf"]); same(sig, hb["sigma"], 1e-7); same(slope, hb["slope"], 1e-7); same(chi2, hb["chi2"], 1e-6)
    same(E2, hb["E_inf_quadratic"], 1e-7); same(sig2, hb["sigma_quadratic"], 1e-5)
    half_acc, half_rej = abs(E_inf - 0.5) <= 3 * sig, abs(E_inf - 0.5) > 5 * sig
    assert (half_acc, half_rej) == (hb["accepted"], hb["decisively_rejected"])

    # three quarters
    w34 = sorted(by["F_34"], key=lambda r: r["Lh"])
    pts = []
    for r, rec in zip(w34, result["three_quarters"]["points"]):
        W, sW = one_direction(r)
        assert rec["L"] == r["Lh"]
        same(W, rec["W"]); same(sW, rec["sigma"], 1e-7); same(r["hwrap"] / r["samples"], rec["W_raw_h"])
        pts.append((1 / r["Lh"], W, sW))
    (W_inf, wslope), (wsig, _), wchi2 = lsq(*zip(*pts), 1)
    (W2, _b, _c), (wsig2, _sb, _sc), _ = lsq(*zip(*pts), 2)
    tq = result["three_quarters"]
    same(W_inf, tq["W_inf"]); same(wsig, tq["sigma"], 1e-7); same(wslope, tq["slope"], 1e-7); same(wchi2, tq["chi2"], 1e-6)
    same(W2, tq["W_inf_quadratic"], 1e-7); same(wsig2, tq["sigma_quadratic"], 1e-5)
    tq_acc, tq_rej = abs(W_inf - 0.75) <= 3 * wsig, abs(W_inf - 0.75) > 5 * wsig
    assert (tq_acc, tq_rej) == (tq["accepted"], tq["decisively_rejected"])

    # additivity
    add = {}
    for r in by["F_add"]:
        n = r["samples"]
        D = r["ssum"] / n
        add[(r["Lh"], r["Lv"])] = (D, math.sqrt(max(r["ssq"] / n - D * D, 0) / n))
    sq = sorted(k for k in add if k[0] == k[1])
    (D_inf, _s), (dsig, _), _c = lsq([1 / k[0] for k in sq], [add[k][0] for k in sq], [add[k][1] for k in sq], 1)
    ad = result["additivity"]
    same(D_inf, ad["D_inf"]); same(dsig, ad["sigma"], 1e-7)
    rect = add[(128, 64)] if frozen else next(v for k, v in add.items() if k[0] != k[1])
    same(rect[0], ad["rectangle"]["D"]); same(rect[1], ad["rectangle"]["sigma"], 1e-7)
    add_acc = abs(D_inf) <= 3 * dsig and abs(rect[0]) <= 3 * rect[1]
    assert add_acc == ad["accepted"]

    # beta/nu from the long side; the short-side exponent
    lg = sorted(by["F_long"], key=lambda r: r["Lh"])
    ks, ys, ses = [], [], []
    for r in lg:
        p, sp = consistent(r)
        ks.append(r["Lh"] / r["Lv"]); ys.append(math.log(1 - p)); ses.append(sp / (1 - p))
    (_a, sl), (_sa, ssl), _c = lsq(ks, ys, ses, 1)
    x, sx = -sl / (2 * math.pi), ssl / (2 * math.pi)
    same(x, result["beta_nu"]["x"], 1e-7); same(sx, result["beta_nu"]["sigma"], 1e-6)
    bn_acc = abs(x - BETA_NU) <= 3 * sx + 0.005
    assert bn_acc == result["beta_nu"]["accepted"]
    sh = sorted(by["F_short"], key=lambda r: r["Lv"])
    ks, ys, ses = [], [], []
    for r in sh:
        p, sp = consistent(r)
        ks.append(r["Lv"] / r["Lh"]); ys.append(math.log(p)); ses.append(sp / p)
    (_a, sl2), (_sa, ssl2), chi2s = lsq(ks, ys, ses, 1)
    xs_short = -sl2 / (2 * math.pi)
    same(xs_short, result["short_side_exponent"]["x"], 1e-7); same(chi2s, result["short_side_exponent"]["chi2"], 1e-6)

    # directed law, its symmetries, and the scan
    sym = []
    for r in by["F_dir"]:
        n, s = r["samples"], r["states"]
        d = directed_summary(s, n)
        for k, v in d.items():
            same(v, result["directed_law"][r["label"]][k])
        P = lambda f: sum(s[i] for i in range(16) if f(i)) / n
        for p1, p2 in ((d["H+ only"], d["H- only"]), (P(lambda i: i & 1), P(lambda i: i & 4)),
                       (P(lambda i: i & 3 == 0), P(lambda i: i & 12 == 0))):
            sym.append(abs(p1 - p2) / math.sqrt(max(p1 + p2, 1e-12) / n))
    assert max(sym) <= 5, sym
    for r, rec in zip(by["F_scan"] + by["F_small"], result["scan"]):
        n, tw = r["samples"], r["px"] or r["py"]
        assert rec["label"] == r["label"]
        if tw:
            p, sp = consistent(r)
            same(p, rec["P_consistent"]); same(sp, rec["sigma"], 1e-7)
            same((r["contr"] + r["cross"]) / (2 * n), rec["P_contractible"])
        else:
            assert rec["P_consistent"] is None
            same(r["contr"] / n, rec["P_contractible"])
        same((n - r["hwrap"]) / n, rec["P_no_horizontal"]); same((n - r["vwrap"]) / n, rec["P_no_vertical"])

    # mirror symmetry of the half-sheared square: x -> -x maps the periods (L,0), (L/2,L) to -w1, w2 - w1, so it exchanges
    # the twists (1,0) and (1,1) and sends class (a,b) to (-a-b, b); the law of the uniform orientation is unchanged
    mirror = []
    sheared = {(r["px"], r["py"]): r for r in by["F_scan"] if r["s"] and 2 * r["s"] == r["Lh"]}
    if (1, 0) in sheared and (1, 1) in sheared:
        r1, r2 = sheared[(1, 0)], sheared[(1, 1)]

        def norm(a, b):
            return (a, b) if a > 0 or (a == 0 and b > 0) else (-a, -b)

        def contr_sym(r):
            return moments([(r["contr"], 0.5), (r["cross"], 0.5), (r["samples"] - r["contr"] - r["cross"], 0.0)], r["samples"])

        pairs = [(consistent(r1), consistent(r2)), (contr_sym(r1), contr_sym(r2))]
        c1 = {tuple(map(int, k.split(","))): v for k, v in r1["classes"].items()}
        c2 = {tuple(map(int, k.split(","))): v for k, v in r2["classes"].items()}
        for (a, b), v in sorted(c1.items(), key=lambda kv: -kv[1])[:4]:
            w, n1, n2 = c2.get(norm(-a - b, b), 0), r1["samples"], r2["samples"]
            pairs.append(((v / n1, math.sqrt(v / n1 * (1 - v / n1) / n1)), (w / n2, math.sqrt(w / n2 * (1 - w / n2) / n2))))
        mirror = [abs(p - q) / math.hypot(sp, sq) for (p, sp), (q, sq) in pairs if sp or sq]
        assert max(mirror) <= 5, mirror

    # verdict
    verdict = "supported" if half_acc and tq_acc else ("refuted" if half_rej or tq_rej else "closed-null")
    assert verdict == result["verdict"]
    assert result["primary"] == {"half_bit_accepted": half_acc, "three_quarters_accepted": tq_acc}
    assert result["secondary"] == {"additivity_accepted": add_acc, "beta_nu_accepted": bn_acc}

    # power: the same rules decisively reject values shifted by 0.01 bit and by 0.005 in wrapping
    power = {"half bit 0.49/0.51": [abs(E_inf - t) / sig for t in (0.49, 0.51)],
             "wrapping 0.745/0.755": [abs(W_inf - t) / wsig for t in (0.745, 0.755)]}
    if frozen:
        assert min(min(v) for v in power.values()) > 5, power

    # independent replays on 16 x 16
    replay = {}
    small = {(r["px"], r["py"]): r for r in by["F_small"]}
    rec = small[(1, 0)]
    m = 20000 if frozen else 600
    p, q = replay_consistency(16, 16, 1, 0, m, "replay-consistency-16"), rec["cons"] / rec["samples"]
    assert abs(p - q) <= 5 * math.sqrt(q * (1 - q) * (1 / m + 1 / rec["samples"])), (p, q)
    replay["x-twisted consistent"] = (round(p, 4), round(q, 4))
    rec = small[(0, 0)]
    m = 10000 if frozen else 400
    (nh, c0), n = replay_untwisted(16, m, "replay-untwisted-16"), rec["samples"]
    for got, ref, name in ((nh, (n - rec["hwrap"]) / n, "untwisted no horizontal"), (c0, rec["contr"] / n, "untwisted contractible")):
        assert abs(got - ref) <= 5 * math.sqrt(ref * (1 - ref) * (1 / m + 1 / n)), (name, got, ref)
        replay[name] = (round(got, 4), round(ref, 4))
    rec = next(r for r in by["F_dir"] if r["L"] == 16)
    m = 2000 if frozen else 150
    (counts, disagree), n = replay_directed(16, m, "replay-directed-16"), rec["samples"]
    assert disagree == 0, disagree
    replay["directed vs undirected disagreements"] = disagree
    for bit, name in ((1, "H+"), (2, "H-"), (4, "V+"), (8, "V-"), (3, "H either")):
        got = sum(c for i, c in enumerate(counts) if i & bit) / m
        ref = sum(c for i, c in enumerate(rec["states"]) if i & bit) / n
        assert abs(got - ref) <= 5 * math.sqrt(max(ref * (1 - ref), 1e-4) * (1 / m + 1 / n)), (name, got, ref)
        replay["directed " + name] = (round(got, 4), round(ref, 4))
    d16 = directed_summary(rec["states"], n)["neither"]
    u16 = 1 - small[(0, 0)]["hwrap"] / small[(0, 0)]["samples"]
    assert abs(d16 - u16) <= 4 * math.sqrt(d16 * (1 - d16) / n + u16 * (1 - u16) / small[(0, 0)]["samples"]), (d16, u16)

    print(f"checked: {len(rows)} rows, verdict {verdict}; half bit E_inf {E_inf:.5f} +- {sig:.5f} ({(E_inf - 0.5) / sig:+.2f} sigma; "
          f"quadratic {E2:.5f} +- {sig2:.5f}); wrapping W_inf {W_inf:.5f} +- {wsig:.5f} ({(W_inf - 0.75) / wsig:+.2f} sigma; "
          f"quadratic {W2:.5f} +- {wsig2:.5f}); additivity D_inf {D_inf:+.5f} +- {dsig:.5f}, rectangle {rect[0]:+.5f} +- {rect[1]:.5f} "
          f"({'accepted' if add_acc else 'rejected'}); beta/nu x {x:.4f} +- {sx:.4f} ({'accepted' if bn_acc else 'rejected'}); "
          f"short-side x {xs_short:.4f}; rectangle identity max {max(abs(z) for z in extra):.2f} sigma; mirror pair max "
          f"{max(mirror, default=0):.2f} sigma; directed symmetries max "
          f"{max(sym):.2f} sigma; power {({k: [round(v, 1) for v in vs] for k, vs in power.items()})}; replay {replay}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:          # rehearsal output with a reduced roster
        raise SystemExit(main(Path(sys.argv[1]), frozen=False))
    raise SystemExit(main())
