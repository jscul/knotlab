"""Referee R1 for FAR-SIGN-20261118-001 (own code; the study's signlib.py, run.py, checks.py, readout.py and the pinned
classlib/keeplib/knotlib are not imported).

  ../../../.venv/bin/python -B referee_sign.py <part> > referee_sign_<part>.json      (from this directory)

The engine is the referee's (COPY-CLASS-R1): SEEDK with knot-local fills from MID-RULE-R1's `local_fills` (irredundant knot sets of one
to three knots, no state limit), SEED's clauses from the referee's own crossing graph and r's quadrants.  A knot set of the treated
shape is one middle knot B(p, r, q) and two end knots, exactly one end pair touching the middle pair in one distinction p; the near
knot is B(a, p, r) (pins r to p where a != p; the other orientation B(p, a, r) is counted apart), the far knot B(c, d, r).

Parts:
  S        SEEDK on fresh seeds: every bracketing of 5, 6, 7 and all 132 of 8, to n = 36; uniform random bracketings of lines of 18
           (30, to n = 40), 26 (20, to n = 48) and, past the study, 34 (12, to n = 56) and 42 (8, to n = 64).  For every crossing-making extension after the
           switch: SEED, and per treated knot set L1 (with (i), (ii)), L2, the sign, the weak sign, the near-pair sign, F1, T1, T2 (as
           L5 states it, and as one whole class of the crossed splits), L6's pattern, the states alpha and beta, the copy class
           (COPY-READ-R1's closure class), the marked picture, the origin of p (line, fill, subdivision) and the copy steps before.
  A        the ablation with knots on ANY pairs, at SEEDK's bases right after the switch: the study's range (bracketings of 5 and 6,
           first three bases, n <= 14) and past it (bracketings of 7 and 8, first eight bases, n <= 20); per pattern of which of {p, q},
           {a, p}, {c, d} already share a knot, the copy steps, the sign, F1 and T1/T2 failures.
  P7       Proposition 7 by the referee's own code: the base's states against its implied betweenness knots, both fills, every knot set
           of each fill (any pairs), and the chain cover of the crossed splits before and after (B).
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for d in ("MEET-ORDERS-20261118-001", "KNOT-SWITCH-20261118-001", "MID-RULE-20261118-001", "COPY-READ-20261118-001",
          "COPY-CLASS-20261118-001"):
    sys.path.insert(0, str(ROOT / "research" / d / "referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_switch as RSW  # noqa: E402
import referee_mid as RMID  # noqa: E402
import referee_copy as RCOPY  # noqa: E402
import referee_class as RCL  # noqa: E402

COPY_CLASS = RCL.COPY_CLASS


def bit(s, x):
    return (s >> x) & 1


def view(S, n):
    """Splits, old crossing graph, crossed splits, and the two classes when the crossed splits' crossing graph is complete bipartite
    (with whether each class is a chain of nested splits)."""
    full = (1 << n) - 1
    sp = RSW.splits(S, n)
    adj = {i: set() for i in range(len(sp))}
    for i, j in itertools.combinations(range(len(sp)), 2):
        if all(RCL.quad(sp[i], sp[j], full)):
            adj[i].add(j)
            adj[j].add(i)
    active = {v for v in adj if adj[v]}
    classes = None
    if active:
        H = nx.Graph()
        H.add_nodes_from(active)
        H.add_edges_from((i, j) for i in active for j in adj[i] if i < j)
        if nx.is_connected(H) and nx.is_bipartite(H):
            X, Y = nx.bipartite.sets(H)
            if H.number_of_edges() == len(X) * len(Y):
                classes = (frozenset(X), frozenset(Y))
    return sp, adj, active, classes


def is_chain(sp, idxs, full):
    """Are these splits pairwise compatible and can they be ordered as nested sides (one line of cuts)?"""
    idxs = list(idxs)
    for i, j in itertools.combinations(idxs, 2):
        if all(RCL.quad(sp[i], sp[j], full)):
            return False
    if len(idxs) <= 2:
        return True
    # a set of compatible splits is a chain iff no three of them have pairwise disjoint (or pairwise covering) chosen sides: test by
    # trying to orient them as a nested sequence
    sides = [(sp[i], full ^ sp[i]) for i in idxs]
    m = len(idxs)
    for start in range(m):
        for ori in (0, 1):
            used = {start}
            cur = sides[start][ori]
            ok = True
            while len(used) < m:
                nxt = [(k, o) for k in range(m) if k not in used for o in (0, 1) if (cur & sides[k][o]) == cur and sides[k][o] != cur]
                if not nxt:
                    ok = False
                    break
                # take the smallest superset
                k, o = min(nxt, key=lambda t: bin(sides[t[0]][t[1]]).count("1"))
                used.add(k)
                cur = sides[k][o]
            if ok:
                return True
    return False


def roles(ks, n):
    mids = [k for k in ks if k[1] == n]
    ends = [k for k in ks if k[1] != n]
    if len(mids) != 1 or len(ends) != 2:
        return None
    mp = {mids[0][0], mids[0][2]}
    pe = [(k[0], k[1]) for k in ends]          # end knot (u, v, n): v between u and r, pins r to v where u != v
    touch = [t for t in range(2) if mp & set(pe[t])]
    if len(touch) != 1:
        return None
    near, far = pe[touch[0]], pe[1 - touch[0]]
    common = mp & set(near)
    if len(common) != 1:
        return {"two_touch": True}
    p = common.pop()
    q = (mp - {p}).pop()
    a = near[0] if near[1] == p else near[1]
    return {"two_touch": False, "p": p, "q": q, "a": a, "c": far[0], "d": far[1], "near_pins_shared": near[1] == p}


def readings(S, n, a1, R, sp, adj, active, classes, new, gained):
    full = (1 << n) - 1
    idx = {s: i for i, s in enumerate(S)}
    p, q, a, c, d = R["p"], R["q"], R["a"], R["c"], R["d"]
    P = [s if bit(s, p) else full ^ s for s in sp]
    rin = [bit(a1, idx[P[i]]) for i in range(len(sp))]           # r on P's side
    moved = {i for i in range(len(sp)) if not rin[i]}
    sepcd = [bit(sp[i], c) != bit(sp[i], d) for i in range(len(sp))]
    out = {}
    kind = {i for i in range(len(sp)) if bit(P[i], a) and not bit(P[i], q)}
    out["L1"] = (moved == {i for i in kind if not bit(P[i], d)} and all(sepcd[i] for i in kind)
                 and all(bit(P[i], d) for i in range(len(sp)) if sepcd[i] and i not in kind)
                 and all(bit(P[i], c) for i in moved))
    pred = {(min(i, j), max(i, j)) for i in moved for j in range(len(sp)) if j not in moved and (P[j] & ~P[i]) == 0}
    out["L2"] = pred == {(min(i, j), max(i, j)) for i, j in new}
    out["sign"] = all(sepcd[i] for i in active)
    out["weak"] = all(rin[i] == bit(P[i], d) for i in active)
    out["near_none"] = not any(bit(sp[i], a) != bit(sp[i], p) for i in active)
    out["F1_premise"] = bool(gained)
    out["T1"] = not (moved - active)
    mc = moved & active
    # T2 as L5 states it: M equals the crossers of some unmoved crossed split; and as one whole class of a complete bipartite base
    out["T2"] = any(adj[m] == moved for m in active - moved)
    out["T2_class"] = classes is not None and mc in classes and not (moved - active)
    newc = any(i in active and j in active for i, j in new)
    out["alpha"] = out["sign"] and out["T1"] and out["T2"] and bool(gained)
    out["beta"] = (not out["sign"]) and not gained and newc
    pq = all(bit(sp[i], p) != bit(sp[i], q) for i in active)
    pd = {i for i in active if bit(sp[i], p) != bit(sp[i], d)}
    out["pattern"] = pq and out["near_none"] and bool(pd) and pd != active
    tr = frozenset((tuple(bit(P[i], x) for x in (q, a, c, d)), i in active) for i in range(len(sp)))
    out["traces"] = tr
    return out


def judge(S, n, a1):
    sp, adj, active, classes = view(S, n)
    _, _, new = RCL.crossing_data(S, n, a1)
    clause_a = not any(i in active and j in active for i, j in new)
    newN = defaultdict(set)
    for i, j in new:
        newN[i].add(j)
        newN[j].add(i)
    gained = sorted(u for u in newN if u not in active)
    after = {v: frozenset(adj[v] | newN.get(v, set())) for v in adj}
    seed = clause_a and all(any(after[m] == after[u] for m in active) for u in gained)
    return seed, (sp, adj, active, classes, new, gained)


def run_S(args):
    idx, T, n0, nmax, closure = args
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"referee-far-sign:{T}:{nmax}")
    origin = {x: "line" for x in range(n0)}
    copies = 0
    acc = Counter()
    marked = defaultdict(set)
    closure_v = defaultdict(set)
    while n < nmax:
        F = RMID.local_fills(S, n, G)
        crossed = RSW.crosses(S, n)
        good = []
        if crossed:
            byext = defaultdict(list)
            for a0, a1, ks in F:
                byext[(a0, a1)].append(ks)
            for (a0, a1), cert in byext.items():
                if not RCOPY.new_crossing(S, n, a1):
                    if RSW.seed_ok(S, n, RMID.apply(S, n, a0, a1)):
                        good += [(a0, a1, ks) for ks in cert]
                    continue
                seed, ctx = judge(S, n, a1)
                acc["crossing extensions"] += 1
                acc[f"seed={int(seed)}"] += 1
                acc["seed != seed_ok"] += seed != RSW.seed_ok(S, n, RMID.apply(S, n, a0, a1))
                if seed:
                    good += [(a0, a1, ks) for ks in cert]
                ext = Counter()
                for ks in cert:
                    R = roles(ks, n)
                    if R is None:
                        continue
                    if R["two_touch"]:
                        acc["knot sets: near pair = middle pair"] += 1
                        continue
                    if not R["near_pins_shared"]:
                        acc["treated shape, near knot pins r to a (other orientation)"] += 1
                        continue
                    o = readings(S, n, a1, R, *ctx)
                    acc["treated knot sets"] += 1
                    lab = "copy" if seed else "refused"
                    for key in ("L1", "L2"):
                        acc[f"{key} fails"] += not o[key]
                    for key in ("sign", "weak", "near_none", "pattern", "alpha", "beta"):
                        ext[key] |= o[key]
                        acc[f"{lab}: {key}"] += o[key]
                    acc[f"{lab}: knot sets"] += 1
                    if o["F1_premise"]:
                        acc["F1 premise"] += 1
                        acc["F1 fails"] += not o["sign"]
                    if o["sign"]:
                        acc["sign knot sets"] += 1
                        acc["T1 and T2 under the sign"] += o["T1"] and o["T2"]
                        acc["T2 as one whole class under the sign"] += o["T2_class"]
                        cls = ctx[3]
                        if cls:
                            acc[f"sign: smaller class {min(len(cls[0]), len(cls[1])) if min(len(cls[0]), len(cls[1])) < 3 else '>=3'}"] += 1
                            full = (1 << n) - 1
                            acc["sign: both classes chains"] += is_chain(ctx[0], cls[0], full) and is_chain(ctx[0], cls[1], full)
                        else:
                            acc["sign: crossed splits not complete bipartite"] += 1
                    acc[f"{lab}: neither alpha nor beta"] += not (o["alpha"] or o["beta"])
                    acc[f"{lab}: p from {origin[R['p']]}"] += 1
                    acc[f"{lab}: copies before {min(copies, 2)}"] += 1
                    if closure:
                        cc = RCOPY.canon0(ks, n, S)
                        closure_v[cc].add(seed)
                        marked[(cc, o["traces"])].add(seed)
                        if cc == COPY_CLASS:
                            acc[f"{lab}: in the copy class"] += 1
                for key in ("sign", "weak", "near_none", "pattern"):
                    acc[f"extension {key}={int(ext[key])} seed={int(seed)}"] += 1
                if not seed:
                    clause_a = not any(i in ctx[2] and j in ctx[2] for i, j in ctx[4])
                    treated = any((R := roles(ks, n)) and not R["two_touch"] and R["near_pins_shared"] for ks in cert)
                    acc[f"refused extension: clause (a) {'holds' if clause_a else 'fails'}, treated knot set {'yes' if treated else 'none'}"] += 1
                acc[f"extension alpha&beta both"] += ext["alpha"] and ext["beta"]
        else:
            good = F
        if good:
            a0, a1, ks = rng.choice(good)
            S2 = RMID.apply(S, n, a0, a1)
            if crossed and RCOPY.new_crossing(S, n, a1):
                copies += 1
            origin[n] = "fill"
        else:
            subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            if not subs:
                break
            u, v = rng.choice(subs)
            ks = ((u, n, v),)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, ks[0])))
            origin[n] = "subdivision"
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
    return dict(acc), {repr(k): sorted(v) for k, v in closure_v.items()}, {repr(k): sorted(v) for k, v in marked.items()}


def starts_S():
    J = []
    for n0 in (5, 6, 7, 8):
        J += [(tuple(T), n0, 36) for T in RM.bracketings(0, n0 - 1)]
    rng = random.Random("referee-far-sign-lines")
    for m, cnt, nmax in ((18, 30, 40), (26, 20, 48), (34, 12, 56), (42, 8, 64)):
        J += [(RM.random_bracketing(0, m - 1, rng), m, nmax) for _ in range(cnt)]
    return [(i,) + j + (True,) for i, j in enumerate(J)]


def part_S(workers=16):
    J = starts_S()
    J.sort(key=lambda j: -j[2])
    tot = Counter()
    by = defaultdict(Counter)
    cv, mv = defaultdict(set), defaultdict(set)
    with Pool(workers) as P:
        for j, (acc, c, m) in zip(J, P.imap(run_S, J, chunksize=1)):
            tot.update(acc)
            by[f"line of {j[2]}" if j[2] >= 18 else "bracketings of 5 to 8"].update(acc)
            for k, v in c.items():
                cv[k] |= set(v)
            for k, v in m.items():
                mv[k] |= set(v)
    out = {"starts": len(J), "all": dict(sorted(tot.items()))}
    out["closure pictures; with both verdicts"] = (len(cv), sum(1 for v in cv.values() if len(v) > 1))
    out["marked pictures; with both verdicts"] = (len(mv), sum(1 for v in mv.values() if len(v) > 1))
    for k in sorted(by):
        out[k] = {x: by[k][x] for x in ("crossing extensions", "seed=1", "extension sign=1 seed=0", "extension sign=0 seed=1",
                                        "F1 fails", "treated knot sets", "L1 fails", "L2 fails")}
    return out


# ---------------- the ablation: knots on any pairs ----------------

def run_A(args):
    idx, T, n0, steps, nlim = args
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"referee-far-sign-ablation:{T}")
    acc = defaultdict(Counter)
    seen = 0
    while n <= nlim:
        F = RMID.local_fills(S, n, G)
        crossed = RSW.crosses(S, n)
        if crossed:
            seen += 1
            if seen > steps:
                break
            allp = frozenset(itertools.combinations(range(n), 2))
            byext = defaultdict(list)
            for a0, a1, ks in RMID.local_fills(S, n, allp):
                byext[(a0, a1)].append(ks)
            for (a0, a1), cert in byext.items():
                if not RCOPY.new_crossing(S, n, a1):
                    continue
                seed, ctx = judge(S, n, a1)
                for ks in cert:
                    R = roles(ks, n)
                    if R is None or R["two_touch"] or not R["near_pins_shared"]:
                        continue
                    o = readings(S, n, a1, R, *ctx)
                    co = lambda x, y: (min(x, y), max(x, y)) in G
                    pat = f"pq={int(co(R['p'], R['q']))} ap={int(co(R['a'], R['p']))} cd={int(co(R['c'], R['d']))}"
                    A = acc[pat]
                    A["knot sets"] += 1
                    A["copy"] += seed
                    A["sign"] += o["sign"]
                    A["sign, refused"] += o["sign"] and not seed
                    A["copy, no sign"] += seed and not o["sign"]
                    A["F1 fails"] += o["F1_premise"] and not o["sign"]
                    A["T1/T2 fail under the sign"] += o["sign"] and not (o["T1"] and o["T2"])
                    A["L1 or L2 fails"] += not (o["L1"] and o["L2"])
            good = []
            byk = defaultdict(list)
            for a0, a1, ks in F:
                byk[(a0, a1)].append(ks)
            for (a0, a1), cert in byk.items():
                if RSW.seed_ok(S, n, RMID.apply(S, n, a0, a1)):
                    good += [(a0, a1, ks) for ks in cert]
        else:
            good = F
        if good:
            a0, a1, ks = rng.choice(good)
            S2 = RMID.apply(S, n, a0, a1)
        else:
            subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            if not subs:
                break
            u, v = rng.choice(subs)
            ks = ((u, n, v),)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, ks[0])))
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
    return {k: dict(v) for k, v in acc.items()}


def part_A(workers=16):
    J = []
    for n0 in (5, 6):
        J += [(tuple(T), n0, 3, 14, "study's range") for T in RM.bracketings(0, n0 - 1)]
    for n0 in (7, 8):
        J += [(tuple(T), n0, 8, 20, "past it") for T in RM.bracketings(0, n0 - 1)]
    J = [(i,) + j[:4] for i, j in enumerate(J)], [j[4] for j in J]
    jobs, labels = J
    out = {}
    with Pool(workers) as P:
        res = P.map(run_A, jobs, chunksize=1)
    for lab in ("study's range", "past it"):
        tot = defaultdict(Counter)
        for r, l in zip(res, labels):
            if l == lab:
                for k, v in r.items():
                    tot[k].update(v)
        out[lab] = {k: dict(tot[k]) for k in sorted(tot)}
    return out


# ---------------- Proposition 7 ----------------

def part_P7():
    n = 7
    sides = {"X": {3, 4, 5}, "0": {0, 3}, "2": {2, 5}, "tau": {6}}
    mask = lambda A: sum(1 << x for x in A)
    full = (1 << n) - 1
    S = tuple(sorted({0, full} | {mask(A) for A in sides.values()} | {full ^ mask(A) for A in sides.values()}))
    implied = [(x, y, z) for x, z in itertools.combinations(range(n), 2) for y in range(n) if y not in (x, z)
               and all(RSW.ok(s, (x, y, z)) for s in S)]
    allowed = tuple(s for s in range(1 << n) if all(RSW.ok(s, k) for k in implied))
    out = {"states": len(S), "implied knots": len(implied), "states = those the implied knots allow": allowed == S}
    sp, adj, active, classes = view(S, n)
    name = {mask(A) if mask(A) in sp else full ^ mask(A): k for k, A in sides.items()}
    out["crossings"] = sorted((name[sp[i]], name[sp[j]]) for i in adj for j in adj[i] if i < j)
    allp = frozenset(itertools.combinations(range(n), 2))
    fills = RMID.local_fills(S, n, allp)
    for label, ks0 in (("A", ((3, 7, 6), (1, 6, 7), (5, 0, 7))), ("B", ((3, 7, 6), (0, 6, 7), (0, 4, 7)))):
        # the fill these knots make (r = 7)
        st = [s | (v << n) for s in S for v in (0, 1) if all(RSW.ok(s | (v << n), k) for k in ks0)]
        a1 = sum(1 << i for i, s in enumerate(S) if (s | (1 << n)) in st)
        fixed = len(st) == len(S)
        seed, ctx = judge(S, n, a1)
        R = roles(ks0, n)
        o = readings(S, n, a1, R, *ctx)
        P = [s if bit(s, R["p"]) else full ^ s for s in ctx[0]]
        idx = {s: i for i, s in enumerate(S)}
        moved = sorted(name[ctx[0][i]] for i in range(len(ctx[0])) if not bit(a1, idx[P[i]]))
        same = [ks for a0, a1b, ks in fills if a1b == a1]
        shaped = [(ks, readings(S, n, a1, roles(ks, n), *ctx)["sign"]) for ks in same
                  if roles(ks, n) and not roles(ks, n)["two_touch"] and roles(ks, n)["near_pins_shared"]]
        rec = {"r fixed on every state": fixed, "SEED": seed, "sign": o["sign"], "moved": moved, "T1": o["T1"], "T2": o["T2"],
               "knot sets of this fill (any pairs, irredundant, <= 3 knots)": len(same),
               "treated-shape knot sets; with the sign": (len(shaped), sum(1 for _, s in shaped if s))}
        if label == "B":
            S2 = tuple(sorted(st))
            sp2, adj2, act2, cls2 = view(S2, n + 1)
            full2 = (1 << (n + 1)) - 1
            # least chain cover of the splits after the fill (an axis of a lattice embedding is a chain of splits)
            best = None
            idxs = list(range(len(sp2)))
            for k in range(1, len(idxs) + 1):
                for assign in itertools.product(range(k), repeat=len(idxs)):
                    groups = [[i for i in idxs if assign[i] == g] for g in range(k)]
                    if all(is_chain(sp2, g, full2) for g in groups if g):
                        best = k
                        break
                if best:
                    break
            rec["least chain cover of the splits after (lattice dimension)"] = best
            # and before
            idxs0 = list(range(len(sp)))
            for k in range(1, len(idxs0) + 1):
                if any(all(is_chain(sp, [i for i in idxs0 if assign[i] == g], full) for g in range(k))
                       for assign in itertools.product(range(k), repeat=len(idxs0))):
                    rec["least chain cover before"] = k
                    break
            rec["crossed splits complete bipartite after (two classes in L5's sense)"] = cls2 is not None
        out[label] = rec
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"S": part_S, "A": part_A, "P7": part_P7}[part](), indent=1, default=str))
