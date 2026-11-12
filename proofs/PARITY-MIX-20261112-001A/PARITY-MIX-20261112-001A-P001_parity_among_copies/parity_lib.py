"""A parity knot among stitched copies (research/PARITY-MIX-20261112-001/preregistration.md, ticket A).

Copies of a harmony H (states W, P places) at (r, c) on the n x m repeat; at every cell the mixed knot (x, x + e2, x + e1) is either the
not-all-equal one-order stitch (as in SHIFT-LOCK-20261112-001) or a flip-blind parity knot: X(x) xor X(x + e2) xor X(x + e1) is
0...0 or 1...1 at its places (one hidden reference distinction per knot). Count r: the copies whose count along the first copy shift
is r. Everything is read up to flips: two states of a copy are equal up to a flip when they are equal or complements."""
import itertools
import random
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SHIFT-LOCK-20261112-001A/SHIFT-LOCK-20261112-001A-P001_two_shift_locks"))
import shift_lib as S  # noqa: E402

E = S.E


def harmonies():
    return S.harmonies()


def name(h):
    return S.name(h)


def setup(h):
    st = S.setup(h)
    P = st["P"]
    mask = (1 << P) - 1
    W = st["W"]
    index = {x: i for i, x in enumerate(W)}
    st["flip"] = [index[x ^ mask] for x in W]
    st["cls"] = [min(i, st["flip"][i]) for i in range(len(W))]
    return st


def flip_blind_triples(st):
    """ordered (u, v, w) in W^3 with u xor v xor w in {0...0, 1...1}"""
    W, P = st["W"], st["P"]
    mask = (1 << P) - 1
    Ws = set(W)
    n = 0
    for u in W:
        for v in W:
            w = u ^ v
            n += (w in Ws) + ((w ^ mask) in Ws)
    return n


def largest_subspace(st, cap=8):
    """the largest d such that some d-dimensional subspace U of F_2^P / <1...1> has every non-zero element a class of W"""
    W, P = st["W"], st["P"]
    mask = (1 << P) - 1
    canon = lambda x: min(x, x ^ mask)
    classes = sorted({canon(x) for x in W})
    cs = set(classes)
    best = 0

    def grow(span, basis_last):
        nonlocal best
        best = max(best, len(span).bit_length() - 1)
        if best >= cap:
            return
        for x in classes:
            if x <= basis_last or x in span:
                continue
            new = span | {canon(s ^ x) for s in span}
            if all(y in cs for y in new if y != 0):
                grow(new, x)
    grow({0}, -1)
    return best


def placements_all(n, m):
    return [frozenset(c for c in range(n * m) if (mask >> c) & 1) for mask in range(1 << (n * m))]


def translation_classes(n, m):
    """one placement per class under the translations of the n x m repeat, with the class size"""
    cells = n * m
    seen, out = set(), []
    for mask in range(1 << cells):
        if mask in seen:
            continue
        orbit = set()
        for dr in range(n):
            for dc in range(m):
                t = 0
                for c in range(cells):
                    if (mask >> c) & 1:
                        r, q = divmod(c, m)
                        t |= 1 << (((r + dr) % n) * m + (q + dc) % m)
                orbit.add(t)
        seen |= orbit
        out.append((frozenset(c for c in range(cells) if (mask >> c) & 1), len(orbit)))
    return out


def placements_sampled(n, m, ks, N, tag):
    """for each k in ks, N subsets of k cells drawn uniformly (seeded by tag, n, m, k, sample)"""
    out = []
    cells = list(range(n * m))
    for k in ks:
        for s in range(N):
            rng = random.Random("%s|%d|%d|%d|%d" % (tag, n, m, k, s))
            out.append((k, frozenset(rng.sample(cells, k))))
    return out


def knots(n, m):
    v = S.cell(n, m)
    return [(v(r, c), v(r, c + 1), v(r + 1, c)) for r in range(n) for c in range(m)]


def build(st, n, m, K, offset=0):
    """CNF for one copy of the arrangement: NAE stitch at cells not in K, flip-blind parity at cells in K; variables shifted by offset.
    Returns (clauses, next free variable, var)."""
    h, P = st["h"], st["P"]
    nae = [k for c, k in enumerate(knots(n, m)) if c not in K]
    cl, nv, var0 = E.build((n * m, nae), h, "one order")
    var = lambda x, i: var0(x, i) + offset
    cl = [[l + offset if l > 0 else l - offset for l in c] for c in cl]
    nxt = nv + offset + 1
    for c, (x, y, z) in enumerate(knots(n, m)):
        if c not in K:
            continue
        r = nxt
        nxt += 1
        for i in range(P):
            lits = [var(x, i), var(y, i), var(z, i), r]
            for signs in itertools.product((1, -1), repeat=4):
                if sum(1 for s in signs if s < 0) % 2 == 1:  # forbid the assignments of odd parity
                    cl.append([s * l for s, l in zip(signs, lits)])
    return cl, nxt, var


def eqmod_clauses(st, var1, var2, x, sel, nxt):
    """sel -> copy x equal up to a flip in the two copies of the arrangement (a fresh choice variable f per copy)"""
    P = st["P"]
    f = nxt
    nxt += 1
    cl = []
    for i in range(P):
        a, b = var1(x, i), var2(x, i)
        cl += [[-sel, f, a, -b], [-sel, f, -a, b], [-sel, -f, a, b], [-sel, -f, -a, -b]]
    return cl, nxt


def differ_mod_clauses(st, var1, var2, xs, sel, nxt):
    """sel -> some copy among xs differs in the two copies even up to a flip"""
    P = st["P"]
    cl, gs = [], []
    for x in xs:
        g = nxt
        nxt += 1
        gs.append(g)
        eqs, nes = [], []
        for i in range(P):
            a, b = var1(x, i), var2(x, i)
            d = nxt
            nxt += 1
            cl += [[-d, a, -b], [-d, -a, b]]  # d -> equal at i
            eqs.append(d)
            e = nxt
            nxt += 1
            cl += [[-e, a, b], [-e, -a, -b]]  # e -> unequal at i
            nes.append(e)
        cl.append([-g] + eqs)
        cl.append([-g] + nes)
    cl.append([-sel] + gs)
    return cl, nxt


def reach(st, n, m, K):
    """has a state; for each count r >= 1: flip-frozen, and fixed by count 0 up to flips"""
    cl1, nxt, var1 = build(st, n, m, K, 0)
    cl2, nxt2, var2 = build(st, n, m, K, nxt)
    nxt = nxt2
    v = S.cell(n, m)
    out = {"state": None, "frozen": [], "fixed": []}
    with Solver(name="cadical153", bootstrap_with=cl1) as s:
        out["state"] = s.solve()
    if not out["state"]:
        return out
    cl = cl1 + cl2
    A0 = nxt
    nxt += 1
    for c in range(m):
        c2, nxt = eqmod_clauses(st, var1, var2, v(0, c), A0, nxt)
        cl += c2
    D = {}
    for r in range(1, n):
        D[r] = nxt
        nxt += 1
        c2, nxt = differ_mod_clauses(st, var1, var2, [v(r, c) for c in range(m)], D[r], nxt)
        cl += c2
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        for r in range(1, n):
            frozen = not s.solve(assumptions=[D[r]])
            fixed = frozen or not s.solve(assumptions=[A0, D[r]])
            out["frozen"].append(frozen)
            out["fixed"].append(fixed)
    return out


def functional_slots(st):
    """for the not-all-equal stitch: for each slot, whether the classes of the other two members (up to flips) leave at most one class
    for it (worst case over all known pairs)"""
    R, cls, flip = st["R"], st["cls"], st["flip"]
    out = {}
    for slot in range(3):
        others = [j for j in range(3) if j != slot]
        seen = {}
        ok = True
        for t in R:
            key = (cls[t[others[0]]], cls[t[others[1]]])
            val = cls[t[slot]]
            if seen.setdefault(key, val) != val:
                ok = False
                break
        out[slot] = ok
    return out


def syntactic(st, n, m, K, func):
    """counts r >= 1 reached from count 0 by propagation up to flips: a knot with two known members whose relation forces the third
    (always for parity; for the not-all-equal stitch in its functional slots) makes the third known"""
    v = S.cell(n, m)
    known = {v(0, c) for c in range(m)}
    ks = knots(n, m)
    changed = True
    while changed:
        changed = False
        for c, t in enumerate(ks):
            unk = [j for j in range(3) if t[j] not in known]
            if len(unk) != 1:
                continue
            j = unk[0]
            if c in K or func[j]:
                known.add(t[j])
                changed = True
    return [all(v(r, c) in known for c in range(m)) for r in range(1, n)]


def cell_row(st, n, m, K, func):
    rc = reach(st, n, m, K)
    row = {"k": len(K), "state": rc["state"]}
    if not rc["state"]:
        return row
    syn = syntactic(st, n, m, K, func)
    row["flip-frozen counts"] = sum(rc["frozen"])
    row["counts fixed by count 0"] = sum(rc["fixed"])
    row["counts reached"] = sum(syn)
    row["fixed but unreached counts"] = sum(1 for f, z, y in zip(rc["fixed"], rc["frozen"], syn) if f and not z and not y)
    row["full fixing"] = all(rc["fixed"]) and not all(rc["frozen"])
    return row
