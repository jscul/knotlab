"""ops.py: values as operators under a commutation rule, for patterns whose distinctions have one or two holders
(EVENTUAL-R-20261126-001, README.md). A value is a signed Pauli product that squares to +1 (the 20 November census's
encoding, i^p X^x Z^z, and its multiplication); the values of the distinctions in `anti` fail to commute, all others
commute (A_i = X_i Z^{j<i, (i, j) in anti}). A knot's operator is the product of its places' values. The state is the
one the signed knots fix: every knot even except, in each closed component (no loose distinction), its last knot,
whose sign is the one the component's product forces. A read set P is a set of distinctions whose values commute; its
laws are every product of knots whose distinctions left over after cancelling lie inside P, each with its sign."""
import sys, itertools
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules'))
from census import product                      # noqa: E402
I = (0, 0, 0)


def commute(a, b):
    return ((a[1] & b[2]).bit_count() + (a[2] & b[1]).bit_count()) % 2 == 0


def holders(knots):
    h = {}
    for u, k in enumerate(knots):
        for d in k: h.setdefault(d, []).append(u)
    return h


def coheld(knots):
    """pairs of distinctions some knot holds both of"""
    out = set()
    for k in knots:
        for a, b in itertools.combinations(sorted(set(k)), 2): out.add((a, b))
    return out


def rule_R(knots_for_rule, m):
    """anticommuting pairs under R read off `knots_for_rule`: distinctions no knot of it holds both of"""
    co = coheld(knots_for_rule)
    return {(a, b) for a, b in itertools.combinations(range(m), 2) if (a, b) not in co}


def realise(m, anti):
    ops = []
    for i in range(m):
        z = sum(1 << j for j in range(i) if (j, i) in anti)
        ops.append((0, 1 << i, z))
    return ops


def mul(ops):
    acc = I
    for o in ops: acc = product(acc, o)
    return acc


def knot_ops(knots, vals):
    return [mul([vals[d] for d in sorted(k)]) for k in knots]


def components(knots):
    G = nx.Graph(); G.add_nodes_from(range(len(knots)))
    for d, hs in holders(knots).items():
        if len(hs) == 2: G.add_edge(*hs)
    return [sorted(c) for c in nx.connected_components(G)]


def signs(knots, K):
    """every knot even but the last of each closed component, which takes the sign its component's product forces;
    returns (signs, list of closed components with their forced sign)"""
    s = [0] * len(knots); h = holders(knots); closed = []
    for comp in components(knots):
        if all(len(h[d]) == 2 for u in comp for d in knots[u]):
            tot = mul([K[u] for u in comp])
            assert tot in (I, (2, 0, 0)), 'a closed component multiplies to a scalar when its knots commute'
            s[comp[-1]] = int(tot == (2, 0, 0)); closed.append((comp, s[comp[-1]]))
    return s, closed


def r1(K, among=None):
    idx = range(len(K)) if among is None else among
    return all(commute(K[u], K[v]) for u, v in itertools.combinations(idx, 2))


def laws(knots, vals, K, s, P, use):
    """the laws on read set P from the knots in `use`: a reduced basis of (subset of P as a bitmask, parity) pairs;
    each law is a product of knots whose leftover distinctions lie in P, its parity the sign of that product"""
    P = set(P); stars = {u: sum(1 << d for d in knots[u]) for u in use}
    outside = lambda x: x & ~sum(1 << d for d in P)
    # solve for sets U of knots with outside(XOR of stars) == 0: Gaussian elimination on (outside part | U indicator)
    use = list(use); n = len(use)
    rows = [(outside(stars[u]), 1 << j) for j, u in enumerate(use)]
    piv = {}; kernel = []
    for x, tag in rows:
        while x:
            h = x.bit_length() - 1
            if h in piv: px, pt = piv[h]; x ^= px; tag ^= pt
            else: piv[h] = (x, tag); break
        if not x: kernel.append(tag)
    out = []
    for tag in kernel:
        U = [use[j] for j in range(n) if tag >> j & 1]
        g = mul([(2 * s[u], 0, 0) for u in U] + [K[u] for u in U])
        S = 0
        for u in U: S ^= stars[u]
        if S == 0:
            assert g in (I, (2, 0, 0)); out.append((0, g[0] // 2)); continue
        rest = product(g, mul([vals[d] for d in sorted(d for d in P if S >> d & 1)]))
        assert rest in (I, (2, 0, 0)), 'a law on P is a signed product of P\'s values'
        out.append((S, rest[0] // 2))
    return reduce_laws(out)


def reduce_laws(pairs):
    piv = {}; bad = False
    for S, b in pairs:
        while S:
            h = S.bit_length() - 1
            if h in piv: S ^= piv[h][0]; b ^= piv[h][1]
            else: piv[h] = (S, b); break
        if not S and b: bad = True
    # fully reduce for a canonical form
    keys = sorted(piv)
    for h in keys:
        S, b = piv[h]
        for h2 in keys:
            if h2 != h and piv[h2][0] >> h & 1:
                piv[h2] = (piv[h2][0] ^ S, piv[h2][1] ^ b)
    return (tuple(sorted(piv.values())), bad)


def maximal_read_sets(knots, co=None):
    """the maximal sets of distinctions whose values commute under R (pairwise held by a common knot)"""
    co = coheld(knots) if co is None else co
    G = nx.Graph(); G.add_nodes_from(holders(knots)); G.add_edges_from(co)
    return [sorted(c) for c in nx.find_cliques(G)]
