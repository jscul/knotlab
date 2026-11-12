"""Lines in the increments (research/LINE-LOCK-20261112-001/preregistration.md, ticket A).

A harmony H (kinds (0, a, b), period P, states W as P-bit words) stitched in one order: R(u, v, w) iff NAE(u_i, v_{i+a}, w_{i+b}) for
every kind and place i. For one orbit O of the group <shift, flip> (which acts on O simply transitively through Q, the group of
shifts by the orbit's own period with the flip, the flip identified with a half shift when the orbit is antiperiodic), the increments
are A = {(y, z) in Q^2 : R(u, y.u, z.u)}. A cyclic subgroup C = <(g, h)> inside A, or a coset d + C inside A, is listed with its order
and with the multiplier lambda (h = lambda g when h lies in <g>), and called degenerate when it is one of {(a, 0)}, {(a, a)}, {(0, b)}
(states constant along a direction)."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series"))
sys.path.insert(0, str(ROOT / "proofs/ODD-FAMILY-20261112-001A/ODD-FAMILY-20261112-001A-P001_symmetric_steps"))


def rot(x, s, P):
    s %= P
    mask = (1 << P) - 1
    return ((x >> s) | (x << (P - s))) & mask


def census_harmonies():
    """the 66 harmonies of span at most 8 (every period), as dicts with P, kinds, states (ints), name"""
    import nest_lib as N
    out = []
    for h in N.harmonies(max_span=8, max_period=10 ** 9):
        W = sorted({sum(b << i for i, b in enumerate(w)) for w in N.states(h)})
        out.append({"name": " + ".join(h["orbits"]), "P": h["P"], "kinds": [tuple(k) for k in h["kinds"]], "states": W,
                    "source": "span <= 8"})
    return out


ODD_SETS = [(61, (1, 2, 11, 22, 39, 50, 59, 60)), (61, (1, 11, 25, 30, 31, 36, 50, 60)),
            (73, (1, 2, 19, 27, 46, 54, 71, 72)), (73, (1, 23, 27, 36, 37, 46, 50, 72)),
            (193, (1, 2, 31, 54, 65, 81, 112, 128, 139, 162, 191, 192)), (193, (1, 3, 25, 50, 81, 95, 98, 112, 143, 168, 190, 192)),
            (193, (1, 27, 56, 64, 81, 96, 97, 112, 129, 137, 166, 192))]


def odd_harmonies():
    """the 7 odd step sets of ODD-FAMILY-20261112-001 (3 up to a multiplier), with every state enumerated"""
    import fam_lib as F
    from pysat.solvers import Solver
    out = []
    for n, S in ODD_SETS:
        kinds = [tuple(k) for k in F.kinds(S, n)]
        cl = []
        for (_, a, b) in kinds:
            for i in range(n):
                t = [i + 1, (i + a) % n + 1, (i + b) % n + 1]
                cl.append(t)
                cl.append([-x for x in t])
        W = []
        with Solver(name="cadical153", bootstrap_with=cl) as s:
            while s.solve():
                m = s.get_model()
                x = sum(1 << i for i in range(n) if m[i] > 0)
                W.append(x)
                s.add_clause([-(i + 1) if (x >> i) & 1 else (i + 1) for i in range(n)])
        out.append({"name": "odd %d %s" % (n, list(S)), "P": n, "kinds": kinds, "states": sorted(W), "source": "odd step set"})
    return out


def nae_ok(u, y, z, kinds, P):
    mask = (1 << P) - 1
    for (_, a, b) in kinds:
        ya, zb = rot(y, a, P), rot(z, b, P)
        if (u & ya & zb) | (~u & ~ya & ~zb & mask):
            return False
    return True


def orbits(h):
    """the orbits of <shift, flip> on the states: (representative, own period p, antiperiodic?)"""
    P, W = h["P"], set(h["states"])
    mask = (1 << P) - 1
    seen, out = set(), []
    for u in sorted(W):
        if u in seen:
            continue
        p = next(d for d in range(1, P + 1) if P % d == 0 and rot(u, d, P) == u)
        anti = any(rot(u, a, P) == (u ^ mask) for a in range(p))
        orb = {rot(u, a, P) for a in range(p)} | {rot(u, a, P) ^ mask for a in range(p)}
        seen |= orb
        out.append((u, p, anti))
    return out


def group(p, anti):
    """Q as a list of elements (a, e) and its addition; with an antiperiodic orbit the flip is a half shift (e = 0 only, p even)"""
    if anti:
        els = [(a, 0) for a in range(p)]
        add = lambda x, y: ((x[0] + y[0]) % p, 0)
    else:
        els = [(a, e) for e in (0, 1) for a in range(p)]
        add = lambda x, y: ((x[0] + y[0]) % p, x[1] ^ y[1])
    return els, add


def act(u, g, P, anti, p):
    a, e = g
    x = rot(u, a, P)
    return x ^ ((1 << P) - 1) if e else x


def increments(h, u, p, anti):
    P = h["P"]
    els, add = group(p, anti)
    st = {g: act(u, g, P, anti, p) for g in els}
    A = {(g, k) for g in els for k in els if nae_ok(u, st[g], st[k], h["kinds"], P)}
    return els, add, A


def order(g, add, zero):
    k, x = 1, g
    while x != zero:
        x = add(x, g)
        k += 1
    return k


def multiples(gen, add, zero):
    out, x = [zero], gen
    while x != zero:
        out.append(x)
        x = add(x, gen)
    return out


def subgroups_inside(els, add, A, with_cosets=True):
    """cyclic subgroups C = <(g, h)> of Q^2 of order >= 2 with C inside A, and cosets d + C inside A (d not in C); one entry per
    distinct set"""
    zero = (0, 0)
    add2 = lambda x, y: (add(x[0], y[0]), add(x[1], y[1]))
    z2 = (zero, zero)
    found, cos = {}, {}
    for gen in A:
        if gen == z2:
            continue
        mult = multiples(gen, add2, z2)
        if all(m in A for m in mult):
            key = frozenset(mult)
            found.setdefault(key, gen)
    if with_cosets:
        # cosets d + C inside A, d not in C (C need not lie in A): d and d + g are both in A, so g is a difference of two points of A
        for d in A:
            for gen in A:
                g = (add(gen[0], (inv(d[0], add, els))), add(gen[1], inv(d[1], add, els)))  # the step from d to another point of A
                if g == z2:
                    continue
                mult = multiples(g, add2, z2)
                if len(mult) < 2:
                    continue
                pts = frozenset(add2(d, m) for m in mult)
                if z2 in pts:
                    continue
                if all(x in A for x in pts):
                    cos.setdefault(pts, (d, g))
    return found, cos


def inv(x, add, els):
    for y in els:
        if add(x, y) == (0, 0):
            return y


def mul(k, x, add, zero):
    y = zero
    for _ in range(k):
        y = add(y, x)
    return y


def odd_prime_factors(k):
    out, d = [], 3
    while d * d <= k:
        if k % d == 0:
            out.append(d)
            while k % d == 0:
                k //= d
        d += 2
    if k > 2:
        out.append(k)
    return out


def classify(gen, k, add):
    """for a generator of order k: at each odd prime q dividing k, the order-q element (k/q).gen = (g', h') and whether it is genuine
    (g' != 0, h' != 0, g' != h'), with lambda = h'/g' in Z_q when h' lies in <g'>"""
    zero = (0, 0)
    out = {}
    for q in odd_prime_factors(k):
        g2 = mul(k // q, gen[0], add, zero)
        h2 = mul(k // q, gen[1], add, zero)
        genuine = g2 != zero and h2 != zero and g2 != h2
        lam = None
        if g2 != zero:
            x = zero
            for j in range(q):
                if x == h2:
                    lam = j
                    break
                x = add(x, g2)
        out[str(q)] = {"genuine": genuine, "lambda": lam}
    return out


def f4_blocks(els, add, A, p, anti):
    """the two Z2 x Z2 graphs {0, (k, e), (e, k+e), (k+e, k)} and mirror, k the flip and e the half shift (orbit not antiperiodic, p
    even): inside A?"""
    if anti or p % 2:
        return []
    k, e = (0, 1), (p // 2, 0)
    ke = add(k, e)
    z = (0, 0)
    out = []
    for name, pts in (("graph", [(z, z), (k, e), (e, ke), (ke, k)]), ("mirror", [(z, z), (e, k), (ke, e), (k, ke)])):
        if all(x in A for x in pts):
            out.append(name)
    return out


def free_pairs(els, add, A):
    """cyclic subgroups H of Q of order >= 2 with H x H inside A"""
    zero = (0, 0)
    out = []
    seen = set()
    for g in els:
        if g == zero:
            continue
        H = frozenset(multiples(g, add, zero))
        if H in seen:
            continue
        seen.add(H)
        if all((x, y) in A for x in H for y in H):
            out.append({"generator": list(g), "order": len(H)})
    return out


def free_site(h):
    """a state with a free site on Z: flipping one place of its periodic extension keeps every knot (window of 3P around it)"""
    P, kinds = h["P"], h["kinds"]
    span = max(b for (_, a, b) in kinds)
    L = 3 * max(P, span + 1)
    for u in h["states"]:
        w = [(u >> (i % P)) & 1 for i in range(L)]
        c = L // 2
        for shift in range(P):
            pos = c + shift
            w2 = list(w)
            w2[pos] ^= 1
            ok = True
            for (_, a, b) in kinds:
                for j in (pos, pos - a, pos - b):
                    if 0 <= j and j + b < L and w2[j] == w2[j + a] == w2[j + b]:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return {"state": u, "place": shift}
    return None


def summarise(h):
    out = []
    for (u, p, anti) in orbits(h):
        els, add, A = increments(h, u, p, anti)
        subs, cos = subgroups_inside(els, add, A)
        rows = []
        for key, gen in subs.items():
            rows.append({"generator": [list(gen[0]), list(gen[1])], "order": len(key), "odd parts": classify(gen, len(key), add)})
        crow = []
        for key, (d, g) in cos.items():
            crow.append({"offset": [list(d[0]), list(d[1])], "generator": [list(g[0]), list(g[1])], "order": len(key),
                         "odd parts": classify(g, len(key), add), "offset without flips": d[0][1] == 0 and d[1][1] == 0})
        gen_rows = [r for r in rows if any(v["genuine"] for v in r["odd parts"].values())]
        gen_cos = [r for r in crow if any(v["genuine"] for v in r["odd parts"].values())]
        out.append({"orbit period": p, "antiperiodic": anti, "Q": len(els), "A": len(A),
                    "cyclic subgroups inside": len(rows), "cosets inside": len(crow),
                    "genuine subgroups": gen_rows, "F4 blocks": f4_blocks(els, add, A, p, anti),
                    "free pairs": free_pairs(els, add, A),
                    "genuine cosets": gen_cos, "genuine cosets a lag can give": [r for r in gen_cos if r["offset without flips"]]})
    return out
