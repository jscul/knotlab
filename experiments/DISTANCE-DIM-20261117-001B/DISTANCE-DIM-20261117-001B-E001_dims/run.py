"""Read-out for DISTANCE-DIM-20261117-001B-E001 (frozen before running).

Implication bases (states = up-sets): the chain of 12, grids 4 x 4, 6 x 6 and 3 x 7, the 5 x 5 grid with a
2 x 2 corner removed, the three-way grid 3 x 3 x 3, the standard example S_3 with a bottom and a top, and bare
S_3.  Readings: comparability from pair patterns and from betweenness; betweenness equal to the intervals;
order rebuilt up to reversal; the dimension-two test; a verified realizer of three where the test fails;
the order-only gap graph in d and in tau (exploratory).
Not-all-equal bases: the thread (n = 30), the weave W(L) (L = 6, 9, 12), the chain grid (L = 8, 10, 12) and a
binary knot tree (depth 4, control).  Readings: pair patterns, strict betweenness among plain distinctions,
the order-only gap graph in tau (degrees, level sizes from a start), and transfer gaps per row
log_3(lambda_0 / |lambda_1|) for the weave (widths 6, 9, 12) and the chain grid (widths 8, 10, 12).

    .venv/bin/python -B run.py      (writes artifacts/.../results.json)
"""

import itertools
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments", "DISTANCE-ORDER-20261117-001B", "DISTANCE-ORDER-20261117-001B-E001_order"))
import dimlib as L  # noqa: E402
import order as O  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "DISTANCE-DIM-20261117-001B", "DISTANCE-DIM-20261117-001B-E001_dims")
TOL = 1e-9


def tau_of(c):
    c = abs(c)
    return math.inf if c < 1e-300 else -math.log(c, 3)


# ---------- implication bases ----------

def implication_case(name, elems, leq):
    t = time.time()
    n = len(elems)
    U = L.upsets(elems, leq)
    D = L.table_from_states(n, U).tolist()
    P = {(u, v) for u in range(n) for v in range(n) if u != v and leq(elems[u], elems[v])}
    comp_true = {frozenset(p) for p in P}
    tr = L.strict_between(D)
    intervals = {(u, w, v) for u in range(n) for v in range(u + 1, n) for w in range(n)
                 if w not in (u, v) and (((u, w) in P and (w, v) in P) or ((v, w) in P and (w, u) in P))}
    comp_tr = L.comparability_from_between(n, tr)
    comp_pat = L.comparable_from_patterns(n, U)
    arcs = L.orient_from_between(n, comp_tr, tr) if comp_tr else None
    Pop = {(v, u) for u, v in P}
    res = {"name": name, "elements": n, "states": len(U),
           "between_equals_intervals": set(tr) == intervals, "between_triples": len(tr),
           "comparability_from_patterns_exact": comp_pat == comp_true,
           "comparability_from_between_exact": comp_tr == comp_true,
           "order_rebuilt_up_to_reversal": arcs is not None and (arcs == P or arcs == Pop),
           "dimension_at_most_two_from_states": L.dimension_at_most_two(n, comp_tr) if comp_tr else None}
    if res["dimension_at_most_two_from_states"] is False:
        res["realizer_of_three"] = realizer_three(name, elems, leq, P)
    # exploratory: the order-only gap graph in d and in tau, degrees
    N = len(U)
    Td = D
    Tt = [[0 if u == v else tau_of(1 - 2 * D[u][v] / N) for v in range(n)] for u in range(n)]
    res["gap_degrees_d"] = sorted({len(L.rng_gaps(Td, range(n), o)) for o in range(n)})
    res["gap_degrees_tau"] = sorted({len(L.rng_gaps(Tt, range(n), o)) for o in range(n)})
    res["seconds"] = round(time.time() - t, 1)
    return res


def realizer_three(name, elems, leq, P):
    n = len(elems)
    less = lambda u, v: (u, v) in P
    if name.startswith("three-way"):
        exts = []
        for k in range(3):
            key = lambda i: (elems[i][k],) + tuple(elems[i][m] for m in range(3) if m != k)
            exts.append(sorted(range(n), key=key))
        return {"kind": "coordinate", "verified": L.realizer_ok(n, less, exts)}
    exts = L.linear_extensions(n, less)
    for trio in itertools.combinations(exts, 3):
        if L.realizer_ok(n, less, list(trio)):
            return {"kind": "found among %d linear extensions" % len(exts), "verified": True}
    return {"kind": "none among %d linear extensions" % len(exts), "verified": False}


# ---------- not-all-equal bases ----------

def gaps_and_levels(T, n, starts, nbr_of):
    out = {}
    for name, o in starts.items():
        g = L.rng_gaps(T, range(n), o)
        out[name] = {"gap_degree": len(g)}
    return out


def full_gap_graph(T, n):
    return {o: L.rng_gaps(T, range(n), o) for o in range(n)}


def nae_thread(n):
    nn, knots = O.thread(n)
    N, d = O.disagreement_table(nn, knots)
    D = O.as_matrix(nn, d)
    T = [[0 if u == v else tau_of(1 - 2 * D[u][v] / N) for v in range(nn)] for u in range(nn)]
    G = full_gap_graph(T, nn)
    mid = nn // 2
    return {"name": f"thread n={n}", "N": str(N),
            "all_four_patterns": all(0 < D[u][v] < N for u, v in itertools.combinations(range(nn), 2)),
            "between_triples": len(O.between_triples(D, range(nn))),
            "gap_degrees": sorted({len(G[o]) for o in range(nn)}),
            "gap_degree_middle": len(G[mid]),
            "levels_from_middle": L.bfs_levels(nn, lambda u: G[u], mid)}


def weave_case(Lw):
    t = time.time()
    n = Lw * Lw
    if Lw <= 6:
        _, knots = O.weave_knots(Lw)
        N, d0 = O.disagreement_table(n, knots, [(0, v) for v in range(1, n)])
        d0 = {v: d0[(0, v)] for v in range(1, n)}
    else:
        N, d0 = O.weave_transfer_crt(Lw)
    d0[0] = 0
    tr = lambda u, v: ((v % Lw) - (u % Lw)) % Lw + Lw * (((v // Lw) - (u // Lw)) % Lw)
    tau0 = {v: (0 if v == 0 else tau_of(1 - 2 * d0[v] / N)) for v in range(n)}
    T = [[tau0[tr(u, v)] for v in range(n)] for u in range(n)]
    g0 = L.rng_gaps(T, range(n), 0)
    nbr = lambda u: [(u % Lw + (w % Lw)) % Lw + Lw * ((u // Lw + w // Lw) % Lw) for w in g0]
    return {"name": f"weave L={Lw}", "N": str(N), "gap_degree": len(g0),
            "gap_offsets": sorted(((w % Lw + Lw // 2) % Lw - Lw // 2, (w // Lw + Lw // 2) % Lw - Lw // 2) for w in g0),
            "levels_from_start": L.bfs_levels(n, nbr, 0), "seconds": round(time.time() - t, 1)}


def chain_grid_case(Lg):
    t = time.time()
    N, rates = L.chain_grid_rates(Lg)
    cg = lambda di, dj: 1 - 2 * rates[(di % Lg, dj % Lg)]          # grid-grid correlation by offset
    # distinctions: ('g', i, j), ('h', i, j) on (i,j)-(i+1,j), ('v', i, j) on (i,j)-(i,j+1)
    ends = lambda x: [(x[1], x[2])] if x[0] == "g" else ([(x[1], x[2]), (x[1] + 1, x[2])] if x[0] == "h" else [(x[1], x[2]), (x[1], x[2] + 1)])
    sign = lambda x: 1.0 if x[0] == "g" else -0.5      # E[s_p | grid] = -(s_u + s_v)/2
    def corr(x, y):
        if x == y:
            return 1.0
        s = 0.0
        for a in ends(x):
            for b in ends(y):
                s += cg(b[0] - a[0], b[1] - a[1])
        return sign(x) * sign(y) * s
    nodes = [(k, i, j) for k in "ghv" for j in range(Lg) for i in range(Lg)]
    n = len(nodes)
    C = np.array([[corr(x, y) for y in nodes] for x in nodes])
    T = [[0 if a == b else tau_of(C[a, b]) for b in range(n)] for a in range(n)]
    idx = {x: k for k, x in enumerate(nodes)}
    g_start, h_start = idx[("g", 0, 0)], idx[("h", 0, 0)]
    G = {}
    for o in range(n):
        G[o] = L.rng_gaps(T, range(n), o)
    # strict betweenness among plain distinctions: c_ac + c_cb - c_ab = 1 (d additive), within TOL
    near = 0
    grid_idx = [idx[("g", i, j)] for j in range(Lg) for i in range(Lg)]
    for a in (g_start, h_start, idx[("v", 0, 0)]):
        for b in range(n):
            if b == a:
                continue
            for c in range(n):
                if c in (a, b):
                    continue
                if abs(C[a, c] + C[c, b] - C[a, b] - 1) < TOL and C[a, c] < 1 - TOL and C[c, b] < 1 - TOL:
                    near += 1
    return {"name": f"chain grid L={Lg}",
            "all_four_patterns": bool(np.all(np.abs(C[np.triu_indices(n, 1)]) < 1 - TOL)),
            "between_triples_through_three_starts": near,
            "gap_degree_grid_start": len(G[g_start]), "gap_degree_private_start": len(G[h_start]),
            "gap_degrees": sorted({len(G[o]) for o in range(n)}),
            "grid_start_gaps": sorted(nodes[w] for w in G[g_start]),
            "levels_from_grid_start": L.bfs_levels(n, lambda u: G[u], g_start),
            "nearest_grid_correlation": cg(1, 0), "grid_private_correlation": corr(("g", 0, 0), ("h", 0, 0)),
            "seconds": round(time.time() - t, 1)}


def knot_tree(depth):
    """Binary tree of knots: every distinction above the last level starts one knot with two new
    distinctions; numbered depth-first so the frontier programme stays small."""
    knots = []
    counter = [1]
    def grow(x, level):
        if level == depth:
            return
        a, b = counter[0], counter[0] + 1
        counter[0] += 2
        knots.append(((x, a, b), O.NAE))
        grow(a, level + 1)
        grow(b, level + 1)
    grow(0, 0)
    n = counter[0]
    N, d = O.disagreement_table(n, knots)
    D = O.as_matrix(n, d)
    T = [[0 if u == v else tau_of(1 - 2 * D[u][v] / N) for v in range(n)] for u in range(n)]
    G = full_gap_graph(T, n)
    st = O.path_steps(n, knots)
    coknot = all(set(G[o]) == {v for v in range(n) if st[o][v] == 1} for o in range(n))
    return {"name": f"knot tree depth {depth}", "n": n, "gap_graph_is_coknot_graph": coknot,
            "levels_from_root": L.bfs_levels(n, lambda u: G[u], 0)}


def transfer_gap_weave(Lw):
    R = 1 << Lw
    bits = (np.arange(R)[:, None] >> np.arange(Lw)[None, :]) & 1
    okm = np.ones((R, R), dtype=bool)
    for i in range(Lw):
        a, a1 = bits[:, i][:, None], bits[:, (i + 1) % Lw][:, None]
        b, b1 = bits[:, i][None, :], bits[:, (i + 1) % Lw][None, :]
        okm &= ~((a == a1) & (a1 == b))
        okm &= ~((a1 == b) & (b == b1))
    ev = np.linalg.eigvals(okm.astype(np.float64))
    mags = np.sort(np.abs(ev))[::-1]
    top = int(np.sum(mags > mags[0] * (1 - 1e-9)))          # eigenvalues sharing the top modulus
    lam1 = mags[top]                                          # the largest modulus below the top
    return {"width": Lw, "lambda0": float(mags[0]), "top_modulus_multiplicity": top, "lambda1_abs": float(lam1),
            "gap_log3": float(math.log(mags[0] / lam1, 3))}


def transfer_gap_chain(Lg):
    R = 1 << Lg
    bits = (np.arange(R)[:, None] >> np.arange(Lg)[None, :]) & 1
    horiz = np.prod(np.where(bits != np.roll(bits, -1, axis=1), 2.0, 1.0), axis=1)
    vert = np.prod(np.where(bits[:, None, :] != bits[None, :, :], 2.0, 1.0), axis=2)
    S = np.sqrt(horiz)[:, None] * vert * np.sqrt(horiz)[None, :]      # same spectrum, symmetric
    ev = np.linalg.eigvalsh(S)
    mags = np.sort(np.abs(ev))[::-1]
    top = int(np.sum(mags > mags[0] * (1 - 1e-9)))
    lam1 = mags[top]
    return {"width": Lg, "lambda0": float(mags[0]), "top_modulus_multiplicity": top, "lambda1_abs": float(lam1),
            "gap_log3": float(math.log(mags[0] / lam1, 3))}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    imp = [("chain 12", *L.grid_poset(12)), ("grid 4x4", *L.grid_poset(4, 4)), ("grid 6x6", *L.grid_poset(6, 6)),
           ("grid 3x7", *L.grid_poset(3, 7)), ("grid 5x5 less a 2x2 corner", *L.young(5, 5, 2, 2)),
           ("three-way grid 3x3x3", *L.grid_poset(3, 3, 3)), ("crown S_3 with bottom and top", *L.with_bottom_top(*L.crown(3))),
           ("bare crown S_3", *L.crown(3))]
    res["implication"] = [implication_case(*c) for c in imp]
    res["nae_thread"] = nae_thread(30)
    res["nae_weave"] = [weave_case(Lw) for Lw in (6, 9, 12)]
    res["nae_chain_grid"] = [chain_grid_case(Lg) for Lg in (8, 10, 12)]
    res["knot_tree"] = knot_tree(4)
    res["transfer_gap_weave"] = [transfer_gap_weave(Lw) for Lw in (6, 9, 12)]
    res["transfer_gap_chain_grid"] = [transfer_gap_chain(Lg) for Lg in (8, 10, 12)]
    res["onsager_slope"] = 1 - math.log(2, 3)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), res["started"], res["finished"])


if __name__ == "__main__":
    main()
