"""Referee R1 for DOUBLE-MEET-20261118-001: the finite triangle failures one size past (own code, on referee_double.py).

  ../../../.venv/bin/python -B referee_double_finite.py      (from this directory; writes referee_double_finite_failures.json)

Replays the 2,500 random discs of 12 knots and 2,500 of 13 knots drawn by `referee_double.py discs` (same seed, same order), and for
every disc with a triangle failure whose three distances are all finite lists the failure's long sides: the pair, b, steps apart, and
whether the two are lone, of opposite classes and facing each other both ways.
"""
import random, itertools, math, json, sys
from collections import Counter
from multiprocessing import Pool
import networkx as nx
import referee_double as R

def check(T):
    T = sorted(T)
    V = sorted({v for t in T for v in R.verts(t)}); ix = {v: k for k, v in enumerate(V)}; n = len(V)
    ts = [tuple(ix[v] for v in R.verts(t)) for t in T]
    D = R.bonds_matrix(n, R.states(n, ts))
    fin = [(x, y, z) for x, z in itertools.combinations(range(n), 2) for y in range(n)
           if y not in (x, z) and D[x][z] < math.inf and D[x][z] > D[x][y] + D[y][z]]
    if not fin:
        return None
    G = nx.Graph()
    for k, t in enumerate(ts):
        for v in t: G.add_edge(("k", k), ("d", v))
    sp = dict(nx.all_pairs_shortest_path_length(G))
    deg = Counter(v for t in T for v in R.verts(t))
    lone = {v: next(t for t in T if v in R.verts(t)) for v in V if deg[v] == 1}
    longs = {(x, z) for x, y, z in fin}
    rows = []
    for x, z in sorted(longs):
        a, c = V[x], V[z]
        isl = a in lone and c in lone
        rows.append({"pair": [a, c], "b": D[x][z], "steps": sp[("d", x)][("d", z)] // 2, "both_lone": isl,
                     "opposite_classes": isl and lone[a][0] != lone[c][0],
                     "facing_both_ways": isl and R.facing(a, lone[a], c) and R.facing(c, lone[c], a)})
    unb = sum(1 for a, b in itertools.combinations(range(n), 2) if D[a][b] == math.inf)
    return {"knots": T, "distinctions": n, "unbonded_pairs": unb, "violating_triples": len(fin), "long_sides": rows}

if __name__ == "__main__":
    rng = random.Random("referee-double-meet")
    d12 = [R.random_disc(12, rng) for _ in range(2500)]
    d13 = [R.random_disc(13, rng) for _ in range(2500)]
    with Pool(16) as P:
        r12 = P.map(check, d12, chunksize=16)
        r13 = P.map(check, d13, chunksize=16)
    out = {"12 knots": [r for r in r12 if r], "13 knots": [r for r in r13 if r]}
    json.dump(out, open("referee_double_finite_failures.json", "w"), indent=1, default=str)
    for k, v in out.items():
        for r in v:
            print(k, r["distinctions"], "unbonded", r["unbonded_pairs"], "violations", r["violating_triples"], r["long_sides"])
