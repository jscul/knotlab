"""third_algebra.py OUT.json: the third-layer referee's chosen-reading third layer, reproduced as algebra from its masks.
SELECTED-KNOTS-20261127-001.  Every class fact at a large scale is a sum of the thirteen ring facts (the families' facts,
one relation: their sum is fixed), so the 29 second-layer distinctions are the 29 masks on the thirteen ring parities.
Checked from the masks alone: the 18 chosen knots hold on the layer-two values and generate all their relations; the
layer-two code's least changes; the class facts of the layer-two code under its own least changes; the three third
facts and their relation; the least layer-two change flipping each; the two extra eligible knots.  The physical
carriers (round 24, scale 52) are the referee's and are not rerun here."""
import sys, json, itertools
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
d = json.load(open(ROOT / 'research/THIRD-LAYER-20261126-001/referee-R1/overlap_counts.json'))['thirteen-ring chosen third knot']
masks = d['their source masks']; n = len(masks); knots = d['eighteen selected second-layer knots']
def bits(v, w): return [(v >> i) & 1 for i in range(w)]
# layer-two values: for each ring-fact vector F with even weight, the 29 parities m_j . F
words = set()
for F in range(1 << 13):
    if bin(F).count('1') % 2: continue
    words.add(sum((bin(m & F).count('1') % 2) << j for j, m in enumerate(masks)))
C2 = sorted(words)
def rank(vs):
    piv = {}
    for v in vs:
        for p in sorted(piv, reverse=True):
            if (v >> p) & 1: v ^= piv[p]
        if v: piv[v.bit_length() - 1] = v
    return len(piv)
dimC2 = rank(C2)
kmask = [sum(1 << j for j in k) for k in knots]
holds = all(all(bin(w & km).count('1') % 2 == 0 for w in C2) for km in kmask)
# the code the 18 knots allow
allowed_count = 2 ** (n - rank(kmask))
# least nonzero words of C2 (its own least changes)
nz = [w for w in C2 if w]; wmin = min(bin(w).count('1') for w in nz)
least = [w for w in nz if bin(w).count('1') == wmin]
third = [sum(1 << j for j in s) for s in d['third facts as three disjoint sets of second-layer distinctions']]
even_on_least = [all(bin(t & w).count('1') % 2 == 0 for w in least) for t in third]
nonconst = [any(bin(t & w).count('1') % 2 for w in C2) for t in third]
rel = all(bin((third[0] ^ third[1] ^ third[2]) & w).count('1') % 2 == 0 for w in C2)
flip = [min(bin(w).count('1') for w in nz if bin(t & w).count('1') % 2) for t in third]
# dimension of layer-three class facts: functionals even on the least words, modulo those even on all of C2
def nullspace_dim(vs, width): return width - rank(vs)
dim_even_least = nullspace_dim(least, n); dim_even_all = nullspace_dim(C2, n)
extra = [sum(1 << j for j in k) for k in d['more eligible second-layer knots checked']]
extra_hold = [all(bin(w & e).count('1') % 2 == 0 for w in C2) for e in extra]
out = {'layer-two distinctions': n, 'dimension of layer-two values': dimC2, 'states': len(C2), 'the 18 knots hold': holds,
       'states the 18 knots allow': allowed_count, 'independent laws of the 18 knots': rank(kmask), 'least layer-two change size': wmin, 'number of least changes': len(least),
       'least changes equal the referee\'s': sorted(sorted(j for j in range(n) if (w >> j) & 1) for w in least) == sorted(map(sorted, d['all shortest layer-two changes as sets of its distinctions'])),
       'rank of least changes': rank(least), 'layer-three class-fact dimension': dim_even_least - dim_even_all,
       'third facts even on every least change': even_on_least, 'third facts not fixed': nonconst, 'their sum fixed': rel,
       'least layer-two change flipping each third fact': flip, 'extra knots hold on layer two': extra_hold}
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out, indent=1))
