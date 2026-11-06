"""Three-fold contacts, the dual configuration and the Fano gadgets (SPACE-SELECTION-20261030-001C); uses gadget_lib of ticket A.

A gadget is three-fold when every inner vertex lies in exactly three triangles.  Its dual configuration has the triangles as points and the
inner vertices as lines (triples of triangles).  Phases (sectors) are signs on the triangles; a phase assignment is proper when no line is
monochromatic.  Exact arithmetic at zeta = exp(i pi/3) is done in Z[zeta] / (zeta^2 - zeta + 1), elements as pairs (a, b) = a + b zeta."""
import itertools
import gadget_lib as G

FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def three_fold(cx):
    inc = G.incidences(cx)
    return all(len(inc[v]) == 3 for v in inc if v not in cx[2])


def three_fold_odd(cx):
    """every contact lies in exactly three triangles with an odd number of base incidences (then exactly one, as they sum to n - 1)"""
    inc = G.incidences(cx)
    return all(len(inc[v]) == 3 and sum(1 for t, r in inc[v] if r == 0) % 2 == 1 for v in inc if v not in cx[2])


def dual_lines(cx):
    inc = G.incidences(cx)
    return [tuple(sorted(t for t, r in inc[v])) for v in sorted(inc) if v not in cx[2]]


def nae_counts(cx):
    """N*(eps): proper phase assignments of the dual configuration with corner-triangle phases eps"""
    n = len(cx[1])
    lines = dual_lines(cx)
    tA, tB, tC = G.corner_triangles(cx)
    N = {e: 0 for e in itertools.product((1, -1), repeat=3)}
    for sig in itertools.product((1, -1), repeat=n):
        if all(not (sig[a] == sig[b] == sig[c]) for a, b, c in lines):
            N[(sig[tA], sig[tB], sig[tC])] += 1
    return N


def corner_sign(cx, e):
    """prod over corner triangles t of eps_t^(number of corners in t)"""
    tA, tB, tC = G.corner_triangles(cx)
    s = 1
    for t, et in ((tA, e[0]), (tB, e[1]), (tC, e[2])):
        s *= et
    return s


# ----------------------------------------------------------------------------- Z[zeta], zeta^2 = zeta - 1
def zmul(x, y):
    a, b = x
    c, d = y
    # (a + b z)(c + d z) = ac + (ad + bc) z + bd z^2, z^2 = z - 1
    return (a * c - b * d, a * d + b * c + b * d)


ZPOW = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]     # zeta^k for k mod 6


def laurent_at_zeta6(L):
    a = b = 0
    for k, c in L.items():
        p = ZPOW[k % 6]
        a += c * p[0]
        b += c * p[1]
    return (a, b)


def zpow(x, k):
    out = (1, 0)
    for _ in range(k):
        out = zmul(out, x)
    return out


MINUS_I_SQRT3 = (1, -2)   # -i sqrt3 = 1 - 2 zeta


def fano_gadgets():
    """all role assignments of the Fano plane with corner triangles on the line (0, 1, 2) and one base incidence per inner line, as
    canonical gadget keys (triangle of A first)"""
    L0, inner = FANO[0], FANO[1:]
    at = {p: [l for l in inner if p in l] for p in range(7)}
    keys = set()
    for tA, tB, tC in itertools.permutations(L0):
        choices = []
        for p in range(7):
            ls = at[p]
            if p == tA:
                opts = [{ls[0]: 1, ls[1]: 2}, {ls[0]: 2, ls[1]: 1}]
            elif p == tB:
                opts = [{ls[0]: 0, ls[1]: 2}, {ls[0]: 2, ls[1]: 0}]
            elif p == tC:
                opts = [{ls[0]: 0, ls[1]: 1}, {ls[0]: 1, ls[1]: 0}]
            else:
                opts = [dict(zip(ls, perm)) for perm in itertools.permutations(range(3))]
            choices.append(opts)
        for pick in itertools.product(*choices):
            if any(sum(1 for p in l if pick[p][l] == 0) != 1 for l in inner):
                continue
            order = [tA] + [p for p in range(7) if p != tA]
            ti = {p: i for i, p in enumerate(order)}
            blocks = [tuple((ti[p], pick[p][l]) for p in l) for l in inner]
            keys.add(G.canonical(7, ti[tB], ti[tC], blocks))
    return keys


def two_colourable(edges, vertices):
    vs = sorted(vertices)
    for c in itertools.product((0, 1), repeat=len(vs) - 1):
        col = dict(zip(vs, (0,) + c))
        if all(not (col[a] == col[b] == col[e]) for a, b, e in edges):
            return True
    return False
