"""Shared-runner job for JOIN-GROWTH-20261118-001B-E001: the frozen census of joins.

Every case is a bare start (joinlib.bare_sizes: each knot max(3, shared + round-1 demand) places plus its listed surplus
distinctions), grown under the fewest counts to 80 rounds, 250,000 junctions or 900 seconds.  Families (research/
JOIN-GROWTH-20261118-001/preregistration.md):

  A1-A6  single rings of knots with adjuncts, each with an annihilator predicted by the product law (P1-P6);
  B      exploratory adjuncts outside the law (no prediction);
  C      two rings joined (P9);
  D      the census of small joins of a ring of five and a two-fold piece (P7 on the D and K joins, P8 on all);
  E      joins of two two-fold pieces, no ring (P10).

The return equation of the product law: y^n (1 + y)^j prod_k F_k(y) = 1, with F_s = 1 + y (1 + y)^s for an adjunct knot with s
surplus distinctions (at one remove from the ring, or at two removes with s >= 2) and F = 1/(1 - y) for a knot at two removes whose
one surplus distinction is the floor's (the renewing offshoot).  Its annihilator: the reversed polynomial of
y^n (1 + y)^j prod N_k - prod D_k, times the reversed D_k."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import joinlib as J  # noqa: E402
import reclib as R  # noqa: E402

ROUNDS, MAXJ, TMAX = 80, 250000, 900.0


# -- delay series as (numerator, denominator) polynomials in y, constant term first ------------------------------------------------
def F_surplus(s):
    """1 + y (1 + y)^s."""
    return R.polyadd([1], [0] + R.polypow([1, 1], s)), [1]


RENEW = ([1], [1, -1])          # 1 / (1 - y)
SPARE = ([1, 1], [1])           # a surplus distinction on a ring knot: 1 + y


def annihilator(n, factors):
    N, D = [1], [1]
    for a, b in factors:
        N = R.polymul(N, a)
        D = R.polymul(D, b)
    E = R.polyadd([0] * n + N, R.polyneg(D))
    while len(E) > 1 and E[-1] == 0:
        E.pop()
    p = R.reverse(E)
    for _, b in factors:
        if len(b) > 1:
            p = R.polymul(p, R.reverse(b))
    if p[-1] < 0:
        p = R.polyneg(p)
    return p


# -- starts ----------------------------------------------------------------------------------------------------------------------
class Start:
    def __init__(self, n):
        self.ring_n = n
        self.k = n
        self.edges = J.ring_edges(n)
        self.surplus = {}
        self.factors = []

    def knot(self, at, s=0):
        """A new knot sharing one distinction with each knot in `at`, with s listed surplus distinctions."""
        new = self.k
        self.k += 1
        for a in (at if isinstance(at, (list, tuple)) else [at]):
            self.edges.append((a, new))
        if s:
            self.surplus[new] = self.surplus.get(new, 0) + s
        return new

    def spare(self, ring_knot, s=1):
        self.surplus[ring_knot] = self.surplus.get(ring_knot, 0) + s
        self.factors += [SPARE] * s
        return self

    def payload(self, family, prediction=True, note=''):
        return {'family': family, 'n': self.k, 'edges': [list(e) for e in self.edges],
                'surplus': {str(k): v for k, v in self.surplus.items()},
                'annihilator': annihilator(self.ring_n, self.factors) if prediction else None, 'note': note}


def lone(st, r, s):
    """A lone adjunct of s listed surplus distinctions at ring knot r: one remove, F_s (its bare places are 1 + 2)."""
    st.knot(r, s)
    st.factors.append(F_surplus(s))


def pair(st, r, a, b):
    """A two-fold piece (A touching r, B touching A) with listed surplus a on A and b on B.  A: one remove, F_a.  B: two removes,
    bare places 1 shared + 1 demand, so the floor gives it one surplus distinction: s_B = b + 1, F = 1/(1 - y) when s_B = 1, else
    F_(s_B)."""
    A = st.knot(r, a)
    st.knot(A, b)
    st.factors.append(F_surplus(a))
    st.factors.append(RENEW if b == 0 else F_surplus(b + 1))


def two_rings(n, m, how, spare_far=False):
    st = Start(n)
    off = n
    st.k = n + m
    st.edges += J.ring_edges(m, off)
    if how == 'D':
        st.edges.append((0, off))
    elif how == 'K':                      # a shared knot: ring 2's knot 0 is ring 1's knot 0
        st.k = n + m - 1
        st.edges = J.ring_edges(n) + [(0, off)] + [(off + i, off + i + 1) for i in range(m - 2)] + [(off + m - 2, 0)]
    elif how == 'P1':
        K = st.k
        st.k += 1
        st.edges += [(0, K), (K, off)]
    if spare_far:
        st.surplus[2] = 1
    return st


def cases():
    out = []
    # A1: lone adjunct with s surplus on rings of 7 and 9, and s = 4 on the ring of five
    for n, s in [(7, 1), (7, 2), (7, 3), (9, 1), (9, 2), (5, 4)]:
        st = Start(n)
        lone(st, 0, s)
        out.append((f'A1-n{n}-s{s}', st.payload('A1')))
    # A2: products on separate ring knots, positions varied
    for name, n, adj, spares in [('n5-s11-at01', 5, [(0, 1), (1, 1)], []), ('n5-s11-at02', 5, [(0, 1), (2, 1)], []),
                                 ('n7-s12-at03', 7, [(0, 1), (3, 2)], []), ('n7-s12-at01', 7, [(0, 1), (1, 2)], []),
                                 ('n5-s2-spare3', 5, [(0, 2)], [3]), ('n7-s111-at024', 7, [(0, 1), (2, 1), (4, 1)], []),
                                 ('n5-s02-at02-spare4', 5, [(0, 0), (2, 2)], [4]), ('n9-s3-spare4', 9, [(0, 3)], [4])]:
        st = Start(n)
        for r, s in adj:
            lone(st, r, s)
        for q in spares:
            st.spare(q)
        out.append((f'A2-{name}', st.payload('A2')))
    # A3: two lone adjuncts on the same ring knot
    for name, n, ss in [('n5-s00', 5, (0, 0)), ('n5-s01', 5, (0, 1)), ('n7-s00', 7, (0, 0))]:
        st = Start(n)
        for s in ss:
            lone(st, 0, s)
        out.append((f'A3-{name}', st.payload('A3')))
    # A4: the bare hanging pair on rings of 7 and 9
    for n in (7, 9):
        st = Start(n)
        pair(st, 0, 0, 0)
        out.append((f'A4-n{n}', st.payload('A4')))
    # A5: hanging pairs with surplus (listed a on A, b on B, b >= 1)
    for n, a, b in [(5, 1, 2), (5, 2, 2), (5, 3, 1), (7, 1, 1), (7, 2, 1)]:
        st = Start(n)
        pair(st, 0, a, b)
        out.append((f'A5-n{n}-a{a}-b{b}', st.payload('A5')))
    # A6: a ring surplus distinction beside a hanging pair (listed a = 1, b = 1), at r or two away
    for q in (0, 2):
        st = Start(5)
        pair(st, 0, 1, 1)
        st.spare(q)
        out.append((f'A6-n5-a1-b1-spare{q}', st.payload('A6')))
    # B: exploratory adjuncts outside the law
    st = Start(5); A = st.knot(0); B = st.knot(A); st.knot(B)
    out.append(('B-chain3-bare', st.payload('B', False, 'chain of three at one, two and three removes')))
    st = Start(5); A = st.knot(0, 1); B = st.knot(A, 1); st.knot(B, 1)
    out.append(('B-chain3-s111', st.payload('B', False, 'chain of three, one listed surplus each')))
    st = Start(5); st.edges += [(0, 5), (0, 5)]; st.k = 6
    out.append(('B-double-share', st.payload('B', False, 'a knot sharing two distinctions with r')))
    st = Start(5); st.knot([0, 2])
    out.append(('B-chord-02', st.payload('B', False, 'a knot touching ring knots 0 and 2')))
    st = Start(5); st.knot([0, 1])
    out.append(('B-chord-01', st.payload('B', False, 'a knot touching ring knots 0 and 1')))
    st = Start(7); st.knot([0, 3])
    out.append(('B-chord-n7-03', st.payload('B', False, 'a knot touching ring knots 0 and 3 of a ring of seven')))
    # C: two rings joined
    for name, n, m, how, sp in [('5-5-K', 5, 5, 'K', False), ('5-5-P1', 5, 5, 'P1', False), ('5-7-D', 5, 7, 'D', False),
                                ('7-7-D', 7, 7, 'D', False), ('5-5-D-spare', 5, 5, 'D', True), ('5-9-D', 5, 9, 'D', False)]:
        out.append((f'C-{name}', two_rings(n, m, how, sp).payload('C', False, 'two rings')))
    # D: small joins of a ring of five (bare, or one surplus at r, r + 1 or r + 2) and a two-fold piece
    ring_variants = [('none', None), ('at-r', 0), ('at-r1', 1), ('at-r2', 2)]
    for vname, q in ring_variants:
        for a in range(3):
            for b in range(3):
                st = Start(5)
                pair(st, 0, a, b)
                if q is not None:
                    st.spare(q)
                out.append((f'D-D-{vname}-a{a}-b{b}', st.payload('D', True, 'shared distinction: A at one remove')))
        for b in range(3):
            st = Start(5)
            lone(st, 0, b)
            if q is not None:
                st.spare(q)
            out.append((f'D-K-{vname}-b{b}', st.payload('D', True, 'shared knot: r is A, B touches r')))
        for a in range(3):
            for b in range(3):
                st = Start(5)
                K = st.knot(0)
                A = st.knot(K, a)
                st.knot(A, b)
                if q is not None:
                    st.surplus[q] = st.surplus.get(q, 0) + 1
                out.append((f'D-P1-{vname}-a{a}-b{b}', st.payload('D', False, 'path of one knot')))
    for a in range(3):
        for b in range(3):
            st = Start(5)
            K1 = st.knot(0)
            K2 = st.knot(K1)
            A = st.knot(K2, a)
            st.knot(A, b)
            out.append((f'D-P2-none-a{a}-b{b}', st.payload('D', False, 'path of two knots')))
    # E: two two-fold pieces joined, no ring (pairs of knots of three places alone; here bare plus listed surplus)
    for name, edges, sp in [('D-b', [(0, 1), (2, 3), (1, 2)], {}), ('D-s2', [(0, 1), (2, 3), (1, 2)], {0: 2, 3: 2}),
                            ('D-ends', [(0, 1), (2, 3), (0, 2)], {1: 2, 3: 2}), ('K-b', [(0, 1), (1, 2)], {0: 2, 2: 2}),
                            ('P1-b', [(0, 1), (3, 4), (1, 2), (2, 3)], {0: 2, 4: 2}), ('D-s1', [(0, 1), (2, 3), (1, 2)], {0: 1, 3: 1})]:
        n = 1 + max(max(e) for e in edges)
        out.append((f'E-{name}', {'family': 'E', 'n': n, 'edges': [list(e) for e in edges],
                                  'surplus': {str(k): v for k, v in sp.items()}, 'annihilator': None, 'note': 'no ring'}))
    return out


def run(case_id, payload):
    edges = [tuple(e) for e in payload['edges']]
    sizes = J.bare_sizes(payload['n'], edges, payload['surplus'])
    g = J.grow(sizes, edges, rounds=ROUNDS, maxj=MAXJ, tmax=TMAX)
    c = g['counts']
    res = dict(g, sizes=sizes)
    res['minimal'] = R.minimal_recurrence(c)
    p = payload['annihilator']
    if p is not None:
        res['annihilated_from'] = R.first_round_annihilated(p, c, last_needed=3)
        res['predicted_rate'] = R.dominant_root(p)
    return res


if __name__ == '__main__':
    cs = cases()
    print(len(cs), 'cases')
    import collections
    print(collections.Counter(p['family'] for _, p in cs))
