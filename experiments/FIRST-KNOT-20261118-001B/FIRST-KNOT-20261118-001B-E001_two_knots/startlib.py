"""Growth from a start of several parity knots (FIRST-KNOT-20261118-001B).

Reuses the joining policy and count rules of FRESH-COUNT-20261118-001B's freelib.py (imported from that closed record) and adds:
a presentation whose round 0 is a given set of junctions, and the implied-parity test by GF(2) elimination (the structural test of
freelib, "takes every loose bit", assumes one connected pattern and does not hold for starts of several components)."""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT / 'experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count'))
import freelib as F  # noqa: E402


def from_junctions(stars):
    """Round 0 is the given junctions (lists of bit ids; a bit in two junctions is shared)."""
    owner = defaultdict(list)
    for j, S in enumerate(stars):
        for b in S:
            owner[b].append(j)
    if max(len(v) for v in owner.values()) > 2:
        raise ValueError('a distinction in three junctions')
    P = F.Presentation(1, linalg=True)
    P.bits_of = [list(S) for S in stars]
    P.owner = dict(owner)
    P.nbits = max(owner) + 1
    P.nbr = [set() for _ in stars]
    for b, js in owner.items():
        if len(js) == 2:
            P.nbr[js[0]].add(js[1])
            P.nbr[js[1]].add(js[0])
    n = len(stars)
    P.parents = [0] * n
    P.fresh = [len(S) for S in stars]
    P.round_of = [0] * n
    P.demand_at_birth = [None] * n
    P.live = list(range(n))
    P.basis = {}
    for j in range(n):
        P._add_row(j)
    return P


def gf2(rule):
    """The rule, with each new junction's implied flag recomputed by GF(2) elimination on its old bits."""
    def r(P, info, rng):
        for i in info:
            i['implied'] = P._reduce(P._mask(P.bits_of[i['j']][:i['p']])) == 0
        return rule(P, info, rng)
    r.__name__ = getattr(rule, '__name__', 'rule')
    return r


def grow(stars, rule, rounds, max_junctions=4000):
    P = from_junctions(stars)
    outcome = 'alive'
    for _ in range(rounds):
        r = P.step(gf2(rule), None)
        if r is None:
            outcome = 'stall'
            break
        if r['new'] == 0:
            outcome = 'closed'
            break
        if len(P.bits_of) > max_junctions:
            outcome = 'big'
            break
    return P, outcome


def pair(a, b, share):
    """Knots of a and b places, apart (share = 0) or sharing one distinction (share = 1)."""
    A = list(range(a))
    if share == 0:
        return [A, list(range(a, a + b))]
    return [A, [a - 1] + list(range(a, a + b - 1))]


def fewest_floor(m):
    """The fewest rule with the knot floor m in place of three (a control): 0 at an implied junction of demand 0, else
    max(d, m - p, 1)."""
    def rule(P, info, rng):
        return [i['d'] if (i['implied'] and i['d'] == 0) else max(i['d'], m - i['p'], 1) for i in info]
    rule.__name__ = f'fewest_floor{m}'
    return rule


def share(a, b, s):
    """Knots of a and b places sharing s distinctions (s = 0: apart)."""
    A = list(range(a))
    return [A, A[a - s:] + list(range(a, a + b - s))]


def open_counts(stars):
    from collections import Counter
    c = Counter(x for S in stars for x in S)
    return [sum(1 for x in S if c[x] == 1) for S in stars]


def stall_round(l, c):
    """FRESH-COUNT Theorem 2 extended (the advisor's table): the round at which a single seed on l distinctions stalls under one
    count c >= 2, or None if it runs."""
    if l <= 1 or c == l:
        return None
    if c <= l - 2:
        return 2
    if c == l - 1:
        return 4
    return 3


def predicted_uniform(stars, c, rounds):
    """Survival, stall round and junctions per round predicted by S1 and S2 for one count c >= 2."""
    from math import comb
    ls = open_counts(stars)
    stalls = [stall_round(l, c) for l in ls]
    stalls = [r for r in stalls if r is not None]
    if stalls:
        return {'survives': False, 'stall_round': min(stalls)}
    counts = [len(stars)]
    for t in range(1, rounds + 1):
        n = 0
        for l in ls:
            if l == c:
                n += comb(t + c - 1, c - 1)
            elif l == 1:
                n += 1 if t == 1 else comb(t - 1 + c - 1, c - 1)
        counts.append(n)
    return {'survives': True, 'counts': counts}


def predicted_fewest_piece(l, t):
    """Junctions created in round t >= 1 by one piece with l open distinctions of a start sharing one distinction, under the
    fewest rule (the advisor's table): l = 2: t + 1; l >= 3: C(l, t) up to the top, 1 at t = l + 1, t - l after."""
    from math import comb
    if l == 2:
        return t + 1
    if t <= l:
        return comb(l, t)
    if t == l + 1:
        return 1
    return t - l


def in_scope(stars):
    """Lemma 1's hypothesis: no two start junctions have a common neighbour among the start junctions."""
    n = len(stars)
    nb = [{k for k in range(n) if k != j and set(stars[j]) & set(stars[k])} for j in range(n)]
    return not any(nb[i] & nb[j] for i in range(n) for j in range(i + 1, n))
