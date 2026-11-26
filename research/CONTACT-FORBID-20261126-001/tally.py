"""tally.py contact_runs.jsonl: the contact cases (README.md): by source, kind of edit, knot law, law and weighting, the
placements, those where some reader's complete record moves with the far setting (and of them, in the shape of its
births), the largest total variation, the single values unchanged, and the largest score."""
import sys, json, collections
from fractions import Fraction
c, tvmax, best = collections.Counter(), collections.defaultdict(Fraction), collections.defaultdict(Fraction)
for l in open(sys.argv[1]):
    r = json.loads(l)
    for w in ('U', 'S'):
        k = (r['source'], r['kind of edit'], r['law'], r['arm'], w)
        mv = r[w]['record moves']
        c[k + ('placements',)] += 1
        moved = [m for m in mv if Fraction(m['largest total variation']) > 0]
        c[k + ('a record moves',)] += bool(moved)
        c[k + ('every record moves',)] += len(moved) == len(mv)
        c[k + ('in shape',)] += any(m['in the shape of its births'] for m in mv)
        c[k + ('single unchanged',)] += r[w]['single unchanged']
        tvmax[k] = max(tvmax[k], max(Fraction(m['largest total variation']) for m in mv))
        best[k] = max(best[k], Fraction(r[w]['score']))
print('| source | edit | knot law | law | weighting | placements | a record moves | every record moves | in the shape of births | largest total variation | single values unchanged | largest score |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for k in sorted({k[:5] for k in c}):
    print('| %s | %s | %s | %s | %s | %d | %d | %d | %d | %s | %d | %.4g |' % (k + tuple(c[k + (x,)] for x in ('placements', 'a record moves', 'every record moves', 'in shape'))
          + ('%.4g' % float(tvmax[k]), c[k + ('single unchanged',)], float(best[k]))))
