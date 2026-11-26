"""tally_tables.py RUNS...: the census tables (README.md, "Kinds"): per kind of edit, knot law, law and weighting, the
placements read, those that do not split, and among those that split: excess without signalling (score above 2, or 3/4
for the Mermin game, with every complete record unchanged by far settings), excess with only the single values
unchanged, excess with a single value changed, and no excess; the largest score of each kind; and the placements where
forbidding answers a reader's own setting."""
import sys, json, gzip, collections
from fractions import Fraction


def rows(paths):
    for p in paths:
        for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)):
            yield json.loads(l)


c, best, examples = collections.Counter(), {}, collections.defaultdict(list)
for r in rows(sys.argv[1:]):
    key = (r['kind of edit'], r['law'], r['arm'])
    if r['kind'] != 'read' or 'U' not in r: continue
    dep = r.get('forbidding changes with own setting')
    for w in ('U', 'S'):
        k = key + (w,)
        c[k + ('read',)] += 1
        if dep is not None and any(dep): c[k + ('forbidding answers a setting',)] += 1
        if not r['splits']: c[k + ('does not split',)] += 1; continue
        bound = Fraction(3, 4) if r['kind of edit'] == 'M1' else Fraction(2)
        s = max(Fraction(v) for v in r[w]['scores'].values())
        kind = ('no excess' if s <= bound else 'excess without signalling' if r[w]['record unchanged']
                else 'excess, single values unchanged' if r[w]['single unchanged'] else 'excess, a single value changed')
        c[k + (kind,)] += 1
        if s > best.get(k + (kind,), Fraction(-1)): best[k + (kind,)] = s
        if kind != 'no excess' and len(examples[k + (kind,)]) < 3:
            examples[k + (kind,)].append((r['start'], r['readers'], r[w]['scores']))
cols = ['read', 'does not split', 'no excess', 'excess without signalling', 'excess, single values unchanged',
        'excess, a single value changed', 'forbidding answers a setting']
print('| edit | knot law | law | weighting | ' + ' | '.join(cols) + ' |')
print('|' + '---|' * (4 + len(cols)))
for k in sorted({k[:4] for k in c}):
    cells = []
    for col in cols:
        n = c[k + (col,)]
        cells.append('%d%s' % (n, ' (best %s)' % best[k + (col,)] if col.startswith('excess') and n else ''))
    print('| ' + ' | '.join(k) + ' | ' + ' | '.join(cells) + ' |')
for k, ex in sorted(examples.items()):
    print(k, ex)
