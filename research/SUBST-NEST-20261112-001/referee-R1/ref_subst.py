#!/usr/bin/env python3
"""Referee SUBST-NEST-R1: the referee's own code (no import of subst_lib.py or check.py).

    python3 -B ref_subst.py --part blocks|census|gadgets|random [--workers 6]

blocks:  every living connected block (3 to 5 distinctions, any knots; 6 with up to 5 knots), one per isomorphism class; for each,
         its states, its spare distinctions, and its template under each of the three block-triple sets (empty, rigid, else);
         and the referee's lemma checked on the template: with the block's knots as block triples, a template triple (t1, t2, t3)
         differs at a distinction only if that distinction is spare.
census:  every block x block-triple set x test (chains of 4, 8, 16 knots and the three-copy nestings of levels 1 to 3 substituted
         once; chains of 4 and 8 and nestings 1 and 2 substituted twice): the FULL tie relation of the substituted pattern (not
         only from the roots), so that every tie outside a copy is seen; the parts tied across the whole pattern; for each root
         (0, p, ..., p) its tie class, ties outside its copy, tie extent and farthest distinction (steps apart).
gadgets: knot substitution by the three-copy gadget (levels 0 to 5) and by the Fano plane less one knot (levels 0 to 4): the
         terminals' relation, the full tie relation, distinction counts.
random:  the referee's lemma (spare iff not pinned) on 500 random living blocks of 6 to 10 distinctions, checked by SAT on one knot
         substituted once, and on the chain of 8 knots substituted once for some of them."""
import itertools
import json
import random
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent


def nae(a, b, c):
    return not (a == b == c)


def states(m, K):
    return [s for s in itertools.product((0, 1), repeat=m) if all(nae(s[a], s[b], s[c]) for a, b, c in K)]


def canon(m, K):
    return min(tuple(sorted(tuple(sorted(p[x] for x in e)) for e in K)) for p in itertools.permutations(range(m)))


def connected(m, K):
    seen = {0}
    grew = True
    while grew:
        grew = False
        for e in K:
            if seen & set(e) and not set(e) <= seen:
                seen |= set(e)
                grew = True
    return seen == set(range(m))


def blocks():
    out = set()
    for m in range(3, 7):
        tri = list(itertools.combinations(range(m), 3))
        kmax = len(tri) if m <= 5 else 5
        for k in range(1, kmax + 1):
            for K in itertools.combinations(tri, k):
                if set(itertools.chain(*K)) != set(range(m)) or not connected(m, K):
                    continue
                c = canon(m, K)
                if (m, c) in out:
                    continue
                if states(m, c):
                    out.add((m, c))
    return sorted(out)


def spare(m, K):
    """p is spare when B's other distinctions can be valued so that every knot holds both values among its members other than p"""
    out = []
    for p in range(m):
        rest = [q for q in range(m) if q != p]
        for vals in itertools.product((0, 1), repeat=m - 1):
            u = dict(zip(rest, vals))
            if all(len({u[x] for x in e if x != p}) == 2 for e in K):
                out.append(p)
                break
    return out


def triple_sets(m, K):
    return {"diagonal": [(p, p, p) for p in range(m)],
            "the block's knots": sorted({q for e in K for q in itertools.permutations(e)}),
            "every distinct triple": list(itertools.permutations(range(m), 3))}


def template(m, K, T):
    S = states(m, K)
    A = np.array(S, dtype=np.int8)                         # states x m
    out = []
    for i, j, k in itertools.product(range(len(S)), repeat=3):
        a, b, c = S[i], S[j], S[k]
        if all(nae(a[p], b[q], c[r]) for p, q, r in T):
            out.append((i, j, k))
    return S, out


def substitute(P, B, T):
    n, PK = P
    m, BK = B
    idx = lambda v, p: v * m + p
    knots = [(idx(v, a), idx(v, b), idx(v, c)) for v in range(n) for a, b, c in BK]
    knots += [(idx(x, p), idx(y, q), idx(z, r)) for x, y, z in PK for p, q, r in T]
    return (n * m, knots)


def chain(k):
    return (2 * k + 1, [(2 * i, 2 * i + 1, 2 * i + 2) for i in range(k)])


def nesting(level):
    """the drawn three-copy nesting: upward cells (x, y), x AND y = 0, of side 2^level"""
    N = 1 << level
    cells = [(x, y) for x in range(N) for y in range(N - x) if x & y == 0]
    pts = sorted({p for (x, y) in cells for p in ((x, y), (x + 1, y), (x, y + 1))})
    idx = {p: i for i, p in enumerate(pts)}
    knots = [(idx[(x, y)], idx[(x + 1, y)], idx[(x, y + 1)]) for (x, y) in cells]
    first = idx[(0, 0)]
    # relabel so that the corner (0, 0) is distinction 0 (the census's "P's first distinction")
    perm = list(range(len(pts)))
    perm[0], perm[first] = perm[first], perm[0]
    return (len(pts), [tuple(perm[a] for a in t) for t in knots])


def tie_relation(n, knots, seed=0, rounds=64):
    """None if no state; else dict rel[(u, v)] = forced value of x_u xor x_v for every tied pair u < v"""
    rng = random.Random(seed)
    cl = [c for a, b, c3 in knots for c in ([a + 1, b + 1, c3 + 1], [-(a + 1), -(b + 1), -(c3 + 1)])]
    with Glucose4(bootstrap_with=cl) as s:
        if not s.solve():
            return None
        X = []
        for _ in range(rounds):
            s.set_phases([v if rng.random() < 0.5 else -v for v in range(1, n + 1)])
            s.solve()
            m = s.get_model()
            X.append([1 if (v <= len(m) and m[v - 1] > 0) else 0 for v in range(1, n + 1)])
        X = np.array(X, dtype=np.uint8)
        used = np.zeros(n, dtype=bool)
        for t in knots:
            used[list(t)] = True
        D = X ^ X[0:1, :]
        groups = {}
        for v in np.where(used)[0]:
            groups.setdefault(D[:, v].tobytes(), []).append(int(v))
        rel = {}
        for g in groups.values():
            rest = g
            while len(rest) > 1:
                a = rest[0]
                keep = []
                cls = [a]
                for v in rest[1:]:
                    e = int(X[0, a] ^ X[0, v])
                    if s.solve(assumptions=[-(a + 1), (v + 1) if e == 0 else -(v + 1)]):
                        keep.append(v)
                    else:
                        cls.append(v)
                for i, u in enumerate(cls):
                    for w in cls[i + 1:]:
                        rel[(min(u, w), max(u, w))] = int(X[0, u] ^ X[0, w])
                rest = keep
        return rel


def steps(n, knots, src):
    nb = [set() for _ in range(n)]
    for t in knots:
        for a in t:
            nb[a] |= set(t) - {a}
    d = [-1] * n
    d[src] = 0
    q = deque([src])
    while q:
        x = q.popleft()
        for y in nb[x]:
            if d[y] < 0:
                d[y] = d[x] + 1
                q.append(y)
    return d


TESTS = [(1, "chain 4", chain(4)), (1, "chain 8", chain(8)), (1, "chain 16", chain(16)), (1, "nesting 1", nesting(1)),
         (1, "nesting 2", nesting(2)), (1, "nesting 3", nesting(3)), (2, "chain 4", chain(4)), (2, "chain 8", chain(8)),
         (2, "nesting 1", nesting(1)), (2, "nesting 2", nesting(2))]


def cell(args):
    (m, K), tname = args
    T = triple_sets(m, K)[tname]
    sp = set(spare(m, K))
    out = {"block": [m, [list(e) for e in K]], "triples": tname, "spare": sorted(sp), "tests": []}
    for k, name, P in TESTS:
        Q = P
        addr = {v: (v,) for v in range(P[0])}
        for _ in range(k):
            Q2 = substitute(Q, (m, K), T)
            addr = {v * m + p: addr[v] + (p,) for v in range(Q[0]) for p in range(m)}
            Q = Q2
        n, knots = Q
        rel = tie_relation(n, knots, seed=k * 100 + len(name))
        row = {"substitutions": k, "pattern": name, "distinctions": n, "knots": len(knots), "lives": rel is not None}
        if rel is not None:
            # parts tied across the whole pattern: for the last block coordinate p, all (v..., p) with the same inner address
            outside = [(u, v) for (u, v) in rel if addr[u][0] != addr[v][0]]
            row["tied pairs"] = len(rel)
            row["tied pairs between different P-distinctions"] = len(outside)
            row["relations between copies"] = sorted({rel[x] for x in outside})
            roots = []
            inv = {a: i for i, a in addr.items()}
            for p in range(m):
                r = inv[(0,) + (p,) * k]
                tied = [r] + [v for (a, v) in rel if a == r] + [a for (a, v) in rel if v == r]
                d = steps(n, knots, r)
                roots.append({"column": p, "tied": len(tied), "outside its copy": sum(1 for v in tied if addr[v][0] != 0),
                              "tie extent": max(d[v] for v in tied), "farthest distinction": max(d)})
            row["roots"] = roots
            if tname == "the block's knots":
                # the lemma: pinned (tied outside its copy) iff not spare; and every pinned part is one class, relation equal
                pinned = {rt["column"] for rt in roots if rt["outside its copy"] > 0}
                row["pinned columns = not spare"] = pinned == set(range(m)) - sp
                row["pinned roots reach the farthest distinction"] = all(rt["tie extent"] == rt["farthest distinction"]
                                                                         for rt in roots if rt["outside its copy"] > 0)
        out["tests"].append(row)
    return out


def lemma_on_template(m, K):
    """with T = the block's knots: every template triple equal at every distinction that is not spare; rigid iff no spare"""
    S, tm = template(m, K, triple_sets(m, K)["the block's knots"])
    sp = set(spare(m, K))
    differs = set()
    for i, j, k in tm:
        for p in range(m):
            if not (S[i][p] == S[j][p] == S[k][p]):
                differs.add(p)
    rigid = all(i == j == k for i, j, k in tm)
    return {"states": len(S), "template triples": len(tm), "spare": sorted(sp), "distinctions that differ in some template triple": sorted(differs),
            "lemma (differs iff spare)": differs == sp, "rigid": rigid, "rigid iff no spare": rigid == (not sp)}


def blocks_part():
    bl = blocks()
    rows = []
    for m, K in bl:
        r = {"block": [m, [list(e) for e in K]], "states": len(states(m, K)), "spare": spare(m, K), "templates": {}}
        for tname, T in triple_sets(m, K).items():
            S, tm = template(m, K, T)
            r["templates"][tname] = {"triples": len(tm), "empty": not tm, "rigid": bool(tm) and all(i == j == k for i, j, k in tm)}
        r["lemma"] = lemma_on_template(m, K)
        # the block's own ties
        sts = states(m, K)
        r["own tied pairs"] = sum(1 for a, b in itertools.combinations(range(m), 2) if len({s[a] ^ s[b] for s in sts}) == 1)
        rows.append(r)
    by_m = {}
    for m, _ in bl:
        by_m[m] = by_m.get(m, 0) + 1
    return {"blocks": len(bl), "by size": by_m, "rows": rows}


def gadgets_part():
    G = {"three-copy": (6, [(0, 3, 4), (3, 1, 5), (4, 5, 2)]),
         "Fano less one knot": (7, [(0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)])}
    out = {}
    for name, (g, GK) in G.items():
        rel1 = sorted({(s[0], s[1], s[2]) for s in states(g, GK)})
        rows = []
        for L in range(0, 6 if name == "three-copy" else 5):
            n, knots = 3, [(0, 1, 2)]
            for _ in range(L):
                new, nxt = [], n
                for a, b, c in knots:
                    mp = {0: a, 1: b, 2: c}
                    for v in range(3, g):
                        mp[v] = nxt
                        nxt += 1
                    new += [tuple(mp[x] for x in t) for t in GK]
                n, knots = nxt, new
            rel = tie_relation(n, knots, seed=L)
            tied0 = 1 + sum(1 for (a, b) in rel if 0 in (a, b)) if rel is not None else None
            d = steps(n, knots, 0)
            tied_set = [0] + [b for (a, b) in rel if a == 0] if rel is not None else []
            rows.append({"level": L, "distinctions": n, "knots": len(knots), "lives": rel is not None, "tied pairs": None if rel is None else len(rel),
                         "tied to terminal 0": tied0, "share": None if rel is None else tied0 / n,
                         "tie extent": max(d[v] for v in tied_set) if rel is not None else None, "farthest distinction": max(d)})
        out[name] = {"terminal relation after one level": [list(x) for x in rel1], "levels": rows}
    return out


def can_differ(m, K, p):
    """on one P-knot (three copies x, y, z), with the block's knots in every order: is there a state with x_p = 0, y_p = 1? (SAT)"""
    Q = substitute((3, [(0, 1, 2)]), (m, K), triple_sets(m, K)["the block's knots"])
    cl = [c for a, b, c3 in Q[1] for c in ([a + 1, b + 1, c3 + 1], [-(a + 1), -(b + 1), -(c3 + 1)])]
    with Glucose4(bootstrap_with=cl) as s:
        return s.solve(assumptions=[-(0 * m + p + 1), (1 * m + p + 1)])


def random_part():
    """random living blocks of 6 to 10 distinctions: (a) on one P-knot, a distinction can differ between two copies exactly when it
    is spare (SAT); (b) for some, the chain of 8 knots substituted once: pinned parts are exactly the parts that are not spare"""
    rng = random.Random(20261113)
    out = {"checked": 0, "failures": [], "by size": {}, "chain checks": 0, "chain failures": []}
    for m in (6, 7, 8, 9, 10):
        tri = list(itertools.combinations(range(m), 3))
        done = 0
        while done < 100:
            k = rng.randint(m - 1, min(len(tri), 3 * m))
            K = rng.sample(tri, k)
            if set(itertools.chain(*K)) != set(range(m)) or not connected(m, K) or not states(m, K):
                continue
            done += 1
            sp = set(spare(m, K))
            differ = {p for p in range(m) if can_differ(m, K, p)}
            out["checked"] += 1
            key = str(m)
            out["by size"].setdefault(key, {"blocks": 0, "spare counts": {}})
            out["by size"][key]["blocks"] += 1
            sc = str(len(sp))
            out["by size"][key]["spare counts"][sc] = out["by size"][key]["spare counts"].get(sc, 0) + 1
            if differ != sp:
                out["failures"].append([m, K, sorted(sp), sorted(differ)])
            if m <= 7 and done % 5 == 0:
                c = cell(((m, tuple(K)), "the block's knots"))
                t = [x for x in c["tests"] if x["pattern"] == "chain 8" and x["substitutions"] == 1][0]
                out["chain checks"] += 1
                if not (t["pinned columns = not spare"] and t["pinned roots reach the farthest distinction"]):
                    out["chain failures"].append([m, K])
    return out


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    t0 = time.time()
    if part == "blocks":
        res = blocks_part()
    elif part == "census":
        bl = blocks()
        jobs = [((m, K), t) for m, K in bl for t in ("diagonal", "the block's knots", "every distinct triple")]
        with Pool(workers) as pool:
            res = {"cells": pool.map(cell, jobs, chunksize=1)}
    elif part == "gadgets":
        res = gadgets_part()
    elif part == "random":
        res = random_part()
    res["seconds"] = round(time.time() - t0, 1)
    (HERE / f"result_{part}.json").write_text(json.dumps(res, indent=1) + "\n")
    print("wrote", part, res["seconds"], "s")
