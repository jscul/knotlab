"""The frozen census of PERIODIC-READ-20261111-001A-E001 (contract.json beside this file): infinite bases with periodic overlap.

A periodic knot pattern is given by finitely many distinction kinds and knot kinds over Z^d: a knot kind names three (kind, shift)
pairs, and the infinite pattern has the distinction (v, z) for every kind v and z in Z^d and, for every knot kind and z, the knot on
its three distinctions shifted by z. Nothing limits how many knots lie on a pair. The not-all-equal law (NAE) is read on it:
  a value pattern on a finite set S extends to a state of the infinite pattern
    - if it extends to a state of a periodic quotient (the pattern modulo a sublattice) in which S stays distinct (lower bound), and
    - not if it fails in the window of radius R around the origin (upper bound), by compactness;
  along one direction (d = 1) a window of radius R >= max|z in S| + 2^(k span) + span decides exactly (a path of the de Bruijn
  graph longer than its nodes repeats a node, so it can be continued for ever on each side).
A verdict counts only when settled. Read faithfully to radius 2: no frozen distinction, no tied pair and no hollow triple other than a
knot among sets meeting the origin cell within graph distance 2, and every knot's pairs free.

Families (frozen): F1, d = 1: one or two distinction kinds, one to three knot kinds, shifts in {0, 1, 2}; F2, d = 2: one distinction
kind, one to three knot kinds, shifts in {-1, 0, 1}^2; connected; up to relabelling, reversal (F1) and the eight symmetries of Z^2
(F2); F2 read on every pattern with one or two knot kinds and a sample of 500 of the 2,120 with three (seed 20261120). In two
shifts a third bound helps: patterns repeating in one shift only (period 2 or 3), exact along the other. Readings: states; the faithful reading to radius 2 with settledness; how many knots lie on each pair; for each pattern read
faithfully, whether some periodic quotient (F1: n = 3 to 15; F2: index 9 to 30) is itself read faithfully as a finite base, the source
labels at a periodic state (each kind's distinction at the origin flipped by a change inside the box of radius 3), and for each pair
two steps apart whether it lies in a bond of four with two distinctions next to it.

Run from the repository root:
    .venv/bin/python -B experiments/PERIODIC-READ-20261111-001A/PERIODIC-READ-20261111-001A-E001_periodic_census/census.py
Output: artifacts/PERIODIC-READ-20261111-001A/PERIODIC-READ-20261111-001A-E001_periodic_census/census.json and census_log.txt.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIB = os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
LIB_SHA = "aee9a2eda0907064b89eae4fe4badddb22b80fecb62bd91d5a5fa448397010de"
sys.path.insert(0, LIB)
import knots_alone as ka  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "PERIODIC-READ-20261111-001A", "PERIODIC-READ-20261111-001A-E001_periodic_census")

# Frozen parameters (contract.json, "definitions")
F1_KINDS, F1_KNOTS, F1_SPAN, F1_R, F1_QUOT = (1, 2), 3, 2, 24, range(2, 16)
F2_KNOTS, F2_R = 3, 6
F2_SAMPLE3, F2_SEED = 500, 20261120          # every pattern with one or two knot kinds, and a sample of 500 with three
F2_STRIPS = (2, 3)                          # strips periodic in one coordinate with these periods, exact along the other
WORKERS = 8
F2_LATTICES = [(a, b, n // a) for n in range(3, 31) for a in range(1, n + 1) if n % a == 0 for b in range(n // a)]
RADIUS, BOX = 2, 3
QUOT_FAITHFUL_F1, QUOT_FAITHFUL_F2 = range(3, 16), (9, 30)


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


def norm_knot(knot):
    m = min(s for _, s in knot)
    return tuple(sorted((v, tuple(a - b for a, b in zip(s, m))) for v, s in knot))


def nae_clauses(T):
    return [c for t in T for c in ([x + 1 for x in t], [-(x + 1) for x in t])]


class Pattern:
    def __init__(self, d, k, knots):
        self.d, self.k = d, k
        self.knots = sorted({norm_knot(t) for t in knots})

    def window(self, R):
        cs = set(itertools.product(range(-R, R + 1), repeat=self.d))
        idx = {}
        for z in sorted(cs):
            for v in range(self.k):
                idx[(v, z)] = len(idx)
        T = []
        for t in self.knots:
            for z in cs:
                pts = [(v, tuple(a + b for a, b in zip(z, s))) for v, s in t]
                if all(p[1] in cs for p in pts):
                    T.append(tuple(idx[p] for p in pts))
        return idx, T

    def quotient(self, q):
        """q = n (d = 1) or (a, b, c), the sublattice spanned by (a, b) and (0, c) (d = 2). Returns idx, knots, reduction or Nones."""
        if self.d == 1:
            n = q
            red = (lambda z: (z[0] % n,))
            cs = [(x,) for x in range(n)]
        else:
            a, b, c = q

            def red(z):
                qq, x0 = divmod(z[0], a)
                return (x0, (z[1] - qq * b) % c)
            cs = [(x, y) for x in range(a) for y in range(c)]
        idx = {}
        for z in cs:
            for v in range(self.k):
                idx[(v, z)] = len(idx)
        T = set()
        for t in self.knots:
            for z in cs:
                pts = [(v, red(tuple(a_ + b_ for a_, b_ in zip(z, s)))) for v, s in t]
                if len(set(pts)) < 3:
                    return None, None, None
                T.add(tuple(sorted(idx[p] for p in pts)))
        return idx, sorted(T), red

    def pair_counts(self):
        c = Counter()
        for t in self.knots:
            for e1, e2 in itertools.combinations(sorted(t), 2):
                c[(e1[0], e2[0], tuple(x - y for x, y in zip(e2[1], e1[1])))] += 1
        return c


def connected_pattern(P):
    idx, T = P.window(3)
    adj = {i: set() for i in idx.values()}
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    start = idx[(0, (0,) * P.d)]
    seen, st = {start}, [start]
    while st:
        u = st.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                st.append(w)
    need = [idx[(v, (0,) * P.d)] for v in range(P.k)] + [idx[(0, tuple(1 if i == j else 0 for i in range(P.d)))] for j in range(P.d)]
    return all(n in seen for n in need)


class Strip:
    """d = 2: the pattern periodic with period m in coordinate `axis` and infinite in the other, read exactly along the other by a
    window of half-length L > 2^(m span) + span + 4 (a path of its de Bruijn graph longer than its nodes repeats a node). Its states are
    states of the infinite pattern; it shows states periodic in one direction only, such as ones with a wall between two regimes."""

    def __init__(self, P, m, axis):
        self.m, self.axis = m, axis
        other = 1 - axis
        span = max(s[other] for t in P.knots for _, s in t) - min(s[other] for t in P.knots for _, s in t)
        self.L = (1 << (m * max(span, 1))) + span + 6
        cs = [(i, j) for i in range(-self.L, self.L + 1) for j in range(m)]   # i along `other`, j along `axis`
        self.idx = {}
        for i, j in cs:
            z = [0, 0]
            z[other], z[axis] = i, j
            self.idx[(0, tuple(z))] = len(self.idx)
        T = []
        ok = True
        for t in P.knots:
            for i, j in cs:
                pts = []
                for v, sft in t:
                    z = [0, 0]
                    z[other], z[axis] = i + sft[other], (j + sft[axis]) % m
                    pts.append((v, tuple(z)))
                if any(abs(q[1][other]) > self.L for q in pts):
                    continue
                if len(set(pts)) < 3:
                    ok = False
                T.append(tuple(self.idx[q] for q in pts))
        self.ok = ok
        self.s = Minisat22(bootstrap_with=nae_clauses(T)) if ok else None
        self.has = ok and self.s.solve()

    def extends(self, S, p):
        if not self.has:
            return False
        imgs = []
        for v, z in S:
            w = list(z)
            w[self.axis] %= self.m
            imgs.append((v, tuple(w)))
        if len(set(imgs)) < len(imgs):
            return False
        return self.s.solve(assumptions=[(self.idx[x] + 1) * (1 if b else -1) for x, b in zip(imgs, p)])

    def close(self):
        if self.s is not None:
            self.s.delete()


class Reader:
    def __init__(self, P, R, quots, window_exact, strips=()):
        self.P, self.R, self.window_exact = P, R, window_exact
        self.strips = [Strip(P, m, axis) for m in strips for axis in (0, 1)] if P.d == 2 else []
        self.widx, self.wT = P.window(R)
        self.ws = Minisat22(bootstrap_with=nae_clauses(self.wT))
        self.wok = self.ws.solve()
        self.quots = []
        for q in quots:
            qidx, qT, red = P.quotient(q)
            if qidx is None:
                continue
            s = Minisat22(bootstrap_with=nae_clauses(qT))
            if s.solve():
                self.quots.append((q, qidx, qT, s, red))
            else:
                s.delete()
        self.cache = {}

    def extends(self, S, p):
        key = (tuple(S), p)
        if key not in self.cache:
            res = None
            if not self.wok or not self.ws.solve(assumptions=[(self.widx[x] + 1) * (1 if b else -1) for x, b in zip(S, p)]):
                res = False
            elif self.window_exact:
                res = True
            else:
                for q, qidx, qT, s, red in self.quots:
                    imgs = [(v, red(z)) for v, z in S]
                    if len(set(imgs)) < len(imgs):
                        continue
                    if s.solve(assumptions=[(qidx[x] + 1) * (1 if b else -1) for x, b in zip(imgs, p)]):
                        res = True
                        break
                if res is None:
                    for st in self.strips:
                        if st.extends(S, p):
                            res = True
                            break
            self.cache[key] = res
        return self.cache[key]

    def status(self, S):
        vals = [self.extends(list(S), p) for p in itertools.product((0, 1), repeat=len(S))]
        if all(v is True for v in vals):
            return "free"
        if any(v is False for v in vals):
            return "constrained"
        return "unsettled"

    def close(self):
        self.ws.delete()
        for q in self.quots:
            q[3].delete()
        for st in self.strips:
            st.close()


def adjacency(P, R):
    idx, T = P.window(R)
    inv = {i: x for x, i in idx.items()}
    adj = {}
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj.setdefault(inv[a], set()).add(inv[b])
            adj.setdefault(inv[b], set()).add(inv[a])
    return adj, {tuple(sorted(inv[x] for x in t)) for t in T}


def ball(adj, src, r):
    dist = {x: 0 for x in src}
    fr = list(src)
    for d in range(1, r + 1):
        nx = []
        for u in fr:
            for w in adj.get(u, ()):
                if w not in dist:
                    dist[w] = d
                    nx.append(w)
        fr = nx
    return dist


def faithful_reading(P, rd):
    """Sets meeting the origin cell within graph distance RADIUS. Stops at the first settled violation (the reading is then not
    faithful); otherwise it is faithful when every set is settled and unsettled when some is not."""
    adj, knots = adjacency(P, RADIUS + 4)
    o = (0,) * P.d
    origin = [(v, o) for v in range(P.k)]
    near = sorted(ball(adj, origin, RADIUS))
    stat = {}

    def st(S):
        S = tuple(sorted(S))
        if S not in stat:
            stat[S] = rd.status(S)
        return stat[S]

    def result(faithful, why):
        return {"faithful": faithful, "why": why, "unsettled sets": sum(1 for v in stat.values() if v == "unsettled"),
                "sets read": len(stat)}, adj, knots, origin
    for x in origin:
        if st((x,)) == "constrained":
            return result(False, "frozen")
    for a in origin:
        for b in near:
            if b != a and st((a, b)) == "constrained":
                return result(False, "tied pair")
    for a in origin:
        for b, c in itertools.combinations([x for x in near if x != a], 2):
            t = tuple(sorted((a, b, c)))
            ps = [st(q) for q in itertools.combinations(t, 2)]
            if "constrained" in ps:
                return result(False, "tied pair")
            if "unsettled" in ps:
                continue
            s_ = st(t)
            if t not in knots and s_ == "constrained":
                return result(False, "unnamed hollow triple")
    unsettled = any(v == "unsettled" for v in stat.values())
    return result(None if unsettled else True, "unsettled" if unsettled else "faithful")


def source_labels(P, rd):
    """At a periodic state from the first quotient with states: can each origin distinction be flipped by a change inside the box?"""
    if not rd.quots:
        return None
    q, qidx, qT, s, red = rd.quots[0]
    s.solve()
    m = set(x for x in s.get_model() if x > 0)
    sigma = {x: (1 if qidx[(x[0], red(x[1]))] + 1 in m else 0) for x in rd.widx}
    out = {}
    for v in range(P.k):
        o = (v, (0,) * P.d)
        assum = [(rd.widx[x] + 1) * (1 if sigma[x] else -1) for x in rd.widx if max(abs(c) for c in x[1]) > BOX]
        assum.append((rd.widx[o] + 1) * (-1 if sigma[o] else 1))
        out[v] = rd.ws.solve(assumptions=assum)
    return {"periodic state from": list(q) if isinstance(q, tuple) else q, "native": all(out.values()), "kinds flipped": sum(out.values())}


def bonds_of_four(P, rd, adj, knots, origin):
    """For each distinction two steps from an origin distinction: is it in a bond of four with two distinctions next to it or to the
    origin distinction? A bond: constrained, every three-element part free."""
    rows = Counter()
    for o in origin:
        dist = ball(adj, [o], 2)
        for w in sorted(x for x, d in dist.items() if d == 2):
            region = sorted((set(adj.get(o, ())) | set(adj.get(w, ()))) - {o, w})
            verdict = "none"
            for x, y in itertools.combinations(region, 2):
                S = tuple(sorted((o, w, x, y)))
                whole = rd.status(S)
                if whole == "free":
                    continue
                parts = [rd.status(tuple(sorted(set(S) - {u}))) for u in S]
                if whole == "constrained" and all(p == "free" for p in parts):
                    verdict = "bond"
                    break
                if whole == "unsettled" or any(p == "unsettled" for p in parts):
                    verdict = "unsettled" if verdict == "none" else verdict
            rows[verdict] += 1
    return dict(rows)


def quotient_faithful(P):
    if P.d == 1:
        qs = list(QUOT_FAITHFUL_F1)
    else:
        lo, hi = QUOT_FAITHFUL_F2
        qs = [q for q in F2_LATTICES if lo <= q[0] * q[2] <= hi]
    tried = faithful = 0
    for q in qs:
        qidx, qT, red = P.quotient(q)
        if qidx is None or not ka.connected(len(qidx), qT):
            continue
        tried += 1
        r = ka.read_law_sat(len(qidx), qT, ka.LAWS["NAE"])
        faithful += bool(r.get("faithful"))
    return {"quotients read": tried, "read faithfully": faithful}


def read_pattern(item):
    d, k, knots = item
    P = Pattern(d, k, [tuple((v, tuple(s)) for v, s in t) for t in knots])
    if d == 1:
        rd = Reader(P, F1_R, list(F1_QUOT), window_exact=True)
    else:
        rd = Reader(P, F2_R, F2_LATTICES, window_exact=False, strips=F2_STRIPS)
    pc = P.pair_counts()
    rec = {"d": d, "k": k, "knots": [[[v, list(s)] for v, s in t] for t in P.knots], "max knots per pair": max(pc.values()),
           "pairs by count": dict(sorted(Counter(pc.values()).items())), "window has states": rd.wok,
           "periodic states": len(rd.quots)}
    if not rd.wok:
        rec["states"] = False
        rd.close()
        return rec
    rec["states"] = True if (rd.quots or d == 1 or any(st.has for st in rd.strips)) else None
    fr, adj, knots_set, origin = faithful_reading(P, rd)
    rec.update(fr)
    if fr["faithful"]:
        rec["source"] = source_labels(P, rd)
        rec["bonds of four at graph distance 2"] = bonds_of_four(P, rd, adj, knots_set, origin)
        rec["quotients"] = quotient_faithful(P)
    rd.close()
    return rec


# ----------------------------------------------------------------------------------------------------------------------

D4 = [((1, 0), (0, 1)), ((0, -1), (1, 0)), ((-1, 0), (0, -1)), ((0, 1), (-1, 0)), ((1, 0), (0, -1)), ((-1, 0), (0, 1)),
      ((0, 1), (1, 0)), ((0, -1), (-1, 0))]


def family1():
    out = {}
    for k in F1_KINDS:
        elems = [(v, (s,)) for v in range(k) for s in range(F1_SPAN + 1)]
        shapes = sorted({norm_knot(t) for t in itertools.combinations(elems, 3)})
        for m in range(1, F1_KNOTS + 1):
            for ks in itertools.combinations(shapes, m):
                P = Pattern(1, k, ks)
                if not connected_pattern(P):
                    continue
                best = None
                for perm in itertools.permutations(range(k)):
                    for rev in (False, True):
                        c = tuple(sorted({norm_knot([(perm[v], ((F1_SPAN - s[0]) if rev else s[0],)) for v, s in t]) for t in P.knots}))
                        if best is None or c < best:
                            best = c
                out.setdefault(best, (1, k, P.knots))
    return list(out.values())


def family2():
    pts = list(itertools.product((-1, 0, 1), repeat=2))
    shapes = sorted({norm_knot([(0, p) for p in t]) for t in itertools.combinations(pts, 3)})
    out = {}
    for m in range(1, F2_KNOTS + 1):
        for ks in itertools.combinations(shapes, m):
            P = Pattern(2, 1, ks)
            if not connected_pattern(P):
                continue
            ap = lambda M, s: (M[0][0] * s[0] + M[0][1] * s[1], M[1][0] * s[0] + M[1][1] * s[1])
            c = min(tuple(sorted({norm_knot([(v, ap(M, s)) for v, s in t]) for t in P.knots})) for M in D4)
            out.setdefault(c, (2, 1, P.knots))
    return list(out.values())


def summarize(r1, r2):
    sm = {}
    sm["P1"] = {"F1 patterns": len(r1), "unsettled readings": sum(1 for r in r1 if r.get("states") and r.get("faithful") is None),
                "holds": all(r.get("faithful") is not None for r in r1 if r.get("states"))}
    f2f = [r for r in r2 if r.get("faithful")]
    over = [r for r in f2f if r["max knots per pair"] >= 3]
    over4 = [r for r in f2f if r["max knots per pair"] >= 4]
    sm["P2"] = {"F2 read faithfully (settled)": len(f2f), "with a pair in three or more knots": len(over),
                "with a pair in four or more knots": len(over4), "examples": [r["knots"] for r in over4[:5]], "holds": len(over4) > 0}
    allf = [r for r in r1 + r2 if r.get("faithful")]
    beyond = [r for r in f2f if r.get("quotients", {}).get("quotients read") and r["quotients"]["read faithfully"] == 0]
    sm["P3"] = {"faithful patterns with no quotient read faithfully": len(beyond), "examples": [r["knots"] for r in beyond[:5]],
                "holds": len(beyond) > 0}
    rows = Counter()
    bad = []
    for r in f2f:
        b = r.get("bonds of four at graph distance 2", {})
        rows.update(b)
        if b.get("none"):
            bad.append(r["knots"])
    sm["P4"] = {"pairs two steps apart (F2 faithful)": dict(rows), "patterns with a pair in no bond of four": len(bad),
                "examples": bad[:5], "holds": not bad}
    src = [r for r in allf if r.get("source") is not None]
    sm["P5"] = {"faithful with a periodic state": len(src), "native": sum(1 for r in src if r["source"]["native"]),
                "holds": all(r["source"]["native"] for r in src)}
    sm["measured"] = {
        "F1": dict(Counter(f"faithful={r.get('faithful')} max pair={r['max knots per pair']}" for r in r1)),
        "F2": dict(Counter(f"states={r.get('states')} faithful={r.get('faithful')} max pair={r['max knots per pair']}" for r in r2)),
        "F2 window states but no periodic state found": sum(1 for r in r2 if r["window has states"] and not r["periodic states"])}
    sm["failures"] = [k for k in ("P1", "P2", "P3", "P4", "P5") if not sm[k]["holds"]]
    return sm


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(LIB, "knots_alone.py"), "rb").read()).hexdigest()
    log("library hash matches:", have == LIB_SHA)
    if have != LIB_SHA:
        raise SystemExit("library changed")
    fam1 = family1()
    every2 = family2()
    import random
    small = [x for x in every2 if len(x[2]) <= 2]
    three = [x for x in every2 if len(x[2]) == 3]
    fam2 = small + random.Random(F2_SEED).sample(three, F2_SAMPLE3)
    log("families: F1", len(fam1), "F2", len(fam2), "of", len(every2), Counter(len(k) for _, _, k in fam2))
    with Pool(WORKERS) as pool:
        r1 = pool.map(read_pattern, fam1, chunksize=2)
        log("F1 done", round(time.time() - t0, 1), "s")
        r2 = pool.map(read_pattern, fam2, chunksize=2)
        log("F2 done", round(time.time() - t0, 1), "s")
    out = {"F1": r1, "F2": r2, "coverage": {"F1": len(r1), "F2": len(r2), "F2 family": len(every2), "F2 three-kind sample": F2_SAMPLE3}}
    out["summary"] = summarize(r1, r2)
    log("summary:", json.dumps(out["summary"], default=str)[:4000])
    json.dump(out, open(os.path.join(OUT, "census.json"), "w"), indent=1, default=str)
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
