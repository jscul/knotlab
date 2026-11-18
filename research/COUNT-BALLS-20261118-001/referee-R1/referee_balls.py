"""Referee R1 for COUNT-BALLS-20261118-001 (own code; the study's weave.py, chain.py, census.py are not imported).

  ../../../.venv/bin/python -B referee_balls.py > referee_balls.json      (from this directory)

1. The weave's short-range correlations from the referee's own NAE strip transfer (WEAVE-MIX-R1's row_product) on cylinders of
   width 9 and 12, along the transfer (a lattice line) at r = 1, 2, 3: against the study's exact row value at r = 2 (c2_row) and the
   exact -1/3 at r = 1.
2. Stephenson's amplitude from its closed form, and the chain grid's l = 1 rate ratio and the axis rate from the closed form.
3. The chain grid's reduction (S5), literally: a 3 x 3 grid with one NAE knot (and its loose distinction) on every edge,
   enumerated, against the Ising model at t = -1/3 on the grid.
4. The census's first merge at n = 7, rebuilt from the splits printed in the note: the two bases' sorted count rows, k and lambda.

  ../../../.venv/bin/python -B referee_balls.py golab > referee_golab.json
  ../../../.venv/bin/python -B referee_balls.py golab_fine > referee_golab_fine.json     (the polygon at 4,000 and 16,000 points)
  ../../../.venv/bin/python -B referee_balls.py small > referee_small.json

6. Small statements, from split bases written out: S2's ladder (2 x 10) against comb (line of 10 with a pendant on each inner
   distinction), the number of distinctions at each count from every middle start, with k and lambda; S4's star with three tips on
   four distinctions against its translate by one tip's state: the multisets of the states' sorted Hamming rows, and k.

5. Goląb's pi of the chain grids' outlines from the closed form, written from scratch: the decay rate in direction x is the
   support function m(x) = max{q . x : cosh q1 + cosh q2 = A}, A = (1 + t^2)^2 / (2t(1 - t^2)), t = 3^-l; the outline is m's unit
   ball, and Goląb's pi is half its perimeter measured in m itself (a polygon of 4,000 points).  Gates: the circle (pi), the
   taxicab diamond (4) and the regular hexagon (3) through the same perimeter routine.
"""
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/WEAVE-MIX-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))


def weave_corr():
    import referee_weavemix as W
    out = {}
    arr = {(i, 0, t): 0 for i in range(1) for t in "UD"}                  # plain NAE on every knot
    for w in (9, 12):
        M = W.row_product(w, arr)
        ev, Rv = np.linalg.eig(M)
        evL, Lv = np.linalg.eig(M.T)
        i0, j0 = int(np.argmax(np.abs(ev))), int(np.argmax(np.abs(evL)))
        lam = ev[i0].real
        r = np.abs(Rv[:, i0].real)
        l = np.abs(Lv[:, j0].real)
        S = 2.0 * ((np.arange(1 << w)[:, None] >> np.arange(w)[None, :]) & 1) - 1.0
        v = S[:, 0] * r
        seq = []
        for k in range(1, 4):
            v = M @ v / lam
            seq.append(float((l * S[:, 0]) @ v / (l @ r)))
        out[w] = seq
        print("weave", w, seq, file=sys.stderr, flush=True)
    return out


def closed_forms():
    import mpmath as mp
    mp.mp.dps = 30
    E0 = mp.mpf(2) ** (mp.mpf(1) / 12) * mp.e ** (3 * mp.zeta(-1, derivative=1))
    a = 2 * mp.mpf(3) ** (-mp.mpf(1) / 4) * E0 ** 2
    t = 1 / 3
    A = (1 + t * t) ** 2 / (2 * t * (1 - t * t))
    ax = math.acosh(A - 1)
    dg = 2 * math.acosh(A / 2) / math.sqrt(2)
    K = math.atanh(t)
    Ks = math.atanh(math.exp(-2 * K))
    return {"stephenson_a_closed_form": str(a), "A_l1": A, "axis_rate_l1": ax, "two_Kstar_minus_K": 2 * (Ks - K),
            "diagonal_rate_l1": dg, "diagonal_over_axis_l1": dg / ax}


def chain_grid_literal(L=3):
    """3 x 3 grid distinctions g(i, j); on every edge (u, v) one loose distinction x with NAE(u, x, v).  Enumerate the allowed states,
    and the correlation of grid spins, against the Ising model at t = -1/3 on the same grid (open boundary)."""
    pts = [(i, j) for i in range(L) for j in range(L)]
    idx = {p: k for k, p in enumerate(pts)}
    edges = [(idx[(i, j)], idx[(i + 1, j)]) for i in range(L - 1) for j in range(L)] + \
            [(idx[(i, j)], idx[(i, j + 1)]) for i in range(L) for j in range(L - 1)]
    ng = len(pts)
    # summing each loose distinction exactly: weight 1 if u = v (x forced), 2 if u != v (x free) -- enumerate the loose bits too
    corr_lit = {}
    Z = 0
    acc = np.zeros((ng, ng))
    for g in range(1 << ng):
        w = 1
        for u, v in edges:
            gu, gv = (g >> u) & 1, (g >> v) & 1
            cnt = sum(1 for x in (0, 1) if not (gu == x == gv))          # NAE(u, x, v): not all equal
            w *= cnt
        if w == 0:
            continue
        s = np.array([1 if (g >> k) & 1 else -1 for k in range(ng)])
        Z += w
        acc += w * np.outer(s, s)
    lit = acc / Z
    # Ising at tanh K = -1/3: weight exp(K s_u s_v)
    K = math.atanh(-1 / 3)
    Zi = 0
    acci = np.zeros((ng, ng))
    for g in range(1 << ng):
        s = np.array([1 if (g >> k) & 1 else -1 for k in range(ng)])
        w = math.exp(K * sum(s[u] * s[v] for u, v in edges))
        Zi += w
        acci += w * np.outer(s, s)
    ising = acci / Zi
    return {"grid": L, "max_difference_literal_vs_ising": float(np.max(np.abs(lit - ising))),
            "corner_to_corner_literal": float(lit[0, ng - 1]), "corner_to_corner_ising": float(ising[0, ng - 1])}


def census_merge():
    import referee_cap as KC
    names = "abcdefg"
    def split(s):
        a, b = s.split("|")
        return sum(1 << names.index(c) for c in a)
    A = ["ce|abdfg", "bce|adfg", "bcde|afg", "af|bcdeg", "abcdf|eg", "bcef|adg"]
    B = ["ad|bcefg", "abd|cefg", "ce|abdfg", "bcde|afg", "abdf|ceg", "abcdf|eg"]
    out = {}
    for name, sp in (("first (k = lambda = 3 claimed)", A), ("second (k = lambda = 2 claimed)", B)):
        full = (1 << 7) - 1
        S = sorted({0, full} | {split(s) for s in sp} | {full ^ split(s) for s in sp})
        D = [[sum(((s >> u) ^ (s >> v)) & 1 for s in S) for v in range(7)] for u in range(7)]
        rows = sorted(tuple(sorted(D[u][v] for v in range(7) if v != u)) for u in range(7))
        m = KC.measure(S, 7)
        out[name] = {"states": len(S), "k": m["k"], "lambda": m["lam"], "sorted_rows": rows}
    out["same_multiset_of_sorted_rows"] = out["first (k = lambda = 3 claimed)"]["sorted_rows"] == out["second (k = lambda = 2 claimed)"]["sorted_rows"]
    return out


def golab_from_norm(norm, N=4000):
    th = np.linspace(0, 2 * math.pi, N, endpoint=False)
    pts = np.array([[math.cos(x) / norm(math.cos(x), math.sin(x)), math.sin(x) / norm(math.cos(x), math.sin(x))] for x in th])
    seg = np.roll(pts, -1, axis=0) - pts
    return float(sum(norm(d[0], d[1]) for d in seg) / 2)


def chain_rate(A):
    from scipy.optimize import minimize_scalar
    q1max = math.acosh(A - 1)
    def m(c, s):
        def neg(q1):
            return -(q1 * c + math.acosh(max(1.0, A - math.cosh(q1))) * abs(s))
        r = minimize_scalar(neg, bounds=(-q1max, q1max), method="bounded", options={"xatol": 1e-13})
        return -r.fun
    return m


def golab():
    hexn = lambda x, y: max(abs(x * math.cos(k * math.pi / 3) + y * math.sin(k * math.pi / 3)) for k in range(3)) * 2 / math.sqrt(3)
    gates = {"circle": golab_from_norm(lambda x, y: math.hypot(x, y)), "taxicab": golab_from_norm(lambda x, y: abs(x) + abs(y)),
             "hexagon": golab_from_norm(hexn)}
    out = {}
    for l in (1, 2, 3, 4, 6):
        t = 3.0 ** (-l)
        A = (1 + t * t) ** 2 / (2 * t * (1 - t * t))
        out[f"l={l}"] = round(golab_from_norm(chain_rate(A)), 6)
        print("golab", l, out[f"l={l}"], file=sys.stderr, flush=True)
    return {"gates": gates, "golab_pi": out}


def split_states(n, splits):
    full = (1 << n) - 1
    st = {0, full}
    for A in splits:
        m = sum(1 << u for u in A)
        st |= {m, full ^ m}
    return sorted(st)


def small():
    import referee_cap as KC
    pc = lambda x: bin(x).count("1")
    def layers(S, n, u):
        out = {}
        for v in range(n):
            if v != u:
                c = sum(((s >> u) ^ (s >> v)) & 1 for s in S)
                out[c] = out.get(c, 0) + 1
        return dict(sorted(out.items()))
    m = 10
    lad = [(r, i) for r in range(2) for i in range(m)]
    li = {p: k for k, p in enumerate(lad)}
    lad_splits = [[li[(r, i)] for r in range(2) for i in range(c + 1)] for c in range(m - 1)] + [[li[(0, i)] for i in range(m)]]
    L = split_states(2 * m, lad_splits)
    # comb: line 0..m-1, pendant m-1+i on inner i = 1..m-2; splits = the tree's edges
    import networkx as nx
    T = nx.path_graph(m)
    for i in range(1, m - 1):
        T.add_edge(i, m - 1 + i)
    nc = T.number_of_nodes()
    comb_splits = []
    for u, v in list(T.edges()):
        T.remove_edge(u, v)
        comb_splits.append(sorted(nx.node_connected_component(T, u)))
        T.add_edge(u, v)
    C = split_states(nc, comb_splits)
    mid = range(2, m - 2)
    out = {"ladder": {"n": 2 * m, "measure": KC.measure(L, 2 * m), "layers_from_middle": {i: layers(L, 2 * m, li[(0, i)]) for i in mid}},
           "comb": {"n": nc, "measure": KC.measure(C, nc), "layers_from_middle": {i: layers(C, nc, i) for i in mid},
                    "layers_from_the_pendant_of_a_middle": {i: layers(C, nc, m - 1 + i) for i in mid}},
           "ladder_and_comb_profiles_equal": sorted(tuple(sorted(layers(L, 2 * m, u).items())) for u in range(2 * m)) ==
                                             sorted(tuple(sorted(layers(C, nc, u).items())) for u in range(nc))}
    star = split_states(4, [[0], [1], [2]])                              # centre d = 3, tips a, b, c
    x = 1                                                                # tip a's state
    tr = sorted(s ^ x for s in star)
    prof = lambda S: sorted(tuple(sorted(pc(a ^ b) for b in S if b != a)) for a in S)
    out["star_and_translate"] = {"star_k": KC.measure(star, 4)["k"], "translate_k": KC.measure(tr, 4)["k"],
                                 "translate_states": tr, "same_state_profile": prof(star) == prof(tr)}
    return out


def golab_fine():
    out = {}
    for l in (3, 4, 6, 8, 12):
        t = 3.0 ** (-l)
        A = (1 + t * t) ** 2 / (2 * t * (1 - t * t))
        out[f"l={l}"] = {str(N): round(golab_from_norm(chain_rate(A), N), 7) for N in (4000, 16000)}
    return {"golab_pi_by_polygon_size": out}


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "small":
    print(json.dumps(small(), indent=1, default=str))
elif __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "golab_fine":
    print(json.dumps(golab_fine(), indent=1))
elif __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "golab":
    print(json.dumps(golab(), indent=1))
elif __name__ == "__main__":
    res = {"1_weave_short_range": weave_corr(), "2_closed_forms": closed_forms(), "3_chain_grid_literal": chain_grid_literal(),
           "4_census_first_merge": census_merge()}
    print(json.dumps(res, indent=1, default=str))
