"""forced.py OUT.jsonl: the space of forced relations among cycle parities, per stage (the advisor's test).  B is the set
of distinction sets that are at once a sum of knots' laws, an allowed change (a cycle of the graph reading) and empty on
the loose distinctions: the cut of a set of knots holding no loose distinction that is also a cycle (the literature's
bicycle space over two values).  If B = 0 no relation among cycle parities over the allowed states is forced by the
knots' laws beyond identities of the cycles themselves, whatever the carriers.  For B != 0 each element is listed with
its knots (which laws sum to it), whether one of them was born after the start, and its decomposition into
distinction-disjoint cycles.  Read on the witnesses of binding.py, rounds 0 to 3 of ordinary parity growth, and on
every census start of three to five knots and the 900 fresh starts of six to eight knots, rounds 0 and 1 (and 2 where
read).  Every distinction has at most two holders (checked)."""
import sys, os, json, collections, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as BD
classes, forbid = BD.classes, BD.forbid


def intersect(A, B, n):
    """basis of span(A) ∩ span(B) (vectors as ints)"""
    # solve sum a_i A_i = sum b_j B_j: stack [A | 0] and [B | ...] by elimination on pairs (v, tag)
    A = [a for a in A]; B = [b for b in B]
    basis_A = []
    piv = {}
    for a in A:
        v = a
        for p in sorted(piv, reverse=True):
            if (v >> p) & 1: v ^= piv[p]
        if v: piv[v.bit_length() - 1] = v; basis_A.append(v)
    # reduce A to echelon; for each b in a basis of B reduce by A; vectors of B whose combination reduces to 0 lie in A
    pivA = dict(piv)
    def red(v):
        for p in sorted(pivA, reverse=True):
            if (v >> p) & 1: v ^= pivA[p]
        return v
    # find combinations of B lying in span A: kernel of the map b -> red(b)
    Bb = []
    pivB = {}
    for b in B:
        v = b
        for p in sorted(pivB, reverse=True):
            if (v >> p) & 1: v ^= pivB[p]
        if v: pivB[v.bit_length() - 1] = v; Bb.append(v)
    R = [red(b) for b in Bb]
    # kernel of the matrix with columns R over GF(2): combinations c with sum c_i R_i = 0
    m = len(R); comb = []
    piv2 = {}
    for i, r in enumerate(R):
        v, tag = r, 1 << i
        for p in sorted(piv2, reverse=True):
            if (v >> p) & 1: v ^= piv2[p][0]; tag ^= piv2[p][1]
        if v: piv2[v.bit_length() - 1] = (v, tag)
        else: comb.append(tag)
    out = []
    for tag in comb:
        v = 0
        for i in range(m):
            if (tag >> i) & 1: v ^= Bb[i]
        out.append(v)
    return out


def read(supports, start_knots):
    names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    assert all(len(h) <= 2 for h in holders.values()), 'a distinction held three times'
    rows = [sum(1 << idx[x] for x in r) for r in supports]
    loose = sum(1 << idx[x] for x, h in holders.items() if len(h) == 1)
    Z = classes.nullspace(rows, n)
    RZ = intersect(rows, Z, n)                                  # sums of laws that are also allowed changes
    noloose = classes.nullspace([1 << i for i in range(n) if (loose >> i) & 1], n)  # vectors zero on loose
    B = intersect(RZ, noloose, n)
    rec = {'distinctions': n, 'dim Z': len(Z), 'dim of laws ∩ changes': len(RZ), 'dim B': len(B), 'elements': []}
    for v in B[:6]:
        # which knots' laws sum to v: solve rows-combination
        piv = {}; tagof = {}
        for i, r in enumerate(rows):
            w, tag = r, 1 << i
            for p in sorted(piv, reverse=True):
                if (w >> p) & 1: w ^= piv[p]; tag ^= tagof[p]
            if w: p = w.bit_length() - 1; piv[p] = w; tagof[p] = tag
        w, tag = v, 0
        for p in sorted(piv, reverse=True):
            if (w >> p) & 1: w ^= piv[p]; tag ^= tagof[p]
        K = [i for i in range(len(rows)) if (tag >> i) & 1]
        rec['elements'].append({'size': bin(v).count('1'), 'knots summing to it': K,
                                'holds a knot born after the start': any(k >= start_knots for k in K)})
    return rec


if __name__ == '__main__':
    out = sys.argv[1]; which = sys.argv[2] if len(sys.argv) > 2 else 'witnesses'
    with open(out, 'w') as f:
        if which == 'witnesses':
            items = list(BD.witnesses()); rounds = 3
        elif which == 'census':
            S = forbid.census(); items = [('census %d' % i, forbid.supports_of(s)) for i, s in enumerate(S)]; rounds = 2
        else:
            items = [('held out %d-%d' % (n, j), forbid.supports_of(s)) for n in (6, 7, 8) for j, s in enumerate(forbid.sampled(n, 300, 20261206 + n))]; rounds = 2
        for name, S in items:
            rec = {'start': name, 'knots': len(S), 'rounds': []}; st = S
            for t in range(0, rounds + 1):
                if t:
                    nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
                    if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                    st = nxt
                if len({x for r in st for x in r}) > 600: rec['rounds'].append({'round': t, 'end': 'not read'}); break
                try: r = read(st, len(S)); r['round'] = t; rec['rounds'].append(r)
                except AssertionError as e: rec['rounds'].append({'round': t, 'end': str(e)}); break
            f.write(json.dumps(rec) + '\n'); f.flush()
