"""Referee R1 for MID-RULE-20261118-001 (own code; the study's midlib.py, run.py and the pinned knotlib/picklib/melib are not
imported).

  ../../../.venv/bin/python -B referee_mid.py <part> > referee_mid_<part>.json      (from this directory)

A knot on the new distinction r = n and an old pair is a middle knot B(u, r, v) (pins r to u where u = v) or an end knot B(u, v, r)
(pins r to v where u != v).  A fill is a set of at most three such knots whose allowed masks intersect in exactly one value of r per
old state (no state added), not a copy.  A pair of old splits comes to cross when r lands in its empty quadrant.

Parts:
  e1        random bases of betweenness knots on 5 to 8 distinctions, 3 to 7 knots (not grown, the referee's seed): every fill
            with every certificate of one to three knots; does any fill with a certificate of at most one end knot make a new
            crossing, change any relation of two splits (so k), or change lambda?  Also every certificate of a crossing-making fill: how many end knots.
  k         MID2K and ONEK (knot-local: the referee's own enumeration of irredundant fills on co-knotted pairs, in Python integers)
            from every bracketing of 5, 6, 7 and every
            third of 8 to n = 60, and every third of those to n = 75: fills per run, k and lambda after the first fill, full grids.
  e5        MID2F (free) from the line of 5, once for each of its ten possible first fills, to n = 14: full grids, against E5
            (a full grid exactly when the first fill spans the line).
"""
import itertools
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-SWITCH-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/COUNT-BALLS-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_cap as KC  # noqa: E402
import referee_switch as RSW  # noqa: E402
import referee_census as RCN  # noqa: E402

pc = int.bit_count


def cols(S, n):
    full = (1 << len(S)) - 1
    O = [sum(1 << i for i, s in enumerate(S) if (s >> u) & 1) for u in range(n)]
    return O, [full ^ o for o in O], full


def knots_on(S, n, pairs):
    """Every knot on r = n and an old pair: (kind, knot, pin0, pin1), pins as masks over the states."""
    O, Z, full = cols(S, n)
    out = []
    for u, v in pairs:
        ne = (O[u] & Z[v]) | (Z[u] & O[v])
        out.append(("mid", (u, n, v), Z[u] & Z[v], O[u] & O[v]))
        out.append(("end", (u, v, n), ne & Z[v], ne & O[v]))
        out.append(("end", (v, u, n), ne & Z[u], ne & O[u]))
    return out


def fills_with_certificates(S, n, pairs):
    """{(a0, a1): [(end knots, middle knots) of each certificate]} over every certificate of one to three knots (a certificate:
    consistent pins covering every old state; redundant ones included, which changes no minimum)."""
    O, Z, full = cols(S, n)
    K = knots_on(S, n, pairs)
    K = [k for k in K if k[2] | k[3]]
    cols_set = set(O)
    out = {}
    for size in (1, 2, 3):
        for c in itertools.combinations(range(len(K)), size):
            p0 = p1 = 0
            ok = True
            for i in c:
                q0, q1 = K[i][2], K[i][3]
                if (q0 & p1) or (q1 & p0):
                    ok = False
                    break
                p0 |= q0
                p1 |= q1
            if not ok or (p0 | p1) != full or p1 in cols_set:
                continue
            e = sum(1 for i in c if K[i][0] == "end")
            out.setdefault((full ^ p1, p1), []).append((e, size - e))
    return out


def apply(S, n, a0, a1):
    return tuple(sorted([s for i, s in enumerate(S) if (a0 >> i) & 1] + [s | (1 << n) for i, s in enumerate(S) if (a1 >> i) & 1]))


def relations(S, n):
    """For every pair of splits (by their state), the set of occupied quadrants."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    rel = {}
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        rel[(i, j)] = tuple(bool(x) for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b)))
    return sp, rel


def kl(S, n):
    return RCN.chromatic(sorted({min(s, ((1 << n) - 1) ^ s) for s in S if s not in (0, (1 << n) - 1)}), (1 << n) - 1), \
        KC.measure(list(S), n)["lam"]


def e1_case(seed):
    rng = random.Random(f"e1-{seed}")
    while True:
        n = rng.randint(5, 8)
        kn = [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(3, 7))]
        S = tuple(s for s in range(1 << n) if all(RSW.ok(s, k) for k in kn))
        if RSW.copy_free(S, n):
            break
    pairs = list(itertools.combinations(range(n), 2))
    F = fills_with_certificates(S, n, pairs)
    sp, rel0 = relations(S, n)
    l0 = KC.measure(list(S), n)["lam"]                    # k is read through the relations (crossings), not recoloured
    res = {"n": n, "fills": len(F), "low_end_fills": 0, "low_end_violations": 0, "crossing_fills": 0,
           "crossing_fill_min_ends": None}
    mins = []
    for (a0, a1), ends in F.items():
        S2 = apply(S, n, a0, a1)
        full2 = (1 << (n + 1)) - 1
        # old splits extended: the same index order, as each state keeps its place
        changed = False
        new_cross = False
        for (i, j), q in rel0.items():
            a, b = sp[i], sp[j]
            # the extended states: a's state gets r's value there
            idx_a, idx_b = S.index(a), S.index(b)
            ra, rb = (a1 >> idx_a) & 1, (a1 >> idx_b) & 1
            A, Bb = a | (ra << n), b | (rb << n)
            q2 = tuple(bool(x) for x in (A & Bb, A & (full2 ^ Bb), (full2 ^ A) & Bb, (full2 ^ A) & (full2 ^ Bb)))
            if q2 != q:
                changed = True
                if all(q2) and not all(q):
                    new_cross = True
        least = min(e for e, _ in ends)
        if new_cross:
            res["crossing_fills"] += 1
            mins.append(least)
        if least <= 1:
            res["low_end_fills"] += 1
            l2 = KC.measure(list(S2), n + 1)["lam"]
            if changed or new_cross or l2 != l0:
                res["low_end_violations"] += 1
    res["crossing_fill_min_ends"] = min(mins) if mins else None
    return res


def part_e1(count=400, workers=16):
    with Pool(workers) as P:
        rows = P.map(e1_case, range(count), chunksize=4)
    return {"bases": len(rows), "fills": sum(r["fills"] for r in rows), "fills_with_a_low_end_certificate": sum(r["low_end_fills"] for r in rows),
            "low_end_fills_changing_a_relation_or_k_or_lambda": sum(r["low_end_violations"] for r in rows),
            "crossing_fills": sum(r["crossing_fills"] for r in rows),
            "least_end_knots_in_any_certificate_of_a_crossing_fill": min((r["crossing_fill_min_ends"] for r in rows
                                                                          if r["crossing_fill_min_ends"] is not None), default=None)}


def mid_test(rule, ks, n):
    mids = sum(1 for k in ks if k[1] == n)
    return mids >= 2 if rule == "MID2" else (len(ks) - mids) <= 1


def local_fills(S, n, G):
    """Every irredundant knot set of one to three knots on r = n and co-knotted pairs (G) that pins r on every state, not a copy:
    [(a0, a1, knots)].  Python integers (any number of states).  Every such set holds a middle knot (only middle knots pin the
    all-equal states), so each is found from one of its middle knots."""
    O, Z, full = cols(S, n)
    K = [k for k in knots_on(S, n, sorted(G)) if k[2] | k[3]]
    colset = set(O)
    out = {}
    for i, (kind, kn, p0, p1) in enumerate(K):
        if kind != "mid":
            continue
        rest = full ^ (p0 | p1)
        if rest == 0:
            if p1 not in colset:
                out[(i,)] = (full ^ p1, p1, (kn,))
            continue
        cons = [j for j, k in enumerate(K) if j != i and not (k[2] & p1) and not (k[3] & p0) and (k[2] | k[3]) & rest]
        for j in cons:
            q0, q1 = p0 | K[j][2], p1 | K[j][3]
            if (q0 | q1) == full and not (K[j][2] & p1) and not (K[j][3] & p0):
                key = tuple(sorted((i, j)))
                if q1 not in colset and key not in out:
                    out[key] = (full ^ q1, q1, (kn, K[j][1]))
        for j, l in itertools.combinations(cons, 2):
            a, b = K[j], K[l]
            if (a[2] & b[3]) or (a[3] & b[2]):
                continue
            q0, q1 = p0 | a[2] | b[2], p1 | a[3] | b[3]
            if (q0 | q1) != full or q1 in colset:
                continue
            # irredundant: no two of the three already pin everything
            if ((p0 | p1 | a[2] | a[3]) == full) or ((p0 | p1 | b[2] | b[3]) == full) or ((a[2] | a[3] | b[2] | b[3]) == full):
                continue
            key = tuple(sorted((i, j, l)))
            if key not in out:
                out[key] = (full ^ q1, q1, (kn, a[1], b[1]))
    return list(out.values())


def k_run(args):
    rule, T, nmax = args
    n0 = 1 + max(max(k) for k in T)
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"{rule}:{T}")
    fills = 0
    after = []
    full = 0
    while n < nmax:
        F = local_fills(S, n, G)
        crossed = RSW.crosses(S, n)
        good = F if not crossed else [f for f in F if mid_test(rule, f[2], n)]
        if good:
            a0, a1, ks = rng.choice(good)
            S2 = apply(S, n, a0, a1)
            fills += 1
        else:
            subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            if not subs:
                break
            u, v = rng.choice(subs)
            k = (u, n, v)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, k)))
            ks = (k,)
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
        if fills:
            after.append(kl(S, n))
            full += RSW.full_grid(S, n)
    return {"rule": rule, "nmax": nmax, "n0": n0, "n_end": n, "fills": fills, "two_orders_after_first_fill": all(x == (2, 2) for x in after),
            "full_grids": full}


def part_k(workers=16):
    Ts = []
    for n0 in (5, 6, 7):
        Ts += [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    Ts += [tuple(T) for T in RM.bracketings(0, 7)][::3]
    jobs = [(r, T, 60) for r in ("MID2", "ONE") for T in Ts] + [(r, T, 75) for r in ("MID2", "ONE") for T in Ts[::3]]
    with Pool(workers) as P:
        rows = P.map(k_run, jobs, chunksize=1)
    out = {}
    for r in ("MID2", "ONE"):
        for nm in (60, 75):
            R = [x for x in rows if x["rule"] == r and x["nmax"] == nm]
            if not R:
                continue
            out[f"{r} to n = {nm}"] = {"runs": len(R), "fills_per_run": dict(sorted({str(f): sum(1 for x in R if x["fills"] == f)
                                                                                   for f in {x["fills"] for x in R}}.items())),
                                       "two_orders_after_first_fill": sum(x["two_orders_after_first_fill"] for x in R),
                                       "runs_with_a_full_grid": sum(x["full_grids"] > 0 for x in R)}
    return out


def e5_run(first):
    """MID2F from the line of 5 with the given first fill (a triple (a, c, b)), to n = 14."""
    n0 = 5
    S, n = RM.line_states(n0), n0
    a, c, b = first
    k = [(a, n, b), (c, a, n), (c, b, n)]
    S = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if all(RSW.ok(x, kk) for kk in k)))
    n += 1
    rng = random.Random(f"e5-{first}")
    fulls = []
    while n < 14:
        pairs = list(itertools.combinations(range(n), 2))
        F = fills_with_certificates(S, n, pairs)
        good2 = sorted(f for f, certs in F.items() if any(m >= 2 for _, m in certs))      # MID2: two or more middle knots
        if good2:
            q0, q1 = rng.choice(good2)
            S = apply(S, n, q0, q1)
        else:
            subs = [(u, v) for u, v in pairs if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            u, v = rng.choice(subs)
            kk = (u, n, v)
            S = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, kk)))
        n += 1
        fulls.append(RSW.full_grid(S, n))
    return {"first_fill": list(first), "spans": first[0] == 0 and first[2] == n0 - 1,
            "full_grids": sum(fulls), "lam_end": kl(S, n)[1]}


def part_e5(workers=10):
    firsts = [(a, c, b) for a, b in itertools.combinations(range(5), 2) for c in range(a + 1, b)]
    with Pool(workers) as P:
        rows = P.map(e5_run, firsts, chunksize=1)
    return {"rows": rows, "agrees_with_E5": all((r["full_grids"] > 0) == r["spans"] for r in rows)}


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"e1": part_e1, "k": part_k, "e5": part_e5}[part]
    print(json.dumps(f(), indent=1, default=str))
