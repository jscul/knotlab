"""tally_count.py: the structural pre-count (README.md, "Order"): per kind of edit, knot law and law, placements by
kind, and among those read the ones where some setting pair removes old states, on one reader's side or both."""
import sys, json, collections
for path in sys.argv[1:]:
    c = collections.Counter(); f = collections.Counter()
    for l in open(path):
        r = json.loads(l); key = (r['kind of edit'], r['law'], r['arm'])
        c[key + (r['kind'],)] += 1
        if r['kind'] == 'read':
            f[key + ('forbids somewhere',)] += r['forbids somewhere']
            f[key + ('one side',)] += r['one-sided forbidding']
            f[key + ('both sides',)] += r['two-sided forbidding']
            f[key + ('splits',)] += r['splits']
    keys = sorted({k[:3] for k in c})
    print('| edit | knot law | law | read | shared birth | no allowed state | not read | splits | forbids somewhere | on one side | on both sides |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for k in keys:
        print('| %s | %s | %s | %d | %d | %d | %d | %d | %d | %d | %d |' % (k + tuple(c[k + (x,)] for x in ('read', 'shared birth', 'no allowed state', 'not read'))
              + tuple(f[k + (x,)] for x in ('splits', 'forbids somewhere', 'one side', 'both sides'))))
