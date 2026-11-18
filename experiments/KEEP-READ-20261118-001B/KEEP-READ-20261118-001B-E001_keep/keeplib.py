"""KEEP-READ-20261118-001B-E001: what the knots read in SEED's second phase.

Along SEEDK runs (KNOT-SWITCH-20261118-001B's knotlib.py, pinned), after the switch, every zero-cost KF3 move (a knot set) is
labelled by its outcome (lambda after: 2 keeps two orders, more raises) and by SEED's acceptance, and given its local knot picture
at radius r = 1, 2, 3.  The picture is the incidence graph of distinctions and knots: the move's knots and every old knot within r
steps of the old distinctions the move uses (a step joins a distinction to a knot holding it); the new distinction, the move's
knots and each distinction's role in each knot (middle or end) are marked.  Pictures are compared by the Weisfeiler-Lehman hash and
confirmed by exact isomorphism.
"""
import itertools
import os
import random
import sys
from collections import defaultdict

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "KNOT-SWITCH-20261118-001B", "KNOT-SWITCH-20261118-001B-E001_switch"))
import knotlib as K  # noqa: E402

M, L, P = K.M, K.L, K.P


def picture(knots, move, n, r):
    """The radius-r local knot picture of a move (its knots hold the new distinction n)."""
    holding = defaultdict(list)
    for i, k in enumerate(knots):
        for v in k:
            holding[v].append(i)
    start = {v for k in move for v in k if v != n}
    vs = set(start)
    ks = set()
    frontier = set(start)
    for _ in range(r):
        new_k = {i for v in frontier for i in holding[v]} - ks
        ks |= new_k
        new_v = {v for i in new_k for v in knots[i]} - vs
        vs |= new_v
        frontier = new_v
    G = nx.Graph()
    G.add_node(("d", n), kind="new")
    for v in vs:
        G.add_node(("d", v), kind="start" if v in start else "old")
    for j, k in enumerate(move):
        G.add_node(("m", j), kind="move")
        for pos, v in enumerate(k):
            G.add_edge(("m", j), ("d", v), role="mid" if pos == 1 else "end")
    for i in ks:
        k = knots[i]
        G.add_node(("k", i), kind="knot")
        for pos, v in enumerate(k):
            if ("d", v) not in G:
                G.add_node(("d", v), kind="old")
            G.add_edge(("k", i), ("d", v), role="mid" if pos == 1 else "end")
    return G


def picture_closure(S, n, move):
    """The closure picture: the move's knots, and every betweenness that the states imply among the move's old distinctions,
    each with its middle (local in support, read from the states)."""
    O, Z, full = M.cols(S, n)
    D = sorted({v for k in move for v in k if v != n})
    G = nx.Graph()
    G.add_node(("d", n), kind="new")
    for v in D:
        G.add_node(("d", v), kind="start")
    for j, k in enumerate(move):
        G.add_node(("m", j), kind="move")
        for pos, v in enumerate(k):
            G.add_edge(("m", j), ("d", v), role="mid" if pos == 1 else "end")
    c = 0
    for x, y, z in itertools.permutations(D, 3):
        if x < z and ((full ^ (O[x] ^ O[z])) & (O[x] ^ O[y])) == 0:      # B(x, y, z): never x = z != y
            G.add_node(("i", c), kind="implied")
            G.add_edge(("i", c), ("d", x), role="end")
            G.add_edge(("i", c), ("d", y), role="mid")
            G.add_edge(("i", c), ("d", z), role="end")
            c += 1
    return G


def coverage(knots, move, n, r):
    """The fraction of the old distinctions within radius r of the move's old distinctions."""
    G = picture(knots, move, n, r)
    return (sum(1 for v, d in G.nodes(data=True) if v[0] == "d") - 1) / n


def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="kind", edge_attr="role", iterations=4)


def same(G, H):
    return nx.is_isomorphic(G, H, node_match=lambda a, b: a["kind"] == b["kind"], edge_match=lambda a, b: a["role"] == b["role"])


def serial(G):
    return {"nodes": [[list(v), d["kind"]] for v, d in G.nodes(data=True)],
            "edges": [[list(a), list(b), d["role"]] for a, b, d in G.edges(data=True)]}


def unserial(x):
    G = nx.Graph()
    for v, kind in x["nodes"]:
        G.add_node(tuple(v), kind=kind)
    for a, b, role in x["edges"]:
        G.add_edge(tuple(a), tuple(b), role=role)
    return G


def moves_after_switch(knots0, n0, nmax, seed_value, radii=(0, 1, 2, "c")):
    """A SEEDK run; after the switch, every zero-cost move with its outcome, acceptance, features and picture hashes; and, for
    each radius and hash, one serialised picture per outcome (keeps two orders or raises), for exact comparison."""
    rng = random.Random(seed_value)
    S = M.base(n0, knots0)
    G = M.pairs_of(knots0)
    knots = list(knots0)
    n = n0
    out = []
    reps = {r: {} for r in radii}
    while n < nmax:
        b = K.betti(n, knots)
        ops, kind = K.seedk_options(S, n, G, b["b2"])
        if not ops:
            break
        if b["b2"] > 0:
            mv = L.moves(S, n, G)
            zero = [x for x in mv if P.pc(x[0]) + P.pc(x[1]) == len(S)]
            acc = {x[:2] for x in ops} if kind == "fill" else set()
            lam_of = {}
            fk0 = len(K.filled_knots(knots))
            for a0, a1, ks in zero:
                if (a0, a1) not in lam_of:
                    lam_of[(a0, a1)] = P.kl(M.apply(S, n, a0, a1), n + 1)[1]
                pairs = [tuple(sorted(x for x in k if x != n)) for k in ks]
                after = K.betti(n + 1, knots + list(ks))
                row = {"n": n, "lam_after": lam_of[(a0, a1)], "accepted": (a0, a1) in acc, "ext": [a0, a1],
                       "knots": len(ks), "components": K.components(pairs), "db1": after["b1"] - b["b1"],
                       "db2": after["b2"] - b["b2"], "new_filled": len(K.filled_knots(knots + list(ks))) - fk0,
                       "middles": sum(1 for k in ks if k[1] == n)}
                row["coverage1"] = coverage(knots, ks, n, 1)
                row["coverage2"] = coverage(knots, ks, n, 2)
                for r in radii:
                    pic = picture_closure(S, n, ks) if r == "c" else picture(knots, ks, n, r)
                    h = wl(pic)[:12]
                    row[f"h{r}"] = h
                    key = "keep" if row["lam_after"] == 2 else "raise"
                    reps[r].setdefault(h, {}).setdefault(key, pic)
                out.append(row)
        a0, a1, ks = rng.choice(ops)
        S = M.apply(S, n, a0, a1)
        G = G | M.pairs_of(ks)
        knots += list(ks)
        n += 1
    verified = {}
    for r in radii:                         # hashes met with both outcomes in this run, confirmed by exact isomorphism
        mixed = [h for h, d in reps[r].items() if len(d) == 2]
        ok = [h for h in mixed if same(reps[r][h]["keep"], reps[r][h]["raise"])]
        verified[r] = {"mixed": len(mixed), "isomorphic": len(ok), "hashes": ok,
                       "example": ({"keep": serial(reps[r][ok[0]]["keep"]), "raise": serial(reps[r][ok[0]]["raise"])} if ok else None)}
    return out, verified
