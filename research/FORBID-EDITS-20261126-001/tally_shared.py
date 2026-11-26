"""tally_shared.py RUNS...: the contact addendum (README.md, "With a contact"): the placements with a birth of two
readers, by kind of edit, knot law, law and weighting: how many, how many with a complete record changed by a far
setting, the kinds of excess, and the largest score."""
import sys, json, gzip, collections
from fractions import Fraction
c, best = collections.Counter(), {}
for p in sys.argv[1:]:
    for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)):
        r = json.loads(l)
        if r['kind'] != 'shared birth, read' or 'U' not in r: continue
        for w in ('U', 'S'):
            k = (r['kind of edit'], r['law'], r['arm'], w)
            bound = Fraction(3, 4) if r['kind of edit'] == 'M1' else Fraction(2)
            s = max(Fraction(v) for v in r[w]['scores'].values())
            kind = ('no excess' if s <= bound else 'excess without signalling' if r[w]['record unchanged']
                    else 'excess, single unchanged' if r[w]['single unchanged'] else 'excess, single changed')
            c[k + (kind,)] += 1; c[k + ('read',)] += 1; c[k + ('record changed',)] += not r[w]['record unchanged']
            if s > best.get(k, (Fraction(-1),))[0]: best[k] = (s, r[w]['record unchanged'])
print('| edit | knot law | law | weighting | placements with a birth of two readers | record changed | no excess | excess without signalling | excess, single values unchanged | excess, a single value changed | largest score |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for k in sorted({k[:4] for k in c}):
    print('| %s | %s | %s | %s | %d | %d | %d | %d | %d | %d | %.4g |' % (k + tuple(c[k + (x,)] for x in (
        'read', 'record changed', 'no excess', 'excess without signalling', 'excess, single unchanged', 'excess, single changed')) + (float(best[k][0]),)))
