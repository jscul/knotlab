"""Spin sectors of the knot's count (THREEFOLD-SPINSUM-20261030-001A).

For the incidence graph B of a three-fold space on a minimal map, an even subgraph chi (every vertex of even degree) has a homology class in
H_1(surface; Z_2), read by spin_lib.hclass.  At the knot's coupling x = i/sqrt(3) its weight is x^|chi| = (-1/3)^(|chi|/2) (|chi| is even in
a bipartite graph).  A spin structure is a quadratic form q on H_1; all of them are q_ref + (a linear functional), with q_ref the knot's
Cimasoni-Reshetikhin form (THREEFOLD-SPIN-20261030-001A).  The sector value of q is the q-signed sum of weights, normalized so that the
Arf-signed average over spin structures is a colouring count."""
import itertools
from fractions import Fraction as Fr
import spin_lib as S


def even_subgraphs(edges, avoid=None):
    """all even subgraphs (edge bit masks of the full graph) of the graph with the vertex `avoid` deleted"""
    keep = [k for k, (u, v) in enumerate(edges) if avoid not in (u, v)]
    fund = []
    for m in S.fundamental_cycles([edges[k] for k in keep]):
        fund.append(sum(1 << k for j, k in enumerate(keep) if m >> j & 1))
    out = []
    for coeffs in itertools.product((0, 1), repeat=len(fund)):
        Z = 0
        for c, m in zip(coeffs, fund):
            if c:
                Z ^= m
        out.append(Z)
    return out


def class_sums(evs, H1, x2=Fr(-1, 3)):
    """E_alpha: the weight x^|chi| = x2^(|chi|/2) summed over even subgraphs of class alpha"""
    E = {}
    for Z in evs:
        h = S.hclass(Z, H1)
        E[h] = E.get(h, 0) + x2 ** (bin(Z).count('1') // 2)
    return E


def classes_of(g):
    return list(itertools.product((0, 1), repeat=2 * g))


def spin_structures(qref, g):
    """all 4^g quadratic forms q_ref + beta (beta a linear functional in the class coordinates), as (beta, dict)"""
    cl = classes_of(g)
    return [(beta, {h: (qref[h] + sum(x * y for x, y in zip(beta, h))) % 2 for h in cl}) for beta in cl]


def arf(q, g):
    s = sum((-1) ** v for v in q.values())
    return 0 if s == 2 ** g else 1 if s == -(2 ** g) else None


def intersection(qref):
    """the intersection form recovered from a quadratic form: x.y = q(x + y) + q(x) + q(y)"""
    return lambda x, y: (qref[tuple(a ^ b for a, b in zip(x, y))] + qref[x] + qref[y]) % 2


def sector(q, E):
    return sum((-1) ** q[h] * w for h, w in E.items())


def induced(q, qref, realized):
    """q is the spin structure of some perfect matching D: q = q_ref + (a . -) with a = [D xor D0] realized"""
    dot = intersection(qref)
    return any(all(q[h] == (qref[h] + dot(a, h)) % 2 for h in q) for a in realized)
