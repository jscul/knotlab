"""Referee R1 for KNOT-SWITCH-20261118-001 (own code; the study's knotlib.py, run.py and the pinned melib/nnlib/picklib are not
imported).

  ../../../.venv/bin/python -B referee_switch.py <part> > referee_switch_<part>.json      (from this directory)

Knots are triples (x, y, z) with y between x and z (B(x, y, z) forbids x = z != y).  The knot complex: vertices the distinctions,
edges the pairs that share a knot, triangles the distinct knot triples; b2 over GF(2) by the referee's own elimination.  A filled
knot: four distinctions whose four triples carry knots with middles forming the fill pattern (each distinction the middle of one,
the middles pairing up as in a knot (a, c, b) and its fill B(a, r, b), B(c, a, r), B(c, b, r)).

Parts:
  w2         every way of giving the four triples of four distinctions one knot each with every distinction a middle once (the
             nine derangements): the patterns they allow, whether two of the four are forced to be copies, whether two splits cross.
  w4         the line of n = 4 to 9 presented by every knot it satisfies: b2, filled knots, crossings.
  converse   random presentations (5 to 7 distinctions, 3 to 9 random betweenness knots), copy-free bases: is there a crossing
             without a filled knot in the presentation, and without one among all the knots the base satisfies?
  runs       KF3 (cheapest knot-local, uniform over knot sets) to n = 30 and SEEDK (SEED with knot-local moves, its switch read from
             the crossings) to n = 40, one seed each, from every bracketing of 5, 6, 7 and every third of 8: at every step whether
             nothing crosses, no filled knot, b2 = 0 and no fill yet agree; SEEDK's two orders and full grids.
"""
import itertools
import json
import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/COUNT-BALLS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/CUBE-DOUBLING-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_cap as KC  # noqa: E402
import referee_census as RCN  # noqa: E402
import referee_cube as RC  # noqa: E402

pc = RC.pc


def ok(s, k):
    x, y, z = k
    return not ((((s >> x) ^ (s >> z)) & 1) == 0 and (((s >> x) ^ (s >> y)) & 1) == 1)


def states_of(n, knots):
    return tuple(s for s in range(1 << n) if all(ok(s, k) for k in knots))


def rank2(rows):
    basis = []
    for r in rows:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
    return len(basis)


def b2(knots):
    T = sorted({tuple(sorted(k)) for k in knots})
    E = sorted({e for t in T for e in itertools.combinations(t, 2)})
    ix = {e: i for i, e in enumerate(E)}
    return len(T) - rank2([sum(1 << ix[e] for e in itertools.combinations(t, 2)) for t in T])


FILL_TYPE = set()
for a, b, c, r in itertools.permutations(range(4)):
    # a knot (a, c, b) and its fill: middles c on {a,b,c}, r on {a,b,r}, a on {a,c,r}, b on {b,c,r}
    FILL_TYPE.add(frozenset({(frozenset({a, b, c}), c), (frozenset({a, b, r}), r), (frozenset({a, c, r}), a), (frozenset({b, c, r}), b)}))


def filled_knots(knots):
    mids = {}
    for x, y, z in knots:
        mids.setdefault(frozenset((x, y, z)), set()).add(y)
    verts = sorted({v for k in knots for v in k})
    out = []
    for Q in itertools.combinations(verts, 4):
        trip = [frozenset(t) for t in itertools.combinations(Q, 3)]
        if not all(t in mids for t in trip):
            continue
        loc = {v: i for i, v in enumerate(Q)}
        for choice in itertools.product(*[sorted(mids[t]) for t in trip]):
            pat = frozenset((frozenset(loc[v] for v in t), loc[m]) for t, m in zip(trip, choice))
            if pat in FILL_TYPE:
                out.append(Q)
                break
    return out


def splits(S, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in S if s not in (0, full)})


def crosses(S, n):
    full = (1 << n) - 1
    sp = splits(S, n)
    return any(all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))) for a, b in itertools.combinations(sp, 2))


def copy_free(S, n):
    cols = [tuple((s >> u) & 1 for s in S) for u in range(n)]
    comp = [tuple(1 - x for x in c) for c in cols]
    return len(set(cols)) == n and not any(cols[u] == comp[v] for u in range(n) for v in range(n))


def implied_knots(S, n):
    return [(x, y, z) for x, z in itertools.combinations(range(n), 2) for y in range(n) if y not in (x, z)
            and all(ok(s, (x, y, z)) for s in S)]


# ---------------- parts ----------------

def part_w2():
    out = []
    trip = [frozenset(t) for t in itertools.combinations(range(4), 3)]
    for choice in itertools.product(*[sorted(t) for t in trip]):
        if sorted(choice) != [0, 1, 2, 3]:
            continue
        knots = []
        for t, m in zip(trip, choice):
            e = sorted(t - {m})
            knots.append((e[0], m, e[1]))
        S = states_of(4, knots)
        pat = frozenset((frozenset(t), m) for t, m in zip(trip, choice))
        cols = [tuple((s >> u) & 1 for s in S) for u in range(4)]
        out.append({"middles": list(choice), "fill_type": pat in FILL_TYPE, "patterns": [format(s, "04b")[::-1] for s in S],
                    "copies_forced": len(set(cols)) < 4, "crossing": crosses(S, 4)})
    return out


def part_w4():
    out = []
    for n in range(4, 10):
        S = RM.line_states(n)
        K = implied_knots(S, n)
        out.append({"n": n, "implied_knots": len(K), "b2": b2(K), "C(n-1,3)": len(list(itertools.combinations(range(n - 1), 3))),
                    "filled_knots": len(filled_knots(K)), "crossing": crosses(S, n)})
    return out


def part_converse(count=3000, seed=20261118):
    rng = random.Random(seed)
    res = {"bases": 0, "with_crossing": 0, "crossing_without_presented_filled_knot": 0,
           "crossing_without_any_filled_knot": 0, "filled_knot_without_crossing": 0, "examples": []}
    tried = 0
    while res["bases"] < count and tried < 50 * count:
        tried += 1
        n = rng.randint(5, 7)
        m = rng.randint(3, 9)
        knots = []
        for _ in range(m):
            x, y, z = rng.sample(range(n), 3)
            knots.append((x, y, z))
        S = states_of(n, knots)
        if len(S) < 4 or not copy_free(S, n):
            continue
        res["bases"] += 1
        cr = crosses(S, n)
        fp = bool(filled_knots(knots))
        fa = bool(filled_knots(implied_knots(S, n)))
        res["with_crossing"] += cr
        res["filled_knot_without_crossing"] += (fp and not cr)
        if cr and not fp:
            res["crossing_without_presented_filled_knot"] += 1
            if len(res["examples"]) < 3:
                res["examples"].append({"n": n, "knots": knots, "states": len(S), "filled_knot_among_all_satisfied_knots": fa})
        if cr and not fa:
            res["crossing_without_any_filled_knot"] += 1
    return res


def seed_ok(S, n, S2):
    """SEED's condition after its switch: no new crossing between two splits that crossed something; a split that crossed nothing
    and gains crossings ends with exactly the crossers of one that crossed something."""
    full = (1 << n) - 1
    sp = splits(S, n)
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            G.add_edge(i, j)
    sp2 = splits(S2, n + 1)
    full2 = (1 << (n + 1)) - 1
    m = {i: next(j for j, b in enumerate(sp2) if (b & full) in (a, full ^ a)) for i, a in enumerate(sp)}
    G2 = nx.Graph()
    G2.add_nodes_from(range(len(sp2)))
    for i, j in itertools.combinations(range(len(sp2)), 2):
        a, b = sp2[i], sp2[j]
        if all(x for x in (a & b, a & (full2 ^ b), (full2 ^ a) & b, (full2 ^ a) & (full2 ^ b))):
            G2.add_edge(i, j)
    active = {v for v in G if G.degree(v)}
    new = [(i, j) for i, j in itertools.combinations(range(len(sp)), 2) if not G.has_edge(i, j) and G2.has_edge(m[i], m[j])]
    if any(i in active and j in active for i, j in new):
        return False
    gained = {v for e in new for v in e if v not in active}
    nb = {v: frozenset(G2[m[v]]) for v in range(len(sp))}
    olds = {nb[v] for v in active}
    return all(nb[u] in olds for u in gained)


def full_grid(S, n):
    full = (1 << n) - 1
    sp = splits(S, n)
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            G.add_edge(i, j)
    if not G.number_of_edges():
        return False
    parts = list(nx.connected_components(nx.complement(G)))
    if any(G.has_edge(a, b) for P in parts for a, b in itertools.combinations(P, 2)):
        return False
    if G.number_of_edges() != (len(sp) ** 2 - sum(len(P) ** 2 for P in parts)) // 2:
        return False
    prod = 1
    for P in parts:
        prod *= len(P) + 1
    return prod == n


def one_run(args):
    rule, T, seed, nmax = args
    n0 = 1 + max(max(k) for k in T) if T else 3
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    knots = list(T)
    rng = random.Random(f"{rule}:{T}:{seed}")
    agree = True
    steps = 0
    fill_made = False
    after = []
    subs_after_full = []
    seen_full = False
    nfull = 0
    while n < nmax and len(S) <= 60:
        cost, top = RM.options(S, n, G)
        move = None
        if rule == "KF3":
            if top:
                move = rng.choice(top)
        else:                                                     # SEEDK
            if cost == 0:
                good = top if not crosses(S, n) else [t for t in top if seed_ok(S, n, RM.extend(S, n, t[0], t[1]))]
                if good:
                    move = rng.choice(good)
            if move is None:
                subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
                if subs:
                    u, v = rng.choice(subs)
                    k = (u, n, v)
                    S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if ok(x, k)))
                    move = ("sub", S2, (k,))
        if move is None:
            break
        if move[0] == "sub":
            S2, ks = move[1], move[2]
        else:
            S2, ks = RM.extend(S, n, move[0], move[1]), move[2]
        kind = "fill" if len(S2) == len(S) else "sub"
        if kind == "sub" and seen_full:
            subs_after_full.append(full_grid(S, n))
        fill_made = fill_made or kind == "fill"
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
        knots += list(ks)
        cr = crosses(S, n)
        fk = bool(filled_knots(knots))
        z = b2(knots) == 0
        if not ((not cr) == (not fk) == z == (not fill_made)):
            agree = False
        steps += 1
        if fill_made:
            m = KC.measure(list(S), n)
            after.append((RCN.chromatic(splits(S, n), (1 << n) - 1), m["lam"]))
        if full_grid(S, n):
            seen_full = True
            nfull += 1
    return {"rule": rule, "n0": n0, "steps": steps, "readings_agree": agree,
            "two_orders_after_first_fill": all(x == (2, 2) for x in after) if rule == "SEEDK" else None,
            "lam_end": after[-1][1] if after else 1, "full_grids": nfull,
            "subdivisions_after_first_full_grid_all_at_full_grids": all(subs_after_full) if subs_after_full else None}


def part_runs(workers=16):
    from multiprocessing import Pool
    Ts = []
    for n0 in (5, 6, 7):
        Ts += [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    Ts += [tuple(T) for T in RM.bracketings(0, 7)][::3]
    jobs = [("KF3", T, 0, 30) for T in Ts] + [("SEEDK", T, 0, 40) for T in Ts]
    with Pool(workers) as P:
        rows = P.map(one_run, jobs, chunksize=1)
    out = {"bracketings": len(Ts)}
    for rule in ("KF3", "SEEDK"):
        R = [r for r in rows if r["rule"] == rule]
        out[rule] = {"runs": len(R), "steps": sum(r["steps"] for r in R), "readings_agree_every_step": sum(r["readings_agree"] for r in R)}
        if rule == "SEEDK":
            out[rule]["two_orders_every_step_after_first_fill"] = sum(bool(r["two_orders_after_first_fill"]) for r in R)
            out[rule]["later_subdivisions_all_at_full_grids"] = sum(r["subdivisions_after_first_full_grid_all_at_full_grids"] is True for r in R)
            out[rule]["three_or_more_full_grids"] = sum(r["full_grids"] >= 3 for r in R)
        else:
            out[rule]["lam_end"] = sorted({r["lam_end"] for r in R})
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"w2": part_w2, "w4": part_w4, "converse": part_converse, "runs": part_runs}[part]
    print(json.dumps(f(), indent=1, default=str))
