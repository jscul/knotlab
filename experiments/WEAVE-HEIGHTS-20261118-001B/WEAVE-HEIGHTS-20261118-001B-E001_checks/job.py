"""Shared-runner job for WEAVE-HEIGHTS-20261118-001B-E001: mechanical checks of each step of ticket A's proofs on weave discs.
Reuses DOUBLE-MEET's weavelib.py (discs, height distances, the cyclic criterion) unchanged."""
import itertools
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches"))
import importlib.util  # noqa: E402
import weavelib as W  # noqa: E402

_spec = importlib.util.spec_from_file_location("dm_job", ROOT / "experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches/job.py")
DM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DM)  # DOUBLE-MEET's discs_of_size, unchanged

M, N, nx = W.M, W.N, W.nx
SH = 12


def cases():
    for k in range(1, 13):
        sh = SH if k >= 10 else 1
        for s in range(sh):
            yield f"discs-k{k}-s{s}", {"k": k, "shard": s, "of": sh}


def forward(a, b):
    d = (b[0] - a[0], b[1] - a[1])
    return d in ((1, 0), (-1, 1), (0, -1))


def check(T, k):
    r = {"discs": 1, "flag_fail": 0, "convex_fail": 0, "triangle_fail": 0, "level_knots": 0, "dd_fail": 0, "lone_fail": 0,
         "states_vs_omega_fail": 0, "omega_checked": 0, "criterion_sets": 0, "criterion_fail": 0, "bonded_pairs": 0, "below_bound": 0}
    V = sorted({v for t in T for v in W.verts(t)})
    ix = {v: i for i, v in enumerate(V)}
    E = {tuple(sorted(e)) for t in T for e in itertools.combinations(W.verts(t), 2)}
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    # Lemma 0: every 3-clique of the pair graph is a knot of T
    Tset = {frozenset(W.verts(t)) for t in T}
    for a, b, c in itertools.combinations(V, 3):
        if G.has_edge(a, b) and G.has_edge(b, c) and G.has_edge(a, c) and frozenset((a, b, c)) not in Tset:
            r["flag_fail"] += 1
    dist = dict(nx.all_pairs_shortest_path_length(G))
    # bridged-graph properties used in Lemma 5: convex balls and the triangle condition
    for x in V:
        for t in range(1, max(dist[x].values()) + 1):
            ball = {v for v in V if dist[x][v] <= t - 1}
            for u, w in itertools.combinations(sorted(ball), 2):
                for z in V:
                    if z not in ball and dist[u][z] + dist[z][w] == dist[u][w]:
                        r["convex_fail"] += 1
                        break
        for a, b in E:
            if dist[x][a] == dist[x][b] >= 1:
                if not any(G.has_edge(w, a) and G.has_edge(w, b) and dist[x][w] == dist[x][a] - 1 for w in V):
                    r["triangle_fail"] += 1
        # Lemma 5: no level knot
        for t_ in T:
            vs = W.verts(t_)
            if len({dist[x][v] for v in vs}) == 1:
                r["level_knots"] += 1
    DD = W.height_distances(T)
    for a, b in itertools.combinations(V, 2):
        r["dd_fail"] += DD[a][b] + DD[b][a] != 3 * dist[a][b]
    # Lemma 8
    deg = {v: sum(v in W.verts(t) for t in T) for v in V}
    for x in V:
        if deg[x] != 1:
            continue
        kx = next(t for t in T if x in W.verts(t))
        a0, a1, a2 = W.verts(kx)
        cyc = [a0, a1, a2] if forward(a0, a1) else [a0, a2, a1]
        i = cyc.index(x)
        u, v = cyc[(i + 1) % 3], cyc[(i + 2) % 3]
        for s in V:
            if s != x and DD[s][x] != DD[s][v] + 1:
                r["lone_fail"] += 1
            if s != x and DD[x][s] != 1 + DD[u][s]:
                r["lone_fail"] += 1
    n = len(V)
    st = M.states(n, [(N.NAE3, tuple(sorted(ix[v] for v in W.verts(t)))) for t in sorted(T)])
    # Lemma 1: states = 2 x (choices of one falling pair per knot, consistent on shared pairs), checked to eight knots
    if k <= 8:
        r["omega_checked"] = 1
        pairs_of = [list(itertools.combinations(sorted(W.verts(t)), 2)) for t in sorted(T)]
        count = 0
        for choice in itertools.product(range(3), repeat=len(pairs_of)):
            chosen = {}
            ok = True
            for kn, ch in zip(pairs_of, choice):
                for j, p in enumerate(kn):
                    want = j == ch
                    if chosen.get(p, want) != want:
                        ok = False
                        break
                    chosen[p] = want
                if not ok:
                    break
            count += ok
        r["states_vs_omega_fail"] = int(len(st) != 2 * count)
        # Proposition 3, set by set
        tight = W.tight_sets(V, DD)
        free = M.free_table(n, st)
        for mask in range(1 << n):
            r["criterion_sets"] += 1
            r["criterion_fail"] += any((m & mask) == m for m in tight) != (not free[mask])
    # Theorem 7 on discs of twelve knots (one size past DOUBLE-MEET's census)
    if k == 12:
        D = M.bond_matrix(n, st)
        for a, b in itertools.combinations(range(n), 2):
            if D[a][b] != math.inf:
                r["bonded_pairs"] += 1
                r["below_bound"] += D[a][b] < dist[V[a]][V[b]] + 1
    return r


def run(case_id, p):
    acc = {}
    for i, T in enumerate(DM.discs_of_size(p["k"])):
        if i % p["of"] != p["shard"]:
            continue
        for key, v in check(T, p["k"]).items():
            acc[key] = acc.get(key, 0) + v
    acc["k"] = p["k"]
    return acc
