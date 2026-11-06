"""Signs interpolate away (PLAIN-COUNT-20261031-001A).

A negated incidence (point p, line l) is replaced by an unsigned long edge p - l_1 - p_1 - ... - l_k - p_k - l with k capped pairs
(cross_lib.long_edge). Between p and p_k it acts by 9^k (P+ + t P-) with t = (-1/3)^k, so a system with L negated incidences replaced
this way counts 9^(kL) q(t) for a polynomial q of degree at most L: q(-1) is the signed count and q(1) the count with the signs dropped.

The pieces of an instance are the components left once the junction squares' vertices are removed: a component holding page vertices is
that page (with any long edges and caps hanging in it), the rest is the host."""
import numpy as np
import networkx as nx
import sympy as sp
import cross_lib as X


def unsign(Bs, k, tag='u'):
    """a plain builder: every negated edge of Bs replaced by an unsigned long edge with k capped pairs"""
    B = X.Builder()
    B.g = Bs.g.copy()
    for n, e in enumerate(sorted(Bs.neg, key=str)):
        p, l = sorted(e, key=lambda v: 0 if X.is_point(v) else 1)
        B.g.remove_edge(p, l)
        X.long_edge(B, p, l, k, (tag, n))
    return B


def value_at(counts, L, t0):
    """q(t0) from plain counts at L + 1 lengths (dict k -> count)"""
    ks = sorted(counts)[:L + 1]
    assert len(ks) == L + 1
    rows = sp.Matrix([[sp.Rational(-1, 3) ** (k * j) for j in range(L + 1)] for k in ks])
    rhs = sp.Matrix([sp.Rational(counts[k], 9 ** (k * L)) for k in ks])
    a = rows.LUsolve(rhs)
    return sum(a[j] * sp.Integer(t0) ** j for j in range(L + 1))


def is_page(v):
    return len(v) == 3 and isinstance(v[1], tuple) and v[1][0] in ('Q', 'R')


def squares_of(B):
    tags = sorted({v[2] for v in B.g if v[1] == 'J'}, key=str)
    return [(('pt', 'J', j, 0), ('ln', 'J', j, 1), ('pt', 'J', j, 2), ('ln', 'J', j, 3)) for j in tags]


def leaves(B):
    """the planar pieces: the host with every junction square's edges, and one piece per page with its square's edges"""
    sqs = squares_of(B)
    sqv = {v for S in sqs for v in S}
    rest = B.g.subgraph([v for v in B.g if v not in sqv])
    host_vs, pages = set(), []
    for comp in nx.connected_components(rest):
        if any(is_page(v) for v in comp):
            att = {w for v in comp for w in B.g[v] if w in sqv}
            S = [s for s in sqs if set(s) & att]
            assert len(S) == 1
            pages.append((sorted(comp, key=str), S[0]))
        else:
            host_vs |= comp
    host = B.g.subgraph(host_vs | sqv).copy()
    for S in sqs:
        host.add_edges_from((S[i], S[(i + 1) % 4]) for i in range(4))
    out = [(host, sqs)]
    for comp, S in sorted(pages, key=lambda x: str(x[0][0])):
        g = B.g.subgraph(set(comp) | set(S)).copy()
        g.add_edges_from((S[i], S[(i + 1) % 4]) for i in range(4))
        out.append((g, [S]))
    return out


def certify(B, TW, AM):
    """a Pfaffian certificate: every piece planar, and the glued Kasteleyn signing leaves the instance non-colourable
    (THREEFOLD-AMPLITUDE C, Lemma 4). Returns (certified, pieces, glued signing)."""
    lv = leaves(B)
    planar = all(nx.check_planarity(g)[0] for g, s in lv)
    kap = TW.kasteleyn_tree_signing(lv)
    C = X.Builder()
    C.g, C.neg = B.g, set(kap)
    H, neg = C.system()
    return planar and not AM.colourable(H, neg), lv, kap


def _popcount(x):
    x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return (x * np.uint64(0x0101010101010101)) >> np.uint64(56)


def minimal_page_signs(Bs):
    """switch at vertices inside each page so that it carries as few negations as possible (exhaustive over all switchings inside the
    page, meet in the middle); switching leaves every count unchanged. Returns a builder on the same graph and {page: (before, after)}."""
    B = X.Builder()
    B.g = Bs.g
    neg = set(Bs.neg)
    report = {}
    for tag in sorted({v[1] for v in Bs.g if is_page(v)}, key=str):
        vs = sorted((v for v in Bs.g if is_page(v) and v[1] == tag), key=str)
        edges = sorted({frozenset((a, b)) for a in vs for b in Bs.g[a]}, key=str)
        assert len(edges) <= 64
        eid = {e: i for i, e in enumerate(edges)}
        sigma = np.uint64(sum(1 << eid[e] for e in edges if e in neg))
        masks = [np.uint64(sum(1 << eid[frozenset((v, w))] for w in Bs.g[v])) for v in vs]
        h = len(vs) // 2
        lo, hi = [np.uint64(0)], [np.uint64(0)]
        for m in masks[:h]:
            lo = lo + [a ^ m for a in lo]
        for m in masks[h:]:
            hi = hi + [b ^ m for b in hi]
        lo, hi = np.array(lo, dtype=np.uint64), np.array(hi, dtype=np.uint64)
        tot = _popcount(lo[:, None] ^ hi[None, :] ^ sigma)
        i, j = np.unravel_index(int(np.argmin(tot)), tot.shape)
        best = int(lo[i] ^ hi[j] ^ sigma)
        before = sum(1 for e in edges if e in neg)
        neg -= set(edges)
        neg |= {edges[t] for t in range(len(edges)) if best >> t & 1}
        report[tag] = (before, bin(best).count("1"))
    B.neg = neg
    return B, report
