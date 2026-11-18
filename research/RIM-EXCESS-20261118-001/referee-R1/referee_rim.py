"""Referee R1 for RIM-EXCESS-20261118-001 (own code; the study's polylib.py, job.py and the pinned weavelib are not imported, except
where marked: the study's polylib as a cross-check of its own search, and its weavelib only to regenerate its random patches exactly).

  ../../../.venv/bin/python -B referee_rim.py <part> > referee_rim_<part>.json      (from this directory)

Discs, states and brute-force bonds from the referee's DOUBLE-MEET-R1 code; walk weights D from its WEAVE-HEIGHTS-R1 code.  The
referee's own polygon search (`search`) follows ticket A's statement (levels e = 0, 1, ...; members within detour 3e; cyclic
sequences through x and z of s + 2 + e members with D-sum 3(s + e), each member on a D-geodesic between its neighbours), with three
prunings that are valid for bonds: the lower bound on the rest of the walk; every contiguous run of the sequence so far, closed up,
must not be tight (it would be a tight proper sub-collection); and removing two consecutive members lowers the D-sum by at most 3
(Lemma P's remark).  A completed sequence is a bond when no proper sub-collection of three or more members has a cyclic order of
D-sum at most 3(k - 2) (the referee's numpy Held-Karp).

Parts:
  lemmaP     every bond of every disc of ten knots (one size past the study's nine), brute force from the states: least cyclic D-sum
             = 3(m - 2), and every tight cyclic order (all enumerated) geodesic at every member.
  validate   every disc of ten and eleven knots, brute force on every pair: the referee's search on every pair with an excess or no
             bond, every lone pair of opposite classes facing each other, and 3,000 other pairs; the study's own search on the same
             excess and unbonded pairs (its R2 compared only discs to nine knots, where no bonded pair has an excess).
  k13        every disc of thirteen knots (one size past the study's twelve): the referee's search on every lone pair of opposite
             classes facing each other, to the largest excess the disc allows (|V| - 2 - s, so that "none" certifies no bond), the
             largest excess; and 3,000 random thirteen-knot discs by brute force on every pair (where
             the excess and the unbonded pairs lie).
  random     the study's 160 random patches of 20 to 40 knots, regenerated with its generator and seeds: every facing pair with the
             referee's search, emax 12, 300 seconds each.
  finish     the pairs part random left unsettled, searched to the largest excess the patch allows (|V| - 2 - s), 540 seconds each:
             exhausting that level certifies that no bond holds the pair.
  k14        every disc of fourteen knots (two sizes past): the same search on every lone opposite facing pair.
  validate_big  3,000 random discs each of twelve and thirteen knots: brute force on every pair, and the referee's search on every pair
             with an excess or no bond.
"""
import heapq
import itertools
import json
import math
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/DOUBLE-MEET-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/WEAVE-HEIGHTS-20261118-001/referee-R1"))
import referee_double as RD  # noqa: E402
import referee_heights as RH  # noqa: E402


def patch(T):
    T = sorted(T)
    V = sorted({v for t in T for v in RD.verts(t)})
    E = {tuple(sorted(e)) for t in T for e in itertools.combinations(RD.verts(t), 2)}
    G = nx.Graph()
    G.add_edges_from(E)
    sp = dict(nx.all_pairs_shortest_path_length(G))
    D = RH.walk_weights(V, E)
    deg = Counter(v for t in T for v in RD.verts(t))
    lone = {v: next(t for t in T if v in RD.verts(t)) for v in V if deg[v] == 1}
    return T, V, D, sp, lone


def facing_pair(lone, x, z):
    return (x in lone and z in lone and lone[x][0] != lone[z][0] and RD.facing(x, lone[x], z) and RD.facing(z, lone[z], x))


def tight_proper(pts, D):
    """Is there a sub-collection of pts, of k >= 3 members and not all of pts, with a cyclic order of D-sum <= 3(k - 2)?"""
    n = len(pts)
    Wm = np.array([[D[pts[a]][pts[b]] for b in range(n)] for a in range(n)], dtype=np.float64)
    dp = np.full((1 << n, n), np.inf)
    for s in range(n):
        dp[1 << s, s] = 0
    full = (1 << n) - 1
    for mask in range(1, 1 << n):
        row = dp[mask]
        if not np.isfinite(row).any():
            continue
        s = (mask & -mask).bit_length() - 1
        k = bin(mask).count("1")
        if k >= 3 and mask != full and (row + Wm[:, s]).min() <= 3 * (k - 2):
            return True
        cand = (row[:, None] + Wm).min(axis=0)
        for q in range(s + 1, n):
            if not (mask >> q) & 1 and cand[q] < dp[mask | (1 << q), q]:
                dp[mask | (1 << q), q] = cand[q]
    return False


def search(P_, x, z, emax=6, time_limit=None):
    """Least bond size - 1 holding x, z: (b or None, s, status) with status 'exact', 'none to emax' or 'timeout at e'."""
    T, V, D, sp, lone = P_
    s = sp[x][z]
    t0 = time.time()
    for e in range(emax + 1):
        m = s + 2 + e
        budget = 3 * (s + e)
        cand = [p for p in V if p not in (x, z) and min(D[x][p] + D[p][z] - D[x][z], D[z][p] + D[p][x] - D[z][x]) <= 3 * e]
        seen = set()
        found = []
        timed = [False]

        def dfs(seq, pre, has_z):
            # pre[i] = D-sum of seq[0..i] along the sequence
            if found or timed[0]:
                return
            if time_limit and time.time() - t0 > time_limit:
                timed[0] = True
                return
            last = seq[-1]
            k = len(seq)
            if k == m:
                if not has_z or pre[-1] + D[last][x] != budget:
                    return
                if D[seq[-2]][last] + D[last][x] != D[seq[-2]][x] or D[last][x] + D[x][seq[1]] != D[last][seq[1]]:
                    return
                key = frozenset(seq)
                if key in seen:
                    return
                seen.add(key)
                if not tight_proper(sorted(key), D):
                    found.append(key)
                return
            pool = ([z] if not has_z else []) + [p for p in cand if p not in seq]
            for q in pool:
                w2 = pre[-1] + D[last][q]
                rest = (D[q][z] + D[z][x]) if (not has_z and q != z) else D[q][x]
                if w2 + rest > budget:
                    continue
                if k >= 2 and D[seq[-2]][last] + D[last][q] != D[seq[-2]][q]:
                    continue
                if k >= 3 and D[seq[-3]][seq[-2]] + D[seq[-2]][last] + D[last][q] - D[seq[-3]][q] > 3:
                    continue
                # every contiguous run ending at q, closed up, must not be tight (it is a proper sub-collection)
                pre2 = pre + [w2]
                bad = False
                for i in range(0, k - 1):
                    run = k + 1 - i                       # members seq[i..k-1] and q
                    if run >= 3 and run < m and pre2[-1] - pre2[i] + D[q][seq[i]] <= 3 * (run - 2):
                        bad = True
                        break
                if bad:
                    continue
                dfs(seq + [q], pre2, has_z or q == z)

        dfs([x], [0], False)
        if found:
            return m - 1, s, "exact"
        if timed[0]:
            return None, s, f"timeout at e = {e}"
    return None, s, f"none to {emax}"


# ---------------- brute force ----------------

def bond_masks(n, st):
    free = np.zeros(1 << n, dtype=bool)
    for msk in range(1 << n):
        code = np.zeros(len(st), dtype=np.int64)
        k = 0
        for v in range(n):
            if (msk >> v) & 1:
                code |= ((st >> v) & 1) << k
                k += 1
        free[msk] = bool(np.all(np.bincount(code, minlength=1 << k)))
    return [msk for msk in range(1, 1 << n) if not free[msk] and all(free[msk & ~(1 << i)] for i in range(n) if (msk >> i) & 1)]


def brute(P_):
    T, V, D, sp, lone = P_
    ix = {v: i for i, v in enumerate(V)}
    n = len(V)
    st = RD.states(n, [tuple(ix[w] for w in RD.verts(t)) for t in T])
    bonds = bond_masks(n, st)
    b = {}
    for msk in bonds:
        vs = [V[i] for i in range(n) if (msk >> i) & 1]
        for x, z in itertools.combinations(vs, 2):
            b[(x, z)] = min(b.get((x, z), math.inf), len(vs) - 1)
    return bonds, b


# ---------------- parts ----------------

def lemmaP_disc(T):
    P_ = patch(T)
    T, V, D, sp, lone = P_
    bonds, _ = brute(P_)
    r = Counter(discs=1)
    for msk in bonds:
        pts = [V[i] for i in range(len(V)) if (msk >> i) & 1]
        m = len(pts)
        r["bonds"] += 1
        # every cyclic order with D-sum <= 3(m - 2), enumerated from pts[0]
        orders = []

        def go(seq, w):
            if w + (D[seq[-1]][pts[0]] if len(seq) == m else 0) > 3 * (m - 2):
                return
            if len(seq) == m:
                orders.append((seq, w + D[seq[-1]][pts[0]]))
                return
            for q in pts:
                if q not in seq and w + D[seq[-1]][q] + D[q][pts[0]] <= 3 * (m - 2):
                    go(seq + [q], w + D[seq[-1]][q])
        go([pts[0]], 0)
        r["tight orders"] += len(orders)
        r["no tight order"] += not orders
        for seq, w in orders:
            r["tight order D-sum != 3(m - 2)"] += w != 3 * (m - 2)
            r["tight order not geodesic"] += any(D[seq[i - 1]][seq[i]] + D[seq[i]][seq[(i + 1) % m]] != D[seq[i - 1]][seq[(i + 1) % m]]
                                                 for i in range(m))
    return dict(r)


def part_lemmaP(workers=16):
    by = RD.discs_upto(10)
    acc = Counter()
    with Pool(workers) as P:
        for r in P.imap_unordered(lemmaP_disc, by[10], chunksize=8):
            acc.update(r)
    return {"discs of ten knots": dict(acc)}


def validate_disc(args):
    T, sample_seed = args
    P_ = patch(T)
    T, V, D, sp, lone = P_
    _, b = brute(P_)
    rng = random.Random(sample_seed)
    r = Counter(discs=1)
    rows = []
    for x, z in itertools.combinations(V, 2):
        true = b.get((x, z), math.inf)
        s = sp[x][z]
        e = None if true == math.inf else true - s - 1
        fac = facing_pair(lone, x, z)
        r["pairs"] += 1
        r["below steps + 1"] += e is not None and e < 0
        interesting = e is None or e >= 1 or fac
        if not interesting and rng.random() > 0.004:
            continue
        got, s2, status = search(P_, x, z, emax=6)
        r["searched"] += 1
        r[f"searched e={'none' if e is None else e}"] += 1
        ok = (got is None and e is None and status == "none to 6") or (got == true)
        r["search mismatch"] += not ok
        if e is None or e >= 1:
            rows.append((sorted(T), x, z, e))
            r[f"excess or unbonded: lone opposite facing={int(fac)}"] += 1
    return dict(r), rows


def study_search_check(row):
    """The study's own search (its polylib, imported read only) on one excess or unbonded pair."""
    T, x, z, e = row
    sys.path.insert(0, str(ROOT / "experiments/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess"))
    import polylib as SP  # noqa: E402
    got, s, to = SP.pair_b_polygons(frozenset(tuple(t) for t in T), tuple(x), tuple(z), emax=6, time_limit=60)
    ok = (not to) and ((got is None and e is None) or (got is not None and e is not None and got - s - 1 == e))
    return {"compared": 1, "study search mismatch": int(not ok), "study search timeout": int(to)}


def part_validate(workers=16):
    by = RD.discs_upto(11)
    out = {}
    for k in (10, 11):
        acc = Counter()
        rows = []
        with Pool(workers) as P:
            for r, rw in P.imap_unordered(validate_disc, [(T, f"v{k}:{i}") for i, T in enumerate(sorted(by[k], key=sorted))], chunksize=8):
                acc.update(r)
                rows += rw
            sacc = Counter()
            for r in P.imap_unordered(study_search_check, rows, chunksize=4):
                sacc.update(r)
        out[f"every disc of {k} knots"] = dict(sorted(acc.items()))
        out[f"every disc of {k} knots: the study's search on the excess and unbonded pairs"] = dict(sacc)
    return out


def k13_disc(T):
    P_ = patch(T)
    T, V, D, sp, lone = P_
    r = Counter(discs=1)
    for x, z in itertools.combinations(sorted(lone), 2):
        if not facing_pair(lone, x, z):
            continue
        top = len(V) - 2 - sp[x][z]                     # no bond has more than |V| members
        got, s, status = search(P_, x, z, emax=top, time_limit=120)
        r["facing pairs"] += 1
        r["excess " + str(got - s - 1) if got is not None else
          ("unbonded (certified: no bond of any size)" if status == f"none to {top}" else status)] += 1
    return dict(r)


def k13_brute(T):
    P_ = patch(T)
    T, V, D, sp, lone = P_
    _, b = brute(P_)
    r = Counter(discs=1)
    for x, z in itertools.combinations(V, 2):
        true = b.get((x, z), math.inf)
        e = None if true == math.inf else true - sp[x][z] - 1
        r["pairs"] += 1
        if e is None or e >= 1:
            r[f"{'unbonded' if e is None else 'excess ' + str(e)}: lone opposite facing={int(facing_pair(lone, x, z))}"] += 1
        r["below steps + 1"] += e is not None and e < 0
    return dict(r)


def part_k13(workers=16):
    by = RD.discs_upto(13)
    out = {"discs of 13 knots": len(by[13])}
    with Pool(workers) as P:
        acc = Counter()
        for r in P.imap_unordered(k13_disc, by[13], chunksize=16):
            acc.update(r)
        out["every disc of 13 knots, facing pairs by the referee's search"] = dict(sorted(acc.items()))
        rng = random.Random("referee-rim-13")
        sample = rng.sample(sorted(by[13], key=sorted), 3000)
        acc = Counter()
        for r in P.imap_unordered(k13_brute, sample, chunksize=8):
            acc.update(r)
        out["3,000 random discs of 13 knots, every pair by brute force"] = dict(sorted(acc.items()))
    return out


def validate_big(args):
    """Brute force on every pair of one disc, and the referee's search on every pair with an excess or no bond."""
    T = args
    P_ = patch(T)
    T, V, D, sp, lone = P_
    _, b = brute(P_)
    r = Counter(discs=1)
    for x, z in itertools.combinations(V, 2):
        true = b.get((x, z), math.inf)
        e = None if true == math.inf else true - sp[x][z] - 1
        if e is None or e >= 1:
            got, s, status = search(P_, x, z, emax=6, time_limit=120)
            r[f"searched {'unbonded' if e is None else 'excess ' + str(e)}"] += 1
            r["search mismatch"] += not ((got is None and e is None and status == "none to 6") or got == true)
            r[f"lone opposite facing={int(facing_pair(lone, x, z))}"] += 1
    return dict(r)


def part_validate_big(workers=16):
    rng = random.Random("referee-rim-validate-big")
    out = {}
    with Pool(workers) as P:
        for k in (12, 13):
            Ts = [RD.random_disc(k, rng) for _ in range(3000)]
            acc = Counter()
            for r in P.imap_unordered(validate_big, Ts, chunksize=8):
                acc.update(r)
            out[f"3,000 random discs of {k} knots"] = dict(sorted(acc.items()))
    return out


def finish_pair(args):
    seed, k, T, x, z = args
    P_ = patch(T)
    _, V, D, sp, lone = P_
    top = len(V) - 2 - sp[x][z]
    t0 = time.time()
    got, s, status = search(P_, x, z, emax=top, time_limit=540)
    return {"seed": seed, "patch": k, "knots": len(T), "distinctions": len(V), "pair": [x, z], "steps": s, "largest possible excess": top,
            "b": got, "status": status if got is None else "exact",
            "verdict": ("unbonded (certified: no bond of any size)" if got is None and status == f"none to {top}" else
                        ("bonded" if got is not None else "unsettled")), "seconds": round(time.time() - t0, 1)}


def part_finish(workers=16):
    """The pairs left unsettled by part random, searched to the largest excess their patch allows (|V| - 2 - s), 540 s each."""
    prev = json.load(open(HERE / "referee_rim_random.json"))
    pats = {(sd, k): T for sd, k, T in regenerate()}
    jobs = [(r["seed"], r["patch"], pats[(r["seed"], r["patch"])], tuple(r["pair"][0]), tuple(r["pair"][1]))
            for r in prev["unsettled or excess >= 1"] if r["b"] is None]
    with Pool(workers) as P:
        res = P.map(finish_pair, jobs, chunksize=1)
    return {"pairs": len(jobs), "results": res}


def polyiamonds(k):
    """Every patch of k knots joined through shared pairs, up to translation (no disc test yet)."""
    level = {RD.canon({("u", 0, 0)}), RD.canon({("d", 0, 0)})}
    for _ in range(2, k + 1):
        nxt = set()
        for T in level:
            for t in T:
                for u in RD.adjacent(t):
                    if u not in T:
                        nxt.add(RD.canon(set(T) | {u}))
        level = nxt
    return sorted(level, key=sorted)


def k14_chunk(Ts):
    r = Counter()
    for T in Ts:
        if not RD.disc(T):
            continue
        r.update(k13_disc(T))
    return dict(r)


def part_k14(workers=16):
    """Every disc of fourteen knots: the referee's search on every lone opposite facing pair, to the size bound."""
    Ts = polyiamonds(14)
    chunks = [Ts[i::400] for i in range(400)]
    acc = Counter()
    with Pool(workers) as P:
        for r in P.imap_unordered(k14_chunk, chunks):
            acc.update(r)
    return {"patches of 14 knots": len(Ts), "every disc of 14 knots, facing pairs by the referee's search": dict(sorted(acc.items()))}


def regenerate():
    """The study's 160 random patches (its job.py 'random' case), regenerated with its generator and seeds (its weavelib)."""
    sys.path.insert(0, str(ROOT / "experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches"))
    import weavelib as SW  # noqa: E402
    out = []
    for i in range(40):
        rng = random.Random(6000 + i)
        for k in range(4):
            T = {("u", 0, 0)}
            size = rng.randint(20, 40)
            while len(T) < size:
                t = rng.choice(sorted(T))
                nb = rng.choice(SW.nbrs(t))
                if nb not in T and SW.is_disc(T | {nb}):
                    T.add(nb)
            out.append((6000 + i, k, frozenset(T)))
    return out


def random_pair(args):
    seed, k, T, x, z = args
    P_ = patch(T)
    t0 = time.time()
    got, s, status = search(P_, x, z, emax=12, time_limit=300)
    return {"seed": seed, "patch": k, "knots": len(T), "pair": [x, z], "steps": s, "b": got,
            "excess": None if got is None else got - s - 1, "status": status, "seconds": round(time.time() - t0, 1)}


def part_random(workers=16):
    pats = regenerate()
    jobs = []
    for seed, k, T in pats:
        _, V, D, sp, lone = patch(T)
        assert all(RD.disc(T) for _ in [0])
        for x, z in itertools.combinations(sorted(lone), 2):
            if facing_pair(lone, x, z):
                jobs.append((seed, k, T, x, z))
    with Pool(workers) as P:
        res = P.map(random_pair, jobs, chunksize=1)
    hist = Counter(r["status"] if r["b"] is None else f"excess {r['excess']}" for r in res)
    return {"patches": len(pats), "facing pairs": len(jobs), "outcomes": dict(sorted(hist.items())),
            "unsettled or excess >= 1": [r for r in res if r["b"] is None or r["excess"] >= 1],
            "slowest settled (seconds)": sorted((r["seconds"] for r in res if r["b"] is not None), reverse=True)[:5]}


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"lemmaP": part_lemmaP, "validate": part_validate, "k13": part_k13, "random": part_random,
                      "validate_big": part_validate_big, "finish": part_finish,
                      "k14": part_k14}[part](),
                     indent=1, default=str))
