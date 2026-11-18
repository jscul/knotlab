"""Referee R1 for ROW-ARRANGE-20261118-001 (own code; the study's readings.py, families.py, job.py and merge.py are not used for any
result; `check_canon` imports the study's canon_view only to test it).

  ../../../.venv/bin/python -B referee_rows.py census <pop> <n> [workers]    > referee_rows_<pop>_<n>.json
  ../../../.venv/bin/python -B referee_rows.py families <n> <parents> <seed> [workers] > referee_rows_families_<n>_<parents>.json
  ../../../.venv/bin/python -B referee_rows.py proofs                        > referee_rows_proofs.json
  ../../../.venv/bin/python -B referee_rows.py check_canon <n>               > referee_rows_canon_<n>.json
  ../../../.venv/bin/python -B referee_rows.py pairs                         > referee_rows_pairs.json

Populations from the referee's COUNT-BALLS-R1 census engine (`referee_census`: CUBE-DOUBLING-R1's closure of one to three
betweenness knots, A99 admission, its own canonical form): one-split (at most two new states per step) at n = 7, 8 and the cheapest
growth to 12.  Families: `parents` random classes of the one-split population at n - 1 (the referee's own seed), every one-split
child of each, classes by the canonical form of the count table (which determines these bases, DISTANCE-ORDER-20261117-001,
statement 1).

Readings of the count table D (D[u][v] = states in which u and v differ), each a multiset over starts x, from the note's words:
  a     the sorted row;   N1  the row with the rows at the least count from x;
  W2    two rounds of colour refinement on the complete count-weighted table from equal colours (round one is the row);
  WL    refinement run n rounds (to rest);   BW4  refinement started from each start's view within count 4;
  B_r   the table on the distinctions within count r of x, x marked, up to renaming, r = 2, 4, ..., 14.
Colour names are shared across a population (one dictionary per round).  Views and tables are put in canonical form by the
referee's own routine: invariant refinement inside the view, then every order of the remaining cells (brute force), branching on
the first cell when the brute force would be too large; the certificate is the least relabelled table.  k is the exact least number
of colours of the crossing graph, lambda Eppstein's (KNOT-CAP-R1 `measure`).
"""
import hashlib
import itertools
import json
import math
import random
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/COUNT-BALLS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/CUBE-DOUBLING-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
import referee_census as RCN  # noqa: E402
import referee_cube as RC  # noqa: E402
import referee_cap as KC  # noqa: E402

RADII = [2, 4, 6, 8, 10, 12, 14]
LIMIT = 4000


def h(x):
    return hashlib.blake2b(repr(x).encode(), digest_size=12).hexdigest()


# ---------------- canonical form of a small weighted table ----------------

def refine(M, key):
    m = len(M)
    while True:
        new = [h((key[v], tuple(sorted((M[v][u], key[u]) for u in range(m) if u != v)))) for v in range(m)]
        if len(set(new)) == len(set(key)):
            return new
        key = new


def canon(M, marked=True):
    """The least relabelled table of M over every order compatible with the invariant refinement (node 0 fixed first if marked)."""
    m = len(M)
    A = np.array(M, dtype=np.int64)
    iu = np.triu_indices(m, 1)
    best = [None]

    def leafs(key):
        key = refine(M, key)
        cells = defaultdict(list)
        for v in range(m):
            cells[key[v]].append(v)
        names = sorted(cells)
        size = math.prod(math.factorial(len(cells[c])) for c in names)
        if size <= LIMIT:
            for combo in itertools.product(*[itertools.permutations(cells[c]) for c in names]):
                o = [v for part in combo for v in part]
                cand = (o.index(0) if marked else -1, tuple(A[np.ix_(o, o)][iu].tolist()))     # where the mark sits
                if best[0] is None or cand < best[0]:
                    best[0] = cand
            return
        c = next(c for c in names if len(cells[c]) > 1)
        for v in cells[c]:
            k2 = list(key)
            k2[v] = h(("ind", key[v]))
            leafs(k2)

    leafs(["x"] + [""] * (m - 1) if marked else [""] * m)
    return best[0]


# ---------------- populations ----------------

def population(pop, nmax):
    import os
    cache = os.environ.get("REFEREE_POP_CACHE")
    if cache:
        f = Path(cache) / f"pop_{pop}_{nmax}.json"
        if f.exists():
            return {int(k): v for k, v in json.load(open(f)).items()}
    out = _population(pop, nmax)
    if cache:
        json.dump(out, open(f, "w"))
    return out


def _population(pop, nmax):
    st = sorted(S for S in range(8) if RC.allowed(S, 3, [(0, 1, 2)]))
    n = 3
    level = {RCN.canon(st, n): st}
    out = {3: list(level.values())}
    while n < nmax:
        nxt = {}
        for S in level.values():
            for e in children(S, n, pop):
                kk = RCN.canon(e, n + 1)
                if kk not in nxt:
                    nxt[kk] = e
        level = nxt
        n += 1
        out[n] = list(level.values())
        print("population", pop, n, len(level), file=sys.stderr, flush=True)
    return out


def children(S, n, pop="one-split"):
    ext, O, Z, full = RC.closure(S, n)
    N = len(S)
    adm = [(a0, a1) for a0, a1 in ext if RC.admitted(a0, a1, O, Z, full, N)]
    if not adm:
        return []
    if pop == "cheap":
        low = min(RC.pc(a0) + RC.pc(a1) for a0, a1 in adm)
        keep = [x for x in adm if RC.pc(x[0]) + RC.pc(x[1]) == low]
    else:
        keep = [x for x in adm if RC.pc(x[0]) + RC.pc(x[1]) <= N + 2]
    return [list(e) for e in sorted({tuple(RC.apply(S, n, a0, a1)) for a0, a1 in keep})]


# ---------------- per-base readings ----------------

def table(S, n):
    O, Z, full = RC.cols(S, n)
    return [[RC.pc(Z[u] & O[v]) + RC.pc(O[u] & Z[v]) for v in range(n)] for u in range(n)]


def view(D, x, r):
    ball = [x] + [y for y in range(len(D)) if y != x and D[x][y] <= r]
    return canon([[D[u][v] for v in ball] for u in ball])


def per_base(args):
    S, n = args
    D = table(S, n)
    rows = [tuple(sorted(D[x][y] for y in range(n) if y != x)) for x in range(n)]
    a = tuple(sorted(rows))
    N1 = []
    for x in range(n):
        m = min(D[x][y] for y in range(n) if y != x)
        N1.append((rows[x], tuple(sorted(rows[y] for y in range(n) if y != x and D[x][y] == m))))
    out = {"D": D, "N": len(S), "k": RCN.chromatic(RC.splits_of(S, n), (1 << n) - 1), "lam": KC.measure(S, n)["lam"],
           "a": h(a), "N1": h(tuple(sorted(N1))), "rows_distinct": len(set(rows)) == n}
    cache = {}
    for r in RADII:
        vs = []
        for x in range(n):
            ball = tuple([x] + [y for y in range(n) if y != x and D[x][y] <= r])
            if ball not in cache:
                cache[ball] = h(canon([[D[u][v] for v in ball] for u in ball]))
            vs.append(cache[ball])
        out[f"v{r}"] = vs
        out[f"B{r}"] = h(tuple(sorted(vs)))
    return out


def refinement(infos, rounds, start_key=None):
    """Colour refinement on every base of a population with shared colour names; the multiset after each round."""
    cols = [[0] * len(I["D"]) if start_key is None else list(I[start_key]) for I in infos]
    hist = []
    for _ in range(rounds):
        names = {}
        new = []
        for I, c in zip(infos, cols):
            D = I["D"]
            n = len(D)
            sig = [(c[x], tuple(sorted((D[x][y], c[y]) for y in range(n) if y != x))) for x in range(n)]
            new.append([names.setdefault(s, len(names)) for s in sig])
        cols = new
        hist.append([tuple(sorted(c)) for c in cols])
    return hist


def assess(infos, name):
    groups = defaultdict(list)
    for I in infos:
        groups[I[name]].append(I)
    multi = [g for g in groups.values() if len(g) > 1]
    return {"groups": len(groups), "multi": len(multi), "mix_k": sum(len({x["k"] for x in g}) > 1 for g in multi),
            "mix_lam": sum(len({x["lam"] for x in g}) > 1 for g in multi), "mix_N": sum(len({x["N"] for x in g}) > 1 for g in multi)}


def read_population(bases, n, workers):
    with Pool(workers) as P:
        infos = P.map(per_base, [(S, n) for S in bases], chunksize=64)
    h2 = refinement(infos, max(2, n))
    for I, w2, wl in zip(infos, h2[1], h2[-1]):
        I["W2"], I["WL"] = w2, wl
    hb = refinement(infos, max(2, n), start_key="v4")
    for I, b in zip(infos, hb[-1]):
        I["BW4"] = b
    out = {"classes": len(infos), "rows_distinct": sum(I["rows_distinct"] for I in infos)}
    for name in ["a", "N1", "W2", "WL", "BW4"] + [f"B{r}" for r in RADII]:
        out[name] = assess(infos, name)
    out["least_local_radius_determining_k"] = next((r for r in RADII if out[f"B{r}"]["mix_k"] == 0), None)
    return out, infos


def census(pop, n, workers):
    P = population(pop, n)
    res = {}
    for m in (range(4, n + 1) if pop == "cheap" else [n - 1, n] if n >= 8 else [n]):
        r, _ = read_population(P[m], m, workers)
        res[m] = r
        print("read", pop, m, json.dumps({k: (v["groups"], v["mix_k"]) if isinstance(v, dict) else v for k, v in r.items()}),
              file=sys.stderr, flush=True)
    return {"population": pop, "levels": res}


def table_class(args):
    S, n = args
    return h(canon(table(S, n), marked=False))


def families(n, parents, seed, workers):
    P = population("one-split", n - 1)
    pool = P[n - 1]
    rng = random.Random(f"referee-families-{n}-{seed}")
    pick = rng.sample(range(len(pool)), parents)
    raw = []
    for p in pick:
        raw.extend(children(pool[p], n - 1))
    with Pool(workers) as Q:
        keys = Q.map(table_class, [(S, n) for S in raw], chunksize=64)
    seen = {}
    for S, k in zip(raw, keys):
        seen.setdefault(k, S)
    print("families", n, parents, "children", len(raw), "classes", len(seen), file=sys.stderr, flush=True)
    bases = list(seen.values())
    r, infos = read_population(bases, n, workers)
    ex = {}
    for name in ("N1", "W2", "WL"):
        groups = defaultdict(list)
        for S, I in zip(bases, infos):
            groups[I[name]].append((S, I))
        ex[name] = [[{"splits": RCN.names(RC.splits_of(S, n), n), "k": I["k"], "lam": I["lam"], "N": I["N"]} for S, I in g]
                    for g in groups.values() if len({I["k"] for _, I in g}) > 1][:5]
    return {"n": n, "parents": parents, "parents_of": len(pool), "seed": seed, "children": len(raw), "classes": len(seen),
            "readings": r, "groups_mixing_k": ex}


# ---------------- the proofs' families ----------------

def partial_cube_base(G):
    import networkx as nx
    nodes = sorted(G.nodes(), key=repr)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    full = (1 << n) - 1
    st = {0, full}
    for a, b in G.edges():
        m = sum(1 << idx[x] for x in nodes if dist[x][a] < dist[x][b])
        st |= {m, full ^ m}
    return sorted(st), n, nodes, dist, idx


def betweenness_solutions(G):
    S, n, nodes, dist, idx = partial_cube_base(G)
    tr = [(idx[x], idx[y], idx[z]) for x, z in itertools.combinations(nodes, 2) for y in nodes
          if y not in (x, z) and dist[x][y] + dist[y][z] == dist[x][z]]
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(len(s), dtype=bool)
    for a, b, c in tr:
        x, y, z = (s >> a) & 1, (s >> b) & 1, (s >> c) & 1
        ok &= ~((x == z) & (x != y))
    return sorted(int(v) for v in s[ok]) == S


def ringpair(a, b):
    import networkx as nx
    G = nx.cycle_graph(2 * a)
    for i in range(1, 2 * b):
        G.add_edge(("b", i), ("b", i + 1) if i + 1 < 2 * b else 0)
    G.add_edge(0, ("b", 1))
    return G


def simplex(H):
    import networkx as nx
    G = nx.Graph()
    for v in H.nodes():
        G.add_edge((), (v,))
    for u, v in H.edges():
        e = tuple(sorted((u, v)))
        G.add_edge((u,), e)
        G.add_edge((v,), e)
    return G


def read_graph(G, radii):
    S, n, *_ = partial_cube_base(G)
    I = per_base((S, n))
    return S, n, I


def proofs():
    import networkx as nx
    out = {"R1_betweenness_solution_set_is_the_halfspaces": {
        "F(2,4)": betweenness_solutions(ringpair(2, 4)), "F(3,3)": betweenness_solutions(ringpair(3, 3)),
        "kappa(C6)": betweenness_solutions(simplex(nx.cycle_graph(6))), "kappa(P5)": betweenness_solutions(simplex(nx.path_graph(5)))}}
    print("R1", out, file=sys.stderr, flush=True)
    pairs = {"R2 r=2: F(2,6) v F(4,4)": ((2, 6), (4, 4)), "R2 r=2: F(2,4) v F(3,3)": ((2, 4), (3, 3)),
             "R2 r=4: F(4,12) v F(8,8)": ((4, 12), (8, 8)), "R2 r=4: F(4,8) v F(6,6)": ((4, 8), (6, 6)),
             "below the condition, r=4: F(3,9) v F(6,6)": ((3, 9), (6, 6)), "below, r=4: F(3,5) v F(4,4)": ((3, 5), (4, 4)),
             "below, r=6: F(5,7) v F(6,6)": ((5, 7), (6, 6)), "R2 r=6: F(6,10) v F(8,8)": ((6, 10), (8, 8))}
    out["R2"] = {}
    for name, (p, q) in pairs.items():
        res = {}
        Is = []
        for ab in (p, q):
            S, n, I = read_graph(ringpair(*ab), RADII)
            Is.append(I)
            res[f"F{ab}"] = {"n": n, "N": len(S), "k": I["k"], "lam": I["lam"]}
        res["equal_views"] = {f"B{r}": Is[0][f"B{r}"] == Is[1][f"B{r}"] for r in RADII}
        res["equal_a"] = Is[0]["a"] == Is[1]["a"]
        out["R2"][name] = res
        print("R2", name, json.dumps(res), file=sys.stderr, flush=True)
    Is = []
    res = {}
    for name, H in (("kappa(C10)", nx.cycle_graph(10)), ("kappa(C5+C5)", nx.disjoint_union(nx.cycle_graph(5), nx.cycle_graph(5)))):
        S, n, I = read_graph(simplex(H), RADII)
        Is.append(I)
        res[name] = {"n": n, "N": len(S), "k": I["k"], "lam": I["lam"]}
    h2 = refinement(Is, 21)
    res["equal"] = {"a": Is[0]["a"] == Is[1]["a"], "N1": Is[0]["N1"] == Is[1]["N1"], "W2": h2[1][0] == h2[1][1],
                    "WL (21 rounds)": h2[-1][0] == h2[-1][1], **{f"B{r}": Is[0][f"B{r}"] == Is[1][f"B{r}"] for r in RADII}}
    out["R3"] = res
    print("R3", json.dumps(res), file=sys.stderr, flush=True)
    return out


def check_canon(n):
    """The study's canon_view against the referee's canonical form on every view of every one-split class at n: the two must give
    the same partition of the views (each of the study's classes one of the referee's, and back)."""
    sys.path.insert(0, str(ROOT / "experiments/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings"))
    import readings as STUDY  # noqa: E402  (tested, not used for results)
    P = population("one-split", n)[n]
    pairs = {}
    relab = [0, 0]
    rng = random.Random(7)
    for S in P:
        D = table(S, n)
        for r in RADII:
            for x in range(n):
                ball = [x] + [y for y in range(n) if y != x and D[x][y] <= r]
                M = [[D[u][v] for v in ball] for u in ball]
                rest = ball[1:]
                rng.shuffle(rest)                          # a random relabelling of the same view, x kept first
                M2 = [[D[u][v] for v in [x] + rest] for u in [x] + rest]
                s1, s2 = STUDY.canon_view(M), STUDY.canon_view(M2)
                pairs[(h(canon(M)), s1)] = 1
                pairs[(h(canon(M2)), s2)] = 1
                relab[0] += 1
                relab[1] += s1 != s2
    mine, theirs = defaultdict(set), defaultdict(set)
    for a, b in pairs:
        mine[a].add(b)
        theirs[b].add(a)
    return {"n": n, "relabelled_pairs": relab[0], "study_name_changed_by_relabelling": relab[1],
            "views_classes_referee": len(mine), "views_classes_study": len(theirs),
            "referee_classes_split_by_the_study": sum(len(v) > 1 for v in mine.values()),
            "study_classes_merging_referee_classes": sum(len(v) > 1 for v in theirs.values())}


def from_splits(names):
    letters = "abcdefghij"
    n = 1 + max(letters.index(c) for nm in names for c in nm if c != "|")
    full = (1 << n) - 1
    st = {0, full}
    for nm in names:
        m = sum(1 << letters.index(c) for c in nm.split("|")[0])
        st |= {m, full ^ m}
    return sorted(st), n


def pairs():
    """The note's failing pairs (post hoc), rebuilt from the splits it prints: which readings agree, k, lambda, N."""
    P = {"N1 at eight": (["ce|abdfgh", "adf|bcegh", "ag|bcdefh", "bceg|adfh", "afg|bcdeh", "abcdfg|eh"],
                         ["ad|bcefgh", "bce|adfgh", "af|bcdegh", "cef|abdgh", "adfg|bceh", "abcdfg|eh"]),
         "B6 at seven": (["a|bcdefg", "e|abcdfg", "ce|abdfg", "bce|adfg", "bcde|afg", "adf|bceg"],
                         ["ce|abdfg", "bce|adfg", "bcde|afg", "abcdf|eg", "bcef|adg"])}
    out = {}
    for name, (x, y) in P.items():
        Is = []
        for sp in (x, y):
            S, n = from_splits(sp)
            assert len(RC.splits_of(S, n)) == len(sp)
            I = per_base((S, n))
            Is.append(I)
        hh = refinement(Is, 8)
        out[name] = {"k": [I["k"] for I in Is], "lam": [I["lam"] for I in Is], "N": [I["N"] for I in Is],
                     "equal": {"a": Is[0]["a"] == Is[1]["a"], "N1": Is[0]["N1"] == Is[1]["N1"], "W2": hh[1][0] == hh[1][1],
                               "WL": hh[-1][0] == hh[-1][1], **{f"B{r}": Is[0][f"B{r}"] == Is[1][f"B{r}"] for r in RADII}}}
    return out


if __name__ == "__main__" and sys.argv[1] == "pairs":
    print(json.dumps(pairs(), indent=1))
elif __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "census":
        res = census(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 8)
    elif mode == "families":
        res = families(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 8)
    elif mode == "proofs":
        res = proofs()
    elif mode == "check_canon":
        res = check_canon(int(sys.argv[2]))
    print(json.dumps(res, indent=1, default=str))
