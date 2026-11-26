"""tally_xcount.py RUNS...: the extension's pre-count (README.md, "The extension"): per kind of edit, size and law, the
placements read, those with a shared birth or nothing loose to read, and those where forbidding answers a reader's own
setting on one side or on every side (with how many of them split). The two knot laws give the same counts."""
import sys, json, gzip, collections
c = collections.Counter()
for p in sys.argv[1:]:
    for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)):
        r = json.loads(l)
        k = (r['kind of edit'], r['n'], r['law'], r['arm'])
        if r['kind'] != 'read': c[k + (r['kind'],)] += 1; continue
        d = r['forbidding changes with own setting']
        c[k + ('read',)] += 1
        c[k + ('one',)] += any(d); c[k + ('one, splits',)] += any(d) and r['splits']
        c[k + ('every',)] += all(d); c[k + ('every, splits',)] += all(d) and r['splits']
keys = sorted({k[:4] for k in c})
assert all(c[(e, n, 'parity', a, x)] == c[(e, n, 'nae', a, x)] for e, n, _, a in keys for x in ('read', 'one', 'every'))
print('| edit | knots | law | read | shared birth | nothing loose to read | forbidding answers a setting, one side (splits) | every side (splits) |')
print('|---|---|---|---|---|---|---|---|')
for k in keys:
    if k[2] == 'nae':
        print('| %s | %d | %s | %d | %d | %d | %d (%d) | %d (%d) |' % (k[0], k[1], k[3], c[k + ('read',)], c[k + ('shared birth',)], c[k + ('not read',)],
              c[k + ('one',)], c[k + ('one, splits',)], c[k + ('every',)], c[k + ('every, splits',)]))
