"""Shared-runner job for the referee's checks of the four bare-growth studies of 2026-11-20 (ORDINARY-DYNAMICS, BOND-CLOSURE,
FRESH-DEMAND, SERIAL-REPAIRS), with the referee's own code only: its EXPLOSIVE-R1 grower (the program's rule, structural implied
test), its exact least-bond MILP (LATER-BOND-READING-R1's bondmilp.py) and its REDUCE-BLOCKS-R1 random starts.

Parts:
- OD: the four-knot pair (centre with no spare / one spare loose distinction): counts for 30 rounds; at the first reached stage the
  least bond holding two of the three y's and all three (study: 3 against 4); the chain variant at L = 6 (one past the registered
  lengths): whole-stage ordinary distance from the extra unary birth to the P's, and the same bond values; the sharp general control
  (u, a, b, x with private doubled witnesses; loose 1, 2, 2 and x at 0 or 1): the fresh count of the birth {u, a, b}.
- BC: on every stage, rounds 0 to 3, of 300 random starts of 6 to 10 knots within seven places, each birth of three or more parents:
  the least bond holding p - 1 of its inputs, against whether the birth takes every loose distinction (the criterion: = p exactly
  when it does).
- FD: on the same stages, every birth's lookahead demand recomputed by the study's formula (1) from its parents' child lists alone,
  against the engine's demand.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXPLOSIVE-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1", "research/REDUCE-BLOCKS-20261119-001/referee-R1",
          "research/LATER-BOND-READING-20261119-001/referee-R1", "research/MERGE-BURST-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def wired(S):
    own = defaultdict(list)
    for j, q in enumerate(S):
        for x in q:
            own[x].append(j)
    O = len(S)
    key = defaultdict(list)
    for x, js in own.items():
        key[tuple(sorted(js)) if len(js) == 2 else (js[0], O)].append(x)
    items = sorted(key.items())
    return O + 1, [(k[0], k[1], len(v)) for k, v in items], {x: i for i, (k, v) in enumerate(items) for x in v}


def K(S, marks):
    import bondmilp as B
    n, bd, bof = wired(S)
    v, _ = B.least_bond(n, bd, sorted({bof[x] for x in marks}))
    return v


def four_knot(spare):
    # S = 0 meets U1, U2, U3 (1..3) on s_i; each U_i has two loose distinctions; S has `spare` loose
    stars = [[0, 1, 2], [0, 3, 4], [1, 5, 6], [2, 7, 8]]
    if spare:
        stars[0].append(9)
    return stars


def chain(L, spare):
    """S joined to Z by three disjoint chains of L ordinary steps, interior meetings doubled; U_i (first after S) two loose each;
    Z zero or one loose."""
    stars = defaultdict(list)
    nb = [0]

    def link(a, b, k=1):
        for _ in range(k):
            stars[a].append(nb[0])
            stars[b].append(nb[0])
            nb[0] += 1
    S, Z = "S", "Z"
    for c in range(3):
        prev = S
        for i in range(1, L):
            v = (c, i)
            link(prev, v, 1 if prev == S else 2)
            prev = v
        link(prev, Z, 2 if L > 2 else 1)
    for c in range(3):
        for _ in range(2):
            stars[(c, 1)].append(nb[0])
            nb[0] += 1
    if spare:
        stars[Z].append(nb[0])
        nb[0] += 1
    order = [S, Z] + sorted(k for k in stars if k not in (S, Z))
    return [sorted(stars[k]) for k in order], order


def part_od():
    import networkx as nx
    import job_expl as JX
    out = {}
    for spare in (0, 1):
        G = JX.grower([list(q) for q in four_knot(spare)])
        counts, end = [], "alive"
        st1 = None
        for t in range(30):
            r = G.step(JX.floored, None, None)
            if r != "ok":
                end = r
                break
            counts.append(sum(1 for j in range(len(G.bits)) if G.round[j] == t + 1))
            if t == 0:
                st1 = [sorted(q) for q in G.bits]
                ys = [x for j in range(len(G.bits)) if G.round[j] == 1 and len(G.parents[j]) == 2 for x in G.bits[j][2:]]
        out[f"four knots, spare {spare}"] = {"counts per round": counts, "end": end,
                                            "K(two y's), K(three y's) at the first stage": [K(st1, ys[:2]), K(st1, ys)]}
    for spare in (0, 1):
        S0, order = chain(6, spare)
        G = JX.grower([list(q) for q in S0])
        r = G.step(JX.floored, None, None)
        st = [sorted(q) for q in G.bits]
        born = [j for j in range(len(G.bits)) if G.round[j] == 1]
        P = [j for j in born if len(G.parents[j]) == 2]
        un = [j for j in born if len(G.parents[j]) == 1]
        g = nx.Graph()
        own = defaultdict(list)
        for j, q in enumerate(st):
            for x in q:
                own[x].append(j)
        for js in own.values():
            if len(js) == 2:
                g.add_edge(*js)
        ys = [x for j in P for x in G.bits[j][2:]]
        row = {"round 1": r, "pair births": len(P), "unary births": len(un), "K(two y's), K(three y's)": [K(st, ys[:2]), K(st, ys)]}
        if un:
            row["ordinary distance from the unary birth to the P's"] = min(nx.shortest_path_length(g, un[0], p) for p in P)
        r2 = G.step(JX.floored, None, None)
        trip = [j for j in range(len(G.bits)) if G.round[j] == 2 and len(G.parents[j]) == 3]
        row["round 2: the triple's fresh count"] = [G.fresh[j] for j in trip]
        out[f"chain L = 6, spare {spare}"] = row
    # the sharp general control
    for xl in (0, 1):
        nbx = [0]
        stars = defaultdict(list)

        def link(a, b, k):
            for _ in range(k):
                stars[a].append(nbx[0])
                stars[b].append(nbx[0])
                nbx[0] += 1
        for pr in (("u", "a"), ("u", "b"), ("a", "b"), ("a", "x"), ("b", "x")):
            w = "w" + "".join(pr)
            link(pr[0], w, 2)
            link(pr[1], w, 2)
        for k, c in (("u", 1), ("a", 2), ("b", 2), ("x", xl)):
            for _ in range(c):
                stars[k].append(nbx[0])
                nbx[0] += 1
        names = sorted(stars)
        G = JX.grower([sorted(stars[k]) for k in names])
        r = G.step(JX.floored, None, None)
        idx = {k: i for i, k in enumerate(names)}
        tri = [j for j in range(len(G.bits)) if G.round[j] == 1 and G.parents[j] == {idx["u"], idx["a"], idx["b"]}]
        out[f"general control, x loose {xl}"] = {"round 1": r, "fresh count of {u,a,b}": [G.fresh[j] for j in tri]}
    return out


def stages(rng, n):
    import job_rb as RB
    import job_expl as JX
    sizes, e = RB.sample(n, rng, P=7)
    import job_ring as JR
    G = JX.grower(JR.stars_of(len(sizes), e, list(sizes)))
    for t in range(4):
        before = [sorted(q) for q in G.bits]
        nb = len(G.bits)
        loose = {x for q in before for x in q if sum(1 for qq in before if x in qq) == 1}
        r = G.step(JX.floored, None, None)
        if r != "ok":
            return
        yield before, loose, G, nb
        if len(G.bits) > 400:
            return


def part_bc_fd(seed, count):
    import networkx as nx
    rng = random.Random(seed)
    s = Counter()
    bad = []
    for i in range(count):
        n = rng.randint(6, 10)
        for before, loose, G, nb in stages(rng, n):
            new = list(range(nb, len(G.bits)))
            for j in new:
                P = sorted(G.parents[j])
                p = len(P)
                # FD: formula (1) from the parents' child lists
                sib = [k for k in new if k != j and G.parents[k] & G.parents[j]]
                I = {k: G.parents[k] & G.parents[j] for k in sib}
                g = nx.Graph()
                g.add_nodes_from(sib)
                for a, b in itertools.combinations(sib, 2):
                    if G.parents[a] & G.parents[b]:
                        g.add_edge(a, b)
                Q = [set(c) for c in nx.find_cliques(g) if len(c) >= 2 and not set.intersection(*(I[k] for k in c))]
                U = set().union(*Q) if Q else set()
                D = len(Q) + len([k for k in sib if k not in U])
                s["births: formula (1) checked"] += 1
                s["births: formula (1) equals the engine's demand"] += D == G.dem[j]
                if D != G.dem[j] and len(bad) < 5:
                    bad.append(["FD", P, D, G.dem[j]])
                # BC: p >= 3, the least bond on p - 1 inputs
                if p >= 3:
                    inputs = [x for x in G.bits[j] if x in loose]
                    exhausts = set(inputs) == loose
                    b = K(before, inputs[:p - 1])
                    s[f"BC: births with {min(p, 6)}{'+' if p >= 6 else ''} parents"] += 1
                    s["BC: criterion agrees"] += (b == p) == exhausts
                    s["BC: exhausting births"] += exhausts
                    if (b == p) != exhausts and len(bad) < 10:
                        bad.append(["BC", P, b, exhausts])
    return {"counts": dict(s), "failures": bad}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("OD", {"part": "OD"})] + [(f"BCFD-{c}", {"part": "BCFD", "c": c}) for c in range(3)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "OD":
        r = part_od()
    else:
        r = part_bc_fd(f"g1-{p['c']}", 100)
    return json.loads(json.dumps(r, default=lambda o: int(o) if hasattr(o, "__int__") else str(o)))
