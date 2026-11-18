"""CUMULANT-DIST-20261118-001B-E001: the frozen run.  python3 -B run.py --part <name>; python3 -B run.py --score."""
import argparse
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta"
sys.path.insert(0, str(HERE))
import cumlib as L  # noqa: E402


def trees(kmax_mixed=5, kmax_pure=6):
    """Every knot tree up to kmax_mixed knots under every assignment of parity/NAE to its knots, and pure trees to kmax_pure:
    delta for every pair against steps apart; the mixed identity kappa({x,y} + parity pendants) = (-1/3)^a."""
    rows = []
    for k in range(1, kmax_pure + 1):
        for knots, n in L.tree_shapes(k):
            sp = L.steps_apart(knots, n)
            assigns = itertools.product("PN", repeat=k) if k <= kmax_mixed else [("P",) * k, ("N",) * k]
            for laws in assigns:
                kn = list(zip(laws, knots))
                B = L.Base(L.states_from_knots(n, kn), n)
                bad, worst, idfail = 0, 0.0, 0
                for x, y in itertools.combinations(range(n), 2):
                    d = sp[x][y]
                    v, S, kap = B.delta(x, y, smax=d + 2)
                    if abs(v - d) > 1e-9:
                        bad += 1
                        worst = max(worst, abs(v - d))
                # the identity on one far pair: x, y at the two ends of a longest path
                rows.append({"k": k, "laws": "".join(laws), "n": n, "pairs": n * (n - 1) // 2, "mismatch": bad, "worst": worst})
    return rows


def mixed_identity(kmax=5):
    """For every mixed chain of k knots: kappa of {x, y} with the parity knots' pendants = (-1/3)^(number of NAE knots)."""
    out = []
    for k in range(1, kmax + 1):
        for laws in itertools.product("PN", repeat=k):
            knots, n = [], 1
            for i in range(k):
                knots.append((laws[i], (n - 1, n, n + 1)))
                n += 2
            B = L.Base(L.states_from_knots(n, knots), n)
            x, y = 0, n - 1
            pend = [kn[1][1] for kn in knots if kn[0] == "P"]
            S = tuple(sorted([x, y] + pend))
            kap = B.cumulant(S)
            a = laws.count("N")
            out.append({"laws": "".join(laws), "kappa": kap, "expected": (-1 / 3) ** a, "ok": abs(kap - (-1 / 3) ** a) < 1e-12})
    return out


def nae_separated(kmax=5):
    """On NAE chains: for 4-sets separated by a distinction, kappa_4 = -2 * 3^-(d1 + d2) with the separated pairing's steps."""
    out = []
    for k in range(3, kmax + 1):
        knots, n = [], 1
        for i in range(k):
            knots.append(("N", (n - 1, n, n + 1)))
            n += 2
        B = L.Base(L.states_from_knots(n, knots), n)
        sp = L.steps_apart([kk for _, kk in knots], n)
        pos = {v: (v + 1) // 2 for v in range(n)}           # knot index along the chain (shared distinctions at even v)
        bad = 0
        tested = 0
        for S in itertools.combinations(range(n), 4):
            a, b, c, d = sorted(S, key=lambda v: (v // 2, v))
            # separated pairing: the two lowest along the chain against the two highest, with a separating shared distinction
            sep = any(v % 2 == 0 and max(a, b) <= v <= min(c, d) for v in range(n))
            if not sep:
                continue
            tested += 1
            want = -2 * 3.0 ** (-(sp[a][b] + sp[c][d]))
            if abs(B.cumulant(S) - want) > 1e-12:
                bad += 1
        out.append({"k": k, "tested": tested, "mismatch": bad})
    return out


def linear(nbases=300, seed=7):
    """Random bases cut out by parity knots on 6 to 9 distinctions: delta (exact search) against the least circuit through the
    pair minus 2."""
    rng = random.Random(seed)
    rows = []
    for _ in range(nbases):
        n = rng.randint(6, 9)
        triples = list(itertools.combinations(range(n), 3))
        kn = [("P", t) for t in rng.sample(triples, rng.randint(2, 6))]
        B = L.Base(L.states_from_knots(n, kn), n)
        words = L.dual_codewords(kn, n)
        bad = 0
        for x, y in itertools.combinations(range(n), 2):
            c = L.min_circuit_through(words, x, y)
            v = B.delta(x, y)[0]
            if not ((c == math.inf and v == math.inf) or abs(v - (c - 2)) < 1e-9):
                bad += 1
        rows.append({"n": n, "knots": [list(k) for _, k in kn], "mismatch": bad})
    return rows


def rings(mmax=6):
    out = []
    for m in range(3, mmax + 1):
        for law in "PN":
            knots = []
            for i in range(m):
                knots.append((law, (2 * i, 2 * i + 1, (2 * i + 2) % (2 * m))))
            n = 2 * m
            B = L.Base(L.states_from_knots(n, knots), n)
            sp = L.steps_apart([k for _, k in knots], n)
            tab = {f"{x}-{y}": {"steps": sp[x][y], "delta": B.delta(x, y, smax=sp[x][y] + 2)[0], "tau": L.tau(B.correlation(x, y))}
                   for x, y in itertools.combinations(range(n), 2)}
            out.append({"m": m, "law": law, "N": B.N, "table": tab})
    return out


def chain_patch(W=4, H=4):
    """The chain grid (l = 1) on a W x H open patch, read on its grid distinctions through the reduced law (weight 1 when two
    neighbours agree, 2 when not): delta among grid distinctions (sets up to six) against tau."""
    n = W * H
    cells = [(i, j) for i in range(W) for j in range(H)]
    ix = {c: k for k, c in enumerate(cells)}
    links = [(ix[(i, j)], ix[(i + 1, j)]) for i in range(W - 1) for j in range(H)] + \
            [(ix[(i, j)], ix[(i, j + 1)]) for i in range(W) for j in range(H - 1)]
    states = np.arange(1 << n, dtype=np.int64)
    w = np.ones(len(states))
    for a, b in links:
        w *= np.where(((states >> a) & 1) == ((states >> b) & 1), 1.0, 2.0)
    B = L.Base(list(states), n, weights=w)
    rows = []
    for x, y in itertools.combinations(range(n), 2):
        t = L.tau(B.correlation(x, y))
        v, S, kap = B.delta(x, y, smax=6)
        rows.append({"x": cells[x], "y": cells[y], "L1": abs(cells[x][0] - cells[y][0]) + abs(cells[x][1] - cells[y][1]),
                     "tau": t, "delta": v, "argmin_size": len(S)})
    return rows


def bubble():
    """Sum over z of C(0, z)^2 on the endless chain grid (l = 1), from COUNT-BALLS's Kac-Ward code, z within 30."""
    sys.path.insert(0, str(ROOT / "experiments/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines"))
    import chain as CH
    t = 1 / 3
    R = CH.Resolvent(t)
    tot = 1.0
    for a in range(0, 31):
        for b in range(0, a + 1):
            if (a, b) == (0, 0) or a * a + b * b > 900:
                continue
            c = CH.corr_reweight(R, t, CH.path([(1, 0)] * a + [(0, 1)] * b))
            mult = len({(sx * u, sy * v) for u, v in {(a, b), (b, a)} for sx in (1, -1) for sy in (1, -1)})
            tot += mult * c * c
    return {"bubble": tot}


def weave_patch(R=2):
    """A patch of the six-regular weave (every distinction within R steps of the centre, NAE on every knot inside): delta
    (sets up to six) against tau for every pair."""
    sites = [(i, j) for i in range(-R, R + 1) for j in range(-R, R + 1) if max(abs(i), abs(j), abs(i + j)) <= R]
    ix = {p: k for k, p in enumerate(sites)}
    knots = []
    for (i, j) in sites:
        for tri in (((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i, j + 1), (i + 1, j + 1))):
            if all(p in ix for p in tri):
                knots.append(("N", tuple(ix[p] for p in tri)))
    n = len(sites)
    B = L.Base(L.states_from_knots(n, knots), n)
    rows = []
    for x, y in itertools.combinations(range(n), 2):
        t = L.tau(B.correlation(x, y))
        v, S, kap = B.delta(x, y, smax=6)
        a, b = sites[x], sites[y]
        rows.append({"x": a, "y": b, "steps": max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[0] - b[0] + a[1] - b[1])),
                     "tau": t, "delta": v, "argmin_size": len(S)})
    return {"n": n, "knots": len(knots), "N": B.N, "rows": rows}


def split_line(m=8):
    """The split line of m points (states: the cuts and the two all-equal states): |kappa_S| for |S| <= 4 against the switching
    rotation (i -> i + 1 mod m, the last point's values flipped), and delta for every pair (sets up to 6)."""
    full = (1 << m) - 1
    st = {0, full}
    for c in range(m - 1):
        cut = (1 << (c + 1)) - 1
        st |= {cut, full ^ cut}
    st = sorted(st)
    B = L.Base(st, m)
    rot = sorted({((s << 1) & full) | ((((s >> (m - 1)) & 1) ^ 1)) for s in st})
    same_set = rot == st
    asym = 0
    for r in range(1, 5):
        for S in itertools.combinations(range(m), r):
            S2 = tuple(sorted((v + 1) % m for v in S))
            if abs(abs(B.cumulant(S)) - abs(B.cumulant(S2))) > 1e-12:
                asym += 1
    deltas = {f"{x}-{y}": B.delta(x, y, smax=6)[0] for x, y in itertools.combinations(range(m), 2)}
    return {"m": m, "N": B.N, "rotation_maps_states": same_set, "asymmetric_cumulants": asym, "delta": deltas,
            "cap": 2 + math.log(2, 3), "max_delta": max(deltas.values())}


def split_grid_switching(W, H):
    """Switching equivalences of the W x H split grid: pairs (permutation, switch) mapping the state set to itself, with a
    corner fixed; does one take the corner's neighbour to the far corner?"""
    cells = [(i, j) for i in range(W) for j in range(H)]
    n = len(cells)
    full = (1 << n) - 1
    st = {0, full}
    for ax, size in ((0, W), (1, H)):
        for c in range(size - 1):
            m = sum(1 << k for k, p in enumerate(cells) if p[ax] <= c)
            st |= {m, full ^ m}
    st = sorted(st)

    def incidence(states, colour):
        G = nx.Graph()
        for v in range(n):
            G.add_node(("v", v), c=colour.get(v, "plain"))
        for i, s in enumerate(states):
            G.add_node(("s", i), c="state")
            for v in range(n):
                if (s >> v) & 1:
                    G.add_edge(("s", i), ("v", v))
        return G
    corner, nb, far = cells.index((0, 0)), cells.index((0, 1)), cells.index((W - 1, H - 1))
    G0 = incidence(st, {corner: "corner", nb: "target"})
    found = []
    for sigma in st:
        st2 = sorted(s ^ sigma for s in st)
        G1 = incidence(st2, {corner: "corner", far: "target"})
        if nx.is_isomorphic(G0, G1, node_match=lambda a, b: a["c"] == b["c"]):
            found.append(sigma)
    # every switching automorphism fixing the corner (as a count)
    return {"W": W, "H": H, "N": len(st), "neighbour_to_far_corner": len(found) > 0, "switches_that_do": len(found)}


PARTS = {"trees": trees, "mixed_identity": mixed_identity, "nae_separated": nae_separated, "linear": linear, "rings": rings,
         "chain_patch": chain_patch, "bubble": bubble, "weave_patch": weave_patch, "split_line": split_line,
         "split_grid": lambda: [split_grid_switching(3, 3), split_grid_switching(3, 4), split_grid_switching(4, 4)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    (ART / "parts").mkdir(parents=True, exist_ok=True)
    if a.part:
        t0 = time.time()
        res = PARTS[a.part]()
        json.dump({"part": a.part, "seconds": round(time.time() - t0, 1), "result": res}, open(ART / "parts" / f"{a.part}.json", "w"),
                  indent=1, default=str)
        print(a.part, "done", round(time.time() - t0, 1), flush=True)
    if a.score:
        import score
        score.main(ART)


if __name__ == "__main__":
    main()
