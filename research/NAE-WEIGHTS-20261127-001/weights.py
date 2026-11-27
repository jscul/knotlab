"""weights.py OUT.json: correlations under weightings of not-all-equal states.  NAE-WEIGHTS-20261127-001; README.md.

Values are read as signs (a distinction's value v as (-1)^v), and a weighting gives each allowed state a weight.
  equal       every allowed state the same weight (the scaffold under test)
  completions each allowed state weighted by its number of completions after one round of ordinary not-all-equal
              growth: the product over the round's births of 2^f - [the birth's inputs are all equal], f its fresh count
W1  On every tree-shaped census start (no cycle of shared distinctions, no two knots sharing two) and every pair of
    distinctions x, y: under the equal weighting the mean of the product of their signs is the product, over the knots on
    the route between them, of -1/(2^(a-1) - 1), a the knot's places (exact fractions).
W1r On the two rings of SIGNED-COUNT-20261126-001: the route formula over both routes, divided by one plus the ring's
    own product, against the exact means (-15/41, -33/95 with the far edit, -3/13).
W2  On every tree-shaped census start: for every two disjoint sets of knots and every pair of sign products of even
    size, each on the distinctions of one set alone, the mean of their product equals the product of their means
    (exact independence), under the equal weighting.
W3  The ring of four of SIGNED-COUNT: the number of its 82 states in which the four shared distinctions have even parity.
Under the completions weighting (the swap of the scaffold): W1 and W2 read on the same starts, no prediction."""
import sys, json, itertools, collections
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research' / 'NAE-LAYER-20261127-001'))
import t7 as T, census as C
forbid = T.forbid


def weighted_states(S, weighting):
    names, idx, sol = T.states(S)
    if weighting == 'equal': return names, idx, [(s, 1) for s in sol]
    st, status, births = forbid.grown(S, 'nae', 'ordinary')
    if status != 'funded': return names, idx, None
    out = []
    for s in sol:
        w = 1
        for b in births:
            ins = [(s >> idx[x]) & 1 for x in b['inputs']]
            w *= 2 ** b['f'] - (1 if len(set(ins)) == 1 else 0)
        out.append((s, w))
    return names, idx, out


def mean(ws, fn):
    tot = sum(w for _, w in ws); return Fraction(sum(w * fn(s) for s, w in ws), tot)


def sgn(s, bits): return -1 if sum((s >> b) & 1 for b in bits) % 2 else 1


def route_factor(S, x, y):
    """the product of -1/(2^(a-1) - 1) over the knots on the route from x to y (a tree start: unique route)"""
    h = forbid.holders(S)
    nb = collections.defaultdict(list)                    # distinction graph: x - knot - y
    for k, r in enumerate(S):
        for d in r: nb[('d', d)].append(('k', k)); nb[('k', k)].append(('d', d))
    prev = {('d', x): None}; frontier = [('d', x)]
    while frontier:
        nxt = []
        for u in frontier:
            for v in nb[u]:
                if v not in prev: prev[v] = u; nxt.append(v)
        frontier = nxt
    if ('d', y) not in prev: return Fraction(0)
    f = Fraction(1); u = ('d', y)
    while u is not None:
        if u[0] == 'k': a = len(S[u[1]]); f *= Fraction(-1, 2 ** (a - 1) - 1)
        u = prev[u]
    return f


if __name__ == '__main__':
    out = {}
    trees = [forbid.supports_of(s) for s in forbid.census() if C.tree_shaped(forbid.supports_of(s))]
    out['tree-shaped census starts'] = len(trees)
    for weighting in ('equal', 'completions'):
        w1 = collections.Counter(); w2 = collections.Counter(); ex1 = []; ex2 = []
        for S in trees:
            names, idx, ws = weighted_states(S, weighting)
            if ws is None: w1['not grown'] += 1; continue
            for x, y in itertools.combinations(names, 2):
                m = mean(ws, lambda s: sgn(s, [idx[x], idx[y]])); pred = route_factor(S, x, y)
                w1['pairs'] += 1; w1['equal to the route product'] += m == pred
                if m != pred and len(ex1) < 5: ex1.append([list(map(list, S)), x, y, str(m), str(pred)])
            K = list(range(len(S)))
            for r1 in range(1, len(K)):
                for A in itertools.combinations(K, r1):
                    rest = [k for k in K if k not in A]
                    for r2 in range(1, len(rest) + 1):
                        for B in itertools.combinations(rest, r2):
                            if A > B: continue
                            dA = sorted({x for k in A for x in S[k]}); dB = sorted({x for k in B for x in S[k]})
                            if set(dA) & set(dB): continue
                            for fa in itertools.combinations(dA, 2):
                                for fb in itertools.combinations(dB, 2):
                                    ia = [idx[v] for v in fa]; ib = [idx[v] for v in fb]
                                    mab = mean(ws, lambda s: sgn(s, ia + ib)); ma = mean(ws, lambda s: sgn(s, ia)); mb = mean(ws, lambda s: sgn(s, ib))
                                    w2['pairs of functions'] += 1; w2['independent'] += mab == ma * mb
                                    if mab != ma * mb and len(ex2) < 5: ex2.append([list(map(list, S)), fa, fb, str(mab), str(ma * mb)])
        out[weighting] = {'W1': dict(w1), 'W1 exceptions': ex1, 'W2': dict(w2), 'W2 exceptions': ex2}
    # W1r and W3 on SIGNED-COUNT's rings
    ring4 = ((0, 1, 10), (0, 2, 11), (1, 3, 12), (2, 3, 13)); ring4e = ((0, 1, 10), (0, 2, 11), (1, 3, 12, 20), (2, 3, 13))
    ring3 = ((0, 1, 10), (0, 2, 11), (1, 2, 12))
    def ring_formula(knots_direct, knots_around, knots_all):
        c = lambda a: Fraction(-1, 2 ** (a - 1) - 1)
        d = 1
        for a in knots_direct: d *= c(a)
        r = 1
        for a in knots_around: r *= c(a)
        z = 1
        for a in knots_all: z *= c(a)
        return (d + r) / (1 + z)
    rr = {}
    for label, S, direct, around in (('ring of four', ring4, [3], [3, 3, 3]), ("ring of four, Bob's edit", ring4e, [3], [3, 4, 3]), ('ring of three', ring3, [3], [3, 3])):
        names, idx, ws = weighted_states(S, 'equal')
        exact = mean(ws, lambda s: sgn(s, [idx[0], idx[1]]))
        rr[label] = {'states': len(ws), 'exact mean of signs of 0 and 1': str(exact), 'route formula': str(ring_formula(direct, around, [len(k) for k in S]))}
    out['W1r'] = rr
    names, idx, ws = weighted_states(ring4, 'equal')
    out['W3'] = {'states': len(ws), 'even parity of the four shared distinctions': sum(1 for s, _ in ws if sgn(s, [idx[0], idx[1], idx[2], idx[3]]) == 1)}
    json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str); print(json.dumps(out, indent=1, default=str)[:3000])
