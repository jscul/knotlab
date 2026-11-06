#!/usr/bin/env python3
"""Check of DIRECTIONAL-RIGIDITY-20261023-001B-P001 (standard library only).

- Kinds: the 30 three-place tiling placements split into four kinds by their doubly allowed and coin-pinned patterns (h/v
  stripes, diagonal stripes, straight walls, bending walls); the kinds are compared with the groups of
  DIRECTIONAL-RIGIDITY-20261023-001A-E001.
- Proposition 1 (no relational criterion): the ternary operations preserving R and its complement, for all 54 tiling
  placements; the classes of the three-place placements under renaming places and complementing, and the kinds in each.
- Theorem 2 (stripes): for every stripe placement, torus 3 x 3, 3 x 4, 4 x 4, 4 x 5, 5 x 5, twist and class of the list (minus the
  diagonal class for diagonal stripes), the stripe assignment of the proof satisfies every clause of a strip of 24 periods of the
  cylinder, for a random configuration.
- Theorem 3 (straight walls): for the eight straight-wall placements on 3 x 3, 3 x 4 and 4 x 4 in every non-fitting twist, on
  random and on planted configurations, the cylinders along the odd classes among eight (own search: strips with no assignment,
  cyclic covers with a verified one) all contradict or all have assignments; they have assignments exactly when the wall
  construction of the proof satisfies every clause of a strip of 24 periods for some staircase; always all contradict when the
  relative twist is odd on the diagonal class.
- Proposition 4 (bending walls): for each of the twelve bending placements, one configuration on 3 x 3 whose pattern among eight
  classes is certified both ways and is selective.
- Theorem 7 (rotating walls): for the four bending placements with no free place (54, 109, 147, 151), the patterns predicted from
  the valid wall cycles of the torus equal the frozen 3 x 3 histograms of A over 16 classes in every twist, and equal the
  certified patterns among eight classes of their selective examples and of random configurations on 3 x 3 and 3 x 4.
- Results of A (frozen rows): per kind, the patterns observed; for straight walls, the exact counts on 3 x 3 and 3 x 4 against
  the formula of Theorem 3 and the sampled counts on 4 x 4, 4 x 5, 5 x 5 against its probability.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import math
import random
import sys
from itertools import permutations
from pathlib import Path

sys.setrecursionlimit(20000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
A_ROWS = ROOT / "artifacts/DIRECTIONAL-RIGIDITY-20261023-001A/DIRECTIONAL-RIGIDITY-20261023-001A-E001_rigidity/rows.jsonl"
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSES = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]
STRIPE_CLASSES = CLASSES + [(1, 3), (3, 1), (1, -3), (3, -1), (2, 3), (3, 2), (1, 4), (4, 1), (3, 4), (4, 3)]
TORI = [(3, 3), (3, 4), (4, 4), (4, 5), (5, 5)]
UPO, DNO = ((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))
SEED = 20261023
GROUPS = {  # groups of DIRECTIONAL-RIGIDITY-20261023-001A-E001, fixed by scoping
    "saturated": {45, 61, 101, 103, 135, 149, 157, 199},
    "one-dimensional": {91, 94, 123, 167, 173, 183},
    "never": {127, 191, 223, 239},
    "selective": {54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215},
}
SELECTIVE_EXAMPLES = [  # (placement, twist, configuration) on 3 x 3, located with the producer's program of A
    (54, (0, 0), 168100), (62, (0, 0), 77851), (109, (0, 0), 204805), (110, (0, 0), 24642), (111, (0, 0), 36954),
    (125, (0, 0), 49253), (147, (0, 1), 30817), (151, (0, 1), 110633), (155, (0, 1), 45276), (159, (0, 1), 227852),
    (203, (0, 1), 123079), (215, (0, 1), 45302),
]


# ------------------------------------------------------------------ patterns and kinds

def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def bit(p, k):
    return (p >> k) & 1


def lone(p):
    """The place whose value differs from the other two, or None for 000 and 111."""
    for k in range(3):
        a, b = [bit(p, m) for m in range(3) if m != k]
        if a == b != bit(p, k):
            return k
    return None


def flip1(R):
    return sum(1 << (p ^ 2) for p in range(8) if R >> p & 1)


def frame(R):
    """(relation in the constant frame, flipped?) or None: flip place 1 when U holds 010 and 101 but not 000."""
    U = R & comp(R)
    if U & 1:
        return R, False
    if U >> 2 & 1:
        return flip1(R), True
    return None


def contains_all(U, pred):
    return all(U >> p & 1 for p in range(8) if pred(p))


def diagonal_stripes(R):
    U = R & comp(R)
    return [b for b in (0, 1) if contains_all(U, lambda p, b=b: bit(p, 0) ^ bit(p, 2) == b)]


def hv_stripes(R):
    U = R & comp(R)
    return [a for a in (0, 1) if contains_all(U, lambda p, a=a: bit(p, 0) ^ bit(p, 1) == a or bit(p, 1) ^ bit(p, 2) == a)]


def lone_sets(R):
    F, _ = frame(R)
    U = F & comp(F)
    free = {lone(p) for p in range(8) if U >> p & 1} - {None}
    allowed = {lone(p) for p in range(8) if (F | comp(F)) >> p & 1} - {None}
    return free, allowed


def kind(R):
    if hv_stripes(R):
        return "h/v stripes"
    if diagonal_stripes(R):
        return "diagonal stripes"
    if frame(R) is None:
        return "other"
    free, allowed = lone_sets(R)
    if 1 in free:
        return "other"
    return "bending walls" if {0, 2} <= allowed else "straight walls"


# ------------------------------------------------------------------ Proposition 1: polymorphisms and renaming

def preserves(f, R):
    T = [p for p in range(8) if R >> p & 1]
    for a in T:
        for b in T:
            for c in T:
                r = sum(((f >> (bit(a, k) | bit(b, k) << 1 | bit(c, k) << 2)) & 1) << k for k in range(3))
                if not R >> r & 1:
                    return False
    return True


PROJ = {sum(((i >> k) & 1) << i for i in range(8)) for k in range(3)}
CONST = {0, 255}
MAJ = sum((1 if bin(i).count("1") >= 2 else 0) << i for i in range(8))


def clone3(R):
    return {f for f in range(256) if preserves(f, R) and preserves(f, comp(R))}


def rename(R, pi):
    return sum(1 << sum(bit(p, k) << pi[k] for k in range(3)) for p in range(8) if R >> p & 1)


def renaming_classes(placements):
    out, seen = [], set()
    for R in sorted(placements):
        if R in seen:
            continue
        orbit = {S for pi in permutations(range(3)) for S in (rename(R, pi), rename(comp(R), pi))}
        members = sorted(S for S in placements if S in orbit)
        seen |= set(members)
        out.append(members)
    return out


# ------------------------------------------------------------------ worlds, lifted picture and cylinder strips

def triangles(L, M):
    return [[(i + a, j + b) for a, b in offs] for j in range(M) for i in range(L) for offs in (UPO, DNO)]


def vid(p, L, M):
    return (p[1] % M) * L + p[0] % L


def deck(p, L, M):
    return (p[0] // L, p[1] // M)


def gauge(p, q, L, M):
    d = deck(p, L, M)
    return (q[0] * d[0] + q[1] * d[1]) & 1


def fitting(R, L, M):
    U = R & comp(R)
    tris = triangles(L, M)
    V = L * M
    out = []
    for q in TWISTS:
        by_last = [[] for _ in range(V)]
        for P in tris:
            vs = [vid(p, L, M) for p in P]
            by_last[max(vs)].append((vs, [gauge(p, q, L, M) for p in P]))
        h = [0] * V

        def go(v):
            if v == V:
                return True
            for b in (0, 1):
                h[v] = b
                if all(U >> sum((h[vs[k]] ^ g[k]) << k for k in range(3)) & 1 for vs, g in by_last[v]) and go(v + 1):
                    return True
            return False

        if go(0):
            out.append(q)
    return out


def odd_classes(classes, fit, q):
    return [c for c in classes if fit and all(((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1 for f in fit)]


def diagonal_class(L, M):
    l = L * M // math.gcd(L, M)
    return (l // L, l // M)


def norm(c):
    return c if c > (0, 0) else (-c[0], -c[1])


def complement_basis(c):
    for u0 in range(-5, 6):
        for u1 in range(-5, 6):
            if c[0] * u1 - c[1] * u0 == 1:
                return (u0, u1)
    raise ValueError(c)


def layout(L, M, c, sheets, cyclic):
    """Cylinder cover as in LINE-DETECTOR-20261023-001B-P001: node keys (vertex, sheet) and (triangle, corner nodes)."""
    tris = triangles(L, M)
    nodes, out = {}, []
    for f, P in enumerate(tris):
        corners = []
        for p in P:
            d = deck(p, L, M)
            corners.append((vid(p, L, M), c[0] * d[1] - c[1] * d[0]))
        for m in range(sheets):
            out.append((f, [nodes.setdefault((v, (t + m) % sheets if cyclic else t + m), len(nodes)) for v, t in corners]))
    return nodes, out


def clauses(R, L, M, q, x, c, sheets, cyclic):
    nodes, lay = layout(L, M, c, sheets, cyclic)
    tris = triangles(L, M)
    out = []
    for f, nd in lay:
        P = tris[f]
        rel = comp(R) if x >> f & 1 else R
        g = [gauge(p, q, L, M) for p in P]
        for pat in range(8):
            if not rel >> pat & 1:
                out.append([(-(nd[k] + 1) if bit(pat, k) ^ g[k] else nd[k] + 1) for k in range(3)])
    return len(nodes), out, nodes


def dpll(n, cls):
    occ = [[] for _ in range(2 * n + 2)]
    for i, cl in enumerate(cls):
        for lit in cl:
            occ[lit if lit > 0 else n - lit].append(i)
    val = [-1] * (n + 1)

    def lit_val(lit):
        v = val[abs(lit)]
        return -1 if v < 0 else (v if lit > 0 else 1 - v)

    def propagate(trail, start):
        i = start
        while i < len(trail):
            var = trail[i]
            neg = -var if val[var] == 1 else var
            for ci in occ[neg if neg > 0 else n - neg]:
                free, sat = [], False
                for lit in cls[ci]:
                    lv = lit_val(lit)
                    if lv == 1:
                        sat = True
                        break
                    if lv < 0:
                        free.append(lit)
                if sat:
                    continue
                if not free:
                    return False
                if len(free) == 1:
                    val[abs(free[0])] = 1 if free[0] > 0 else 0
                    trail.append(abs(free[0]))
            i += 1
        return True

    def solve(trail):
        start = len(trail)
        var = next((v for v in range(1, n + 1) if val[v] < 0), None)
        if var is None:
            return True
        for b in (0, 1):
            val[var] = b
            trail.append(var)
            if propagate(trail, len(trail) - 1) and solve(trail):
                return True
            while len(trail) > start:
                val[trail.pop()] = -1
        return False

    if not solve([]):
        return None
    return [val[v] for v in range(1, n + 1)]


def satisfies(cls, assignment):
    return all(any((assignment[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in cls)


def certify(R, L, M, q, x, c):
    """True: a strip of 12, 24 or 36 periods has no assignment; False: a cyclic cover of at most 12 sheets has a verified one."""
    for k in range(1, 13):
        n, cl, _ = clauses(R, L, M, q, x, c, k, True)
        a = dpll(n, cl)
        if a is not None:
            return False if satisfies(cl, a) else None
    for periods in (12, 24, 36):
        n, cl, _ = clauses(R, L, M, q, x, c, periods, False)
        if dpll(n, cl) is None:
            return True
    return None


def strip_assignment_ok(R, L, M, q, x, c, F, sheets=24):
    """Does the lifted assignment F (a function on Z^2 with F(p + w) = F(p) + q(c)) satisfy every clause of the strip?

    A node (v, t) of the strip is the vertex v lifted by the deck vector t u, u a complement of c; its value is F(p) + q.deck(p)
    (the change of variables of the proof's Lemma A). The quasi-periodicity is checked at the same time."""
    n, cl, nodes = clauses(R, L, M, q, x, c, sheets, False)
    u = complement_basis(c)
    w = (c[0] * L, c[1] * M)
    qc = (q[0] * c[0] + q[1] * c[1]) & 1
    a = [0] * n
    for (v, t), idx in nodes.items():
        d = (t * u[0], t * u[1])
        p = (v % L + d[0] * L, v // L + d[1] * M)
        for k in (-1, 1):
            pk = (p[0] + k * w[0], p[1] + k * w[1])
            if F(pk) != F(p) ^ qc:
                return False
        a[idx] = F(p) ^ ((q[0] * d[0] + q[1] * d[1]) & 1)
    return satisfies(cl, a)


# ------------------------------------------------------------------ Theorem 2: stripe assignments

def stripe_assignment(R, L, M, q, c, kind_name, wrong_parity=0):
    """The lifted doubly allowed assignment of the proof of Theorem 2, or None if the class is excluded (wrong_parity: control)."""
    qc = ((q[0] * c[0] + q[1] * c[1]) & 1) ^ wrong_parity
    w = (c[0] * L, c[1] * M)
    if kind_name == "diagonal stripes":
        beta = diagonal_stripes(R)[0]
        delta = w[0] - w[1]
        if delta == 0:
            return None
        mu = qc ^ (beta * w[0] & 1)
        D = abs(delta)
        return lambda p: ((((p[0] - p[1]) // D) * mu) & 1) ^ (beta * p[0] & 1)
    alpha = hv_stripes(R)[0]
    if w[1] != 0:
        mu = qc ^ (alpha * w[0] & 1)
        D = abs(w[1])
        return lambda p: (((p[1] // D) * mu) & 1) ^ (alpha * p[0] & 1)
    mu = qc ^ (alpha * w[1] & 1)
    D = abs(w[0])
    return lambda p: (((p[0] // D) * mu) & 1) ^ (alpha * p[1] & 1)


# ------------------------------------------------------------------ Theorem 3: walls

def wall_assignment(R, L, M, c, s, a):
    """Lifted assignment of the proof of Theorem 3: walls at the staircases s + k delta, value a on the diagonal D_s.

    In the constant frame the diagonal D_t = {i - j = t} has value a + k + 1 for s + k D < t <= s + (k + 1) D, D = |delta|;
    flipped placements get the frame flip (i + j) mod 2 back."""
    w = (c[0] * L, c[1] * M)
    D = abs(w[0] - w[1])
    _, flipped = frame(R)

    def F(p):
        k = (p[0] - p[1] - s - 1) // D
        return (a ^ 1 ^ (k & 1)) ^ (((p[0] + p[1]) & 1) if flipped else 0)

    return F


def planted(R, L, M, q, rng):
    """A configuration whose staircase s (random) is compatible: the coins on its 2l triangles accept the wall patterns."""
    g = math.gcd(L, M)
    l = L * M // g
    s, a = rng.randrange(g), rng.randrange(2)
    x = rng.randrange(1 << (2 * L * M))
    _, flipped = frame(R)

    def F(p):
        v = a if p[0] - p[1] == s else 1 - a
        return v ^ (((p[0] + p[1]) & 1) if flipped else 0)

    for t in range(l):
        for typ, base in ((0, (s + t, t)), (1, (s + t + 1, t))):
            offs = UPO if typ == 0 else DNO
            pat = sum(F((base[0] + o[0], base[1] + o[1])) << k for k, o in enumerate(offs))
            coin = 0 if R >> pat & 1 else 1
            assert comp(R) >> pat & 1 if coin else True
            f = 2 * ((base[1] % M) * L + base[0] % L) + typ
            dk = (base[0] // L, base[1] // M)
            x = (x & ~(1 << f)) | ((coin ^ ((q[0] * dk[0] + q[1] * dk[1]) & 1)) << f)
    return x


def theorem3_checks(rng, straight):
    out = {"cases": 0, "configurations": 0, "planted": 0, "undetermined": 0, "all odd classes agree": 0,
           "assignments exactly when a wall construction verifies": 0, "relative twist odd on the diagonal: all contradict": 0,
           "relative twist odd on the diagonal: configurations": 0, "with assignments": 0}
    for R in sorted(straight):
        for L, M in ((3, 3), (3, 4), (4, 4)):
            fit = fitting(R, L, M)
            d = diagonal_class(L, M)
            g = math.gcd(L, M)
            for q in TWISTS:
                if q in fit:
                    continue
                out["cases"] += 1
                r = (q[0] ^ fit[0][0], q[1] ^ fit[0][1])
                rd = (r[0] * d[0] + r[1] * d[1]) & 1
                odd = odd_classes(CLASSES, fit, q)[:3]
                configs = [rng.randrange(1 << (2 * L * M)) for _ in range(2)]
                if not rd:
                    configs.append(planted(R, L, M, q, rng))
                    out["planted"] += 1
                for x in configs:
                    out["configurations"] += 1
                    st = [certify(R, L, M, q, x, c) for c in odd]
                    if None in st:
                        out["undetermined"] += 1
                        continue
                    agree = len(set(st)) == 1
                    out["all odd classes agree"] += agree
                    has = agree and not st[0]
                    out["with assignments"] += has
                    walls = (not rd) and any(all(strip_assignment_ok(R, L, M, q, x, c, wall_assignment(R, L, M, c, s, a))
                                                 for c in odd) for s in range(g) for a in (0, 1))
                    out["assignments exactly when a wall construction verifies"] += agree and (has == walls)
                    if rd:
                        out["relative twist odd on the diagonal: configurations"] += 1
                        out["relative twist odd on the diagonal: all contradict"] += all(st)
    return out


# ------------------------------------------------------------------ Theorem 7: rotating walls

CCW = {0: (0, 1, 2), 1: (0, 2, 1)}  # places of up and down triangles in counterclockwise order


def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def wall_moves(L, M):
    """For each torus triangle and entry edge k (from the k-th to the (k+1)-th corner counterclockwise): the left and the right
    turn, as (turn 0 left / 1 right, lone place, next triangle and its entry edge, deck shift)."""
    def corners(typ, i, j):
        return [(i + a, j + b) for a, b in (UPO if typ == 0 else DNO)]

    where = {}
    for typ in (0, 1):
        for i in range(-1, L + 1):
            for j in range(-1, M + 1):
                cs, ccw = corners(typ, i, j), CCW[typ]
                for k in range(3):
                    where.setdefault(frozenset((cs[ccw[k]], cs[ccw[(k + 1) % 3]])), []).append((typ, i, j, k))
    moves = {}
    for typ in (0, 1):
        for i in range(L):
            for j in range(M):
                cs, ccw = corners(typ, i, j), CCW[typ]
                for k in range(3):
                    opts = []
                    for turn, exit_k, lone_k in ((0, (k - 1) % 3, k), (1, (k + 1) % 3, (k + 1) % 3)):
                        edge = frozenset((cs[ccw[exit_k]], cs[ccw[(exit_k + 1) % 3]]))
                        t2, i2, j2, k2 = next(t for t in where[edge] if t[:3] != (typ, i, j))
                        opts.append((turn, ccw[lone_k], (t2, i2 % L, j2 % M, k2), (i2 // L, j2 // M)))
                    moves[(typ, i, j, k)] = opts
    return moves


def pinned_values(R):
    fr, _ = frame(R)
    U = fr & comp(fr)
    return {lone(p): bit(p, lone(p)) for p in range(8) if fr >> p & 1 and not U >> p & 1 and lone(p) is not None}


def rotating_pattern(R, L, M, q, x, classes, moves):
    """Theorem 7's pattern (bit set: the cylinder contradicts) over the classes, from the valid wall cycles of the torus."""
    _, flipped = frame(R)
    val = pinned_values(R)
    qf = (q[0] ^ (L & 1), q[1] ^ (M & 1)) if flipped else q
    coin = {(typ, i, j): ((x >> (2 * (j * L + i) + typ)) & 1) ^ (((i + j) & 1) if flipped else 0)
            for typ in (0, 1) for i in range(L) for j in range(M)}
    seen, cycles = set(), []
    for s0 in moves:
        for b0 in (0, 1):
            if (s0, b0) in seen:
                continue
            s, b, pos, path, closed = s0, b0, (0, 0), [], False
            while (s, b) not in seen:
                seen.add((s, b))
                path.append((s, pos))
                nxt = [(s2, b ^ ((qf[0] * dk[0] + qf[1] * dk[1]) & 1), (pos[0] + dk[0], pos[1] + dk[1]))
                       for turn, place, s2, dk in moves[s] if place in val and val[place] ^ coin[s[:3]] ^ b == turn]
                if not nxt:
                    break
                s, b, pos = nxt[0]
                if (s, b) == (s0, b0):
                    closed = True
                    break
            if closed:
                visits, overlaps = {}, []
                for st, p in path:
                    for p0 in visits.setdefault(st[:3], []):
                        overlaps.append((p[0] - p0[0], p[1] - p0[1]))
                    visits[st[:3]].append(p)
                cycles.append((pos, overlaps))
    m = 0
    for k, c in enumerate(classes):
        if (qf[0] * c[0] + qf[1] * c[1]) & 1 and not any(
                det(c, e) and not any(det(d, e) % det(c, e) == 0 and det(c, d) % det(c, e) == 0 for d in ov)
                for e, ov in cycles):
            m |= 1 << k
    return m


def theorem7_checks(rng, rotating, rows):
    out = {"placements": sorted(rotating), "one pinned value each": all(len(set(pinned_values(R).values())) == 1 for R in rotating),
           "exhaustive 3 x 3 histograms (16 classes) equal to A": {}, "certified configurations": 0,
           "predicted pattern equals the certified one": 0, "selective among them": 0, "undetermined": 0}
    moves33 = wall_moves(3, 3)
    by = {(r["R"], r["L"], r["M"]): r for r in rows}
    for R in sorted(rotating):
        row = by.get((R, 3, 3))
        if row is None:
            continue
        cls = [tuple(c) for c in row["classes"]]
        for qs, t in sorted(row["twists"].items()):
            q = (int(qs[0]), int(qs[1]))
            hist = {}
            for x in range(1 << 18):
                m = rotating_pattern(R, 3, 3, q, x, cls, moves33)
                hist[m] = hist.get(m, 0) + 1
            obs = {int(k): v for k, v in t["patterns"].items()}
            obs[0] = obs.get(0, 0) + t["sat"]
            out["exhaustive 3 x 3 histograms (16 classes) equal to A"][f"{R} twist {qs}"] = hist == obs
            out["non-global nonzero patterns predicted"] = out.get("non-global nonzero patterns predicted", 0) + sum(
                n for m, n in hist.items() if m and m != t["odd_mask"])
    examples = [(R, 3, 3, q, x) for R, q, x in SELECTIVE_EXAMPLES if R in rotating]
    for R in sorted(rotating):
        for L, M in ((3, 3), (3, 4)):
            fit = fitting(R, L, M)
            for q in TWISTS:
                if q not in fit:
                    examples += [(R, L, M, q, rng.randrange(1 << (2 * L * M)))]
    movesLM = {(3, 3): moves33, (3, 4): wall_moves(3, 4)}
    for R, L, M, q, x in examples:
        st = [certify(R, L, M, q, x, c) for c in CLASSES]
        if None in st:
            out["undetermined"] += 1
            continue
        cert = sum(1 << k for k, v in enumerate(st) if v)
        pred = rotating_pattern(R, L, M, q, x, CLASSES, movesLM[(L, M)])
        out["certified configurations"] += 1
        out["predicted pattern equals the certified one"] += pred == cert
        odd = odd_classes(CLASSES, fitting(R, L, M), q)
        oddm = sum(1 << k for k, c in enumerate(CLASSES) if c in odd)
        out["selective among them"] += cert != oddm and bin(cert).count("1") >= 2
    return out


# ------------------------------------------------------------------ results of A

def formula_empty(L, M):
    g = math.gcd(L, M)
    l = L * M // g
    return (1 << (2 * L * M)) - ((1 << (2 * l)) - 2) ** g, 1 - (1 - 2.0 ** (1 - 2 * l)) ** g


def a_results(rows, kinds):
    out = {"rows": len(rows), "straight walls": {}, "diagonal stripes: patterns outside the diagonal class": 0,
           "h/v stripes: nonzero patterns": 0, "bending walls: selective (placement, torus) pairs": [],
           "bending walls: (placement, torus) pairs without a selective pattern": [],
           "placements with single lines and global contradictions, by kind": {}}
    for row in rows:
        R, L, M = row["R"], row["L"], row["M"]
        k = kinds.get(R)
        if k is None:
            continue
        cls = [tuple(c) for c in row["classes"]]
        dmask = sum(1 << i for i, c in enumerate(cls) if norm(c) == norm(tuple(row["diagonal_class"])))
        fit = [tuple(f) for f in row["fitting"]]
        single = glob = sel = False
        for qs, t in row["twists"].items():
            q = (int(qs[0]), int(qs[1]))
            om = t["odd_mask"]
            pats = {int(m): n for m, n in t["patterns"].items()}
            nz = {m: n for m, n in pats.items() if m}
            single |= any(bin(m).count("1") == 1 for m in nz)
            glob |= om in nz and bin(om).count("1") >= 2
            sel |= any(m != om and bin(m).count("1") >= 2 and not m & ~om for m in nz)
            if k == "diagonal stripes":
                out["diagonal stripes: patterns outside the diagonal class"] += sum(n for m, n in nz.items() if m & ~dmask)
            elif k == "h/v stripes":
                out["h/v stripes: nonzero patterns"] += sum(nz.values())
            elif k == "straight walls" and q not in fit:
                d = tuple(row["diagonal_class"])
                r = (q[0] ^ fit[0][0], q[1] ^ fit[0][1])
                rd = (r[0] * d[0] + r[1] * d[1]) & 1
                empty = t["sat"] + pats.get(0, 0)
                other = t["total"] - empty - pats.get(om, 0)
                exact, prob = formula_empty(L, M)
                rec = out["straight walls"].setdefault(f"{L}x{M}", {"cases": 0, "other patterns": 0, "exact counts equal": 0,
                                                                  "exact cases": 0, "max |z| of sampled counts": 0.0})
                rec["cases"] += 1
                rec["other patterns"] += other
                if row["mode"] == "e":
                    rec["exact cases"] += 1
                    rec["exact counts equal"] += empty == (0 if rd else exact)
                else:
                    p = 0.0 if rd else prob
                    n = t["total"]
                    sd = math.sqrt(max(n * p * (1 - p), 1e-12))
                    z = abs(empty - n * p) / sd if p > 0 else (0.0 if empty == 0 else float("inf"))
                    rec["max |z| of sampled counts"] = max(rec["max |z| of sampled counts"], round(z, 2))
        if k == "bending walls":
            (out["bending walls: selective (placement, torus) pairs"] if sel
             else out["bending walls: (placement, torus) pairs without a selective pattern"]).append(f"{R}@{L}x{M}")
        if single and glob:
            out["placements with single lines and global contradictions, by kind"].setdefault(k, []).append(f"{R}@{L}x{M}")
    out["bending walls: selective (placement, torus) pairs"] = len(out["bending walls: selective (placement, torus) pairs"])
    return out


# ------------------------------------------------------------------ main

def main() -> int:
    rng = random.Random(SEED)
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    pair = sorted(r["R"] for r in census if r["kind"] == "pair" and r["class"] == "TILING")
    three = sorted(r["R"] for r in census if r["kind"] == "three" and r["class"] == "TILING")
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    checks, controls = {}, {}

    # kinds
    kinds = {R: kind(R) for R in three}
    by_kind = {}
    for R, k in kinds.items():
        by_kind.setdefault(k, []).append(R)
    expected = {"h/v stripes": GROUPS["never"] - {191, 239}, "diagonal stripes": GROUPS["one-dimensional"] | {191, 239},
                "straight walls": GROUPS["saturated"], "bending walls": GROUPS["selective"]}
    checks["kinds"] = {k: sorted(v) for k, v in sorted(by_kind.items())}
    checks["kinds equal the groups of A"] = all(set(by_kind.get(k, [])) == v for k, v in expected.items()) and "other" not in by_kind
    checks["lone places in the constant frame (free, allowed)"] = {
        str(R): [sorted(s) for s in lone_sets(R)] for R in three if kinds[R] in ("straight walls", "bending walls")}
    print("kinds", checks["kinds equal the groups of A"], flush=True)

    # Proposition 1
    c3 = {R: clone3(R) for R in three}
    cp = {R: clone3(R) for R in pair}
    checks["Proposition 1(a)"] = {
        "three-place placements": len(three),
        "only projections, plus both constants exactly when U holds 000": sum(
            c3[R] == (PROJ | CONST if (R & comp(R)) & 1 else PROJ) for R in three),
        "two-literal placements": len(pair),
        "two-literal placements preserved by majority": sum(MAJ in cp[R] for R in pair)}
    classes = renaming_classes(three)
    mixed = [c for c in classes if {kinds[R] for R in c} & {"bending walls"} and {kinds[R] for R in c} - {"bending walls"}]
    checks["Proposition 1(b)"] = {"renaming classes": len(classes),
                                  "classes with their kinds": [[f"{R}:{kinds[R]}" for R in c] for c in classes],
                                  "classes containing a bending-wall and a rigid placement": len(mixed)}
    print("proposition 1", flush=True)

    # Theorem 2
    t2 = {"cases": 0, "stripe assignments satisfying every clause": 0, "excluded (diagonal class)": 0}
    for R in three:
        k = kinds[R]
        if k not in ("diagonal stripes", "h/v stripes"):
            continue
        for L, M in TORI:
            for q in TWISTS:
                for c in STRIPE_CLASSES:
                    F = stripe_assignment(R, L, M, q, c, k)
                    if F is None:
                        t2["excluded (diagonal class)"] += 1
                        assert norm(c) == norm(diagonal_class(L, M))
                        continue
                    t2["cases"] += 1
                    t2["stripe assignments satisfying every clause"] += strip_assignment_ok(R, L, M, q, rng.randrange(1 << (2 * L * M)), c, F)
    checks["Theorem 2"] = t2
    # controls: the opposite parity breaks the quasi-periodicity; diagonal stripes are not doubly allowed for wall placements
    bad_parity = wrong_kind = cases_p = cases_k = 0
    for R in three:
        k = kinds[R]
        for L, M in ((3, 3), (4, 5)):
            fit = fitting(R, L, M)
            for q in TWISTS:
                for c in CLASSES:
                    if norm(c) == norm(diagonal_class(L, M)):
                        continue
                    if k in ("diagonal stripes", "h/v stripes"):
                        F = stripe_assignment(R, L, M, q, c, k, wrong_parity=1)
                        cases_p += 1
                        bad_parity += not strip_assignment_ok(R, L, M, q, 0, c, F, 4)
                    elif c in odd_classes(CLASSES, fit, q):
                        D = abs(c[0] * L - c[1] * M)
                        F = lambda p, D=D: ((p[0] - p[1]) // D) & 1
                        cases_k += 1
                        wrong_kind += not strip_assignment_ok(R, L, M, q, 0, c, F, 4)
    controls["stripe assignments with the opposite parity that fail (must be all)"] = [bad_parity, cases_p]
    controls["diagonal stripes on wall placements along odd classes, all coins R, that fail (must be all)"] = [wrong_kind, cases_k]
    print("theorem 2", flush=True)

    # Theorem 3
    straight = [R for R in three if kinds[R] == "straight walls"]
    t3 = theorem3_checks(rng, straight)
    checks["Theorem 3"] = t3
    # control: the wall construction fails for configurations whose cylinders contradict (counted inside), and the frame
    # hypothesis holds: U has no lone-1 pattern and the allowed lone places omit 0 or 2
    controls["straight-wall placements whose constant frame flips place 1"] = sorted(R for R in straight if frame(R)[1])
    print("theorem 3", flush=True)

    # Proposition 4
    prop = []
    for R, q, x in SELECTIVE_EXAMPLES:
        fit = fitting(R, 3, 3)
        st = {c: certify(R, 3, 3, q, x, c) for c in CLASSES}
        odd = odd_classes(CLASSES, fit, q)
        S = [c for c in CLASSES if st[c]]
        prop.append({"placement": R, "kind": kinds[R], "twist": f"{q[0]}{q[1]}", "configuration": x,
                     "contradicts along": [list(c) for c in S],
                     "has assignments along (odd)": [list(c) for c in odd if st[c] is False],
                     "undetermined": [list(c) for c in CLASSES if st[c] is None],
                     "selective": len(S) >= 2 and all(c in odd for c in S) and any(st[c] is False for c in odd)})
    checks["Proposition 4"] = prop
    print("proposition 4", flush=True)

    # results of A
    rows = [json.loads(l) for l in A_ROWS.read_text().splitlines() if l.strip()]
    checks["results of A"] = a_results(rows, kinds)

    # Theorem 7
    rotating = [R for R in three if kinds[R] == "bending walls" and not lone_sets(R)[0]]
    t7 = theorem7_checks(rng, rotating, rows)
    checks["Theorem 7"] = t7
    print("theorem 7", flush=True)

    ar = checks["results of A"]
    sw = ar["straight walls"]
    ok = (checks["kinds equal the groups of A"]
          and checks["Proposition 1(a)"]["only projections, plus both constants exactly when U holds 000"] == 30
          and checks["Proposition 1(a)"]["two-literal placements preserved by majority"] == 24
          and checks["Proposition 1(b)"]["classes containing a bending-wall and a rigid placement"] == 5
          and t2["cases"] > 0 and t2["stripe assignments satisfying every clause"] == t2["cases"]
          and all(v[0] == v[1] > 0 for k, v in controls.items() if k.endswith("(must be all)"))
          and t3["undetermined"] == 0 and t3["all odd classes agree"] == t3["configurations"]
          and t3["assignments exactly when a wall construction verifies"] == t3["configurations"]
          and t3["relative twist odd on the diagonal: all contradict"] == t3["relative twist odd on the diagonal: configurations"] > 0
          and t3["with assignments"] > 0
          and all(p["selective"] and not p["undetermined"] for p in prop)
          and ar["diagonal stripes: patterns outside the diagonal class"] == 0 and ar["h/v stripes: nonzero patterns"] == 0
          and all(v["other patterns"] == 0 and v["exact counts equal"] == v["exact cases"] for v in sw.values())
          and all(v["max |z| of sampled counts"] < 5 for v in sw.values())
          and set(ar["placements with single lines and global contradictions, by kind"]) <= {"bending walls"}
          and t7["placements"] == [54, 109, 147, 151] and t7["one pinned value each"]
          and len(t7["exhaustive 3 x 3 histograms (16 classes) equal to A"]) == 16
          and all(t7["exhaustive 3 x 3 histograms (16 classes) equal to A"].values())
          and t7["undetermined"] == 0 and t7["certified configurations"] > 0
          and t7["predicted pattern equals the certified one"] == t7["certified configurations"] and t7["selective among them"] > 0)
    result["checks"], result["controls"] = checks, controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": checks, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
