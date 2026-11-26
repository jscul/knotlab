"""pairs.py GROWN.jsonl... OUT.jsonl: every pair of starts of one kind, in both readings, as alike.py's `agreement`.
One line per pair: the two starts (knots, index), the kind, and for sig0 and sig1 [first round nested, first round
equal, rounds compared]."""
import sys, json, itertools, collections
import alike
starts = []
for path in sys.argv[1:-1]:
    for l in open(path):
        x = json.loads(l)
        if x['kind'] in ('stalls', 'closes', 'unread'): continue
        starts.append(x)
by = collections.defaultdict(list)
for x in starts: by[x['kind']].append(x)
with open(sys.argv[-1], 'w') as f:
    for k, xs in sorted(by.items()):
        for a, b in itertools.combinations(xs, 2):
            out = {'kind': k, 'a': [a['n knots'], a['index']], 'b': [b['n knots'], b['index']]}
            for R in ('sig0', 'sig1'):
                out[R] = list(alike.agreement(a['rows'], b['rows'], R))
            f.write(json.dumps(out) + '\n')
print({k: len(v) for k, v in by.items()})
